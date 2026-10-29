"""Replay model: recorded trajectories, a playback clock and reconstructed events.

Pure Python (no CARLA, no pygame) and read-only; used by scripts/replay_run.py.

Timeline.  The clock is the reconstruction's global time (``reconstruction/global/alignment.json``:
matched collisions, else a recorder's observed trajectory):

    t_global = t_local + offset_to_global(X),   t_local = source_timestamp - origin(X)

for every sample of recorder X (its poses, events, tracks and perceived
states), where ``origin(X)`` is X's own clock origin as its local graph records
it.  Recorders are synchronised by the reconstruction's alignment, never by the
simulator's shared clock.  A recorder the reconstruction could not align has no
place on that timeline: it is not replayed, and the replay says so.  Only when no
recorder is aligned does the viewer fall back to the recorded source timestamps
of every recorder (one simulator clock in a CARLA run), and says so.  Replay time
runs from 0 at the earliest sample shown; ``display_time`` gives t_global (or
the source-clock time).

Poses.  A recorder is drawn at the poses of its pose source -- by default its own
recorded stream (``ego.jsonl``, the GNSS-like pose, exact in CARLA); the robustness
study passes a perturbed source (``ReplayRun.load(pose_factory=...)``), as the
reconstruction does.  A radar track is drawn where its vehicle-frame measurement
(``longitudinal_m``, ``lateral_m``) puts it from its observer's pose.

Road users.  The fusion's anonymous road users (``global/anonymous_entities.json``:
U1, U2, ...) are drawn once each: one box of the fitted footprint at the fused
position and heading, with the position uncertainty, labelled with the tracks
it fuses and their observers; those tracks are no ghosts of their own.  A track
the fusion identified with a recorder is that recorder's replayed vehicle.

Inputs.  The viewer shows what the reconstruction knows, not what the
simulator knew.  It reads the recorders' own files (``vehicles/<id>/ego.jsonl``,
``vehicles/<id>/metadata.json``: blueprint and own footprint), the
reconstruction outputs (``reconstruction/<id>/``, ``reconstruction/global/``
graph, associations and road users) and the global reconstruction parameters
(``configs/reconstruction.yaml``).  It never reads ground truth, the run's own
``metadata.json``, the scenario configuration or the privileged evaluation: a
road user that recorded nothing exists here only as what the recorders' radars
saw of it, under an anonymous name.
"""

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
    """Interpolate from ``a`` to ``b`` (degrees) the shorter way round."""
    return a + ((b - a + 180.0) % 360.0 - 180.0) * f


def wrap_deg(angle: float) -> float:
    """``angle`` in [-180, 180)."""
    return (angle + 180.0) % 360.0 - 180.0


# --------------------------------------------------------------------------
# Recorded trajectories
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Pose:
    """A CARLA transform: world-frame metres and degrees."""

    x: float
    y: float
    z: float
    yaw: float
    pitch: float = 0.0
    roll: float = 0.0


class Trajectory:
    """The recorded poses of one vehicle, interpolated between samples.

    Position and recorded speed interpolate linearly, angles the shorter way
    round.  Outside the recorded span the first or last pose is held; nothing
    is extrapolated.
    """

    def __init__(self, times: Sequence[float], poses: Sequence[Pose], speeds: Optional[Sequence[float]] = None):
        if not times or len(times) != len(poses):
            raise ValueError("a trajectory needs one pose per timestamp")
        self.times: List[float] = []
        self.poses: List[Pose] = []
        self.speeds: List[float] = []
        for index in sorted(range(len(times)), key=lambda i: times[i]):
            if self.times and times[index] <= self.times[-1] + _EPS:
                continue  # a repeated timestamp adds nothing to interpolate
            self.times.append(float(times[index]))
            self.poses.append(poses[index])
            self.speeds.append(float(speeds[index]) if speeds is not None else 0.0)

    @classmethod
    def from_records(cls, records: Sequence[Mapping[str, Any]]) -> "Trajectory":
        """From ego.jsonl records (timestamp, x, y, z, yaw_deg, pitch_deg, roll_deg, velocity)."""
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
        """The same poses on a clock ``delta`` seconds ahead (t -> t + delta)."""
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


