#!/usr/bin/env python3
"""Privileged evaluation of the road-user fusion over a set of reconstructed runs (evaluation only).

    python scripts/fusion_metrics.py traces/*/run_* [--out traces/fusion_metrics]

Per run: ``<run>/reconstruction/evaluation/fusion_metrics.json|md`` (``cdf.evaluation.fusion_metrics``).
Campaign: ``<out>.json|md`` -- identity decisions, merges and fragmentation summed over the runs, the
pooled distributions of the fused state errors, the observed-trajectory alignments, and the provenance
of the numbers (code and configuration hashes, git commit, runs, time).  Ground truth is read here only,
after the reconstruction was written.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cdf.evaluation.fusion_metrics import EXPECTED_WITHIN, evaluate_fusion, stats_lines  # noqa: E402
from cdf.evaluation.gt_audit import stats  # noqa: E402
from cdf.evaluation.provenance import provenance  # noqa: E402
from cdf.reconstruction.config import load_config  # noqa: E402
from cdf.reconstruction.render import write_json, write_text  # noqa: E402


def _cell(value) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return "{0:.3f}".format(value)
    return str(value)


def main() -> int:
    parser = argparse.ArgumentParser(description="Road-user fusion against ground truth (privileged)")
    parser.add_argument("run_dirs", nargs="+", type=Path)
    parser.add_argument("--out", type=Path, default=ROOT / "traces" / "fusion_metrics",
                        help="campaign output path without extension (default traces/fusion_metrics)")
    args = parser.parse_args()
    runs = sorted(path for path in args.run_dirs if (path / "reconstruction" / "global" / "anonymous_entities.json").exists())
    pooled = defaultdict(list)
    by_method = defaultdict(lambda: defaultdict(list))
    counts, merges, within = Counter(), Counter(), Counter()
    normalised = impure = compared = 0
    rows, alignments, entities = [], [], []
    for run in runs:
        result = evaluate_fusion(run)
        raw = result.pop("_raw", None)
        counts.update(result["decision_counts"])
        merges.update(result["merges"])
        for entity in result["entities"]:
            entities.append(dict(entity, run=result["run"]))
        for key, values in (raw or {}).get("errors", {}).items():
            pooled[key] += values
        for method, table in (raw or {}).get("by_method", {}).items():
            for key, values in table.items():
                by_method[method][key] += values
        calibration = result["calibration"]
        normalised += calibration["states"]
        impure += result["impure_states"]
        compared += result["states_compared"]
        for key in EXPECTED_WITHIN:
            within[key] += calibration["observed_within"][key] * calibration["states"]
        for item in result["observed_alignment"]:
            alignments.append(dict(item, run=result["run"]))
        rows.append({"run": result["run"], "decision_counts": result["decision_counts"], "merges": result["merges"],
                     "entities": len(result["entities"]),
                     "false_entities_of_recorders": sum(e["identity_is_recorder"] for e in result["entities"]),
                     "fragmentation": result["fragmentation"],
                     "centre_error_median_m": result["state_errors"].get("centre_error_m", {}).get("median"),
                     "single_track_centre_error_median_m":
                         result["state_errors"].get("single_track_nominal_centre_error_m", {}).get("median")})
    cfg = load_config()
    fragments = [len(ids) for row in rows for ids in row["fragmentation"].values()]
    purity = [e["purity"] for e in entities if e["purity"] is not None]
    campaign = {
        "definition": "road-user fusion against ground truth: identity decisions of the aligned recorders' tracks, "
                      "merges over pairs of anonymous tracks, fragmentation of each true road user over anonymous "
                      "entities, pooled fused-state errors against the entity's majority identity, observed-"
                      "trajectory alignments",
        "provenance": provenance(cfg.to_dict(), [r["run"] for r in rows]),
        "decision_counts": dict(sorted(counts.items())),
        "merges": dict(merges),
        "entities": len(entities),
        "entity_purity": stats(purity),
        "entities_per_true_road_user": stats(fragments),
        "states_compared": compared,
        "impure_states": impure,
        "pooled_state_errors": {key: stats(values) for key, values in sorted(pooled.items())},
        "pooled_state_errors_by_method": {method: {key: stats(values) for key, values in sorted(table.items())}
                                          for method, table in sorted(by_method.items())},
        "calibration": {"states": normalised,
                        "observed_within": {k: round(within[k] / max(normalised, 1), 3) for k in EXPECTED_WITHIN},
                        "expected_within_gaussian": {k: round(v, 3) for k, v in EXPECTED_WITHIN.items()}},
        "observed_alignment": alignments,
        "runs": rows,
    }
    write_json(args.out.with_suffix(".json"), campaign)
    lines = ["# Road-user fusion against ground truth (campaign)", "",
             "Privileged evaluation: ground truth is read only here, after the reconstruction was written. "
             "Provenance: commit `{0}`{1}, code `{2}`, configuration `{3}`, {4}.".format(
                 campaign["provenance"]["git_commit"], " (uncommitted changes)" if campaign["provenance"]["git_dirty"] else "",
                 campaign["provenance"]["code_sha256"][:16], campaign["provenance"]["config_sha256"][:16],
                 campaign["provenance"]["generated_utc"]), "",
             "## Identity decisions (tracks of aligned recorders)", "",
             ", ".join("{0}: {1}".format(k, v) for k, v in campaign["decision_counts"].items()), "",
             "Merges over pairs of anonymous tracks: correct {0}, false {1}, missed {2}. Anonymous entities: {3} "
             "(purity median {4}, min {5}); entities per true road user: median {6}, max {7}.".format(
                 merges["correct"], merges["false"], merges["missed"], len(entities),
                 _cell(campaign["entity_purity"]["median"]), _cell(min(purity) if purity else None),
                 _cell(campaign["entities_per_true_road_user"]["median"]),
                 _cell(campaign["entities_per_true_road_user"]["max"])), "",
             "## Per run", "",
             "| Run | Decisions | Merges c/f/m | Entities | Of recorders | Fragmentation | Fused centre err. median | Single-track centre err. median |",
             "|-----|-----------|--------------|---------:|-------------:|---------------|-------------------------:|--------------------------------:|"]
    for row in rows:
        lines.append("| {0} | {1} | {2}/{3}/{4} | {5} | {6} | {7} | {8} | {9} |".format(
            row["run"], ", ".join("{0} {1}".format(v, k) for k, v in row["decision_counts"].items()),
            row["merges"]["correct"], row["merges"]["false"], row["merges"]["missed"], row["entities"],
            row["false_entities_of_recorders"],
            ", ".join("{0}->{1}".format(pid, "/".join(ids)) for pid, ids in row["fragmentation"].items()) or "-",
            _cell(row["centre_error_median_m"]), _cell(row["single_track_centre_error_median_m"])))
    lines += ["", "## Pooled fused-state errors", "",
              "Against the entity's majority identity, at the {0} instants every source track was on it; {1} "
              "impure instants (a source track on another body: an association error) are excluded.".format(
                  compared, impure), ""] + stats_lines(campaign["pooled_state_errors"])
    for method, table in campaign["pooled_state_errors_by_method"].items():
        lines += ["", "### Method: " + method, ""] + stats_lines(table)
    calibration = campaign["calibration"]
    lines += ["", "Calibration of the declared position uncertainty over {0} states: within 1/2/3 sigma {1} "
              "(a Gaussian would give {2}).".format(
                  calibration["states"], "/".join(_cell(calibration["observed_within"][k]) for k in EXPECTED_WITHIN),
                  "/".join(_cell(calibration["expected_within_gaussian"][k]) for k in EXPECTED_WITHIN))]
    if alignments:
        lines += ["", "## Observed-trajectory alignment", "",
                  "| Run | Recorder | Accepted | Estimated | True | Error | Interval |",
                  "|-----|----------|----------|----------:|-----:|------:|----------|"]
        for item in alignments:
            lines.append("| {0} | {1} | {2} | {3} | {4} | {5} | {6} |".format(
                item["run"], item["recorder"], item["accepted"], _cell(item["estimated_offset_s"]),
                _cell(item["true_offset_s"]), _cell(item["error_s"]), _cell(item["interval"])))
    write_text(args.out.with_suffix(".md"), "\n".join(lines) + "\n")
    print("{0} runs; decisions {1}; merges {2}".format(len(rows), dict(counts), dict(merges)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
