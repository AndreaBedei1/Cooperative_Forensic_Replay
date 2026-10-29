"""Privileged triggers for scripted actions (scenario construction only).

A triggered action has no fixed start time.  It is armed when the run starts
and fires when a condition on the simulator's true state becomes true; it then
starts ``reaction_s`` later and plays exactly like a timed action.  This is how
a scenario makes one vehicle *react* to another (an evasive manoeuvre that
happens because a car cut in, and does not happen when it does not) instead of
replaying a schedule that coincides with it.

The condition reads true poses of other actors, which no recorder has.  That is
legitimate for building a scenario and for nothing else: firings are written to
``ground_truth/triggers.jsonl`` only, never to ``vehicles/``, and the
reconstruction never sees them.  A trigger whose target is not in the run (a
counterfactual without that vehicle) can never fire.

Kinds:

``envelope_entry``
    Fires the first time any part of the target's true bounding box lies in a
    corridor ahead of the owner's front face: ``ahead_m`` long, as wide as the
    owner plus ``lateral_margin_m`` on each side, in the owner's own frame.

``corridor_clearance``
    Fires the first time the target's true bounding box is inside the owner's
    lateral corridor (as wide as the owner plus ``lateral_margin_m`` on each
    side) with some of it ahead of the owner's front face, and the clearance
    from that face to the nearest part of the box inside the corridor is at
    most ``clearance_m``: a vehicle that cuts in close, measured box to box
    (exact geometry, any orientation; negative when the part inside the
    corridor reaches back beside the owner).  The firing record carries the
    measured clearance.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple

__all__ = ["ActionTrigger", "Pose", "TRIGGER_KINDS", "envelope_entry", "box_outline", "corridor_front_clearance"]

TRIGGER_KINDS = ("envelope_entry", "corridor_clearance")


@dataclass(frozen=True)
class Pose:
    """A vehicle's true planar pose and bounding box (centre, yaw, half extents)."""

    x: float
    y: float
    yaw_deg: float
    half_length: float
    half_width: float


@dataclass
class ActionTrigger:
    """When an armed action fires.  See the module docstring."""

    kind: str
    target: str
    ahead_m: float = 15.0
    lateral_margin_m: float = 0.3
    reaction_s: float = 0.5
    window_start_s: float = 0.0
    window_end_s: float = math.inf
    clearance_m: float = 3.0

    def __post_init__(self) -> None:
        if self.kind not in TRIGGER_KINDS:
            raise ValueError("unknown trigger kind {0!r} (known: {1})".format(self.kind, ", ".join(TRIGGER_KINDS)))
        if not self.target:
            raise ValueError("a trigger needs a target participant")
        if self.ahead_m <= 0.0 or self.reaction_s < 0.0 or self.lateral_margin_m < 0.0 or self.clearance_m < 0.0:
            raise ValueError("trigger distances and delays must be non-negative (ahead_m > 0)")
        if self.window_end_s < self.window_start_s:
            raise ValueError("trigger window ends before it starts")

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "ActionTrigger":
        window = d.get("window_s") or [0.0, math.inf]
        return ActionTrigger(
            kind=str(d.get("kind", "")),
            target=str(d.get("target", "")),
            ahead_m=float(d.get("ahead_m", 15.0)),
            lateral_margin_m=float(d.get("lateral_margin_m", 0.3)),
            reaction_s=float(d.get("reaction_s", 0.5)),
            window_start_s=float(window[0]),
            window_end_s=float(window[1]),
            clearance_m=float(d.get("clearance_m", 3.0)),
        )

    def in_window(self, t: float) -> bool:
        return self.window_start_s <= float(t) <= self.window_end_s

    def condition(self, owner: Pose, target: Pose) -> bool:
        if self.kind == "envelope_entry":
            return envelope_entry(owner, target, self.ahead_m, self.lateral_margin_m)
        if self.kind == "corridor_clearance":
            clearance = corridor_front_clearance(owner, target, self.lateral_margin_m)
            return clearance is not None and clearance <= self.clearance_m
        raise ValueError(self.kind)

    def measure(self, owner: Pose, target: Pose) -> Dict[str, float]:
        """What the condition measured (for the privileged firing record)."""
        if self.kind == "corridor_clearance":
            clearance = corridor_front_clearance(owner, target, self.lateral_margin_m)
            return {} if clearance is None else {"front_clearance_m": round(clearance, 3)}
        return {}

    def describe(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"kind": self.kind, "target": self.target}
        if self.kind == "corridor_clearance":
            out["clearance_m"] = self.clearance_m
        else:
            out["ahead_m"] = self.ahead_m
        out.update({"lateral_margin_m": self.lateral_margin_m, "reaction_s": self.reaction_s,
                    "window_s": [self.window_start_s, None if math.isinf(self.window_end_s) else self.window_end_s]})
        return out


