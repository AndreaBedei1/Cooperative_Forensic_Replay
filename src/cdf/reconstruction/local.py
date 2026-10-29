
from __future__ import annotations

import bisect
import json
import math
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np

from ..recording.compact_observations import load_radar_observations
from .config import CollisionConfig, ReconstructionConfig, SemanticsConfig
from .conflict import PREDICTED_OVERLAP, UNSAFE_FORWARD_GAP, ConflictAssessment, assess_conflict, occluded_by
from .road import RoadFrame
from .models import (ACTION, FACT, OUTCOME, PERCEPTION, SAME_TRACK, GraphEdge, GraphNode,
                     LocalGraph, SemanticEvent, TraceFrame, display_order, precedes_edges)
from .tracking import (EgoFootprint, EgoState, EgoTrajectory, LocalTrack, RadarMount, RadarStream,
                       TrackSample, build_local_tracks, ego_trajectory)
from .world_state import UNKNOWN, PerceivedWorld, span_values

PEDAL_RELEASE_DEBOUNCE_S = 0.2
MOVING_SPEED_MPS = 1.0
MIN_EPISODE_S = 0.3
CRITICAL_RELEASE_DEBOUNCE_S = 0.2
STRIKE_CLOSING_WINDOW_S = 0.2
DEFAULT_SIGN_TRACK_GAP_S = 0.6
MIN_RELATIVE_SPEED_MPS = 0.3
SAME_DIRECTION_DEG, OPPOSING_DEG, CROSSING_DEG = 30.0, 150.0, (60.0, 120.0)
SIGN_REACQUIRE_MAX_GAP_S = 5.0
SIGN_REACQUIRE_MAX_SPEED_MPS = 0.5
SIGN_REACQUIRE_MAX_TURN_DEG = 3.0
SIGN_REACQUIRE_MAX_CENTRE_PX = 15.0
SIGN_REACQUIRE_MAX_SIZE_RATIO = 1.25

Span = Tuple[int, Optional[int]]


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _local_time(record: Mapping[str, Any], clock_origin: float, key: str = "timestamp") -> float:
    return round(float(record[key]) - clock_origin, 4)



def active_intervals(times: Sequence[float], values: Sequence[Any], turns_on: Callable[[Any], bool],
                     turns_off: Callable[[Any], bool], release_debounce_s: float = 0.0,
                     initially_on: Optional[bool] = None) -> List[Span]:
    spans: List[Span] = []
    start: Optional[int] = None
    release: Optional[int] = None
    for index, value in enumerate(values):
        if start is None:
            active = initially_on if index == 0 and initially_on is not None else turns_on(value)
            if active:
                start = index
            continue
        if turns_on(value):
            release = None
        elif release is None and turns_off(value):
            release = index
        if release is not None and times[index] - times[release] >= release_debounce_s - 1e-6:
            spans.append((start, release))
            start = release = None
    if start is not None:
        spans.append((start, None))
    return spans


def state_events(owner: str, subject: Optional[str], start_type: str, end_type: str, kind: str,
                 source: str, times: Sequence[float], spans: Sequence[Span],
                 announce_initial: bool = True) -> List[SemanticEvent]:
    events = []
    for start, end in spans:
        if start > 0 or announce_initial:
            attributes = {"active_at_first_observation": True} if start == 0 else {}
            events.append(SemanticEvent(type=start_type, kind=kind, actor_id=owner, subject_id=subject,
                                        t_local=times[start], attributes=attributes, source=source))
        if end is not None:
            events.append(SemanticEvent(type=end_type, kind=kind, actor_id=owner, subject_id=subject,
                                        t_local=times[end], source=source))
    return events


def _gaps(spans: Sequence[Span], count: int) -> List[Span]:
    gaps: List[Span] = []
    cursor = 0
    for start, end in spans:
        if start > cursor:
            gaps.append((cursor, start))
        if end is None:
            return gaps
        cursor = end
    if cursor < count:
        gaps.append((cursor, None))
    return gaps


def _lasting(spans: Sequence[Span], times: Sequence[float], keep: Sequence[Span] = ()) -> List[Span]:
    return [(start, end) for start, end in spans
            if end is None or (start, end) in keep or times[end] - times[start] >= MIN_EPISODE_S - 1e-6]



def control_events(owner: str, controls: Sequence[Mapping[str, Any]], clock_origin: float,
                   cfg: SemanticsConfig, world: Optional[PerceivedWorld] = None) -> List[SemanticEvent]:
    if not controls:
        return []
    times = [_local_time(record, clock_origin) for record in controls]
    brake = [float(record["brake"]) for record in controls]
    level = cfg.brake_onset_threshold
    spans = active_intervals(times, brake, lambda value: value >= level, lambda value: value < level,
                             PEDAL_RELEASE_DEBOUNCE_S)
    throttle = [float(record["throttle"]) for record in controls]
    on, off = cfg.throttle_on_threshold, cfg.throttle_off_threshold
    throttle_spans = active_intervals(times, throttle, lambda value: value >= on, lambda value: value <= off,
                                      cfg.throttle_release_debounce_s)
    if world is not None:
        world.add_ego_state("BRAKE", times, spans)
        world.add_ego_state("THROTTLE", times, throttle_spans)
    return (state_events(owner, None, "BRAKE_START", "BRAKE_END", ACTION, "controls", times, spans)
            + state_events(owner, None, "THROTTLE_START", "THROTTLE_END", ACTION, "controls", times, throttle_spans))


def indicator_events(owner: str, lights: Optional[Sequence[Mapping[str, Any]]], clock_origin: float,
                     start: float, world: Optional[PerceivedWorld] = None) -> List[SemanticEvent]:
    if lights is None:
        if world is not None:
            world.add_ego_unknown("INDICATOR_LEFT", start)
            world.add_ego_unknown("INDICATOR_RIGHT", start)
        return []
    if not lights:
        return []
    times = [_local_time(record, clock_origin) for record in lights]
    events: List[SemanticEvent] = []
    for side, key in (("LEFT", "left_blinker"), ("RIGHT", "right_blinker")):
        values = [bool(record.get(key)) for record in lights]
        spans = active_intervals(times, values, lambda value: value, lambda value: not value)
        if world is not None:
            world.add_ego_state("INDICATOR_" + side, times, spans)
        events += state_events(owner, None, "INDICATOR_{0}_START".format(side), "INDICATOR_{0}_END".format(side),
                               ACTION, "lights", times, spans)
    return events


def yaw_rates(ego: EgoTrajectory, window_s: float) -> List[float]:
    rates = []
    for state in ego.states:
        t0, t1 = state.t_local - window_s, state.t_local
        if t0 < ego.start:
            t0, t1 = ego.start, min(ego.start + window_s, ego.end)
        rates.append(0.0 if t1 - t0 < 1e-6 else math.degrees(ego.at(t1).heading - ego.at(t0).heading) / (t1 - t0))
    return rates


def turn_events(owner: str, ego: EgoTrajectory, cfg: SemanticsConfig,
                world: Optional[PerceivedWorld] = None) -> List[SemanticEvent]:
    times = [state.t_local for state in ego.states]
    headings = [state.heading for state in ego.states]
    speeds = [state.speed for state in ego.states]
    rates = yaw_rates(ego, cfg.turn_yaw_rate_window_s)
    events: List[SemanticEvent] = []
    for name, sign in (("TURN_LEFT", -1.0), ("TURN_RIGHT", 1.0)):
        def turns_on(index: int, sign: float = sign) -> bool:
            return speeds[index] >= cfg.turn_min_speed_mps and sign * rates[index] >= cfg.turn_yaw_rate_on_dps

        def turns_off(index: int, sign: float = sign) -> bool:
            return speeds[index] < cfg.turn_min_speed_mps or sign * rates[index] < cfg.turn_yaw_rate_off_dps

        kept = []
        for start, end in active_intervals(times, list(range(len(times))), turns_on, turns_off,
                                           cfg.turn_release_debounce_s):
            last = len(times) - 1 if end is None else end
            onset = start
            while onset > 0 and not turns_off(onset - 1):
                onset -= 1
            before = ego.at(max(times[onset] - cfg.turn_yaw_rate_window_s, ego.start)).heading
            change = sign * math.degrees(headings[last] - before)
            if (times[last] - times[start] >= cfg.turn_min_duration_s - 1e-6
                    and change >= cfg.turn_min_heading_change_deg):
                kept.append((start, end))
        if world is not None:
            world.add_ego_state(name, times, kept)
        events += state_events(owner, None, name + "_START", name + "_END", FACT, "ego", times, kept)
    return events


