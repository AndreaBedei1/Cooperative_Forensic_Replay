"""Driving lanes of a public OpenDRIVE file without the carla module (pure Python).

Map geometry shared by the reconstruction (road-relative cut-in, ``reconstruction.road``) and the replay,
which draws the road from it.  ``carla.Map.generate_waypoints`` does
that when the CARLA client library is importable; this module samples the same geometry directly from the
.xodr text so the headless export works on any Python: plan-view reference line (``line`` and ``arc``
records), ``laneOffset`` and lane ``width`` cubics, ``driving`` lanes of every lane section.  Output in the
CARLA world frame (OpenDRIVE y and heading negated), as ``LaneSample``.  ``spiral``, ``poly3`` and
``paramPoly3`` records are not implemented: a road using them is skipped (the maps of this campaign, Town05
and Town03, use only lines and arcs).  Map geometry only: no run, scenario or ground-truth data.
"""

from __future__ import annotations

import math
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from dataclasses import dataclass


@dataclass(frozen=True)
class LaneSample:
    """One stretch of a driving lane: centre, heading [deg], width and length [m] (world frame)."""

    x: float
    y: float
    yaw: float
    width: float
    length: float


def _cubic(records: Sequence[Tuple[float, float, float, float, float]], ds: float) -> float:
    """Value of the record (start, a, b, c, d) in force at ``ds``: a + b u + c u^2 + d u^3, u = ds - start."""
    current = records[0]
    for record in records:
        if record[0] <= ds + 1e-9:
            current = record
    u = ds - current[0]
    return current[1] + current[2] * u + current[3] * u * u + current[4] * u * u * u


def _poly(element: ET.Element, start: str) -> Tuple[float, float, float, float, float]:
    return (float(element.get(start, 0.0)), float(element.get("a", 0.0)), float(element.get("b", 0.0)),
            float(element.get("c", 0.0)), float(element.get("d", 0.0)))


class _ReferenceLine:
    def __init__(self, plan_view: ET.Element):
        self.segments = []
        for geometry in plan_view.findall("geometry"):
            child = list(geometry)[0] if len(geometry) else None
            if child is None or child.tag not in ("line", "arc"):
                raise NotImplementedError(child.tag if child is not None else "empty geometry")
            curvature = float(child.get("curvature", 0.0)) if child.tag == "arc" else 0.0
            self.segments.append((float(geometry.get("s")), float(geometry.get("x")), float(geometry.get("y")),
                                  float(geometry.get("hdg")), float(geometry.get("length")), curvature))

    def at(self, s: float) -> Tuple[float, float, float]:
        """(x, y, heading) of the reference line at ``s`` (OpenDRIVE frame)."""
        seg = self.segments[0]
        for candidate in self.segments:
            if candidate[0] <= s + 1e-9:
                seg = candidate
        s0, x0, y0, hdg, length, k = seg
        ds = min(max(s - s0, 0.0), length)
        if abs(k) < 1e-12:
            return x0 + ds * math.cos(hdg), y0 + ds * math.sin(hdg), hdg
        return (x0 + (math.sin(hdg + k * ds) - math.sin(hdg)) / k,
                y0 + (math.cos(hdg) - math.cos(hdg + k * ds)) / k, hdg + k * ds)


def lanes_from_opendrive(text: str, spacing: float = 2.0) -> List[LaneSample]:
    """Driving-lane stretches (centre, yaw [deg], width, length) every ``spacing`` metres, CARLA world frame."""
    root = ET.fromstring(text)
    lanes: List[LaneSample] = []
    for road in root.findall("road"):
        try:
            line = _ReferenceLine(road.find("planView"))
        except NotImplementedError:
            continue
        length = float(road.get("length"))
        lanes_el = road.find("lanes")
        offsets = [_poly(e, "s") for e in lanes_el.findall("laneOffset")] or [(0.0, 0.0, 0.0, 0.0, 0.0)]
        sections = lanes_el.findall("laneSection")
        starts = [float(sec.get("s")) for sec in sections] + [length]
        for index, section in enumerate(sections):
            s_start, s_end = starts[index], starts[index + 1]
            sides = []
            for side, sign in (("left", 1.0), ("right", -1.0)):
                group = section.find(side)
                if group is None:
                    continue
                ordered = sorted(group.findall("lane"), key=lambda lane: abs(int(lane.get("id"))))
                sides.append((sign, [(lane.get("type"), [_poly(w, "sOffset") for w in lane.findall("width")])
                                     for lane in ordered]))
            n = max(int(math.floor((s_end - s_start) / spacing)), 1)
            for k in range(n):
                s = s_start + (k + 0.5) * (s_end - s_start) / n
                x, y, hdg = line.at(s)
                t0 = _cubic(offsets, s)
                nx, ny = -math.sin(hdg), math.cos(hdg)
                for sign, group in sides:
                    inner = 0.0
                    for lane_type, widths in group:
                        width = _cubic(widths, s - s_start) if widths else 0.0
                        if lane_type == "driving" and width > 0.5:
                            t = t0 + sign * (inner + width / 2.0)
                            cx, cy = x + t * nx, y + t * ny
                            lanes.append(LaneSample(cx, -cy, -math.degrees(hdg), width,
                                                    (s_end - s_start) / n * 1.2))
                        inner += width
    return lanes


