
from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

from ..common.config import Config
from ..common.geometry import angle_diff_deg, distance
from .carla_client import import_carla
from .controllers import RoutePlan, ScriptedAction, ScriptedController
from .triggers import ActionTrigger

LOGGER = logging.getLogger(__name__)

__all__ = [
    "SpawnSpec",
    "RouteSpec",
    "ParticipantSpec",
    "ScenarioSpec",
    "build_route",
    "resolve_spawn_waypoint",
    "junction_approach_waypoint",
]




@dataclass
class SpawnSpec:

    anchor: str = "spawn_index"
    index: int = 0
    x: float = 0.0
    y: float = 0.0
    junction_x: float = 0.0
    junction_y: float = 0.0
    bearing_deg: float = 0.0
    back_m: float = 40.0
    forward_m: float = 0.0
    lane_offset: int = 0

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "SpawnSpec":
        return SpawnSpec(
            anchor=d.get("anchor", "spawn_index"),
            index=int(d.get("index", 0)),
            x=float(d.get("x", 0.0)),
            y=float(d.get("y", 0.0)),
            junction_x=float(d.get("junction_x", 0.0)),
            junction_y=float(d.get("junction_y", 0.0)),
            bearing_deg=float(d.get("bearing_deg", 0.0)),
            back_m=float(d.get("back_m", 40.0)),
            forward_m=float(d.get("forward_m", 0.0)),
            lane_offset=int(d.get("lane_offset", 0)),
        )


@dataclass
class RouteSpec:

    length_m: float = 200.0
    step_m: float = 2.0
    turns: List[str] = field(default_factory=list)
    """Turn decisions consumed in order at successive junctions:
    ``"straight"``, ``"left"`` or ``"right"``. Exhausted decisions default to
    ``"straight"``."""

    turn_lookahead: bool = False
    """Resolve a turn by where each candidate *leads* rather than by its own
    heading at the junction entry.

    Off by default, and deliberately so. At a junction entry every connecting
    lane still runs along the approach, so the candidates' own headings can sit
    within a degree of each other while leading to different roads; the decision
    is then settled by which lane CARLA lists first, and ``left``, ``right`` and
    ``straight`` all select the same one. Looking downstream fixes that, but it
    also changes which exit a roundabout takes, and S07 is frozen on the original
    choice. So the scenarios that need a turn they can rely on ask for this, and
    the ones recorded before it keep exactly the routes they were recorded with.
    """

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "RouteSpec":
        return RouteSpec(
            length_m=float(d.get("length_m", 200.0)),
            step_m=float(d.get("step_m", 2.0)),
            turns=[str(t) for t in d.get("turns", [])],
            turn_lookahead=bool(d.get("turn_lookahead", False)),
        )


