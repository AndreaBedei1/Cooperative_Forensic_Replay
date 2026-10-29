
from __future__ import annotations

import json
import math
import statistics
from bisect import bisect_right
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from ..reconstruction.config import ReconstructionConfig, load_config
from ..reconstruction.conflict import HEADING_MIN_SPEED_MPS, OBLIQUE_VIEW_DEG
from ..reconstruction.models import transition_of
from ..reconstruction.tracking import EgoFootprint
from ..reconstruction.world_state import compact_state

FALLBACK_BLUEPRINT = "vehicle.tesla.model3"
SPEEDS = (0.25, 0.5, 1.0, 2.0)
_EPS = 1e-6


def _read_json(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def lerp(a: float, b: float, f: float) -> float:
    return a + (b - a) * f


def lerp_angle_deg(a: float, b: float, f: float) -> float:
    return a + ((b - a + 180.0) % 360.0 - 180.0) * f


def wrap_deg(angle: float) -> float:
    return (angle + 180.0) % 360.0 - 180.0



@dataclass(frozen=True)
class Pose:

    x: float
    y: float
    z: float
    yaw: float
    pitch: float = 0.0
    roll: float = 0.0


class Trajectory:

    def __init__(self, times: Sequence[float], poses: Sequence[Pose], speeds: Optional[Sequence[float]] = None):
        if not times or len(times) != len(poses):
            raise ValueError("a trajectory needs one pose per timestamp")
        self.times: List[float] = []
        self.poses: List[Pose] = []
        self.speeds: List[float] = []
        for index in sorted(range(len(times)), key=lambda i: times[i]):
            if self.times and times[index] <= self.times[-1] + _EPS:
                continue
            self.times.append(float(times[index]))
            self.poses.append(poses[index])
            self.speeds.append(float(speeds[index]) if speeds is not None else 0.0)

    @classmethod
    def from_records(cls, records: Sequence[Mapping[str, Any]]) -> "Trajectory":
        times, poses, speeds = [], [], []
        for record in records:
            times.append(float(record["timestamp"]))
            poses.append(Pose(float(record["x"]), float(record["y"]), float(record["z"]), float(record["yaw_deg"]),
                              float(record.get("pitch_deg", 0.0)), float(record.get("roll_deg", 0.0))))
            velocity = record.get("velocity") or {}
            speeds.append(math.hypot(float(velocity.get("x", 0.0)), float(velocity.get("y", 0.0))))
        return cls(times, poses, speeds)

    @property
    def start(self) -> float:
        return self.times[0]

    @property
    def end(self) -> float:
        return self.times[-1]

    def _bracket(self, t: float) -> Tuple[int, float]:
        if t <= self.times[0]:
            return 0, 0.0
        if t >= self.times[-1]:
            return len(self.times) - 1, 0.0
        index = bisect_right(self.times, t) - 1
        return index, (t - self.times[index]) / (self.times[index + 1] - self.times[index])

    def shifted(self, delta: float) -> "Trajectory":
        return Trajectory([t + delta for t in self.times], list(self.poses), list(self.speeds))

    def pose_at(self, t: float) -> Pose:
        index, f = self._bracket(t)
        a = self.poses[index]
        if f == 0.0:
            return a
        b = self.poses[index + 1]
        return Pose(lerp(a.x, b.x, f), lerp(a.y, b.y, f), lerp(a.z, b.z, f), lerp_angle_deg(a.yaw, b.yaw, f),
                    lerp_angle_deg(a.pitch, b.pitch, f), lerp_angle_deg(a.roll, b.roll, f))

    def speed_at(self, t: float) -> float:
        index, f = self._bracket(t)
        if f == 0.0:
            return self.speeds[index]
        return lerp(self.speeds[index], self.speeds[index + 1], f)



class PlaybackClock:

    def __init__(self, duration: float, speed: float = 0.5, start: float = 0.0, playing: bool = True):
        if duration < 0:
            raise ValueError("duration must not be negative")
        if speed <= 0:
            raise ValueError("speed must be positive")
        self.duration = float(duration)
        self.speed = float(speed)
        self.time = self._clamp(start)
        self.playing = bool(playing) and not self.at_end

    def _clamp(self, t: float) -> float:
        return min(max(float(t), 0.0), self.duration)

    @property
    def at_end(self) -> bool:
        return self.time >= self.duration - _EPS

    def advance(self, wall_dt: float) -> None:
        if self.playing and wall_dt > 0:
            self.time = self._clamp(self.time + wall_dt * self.speed)
            if self.at_end:
                self.playing = False

    def toggle(self) -> None:
        if not self.playing and self.at_end:
            self.time = 0.0
        self.playing = not self.playing

    def pause(self) -> None:
        self.playing = False

    def seek(self, delta: float) -> None:
        self.time = self._clamp(self.time + delta)

    def seek_to(self, t: float) -> None:
        self.time = self._clamp(t)

    def restart(self) -> None:
        self.time = 0.0

    def set_speed(self, speed: float) -> None:
        if speed <= 0:
            raise ValueError("speed must be positive")
        self.speed = float(speed)



@dataclass(frozen=True)
class ReplayEvent:
    time: float
    actor: str
    event_type: str
    subject: Optional[str]
    node_id: str
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StateInterval:

    actor: str
    state: str
    subject: Optional[str]
    start: float
    end: Optional[float]

    def active_at(self, t: float) -> bool:
        return self.start - _EPS <= t and (self.end is None or t < self.end - _EPS)


def state_intervals(events: Sequence[ReplayEvent], observed_from: float = 0.0) -> List[StateInterval]:
    open_: Dict[Tuple[str, Optional[str]], ReplayEvent] = {}
    appeared: Dict[Optional[str], float] = {}
    out: List[StateInterval] = []
    for event in events:
        if event.event_type.startswith("TRACK_APPEARED"):
            appeared[event.subject] = event.time
        transition = transition_of(event.event_type)
        if transition is None:
            continue
        state, starts = transition
        key = (state, event.subject)
        if starts:
            if key in open_:
                out.append(StateInterval(event.actor, state, event.subject, open_[key].time, event.time))
            open_[key] = event
            continue
        begin = open_.pop(key, None)
        since = begin.time if begin is not None else appeared.get(event.subject, observed_from)
        out.append(StateInterval(event.actor, state, event.subject, since, event.time))
    for (state, subject), begin in open_.items():
        out.append(StateInterval(begin.actor, state, subject, begin.time, None))
    return sorted(out, key=lambda item: (item.start, item.state, item.subject or ""))


@dataclass
class PerceivedStates:

    times: List[float]
    states: List[Dict[str, Any]]

    def state_at(self, t: float) -> Optional[Dict[str, Any]]:
        index = bisect_right(self.times, t + _EPS) - 1
        return None if index < 0 else self.states[index]


def load_perceived_states(path: Path, origin: float, run_start: float) -> Optional[PerceivedStates]:
    times, states = [], []
    for row in _read_jsonl(path):
        if row.get("perceived_state") is not None:
            times.append(round(origin + float(row["t_local"]) - run_start, 6))
            states.append(row["perceived_state"])
    return PerceivedStates(times, states) if states else None


@dataclass
class LocalEvents:
    recorder: str
    origin: float
    events: List[ReplayEvent]
    intervals: List[StateInterval]


def load_local_events(path: Path, run_start: float, clock_origin: Optional[float] = None) -> LocalEvents:
    graph = _read_json(path)
    owner = str(graph["owner"])
    origin = float(graph["recorder"]["clock"]["origin_source_timestamp"])
    offset = (origin if clock_origin is None else clock_origin) - run_start
    events = [ReplayEvent(round(offset + float(node["t_local"]), 6), owner, str(node["event_type"]),
                          node.get("subject_id"), str(node["node_id"]),dict(node.get('attributes') or {})) for node in graph["nodes"]]
    return LocalEvents(owner, origin, events, state_intervals(events, observed_from=round(offset, 6)))


@dataclass(frozen=True)
class CollisionMark:
    time: float
    participants: Tuple[str, ...]
    node_id: str


def load_collisions(path: Path, origins: Mapping[str, float], run_start: float) -> List[CollisionMark]:
    marks = []
    for node in _read_json(path)["nodes"]:
        if node["event_type"] != "COLLISION":
            continue
        times = [origins[obs["graph"]] + float(obs["t_local"]) - run_start
                 for obs in node.get("observations", []) if obs["graph"] in origins]
        if times:
            marks.append(CollisionMark(round(min(times), 6), tuple(node.get("participants") or ()), str(node["node_id"])))
    return sorted(marks, key=lambda mark: mark.time)


def load_recontacts(path: Path) -> set:
    nodes = [node for node in _read_json(path)["nodes"] if node["event_type"] == "COLLISION"]
    collisions = {(str(obs["graph"]), str(obs["local_node"])) for node in nodes for obs in node.get("observations", [])}
    recontacts = {(str(graph), str(local_node)) for node in nodes
                  for item in (node.get("attributes") or {}).get("recontacts", [])
                  for graph, local_node, _ in item.get("observations", [])}
    return recontacts - collisions


ASSOCIATED = "ASSOCIATED"
ANONYMOUS = "ANONYMOUS"


def load_track_statuses(path: Path) -> Dict[Tuple[str, str], Tuple[str, Optional[str]]]:
    statuses: Dict[Tuple[str, str], Tuple[str, Optional[str]]] = {}
    for item in _read_json(path):
        status = str(item.get("status") or ANONYMOUS)
        entity = str(item["global_entity"]) if status == ASSOCIATED else None
        statuses[(str(item["local_graph"]), str(item["local_track"]))] = (status, entity)
    return statuses



GHOST_HEIGHT_M = 1.5
DEFAULT_FOOTPRINT = EgoFootprint(-2.3, 2.3, -0.95, 0.95)
HEADING_FROM_VELOCITY, HEADING_HELD, HEADING_UNKNOWN = "velocity", "held", "unknown"


def local_to_world(origin: Pose, x_local: float, y_local: float) -> Tuple[float, float]:
    c0, s0 = math.cos(math.radians(origin.yaw)), math.sin(math.radians(origin.yaw))
    return origin.x + c0 * x_local - s0 * y_local, origin.y + s0 * x_local + c0 * y_local


def rotate(x: float, y: float, yaw_deg: float) -> Tuple[float, float]:
    c, s = math.cos(math.radians(yaw_deg)), math.sin(math.radians(yaw_deg))
    return c * x - s * y, s * x + c * y


@dataclass(frozen=True)
class GhostGeometry:

    length: float = 4.6
    width: float = 1.9
    height: float = GHOST_HEIGHT_M
    max_gap: float = 0.5

    @classmethod
    def from_config(cls, config: ReconstructionConfig) -> "GhostGeometry":
        return cls(length=float(config.semantics.target_length_m), width=float(config.semantics.target_width_m),
                   max_gap=float(config.tracking.max_track_gap_s))


def track_heading(vx: float, vy: float, vel_std: float) -> Optional[float]:
    if math.hypot(vx, vy) < max(HEADING_MIN_SPEED_MPS, 2.0 * max(vel_std, 0.0)):
        return None
    return math.degrees(math.atan2(vy, vx))


def nominal_box_centre(longitudinal: float, lateral: float, surface_offset: float, heading_deg: float,
                       footprint: EgoFootprint, length: float, width: float) -> Tuple[float, float]:
    ux, uy = math.cos(math.radians(heading_deg)), math.sin(math.radians(heading_deg))
    nx, ny = footprint.outward(longitudinal, lateral)
    near_x, near_y = longitudinal - surface_offset * nx, lateral - surface_offset * ny
    gx, gy = -nx, -ny
    along, across = gx * ux + gy * uy, -gx * uy + gy * ux
    oblique = math.sin(math.radians(OBLIQUE_VIEW_DEG))
    back = math.copysign(length / 2.0 * min(abs(along) / oblique, 1.0), along)
    side = math.copysign(width / 2.0 * min(abs(across) / oblique, 1.0), across)
    return near_x - back * ux + side * uy, near_y - back * uy - side * ux


@dataclass(frozen=True)
class TrackPoint:

    time: float
    position: Tuple[float, float]
    centre: Tuple[float, float]
    yaw: float
    heading: str
    measured: bool
    clearance: Optional[float] = None


@dataclass
class TrackPath:

    recorder: str
    track_id: str
    samples: List[TrackPoint]
    status: str = ANONYMOUS
    entity: Optional[str] = None
    max_gap: float = 0.5
    road_user: Optional[str] = None
    times: List[float] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.samples = sorted(self.samples, key=lambda sample: sample.time)
        self.times = [sample.time for sample in self.samples]

    @property
    def name(self) -> str:
        return "{0}:{1}".format(self.recorder, self.track_id)

    @property
    def ghost(self) -> bool:
        return self.status != ASSOCIATED and self.road_user is None

    @property
    def label(self) -> str:
        if self.road_user is not None:
            return "{0} → {1}".format(self.name, self.road_user)
        if self.ghost:
            return "{0} / {1}".format(self.name, ANONYMOUS)
        return "{0} → {1}".format(self.name, self.entity)

    @property
    def start(self) -> float:
        return self.times[0]

    @property
    def end(self) -> float:
        return self.times[-1]

    def state_at(self, t: float) -> Optional[TrackPoint]:
        if not self.samples or t < self.times[0] - _EPS or t > self.times[-1] + _EPS:
            return None
        index = max(0, bisect_right(self.times, t + _EPS) - 1)
        a = self.samples[index]
        if index == len(self.samples) - 1 or t <= a.time + _EPS:
            return a
        b = self.samples[index + 1]
        if b.time - a.time > self.max_gap + _EPS:
            return None
        f = (t - a.time) / (b.time - a.time)
        yaw = a.yaw
        if (a.heading == HEADING_UNKNOWN) == (b.heading == HEADING_UNKNOWN):
            yaw = lerp_angle_deg(a.yaw, b.yaw, f)
        clearance = None if a.clearance is None or b.clearance is None else lerp(a.clearance, b.clearance, f)
        return TrackPoint(t, (lerp(a.position[0], b.position[0], f), lerp(a.position[1], b.position[1], f)),
                          (lerp(a.centre[0], b.centre[0], f), lerp(a.centre[1], b.centre[1], f)),
                          yaw, a.heading, a.measured, clearance)


def load_tracks(path: Path, recorder: str, trajectory: Trajectory, frame_origin: Pose, clock_origin: float,
                run_start: float, footprint: Optional[EgoFootprint] = None, geometry: Optional[GhostGeometry] = None,
                statuses: Optional[Mapping[Tuple[str, str], Tuple[str, Optional[str]]]] = None,
                recorded: Optional[Trajectory] = None,
                road_users: Optional[Mapping[Tuple[str, str], str]] = None) -> List[TrackPath]:
    footprint = footprint or DEFAULT_FOOTPRINT
    geometry = geometry or GhostGeometry()
    rows: Dict[str, List[Dict[str, Any]]] = {}
    for row in _read_jsonl(path):
        rows.setdefault(str(row["track_id"]), []).append(row)
    tracks = []
    for track_id in sorted(rows):
        samples, held = [], None
        for row in sorted(rows[track_id], key=lambda item: float(item["t_local"])):
            source_time = clock_origin + float(row["t_local"])
            observer = trajectory.pose_at(source_time)
            own = (recorded or trajectory).pose_at(source_time)
            if row.get("longitudinal_m") is not None and row.get("lateral_m") is not None:
                dx, dy = rotate(float(row["longitudinal_m"]), float(row["lateral_m"]), observer.yaw)
                position = (observer.x + dx, observer.y + dy)
            else:
                position = local_to_world(frame_origin, float(row["x_m"]), float(row["y_m"]))
            motion = track_heading(float(row.get("vx_mps") or 0.0), float(row.get("vy_mps") or 0.0),
                                   float(row.get("vel_std_mps") or 0.0))
            if motion is not None:
                yaw, heading = wrap_deg(observer.yaw + frame_origin.yaw + motion - own.yaw), HEADING_FROM_VELOCITY
                held = yaw
            elif held is not None:
                yaw, heading = held, HEADING_HELD
            else:
                yaw, heading = observer.yaw, HEADING_UNKNOWN
            centre = position
            if row.get("longitudinal_m") is not None and row.get("lateral_m") is not None:
                lon, lat = float(row["longitudinal_m"]), float(row["lateral_m"])
                cx, cy = nominal_box_centre(lon, lat, float(row.get("surface_offset_m") or 0.0), yaw - observer.yaw,
                                            footprint, geometry.length, geometry.width)
                dx, dy = rotate(cx - lon, cy - lat, observer.yaw)
                centre = (position[0] + dx, position[1] + dy)
            samples.append(TrackPoint(round(source_time - run_start, 6), position, centre, yaw, heading,
                                      bool(row.get("measured", True)),
                                      None if row.get("clearance_m") is None else float(row["clearance_m"])))
        status, entity = (statuses or {}).get((recorder, track_id), (ANONYMOUS, None))
        tracks.append(TrackPath(recorder, track_id, samples, status, entity, geometry.max_gap,
                                (road_users or {}).get((recorder, track_id))))
    return tracks



@dataclass(frozen=True)
class EntityState:

    time: float
    centre: Tuple[float, float]
    yaw: Optional[float]
    heading: str
    speed: float
    pos_std: float
    method: str
    observers: Tuple[str, ...]
    measured: bool


@dataclass
class EntityPath:

    entity_id: str
    source_tracks: List[str]
    observers: List[str]
    length: float
    width: float
    states: List[EntityState]
    max_gap: float = 0.5
    times: List[float] = field(init=False, repr=False)
    identity_ambiguous: bool = False

    def __post_init__(self) -> None:
        self.states = sorted(self.states, key=lambda state: state.time)
        self.times = [state.time for state in self.states]

    @property
    def name(self) -> str:
        return self.entity_id

    @property
    def label(self) -> str:
        return "{0} / {1}".format(self.entity_id, ANONYMOUS)

    @property
    def sources(self) -> str:
        return " + ".join(self.source_tracks)

    @property
    def start(self) -> float:
        return self.times[0]

    @property
    def end(self) -> float:
        return self.times[-1]

    def state_at(self, t: float) -> Optional[EntityState]:
        if not self.states or t < self.times[0] - _EPS or t > self.times[-1] + _EPS:
            return None
        index = max(0, bisect_right(self.times, t + _EPS) - 1)
        a = self.states[index]
        if index == len(self.states) - 1 or t <= a.time + _EPS:
            return a
        b = self.states[index + 1]
        if b.time - a.time > self.max_gap + _EPS:
            return None
        f = (t - a.time) / (b.time - a.time)
        yaw = a.yaw
        if a.yaw is not None and b.yaw is not None:
            yaw = lerp_angle_deg(a.yaw, b.yaw, f)
        return EntityState(t, (lerp(a.centre[0], b.centre[0], f), lerp(a.centre[1], b.centre[1], f)), yaw,
                           a.heading, lerp(a.speed, b.speed, f), lerp(a.pos_std, b.pos_std, f), a.method,
                           a.observers, a.measured or b.measured)


def load_entities(path: Path, run_start: float, max_gap: float = 0.5) -> List[EntityPath]:
    if not Path(path).exists():
        return []
    entities = []
    for item in _read_json(path).get("entities", []):
        states = []
        for row in item.get("trajectory", []):
            heading = row.get("heading_source")
            states.append(EntityState(
                round(float(row["t_global"]) - run_start, 6), (float(row["x"]), float(row["y"])),
                None if row.get("heading_deg") is None else float(row["heading_deg"]),
                {"velocity": HEADING_FROM_VELOCITY, "held": HEADING_HELD}.get(heading, HEADING_UNKNOWN),
                math.hypot(float(row.get("vx") or 0.0), float(row.get("vy") or 0.0)), float(row.get("pos_std_m") or 0.0),
                str(row.get("method") or ""), tuple(row.get("observers") or ()), bool(row.get("measured_by"))))
        if states:
            footprint = item.get("footprint") or {}
            entities.append(EntityPath(str(item["id"]), [str(name) for name in item.get("source_tracks", [])],
                                       [str(name) for name in item.get("observers", [])],
                                       float(footprint.get("length_m") or 4.6), float(footprint.get("width_m") or 1.9),
                                       states, max_gap, identity_ambiguous=bool(item.get('identity_ambiguous', False))))
    return entities



MAP_MIN_FIT = 0.98
MAP_MARGIN = 0.05


def choose_map(fits: Mapping[str, float], networks: Mapping[str, str], current: Optional[str] = None) -> Optional[str]:
    if not fits:
        return None
    best = max(fits.values())
    if best < MAP_MIN_FIT:
        return None
    winners = {networks.get(name, name) for name, fit in fits.items() if fit >= best - 1e-9}
    if len(winners) > 1:
        return None
    network = winners.pop()
    if any(fit > best - MAP_MARGIN for name, fit in fits.items() if networks.get(name, name) != network):
        return None
    same = [name for name in fits if networks.get(name, name) == network]
    return sorted(same, key=lambda name: (name != current, name.endswith("_Opt"), len(name), name))[0]



GLOBAL_CLOCK = "t_global"
SOURCE_CLOCK = "source"


def recorder_clocks(run_dir: Path, ids: Sequence[str]) -> Tuple[str, Dict[str, float], Dict[str, float]]:
    rec = Path(run_dir) / "reconstruction"
    origins: Dict[str, float] = {}
    for pid in ids:
        graph = rec / pid / "local_graph.json"
        if graph.exists():
            origins[pid] = float(_read_json(graph)["recorder"]["clock"]["origin_source_timestamp"])
    offsets: Dict[str, float] = {}
    if (rec / "global" / "alignment.json").exists():
        for name, info in (_read_json(rec / "global" / "alignment.json").get("graphs") or {}).items():
            if info.get("status") == "ALIGNED" and info.get("offset_to_global") is not None:
                offsets[str(name)] = float(info["offset_to_global"])
    aligned = any(pid in origins and pid in offsets for pid in ids)
    return (GLOBAL_CLOCK if aligned else SOURCE_CLOCK), origins, offsets


def _pose_source_trajectory(source: Any, records: Sequence[Mapping[str, Any]], origin: float) -> Trajectory:
    times, poses, speeds = [], [], []
    for record in records:
        t = float(record["timestamp"])
        pose = source.pose_at(t - origin)
        times.append(t)
        poses.append(Pose(float(pose.x), float(pose.y), float(record["z"]), math.degrees(float(pose.yaw)),
                          float(record.get("pitch_deg", 0.0)), float(record.get("roll_deg", 0.0))))
        speeds.append(math.hypot(float(pose.vx), float(pose.vy)))
    return Trajectory(times, poses, speeds)


@dataclass
class Participant:

    participant_id: str
    blueprint: str
    blueprint_source: str
    trajectory: Trajectory
    frame_origin: Pose
    footprint: Optional[EgoFootprint] = None
    recorded: Optional[Trajectory] = None


@dataclass
class ReplayRun:
    run_dir: Path
    name: str
    participants: List[Participant]
    start: float
    duration: float
    local_events: Dict[str, LocalEvents] = field(default_factory=dict)
    entity_event_overrides: List[ReplayEvent] = field(default_factory=list)
    entity_source_nodes: set = field(default_factory=set)
    collisions: List[CollisionMark] = field(default_factory=list)
    clock: str = SOURCE_CLOCK
    clock_origins: Dict[str, float] = field(default_factory=dict)
    identities: Dict[Tuple[str, str], str] = field(default_factory=dict)
    tracks: Dict[str, List[TrackPath]] = field(default_factory=dict)
    perceived: Dict[str, PerceivedStates] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)
    geometry: GhostGeometry = field(default_factory=GhostGeometry)
    entities: List[EntityPath] = field(default_factory=list)
    road_users: Dict[Tuple[str, str], str] = field(default_factory=dict)
    hidden: List[str] = field(default_factory=list)
    recording_zero: float = 0.0

    @classmethod
    def load(cls, run_dir: Path, geometry: Optional[GhostGeometry] = None,
             pose_factory: Optional[Callable[[Path, float], Any]] = None) -> "ReplayRun":
        run_dir = Path(run_dir)
        notes: List[str] = []
        if pose_factory is None:
            from ..reconstruction.common_frame import TabulatedPoseSource
            pose_factory = TabulatedPoseSource.factory_for_run(run_dir)
            if pose_factory is not None:
                notes.append("recorders drawn at the poses the reconstruction used (global/recorder_poses.json)")
        vehicles_dir = run_dir / "vehicles"
        ids = sorted(p.name for p in vehicles_dir.iterdir()
                     if (p / "ego.jsonl").exists()) if vehicles_dir.is_dir() else []
        if not ids:
            raise ValueError("no vehicles/<id>/ego.jsonl under " + str(run_dir))

        clock, origins, offsets = recorder_clocks(run_dir, ids)
        hidden = []
        if clock == GLOBAL_CLOCK:
            hidden = [pid for pid in ids if pid not in offsets or pid not in origins]
            for pid in hidden:
                notes.append("{0} has no global clock (the reconstruction could not align it): not replayed".format(pid))
            ids = [pid for pid in ids if pid not in hidden]
        elif offsets:
            notes.append("no recorder is aligned: replay on the recorded source timestamps")
        participants = []
        for pid in ids:
            records = _read_jsonl(vehicles_dir / pid / "ego.jsonl")
            meta: Dict[str, Any] = {}
            try:
                meta = _read_json(vehicles_dir / pid / "metadata.json")
            except (OSError, ValueError):
                pass
            blueprint, source = meta.get("blueprint"), "recorded"
            if not blueprint:
                blueprint, source = FALLBACK_BLUEPRINT, "fallback"
                notes.append("{0}: no recorded blueprint; using {1}".format(pid, FALLBACK_BLUEPRINT))
            first = records[0]
            recorded = Trajectory.from_records(records)
            trajectory = recorded
            frame_origin = Pose(float(first["x"]), float(first["y"]), float(first["z"]), float(first["yaw_deg"]))
            if pose_factory is not None and pid in origins:
                trajectory = _pose_source_trajectory(pose_factory(vehicles_dir / pid, origins[pid]), records,
                                                     origins[pid])
                recorded, frame_origin = trajectory, trajectory.poses[0]
            if clock == GLOBAL_CLOCK:
                recorded = recorded.shifted(offsets[pid] - origins[pid])
                trajectory = trajectory.shifted(offsets[pid] - origins[pid])
            participants.append(Participant(pid, str(blueprint), source, trajectory, frame_origin,
                                            EgoFootprint.from_metadata(meta.get("ego_footprint")), recorded))
        start = min(p.trajectory.start for p in participants)
        end = max(p.trajectory.end for p in participants)
        run = cls(run_dir=run_dir, name="{0} / {1}".format(run_dir.parent.name, run_dir.name),
                  participants=participants, start=start, duration=round(end - start, 6), notes=notes,
                  geometry=geometry or GhostGeometry.from_config(load_config()), clock=clock,
                  clock_origins=({pid: offsets[pid] for pid in ids} if clock == GLOBAL_CLOCK else dict(origins)),
                  hidden=hidden,
                  recording_zero=(statistics.median(origins[pid] - offsets[pid] for pid in ids)
                                  if clock == GLOBAL_CLOCK and ids else 0.0))
        run._load_reconstruction()
        return run

    def _load_reconstruction(self) -> None:
        rec = self.run_dir / "reconstruction"
        statuses: Dict[Tuple[str, str], Tuple[str, Optional[str]]] = {}
        if (rec / "global" / "associations.json").exists():
            statuses = load_track_statuses(rec / "global" / "associations.json")
        self.identities = {key: entity for key, (status, entity) in statuses.items()
                           if status == ASSOCIATED and entity is not None}
        if self.clock == GLOBAL_CLOCK:
            self.entities = load_entities(rec / "global" / "anonymous_entities.json", self.start, self.geometry.max_gap)
            self.road_users = {(name.split(":", 1)[0], name.split(":", 1)[1]): entity.entity_id
                               for entity in self.entities for name in entity.source_tracks if ":" in name}
        for participant in self.participants:
            pid = participant.participant_id
            graph = rec / pid / "local_graph.json"
            if not graph.exists():
                self.notes.append("{0}: no local_graph.json; no events shown".format(pid))
                continue
            local = load_local_events(graph, self.start, self.clock_origins.get(pid))
            self.local_events[pid] = local
            origin = self.clock_origins.get(pid, local.origin)
            tracks = rec / pid / "local_tracks.jsonl"
            if tracks.exists():
                self.tracks[pid] = load_tracks(tracks, pid, participant.trajectory, participant.frame_origin,
                                               origin, self.start, participant.footprint, self.geometry, statuses,
                                               participant.recorded, self.road_users)
            trace = rec / pid / "local_trace.jsonl"
            perceived = load_perceived_states(trace, origin, self.start) if trace.exists() else None
            if perceived is not None:
                self.perceived[pid] = perceived
        origins = {pid: self.clock_origins.get(pid, local.origin) for pid, local in self.local_events.items()}
        if (rec / "global" / "global_graph.json").exists():
            self.collisions = load_collisions(rec / "global" / "global_graph.json", origins, self.start)
            recontacts = load_recontacts(rec / "global" / "global_graph.json")
            for pid, local in self.local_events.items():
                local.events = [replace(event, event_type="RECONTACT") if (pid, event.node_id) in recontacts else event
                                for event in local.events]
            if self.clock == GLOBAL_CLOCK:
                graph = _read_json(rec / 'global' / 'global_graph.json')
                self.entity_source_nodes.update((s['graph'], s['local_node'])
                                                for s in graph.get('suppressed_local_nodes', []))
                for node in graph['nodes']:
                    attrs = node.get('attributes') or {}
                    if attrs.get('aggregation') != 'entity_state_union' or node.get('t_global') is None:
                        continue
                    observers = {s['graph'] for s in attrs.get('source_local_nodes',[])}
                    if len(observers) != 1:
                        raise ValueError('An entity event must have one observing recorder')
                    actor = next(iter(observers))
                    if actor not in self.local_events:
                        continue
                    self.entity_event_overrides.append(ReplayEvent(node['t_global']-self.start,actor,
                        node['event_type'],node.get('subject_id'),node['node_id'],attrs))
                    self.entity_source_nodes.update((s['graph'],s['local_node'])
                                                    for s in attrs.get('source_local_nodes',[]))


    def display_time(self, t: float) -> float:
        return (round(t + self.start, 6) if self.clock == GLOBAL_CLOCK else round(t, 6)) + 0.0

    def recording_time(self, t: float) -> float:
        return self.start + t + (self.recording_zero if self.clock == GLOBAL_CLOCK else 0.0)

    def replay_time_of(self, t_recording: float) -> float:
        return t_recording - self.start - (self.recording_zero if self.clock == GLOBAL_CLOCK else 0.0)

    def participant(self, participant_id: str) -> Participant:
        return next(p for p in self.participants if p.participant_id == participant_id)

    def all_events(self) -> List[ReplayEvent]:
        return sorted((e for local in self.local_events.values() for e in local.events),
                      key=lambda e: (e.time, e.actor, e.node_id))

    def recent_events(self, actor: str, t: float, window: float) -> List[ReplayEvent]:
        local = self.local_events.get(actor)
        if local is None:
            return []
        return [e for e in self.display_events() if e.actor == actor and t - window < e.time <= t + _EPS]

    def display_events(self) -> List[ReplayEvent]:
        events = [e for e in self.all_events() if (e.actor,e.node_id) not in self.entity_source_nodes]
        return sorted(events+self.entity_event_overrides,key=lambda e:(e.time,e.actor,e.node_id))

    def active_states(self, actor: str, t: float) -> List[StateInterval]:
        local = self.local_events.get(actor)
        return [] if local is None else [item for item in local.intervals if item.active_at(t)]

    def perceived_lines(self, actor: str, t: float) -> Optional[List[str]]:
        perceived = self.perceived.get(actor)
        if perceived is None:
            return None
        return compact_state(perceived.state_at(t), lambda track: self.subject_name(actor, track))

    def collisions_near(self, t: float, window: float) -> List[CollisionMark]:
        return [mark for mark in self.collisions if t - window < mark.time <= t + _EPS]

    def event_times(self) -> List[float]:
        times = sorted({e.time for e in self.all_events()} | {m.time for m in self.collisions})
        return [t for t in times if 0.0 - _EPS <= t <= self.duration + _EPS]

    def next_event_time(self, t: float) -> Optional[float]:
        return next((x for x in self.event_times() if x > t + _EPS), None)

    def previous_event_time(self, t: float) -> Optional[float]:
        return next((x for x in reversed(self.event_times()) if x < t - _EPS), None)

    def subject_name(self, actor: str, subject: Optional[str]) -> str:
        if subject is None:
            return ""
        entity = self.identities.get((actor, subject)) or self.road_users.get((actor, subject))
        return subject if entity is None else "{0} ({1})".format(subject, entity)

    def all_tracks(self) -> List[TrackPath]:
        return [track for participant in self.participants for track in self.tracks.get(participant.participant_id, [])]

    def ghost_tracks(self) -> List[TrackPath]:
        return [track for track in self.all_tracks() if track.ghost]

    def entities_at(self, t: float) -> List[Tuple[EntityPath, EntityState]]:
        out = []
        for entity in self.entities:
            if entity.identity_ambiguous:
                continue
            state = entity.state_at(t)
            if state is not None:
                out.append((entity, state))
        return out

    def entity(self, entity_id: str) -> Optional[EntityPath]:
        return next((entity for entity in self.entities if entity.entity_id == entity_id), None)

    def anonymous_at(self, recorder: str, t: float) -> List[Tuple[TrackPath, TrackPoint]]:
        alive = []
        for track in self.tracks.get(recorder, []):
            state = track.state_at(t) if track.ghost else None
            if state is not None:
                alive.append((track, state))
        return alive

    def map_samples(self) -> List[Vector]:
        return [(pose.x, pose.y, pose.z) for participant in self.participants for pose in participant.trajectory.poses]