# --------------------------------------------------------------------------
# Playback clock
# --------------------------------------------------------------------------

class PlaybackClock:
    """Replay time from 0 to ``duration``, advanced by wall time.

    At speed s one wall second advances the replay by s seconds.  Only the
    sampling instant changes with s; the recorded trajectory never does.
    """

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
        """Pause or resume; resuming at the end starts again from 0."""
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


# --------------------------------------------------------------------------
# Reconstructed events (read from existing outputs, never recomputed)
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class ReplayEvent:
    time: float  # replay time
    actor: str  # the recorder whose local graph holds the event
    event_type: str
    subject: Optional[str]
    node_id: str
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StateInterval:
    """One START..END (or ENTRY..EXIT) pair of a recorder's local graph, in replay time."""

    actor: str
    state: str
    subject: Optional[str]
    start: float
    end: Optional[float]  # None: still active when observation ended

    def active_at(self, t: float) -> bool:
        return self.start - _EPS <= t and (self.end is None or t < self.end - _EPS)


def state_intervals(events: Sequence[ReplayEvent], observed_from: float = 0.0) -> List[StateInterval]:
    """Pair the START/END transitions of one recorder's events (in graph order).

    An END without an observed START (a track first seen inside the ego path,
    whose entry was never seen) is shown from the subject's latest appearance
    before it (a road user seen in several segments: the segment the END
    belongs to), or from ``observed_from`` (the recorder's first sample) for its
    own states.
    """
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
    """A recorder's perceived state per trace frame (``local_trace.jsonl``), on the replay timeline.

    Read as written by the reconstruction: the state AT each frame time, after
    its transitions.  Between frames the latest frame holds (frames are 0.1 s apart).
    """

    times: List[float]
    states: List[Dict[str, Any]]

    def state_at(self, t: float) -> Optional[Dict[str, Any]]:
        index = bisect_right(self.times, t + _EPS) - 1
        return None if index < 0 else self.states[index]


def load_perceived_states(path: Path, origin: float, run_start: float) -> Optional[PerceivedStates]:
    """None when the trace predates perceived states (the viewer then pairs START/END events)."""
    times, states = [], []
    for row in _read_jsonl(path):
        if row.get("perceived_state") is not None:
            times.append(round(origin + float(row["t_local"]) - run_start, 6))
            states.append(row["perceived_state"])
    return PerceivedStates(times, states) if states else None


@dataclass
class LocalEvents:
    recorder: str
    origin: float  # source timestamp of the recorder's t_local = 0
    events: List[ReplayEvent]
    intervals: List[StateInterval]


def load_local_events(path: Path, run_start: float, clock_origin: Optional[float] = None) -> LocalEvents:
    """Events of one local_graph.json on the replay timeline (read-only).

    ``clock_origin``: the replay clock's value at the recorder's t_local = 0 (its
    offset_to_global on the global clock); by default its recorded source origin.
    """
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
    """COLLISION nodes of global_graph.json; participants as the fusion reported them."""
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
    """(recorder, local node) of the local collisions the fusion kept as recontacts of the collision they follow
    (``attributes.recontacts`` of a global COLLISION node), unless the same local report is also an observation of
    a collision: a recorder's sensor may report a contact with a third vehicle and a recontact as one (S04
    ``a_front_pushed``, B: its contact with C and A's recontact), and that report stays the collision."""
    nodes = [node for node in _read_json(path)["nodes"] if node["event_type"] == "COLLISION"]
    collisions = {(str(obs["graph"]), str(obs["local_node"])) for node in nodes for obs in node.get("observations", [])}
    recontacts = {(str(graph), str(local_node)) for node in nodes
                  for item in (node.get("attributes") or {}).get("recontacts", [])
                  for graph, local_node, _ in item.get("observations", [])}
    return recontacts - collisions


