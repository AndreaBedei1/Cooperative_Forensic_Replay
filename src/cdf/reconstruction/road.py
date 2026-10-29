
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np

from ..common.opendrive import LaneSample, best_map, lane_pieces_from_opendrive, lanes_from_opendrive

OPENDRIVE_DIR = Path("CarlaUE4") / "Content" / "Carla" / "Maps" / "OpenDrive"
MAP_MIN_FIT = 0.8
LANE_SEARCH_M = 4.0
MIN_SPEED_MPS = 1.0
LANE_TRAVEL_DEG = 30.0


class RoadLanes:

    def __init__(self, name: str, lanes: Sequence[LaneSample], pieces: Optional[Sequence[Any]] = None) -> None:
        from scipy.spatial import cKDTree
        self.name = name
        self.lanes = list(lanes)
        self.tree = cKDTree(np.array([(lane.x, lane.y) for lane in self.lanes]))
        self._pieces = None if pieces is None else list(pieces)
        self._graph: Optional["LaneGraph"] = None

    @property
    def graph(self) -> Optional["LaneGraph"]:
        if self._graph is None:
            pieces = self._pieces
            if pieces is None:
                source = _opendrive_sources().get(self.name)
                pieces = lane_pieces_from_opendrive(source) if source else []
            self._graph = LaneGraph(pieces) if pieces else None
        return self._graph

    def direction(self, x: float, y: float) -> Optional[float]:
        best: Optional[Tuple[float, float]] = None
        for index in self.tree.query_ball_point((x, y), LANE_SEARCH_M):
            lane = self.lanes[index]
            yaw = math.radians(lane.yaw)
            dx, dy = x - lane.x, y - lane.y
            along, across = dx * math.cos(yaw) + dy * math.sin(yaw), -dx * math.sin(yaw) + dy * math.cos(yaw)
            if abs(along) <= lane.length / 2.0 and abs(across) <= lane.width / 2.0:
                if best is None or abs(across) < best[0]:
                    best = (abs(across), yaw)
        return None if best is None else best[1]


_SOURCES: Optional[Dict[str, str]] = None
_ROADS: Dict[str, RoadLanes] = {}


def _opendrive_sources() -> Dict[str, str]:
    global _SOURCES
    if _SOURCES is None:
        _SOURCES = {}
        try:
            from ..common.config import load_run_config
            from ..common.installation import find_carla_root as find_root
            root = find_root(load_run_config().get("simulation.carla_root"))
        except Exception:
            root = None
        if root is not None:
            _SOURCES = {path.stem: path.read_text(encoding="utf-8", errors="replace")
                        for path in sorted((Path(root) / OPENDRIVE_DIR).glob("*.xodr"))}
    return _SOURCES


def road_for_positions(points: Sequence[Tuple[float, float]]) -> Optional[RoadLanes]:
    sources = _opendrive_sources()
    if not sources or not points:
        return None
    name, lanes = best_map(sources, points, MAP_MIN_FIT)
    if name is None or not lanes:
        return None
    return _road(name)


def road_named(name: str) -> Optional[RoadLanes]:
    return _road(name) if name in _opendrive_sources() else None


def _road(name: str) -> RoadLanes:
    if name not in _ROADS:
        source = _opendrive_sources()[name]
        _ROADS[name] = RoadLanes(name, lanes_from_opendrive(source), lane_pieces_from_opendrive(source))
    return _ROADS[name]


def road_for_trajectory(points: Sequence[Tuple[float, float]], headings: Sequence[float]) -> Optional[RoadLanes]:
    sources = _opendrive_sources()
    if not sources or not len(points):
        return None
    best: Optional[Tuple[Tuple[float, float], str]] = None
    for name in sorted(sources):
        graph = _road(name).graph
        if graph is None:
            continue
        fits, misfit = 0, 0.0
        for (x, y), heading in zip(points, headings):
            found = graph.candidates((float(x), float(y)), float(heading))
            if found:
                fits += 1
                misfit += min(c[3] for c in found)
        score = (fits / len(points), -misfit / max(fits, 1))
        if best is None or score > best[0]:
            best = (score, name)
    if best is None or best[0][0] < MAP_MIN_FIT:
        return None
    return _road(best[1])


