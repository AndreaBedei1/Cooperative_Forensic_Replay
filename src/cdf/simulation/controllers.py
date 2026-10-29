
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

    throttle: float = 0.0
    brake: float = 0.0
    steer: float = 0.0
    hand_brake: bool = False
    reverse: bool = False
    neutral: bool = False

    def clamped(self) -> "ControlCommand":
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

    t: float
    x: float
    y: float
    yaw: float
    """Heading in degrees."""
    speed: float
    """Ground speed in m/s."""
    vx: float = 0.0
    vy: float = 0.0




@dataclass
class RoutePlan:

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
        if not self.points:
            raise ValueError("route is empty")
        best_i = max(0, min(int(hint), len(self.points) - 1))
        best_d = distance(x, y, *self.points[best_i])
        for i in range(best_i, len(self.points)):
            d = distance(x, y, *self.points[i])
            if d < best_d:
                best_i, best_d = i, d
            elif d > best_d + 12.0:
                break
        return best_i

    def lookahead(
        self, x: float, y: float, distance_m: float, hint: int = 0
    ) -> Tuple[float, float, int]:
        i = self.nearest_index(x, y, hint)
        travelled = 0.0
        j = i
        while j + 1 < len(self.points) and travelled < float(distance_m):
            travelled += distance(*self.points[j], *self.points[j + 1])
            j += 1
        return (self.points[j][0], self.points[j][1], i)

    def offset_point(self, index: int, lateral_m: float) -> Tuple[float, float]:
        idx = max(0, min(int(index), len(self.points) - 1))
        px, py = self.points[idx]
        heading = self.headings[idx]
        rx = -math.sin(math.radians(heading)) * float(lateral_m)
        ry = math.cos(math.radians(heading)) * float(lateral_m)
        return (px + rx, py + ry)

    def remaining_distance(self, index: int) -> float:
        total = 0.0
        for i in range(max(0, int(index)), len(self.points) - 1):
            total += distance(*self.points[i], *self.points[i + 1])
        return total




@dataclass
class ScriptedAction:

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
        return self.enabled and self.trigger is not None and self.fired_at is None

    def fire(self, t: float) -> None:
        if self.fired_at is None:
            self.fired_at = float(t)
            self.t_start = float(t) + float(self.trigger.reaction_s)

    def latest_end(self) -> float:
        if self.armed:
            return float(self.trigger.window_end_s) + float(self.trigger.reaction_s) + float(self.duration)
        return float(self.t_start) + float(self.duration)

    def active_at(self, t: float) -> bool:
        return self.enabled and (self.t_start <= float(t) < self.t_start + self.duration)

    def elapsed_fraction(self, t: float) -> float:
        if self.duration <= 0.0:
            return 1.0
        return max(0.0, min(1.0, (float(t) - self.t_start) / self.duration))

    def started(self, t: float) -> bool:
        return self.enabled and float(t) >= self.t_start

    def describe(self) -> Dict[str, Any]:
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




COAST_REST_SPEED_MPS = 0.3
COAST_MIN_S = 0.5


class PIDLongitudinal:

    def __init__(self, kp: float = 0.55, ki: float = 0.12, integral_limit: float = 4.0) -> None:
        self.kp = float(kp)
        self.ki = float(ki)
        self.integral_limit = float(integral_limit)
        self._integral = 0.0

    def reset(self) -> None:
        self._integral = 0.0

    def preload(self, throttle: float) -> None:
        self._integral = max(-self.integral_limit, min(self.integral_limit, float(throttle) / self.ki))

    def step(self, target_speed: float, current_speed: float, dt: float) -> Tuple[float, float]:
        error = float(target_speed) - float(current_speed)
        self._integral += error * float(dt)
        self._integral = max(-self.integral_limit, min(self.integral_limit, self._integral))
        command = self.kp * error + self.ki * self._integral

        if command >= 0.0:
            return (min(1.0, command), 0.0)
        self._integral = min(self._integral, 0.0)
        return (0.0, min(1.0, -command * 0.6))




class ScriptedController:

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


    def reset(self) -> None:
        self._pid.reset()
        self._route_hint = 0
        self._last_steer = 0.0
        self._lateral_offset = 0.0
        self._current_target_speed = self.base_target_speed
        self._impacted = False
        self._impact_t = None
        self._coast_held = False

    def preload_cruise(self, throttle: float) -> None:
        self._pid.preload(throttle)

    def notify_impact(self) -> None:
        self._impacted = True

    def note_impact_time(self, t: float) -> None:
        if self._impact_t is None:
            self._impact_t = float(t)

    def action(self, action_id: str) -> Optional[ScriptedAction]:
        for a in self.actions:
            if a.action_id == action_id:
                return a
        return None

    def describe(self) -> Dict[str, Any]:
        return {
            "type": "ScriptedController",
            "participant_id": self.participant_id,
            "target_speed": self.base_target_speed,
            "route_points": len(self.route),
            "lookahead_base_m": self.lookahead_base_m,
            "lookahead_time_s": self.lookahead_time_s,
            "actions": [a.describe() for a in self.actions],
        }


    def step(self, state: VehicleState, dt: float) -> ControlCommand:
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
        side, started = 0, -math.inf
        for a in self.actions:
            if a.kind == "indicator" and a.active_at(t) and a.t_start >= started:
                side, started = (-1 if float(a.params.get("side", 0.0)) < 0 else 1), a.t_start
        return side

    def _resolve_target_speed(self, t: float) -> float:
        speed = self.base_target_speed
        for a in self.actions:
            if a.kind in ("set_speed", "hold") and a.started(t):
                speed = float(a.params.get("target_speed", speed))
        self._current_target_speed = speed
        return speed

    def _resolve_brake_override(self, t: float) -> Optional[float]:
        best: Optional[float] = None
        for a in self.actions:
            if a.kind == "brake" and a.active_at(t):
                intensity = float(a.params.get("intensity", 1.0))
                best = intensity if best is None else max(best, intensity)
            elif a.kind == "stop" and a.started(t):
                best = 1.0
        return best

    def _resolve_lateral_offset(self, t: float) -> float:
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
        if len(self.route) < 2:
            return 0.0
        lookahead_m = self.lookahead_base_m + self.lookahead_time_s * max(0.0, state.speed)
        tx, ty, idx = self.route.lookahead(state.x, state.y, lookahead_m, self._route_hint)
        self._route_hint = idx

        if abs(lateral_offset) > 1e-6:
            look_idx = min(len(self.route) - 1, idx + self._points_ahead(idx, lookahead_m))
            tx, ty = self.route.offset_point(look_idx, lateral_offset)

        desired_heading = math.degrees(math.atan2(ty - state.y, tx - state.x))
        error = angle_diff_deg(desired_heading, state.yaw)
        steer = self.steer_gain * (error / 45.0)
        steer = max(-self.max_steer, min(self.max_steer, steer))

        delta = max(-self.steer_rate_limit, min(self.steer_rate_limit, steer - self._last_steer))
        steer = self._last_steer + delta
        self._last_steer = steer
        return steer

    def _points_ahead(self, index: int, lookahead_m: float) -> int:
        travelled = 0.0
        j = index
        while j + 1 < len(self.route) and travelled < lookahead_m:
            travelled += distance(*self.route.points[j], *self.route.points[j + 1])
            j += 1
        return j - index


    @property
    def lateral_offset(self) -> float:
        return self._lateral_offset

    @property
    def target_speed(self) -> float:
        return self._current_target_speed

    @property
    def impacted(self) -> bool:
        return self._impacted
