"""Automatic visual-QA checks of a reconstructed run (reconstruction only, no ground truth).

Each check looks at what the replay shows (``ReplayRun``: the recorders' poses, their tracks and the
anonymous road users as drawn, the reconstructed events and collisions) and flags what a reviewer should
look at: implausible track or road-user motion, boxes that jump or spin, two drawn bodies in one place (two
road users, or a road user on a recorder's own body), events outside a track's lifetime, a
CRITICAL_TTC episode that ends just before the collision of its own pair or starts just after it, a
collision whose recorders are not in contact, a cut-in or a path entry the drawn geometry does not show.
A flag is a reason to look, not a verdict: the visual audit decides.
"""

from __future__ import annotations

import math
import numpy as np
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .model import DEFAULT_FOOTPRINT, HEADING_FROM_VELOCITY, EntityPath, ReplayRun, TrackPath, rotate
from .topdown import _box, _footprint_world
from ..reconstruction.conflict import body_in_corridor

MAX_SPEED_MPS = 70.0  # no road vehicle of the campaign: a faster track or recorder is an artefact
BOX_JUMP_M = 2.5  # the ghost box moved this much more than the track point in one sample
BOX_SPIN_DEG = 45.0  # heading change between consecutive samples, both from the velocity
DUPLICATE_M = 3.0  # two ghosts' centres closer than this at the same instant
CONTACT_M = 1.0  # recorders of a collision farther apart than this (footprint to footprint)
NEAR_COLLISION_S = 1.0  # a CRITICAL_TTC_END this long before / START this long after a collision of its pair
CUT_IN_WINDOW_S = 0.5  # the cut-in's lateral approach is checked over this window after its start (its onset)
CUT_IN_MIN_APPROACH_M = 0.15
CORRIDOR_M = 1.5 + 0.5  # path corridor + hysteresis (semantics.path_half_width_m, path_hysteresis_m)
SAMPLE_STEP_S = 0.1


@dataclass
class Flag:
    check: str
    time: float  # replay time
    display_time: float  # t_global (or source time)
    subject: str
    detail: str


def _polygon_distance(p: Sequence[Tuple[float, float]], q: Sequence[Tuple[float, float]]) -> float:
    """Minimum distance between two convex polygons (0 when they overlap)."""
    def inside(poly, point):
        signs = []
        for i in range(len(poly)):
            (ax, ay), (bx, by) = poly[i], poly[(i + 1) % len(poly)]
            signs.append((bx - ax) * (point[1] - ay) - (by - ay) * (point[0] - ax))
        return all(s >= -1e-9 for s in signs) or all(s <= 1e-9 for s in signs)

    def segment(point, a, b):
        abx, aby = b[0] - a[0], b[1] - a[1]
        f = max(0.0, min(1.0, ((point[0] - a[0]) * abx + (point[1] - a[1]) * aby) / max(abx * abx + aby * aby, 1e-12)))
        return math.hypot(point[0] - a[0] - f * abx, point[1] - a[1] - f * aby)

    if any(inside(q, point) for point in p) or any(inside(p, point) for point in q):
        return 0.0
    best = math.inf
    for one, other in ((p, q), (q, p)):
        for point in one:
            for i in range(len(other)):
                best = min(best, segment(point, other[i], other[(i + 1) % len(other)]))
    return best


def _flag(run: ReplayRun, check: str, t: float, subject: str, detail: str) -> Flag:
    return Flag(check, round(t, 4), round(run.display_time(t), 4), subject, detail)


def _track_motion(run: ReplayRun, track: TrackPath) -> List[Flag]:
    flags = []
    for a, b in zip(track.samples, track.samples[1:]):
        dt = b.time - a.time
        if dt <= 1e-6 or dt > track.max_gap + 1e-6:
            continue
        moved = math.hypot(b.position[0] - a.position[0], b.position[1] - a.position[1])
        if moved / dt > MAX_SPEED_MPS:
            flags.append(_flag(run, "impossible_track_speed", b.time, track.name,
                               "{0:.1f} m/s between samples".format(moved / dt)))
        if not track.ghost:
            continue  # an associated track is drawn as a dot: its nominal box is never shown
        shifted = math.hypot(b.centre[0] - a.centre[0], b.centre[1] - a.centre[1])
        if shifted - moved > BOX_JUMP_M:
            flags.append(_flag(run, "ghost_box_jump", b.time, track.name,
                               "box centre moved {0:.1f} m, track point {1:.1f} m".format(shifted, moved)))
        if a.heading == HEADING_FROM_VELOCITY and b.heading == HEADING_FROM_VELOCITY:
            spin = abs((b.yaw - a.yaw + 180.0) % 360.0 - 180.0)
            if spin > BOX_SPIN_DEG:
                flags.append(_flag(run, "ghost_box_spin", b.time, track.name, "heading turned {0:.0f} deg".format(spin)))
    return flags


