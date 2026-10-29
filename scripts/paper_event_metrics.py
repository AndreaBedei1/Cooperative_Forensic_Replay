#!/usr/bin/env python3
"""Derive phase-correct local-event scores from the committed campaign export.

This is a versioned paper-only derivation: neither reconstruction nor the original
``results/event_validation`` archive is changed. Both predictions and oracle events
are restricted to before the recorder's first contact BEFORE one-to-one matching.
Witnesses with no contact contribute their full recording. Duplicate predictions
count as false positives; non-evaluable predictions are reported and excluded.

    python scripts/paper_event_metrics.py

These are GT-assisted LOCAL event scores, not joint scores of the final global
event and its asserted identity. The export contains event STARTs, not a complete
samplewise assessment of initially active path occupancy. Original observability
flags and interval endpoints are retained. Incorrect last-second context is
recomputed before each participant recorder's FIRST contact, using canonical
contact times; witnesses have no such window. Wrong-vehicle or unsupported
intervals with positive-duration overlap count; duplicates alone do not. This
script does not recompute saved states, proximity, recovery or full active states.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import platform
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cdf.evaluation import event_validation as ev  # noqa: E402

DERIVATION_VERSION = "paper-local-events-v1"
JOB_FIELDS = ("job_family", "job_level", "job_recorder", "job_seed", "job_run")
MANUSCRIPT_CONDITIONS = (
    "G0", "G1", "G2", "radar nominal", "radar severe", "radar extreme",
    "one recorder severe", "one recorder extreme", "G2 + radar severe",
)
ORDER = MANUSCRIPT_CONDITIONS


def condition(row: Mapping[str, str]) -> str:
    """Use recorder, rather than radar, for the unit of asymmetric corruption."""
    family, level = row["job_family"], row["job_level"]
    subset = row.get("job_recorder") or ""
    prefix = ("all but one recorder " if "+" in subset else "one recorder ") if subset else "radar "
    if family == "baseline":
        return "G0"
    if family == "gnss":
        return {"rtk": "G1", "degraded": "G2"}[level]
    if family in ("radar_v3", "radar_asym"):
        return prefix + level
    if family not in ("radar_gnss_v3", "radar_asym_gnss"):
        raise ValueError("Unknown campaign family: " + family)
    gnss, radar = level.replace("gnss ", "").split(" + radar ")
    return {"rtk": "G1", "degraded": "G2"}[gnss] + " + " + prefix + radar


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value in ("True", "true", "1"):
        return True
    if value in ("False", "false", "0", "", None):
        return False
    raise ValueError("Invalid boolean: " + repr(value))


def _event(row: Mapping[str, Any]) -> Dict[str, Any]:
    """Discard earlier classification and duration fields before re-matching."""
    out = {k: row[k] for k in ("recorder", "family", "type", "phase")}
    out.update(subject=row.get("subject") or None, t_local=float(row["t_local"]),
               end=float(row["end"]), open_end=_bool(row.get("open_end")))
    if row["kind"] == "truth":
        out["observable"] = _bool(row.get("observable"))
    else:
        out["track"] = row.get("track", "")
        if row.get("class") == "not evaluable":
            out.update({"class": "not evaluable", "reason": row.get("reason", "")})
    return out


def rematch_before_contact(rows: Iterable[Mapping[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Re-match ONE job/recorder's pre-contact events, ignoring stale matches.

    Retaining witness ``no contact`` rows is intentional. Callers must never pool
    recorders or jobs before matching, even if their event types and times agree.
    """
    selected = [row for row in rows if row["phase"] != "after contact"]
    predictions = [_event(row) for row in selected if row["kind"] == "prediction"]
    truths = [_event(row) for row in selected if row["kind"] == "truth"]
    ev.classify(predictions, truths)
    lookup: Dict[Tuple[Any, ...], List[Dict[str, Any]]] = defaultdict(list)
    for t in truths:
        lookup[(t["type"], t["subject"], t["t_local"])].append(t)
    for p in predictions:
        if p["class"] != "correct":
            continue
        matching = lookup[(p["type"], p["subject"], p["truth_t"])]
        if len(matching) != 1:
            raise ValueError("Ambiguous true interval endpoint for a matched START")
        t = matching[0]
        p["onset_error_s"] = p["t_local"] - t["t_local"]
        if not p["open_end"] and not t["open_end"]:
            p["end_error_s"] = p["end"] - t["end"]
            p["duration_error_s"] = (p["end"] - p["t_local"]) - (t["end"] - t["t_local"])
        overlap = max(0.0, min(p["end"], t["end"]) - max(p["t_local"], t["t_local"]))
        union = max(p["end"], t["end"]) - min(p["t_local"], t["t_local"])
        p["overlap_iou"] = overlap / union if union > 0 else 1.0
    return predictions, truths


