#!/usr/bin/env python3
"""Tables and figures of the robustness campaign on the 22 canonical runs.

    python scripts/campaign_report.py robustness   [--jobs results/robustness/frozen_campaign/jobs.jsonl.gz]

Aggregation only: every number comes from the job records written by ``scripts/robustness.py`` (run by
``scripts/campaign_controller.py``) with their existing evaluation; nothing is recomputed from the recordings and
no threshold is introduced here.  The command rewrites ``<jobs dir>/summary.json|csv|md`` and ``figures/``
(``robustness.summarize``) and ``<jobs dir>/report/`` (tables, csv, json, figures).  ``jobs.jsonl`` (local) or
``jobs.jsonl.gz`` (committed) are read alike.  Conventions:

* One result per job (its complete attempt, else its last failure: ``robustness.latest_results``).  Failed jobs
  are counted and listed, never dropped silently; every aggregate states how many jobs it holds.
* Per condition (family, level) and seed the counts are pooled over the runs (sums, then ratios); the table gives
  the mean over seeds and the standard deviation over seeds (SD; none with one seed).  Distribution metrics of a
  run (a run's median or p95 fused centre error) are summarised as their median over the runs of the seed.
* Two kinds of comparison are kept apart: CORRECTNESS against simulator ground truth (collisions, links,
  associations, merges, fused-state errors, stability audit, event oracle) and STABILITY against the
  unperturbed reconstruction (``event preservation``: core events found again).
* GNSS x radar: paired per run and seed (the same draws as the single-sensor jobs, see robustness.py).  The
  interaction of a metric is I = C - R - G + B (combined, radar only, GNSS only, baseline) per run, averaged over
  the common seeds, then over runs with a 95 % percentile bootstrap interval over runs (2000 resamples, fixed
  seed).  An interaction is only called one when that interval excludes 0.
* An undefined value (no decided track, no true contact, no anonymous road user) is shown as ``n/a`` with the
  reason in the column definition, never as 0.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]

ROBUSTNESS = ROOT / "results" / "robustness" / "frozen_campaign"
BANDS = ["0-10 m", "10-25 m", ">25 m"]
GNSS_LEVELS = ["rtk", "degraded"]
RADAR_LEVELS = ["low", "nominal", "high"]


def observed_gnss_levels(rows: Sequence[Dict[str, Any]]) -> List[str]:
    found = set()
    for row in rows:
        if row.get("family") in ("gnss", "gnss_refined") and row.get("level") in ("rtk", "consumer", "degraded"):
            found.add(row["level"])
        level = str(row.get("level", ""))
        for profile in ("rtk", "consumer", "degraded"):
            if row.get("family") == "radar_gnss_combined" and level.startswith("gnss " + profile + " + radar "):
                found.add(profile)
    return [level for level in ("rtk", "consumer", "degraded") if level in found] or list(GNSS_LEVELS)


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    """A JSON-lines file, gzip-compressed when its name ends in ``.gz``."""
    if not path.exists():
        return []
    if path.suffix == ".gz":
        import gzip
        with gzip.open(str(path), "rt", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _num(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(value) or math.isinf(value) else value


# --------------------------------------------------------------------------------------------------------------
# One job -> flat numbers
# --------------------------------------------------------------------------------------------------------------

def oracle_counts(r: Dict[str, Any], pair: str = "RECONSTRUCTION vs COVERAGE") -> Tuple[int, int, int, List[float]]:
    table = (r.get("event_oracle") or {}).get(pair) or {}
    expected = sum(row.get("expected", 0) for row in table.values())
    matched = sum(row.get("matched", 0) for row in table.values())
    found = sum(row.get("found", 0) for row in table.values())
    deltas = [abs(d) for row in table.values() for d in row.get("deltas", [])]
    return expected, matched, found, deltas


def job_numbers(r: Dict[str, Any]) -> Dict[str, Any]:
    """The per-run quantities of one complete job (counts are summed over runs, distributions summarised)."""
    m = r.get("metrics") or {}
    c = (r.get("campaign") or {}).get("collisions") or {}
    camp = r.get("campaign") or {}
    st = r.get("stability") or {}
    tr = r.get("trajectory") or {}
    ev = r.get("events") or {}
    pe = r.get("pose_errors") or {}
    exp, mat, fnd, deltas = oracle_counts(r)
    out: Dict[str, Any] = {
        "assoc_correct": m.get("associations_correct"), "assoc_decided": m.get("associations_decided"),
        "links_correct": m.get("links_correct"), "links_wrong": m.get("links_wrong"), "links_missed": m.get("links_missed"),
        "merges_correct": m.get("merges_correct"), "merges_false": m.get("merges_false"), "merges_missed": m.get("merges_missed"),
        "phantom_entities": m.get("entities_without_vehicle"),
        "recorders": m.get("recorders"), "recorders_aligned": m.get("recorders_aligned"),
        "max_relative_offset_error_s": m.get("max_abs_relative_offset_error_s"),
        "contacts_true": c.get("true_contacts"), "contacts_detected": c.get("detected"),
        "contacts_identified": c.get("identified"), "contacts_missed": c.get("missed"),
        "contacts_wrong_participants": c.get("detected_wrong_participants"),
        "collisions_extra_vehicle_pairs": c.get("extra_reconstructed_vehicle_pairs"),
        "collision_unmatched_reports": r.get("collision_unmatched"),
        "collision_timing_max_s": (c.get("timing_error_s") or {}).get("max"),
        "events_base": ev.get("base_events"), "events_matched": ev.get("matched"),
        "events_extra": len(ev.get("extra") or []) if ev else None,
        "event_dt_p95_s": (sorted(abs(d) for d in ev.get("time_deltas_s", []))[int(0.95 * (len(ev["time_deltas_s"]) - 1))]
                           if ev.get("time_deltas_s") else None),
        "centre_median_m": (tr.get("centre_error_m") or {}).get("median") if tr else m.get("fused_centre_error_median_m"),
        "centre_p95_m": (tr.get("centre_error_m") or {}).get("p95"),
        "centre_max_m": (tr.get("centre_error_m") or {}).get("max"),
        "velocity_median_mps": (tr.get("velocity_error_mps") or {}).get("median"),
        "velocity_p95_mps": (tr.get("velocity_error_mps") or {}).get("p95"),
        "velocity_max_mps": (tr.get("velocity_error_mps") or {}).get("max"),
        "within_2sigma": ((tr.get("calibration") or {}).get("observed_within") or {}).get("2_sigma"),
        "duplicates": sum((camp.get("duplicate_hypotheses_by_band") or {}).values()) if camp else None,
        "osc": st.get("ego_path_oscillations"), "track_losses": st.get("track_losses"),
        "fragmentation_losses": st.get("fragmentation_losses"), "phantom_tracks": st.get("phantom_tracks"),
        "trajectory_jumps": st.get("trajectory_jumps"), "closure_violations": st.get("closure_violations"),
        "cut_in_tp": (st.get("cut_in") or {}).get("tp"), "cut_in_true": (st.get("cut_in") or {}).get("true"),
        "cut_in_fp": len((st.get("cut_in") or {}).get("fp") or []) if st else None,
        "oracle_expected": exp if r.get("event_oracle") else None, "oracle_matched": mat if r.get("event_oracle") else None,
        "oracle_found": fnd if r.get("event_oracle") else None,
        "oracle_dt_median_s": statistics.median(deltas) if deltas else None,
        "abs_pose_rms_m": (pe.get("absolute_position_m") or {}).get("rms"),
        "rel_pose_rms_m": (pe.get("relative_position_m") or {}).get("rms"),
        "identical_graph": r.get("identical_graph"),
    }
    for prefix, metric, unit in (("position", "absolute_position_m", "m"),
                                 ("heading", "heading_deg", "deg"), ("velocity", "velocity_mps", "mps")):
        stats = pe.get(metric) or {}
        for percentile in ("p50", "p95", "p99", "p995", "max"):
            out["pose_{0}_{1}_{2}".format(prefix, percentile, unit)] = stats.get(percentile)
    for band in BANDS:
        d = (camp.get("decisions_by_band") or {}).get(band) or {}
        out["band_correct_" + band] = d.get("correct link", 0) if camp else None
        out["band_wrong_" + band] = d.get("WRONG link", 0) if camp else None
        out["band_missed_link_" + band] = d.get("missed link", 0) if camp else None
        mg = (camp.get("merges_by_band") or {}).get(band) or {}
        out["band_merge_false_" + band] = mg.get("false", 0) if camp else None
        out["band_merge_missed_" + band] = mg.get("missed", 0) if camp else None
        out["band_merge_correct_" + band] = mg.get("correct", 0) if camp else None
        ce = (camp.get("centre_error_by_band_m") or {}).get(band) or {}
        out["band_centre_median_" + band] = ce.get("median")
        out["band_centre_p95_" + band] = ce.get("p95")
    inc = camp.get("decisions_incident") or {}
    out["incident_correct"] = inc.get("correct link", 0) if camp else None
    out["incident_wrong"] = inc.get("WRONG link", 0) if camp else None
    out["incident_missed_link"] = inc.get("missed link", 0) if camp else None
    out["incident_anonymous"] = inc.get("anonymous", 0) if camp else None
    mi = camp.get("merges_incident") or {}
    out["incident_merge_false"] = mi.get("false", 0) if camp else None
    out["incident_merge_missed"] = mi.get("missed", 0) if camp else None
    out["incident_centre_median_m"] = (camp.get("centre_error_incident_m") or {}).get("median")
    out["incident_centre_p95_m"] = (camp.get("centre_error_incident_m") or {}).get("p95")
    return out


def _sum(rows: Sequence[Dict[str, Any]], key: str) -> Optional[float]:
    values = [_num(r.get(key)) for r in rows]
    values = [v for v in values if v is not None]
    return sum(values) if values else None


def _ratio(rows: Sequence[Dict[str, Any]], num: str, den: str) -> Optional[float]:
    n, d = _sum(rows, num), _sum(rows, den)
    return None if not d else (n or 0.0) / d


def _median(rows: Sequence[Dict[str, Any]], key: str) -> Optional[float]:
    values = [_num(r.get(key)) for r in rows]
    values = [v for v in values if v is not None]
    return statistics.median(values) if values else None


def _max(rows: Sequence[Dict[str, Any]], key: str) -> Optional[float]:
    values = [_num(r.get(key)) for r in rows]
    values = [v for v in values if v is not None]
    return max(values) if values else None


# Condition metrics: name -> (function of the per-run rows of one seed, kind, description).
# kind "truth": against simulator ground truth; "stability": against the unperturbed reconstruction.
METRICS: Dict[str, Tuple[Callable[[Sequence[Dict[str, Any]]], Optional[float]], str, str]] = {
    "association_accuracy": (lambda rs: _ratio(rs, "assoc_correct", "assoc_decided"), "truth",
                             "correct / decided recorder-identity associations (n/a: none decided)"),
    "collision_recall": (lambda rs: _ratio(rs, "contacts_identified", "contacts_true"), "truth",
                         "true vehicle-vehicle contacts reconstructed with exactly their participants"),
    "collision_detection": (lambda rs: _ratio(rs, "contacts_detected", "contacts_true"), "truth",
                            "true contacts with a reconstructed collision node, participants right or not"),
    "wrong_collision_matches": (lambda rs: (_sum(rs, "contacts_wrong_participants") or 0)
                                + (_sum(rs, "collisions_extra_vehicle_pairs") or 0), "truth",
                                "detected contacts with wrong participants + reconstructed vehicle pairs without a true contact"),
    "unmatched_collision_reports": (lambda rs: _sum(rs, "collision_unmatched_reports"), "truth",
                                    "true contacts left without any reconstructed collision"),
    "runs_aligned": (lambda rs: (sum(1 for r in rs if r.get("recorders") and r.get("recorders_aligned") == r.get("recorders"))
                                 / len([r for r in rs if r.get("recorders")])) if [r for r in rs if r.get("recorders")] else None,
                     "truth", "runs with every recorder on the global clock"),
    "max_relative_offset_error_s": (lambda rs: _max(rs, "max_relative_offset_error_s"), "truth",
                                    "largest error of a recorder's estimated clock offset"),
    "wrong_links": (lambda rs: _sum(rs, "links_wrong"), "truth", "tracks linked to the wrong recorder"),
    "missed_links": (lambda rs: _sum(rs, "links_missed"), "truth", "tracks of a recorder left anonymous"),
    "false_merges": (lambda rs: _sum(rs, "merges_false"), "truth", "track pairs merged across different vehicles"),
    "missed_merges": (lambda rs: _sum(rs, "merges_missed"), "truth", "track pairs of one vehicle left apart"),
    "phantom_entities": (lambda rs: _sum(rs, "phantom_entities"), "truth", "anonymous entities on no true vehicle"),
    "duplicate_hypotheses": (lambda rs: _sum(rs, "duplicates"), "truth", "extra entities of one true vehicle"),
    "centre_error_median_m": (lambda rs: _median(rs, "centre_median_m"), "truth",
                              "fused centre error of anonymous road users: per-run median, median over runs [m]"),
    "centre_error_p95_m": (lambda rs: _median(rs, "centre_p95_m"), "truth", "per-run p95, median over runs [m]"),
    "centre_error_max_m": (lambda rs: _max(rs, "centre_max_m"), "truth", "largest fused centre error of any run [m]"),
    "velocity_error_median_mps": (lambda rs: _median(rs, "velocity_median_mps"), "truth",
                                  "fused velocity error: per-run median, median over runs [m/s]"),
    "velocity_error_p95_mps": (lambda rs: _median(rs, "velocity_p95_mps"), "truth", "per-run p95, median over runs [m/s]"),
    "within_2sigma": (lambda rs: _median(rs, "within_2sigma"), "truth",
                      "share of fused states within their declared 2 sigma (Gaussian: 0.865)"),
    "ego_path_oscillations": (lambda rs: _sum(rs, "osc"), "truth", "EGO_PATH changes undone within 3 sweeps (audit)"),
    "track_losses": (lambda rs: _sum(rs, "track_losses"), "truth", "TRACK_LOST of confirmed tracks (audit)"),
    "fragmentation_losses": (lambda rs: _sum(rs, "fragmentation_losses"), "truth", "losses while the radar still saw the body"),
    "phantom_tracks": (lambda rs: _sum(rs, "phantom_tracks"), "truth", "local tracks on no true vehicle (audit)"),
    "closure_violations": (lambda rs: _sum(rs, "closure_violations"), "truth", "CRITICAL_TTC started after the pair's contact"),
    "cut_in_recall": (lambda rs: _ratio(rs, "cut_in_tp", "cut_in_true"), "truth",
                      "CUT_IN against the audit's ground-truth criterion (n/a: no true cut-in)"),
    "oracle_event_recall": (lambda rs: _ratio(rs, "oracle_matched", "oracle_expected"), "truth",
                            "core events of the ground-truth coverage oracle found by the reconstruction"),
    "oracle_event_precision": (lambda rs: _ratio(rs, "oracle_matched", "oracle_found"), "truth",
                               "reconstructed core events matched by the coverage oracle"),
    "event_preservation": (lambda rs: _ratio(rs, "events_matched", "events_base"), "stability",
                           "core events of the unperturbed reconstruction found again"),
    "events_added": (lambda rs: _sum(rs, "events_extra"), "stability", "core events absent from the unperturbed reconstruction"),
    "identical_graphs": (lambda rs: (sum(1 for r in rs if r.get("identical_graph")) / len([r for r in rs if r.get("identical_graph") is not None]))
                         if [r for r in rs if r.get("identical_graph") is not None] else None, "stability",
                         "share of runs whose global graph is node for node the unperturbed one"),
    "event_dt_p95_s": (lambda rs: _median(rs, "event_dt_p95_s"), "stability",
                       "per-run p95 time difference of the preserved events, median over runs [s]"),
    "absolute_pose_rms_m": (lambda rs: _median(rs, "abs_pose_rms_m"), "input", "injected absolute GNSS error, RMS [m]"),
    "relative_pose_rms_m": (lambda rs: _median(rs, "rel_pose_rms_m"), "input", "injected recorder-pair relative error, RMS [m]"),
}
for _prefix, _label, _unit in (("position", "horizontal position", "m"), ("heading", "heading", "deg"),
                               ("velocity", "horizontal velocity", "m/s")):
    for _percentile in ("p50", "p95", "p99", "p995", "max"):
        _field = "pose_{0}_{1}_{2}".format(_prefix, _percentile, "mps" if _unit == "m/s" else _unit)
        _aggregate = _max if _percentile == "max" else _median
        METRICS["absolute_pose_{0}_{1}".format(_prefix, _percentile)] = (
            lambda rs, field=_field, aggregate=_aggregate: aggregate(rs, field), "input",
            "injected {0} error: per-run {1}, median over runs [{2}]".format(_label, _percentile, _unit))
def _band_accuracy(band: str) -> Callable[[Sequence[Dict[str, Any]]], Optional[float]]:
    def accuracy(rs: Sequence[Dict[str, Any]]) -> Optional[float]:
        correct, wrong = _sum(rs, "band_correct_" + band), _sum(rs, "band_wrong_" + band)
        return None if not (correct or wrong) else (correct or 0) / ((correct or 0) + (wrong or 0))
    return accuracy


for _band in BANDS:
    METRICS["association_accuracy " + _band] = (_band_accuracy(_band), "truth",
                                                 "recorder links correct / (correct + wrong), tracks of median range in the band")
    METRICS["missed_links " + _band] = ((lambda b: lambda rs: _sum(rs, "band_missed_link_" + b))(_band), "truth", "")
    METRICS["false_merges " + _band] = ((lambda b: lambda rs: _sum(rs, "band_merge_false_" + b))(_band), "truth", "")
    METRICS["missed_merges " + _band] = ((lambda b: lambda rs: _sum(rs, "band_merge_missed_" + b))(_band), "truth", "")
    METRICS["centre_error_median_m " + _band] = ((lambda b: lambda rs: _median(rs, "band_centre_median_" + b))(_band), "truth", "")
    METRICS["centre_error_p95_m " + _band] = ((lambda b: lambda rs: _median(rs, "band_centre_p95_" + b))(_band), "truth", "")
METRICS["incident_link_accuracy"] = (
    lambda rs: (lambda c, w, m: None if not (c or w or m) else (c or 0) / ((c or 0) + (w or 0) + (m or 0)))(
        _sum(rs, "incident_correct"), _sum(rs, "incident_wrong"), _sum(rs, "incident_missed_link")),
    "truth", "tracks of incident participants that are recorders: correct link / (correct + wrong + missed)")
METRICS["incident_wrong_links"] = (lambda rs: _sum(rs, "incident_wrong"), "truth", "")
METRICS["incident_false_merges"] = (lambda rs: _sum(rs, "incident_merge_false"), "truth", "")
METRICS["incident_centre_error_median_m"] = (lambda rs: _median(rs, "incident_centre_median_m"), "truth",
                                             "fused centre error of non-recording incident participants")


# --------------------------------------------------------------------------------------------------------------
# Aggregation
# --------------------------------------------------------------------------------------------------------------

def condition_table(jobs: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    import robustness
    groups: Dict[Tuple[str, str], Dict[int, List[Dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    failed: Dict[Tuple[str, str], int] = defaultdict(int)
    for r in jobs:
        key = (r["family"], r["level"])
        if r.get("status") != "complete":
            failed[key] += 1
            continue
        groups[key][int(r["seed"])].append(job_numbers(r))
    order = list(robustness.FAMILIES)
    rows = []
    for key in sorted(set(groups) | set(failed), key=lambda k: (order.index(k[0]) if k[0] in order else 99,
                                                                [l for l, _ in robustness.FAMILIES.get(k[0], ([], 0))[0]].index(k[1])
                                                                if k[0] in robustness.FAMILIES else 0)):
        by_seed = groups.get(key, {})
        row: Dict[str, Any] = {"family": key[0], "level": key[1], "seeds": len(by_seed),
                               "jobs_complete": sum(len(v) for v in by_seed.values()), "jobs_failed": failed.get(key, 0)}
        for name, (fn, _, _) in METRICS.items():
            values = [v for v in (_num(fn(rs)) for rs in by_seed.values()) if v is not None]
            row[name] = round(statistics.fmean(values), 4) if values else None
            row[name + " sd"] = round(statistics.stdev(values), 4) if len(values) > 1 else None
            row[name + " n"] = len(values)
        rows.append(row)
    return rows


def _bootstrap_ci(values: Sequence[float], seed: int = 20261015, n: int = 2000) -> Tuple[Optional[float], Optional[float]]:
    import random
    if len(values) < 2:
        return None, None
    rng = random.Random(seed)
    means = sorted(statistics.fmean(rng.choice(values) for _ in values) for _ in range(n))
    return means[int(0.025 * n)], means[int(0.975 * n) - 1]


# Per-run quantities used in the paired GNSS x radar comparison (one value per run and job).
PAIRED = {"association_errors": lambda x: None if x.get("assoc_decided") is None
          else (x["assoc_decided"] or 0) - (x.get("assoc_correct") or 0),
          "missed_contacts": lambda x: None if x.get("contacts_true") is None
          else (x["contacts_true"] or 0) - (x.get("contacts_identified") or 0),
          "wrong_collision_matches": lambda x: None if x.get("contacts_wrong_participants") is None
          else (x["contacts_wrong_participants"] or 0) + (x.get("collisions_extra_vehicle_pairs") or 0),
          "wrong_links": lambda x: x.get("links_wrong"),
          "missed_links": lambda x: x.get("links_missed"),
          "false_merges": lambda x: x.get("merges_false"),
          "missed_merges": lambda x: x.get("merges_missed"),
          "events_lost": lambda x: None if x.get("events_base") is None
          else (x["events_base"] or 0) - (x.get("events_matched") or 0),
          "centre_error_median_m": lambda x: x.get("centre_median_m"),
          "centre_error_p95_m": lambda x: x.get("centre_p95_m"),
          "unaligned_recorders": lambda x: None if x.get("recorders") is None
          else (x["recorders"] or 0) - (x.get("recorders_aligned") or 0)}


def run_key(run: str) -> str:
    """``S04/run_0_a_front_pushed`` whatever the path spelling (absolute, relative, slashes)."""
    return "/".join(str(run).replace("\\", "/").rstrip("/").split("/")[-2:])


def interaction_table(jobs: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Paired comparison of every GNSS x radar cell with its single-sensor conditions (module docstring)."""
    index: Dict[Tuple[str, str, str, int], Dict[str, Any]] = {}
    base: Dict[str, Dict[str, Any]] = {}
    for r in jobs:
        if r.get("status") != "complete":
            continue
        numbers = job_numbers(r)
        if r["family"] == "baseline":
            base[run_key(r["run"])] = numbers
        elif r["family"] in ("radar", "gnss", "radar_gnss_combined"):
            index[(r["family"], r["level"], run_key(r["run"]), int(r["seed"]))] = numbers
    rows = []
    for g in observed_gnss_levels(jobs):
        for rl in RADAR_LEVELS:
            level = "gnss {0} + radar {1}".format(g, rl)
            for name, fn in PAIRED.items():
                per_run: Dict[str, List[Tuple[float, float, float, float]]] = defaultdict(list)
                for (family, lev, run, seed), c in index.items():
                    if family != "radar_gnss_combined" or lev != level or run not in base:
                        continue
                    rr, gg = index.get(("radar", rl, run, seed)), index.get(("gnss", g, run, seed))
                    if rr is None or gg is None:
                        continue
                    values = [fn(base[run]), fn(rr), fn(gg), fn(c)]
                    if any(_num(v) is None for v in values):
                        continue
                    per_run[run].append(tuple(float(v) for v in values))
                if not per_run:
                    rows.append({"gnss": g, "radar": rl, "metric": name, "runs": 0, "note": "insufficient paired evidence"})
                    continue
                means = {run: [statistics.fmean(v[i] for v in vs) for i in range(4)] for run, vs in per_run.items()}
                inter = [m[3] - m[1] - m[2] + m[0] for m in means.values()]
                delta_c = [m[3] - m[0] for m in means.values()]
                additive = [(m[1] - m[0]) + (m[2] - m[0]) for m in means.values()]
                lo, hi = _bootstrap_ci(inter)
                rows.append({"gnss": g, "radar": rl, "metric": name, "runs": len(means),
                             "paired_jobs": sum(len(v) for v in per_run.values()),
                             "baseline_mean": round(statistics.fmean(m[0] for m in means.values()), 4),
                             "radar_only_mean": round(statistics.fmean(m[1] for m in means.values()), 4),
                             "gnss_only_mean": round(statistics.fmean(m[2] for m in means.values()), 4),
                             "combined_mean": round(statistics.fmean(m[3] for m in means.values()), 4),
                             "combined_minus_baseline": round(statistics.fmean(delta_c), 4),
                             "additive_prediction": round(statistics.fmean(additive), 4),
                             "interaction_mean": round(statistics.fmean(inter), 4),
                             "interaction_ci95": [None if lo is None else round(lo, 4), None if hi is None else round(hi, 4)],
                             "interaction_supported": (lo is not None and (lo > 0 or hi < 0))})
    return rows


