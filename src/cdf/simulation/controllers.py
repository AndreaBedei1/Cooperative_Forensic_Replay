"""Deterministic scripted controllers used to generate scenarios.

The controller follows the configured route and timed actions with deterministic
lateral and longitudinal control.

Design
------
A participant's behaviour is fully described by

* a :class:`RoutePlan` -- a fixed polyline the vehicle follows,
* a base target speed, and
* an ordered list of :class:`ScriptedAction` items, each with an explicit
  ``action_id``, start time and duration.

Control is deliberately simple and deterministic: pure-pursuit lateral steering
plus a PI longitudinal controller. No randomness, no wall-clock, no Traffic
Manager in the safety-critical path.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

from ..common.geometry import angle_diff_deg, distance

__all__ = [
    "ControlCommand",
    "VehicleState",
    "RoutePlan",
    "ScriptedAction",
    "ScriptedController",
    "PIDLongitudinal",
]


@dataclass
class ControlCommand:
    """A vehicle actuation command, mirroring ``carla.VehicleControl``."""

    throttle: float = 0.0
    brake: float = 0.0
    steer: float = 0.0
    hand_brake: bool = False
    reverse: bool = False
    neutral: bool = False  # gearbox in neutral (no engine braking)

    def clamped(self) -> "ControlCommand":
        """Clamp every channel into its physical range."""
        return ControlCommand(
            throttle=min(1.0, max(0.0, float(self.throttle))),
            brake=min(1.0, max(0.0, float(self.brake))),
            steer=min(1.0, max(-1.0, float(self.steer))),
            hand_brake=bool(self.hand_brake),
            reverse=bool(self.reverse),
            neutral=bool(self.neutral),
        )


@dataclass
class VehicleState:
    """The controller's view of its own vehicle (own state only)."""

    t: float
    x: float
    y: float
    yaw: float
    """Heading in degrees."""
    speed: float
    """Ground speed in m/s."""
    vx: float = 0.0
    vy: float = 0.0


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------


@dataclass
class RoutePlan:
    """A fixed polyline route with a lateral offset channel.

    The lateral offset is how lane-change and cut-in manoeuvres are produced: the
    pursuit target is displaced sideways from the nominal route, so the vehicle
    smoothly leaves its lane without any map-level lane-change command.
    """

    points: List[Tuple[float, float]] = field(default_factory=list)
    headings: List[float] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.points and not self.headings:
            self.headings = self._derive_headings()

    def _derive_headings(self) -> List[float]:
        out: List[float] = []
        for i in range(len(self.points)):
            j = min(i + 1, len(self.points) - 1)
            k = max(i - 1, 0)
            dx = self.points[j][0] - self.points[k][0]
            dy = self.points[j][1] - self.points[k][1]
            out.append(math.degrees(math.atan2(dy, dx)) if (dx or dy) else 0.0)
        return out

    def __len__(self) -> int:
        return len(self.points)

    def nearest_index(self, x: float, y: float, hint: int = 0) -> int:
        """Index of the closest route point, searching forward from ``hint``.

        Searching forward keeps the controller from snapping back to an earlier
        part of a route that crosses itself (roundabouts, loops).
        """
        if not self.points:
            raise ValueError("route is empty")
        best_i = max(0, min(int(hint), len(self.points) - 1))
        best_d = distance(x, y, *self.points[best_i])
        for i in range(best_i, len(self.points)):
            d = distance(x, y, *self.points[i])
            if d < best_d:
                best_i, best_d = i, d
            elif d > best_d + 12.0:
                # Moving away for a while: the minimum is behind us.
                break
        return best_i

    def lookahead(
        self, x: float, y: float, distance_m: float, hint: int = 0
    ) -> Tuple[float, float, int]:
        """The point ``distance_m`` further along the route, and its index."""
        i = self.nearest_index(x, y, hint)
        travelled = 0.0
        j = i
        while j + 1 < len(self.points) and travelled < float(distance_m):
            travelled += distance(*self.points[j], *self.points[j + 1])
            j += 1
        return (self.points[j][0], self.points[j][1], i)

    def offset_point(self, index: int, lateral_m: float) -> Tuple[float, float]:
        """A route point displaced ``lateral_m`` to its right (positive = right)."""
        idx = max(0, min(int(index), len(self.points) - 1))
        px, py = self.points[idx]
        heading = self.headings[idx]
        # +y is to the right of the heading in CARLA's left-handed planar frame.
        rx = -math.sin(math.radians(heading)) * float(lateral_m)
        ry = math.cos(math.radians(heading)) * float(lateral_m)
        return (px + rx, py + ry)

    def remaining_distance(self, index: int) -> float:
        """Route length remaining from ``index`` to the end."""
        total = 0.0
        for i in range(max(0, int(index)), len(self.points) - 1):
            total += distance(*self.points[i], *self.points[i + 1])
        return total