ASSOCIATED = "ASSOCIATED"  # the fusion identified the track with a recorder: that recorder's replayed vehicle
ANONYMOUS = "ANONYMOUS"  # no recorder identified with it: a road user known only through this track


def load_track_statuses(path: Path) -> Dict[Tuple[str, str], Tuple[str, Optional[str]]]:
    """(recorder, local track) -> (fusion status, associated recorder or None), from associations.json."""
    statuses: Dict[Tuple[str, str], Tuple[str, Optional[str]]] = {}
    for item in _read_json(path):
        status = str(item.get("status") or ANONYMOUS)
        entity = str(item["global_entity"]) if status == ASSOCIATED else None
        statuses[(str(item["local_graph"]), str(item["local_track"]))] = (status, entity)
    return statuses


# --------------------------------------------------------------------------
# Reconstructed tracks: what each recorder's radar knows about other road users
# --------------------------------------------------------------------------

GHOST_HEIGHT_M = 1.5  # drawing only: the radar measures no size
# The CRITICAL_TTC model's own footprint for a recorder that recorded none (conflict._Prediction).
DEFAULT_FOOTPRINT = EgoFootprint(-2.3, 2.3, -0.95, 0.95)
HEADING_FROM_VELOCITY, HEADING_HELD, HEADING_UNKNOWN = "velocity", "held", "unknown"


def local_to_world(origin: Pose, x_local: float, y_local: float) -> Tuple[float, float]:
    """Inverse of the reconstruction's local frame (origin = first ego pose, x forward, y right)."""
    c0, s0 = math.cos(math.radians(origin.yaw)), math.sin(math.radians(origin.yaw))
    return origin.x + c0 * x_local - s0 * y_local, origin.y + s0 * x_local + c0 * y_local


def rotate(x: float, y: float, yaw_deg: float) -> Tuple[float, float]:
    """A vector given in the axes of a vehicle at ``yaw_deg`` (x forward, y right), in world axes."""
    c, s = math.cos(math.radians(yaw_deg)), math.sin(math.radians(yaw_deg))
    return c * x - s * y, s * x + c * y


@dataclass(frozen=True)
class GhostGeometry:
    """The reconstruction's nominal target box and tracking gap (``configs/reconstruction.yaml``).

    A radar measures no size: the box is the reconstruction's hypothesis, not a measured body.
    """

    length: float = 4.6  # semantics.target_length_m
    width: float = 1.9  # semantics.target_width_m
    height: float = GHOST_HEIGHT_M
    max_gap: float = 0.5  # tracking.max_track_gap_s: never interpolate across a longer silence

    @classmethod
    def from_config(cls, config: ReconstructionConfig) -> "GhostGeometry":
        return cls(length=float(config.semantics.target_length_m), width=float(config.semantics.target_width_m),
                   max_gap=float(config.tracking.max_track_gap_s))


def track_heading(vx: float, vy: float, vel_std: float) -> Optional[float]:
    """Direction of motion ``atan2(vy, vx)`` [deg] of a track velocity, in the frame it is given in.

    None when the speed does not fix a direction: below the reconstruction's
    HEADING_MIN_SPEED_MPS, or within twice the estimate's own uncertainty.
    """
    if math.hypot(vx, vy) < max(HEADING_MIN_SPEED_MPS, 2.0 * max(vel_std, 0.0)):
        return None
    return math.degrees(math.atan2(vy, vx))