# --------------------------------------------------------------------------------------------------------------
# Figures
# --------------------------------------------------------------------------------------------------------------

CURVE_PANELS = [("association_accuracy", "association accuracy"), ("collision_recall", "collision recall"),
                ("event_preservation", "event preservation (vs unperturbed)"),
                ("oracle_event_recall", "oracle event recall (vs truth)"),
                ("centre_error_median_m", "fused centre error, median [m]"), ("false_merges", "false merges")]
CURVES = {"radar": ("Radar degradation", ["low", "nominal", "high"]),
          "gnss": ("GNSS degradation (independent receivers)", ["rtk", "degraded"]),
          "gnss_correlated": ("Correlated degraded GNSS (common fraction)", ["degraded common 0.5", "degraded common 0.9",
                                                                              "degraded common 1.0"]),
          "combined": ("GNSS + 10 % collision impulse noise", ["exact + 10%", "RTK + 10%", "degraded independent + 10%",
                                                               "degraded common 0.9 + 10%"]),
          "impulse": ("Collision impulse noise", ["2%", "5%", "10%", "20%"]),
          "downsample": ("Reduced sampling rate", ["10 Hz", "5 Hz"]),
          "outage": ("1 s radar outage (each recorder)", ["1 s radar outage"]),
          "dropout": ("One recorder missing (each in turn)", ["one recorder"])}