# ---------------------------------------------------------------------------
# Scripted actions
# ---------------------------------------------------------------------------


@dataclass
class ScriptedAction:
    """One named, timed behaviour modification.

    ``action_id`` is a stable name for the configured action.

    Supported kinds
    ---------------
    ``brake``        params: ``intensity`` (0..1)
    ``set_speed``    params: ``target_speed`` (m/s)
    ``lane_shift``   params: ``lateral_m`` (signed, positive = right), applied
                     progressively over ``duration``
    ``hold``         params: ``target_speed``; simply maintains a speed
    ``stop``         full brake and hand brake
    ``indicator``    params: ``side`` (-1 left, +1 right, as ``lane_shift``'s sign); the turn indicator is on
                     during ``duration`` -- a light, independent of any motion (a lane change may go
                     unsignalled, an indicator may stay on with no manoeuvre)

    An action with a ``trigger`` (:class:`cdf.simulation.triggers.ActionTrigger`)
    has no start time of its own: it stays armed (``t_start`` infinite) until
    the runner fires it, then starts ``trigger.reaction_s`` later.  One whose
    trigger never fires never plays.
    """

    action_id: str
    kind: str
    t_start: float
    duration: float = 1.0
    params: Dict[str, float] = field(default_factory=dict)
    enabled: bool = True
    trigger: Optional[Any] = None
    fired_at: Optional[float] = None

    def __post_init__(self) -> None:
        if self.trigger is not None and self.fired_at is None:
            self.t_start = math.inf

    @property
    def armed(self) -> bool:
        """Waiting for its trigger."""
        return self.enabled and self.trigger is not None and self.fired_at is None

    def fire(self, t: float) -> None:
        """The trigger's condition became true at ``t``: start after the reaction delay."""
        if self.fired_at is None:
            self.fired_at = float(t)
            self.t_start = float(t) + float(self.trigger.reaction_s)

    def latest_end(self) -> float:
        """When the action is over at the latest: for an armed one, if it fired at
        the end of its trigger window."""
        if self.armed:
            return float(self.trigger.window_end_s) + float(self.trigger.reaction_s) + float(self.duration)
        return float(self.t_start) + float(self.duration)

    def active_at(self, t: float) -> bool:
        return self.enabled and (self.t_start <= float(t) < self.t_start + self.duration)

    def elapsed_fraction(self, t: float) -> float:
        """Progress through the action in ``[0, 1]``."""
        if self.duration <= 0.0:
            return 1.0
        return max(0.0, min(1.0, (float(t) - self.t_start) / self.duration))

    def started(self, t: float) -> bool:
        return self.enabled and float(t) >= self.t_start

    def describe(self) -> Dict[str, Any]:
        """Serialisable description for the run manifest."""
        out = {
            "action_id": self.action_id,
            "kind": self.kind,
            "t_start": None if math.isinf(self.t_start) else self.t_start,
            "duration": self.duration,
            "params": dict(self.params),
            "enabled": self.enabled,
        }
        if self.trigger is not None:
            out["trigger"] = self.trigger.describe()
            out["fired_at"] = self.fired_at
        return out


# ---------------------------------------------------------------------------
# Longitudinal control
# ---------------------------------------------------------------------------


# A coasting vehicle (post_impact_mode "coast") that has come to rest is held by its brake.
COAST_REST_SPEED_MPS = 0.3
COAST_MIN_S = 0.5