@dataclass
class RoadFrame:

    road: RoadLanes
    x0: float
    y0: float
    yaw0: float
    _reference: Dict[int, Any] = field(default_factory=dict, repr=False, compare=False)
    source: str = "own poses"

    @classmethod
    def from_ego_records(cls, records: Sequence[Mapping[str, Any]], step: int = 5,
                         map_name: Optional[str] = None) -> Optional["RoadFrame"]:
        if not records:
            return None
        road = road_named(map_name) if map_name else None
        source = "incident context"
        if road is None:
            sample = records[::step]
            road = road_for_trajectory([(float(r["x"]), float(r["y"])) for r in sample],
                                       [math.radians(float(r["yaw_deg"])) for r in sample])
            source = "own poses"
        if road is None:
            return None
        first = records[0]
        return cls(road, float(first["x"]), float(first["y"]), math.radians(float(first["yaw_deg"])), source=source)

    def to_world(self, x: float, y: float) -> Tuple[float, float]:
        c, s = math.cos(self.yaw0), math.sin(self.yaw0)
        return self.x0 + c * x - s * y, self.y0 + s * x + c * y

    def vector_to_world(self, vx: float, vy: float) -> Tuple[float, float]:
        c, s = math.cos(self.yaw0), math.sin(self.yaw0)
        return c * vx - s * vy, s * vx + c * vy

    def reference(self, ego: Any) -> Optional["ReferencePath"]:
        key = id(ego)
        if key not in self._reference:
            graph = self.road.graph
            if graph is None:
                self._reference[key] = None
            else:
                states = ego.states
                xy = np.array([self.to_world(s.x, s.y) for s in states])
                headings = np.array([self.yaw0 + s.heading for s in states])
                self._reference[key] = ReferencePath(graph, np.array([s.t_local for s in states]), xy, headings)
        return self._reference[key]

    def path_at(self, ego: Any, t: float) -> Optional[Tuple["LanePath", float, float]]:
        reference = self.reference(ego)
        if reference is None:
            return None
        path = reference.path(reference.index(t))
        if path is None:
            return None
        own = ego.at(t)
        s0, l0, _ = path.project(np.array([self.to_world(own.x, own.y)]))[0]
        return path, float(s0), float(l0)

    def to_path(self, ego: Any, t: float, local_xy: np.ndarray) -> Optional[np.ndarray]:
        state = self.path_at(ego, t)
        if state is None:
            return None
        path, s0, l0 = state
        world = np.array([self.to_world(float(x), float(y)) for x, y in np.atleast_2d(local_xy)])
        out = path.project(world)
        out[:, 0] -= s0
        out[:, 1] -= l0
        return out

    def lane_headings(self, x: float, y: float) -> List[float]:
        graph = self.road.graph
        if graph is None:
            return []
        found = sorted((abs(offset), h) for _, _, offset, width, h in graph.nearby(self.to_world(x, y))
                       if abs(offset) <= 0.5 * width + 0.5)
        return [_wrap(h - self.yaw0) for _, h in found]

    def lane_curvature(self, x: float, y: float, vx: float, vy: float) -> Optional[float]:
        graph = self.road.graph
        speed = math.hypot(vx, vy)
        if graph is None or speed < MIN_SPEED_MPS:
            return None
        wvx, wvy = self.vector_to_world(vx, vy)
        travel = math.atan2(wvy, wvx)
        found = sorted((abs(offset), i, s) for i, s, offset, width, h in graph.nearby(self.to_world(x, y))
                       if abs(offset) <= 0.5 * width + 0.5 and abs(_wrap(h - travel)) <= math.radians(LANE_TRAVEL_DEG))
        if not found:
            return None
        _, i, s = found[0]
        piece = graph.pieces[i]
        if str(piece.junction) not in ("-1", "None", ""):
            return None
        cumulative = graph.paths[i].cumulative
        s0, s1 = max(s - 5.0, 0.0), min(s + 5.0, float(cumulative[-1]))
        if s1 - s0 < 2.0:
            return None
        headings = np.unwrap(np.asarray(piece.headings, dtype=float))
        return float((np.interp(s1, cumulative, headings) - np.interp(s0, cumulative, headings)) / (s1 - s0))

    def along_lane(self, x: float, y: float, vx: float, vy: float) -> Optional[Tuple[float, float]]:
        wx, wy = self.to_world(x, y)
        wvx, wvy = self.vector_to_world(vx, vy)
        speed = math.hypot(wvx, wvy)
        if speed < MIN_SPEED_MPS:
            return None
        heading = self.road.direction(wx, wy)
        if heading is None:
            return None
        dx, dy = math.cos(heading), math.sin(heading)
        along = wvx * dx + wvy * dy
        if abs(along) < speed * math.cos(math.radians(LANE_TRAVEL_DEG)):
            return None
        c, s = math.cos(self.yaw0), math.sin(self.yaw0)
        lvx, lvy = along * dx, along * dy
        return c * lvx + s * lvy, -s * lvx + c * lvy

    def lane_toward_speed(self, x: float, y: float, vx: float, vy: float,
                          ego_x: float, ego_y: float) -> Optional[float]:
        wx, wy = self.to_world(x, y)
        wvx, wvy = self.vector_to_world(vx, vy)
        if math.hypot(wvx, wvy) < MIN_SPEED_MPS:
            return None
        heading = self.road.direction(wx, wy)
        if heading is None:
            return None
        dx, dy = math.cos(heading), math.sin(heading)
        if wvx * dx + wvy * dy < 0.0:
            dx, dy = -dx, -dy
        nx, ny = -dy, dx
        ex, ey = self.to_world(ego_x, ego_y)
        side = (ex - wx) * nx + (ey - wy) * ny
        if abs(side) < 1e-6:
            return None
        return (wvx * nx + wvy * ny) * (1.0 if side > 0 else -1.0)