def _entity_motion(run: ReplayRun, entity: EntityPath) -> List[Flag]:
    """A road user's drawn box: faster than any vehicle, a jump beyond its own speed, a sudden turn."""
    flags = []
    for a, b in zip(entity.states, entity.states[1:]):
        dt = b.time - a.time
        if dt <= 1e-6 or dt > entity.max_gap + 1e-6:
            continue
        moved = math.hypot(b.centre[0] - a.centre[0], b.centre[1] - a.centre[1])
        if moved / dt > MAX_SPEED_MPS:
            flags.append(_flag(run, "impossible_road_user_speed", b.time, entity.entity_id,
                               "{0:.1f} m/s between states".format(moved / dt)))
        if moved - 0.5 * (a.speed + b.speed) * dt > BOX_JUMP_M:
            flags.append(_flag(run, "road_user_box_jump", b.time, entity.entity_id,
                               "box moved {0:.1f} m at {1:.1f} m/s".format(moved, 0.5 * (a.speed + b.speed))))
        if (a.heading == HEADING_FROM_VELOCITY and b.heading == HEADING_FROM_VELOCITY
                and a.yaw is not None and b.yaw is not None):
            spin = abs((b.yaw - a.yaw + 180.0) % 360.0 - 180.0)
            if spin > BOX_SPIN_DEG:
                flags.append(_flag(run, "road_user_box_spin", b.time, entity.entity_id,
                                   "heading turned {0:.0f} deg".format(spin)))
    return flags


def _recorder_motion(run: ReplayRun) -> List[Flag]:
    flags = []
    for participant in run.participants:
        trajectory = participant.trajectory
        for (t0, p0), (t1, p1) in zip(zip(trajectory.times, trajectory.poses),
                                      zip(trajectory.times[1:], trajectory.poses[1:])):
            if t1 - t0 > 1e-6 and math.hypot(p1.x - p0.x, p1.y - p0.y) / (t1 - t0) > MAX_SPEED_MPS:
                flags.append(_flag(run, "impossible_recorder_speed", t1 - run.start, participant.participant_id,
                                   "pose jump {0:.1f} m".format(math.hypot(p1.x - p0.x, p1.y - p0.y))))
    return flags


def _ghosts_at(run: ReplayRun, t: float) -> List[Tuple[str, TrackPath, Any]]:
    out = []
    for participant in run.participants:
        for track in run.tracks.get(participant.participant_id, []):
            if track.ghost:
                point = track.state_at(t)
                if point is not None:
                    out.append((participant.participant_id, track, point))
    return out


def _bodies_at(run: ReplayRun, t: float) -> List[Tuple[str, str, List[Tuple[float, float]]]]:
    """(kind, name, footprint) of every body drawn at ``t``: recorders and anonymous road users."""
    out = [("recorder", p.participant_id, _footprint_world(p.trajectory.pose_at(run.start + t), p.footprint))
           for p in run.participants]
    for entity, state in run.entities_at(t):
        yaw = state.yaw if state.yaw is not None else 0.0
        out.append(("road_user", entity.entity_id, _box(state.centre, yaw, entity.length, entity.width)))
    return out


def _overlapping_bodies(run: ReplayRun) -> List[Flag]:
    """Two drawn bodies in one place: two road users (one body fused twice) or a road user on a recorder's
    own footprint (a recorder seen as an anonymous road user).  Contacts at collisions excepted."""
    flags, seen = [], set()
    steps = int(run.duration / SAMPLE_STEP_S) + 1
    for k in range(steps):
        t = k * SAMPLE_STEP_S
        if any(abs(mark.time - t) <= 1.0 for mark in run.collisions):
            continue
        bodies = _bodies_at(run, t)
        for i in range(len(bodies)):
            for j in range(i + 1, len(bodies)):
                (ka, na, pa), (kb, nb, pb) = bodies[i], bodies[j]
                if "road_user" not in (ka, kb):
                    continue
                if _polygon_distance(pa, pb) > 0.0:
                    continue
                check = "road_users_overlap" if ka == kb else "road_user_on_recorder"
                key = (check, na, nb)
                if key not in seen:
                    seen.add(key)
                    flags.append(_flag(run, check, t, "{0} / {1}".format(na, nb), "drawn bodies overlap from here"))
    return flags