@dataclass
class ParticipantSpec:

    participant_id: str
    blueprint: str = "vehicle.tesla.model3"
    spawn: SpawnSpec = field(default_factory=SpawnSpec)
    route: RouteSpec = field(default_factory=RouteSpec)
    initial_speed: float = 0.0
    """Velocity imparted at spawn, m/s, so the encounter does not need a long
    acceleration run-up."""
    target_speed: float = 12.0
    sensor_profile: Optional[str] = None
    """Per-participant radar profile override (``configs/sensors/<name>.yaml``).
    No campaign scenario uses one: every vehicle carries the baseline radars."""
    actions: List[ScriptedAction] = field(default_factory=list)
    post_impact_stop: bool = True
    post_impact_mode: str = ""
    """``stop``, ``coast``, ``deflect`` or ``drive``. Empty keeps whatever
    ``post_impact_stop`` says, so no existing scenario changes behaviour."""
    post_impact_lateral_m: float = 0.0
    """How far ``deflect`` carries this vehicle off its line, signed, positive
    to the right of travel. Ignored in every other mode."""
    post_impact_deflect_s: float = 1.5
    """How long that displacement takes to come in."""
    record: bool = True
    """``false``: a physical vehicle that is not a recorder.  It is spawned, drives,
    is seen by the others' sensors and is in ``ground_truth/``, but carries no
    sensors and writes nothing under ``vehicles/``; the run's ``metadata.json``
    lists recorders only."""

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "ParticipantSpec":
        actions = []
        for a in d.get("actions", []) or []:
            trigger = a.get("trigger")
            if trigger is not None and "t_start" in a:
                raise ValueError("action {0!r} has both a trigger and a t_start".format(a["action_id"]))
            actions.append(
                ScriptedAction(
                    action_id=a["action_id"],
                    kind=a["kind"],
                    t_start=float(a.get("t_start", 0.0)),
                    duration=float(a.get("duration", 1.0)),
                    params={k: float(v) for k, v in (a.get("params", {}) or {}).items()},
                    enabled=bool(a.get("enabled", True)),
                    trigger=None if trigger is None else ActionTrigger.from_dict(trigger),
                )
            )
        return ParticipantSpec(
            participant_id=str(d["id"]),
            blueprint=d.get("blueprint", "vehicle.tesla.model3"),
            spawn=SpawnSpec.from_dict(d.get("spawn", {}) or {}),
            route=RouteSpec.from_dict(d.get("route", {}) or {}),
            initial_speed=float(d.get("initial_speed", 0.0)),
            target_speed=float(d.get("target_speed", 12.0)),
            sensor_profile=d.get("sensor_profile"),
            actions=actions,
            post_impact_stop=bool(d.get("post_impact_stop", True)),
            post_impact_mode=str(d.get("post_impact_mode", "") or ""),
            post_impact_lateral_m=float(d.get("post_impact_lateral_m", 0.0)),
            post_impact_deflect_s=float(d.get("post_impact_deflect_s", 1.5)),
            record=bool(d.get("record", True)),
        )


@dataclass
class ScenarioSpec:

    scenario_id: str
    name: str
    description: str = ""
    map_name: str = "Town05"
    variant: str = "default"
    participants: List[ParticipantSpec] = field(default_factory=list)

    max_duration_s: float = 30.0
    context: Dict[str, Any] = field(default_factory=dict)

    def participant(self, participant_id: str) -> ParticipantSpec:
        for p in self.participants:
            if p.participant_id == participant_id:
                return p
        raise KeyError("no participant {0!r} in scenario {1}".format(participant_id, self.scenario_id))

    @property
    def participant_ids(self) -> List[str]:
        return [p.participant_id for p in self.participants]

    @property
    def recorder_ids(self) -> List[str]:
        return [p.participant_id for p in self.participants if p.record]

    def without(self, participant_ids: Sequence[str]) -> "ScenarioSpec":
        unknown = sorted(set(participant_ids) - set(self.participant_ids))
        if unknown:
            raise KeyError("no participant(s) {0} in scenario {1}".format(unknown, self.scenario_id))
        kept = [p for p in self.participants if p.participant_id not in set(participant_ids)]
        return ScenarioSpec(scenario_id=self.scenario_id, name=self.name, description=self.description,
                            map_name=self.map_name, variant=self.variant, participants=kept,
                            max_duration_s=self.max_duration_s, context=dict(self.context))

    @staticmethod
    def from_config(cfg: Config, variant: Optional[str] = None) -> "ScenarioSpec":
        from ..common.config import deep_merge

        block = cfg.get("scenario", None)
        if block is None:
            raise KeyError(
                "configuration has no 'scenario' section; was a scenario config loaded?"
            )
        chosen = variant or block.get("default_variant", "default")
        variants = block.get("variants", {}) or {}
        if chosen != "default" and chosen not in variants:
            raise KeyError(
                "scenario {0} has no variant {1!r} (available: {2})".format(
                    block.get("scenario_id"), chosen, sorted(variants.keys()) or ["default"]
                )
            )
        merged = dict(block)
        if chosen in variants:
            merged = deep_merge(merged, variants[chosen] or {})
        overrides = merged.pop("participant_overrides", {}) or {}
        participants = []
        for pdict in merged.get("participants", []) or []:
            pid = str(pdict["id"])
            if pid in overrides:
                pdict = deep_merge(pdict, overrides[pid] or {})
            participants.append(ParticipantSpec.from_dict(pdict))

        spec = ScenarioSpec(
            scenario_id=str(merged["scenario_id"]),
            name=str(merged.get("name", merged["scenario_id"])),
            description=str(merged.get("description", "")),
            map_name=str(merged.get("map", "Town05")),
            variant=chosen,
            participants=participants,
            max_duration_s=float(merged.get("max_duration_s", 30.0)),
            context=dict(merged.get("context") or {}),
        )
        ids = spec.participant_ids
        if len(set(ids)) != len(ids):
            raise ValueError("scenario {0}: duplicate participant ids {1}".format(spec.scenario_id, ids))
        if spec.participants and not spec.recorder_ids:
            raise ValueError("scenario {0}: no participant records".format(spec.scenario_id))
        for participant in spec.participants:
            for action in participant.actions:
                if action.trigger is not None and action.trigger.target not in ids:
                    raise ValueError("scenario {0}: {1} triggers on unknown participant {2!r}".format(
                        spec.scenario_id, action.action_id, action.trigger.target))
        return spec