PATH_AHEAD_M = 80.0
PATH_BEHIND_M = 10.0
CONTACT_M = 0.3
CONTINUATION_DEG = 30.0
MATCH_RADIUS_M = 6.0
MATCH_EDGE_MARGIN_M = 1.0
MATCH_HEADING_DEG = 45.0
MATCH_HEADING_STD_DEG = 20.0
LANE_CHANGE_COST = 3.0
JUMP_COST = 20.0


def _wrap(angle: float) -> float:
    return (angle + math.pi) % (2.0 * math.pi) - math.pi


class LanePath:

    def __init__(self, points: Sequence[Tuple[float, float]]) -> None:
        self.points = np.asarray(points, dtype=float)
        seg = np.diff(self.points, axis=0)
        self.lengths = np.hypot(seg[:, 0], seg[:, 1])
        self.headings = np.arctan2(seg[:, 1], seg[:, 0])
        self.cumulative = np.concatenate([[0.0], np.cumsum(self.lengths)])

    def project(self, xy: np.ndarray) -> np.ndarray:
        xy = np.atleast_2d(np.asarray(xy, dtype=float))
        a = self.points[:-1][None, :, :]
        d = (self.points[1:] - self.points[:-1])[None, :, :]
        rel = xy[:, None, :] - a
        length2 = np.maximum(np.sum(d * d, axis=2), 1e-9)
        f = np.clip(np.sum(rel * d, axis=2) / length2, 0.0, 1.0)
        foot = a + f[:, :, None] * d
        dist = np.hypot(*(xy[:, None, :] - foot).transpose(2, 0, 1))
        k = np.argmin(dist, axis=1)
        idx = np.arange(len(xy))
        h = self.headings[k]
        off = xy - foot[idx, k]
        lateral = -np.sin(h) * off[:, 0] + np.cos(h) * off[:, 1]
        s = self.cumulative[k] + f[idx, k] * self.lengths[k]
        return np.column_stack([s, lateral, h])