def _save(fig: Any, out: Path, name: str) -> List[Path]:
    out.mkdir(parents=True, exist_ok=True)
    paths = []
    for suffix in ("pdf", "svg", "png"):
        path = out / "{0}.{1}".format(name, suffix)
        fig.savefig(str(path), dpi=200 if suffix == "png" else None)
        paths.append(path)
    return paths


def curve_figures(rows: Sequence[Dict[str, Any]], out: Path) -> List[Path]:
    from cdf.evaluation.figures import DOUBLE_COLUMN_IN, paper_style
    plt = paper_style()
    base = next((r for r in rows if r["family"] == "baseline"), None)
    written = []
    for family, (title, levels) in CURVES.items():
        if family in ("gnss", "gnss_refined"):
            levels = observed_gnss_levels([r for r in rows if r.get("family") == family])
        elif family in ("gnss_correlated", "combined"):
            current = [r["level"] for r in rows if r.get("family") == family]
            levels = [lev for lev in levels if lev in current] + [lev for lev in current if lev not in levels]
        items = [next((r for r in rows if r["family"] == family and r["level"] == lev), None) for lev in levels]
        if not any(items):
            continue
        series = [("unperturbed", base)] + list(zip(levels, items))
        fig, grid = plt.subplots(2, 3, figsize=(DOUBLE_COLUMN_IN, 4.0))
        for axis, (key, label) in zip(grid.flat, CURVE_PANELS):
            xs, ys, es = [], [], []
            for x, (lev, row) in enumerate(series):
                value = None if row is None else row.get(key)
                xs.append(x)
                ys.append(math.nan if value is None else value)
                es.append(0.0 if row is None or row.get(key + " sd") is None else row[key + " sd"])
            axis.errorbar(xs, ys, yerr=es, marker="o", capsize=3, linewidth=1.2, markersize=4)
            axis.set_xticks(xs)
            axis.set_xticklabels([lev for lev, _ in series], rotation=30, ha="right")
            axis.set_title(label)
            axis.grid(alpha=0.3)
            if key in ("association_accuracy", "collision_recall", "event_preservation", "oracle_event_recall"):
                axis.set_ylim(-0.02, 1.02)
        fig.suptitle(title + "  (mean +- SD over seeds; n/a points omitted)")
        fig.tight_layout()
        written += _save(fig, out, "curve_" + family)
        plt.close(fig)
    # GNSS x radar as lines: one line per GNSS level over the radar levels, radar-only as reference.
    combo = [r for r in rows if r["family"] == "radar_gnss_combined"]
    if combo:
        gnss_levels = observed_gnss_levels(combo)
        fig, grid = plt.subplots(2, 3, figsize=(DOUBLE_COLUMN_IN, 4.0))
        for axis, (key, label) in zip(grid.flat, CURVE_PANELS):
            for name, rows_of in [("radar only", [next((r for r in rows if r["family"] == "radar" and r["level"] == rl), None)
                                                  for rl in RADAR_LEVELS])] + \
                    [("GNSS " + g, [next((r for r in combo if r["level"] == "gnss {0} + radar {1}".format(g, rl)), None)
                                    for rl in RADAR_LEVELS]) for g in gnss_levels]:
                ys = [math.nan if r is None or r.get(key) is None else r[key] for r in rows_of]
                es = [0.0 if r is None or r.get(key + " sd") is None else r[key + " sd"] for r in rows_of]
                axis.errorbar(range(3), ys, yerr=es, marker="o", capsize=2, linewidth=1.0, markersize=3, label=name)
            axis.set_xticks(range(3))
            axis.set_xticklabels(RADAR_LEVELS)
            axis.set_title(label)
            axis.grid(alpha=0.3)
        grid.flat[0].legend(fontsize=6)
        fig.suptitle("Simultaneous GNSS and radar degradation (x: radar level)")
        fig.tight_layout()
        written += _save(fig, out, "curve_radar_gnss_combined")
        plt.close(fig)
    return written