def motion_events(owner: str, ego: EgoTrajectory, cfg: SemanticsConfig,
                  speed_limit_kmh: Optional[float], world: Optional[PerceivedWorld] = None) -> List[SemanticEvent]:
    times = [state.t_local for state in ego.states]
    speeds = [state.speed for state in ego.states]
    moving = active_intervals(times, speeds, lambda speed: speed > MOVING_SPEED_MPS,
                              lambda speed: speed < cfg.full_stop_speed_mps,
                              initially_on=speeds[0] >= cfg.full_stop_speed_mps)
    stopped = _gaps(moving, len(times))
    events = state_events(owner, None, "MOVING_START", "MOVING_END", FACT, "ego", times, moving)
    events += state_events(owner, None, "STOP_START", "STOP_END", FACT, "ego", times, stopped)
    if world is not None:
        world.add_ego_state("MOVING", times, moving)
        world.add_ego_state("STOP", times, stopped)
    if speed_limit_kmh is not None:
        limit = float(speed_limit_kmh) / 3.6
        margin = cfg.speed_limit_hysteresis_kmh / 3.6
        speeding = active_intervals(times, speeds, lambda speed: speed > limit + margin,
                                    lambda speed: speed <= limit - margin)
        events += state_events(owner, None, "SPEED_LIMIT_EXCEEDED_START", "SPEED_LIMIT_EXCEEDED_END",
                               FACT, "ego", times, speeding)
        if world is not None:
            world.add_ego_state("SPEED_LIMIT_EXCEEDED", times, speeding)
    elif world is not None:
        world.add_ego_unknown("SPEED_LIMIT_EXCEEDED", times[0])
    return events


def sample_period(ego: EgoTrajectory) -> float:
    times = [float(t) for t in ego.times]
    return statistics.median(b - a for a, b in zip(times, times[1:])) if len(times) > 1 else 0.0


def velocity_jump(ego: EgoTrajectory, t_local: float, period: float) -> Tuple[float, float]:
    before, after = ego.at(t_local - period), ego.at(t_local + period)
    dvx, dvy = after.vx - before.vx, after.vy - before.vy
    return math.hypot(dvx, dvy) / (2.0 * period), math.atan2(dvy, dvx)


def impact_direction_angle(ego: EgoTrajectory, contact_t: float, burst_t: float, period: float,
                           cfg: CollisionConfig) -> Optional[float]:
    if period <= 0.0:
        return None
    first, second = velocity_jump(ego, contact_t, period), velocity_jump(ego, burst_t, period)
    if min(first[0], second[0]) < cfg.impact_acceleration_mps2:
        return None
    return abs(math.degrees(math.remainder(second[1] - first[1], 2.0 * math.pi)))


@dataclass
class Contact:

    first: float
    last: float
    peak: float
    attributes: Dict[str, Any]
    merged: List[Dict[str, Any]]


def collision_events(owner: str, collisions: Sequence[Mapping[str, Any]], clock_origin: float,
                     cfg: CollisionConfig, ego: EgoTrajectory) -> List[SemanticEvent]:
    return contact_events(owner, collision_contacts(collisions, clock_origin, cfg, ego))


def contact_events(owner: str, contacts: Sequence[Contact]) -> List[SemanticEvent]:
    events = []
    for contact in contacts:
        attributes = dict({"peak_impulse": round(contact.peak, 2)}, **contact.attributes)
        if contact.merged:
            attributes["merged_bursts"] = [[round(b["first"], 3), round(b["peak"], 2)] for b in contact.merged]
        events.append(SemanticEvent(type="COLLISION", kind=OUTCOME, actor_id=owner, t_local=contact.first,
                                    attributes=attributes, source="collision_sensor", confidence=1.0))
    return events


def collision_contacts(collisions: Sequence[Mapping[str, Any]], clock_origin: float,
                       cfg: CollisionConfig, ego: EgoTrajectory) -> List[Contact]:
    period = sample_period(ego)
    bursts: List[Dict[str, Any]] = []
    for record in sorted(collisions, key=lambda item: float(item["timestamp"])):
        t_local = _local_time(record, clock_origin)
        impulse = float(record["impulse"])
        if bursts and t_local - bursts[-1]["last"] <= 1.5 * period:
            bursts[-1]["last"] = t_local
            bursts[-1]["peak"] = max(bursts[-1]["peak"], impulse)
        else:
            bursts.append({"first": t_local, "last": t_local, "peak": impulse})

    contacts: List[Dict[str, Any]] = []
    for burst in bursts:
        current = contacts[-1] if contacts else None
        attributes: Dict[str, Any] = {}
        if current is not None and burst["first"] - current["last"] <= cfg.merge_gap_s:
            ratio = burst["peak"] / current["peak"] if current["peak"] > 0 else math.inf
            angle = None
            if burst["peak"] < cfg.min_new_impact_impulse:
                new, evidence = False, None
            elif ratio >= cfg.new_impact_ratio:
                new, evidence = True, "peak"
            elif ratio < cfg.min_impact_ratio:
                new, evidence = False, None
            else:
                angle = impact_direction_angle(ego, current["first"], burst["first"], period, cfg)
                if angle is not None:
                    new, evidence = angle > cfg.reversal_angle_deg, "reversed velocity jump"
                else:
                    new, evidence = ratio >= cfg.undirected_impact_ratio, "peak without direction evidence"
            if not new:
                current["last"] = burst["last"]
                current["peak"] = max(current["peak"], burst["peak"])
                current["merged"].append(burst)
                continue
            attributes["new_contact"] = {"break_s": round(burst["first"] - current["last"], 2),
                                         "peak_ratio": round(ratio, 2), "evidence": evidence}
            if angle is not None:
                attributes["new_contact"]["reversal_deg"] = round(angle)
        contacts.append(dict(burst, attributes=attributes, merged=[]))
    return [Contact(first=contact["first"], last=contact["last"], peak=contact["peak"],
                    attributes=contact["attributes"], merged=contact["merged"]) for contact in contacts]


SIGN_STATES = {"STOP": "STOP_SIGN_DETECTED", "YIELD": "YIELD_SIGN_DETECTED"}


def _stood_still(ego: EgoTrajectory, start: float, end: float) -> bool:
    during = [state for state in ego.states if start - 1e-6 <= state.t_local <= end + 1e-6]
    turn = abs(math.degrees(ego.at(end).heading - ego.at(start).heading))
    return (bool(during) and turn <= SIGN_REACQUIRE_MAX_TURN_DEG
            and all(state.speed <= SIGN_REACQUIRE_MAX_SPEED_MPS for state in during))


def _same_image_place(first: Sequence[float], second: Sequence[float]) -> bool:
    (x1, y1, w1, h1), (x2, y2, w2, h2) = first, second
    if min(w1, h1, w2, h2) <= 0:
        return False
    centre = math.hypot((x1 + w1 / 2.0) - (x2 + w2 / 2.0), (y1 + h1 / 2.0) - (y2 + h2 / 2.0))
    return (centre <= SIGN_REACQUIRE_MAX_CENTRE_PX and max(w1 / w2, w2 / w1) <= SIGN_REACQUIRE_MAX_SIZE_RATIO
            and max(h1 / h2, h2 / h1) <= SIGN_REACQUIRE_MAX_SIZE_RATIO)


def sign_continuity(signs: Sequence[Mapping[str, Any]], clock_origin: float,
                    ego: Optional[EgoTrajectory]) -> Dict[str, str]:
    ordered = sorted(signs, key=lambda record: float(record["timestamp_first"]))
    local_id: Dict[str, str] = {}
    for index, record in enumerate(ordered):
        track_id = str(record["sign_track_id"])
        local_id[track_id] = track_id
        if ego is None or not record.get("best_bbox"):
            continue
        first = _local_time(record, clock_origin, "timestamp_first")
        for earlier in reversed(ordered[:index]):
            if str(earlier.get("class", "")).upper() != str(record.get("class", "")).upper():
                continue
            last = _local_time(earlier, clock_origin, "timestamp_last")
            if (0.0 <= first - last <= SIGN_REACQUIRE_MAX_GAP_S and earlier.get("best_bbox")
                    and _stood_still(ego, last, first) and _same_image_place(earlier["best_bbox"], record["best_bbox"])):
                local_id[track_id] = local_id[str(earlier["sign_track_id"])]
                break
    return local_id