def nominal_box_centre(longitudinal: float, lateral: float, surface_offset: float, heading_deg: float,
                       footprint: EgoFootprint, length: float, width: float) -> Tuple[float, float]:
    """Centre, in the recorder's vehicle frame, of the nominal box of one track sample.

    The placement of the CRITICAL_TTC model (``conflict._Prediction``), repeated
    for drawing: the tracked point moved back by its surface offset towards the
    recorder is the target's near surface (the corner towards the recorder when
    seen obliquely, the middle of the facing side when seen along one of its
    axes); the box lies behind it, in each of its axes by a weight growing from
    0 (looking along that face) to 1 at OBLIQUE_VIEW_DEG and beyond.
    ``heading_deg`` is the box heading relative to the recorder.
    """
    ux, uy = math.cos(math.radians(heading_deg)), math.sin(math.radians(heading_deg))
    nx, ny = footprint.outward(longitudinal, lateral)
    near_x, near_y = longitudinal - surface_offset * nx, lateral - surface_offset * ny
    gx, gy = -nx, -ny  # from the target towards the recorder
    along, across = gx * ux + gy * uy, -gx * uy + gy * ux  # in the target's axes (across = its right)
    oblique = math.sin(math.radians(OBLIQUE_VIEW_DEG))
    back = math.copysign(length / 2.0 * min(abs(along) / oblique, 1.0), along)
    side = math.copysign(width / 2.0 * min(abs(across) / oblique, 1.0), across)
    return near_x - back * ux + side * uy, near_y - back * uy - side * ux


@dataclass(frozen=True)
class TrackPoint:
    """One track sample (or an instant between two) on the replay timeline, in world coordinates."""

    time: float
    position: Tuple[float, float]  # the track estimate, as the reconstruction wrote it
    centre: Tuple[float, float]  # the nominal box behind the observed near surface
    yaw: float  # box heading [deg]: the estimated motion, else the last reliable one, else the recorder's
    heading: str  # HEADING_FROM_VELOCITY, HEADING_HELD or HEADING_UNKNOWN (no direction to show)
    measured: bool  # False: predicted by the tracker without a radar return
    clearance: Optional[float] = None  # body to body: the near surface to the observer's own footprint [m]


@dataclass
class TrackPath:
    """One radar track of one recorder on the replay timeline.

    Shown only between its first and last sample (its TRACK_LOST): interpolated
    between consecutive samples of this track at most ``max_gap`` apart, never
    extrapolated and never continued by anything else.  Tracks are never merged:
    two recorders seeing the same road user give two tracks.
    """

    recorder: str
    track_id: str
    samples: List[TrackPoint]
    status: str = ANONYMOUS
    entity: Optional[str] = None  # the associated recorder (ASSOCIATED only)
    max_gap: float = 0.5
    road_user: Optional[str] = None  # the anonymous road user (U1, ...) the fusion made of it, if any
    times: List[float] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.samples = sorted(self.samples, key=lambda sample: sample.time)
        self.times = [sample.time for sample in self.samples]

    @property
    def name(self) -> str:
        """``A:track_001``: the recorder and its local track id (the only name the reconstruction gives it)."""
        return "{0}:{1}".format(self.recorder, self.track_id)

    @property
    def ghost(self) -> bool:
        """Drawn as a body of its own: no recorder was identified with it and it belongs to no fused
        road user.  An associated track is the associated recorder's replayed vehicle, and a track of a
        road user is drawn through that road user's single box: neither gets a second body."""
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
        """The track at ``t``: a sample, or between two consecutive samples of this track; None outside."""
        if not self.samples or t < self.times[0] - _EPS or t > self.times[-1] + _EPS:
            return None
        index = max(0, bisect_right(self.times, t + _EPS) - 1)
        a = self.samples[index]
        if index == len(self.samples) - 1 or t <= a.time + _EPS:
            return a
        b = self.samples[index + 1]
        if b.time - a.time > self.max_gap + _EPS:
            return None  # a silence the tracker does not bridge: nothing is known in between
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
    """A recorder's tracks from its ``local_tracks.jsonl``, each sample from its observer's pose.

    The estimate is placed by its vehicle-frame offsets (``longitudinal_m``,
    ``lateral_m``) from the observer's pose at the sample (``trajectory``: its pose
    source); without them, by the local-frame estimate (``x_m``, ``y_m``) through
    the local frame's origin (the first recorded pose).  The box heading is
    ``atan2(vy, vx)`` of the estimated velocity (in the local frame) when the
    speed fixes it (``track_heading``), turned into the observer's pose through its
    recorded heading (``recorded``), else the track's last reliable heading, else
    unknown (the box is then drawn parallel to the recorder, as the CRITICAL_TTC
    model takes it, with no direction).  Tracks of different recorders are never
    compared or merged.
    """
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
            observer = trajectory.pose_at(source_time)  # the observer's pose (its pose source) at the sample
            own = (recorded or trajectory).pose_at(source_time)  # its recorded pose: its local heading
            if row.get("longitudinal_m") is not None and row.get("lateral_m") is not None:
                dx, dy = rotate(float(row["longitudinal_m"]), float(row["lateral_m"]), observer.yaw)
                position = (observer.x + dx, observer.y + dy)
            else:
                position = local_to_world(frame_origin, float(row["x_m"]), float(row["y_m"]))
            motion = track_heading(float(row.get("vx_mps") or 0.0), float(row.get("vy_mps") or 0.0),
                                   float(row.get("vel_std_mps") or 0.0))
            if motion is not None:
                # Local-frame direction -> relative to the observer (recorded) -> through the drawn pose.
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