Vector = Tuple[float, float, float]


def rotation_axes(yaw: float, pitch: float, roll: float = 0.0) -> Tuple[Vector, Vector, Vector]:
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    cp, sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))
    cr, sr = math.cos(math.radians(roll)), math.sin(math.radians(roll))
    forward = (cp * cy, cp * sy, sp)
    right = (sr * sp * cy - cr * sy, sr * sp * sy + cr * cy, -sr * cp)
    up = (-(cr * sp * cy + sr * sy), cy * sr - cr * sp * sy, cr * cp)
    return forward, right, up


NEAR_PLANE_M = 0.1


def project(point: Vector, camera: Pose, fov_deg: float, width: int, height: int) -> Optional[Tuple[float, float]]:
    forward, right, up = rotation_axes(camera.yaw, camera.pitch, camera.roll)
    d = (point[0] - camera.x, point[1] - camera.y, point[2] - camera.z)
    depth = sum(a * b for a, b in zip(d, forward))
    if depth < NEAR_PLANE_M:
        return None
    focal = width / (2.0 * math.tan(math.radians(fov_deg) / 2.0))
    across = sum(a * b for a, b in zip(d, right))
    upward = sum(a * b for a, b in zip(d, up))
    return width / 2.0 + focal * across / depth, height / 2.0 - focal * upward / depth


