"""Ground-truth radar coverage of a recorder (privileged: evaluation only).

Whether another vehicle lay within the field of view and range of one of a recorder's radars, with a clear
line of sight, at one simulator frame: true poses and boxes (``ground_truth/states.jsonl``) and the radars'
own mounts and fields of view (``vehicles/<id>/radar/<sensor>/metadata.json``).  Used by the radar
visibility audit (``scripts/audit_radar_visibility.py``) and the event oracle (``cdf.evaluation.event_oracle``);
``cdf.reconstruction`` never imports it.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

import numpy as np

from ..replay.model import rotation_axes


def rotation(yaw: float, pitch: float, roll: float) -> np.ndarray:
    """Columns: world-frame forward, right, up of a CARLA rotation (degrees)."""
    forward, right, up = rotation_axes(yaw, pitch, roll)
    return np.array([forward, right, up]).T


class Box:
    """A vehicle's oriented bounding box (centre at the body's mid height)."""

    def __init__(self, state: Mapping[str, Any]):
        tf, ext = state["transform"], state["bbox_extent"]
        self.rot = rotation(tf["yaw_deg"], tf["pitch_deg"], tf["roll_deg"])
        self.extent = np.array([ext["x"], ext["y"], ext["z"]])
        self.centre = np.array([tf["x"], tf["y"], tf["z"]]) + self.rot @ np.array([0.0, 0.0, ext["z"]])

    def local(self, points: np.ndarray) -> np.ndarray:
        return (points - self.centre) @ self.rot

    def contains(self, points: np.ndarray, margin: float) -> np.ndarray:
        return np.all(np.abs(self.local(points)) <= self.extent + margin, axis=1)

    def distance_2d(self, points: np.ndarray) -> np.ndarray:
        local = self.local(points)[:, :2]
        outside = np.maximum(np.abs(local) - self.extent[:2], 0.0)
        return np.hypot(outside[:, 0], outside[:, 1])

    def surface_points(self) -> np.ndarray:
        steps = [-1.0, 0.0, 1.0]
        grid = np.array([[a, b, c] for a in steps for b in steps for c in steps if (a, b, c) != (0.0, 0.0, 0.0)])
        return self.centre + (grid * self.extent) @ self.rot.T

    def blocks(self, start: np.ndarray, end: np.ndarray) -> bool:
        """Does the horizontal segment start-end pass through this box (2-D)?"""
        a, b = self.local(start[None])[0][:2], self.local(end[None])[0][:2]
        t0, t1 = 0.0, 1.0
        d = b - a
        for axis in (0, 1):
            if abs(d[axis]) < 1e-9:
                if abs(a[axis]) > self.extent[axis]:
                    return False
                continue
            lo = (-self.extent[axis] - a[axis]) / d[axis]
            hi = (self.extent[axis] - a[axis]) / d[axis]
            lo, hi = min(lo, hi), max(lo, hi)
            t0, t1 = max(t0, lo), min(t1, hi)
            if t0 > t1:
                return False
        return t1 > 0.02 and t0 < 0.98


@dataclass
class RadarView:
    """One radar of a recorder: mount (vehicle frame) and field of view, from its own metadata."""

    sensor_id: str
    position: np.ndarray  # x forward, y right, z up (m)
    rotation: np.ndarray
    half_horizontal: float  # rad
    half_vertical: float  # rad
    range_m: float

    @classmethod
    def from_metadata(cls, meta: Mapping[str, Any]) -> "RadarView":
        mount = meta.get("sensor_transform") or {}
        return cls(str(meta.get("sensor_id", "radar")),
                   np.array([mount.get("x", 0.0), mount.get("y", 0.0), mount.get("z", 0.6)]),
                   rotation(mount.get("yaw_deg", 0.0), mount.get("pitch_deg", 0.0), 0.0),
                   math.radians(float(meta.get("horizontal_fov_deg", 150.0))) / 2.0,
                   math.radians(float(meta.get("vertical_fov_deg", 20.0))) / 2.0,
                   float(meta.get("range_m", 90.0)))


@dataclass
class Coverage:
    in_range: bool  # part of the body within some radar's range
    inside_fov: bool  # part of the body within some radar's field of view and range
    occluded: bool  # inside a field of view, but every such line of sight crosses another vehicle's box
    radar: Optional[str]  # the radar seeing most of the body

    @property
    def visible(self) -> bool:
        return self.inside_fov and not self.occluded


def coverage(own: Mapping[str, Any], target: str, world: Mapping[str, Mapping[str, Any]],
             radars: Sequence[RadarView], boxes: Optional[Mapping[str, Box]] = None,
             partial: bool = True) -> Coverage:
    """The coverage of ``target`` by the radars of the vehicle in state ``own`` at one frame (``world``:
    participant -> state at that frame).  ``partial``: the body is seen when one of its surface points inside
    a field of view has a clear line of sight (a radar sees part of a body past another); otherwise only the
    line of sight to its centre counts (the visibility audit's simpler rule)."""
    boxes = boxes if boxes is not None else {pid: Box(state) for pid, state in world.items()}
    owner = own["participant_id"]
    tf = own["transform"]
    own_rot = rotation(tf["yaw_deg"], tf["pitch_deg"], tf["roll_deg"])
    own_pos = np.array([tf["x"], tf["y"], tf["z"]])
    box = boxes[target]
    in_range_any, inside_any, occluded_all, best = False, False, True, None
    for radar in radars:
        sensor = own_pos + own_rot @ radar.position
        local = (box.surface_points() - sensor) @ (own_rot @ radar.rotation)
        dist = np.linalg.norm(local, axis=1)
        az = np.arctan2(local[:, 1], local[:, 0])
        el = np.arctan2(local[:, 2], np.hypot(local[:, 0], local[:, 1]))
        in_range = dist <= radar.range_m
        inside = in_range & (np.abs(az) <= radar.half_horizontal) & (np.abs(el) <= radar.half_vertical)
        in_range_any |= bool(in_range.any())
        if not inside.any():
            continue
        inside_any = True
        others = [other for pid, other in boxes.items() if pid not in (owner, target)]
        targets = box.surface_points()[inside] if partial else box.centre[None]
        blocked = all(any(other.blocks(sensor, point) for other in others) for point in targets)
        occluded_all &= blocked
        share = float(inside.mean())
        if not blocked and (best is None or share > best[0]):
            best = (share, radar.sensor_id)
    return Coverage(in_range_any, inside_any, inside_any and occluded_all, None if best is None else best[1])


def frames_by_participant(states: Iterable[Mapping[str, Any]]) -> Dict[int, Dict[str, Mapping[str, Any]]]:
    out: Dict[int, Dict[str, Mapping[str, Any]]] = {}
    for state in states:
        out.setdefault(int(state["frame"]), {})[state["participant_id"]] = state
    return out


def radar_views(vehicle_dir: Any) -> List[Any]:
    """(RadarView, observations) of every radar of a recorder (its own files)."""
    from ..recording.compact_observations import load_radar_observations
    return [(RadarView.from_metadata(obs.metadata), obs) for obs in load_radar_observations(vehicle_dir)]