# --------------------------------------------------------------------------
# Road users that recorded nothing: the fusion's anonymous entities
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class EntityState:
    """One fused state of an anonymous road user on the replay timeline (world frame)."""

    time: float
    centre: Tuple[float, float]
    yaw: Optional[float]  # box heading [deg]; None while no heading is known
    heading: str  # HEADING_FROM_VELOCITY, HEADING_HELD or HEADING_UNKNOWN
    speed: float
    pos_std: float  # position uncertainty [m] (1 sigma, largest axis)
    method: str  # box_fit or covariance_intersection
    observers: Tuple[str, ...]  # recorders whose tracks give this state
    measured: bool  # some observer measured it at this instant (else only predicted)


@dataclass
class EntityPath:
    """An anonymous road user (U1, ...) as the fusion made it: one body, never named after a participant."""

    entity_id: str
    source_tracks: List[str]
    observers: List[str]
    length: float  # footprint used for drawing (fitted, prior or observed extent)
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
        """The fused state at ``t``: a state, or between two consecutive ones; None outside or across a gap."""
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
    """The anonymous road users of ``global/anonymous_entities.json`` on the replay timeline (t_global)."""
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


# --------------------------------------------------------------------------
# The map a run was recorded on
# --------------------------------------------------------------------------

MAP_MIN_FIT = 0.98  # share of the recorded ego positions that must lie in a driving lane of the map
MAP_MARGIN = 0.05  # ...by this much more than in any other road network


def choose_map(fits: Mapping[str, float], networks: Mapping[str, str], current: Optional[str] = None) -> Optional[str]:
    """The map whose driving lanes carry the recorders' own recorded positions.

    ``fits``: map -> share of the recorded ego positions inside one of its
    driving lanes; ``networks``: map -> its road network (equal OpenDRIVE, e.g.
    Town05 and Town05_Opt).  None when no map fits, or when a different road
    network fits almost as well (pass the map explicitly then).  Among the maps
    of the winning road network the server's current map is preferred (no
    reload), then the plain name over a variant.
    """
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


# --------------------------------------------------------------------------
# A recorded run
# --------------------------------------------------------------------------

GLOBAL_CLOCK = "t_global"  # the reconstruction's collision-anchored global time
SOURCE_CLOCK = "source"  # the recorded source timestamps (one simulator clock in a CARLA run)


