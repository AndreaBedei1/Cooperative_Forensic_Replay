
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Sequence, Tuple

import numpy as np

from .config import SemanticsConfig
from .tracking import EgoFootprint, EgoState, TrackSample

MAX_SEARCH_DECELERATION_MPS2 = 30.0
BISECTION_STEPS = 14
HEADING_MIN_SPEED_MPS = 1.0
MAX_CURVATURE_PER_M = 0.2
OBLIQUE_VIEW_DEG = 20.0
DEFAULT_FOOTPRINT = EgoFootprint(-2.3, 2.3, -0.95, 0.95)

PREDICTED_OVERLAP = "PREDICTED_OVERLAP"
UNSAFE_FORWARD_GAP = "UNSAFE_FORWARD_GAP"
IN_PATH = "IN_PATH"
FRONT_LATERAL = "FRONT_LATERAL"


@dataclass
class ForwardGap:

    leader: bool
    region: Optional[str]
    longitudinal_clearance_m: float
    front_clearance_m: float
    lateral_body_gap_m: float
    lateral_approach_mps: float
    time_headway_s: Optional[float]
    minimum_time_gap_s: float
    time_gap_distance_m: float
    required_distance_m: float
    unsafe: bool
    released: bool

    @property
    def margin_m(self) -> float:
        return self.longitudinal_clearance_m - self.required_distance_m


@dataclass
class ConflictAssessment:

    encounter: str
    collision_course: bool
    ttc_s: Optional[float]
    overlap_s: Optional[Tuple[float, float]]
    required_deceleration_mps2: Optional[float]
    avoidance_by: Optional[str]
    available_deceleration_mps2: float
    critical: bool
    known: bool
    target_speed_mps: float
    target_acceleration_mps2: float
    ego_speed_mps: float
    forward: Optional[ForwardGap] = None
    occluded: bool = False
    critical_reason: Optional[str] = None
    inside_envelope: bool = False
    contact_imminent: bool = False

    @property
    def braking_margin_mps2(self) -> Optional[float]:
        if self.required_deceleration_mps2 is None or math.isinf(self.required_deceleration_mps2):
            return None
        return self.available_deceleration_mps2 - self.required_deceleration_mps2

    @property
    def forward_known(self) -> bool:
        return self.known and not self.occluded

    @property
    def at_rest(self) -> bool:
        return self.ego_speed_mps < HEADING_MIN_SPEED_MPS and self.target_speed_mps < HEADING_MIN_SPEED_MPS

    def overlap_released(self, release_deceleration_mps2: float) -> bool:
        if self.contact_imminent or (self.inside_envelope and not self.at_rest):
            return False
        return (not self.collision_course or self.required_deceleration_mps2 is None
                or self.required_deceleration_mps2 < release_deceleration_mps2)

    def forward_released(self) -> bool:
        if self.forward is None:
            return True
        return not self.occluded and self.forward.released

    def released(self, release_deceleration_mps2: float, forward_engaged: bool = True) -> bool:
        if not self.known:
            return False
        return (self.overlap_released(release_deceleration_mps2)
                and (not forward_engaged or self.forward_released()))


def minimum_time_gap_s(speed_mps: float, table: Sequence[Sequence[float]]) -> float:
    points = sorted((float(kmh), float(gap)) for kmh, gap in table)
    kmh = max(speed_mps, 0.0) * 3.6
    if kmh <= points[0][0]:
        return points[0][1]
    for (k0, t0), (k1, t1) in zip(points, points[1:]):
        if kmh <= k1:
            return t0 + (t1 - t0) * (kmh - k0) / (k1 - k0)
    return points[-1][1]


def safe_following_distance(ego_speed_mps: float, cfg: SemanticsConfig) -> Tuple[float, float, float]:
    ego_speed = max(ego_speed_mps, 0.0)
    time_gap = minimum_time_gap_s(ego_speed, cfg.critical_time_gap_table)
    distance = ego_speed * time_gap
    return time_gap, distance, max(distance, cfg.critical_min_following_distance_m)


def lateral_body_gap(y_min: float, y_max: float, half_width: float) -> float:
    return max(y_min - half_width, -half_width - y_max, 0.0)