HEATMAPS = [("collision_recall", "collision recall", "{0:.3f}"),
            ("wrong_collision_matches", "wrong collision matches", "{0:.1f}"),
            ("association_accuracy", "association accuracy", "{0:.3f}"),
            ("false_merges", "false merges", "{0:.1f}"),
            ("centre_error_median_m", "fused centre error, median [m]", "{0:.2f}"),
            ("event_preservation", "event preservation (vs unperturbed)", "{0:.3f}")]


def heatmaps(rows: Sequence[Dict[str, Any]], out: Path) -> List[Path]:
    from cdf.evaluation.figures import DOUBLE_COLUMN_IN, paper_style
    import numpy as np
    plt = paper_style()
    combo = {r["level"]: r for r in rows if r["family"] == "radar_gnss_combined"}
    if not combo:
        return []
    gnss_levels = observed_gnss_levels(rows)
    fig, grid = plt.subplots(2, 3, figsize=(DOUBLE_COLUMN_IN, 5.2))
    for axis, (key, label, fmt) in zip(grid.flat, HEATMAPS):
        values = np.full((len(gnss_levels), len(RADAR_LEVELS)), np.nan)
        texts = [["" for _ in RADAR_LEVELS] for _ in gnss_levels]
        for i, g in enumerate(gnss_levels):
            for j, rl in enumerate(RADAR_LEVELS):
                row = combo.get("gnss {0} + radar {1}".format(g, rl))
                value = None if row is None else row.get(key)
                if value is None:
                    texts[i][j] = "n/a" if row is not None else "not run"
                    continue
                values[i, j] = value
                sd = row.get(key + " sd")
                texts[i][j] = fmt.format(value) + ("\n+-" + fmt.format(sd) if sd is not None else "") + \
                    "\nn={0}".format(row.get(key + " n"))
        masked = np.ma.masked_invalid(values)
        image = axis.imshow(masked, cmap="viridis", aspect="auto")
        for i in range(len(gnss_levels)):
            for j in range(3):
                axis.text(j, i, texts[i][j], ha="center", va="center", fontsize=6, color="black",
                          bbox={"boxstyle": "round,pad=0.15", "facecolor": "white", "alpha": 0.7, "linewidth": 0})
        axis.set_xticks(range(3))
        axis.set_xticklabels(RADAR_LEVELS)
        axis.set_xlabel("radar profile")
        axis.set_yticks(range(len(gnss_levels)))
        axis.set_yticklabels(gnss_levels)
        axis.set_ylabel("GNSS profile")
        axis.set_title(label)
        fig.colorbar(image, ax=axis, fraction=0.046)
    fig.suptitle("GNSS x radar: mean +- SD over seeds (n = seeds); n/a = undefined")
    fig.tight_layout()
    written = _save(fig, out, "heatmap_radar_gnss_combined")
    plt.close(fig)
    return written