def box_outline(pose: Pose, step: float = 0.25) -> List[Tuple[float, float]]:
    """Points every ``step`` metres along a box's outline, world frame."""
    c, s = math.cos(math.radians(pose.yaw_deg)), math.sin(math.radians(pose.yaw_deg))
    ex, ey = pose.half_length, pose.half_width

    def ticks(extent: float) -> Iterable[float]:
        n = max(1, int(math.ceil(2.0 * extent / step)))
        return [-extent + 2.0 * extent * i / n for i in range(n + 1)]

    local = [(x, side * ey) for x in ticks(ex) for side in (-1.0, 1.0)]
    local += [(side * ex, y) for y in ticks(ey) for side in (-1.0, 1.0)]
    return [(pose.x + c * x - s * y, pose.y + s * x + c * y) for x, y in local]


def envelope_entry(owner: Pose, target: Pose, ahead_m: float, lateral_margin_m: float) -> bool:
    """Is any part of ``target``'s box inside the corridor ahead of ``owner``'s front face?

    Owner frame: x forward, y to the right (CARLA's left-handed convention);
    the corridor is ``half_length < x <= half_length + ahead_m`` and
    ``|y| <= half_width + lateral_margin_m``.
    """
    c, s = math.cos(math.radians(owner.yaw_deg)), math.sin(math.radians(owner.yaw_deg))
    front = owner.half_length
    half = owner.half_width + lateral_margin_m
    for px, py in box_outline(target):
        dx, dy = px - owner.x, py - owner.y
        along = c * dx + s * dy
        across = -s * dx + c * dy
        if front < along <= front + ahead_m and abs(across) <= half:
            return True
    return False


def _in_owner_frame(owner: Pose, pose: Pose) -> List[Tuple[float, float]]:
    """The corners of ``pose``'s box in ``owner``'s frame (x forward, y right)."""
    c, s = math.cos(math.radians(owner.yaw_deg)), math.sin(math.radians(owner.yaw_deg))
    tc, ts = math.cos(math.radians(pose.yaw_deg)), math.sin(math.radians(pose.yaw_deg))
    corners = []
    for lx, ly in ((pose.half_length, -pose.half_width), (pose.half_length, pose.half_width),
                   (-pose.half_length, pose.half_width), (-pose.half_length, -pose.half_width)):
        dx = pose.x + tc * lx - ts * ly - owner.x
        dy = pose.y + ts * lx + tc * ly - owner.y
        corners.append((c * dx + s * dy, -s * dx + c * dy))
    return corners


def _clip(polygon: List[Tuple[float, float]], inside: Any, cut: Any) -> List[Tuple[float, float]]:
    """One Sutherland-Hodgman step: keep the part of a convex polygon where ``inside(point)``."""
    out: List[Tuple[float, float]] = []
    for i, current in enumerate(polygon):
        previous = polygon[i - 1]
        if inside(current):
            if not inside(previous):
                out.append(cut(previous, current))
            out.append(current)
        elif inside(previous):
            out.append(cut(previous, current))
    return out


def corridor_front_clearance(owner: Pose, target: Pose, lateral_margin_m: float) -> Optional[float]:
    """Clearance from ``owner``'s front face to the part of ``target``'s box inside its corridor.

    The corridor is ``|y| <= half_width + lateral_margin_m`` in the owner's frame
    (x forward, y right).  None when no part of the target's box is inside it
    ahead of the front face; negative when the part inside reaches back beside
    the owner.  Exact box geometry, any relative orientation.
    """
    half = owner.half_width + lateral_margin_m

    def cut_at(y_limit: float) -> Any:
        def cut(p: Tuple[float, float], q: Tuple[float, float]) -> Tuple[float, float]:
            f = (y_limit - p[1]) / (q[1] - p[1])
            return p[0] + f * (q[0] - p[0]), y_limit
        return cut

    polygon = _clip(_in_owner_frame(owner, target), lambda p: p[1] <= half, cut_at(half))
    polygon = _clip(polygon, lambda p: p[1] >= -half, cut_at(-half))
    if not polygon or max(x for x, _ in polygon) <= owner.half_length:
        return None
    return min(x for x, _ in polygon) - owner.half_length


def fire_due_triggers(t: float, poses: Dict[str, Pose], armed: Iterable[Tuple[str, Any]]) -> List[Dict[str, Any]]:
    """Fire every armed action whose condition holds at scenario time ``t``.

    ``armed`` yields ``(owner_id, action)`` for actions with a trigger that has
    not fired yet; ``poses`` holds every participant actually in the run.
    Returns one privileged record per firing.
    """
    fired = []
    for owner_id, action in armed:
        trigger: Optional[ActionTrigger] = action.trigger
        if trigger is None or action.fired_at is not None or not trigger.in_window(t):
            continue
        owner, target = poses.get(owner_id), poses.get(trigger.target)
        if owner is None or target is None:
            continue  # the target is not in this run: the action can never fire
        if trigger.condition(owner, target):
            action.fire(t)
            record = {"t_scenario": round(float(t), 4), "participant_id": owner_id,
                      "action_id": action.action_id, "trigger": trigger.describe(),
                      "action_t_start": round(float(action.t_start), 4)}
            measured = trigger.measure(owner, target)
            if measured:
                record["measured"] = measured
            fired.append(record)
    return fired