def _duplicates(run: ReplayRun) -> List[Flag]:
    flags, seen = [], set()
    steps = int(run.duration / SAMPLE_STEP_S) + 1
    for k in range(steps):
        t = k * SAMPLE_STEP_S
        ghosts = _ghosts_at(run, t)
        for i in range(len(ghosts)):
            for j in range(i + 1, len(ghosts)):
                (oa, ta, pa), (ob, tb, pb) = ghosts[i], ghosts[j]
                if math.hypot(pa.centre[0] - pb.centre[0], pa.centre[1] - pb.centre[1]) > DUPLICATE_M:
                    continue
                check = "duplicate_ghost_same_observer" if oa == ob else "duplicate_ghost_across_observers"
                key = (check, ta.name, tb.name)
                if key not in seen:
                    seen.add(key)
                    flags.append(_flag(run, check, t, "{0} / {1}".format(ta.name, tb.name),
                                       "centres within {0:.1f} m from here".format(DUPLICATE_M)))
    return flags


def _events_outside_lifetime(run: ReplayRun) -> List[Flag]:
    flags = []
    for participant in run.participants:
        pid = participant.participant_id
        tracks = {track.track_id: track for track in run.tracks.get(pid, [])}
        local = run.local_events.get(pid)
        for event in (local.events if local else []):
            track = tracks.get(event.subject) if event.subject else None
            if track is None:
                continue
            if event.time < track.start - 0.06 or event.time > track.end + 0.06:
                flags.append(_flag(run, "event_outside_track_lifetime", event.time, "{0}:{1}".format(pid, event.subject),
                                   "{0} outside {1:.2f}..{2:.2f}".format(event.event_type, run.display_time(track.start),
                                                                          run.display_time(track.end))))
    return flags


def _partner_tracks(run: ReplayRun, recorder: str, mark: Any) -> List[str]:
    """The recorder's tracks that are the other party of a collision: associated with a participant, or an
    anonymous ghost touching the recorder at the collision (within CONTACT_M)."""
    participant = next(p for p in run.participants if p.participant_id == recorder)
    body = _footprint_world(participant.trajectory.pose_at(run.start + mark.time), participant.footprint)
    out = []
    for track in run.tracks.get(recorder, []):
        if track.road_user is not None:
            entity = run.entity(track.road_user)
            state = entity.state_at(mark.time) if entity is not None else None
            if state is not None and _polygon_distance(body, _box(state.centre, state.yaw or 0.0, entity.length,
                                                                  entity.width)) <= CONTACT_M:
                out.append(track.track_id)
            continue
        if not track.ghost:
            if track.entity in mark.participants and track.entity != recorder:
                out.append(track.track_id)
            continue
        point = track.state_at(mark.time)
        if point is not None and _polygon_distance(body, _box(point.centre, point.yaw, run.geometry.length,
                                                              run.geometry.width)) <= CONTACT_M:
            out.append(track.track_id)
    return out


def _critical_around_collisions(run: ReplayRun) -> List[Flag]:
    flags = []
    for mark in run.collisions:
        for recorder in mark.participants:
            local = run.local_events.get(recorder)
            if local is None:
                continue
            partners = _partner_tracks(run, recorder, mark)
            own_collisions = [other.time for other in run.collisions if recorder in other.participants]
            for event in local.events:
                if event.subject not in partners:
                    continue
                at_a_collision = any(abs(event.time - time) <= 0.01 for time in own_collisions)
                if (event.event_type == "CRITICAL_TTC_END" and not at_a_collision
                        and mark.time - NEAR_COLLISION_S <= event.time < mark.time - 1e-6):
                    flags.append(_flag(run, "critical_end_before_own_collision", event.time,
                                       "{0}:{1}".format(recorder, event.subject),
                                       "{0:.2f} s before the collision".format(mark.time - event.time)))
                if event.event_type == "CRITICAL_TTC_START" and mark.time - 1e-6 <= event.time <= mark.time + NEAR_COLLISION_S:
                    flags.append(_flag(run, "critical_start_after_own_collision", event.time,
                                       "{0}:{1}".format(recorder, event.subject),
                                       "{0:.2f} s after the collision".format(event.time - mark.time)))
    return flags


