#!/usr/bin/env python3
"""Event validation of campaign v3 jobs (docs/EVENT_VALIDATION.md): per-job analysis, then tables and figures.

    python scripts/event_validation.py --kept F:/CarlaGraph_v3_kept --out results/event_validation --workers 20

``--kept`` holds the jobs regenerated with their outputs (``scripts/regenerate_campaign_jobs.py``,
``regenerated.jsonl``); only jobs whose scorecard is identical to the campaign's are analysed.  The truth of a run is
computed once, from the canonical recording (``traces/``).  Per-job results go to ``<out>/jobs/``; a second call
reuses them (``--aggregate-only`` skips the analysis).
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import subprocess
import sys
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cdf.evaluation import event_validation as ev  # noqa: E402

LEVELS = ("none", "nominal", "severe", "extreme")
INCORRECT = ("wrong vehicle", "unsupported")


def _name(run: str) -> str:
    return run.replace("/", "__")


def job_id(line: Mapping[str, Any]) -> str:
    rec = "_" + line["recorder"] if line.get("recorder") else ""
    return "{0}_{1}{2}_seed{3}__{4}".format(line["family"], line["level"].replace(" ", "_").replace("+", "and"), rec,
                                           line["seed"], _name(line["run"]))


# ----------------------------------------------------------------------------------------------------------------
# per run and per job (worker processes)
# ----------------------------------------------------------------------------------------------------------------

def truth_task(run: str, out: str) -> str:
    target = Path(out) / "truth" / (_name(run) + ".json")
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(ev.truth_intervals(ROOT / "traces" / run)), encoding="utf-8")
    return run


def job_task(line: Dict[str, Any], out: str) -> str:
    out_dir = Path(out) / "jobs"
    name = job_id(line)
    target = out_dir / (name + ".json.gz")
    if target.exists():
        return name
    truth = json.loads((Path(out) / "truth" / (_name(line["run"]) + ".json")).read_text(encoding="utf-8"))
    result = ev.analyse(Path(line["kept"]), truth)
    states = result.pop("states")
    np.savez_compressed(str(out_dir / (name + "_states.npz")), **states)
    result["states_summary"] = {k: _stats(v) for k, v in states.items()}
    result["job"] = {k: line.get(k) for k in ("family", "level", "recorder", "seed", "run", "kept")}
    text = json.dumps(result)  # serialised first: a failure leaves no partial file behind
    partial = target.with_name(target.name + ".partial")
    with gzip.open(str(partial), "wt", encoding="utf-8") as handle:
        handle.write(text)
    partial.replace(target)
    return name


def _stats(values: np.ndarray) -> Dict[str, Any]:
    if not len(values):
        return {"n": 0}
    return {"n": int(len(values)), "median": float(np.median(values)), "p95": float(np.percentile(values, 95)),
            "within_1_5m": float(np.mean(values <= ev.IDENTITY_M))}


# ----------------------------------------------------------------------------------------------------------------
# aggregation
# ----------------------------------------------------------------------------------------------------------------

GNSS_NAME = {"rtk": "G1", "degraded": "G2"}
ORDER = ["G0", "G1", "G2", "radar nominal", "radar severe", "radar extreme",
         "one radar nominal", "one radar severe", "one radar extreme",
         "all but one radar nominal", "all but one radar severe", "all but one radar extreme",
         "G1 + radar nominal", "G1 + radar severe", "G2 + radar nominal", "G2 + radar severe",
         "G2 + one radar nominal", "G2 + one radar severe", "G2 + all but one radar nominal",
         "G2 + all but one radar severe"]


def condition(job: Mapping[str, Any]) -> str:
    family, level = job["family"], str(job["level"])
    subset = ("one " if "+" not in str(job.get("recorder") or "") else "all but one ") if job.get("recorder") else ""
    if family == "baseline":
        return "G0"
    if family == "gnss":
        return GNSS_NAME.get(level, level)
    if family in ("radar_v3", "radar_asym"):
        return "{0}radar {1}".format(subset, level)
    gnss, radar = level.replace("gnss ", "").split(" + radar ")
    return "{0} + {1}radar {2}".format(GNSS_NAME.get(gnss, gnss), subset, radar)


def _ratio(a: float, b: float) -> Optional[float]:
    return round(a / b, 4) if b else None


def _pct(values: Sequence[float], q: float) -> Optional[float]:
    return round(float(np.percentile(values, q)), 3) if len(values) else None


def aggregate(results: List[Dict[str, Any]], out: Path, states_dir: Path) -> Dict[str, List[Dict[str, Any]]]:
    by = defaultdict(list)
    for r in results:
        by[condition(r["job"])].append(r)
    conditions = sorted(by, key=lambda c: ORDER.index(c) if c in ORDER else len(ORDER))
    tables: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for cond in conditions:
        jobs = by[cond]
        # A. events per family (before contact, and every phase)
        for phase in ("before contact", "all"):
            for family in list(ev.FAMILIES) + ["all"]:
                preds = [p for j in jobs for p in j["predictions"]
                         if (family == "all" or p["family"] == family) and (phase == "all" or p["phase"] != "after contact")]
                truths = [t for j in jobs for t in j["truths"]
                          if (family == "all" or t["family"] == family) and (phase == "all" or t["phase"] != "after contact")]
                n = Counter(p["class"] for p in preds)
                tp, fp = n["correct"], n["wrong vehicle"] + n["unsupported"]
                fn = sum(not t["matched"] for t in truths)
                obs = [t for t in truths if t["observable"]]
                tables["events"].append({
                    "condition": cond, "phase": phase, "family": family, "jobs": len(jobs), "predictions": len(preds),
                    "TP": tp, "FP": fp, "FP_wrong_vehicle": n["wrong vehicle"], "FP_unsupported": n["unsupported"],
                    "FP_subject_phantom": sum(p["class"] in INCORRECT and p["subject"] is None for p in preds),
                    "duplicates": n["duplicate"], "not_evaluable": n["not evaluable"], "FN": fn,
                    "true_events": len(truths), "true_observable": len(obs),
                    "FN_observable": sum(not t["matched"] for t in obs),
                    "precision": _ratio(tp, tp + fp), "recall": _ratio(tp, tp + fn),
                    "recall_observable": _ratio(sum(t["matched"] for t in obs), len(obs))})
        # B. durations of the matched events
        for family in list(ev.FAMILIES) + ["all"]:
            matched = [p for j in jobs for p in j["predictions"] if p["class"] == "correct"
                       and (family == "all" or p["family"] == family) and p["phase"] != "after contact"]
            onset = [abs(p["onset_error_s"]) for p in matched]
            duration = [abs(p["duration_error_s"]) for p in matched if p.get("duration_error_s") is not None]
            iou = [p["overlap_iou"] for p in matched if p.get("overlap_iou") is not None]
            tables["durations"].append({
                "condition": cond, "family": family, "matched": len(matched),
                "onset_abs_median_s": _pct(onset, 50), "onset_abs_p95_s": _pct(onset, 95),
                "closed_pairs": len(duration), "duration_abs_median_s": _pct(duration, 50),
                "duration_abs_p95_s": _pct(duration, 95), "iou_median": _pct(iou, 50), "iou_p5": _pct(iou, 5)})
        # C. active-state time
        rec = [v for j in jobs for v in j["active"]["recorders"].values()]
        n, n_pre = sum(v["n"] for v in rec), sum(v["n_pre_contact"] for v in rec)
        tables["time"].append({
            "condition": cond, "recorder_seconds": round(n * ev.GRID_S, 1),
            "spurious_pct": _ratio(100 * sum(v["spurious"] for v in rec), n),
            "spurious_phantom_pct": _ratio(100 * sum(v["spurious_phantom"] for v in rec), n),
            "missing_pct": _ratio(100 * sum(v["missing"] for v in rec), n),
            "incorrect_pct": _ratio(100 * sum(v["incorrect"] for v in rec), n),
            "pre_contact_seconds": round(n_pre * ev.GRID_S, 1),
            "incorrect_pre_pct": _ratio(100 * sum(v["incorrect_pre"] for v in rec), n_pre),
            "spurious_pre_pct": _ratio(100 * sum(v["spurious_pre"] for v in rec), n_pre),
            "missing_pre_pct": _ratio(100 * sum(v["missing_pre"] for v in rec), n_pre)})
        # D. replays
        rows = [replay_row(j) for j in jobs]
        tables["replays"] += rows
        k = len(rows)
        tables["replay_summary"].append({
            "condition": cond, "replays": k,
            "incorrect_context_pct": _ratio(100 * sum(r["incorrect_events"] > 0 for r in rows), k),
            "incorrect_context_before_contact_pct": _ratio(100 * sum(r["incorrect_events_before_contact"] > 0 for r in rows), k),
            "incorrect_context_immediately_before_contact_pct": _ratio(100 * sum(r["incorrect_active_last_second"] > 0 for r in rows), k),
            "of_which_phantom_pct": _ratio(100 * sum(r["incorrect_active_last_second_phantom"] > 0 for r in rows), k),
            "phantom_within_2m_at_impact_pct": _ratio(100 * sum(r["phantoms_at_impact_<=2m"] > 0 for r in rows), k),
            "phantom_within_5m_at_impact_pct": _ratio(100 * sum(r["phantoms_at_impact_<=5m"] > 0 for r in rows), k)})
        # E. saved states (pooled raw values)
        pooled: Dict[str, List[np.ndarray]] = defaultdict(list)
        for j in jobs:
            with np.load(str(states_dir / (job_id(j["job"]) + "_states.npz"))) as data:
                for key in data.files:
                    pooled[key].append(data[key])
        for key in ("track_measured", "track_predicted", "entity_measured", "entity_predicted"):
            values = np.concatenate(pooled[key]) if pooled[key] else np.array([])
            row = {"condition": cond, "states": key}
            row.update(_stats(values))
            tables["states"].append(row)
        # F. relevance (participants)
        rel = [x for j in jobs for x in j["relevance"] if x["role"] == "participant"]
        observable = [x for x in rel if x["observable_true_warning_about_partner"]]
        tables["relevance"].append({
            "condition": cond, "contact_sides": len(rel),
            "participants_correct_pct": _ratio(100 * sum(bool(x["participants_correct"]) for x in rel), len(rel)),
            "sides_with_true_warning": sum(bool(x["true_warning_about_partner"]) for x in rel),
            "sides_with_observable_true_warning": len(observable),
            "correct_warning_given_observable_pct": _ratio(
                100 * sum(bool(x["correct_warning_about_partner"]) for x in observable), len(observable)),
            "correct_warning_all_sides_pct": _ratio(100 * sum(bool(x["correct_warning_about_partner"]) for x in rel), len(rel)),
            "incorrect_events_in_8s_per_side": _ratio(sum(x["events_wrong_vehicle"] + x["events_unsupported"] for x in rel), len(rel)),
            "sides_with_incorrect_event_about_pair_pct": _ratio(100 * sum(x["incorrect_about_pair"] > 0 for x in rel), len(rel)),
            "partner_tracked_before_impact_pct": _ratio(100 * sum(bool(x["partner_tracked_before_impact"]) for x in rel), len(rel))})
        # G. proximity at impact, by kind and bin (per contact)
        contacts = sum(len(j["contacts"]) for j in jobs)
        kinds = ["phantom", "ghost of a colliding recorder", "ghost of another recorder", "other vehicle"]
        if any(x["kind"] == "colliding vehicle" for j in jobs for x in j["proximity"]):
            kinds.append("colliding vehicle")  # a collision with a non-recording vehicle (none in the 22 runs)
        for kind in kinds:
            prox = [x for j in jobs for x in j["proximity"] if x["kind"] == kind]
            bins = Counter(x["bin_at_impact"] for x in prox)
            row = {"condition": cond, "kind": kind, "contacts": contacts, "entities": len(prox)}
            for label, _ in ev.BINS:
                row["at_impact " + label] = bins[label]
            row["absent at impact"] = bins["absent"]
            row["within_5m_in_8s_before"] = sum(x["within_5m_in_8s_before"] for x in prox)
            row["with_incorrect_event"] = sum(x["incorrect_event"] for x in prox)
            row["with_incorrect_event_within_5m_at_impact"] = sum(
                x["incorrect_event"] and x["clearance_at_impact_m"] is not None and x["clearance_at_impact_m"] <= 5.0
                for x in prox)
            tables["proximity"].append(row)
        # H. recovery
        recs = [x for j in jobs for x in j["recovery"]]
        for zone in ev.ZONES_M:
            col = "zone_{0:g}m".format(zone)
            counts = Counter(x[col] for x in recs)
            tables["recovery"].append({"condition": cond, "zone": "<= {0:g} m".format(zone), "tracks": len(recs),
                                       "pair within the zone from the start": sum(bool(x[col + "_from_start"]) for x in recs),
                                       **counts})
        tables["recovery_association"].append({"condition": cond, "tracks": len(recs),
                                               **Counter(x["association"] for x in recs)})
        # I. phantoms
        phantom_fp = sum(p["class"] in INCORRECT and p["subject"] is None for j in jobs for p in j["predictions"]
                         if p["phase"] != "after contact")
        all_fp = sum(p["class"] in INCORRECT for j in jobs for p in j["predictions"] if p["phase"] != "after contact")
        prox_ph = [x for j in jobs for x in j["proximity"] if x["kind"] == "phantom"]
        tables["phantoms"].append({
            "condition": cond, "jobs": len(jobs), "phantoms_per_job": _ratio(sum(j["phantom_entities"] for j in jobs), len(jobs)),
            "contacts": contacts,
            "phantoms_at_impact_per_contact": _ratio(sum(x["bin_at_impact"] != "absent" for x in prox_ph), contacts),
            "phantoms_<=5m_at_impact_per_contact": _ratio(sum(x["clearance_at_impact_m"] is not None and x["clearance_at_impact_m"] <= 5.0 for x in prox_ph), contacts),
            "phantoms_<=2m_at_impact_per_contact": _ratio(sum(x["clearance_at_impact_m"] is not None and x["clearance_at_impact_m"] <= 2.0 for x in prox_ph), contacts),
            "phantoms_within_5m_in_8s_before_per_contact": _ratio(sum(x["within_5m_in_8s_before"] for x in prox_ph), contacts),
            "incorrect_events_before_contact": all_fp, "of_which_phantom_subject": phantom_fp,
            "phantom_share_of_incorrect_events": _ratio(phantom_fp, all_fp)})
    tables["by_degraded_radars"] = by_degraded_radars(results)
    return tables


def degraded(job: Mapping[str, Any], recorders: Sequence[str]) -> List[str]:
    """The recorders whose radar the job degrades."""
    if job["family"] in ("baseline", "gnss"):
        return []
    if job.get("recorder"):
        return str(job["recorder"]).split("+")
    return list(recorders)


def by_degraded_radars(results: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    """Per GNSS, radar level, number of recorders of the run and number of degraded radars (the same runs compared):
    false events and who raised them (a recorder with a degraded radar or with an intact one), phantoms near the
    impact, incorrect context in the last second before a contact."""
    groups: Dict[tuple, List[Mapping[str, Any]]] = defaultdict(list)
    for r in results:
        job = r["job"]
        if job["family"] == "baseline" or job["family"] == "gnss":
            continue
        recorders = sorted({x["recorder"] for x in r["relevance"]})
        bad = degraded(job, recorders)
        level = str(job["level"])
        gnss = "G0" if "gnss" not in level else GNSS_NAME.get(level.split(" + ")[0].replace("gnss ", ""), "?")
        radar = level.split("radar ")[-1]
        n = "all" if len(bad) == len(recorders) else str(len(bad))
        groups[(gnss, radar, len(recorders), n)].append(dict(r, _bad=bad))
    rows = []
    for (gnss, radar, nrec, n), jobs in sorted(groups.items(), key=lambda kv: (kv[0][0], LEVELS.index(kv[0][1]) if kv[0][1] in LEVELS else 9,
                                                                              kv[0][2], kv[0][3])):
        preds = [dict(p, _bad=p["recorder"] in j["_bad"]) for j in jobs for p in j["predictions"] if p["phase"] != "after contact"]
        wrong = [p for p in preds if p["class"] in INCORRECT]
        tp = sum(p["class"] == "correct" for p in preds)
        contacts = sum(len(j["contacts"]) for j in jobs)
        prox = [x for j in jobs for x in j["proximity"] if x["kind"] == "phantom"]
        rows.append({
            "gnss": gnss, "radar": radar, "recorders_in_run": nrec, "degraded_radars": n, "jobs": len(jobs),
            "contacts": contacts, "TP": tp, "FP": len(wrong), "precision": _ratio(tp, tp + len(wrong)),
            "FP_per_job": _ratio(len(wrong), len(jobs)),
            "FP_raised_by_degraded_recorder": sum(p["_bad"] for p in wrong),
            "FP_raised_by_intact_recorder": sum(not p["_bad"] for p in wrong),
            "FP_about_phantom": sum(p["subject"] is None for p in wrong),
            "phantoms_per_job": _ratio(sum(j["phantom_entities"] for j in jobs), len(jobs)),
            "phantoms_<=2m_at_impact_per_contact": _ratio(sum(x["clearance_at_impact_m"] is not None and x["clearance_at_impact_m"] <= 2.0 for x in prox), contacts),
            "phantoms_<=5m_at_impact_per_contact": _ratio(sum(x["clearance_at_impact_m"] is not None and x["clearance_at_impact_m"] <= 5.0 for x in prox), contacts),
            "replays_incorrect_last_second_pct": _ratio(100 * sum(any(b["incorrect_events_active"] for b in j["active"]["before_contact"]) for j in jobs), len(jobs)),
            "replays_phantom_incorrect_last_second_pct": _ratio(100 * sum(any(b["incorrect_events_active_phantom"] for b in j["active"]["before_contact"]) for j in jobs), len(jobs))})
    return rows


def replay_row(j: Mapping[str, Any]) -> Dict[str, Any]:
    preds = j["predictions"]
    before = [b for b in j["active"]["before_contact"]]
    prox = [x for x in j["proximity"] if x["kind"] == "phantom"]
    row = dict(j["job"])
    row.pop("kept", None)
    row.update({
        "condition": condition(j["job"]), "contacts": len(j["contacts"]),
        "predictions": len(preds), "correct": sum(p["class"] == "correct" for p in preds),
        "incorrect_events": sum(p["class"] in INCORRECT for p in preds),
        "incorrect_events_before_contact": sum(p["class"] in INCORRECT and p["phase"] != "after contact" for p in preds),
        "incorrect_events_phantom_subject": sum(p["class"] in INCORRECT and p["subject"] is None for p in preds),
        "missed_true_events": sum(not t["matched"] for t in j["truths"]),
        "incorrect_active_last_second": sum(b["incorrect_events_active"] for b in before),
        "incorrect_active_last_second_phantom": sum(b["incorrect_events_active_phantom"] for b in before),
        "phantom_entities": j["phantom_entities"], "entities": j["entities"],
        "phantoms_at_impact_<=2m": sum(x["clearance_at_impact_m"] is not None and x["clearance_at_impact_m"] <= 2.0 for x in prox),
        "phantoms_at_impact_<=5m": sum(x["clearance_at_impact_m"] is not None and x["clearance_at_impact_m"] <= 5.0 for x in prox),
        "participants_correct": all(bool(c["participants_correct"]) for c in j["contacts"]),
        "recovery_tracks": len(j["recovery"])})
    return row


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]], compress: bool = False) -> None:
    if not rows:
        return
    keys: List[str] = []
    for row in rows:
        for k in row:
            if k not in keys:
                keys.append(k)
    opener = (lambda p: gzip.open(str(p), "wt", encoding="utf-8", newline="")) if compress else \
        (lambda p: open(str(p), "w", encoding="utf-8", newline=""))
    with opener(path) as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: (json.dumps(v) if isinstance(v, (list, dict)) else v) for k, v in row.items()})


def write_md(path: Path, tables: Mapping[str, Sequence[Mapping[str, Any]]], titles: Mapping[str, str]) -> None:
    lines = ["# Event validation, relevance at impact and phantoms: tables", "",
             "Definitions: `docs/EVENT_VALIDATION.md`.  Counts with their denominators; percentages are of the column "
             "named in the header.", ""]
    for name, title in titles.items():
        rows = tables.get(name) or []
        if not rows:
            continue
        keys: List[str] = []
        for row in rows:
            for k in row:
                if k not in keys:
                    keys.append(k)
        lines += ["## " + title, "", "| " + " | ".join(keys) + " |", "|" + "---|" * len(keys)]
        for row in rows:
            lines.append("| " + " | ".join("" if row.get(k) is None else str(row.get(k)) for k in keys) + " |")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--kept", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=ROOT / "results" / "event_validation")
    parser.add_argument("--families", default="baseline,radar_v3")
    parser.add_argument("--workers", type=int, default=20)
    parser.add_argument("--work", type=Path, default=None,
                        help="per-run truth and per-job results (default <out>/work; large: keep it outside git)")
    parser.add_argument("--aggregate-only", action="store_true")
    args = parser.parse_args(argv)
    lines = [json.loads(l) for l in (args.kept / "regenerated.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    families = set(args.families.split(","))
    usable = [l for l in lines if l["family"] in families and l["status"] == "complete" and l["scorecard_identical"]]
    refused = [l for l in lines if l["family"] in families and not (l["status"] == "complete" and l["scorecard_identical"])]
    work = args.work or args.out / "work"
    (work / "jobs").mkdir(parents=True, exist_ok=True)
    args.out.mkdir(parents=True, exist_ok=True)
    if not args.aggregate_only:
        runs = sorted({l["run"] for l in usable})
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            for f in as_completed([pool.submit(truth_task, run, str(work)) for run in runs]):
                f.result()
            print("truth of {0} runs".format(len(runs)), flush=True)
            futures = {pool.submit(job_task, l, str(work)): l for l in usable}
            for n, f in enumerate(as_completed(futures), 1):
                f.result()
                if n % 20 == 0 or n == len(futures):
                    print("{0}/{1} jobs analysed".format(n, len(futures)), flush=True)
    results = []
    for l in usable:
        with gzip.open(str(work / "jobs" / (job_id(l) + ".json.gz")), "rt", encoding="utf-8") as handle:
            results.append(json.load(handle))
    tables = aggregate(results, args.out, work / "jobs")
    for name, rows in tables.items():
        write_csv(args.out / (name + ".csv"), rows)
    events, truths, contacts, prox, recov = [], [], [], [], []
    for r in results:
        # job_* columns: an event's own "family" (CRITICAL_TTC, ...) must not overwrite the job's
        key = {"job_" + k: r["job"].get(k) for k in ("family", "level", "recorder", "seed", "run")}
        key["condition"] = condition(r["job"])
        events += [dict(key, kind="prediction", **p) for p in r["predictions"]]
        truths += [dict(key, kind="truth", **t) for t in r["truths"]]
        contacts += [dict(key, **x) for x in r["relevance"]]
        prox += [dict(key, **x) for x in r["proximity"]]
        recov += [dict(key, **x) for x in r["recovery"]]
    write_csv(args.out / "events.csv.gz", events + truths, compress=True)
    write_csv(args.out / "contacts.csv", contacts)
    write_csv(args.out / "proximity.csv.gz", prox, compress=True)
    write_csv(args.out / "recovery.csv", recov)
    write_md(args.out / "tables.md", tables, {
        "events": "1. Conflict events: TP, FP, FN, precision, recall (per family)",
        "durations": "2a. Onset, duration and overlap of the matched events (before contact)",
        "time": "2b. Evaluated time with an incorrect active state",
        "replay_summary": "2c. Replays with incorrect event context",
        "states": "2d. Saved states against the truth (measured and predicted)",
        "relevance": "3. Relevance per collision (participant sides, 8 s before the contact)",
        "proximity": "4. Estimated road users at each impact, by full-box clearance to the colliding pair",
        "recovery": "5a. Recovery of the tracks of a collision partner, by distance zone",
        "recovery_association": "5b. Association of those tracks (reported apart)",
        "phantoms": "6. Phantoms and the incident",
        "by_degraded_radars": "7. One, two or all radars degraded (same runs; who raises the false events)"})
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True, text=True).stdout.strip()
    # The analysis code (not this run's own outputs) must match the commit.
    dirty = bool(subprocess.run(["git", "status", "--porcelain", "--untracked-files=no", "--", "src", "scripts",
                                 "configs"], cwd=str(ROOT), capture_output=True, text=True).stdout.strip())
    expected = Counter(l["family"] for l in lines if l["family"] in families)
    (args.out / "provenance.json").write_text(json.dumps({
        "analysis_commit": commit, "analysis_tree_dirty": dirty,
        "campaign_code": "tag campaign-v3 (df12f759), regenerated with scripts/regenerate_campaign_jobs.py",
        "kept_jobs": str(args.kept), "per_job_results": str(work), "families": sorted(families),
        "jobs_regenerated": len([l for l in lines if l["family"] in families]), "jobs_analysed": len(usable),
        "jobs_refused": [{k: l.get(k) for k in ("family", "level", "recorder", "seed", "run", "status",
                                                "scorecard_identical")} for l in refused],
        "jobs_by_family": dict(Counter(l["family"] for l in usable)),
        "definitions": "docs/EVENT_VALIDATION.md"}, indent=1), encoding="utf-8")
    sys.path.insert(0, str(ROOT / "scripts"))
    import event_validation_figures
    event_validation_figures.draw(results, tables, args.out / "figures")
    print("analysed {0} jobs ({1} refused) -> {2}".format(len(usable), len(refused), args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