class LaneGraph:

    def __init__(self, pieces: Sequence[Any]) -> None:
        from scipy.spatial import cKDTree
        self.pieces = list(pieces)
        self.points = [np.asarray(piece.points, dtype=float) for piece in self.pieces]
        self.widths = [np.asarray(piece.widths, dtype=float) for piece in self.pieces]
        self.paths = [LanePath(points) for points in self.points]
        owners = [(i, k) for i, pts in enumerate(self.points) for k in range(len(pts))]
        self.owner = np.array(owners, dtype=int)
        self.tree = cKDTree(np.vstack(self.points))
        starts = cKDTree(np.array([pts[0] for pts in self.points]))
        self.successors: List[List[int]] = []
        for i, piece in enumerate(self.pieces):
            heading = piece.headings[-1]
            found = [j for j in starts.query_ball_point(self.points[i][-1], CONTACT_M)
                     if j != i and abs(_wrap(self.pieces[j].headings[0] - heading)) <= math.radians(CONTINUATION_DEG)]
            self.successors.append(sorted(found))
        index = {piece.key: i for i, piece in enumerate(self.pieces)}
        self.neighbours: List[List[int]] = []
        for piece in self.pieces:
            road, section, lane = piece.key
            sign = 1 if lane > 0 else -1
            self.neighbours.append(sorted(index[(road, section, lane + d)] for d in (-1, 1)
                                          if (road, section, lane + d) in index and (lane + d) * sign > 0))
        self._reach: Dict[int, set] = {}

    def length(self, i: int) -> float:
        return float(self.paths[i].cumulative[-1])

    def nearby(self, xy: Tuple[float, float]) -> List[Tuple[int, float, float, float, float]]:
        out = []
        near: Dict[int, List[int]] = {}
        for flat in self.tree.query_ball_point(xy, MATCH_RADIUS_M):
            i, k = self.owner[flat]
            near.setdefault(int(i), []).append(int(k))
        for i, ks in near.items():
            path = self.paths[i]
            lo, hi = max(min(ks) - 1, 0), min(max(ks) + 1, len(path.points) - 1)
            if hi <= lo:
                continue
            sub = LanePath(path.points[lo:hi + 1])
            s, offset, h = sub.project(np.array([xy]))[0]
            s += path.cumulative[lo]
            out.append((i, float(s), float(offset), float(np.interp(s, path.cumulative, self.widths[i])), float(h)))
        return out

    def candidates(self, xy: Tuple[float, float], heading: float) -> List[Tuple[int, float, float, float]]:
        out = []
        for i, s, offset, width, h in self.nearby(xy):
            dh = abs(_wrap(h - heading))
            if abs(offset) > 0.5 * width + MATCH_EDGE_MARGIN_M or dh > math.radians(MATCH_HEADING_DEG):
                continue
            cost = (offset / max(0.5 * width, 0.5)) ** 2 + (dh / math.radians(MATCH_HEADING_STD_DEG)) ** 2
            out.append((i, s, offset, float(cost)))
        return out

    def reachable(self, i: int) -> set:
        if i not in self._reach:
            seen, frontier = {i}, [i]
            for _ in range(2):
                frontier = [j for k in frontier for j in self.successors[k] if j not in seen]
                seen.update(frontier)
            self._reach[i] = seen
        return self._reach[i]

    def transition(self, i: int, s_i: float, j: int, s_j: float) -> float:
        if i == j:
            return 0.0 if s_j >= s_i - 0.5 else 2.0
        reach = self.reachable(i)
        if j in reach:
            return 0.0
        if any(j in self.neighbours[k] for k in reach) or any(k in self.neighbours[j] for k in reach):
            return LANE_CHANGE_COST
        return JUMP_COST