class PIDLongitudinal:
    """A small PI speed controller with anti-windup.

    Derivative action is omitted on purpose: with a fixed 0.05 s step and a noise
    free own-speed signal it adds nothing but sensitivity to step changes in the
    target, which scripted actions produce constantly.
    """

    def __init__(self, kp: float = 0.55, ki: float = 0.12, integral_limit: float = 4.0) -> None:
        self.kp = float(kp)
        self.ki = float(ki)
        self.integral_limit = float(integral_limit)
        self._integral = 0.0

    def reset(self) -> None:
        self._integral = 0.0

    def preload(self, throttle: float) -> None:
        """Start as if already cruising: the integral term alone gives ``throttle`` (within its limit)."""
        self._integral = max(-self.integral_limit, min(self.integral_limit, float(throttle) / self.ki))

    def step(self, target_speed: float, current_speed: float, dt: float) -> Tuple[float, float]:
        """Return ``(throttle, brake)`` for the given speed error."""
        error = float(target_speed) - float(current_speed)
        self._integral += error * float(dt)
        self._integral = max(-self.integral_limit, min(self.integral_limit, self._integral))
        command = self.kp * error + self.ki * self._integral

        if command >= 0.0:
            return (min(1.0, command), 0.0)
        # Release the integral when braking so it does not fight the next accel.
        self._integral = min(self._integral, 0.0)
        return (0.0, min(1.0, -command * 0.6))


# ---------------------------------------------------------------------------
# The scripted controller
# ---------------------------------------------------------------------------