# --------------------------------------------------------------------------------------------------------------
# Markdown
# --------------------------------------------------------------------------------------------------------------

def _fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return "{0:.{1}f}".format(value, digits)
    return str(value)


def _cell(row: Dict[str, Any], key: str, digits: int = 3) -> str:
    value, sd = row.get(key), row.get(key + " sd")
    return _fmt(value, digits) + ("" if not sd else " +- " + _fmt(sd, digits))


MAIN_COLUMNS = [("collision_recall", 3), ("wrong_collision_matches", 1), ("association_accuracy", 3), ("wrong_links", 1),
                ("missed_links", 1), ("false_merges", 1), ("missed_merges", 1), ("centre_error_median_m", 2),
                ("centre_error_p95_m", 2), ("runs_aligned", 3), ("event_preservation", 3), ("oracle_event_recall", 3),
                ("ego_path_oscillations", 1), ("identical_graphs", 3)]


def robustness_markdown(rows: Sequence[Dict[str, Any]], inter: Sequence[Dict[str, Any]], jobs: Sequence[Dict[str, Any]],
                        attempts: int, provenance: Dict[str, Any]) -> str:
    lines = ["# Frozen robustness campaign: tables", "",
             "Generated by `scripts/campaign_report.py robustness` from `jobs.jsonl` (aggregation conventions in its "
             "docstring).  Mean over seeds +- SD over seeds; `n/a`: undefined (see the metric definitions below).", "",
             "Provenance of the jobs: commit `{0}`, code `{1}`, configuration (frozen) `{2}`.".format(
                 provenance.get("git_commit"), str(provenance.get("code_sha256"))[:16],
                 str(provenance.get("config_sha256"))[:16]), "",
             "Jobs: {0} ({1} complete, {2} failed after all attempts); attempts recorded: {3}.".format(
                 len(jobs), sum(1 for j in jobs if j.get("status") == "complete"),
                 sum(1 for j in jobs if j.get("status") != "complete"), attempts), "",
             "## All conditions (correctness against simulator truth unless marked)", "",
             "| family | level | seeds | jobs | failed | " + " | ".join(k for k, _ in MAIN_COLUMNS) + " |",
             "|---|---|--:|--:|--:|" + "--:|" * len(MAIN_COLUMNS)]
    for row in rows:
        lines.append("| {0} | {1} | {2} | {3} | {4} | {5} |".format(
            row["family"], row["level"], row["seeds"], row["jobs_complete"], row["jobs_failed"],
            " | ".join(_cell(row, k, d) for k, d in MAIN_COLUMNS)))
    lines += ["", "`event_preservation` is STABILITY against the unperturbed reconstruction, not correctness.", "",
              "## Distance bands (median radar range of the track; correctness)", "",
              "| family | level | " + " | ".join("assoc. acc. " + b for b in BANDS) + " | " +
              " | ".join("false merges " + b for b in BANDS) + " | " + " | ".join("missed merges " + b for b in BANDS) +
              " | " + " | ".join("centre median " + b for b in BANDS) + " |",
              "|---|---|" + "--:|" * 12]
    for row in rows:
        lines.append("| {0} | {1} | {2} | {3} | {4} | {5} |".format(
            row["family"], row["level"], " | ".join(_cell(row, "association_accuracy " + b) for b in BANDS),
            " | ".join(_cell(row, "false_merges " + b, 1) for b in BANDS),
            " | ".join(_cell(row, "missed_merges " + b, 1) for b in BANDS),
            " | ".join(_cell(row, "centre_error_median_m " + b, 2) for b in BANDS)))
    lines += ["", "## Incident participants (true contact partners; correctness)", "",
              "| family | level | link accuracy | wrong links | false merges | centre error median [m] |",
              "|---|---|--:|--:|--:|--:|"]
    for row in rows:
        lines.append("| {0} | {1} | {2} | {3} | {4} | {5} |".format(
            row["family"], row["level"], _cell(row, "incident_link_accuracy"), _cell(row, "incident_wrong_links", 1),
            _cell(row, "incident_false_merges", 1), _cell(row, "incident_centre_error_median_m", 2)))
    lines += ["", "## Combined GNSS and radar degradation: paired interaction", "",
              "I = C - R - G + B per run (mean over common seeds), mean over runs, 95 % bootstrap interval over runs. "
              "`supported`: the interval excludes 0.", "",
              "| GNSS | radar | metric | runs | B | R | G | C | C - B | additive (R-B)+(G-B) | I | I 95 % CI | supported |",
              "|---|---|---|--:|--:|--:|--:|--:|--:|--:|--:|---|---|"]
    for r in inter:
        if not r.get("runs"):
            lines.append("| {0} | {1} | {2} | 0 | | | | | | | | {3} | |".format(r["gnss"], r["radar"], r["metric"], r["note"]))
            continue
        lines.append("| {gnss} | {radar} | {metric} | {runs} | {baseline_mean} | {radar_only_mean} | {gnss_only_mean} | "
                     "{combined_mean} | {combined_minus_baseline} | {additive_prediction} | {interaction_mean} | "
                     "{ci} | {sup} |".format(ci=r["interaction_ci95"], sup="yes" if r["interaction_supported"] else "no",
                                             **r))
    lines += ["", "## Metric definitions", ""]
    for name, (_, kind, text) in METRICS.items():
        if text:
            lines.append("- `{0}` ({1}): {2}".format(name, kind, text))
    return "\n".join(lines) + "\n"