def project_segment(a: Vector, b: Vector, camera: Pose, fov_deg: float, width: int,
                    height: int) -> Optional[Tuple[Tuple[float, float], Tuple[float, float]]]:
    forward, _, _ = rotation_axes(camera.yaw, camera.pitch, camera.roll)
    eye = (camera.x, camera.y, camera.z)
    da = sum((p - e) * f for p, e, f in zip(a, eye, forward))
    db = sum((p - e) * f for p, e, f in zip(b, eye, forward))
    near = NEAR_PLANE_M + 1e-3
    if da < near and db < near:
        return None
    if da < near or db < near:
        f = (near - da) / (db - da)
        cut = tuple(lerp(pa, pb, f) for pa, pb in zip(a, b))
        a, b = (cut, b) if da < near else (a, cut)
    pa, pb = project(a, camera, fov_deg, width, height), project(b, camera, fov_deg, width, height)
    return None if pa is None or pb is None else (pa, pb)


BOX_EDGES = ((0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7))


def box_corners(centre: Tuple[float, float], yaw: float, length: float, width: float, z: float,
                height: float) -> List[Vector]:
    base = []
    for ox, oy in ((length / 2.0, -width / 2.0), (length / 2.0, width / 2.0),
                   (-length / 2.0, width / 2.0), (-length / 2.0, -width / 2.0)):
        dx, dy = rotate(ox, oy, yaw)
        base.append((centre[0] + dx, centre[1] + dy))
    return [(x, y, z) for x, y in base] + [(x, y, z + height) for x, y in base]