def sign_events(owner: str, signs: Sequence[Mapping[str, Any]], clock_origin: float,
                recording_end: float, track_gap_s: float, ego: Optional[EgoTrajectory] = None,
                world: Optional[PerceivedWorld] = None) -> List[SemanticEvent]:
    events = []
    local_id = sign_continuity(signs, clock_origin, ego)
    for record in sorted(signs, key=lambda item: float(item["timestamp_first"])):
        name = SIGN_STATES.get(str(record.get("class", "")).upper())
        if name is None:
            continue
        track_id = str(record["sign_track_id"])
        subject = local_id[track_id]
        confidence = round(float(record.get("best_confidence", 0.0)), 3)
        start = _local_time(record, clock_origin, "timestamp_confirmed")
        attributes: Dict[str, Any] = {"relevant_to_ego_path": bool(record.get("relevant_to_ego_path"))}
        if subject != track_id:
            attributes.update(reacquired=True, sign_track=track_id)
        events.append(SemanticEvent(
            type=name + "_START", kind=PERCEPTION, actor_id=owner, subject_id=subject,
            t_local=start, attributes=attributes, source="camera", confidence=confidence))
        last = _local_time(record, clock_origin, "timestamp_last")
        end = last if recording_end - last > track_gap_s else None
        if end is not None:
            events.append(SemanticEvent(type=name + "_END", kind=PERCEPTION, actor_id=owner,
                                        subject_id=subject, t_local=end, source="camera", confidence=confidence,
                                        attributes={} if subject == track_id else {"sign_track": track_id}))
        if world is not None:
            world.add_sign(subject, str(record.get("class", "")).upper(), start, bool(record.get("relevant_to_ego_path")))
    return events


@dataclass
class RelativeMotion:

    longitudinal_speed_mps: float
    lateral_speed_mps: float
    heading_deg: Optional[float]
    t_cpa_s: Optional[float]
    d_cpa_m: Optional[float]
    known: bool
    d_cpa_clearance_m: Optional[float] = None


def relative_motion(sample: TrackSample, own: EgoState, cfg: SemanticsConfig,
                    footprint: Optional[EgoFootprint] = None) -> RelativeMotion:
    c, s = math.cos(own.heading), math.sin(own.heading)
    dvx, dvy = sample.vx_mps - own.vx, sample.vy_mps - own.vy
    v_long, v_lat = c * dvx + s * dvy, -s * dvx + c * dvy
    heading = None
    if sample.speed_mps >= 1.0:
        heading = (math.degrees(math.atan2(sample.vy_mps, sample.vx_mps) - own.heading) + 180.0) % 360.0 - 180.0
    speed2 = v_long * v_long + v_lat * v_lat
    t_cpa = d_cpa = d_cpa_clearance = None
    if speed2 >= MIN_RELATIVE_SPEED_MPS ** 2:
        t_cpa = -(sample.longitudinal_m * v_long + sample.lateral_m * v_lat) / speed2
        cpa_long, cpa_lat = sample.longitudinal_m + v_long * t_cpa, sample.lateral_m + v_lat * t_cpa
        d_cpa = math.hypot(cpa_long, cpa_lat)
        horizon = cfg.prediction_horizon_s
        start = (sample.longitudinal_m, sample.lateral_m)
        end = (sample.longitudinal_m + v_long * horizon, sample.lateral_m + v_lat * horizon)
        if footprint is not None:
            miss, _ = footprint.segment_distance(start, end)
        else:
            fraction = min(max(t_cpa / horizon, 0.0), 1.0)
            miss = math.hypot(start[0] + fraction * (end[0] - start[0]), start[1] + fraction * (end[1] - start[1]))
        d_cpa_clearance = max(miss - sample.surface_offset_m, 0.0)
    known = (not sample.identity_ambiguous and sample.pos_std_m <= cfg.max_position_std_m
             and sample.vel_std_mps <= cfg.max_velocity_std_mps)
    return RelativeMotion(v_long, v_lat, heading, t_cpa, d_cpa, known, d_cpa_clearance)


def motion_relation(sample: TrackSample, motion: RelativeMotion, cfg: SemanticsConfig) -> str:
    if not motion.known or motion.heading_deg is None or sample.speed_mps < cfg.cut_in_min_target_speed_mps:
        return UNKNOWN
    angle = abs(motion.heading_deg)
    if angle <= SAME_DIRECTION_DEG:
        return "SAME_DIRECTION"
    if angle >= OPPOSING_DEG:
        return "OPPOSING"
    if CROSSING_DEG[0] <= angle <= CROSSING_DEG[1]:
        return "CROSSING"
    return UNKNOWN


def appearance_side(bearing_deg: float, cfg: SemanticsConfig) -> str:
    if abs(bearing_deg) <= cfg.track_appeared_front_deg:
        return "FRONT"
    return "LEFT" if bearing_deg < 0 else "RIGHT"


def mark_occlusions(tracks: Sequence[LocalTrack], ego: EgoTrajectory, footprint: Optional[EgoFootprint],
                    cfg: SemanticsConfig) -> None:
    for track in tracks:
        others = [other for other in tracks if other is not track]
        for sample in track.samples:
            present = [near for near in (other.sample_near(sample.t_local) for other in others) if near is not None]
            sample.occluded = bool(present) and occluded_by(sample, ego.at(sample.t_local), present, footprint, cfg)


def _critical_assessments(samples: Sequence[TrackSample], ego: EgoTrajectory, cfg: SemanticsConfig,
                          footprint: Optional[EgoFootprint] = None,
                          leader: Optional[Sequence[bool]] = None) -> List[ConflictAssessment]:
    first = samples[0].t_local if samples else 0.0
    return [assess_conflict(sample, ego.at(sample.t_local), footprint, cfg, sample.t_local - first,
                            None if leader is None else leader[index])
            for index, sample in enumerate(samples)]


def closing_spans(times: Sequence[float], samples: Sequence[TrackSample], cfg: SemanticsConfig) -> List[Span]:
    closing = cfg.closing_speed_threshold_mps
    spans = active_intervals(times, samples, lambda s: s.closing_speed_mps >= closing,
                             lambda s: s.closing_speed_mps < closing / 2.0)
    return _lasting(spans, times)


def contact_partners(contacts: Sequence[Contact], tracks: Sequence[LocalTrack], period: float,
                     cfg: SemanticsConfig, touching_clearance_m: float) -> Dict[str, List[Tuple[float, float]]]:
    closing = {track.track_id: span_values(len(track.samples), closing_spans(
        [round(sample.t_local, 4) for sample in track.samples], track.samples, cfg)) for track in tracks}
    partners: Dict[str, List[Tuple[float, float]]] = {}
    for contact in contacts:
        found = []
        for track in tracks:
            near = [index for index, sample in enumerate(track.samples)
                    if contact.first - period - 1e-6 <= sample.t_local <= contact.first + 1e-6]
            before = [index for index in near if track.samples[index].t_local < contact.first - 1e-6]
            if (before and closing[track.track_id][before[-1]] is True
                    and min(track.samples[index].clearance_m for index in near) <= touching_clearance_m + 1e-9):
                found.append(track.track_id)
        if len(found) == 1:
            partners.setdefault(found[0], []).append((contact.first, contact.last))
    return partners


def contact_holds(contacts: Sequence[Contact], tracks: Sequence[LocalTrack], period: float,
                  touching_clearance_m: float,
                  partners: Dict[str, List[Tuple[float, float]]]) -> Dict[str, List[Tuple[float, float]]]:
    holds: Dict[str, List[Tuple[float, float]]] = {}
    for contact in contacts:
        for track in tracks:
            if (contact.first, contact.last) in partners.get(track.track_id, ()):
                continue
            if any(contact.first - period - 1e-6 <= sample.t_local <= contact.last + 1e-6
                   and sample.clearance_m <= touching_clearance_m + 1e-9 for sample in track.samples):
                holds.setdefault(track.track_id, []).append((contact.first, contact.last))
    return holds


