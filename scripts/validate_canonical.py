#!/usr/bin/env python3
"""Automatic acceptance check of the canonical development set (run after the reconstruction and evaluation).

    python scripts/validate_canonical.py [--out docs/CANONICAL_VALIDATION.md]

Checks the manifest (S01..S19, 22 runs, no gaps, no stray folders), then per run: reconstruction files present
and finite (no NaN/Inf in any JSON), made with the current ``configs/reconstruction.yaml`` (the configuration
recorded in ``global_graph.json``; anything else is a stale output), every recorder aligned, collisions reconstructed (evaluation), no wrong
collision pairing, no wrong recorder link, no false merge, no global CRITICAL_TTC episode of a colliding pair
after its contact while touching, replay loading (global clock, boxes, events) and the standard replay panels
(the recorder's current state above its recent events, no '?', no PREDICTED, at most the panel line limit
plus '... +N more', no repeated subject, no recent event lost unless the panel is truncated) and the viewer's
recorder panels (``recorder_panel``: at most ``MAX_STATE_LINES`` states plus '... +N more', the latest
``MAX_EVENT_LINES`` events newest first and none dropped, no '?', UNKNOWN or PREDICTED); the
last two groups are the semantic anomalies, with the semantic stability of every recorder's local trace (no
reconstruction output needs ground truth for it): no EGO_PATH_ENTRY / EXIT of one subject undone within
``OSCILLATION_S`` (three radar sweeps: no manoeuvre does that), no CUT_IN without the EGO_PATH_ENTRY of its
subject that confirms it.  The privileged stability audit (``scripts/stability_audit.py``, ground truth through
``evaluation/stability.json``) adds warnings: phantom tracks, track losses while the radar kept measuring the
body (fragmentation), simultaneous duplicate tracks of one body, CUT_IN events without a true cut-in or true
cut-ins not reported, and EGO_PATH oscillations per true road user (a failure).  Unresolved identities: tracks whose identity decision the
reconstruction itself left UNRESOLVED (``unresolved_tracks``; no ground truth).  Ground truth is read only through the
evaluation files.  Exit status 1 on any FAIL.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cdf.reconstruction.config import load_config  # noqa: E402
from cdf.replay.model import ReplayRun  # noqa: E402
from cdf.replay.presentation import (EVENT, MAX_EVENT_LINES, MAX_PANEL_LINES, MAX_STATE_LINES, MORE,  # noqa: E402
                                     recorder_panel, standard_panel_lines)

CANONICAL = {
    "S01": ["crash"], "S02": ["crash"], "S03": ["crash"],
    "S04": ["a_front_pushed", "b_rear_first"], "S05": ["crash"], "S06": ["crash"], "S07": ["merge_conflict"],
    "S08": ["rolls_through"], "S09": ["near_simultaneous"], "S10": ["deflected_into_c"], "S11": ["consequential"],
    "S12": ["crash"], "S13": ["abreast", "platoon", "passing"], "S14": ["surrounded"], "S15": ["dense_platoon"],
    "S16": ["overtaking"], "S17": ["occlusion_reappearance"], "S18": ["collision_ambiguity"],
    "S19": ["highway_curve"],
}
OSCILLATION_S = 0.15  # an EGO_PATH change undone within three 20 Hz radar sweeps
SET_NAME = "S01..{0}".format(max(CANONICAL))


def canonical_runs():
    return [ROOT / "traces" / sid / ("run_0_" + variant) for sid in sorted(CANONICAL) for variant in CANONICAL[sid]]


def _finite(value):
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(_finite(v) for v in value.values())
    if isinstance(value, list):
        return all(_finite(v) for v in value)
    return True


def manifest_problems():
    problems = []
    ids = sorted(p.name for p in (ROOT / "traces").iterdir() if p.is_dir())
    if ids != sorted(CANONICAL):
        problems.append("scenario folders are not exactly {0}: {1}".format(SET_NAME, ids))
    found = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "traces").glob("S*/run_*"))
    expected = sorted(p.relative_to(ROOT).as_posix() for p in canonical_runs())
    if found != expected:
        problems.append("run folders differ from the canonical set: extra {0}, missing {1}".format(
            sorted(set(found) - set(expected)), sorted(set(expected) - set(found))))
    configs = sorted(p.name.split("_")[0].upper() for p in (ROOT / "configs/scenarios").glob("*.yaml"))
    if configs != sorted(CANONICAL):
        problems.append("scenario configs are not exactly {0}: {1}".format(SET_NAME, configs))
    return problems


def config_digest(config) -> str:
    return hashlib.sha256(json.dumps(config, sort_keys=True).encode("utf-8")).hexdigest()[:12]


def current_config():
    """The current configuration as a run records it (JSON: tuples become lists)."""
    return json.loads(json.dumps(load_config().to_dict()))


def unresolved_tracks(rec: Path) -> set:
    """Tracks whose identity the reconstruction left UNRESOLVED: a recorder link or a road-user link refused as
    UNRESOLVED, or an earlier entity a retrospective test could not resolve (reconstruction files only)."""
    out = set()
    for a in json.loads((rec / "global/associations.json").read_text(encoding="utf-8")):
        if any("UNRESOLVED" in text for text in a.get("evidence", []) + a.get("blocking", [])):
            out.add(a["local_graph"] + ":" + a["local_track"])
    entities = json.loads((rec / "global/anonymous_entities.json").read_text(encoding="utf-8"))
    for e in entities.get("association_evidence", []):
        if (e.get("refused") or "").startswith("UNRESOLVED"):
            out.update((e["a"], e["b"]))
    for d in entities.get("retrospective") or []:
        if not d.get("resolved"):
            out.update(d.get("earlier") or [])
    return out


def semantic_stability(rec: Path) -> list:
    """Problems of the recorders' local traces (reconstruction outputs only): an EGO_PATH_ENTRY / EXIT of one
    subject undone within ``OSCILLATION_S``, a CUT_IN whose subject never enters the path during it."""
    problems = []
    for graph_path in sorted(rec.glob("*/local_graph.json")):
        owner = graph_path.parent.name
        nodes = json.loads(graph_path.read_text(encoding="utf-8"))["nodes"]
        path = {}
        for n in nodes:
            if n["event_type"] in ("EGO_PATH_ENTRY", "EGO_PATH_EXIT"):
                path.setdefault(n["subject_id"], []).append((n["t_local"], n["event_type"]))
        for subject, events in path.items():
            events.sort()
            for (t0, e0), (t1, e1) in zip(events, events[1:]):
                if e0 != e1 and t1 - t0 <= OSCILLATION_S + 1e-6:
                    problems.append("{0}: EGO_PATH of {1} undone within {2:.2f} s at {3:.2f}".format(
                        owner, subject, t1 - t0, t0))
        for side in ("LEFT", "RIGHT"):
            starts = sorted((n["t_local"], n["subject_id"]) for n in nodes if n["event_type"] == "CUT_IN_FROM_" + side + "_START")
            ends = sorted((n["t_local"], n["subject_id"]) for n in nodes if n["event_type"] == "CUT_IN_FROM_" + side + "_END")
            for start, subject in starts:
                end = next((t for t, s in ends if s == subject and t >= start), None)
                if not any(t >= start - 1e-6 and (end is None or t <= end + 1e-6) for t, e in path.get(subject, [])
                           if e == "EGO_PATH_ENTRY"):
                    problems.append("{0}: CUT_IN of {1} at {2:.2f} without its EGO_PATH_ENTRY".format(owner, subject, start))
    return problems


def stability_warnings(rec: Path, info: dict) -> tuple:
    """(failures, warnings) of the privileged stability audit of this run (``evaluation/stability.json``, written by
    ``scripts/stability_audit.py``; absent: nothing to report)."""
    path = rec / "evaluation" / "stability.json"
    if not path.exists():
        info["stability"] = "-"
        return [], ["no stability audit (evaluation/stability.json)"]
    audit = json.loads(path.read_text(encoding="utf-8"))
    fails, warns = [], []
    oscillations = phantoms = fragmentation = duplicates = 0
    for owner, recorder in sorted(audit.get("recorders", {}).items()):
        tracks = recorder.get("tracks", {})
        phantoms += len(tracks.get("phantoms", []))
        fragmentation += sum(1 for loss in tracks.get("losses", []) if loss.get("kind") == "fragmentation")
        duplicates += len(tracks.get("duplicates", []))
        oscillations += sum(v.get("oscillations", 0) for v in (recorder.get("ego_path") or {}).values())
    cut_in = audit.get("cut_in") or {}
    info["stability"] = "{0}/{1}/{2}/{3}".format(oscillations, phantoms, fragmentation, duplicates)
    info["cut_in"] = "{0}/{1}/{2}".format(cut_in.get("tp", 0), len(cut_in.get("fp", [])), len(cut_in.get("missed", [])))
    if oscillations:
        fails.append("{0} EGO_PATH oscillation(s) per true road user".format(oscillations))
    if phantoms:
        warns.append("{0} phantom track(s)".format(phantoms))
    if fragmentation:
        warns.append("{0} track loss(es) while the radar kept measuring the body".format(fragmentation))
    if duplicates:
        warns.append("{0} simultaneous duplicate track(s)".format(duplicates))
    if cut_in.get("fp"):
        warns.append("CUT_IN without a true cut-in: {0}".format(cut_in["fp"]))
    if cut_in.get("missed"):
        warns.append("true cut-in not reported: {0}".format(cut_in["missed"]))
    return fails, warns


def check_run(run: Path):
    fails, warns, info = [], [], {"semantic": 0}
    rec = run / "reconstruction"
    for name in ("global/global_graph.json", "global/alignment.json", "global/associations.json",
                 "global/anonymous_entities.json", "evaluation/evaluation.json"):
        if not (rec / name).exists():
            fails.append("missing " + name)
    if fails:
        return fails, warns, info
    for path in rec.rglob("*.json"):
        if not _finite(json.loads(path.read_text(encoding="utf-8"))):
            fails.append("non-finite number in " + path.relative_to(rec).as_posix())
    graph = json.loads((rec / "global/global_graph.json").read_text(encoding="utf-8"))
    if graph.get("reconstruction_config") != current_config():
        fails.append("stale reconstruction: made with configuration {0}, not the current {1}".format(
            config_digest(graph.get("reconstruction_config")), config_digest(current_config())))
    info["unresolved"] = len(unresolved_tracks(rec))
    alignment = json.loads((rec / "global/alignment.json").read_text(encoding="utf-8"))
    unaligned = [g for g, c in alignment["graphs"].items() if c["status"] != "ALIGNED"]
    if unaligned:
        warns.append("recorders not aligned: {0}".format(unaligned))
    fusion = json.loads((rec / "evaluation/fusion_metrics.json").read_text(encoding="utf-8"))
    evaluation = json.loads((rec / "evaluation/evaluation.json").read_text(encoding="utf-8"))
    collisions = evaluation.get("collisions", [])
    lost = [c for c in collisions if c.get("reconstructed_as") is None]
    info["collisions"] = "{0}/{1}".format(len(collisions) - len(lost), len(collisions))
    if lost:
        warns.append("{0} vehicle contact(s) not reconstructed".format(len(lost)))
    wrong_pairs = [c for c in collisions if c.get("reconstructed_as") is not None and c.get("participants_correct") is False]
    if wrong_pairs or evaluation.get("extra_collisions"):
        fails.append("wrong collision pairing ({0} wrong, {1} reconstructed without a contact)".format(
            len(wrong_pairs), len(evaluation.get("extra_collisions") or [])))
    verdicts = {}
    for d in fusion.get("track_decisions", []):
        key = d["verdict"].split(" (")[0]
        verdicts[key] = verdicts.get(key, 0) + 1
    info["links"] = verdicts
    if any(k.lower().startswith("wrong") for k in verdicts):
        fails.append("wrong recorder link / identity: {0}".format({k: v for k, v in verdicts.items() if k.lower().startswith("wrong")}))
    if verdicts.get("missed link"):
        warns.append("{0} missed recorder link(s) (a track of a recorder left anonymous)".format(verdicts["missed link"]))
    merges = fusion.get("merges", {})
    info["merges"] = merges
    if merges.get("false", 0):
        fails.append("{0} false merge(s)".format(merges["false"]))
    if merges.get("missed", 0):
        warns.append("{0} missed merge(s) (unresolved identities, conservative)".format(merges["missed"]))
    for c in (n for n in graph["nodes"] if n["event_type"] == "COLLISION" and n.get("participants")):
        late = [n for n in graph["nodes"] if n["event_type"] == "CRITICAL_TTC_START" and n.get("t_global") is not None
                and n["t_global"] > c["t_global"] and {n["actor_id"], n["subject_id"]} == set(c["participants"])]
        if late:
            fails.append("global CRITICAL_TTC of {0} after their contact".format(c["participants"]))
            info["semantic"] += 1
    unstable = semantic_stability(rec)
    if unstable:
        fails.append("semantic instability: " + "; ".join(unstable[:4]) + ("; ..." if len(unstable) > 4 else ""))
        info["semantic"] += len(unstable)
    audit_fails, audit_warns = stability_warnings(rec, info)
    fails += audit_fails
    warns += audit_warns
    try:
        replay = ReplayRun.load(run)
    except Exception as exc:  # reported, never hidden
        fails.append("replay does not load: {0!r}".format(exc))
        return fails, warns, info
    if replay.clock != "t_global":
        fails.append("replay not on the global clock")
    steps = [k * 0.1 for k in range(int(replay.duration / 0.1) + 1)]
    info["boxes_max"] = max(len(replay.entities_at(t)) for t in steps)
    info["events"] = len(replay.display_events())
    for t in steps:
        for p in replay.participants:
            lines = standard_panel_lines(replay, p.participant_id, t, 1.0)
            texts = [text for text, _ in lines]
            too_many = len(lines) > MAX_PANEL_LINES + 1 or (len(lines) == MAX_PANEL_LINES + 1 and lines[-1][1] != MORE)
            if too_many or any("?" in x or "PREDICTED" in x for x in texts):
                fails.append("panel rule broken at t={0:.1f} ({1})".format(t, p.participant_id))
                info["semantic"] += 1
                break
            subjects = [text.split(":")[0] for text, kind in lines if kind not in (EVENT, MORE)]
            if len(subjects) != len(set(subjects)):
                fails.append("a global subject repeated in a panel at t={0:.1f}".format(t))
                info["semantic"] += 1
            kinds = [kind for _, kind in lines if kind != MORE]
            if EVENT in kinds and any(kind != EVENT for kind in kinds[kinds.index(EVENT):]):
                fails.append("a state listed below the recent events at t={0:.1f}".format(t))
                info["semantic"] += 1
            recent = replay.recent_events(p.participant_id, t, 1.0)
            if (not lines or lines[-1][1] != MORE) and kinds.count(EVENT) != len(recent):
                fails.append("a recent event hidden at t={0:.1f}".format(t))
                info["semantic"] += 1
            panel = recorder_panel(replay, p.participant_id, t)
            texts = [text for text, _ in panel.states + panel.events]
            ages = [float(text.split(" s ")[0]) for text, _ in panel.events]
            if (len(panel.states) > MAX_STATE_LINES + 1
                    or (len(panel.states) == MAX_STATE_LINES + 1 and panel.states[-1][1] != MORE)
                    or len(panel.events) != min(panel.events_total, MAX_EVENT_LINES)
                    or any(b > a + 1e-9 for a, b in zip(ages, ages[1:]))
                    or any("?" in x or "UNKNOWN" in x or "PREDICTED" in x for x in texts)):
                fails.append("recorder panel rule broken at t={0:.1f} ({1})".format(t, p.participant_id))
                info["semantic"] += 1
        if fails:
            break
    return fails, warns, info


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    lines = ["# Canonical development set: automatic validation", ""]
    problems = manifest_problems()
    lines.append("Manifest: " + ("OK ({0}, {1} runs)".format(SET_NAME, len(canonical_runs())) if not problems else "FAIL: " + "; ".join(problems)))
    lines += ["", "Reconstruction: the single reconstruction method, `configs/reconstruction.yaml` (configuration digest "
              "{0}); every run is checked to carry exactly this configuration.".format(config_digest(current_config()))]
    lines += ["", "Stability (privileged audit, `evaluation/stability.json`): EGO_PATH oscillations / phantom tracks / "
              "fragmentation losses / duplicate tracks; CUT_IN: true positives / without a true cut-in / missed.", "",
              "| run | status | collisions | recorder/identity decisions | merges (correct/false/missed) | unresolved identities | semantic anomalies | stability (osc/phantom/frag/dup) | CUT_IN (TP/FP/missed) | boxes (max at once) | events | warnings / failures |",
              "|---|---|---|---|---|--:|--:|---|---|--:|--:|---|"]
    failed = bool(problems)
    for run in canonical_runs():
        fails, warns, info = check_run(run)
        status = "FAIL" if fails else ("WARN" if warns else "PASS")
        failed |= bool(fails)
        merges = info.get("merges", {})
        lines.append("| {0} | {1} | {2} | {3} | {4}/{5}/{6} | {10} | {11} | {12} | {13} | {7} | {8} | {9} |".format(
            run.relative_to(ROOT / "traces").as_posix(), status, info.get("collisions", "-"),
            ", ".join("{0} {1}".format(k, v) for k, v in sorted(info.get("links", {}).items())),
            merges.get("correct", 0), merges.get("false", 0), merges.get("missed", 0), info.get("boxes_max", "-"),
            info.get("events", "-"), "; ".join(["FAIL: " + f for f in fails] + ["WARN: " + w for w in warns]) or "-",
            info.get("unresolved", "-"), info.get("semantic", "-"), info.get("stability", "-"), info.get("cut_in", "-")))
    text = "\n".join(lines) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    print(text)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