def map_match(graph: LaneGraph, xy: np.ndarray, headings: np.ndarray) -> List[Optional[Tuple[int, float, float]]]:
    out: List[Optional[Tuple[int, float, float]]] = [None] * len(xy)
    k = 0
    while k < len(xy):
        cands = graph.candidates(tuple(xy[k]), float(headings[k]))
        if not cands:
            k += 1
            continue
        layers, costs, back = [cands], [np.array([c[3] for c in cands])], [None]
        m = k + 1
        while m < len(xy):
            nxt = graph.candidates(tuple(xy[m]), float(headings[m]))
            if not nxt:
                break
            prev = layers[-1]
            total = np.empty(len(nxt))
            pointer = np.empty(len(nxt), dtype=int)
            for b, (j, s_j, _, e_j) in enumerate(nxt):
                options = [costs[-1][a] + graph.transition(i, s_i, j, s_j) for a, (i, s_i, _, _) in enumerate(prev)]
                a = int(np.argmin(options))
                total[b], pointer[b] = options[a] + e_j, a
            layers.append(nxt)
            costs.append(total)
            back.append(pointer)
            m += 1
        best = int(np.argmin(costs[-1]))
        for layer in range(len(layers) - 1, -1, -1):
            i, s, offset, _ = layers[layer][best]
            out[k + layer] = (i, s, offset)
            if back[layer] is not None:
                best = int(back[layer][best])
        k = m
    return out


def _chain(graph: LaneGraph, start: int, route: Sequence[int], future: np.ndarray, ahead: float) -> List[int]:
    chain, length = [start], graph.length(start)
    pending = list(route)
    while length < ahead:
        options = graph.successors[chain[-1]]
        if not options:
            break
        nxt = next((j for j in options if pending and j == pending[0]), None)
        if nxt is not None:
            pending.pop(0)
        elif len(options) == 1:
            nxt = options[0]
        elif len(future):
            def miss(j: int) -> float:
                pts = graph.points[j]
                return float(np.mean(np.min(np.hypot(pts[:, None, 0] - future[None, :, 0],
                                                     pts[:, None, 1] - future[None, :, 1]), axis=1)))
            nxt = min(options, key=miss)
        else:
            heading = graph.pieces[chain[-1]].headings[-1]
            nxt = min(options, key=lambda j: abs(_wrap(graph.pieces[j].headings[-1] - heading)))
        if nxt in chain:
            break
        while pending and pending[0] in chain:
            pending.pop(0)
        chain.append(nxt)
        length += graph.length(nxt)
    return chain


class ReferencePath:

    def __init__(self, graph: LaneGraph, times: np.ndarray, xy: np.ndarray, headings: np.ndarray) -> None:
        self.graph = graph
        self.times = np.asarray(times, dtype=float)
        self.xy = np.asarray(xy, dtype=float)
        self.headings = np.asarray(headings, dtype=float)
        self.match = map_match(graph, self.xy, self.headings)
        self._paths: Dict[int, LanePath] = {}
        self.episode: List[Optional[int]] = []
        current, key = -1, None
        for m in self.match:
            piece = None if m is None else m[0]
            if piece is None:
                self.episode.append(None)
                key = None
                continue
            if piece != key:
                current, key = current + 1, piece
            self.episode.append(current)
        self._start: Dict[int, int] = {}
        for k, e in enumerate(self.episode):
            if e is not None and e not in self._start:
                self._start[e] = k

    def index(self, t: float) -> int:
        return int(np.clip(np.searchsorted(self.times, t - 1e-9), 0, len(self.times) - 1)) if len(self.times) else 0

    def lane_at(self, k: int) -> Optional[Tuple[str, int, int]]:
        m = self.match[k]
        return None if m is None else self.graph.pieces[m[0]].key

    def path(self, k: int) -> Optional[LanePath]:
        e = self.episode[k]
        if e is None:
            return None
        if e not in self._paths:
            first = self._start[e]
            piece = self.match[first][0]
            later = [m[0] for m in self.match[first:] if m is not None and m[0] != piece]
            route = [p for n, p in enumerate(later) if n == 0 or p != later[n - 1]]
            after = [k for k in range(first, len(self.match)) if self.episode[k] != e]
            future = self.xy[after[0]:] if after else np.empty((0, 2))
            chain = _chain(self.graph, piece, route, future, PATH_AHEAD_M + self.graph.length(piece))
            points = np.vstack([self.graph.points[i] if n == 0 else self.graph.points[i][1:]
                                for n, i in enumerate(chain)])
            h0 = self.graph.pieces[chain[0]].headings[0]
            behind = points[0] - PATH_BEHIND_M * np.array([math.cos(h0), math.sin(h0)])
            self._paths[e] = LanePath(np.vstack([behind[None, :], points]))
        return self._paths[e]