def junction_approach_waypoint(
    carla_map: Any,
    junction_x: float,
    junction_y: float,
    bearing_deg: float,
    back_m: float,
    search_radius: float = 60.0,
    sample_step: float = 2.0,
) -> Any:
    carla = import_carla()
    best = None
    best_score = float("inf")

    for wp in carla_map.generate_waypoints(sample_step):
        if wp.lane_type != carla.LaneType.Driving or wp.is_junction:
            continue
        loc = wp.transform.location
        d = distance(loc.x, loc.y, junction_x, junction_y)
        if d > search_radius or d < 8.0:
            continue
        heading = wp.transform.rotation.yaw
        to_junction = math.degrees(math.atan2(junction_y - loc.y, junction_x - loc.x))
        if abs(angle_diff_deg(heading, to_junction)) > 35.0:
            continue
        bearing_err = abs(angle_diff_deg(heading, bearing_deg))
        if bearing_err > 30.0:
            continue
        score = abs(d - back_m) + bearing_err * 0.5
        if score < best_score:
            best_score = score
            best = wp

    if best is None:
        raise ValueError(
            "no lane approaches junction ({0:.1f}, {1:.1f}) on bearing {2:.1f} deg "
            "within {3:.0f} m".format(junction_x, junction_y, bearing_deg, search_radius)
        )
    return best


def resolve_spawn_waypoint(carla_map: Any, spawn_points: Sequence[Any], spec: SpawnSpec) -> Any:
    carla = import_carla()

    if spec.anchor == "spawn_index":
        if not 0 <= spec.index < len(spawn_points):
            raise IndexError(
                "spawn index {0} out of range (map has {1} spawn points)".format(
                    spec.index, len(spawn_points)
                )
            )
        wp = carla_map.get_waypoint(
            spawn_points[spec.index].location,
            project_to_road=True,
            lane_type=carla.LaneType.Driving,
        )
    elif spec.anchor == "location":
        wp = carla_map.get_waypoint(
            carla.Location(x=spec.x, y=spec.y, z=0.0),
            project_to_road=True,
            lane_type=carla.LaneType.Driving,
        )
    elif spec.anchor == "junction_approach":
        wp = junction_approach_waypoint(
            carla_map,
            spec.junction_x,
            spec.junction_y,
            spec.bearing_deg,
            spec.back_m,
        )
    else:
        raise ValueError("unknown spawn anchor {0!r}".format(spec.anchor))

    if wp is None:
        raise ValueError("spawn spec {0!r} did not resolve to a driving lane".format(spec))

    for _ in range(abs(spec.lane_offset)):
        nxt = wp.get_right_lane() if spec.lane_offset > 0 else wp.get_left_lane()
        if nxt is None or nxt.lane_type != carla.LaneType.Driving or nxt.lane_id * wp.lane_id < 0:
            raise ValueError(
                "participant requests lane_offset {0} but no same-direction drivable "
                "lane exists there".format(spec.lane_offset)
            )
        wp = nxt

    if abs(spec.forward_m) > 1e-6:
        nxts = wp.next(abs(spec.forward_m)) if spec.forward_m > 0 else wp.previous(abs(spec.forward_m))
        if not nxts:
            raise ValueError(
                "cannot offset spawn by {0} m along the lane".format(spec.forward_m)
            )
        wp = nxts[0]
    return wp


