"""A worked example of one reconstructed run: what the recorders established, then (separately) what was true.

Deterministic, no model call.  Two parts, computed in this order:

1. RECONSTRUCTION (admissible).  Only the recorder's own files and the
   reconstruction outputs are read: ``reconstruction/global/`` (alignment,
   associations, global graph), ``reconstruction/<recorder>/`` (local graphs,
   the observer's ``local_trace.jsonl``) and the observer's own
   ``vehicles/<id>/controls.jsonl`` (its steering command).  The part runs under an
   audit hook and fails if anything under ``ground_truth/``,
   ``reconstruction/evaluation/``, ``configs/scenarios/`` or the run's own
   ``metadata.json`` is opened.
2. PRIVILEGED EVALUATION, clearly separated: the simulator's ground truth
   (``ground_truth/``) and the privileged evaluation (track identities), read only
   after part 1 is complete, to judge whether the experiment did what it was
   designed to do.  Nothing of it flows back: the isolation check reconstructs the
   run again from a copy holding only ``vehicles/`` and the supplied incident
   context and requires byte-identical reconstruction outputs.

Delays between a perceived hazard and the recorder's own steering command are
reported as observed vehicle response delays: the sensors say when the hazard
was perceivable by the vehicle, not when a driver perceived it, so they are not
human reaction times.
"""

from __future__ import annotations

import json
import math
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

# A steering command counts as a response once |steer| reaches this and stays there for STEER_HOLD_S
# (the controller's idle noise in the campaign is below 1e-4).
STEER_ONSET = 0.001
STEER_HOLD_S = 0.2
# The heading responds once |yaw rate| reaches this (EGO_MOTION facts, 10 Hz).
YAW_RATE_ONSET_DPS = 0.5
FORBIDDEN_PARTS = ("ground_truth", os.sep + "evaluation" + os.sep, os.sep + "scenarios" + os.sep)


