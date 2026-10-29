"""A common coordinate frame for the recorders' observations (reconstruction side, no ground truth).

Every recorder logs its own pose stream (``ego.jsonl``: position and heading in the map frame, the
recorded GNSS/INS pose; in the CARLA campaign it is exact, the robustness study perturbs it).  A
``PoseSource`` gives a recorder's pose at an instant of its own clock.  A radar track sample is measured
relative to the recorder's body (vehicle frame: longitudinal, lateral); it is placed in the common frame
by composing that relative measurement with the recorder's pose at the same instant -- never through
another recorder, the scenario or ground truth.  Times are put on the global clock with the recorder's
``offset_to_global`` (``reconstruction/global/alignment.json``).

What each sample carries (``CommonSample``): the track point (median of its returns), the observed near
surface (the point moved back towards the recorder by its depth, as the CRITICAL_TTC model does), the
ground velocity, its uncertainty, the line of sight from the recorder's body, and -- in memory only -- the
radar returns the track claimed in that sweep, each with the position of the radar that produced it.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np

from .tracking import EgoFootprint, EgoTrajectory, LocalTrack

DEFAULT_BODY = EgoFootprint(-2.3, 2.3, -0.95, 0.95)
HEADING_MIN_SPEED_MPS = 1.0  # below this a target's motion fixes no heading (conflict.HEADING_MIN_SPEED_MPS)


@dataclass(frozen=True)
class WorldPose:
    """A recorder's pose in the common (map) frame: metres, radians, metres per second."""

    x: float
    y: float
    yaw: float
    vx: float = 0.0
    vy: float = 0.0

    def to_world(self, longitudinal: float, lateral: float) -> np.ndarray:
        c, s = math.cos(self.yaw), math.sin(self.yaw)
        return np.array([self.x + c * longitudinal - s * lateral, self.y + s * longitudinal + c * lateral])

    def to_vehicle(self, point: Sequence[float]) -> Tuple[float, float]:
        dx, dy = float(point[0]) - self.x, float(point[1]) - self.y
        c, s = math.cos(self.yaw), math.sin(self.yaw)
        return c * dx + s * dy, -s * dx + c * dy