def critical_intervals(times: Sequence[float], assessments: Sequence[ConflictAssessment],
                       release_deceleration_mps2: float, release_debounce_s: float = CRITICAL_RELEASE_DEBOUNCE_S,
                       contacts: Sequence[Tuple[float, float]] = (),
                       holds: Sequence[Tuple[float, float]] = (),
                       touching: Optional[Sequence[bool]] = None) -> Tuple[List[Span], List[Span]]:
    spans: List[Span] = []
    collided: List[Span] = []
    start: Optional[int] = None
    release: Optional[int] = None
    forward_engaged = False
    pending = sorted([(float(first), float(last), True) for first, last in contacts]
                     + [(float(first), float(last), False) for first, last in holds])
    held, held_forward = False, False
    contact_until = -math.inf
    resolved: Optional[int] = None
    for index, assessment in enumerate(assessments):
        while pending and pending[0][0] <= times[index] + 1e-6:
            _, last, partner = pending.pop(0)
            if not partner and start is not None:
                continue
            if start is not None:
                spans.append((start, index))
                collided.append((start, index))
                held_forward, start, release = forward_engaged, None, None
            elif not held:
                held_forward = False
            held, resolved, contact_until = True, None, max(contact_until, last)
        if held:
            if (times[index] <= contact_until + 1e-6 or (touching is not None and touching[index])
                    or not assessment.released(release_deceleration_mps2, held_forward)):
                resolved = None
            else:
                resolved = index if resolved is None else resolved
                if times[index] - times[resolved] >= release_debounce_s - 1e-6:
                    held = False
            continue
        if assessment.critical:
            if start is None:
                start, forward_engaged = index, False
            forward_engaged = forward_engaged or UNSAFE_FORWARD_GAP in (assessment.critical_reason or "")
            release = None
            continue
        if start is None:
            continue
        if not assessment.released(release_deceleration_mps2, forward_engaged):
            release = None
            continue
        if release is None:
            release = index
        if times[index] - times[release] >= release_debounce_s - 1e-6:
            spans.append((start, release))
            start = release = None
    if start is not None:
        spans.append((start, None))
    return spans, collided


def cut_in_spans(times: Sequence[float], samples: Sequence[TrackSample], motions: Sequence[RelativeMotion],
                 cfg: SemanticsConfig, body_gaps: Sequence[float],
                 target_lateral_speeds: Optional[Sequence[float]] = None,
                 body_sides: Optional[Sequence[int]] = None,
                 body_ahead: Optional[Sequence[bool]] = None,
                 lane_toward_speeds: Optional[Sequence[Optional[float]]] = None,
                 impact_from: Optional[float] = None) -> Tuple[List[Span], List[Span]]:
    left: List[Span] = []
    right: List[Span] = []
    run: Optional[Tuple[int, int, float]] = None
    ahead_since: Optional[int] = None
    active: Optional[Tuple[int, int]] = None
    settle: Optional[int] = None
    for index, (sample, motion) in enumerate(zip(samples, motions)):
        lateral_speed = (motion.lateral_speed_mps if target_lateral_speeds is None
                         else target_lateral_speeds[index])
        if not motion.known or sample.occluded:
            run, settle = (None if active is None else run), None
            ahead_since = None
            continue
        if active is not None:
            start, side = active
            if -side * lateral_speed < cfg.cut_in_settle_speed_mps:
                settle = index if settle is None else settle
                if times[index] - times[settle] >= cfg.cut_in_settle_s - 1e-6:
                    (left if side < 0 else right).append((start, settle))
                    active, run, settle = None, None, None
            else:
                settle = None
            continue
        if impact_from is not None and times[index] >= impact_from - 1e-6:
            run, ahead_since = None, None
            continue
        side = (-1 if sample.lateral_m < 0 else 1) if body_sides is None else body_sides[index]
        toward = -side * lateral_speed
        parallel = (motion.heading_deg is not None and abs(motion.heading_deg) <= cfg.cut_in_max_heading_deg
                    and sample.speed_mps >= cfg.cut_in_min_target_speed_mps)
        ahead = sample.ahead_m > 0 if body_ahead is None else body_ahead[index]
        lane_toward = None if lane_toward_speeds is None else lane_toward_speeds[index]
        keeps_lane = lane_toward is not None and lane_toward < cfg.cut_in_lateral_speed_mps
        if keeps_lane or not (parallel and toward >= cfg.cut_in_lateral_speed_mps
                              and (target_lateral_speeds is None or toward > sample.vel_std_mps)):
            run, ahead_since = None, None
            continue
        if run is None or run[1] != side:
            run, ahead_since = (index, side, body_gaps[index]), None
        if not ahead:
            ahead_since = None
            continue
        ahead_since = index if ahead_since is None else ahead_since
        gap = body_gaps[index]
        due = gap / toward <= cfg.cut_in_horizon_s
        if (run[2] >= cfg.cut_in_outside_margin_m
                and run[2] - gap >= cfg.cut_in_min_displacement_m
                and times[index] - times[ahead_since] >= cfg.cut_in_persistence_s - 1e-6 and due
                and body_gaps[index] <= cfg.cut_in_preentry_margin_m + 1e-9):
            active, settle = (run[0], run[1]), None
    if active is not None:
        (left if active[1] < 0 else right).append((active[0], None))
    return left, right


def path_occupancy(times: Sequence[float], margins: Sequence[Optional[float]], sigmas: Sequence[float],
                   cfg: SemanticsConfig) -> Tuple[List[Span], Optional[bool]]:
    k, need = cfg.path_occupancy_quantile, max(int(cfg.path_min_definite_samples), 1)
    definite: List[Optional[bool]] = []
    for margin, sigma in zip(margins, sigmas):
        if margin is None:
            definite.append(None)
        elif margin >= k * sigma:
            definite.append(True)
        elif margin <= -k * sigma:
            definite.append(False)
        else:
            definite.append(None)
    state: Optional[bool] = None
    initial: Optional[bool] = None
    last_definite = -1
    spans: List[Span] = []
    start: Optional[int] = None
    run_state, run_length = None, 0
    for index, value in enumerate(definite):
        if value is None:
            continue
        if value == run_state:
            run_length += 1
        else:
            run_state, run_length = value, 1
        if state is None:
            if run_length >= need:
                state = initial = value
                last_definite = index
                if value:
                    start = 0
            continue
        if value == state:
            last_definite = index
            continue
        if run_length < need:
            continue
        first = index - run_length + 1
        crossing = next((j for j in range(last_definite + 1, first + 1)
                         if margins[j] is not None and (margins[j] > 0.0) == value), first)
        if value:
            start = crossing
        else:
            spans.append((start if start is not None else 0, crossing))
            start = None
        state, last_definite = value, index
    if state and start is not None:
        spans.append((start, None))
    return spans, initial


def _path_cause(index: int, times: Sequence[float], supports: Sequence[np.ndarray], ego: EgoTrajectory,
                road: Optional["RoadFrame"], corridor: float, since: Optional[int] = None) -> str:
    lo = max(0, next((j for j in range(index, -1, -1) if times[index] - times[j] >= 0.5), 0))
    if since is not None:
        lo = min(lo, since)
    own0, own1 = ego.at(times[lo]), ego.at(times[index])
    body0, body1 = supports[lo], supports[index]
    state = road.path_at(ego, times[lo]) if road is not None else None
    if state is not None:
        frame = state[0]

        def lateral(points: np.ndarray) -> np.ndarray:
            return frame.project(np.array([road.to_world(*point) for point in points]))[:, 1]
    else:
        c, s = math.cos(own0.heading), math.sin(own0.heading)

        def lateral(points: np.ndarray) -> np.ndarray:
            return -s * (points[:, 0] - own0.x) + c * (points[:, 1] - own0.y)
    y0, y1 = lateral(body0), lateral(body1)
    c0, c1 = (float(v) for v in lateral(np.array([[own0.x, own0.y], [own1.x, own1.y]])))

    def overlaps(y: np.ndarray, centre_line: float) -> bool:
        return min(float(np.max(y)), centre_line + corridor) - max(float(np.min(y)), centre_line - corridor) > 0.0

    now = overlaps(y1, c1)
    if now == overlaps(y0, c0):
        return "LONGITUDINAL"
    target = overlaps(y0, c1) != now
    recorder = overlaps(y1, c0) != now
    if target and not recorder:
        return "TARGET_LATERAL"
    if recorder and not target:
        return "RECORDER_LATERAL"
    return "MUTUAL_LATERAL"