def recorder_clocks(run_dir: Path, ids: Sequence[str]) -> Tuple[str, Dict[str, float], Dict[str, float]]:
    """(clock, source origins, offsets_to_global) from the reconstruction outputs only.

    GLOBAL_CLOCK when at least one recorder has a local graph with its clock
    origin and an ALIGNED offset in ``reconstruction/global/alignment.json`` (the
    recorders without one are not replayed); otherwise SOURCE_CLOCK (the origins
    and offsets found are still returned).
    """
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
    """A recorder's poses from its pose source at its recorded instants (heights and attitude as recorded)."""
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
    """A recorder: a vehicle with its own recorded ``ego.jsonl`` (the only vehicles replayed)."""

    participant_id: str
    blueprint: str
    blueprint_source: str  # "recorded" or "fallback"
    trajectory: Trajectory  # the poses drawn: its pose source on the replay clock
    frame_origin: Pose  # first pose in file order of its pose source: the reconstruction's local frame
    footprint: Optional[EgoFootprint] = None  # its own recorded footprint (vehicle frame)
    recorded: Optional[Trajectory] = None  # the pose stream of its local frame on the replay clock (local headings)


@dataclass
class ReplayRun:
    run_dir: Path
    name: str
    participants: List[Participant]
    start: float  # source timestamp of replay time 0
    duration: float
    local_events: Dict[str, LocalEvents] = field(default_factory=dict)
    entity_event_overrides: List[ReplayEvent] = field(default_factory=list)
    entity_source_nodes: set = field(default_factory=set)
    collisions: List[CollisionMark] = field(default_factory=list)
    clock: str = SOURCE_CLOCK  # GLOBAL_CLOCK (reconstruction alignment) or SOURCE_CLOCK (recorded timestamps)
    clock_origins: Dict[str, float] = field(default_factory=dict)  # the clock's value at each recorder's t_local = 0
    identities: Dict[Tuple[str, str], str] = field(default_factory=dict)
    tracks: Dict[str, List[TrackPath]] = field(default_factory=dict)
    perceived: Dict[str, PerceivedStates] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)
    geometry: GhostGeometry = field(default_factory=GhostGeometry)
    entities: List[EntityPath] = field(default_factory=list)  # anonymous road users (U1, ...)
    road_users: Dict[Tuple[str, str], str] = field(default_factory=dict)  # (recorder, track) -> U1, ...
    hidden: List[str] = field(default_factory=list)  # recorders without a global clock: not replayed
    recording_zero: float = 0.0  # the recorders' clock at t_global = 0 (median over the aligned recorders)

    @classmethod
    def load(cls, run_dir: Path, geometry: Optional[GhostGeometry] = None,
             pose_factory: Optional[Callable[[Path, float], Any]] = None) -> "ReplayRun":
        """Read a run: the recorders' own files and the reconstruction outputs only (module docstring).
        ``pose_factory(vehicle_dir, clock_origin)`` gives a recorder's pose source (a
        ``cdf.reconstruction.common_frame.PoseSource``); by default its recorded stream."""
        run_dir = Path(run_dir)
        notes: List[str] = []
        if pose_factory is None:
            # The poses the reconstruction used when they are not the recorded streams (perturbed GNSS/INS,
            # mutual refinement): written by the reconstruction, never the simulator's.
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
                # The local frame of the radar tracks is the measured one too (pipeline.measured_ego_records):
                # tracks are turned with these poses, never with the exact stream.
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
            # A recontact is part of the collision it follows: RECONTACT in the panels, not a further collision.
            recontacts = load_recontacts(rec / "global" / "global_graph.json")
            for pid, local in self.local_events.items():
                local.events = [replace(event, event_type="RECONTACT") if (pid, event.node_id) in recontacts else event
                                for event in local.events]
            if self.clock == GLOBAL_CLOCK:
                graph = _read_json(rec / 'global' / 'global_graph.json')
                # Local events the global graph deliberately does not assert stay out of the display.
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

    # -- queries --------------------------------------------------------------

    def display_time(self, t: float) -> float:
        """Replay time -> the clock shown to the user: t_global, or seconds since the first source sample."""
        return (round(t + self.start, 6) if self.clock == GLOBAL_CLOCK else round(t, 6)) + 0.0  # no -0.0

    def recording_time(self, t: float) -> float:
        """Replay time -> the recorders' own clock (``cdf.replay.sync``), from the reconstruction's alignment and
        the recorders' timestamps only: t_global + (clock origin - offset_to_global) of the aligned recorders."""
        return self.start + t + (self.recording_zero if self.clock == GLOBAL_CLOCK else 0.0)

    def replay_time_of(self, t_recording: float) -> float:
        return t_recording - self.start - (self.recording_zero if self.clock == GLOBAL_CLOCK else 0.0)

    def participant(self, participant_id: str) -> Participant:
        return next(p for p in self.participants if p.participant_id == participant_id)

    def all_events(self) -> List[ReplayEvent]:
        return sorted((e for local in self.local_events.values() for e in local.events),
                      key=lambda e: (e.time, e.actor, e.node_id))

    def recent_events(self, actor: str, t: float, window: float) -> List[ReplayEvent]:
        """Events of ``actor`` in (t - window, t]."""
        local = self.local_events.get(actor)
        if local is None:
            return []
        return [e for e in self.display_events() if e.actor == actor and t - window < e.time <= t + _EPS]

    def display_events(self) -> List[ReplayEvent]:
        """Read the persisted entity timeline for display, keeping source events available in all_events."""
        events = [e for e in self.all_events() if (e.actor,e.node_id) not in self.entity_source_nodes]
        return sorted(events+self.entity_event_overrides,key=lambda e:(e.time,e.actor,e.node_id))

    def active_states(self, actor: str, t: float) -> List[StateInterval]:
        local = self.local_events.get(actor)
        return [] if local is None else [item for item in local.intervals if item.active_at(t)]

    def perceived_lines(self, actor: str, t: float) -> Optional[List[str]]:
        """The recorder's own perceived state at ``t`` as compact lines (tracks named
        as in ``subject_name``); None when the reconstruction wrote no perceived state."""
        perceived = self.perceived.get(actor)
        if perceived is None:
            return None
        return compact_state(perceived.state_at(t), lambda track: self.subject_name(actor, track))

    def collisions_near(self, t: float, window: float) -> List[CollisionMark]:
        """Collisions in (t - window, t]."""
        return [mark for mark in self.collisions if t - window < mark.time <= t + _EPS]

    def event_times(self) -> List[float]:
        times = sorted({e.time for e in self.all_events()} | {m.time for m in self.collisions})
        return [t for t in times if 0.0 - _EPS <= t <= self.duration + _EPS]

    def next_event_time(self, t: float) -> Optional[float]:
        return next((x for x in self.event_times() if x > t + _EPS), None)

    def previous_event_time(self, t: float) -> Optional[float]:
        return next((x for x in reversed(self.event_times()) if x < t - _EPS), None)

    def subject_name(self, actor: str, subject: Optional[str]) -> str:
        """``track_001 (B)`` when the fusion associated the track with a recorder, ``track_001 (U1)`` when it
        made it part of an anonymous road user, else the local name."""
        if subject is None:
            return ""
        entity = self.identities.get((actor, subject)) or self.road_users.get((actor, subject))
        return subject if entity is None else "{0} ({1})".format(subject, entity)

    def all_tracks(self) -> List[TrackPath]:
        """Every track of every recorder, recorder by recorder (never merged across recorders)."""
        return [track for participant in self.participants for track in self.tracks.get(participant.participant_id, [])]

    def ghost_tracks(self) -> List[TrackPath]:
        """The anonymous tracks: road users no recorder was identified with, drawn as ghost boxes."""
        return [track for track in self.all_tracks() if track.ghost]

    def entities_at(self, t: float) -> List[Tuple[EntityPath, EntityState]]:
        """The anonymous road users present at ``t``, with their fused state."""
        out = []
        for entity in self.entities:
            if entity.identity_ambiguous:
                continue  # retain its points/diagnostics; no asserted physical box
            state = entity.state_at(t)
            if state is not None:
                out.append((entity, state))
        return out

    def entity(self, entity_id: str) -> Optional[EntityPath]:
        return next((entity for entity in self.entities if entity.entity_id == entity_id), None)

    def anonymous_at(self, recorder: str, t: float) -> List[Tuple[TrackPath, TrackPoint]]:
        """The recorder's anonymous tracks alive at ``t``, with their state."""
        alive = []
        for track in self.tracks.get(recorder, []):
            state = track.state_at(t) if track.ghost else None
            if state is not None:
                alive.append((track, state))
        return alive

    def map_samples(self) -> List[Vector]:
        """The recorders' own recorded positions (only to recognise the map they drove on)."""
        return [(pose.x, pose.y, pose.z) for participant in self.participants for pose in participant.trajectory.poses]