def _ratio(numerator: int, denominator: int) -> Optional[float]:
    return numerator / denominator if denominator else None


def _quantile(values: Sequence[float], q: float) -> Optional[float]:
    return float(np.percentile(values, q)) if values else None


def summarize(predictions: Sequence[Mapping[str, Any]], truths: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    n = Counter(p["class"] for p in predictions)
    tp = n["correct"]
    fp = n["wrong vehicle"] + n["unsupported"] + n["duplicate"]
    fn = sum(not t["matched"] for t in truths)
    observable = [t for t in truths if t["observable"]]
    observable_tp = sum(t["matched"] for t in observable)
    evaluable = len(predictions) - n["not evaluable"]
    assert tp + fn == len(truths), "True START accounting is inconsistent"
    assert tp + fp == evaluable, "Prediction accounting is inconsistent"
    assert tp == sum(t["matched"] for t in truths), "Matching is not one-to-one"
    onset = [abs(p["onset_error_s"]) for p in predictions if p["class"] == "correct"]
    overlap = [p["overlap_iou"] for p in predictions if p["class"] == "correct"]
    return {"predictions": len(predictions), "evaluable_predictions": evaluable,
            "tp": tp, "fp": fp, "duplicates": n["duplicate"], "wrong_vehicle": n["wrong vehicle"],
            "unsupported": n["unsupported"], "not_evaluable": n["not evaluable"],
            "phantom_false_predictions": sum(p["class"] in ("wrong vehicle", "unsupported", "duplicate")
                                               and p["subject"] is None for p in predictions),
            "truths": len(truths), "fn": fn, "observable_truths": len(observable),
            "observable_tp": observable_tp, "precision": _ratio(tp, evaluable),
            "recall": _ratio(tp, len(truths)), "observable_recall": _ratio(observable_tp, len(observable)),
            "matched_abs_onset_median_s": _quantile(onset, 50),
            "matched_abs_onset_p95_s": _quantile(onset, 95),
            "matched_interval_iou_median": _quantile(overlap, 50)}


def incorrect_first_contact_intervals(predictions: Sequence[Mapping[str, Any]], contact: Optional[float]) -> int:
    """Positive-duration overlap with [contact - 1, contact), never duplicates.

    An interval ending at the window start or starting exactly at impact does not
    occupy the pre-impact window. Zero-duration intervals are also excluded.
    """
    if contact is None:
        return 0
    return sum(p["class"] in ("wrong vehicle", "unsupported")
               and max(p["t_local"], contact - ev.IMMEDIATE_S) < min(p["end"], contact)
               for p in predictions)


def canonical_first_contacts(runs: Iterable[str]) -> Tuple[Dict[str, Dict[str, float]], Dict[str, str]]:
    """The campaign changes radar/GNSS only, so canonical contact times apply."""
    result: Dict[str, Dict[str, float]] = {}
    hashes = {}
    for run in sorted(set(runs)):
        rec = ROOT / "traces" / run / "reconstruction"
        path = rec / "evaluation/evaluation.json"
        collisions = json.loads(path.read_text())["collisions"]
        hashes[str(path.relative_to(ROOT))] = _sha(path)
        contacts = {}
        for graph_path in sorted(rec.glob("*/local_graph.json")):
            graph = json.loads(graph_path.read_text())
            recorder = graph_path.parent.name
            origin = graph["recorder"]["clock"]["origin_source_timestamp"]
            own = [float(c["sim_time"]) - origin for c in collisions if recorder in c["participants"]]
            if own:
                contacts[recorder] = round(min(own), 4)
            hashes[str(graph_path.relative_to(ROOT))] = _sha(graph_path)
        result[run] = contacts
    return result, hashes


def derive(rows: Iterable[Mapping[str, str]],
           first_contacts: Optional[Mapping[str, Mapping[str, float]]] = None) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[Tuple[str, ...], List[Mapping[str, str]]] = defaultdict(list)
    for row in rows:
        if row["kind"] not in ("prediction", "truth"):
            raise ValueError("Unknown event kind: " + row["kind"])
        if row["phase"] not in ("before contact", "after contact", "no contact"):
            raise ValueError("Unknown contact phase: " + row["phase"])
        grouped[tuple(row[k] for k in JOB_FIELDS) + (row["recorder"],)].append(row)
    by_condition: Dict[str, List[Tuple[Tuple[str, ...], List[Dict[str, Any]], List[Dict[str, Any]]]]] = defaultdict(list)
    job_rows = []
    for key, group in grouped.items():
        cond = condition(group[0])
        ps, ts = rematch_before_contact(group)
        by_condition[cond].append((key, ps, ts))
        contact = None if first_contacts is None else first_contacts[key[4]].get(key[-1])
        job_rows.append(dict(zip(JOB_FIELDS + ("recorder",), key), condition=cond,
                             first_contact_t_local=contact,
                             incorrect_first_contact_intervals=incorrect_first_contact_intervals(ps, contact),
                             **summarize(ps, ts)))
    pooled_rows, seed_rows = [], []
    families = list(ev.FAMILIES) + ["all"]
    ordered = sorted(by_condition, key=lambda c: (ORDER.index(c) if c in ORDER else len(ORDER), c))
    for cond in ordered:
        groups = by_condition[cond]
        for family in families:
            def select(subset):
                ps = [p for _, pp, _ in subset for p in pp if family == "all" or p["family"] == family]
                ts = [t for _, _, tt in subset for t in tt if family == "all" or t["family"] == family]
                summary = summarize(ps, ts)
                jobs = {key[:-1] for key, _, _ in subset}
                eligible, flagged = set(), set()
                if first_contacts is not None:
                    eligible = {job for job in jobs if first_contacts[job[4]]}
                    for key, pp, _ in subset:
                        contact = first_contacts[key[4]].get(key[-1])
                        local = [p for p in pp if family == "all" or p["family"] == family]
                        if incorrect_first_contact_intervals(local, contact):
                            flagged.add(key[:-1])
                summary.update(first_contact_context_jobs=len(eligible),
                               incorrect_first_contact_context_jobs=len(flagged),
                               incorrect_first_contact_context_rate=_ratio(len(flagged), len(eligible)))
                return summary
            pooled_rows.append({"condition": cond, "family": family,
                                "jobs": len({key[:-1] for key, _, _ in groups}), **select(groups)})
            for seed in sorted({key[3] for key, _, _ in groups}, key=int):
                subset = [item for item in groups if item[0][3] == seed]
                seed_rows.append({"condition": cond, "family": family, "seed": int(seed),
                                  "jobs": len({key[:-1] for key, _, _ in subset}), **select(subset)})
    return {"pooled": pooled_rows, "by_seed": seed_rows, "by_recorder": job_rows}


def _write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_results(source: Path, out: Path) -> Dict[str, Any]:
    with gzip.open(source, "rt", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    contacts, contact_hashes = canonical_first_contacts(row["job_run"] for row in rows)
    result = derive(rows, contacts)
    out.mkdir(parents=True, exist_ok=True)
    _write_csv(out / "event_metrics.csv", result["pooled"])
    _write_csv(out / "event_metrics_by_seed.csv", result["by_seed"])
    _write_csv(out / "event_metrics_by_recorder.csv", result["by_recorder"])
    jobs = {tuple(row[k] for k in JOB_FIELDS) for row in rows}
    families = Counter(key[0] for key in jobs)
    provenance_source = ROOT / "results/event_validation/provenance.json"
    provenance = {
        "derivation_version": DERIVATION_VERSION, "source": str(source.relative_to(ROOT)),
        "source_sha256": _sha(source), "original_analysis_provenance_sha256": _sha(provenance_source),
        "original_analysis_provenance": json.loads(provenance_source.read_text()),
        "script_sha256": _sha(Path(__file__)),
        "classifier_sha256": _sha(ROOT / "src/cdf/evaluation/event_validation.py"),
        "matcher_sha256": _sha(ROOT / "src/cdf/evaluation/event_oracle.py"),
        "python": platform.python_version(), "numpy": np.__version__, "source_rows": len(rows),
        "jobs": len(jobs), "jobs_by_family": dict(sorted(families.items())),
        "matching_window_s": ev.MATCH_WINDOW_S,
        "phase": "Filter both sides before matching; before contact plus whole logs of non-contact witnesses",
        "precision": "correct / all evaluable predictions; duplicates are false positives",
        "observable_recall": "matched observable true STARTs / observable true STARTs",
        "aggregation": "pooled ratios; per-seed ratios exported separately; no additional independent crash cases",
        "scope": "GT-assisted local START-event correspondence; not final global event-and-identity accuracy",
        "last_second_context": "A job is flagged if a wrong-vehicle or unsupported predicted interval has "
            "positive-duration overlap with [t_first_contact - 1, t_first_contact), for at least one contact "
            "participant recorder. Uses corrected pre-contact classes. Duplicate predictions alone do not flag "
            "context. Witnesses have no window. This differs from original all-contact replay summaries.",
        "canonical_contact_input_sha256": contact_hashes,
        "unchanged_analyses": ["saved states", "recovery", "proximity", "full samplewise active states"],
        "original_campaign_outputs_modified": False,
    }
    (out / "event_metrics_provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    lines = ["# Phase-correct local event metrics for the paper", "",
             "Reproduce with `python scripts/paper_event_metrics.py`.", "",
             "Both sides are restricted before one-to-one matching. Duplicate predictions count as false positives. "
             "Whole recordings from non-contact witnesses are retained. These are pooled local-event scores using "
             "the original GT-assisted physical correspondence, not a new global attribution score.", "",
             "Last-second context flags jobs with a wrong-vehicle/unsupported interval occupying part of the "
             "second before a participant recorder's first contact. Duplicates alone do not flag context. "
             "Boundary-only intersection is excluded. This differs from the archived all-contact summary.", "",
             "| Condition | Jobs | Predictions | TP | FP | Duplicates | True STARTs | FN | Observable TP/true | Precision | Observable recall | First-contact last-second flags |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for row in result["pooled"]:
        if row["family"] != "all":
            continue
        lines.append("| {condition} | {jobs} | {predictions} | {tp} | {fp} | {duplicates} | {truths} | {fn} | "
                     "{observable_tp}/{observable_truths} | {precision:.6f} | {observable_recall:.6f} | "
                     "{incorrect_first_contact_context_jobs}/{first_contact_context_jobs} |".format(**row))
    lines += ["", "Every recorder/job and every pooled row passes TP + FN = true STARTs and TP + FP = evaluable predictions.",
              "Original campaign outputs and their provenance remain unchanged. This derivation does not repair or replace "
              "the separate recovery, proximity, initial active-state, or state-error analyses.", ""]
    (out / "event_metrics.md").write_text("\n".join(lines), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "results/event_validation/events.csv.gz")
    parser.add_argument("--out", type=Path, default=ROOT / "results/paper_evaluation")
    args = parser.parse_args()
    result = write_results(args.source.resolve(), args.out)
    for row in result["pooled"]:
        if row["family"] == "all" and row["condition"] in MANUSCRIPT_CONDITIONS:
            print("{condition}: jobs={jobs} TP={tp} FP={fp} FN={fn} P={precision:.6f} R_obs={observable_recall:.6f} "
                  "Last1s={incorrect_first_contact_context_jobs}/{first_contact_context_jobs} "
                  "({incorrect_first_contact_context_rate:.6f}) "
                  "onset_median={matched_abs_onset_median_s:.3f}s IoU_median={matched_interval_iou_median:.3f}".format(**row))


if __name__ == "__main__":
    main()
