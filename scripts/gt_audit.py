#!/usr/bin/env python3
"""Privileged ground-truth audit of reconstructed runs (evaluation only).

    python scripts/gt_audit.py traces/S*/run_* --name gt_audit_baseline

Per run: ``<run>/reconstruction/evaluation/<name>.json`` and ``.md`` (collisions, associations, track
identity purity and error distributions, CRITICAL_TTC and CUT_IN start geometry against the truth);
campaign: ``traces/<name>.json`` and ``.md`` with the errors pooled over every track sample.  Errors are
in physical units (m, m/s, deg), distributions as median / IQR / p90 / p95 / max.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cdf.evaluation.gt_audit import ERROR_KEYS, gt_audit_run, stats  # noqa: E402

LABELS = {"centre_error_m": "box centre error [m]", "surface_error_m": "track point to true outline [m]",
          "speed_error_mps": "speed error [m/s]", "velocity_error_mps": "velocity vector error [m/s]",
          "heading_error_deg": "heading error [deg]"}


def _commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True, text=True,
                              check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _fmt(value: Any, digits: int = 2) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return "{0:.{1}f}".format(value, digits)
    return str(value)


def stats_table(pooled: Dict[str, Dict[str, Any]]) -> List[str]:
    lines = ["| quantity | n | median | IQR | p90 | p95 | max |", "|---|---|---|---|---|---|---|"]
    for key in ERROR_KEYS:
        s = pooled[key]
        lines.append("| {0} | {1} | {2} | {3} | {4} | {5} | {6} |".format(
            LABELS[key], s["n"], _fmt(s["median"]), _fmt(s["iqr"]), _fmt(s["p90"]), _fmt(s["p95"]), _fmt(s["max"])))
    return lines


def run_markdown(result: Dict[str, Any], commit: str) -> str:
    lines = ["# Ground-truth audit (privileged, evaluation only): {0}".format(result["run"]), "",
             "Reconstruction result vs ground truth; the reconstruction never reads these files.", "",
             "## Tracks", "",
             "| track | samples | identity | purity | switches | unmatched | centre err. median / p95 [m] | "
             "speed err. median / p95 [m/s] | heading err. median / p95 [deg] |",
             "|---|---|---|---|---|---|---|---|---|"]
    for item in result["tracks"]:
        lines.append("| {0} | {1} | {2} | {3} | {4} | {5} | {6} / {7} | {8} / {9} | {10} / {11} |".format(
            item["track"], item["samples"], item["identity"], _fmt(item["purity"], 3), item["identity_switches"],
            item["unmatched_samples"], _fmt(item["centre_error_m"]["median"]), _fmt(item["centre_error_m"]["p95"]),
            _fmt(item["speed_error_mps"]["median"]), _fmt(item["speed_error_mps"]["p95"]),
            _fmt(item["heading_error_deg"]["median"], 1), _fmt(item["heading_error_deg"]["p95"], 1)))
    lines += ["", "## Pooled track errors (every track sample)", ""] + stats_table(result["pooled_track_errors"])
    lines += ["", "## CRITICAL_TTC_START geometry", "",
              "| recorder | track | true identity | t_local [s] | reason | clearance rec / true [m] | body gap rec / true [m] | "
              "bumper gap true [m] | d_min [m] |", "|---|---|---|---|---|---|---|---|---|"]
    for row in result["critical_ttc_starts"]:
        lines.append("| {0} | {1} | {2} | {3:.2f} | {4} | {5} / {6} | {7} / {8} | {9} | {10} |".format(
            row["recorder"], row["track"], row["true_identity"], row["t_local"], row.get("reason") or "-",
            _fmt(row.get("clearance_m")), _fmt(row.get("true_clearance_m")), _fmt(row.get("body_gap_m")),
            _fmt(row.get("true_body_gap_m")), _fmt(row.get("true_bumper_gap_m")), _fmt(row.get("d_min_m"))))
    lines += ["", "## CUT_IN start geometry", "",
              "| recorder | track | true identity | t_local [s] | direction | body gap rec / true [m] | "
              "lateral speed rec / true [m/s] |", "|---|---|---|---|---|---|---|"]
    for row in result["cut_in_starts"]:
        lines.append("| {0} | {1} | {2} | {3:.2f} | {4} | {5} / {6} | {7} / {8} |".format(
            row["recorder"], row["track"], row["true_identity"], row["t_local"], row.get("direction", "-"),
            _fmt(row.get("body_gap_m")), _fmt(row.get("true_body_gap_m")), _fmt(row.get("lateral_speed_mps")),
            _fmt(row.get("true_lateral_speed_mps"))))
    lines += ["", "## Collisions and associations (from evaluation.json)", ""]
    for contact in result.get("collisions") or []:
        lines.append("- {0}".format(json.dumps(contact, sort_keys=True)))
    lines.append("- extra reconstructed collisions: {0}".format(len(result.get("extra_collisions") or [])))
    for item in result.get("associations") or []:
        lines.append("- {0}: {1} ({2}), true identity {3}".format(item["track"], item["decision"], item["status"],
                                                                 item.get("true_identity")))
    lines += ["", "Reconstruction commit: `{0}`.".format(commit), ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Privileged ground-truth audit (evaluation only)")
    parser.add_argument("runs", nargs="+", type=Path)
    parser.add_argument("--name", default="gt_audit_baseline")
    parser.add_argument("--index", type=Path, default=ROOT / "traces")
    args = parser.parse_args()
    commit = _commit()
    pooled: Dict[str, List[float]] = {key: [] for key in ERROR_KEYS}
    pooled_anonymous: Dict[str, List[float]] = {key: [] for key in ERROR_KEYS}
    summary = []
    for run_dir in args.runs:
        result = gt_audit_run(run_dir)
        for key in ERROR_KEYS:
            pooled[key] += result["_raw"][key]
            pooled_anonymous[key] += result["_raw_anonymous"][key]
        result.pop("_raw")
        result.pop("_raw_anonymous")
        result["reconstruction_commit"] = commit
        out = run_dir / "reconstruction" / "evaluation"
        (out / (args.name + ".json")).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        (out / (args.name + ".md")).write_text(run_markdown(result, commit), encoding="utf-8")
        tracks = result["tracks"]
        summary.append({"run": result["run"], "tracks": len(tracks),
                        "impure_tracks": [t["track"] for t in tracks if t["purity"] is not None and t["purity"] < 0.95],
                        "switching_tracks": [t["track"] for t in tracks if t["identity_switches"]],
                        "centre_error_median_m": result["pooled_track_errors"]["centre_error_m"]["median"],
                        "centre_error_p95_m": result["pooled_track_errors"]["centre_error_m"]["p95"],
                        "critical_starts": len(result["critical_ttc_starts"]), "cut_ins": len(result["cut_in_starts"])})
        print(result["run"], "tracks", len(tracks), "centre median",
              result["pooled_track_errors"]["centre_error_m"]["median"])
    campaign = {"privileged": "ground truth used for evaluation only", "reconstruction_commit": commit,
                "runs": summary, "pooled_track_errors": {key: stats(values) for key, values in pooled.items()},
                "pooled_anonymous_track_errors": {key: stats(values) for key, values in pooled_anonymous.items()}}
    (args.index / (args.name + ".json")).write_text(json.dumps(campaign, indent=1, sort_keys=True) + "\n",
                                                    encoding="utf-8")
    lines = ["# Ground-truth audit ({0}), campaign".format(args.name), "",
             "Privileged evaluation only.  Per-run details in each run's reconstruction/evaluation/{0}.md.".format(args.name),
             "", "## All tracks, every sample", ""] + stats_table(campaign["pooled_track_errors"])
    lines += ["", "## Anonymous tracks only", ""] + stats_table(campaign["pooled_anonymous_track_errors"])
    lines += ["", "## Runs", "", "| run | tracks | impure (<95 %) | identity switches | centre err. median / p95 [m] | "
              "CRITICAL_TTC starts | CUT_IN starts |", "|---|---|---|---|---|---|---|"]
    for row in summary:
        lines.append("| {0} | {1} | {2} | {3} | {4} / {5} | {6} | {7} |".format(
            row["run"], row["tracks"], ", ".join(row["impure_tracks"]) or "-", ", ".join(row["switching_tracks"]) or "-",
            _fmt(row["centre_error_median_m"]), _fmt(row["centre_error_p95_m"]), row["critical_starts"], row["cut_ins"]))
    lines += ["", "Reconstruction commit: `{0}`.".format(commit), ""]
    (args.index / (args.name + ".md")).write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