def _read_json(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


# --------------------------------------------------------------------------
# File-access audit of part 1
# --------------------------------------------------------------------------

_OPENED: List[str] = []
_RECORDING = [False]
_HOOKED = [False]


def _audit(event: str, args: Tuple[Any, ...]) -> None:
    if not _RECORDING[0] or event != "open" or not args:
        return
    try:
        if isinstance(args[0], (str, bytes, os.PathLike)):
            _OPENED.append(os.path.abspath(os.fsdecode(os.fspath(args[0]))))
    except Exception:  # an audit hook must never break the audited call
        pass


class FileAudit:
    """Records every file opened while active (sys.addaudithook, installed once per process)."""

    def __enter__(self) -> "FileAudit":
        if not _HOOKED[0]:
            sys.addaudithook(_audit)
            _HOOKED[0] = True
        del _OPENED[:]
        _RECORDING[0] = True
        return self

    def __exit__(self, *exc: Any) -> None:
        _RECORDING[0] = False
        self.opened = list(_OPENED)


def privileged_reads(opened: Sequence[str], run_dir: Path) -> List[str]:
    """The opened files a reconstruction-only computation must never touch."""
    run_metadata = os.path.normcase(os.path.abspath(str(Path(run_dir) / "metadata.json")))
    return [path for path in opened if os.path.normcase(path) == run_metadata
            or any(part in os.path.normcase(path) for part in FORBIDDEN_PARTS)]


# --------------------------------------------------------------------------
# Part 1: the reconstruction
# --------------------------------------------------------------------------

@dataclass
class TimelineRow:
    t_local: Optional[float]
    t_global: Optional[float]
    event: str
    actor: str
    subject: str
    facts_t_local: Optional[float] = None
    clearance_m: Optional[float] = None
    required_m: Optional[float] = None
    reason: Optional[str] = None
    note: str = ""


@dataclass
class ReconstructionPart:
    observer: str
    track: str
    offsets: Dict[str, Optional[float]]
    statuses: Dict[Tuple[str, str], Tuple[str, str]]
    timeline: List[TimelineRow]
    samples: List[Dict[str, Any]]
    delays: Dict[str, Optional[float]]
    cut_ins: Dict[str, List[str]]
    opened: List[str] = field(default_factory=list)


def _subject_label(graph: str, track: Optional[str], statuses: Dict[Tuple[str, str], Tuple[str, str]]) -> str:
    if not track:
        return "-"
    status, entity = statuses.get((graph, track), ("ANONYMOUS", "{0}:{1}".format(graph, track)))
    if status == "ASSOCIATED":
        return "{0} (associated, {1}:{2})".format(entity, graph, track)
    return "{0}:{1} (anonymous)".format(graph, track)


def _frames(trace_path: Path) -> List[Dict[str, Any]]:
    return sorted(_read_jsonl(trace_path), key=lambda frame: float(frame["t_local"]))


def _frame_at_or_before(frames: Sequence[Dict[str, Any]], t_local: float) -> Optional[Dict[str, Any]]:
    best = None
    for frame in frames:
        if float(frame["t_local"]) <= t_local + 1e-6:
            best = frame
        else:
            break
    return best


def _frame_at_or_after(frames: Sequence[Dict[str, Any]], t_local: float) -> Optional[Dict[str, Any]]:
    """The first trace frame at or after ``t_local``: a frame holds the state after its own transitions, so an
    event between two 10 Hz frames is first described by the next one."""
    return next((frame for frame in frames if float(frame["t_local"]) >= t_local - 1e-6), None)


def _fact(frame: Optional[Dict[str, Any]], kind: str, subject: Optional[str] = None) -> Optional[Dict[str, Any]]:
    if frame is None:
        return None
    for fact in frame["facts"]:
        if fact["type"] == kind and (subject is None or fact.get("subject_id") == subject):
            return fact["attributes"]
    return None


def steering_onset(controls_path: Path, clock_origin: float, after: float = 0.0) -> Optional[float]:
    """Local time of the first sustained steering command (|steer| >= STEER_ONSET for STEER_HOLD_S)."""
    rows = sorted(((float(r["timestamp"]) - clock_origin, float(r["steer"])) for r in _read_jsonl(controls_path)),
                  key=lambda item: item[0])
    for index, (t, steer) in enumerate(rows):
        if t < after - 1e-9 or abs(steer) < STEER_ONSET:
            continue
        held = [s for u, s in rows[index:] if u <= t + STEER_HOLD_S + 1e-9]
        if all(abs(s) >= STEER_ONSET and math.copysign(1.0, s) == math.copysign(1.0, steer) for s in held):
            return round(t, 3)
    return None


def reconstruction_part(run_dir: Path, observer: str = "A", track: str = "track_001") -> ReconstructionPart:
    """Part 1 of the module docstring: only admissible files, under the file audit."""
    run_dir = Path(run_dir)
    with FileAudit() as audit:
        rec = run_dir / "reconstruction"
        alignment = _read_json(rec / "global" / "alignment.json")
        offsets = {name: clock.get("offset_to_global") for name, clock in alignment["graphs"].items()}
        statuses = {(str(a["local_graph"]), str(a["local_track"])): (str(a["status"]), str(a["global_entity"]))
                    for a in _read_json(rec / "global" / "associations.json")}
        graphs = {path.parent.name: _read_json(path) for path in sorted(rec.glob("*/local_graph.json"))}
        frames = _frames(rec / observer / "local_trace.jsonl")
        offset = offsets.get(observer)

        def to_global(t_local: Optional[float]) -> Optional[float]:
            return None if t_local is None or offset is None else round(t_local + offset, 3)

        nodes = graphs[observer]["nodes"]
        partner = next((tr for (graph, tr), (status, _) in sorted(statuses.items())
                        if graph == observer and tr != track and status == "ASSOCIATED"), None)

        def first(event_type: str, subject: Optional[str]) -> Optional[Dict[str, Any]]:
            return next((n for n in nodes if n["event_type"].startswith(event_type)
                         and (subject is None or n.get("subject_id") == subject)), None)

        timeline: List[TimelineRow] = []

        def row(node: Optional[Dict[str, Any]], subject: Optional[str], note: str = "") -> None:
            if node is None:
                return
            t = float(node["t_local"])
            frame = _frame_at_or_after(frames, t) or _frame_at_or_before(frames, t)
            state = _fact(frame, "TRACK_STATE", subject) if subject else None
            timeline.append(TimelineRow(
                t, to_global(t), node["event_type"], observer, _subject_label(observer, subject, statuses),
                None if frame is None else float(frame["t_local"]),
                None if state is None else state.get("longitudinal_clearance_m"),
                None if state is None else state.get("required_safe_distance_m"),
                None if state is None else state.get("critical_reason"), note))

        row(first("TRACK_APPEARED", track), track)
        known = next((float(f["t_local"]) for f in frames
                      if (_fact(f, "TRACK_STATE", track) or {}).get("estimate_known")), None)
        if known is not None:
            frame = _frame_at_or_before(frames, known)
            state = _fact(frame, "TRACK_STATE", track) or {}
            timeline.append(TimelineRow(known, to_global(known), "track estimate known (age and std gates)", observer,
                                        _subject_label(observer, track, statuses), known,
                                        state.get("longitudinal_clearance_m"), state.get("required_safe_distance_m"),
                                        state.get("critical_reason")))
        row(first("CRITICAL_TTC_START", track), track)
        row(first("CUT_IN_FROM_", track), track)
        row(first("EGO_PATH_ENTRY", track), track)
        clock_origin = float(graphs[observer]["recorder"]["clock"]["origin_source_timestamp"])
        hazard = min((r.t_local for r in timeline if r.event.startswith(("CRITICAL_TTC_START", "CUT_IN"))), default=0.0)
        steer = steering_onset(run_dir / "vehicles" / observer / "controls.jsonl", clock_origin, after=hazard)
        if steer is not None:
            frame = _frame_at_or_before(frames, steer)
            state = _fact(frame, "TRACK_STATE", track) or {}
            timeline.append(TimelineRow(steer, to_global(steer), "steering command onset (controls.jsonl)", observer,
                                        "-", None if frame is None else float(frame["t_local"]),
                                        state.get("longitudinal_clearance_m"), state.get("required_safe_distance_m"),
                                        state.get("critical_reason"),
                                        "abs(steer) >= {0} held {1} s".format(STEER_ONSET, STEER_HOLD_S)))
        yaw = next((float(f["t_local"]) for f in frames if float(f["t_local"]) >= hazard - 1e-9
                    and abs((_fact(f, "EGO_MOTION") or {}).get("yaw_rate_dps", 0.0)) >= YAW_RATE_ONSET_DPS), None)
        if yaw is not None:
            timeline.append(TimelineRow(yaw, to_global(yaw), "heading response onset (EGO_MOTION)", observer, "-",
                                        yaw, note="abs(yaw rate) >= {0} deg/s".format(YAW_RATE_ONSET_DPS)))
        if partner is not None:
            row(first("CRITICAL_TTC_START", partner), partner)
        collision = first("COLLISION", None)
        if collision is not None:
            gnode = next((n for n in _read_json(rec / "global" / "global_graph.json")["nodes"]
                          if n["event_type"] == "COLLISION"
                          and any(o.get("graph") == observer for o in n.get("observations") or [])), None)
            participants = ", ".join(gnode.get("participants") or []) if gnode else "-"
            row(collision, partner, note="global participants: " + participants)
        timeline.sort(key=lambda r: (r.t_local if r.t_local is not None else 1e9))

        samples = []
        for frame in frames:
            t = float(frame["t_local"])
            state = _fact(frame, "TRACK_STATE", track)
            if state is None:
                continue
            ego = _fact(frame, "EGO_MOTION") or {}
            control = _fact(frame, "EGO_CONTROL") or {}
            samples.append({
                "t_local": t, "t_global": to_global(t), "ego_speed_mps": state.get("ego_speed_mps"),
                "target_speed_mps": state.get("speed_mps"), "clearance_m": state.get("longitudinal_clearance_m"),
                "lateral_m": state.get("lateral_m"), "body_gap_m": state.get("lateral_body_gap_m"),
                "t_front_s": state.get("minimum_time_gap_s"), "d_timegap_m": state.get("time_gap_distance_m"),
                "d_min_m": state.get("required_safe_distance_m"), "region": state.get("forward_region"),
                "reason": state.get("critical_reason"), "collision_course": state.get("collision_course"),
                "ttc_s": state.get("ttc_s"), "known": state.get("estimate_known"),
                "occluded": state.get("line_of_sight_occluded"), "steer": control.get("steer"),
                "yaw_rate_dps": ego.get("yaw_rate_dps")})

        def delay(anchor_prefix: str) -> Optional[float]:
            anchor = next((r.t_local for r in timeline if r.event.startswith(anchor_prefix)), None)
            return None if anchor is None or steer is None else round(steer - anchor, 3)

        delays = {"perception (CUT_IN start) -> steering": delay("CUT_IN_FROM_"),
                  "path entry (EGO_PATH_ENTRY) -> steering": delay("EGO_PATH_ENTRY"),
                  "critical (CRITICAL_TTC_START on the track) -> steering": delay("CRITICAL_TTC_START"),
                  "steering -> heading response": None if steer is None or yaw is None else round(yaw - steer, 3)}
        cut_ins = {owner: ["{0} {1} at {2}".format(n["event_type"],
                                                     _subject_label(owner, n.get("subject_id"), statuses), n["t_local"])
                           for n in graph["nodes"]
                           if n["event_type"].startswith("CUT_IN") and n["event_type"].endswith("_START")]
                   for owner, graph in sorted(graphs.items())}
    part = ReconstructionPart(observer, track, offsets, statuses, timeline, samples, delays, cut_ins, audit.opened)
    leaks = privileged_reads(part.opened, run_dir)
    if leaks:
        raise RuntimeError("the reconstruction part opened privileged files: {0}".format(leaks))
    return part


# --------------------------------------------------------------------------
# Isolation check: the privileged files change nothing in the reconstruction
# --------------------------------------------------------------------------

def isolation_check(run_dir: Path) -> Dict[str, Any]:
    """Reconstruct a copy holding only vehicles/ and the incident context; compare every output byte for byte."""
    from ..reconstruction.config import load_config
    from ..reconstruction.pipeline import reconstruct_run

    run_dir = Path(run_dir)
    reference = run_dir / "reconstruction"
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp) / run_dir.parent.name / run_dir.name
        shutil.copytree(str(run_dir / "vehicles"), str(copy / "vehicles"))
        if (run_dir / "incident_context.json").exists():
            shutil.copy2(str(run_dir / "incident_context.json"), str(copy / "incident_context.json"))
        reconstruct_run(copy, load_config())
        produced = sorted(p.relative_to(copy / "reconstruction").as_posix()
                          for p in (copy / "reconstruction").rglob("*") if p.is_file())
        differ = [name for name in produced if not (reference / name).exists()
                  or (reference / name).read_bytes() != (copy / "reconstruction" / name).read_bytes()]
        privileged_present = sorted(name for name in ("ground_truth", "metadata.json") if (run_dir / name).exists())
    return {"compared_files": len(produced), "different_files": differ, "identical": not differ,
            "privileged_inputs_absent_from_copy": privileged_present}