class PoseSource:
    """Where a recorder was, by its own clock (t_local).  Subclasses: the recorded stream, a perturbed one.

    ``position_std_m`` (per axis) and ``yaw_std_rad`` are the accuracy the source declares, as a GNSS/INS
    receiver reports its own estimate: the association gates widen with them.  0 for an exact stream.
    ``velocity_std_mps`` likewise for the recorded velocity."""

    name = "abstract"
    position_std_m = 0.0
    yaw_std_rad = 0.0
    velocity_std_mps = 0.0

    def pose_at(self, t_local: float) -> WorldPose:  # pragma: no cover - interface
        raise NotImplementedError

    def poses_at(self, times: Sequence[float]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """(x, y, yaw) arrays at many instants of the recorder's clock (default: one by one)."""
        poses = [self.pose_at(float(t)) for t in times]
        return (np.array([p.x for p in poses]), np.array([p.y for p in poses]), np.array([p.yaw for p in poses]))

    @property
    def start(self) -> float:  # pragma: no cover - interface
        raise NotImplementedError

    @property
    def end(self) -> float:  # pragma: no cover - interface
        raise NotImplementedError


class RecordedPoseSource(PoseSource):
    """The recorder's own recorded pose stream (``ego.jsonl``), interpolated linearly (heading unwrapped).

    Baseline of the campaign: CARLA writes the exact pose, so this is an ideal GNSS/INS; the robustness
    study replaces it with a perturbed source (``PerturbedPoseSource``)."""

    name = "recorded"

    def __init__(self, records: Sequence[Mapping[str, Any]], clock_origin: float) -> None:
        rows = sorted(records, key=lambda record: float(record["timestamp"]))
        self.times = np.array([float(r["timestamp"]) - clock_origin for r in rows])
        self.x = np.array([float(r["x"]) for r in rows])
        self.y = np.array([float(r["y"]) for r in rows])
        self.yaw = np.unwrap(np.radians([float(r["yaw_deg"]) for r in rows]))
        velocity = [r.get("velocity") or {} for r in rows]
        self.vx = np.array([float(v.get("x", 0.0)) for v in velocity])
        self.vy = np.array([float(v.get("y", 0.0)) for v in velocity])

    @classmethod
    def from_vehicle_dir(cls, vehicle_dir: Path, clock_origin: float) -> "RecordedPoseSource":
        path = Path(vehicle_dir) / "ego.jsonl"
        with path.open(encoding="utf-8") as handle:
            records = [json.loads(line) for line in handle if line.strip()]
        return cls(records, clock_origin)

    @property
    def start(self) -> float:
        return float(self.times[0])

    @property
    def end(self) -> float:
        return float(self.times[-1])

    def pose_at(self, t_local: float) -> WorldPose:
        t = min(max(t_local, self.times[0]), self.times[-1])
        return WorldPose(float(np.interp(t, self.times, self.x)), float(np.interp(t, self.times, self.y)),
                         float(np.interp(t, self.times, self.yaw)), float(np.interp(t, self.times, self.vx)),
                         float(np.interp(t, self.times, self.vy)))

    def poses_at(self, times: Sequence[float]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        t = np.clip(np.asarray(times, dtype=float), self.times[0], self.times[-1])
        return np.interp(t, self.times, self.x), np.interp(t, self.times, self.y), np.interp(t, self.times, self.yaw)


# The poses the reconstruction placed the recorders at, written to ``global/RECORDER_POSES_FILE`` when they are not
# the recorded stream itself (a perturbed GNSS/INS, a mutual refinement): the RECONSTRUCTION viewer draws them.
RECORDER_POSES_FILE = "recorder_poses.json"


def is_recorded_stream(source: PoseSource) -> bool:
    """True for the recorder's own recorded stream, unchanged (G0: ``ego.jsonl`` is the pose used)."""
    return type(source) is RecordedPoseSource


def recorder_pose_record(poses: Mapping[str, PoseSource], origins: Mapping[str, float],
                         times: Mapping[str, Sequence[float]]) -> Dict[str, Any]:
    """The content of ``RECORDER_POSES_FILE``: each recorder's pose source sampled at its own record instants
    ``t_local`` (seconds after ``clock_origin``, its first record)."""
    recorders = {}
    for name in sorted(poses):
        source, t = poses[name], [float(v) for v in times[name]]
        samples = [source.pose_at(v) for v in t]
        recorders[name] = {"source": getattr(source, "name", type(source).__name__),
                           "declared_position_std_m": getattr(source, "position_std_m", 0.0),
                           "clock_origin": float(origins[name]), "t_local": t,
                           "x": [p.x for p in samples], "y": [p.y for p in samples],
                           "yaw_rad": [p.yaw for p in samples], "vx": [p.vx for p in samples],
                           "vy": [p.vy for p in samples]}
    return {"definition": "the pose of each recorder that the reconstruction used (map frame of the pose streams, "
                          "after any perturbation of the GNSS/INS and any mutual refinement), at its own record "
                          "instants; absent when that pose is the recorded stream itself (G0)",
            "recorders": recorders}


class TabulatedPoseSource(PoseSource):
    """A recorder's poses as written to ``RECORDER_POSES_FILE``, interpolated linearly."""

    def __init__(self, entry: Mapping[str, Any], clock_origin: float) -> None:
        self.name = str(entry.get("source", "tabulated"))
        self.position_std_m = float(entry.get("declared_position_std_m", 0.0))
        self.times = np.array(entry["t_local"], dtype=float) + (float(entry["clock_origin"]) - clock_origin)
        self.x, self.y = np.array(entry["x"], dtype=float), np.array(entry["y"], dtype=float)
        self.yaw = np.unwrap(np.array(entry["yaw_rad"], dtype=float))
        self.vx, self.vy = np.array(entry["vx"], dtype=float), np.array(entry["vy"], dtype=float)

    @classmethod
    def factory_for_run(cls, run_dir: Path) -> Optional[Any]:
        """A ``pose_factory(vehicle_dir, clock_origin)`` reading the run's ``RECORDER_POSES_FILE``, or None
        when the reconstruction used the recorded streams."""
        path = Path(run_dir) / "reconstruction" / "global" / RECORDER_POSES_FILE
        if not path.exists():
            return None
        recorders = json.loads(path.read_text(encoding="utf-8"))["recorders"]

        def make(vehicle_dir: Path, clock_origin: float) -> PoseSource:
            name = Path(vehicle_dir).name
            if name not in recorders:
                return RecordedPoseSource.from_vehicle_dir(vehicle_dir, clock_origin)
            return cls(recorders[name], clock_origin)
        return make

    @property
    def start(self) -> float:
        return float(self.times[0])

    @property
    def end(self) -> float:
        return float(self.times[-1])

    def pose_at(self, t_local: float) -> WorldPose:
        t = min(max(t_local, self.times[0]), self.times[-1])
        return WorldPose(float(np.interp(t, self.times, self.x)), float(np.interp(t, self.times, self.y)),
                         float(np.interp(t, self.times, self.yaw)), float(np.interp(t, self.times, self.vx)),
                         float(np.interp(t, self.times, self.vy)))


@dataclass
class CommonSample:
    """One radar track sample in the common frame (see the module docstring)."""

    t_local: float
    t_global: float
    point: np.ndarray  # track point (median of its returns)
    near: np.ndarray  # observed near surface
    velocity: np.ndarray  # ground velocity
    pos_std: float
    vel_std: float
    observer: np.ndarray  # the recorder's body point nearest the target (line-of-sight origin)
    measured: bool
    heading: Optional[float] = None  # direction of motion [rad] when the speed fixes it
    # Variance (m^2 per axis) the observer's own pose adds to the sample: the pose source's declared
    # position accuracy and its heading accuracy times the range.
    pose_var: float = 0.0
    returns: Optional[np.ndarray] = field(default=None, repr=False)  # (N, 2) claimed returns, common frame
    origins: Optional[np.ndarray] = field(default=None, repr=False)  # (N, 2) their radars' positions

    @property
    def speed(self) -> float:
        return float(np.hypot(*self.velocity))

    @property
    def line_of_sight(self) -> np.ndarray:
        line = self.near - self.observer
        return line / max(float(np.hypot(*line)), 1e-6)


@dataclass
class CommonTrack:
    """A recorder's radar track in the common frame, on the global clock."""

    recorder: str
    track_id: str
    samples: List[CommonSample]
    status: str = "ANONYMOUS"  # as the collision-based association left it
    entity: Optional[str] = None  # the recorder it was associated with, if any
    identity_ambiguous: bool = False
    parent_track: Optional[str] = None
    # The observer's own first collision (global time): from then on its ego-motion compensation, hence its
    # tracks' velocity estimates, are corrupted by the impulse.  None: no collision of its own.
    own_impact: Optional[float] = None

    @property
    def name(self) -> str:
        return "{0}:{1}".format(self.recorder, self.track_id)

    @property
    def start(self) -> float:
        return self.samples[0].t_global

    @property
    def end(self) -> float:
        return self.samples[-1].t_global

    def at(self, t_global: float, tolerance: float = 0.026) -> Optional[CommonSample]:
        times = np.array([s.t_global for s in self.samples])
        index = int(np.argmin(np.abs(times - t_global)))
        return self.samples[index] if abs(times[index] - t_global) <= tolerance else None

    def state_at(self, t_global: float, tolerance: float = 0.026) -> Optional[CommonSample]:
        """The nearest sample within ``tolerance``, moved to ``t_global`` at its own velocity: two recorders'
        radars need not sample at the same instants."""
        sample = self.at(t_global, tolerance)
        return None if sample is None else shifted(sample, t_global)


def shifted(sample: CommonSample, t_global: float) -> CommonSample:
    """A sample carried to a nearby instant at the target's own velocity (its observer point and the radar
    positions stay: they only orient the lines of sight)."""
    dt = t_global - sample.t_global
    if abs(dt) < 1e-9:
        return sample
    move = sample.velocity * dt
    return replace(sample, t_global=t_global, point=sample.point + move, near=sample.near + move,
                   returns=None if sample.returns is None else sample.returns + move)


@dataclass
class RecorderBody:
    """A recorder's own body in the common frame: its pose source, footprint and clock offset."""

    recorder: str
    poses: PoseSource
    footprint: Optional[EgoFootprint]
    offset_to_global: float
    # The recorder's own collision reports (its collision sensor, first callback): (t_global, the other
    # recorders of the matched contact; empty when no other recorder reported it).
    contacts: Tuple[Tuple[float, Tuple[str, ...]], ...] = ()

    def pose_at_global(self, t_global: float) -> WorldPose:
        return self.poses.pose_at(t_global - self.offset_to_global)

    def covers(self, t_global: float) -> bool:
        t_local = t_global - self.offset_to_global
        return self.poses.start - 1e-6 <= t_local <= self.poses.end + 1e-6

    def polygon(self, t_global: float) -> np.ndarray:
        """(4, 2) corners of the recorder's footprint in the common frame."""
        pose, fp = self.pose_at_global(t_global), self.footprint or DEFAULT_BODY
        return np.array([pose.to_world(x, y) for x, y in ((fp.x_max, fp.y_min), (fp.x_max, fp.y_max),
                                                           (fp.x_min, fp.y_max), (fp.x_min, fp.y_min))])

    def distance(self, t_global: float, point: Sequence[float]) -> float:
        """Distance from a point to the recorder's footprint (0 inside)."""
        pose, fp = self.pose_at_global(t_global), self.footprint or DEFAULT_BODY
        x, y = pose.to_vehicle(point)
        return float(math.hypot(max(fp.x_min - x, 0.0, x - fp.x_max), max(fp.y_min - y, 0.0, y - fp.y_max)))

    def outline_distance(self, t_global: float, point: Sequence[float]) -> float:
        """Distance from a point to the recorder's footprint outline: an observed near surface lies on it,
        so a point inside the body is as far from it as from the nearest edge."""
        pose, fp = self.pose_at_global(t_global), self.footprint or DEFAULT_BODY
        x, y = pose.to_vehicle(point)
        if fp.x_min <= x <= fp.x_max and fp.y_min <= y <= fp.y_max:
            return float(min(x - fp.x_min, fp.x_max - x, y - fp.y_min, fp.y_max - y))
        return float(math.hypot(max(fp.x_min - x, 0.0, x - fp.x_max), max(fp.y_min - y, 0.0, y - fp.y_max)))


def _outline_points(pose: WorldPose, footprint: EgoFootprint, step: float = 0.05) -> np.ndarray:
    xs = np.arange(footprint.x_min, footprint.x_max + 1e-9, step)
    ys = np.arange(footprint.y_min, footprint.y_max + 1e-9, step)
    local = np.vstack([np.column_stack([xs, np.full(len(xs), footprint.y_min)]),
                       np.column_stack([xs, np.full(len(xs), footprint.y_max)]),
                       np.column_stack([np.full(len(ys), footprint.x_min), ys]),
                       np.column_stack([np.full(len(ys), footprint.x_max), ys])])
    c, s = math.cos(pose.yaw), math.sin(pose.yaw)
    return np.column_stack([pose.x + c * local[:, 0] - s * local[:, 1], pose.y + s * local[:, 0] + c * local[:, 1]])


def _rect_distance(points: np.ndarray, pose: WorldPose, footprint: EgoFootprint) -> np.ndarray:
    c, s = math.cos(pose.yaw), math.sin(pose.yaw)
    dx, dy = points[:, 0] - pose.x, points[:, 1] - pose.y
    lx, ly = c * dx + s * dy, -s * dx + c * dy
    gx = np.maximum(np.maximum(footprint.x_min - lx, 0.0), lx - footprint.x_max)
    gy = np.maximum(np.maximum(footprint.y_min - ly, 0.0), ly - footprint.y_max)
    return np.hypot(gx, gy)


def footprint_gap(pose_a: WorldPose, footprint_a: Optional[EgoFootprint], pose_b: WorldPose,
                  footprint_b: Optional[EgoFootprint]) -> float:
    """Distance between two vehicles' footprints (0 when they touch or overlap), to about 0.05 m."""
    fa, fb = footprint_a or DEFAULT_BODY, footprint_b or DEFAULT_BODY
    return float(min(_rect_distance(_outline_points(pose_a, fa), pose_b, fb).min(),
                     _rect_distance(_outline_points(pose_b, fb), pose_a, fa).min()))


def contact_check(poses: Mapping[str, "PoseSource"], footprints: Mapping[str, Optional[EgoFootprint]],
                  contact_consistency_m: float):
    """For the collision matching (``alignment.match_collisions``): (gap, tolerance) between two recorders'
    footprints, each at its own report time (its own clock) from its own pose stream; None when a recorder
    has no pose stream.  The tolerance grows with the pose sources' declared accuracy."""
    def check(first: str, t_first: float, second: str, t_second: float) -> Optional[Tuple[float, float]]:
        if first not in poses or second not in poses:
            return None
        sigma = math.hypot(getattr(poses[first], "position_std_m", 0.0), getattr(poses[second], "position_std_m", 0.0))
        gap = footprint_gap(poses[first].pose_at(t_first), footprints.get(first), poses[second].pose_at(t_second),
                            footprints.get(second))
        return gap, contact_consistency_m + 3.0 * sigma
    return check


def outline_distances(poses: PoseSource, footprint: Optional[EgoFootprint], t_local: Sequence[float],
                      points: np.ndarray, inside_zero: bool = False) -> Tuple[np.ndarray, np.ndarray]:
    """``RecorderBody.outline_distance`` for many (instant of the recorder's clock, point) pairs at once:
    (distances, mask of the instants the pose source covers).  ``inside_zero``: a point inside the body is
    at distance 0 (``RecorderBody.distance``)."""
    t = np.asarray(t_local, dtype=float)
    points = np.asarray(points, dtype=float).reshape(-1, 2)
    valid = (t >= poses.start - 1e-6) & (t <= poses.end + 1e-6)
    x, y, yaw = poses.poses_at(t)
    c, s = np.cos(yaw), np.sin(yaw)
    dx, dy = points[:, 0] - x, points[:, 1] - y
    lx, ly = c * dx + s * dy, -s * dx + c * dy
    fp = footprint or DEFAULT_BODY
    inside = (lx >= fp.x_min) & (lx <= fp.x_max) & (ly >= fp.y_min) & (ly <= fp.y_max)
    edge = np.minimum(np.minimum(lx - fp.x_min, fp.x_max - lx), np.minimum(ly - fp.y_min, fp.y_max - ly))
    zero = np.zeros_like(lx)
    outside = np.hypot(np.maximum(np.maximum(fp.x_min - lx, zero), lx - fp.x_max),
                       np.maximum(np.maximum(fp.y_min - ly, zero), ly - fp.y_max))
    return np.where(inside, 0.0 if inside_zero else edge, outside), valid


def entry_distances(poses: PoseSource, footprint: Optional[EgoFootprint], t_local: Sequence[float],
                    points: np.ndarray, origins: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """How far an observed near surface lies from where its line of sight enters the recorder's body.

    For each (instant of the recorder's clock, observed near surface ``points``, observing radar side
    ``origins``): the ray from the origin through the point meets the body's footprint first at its entry
    point -- the surface that observer can see; the distance is between the point and that entry point
    (a point beyond it, inside the body, is that far off: the body would have hidden it).  A ray that
    misses the body gives the point's distance to the footprint.  Returns (distances, mask of the instants
    the pose source covers)."""
    t = np.asarray(t_local, dtype=float)
    points = np.asarray(points, dtype=float).reshape(-1, 2)
    origins = np.asarray(origins, dtype=float).reshape(-1, 2)
    valid = (t >= poses.start - 1e-6) & (t <= poses.end + 1e-6)
    x, y, yaw = poses.poses_at(t)
    c, s = np.cos(yaw), np.sin(yaw)
    fp = footprint or DEFAULT_BODY

    def body_frame(xy: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        dx, dy = xy[:, 0] - x, xy[:, 1] - y
        return c * dx + s * dy, -s * dx + c * dy

    px, py = body_frame(points)
    ox, oy = body_frame(origins)
    dx, dy = px - ox, py - oy
    reach = np.hypot(dx, dy)
    ux, uy = dx / np.maximum(reach, 1e-9), dy / np.maximum(reach, 1e-9)
    with np.errstate(divide="ignore", invalid="ignore"):
        tx1, tx2 = (fp.x_min - ox) / ux, (fp.x_max - ox) / ux
        ty1, ty2 = (fp.y_min - oy) / uy, (fp.y_max - oy) / uy
    # A ray parallel to a pair of faces: inside that slab for every s, or never.
    inside_x = (ox >= fp.x_min) & (ox <= fp.x_max)
    inside_y = (oy >= fp.y_min) & (oy <= fp.y_max)
    tx_low = np.where(np.abs(ux) < 1e-12, np.where(inside_x, -np.inf, np.inf), np.minimum(tx1, tx2))
    tx_high = np.where(np.abs(ux) < 1e-12, np.where(inside_x, np.inf, -np.inf), np.maximum(tx1, tx2))
    ty_low = np.where(np.abs(uy) < 1e-12, np.where(inside_y, -np.inf, np.inf), np.minimum(ty1, ty2))
    ty_high = np.where(np.abs(uy) < 1e-12, np.where(inside_y, np.inf, -np.inf), np.maximum(ty1, ty2))
    enter, leave = np.maximum(tx_low, ty_low), np.minimum(tx_high, ty_high)
    hit = (enter <= leave) & (leave >= 0.0)
    zero = np.zeros_like(px)
    outside = np.hypot(np.maximum(np.maximum(fp.x_min - px, zero), px - fp.x_max),
                       np.maximum(np.maximum(fp.y_min - py, zero), py - fp.y_max))
    distance = np.where(hit, np.abs(reach - np.maximum(enter, 0.0)), outside)
    return distance, valid


def common_track(track: LocalTrack, recorder: str, ego: EgoTrajectory, poses: PoseSource,
                 footprint: Optional[EgoFootprint], offset_to_global: float, status: str = "ANONYMOUS",
                 entity: Optional[str] = None) -> CommonTrack:
    """One local track in the common frame.

    The track's position relative to the recorder's body (longitudinal, lateral) and its ground velocity
    expressed in the recorder's axes (through the recorder's own heading in its local frame) are composed
    with the recorder's pose from ``poses``; so are its claimed returns."""
    fp = footprint or DEFAULT_BODY
    samples = []
    returns = track.returns or [None] * len(track.samples)
    for sample, claimed in zip(track.samples, returns):
        pose = poses.pose_at(sample.t_local)
        local = ego.at(sample.t_local)
        nx, ny = fp.outward(sample.longitudinal_m, sample.lateral_m)
        near_x = sample.longitudinal_m - sample.surface_offset_m * nx
        near_y = sample.lateral_m - sample.surface_offset_m * ny
        bx, by = fp.nearest(near_x, near_y)
        c, s = math.cos(local.heading), math.sin(local.heading)
        rel_vx, rel_vy = c * sample.vx_mps + s * sample.vy_mps, -s * sample.vx_mps + c * sample.vy_mps
        cw, sw = math.cos(pose.yaw), math.sin(pose.yaw)
        velocity = np.array([cw * rel_vx - sw * rel_vy, sw * rel_vx + cw * rel_vy])
        speed = float(np.hypot(*velocity))
        world_returns = world_origins = None
        if claimed is not None:
            points, origins = claimed
            world_returns = _local_to_world(points, local, pose)
            world_origins = _local_to_world(origins, local, pose)
        reach = math.hypot(sample.longitudinal_m, sample.lateral_m)
        samples.append(CommonSample(
            t_local=sample.t_local, t_global=round(sample.t_local + offset_to_global, 4),
            point=pose.to_world(sample.longitudinal_m, sample.lateral_m), near=pose.to_world(near_x, near_y),
            velocity=velocity, pos_std=sample.pos_std_m, vel_std=sample.vel_std_mps,
            observer=pose.to_world(float(bx), float(by)), measured=sample.measured,
            heading=math.atan2(velocity[1], velocity[0]) if speed >= HEADING_MIN_SPEED_MPS else None,
            returns=world_returns, origins=world_origins,
            pose_var=poses.position_std_m ** 2 + (poses.yaw_std_rad * reach) ** 2))
    return CommonTrack(recorder=recorder, track_id=track.track_id, samples=samples, status=status, entity=entity,
                       identity_ambiguous=track.identity_ambiguous, parent_track=track.parent_track)


def _local_to_world(points: np.ndarray, local: Any, pose: WorldPose) -> np.ndarray:
    """Local-frame points of a recorder -> its vehicle frame (local pose) -> common frame (pose source)."""
    points = np.asarray(points, dtype=float).reshape(-1, 2)
    c, s = math.cos(local.heading), math.sin(local.heading)
    dx, dy = points[:, 0] - local.x, points[:, 1] - local.y
    vx, vy = c * dx + s * dy, -s * dx + c * dy
    cw, sw = math.cos(pose.yaw), math.sin(pose.yaw)
    return np.column_stack([pose.x + cw * vx - sw * vy, pose.y + sw * vx + cw * vy])