# --------------------------------------------------------------------------
# Camera geometry (CARLA / Unreal conventions: x forward, y right, z up)
# --------------------------------------------------------------------------

Vector = Tuple[float, float, float]


def rotation_axes(yaw: float, pitch: float, roll: float = 0.0) -> Tuple[Vector, Vector, Vector]:
    """World-frame forward, right and up unit vectors of a rotation in degrees."""
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    cp, sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))
    cr, sr = math.cos(math.radians(roll)), math.sin(math.radians(roll))
    forward = (cp * cy, cp * sy, sp)
    right = (sr * sp * cy - cr * sy, sr * sp * sy + cr * cy, -sr * cp)
    up = (-(cr * sp * cy + sr * sy), cy * sr - cr * sp * sy, cr * cp)
    return forward, right, up


NEAR_PLANE_M = 0.1


def project(point: Vector, camera: Pose, fov_deg: float, width: int, height: int) -> Optional[Tuple[float, float]]:
    """Pixel of a world point in a pinhole camera (horizontal FOV), None if behind it."""
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
    """Pixels of the part of a world segment in front of the camera (clipped at the near plane)."""
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


# Bottom face, top face, then the vertical edges of box_corners().
BOX_EDGES = ((0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7))


def box_corners(centre: Tuple[float, float], yaw: float, length: float, width: float, z: float,
                height: float) -> List[Vector]:
    """An upright box: bottom front-left, front-right, rear-right, rear-left, then the same on top."""
    base = []
    for ox, oy in ((length / 2.0, -width / 2.0), (length / 2.0, width / 2.0),
                   (-length / 2.0, width / 2.0), (-length / 2.0, -width / 2.0)):
        dx, dy = rotate(ox, oy, yaw)
        base.append((centre[0] + dx, centre[1] + dy))
    return [(x, y, z) for x, y in base] + [(x, y, z + height) for x, y in base]


