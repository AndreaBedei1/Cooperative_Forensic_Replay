
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np

from .config import TrackingConfig

INITIAL_VELOCITY_STD_MPS = 10.0
MIN_CLOSING_FOR_TTC_MPS = 0.1
OWN_BODY_MARGIN_M = 0.05
NEAR_SURFACE_PERCENTILE = 10.0
SURFACE_OFFSET_HALF_WINDOW = 2
ACCELERATION_HALF_WINDOW_S = 0.15



@dataclass
class EgoState:
    t_local: float
    x: float
    y: float
    heading: float
    vx: float
    vy: float
    yaw_rate: float = 0.0
    z: float = 0.0
    pitch: float = 0.0
    roll: float = 0.0

    @property
    def speed(self) -> float:
        return math.hypot(self.vx, self.vy)


class EgoTrajectory:

    def __init__(self, states: Sequence[EgoState]) -> None:
        if not states:
            raise ValueError("an ego trajectory needs at least one state")
        self.states = list(states)
        self.times = np.array([state.t_local for state in self.states], dtype=float)
        self._columns = {name: np.array([getattr(state, name) for state in self.states], dtype=float)
                         for name in ("x", "y", "heading", "vx", "vy", "z", "pitch", "roll")}
        self._columns["yaw_rate"] = (np.gradient(self._columns["heading"], self.times)
                                     if len(self.times) > 1 else np.zeros(len(self.times)))

    def at(self, t_local: float) -> EgoState:
        values = {name: float(np.interp(t_local, self.times, column))
                  for name, column in self._columns.items()}
        return EgoState(t_local=float(t_local), **values)

    @property
    def start(self) -> float:
        return float(self.times[0])

    @property
    def end(self) -> float:
        return float(self.times[-1])


def ego_trajectory(ego_records: Sequence[Mapping[str, Any]], clock_origin: float) -> EgoTrajectory:
    first = ego_records[0]
    yaw0 = math.radians(float(first["yaw_deg"]))
    c0, s0 = math.cos(yaw0), math.sin(yaw0)
    headings = np.unwrap([math.radians(float(record["yaw_deg"])) - yaw0 for record in ego_records])
    pitches = np.unwrap([math.radians(float(record.get("pitch_deg", 0.0))) for record in ego_records])
    rolls = np.unwrap([math.radians(float(record.get("roll_deg", 0.0))) for record in ego_records])
    states = []
    for record, heading, pitch, roll in zip(ego_records, headings, pitches, rolls):
        dx = float(record["x"]) - float(first["x"])
        dy = float(record["y"]) - float(first["y"])
        world_vx = float(record["velocity"]["x"])
        world_vy = float(record["velocity"]["y"])
        states.append(EgoState(
            t_local=round(float(record["timestamp"]) - clock_origin, 4),
            x=c0 * dx + s0 * dy, y=-s0 * dx + c0 * dy, heading=float(heading),
            vx=c0 * world_vx + s0 * world_vy, vy=-s0 * world_vx + c0 * world_vy,
            z=float(record.get("z", 0.0)) - float(first.get("z", 0.0)), pitch=float(pitch), roll=float(roll)))
    return EgoTrajectory(states)



