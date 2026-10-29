
from __future__ import annotations

import json
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..evaluation.reconstruction import RECONTACT_MAX_PAUSE_S, RECONTACT_MAX_SEPARATION_M, truth_separation
from ..reconstruction.fusion import group_recontacts
from ..reconstruction.tracking import EgoFootprint
from .model import (CollisionMark, LocalEvents, Participant, Pose, ReplayEvent, ReplayRun, Trajectory,
                    state_intervals)

GROUND_TRUTH_CLOCK = "t_contact"
CONTACT_GAP_S = 0.5


def _jsonl(path: Path) -> List[Dict[str, Any]]:
    with Path(path).open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


@dataclass(frozen=True)
class ContactEpisode:
    pair: Tuple[str, str]
    start: float
    end: float
    callbacks: int
    peak_impulse: float


def contact_episodes(collisions: List[Dict[str, Any]], actor_ids: Dict[int, str], start: float,
                     gap_s: float = CONTACT_GAP_S) -> Tuple[List[ContactEpisode], List[ContactEpisode]]:
    per_pair: Dict[Tuple[str, str], List[Tuple[float, float]]] = defaultdict(list)
    for c in collisions:
        other = actor_ids.get(int(c.get("other_actor_id", -1)))
        if other is None:
            other = "static:" + (str(c.get("other_type_id")) or "unknown")
        pair = tuple(sorted((str(c["participant_id"]), other)))
        per_pair[pair].append((float(c["timestamp"]) - start, float(c.get("impulse", 0.0))))
    vehicles, static = [], []
    for pair, hits in sorted(per_pair.items()):
        hits.sort()
        first = last = hits[0][0]
        peak, count = hits[0][1], 1
        for t, impulse in hits[1:]:
            if t - last > gap_s:
                (static if pair[0].startswith("static:") or pair[1].startswith("static:") else vehicles).append(
                    ContactEpisode(pair, round(first, 6), round(last, 6), count, peak))
                first, peak, count = t, impulse, 0
            last, peak, count = t, max(peak, impulse), count + 1
        (static if pair[0].startswith("static:") or pair[1].startswith("static:") else vehicles).append(
            ContactEpisode(pair, round(first, 6), round(last, 6), count, peak))
    return sorted(vehicles, key=lambda e: (e.start, e.pair)), sorted(static, key=lambda e: (e.start, e.pair))


def _footprint(extent: Optional[Dict[str, float]]) -> Optional[EgoFootprint]:
    if not extent:
        return None
    ex, ey = float(extent["x"]), float(extent["y"])
    return EgoFootprint(x_min=-ex, x_max=ex, y_min=-ey, y_max=ey)


class GroundTruthRun(ReplayRun):

    contact_zero: float = 0.0
    episodes: List[ContactEpisode]
    static_contacts: List[ContactEpisode]
    map_name: Optional[str] = None
    recorders: List[str]

    def display_time(self, t: float) -> float:
        return round(t - self.contact_zero, 6) + 0.0

    def recording_time(self, t: float) -> float:
        return self.start + t

    def replay_time_of(self, t_recording: float) -> float:
        return t_recording - self.start

    def scenario_time(self, t: float) -> float:
        return round(t, 6) + 0.0


def load_ground_truth_run(run_dir: Path) -> GroundTruthRun:
    run_dir = Path(run_dir)
    gt = run_dir / "ground_truth"
    states = _jsonl(gt / "states.jsonl")
    if not states:
        raise ValueError("no ground_truth/states.jsonl under " + str(run_dir))
    metadata = json.loads((gt / "metadata.json").read_text(encoding="utf-8")) if (gt / "metadata.json").exists() else {}
    start = min(float(s["timestamp"]) for s in states)
    by_pid: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    actor_ids: Dict[int, str] = {}
    for s in states:
        by_pid[str(s["participant_id"])].append(s)
        actor_ids[int(s["actor_id"])] = str(s["participant_id"])
    participants = []
    for pid in sorted(by_pid):
        rows = sorted(by_pid[pid], key=lambda s: float(s["timestamp"]))
        times, poses, speeds = [], [], []
        for s in rows:
            tf, v = s["transform"], s["velocity"]
            times.append(float(s["timestamp"]))
            poses.append(Pose(float(tf["x"]), float(tf["y"]), float(tf["z"]), float(tf["yaw_deg"]),
                              float(tf.get("pitch_deg", 0.0)), float(tf.get("roll_deg", 0.0))))
            speeds.append(math.hypot(float(v["x"]), float(v["y"])))
        trajectory = Trajectory(times, poses, speeds)
        participants.append(Participant(pid, str(rows[0]["type_id"]), "ground truth", trajectory, poses[0],
                                        _footprint(rows[0].get("bbox_extent")), trajectory))
    end = max(p.trajectory.end for p in participants)
    collisions = _jsonl(gt / "collisions.jsonl") if (gt / "collisions.jsonl").exists() else []
    episodes, static = contact_episodes(collisions, actor_ids, start)
    separation = truth_separation(states)
    incidents = group_recontacts(episodes, lambda e: e.pair, lambda e: e.start,
                                 lambda pair, t1, t2: separation(pair, start + t1, start + t2),
                                 RECONTACT_MAX_PAUSE_S, RECONTACT_MAX_SEPARATION_M)
    run = GroundTruthRun(run_dir=run_dir, name="GROUND TRUTH  {0} / {1}".format(run_dir.parent.name, run_dir.name),
                         participants=participants, start=start, duration=round(end - start, 6),
                         clock=GROUND_TRUTH_CLOCK, clock_origins={})
    run.episodes, run.static_contacts = episodes, static
    run.contact_zero = episodes[0].start if episodes else 0.0
    run.map_name = metadata.get("map")
    run.recorders = [p["participant_id"] for p in metadata.get("participants", []) if p.get("record")]
    run.collisions = [CollisionMark(e.start, e.pair, "gt_contact_{0}".format(i)) for i, (e, _) in enumerate(incidents)]
    events: Dict[str, List[ReplayEvent]] = defaultdict(list)
    for i, (first, later) in enumerate(incidents):
        for j, e in enumerate([first] + later):
            kind, node = ("CONTACT", "c{0}".format(i)) if j == 0 else ("RECONTACT", "c{0}r{1}".format(i, j))
            for me, other in (e.pair, e.pair[::-1]):
                attrs = {"callbacks": e.callbacks, "peak_impulse_Ns": round(e.peak_impulse, 1)}
                events[me].append(ReplayEvent(e.start, me, kind + "_START", other, node + "s", attrs))
                events[me].append(ReplayEvent(e.end, me, kind + "_END", other, node + "e", attrs))
    for i, e in enumerate(static):
        me = e.pair[1] if e.pair[0].startswith("static:") else e.pair[0]
        other = e.pair[0] if me == e.pair[1] else e.pair[1]
        events[me].append(ReplayEvent(e.start, me, "STATIC_CONTACT", other, "s{0}".format(i), {}))
    for p in participants:
        evs = sorted(events.get(p.participant_id, []),
                     key=lambda ev: (ev.time, ev.event_type.endswith("_END"), ev.node_id))
        run.local_events[p.participant_id] = LocalEvents(p.participant_id, start, evs, state_intervals(evs))
    roles = ", ".join("{0}{1}".format(p.participant_id, "" if p.participant_id in run.recorders else " (not recording)")
                      for p in participants)
    run.notes.append("ground truth: vehicles " + roles)
    return run