def resources_table(jobs: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    by_family: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in jobs:
        by_family[r["family"]].append(r)
    rows = []
    for family, rs in by_family.items():
        walls = sorted(float(r.get("wall_s") or 0.0) for r in rs)
        peaks = [float((r.get("resources") or {}).get("peak_mb") or 0.0) for r in rs]
        rows.append({"family": family, "jobs": len(rs), "wall_median_s": round(statistics.median(walls), 1),
                     "wall_p95_s": round(walls[int(0.95 * (len(walls) - 1))], 1), "wall_max_s": round(walls[-1], 1),
                     "cpu_hours": round(sum(walls) / 3600.0, 2), "worker_peak_mb_max": round(max(peaks), 1) if peaks else None})
    return rows


def _write_csv(path: Path, rows: Sequence[Dict[str, Any]]) -> None:
    if not rows:
        return
    keys: List[str] = []
    for row in rows:
        keys += [k for k in row if k not in keys]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: (json.dumps(v) if isinstance(v, (list, dict)) else v) for k, v in row.items()})


def robustness_report(jobs_path: Path, out: Path) -> int:
    import robustness
    raw = _read_jsonl(jobs_path)
    jobs = robustness.latest_results(raw)
    robustness.summarize(raw, jobs_path.parent)  # summary.json|csv|md and figures/ beside the job records
    rows = condition_table(jobs)
    inter = interaction_table(jobs)
    resources = resources_table(raw)
    failures = [{"run": r["run"], "family": r["family"], "level": r["level"], "recorder": r.get("recorder"),
                 "seed": r["seed"], "attempts": sum(1 for x in raw if (x["run"], x["family"], x["level"], x.get("recorder"),
                                                                       x["seed"]) == (r["run"], r["family"], r["level"],
                                                                                      r.get("recorder"), r["seed"])),
                 "error": r.get("error")} for r in jobs if r.get("status") != "complete"]
    retried = sum(1 for r in jobs if r.get("status") == "complete" and int(r.get("attempt") or 1) > 1)
    provenance = next((r.get("provenance") for r in jobs if r.get("family") == "baseline" and r.get("provenance")), {}) or {}
    out.mkdir(parents=True, exist_ok=True)
    partial = [{"run": run_key(r["run"]), "family": r["family"], "level": r["level"], "recorder": r.get("recorder"),
                "seed": r["seed"], "components": sorted(r["evaluation_errors"])}
               for r in jobs if r.get("status") == "complete" and r.get("evaluation_errors")]
    commits = defaultdict(int)
    for r in jobs:
        commits[(r.get("provenance") or {}).get("git_commit")] += 1
    record = {"jobs": len(jobs), "attempts": len(raw), "complete": sum(1 for r in jobs if r.get("status") == "complete"),
              "failed": len(failures), "retried_then_complete": retried, "provenance": provenance,
              "jobs_by_commit": dict(commits), "partial_evaluations": partial,
              "conditions": rows, "interaction": inter, "resources": resources, "failures": failures,
              "metric_kinds": {k: v[1] for k, v in METRICS.items()}}
    (out / "summary.json").write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    _write_csv(out / "conditions.csv", rows)
    _write_csv(out / "interaction.csv", inter)
    _write_csv(out / "resources.csv", resources)
    _write_csv(out / "failures.csv", failures)
    (out / "tables.md").write_text(robustness_markdown(rows, inter, jobs, len(raw), provenance), encoding="utf-8")
    figures = curve_figures(rows, out / "figures") + heatmaps(rows, out / "figures")
    print("conditions", len(rows), "interaction rows", len(inter), "figures", len(figures), "failed jobs", len(failures))
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("study", choices=("robustness",))
    parser.add_argument("--jobs", type=Path, default=None,
                        help="job records (default: <results>/jobs.jsonl if present, else jobs.jsonl.gz)")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    jobs = args.jobs or (ROBUSTNESS / "jobs.jsonl" if (ROBUSTNESS / "jobs.jsonl").exists() else ROBUSTNESS / "jobs.jsonl.gz")
    return robustness_report(jobs, args.out or jobs.parent / "report")


if __name__ == "__main__":
    raise SystemExit(main())