# --------------------------------------------------------------------------
# Part 2: the privileged evaluation
# --------------------------------------------------------------------------

def _states_by_time(run_dir: Path) -> Tuple[Dict[float, Dict[str, Dict[str, Any]]], Dict[int, str]]:
    by_t: Dict[float, Dict[str, Dict[str, Any]]] = {}
    actors: Dict[int, str] = {}
    for row in _read_jsonl(Path(run_dir) / "ground_truth" / "states.jsonl"):
        by_t.setdefault(round(float(row["timestamp"]), 4), {})[str(row["participant_id"])] = row
        actors[int(row["actor_id"])] = str(row["participant_id"])
    return by_t, actors


def _relative(ego: Dict[str, Any], other: Dict[str, Any]) -> Tuple[float, float]:
    yaw = math.radians(ego["transform"]["yaw_deg"])
    dx, dy = other["transform"]["x"] - ego["transform"]["x"], other["transform"]["y"] - ego["transform"]["y"]
    return math.cos(yaw) * dx + math.sin(yaw) * dy, -math.sin(yaw) * dx + math.cos(yaw) * dy


def privileged_part(run_dir: Path, part: ReconstructionPart) -> Dict[str, Any]:
    """Part 2 of the module docstring: ground truth and the privileged evaluation, read only now."""
    run_dir = Path(run_dir)
    truth = run_dir / "ground_truth"
    evaluation = _read_json(run_dir / "reconstruction" / "evaluation" / "evaluation.json")
    identities = {row["track"]: row.get("true_identity") for row in evaluation.get("tracks", [])}
    metadata = _read_json(truth / "metadata.json")
    unrecorded = [p["participant_id"] for p in metadata.get("participants", []) if not p.get("record", True)]
    collisions = _read_jsonl(truth / "collisions.jsonl") if (truth / "collisions.jsonl").exists() else []
    triggers = _read_jsonl(truth / "triggers.jsonl") if (truth / "triggers.jsonl").exists() else []
    counterfactuals = _read_json(truth / "counterfactuals.json") if (truth / "counterfactuals.json").exists() else {}
    observer_first = float(json.loads((run_dir / "vehicles" / part.observer / "ego.jsonl").open(
        encoding="utf-8").readline())["timestamp"])
    by_t, actors = _states_by_time(run_dir)
    hidden = identities.get("{0}:{1}".format(part.observer, part.track))
    lateral = []
    if hidden:
        for t_local in (0.0, 2.0, 2.4, 2.6, 2.8, 3.0, 3.3, 3.6, 4.0, 4.4, 4.95):
            key = min(by_t, key=lambda ts: abs(ts - (observer_first + t_local)))
            states = by_t[key]
            if part.observer in states and hidden in states:
                lon, lat = _relative(states[part.observer], states[hidden])
                half_obs = states[part.observer]["bbox_extent"]["x"]
                half_hid = states[hidden]["bbox_extent"]["x"]
                lateral.append({"t_local": t_local, "centre_lon_m": round(lon, 2), "centre_lat_m": round(lat, 2),
                                "bumper_gap_m": round(lon - half_obs - half_hid, 2)})
    pairs = sorted({tuple(sorted((str(c["participant_id"]), actors.get(int(c["other_actor_id"]), "other"))))
                    for c in collisions})
    factual = (counterfactuals or {}).get("factual") or {}
    variants = (counterfactuals or {}).get("counterfactuals") or {}
    anonymous = ["{0}:{1}".format(graph, track) for (graph, track), (status, _) in part.statuses.items()
                 if status != "ASSOCIATED"]
    critical = next((r for r in part.timeline if r.event == "CRITICAL_TTC_START"
                     and r.subject.startswith("{0}:{1}".format(part.observer, part.track))), None)
    truth_gap = None
    if hidden and critical is not None:
        key = min(by_t, key=lambda ts: abs(ts - (observer_first + critical.t_local)))
        states = by_t[key]
        lon, _ = _relative(states[part.observer], states[hidden])
        truth_gap = round(lon - states[part.observer]["bbox_extent"]["x"] - states[hidden]["bbox_extent"]["x"], 2)
    lat = [row["centre_lat_m"] for row in lateral]
    observed_gaps = (factual.get("box_gaps") or {}).get("{0}-{1}".format(part.observer, hidden)) or {}
    swerve = variants.get("swerve_disabled") or {}
    without = variants.get("without_{0}".format(hidden)) or {}
    checks = [
        ("every anonymous track is the unrecorded participant",
         bool(anonymous) and all(identities.get(name) in unrecorded for name in anonymous),
         ", ".join("{0} = {1}".format(name, identities.get(name)) for name in sorted(anonymous))),
        ("{0} cuts in ahead of {1}".format(hidden, part.observer),
         bool(lat) and lat[0] >= 3.0 and min(lat) <= 1.5 and all(row["bumper_gap_m"] > 0 for row in lateral),
         "centre lateral offset {0:.2f} m -> {1:.2f} m, always ahead".format(lat[0], min(lat)) if lat else "-"),
        ("{0} avoids {1}".format(part.observer, hidden),
         bool(hidden) and all(not (hidden in pair and part.observer in pair) for pair in pairs)
         and (observed_gaps.get("min_box_gap_m") or 0.0) > 0.0,
         "smallest box gap {0} m".format(observed_gaps.get("min_box_gap_m"))),
        ("{0} strikes B".format(part.observer), ("A", "B") in pairs,
         "true contacts: " + ", ".join("-".join(pair) for pair in pairs)),
        ("{0} collides with nobody".format(hidden), bool(hidden) and all(hidden not in pair for pair in pairs), "-"),
        ("without {0}: no collision".format(hidden), bool(without) and not (without.get("collisions") or {}),
         "counterfactuals.json"),
        ("swerve disabled: {0} runs into {1}".format(part.observer, hidden),
         "{0}-{1}".format(part.observer, hidden) in (swerve.get("collisions") or {}),
         json.dumps(swerve.get("collisions"))),
        ("reconstructed clearance at the critical start vs true bumper gap",
         critical is not None and truth_gap is not None and abs((critical.clearance_m or 0.0) - truth_gap) <= 0.3,
         "{0} m reconstructed, {1} m true".format(None if critical is None else critical.clearance_m, truth_gap))]
    # When the hazards were perceivable per ground truth: the event oracle (cdf.evaluation.event_oracle) under
    # the reconstruction's own definitions, all-seeing (PERFECT) and within the observer's radar coverage.
    from ..reconstruction.config import load_config
    from .event_oracle import compare_run
    oracle = compare_run(run_dir, load_config())
    first: Dict[Tuple[str, str], Dict[str, Optional[float]]] = {}
    cut = oracle["first_contact_t_local"].get(part.observer, math.inf)
    for source in ("RECONSTRUCTION", "COVERAGE", "PERFECT"):
        for event in oracle["events"][source].get(part.observer, []):
            if event["subject"] is None or event["t_local"] >= cut or event["type"] == "TRACK_APPEARED":
                continue
            key = (event["subject"], event["type"])
            row = first.setdefault(key, {"RECONSTRUCTION": None, "COVERAGE": None, "PERFECT": None})
            if row[source] is None or event["t_local"] < row[source]:
                row[source] = event["t_local"]
    return {"identities": identities, "unrecorded": unrecorded, "collision_pairs": pairs, "triggers": triggers,
            "counterfactuals": counterfactuals, "relative_to_observer": lateral, "hidden": hidden,
            "headline": evaluation.get("headline"), "checks": checks, "oracle_first_events": first,
            "first_contact_t_local": None if cut == math.inf else cut}


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def _f(value: Any, digits: int = 2) -> str:
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        return "{0:.{1}f}".format(value, digits)
    return str(value)