def target_box(sample: TrackSample, own: EgoState, footprint: Optional[EgoFootprint],
               cfg: SemanticsConfig) -> Tuple[np.ndarray, np.ndarray, Tuple[float, float], float, float]:
    footprint = footprint or DEFAULT_FOOTPRINT
    c, s = math.cos(own.heading), math.sin(own.heading)
    tvx, tvy = c * sample.vx_mps + s * sample.vy_mps, -s * sample.vx_mps + c * sample.vy_mps
    tvy = math.copysign(max(abs(tvy) - sample.vel_std_mps, 0.0), tvy)
    speed = math.hypot(tvx, tvy)
    if sample.body_estimate is not None:
        x, y, heading, length, width = sample.body_estimate
        dx, dy = x - own.x, y - own.y
        angle = heading - own.heading
        return (np.array([c * dx + s * dy, -s * dx + c * dy]),
                np.array([math.cos(angle), math.sin(angle)]), (length / 2, width / 2), speed, angle)
    if speed >= HEADING_MIN_SPEED_MPS:
        ux, uy = tvx / speed, tvy / speed
    else:
        ux, uy = 1.0, 0.0
    nx, ny = footprint.outward(sample.longitudinal_m, sample.lateral_m)
    near = np.array([sample.longitudinal_m - sample.surface_offset_m * nx,
                     sample.lateral_m - sample.surface_offset_m * ny])
    length, width = cfg.target_length_m, cfg.target_width_m
    gx, gy = -nx, -ny
    along, across = gx * ux + gy * uy, gx * -uy + gy * ux
    oblique = math.sin(math.radians(OBLIQUE_VIEW_DEG))
    weight_along, weight_across = min(abs(along) / oblique, 1.0), min(abs(across) / oblique, 1.0)
    centre = (near - math.copysign(length / 2.0 * weight_along, along) * np.array([ux, uy])
              - math.copysign(width / 2.0 * weight_across, across) * np.array([-uy, ux]))
    return centre, np.array([ux, uy]), (length / 2.0, width / 2.0), speed, math.atan2(uy, ux)


def box_corners(centre: np.ndarray, unit: np.ndarray, half: Tuple[float, float]) -> np.ndarray:
    along, across = unit * half[0], np.array([-unit[1], unit[0]]) * half[1]
    return np.array([centre + along + across, centre + along - across, centre - along - across, centre - along + across])


def body_in_corridor(corners: np.ndarray, front: float, half_width: float) -> bool:
    clipped = []
    for a, b in zip(corners, np.roll(corners, -1, axis=0)):
        if a[0] >= front:
            clipped.append(a)
        if (a[0] >= front) != (b[0] >= front):
            clipped.append(a + (b - a) * (front - a[0]) / (b[0] - a[0]))
    if not clipped or float(np.max(corners[:, 0])) <= front:
        return False
    ys = np.asarray(clipped)[:, 1]
    return bool(np.min(ys) <= half_width and np.max(ys) >= -half_width)


def segment_hits_box(p0: np.ndarray, p1: np.ndarray, centre: np.ndarray, unit: np.ndarray,
                     half: Tuple[float, float]) -> bool:
    def local(point: np.ndarray) -> np.ndarray:
        d = point - centre
        return np.array([d[0] * unit[0] + d[1] * unit[1], -d[0] * unit[1] + d[1] * unit[0]])
    a, b = local(np.asarray(p0, dtype=float)), local(np.asarray(p1, dtype=float))
    d = b - a
    low, high = 0.0, 1.0
    for axis in (0, 1):
        for sign in (-1.0, 1.0):
            p = sign * d[axis]
            q = half[axis] - sign * a[axis]
            if abs(p) < 1e-12:
                if q < 0.0:
                    return False
                continue
            r = q / p
            if p < 0.0:
                low = max(low, r)
            else:
                high = min(high, r)
            if low > high:
                return False
    return True


def near_surface_point(sample: TrackSample, footprint: Optional[EgoFootprint]) -> np.ndarray:
    footprint = footprint or DEFAULT_FOOTPRINT
    nx, ny = footprint.outward(sample.longitudinal_m, sample.lateral_m)
    return np.array([sample.longitudinal_m - sample.surface_offset_m * nx,
                     sample.lateral_m - sample.surface_offset_m * ny])


