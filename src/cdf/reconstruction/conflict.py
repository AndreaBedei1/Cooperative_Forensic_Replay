"""Collision course, braking avoidability and safe following distance of a radar track: the CRITICAL_TTC model.

CRITICAL_TTC is true for either of two reasons (``critical_reason``):

* PREDICTED_OVERLAP: a predicted 2-D collision course that braking can no longer
  avoid with the available deceleration (points 1-3 below);
* UNSAFE_FORWARD_GAP: a road user ahead of the recorder, in its path or entering
  it from just beside it, is closer than the safe following distance (point 4),
  whether or not the two are on a collision course at their current speeds.

CRITICAL_TTC is the event's historical name: a forward gap can be unsafe while the
classical TTC is infinite (two cars at the same speed 3 m apart never meet), so an
UNSAFE_FORWARD_GAP alone has no TTC (``ttc_s`` None).  A time headway is not a TTC.

Everything is local to one recorder: its own odometry (speed, yaw rate), its own
footprint and one smoothed radar track.  At each track sample the future is
predicted over ``prediction_horizon_s`` in the recorder's vehicle frame:

  recorder  its footprint, inflated into a safety envelope (the standstill
            margin d0 ahead and behind, ``critical_lateral_margin_m`` at the
            sides), moving along its current path: constant speed and yaw rate
            (a circular arc, a straight line when not turning);
  target    a box of nominal size (``target_length_m`` x ``target_width_m``: the
            radar measures no size) placed behind its observed near surface
            (the corner towards the recorder when seen obliquely, the middle of
            the facing side when seen along one of its axes) and moving at its
            estimated velocity.  Its velocity across the recorder's heading
            counts only beyond the estimate's uncertainty (a car's null
            hypothesis is to keep its lane).  A target decelerating at least
            ``target_braking_min_mps2`` keeps its measured deceleration until
            it stops.

1. COLLISION COURSE: the two boxes overlap somewhere within the horizon.  The
   time of the first overlap is the TTC; the span of overlapping instants is the
   temporal overlap of the two vehicles in the conflict area.  A target that
   approaches radially but passes ahead of or behind the recorder never
   overlaps: no collision course, whatever its range rate.  A target already
   inside the envelope (``inside_envelope``: the present overlap, near contact)
   starts a collision course only while it still closes in; that it stops
   closing in is no evidence that the conflict is over (point 5).
2. AVOIDANCE BY BRAKING: the smallest deceleration that removes every overlap
   when the braking vehicle reacts after ``critical_reaction_time_s`` and then
   brakes along its path until it stops (bisection; the overlap disappears
   monotonically with harder braking).  The braking vehicle is the recorder
   when its braking can avoid the conflict (it closes on the target, or crosses
   its path); when even an instant stop of the recorder cannot (a target
   closing in from behind or from the side), it is the target, with the same
   reaction time.
3. CRITICAL: a collision course whose required deceleration is at least the
   available one (``critical_deceleration_mps2``), claimed only while the track
   estimate is precise enough (``max_position_std_m``, ``max_velocity_std_mps``,
   as for CUT_IN) and the track at least ``critical_min_track_age_s`` old: a
   young track's velocity is not yet known (the smoother's uncertainty at a
   track's first samples already draws on later data and understates it).

For a target ahead in the same lane points 1-3 check whether the recorder can
still stop short of the target as it moves now (keeping its speed, or its
measured deceleration when it brakes): a car ahead at the recorder's own speed
is never on a collision course, however close it is.  Point 4 adds what that
misses: the room the recorder would need if the vehicle ahead braked.  For
crossing traffic the space-time overlap of the two predicted footprints
replaces any one-dimensional distance: a car that crosses ahead of or behind the
recorder's envelope is not on a collision course, whatever its range rate.

4. SAFE FOLLOWING DISTANCE (UNSAFE_FORWARD_GAP).  The longitudinal clearance
   from the recorder's front face to the rear face of the target's nominal box,
   along the recorder's heading (never the radar range), is compared with

       d_min = max(v_ego * t_front(v_ego), critical_min_following_distance_m = 2 m)

   where v_ego is the recorder's own speed and t_front the minimum following time
   gap of UN Regulation No. 157 (ALKS, vehicles M1 / N1): 1.0 s at 7.2 km/h,
   1.1 s at 10, 1.2 s at 20, 1.3 s at 30, 1.4 s at 40, 1.5 s at 50, 1.6 s at
   60 km/h, linear in between, the first and last values held outside the table
   (no extrapolation above 60 km/h; below 7.2 km/h the 2 m minimum rules).  No
   margin is added and the target's speed is not used: the gap can be unsafe
   when the target is as fast as the recorder, or a little faster.  The braking
   avoidability of points 2-3 (reaction time, decelerations) is not part of it.

   It applies only to a road user that is a leader of the recorder: moving in
   the same direction (SAME_DIRECTION encounter), its body ahead of the
   recorder's front face, either overlapping the path corridor
   (``path_half_width_m`` either side of the heading) or within
   ``critical_front_lateral_margin_m`` of it while approaching it laterally
   (``critical_front_lateral_speed_mps`` beyond the estimate's uncertainty), and
   with the recorder itself moving (at least ``critical_forward_min_speed_mps``,
   the MOVING threshold; from 1 to 2 m/s the 2 m minimum binds).  A car beside
   or behind the recorder, a car keeping its own lane next to the corridor and a
   car further away are never critical for this reason (they still are when the
   2-D prediction finds a collision course).  Without a predicted overlap there
   is no TTC: ``ttc_s`` stays None (a time headway is not a TTC).  The reason
   starts when a leader's clearance drops below d_min; it ends only as point 5
   says (``ForwardGap.released``), not as soon as one leader condition fails.
   The estimate gates of point 3 apply, and a track seen past another tracked
   vehicle (``TrackSample.occluded``) gives no evidence either way for this
   reason, since its returns may be hidden by or mixed with that vehicle's: it
   neither starts nor ends it.

5. RELEASE (CRITICAL_TTC_END, ``local.critical_intervals``).  A sample is
   either critical (point 3 or 4), clearly resolved (``released``) or neither;
   only a run of resolved samples lasting the 0.2 s debounce ends the state, at
   its first sample, and any other sample restarts the run.  Resolved means, on
   a known estimate:

   * no collision course, or one that braking avoids with less than
     ``critical_release_ratio`` x the available deceleration;
   * no imminent contact along the line of sight: a target closing in at
     ``closing_speed_threshold_mps`` or more that would cover its clearance
     within ``critical_reaction_time_s`` (clearance / closing speed, the
     TRACK_STATE ``closing_ttc_s``) is not resolved, whatever the 2-D
     prediction says (its constant-velocity target misses a curved path: S07,
     a car merging into a roundabout alongside a recorder that turns);
   * the target's box outside the recorder's safety envelope now (no near
     contact), unless both stand still (below ``HEADING_MIN_SPEED_MPS``, so
     nothing moves toward anything): a target that touches the envelope and
     momentarily stops closing in (below ``closing_speed_threshold_mps``) is
     not released by that alone;
   * when the unsafe forward gap was a reason of this episode, that leader
     clearly gone, seen without occlusion: the recorder below the MOVING
     threshold, or the clearance beyond ``critical_forward_release_factor`` x
     d_min, or its whole body level with or behind the recorder's front face
     (no longer ahead at all), or its body more than ``path_hysteresis_m``
     outside the corridor (the EGO_PATH_EXIT hysteresis) and not moving back
     toward it beyond its velocity uncertainty (``ForwardGap.released``).  The
     leader conditions of point 4 are a start gate: failing one of them by a
     centimetre (a body 0.01 m outside the corridor) does not end the state.

6. COLLISION (``local.contact_partners``, ``local.critical_intervals``).
   CRITICAL_TTC describes the pre-collision threat.  When the recorder's own
   collision sensor reports a contact with the track of an active episode, the
   episode ends at the collision's timestamp (COLLISION first, then
   CRITICAL_TTC_END, at the same instant), whatever the release says: the
   separation, the stop or the boxes leaving the envelope belong to the
   post-impact dynamics.  The continuing contact is a post-impact state, not a
   new episode: none starts for that track while the contact lasts (to its last
   callback), nor afterwards until the conflict has been clearly resolved as in
   point 5; a genuinely new conflict can then start a new episode.  The
   collision ends only its own pair: the recorder's other tracks keep their
   episodes.  The sensor names no partner; it is the recorder's only track
   CLOSING and touching it at the contact (``contact_partners``), otherwise no
   track (a car striking from the rear blind zone) and nothing ends early.

The safe distance follows the idea of art. 149 of the Italian Highway Code (keep
a distance that lets the recorder stop in time and avoid a collision with the
vehicle ahead) and of Directive 2006/126/EC (adequate distance to the vehicles
in front and at the side, speed that allows stopping within the free distance),
which prescribe no numbers.  UN R157 regulates automated lane keeping systems:
its time-gap table is used here as a technical reference, not as a universal
law of human driving, and no single European "critical TTC" threshold exists.
UN R152 (AEBS) asks for at least 5 m/s^2 of braking demand when a collision is
imminent; the reaction time and deceleration of the collision-course model are
modelling assumptions of this reconstruction, not values prescribed by EU or
UNECE rules.

Parameters are global and documented in ``configs/reconstruction.yaml``.  Limits:
constant velocity / yaw rate (no intent, no lane geometry), a nominal target
size, braking as the only avoidance manoeuvre (no swerve), one track at a time
for the prediction (no occlusion of the predicted paths by third vehicles).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Sequence, Tuple

import numpy as np

from .config import SemanticsConfig
from .tracking import EgoFootprint, EgoState, TrackSample

# Bisection on the deceleration: upper bound (no road vehicle brakes harder) and steps.
MAX_SEARCH_DECELERATION_MPS2 = 30.0
BISECTION_STEPS = 14
# Below this speed a target's heading is unknown: it is taken parallel to the recorder.
HEADING_MIN_SPEED_MPS = 1.0
# The recorder's path curvature is limited to this (a 5 m radius).
MAX_CURVATURE_PER_M = 0.2
# Beyond this angle between the line of sight and a target's axis, its near surface point is
# taken as the corner towards the recorder (see target_box).
OBLIQUE_VIEW_DEG = 20.0
# A recorder footprint for tracks of a recorder whose own shape is unknown.
DEFAULT_FOOTPRINT = EgoFootprint(-2.3, 2.3, -0.95, 0.95)

PREDICTED_OVERLAP = "PREDICTED_OVERLAP"
UNSAFE_FORWARD_GAP = "UNSAFE_FORWARD_GAP"
IN_PATH = "IN_PATH"
FRONT_LATERAL = "FRONT_LATERAL"


@dataclass
class ForwardGap:
    """The safe-following-distance check of one target (module docstring, point 4).

    Conflict-model output: never part of the forensic packet given to an LLM.
    """

    leader: bool  # a road user the recorder follows: same direction, ahead, in or entering the path, recorder moving
    region: Optional[str]  # IN_PATH (body overlaps the corridor) or FRONT_LATERAL (beside it, approaching), else None
    longitudinal_clearance_m: float  # recorder's front face -> target box's rear face, along the recorder's heading
    front_clearance_m: float  # recorder's front face -> target box's front face (<= 0: no part of it ahead)
    lateral_body_gap_m: float  # target box -> path corridor, across the heading (0: it overlaps the corridor)
    lateral_approach_mps: float  # speed toward the corridor (relative, + = closing in), before the uncertainty
    time_headway_s: Optional[float]  # clearance / recorder speed (a time gap, not a TTC)
    minimum_time_gap_s: float  # t_front: UN R157 table at the recorder's speed
    time_gap_distance_m: float  # v_ego * t_front
    required_distance_m: float  # d_min = max(v_ego * t_front, critical_min_following_distance_m)
    unsafe: bool  # a leader closer than d_min (before the estimate gates)
    # The leader is clearly gone (module docstring, point 5): recorder below the MOVING threshold, or
    # clearance > release factor x d_min, or no part of its body ahead of the front face, or its body
    # beyond the path hysteresis outside the corridor and not moving back toward it.
    released: bool

    @property
    def margin_m(self) -> float:
        """Clearance minus required distance (negative when unsafe)."""
        return self.longitudinal_clearance_m - self.required_distance_m


@dataclass
class ConflictAssessment:
    """What the prediction says about one target at one instant."""

    encounter: str  # SAME_DIRECTION, OPPOSING, CROSSING, OBLIQUE or STATIONARY
    collision_course: bool
    ttc_s: Optional[float]  # time to the first predicted overlap (constant speeds)
    overlap_s: Optional[Tuple[float, float]]  # first and last predicted overlapping instants
    required_deceleration_mps2: Optional[float]  # None without collision course; inf: braking cannot avoid it
    avoidance_by: Optional[str]  # "recorder" or "target": whose braking the requirement refers to
    available_deceleration_mps2: float
    critical: bool  # either reason below, claimed only on a known estimate
    known: bool  # the track estimate is precise enough for a claim (max_position_std_m, max_velocity_std_mps)
    target_speed_mps: float
    target_acceleration_mps2: float  # used in the prediction (0 unless it brakes)
    ego_speed_mps: float
    forward: Optional[ForwardGap] = None  # safe following distance (None: not evaluated)
    occluded: bool = False  # seen past another tracked vehicle: no forward-gap evidence either way
    critical_reason: Optional[str] = None  # PREDICTED_OVERLAP, UNSAFE_FORWARD_GAP or both joined by "+"
    inside_envelope: bool = False  # the target's box overlaps the recorder's safety envelope now (near contact)
    contact_imminent: bool = False  # closing in so fast that its clearance goes within the reaction time

    @property
    def braking_margin_mps2(self) -> Optional[float]:
        """Available minus required deceleration (negative when critical)."""
        if self.required_deceleration_mps2 is None or math.isinf(self.required_deceleration_mps2):
            return None
        return self.available_deceleration_mps2 - self.required_deceleration_mps2

    @property
    def forward_known(self) -> bool:
        """The forward-gap reason can be claimed either way (estimate gates, line of sight clear)."""
        return self.known and not self.occluded

    @property
    def at_rest(self) -> bool:
        """Recorder and target both slower than HEADING_MIN_SPEED_MPS: nothing moves toward anything."""
        return self.ego_speed_mps < HEADING_MIN_SPEED_MPS and self.target_speed_mps < HEADING_MIN_SPEED_MPS

    def overlap_released(self, release_deceleration_mps2: float) -> bool:
        """The collision-course reason is clearly off (module docstring, point 5): no imminent line-of-sight
        contact, no near contact (unless both stand still) and no collision course, or one braking avoids
        below the release deceleration."""
        if self.contact_imminent or (self.inside_envelope and not self.at_rest):
            return False
        return (not self.collision_course or self.required_deceleration_mps2 is None
                or self.required_deceleration_mps2 < release_deceleration_mps2)

    def forward_released(self) -> bool:
        """The forward-gap reason is clearly off: the leader is gone, seen without occlusion (an occluded
        sample is no evidence either way: it does not end the reason)."""
        if self.forward is None:
            return True
        return not self.occluded and self.forward.released

    def released(self, release_deceleration_mps2: float, forward_engaged: bool = True) -> bool:
        """Clearly resolved (the release of CRITICAL_TTC, module docstring point 5); False on an uncertain
        estimate.  ``forward_engaged``: the unsafe forward gap was a reason of the current episode, so
        that leader must be gone too (a reason that never applied cannot hold the state)."""
        if not self.known:
            return False
        return (self.overlap_released(release_deceleration_mps2)
                and (not forward_engaged or self.forward_released()))


def minimum_time_gap_s(speed_mps: float, table: Sequence[Sequence[float]]) -> float:
    """Minimum following time gap (s) at a speed, from a (km/h, s) table: linear interpolation, ends held."""
    points = sorted((float(kmh), float(gap)) for kmh, gap in table)
    kmh = max(speed_mps, 0.0) * 3.6
    if kmh <= points[0][0]:
        return points[0][1]
    for (k0, t0), (k1, t1) in zip(points, points[1:]):
        if kmh <= k1:
            return t0 + (t1 - t0) * (kmh - k0) / (k1 - k0)
    return points[-1][1]


def safe_following_distance(ego_speed_mps: float, cfg: SemanticsConfig) -> Tuple[float, float, float]:
    """(t_front, v_ego * t_front, d_min) for the recorder's speed (module docstring, point 4).

    d_min = max(v_ego * t_front(v_ego), critical_min_following_distance_m): only the recorder's own
    speed counts, never the target's, and nothing is added to it.
    """
    ego_speed = max(ego_speed_mps, 0.0)
    time_gap = minimum_time_gap_s(ego_speed, cfg.critical_time_gap_table)
    distance = ego_speed * time_gap
    return time_gap, distance, max(distance, cfg.critical_min_following_distance_m)


def lateral_body_gap(y_min: float, y_max: float, half_width: float) -> float:
    """Distance across the heading from a body spanning [y_min, y_max] to the corridor |y| <= half_width."""
    return max(y_min - half_width, -half_width - y_max, 0.0)


def target_box(sample: TrackSample, own: EgoState, footprint: Optional[EgoFootprint],
               cfg: SemanticsConfig) -> Tuple[np.ndarray, np.ndarray, Tuple[float, float], float, float]:
    """The target's nominal box in the recorder's vehicle frame: (centre, unit heading, half sizes,
    speed used, heading angle) -- see the module docstring, "target"."""
    footprint = footprint or DEFAULT_FOOTPRINT
    c, s = math.cos(own.heading), math.sin(own.heading)
    # Target: ground velocity in the recorder's axes, heading, near surface, box centre.
    tvx, tvy = c * sample.vx_mps + s * sample.vy_mps, -s * sample.vx_mps + c * sample.vy_mps
    # The target's motion across the recorder's heading counts only beyond the uncertainty of
    # its estimate: a radar track's median point slides over the target's visible body while
    # the view angle changes (S06: an oncoming car passing beside the recorder looked 1 m/s
    # closer to its lane than it was), and the null hypothesis for a car is to keep to its
    # lane, parallel to the recorder, not to head straight at it.
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
    # The near surface point is the part of the target closest to the recorder: seen obliquely,
    # the corner towards it; seen along one of its axes, the middle of the facing side.  The
    # box lies behind it, in each of its two axes by a weight growing from 0 (looking along
    # that face) to 1 at OBLIQUE_VIEW_DEG and beyond.
    gx, gy = -nx, -ny  # from the target towards the recorder
    along, across = gx * ux + gy * uy, gx * -uy + gy * ux  # in the target's axes (across = its right)
    oblique = math.sin(math.radians(OBLIQUE_VIEW_DEG))
    weight_along, weight_across = min(abs(along) / oblique, 1.0), min(abs(across) / oblique, 1.0)
    centre = (near - math.copysign(length / 2.0 * weight_along, along) * np.array([ux, uy])
              - math.copysign(width / 2.0 * weight_across, across) * np.array([-uy, ux]))
    return centre, np.array([ux, uy]), (length / 2.0, width / 2.0), speed, math.atan2(uy, ux)


def box_corners(centre: np.ndarray, unit: np.ndarray, half: Tuple[float, float]) -> np.ndarray:
    along, across = unit * half[0], np.array([-unit[1], unit[0]]) * half[1]
    return np.array([centre + along + across, centre + along - across, centre - along - across, centre - along + across])


def body_in_corridor(corners: np.ndarray, front: float, half_width: float) -> bool:
    """Exact overlap of an oriented body with the forward half-strip.

    Clip the convex box to x >= front before testing its lateral extent; an
    axis-aligned bounding rectangle can otherwise invent overlap at a corner.
    """
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
    """Whether the segment p0-p1 enters the oriented box (clipping in the box's own axes)."""
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
    """The target's observed near surface in the vehicle frame: the tracked point moved back by its depth."""
    footprint = footprint or DEFAULT_FOOTPRINT
    nx, ny = footprint.outward(sample.longitudinal_m, sample.lateral_m)
    return np.array([sample.longitudinal_m - sample.surface_offset_m * nx,
                     sample.lateral_m - sample.surface_offset_m * ny])


def occluded_by(sample: TrackSample, own: EgoState, others: Sequence[TrackSample],
                footprint: Optional[EgoFootprint], cfg: SemanticsConfig) -> bool:
    """Whether the line of sight from the recorder's body to the sample's near surface crosses the nominal
    box (grown by ``occlusion_margin_m``) of another track of the same recorder at the same instant:
    the target is seen past that vehicle, and its radar returns may be hidden by or mixed with it."""
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
    """Separating-axis test of two oriented rectangles, vectorised over time (``angle_b`` one angle or one per
    instant)."""
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
    """Distance along the path: constant speed until ``reaction``, then braking at ``deceleration`` to a stop."""
    distance = speed * np.minimum(times, reaction)
    after = np.maximum(times - reaction, 0.0)
    if deceleration <= 0.0:
        return distance + speed * after
    stop = speed / deceleration
    braking = np.minimum(after, stop)
    return distance + speed * braking - 0.5 * deceleration * braking * braking


def _target_travel(times: np.ndarray, speed: float, acceleration: float) -> np.ndarray:
    """Distance of a target that keeps a (negative) acceleration until it stops."""
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
    """The two predicted footprints of one sample, ready for repeated overlap tests."""

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
        # Target: its nominal box behind the observed near surface, moving at its velocity.
        centre, unit, half, speed, angle = target_box(sample, own, footprint, cfg)
        self.target_speed = speed
        self.target_angle = angle
        acceleration = sample.acceleration_mps2 if self.target_speed >= HEADING_MIN_SPEED_MPS else 0.0
        self.target_acceleration = (max(acceleration, -MAX_SEARCH_DECELERATION_MPS2)
                                    if acceleration <= -cfg.target_braking_min_mps2 else 0.0)
        self.target_centre = centre
        self.target_unit = unit
        # A fitted body's orientation and its translation velocity are distinct
        # (e.g. lateral motion without body yaw). Never forecast along box yaw.
        tvx, tvy = c * sample.vx_mps + s * sample.vy_mps, -s * sample.vx_mps + c * sample.vy_mps
        tvy = math.copysign(max(abs(tvy)-sample.vel_std_mps,0.0),tvy)
        self.target_motion_unit = np.array([tvx,tvy])/speed if speed > 1e-9 else unit
        self.target_half = half
        # The lane the target keeps bends its predicted path as the recorder's yaw rate bends the recorder's (the
        # null hypothesis on a curve: a car keeps its lane, it does not leave it along a tangent).
        curvature = float(getattr(sample, "path_curvature", None) or 0.0)
        self.target_curvature = max(-MAX_CURVATURE_PER_M, min(MAX_CURVATURE_PER_M, curvature))
        self.encounter = _encounter(self.target_speed,math.degrees(math.atan2(self.target_motion_unit[1],self.target_motion_unit[0])))
        # Relative velocity across the recorder's heading (+ = to its right; no uncertainty removed).
        self.lateral_relative_speed = -s * (sample.vx_mps - own.vx) + c * (sample.vy_mps - own.vy)

    def ego_pose(self, travel: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Envelope centres and headings after travelling ``travel`` metres along the path."""
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
        """Overlap at every predicted instant, given who brakes how hard after what reaction time."""
        centres, angles = self.ego_pose(_travel(self.times, self.ego_speed, ego_reaction, ego_deceleration))
        if target_deceleration > 0.0:
            moved = _travel(self.times, self.target_speed, target_reaction, target_deceleration)
        else:
            moved = _target_travel(self.times, self.target_speed, self.target_acceleration)
        k, unit = self.target_curvature, self.target_motion_unit
        if abs(k) < 1e-6:
            targets = self.target_centre + moved[:, None] * unit
            target_angles = self.target_angle
        else:  # along an arc of the lane's curvature (+ = to the right of its motion)
            theta = k * moved
            right = np.array([-unit[1], unit[0]])
            targets = (self.target_centre + (np.sin(theta) / k)[:, None] * unit
                       + ((1.0 - np.cos(theta)) / k)[:, None] * right)
            target_angles = self.target_angle + theta
        return _overlap(centres, angles, self.ego_half, targets, target_angles, self.target_half)


def _required(predict) -> float:
    """Smallest deceleration (bisection) for which ``predict(a)`` shows no overlap; inf if none suffices."""
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
    """The safe-following-distance check of one prediction (module docstring, point 4)."""
    corners = box_corners(prediction.target_centre, prediction.target_unit, prediction.target_half)
    clearance = float(corners[:, 0].min()) - prediction.footprint.x_max
    front_clearance = float(corners[:, 0].max()) - prediction.footprint.x_max
    y_min, y_max = float(corners[:, 1].min()), float(corners[:, 1].max())
    gap = lateral_body_gap(y_min, y_max, cfg.path_half_width_m)
    # Toward the corridor: the side the body lies on (a body overlapping the corridor has no side).
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
    # Release (point 5): geometric hysteresis, never the start gate failing by a hair.
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
    """Collision course, TTC, braking avoidability and safe following distance of one track sample
    (see the module docstring).

    ``track_age_s``: time since the track's first sample (None: old enough).  ``sample.occluded``
    (set by the local reconstruction) withholds the forward-gap reason either way.  ``leader_gate``: whether
    the target is in the recorder's path or in a confirmed cut-in into it at this sample (``local.track_events``);
    False: it is no leader, whatever its box geometry at this one sample (a car beside the recorder, its box
    rotated by a heading error, or a lateral speed estimate that no path entry confirms); None: not known.
    """
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
    """A forward gap whose target is not a leader of the recorder (``leader_gate`` False) is never unsafe."""
    if leader_gate is False and (forward.leader or forward.unsafe):
        import dataclasses
        return dataclasses.replace(forward, leader=False, unsafe=False)
    return forward


def _collision_course(prediction: "_Prediction", sample: TrackSample, cfg: SemanticsConfig,
                      result: ConflictAssessment) -> None:
    """Points 1-2 of the module docstring: overlap, TTC and the deceleration that removes it."""
    overlap = prediction.overlaps()
    result.inside_envelope = bool(overlap[0])
    if not overlap.any():
        return
    if overlap[0] and sample.closing_speed_mps < cfg.closing_speed_threshold_mps:
        # Already inside the envelope, but no longer closing in: no new collision course.  It is
        # not a release either (inside_envelope holds the state, point 5).
        return
    times = prediction.times[overlap]
    result.collision_course = True
    result.ttc_s = round(float(times[0]), 3)
    result.overlap_s = (round(float(times[0]), 3), round(float(times[-1]), 3))
    reaction = cfg.critical_reaction_time_s
    if not prediction.overlaps(ego_deceleration=MAX_SEARCH_DECELERATION_MPS2).any():
        # The recorder's own braking can remove the overlap (it closes on the target or
        # crosses its path): its requirement, with its reaction time.
        required = _required(lambda a: prediction.overlaps(ego_deceleration=a, ego_reaction=reaction))
        by = "recorder"
    else:
        # Even an instant stop of the recorder leaves the overlap (a target closing in from
        # behind or from the side): only the target's braking can avoid it.
        required = _required(lambda b: prediction.overlaps(target_deceleration=b, target_reaction=reaction))
        by = "target"
    result.required_deceleration_mps2 = required
    result.avoidance_by = by