def _collision_geometry(run: ReplayRun) -> List[Flag]:
    flags = []
    for mark in run.collisions:
        bodies = [(p.participant_id, _footprint_world(p.trajectory.pose_at(run.start + mark.time), p.footprint))
                  for p in run.participants if p.participant_id in mark.participants]
        for i in range(len(bodies)):
            for j in range(i + 1, len(bodies)):
                gap = _polygon_distance(bodies[i][1], bodies[j][1])
                if gap > CONTACT_M:
                    flags.append(_flag(run, "collision_without_contact", mark.time,
                                       "{0},{1}".format(bodies[i][0], bodies[j][0]),
                                       "footprints {0:.2f} m apart at the collision".format(gap)))
    return flags


def _in_vehicle_frame(pose: Any, point: Tuple[float, float]) -> Tuple[float, float]:
    dx, dy = point[0] - pose.x, point[1] - pose.y
    return rotate(dx, dy, -pose.yaw)


def _geometry_of_events(run: ReplayRun) -> List[Flag]:
    flags = []
    for participant in run.participants:
        pid = participant.participant_id
        tracks = {track.track_id: track for track in run.tracks.get(pid, [])}
        local = run.local_events.get(pid)
        footprint = participant.footprint or DEFAULT_FOOTPRINT
        for event in (local.events if local else []):
            track = tracks.get(event.subject) if event.subject else None
            if track is None:
                continue
            now = track.state_at(event.time)
            if now is None:
                continue
            pose = participant.trajectory.pose_at(run.start + event.time)
            x, y = _in_vehicle_frame(pose, now.position)
            if event.event_type.startswith("CUT_IN_FROM_") and event.event_type.endswith("_START"):
                # The START is the onset of the lateral approach: over the window that follows it the target
                # comes laterally closer to the recorder, from the side the event names, each position in the
                # recorder's own frame of its instant (two cars following one bend keep their lateral offset;
                # a frame frozen earlier would turn the bend into a lateral motion).
                after = track.state_at(event.time + CUT_IN_WINDOW_S)
                if after is not None:
                    later = participant.trajectory.pose_at(run.start + event.time + CUT_IN_WINDOW_S)
                    y0 = y
                    _, y1 = _in_vehicle_frame(later, after.position)
                    side_ok = (y0 > 0) if "RIGHT" in event.event_type else (y0 < 0)
                    if not side_ok or abs(y0) - abs(y1) < CUT_IN_MIN_APPROACH_M:
                        flags.append(_flag(run, "cut_in_without_lateral_approach", event.time, "{0}:{1}".format(pid, event.subject),
                                           "lateral {0:+.2f} -> {1:+.2f} m over {2:.1f} s".format(y0, y1, CUT_IN_WINDOW_S)))
            body = event.attributes.get('estimated_body_corners_vehicle_m')
            inside = (body_in_corridor(np.asarray(body),footprint.x_max-.5,CORRIDOR_M) if body
                      else x >= footprint.x_max-.5 and abs(y) <= CORRIDOR_M)
            # An entry the body's own returns proved (``occupancy_evidence``) holds where its nominal box sits
            # short of them (a car seen from beside): only the box is drawn, the returns are not re-checked here.
            if event.event_type == "EGO_PATH_ENTRY" and not inside and event.attributes.get("occupancy_evidence") != "returns":
                flags.append(_flag(run, "path_entry_outside_corridor", event.time, "{0}:{1}".format(pid, event.subject),
                                   "track at {0:+.1f} m ahead, {1:+.1f} m lateral".format(x, y)))
    return flags


def check_run(run: ReplayRun) -> List[Flag]:
    """Every automatic flag of one run, in time order."""
    flags: List[Flag] = []
    for track in run.all_tracks():
        flags += _track_motion(run, track)
    for entity in run.entities:
        flags += _entity_motion(run, entity)
    flags += _recorder_motion(run)
    flags += _duplicates(run)
    flags += _overlapping_bodies(run)
    flags += _events_outside_lifetime(run)
    flags += _critical_around_collisions(run)
    flags += _collision_geometry(run)
    flags += _geometry_of_events(run)
    return sorted(flags, key=lambda flag: (flag.time, flag.check, flag.subject))


def flags_as_dicts(flags: Sequence[Flag]) -> List[Dict[str, Any]]:
    return [asdict(flag) for flag in flags]