def build_route(carla_map: Any, start_wp: Any, spec: RouteSpec) -> RoutePlan:
    points: List[Tuple[float, float]] = []
    headings: List[float] = []

    wp = start_wp
    turns = list(spec.turns)
    travelled = 0.0
    step = max(0.5, float(spec.step_m))
    guard = int(spec.length_m / step) * 4 + 100

    while travelled < float(spec.length_m) and guard > 0:
        guard -= 1
        tf = wp.transform
        points.append((float(tf.location.x), float(tf.location.y)))
        headings.append(float(tf.rotation.yaw))

        candidates = wp.next(step)
        if not candidates:
            LOGGER.warning(
                "route ended early after %.1f m of %.1f m requested", travelled, spec.length_m
            )
            break
        if len(candidates) == 1:
            wp = candidates[0]
        else:
            decision = turns.pop(0) if turns else "straight"
            wp = _choose_successor(
                wp, candidates, decision, lookahead=spec.turn_lookahead
            )
        travelled += step

    if len(points) < 2:
        raise ValueError("route degenerated to fewer than two points")
    return RoutePlan(points=points, headings=headings)


def _eventual_heading(candidate: Any, probe_m: float = 14.0) -> float:
    wp = candidate
    travelled = 0.0
    step = 2.0
    while travelled < probe_m:
        nxt = wp.next(step)
        if not nxt or len(nxt) > 1:
            break
        wp = nxt[0]
        travelled += step
    return float(wp.transform.rotation.yaw)


def _choose_successor(
    current: Any,
    candidates: Sequence[Any],
    decision: str,
    lookahead: bool = False,
) -> Any:
    base = current.transform.rotation.yaw
    scored: List[Tuple[float, Any]] = []
    for c in candidates:
        delta = angle_diff_deg(c.transform.rotation.yaw, base)
        scored.append((delta, c))

    if lookahead and len(scored) > 1 and max(abs(d) for d, _ in scored) < 10.0:
        scored = [
            (angle_diff_deg(_eventual_heading(c), base), c) for _, c in scored
        ]

    decision = (decision or "straight").lower()
    if decision == "straight":
        return min(scored, key=lambda s: abs(s[0]))[1]
    if decision == "right":
        rights = [s for s in scored if s[0] > 12.0]
        return max(rights, key=lambda s: s[0])[1] if rights else min(
            scored, key=lambda s: abs(s[0])
        )[1]
    if decision == "left":
        lefts = [s for s in scored if s[0] < -12.0]
        return min(lefts, key=lambda s: s[0])[1] if lefts else min(
            scored, key=lambda s: abs(s[0])
        )[1]
    raise ValueError("unknown turn decision {0!r}".format(decision))


def make_controller(spec: ParticipantSpec, route: RoutePlan) -> ScriptedController:
    return ScriptedController(
        participant_id=spec.participant_id,
        route=route,
        target_speed=spec.target_speed,
        actions=list(spec.actions),
        post_impact_stop=spec.post_impact_stop,
        post_impact_mode=spec.post_impact_mode,
        post_impact_lateral_m=spec.post_impact_lateral_m,
        post_impact_deflect_s=spec.post_impact_deflect_s,
    )