def part_files(part: ReconstructionPart, run_dir: Path) -> List[str]:
    """The run files opened by part 1, relative to the run directory, in a stable order."""
    root = os.path.normcase(os.path.abspath(str(run_dir))) + os.sep
    return sorted({path[len(root):].replace(os.sep, "/") for path in part.opened
                   if os.path.normcase(path).startswith(root)})


def render(run_dir: Path, part: ReconstructionPart, isolation: Dict[str, Any], truth: Dict[str, Any],
           sample_times: Sequence[float]) -> str:
    name = "{0}/{1}".format(Path(run_dir).parent.name, Path(run_dir).name)
    out = ["# Worked example: {0}".format(name), "",
           "Generated by `scripts/worked_example.py` (deterministic, no model call).  Part 1 uses only the "
           "recorders' own files and the reconstruction outputs; part 2, clearly separated, is the privileged "
           "evaluation against the simulator's ground truth and is never an input of part 1.", "",
           "## Part 1. Reconstruction (admissible inputs only)", "",
           "Observer {0}, anonymous radar track {1}.  Time: t_global = t_local + offset_to_global from the "
           "collision-anchored alignment ({2}).  Safe following distance d_min = max(v_ego x t_front(v_ego), 2 m), "
           "t_front from the UN R157 (ALKS, M1/N1) table, an engineering reference.  CRITICAL_TTC is the event's "
           "historical name: an UNSAFE_FORWARD_GAP has no classical TTC (ttc_s is shown only where a 2-D overlap "
           "is predicted).".format(part.observer, "{0}:{1}".format(part.observer, part.track),
                                   ", ".join("{0} {1:+.2f} s".format(g, o) for g, o in sorted(part.offsets.items())
                                             if o is not None)), "",
           "Track identities known to the reconstruction (associations.json):", "",
           "| local track | status | global entity |", "|---|---|---|"]
    for (graph, track), (status, entity) in sorted(part.statuses.items()):
        out.append("| {0}:{1} | {2} | {3} |".format(graph, track, status, entity))
    out += ["", "### 1.1 Timeline", "",
            "| t_global | t_local | event | actor | subject | facts at t_local | clearance m | d_min m | "
            "critical reason | note |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for r in part.timeline:
        ahead = r.clearance_m is not None and r.clearance_m > 0.0
        out.append("| {0} | {1} | {2} | {3} | {4} | {5} | {6} | {7} | {8} | {9} |".format(
            _f(r.t_global), _f(r.t_local), r.event, r.actor, r.subject, _f(r.facts_t_local),
            _f(r.clearance_m) if ahead or r.clearance_m is None else "not ahead",
            _f(r.required_m) if ahead else "-", r.reason or "-", r.note or ""))
    out += ["", "### 1.2 {0}'s TRACK_STATE facts of {0}:{1}".format(part.observer, part.track), "",
            "| t_local | t_global | v_ego m/s | v_target m/s | clearance m | lateral m | body gap m | t_front s | "
            "d_timegap m | d_min m | region | critical reason | collision course | ttc_s | steer |",
            "|" + "---|" * 15]
    wanted = {round(t, 2) for t in sample_times}
    for s in part.samples:
        if round(s["t_local"], 2) not in wanted:
            continue
        cells = [_f(s["t_local"]), _f(s["t_global"]), _f(s["ego_speed_mps"]), _f(s["target_speed_mps"]),
                 _f(s["clearance_m"]), _f(s["lateral_m"]), _f(s["body_gap_m"]), _f(s["t_front_s"], 3),
                 _f(s["d_timegap_m"]), _f(s["d_min_m"]), _f(s["region"]), _f(s["reason"]),
                 _f(s["collision_course"]), _f(s["ttc_s"]), _f(s["steer"], 3)]
        out.append("| " + " | ".join(cells) + " |")
    out += ["", "### 1.3 Observed vehicle response delays", "",
            "From a hazard the recorder's sensors established to the recorder's own steering command "
            "(controls.jsonl, abs(steer) >= {0} held {1} s).  These are observed vehicle response delays, not human "
            "reaction times: the sensors say when the hazard was perceivable by the vehicle, not when a driver "
            "perceived it.  A human driver can perceive cues the radar does not measure (turn indicators, the other "
            "driver's gaze, the lane-change intent shown by a drift) and can miss what it measures (inattention, "
            "blind spots); an automated driving system perceives through its own sensors and adds its own "
            "processing and planning time.  These delays are inputs for an expert's analysis, to be read against "
            "perception-reaction time distributions chosen for the right expectation level and kinematic context "
            "(docs/event_definitions.md), never a verdict on avoidability or responsibility.".format(
                STEER_ONSET, STEER_HOLD_S), "", "| interval | s |", "|---|---|"]
    for label, value in part.delays.items():
        out.append("| {0} | {1} |".format(label, _f(value)))
    out += ["", "### 1.4 Cut-ins established by each recorder", ""]
    for owner, items in part.cut_ins.items():
        out.append("- {0}: {1}".format(owner, "; ".join(items) if items else "none"))
    out += ["", "### 1.5 Isolation checks", "",
            "- File audit of part 1: it opened {0} (and nothing else of the run): none under ground_truth/, "
            "reconstruction/evaluation/, configs/scenarios/, nor the run's metadata.json.".format(
                ", ".join(part_files(part, run_dir))),
            "- Reconstruction rerun from a copy holding only vehicles/ and the incident context (no {0}): {1} "
            "output files compared, {2}.".format(
                ", ".join(isolation["privileged_inputs_absent_from_copy"]) or "privileged files",
                isolation["compared_files"],
                "all byte-identical" if isolation["identical"]
                else "DIFFERENT: " + ", ".join(isolation["different_files"])),
            "", "## Part 2. Privileged evaluation (ground truth; never an input of part 1)", ""]
    hidden = truth["hidden"]
    out += ["| check | result | detail |", "|---|---|---|"]
    for label, passed, detail in truth["checks"]:
        out.append("| {0} | {1} | {2} |".format(label, "PASS" if passed else "FAIL", detail))
    out.append("")
    out.append("- Track identities (privileged evaluation): " + "; ".join(
        "{0} = {1}".format(track, who) for track, who in sorted(truth["identities"].items())))
    out.append("- Participants that recorded nothing: {0}.".format(", ".join(truth["unrecorded"]) or "none"))
    out.append("- True vehicle contacts (ground_truth/collisions.jsonl): {0}{1}.".format(
        ", ".join("-".join(pair) for pair in truth["collision_pairs"]) or "none",
        "" if not hidden else "; {0} touches nobody".format(hidden) if all(hidden not in pair for pair in truth[
            "collision_pairs"]) else ""))
    for trigger in truth["triggers"]:
        out.append("- Scripted response (privileged trigger): {0} fired at {1:.2f} s ({2}, measured {3}); the "
                   "action started at {4:.2f} s.".format(trigger.get("action_id"), float(trigger.get("t_scenario")),
                                                          (trigger.get("trigger") or {}).get("kind"),
                                                          json.dumps(trigger.get("measured")),
                                                          float(trigger.get("action_t_start"))))
        out.append("  The observed steering onset of part 1 is this scripted action's start: the response delays "
                   "of part 1 measure the scenario's trigger logic plus its scripted latency, not a driver.")
    if truth["relative_to_observer"]:
        out += ["", "{0} relative to {1} (centres, {1}'s heading; bumper gap along it):".format(hidden, part.observer),
                "", "| t_local | longitudinal m | lateral m | bumper gap m |", "|---|---|---|---|"]
        for row in truth["relative_to_observer"]:
            out.append("| {0:.2f} | {1:.2f} | {2:.2f} | {3:.2f} |".format(
                row["t_local"], row["centre_lon_m"], row["centre_lat_m"], row["bumper_gap_m"]))
    factual = (truth["counterfactuals"] or {}).get("factual") or {}
    if factual:
        out += ["", "Factual run: collisions {0}; smallest box gaps {1}.".format(
            json.dumps(factual.get("collisions")), json.dumps(factual.get("box_gaps")))]
    for label, cf in sorted(((truth["counterfactuals"] or {}).get("counterfactuals") or {}).items()):
        out.append("Counterfactual {0}: collisions {1}.".format(label, json.dumps(cf.get("collisions") or {})))
    if truth.get("oracle_first_events"):
        out += ["", "### 2.1 Hazard perceivability against the ground-truth event oracle", "",
                "First core events of {0} per true subject before {0}'s first contact (t_local {1}): the "
                "reconstruction (part 1), and the reconstruction's own event definitions applied to ground truth "
                "within {0}'s radar coverage (COVERAGE) and with an all-seeing sensor (PERFECT); "
                "`cdf.evaluation.event_oracle`.  The difference is what sensing and tracking cost: when the sensors "
                "established each hazard against when it was geometrically present.".format(
                    part.observer, _f(truth.get("first_contact_t_local"))), "",
                "| subject (true) | event | reconstruction t_local | COVERAGE t_local | PERFECT t_local |",
                "|---|---|---|---|---|"]
        for (subject, event_type), row in sorted(truth["oracle_first_events"].items(),
                                                 key=lambda item: (item[0][0], min(v for v in item[1].values()
                                                                                    if v is not None))):
            out.append("| {0} | {1} | {2} | {3} | {4} |".format(subject, event_type, _f(row["RECONSTRUCTION"]),
                                                               _f(row["COVERAGE"]), _f(row["PERFECT"])))
    if truth.get("headline"):
        out += ["", "Evaluation headline: " + truth["headline"]]
    return "\n".join(out) + "\n"


def write_worked_example(run_dir: Path, observer: str = "A", track: str = "track_001",
                         sample_times: Optional[Sequence[float]] = None, name: Optional[str] = None) -> Path:
    run_dir = Path(run_dir)
    part = reconstruction_part(run_dir, observer, track)  # part 1 first, under the file audit
    isolation = isolation_check(run_dir)
    truth = privileged_part(run_dir, part)
    if sample_times is None:
        sample_times = [0.5, 1.0, 2.0] + [round(2.3 + 0.1 * k, 1) for k in range(28)]
    out_dir = run_dir / "reconstruction" / "evaluation"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / (name or "{0}_worked_example.md".format(run_dir.parent.name.lower()))
    path.write_text(render(run_dir, part, isolation, truth, sample_times), encoding="utf-8")
    return path