def occluded_by(sample: TrackSample, own: EgoState, others: Sequence[TrackSample],
                footprint: Optional[EgoFootprint], cfg: SemanticsConfig) -> bool:
    footprint = footprint or DEFAULT_FOOTPRINT
    target = near_surface_point(sample, footprint)
    qx, qy = footprint.nearest(float(target[0]), float(target[1]))
    eye = np.array([float(qx), float(qy)])
    grow = cfg.occlusion_margin_m
    for other in others:
        centre, unit, half, _, _ = target_box(other, own, footprint, cfg)
        if segment_hits_box(eye, target, centre, unit, (half[0] + grow, half[1] + grow)):
            return True
    return False


def _corners(half_x: float, half_y: float) -> np.ndarray:
    return np.array([[half_x, half_y], [half_x, -half_y], [-half_x, -half_y], [-half_x, half_y]])


def _overlap(centre_a: np.ndarray, angle_a: np.ndarray, half_a: Tuple[float, float],
             centre_b: np.ndarray, angle_b, half_b: Tuple[float, float]) -> np.ndarray:
    ca, sa = np.cos(angle_a), np.sin(angle_a)
    axes_a = [np.column_stack([ca, sa]), np.column_stack([-sa, ca])]
    angle_b = np.broadcast_to(np.asarray(angle_b, dtype=float), np.shape(angle_a))
    cb, sb = np.cos(angle_b), np.sin(angle_b)
    axes_b = [np.column_stack([cb, sb]), np.column_stack([-sb, cb])]
    offset = centre_b - centre_a
    separated = np.zeros(len(angle_a), dtype=bool)
    for axis in axes_a + axes_b:
        radius_a = half_a[0] * np.abs(np.sum(axes_a[0] * axis, axis=1)) + half_a[1] * np.abs(np.sum(axes_a[1] * axis, axis=1))
        radius_b = half_b[0] * np.abs(np.sum(axes_b[0] * axis, axis=1)) + half_b[1] * np.abs(np.sum(axes_b[1] * axis, axis=1))
        separated |= np.abs(np.sum(offset * axis, axis=1)) > radius_a + radius_b
    return ~separated


def _travel(times: np.ndarray, speed: float, reaction: float, deceleration: float) -> np.ndarray:
    distance = speed * np.minimum(times, reaction)
    after = np.maximum(times - reaction, 0.0)
    if deceleration <= 0.0:
        return distance + speed * after
    stop = speed / deceleration
    braking = np.minimum(after, stop)
    return distance + speed * braking - 0.5 * deceleration * braking * braking


def _target_travel(times: np.ndarray, speed: float, acceleration: float) -> np.ndarray:
    if acceleration >= 0.0 or speed <= 0.0:
        return speed * times
    stop = speed / -acceleration
    moving = np.minimum(times, stop)
    return speed * moving + 0.5 * acceleration * moving * moving


def _encounter(target_speed: float, angle_deg: float) -> str:
    if target_speed < HEADING_MIN_SPEED_MPS:
        return "STATIONARY"
    angle = abs(angle_deg)
    if angle <= 30.0:
        return "SAME_DIRECTION"
    if angle >= 150.0:
        return "OPPOSING"
    if 60.0 <= angle <= 120.0:
        return "CROSSING"
    return "OBLIQUE"