def _on_body_returns(returns: Optional[Tuple[np.ndarray, np.ndarray]], t_local: float, ego: EgoTrajectory,
                     body: np.ndarray, face_std: float) -> Optional[np.ndarray]:
    if returns is None or len(returns[0]) < 2:
        return None
    own = ego.at(t_local)
    c, s = math.cos(own.heading), math.sin(own.heading)
    rel = returns[0] - np.array([own.x, own.y])
    vehicle = np.column_stack([rel @ np.array([c, s]), rel @ np.array([-s, c])])
    centre = np.mean(body, axis=0)
    along = 0.5 * (body[0] + body[1]) - centre
    across = 0.5 * (body[0] - body[1])
    half_length, half_width = float(np.hypot(*along)), float(np.hypot(*across))
    if half_length < 1e-6 or half_width < 1e-6:
        return None
    a = (vehicle - centre) @ (along / half_length)
    b = (vehicle - centre) @ (across / half_width)
    on_body = (np.abs(b) <= half_width + 2.0 * face_std) & (np.abs(a) <= 2.0 * half_length)
    return returns[0][on_body] if int(on_body.sum()) >= 2 else None


def _returns_bounds(points: Optional[np.ndarray], t_local: float, ego: EgoTrajectory, road: Optional["RoadFrame"],
                    front: float, corridor: float) -> Optional[Tuple[float, float]]:
    if points is None or len(points) < 2:
        return None
    mapped = road.to_path(ego, t_local, points) if road is not None else None
    if mapped is None:
        own = ego.at(t_local)
        c, s = math.cos(own.heading), math.sin(own.heading)
        rel = points - np.array([own.x, own.y])
        mapped = np.column_stack([rel @ np.array([c, s]), rel @ np.array([-s, c])])
    reach = mapped[:, 0] - front
    margin = np.minimum(reach, corridor - np.abs(mapped[:, 1]))
    return float(np.sort(margin)[-2]), float(np.sort(reach)[-2])


def _entered(span: Span, entries: Sequence[int], needed: Optional[Callable[[int, int], bool]] = None) -> bool:
    start, end = span
    return any(start <= entry and (end is None or entry <= end) and (needed is None or needed(start, entry))
               for entry in entries)


def _manoeuvre_needed(start: int, entry: int, times: Sequence[float], supports: Sequence[np.ndarray],
                      ego: EgoTrajectory, road: Optional["RoadFrame"], corridor: float) -> bool:
    own1 = ego.at(times[entry])
    body = supports[start]
    mapped = road.to_path(ego, times[entry], body) if road is not None else None
    if mapped is not None:
        lateral = mapped[:, 1]
    else:
        c1, s1 = math.cos(own1.heading), math.sin(own1.heading)
        lateral = -s1 * (body[:, 0] - own1.x) + c1 * (body[:, 1] - own1.y)
    return not min(float(np.max(lateral)), corridor) - max(float(np.min(lateral)), -corridor) > 0.0


def _stationary_ego() -> EgoTrajectory:
    return EgoTrajectory([EgoState(t_local=0.0, x=0.0, y=0.0, heading=0.0, vx=0.0, vy=0.0)])