class ScriptedController:
    """Deterministic route-following controller driven by scripted actions.

    Lateral control is pure pursuit against a lookahead point on the route,
    displaced by whatever lateral offset the active ``lane_shift`` actions
    request. Longitudinal control is a PI loop on the current target speed,
    overridden while a ``brake`` or ``stop`` action is active.
    """

    def __init__(
        self,
        participant_id: str,
        route: RoutePlan,
        target_speed: float,
        actions: Optional[Sequence[ScriptedAction]] = None,
        lookahead_base_m: float = 5.0,
        lookahead_time_s: float = 0.6,
        max_steer: float = 0.8,
        steer_gain: float = 0.9,
        steer_rate_limit: float = 0.14,
        post_impact_stop: bool = True,
        post_impact_mode: str = "",
        post_impact_lateral_m: float = 0.0,
        post_impact_deflect_s: float = 1.5,
    ) -> None:
        self.participant_id = participant_id
        self.route = route
        self.base_target_speed = float(target_speed)
        self.actions: List[ScriptedAction] = list(actions or [])
        self.lookahead_base_m = float(lookahead_base_m)
        self.lookahead_time_s = float(lookahead_time_s)
        self.max_steer = float(max_steer)
        self.steer_gain = float(steer_gain)
        self.steer_rate_limit = float(steer_rate_limit)
        self.post_impact_stop = bool(post_impact_stop)
        #: What this vehicle does once it has been hit.
        #:
        #: ``stop``   brake hard, the default and what ``post_impact_stop`` means.
        #: ``coast``  release everything: no throttle, no brake, no steer, and
        #:            let the physics carry the vehicle. This is what a vehicle
        #:            that has just been shunted actually does, and without it
        #:            the speed controller sees it below target and *accelerates*
        #:            into the car in front, so a pushed vehicle looks as though
        #:            it drove into the collision under its own power.  The
        #:            gearbox goes to neutral: with the clutch engaged and no
        #:            throttle, CARLA's engine braking decelerates a car at
        #:            4-7 m/s^2 (measured on the campaign blueprints), several
        #:            times what a real car loses rolling off the pedals.  Once
        #:            the vehicle has come to rest (at least COAST_MIN_S after
        #:            the impact) its brake holds it: in neutral it would
        #:            otherwise roll away down the road's slope.
        #: ``deflect`` coast, and at the same time be carried off line by
        #:            ``post_impact_lateral_m`` over ``post_impact_deflect_s``.
        #:            This is a scenario-generation response to contact, not a
        #:            timed manoeuvre: it has no schedule of its own and cannot
        #:            begin until this vehicle has actually been hit, so a run
        #:            in which the first collision does not happen produces no
        #:            deflection and no second collision either.
        #:
        #:            It exists because CARLA will not reliably carry a struck
        #:            car sideways. Whether the struck vehicle is displaced or
        #:            simply stops depends on which of the two reached the
        #:            crossing first, to within a fifth of a second, and a
        #:            scenario whose story turns on that is not a fixed run.
        #: ``drive``  keep following the route, which ``post_impact_stop: false``
        #:            used to mean on its own.
        self.post_impact_mode = str(
            post_impact_mode or ("stop" if post_impact_stop else "drive")
        ).lower()
        self.post_impact_lateral_m = float(post_impact_lateral_m)
        self.post_impact_deflect_s = max(1e-3, float(post_impact_deflect_s))
        self._impact_t: Optional[float] = None

        self._pid = PIDLongitudinal()
        self._route_hint = 0
        self._last_steer = 0.0
        self._lateral_offset = 0.0
        self._current_target_speed = float(target_speed)
        self._impacted = False
        self._coast_held = False

    # -- state ------------------------------------------------------------

    def reset(self) -> None:
        """Return the controller to its initial state."""
        self._pid.reset()
        self._route_hint = 0
        self._last_steer = 0.0
        self._lateral_offset = 0.0
        self._current_target_speed = self.base_target_speed
        self._impacted = False
        self._impact_t = None
        self._coast_held = False

    def preload_cruise(self, throttle: float) -> None:
        """The vehicle starts the recording already cruising (see ``RawVehicleAgent.hold_initial_velocity``)."""
        self._pid.preload(throttle)

    def notify_impact(self) -> None:
        """Tell the controller its vehicle was hit.

        Post-impact behaviour must be scripted rather than left to physics, so
        that POST_IMPACT_STOP is a reproducible part of the scenario.
        """
        self._impacted = True

    def note_impact_time(self, t: float) -> None:
        """Record when contact happened, for a deflection that follows from it."""
        if self._impact_t is None:
            self._impact_t = float(t)

    def action(self, action_id: str) -> Optional[ScriptedAction]:
        for a in self.actions:
            if a.action_id == action_id:
                return a
        return None

    def describe(self) -> Dict[str, Any]:
        """Serialisable controller description for the run manifest."""
        return {
            "type": "ScriptedController",
            "participant_id": self.participant_id,
            "target_speed": self.base_target_speed,
            "route_points": len(self.route),
            "lookahead_base_m": self.lookahead_base_m,
            "lookahead_time_s": self.lookahead_time_s,
            "actions": [a.describe() for a in self.actions],
        }

    # -- control ----------------------------------------------------------

    def step(self, state: VehicleState, dt: float) -> ControlCommand:
        """Compute the actuation command for this tick."""
        if self._impacted:
            if self._impact_t is None:
                self._impact_t = float(state.t)
            if self.post_impact_mode == "stop":
                return ControlCommand(throttle=0.0, brake=1.0, steer=0.0).clamped()
            if self.post_impact_mode == "coast":
                if (not self._coast_held and state.speed < COAST_REST_SPEED_MPS
                        and float(state.t) - self._impact_t >= COAST_MIN_S):
                    self._coast_held = True
                if self._coast_held:
                    return ControlCommand(throttle=0.0, brake=1.0, steer=0.0).clamped()
                return ControlCommand(throttle=0.0, brake=0.0, steer=0.0, neutral=True).clamped()
            if self.post_impact_mode == "deflect":
                # Coasting, and steered off line by however far the scenario
                # says the impact carried it. The offset ramps in with the same
                # raised cosine a lane shift uses, so the path is a push rather
                # than a swerve.
                frac = min(1.0, (float(state.t) - self._impact_t)
                           / self.post_impact_deflect_s)
                smooth = 0.5 * (1.0 - math.cos(math.pi * frac))
                offset = self.post_impact_lateral_m * smooth
                self._lateral_offset = offset
                return ControlCommand(
                    throttle=0.0, brake=0.0, steer=self._steer(state, offset)
                ).clamped()

        target_speed = self._resolve_target_speed(state.t)
        lateral = self._resolve_lateral_offset(state.t)
        brake_override = self._resolve_brake_override(state.t)

        steer = self._steer(state, lateral)

        if brake_override is not None:
            throttle, brake = 0.0, brake_override
            self._pid.reset()
        else:
            throttle, brake = self._pid.step(target_speed, state.speed, dt)

        return ControlCommand(
            throttle=throttle, brake=brake, steer=steer, hand_brake=False
        ).clamped()

    def indicator(self, t: float) -> int:
        """The side of the turn indicator the scripted ``indicator`` actions ask for at ``t`` (-1 left, +1 right,
        0 off; the latest started active action wins).  Independent of the vehicle's motion and of its impacts."""
        side, started = 0, -math.inf
        for a in self.actions:
            if a.kind == "indicator" and a.active_at(t) and a.t_start >= started:
                side, started = (-1 if float(a.params.get("side", 0.0)) < 0 else 1), a.t_start
        return side

    def _resolve_target_speed(self, t: float) -> float:
        """Latest ``set_speed``/``hold`` action that has started wins."""
        speed = self.base_target_speed
        for a in self.actions:
            if a.kind in ("set_speed", "hold") and a.started(t):
                speed = float(a.params.get("target_speed", speed))
        self._current_target_speed = speed
        return speed

    def _resolve_brake_override(self, t: float) -> Optional[float]:
        """Strongest active braking command, if any."""
        best: Optional[float] = None
        for a in self.actions:
            if a.kind == "brake" and a.active_at(t):
                intensity = float(a.params.get("intensity", 1.0))
                best = intensity if best is None else max(best, intensity)
            elif a.kind == "stop" and a.started(t):
                best = 1.0
        return best

    def _resolve_lateral_offset(self, t: float) -> float:
        """Accumulated lateral displacement requested by ``lane_shift`` actions.

        The offset ramps in smoothly with a raised-cosine profile, which produces
        a realistic cut-in trajectory instead of a step that the pursuit
        controller would chase with a violent steer.
        """
        offset = 0.0
        for a in self.actions:
            if a.kind != "lane_shift" or not a.enabled:
                continue
            if float(t) < a.t_start:
                continue
            target = float(a.params.get("lateral_m", 0.0))
            frac = a.elapsed_fraction(t)
            smooth = 0.5 * (1.0 - math.cos(math.pi * frac))
            offset += target * smooth
        self._lateral_offset = offset
        return offset

    def _steer(self, state: VehicleState, lateral_offset: float) -> float:
        """Pure-pursuit steering toward a laterally displaced lookahead point."""
        if len(self.route) < 2:
            return 0.0
        lookahead_m = self.lookahead_base_m + self.lookahead_time_s * max(0.0, state.speed)
        tx, ty, idx = self.route.lookahead(state.x, state.y, lookahead_m, self._route_hint)
        self._route_hint = idx

        if abs(lateral_offset) > 1e-6:
            # Displace the pursuit target sideways relative to the route heading.
            look_idx = min(len(self.route) - 1, idx + self._points_ahead(idx, lookahead_m))
            tx, ty = self.route.offset_point(look_idx, lateral_offset)

        desired_heading = math.degrees(math.atan2(ty - state.y, tx - state.x))
        error = angle_diff_deg(desired_heading, state.yaw)
        steer = self.steer_gain * (error / 45.0)
        steer = max(-self.max_steer, min(self.max_steer, steer))

        # Rate limiting keeps the trajectory smooth and reproducible.
        delta = max(-self.steer_rate_limit, min(self.steer_rate_limit, steer - self._last_steer))
        steer = self._last_steer + delta
        self._last_steer = steer
        return steer

    def _points_ahead(self, index: int, lookahead_m: float) -> int:
        """How many route points ``lookahead_m`` corresponds to from ``index``."""
        travelled = 0.0
        j = index
        while j + 1 < len(self.route) and travelled < lookahead_m:
            travelled += distance(*self.route.points[j], *self.route.points[j + 1])
            j += 1
        return j - index

    # -- controller state used by the runner ------------------------------

    @property
    def lateral_offset(self) -> float:
        """The lateral displacement currently commanded (metres, + = right)."""
        return self._lateral_offset

    @property
    def target_speed(self) -> float:
        """The speed the controller is currently aiming for (m/s)."""
        return self._current_target_speed

    @property
    def impacted(self) -> bool:
        return self._impacted
