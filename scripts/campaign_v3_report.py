#!/usr/bin/env python3
"""Scientific report of campaign v3 (docs/CAMPAIGN_V3.md): tables, figures and an index, every number computed
from the job records (``jobs.jsonl``: one line per attempt; a job counts with its complete attempt, else its last).

    python scripts/campaign_v3_report.py --jobs <campaign results>/jobs.jsonl --out results/campaign_v3

Statistics.  The unit of replication is the seed: one seed draws every random error of a condition on all the runs.
For each condition and seed the runs are pooled: rates are ratios of sums, counts are means per job, errors are
taken over all the compared states of the runs.  A table gives the mean over seeds, the SD over seeds and a 95 %
confidence interval with Student's t on n_seeds - 1 degrees of freedom.  The 22 scenarios are a designed set, not a
sample: the interval describes the randomness of the perturbations on these runs, not other scenarios.  Intervals
of bounded quantities are truncated to their range (rates to [0, 1], counts and errors at 0).  A paired change
subtracts, run by run, the deterministic G0 baseline job of the same raw data.  Interaction: the GNSS and the
radar errors of a combined job are those of the single-sensor jobs of the same seed, so the interaction of a seed is
its combined change minus the two single-sensor changes.
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
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

# Student's t, two-sided 95 %, by degrees of freedom (larger: the normal 1.96).
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}
FAMILY_ORDER = ("baseline", "gnss", "radar_v3", "radar_asym", "radar_gnss_v3", "radar_asym_gnss")
LEVEL_ORDER = ("none", "rtk", "degraded", "nominal", "severe", "extreme", "gnss rtk + radar nominal",
               "gnss rtk + radar severe", "gnss degraded + radar nominal", "gnss degraded + radar severe")
SUBSETS = ("all", "alone", "all but one")


# ----------------------------------------------------------------------------------------------------------------
# statistics
# ----------------------------------------------------------------------------------------------------------------

def mean_ci(values: Sequence[Optional[float]]) -> Dict[str, Optional[float]]:
    """Mean, SD and 95 % t interval of per-seed values (None values are left out; one value: no SD, no interval)."""
    xs = [float(v) for v in values if v is not None and not math.isnan(float(v))]
    if not xs:
        return {"n": 0, "mean": None, "sd": None, "ci_low": None, "ci_high": None}
    mean = statistics.fmean(xs)
    if len(xs) < 2:
        return {"n": 1, "mean": mean, "sd": None, "ci_low": None, "ci_high": None}
    sd = statistics.stdev(xs)
    half = T95.get(len(xs) - 1, 1.96) * sd / math.sqrt(len(xs))
    return {"n": len(xs), "mean": mean, "sd": sd, "ci_low": mean - half, "ci_high": mean + half}


def quantile(data: Sequence[float], p: float) -> Optional[float]:
    """Linear interpolation between order statistics (as cdf.evaluation.gt_audit.stats)."""
    xs = sorted(data)
    if not xs:
        return None
    position = p * (len(xs) - 1)
    low = int(math.floor(position))
    high = min(low + 1, len(xs) - 1)
    return xs[low] + (xs[high] - xs[low]) * (position - low)


def error_stats(values: Sequence[float]) -> Dict[str, Optional[float]]:
    if not values:
        return {"n": 0, "median": None, "p95": None, "rmse": None}
    return {"n": len(values), "median": quantile(values, 0.5), "p95": quantile(values, 0.95),
            "rmse": math.sqrt(sum(v * v for v in values) / len(values))}


def ratio(numerator: float, denominator: float) -> Optional[float]:
    return numerator / denominator if denominator else None


def bounded(metric: str, interval: Optional[List[float]]) -> Optional[List[float]]:
    """A metric's interval truncated to its feasible range."""
    if interval is None:
        return None
    low, high = interval
    if metric in RATES or metric in DERIVED_RATES or metric in ("coverage_mean", "all_aligned_rate"):
        return [max(0.0, low), min(1.0, high)]
    return [max(0.0, low), high]


# ----------------------------------------------------------------------------------------------------------------
# job records
# ----------------------------------------------------------------------------------------------------------------

def read_jobs(path: Path) -> List[Dict[str, Any]]:
    import robustness
    records = []
    with Path(path).open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:  # a line cut by a crash of the writer: that job stays pending
                    continue
    return robustness.latest_results([r for r in records if r.get("family") in FAMILY_ORDER])