def track_events(owner: str, track: LocalTrack, recording_end: float, cfg: SemanticsConfig,
                 ego: Optional[EgoTrajectory] = None, world: Optional[PerceivedWorld] = None,
                 footprint: Optional[EgoFootprint] = None,
                 contacts: Sequence[Tuple[float, float]] = (), body_based: bool = True,
                 holds: Sequence[Tuple[float, float]] = (),
                 touching_clearance_m: float = 1.0, road: Optional["RoadFrame"] = None,
                 impact_from: Optional[float] = None, recorder_contacts: Sequence[float] = (),
                 approach_window_s: float = 1.0) -> List[SemanticEvent]:
    ego = ego or _stationary_ego()
    samples = track.samples
    times = [round(sample.t_local, 4) for sample in samples]
    motions = [relative_motion(sample, ego.at(sample.t_local), cfg, footprint) for sample in samples]
    subject = track.track_id
    events = [SemanticEvent(type="TRACK_APPEARED_" + appearance_side(samples[0].bearing_deg, cfg), kind=PERCEPTION,
                            actor_id=owner, subject_id=subject, t_local=times[0], source="radar")]

    corridor, hysteresis = cfg.path_half_width_m, cfg.path_hysteresis_m
    from .conflict import target_box, box_corners, body_in_corridor, lateral_body_gap
    front = footprint.x_max if footprint is not None else 0.0
    bodies = [box_corners(*target_box(s, ego.at(s.t_local), footprint, cfg)[:3]) for s in samples]
    path_bodies: List[Optional[np.ndarray]] = [None] * len(samples)
    path_points: List[Optional[np.ndarray]] = [None] * len(samples)
    on_body = [_on_body_returns(track.returns[i], sample.t_local, ego, bodies[i], cfg.path_edge_std_m)
               if body_based and sample.measured and i < len(track.returns) else None
               for i, sample in enumerate(samples)]
    supports = []
    for sample, corners, points in zip(samples, bodies, on_body):
        own = ego.at(sample.t_local)
        c, s = math.cos(own.heading), math.sin(own.heading)
        local_corners = corners @ np.array([[c, s], [-s, c]]) + np.array([own.x, own.y])
        supports.append(local_corners if points is None else np.vstack([local_corners, points]))
    proven = [_returns_bounds(points, sample.t_local, ego, road, front, corridor)
              for sample, points in zip(samples, on_body)]
    if road is not None and body_based:
        for index, (sample, corners) in enumerate(zip(samples, bodies)):
            own = ego.at(sample.t_local)
            c, s = math.cos(own.heading), math.sin(own.heading)
            local_xy = np.vstack([corners @ np.array([[c, s], [-s, c]]) + np.array([own.x, own.y]),
                                  [[sample.x_m, sample.y_m]]])
            mapped = road.to_path(ego, sample.t_local, local_xy)
            if mapped is not None:
                path_bodies[index], path_points[index] = mapped[:-1, :2], mapped[-1]

    def in_path(i: int, front_edge: float, half: float) -> bool:
        body = path_bodies[i] if path_bodies[i] is not None else bodies[i]
        return body_in_corridor(body, front_edge, half)

    if body_based:
        margins: List[Optional[float]] = []
        sigmas: List[float] = []
        evidence: List[Optional[str]] = []
        for i, sample in enumerate(samples):
            body = path_bodies[i] if path_bodies[i] is not None else bodies[i]
            ahead_margin = float(np.max(body[:, 0])) - front
            overlap = min(float(np.max(body[:, 1])), corridor) - max(float(np.min(body[:, 1])), -corridor)
            heading_std = min(sample.vel_std_mps / max(sample.speed_mps, 1e-6), 0.5)
            margin = min(ahead_margin, overlap) if sample.measured else None
            sigma = math.sqrt(sample.pos_std_m ** 2 + cfg.path_edge_std_m ** 2
                              + (0.5 * cfg.target_length_m * heading_std) ** 2)
            source = None if margin is None else "box"
            if margin is not None and proven[i] is not None and proven[i][0] > margin:
                margin, sigma, source = proven[i][0], cfg.path_edge_std_m, "returns"
            margins.append(margin)
            sigmas.append(sigma)
            evidence.append(source)
        path, initially_in = ([], None) if track.identity_ambiguous else path_occupancy(times, margins, sigmas, cfg)
    else:
        path = [] if track.identity_ambiguous else active_intervals(times, samples,
            lambda s: s.ahead_m > 0 and abs(s.lateral_m) <= corridor,
            lambda s: s.ahead_m < -hysteresis or abs(s.lateral_m) > corridor + hysteresis)
        initially_in = bool(path and path[0][0] == 0)
    events[0].attributes['initial_in_ego_path'] = bool(initially_in)
    path_events = state_events(owner, subject, "EGO_PATH_ENTRY", "EGO_PATH_EXIT", PERCEPTION, "radar",
                               times, path, announce_initial=False)
    if body_based:
        k = cfg.path_occupancy_quantile
        for event in path_events:
            index = times.index(round(event.t_local, 4))
            entering = event.type == "EGO_PATH_ENTRY"
            decided = next((j for j in range(index, len(samples)) if margins[j] is not None
                            and (margins[j] >= k * sigmas[j] if entering else margins[j] <= -k * sigmas[j])), None)
            if decided is not None:
                event.attributes["occupancy_evidence"] = evidence[decided]
                event.attributes["occupancy_margin_m"] = round(float(margins[decided]), 3)
                event.attributes["occupancy_sigma_m"] = round(float(sigmas[decided]), 3)
    events += path_events

    closing = closing_spans(times, samples, cfg)
    events += state_events(owner, subject, "CLOSING_START", "CLOSING_END", PERCEPTION, "radar", times, closing)

    first_known = next((index for index, motion in enumerate(motions) if motion.known), len(motions))
    anchor = ego.at(times[0])
    c0, s0 = math.cos(anchor.heading), math.sin(anchor.heading)
    stable_bodies, target_lateral, stable_motions, ahead = [], [], [], []
    for index, (sample, motion, corners) in enumerate(zip(samples, motions, bodies)):
        own = ego.at(sample.t_local)
        if path_bodies[index] is not None:
            stable = path_bodies[index]
            heading = float(path_points[index][2])
            wvx, wvy = road.vector_to_world(sample.vx_mps, sample.vy_mps)
            target_lateral.append(-math.sin(heading) * wvx + math.cos(heading) * wvy)
            angle = ((math.degrees(math.atan2(wvy, wvx) - heading) + 180) % 360 - 180
                     if sample.speed_mps >= 1.0 else None)
            ahead.append(float(np.max(stable[:, 0])) > front or (proven[index] is not None and proven[index][1] > 0.0))
        else:
            c, s = math.cos(own.heading), math.sin(own.heading)
            world_corners = corners @ np.array([[c, s], [-s, c]]) + np.array([own.x, own.y])
            stable = (world_corners - np.array([anchor.x, anchor.y])) @ np.array([[c0, -s0], [s0, c0]])
            target_lateral.append(-s0 * sample.vx_mps + c0 * sample.vy_mps)
            angle = ((math.degrees(math.atan2(sample.vy_mps, sample.vx_mps) - anchor.heading) + 180) % 360 - 180
                     if sample.speed_mps >= 1.0 else None)
            ego_forward = c0 * (own.x - anchor.x) + s0 * (own.y - anchor.y) + front
            ahead.append(float(np.max(stable[:, 0])) > ego_forward
                         or (proven[index] is not None and proven[index][1] > 0.0))
        stable_bodies.append(stable)
        stable_motions.append(RelativeMotion(motion.longitudinal_speed_mps, motion.lateral_speed_mps,
                                             angle, motion.t_cpa_s, motion.d_cpa_m, motion.known,
                                             motion.d_cpa_clearance_m))
    body_gaps = [lateral_body_gap(float(np.min(b[:, 1])), float(np.max(b[:, 1])), corridor)
                 for b in stable_bodies]
    sides = [-1 if float(np.mean(b[:, 1])) < 0 else 1 for b in stable_bodies]
    if not body_based:
        points = [(s.x_m - anchor.x) * -s0 + (s.y_m - anchor.y) * c0 for s in samples]
        body_gaps = [max(abs(y) - corridor, 0.0) for y in points]
        sides = [-1 if y < 0 else 1 for y in points]
        ahead = [(s.x_m-own.x)*c0+(s.y_m-own.y)*s0 > front
                 for s,own in ((s,ego.at(s.t_local)) for s in samples)]
    lane_toward = None
    if road is not None:
        lane_toward = []
        for sample in samples:
            own = ego.at(sample.t_local)
            lane_toward.append(road.lane_toward_speed(sample.x_m, sample.y_m, sample.vx_mps, sample.vy_mps,
                                                      own.x, own.y))
    from_left, from_right = cut_in_spans(times, samples, stable_motions, cfg, body_gaps,
                                        target_lateral, sides, ahead, lane_toward, impact_from)
    entries = [start for start, _ in path if start > 0]

    def needed(span_start: int, entry: int) -> bool:
        return _manoeuvre_needed(span_start, entry, times, supports, ego, road, corridor)

    from_left = [span for span in from_left if _entered(span, entries, needed)]
    from_right = [span for span in from_right if _entered(span, entries, needed)]
    for event in path_events:
        index = times.index(round(event.t_local, 4))
        since = next((start for start, end in from_left + from_right
                      if event.type == "EGO_PATH_ENTRY" and start <= index and (end is None or index <= end)), None)
        event.attributes["cause"] = _path_cause(index, times, supports, ego, road, corridor, since)
    events += state_events(owner, subject, "CUT_IN_FROM_LEFT_START", "CUT_IN_FROM_LEFT_END",
                           PERCEPTION, "radar", times, from_left)
    events += state_events(owner, subject, "CUT_IN_FROM_RIGHT_START", "CUT_IN_FROM_RIGHT_END",
                            PERCEPTION, "radar", times, from_right)

    leader_spans = path + from_left + from_right
    leader = [any(a <= i and (b is None or i <= b) for a, b in leader_spans) for i in range(len(samples))]
    track.leader_spans = [(times[a], None if b is None else times[b]) for a, b in leader_spans]
    track.lane_curvature = {}
    if road is not None:
        for sample in samples:
            curvature = road.lane_curvature(sample.x_m, sample.y_m, sample.vx_mps, sample.vy_mps)
            if curvature is not None:
                track.lane_curvature[round(sample.t_local, 4)] = curvature
    assessments = _critical_assessments([track.conflict_sample(sample) for sample in samples], ego, cfg, footprint,
                                        leader)
    track.lane_held = {}
    if road is not None:
        closing_now = span_values(len(samples), closing)
        struck = [last for first, last in contacts
                  if any(closing_now[i] is True for i, s in enumerate(samples)
                         if first - STRIKE_CLOSING_WINDOW_S - 1e-6 <= s.t_local < first - 1e-6)]
        if closing_now and closing_now[-1] is True:
            struck += [first for first in recorder_contacts if 0.0 <= first - times[-1] <= approach_window_s + 1e-6]
        for index, assessment in enumerate(assessments):
            if PREDICTED_OVERLAP not in (assessment.critical_reason or ""):
                continue
            if (any(end is None or end >= index for _, end in path)
                    or any(last >= times[index] - 1e-6 for last in struck)):
                continue
            sample = samples[index]
            held = road.along_lane(sample.x_m, sample.y_m, sample.vx_mps, sample.vy_mps)
            if held is None:
                continue
            track.lane_held[times[index]] = held
            assessments[index] = assess_conflict(track.conflict_sample(sample), ego.at(sample.t_local), footprint,
                                                 cfg, sample.t_local - samples[0].t_local, leader[index])
    release = cfg.critical_release_ratio * cfg.critical_deceleration_mps2
    touching = [sample.clearance_m <= touching_clearance_m + 1e-9 for sample in samples]
    spans, collided = critical_intervals(times, assessments, release, CRITICAL_RELEASE_DEBOUNCE_S, contacts, holds,
                                         touching)
    critical_spans = _lasting(spans, times, keep=collided)
    first_known_critical = next((index for index, a in enumerate(assessments) if a.known), len(assessments))
    events += state_events(owner, subject, "CRITICAL_TTC_START", "CRITICAL_TTC_END", PERCEPTION, "radar",
                           times, critical_spans)
    for event in events:
        if event.type in ('EGO_PATH_ENTRY','EGO_PATH_EXIT') or event.type.startswith('CUT_IN_FROM_'):
            i = min(range(len(times)), key=lambda k: abs(times[k]-event.t_local))
            event.attributes['estimated_body_corners_vehicle_m'] = [[round(float(v),4) for v in row] for row in bodies[i]]
            event.attributes['geometry'] = 'estimated_body' if body_based else 'point_ablation'
            if event.type.startswith('CUT_IN_FROM_'):
                event.attributes['path_frame_heading_rad'] = round(anchor.heading,6)+0.0
                event.attributes['target_lateral_speed_mps'] = round(target_lateral[i],4)+0.0

    lost_at = times[-1] if times[-1] < recording_end - 1e-3 else None
    if lost_at is not None:
        events.append(SemanticEvent(type="TRACK_LOST", kind=PERCEPTION, actor_id=owner, subject_id=subject,
                                    t_local=lost_at, source="radar"))
    if world is not None:
        count = len(times)
        world.add_track(subject, times, {
            "CLOSING": span_values(count, closing),
            "CRITICAL_TTC": span_values(count, critical_spans, first_known_critical),
            "IN_EGO_PATH": span_values(count, path, count if track.identity_ambiguous else 0),
            "CUT_IN_FROM_LEFT": span_values(count, from_left, first_known),
            "CUT_IN_FROM_RIGHT": span_values(count, from_right, first_known),
        }, lost_at)
    return events