def look_at(eye: Vector, target: Vector) -> Tuple[float, float]:
    """(yaw, pitch) in degrees that point a camera at ``eye`` towards ``target``."""
    dx, dy, dz = target[0] - eye[0], target[1] - eye[1], target[2] - eye[2]
    return math.degrees(math.atan2(dy, dx)), math.degrees(math.atan2(dz, math.hypot(dx, dy)))


def overview_camera(points: Sequence[Vector], heading: float, zoom: float = 1.0, elevation: float = 30.0) -> Pose:
    """Above and behind the centroid of ``points`` along ``heading``, looking at it.

    The distance grows with the spread of the points so that vehicles ahead
    and behind the centroid stay inside a 16:9 frame at the default zoom.
    """
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
    """Behind the vehicle (rotated by ``orbit`` degrees around it), looking just ahead of it."""
    yaw = math.radians(vehicle.yaw + orbit)
    eye = (vehicle.x - distance * math.cos(yaw), vehicle.y - distance * math.sin(yaw), vehicle.z + height)
    ahead = math.radians(vehicle.yaw)
    target = (vehicle.x + 3.0 * math.cos(ahead), vehicle.y + 3.0 * math.sin(ahead), vehicle.z + 1.0)
    cam_yaw, cam_pitch = look_at(eye, target)
    return Pose(eye[0], eye[1], eye[2], cam_yaw, cam_pitch, 0.0)


class FreeCamera:
    """A camera moved by the user: translate in its own frame, turn by yaw/pitch."""

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