@dataclass
class RadarMount:

    x: float = 0.0
    y: float = 0.0
    z: float = 0.6
    yaw: float = 0.0
    pitch: float = 0.0
    sensor_id: str = "radar"

    @classmethod
    def from_metadata(cls, metadata: Mapping[str, Any]) -> "RadarMount":
        transform = metadata.get("sensor_transform") or {}
        return cls(x=float(transform.get("x", 0.0)), y=float(transform.get("y", 0.0)),
                   z=float(transform.get("z", 0.6)), yaw=math.radians(float(transform.get("yaw_deg", 0.0))),
                   pitch=math.radians(float(transform.get("pitch_deg", 0.0))),
                   sensor_id=str(metadata.get("sensor_id", "radar")))

    def directions(self, azimuth: np.ndarray, altitude: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        x, y, z = np.cos(altitude) * np.cos(azimuth), np.cos(altitude) * np.sin(azimuth), np.sin(altitude)
        cp, sp = math.cos(self.pitch), math.sin(self.pitch)
        x, z = x * cp - z * sp, x * sp + z * cp
        cy, sy = math.cos(self.yaw), math.sin(self.yaw)
        return x * cy - y * sy, x * sy + y * cy, z


@dataclass
class RadarStream:

    mount: RadarMount
    observations: Any

    @property
    def sensor_id(self) -> str:
        return self.mount.sensor_id


def sensor_position(ego: EgoState, mount: RadarMount) -> np.ndarray:
    c, s = math.cos(ego.heading), math.sin(ego.heading)
    return np.array([ego.x + c * mount.x - s * mount.y, ego.y + s * mount.x + c * mount.y])


def sensor_velocity(ego: EgoState, mount: RadarMount) -> Tuple[float, float]:
    c, s = math.cos(ego.heading), math.sin(ego.heading)
    forward = c * ego.vx + s * ego.vy - ego.yaw_rate * mount.y
    right = -s * ego.vx + c * ego.vy + ego.yaw_rate * mount.x
    return forward, right


def sensor_point(ego: EgoState, mount: RadarMount) -> np.ndarray:
    cy, sy = math.cos(ego.heading), math.sin(ego.heading)
    cp, sp = math.cos(ego.pitch), math.sin(ego.pitch)
    cr, sr = math.cos(ego.roll), math.sin(ego.roll)
    rotation = np.array([[cp * cy, cy * sp * sr - sy * cr, -(cy * sp * cr + sy * sr)],
                         [cp * sy, sy * sp * sr + cy * cr, cy * sr - sy * sp * cr],
                         [sp, -cp * sr, cp * cr]])
    return np.array([ego.x, ego.y, ego.z]) + rotation @ np.array([mount.x, mount.y, mount.z])


def radar_velocity(ego: EgoTrajectory, mount: RadarMount, t_local: float, t_previous: float) -> np.ndarray:
    if t_local - t_previous <= 1e-6:
        own = ego.at(t_local)
        forward, right = sensor_velocity(own, mount)
        c, s = math.cos(own.heading), math.sin(own.heading)
        return np.array([c * forward - s * right, s * forward + c * right, 0.0])
    return (sensor_point(ego.at(t_local), mount) - sensor_point(ego.at(t_previous), mount)) / (t_local - t_previous)


@dataclass(frozen=True)
class EgoFootprint:

    x_min: float
    x_max: float
    y_min: float
    y_max: float

    @classmethod
    def from_metadata(cls, footprint: Optional[Mapping[str, Any]]) -> Optional["EgoFootprint"]:
        if not footprint:
            return None
        try:
            return cls(x_min=float(footprint["x_min_m"]), x_max=float(footprint["x_max_m"]),
                       y_min=float(footprint["y_min_m"]), y_max=float(footprint["y_max_m"]))
        except (KeyError, TypeError, ValueError):
            return None

    @property
    def centre(self) -> Tuple[float, float]:
        return (self.x_min + self.x_max) / 2.0, (self.y_min + self.y_max) / 2.0

    def nearest(self, x: Any, y: Any) -> Tuple[Any, Any]:
        return np.clip(x, self.x_min, self.x_max), np.clip(y, self.y_min, self.y_max)

    def distance(self, x: Any, y: Any) -> Any:
        qx, qy = self.nearest(x, y)
        return np.hypot(np.asarray(x) - qx, np.asarray(y) - qy)

    def contains(self, x: np.ndarray, y: np.ndarray, margin: float = 0.0) -> np.ndarray:
        return ((x > self.x_min + margin) & (x < self.x_max - margin)
                & (y > self.y_min + margin) & (y < self.y_max - margin))

    def outward(self, x: float, y: float) -> Tuple[float, float]:
        qx, qy = self.nearest(x, y)
        dx, dy = x - float(qx), y - float(qy)
        norm = math.hypot(dx, dy)
        if norm < 1e-6:
            cx, cy = self.centre
            dx, dy = x - cx, y - cy
            norm = max(math.hypot(dx, dy), 1e-6)
        return dx / norm, dy / norm

    def segment_distance(self, p0: Tuple[float, float], p1: Tuple[float, float]) -> Tuple[float, float]:
        x0, y0 = p0
        x1, y1 = p1
        dx, dy = x1 - x0, y1 - y0
        lo, hi = 0.0, 1.0
        inside = True
        for p, q in ((-dx, x0 - self.x_min), (dx, self.x_max - x0), (-dy, y0 - self.y_min), (dy, self.y_max - y0)):
            if abs(p) < 1e-12:
                if q < 0:
                    inside = False
                    break
                continue
            r = q / p
            if p < 0:
                lo = max(lo, r)
            else:
                hi = min(hi, r)
            if lo > hi:
                inside = False
                break
        if inside:
            return 0.0, lo
        candidates = [0.0, 1.0]
        length2 = dx * dx + dy * dy
        if length2 > 1e-12:
            for cx in (self.x_min, self.x_max):
                for cy in (self.y_min, self.y_max):
                    candidates.append(min(max(((cx - x0) * dx + (cy - y0) * dy) / length2, 0.0), 1.0))
        best = min(candidates, key=lambda f: float(self.distance(x0 + f * dx, y0 + f * dy)))
        return float(self.distance(x0 + best * dx, y0 + best * dy)), best



@dataclass
class RadarSweep:

    t_local: float
    points: np.ndarray
    origins: np.ndarray
    radar: np.ndarray
    radial_speed: np.ndarray
    clearance: np.ndarray
    depth: np.ndarray
    own_body: int = 0
    radars: Tuple[str, ...] = ()


def _stream_times(stream: RadarStream, clock_origin: float) -> List[float]:
    return [round(float(timestamp) - clock_origin, 4) for timestamp in stream.observations.timestamps]


def radar_sweeps(streams: Sequence[RadarStream], ego: EgoTrajectory, clock_origin: float, cfg: TrackingConfig,
                 footprint: Optional[EgoFootprint] = None) -> List[RadarSweep]:
    names = tuple(stream.sensor_id for stream in streams)
    times = [_stream_times(stream, clock_origin) for stream in streams]
    lookup = [{t: index for index, t in enumerate(stream_times)} for stream_times in times]
    instants = sorted(set().union(*times)) if times else []
    interval = float(np.median(np.diff(instants))) if len(instants) > 1 else 0.0
    sweeps = []
    for t_local in instants:
        pose = ego.at(t_local)
        c, s = math.cos(pose.heading), math.sin(pose.heading)
        parts: Dict[str, List[np.ndarray]] = {key: [] for key in
                                              ("points", "origins", "radar", "radial", "clearance", "depth")}
        own_body = 0
        for k, stream in enumerate(streams):
            index = lookup[k].get(t_local)
            if index is None:
                continue
            mount = stream.mount
            rows = np.asarray(stream.observations.frame_detections(index), dtype=float).reshape(-1, 4)
            depth, azimuth, altitude, range_rate = rows[:, 0], rows[:, 1], rows[:, 2], rows[:, 3]
            ux, uy, uz = mount.directions(azimuth, altitude)
            vehicle_x, vehicle_y = mount.x + depth * ux, mount.y + depth * uy
            height = mount.z + depth * uz
            valid = (np.isfinite(rows).all(axis=1) & (depth > 0.0)
                     & (height >= cfg.min_height_m) & (height <= cfg.max_height_m))
            previous = times[k][index - 1] if index > 0 else t_local - interval
            if previous < ego.start - 1e-6:
                velocity = radar_velocity(ego, mount, min(t_local + interval, ego.end), t_local)
            else:
                velocity = radar_velocity(ego, mount, t_local, previous)
            line_x, line_y = c * ux - s * uy, s * ux + c * uy
            horizontal = np.maximum(np.hypot(ux, uy), 0.2)
            radial_speed = (range_rate + velocity[0] * line_x + velocity[1] * line_y + velocity[2] * uz) / horizontal
            if footprint is not None:
                inside = valid & footprint.contains(vehicle_x, vehicle_y, OWN_BODY_MARGIN_M)
                own_body += int(inside.sum())
                valid &= ~inside
                clearance = footprint.distance(vehicle_x, vehicle_y)
            else:
                clearance = np.hypot(vehicle_x, vehicle_y)
            origin = sensor_position(pose, mount)
            points = np.column_stack([pose.x + c * vehicle_x - s * vehicle_y, pose.y + s * vehicle_x + c * vehicle_y])
            count = int(valid.sum())
            parts["points"].append(points[valid])
            parts["origins"].append(np.tile(origin, (count, 1)))
            parts["radar"].append(np.full(count, k, dtype=int))
            parts["radial"].append(radial_speed[valid])
            parts["clearance"].append(np.asarray(clearance)[valid])
            parts["depth"].append(depth[valid])

        def joined(key: str, width: Optional[int] = None) -> np.ndarray:
            if parts[key]:
                return np.concatenate(parts[key])
            return np.empty((0, width)) if width else np.empty(0, dtype=int if key == "radar" else float)

        sweeps.append(RadarSweep(t_local=t_local, points=joined("points", 2), origins=joined("origins", 2),
                                 radar=joined("radar"), radial_speed=joined("radial"),
                                 clearance=np.maximum(joined("clearance"), 0.0), depth=joined("depth"),
                                 own_body=own_body, radars=names))
    return sweeps


def cluster_points(points: np.ndarray, max_gap_m: float) -> List[List[int]]:
    remaining = list(range(len(points)))
    clusters = []
    while remaining:
        members = [remaining.pop(0)]
        frontier = list(members)
        while frontier:
            current = frontier.pop()
            close = [i for i in remaining
                     if math.hypot(*(points[i] - points[current])) < max_gap_m]
            for i in close:
                remaining.remove(i)
            members.extend(close)
            frontier.extend(close)
        clusters.append(sorted(members))
    return clusters



@dataclass
class TrackMeasurement:

    t_local: float
    xy: Optional[np.ndarray] = None
    dopplers: List[Tuple[np.ndarray, float]] = field(default_factory=list)
    n_returns: int = 0
    near_clearance: Optional[float] = None
    surface_offset: Optional[float] = None
    radar: Optional[str] = None
    radars: Tuple[str, ...] = ()
    points: Optional[np.ndarray] = field(default=None, repr=False, compare=False)
    origins: Optional[np.ndarray] = field(default=None, repr=False, compare=False)
    competing: bool = False
    doppler_var: float = 0.0
    manoeuvre_dt: Optional[float] = None
    impulse_var: float = 0.0
    velocity_rows: List[Tuple[np.ndarray, float, float]] = field(default_factory=list)


def _transition(dt: float) -> np.ndarray:
    matrix = np.eye(4)
    matrix[0, 2] = matrix[1, 3] = dt
    return matrix


def kf_predict(x: np.ndarray, P: np.ndarray, dt: float, acceleration_std: float) -> Tuple[np.ndarray, np.ndarray]:
    F = _transition(dt)
    G = np.array([[0.5 * dt * dt, 0.0], [0.0, 0.5 * dt * dt], [dt, 0.0], [0.0, dt]])
    Q = (acceleration_std ** 2) * (G @ G.T)
    return F @ x, F @ P @ F.T + Q


def kf_update(x: np.ndarray, P: np.ndarray, z: np.ndarray, H: np.ndarray, R: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    S = H @ P @ H.T + R
    K = P @ H.T @ np.linalg.inv(S)
    x_new = x + K @ (z - H @ x)
    I_KH = np.eye(len(x)) - K @ H
    return x_new, I_KH @ P @ I_KH.T + K @ R @ K.T


def velocity_profile(points: np.ndarray, origins: np.ndarray, radial: np.ndarray,
                     cfg: TrackingConfig) -> List[Tuple[np.ndarray, float, float]]:
    lines = points - origins
    lines = lines / np.maximum(np.hypot(lines[:, 0], lines[:, 1]), 1e-6)[:, None]
    keep = np.ones(len(radial), dtype=bool)
    velocity = None
    for _ in range(2):
        U, r = lines[keep], radial[keep]
        info = U.T @ U
        if len(r) < 2 or np.linalg.eigvalsh(info)[-1] < 1e-9:
            break
        velocity = np.linalg.lstsq(U, r, rcond=None)[0]
        residual = np.abs(radial - lines @ velocity)
        scale = max(cfg.radial_speed_std_mps, 1.4826 * float(np.median(residual[keep])))
        new = residual <= 3.0 * scale
        if new.sum() < 2 or (new == keep).all():
            break
        keep = new
    if velocity is None:
        line = np.median(lines, axis=0)
        line = line / max(float(np.linalg.norm(line)), 1e-6)
        return [(line, float(np.median(radial)), cfg.radial_speed_std_mps ** 2)]
    info = lines[keep].T @ lines[keep]
    values, vectors = np.linalg.eigh(info)
    rows = []
    for value, vector in zip(values, vectors.T):
        variance = cfg.radial_speed_std_mps ** 2 / max(float(value), 1e-9)
        rows.append((vector, float(vector @ velocity), max(variance, cfg.radial_speed_std_mps ** 2)))
    return rows


def _measurement_model(measurement: TrackMeasurement, cfg: TrackingConfig) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    rows = [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]]
    values = [measurement.xy[0], measurement.xy[1]]
    variances = [cfg.measurement_std_m ** 2] * 2
    doppler_rows = measurement.velocity_rows or [(line, radial, cfg.radial_speed_std_mps ** 2)
                                                 for line, radial in measurement.dopplers]
    for line, value, variance in doppler_rows:
        rows.append([0.0, 0.0, float(line[0]), float(line[1])])
        values.append(value)
        variances.append(variance + measurement.doppler_var)
    R = np.diag(variances)
    if measurement.origins is not None and len(measurement.origins):
        R[:2, :2] += polar_covariances(np.asarray(measurement.xy, float)[None, :],
                                       np.median(measurement.origins, axis=0)[None, :], cfg)[0]
    return np.array(rows), np.array(values, dtype=float), R


def _initial_state(measurement: TrackMeasurement, cfg: TrackingConfig) -> Tuple[np.ndarray, np.ndarray]:
    x = np.array([measurement.xy[0], measurement.xy[1], 0.0, 0.0])
    P = np.diag([cfg.measurement_std_m ** 2] * 2 + [INITIAL_VELOCITY_STD_MPS ** 2] * 2)
    if measurement.velocity_rows:
        info = np.eye(2) / INITIAL_VELOCITY_STD_MPS ** 2
        vector = np.zeros(2)
        for line, value, variance in measurement.velocity_rows:
            line = np.asarray(line, dtype=float)
            info += np.outer(line, line) / variance
            vector += line * value / variance
        cov = np.linalg.inv(info)
        x[2:] = cov @ vector
        P[2:, 2:] = cov
    elif measurement.dopplers:
        line, radial = measurement.dopplers[0]
        x[2:] = radial * np.asarray(line, dtype=float)
    return x, P


def manoeuvre_noise(x: np.ndarray, P: np.ndarray, dt: float, cfg: TrackingConfig) -> np.ndarray:
    speed = float(np.hypot(x[2], x[3]))
    if speed < 1e-6:
        return P
    unit = np.array([x[2], x[3]]) / speed
    outer = np.outer(unit, unit)
    dv = cfg.max_braking_mps2 * dt
    out = P.copy()
    out[2:, 2:] += dv * dv * outer
    out[:2, :2] += (0.5 * dv * dt) ** 2 * outer
    return out


def impulse_noise(P: np.ndarray, variance: float, dt: float) -> np.ndarray:
    out = P.copy()
    out[2:, 2:] += variance * np.eye(2)
    out[:2, :2] += variance * dt * dt * np.eye(2)
    return out


def filter_and_smooth(measurements: Sequence[TrackMeasurement], cfg: TrackingConfig) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    boundaries = set()
    last_competing = measurements[0].t_local if measurements[0].competing else -math.inf
    x, P = _initial_state(measurements[0], cfg)
    predicted_x, predicted_P, filtered_x, filtered_P = [x], [P], [x], [P]
    for previous, current in zip(measurements, measurements[1:]):
        x, P = kf_predict(x, P, current.t_local - previous.t_local, cfg.acceleration_std_mps2)
        if current.manoeuvre_dt is not None:
            P = manoeuvre_noise(x, P, current.manoeuvre_dt, cfg)
        if current.impulse_var > 0.0:
            P = impulse_noise(P, current.impulse_var, current.t_local - previous.t_local)
            boundaries.add(len(filtered_x))
        predicted_x.append(x)
        predicted_P.append(P)
        if current.xy is not None:
            H, z, R = _measurement_model(current, cfg)
            if current.competing:
                last_competing = current.t_local
            if (current.t_local - last_competing <= cfg.max_track_gap_s
                    and len(filtered_x) >= cfg.min_track_frames and len(z) > 2):
                innovation = z[2:] - H[2:] @ x
                variance = np.diag(H[2:] @ P @ H[2:].T + R[2:, 2:])
                if np.any(np.abs(innovation) > cfg.smoothing_innovation_sigma * np.sqrt(variance)):
                    boundaries.add(len(filtered_x))
            x, P = kf_update(x, P, z, H, R)
        filtered_x.append(x)
        filtered_P.append(P)

    smoothed_x = list(filtered_x)
    smoothed_P = list(filtered_P)
    for k in range(len(measurements) - 2, -1, -1):
        if k + 1 in boundaries:
            continue
        F = _transition(measurements[k + 1].t_local - measurements[k].t_local)
        gain = filtered_P[k] @ F.T @ np.linalg.inv(predicted_P[k + 1])
        smoothed_x[k] = filtered_x[k] + gain @ (smoothed_x[k + 1] - predicted_x[k + 1])
        smoothed_P[k] = filtered_P[k] + gain @ (smoothed_P[k + 1] - predicted_P[k + 1]) @ gain.T
    return np.array(smoothed_x), np.array(smoothed_P), np.array(filtered_x)



def kf_predict_speed(x: np.ndarray, P: np.ndarray, dt: float, acceleration_std: float,
                     yaw_rate_std: float) -> Tuple[np.ndarray, np.ndarray]:
    F = _transition(dt)
    speed = float(np.hypot(x[2], x[3]))
    along, across = acceleration_std ** 2, acceleration_std ** 2 + (speed * yaw_rate_std) ** 2
    if speed > 1e-6:
        c, s = x[2] / speed, x[3] / speed
        rot = np.array([[c, -s], [s, c]])
        A = rot @ np.diag([along, across]) @ rot.T
    else:
        A = np.eye(2) * across
    G = np.array([[0.5 * dt * dt, 0.0], [0.0, 0.5 * dt * dt], [dt, 0.0], [0.0, dt]])
    return F @ x, F @ P @ F.T + G @ A @ G.T


class _ActiveTrack:

    def __init__(self, birth_order: int, first: TrackMeasurement, cfg: TrackingConfig,
                 lanes: Optional[Callable[[float, float], Sequence[float]]] = None) -> None:
        self.birth_order = birth_order
        self.track_id: Optional[str] = None
        self.x, self.P = _initial_state(first, cfg)
        if lanes is not None:
            self.x, self.P = lane_velocity_prior(self.x, self.P, first, lanes(float(first.xy[0]), float(first.xy[1])),
                                                 cfg)
        self.t_local = first.t_local
        self.measurements = [first]
        self.n_updates = 1
        self.last_update_t = first.t_local
        self.P_update = self.P.copy()
        self.held_heading: Optional[Tuple[float, float]] = None
        self.inside_known = 0
        self.stopped_since: Optional[float] = None
        self._static_run: Optional[float] = None
        self.lanes = lanes
        self._hold(cfg)

    def _hold(self, cfg: TrackingConfig) -> None:
        heading = velocity_heading(self.x, self.P, cfg)
        if heading is not None:
            self.held_heading = heading

    def heading(self, cfg: TrackingConfig) -> Optional[Tuple[float, float]]:
        own = velocity_heading(self.x, self.P, cfg) or self.held_heading
        lanes = self.lanes(float(self.x[0]), float(self.x[1])) if self.lanes is not None else ()
        return body_heading(own, lanes, cfg)

    def predict(self, t_local: float, cfg: TrackingConfig) -> None:
        self.x, self.P = kf_predict_speed(self.x, self.P, t_local - self.t_local, cfg.acceleration_std_mps2,
                                          cfg.yaw_rate_std_rps)
        self.t_local = t_local

    def update(self, measurement: TrackMeasurement, cfg: TrackingConfig) -> None:
        if measurement.manoeuvre_dt is not None:
            self.P = manoeuvre_noise(self.x, self.P, measurement.manoeuvre_dt, cfg)
        if measurement.impulse_var > 0.0:
            self.P = impulse_noise(self.P, measurement.impulse_var, measurement.t_local - self.last_update_t)
        H, z, R = _measurement_model(measurement, cfg)
        self.x, self.P = kf_update(self.x, self.P, z, H, R)
        self.measurements.append(measurement)
        self.n_updates += 1
        self.last_update_t = measurement.t_local
        self.P_update = self.P.copy()
        self._hold(cfg)
        static = bool(measurement.dopplers) and all(abs(r) < cfg.moving_speed_mps for _, r in measurement.dopplers)
        self._static_run = (self._static_run if self._static_run is not None else measurement.t_local) if static else None
        if float(np.hypot(self.x[2], self.x[3])) >= cfg.moving_speed_mps:
            self.stopped_since = None
        elif self.stopped_since is None and self.held_heading is not None:
            self.stopped_since = self._static_run if self._static_run is not None else measurement.t_local

    def coasting_spread(self) -> float:
        grown = self.P[:2, :2] - self.P_update[:2, :2]
        return math.sqrt(max(float(np.linalg.eigvalsh(0.5 * (grown + grown.T))[-1]), 0.0))

    def miss(self, sweep: RadarSweep) -> None:
        self.measurements.append(TrackMeasurement(t_local=sweep.t_local))


def _unit_lines(points: np.ndarray, origins: np.ndarray) -> np.ndarray:
    lines = points - origins
    return lines / np.maximum(np.hypot(lines[:, 0], lines[:, 1]), 1e-6)[:, None]



def chi2_quantile(probability: float, dof: int) -> float:
    if dof == 2:
        return -2.0 * math.log(1.0 - probability)
    lo, hi = 0.0, 20.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if math.erf(mid / math.sqrt(2.0)) < probability:
            lo = mid
        else:
            hi = mid
    return ((lo + hi) / 2.0) ** 2


def polar_covariances(points: np.ndarray, origins: np.ndarray, cfg: TrackingConfig) -> np.ndarray:
    lines = points - origins
    r = np.maximum(np.hypot(lines[:, 0], lines[:, 1]), 1e-6)
    c, s = lines[:, 0] / r, lines[:, 1] / r
    sr2, sa2 = cfg.radar_range_std_m ** 2, (r * math.radians(cfg.radar_azimuth_std_deg)) ** 2
    out = np.empty((len(points), 2, 2))
    out[:, 0, 0] = c * c * sr2 + s * s * sa2
    out[:, 1, 1] = s * s * sr2 + c * c * sa2
    out[:, 0, 1] = out[:, 1, 0] = c * s * (sr2 - sa2)
    return out


def velocity_heading(state: np.ndarray, P: np.ndarray, cfg: TrackingConfig) -> Optional[Tuple[float, float]]:
    speed = float(np.hypot(state[2], state[3]))
    if speed < cfg.moving_speed_mps:
        return None
    across = np.array([-state[3], state[2]]) / speed
    return math.atan2(state[3], state[2]), float(across @ P[2:, 2:] @ across) / (speed * speed)


def lane_velocity_prior(x: np.ndarray, P: np.ndarray, first: TrackMeasurement, lanes: Sequence[float],
                        cfg: TrackingConfig) -> Tuple[np.ndarray, np.ndarray]:
    if not lanes or not first.dopplers:
        return x, P
    sigma = math.radians(cfg.lane_heading_std_deg)
    axis = lanes[0]
    for lane in lanes[1:]:
        gap = (lane - axis + 0.5 * math.pi) % math.pi - 0.5 * math.pi
        if abs(gap) > sigma:
            return x, P
    d = np.array([math.cos(axis), math.sin(axis)])
    line, radial = first.dopplers[0]
    projection = float(np.asarray(line, dtype=float) @ d)
    if abs(projection) >= 0.3:
        speed = radial / projection
        along_var = (cfg.radial_speed_std_mps / abs(projection)) ** 2
    else:
        speed, along_var = 0.0, INITIAL_VELOCITY_STD_MPS ** 2
    across_std = max(abs(speed), math.sqrt(along_var)) * math.sin(sigma)
    rot = np.array([[d[0], -d[1]], [d[1], d[0]]])
    out_x, out_P = x.copy(), P.copy()
    out_x[2:] = speed * d
    out_P[2:, 2:] = rot @ np.diag([along_var, across_std ** 2]) @ rot.T
    out_P[:2, 2:] = 0.0
    out_P[2:, :2] = 0.0
    return out_x, out_P


def body_heading(own: Optional[Tuple[float, float]], lanes: Sequence[float],
                 cfg: TrackingConfig) -> Optional[Tuple[float, float]]:
    prior = math.radians(cfg.lane_heading_std_deg) ** 2
    if not lanes:
        return own
    if own is None:
        return float(lanes[0]), prior
    theta, variance = own

    def axis_gap(lane: float) -> float:
        return (lane - theta + 0.5 * math.pi) % math.pi - 0.5 * math.pi

    gap = min((axis_gap(lane) for lane in lanes), key=abs)
    if gap * gap > 9.0 * (variance + prior):
        return own
    weight = variance / (variance + prior)
    return theta + weight * gap, variance * prior / (variance + prior)


def body_covariance(state: np.ndarray, cfg: TrackingConfig,
                    heading: Optional[Tuple[float, float]] = None) -> np.ndarray:
    a, b = cfg.body_length_m ** 2 / 12.0, cfg.body_width_m ** 2 / 12.0
    if heading is None:
        return np.eye(2) * a
    theta, variance = heading
    rho = math.exp(-2.0 * variance)
    along, across = 0.5 * (a + b) + 0.5 * (a - b) * rho, 0.5 * (a + b) - 0.5 * (a - b) * rho
    c, s = math.cos(theta), math.sin(theta)
    rot = np.array([[c, -s], [s, c]])
    return rot @ np.diag([along, across]) @ rot.T


def covariance_gate(track: "_ActiveTrack", sweep: "RadarSweep", cfg: TrackingConfig,
                    ego_variance: float = 0.0, full: bool = False) -> Tuple[np.ndarray, ...]:
    nu = sweep.points - track.x[:2]
    heading = track.heading(cfg)
    spread = 2.0 * body_covariance(track.x, cfg, None if heading is None else (heading[0], 0.0))
    S = track.P[:2, :2][None, :, :] + spread[None, :, :] + polar_covariances(sweep.points, sweep.origins, cfg)
    det = S[:, 0, 0] * S[:, 1, 1] - S[:, 0, 1] * S[:, 1, 0]
    d2 = (S[:, 1, 1] * nu[:, 0] ** 2 - 2.0 * S[:, 0, 1] * nu[:, 0] * nu[:, 1] + S[:, 0, 0] * nu[:, 1] ** 2) / np.maximum(det, 1e-12)
    u = _unit_lines(sweep.points, sweep.origins)
    predicted = u @ track.x[2:]
    var_r = np.einsum("ni,ij,nj->n", u, track.P[2:, 2:], u) + cfg.radial_speed_std_mps ** 2 + ego_variance
    residual = sweep.radial_speed - predicted
    radial2 = residual ** 2 / var_r
    if full:
        return d2, radial2, np.hypot(nu[:, 0], nu[:, 1]), np.log(np.maximum(det, 1e-12)), np.log(var_r), np.abs(residual)
    return d2, radial2, np.hypot(nu[:, 0], nu[:, 1])


def on_body(track: "_ActiveTrack", points: np.ndarray, cfg: TrackingConfig, widen: bool = True,
            turned: bool = True) -> np.ndarray:
    margin = 3.0 * math.sqrt(max(float(np.linalg.eigvalsh(track.P[:2, :2])[-1]), 0.0)) if widen else 0.0
    offsets = points - track.x[:2]
    heading = track.heading(cfg)
    if heading is None:
        return np.hypot(offsets[:, 0], offsets[:, 1]) <= cfg.body_length_m + margin
    theta, variance = heading
    turn = math.sin(min(3.0 * math.sqrt(max(variance, 0.0)), 0.5 * math.pi)) if turned else 0.0
    c, s = math.cos(theta), math.sin(theta)
    along, across = offsets @ np.array([c, s]), offsets @ np.array([-s, c])
    return ((np.abs(along) <= cfg.body_length_m + cfg.body_width_m * turn + margin)
            & (np.abs(across) <= cfg.body_width_m + cfg.body_length_m * turn + margin))


def _measurement_from_returns(sweep: RadarSweep, mask: np.ndarray, cfg: TrackingConfig) -> TrackMeasurement:
    xy = np.median(sweep.points[mask], axis=0)
    dopplers = []
    counts = []
    rows = []
    for k in sorted(set(sweep.radar[mask].tolist())):
        own = mask & (sweep.radar == k)
        line = np.median(sweep.points[own], axis=0) - sweep.origins[own][0]
        line = line / max(float(np.linalg.norm(line)), 1e-6)
        counts.append((int(own.sum()), k))
        dopplers.append((int(own.sum()), line, float(np.median(sweep.radial_speed[own]))))
        rows.append((int(own.sum()), velocity_profile(sweep.points[own], sweep.origins[own],
                                                      sweep.radial_speed[own], cfg)))
    dopplers.sort(key=lambda item: -item[0])
    rows.sort(key=lambda item: -item[0])
    clearances = sweep.clearance[mask]
    near = float(np.percentile(clearances, NEAR_SURFACE_PERCENTILE))
    offset = max(float(np.median(clearances)) - near, 0.0)
    main = max(counts)[1]
    return TrackMeasurement(t_local=sweep.t_local, xy=xy, dopplers=[(line, radial) for _, line, radial in dopplers],
                            velocity_rows=[row for _, profile in rows for row in profile],
                            n_returns=int(mask.sum()), near_clearance=near, surface_offset=offset,
                            radar=sweep.radars[main] if sweep.radars else str(main),
                            radars=tuple(sorted(sweep.radars[k] if sweep.radars else str(k) for _, k in counts)),
                            points=sweep.points[mask].copy(), origins=sweep.origins[mask].copy())


def _manoeuvre_gate(track: _ActiveTrack, sweep: RadarSweep, candidates: np.ndarray, rivals: np.ndarray,
                    period: float, cfg: TrackingConfig, ego_variance: float = 0.0) -> np.ndarray:
    dt = sweep.t_local - track.last_update_t
    speed = float(np.hypot(track.x[2], track.x[3]))
    if track.track_id is None or not len(sweep.points) or dt > 1.5 * period + 1e-6 or speed < cfg.moving_speed_mps:
        return np.zeros(len(sweep.points), dtype=bool)
    d2, _, euclid = covariance_gate(track, sweep, cfg)
    near = (candidates & ~rivals & (d2 <= chi2_quantile(cfg.gate_probability, 2)) & (euclid <= cfg.position_cap_m)
            & on_body(track, sweep.points, cfg))
    u = _unit_lines(sweep.points, sweep.origins)
    predicted = u @ track.x[2:]
    slowed = predicted * (1.0 - min(1.0, cfg.max_braking_mps2 * dt / speed))
    tolerance = math.sqrt(chi2_quantile(cfg.gate_probability, 1)) * np.sqrt(
        np.einsum("ni,ij,nj->n", u, track.P[2:, 2:], u) + cfg.radial_speed_std_mps ** 2 + ego_variance)
    lo, hi = np.minimum(predicted, slowed) - tolerance, np.maximum(predicted, slowed) + tolerance
    return near & (sweep.radial_speed >= lo) & (sweep.radial_speed <= hi)


def _impact_gate(track: _ActiveTrack, sweep: RadarSweep, candidates: np.ndarray, rivals: np.ndarray,
                 period: float, cfg: TrackingConfig, ego_variance: float = 0.0) -> Tuple[np.ndarray, float]:
    none = (np.zeros(len(sweep.points), dtype=bool), 0.0)
    dt = sweep.t_local - track.last_update_t
    speed = float(np.hypot(track.x[2], track.x[3]))
    if track.track_id is None or not len(sweep.points) or dt > 1.5 * period + 1e-6 or speed < cfg.moving_speed_mps:
        return none
    d2, _, euclid = covariance_gate(track, sweep, cfg)
    near = (candidates & ~rivals & (d2 <= chi2_quantile(cfg.gate_probability, 2)) & (euclid <= cfg.position_cap_m)
            & on_body(track, sweep.points, cfg))
    taken = near & (np.abs(sweep.radial_speed) >= cfg.moving_speed_mps)
    counts = [m.n_returns for m in track.measurements[-5:] if m.xy is not None]
    if not counts or int(taken.sum()) < max(2, math.ceil(0.5 * float(np.median(counts)))):
        return none
    u = _unit_lines(sweep.points[taken], sweep.origins[taken])
    tolerance = math.sqrt(chi2_quantile(cfg.gate_probability, 1)) * np.sqrt(
        np.einsum("ni,ij,nj->n", u, track.P[2:, 2:], u) + cfg.radial_speed_std_mps ** 2 + ego_variance)
    change = np.abs(sweep.radial_speed[taken] - u @ track.x[2:]) - tolerance
    if float(change.max()) <= 0.0:
        return none
    return taken, float(change.max()) ** 2


def _may_touch(track: _ActiveTrack, pose: EgoState, footprint: Optional[EgoFootprint], cfg: TrackingConfig) -> bool:
    c, s = math.cos(pose.heading), math.sin(pose.heading)
    dx, dy = track.x[0] - pose.x, track.x[1] - pose.y
    vx, vy = c * dx + s * dy, -s * dx + c * dy
    if footprint is None:
        return math.hypot(vx, vy) <= cfg.body_length_m
    depth = next((m.surface_offset for m in reversed(track.measurements) if m.surface_offset is not None), 0.0)
    near = float(footprint.distance(vx, vy)) - depth
    sigma = math.sqrt(max(float(np.linalg.eigvalsh(track.P[:2, :2])[-1]), 0.0))
    return near <= cfg.contact_clearance_m + 3.0 * sigma


def _impact_kicks(sweeps: Sequence[RadarSweep], impacts: Optional[Sequence[Tuple[float, float]]],
                  cfg: TrackingConfig) -> Dict[int, float]:
    kicks: Dict[int, float] = {}
    if not impacts:
        return kicks
    times = [sweep.t_local for sweep in sweeps]
    for t, impulse in impacts:
        k = int(np.searchsorted(times, t - 1e-9))
        if k < len(times):
            kicks[k] = kicks.get(k, 0.0) + float(impulse) / cfg.nominal_vehicle_mass_kg
    return {k: v * v for k, v in kicks.items()}


def _statistical_assignment(ordered: Sequence[_ActiveTrack], sweep: RadarSweep, free: np.ndarray,
                            cfg: TrackingConfig, ego_variance: float,
                            stats: Optional[Dict[str, int]],
                            period: float = 0.05,
                            static_since: Optional[np.ndarray] = None) -> Tuple[List[np.ndarray], np.ndarray, np.ndarray, List[Optional[str]], List[float]]:
    n = len(sweep.points)
    masks: List[np.ndarray] = []
    loglik = np.full((len(ordered), n), -np.inf)
    if not n or not ordered:
        return ([np.zeros(n, dtype=bool) for _ in ordered], np.full(n, -1, dtype=int), np.zeros(n, dtype=bool),
                [None] * len(ordered), [0.0] * len(ordered))
    g2, r2 = chi2_quantile(cfg.gate_probability, 2), chi2_quantile(cfg.gate_probability, 1)
    position_gates = []
    for k, track in enumerate(ordered):
        d2, radial2, euclid, logdet, logvar, residual = covariance_gate(track, sweep, cfg, ego_variance, full=True)
        position_gates.append(d2 <= g2)
        statistical = free & (d2 <= g2) & (radial2 <= r2)
        gate = statistical & (euclid <= cfg.position_cap_m) & (residual <= cfg.doppler_cap_mps)
        if track.track_id is not None and float(np.hypot(track.x[2], track.x[3])) < cfg.moving_speed_mps:
            gate &= on_body(track, sweep.points, cfg)
            if static_since is not None and track.stopped_since is not None:
                gate &= ~(static_since < track.stopped_since - cfg.max_track_gap_s)
        if stats is not None:
            stats["cap_rejections"] = stats.get("cap_rejections", 0) + int((statistical & ~gate).sum())
        if track.track_id is None:
            gate &= np.abs(sweep.radial_speed) >= cfg.moving_speed_mps
        masks.append(gate)
        loglik[k] = np.where(gate, -0.5 * (d2 + radial2 + logdet + logvar), -np.inf)
    confirmed = np.array([track.track_id is not None for track in ordered], dtype=bool)
    if confirmed.any():
        claimed = np.isfinite(loglik[confirmed]).any(axis=0)
        loglik[~confirmed] = np.where(claimed[None, :], -np.inf, loglik[~confirmed])
    winners = np.argmax(loglik, axis=0)
    ambiguous = np.zeros(n, dtype=bool)
    if len(ordered) > 1:
        ranked = np.sort(loglik, axis=0)
        best, second = ranked[-1], ranked[-2]
        gap = np.where(np.isfinite(second), best - np.where(np.isfinite(second), second, 0.0), np.inf)
        ambiguous = gap < math.log(cfg.return_likelihood_ratio)
        if stats is not None:
            stats["ambiguous_returns"] = stats.get("ambiguous_returns", 0) + int(ambiguous.sum())
    winners = np.where(np.isfinite(loglik.max(axis=0)) & ~ambiguous, winners, -1)
    masks = [mask & ~ambiguous for mask in masks]
    manoeuvring: List[Optional[str]] = [None] * len(ordered)
    impulses = [0.0] * len(ordered)
    for k, track in enumerate(ordered):
        if (masks[k] & (winners == k)).any():
            continue
        rivals = np.zeros(n, dtype=bool)
        for j, gate in enumerate(position_gates):
            if j != k:
                rivals |= gate
        unclaimed = free & ~ambiguous & (winners < 0)
        braking = _manoeuvre_gate(track, sweep, unclaimed, rivals, period, cfg, ego_variance)
        impulse = 0.0
        if braking.any():
            manoeuvring[k] = "braking"
        else:
            braking, impulse = _impact_gate(track, sweep, unclaimed, rivals, period, cfg, ego_variance)
            if braking.any():
                manoeuvring[k], impulses[k] = "impact", impulse
        if braking.any():
            masks[k] = braking
            winners = np.where(braking, k, winners)
    return masks, winners, ambiguous, manoeuvring, impulses


def associate_returns(sweeps: Sequence[RadarSweep], cfg: TrackingConfig,
                      impacts: Optional[Sequence[Tuple[float, float]]] = None,
                      footprint: Optional["EgoFootprint"] = None, ego: Optional["EgoTrajectory"] = None,
                      stats: Optional[Dict[str, int]] = None,
                      trace: Optional[List[Dict[str, Any]]] = None,
                      lane_headings: Optional[Callable[[float, float], Sequence[float]]] = None) -> List[_ActiveTrack]:
    active: List[_ActiveTrack] = []
    finished: List[_ActiveTrack] = []
    births = 0
    confirmed = 0
    kicks = _impact_kicks(sweeps, impacts, cfg)
    g2 = chi2_quantile(cfg.gate_probability, 2)
    times = [sweep.t_local for sweep in sweeps]
    period = float(np.median(np.diff(times))) if len(times) > 1 else 0.05
    cell = cfg.measurement_std_m
    first_static: Dict[Tuple[int, int], float] = {}
    for sweep in sweeps:
        for (x, y), speed in zip(sweep.points, sweep.radial_speed):
            if abs(speed) < cfg.moving_speed_mps:
                first_static.setdefault((int(round(x / cell)), int(round(y / cell))), sweep.t_local)
    lanes: Optional[Callable[[float, float], Sequence[float]]] = None
    if lane_headings is not None:
        from functools import lru_cache

        @lru_cache(maxsize=None)
        def _lanes_at(ix: int, iy: int) -> Tuple[float, ...]:
            return tuple(lane_headings(ix * cell, iy * cell))

        def _lanes(x: float, y: float) -> Tuple[float, ...]:
            return _lanes_at(int(round(x / cell)), int(round(y / cell)))
        lanes = _lanes
    for index, sweep in enumerate(sweeps):
        free = np.ones(len(sweep.points), dtype=bool)
        ordered = sorted(active, key=lambda item: (item.track_id is None, item.birth_order))
        for track in ordered:
            track.predict(sweep.t_local, cfg)
            if index in kicks and ego is not None and _may_touch(track, ego.at(sweep.t_local), footprint, cfg):
                track.P[2:, 2:] += np.eye(2) * kicks[index]
                dt = sweep.t_local - (sweeps[index - 1].t_local if index else sweep.t_local)
                track.P[:2, :2] += np.eye(2) * kicks[index] * dt * dt
        static_since = None
        if len(sweep.points):
            keys = [(int(round(x / cell)), int(round(y / cell))) for x, y in sweep.points]
            static_since = np.array([first_static.get(key, math.inf) for key in keys])
        masks, winners, ambiguous, manoeuvring, impulses = _statistical_assignment(ordered, sweep, free, cfg,
                                                                        kicks.get(index, 0.0), stats, period,
                                                                        static_since)
        free &= ~ambiguous
        record: Optional[Dict[str, Any]] = None
        if trace is not None:
            record = {"t": sweep.t_local, "owner": np.where(ambiguous, "AMBIG", "").astype(object), "ended": [],
                      "born": [], "confirmed": [], "manoeuvre": [],
                      "pred": {(tr.track_id or "tent%d" % tr.birth_order): (tr.x.copy(), tr.coasting_spread())
                               for tr in ordered}}
            trace.append(record)
        confirmed_support = sum((mask.astype(int) for track, mask in zip(ordered, masks)
                                 if track.track_id is not None), np.zeros(len(sweep.points), dtype=int))
        for k, track in enumerate(ordered):
            mask = masks[k] & (winners == k)
            if mask.any():
                measurement = _measurement_from_returns(sweep, mask, cfg)
                measurement.competing = bool((masks[k] & (confirmed_support > 1)).any())
                measurement.doppler_var = kicks.get(index, 0.0)
                if manoeuvring[k] == "braking":
                    measurement.manoeuvre_dt = sweep.t_local - track.last_update_t
                elif manoeuvring[k] == "impact":
                    measurement.impulse_var = impulses[k]
                if manoeuvring[k] is not None and stats is not None:
                    key = "manoeuvre_updates" if manoeuvring[k] == "braking" else "impact_updates"
                    stats[key] = stats.get(key, 0) + 1
                track.update(measurement, cfg)
                free &= ~mask
                if record is not None:
                    record["owner"][mask] = track.track_id or "tent%d" % track.birth_order
                    if manoeuvring[k] is not None:
                        record["manoeuvre"].append((track.track_id, manoeuvring[k]))
                if track.track_id is None and any(
                        other.track_id is not None and bool(on_body(other, track.x[None, :2], cfg, False, False)[0])
                        for other in ordered):
                    track.inside_known += 1
            else:
                track.miss(sweep)
        survivors = []
        for track in active:
            lost = (sweep.t_local - track.last_update_t > cfg.gap_cap_s
                    or (sweep.t_local > track.last_update_t and 3.0 * track.coasting_spread() > cfg.body_width_m))
            if lost:
                if record is not None:
                    record["ended"].append((track.track_id or "tent%d" % track.birth_order,
                                            round(sweep.t_local - track.last_update_t, 3)))
                if track.track_id is not None:
                    finished.append(track)
            else:
                survivors.append(track)
        active = survivors
        candidates = free & (np.abs(sweep.radial_speed) >= cfg.moving_speed_mps)
        if len(sweep.points):
            for track in active:
                d2, _, _ = covariance_gate(track, sweep, cfg)
                candidates &= (d2 > g2) & ~on_body(track, sweep.points, cfg, turned=track.track_id is not None)
        indices = np.flatnonzero(candidates)
        for cluster in cluster_points(sweep.points[indices], cfg.cluster_distance_m):
            mask = np.zeros(len(sweep.points), dtype=bool)
            mask[indices[cluster]] = True
            births += 1
            active.append(_ActiveTrack(births, _measurement_from_returns(sweep, mask, cfg), cfg, lanes))
            if record is not None:
                record["owner"][mask] = "birth%d" % births
                record["born"].append(births)
        for track in active:
            ready = (track.last_update_t - track.measurements[0].t_local >= cfg.min_track_support_s - 1e-6
                     and track.n_updates >= cfg.min_track_updates)
            if ready and track.track_id is None:
                ready = (2 * track.inside_known < track.n_updates
                         and not any(other.track_id is not None
                                     and bool(on_body(other, track.x[None, :2], cfg, False, False)[0])
                                     for other in active))
            if track.track_id is None and ready:
                confirmed += 1
                track.track_id = "track_{0:03d}".format(confirmed)
                if record is not None:
                    record["confirmed"].append((track.birth_order, track.track_id))
    finished.extend(track for track in active if track.track_id is not None)
    return sorted(finished, key=lambda item: item.track_id)



NOT_WRITTEN = {"path_curvature"}


@dataclass
class TrackSample:

    t_local: float
    x_m: float
    y_m: float
    vx_mps: float
    vy_mps: float
    speed_mps: float
    pos_std_m: float
    vel_std_mps: float
    range_m: float
    bearing_deg: float
    longitudinal_m: float
    lateral_m: float
    closing_speed_mps: float
    closing_ttc_s: Optional[float]
    measured: bool
    n_returns: int
    meas_x_m: Optional[float] = None
    meas_y_m: Optional[float] = None
    clearance_m: Optional[float] = None
    ahead_m: Optional[float] = None
    surface_offset_m: float = 0.0
    radar: Optional[str] = None
    acceleration_mps2: float = 0.0
    relative_vx_mps: float = 0.0
    relative_vy_mps: float = 0.0
    occluded: bool = False
    identity_ambiguous: bool = False

    path_curvature: Optional[float] = None
    body_estimate: Optional[Tuple[float, float, float, float, float]] = None

    def __post_init__(self) -> None:
        if self.clearance_m is None:
            self.clearance_m = self.range_m
        if self.ahead_m is None:
            self.ahead_m = self.longitudinal_m

    def to_dict(self, track_id: str) -> Dict[str, Any]:
        out: Dict[str, Any] = {"track_id": track_id}
        for name, value in self.__dict__.items():
            if name in NOT_WRITTEN:
                continue
            out[name] = round(value, 3) if isinstance(value, float) else value
        return out


@dataclass
class LocalTrack:
    track_id: str
    samples: List[TrackSample]
    returns: List[Optional[Tuple[np.ndarray, np.ndarray]]] = field(default_factory=list, repr=False, compare=False)
    parent_track: Optional[str] = None
    identity_ambiguous: bool = False
    leader_spans: Optional[List[Tuple[float, Optional[float]]]] = field(default=None, repr=False, compare=False)
    lane_held: Dict[float, Tuple[float, float]] = field(default_factory=dict, repr=False, compare=False)
    lane_curvature: Dict[float, float] = field(default_factory=dict, repr=False, compare=False)

    def conflict_sample(self, sample: "TrackSample") -> "TrackSample":
        key = round(sample.t_local, 4)
        held, curvature = self.lane_held.get(key), self.lane_curvature.get(key)
        if held is None and curvature is None:
            return sample
        import dataclasses
        if held is not None:
            sample = dataclasses.replace(sample, vx_mps=held[0], vy_mps=held[1], speed_mps=math.hypot(*held))
        return dataclasses.replace(sample, path_curvature=curvature)

    def leader_at(self, t_local: float) -> Optional[bool]:
        if self.leader_spans is None:
            return None
        return any(a - 1e-6 <= t_local and (b is None or t_local <= b + 1e-6) for a, b in self.leader_spans)

    @property
    def first_t(self) -> float:
        return self.samples[0].t_local

    @property
    def last_t(self) -> float:
        return self.samples[-1].t_local

    def sample_near(self, t_local: float, tolerance_s: float = 0.026) -> Optional[TrackSample]:
        best = min(self.samples, key=lambda sample: abs(sample.t_local - t_local))
        return best if abs(best.t_local - t_local) <= tolerance_s else None

    def summary(self) -> Dict[str, Any]:
        measured = [sample for sample in self.samples if sample.measured]
        closest = min(self.samples, key=lambda sample: sample.range_m)
        nearest = min(self.samples, key=lambda sample: sample.clearance_m)
        return {"track_id": self.track_id,
                "parent_track": self.parent_track, "identity_ambiguous": self.identity_ambiguous,
                "first_seen_t_local": self.first_t, "last_seen_t_local": self.last_t,
                "duration_s": round(self.last_t - self.first_t, 3),
                "measured_sweeps": len(measured),
                "radar_returns": sum(sample.n_returns for sample in self.samples),
                "radars": sorted({sample.radar for sample in measured if sample.radar}),
                "min_range_m": round(closest.range_m, 2),
                "min_range_t_local": closest.t_local,
                "min_clearance_m": round(nearest.clearance_m, 2),
                "min_clearance_t_local": nearest.t_local,
                "max_speed_mps": round(max(sample.speed_mps for sample in self.samples), 2),
                "first_range_m": round(self.samples[0].range_m, 2),
                "first_bearing_deg": round(self.samples[0].bearing_deg, 1),
                "last_range_m": round(self.samples[-1].range_m, 2),
                "last_bearing_deg": round(self.samples[-1].bearing_deg, 1)}


def _relative_sample(t_local: float, state: np.ndarray, covariance: np.ndarray,
                     measurement: TrackMeasurement, ego: EgoTrajectory, radar_mount: Optional[RadarMount],
                     footprint: Optional[EgoFootprint] = None, surface_offset: float = 0.0,
                     acceleration: float = 0.0) -> TrackSample:
    own = ego.at(t_local)
    c, s = math.cos(own.heading), math.sin(own.heading)
    dx, dy = float(state[0]) - own.x, float(state[1]) - own.y
    x_v, y_v = c * dx + s * dy, -s * dx + c * dy
    dvx, dvy = float(state[2]) - own.vx, float(state[3]) - own.vy
    rel_x, rel_y = c * dvx + s * dvy, -s * dvx + c * dvy
    frame_vx, frame_vy = rel_x + own.yaw_rate * y_v, rel_y - own.yaw_rate * x_v
    if footprint is not None:
        distance = float(footprint.distance(x_v, y_v))
        nx, ny = footprint.outward(x_v, y_v)
        ahead = x_v - footprint.x_max
    else:
        distance = math.hypot(x_v, y_v)
        nx, ny = x_v / max(distance, 1e-6), y_v / max(distance, 1e-6)
        ahead = x_v
    closing = -(nx * frame_vx + ny * frame_vy)
    clearance = max(distance - surface_offset, 0.0)
    ttc = clearance / closing if closing > MIN_CLOSING_FOR_TTC_MPS else None
    if radar_mount is not None:
        origin = sensor_position(own, radar_mount)
        range_m = float(np.hypot(float(state[0]) - origin[0], float(state[1]) - origin[1]))
    else:
        range_m = math.hypot(x_v, y_v)
    return TrackSample(
        t_local=t_local, x_m=float(state[0]), y_m=float(state[1]),
        vx_mps=float(state[2]), vy_mps=float(state[3]), speed_mps=float(np.hypot(*state[2:])),
        pos_std_m=float(math.sqrt(max(covariance[0, 0] + covariance[1, 1], 0.0) / 2.0)),
        vel_std_mps=float(math.sqrt(max(covariance[2, 2] + covariance[3, 3], 0.0) / 2.0)),
        range_m=range_m, bearing_deg=math.degrees(math.atan2(y_v, x_v)),
        longitudinal_m=x_v, lateral_m=y_v, closing_speed_mps=closing,
        closing_ttc_s=None if ttc is None else round(ttc, 3),
        measured=measurement.xy is not None, n_returns=measurement.n_returns,
        meas_x_m=None if measurement.xy is None else round(float(measurement.xy[0]), 3),
        meas_y_m=None if measurement.xy is None else round(float(measurement.xy[1]), 3),
        clearance_m=clearance, ahead_m=ahead, surface_offset_m=surface_offset,
        radar=None if radar_mount is None else radar_mount.sensor_id, acceleration_mps2=acceleration,
        relative_vx_mps=rel_x, relative_vy_mps=rel_y)


def surface_offsets(measurements: Sequence[TrackMeasurement]) -> List[float]:
    measured = [index for index, m in enumerate(measurements) if m.surface_offset is not None]
    if not measured:
        return [0.0] * len(measurements)
    raw = [measurements[index].surface_offset for index in measured]
    smooth = [float(np.median(raw[max(k - SURFACE_OFFSET_HALF_WINDOW, 0):k + SURFACE_OFFSET_HALF_WINDOW + 1]))
              for k in range(len(raw))]
    out = []
    for index in range(len(measurements)):
        nearest = min(range(len(measured)), key=lambda k: abs(measured[k] - index))
        out.append(smooth[nearest])
    return out


def _along_velocity(times: np.ndarray, states: np.ndarray, index: int, lo: int, hi: int) -> float:
    velocity = states[index, 2:]
    speed = float(np.linalg.norm(velocity))
    if speed < 0.5:
        return float((np.linalg.norm(states[hi, 2:]) - np.linalg.norm(states[lo, 2:])) / (times[hi] - times[lo]))
    return float((states[hi, 2:] - states[lo, 2:]) @ (velocity / speed) / (times[hi] - times[lo]))


def accelerations(times: Sequence[float], states: np.ndarray, filtered: Optional[np.ndarray] = None) -> List[float]:
    times = np.asarray(times, dtype=float)
    out = []
    for index, t in enumerate(times):
        lo = int(np.searchsorted(times, t - ACCELERATION_HALF_WINDOW_S - 1e-6))
        hi = int(np.searchsorted(times, t + ACCELERATION_HALF_WINDOW_S + 1e-6)) - 1
        if hi <= lo or times[hi] - times[lo] < 1e-6:
            out.append(0.0)
            continue
        smoothed = _along_velocity(times, states, index, lo, hi)
        if filtered is None:
            out.append(smoothed)
            continue
        past = int(np.searchsorted(times, t - 2.0 * ACCELERATION_HALF_WINDOW_S - 1e-6))
        if index <= past or times[index] - times[past] < 1e-6:
            out.append(0.0)
            continue
        causal = _along_velocity(times, filtered, index, past, index)
        out.append(0.0 if smoothed * causal <= 0.0 else
                   (smoothed if abs(smoothed) < abs(causal) else causal))
    return out


def entanglements(tracks: Sequence["_ActiveTrack"], cfg: TrackingConfig) -> Dict[str, float]:
    out: Dict[str, float] = {}
    measured = {}
    for track in tracks:
        rows = [m for m in track.measurements if m.xy is not None]
        if rows:
            measured[track.track_id] = rows
    for loser, rows in measured.items():
        end = rows[-1]
        for winner, mine in measured.items():
            if winner == loser or mine[-1].t_local <= end.t_local + 1e-6 or mine[0].t_local > end.t_local + 1e-6:
                continue
            competing = any(m.competing and end.t_local - cfg.max_track_gap_s - 1e-6 <= m.t_local <= end.t_local + 1e-6
                            for m in mine)
            if not competing:
                continue
            near = min(mine, key=lambda m: abs(m.t_local - end.t_local))
            if float(np.hypot(*(np.asarray(near.xy) - np.asarray(end.xy)))) <= 0.5 * (cfg.body_length_m + cfg.body_width_m):
                out[winner] = min(out.get(winner, math.inf), end.t_local)
    return out


def identity_segments(measurements: Sequence[TrackMeasurement], states: np.ndarray,
                      cfg: TrackingConfig, ambiguous_after: Optional[float] = None) -> List[Tuple[int, int, bool]]:
    wide = []
    for i, (m, state) in enumerate(zip(measurements, states)):
        speed = float(np.hypot(*state[2:]))
        if m.points is None or len(m.points) < cfg.min_track_frames or speed < cfg.moving_speed_mps:
            continue
        transverse = m.points @ (np.array([-state[3], state[2]]) / speed)
        extent = float(np.percentile(transverse, 95) - np.percentile(transverse, 5))
        if extent > cfg.identity_body_width_m + cfg.measurement_std_m:
            wide.append(i)
    groups: List[List[int]] = []
    for i in wide:
        if not groups or measurements[i].t_local - measurements[groups[-1][-1]].t_local > cfg.max_track_gap_s:
            groups.append([])
        groups[-1].append(i)
    ambiguous = np.zeros(len(measurements), dtype=bool)
    times = np.array([m.t_local for m in measurements])
    if ambiguous_after is not None:
        ambiguous |= times > ambiguous_after + 1e-9
    for group in groups:
        if len(group) < cfg.min_track_frames:
            continue
        lo = measurements[group[0]].t_local - cfg.max_track_gap_s
        hi = measurements[group[-1]].t_local + cfg.max_track_gap_s
        ambiguous |= (times >= lo - 1e-9) & (times <= hi + 1e-9)
    cuts = [0] + [i for i in range(1, len(measurements)) if ambiguous[i] != ambiguous[i-1]] + [len(measurements)]
    return [(lo, hi, bool(ambiguous[lo])) for lo, hi in zip(cuts, cuts[1:])]


def build_local_tracks(streams: Sequence[RadarStream], ego: EgoTrajectory, clock_origin: float,
                       cfg: TrackingConfig, footprint: Optional[EgoFootprint] = None,
                       stats: Optional[Dict[str, Any]] = None,
                       impacts: Optional[Sequence[Tuple[float, float]]] = None,
                       lane_headings: Optional[Callable[[float, float], Sequence[float]]] = None) -> List[LocalTrack]:
    mounts = {stream.sensor_id: stream.mount for stream in streams}
    sweeps = radar_sweeps(streams, ego, clock_origin, cfg, footprint)
    if stats is not None:
        stats["own_body_returns_dropped"] = sum(sweep.own_body for sweep in sweeps)
    tracks = []
    association_stats: Dict[str, int] = {}
    raw_tracks = associate_returns(sweeps, cfg, impacts, footprint, ego, association_stats,
                                   lane_headings=lane_headings)
    if stats is not None and association_stats:
        stats["association"] = association_stats
    entangled = entanglements(raw_tracks, cfg)
    if stats is not None and entangled:
        stats["entanglements"] = {k: round(v, 3) for k, v in sorted(entangled.items())}
    for raw in raw_tracks:
        measurements = list(raw.measurements)
        while measurements[-1].xy is None:
            measurements.pop()
        initial, initial_covariances, initial_filtered = filter_and_smooth(measurements, cfg)
        pieces = identity_segments(measurements, initial, cfg, entangled.get(raw.track_id))
        for number, (lo, hi, ambiguous) in enumerate(pieces, 1):
            part = list(measurements[lo:hi])
            while part and part[0].xy is None:
                part.pop(0)
            while part and part[-1].xy is None:
                part.pop()
            if not part:
                continue
            states, covariances, filtered = ((initial, initial_covariances, initial_filtered) if len(pieces) == 1
                                            else filter_and_smooth(part, cfg))
            offsets = surface_offsets(part) if footprint is not None else [0.0] * len(part)
            acceleration = accelerations([m.t_local for m in part], states, filtered)
            samples, returns, radar = [], [], None
            for m, state, covariance, offset, accel in zip(part, states, covariances, offsets, acceleration):
                radar = m.radar or radar
                sample = _relative_sample(m.t_local, state, covariance, m, ego, mounts.get(radar), footprint, offset, accel)
                sample.identity_ambiguous = ambiguous
                samples.append(sample)
                returns.append(None if m.points is None else (m.points, m.origins))
            track_id = raw.track_id if len(pieces) == 1 else raw.track_id + '#segment_' + str(number)
            tracks.append(LocalTrack(track_id=track_id, samples=samples, returns=returns,
                                     parent_track=raw.track_id if len(pieces) > 1 else None,
                                     identity_ambiguous=ambiguous))
    return tracks