def number_events(owner: str, events: List[SemanticEvent]) -> List[SemanticEvent]:
    ordered = display_order(events, lambda event: event.t_local, lambda event: event.type,
                            lambda event: event.actor_id, lambda event: event.subject_id)
    for index, event in enumerate(ordered, 1):
        event.event_id = "{0}:e{1:02d}".format(owner, index)
    return ordered



def _where(sample: TrackSample) -> Dict[str, Any]:
    return {"range_m": round(sample.range_m, 2), "radar": sample.radar, "clearance_m": round(sample.clearance_m, 2),
            "bearing_deg": round(sample.bearing_deg, 1),
            "lateral_m": round(sample.lateral_m, 2), "closing_speed_mps": round(sample.closing_speed_mps, 2)}


def ego_motion_fact(owner: str, ego: EgoTrajectory, t_local: float) -> SemanticEvent:
    state = ego.at(t_local)
    before = ego.at(max(t_local - 0.1, ego.start))
    after = ego.at(min(t_local + 0.1, ego.end))
    dt = max(after.t_local - before.t_local, 1e-6)
    return SemanticEvent(type="EGO_MOTION", kind=FACT, actor_id=owner, t_local=t_local, source="ego",
                         attributes={"speed_mps": round(state.speed, 2),
                                     "acceleration_mps2": round((after.speed - before.speed) / dt, 2),
                                     "yaw_rate_dps": round(math.degrees(after.heading - before.heading) / dt, 1),
                                     "x_m": round(state.x, 2), "y_m": round(state.y, 2),
                                     "heading_deg": round(math.degrees(state.heading), 1)})


def ego_control_fact(owner: str, record: Mapping[str, Any], t_local: float) -> SemanticEvent:
    return SemanticEvent(type="EGO_CONTROL", kind=FACT, actor_id=owner, t_local=t_local, source="controls",
                         attributes={"throttle": round(float(record["throttle"]), 3),
                                     "brake": round(float(record["brake"]), 3),
                                     "steer": round(float(record["steer"]), 3)})


def _rounded(value: Optional[float], digits: int) -> Optional[float]:
    return None if value is None else round(value, digits)


def track_state_fact(owner: str, track_id: str, sample: TrackSample, t_local: float,
                     motion: Optional[RelativeMotion] = None, cfg: Optional[SemanticsConfig] = None,
                     conflict: Optional[ConflictAssessment] = None) -> SemanticEvent:
    attributes = dict(_where(sample), longitudinal_m=round(sample.longitudinal_m, 2),
                      ahead_of_front_m=round(sample.ahead_m, 2), surface_offset_m=round(sample.surface_offset_m, 2),
                      closing_ttc_s=_rounded(sample.closing_ttc_s, 2),
                      speed_mps=round(sample.speed_mps, 2), acceleration_mps2=round(sample.acceleration_mps2, 2),
                      x_m=round(sample.x_m, 2), y_m=round(sample.y_m, 2),
                      vx_mps=round(sample.vx_mps, 2), vy_mps=round(sample.vy_mps, 2),
                      pos_std_m=round(sample.pos_std_m, 2), vel_std_mps=round(sample.vel_std_mps, 2),
                      measured=sample.measured)
    if motion is not None:
        attributes.update(
            relative_longitudinal_speed_mps=round(motion.longitudinal_speed_mps, 2),
            relative_lateral_speed_mps=round(motion.lateral_speed_mps, 2),
            relative_motion_angle_deg=_rounded(motion.heading_deg, 1),
            motion_relation=motion_relation(sample, motion, cfg or SemanticsConfig()),
            t_cpa_s=_rounded(motion.t_cpa_s, 2), d_cpa_m=_rounded(motion.d_cpa_m, 2),
            d_cpa_clearance_m=_rounded(motion.d_cpa_clearance_m, 2))
    if conflict is not None:
        required = conflict.required_deceleration_mps2
        attributes.update(
            ego_speed_mps=round(conflict.ego_speed_mps, 2), encounter=conflict.encounter,
            collision_course=conflict.collision_course, ttc_s=conflict.ttc_s,
            predicted_overlap_s=None if conflict.overlap_s is None else list(conflict.overlap_s),
            target_acceleration_used_mps2=round(conflict.target_acceleration_mps2, 2),
            required_deceleration_mps2=None if required is None or math.isinf(required) else round(required, 2),
            avoidance_by=conflict.avoidance_by,
            braking_margin_mps2=_rounded(conflict.braking_margin_mps2, 2),
            unavoidable_by_braking=required is not None and math.isinf(required),
            estimate_known=conflict.known, critical=conflict.critical, critical_reason=conflict.critical_reason,
            line_of_sight_occluded=conflict.occluded, inside_safety_envelope=conflict.inside_envelope)
        forward = conflict.forward
        if forward is not None:
            attributes.update(
                forward_region=forward.region, forward_leader=forward.leader,
                longitudinal_clearance_m=round(forward.longitudinal_clearance_m, 2),
                lateral_body_gap_m=round(forward.lateral_body_gap_m, 2),
                time_headway_s=_rounded(forward.time_headway_s, 2),
                minimum_time_gap_s=round(forward.minimum_time_gap_s, 3),
                time_gap_distance_m=round(forward.time_gap_distance_m, 2),
                required_safe_distance_m=round(forward.required_distance_m, 2),
                safe_distance_margin_m=round(forward.margin_m, 2))
    return SemanticEvent(type="TRACK_STATE", kind=FACT, actor_id=owner, subject_id=track_id,
                         t_local=t_local, source="radar", attributes=attributes)


def build_trace(owner: str, ego: EgoTrajectory, controls: Sequence[Mapping[str, Any]],
                tracks: Sequence[LocalTrack], events: Sequence[SemanticEvent],
                clock_origin: float, trace_hz: float, semantics: Optional[SemanticsConfig] = None,
                world: Optional[PerceivedWorld] = None, footprint: Optional[EgoFootprint] = None) -> List[TraceFrame]:
    semantics = semantics or SemanticsConfig()
    step = 1.0 / trace_hz
    first = int(math.ceil(ego.start / step - 1e-6))
    last = int(math.floor(ego.end / step + 1e-6))
    times = [round(index * step, 4) for index in range(first, last + 1)]
    if ego.end - times[-1] > 1e-6:
        times.append(round(ego.end, 4))
    by_frame: Dict[int, List[SemanticEvent]] = {}
    for event in events:
        index = min(bisect.bisect_left(times, event.t_local - 1e-6), len(times) - 1)
        by_frame.setdefault(index, []).append(event)
    control_times = [_local_time(record, clock_origin) for record in controls]
    frames = []
    cursor = -1
    for index, t_local in enumerate(times):
        facts = [ego_motion_fact(owner, ego, t_local)]
        while cursor + 1 < len(controls) and control_times[cursor + 1] <= t_local + 1e-6:
            cursor += 1
        if cursor >= 0:
            facts.append(ego_control_fact(owner, controls[cursor], t_local))
        for track in tracks:
            if track.first_t - 1e-6 <= t_local <= track.last_t + 1e-6:
                sample = track.sample_near(t_local)
                if sample is not None:
                    own = ego.at(sample.t_local)
                    motion = relative_motion(sample, own, semantics, footprint)
                    conflict = assess_conflict(track.conflict_sample(sample), own, footprint, semantics,
                                               sample.t_local - track.first_t, track.leader_at(sample.t_local))
                    facts.append(track_state_fact(owner, track.track_id, sample, t_local, motion, semantics, conflict))
        frames.append(TraceFrame(t_local=t_local, facts=facts, events=by_frame.get(index, []),
                                 perceived_state=None if world is None else world.snapshot(t_local, before=False)))
    return frames