def look_at(eye: Vector, target: Vector) -> Tuple[float, float]:
    dx, dy, dz = target[0] - eye[0], target[1] - eye[1], target[2] - eye[2]
    return math.degrees(math.atan2(dy, dx)), math.degrees(math.atan2(dz, math.hypot(dx, dy)))


def overview_camera(points: Sequence[Vector], heading: float, zoom: float = 1.0, elevation: float = 30.0) -> Pose:
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)
    cz = sum(p[2] for p in points) / len(points)
    spread = max(math.hypot(p[0] - cx, p[1] - cy) for p in points)
    distance = zoom * max(20.0, 2.2 * spread + 10.0)
    back, rise = distance * math.cos(math.radians(elevation)), distance * math.sin(math.radians(elevation))
    eye = (cx - back * math.cos(math.radians(heading)), cy - back * math.sin(math.radians(heading)), cz + rise)
    yaw, pitch = look_at(eye, (cx, cy, cz))
    return Pose(eye[0], eye[1], eye[2], yaw, pitch, 0.0)


def follow_camera(vehicle: Pose, orbit: float = 0.0, distance: float = 9.0, height: float = 3.5) -> Pose:
    yaw = math.radians(vehicle.yaw + orbit)
    eye = (vehicle.x - distance * math.cos(yaw), vehicle.y - distance * math.sin(yaw), vehicle.z + height)
    ahead = math.radians(vehicle.yaw)
    target = (vehicle.x + 3.0 * math.cos(ahead), vehicle.y + 3.0 * math.sin(ahead), vehicle.z + 1.0)
    cam_yaw, cam_pitch = look_at(eye, target)
    return Pose(eye[0], eye[1], eye[2], cam_yaw, cam_pitch, 0.0)


class FreeCamera:

    def __init__(self, pose: Pose):
        self.x, self.y, self.z, self.yaw, self.pitch = pose.x, pose.y, pose.z, pose.yaw, pose.pitch

    def move(self, forward: float, right: float, up: float) -> None:
        cy, sy = math.cos(math.radians(self.yaw)), math.sin(math.radians(self.yaw))
        self.x += forward * cy - right * sy
        self.y += forward * sy + right * cy
        self.z += up

    def turn(self, d_yaw: float, d_pitch: float) -> None:
        self.yaw = (self.yaw + d_yaw + 180.0) % 360.0 - 180.0
        self.pitch = max(-89.0, min(89.0, self.pitch + d_pitch))

    @property
    def pose(self) -> Pose:
        return Pose(self.x, self.y, self.z, self.yaw, self.pitch, 0.0)