class _Prediction:

    def __init__(self, sample: TrackSample, own: EgoState, footprint: Optional[EgoFootprint],
                 cfg: SemanticsConfig) -> None:
        self.cfg = cfg
        self.times = np.arange(0.0, cfg.prediction_horizon_s + 1e-9, cfg.prediction_time_step_s)
        c, s = math.cos(own.heading), math.sin(own.heading)
        self.ego_speed = max(c * own.vx + s * own.vy, 0.0)
        curvature = own.yaw_rate / self.ego_speed if self.ego_speed > 1.0 else 0.0
        self.curvature = max(-MAX_CURVATURE_PER_M, min(MAX_CURVATURE_PER_M, curvature))
        footprint = footprint or DEFAULT_FOOTPRINT
        d0, lateral = cfg.critical_standstill_margin_m, cfg.critical_lateral_margin_m
        x_min, x_max = footprint.x_min - d0, footprint.x_max + d0
        y_min, y_max = footprint.y_min - lateral, footprint.y_max + lateral
        self.ego_half = ((x_max - x_min) / 2.0, (y_max - y_min) / 2.0)
        self.ego_offset = np.array([(x_max + x_min) / 2.0, (y_max + y_min) / 2.0])
        self.footprint = footprint
        centre, unit, half, speed, angle = target_box(sample, own, footprint, cfg)
        self.target_speed = speed
        self.target_angle = angle
        acceleration = sample.acceleration_mps2 if self.target_speed >= HEADING_MIN_SPEED_MPS else 0.0
        self.target_acceleration = (max(acceleration, -MAX_SEARCH_DECELERATION_MPS2)
                                    if acceleration <= -cfg.target_braking_min_mps2 else 0.0)
        self.target_centre = centre
        self.target_unit = unit
        tvx, tvy = c * sample.vx_mps + s * sample.vy_mps, -s * sample.vx_mps + c * sample.vy_mps
        tvy = math.copysign(max(abs(tvy)-sample.vel_std_mps,0.0),tvy)
        self.target_motion_unit = np.array([tvx,tvy])/speed if speed > 1e-9 else unit
        self.target_half = half
        curvature = float(getattr(sample, "path_curvature", None) or 0.0)
        self.target_curvature = max(-MAX_CURVATURE_PER_M, min(MAX_CURVATURE_PER_M, curvature))
        self.encounter = _encounter(self.target_speed,math.degrees(math.atan2(self.target_motion_unit[1],self.target_motion_unit[0])))
        self.lateral_relative_speed = -s * (sample.vx_mps - own.vx) + c * (sample.vy_mps - own.vy)

    def ego_pose(self, travel: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        k = self.curvature
        if abs(k) < 1e-6:
            x, y, theta = travel, np.zeros_like(travel), np.zeros_like(travel)
        else:
            theta = k * travel
            x, y = np.sin(theta) / k, (1.0 - np.cos(theta)) / k
        c, s = np.cos(theta), np.sin(theta)
        ox, oy = self.ego_offset
        return np.column_stack([x + c * ox - s * oy, y + s * ox + c * oy]), theta

    def overlaps(self, ego_deceleration: float = 0.0, ego_reaction: float = 0.0,
                 target_deceleration: float = 0.0, target_reaction: float = 0.0) -> np.ndarray:
        centres, angles = self.ego_pose(_travel(self.times, self.ego_speed, ego_reaction, ego_deceleration))
        if target_deceleration > 0.0:
            moved = _travel(self.times, self.target_speed, target_reaction, target_deceleration)
        else:
            moved = _target_travel(self.times, self.target_speed, self.target_acceleration)
        k, unit = self.target_curvature, self.target_motion_unit
        if abs(k) < 1e-6:
            targets = self.target_centre + moved[:, None] * unit
            target_angles = self.target_angle
        else:
            theta = k * moved
            right = np.array([-unit[1], unit[0]])
            targets = (self.target_centre + (np.sin(theta) / k)[:, None] * unit
                       + ((1.0 - np.cos(theta)) / k)[:, None] * right)
            target_angles = self.target_angle + theta
        return _overlap(centres, angles, self.ego_half, targets, target_angles, self.target_half)


def _required(predict) -> float:
    if predict(MAX_SEARCH_DECELERATION_MPS2).any():
        return math.inf
    low, high = 0.0, MAX_SEARCH_DECELERATION_MPS2
    for _ in range(BISECTION_STEPS):
        middle = 0.5 * (low + high)
        if predict(middle).any():
            low = middle
        else:
            high = middle
    return high


def forward_gap(prediction: "_Prediction", cfg: SemanticsConfig, vel_std_mps: float) -> ForwardGap:
    corners = box_corners(prediction.target_centre, prediction.target_unit, prediction.target_half)
    clearance = float(corners[:, 0].min()) - prediction.footprint.x_max
    front_clearance = float(corners[:, 0].max()) - prediction.footprint.x_max
    y_min, y_max = float(corners[:, 1].min()), float(corners[:, 1].max())
    gap = lateral_body_gap(y_min, y_max, cfg.path_half_width_m)
    side = 1.0 if y_min > cfg.path_half_width_m else (-1.0 if y_max < -cfg.path_half_width_m else 0.0)
    approach = -side * prediction.lateral_relative_speed
    if gap <= 0.0:
        region: Optional[str] = IN_PATH
    elif (gap <= cfg.critical_front_lateral_margin_m
          and approach - vel_std_mps >= cfg.critical_front_lateral_speed_mps):
        region = FRONT_LATERAL
    else:
        region = None
    ego_speed = prediction.ego_speed
    leader = (region is not None and clearance > 0.0 and prediction.encounter == "SAME_DIRECTION"
              and ego_speed >= cfg.critical_forward_min_speed_mps)
    time_gap, time_gap_distance, required = safe_following_distance(ego_speed, cfg)
    unsafe = leader and clearance < required
    released = (ego_speed < cfg.critical_forward_min_speed_mps
                or clearance > cfg.critical_forward_release_factor * required
                or front_clearance <= 0.0
                or (gap > cfg.path_hysteresis_m and approach <= vel_std_mps))
    return ForwardGap(leader=leader, region=region, longitudinal_clearance_m=clearance,
                      front_clearance_m=front_clearance, lateral_body_gap_m=gap, lateral_approach_mps=approach,
                      time_headway_s=clearance / ego_speed if ego_speed > 0.1 and clearance > 0.0 else None,
                      minimum_time_gap_s=time_gap, time_gap_distance_m=time_gap_distance,
                      required_distance_m=required, unsafe=unsafe, released=released)


def assess_conflict(sample: TrackSample, own: EgoState, footprint: Optional[EgoFootprint],
                    cfg: SemanticsConfig, track_age_s: Optional[float] = None,
                    leader_gate: Optional[bool] = None) -> ConflictAssessment:
    prediction = _Prediction(sample, own, footprint, cfg)
    available = cfg.critical_deceleration_mps2
    known = (not sample.identity_ambiguous and sample.pos_std_m <= cfg.max_position_std_m and sample.vel_std_mps <= cfg.max_velocity_std_mps
             and (track_age_s is None or track_age_s >= cfg.critical_min_track_age_s - 1e-9))
    result = ConflictAssessment(encounter=prediction.encounter, collision_course=False, ttc_s=None, overlap_s=None,
                                required_deceleration_mps2=None, avoidance_by=None,
                                available_deceleration_mps2=available, critical=False, known=known,
                                target_speed_mps=prediction.target_speed,
                                target_acceleration_mps2=prediction.target_acceleration,
                                ego_speed_mps=prediction.ego_speed,
                                forward=_gated(forward_gap(prediction, cfg, sample.vel_std_mps), leader_gate),
                                occluded=bool(getattr(sample, "occluded", False)),
                                contact_imminent=(sample.closing_speed_mps >= cfg.closing_speed_threshold_mps
                                                  and sample.clearance_m < cfg.critical_reaction_time_s
                                                  * sample.closing_speed_mps))
    _collision_course(prediction, sample, cfg, result)
    reasons = []
    if result.collision_course and result.required_deceleration_mps2 >= available:
        reasons.append(PREDICTED_OVERLAP)
    if result.forward.unsafe and not result.occluded:
        reasons.append(UNSAFE_FORWARD_GAP)
    result.critical = known and bool(reasons)
    result.critical_reason = "+".join(reasons) if result.critical else None
    return result


def _gated(forward: ForwardGap, leader_gate: Optional[bool]) -> ForwardGap:
    if leader_gate is False and (forward.leader or forward.unsafe):
        import dataclasses
        return dataclasses.replace(forward, leader=False, unsafe=False)
    return forward


def _collision_course(prediction: "_Prediction", sample: TrackSample, cfg: SemanticsConfig,
                      result: ConflictAssessment) -> None:
    overlap = prediction.overlaps()
    result.inside_envelope = bool(overlap[0])
    if not overlap.any():
        return
    if overlap[0] and sample.closing_speed_mps < cfg.closing_speed_threshold_mps:
        return
    times = prediction.times[overlap]
    result.collision_course = True
    result.ttc_s = round(float(times[0]), 3)
    result.overlap_s = (round(float(times[0]), 3), round(float(times[-1]), 3))
    reaction = cfg.critical_reaction_time_s
    if not prediction.overlaps(ego_deceleration=MAX_SEARCH_DECELERATION_MPS2).any():
        required = _required(lambda a: prediction.overlaps(ego_deceleration=a, ego_reaction=reaction))
        by = "recorder"
    else:
        required = _required(lambda b: prediction.overlaps(target_deceleration=b, target_reaction=reaction))
        by = "target"
    result.required_deceleration_mps2 = required
    result.avoidance_by = by