def build_local_graph(owner: str, trace: Sequence[TraceFrame], tracks: Sequence[LocalTrack],
                      recorder: Dict[str, Any]) -> LocalGraph:
    events = sorted((event for frame in trace for event in frame.events), key=lambda event: event.event_id)
    nodes = [GraphNode.from_event(event) for event in events]
    edges = precedes_edges(nodes, lambda node: node.t_local, lambda node: node.node_id)
    appeared = {node.subject_id: node.node_id for node in nodes if node.event_type.startswith("TRACK_APPEARED")}
    for node in nodes:
        origin = appeared.get(node.subject_id) if node.subject_id else None
        if origin is not None and origin != node.node_id:
            edges.append(GraphEdge(origin, node.node_id, SAME_TRACK))
    return LocalGraph(owner=owner, nodes=nodes, edges=edges,
                      tracks=[track.summary() for track in tracks], recorder=recorder)


@dataclass
class LocalReconstruction:

    owner: str
    clock_origin: float
    ego: EgoTrajectory
    tracks: List[LocalTrack]
    trace: List[TraceFrame]
    graph: LocalGraph
    footprint: Optional[EgoFootprint] = None


def vehicle_metadata(vehicle_dir: Path) -> Dict[str, Any]:
    path = Path(vehicle_dir) / "metadata.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _sign_track_gap(vehicle_dir: Path) -> float:
    path = vehicle_dir / "metadata.json"
    if path.exists():
        signs = json.loads(path.read_text(encoding="utf-8")).get("traffic_signs") or {}
        if "max_time_gap_s" in signs:
            return float(signs["max_time_gap_s"])
    return DEFAULT_SIGN_TRACK_GAP_S


def reconstruct_vehicle(vehicle_dir: Path, cfg: ReconstructionConfig, clock_origin: Optional[float] = None,
                        context: Optional[Mapping[str, Any]] = None,
                        ego_records: Optional[List[Dict[str, Any]]] = None) -> LocalReconstruction:
    vehicle_dir = Path(vehicle_dir)
    owner = vehicle_dir.name
    context = dict(context or {})
    if ego_records is None:
        ego_records = read_jsonl(vehicle_dir / "ego.jsonl")
    if not ego_records:
        raise ValueError("no ego.jsonl records in " + str(vehicle_dir))
    controls = read_jsonl(vehicle_dir / "controls.jsonl")
    lights = read_jsonl(vehicle_dir / "lights.jsonl") if (vehicle_dir / "lights.jsonl").exists() else None
    collisions = read_jsonl(vehicle_dir / "collisions.jsonl")
    signs = read_jsonl(vehicle_dir / "traffic_signs.jsonl")
    if clock_origin is None:
        clock_origin = float(ego_records[0]["timestamp"])
    ego = ego_trajectory(ego_records, clock_origin)
    road = RoadFrame.from_ego_records(ego_records, map_name=context.get("map"))

    tracks: List[LocalTrack] = []
    footprint_record = vehicle_metadata(vehicle_dir).get("ego_footprint")
    footprint = EgoFootprint.from_metadata(footprint_record)
    streams: List[RadarStream] = []
    radar_stats: Dict[str, Any] = {}
    if (vehicle_dir / "radar").exists():
        streams = [RadarStream(RadarMount.from_metadata(observations.metadata), observations)
                   for observations in load_radar_observations(vehicle_dir)]
        impacts = [(float(c["timestamp"]) - clock_origin, float(c.get("impulse", 0.0))) for c in collisions]
        tracks = build_local_tracks(streams, ego, clock_origin, cfg.tracking, footprint, radar_stats, impacts,
                                    lane_headings=None if road is None else road.lane_headings)

    semantics = cfg.semantics
    mark_occlusions(tracks, ego, footprint, semantics)
    world = PerceivedWorld()
    events: List[SemanticEvent] = []
    events += control_events(owner, controls, clock_origin, semantics, world)
    events += indicator_events(owner, lights, clock_origin, ego.start, world)
    events += motion_events(owner, ego, semantics, context.get("speed_limit_kmh"), world)
    events += turn_events(owner, ego, semantics, world)
    contacts = collision_contacts(collisions, clock_origin, cfg.collision, ego)
    events += contact_events(owner, contacts)
    events += sign_events(owner, signs, clock_origin, ego.end, _sign_track_gap(vehicle_dir), ego, world)
    partners = contact_partners(contacts, tracks, sample_period(ego), semantics, cfg.fusion.touching_clearance_m)
    holds = contact_holds(contacts, tracks, sample_period(ego), cfg.fusion.touching_clearance_m, partners)
    named = {tuple(span) for spans in partners.values() for span in spans}
    holders: Dict[Tuple[float, float], List[str]] = {}
    for track_id, spans in holds.items():
        for span in spans:
            if tuple(span) not in named:
                holders.setdefault(tuple(span), []).append(track_id)
    for span, ids in holders.items():
        if len(ids) == 1:
            partners[ids[0]] = list(partners.get(ids[0], ())) + [span]
            holds[ids[0]] = [h for h in holds[ids[0]] if tuple(h) != span]
    for track in tracks:
        events += track_events(owner, track, ego.end, semantics, ego, world, footprint,
                               partners.get(track.track_id, ()), holds=holds.get(track.track_id, ()),
                               touching_clearance_m=cfg.fusion.touching_clearance_m, road=road,
                               impact_from=min((c.first for c in contacts), default=None),
                               recorder_contacts=[c.first for c in contacts],
                               approach_window_s=cfg.fusion.approach_window_s)
    events = number_events(owner, events)

    trace = build_trace(owner, ego, controls, tracks, events, clock_origin, cfg.trace_hz, semantics, world,
                        footprint)
    frame_times = [frame.t_local for frame in trace]
    for event in events:
        state = world.snapshot(event.t_local, before=True)
        earlier = bisect.bisect_left(frame_times, event.t_local - 1e-6) - 1
        state["facts_t_local"] = frame_times[earlier] if earlier >= 0 else None
        event.perceived_state_before = state
    recorder = {
        "owner": owner,
        "clock": {"origin_source_timestamp": clock_origin,
                  "definition": "t_local = source timestamp - origin (by default this recorder's first ego sample)"},
        "frame": {"definition": "origin = first ego position; x = first heading; "
                                "y = to the right of the first heading (CARLA convention)"},
        "incident_context": context or None,
        "road_map": None if road is None else {"name": road.road.name, "source": road.source},
        "start_t_local": round(ego.start, 4),
        "end_t_local": round(ego.end, 4),
        "trace_hz": cfg.trace_hz,
        "trace_frames": len(trace),
        "inputs": sorted(name for name in ("ego.jsonl", "controls.jsonl", "lights.jsonl", "collisions.jsonl",
                                           "traffic_signs.jsonl", "radar")
                         if (vehicle_dir / name).exists()),
        "radar": None if not streams else {
            "radars": [{"sensor_id": stream.sensor_id,
                        "mount": {"x": round(stream.mount.x, 4), "y": round(stream.mount.y, 4),
                                  "z": round(stream.mount.z, 4), "yaw_deg": round(math.degrees(stream.mount.yaw), 3),
                                  "pitch_deg": round(math.degrees(stream.mount.pitch), 3)}} for stream in streams],
            "ego_footprint": footprint_record,
            "geometry": ("every return placed from its own radar's mount; its Doppler speed corrected by that "
                         "radar's own displacement; clearance = distance from the recorder's footprint to the "
                         "return (a track: to its near surface)") if footprint is not None
            else "own footprint unknown: clearance = distance from the vehicle origin",
            "own_body_returns_dropped": radar_stats.get("own_body_returns_dropped", 0)},
    }
    graph = build_local_graph(owner, trace, tracks, recorder)
    return LocalReconstruction(owner=owner, clock_origin=clock_origin, ego=ego,
                               tracks=tracks, trace=trace, graph=graph, footprint=footprint)