@dataclass(frozen=True)
class LanePiece:
    """One driving lane of one lane section of one road, as a polyline in its direction of travel (CARLA world
    frame): centre points every ~``spacing`` metres including both ends, the travel heading [rad] and the lane
    width at each point.  ``key`` = (road id, section index, lane id); ``junction``: the road's junction id (-1:
    not in a junction)."""

    key: Tuple[str, int, int]
    points: Tuple[Tuple[float, float], ...]
    headings: Tuple[float, ...]
    widths: Tuple[float, ...]
    junction: str


def lane_pieces_from_opendrive(text: str, spacing: float = 1.0) -> List[LanePiece]:
    """Every driving lane of every lane section as a ``LanePiece``.  Right lanes (negative ids) run along the
    reference line, left lanes against it (right-hand traffic; a road with rule="LHT" the other way).  Points at
    both section ends, so pieces that connect share their end points."""
    root = ET.fromstring(text)
    pieces: List[LanePiece] = []
    for road in root.findall("road"):
        try:
            line = _ReferenceLine(road.find("planView"))
        except NotImplementedError:
            continue
        length = float(road.get("length"))
        left_hand = (road.get("rule") or "RHT").upper() == "LHT"
        lanes_el = road.find("lanes")
        offsets = [_poly(e, "s") for e in lanes_el.findall("laneOffset")] or [(0.0, 0.0, 0.0, 0.0, 0.0)]
        sections = lanes_el.findall("laneSection")
        starts = [float(sec.get("s")) for sec in sections] + [length]
        for index, section in enumerate(sections):
            s_start, s_end = starts[index], starts[index + 1]
            if s_end - s_start < 1e-3:
                continue
            n = max(int(math.ceil((s_end - s_start) / spacing)), 1)
            samples = [s_start + k * (s_end - s_start) / n for k in range(n + 1)]
            for side, sign in (("left", 1.0), ("right", -1.0)):
                group = section.find(side)
                if group is None:
                    continue
                ordered = sorted(group.findall("lane"), key=lambda lane: abs(int(lane.get("id"))))
                widths_of = [(int(lane.get("id")), lane.get("type"), [_poly(w, "sOffset") for w in lane.findall("width")])
                             for lane in ordered]
                for position, (lane_id, lane_type, widths) in enumerate(widths_of):
                    if lane_type != "driving" or not widths:
                        continue
                    pts, heads, wids = [], [], []
                    for s in samples:
                        x, y, hdg = line.at(s)
                        t0 = _cubic(offsets, s)
                        inner = sum(_cubic(w, s - s_start) for _, _, w in widths_of[:position] if w)
                        width = _cubic(widths, s - s_start)
                        t = t0 + sign * (inner + width / 2.0)
                        nx, ny = -math.sin(hdg), math.cos(hdg)
                        # CARLA world frame: OpenDRIVE y and headings negated.
                        pts.append((x + t * nx, -(y + t * ny)))
                        heads.append(-hdg)
                        wids.append(max(width, 0.0))
                    if max(wids) <= 0.5:
                        continue
                    along_reference = (lane_id < 0) != left_hand
                    if not along_reference:
                        pts, wids = pts[::-1], wids[::-1]
                        heads = [h + math.pi for h in heads[::-1]]
                    heads = [math.atan2(math.sin(h), math.cos(h)) for h in heads]
                    pieces.append(LanePiece((road.get("id"), index, lane_id), tuple(pts), tuple(heads), tuple(wids),
                                            road.get("junction") or "-1"))
    return pieces


def lane_share(lanes: Sequence[LaneSample], points: Sequence[Tuple[float, float]]) -> float:
    """Share of the points inside some driving-lane stretch (within half its width across, half its length along)."""
    if not lanes or not points:
        return 0.0
    from scipy.spatial import cKDTree
    centres = np.array([(lane.x, lane.y) for lane in lanes])
    tree = cKDTree(centres)
    inside = 0
    for px, py in points:
        for i in tree.query_ball_point((px, py), 4.0):
            lane = lanes[i]
            yaw = math.radians(lane.yaw)
            dx, dy = px - lane.x, py - lane.y
            along, across = dx * math.cos(yaw) + dy * math.sin(yaw), -dx * math.sin(yaw) + dy * math.cos(yaw)
            if abs(along) <= lane.length / 2.0 and abs(across) <= lane.width / 2.0:
                inside += 1
                break
    return inside / len(points)


_CACHE: Dict[str, List[LaneSample]] = {}


def best_map(sources: Dict[str, str], points: Sequence[Tuple[float, float]],
             min_fit: float = 0.8) -> Tuple[Optional[str], Optional[List[LaneSample]]]:
    """The map whose driving lanes contain the largest share of the recorded positions (at least ``min_fit``)."""
    best: Tuple[float, Optional[str]] = (0.0, None)
    for name in sorted(sources):
        if name not in _CACHE:
            _CACHE[name] = lanes_from_opendrive(sources[name])
        share = lane_share(_CACHE[name], points)
        if share > best[0] + 1e-9:
            best = (share, name)
    if best[1] is None or best[0] < min_fit:
        return None, None
    return best[1], _CACHE[best[1]]