def run_name(run: str) -> str:
    path = Path(str(run).replace("\\", "/"))
    return "{0}/{1}".format(path.parent.name, path.name)


def subset_of(record: Mapping[str, Any]) -> str:
    if record["family"] not in ("radar_asym", "radar_asym_gnss") or not record.get("recorder"):
        return "all"
    return "alone" if len(str(record["recorder"]).split("+")) == 1 else "all but one"


def job_values(record: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    """The numbers of one complete job (None for a failed one)."""
    from cdf.evaluation.scorecard import _numbers
    card = record.get("scorecard")
    if record.get("status") != "complete" or not card:
        return None
    numbers = dict(_numbers(card))
    vehicles = [v for v in card["completeness"].get("vehicles", []) if v.get("role") != "recorder"
                and v.get("observable") and v.get("represented") and v.get("coverage") is not None]
    numbers["coverage_values"] = [float(v["coverage"]) for v in vehicles]
    metrics = record.get("metrics") or {}
    numbers["all_aligned"] = (metrics.get("recorders") is not None
                              and metrics.get("recorders_aligned") == metrics.get("recorders"))
    raw = record.get("road_user_errors_raw") or {}
    numbers["centre_errors"] = list(raw.get("centre_error_m", []))
    numbers["speed_errors"] = list(raw.get("speed_error_mps", []))
    pose = (record.get("pose_errors") or {}).get("absolute_position_m") or {}
    numbers["pose_p95_m"] = pose.get("p95")
    numbers["recorders"] = len(card.get("recorders") or [])
    return numbers


# Per seed, the pooled value of each metric from the jobs of one condition (and their baselines for paired changes).
RATES = {"identified_rate": ("identified", "reportable"), "detected_rate": ("detected", "reportable"),
         "represented_rate": ("represented", "observable"), "ttc_in_time_rate": ("ttc_in_time", "ttc_justified"),
         "intrusions_found_rate": ("intrusions_found", "intrusions_expected")}
# Collisions missed (no node) and misattributed (a node naming the wrong participants), over the reportable ones.
DERIVED_RATES = {"missed_rate": (lambda j: (j.get("reportable") or 0) - (j.get("detected") or 0), "reportable"),
                 "misattributed_rate": (lambda j: (j.get("detected") or 0) - (j.get("identified") or 0), "reportable")}
COUNTS = ("invented", "recontact_splits", "duplicates", "rec_ghosts", "phantoms", "phantoms_near", "phantoms_far",
          "wrong_links", "missed_links", "false_merges", "missed_merges", "unconfirmed_ttc")
ERRORS = (("pos", "centre_errors"), ("spd", "speed_errors"))
METRICS = (list(RATES) + list(DERIVED_RATES) + ["{0}_per_job".format(c) for c in COUNTS] + ["coverage_mean", "all_aligned_rate"]
           + ["{0}_{1}".format(prefix, s) for prefix, _ in ERRORS for s in ("median", "p95", "rmse")]
           + ["pose_p95_m"])


def pooled(jobs: Sequence[Mapping[str, Any]]) -> Dict[str, Optional[float]]:
    """The metrics of a set of complete jobs (one condition, one seed), pooled over their runs."""
    out: Dict[str, Optional[float]] = {}
    total = lambda key: sum((j.get(key) or 0) for j in jobs)  # noqa: E731
    for name, (num, den) in RATES.items():
        out[name] = ratio(total(num), total(den))
    for name, (part, den) in DERIVED_RATES.items():
        out[name] = ratio(sum(part(j) for j in jobs), total(den))
    for count in COUNTS:
        values = [j.get(count) for j in jobs if j.get(count) is not None]
        out["{0}_per_job".format(count)] = statistics.fmean(values) if values else None
    coverage = [c for j in jobs for c in j.get("coverage_values", [])]
    out["coverage_mean"] = statistics.fmean(coverage) if coverage else None
    out["all_aligned_rate"] = ratio(sum(1 for j in jobs if j.get("all_aligned")), len(jobs))
    for prefix, key in ERRORS:
        stats = error_stats([v for j in jobs for v in j.get(key, [])])
        for s in ("median", "p95", "rmse"):
            out["{0}_{1}".format(prefix, s)] = stats[s]
    poses = [j["pose_p95_m"] for j in jobs if j.get("pose_p95_m") is not None]
    out["pose_p95_m"] = statistics.fmean(poses) if poses else None
    return out


# ----------------------------------------------------------------------------------------------------------------
# tables
# ----------------------------------------------------------------------------------------------------------------

Condition = Tuple[str, str, str, str]  # family, level, subset, recorders ("all", "2", "3")


def conditions_of(records: Sequence[Mapping[str, Any]]) -> Dict[Condition, List[Mapping[str, Any]]]:
    """Every record under its condition, once pooled over the runs (recorders "all") and once per number of
    recorders of its run."""
    groups: Dict[Condition, List[Mapping[str, Any]]] = defaultdict(list)
    run_recorders = {run_name(r["run"]): (r.get("scorecard") or {}).get("recorders") for r in records
                     if r.get("scorecard")}
    for r in records:
        recorders = run_recorders.get(run_name(r["run"]))
        n = str(len(recorders)) if recorders else "?"
        for stratum in ("all", n):
            groups[(r["family"], r["level"], subset_of(r), stratum)].append(r)
    return groups


def condition_sort_key(condition: Condition) -> Tuple[Any, ...]:
    family, level, subset, stratum = condition
    return (FAMILY_ORDER.index(family) if family in FAMILY_ORDER else 99,
            LEVEL_ORDER.index(level) if level in LEVEL_ORDER else 99, SUBSETS.index(subset), stratum != "all", stratum)


def baseline_values(records: Sequence[Mapping[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {run_name(r["run"]): job_values(r) for r in records
            if r["family"] == "baseline" and job_values(r) is not None}


def condition_table(records: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    """Per condition and seed the pooled metrics and their paired change from the baselines of the same runs;
    then the mean over seeds, SD and 95 % interval (module docstring)."""
    baselines = baseline_values(records)
    rows = []
    for condition, members in sorted(conditions_of(records).items(), key=lambda item: condition_sort_key(item[0])):
        family, level, subset, stratum = condition
        by_seed: Dict[int, List[Mapping[str, Any]]] = defaultdict(list)
        for r in members:
            by_seed[int(r["seed"])].append(r)
        per_seed, paired = [], []
        failed = 0
        for seed, jobs in sorted(by_seed.items()):
            values = [job_values(j) for j in jobs]
            failed += sum(1 for v in values if v is None)
            complete = [(j, v) for j, v in zip(jobs, values) if v is not None]
            if not complete:
                continue
            here = pooled([v for _, v in complete])
            per_seed.append(here)
            # Paired: the jobs whose run has a complete baseline, against those baselines (a failed baseline
            # leaves its own run out, not the seed).
            pairs = [(v, baselines[run_name(j["run"])]) for j, v in complete if run_name(j["run"]) in baselines]
            if pairs:
                mine, base = pooled([v for v, _ in pairs]), pooled([b for _, b in pairs])
                paired.append({k: (None if mine[k] is None or base[k] is None else mine[k] - base[k]) for k in mine})
        row: Dict[str, Any] = {"family": family, "level": level, "subset": subset, "recorders": stratum,
                               "runs": len({run_name(r["run"]) for r in members}), "seeds": len(per_seed),
                               "jobs": len(members), "failed": failed}
        for metric in METRICS:
            summary = mean_ci([p[metric] for p in per_seed])
            row[metric] = summary["mean"]
            row[metric + "_sd"] = summary["sd"]
            row[metric + "_ci"] = bounded(metric, None if summary["ci_low"] is None
                                          else [summary["ci_low"], summary["ci_high"]])
            d = mean_ci([p[metric] for p in paired])
            row["d_" + metric] = d["mean"]
            row["d_" + metric + "_ci"] = None if d["ci_low"] is None else [d["ci_low"], d["ci_high"]]
        rows.append(row)
    return rows


def seed_values(records: Sequence[Mapping[str, Any]], family: str, level: str, subset: str = "all"
                ) -> Dict[int, Dict[str, Optional[float]]]:
    """Per seed: the paired change of every metric of a full-population condition (all 22 runs)."""
    baselines = baseline_values(records)
    by_seed: Dict[int, List[Mapping[str, Any]]] = defaultdict(list)
    for r in records:
        if r["family"] == family and r["level"] == level and subset_of(r) == subset:
            by_seed[int(r["seed"])].append(r)
    out = {}
    for seed, jobs in by_seed.items():
        complete = [(j, job_values(j)) for j in jobs]
        complete = [(j, v) for j, v in complete if v is not None and baselines.get(run_name(j["run"])) is not None]
        if not complete:
            continue
        here = pooled([v for _, v in complete])
        base = pooled([baselines[run_name(j["run"])] for j, _ in complete])
        out[seed] = {k: (None if here[k] is None or base[k] is None else here[k] - base[k]) for k in here}
    return out


def interaction_table(records: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    """GNSS x radar: per seed, the combined change minus the GNSS change and the radar change of the same seed
    (the combined job draws exactly their errors)."""
    rows = []
    for gnss in ("rtk", "degraded"):
        for radar in ("nominal", "severe"):
            combined = seed_values(records, "radar_gnss_v3", "gnss {0} + radar {1}".format(gnss, radar))
            alone_g, alone_r = seed_values(records, "gnss", gnss), seed_values(records, "radar_v3", radar)
            seeds = sorted(set(combined) & set(alone_g) & set(alone_r))
            row: Dict[str, Any] = {"gnss": gnss, "radar": radar, "seeds": len(seeds)}
            for metric in METRICS:
                inter = []
                for s in seeds:
                    parts = (combined[s][metric], alone_g[s][metric], alone_r[s][metric])
                    inter.append(None if None in parts else parts[0] - parts[1] - parts[2])
                summary = mean_ci(inter)
                row[metric + "_combined"] = mean_ci([combined[s][metric] for s in seeds])["mean"]
                row[metric + "_additive"] = mean_ci([None if None in (alone_g[s][metric], alone_r[s][metric])
                                                     else alone_g[s][metric] + alone_r[s][metric] for s in seeds])["mean"]
                row[metric + "_interaction"] = summary["mean"]
                row[metric + "_interaction_ci"] = (None if summary["ci_low"] is None
                                                   else [summary["ci_low"], summary["ci_high"]])
            rows.append(row)
    return rows


ASYM_METRICS = ("phantoms_per_job", "represented_rate", "duplicates_per_job", "rec_ghosts_per_job",
                "identified_rate", "pos_median", "pos_p95", "wrong_links_per_job", "missed_links_per_job")


def asymmetry_table(conditions: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    """One, several or all radars degraded, per radar level, GNSS (ideal or G2) and number of recorders."""
    index = {(c["family"], c["level"], c["subset"], c["recorders"]): c for c in conditions}
    rows = []
    for gnss, asym, full, label in (("G0", "radar_asym", "radar_v3", "{0}"),
                                    ("G2", "radar_asym_gnss", "radar_gnss_v3", "gnss degraded + radar {0}")):
        for level in ("nominal", "severe", "extreme"):
            for stratum in ("2", "3"):
                cells = [("1 (alone)", index.get((asym, label.format(level), "alone", stratum))),
                         ("all but one", index.get((asym, label.format(level), "all but one", stratum))),
                         ("all", index.get((full, label.format(level), "all", stratum)))]
                for degraded, cell in cells:
                    if cell is None:
                        continue
                    row = {"gnss": gnss, "radar": level, "recorders": stratum, "degraded": degraded,
                           "seeds": cell["seeds"], "jobs": cell["jobs"]}
                    for metric in ASYM_METRICS:
                        row[metric] = cell.get(metric)
                        row[metric + "_ci"] = cell.get(metric + "_ci")
                        row["d_" + metric] = cell.get("d_" + metric)
                    rows.append(row)
    return rows


SCENARIO_METRICS = ("identified", "reportable", "invented", "represented", "observable", "duplicates", "phantoms",
                    "rec_ghosts", "wrong_links", "pos_med_m")


def scenario_table(records: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    """Per run and condition: each headline number as the mean over seeds, with its minimum and maximum over the
    seeds (the seed variability of that scenario)."""
    groups: Dict[Tuple[str, str, str, str, str], List[Dict[str, Any]]] = defaultdict(list)
    for r in records:
        values = job_values(r)
        if values is not None:
            groups[(run_name(r["run"]), r["family"], r["level"], subset_of(r), r.get("recorder") or "all")].append(values)
    rows = []
    for (run, family, level, subset, degraded), values in sorted(groups.items()):
        row: Dict[str, Any] = {"run": run, "family": family, "level": level, "subset": subset, "degraded": degraded,
                               "seeds": len(values)}
        for metric in SCENARIO_METRICS:
            xs = [v[metric] for v in values if v.get(metric) is not None]
            row[metric] = statistics.fmean(xs) if xs else None
            row[metric + "_min"] = min(xs) if xs else None
            row[metric + "_max"] = max(xs) if xs else None
        rows.append(row)
    return rows


def failures(records: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    return [{"run": run_name(r["run"]), "family": r["family"], "level": r["level"], "recorder": r.get("recorder"),
             "seed": r["seed"], "attempt": r.get("attempt"), "status": r.get("status"),
             "error": r.get("error") or (r.get("evaluation_errors") or {}).get("scorecard")}
            for r in records if r.get("status") != "complete" or not r.get("scorecard")]


# ----------------------------------------------------------------------------------------------------------------
# output
# ----------------------------------------------------------------------------------------------------------------

def _plain(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, 6)
    if isinstance(value, list):
        return json.dumps([_plain(v) for v in value])
    return value


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    keys: List[str] = []
    for row in rows:
        keys += [k for k in row if k not in keys]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows({k: _plain(row.get(k)) for k in keys} for row in rows)


def _cell(row: Mapping[str, Any], key: str, decimals: int, ci: bool = True) -> str:
    value = row.get(key)
    if value is None:
        return "-"
    text = "{0:.{1}f}".format(value, decimals)
    interval = row.get(key + "_ci") if ci else None
    return text + (" [{0:.{2}f}, {1:.{2}f}]".format(interval[0], interval[1], decimals) if interval else "")


HEADLINE = (("identified_rate", "collisions identified", 3), ("missed_rate", "missed", 3),
            ("misattributed_rate", "misattributed", 3), ("invented_per_job", "invented / job", 2),
            ("represented_rate", "observable represented", 3), ("coverage_mean", "coverage", 3),
            ("duplicates_per_job", "duplicates / job", 2), ("phantoms_per_job", "phantoms / job", 1),
            ("rec_ghosts_per_job", "recorder ghosts / job", 2), ("wrong_links_per_job", "wrong links / job", 2),
            ("pos_median", "position median [m]", 3), ("pos_p95", "position P95 [m]", 3),
            ("pos_rmse", "position RMSE [m]", 3), ("spd_median", "speed median [m/s]", 3),
            ("ttc_in_time_rate", "CRITICAL_TTC in time", 3))


def conditions_markdown(rows: Sequence[Mapping[str, Any]], stratum: str = "all") -> str:
    head = ["family", "level", "degraded", "seeds", "jobs", "failed"] + [h for _, h, _ in HEADLINE]
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for row in rows:
        if row["recorders"] != stratum:
            continue
        out.append("| " + " | ".join([row["family"], row["level"], row["subset"], str(row["seeds"]), str(row["jobs"]),
                                      str(row["failed"])] + [_cell(row, k, d) for k, _, d in HEADLINE]) + " |")
    return "\n".join(out) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--jobs", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--no-figures", action="store_true")
    args = parser.parse_args(argv)
    records = read_jobs(args.jobs)
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    table = condition_table(records)
    interaction = interaction_table(records)
    asymmetry = asymmetry_table(table)
    scenarios = scenario_table(records)
    failed = failures(records)
    write_csv(out / "conditions.csv", table)
    write_csv(out / "interaction.csv", interaction)
    write_csv(out / "asymmetry.csv", asymmetry)
    write_csv(out / "scenarios.csv", scenarios)
    write_csv(out / "failures.csv", failed or [{"run": None}])
    (out / "report_data.json").write_text(json.dumps({"conditions": table, "interaction": interaction,
                                                       "asymmetry": asymmetry, "failures": failed},
                                                      indent=1, default=str) + "\n", encoding="utf-8")
    (out / "conditions.md").write_text(
        "# Campaign v3: reconstruction per condition (all 22 runs)\n\nMean over seeds [95 % t interval over seeds]; "
        "definitions in `scripts/campaign_v3_report.py` and `cdf.evaluation.scorecard`.\n\n"
        + conditions_markdown(table, "all")
        + "\n## Runs with two recorders\n\n" + conditions_markdown(table, "2")
        + "\n## Runs with three recorders\n\n" + conditions_markdown(table, "3"), encoding="utf-8")
    figures: List[Path] = []
    if not args.no_figures:
        import campaign_v3_figures
        figures = campaign_v3_figures.draw(table, interaction, asymmetry, scenarios, out / "figures")
    jobs = len(records)
    complete = sum(1 for r in records if r.get("status") == "complete" and r.get("scorecard"))
    print("{0} jobs ({1} complete, {2} failed or without scorecard); {3} condition rows; {4} figures -> {5}".format(
        jobs, complete, jobs - complete, len(table), len(figures), out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
