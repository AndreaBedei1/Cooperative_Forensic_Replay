#!/usr/bin/env python3
"""Core perception events against the ground-truth event oracle (privileged: evaluation side).

    python scripts/event_oracle.py traces/S*/run_* --label canonical [--workers 8]
    python scripts/event_oracle.py sweeps/*/S*/run_* --label sweeps

Per run (``cdf.evaluation.event_oracle``): the PERFECT and COVERAGE oracle events of every recorder, the
reconstruction's own, their matches and time differences, written to
``<run>/reconstruction/evaluation/event_oracle.json``.  Pooled over the runs:
``results/semantics/event_oracle_<label>.{json,md,csv}`` and ``figures/event_oracle_<label>.{svg,pdf}``.
A run needs its reconstruction and privileged evaluation (``evaluation.json``: the true identity of each
track).
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

LABELS = {"TRACK_APPEARED": "track appeared", "EGO_PATH_ENTRY": "ego-path entry",
          "CUT_IN_FROM_LEFT_START": "cut-in from left", "CUT_IN_FROM_RIGHT_START": "cut-in from right",
          "CRITICAL_TTC_START": "CRITICAL_TTC start", "CRITICAL_TTC_END": "CRITICAL_TTC end"}


def one_run(run: str) -> Dict[str, Any]:
    from cdf.evaluation.event_oracle import compare_run
    from cdf.reconstruction.config import load_config
    run_dir = Path(run)
    try:
        result = compare_run(run_dir, load_config())
    except Exception as exc:  # recorded; the campaign goes on
        return {"run": run, "error": repr(exc)}
    out = run_dir / "reconstruction" / "evaluation" / "event_oracle.json"
    out.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    return result


def markdown(record: Dict[str, Any]) -> str:
    prov = record["provenance"]
    lines = ["# Core events against the ground-truth event oracle ({0})".format(record["label"]), "",
             "Privileged evaluation (`cdf.evaluation.event_oracle`).  PERFECT: the reconstruction's own event "
             "definitions applied to an ideal track of every other vehicle built from ground truth (true near "
             "surface, velocity, acceleration and size; an all-seeing sensor).  COVERAGE: the same ideal track only "
             "where the vehicle was inside one of the recorder's radar fields of view and range with a clear line of "
             "sight.  RECONSTRUCTION: the recorder's own local events, the subject being the true identity of its "
             "track.  Events of one type, recorder and true subject matched one to one, nearest first, within "
             "{0} s; time difference = found - expected (positive: later).  Recorder clocks: local (the alignment "
             "plays no part here).".format(record["match_window_s"]), "",
             "Runs: {0} ({1} failed).  Provenance: code `{2}`, configuration `{3}`, commit `{4}`{5}, {6}.".format(
                 record["runs"], len(record["failed"]), prov["code_sha256"][:16], (prov.get("config_sha256") or "")[:16],
                 prov["git_commit"], " (uncommitted changes)" if prov["git_dirty"] else "", prov["generated_utc"]), ""]
    for window, title in (("pooled_pre_contact", "before each recorder's first contact"), ("pooled", "whole recording")):
        for comparison, rows in record[window].items():
            lines += ["## {0} ({1})".format(comparison, title), "",
                      "| event | found | expected | matched | precision | recall | dt median [s] | dt p5 / p95 [s] | |dt| median [s] |",
                      "|---|--:|--:|--:|--:|--:|--:|--:|--:|"]
            for event_type, row in rows.items():
                lines.append("| {0} | {1} | {2} | {3} | {4} | {5} | {6} | {7} | {8} |".format(
                    LABELS[event_type], row["found"], row["expected"], row["matched"],
                    "-" if row["precision"] is None else "{0:.3f}".format(row["precision"]),
                    "-" if row["recall"] is None else "{0:.3f}".format(row["recall"]),
                    "-" if row["delta_median_s"] is None else "{0:+.2f}".format(row["delta_median_s"]),
                    "-" if row["delta_p05_s"] is None else "{0:+.2f} / {1:+.2f}".format(row["delta_p05_s"], row["delta_p95_s"]),
                    "-" if row["abs_delta_median_s"] is None else "{0:.2f}".format(row["abs_delta_median_s"])))
            lines.append("")
    return "\n".join(lines) + "\n"


def figure(record: Dict[str, Any], results: Sequence[Dict[str, Any]], out: Path, window: str) -> None:
    """Time differences of the matched events (reconstruction vs COVERAGE, COVERAGE vs PERFECT), and
    recall / precision of the reconstruction against COVERAGE, in one window (pre-contact for the paper)."""
    from cdf.evaluation.figures import DOUBLE_COLUMN_IN, paper_style
    plt = paper_style()
    types = [t for t in LABELS if any(r[window]["RECONSTRUCTION vs COVERAGE"][t]["deltas"] for r in results)]
    if not types:
        return
    fig, axes = plt.subplots(1, 2, figsize=(DOUBLE_COLUMN_IN, 3.0))
    for offset, (key, colour) in enumerate((("RECONSTRUCTION vs COVERAGE", "tab:blue"), ("COVERAGE vs PERFECT", "tab:orange"))):
        data = [[d for r in results for d in r[window][key][t]["deltas"]] for t in types]
        positions = [i * 3 + offset for i in range(len(types))]
        kept = [(p, d) for p, d in zip(positions, data) if d]
        if kept:
            parts = axes[0].boxplot([d for _, d in kept], positions=[p for p, _ in kept], widths=0.8, patch_artist=True,
                                    showfliers=True, flierprops={"markersize": 2})
            for patch in parts["boxes"]:
                patch.set_facecolor(colour)
                patch.set_alpha(0.5)
        axes[0].plot([], [], color=colour, linewidth=6, alpha=0.5, label=key.lower())
    axes[0].axhline(0.0, color="grey", linewidth=0.8)
    axes[0].set_xticks([i * 3 + 0.5 for i in range(len(types))])
    axes[0].set_xticklabels([LABELS[t] for t in types], rotation=25, ha="right")
    axes[0].set_ylabel("time difference [s]")
    axes[0].legend()
    axes[0].set_title("matched events: found - expected")
    pooled = record["pooled_pre_contact" if window == "comparison_pre_contact" else "pooled"]["RECONSTRUCTION vs COVERAGE"]
    xs = range(len(types))
    axes[1].bar([x - 0.2 for x in xs], [pooled[t]["recall"] or 0.0 for t in types], width=0.4, label="recall")
    axes[1].bar([x + 0.2 for x in xs], [pooled[t]["precision"] or 0.0 for t in types], width=0.4, label="precision")
    axes[1].set_xticks(list(xs))
    axes[1].set_xticklabels([LABELS[t] for t in types], rotation=25, ha="right")
    axes[1].set_ylim(0.0, 1.05)
    axes[1].legend()
    axes[1].set_title("reconstruction vs. COVERAGE oracle (pre-contact)")
    for axis in axes:
        axis.grid(alpha=0.3)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    for suffix in ("svg", "pdf"):
        fig.savefig(str(out.with_suffix("." + suffix)), bbox_inches="tight")
    plt.close(fig)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("runs", nargs="+", type=Path)
    parser.add_argument("--label", required=True)
    parser.add_argument("--results", type=Path, default=ROOT / "results" / "semantics")
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args(argv)
    from cdf.evaluation.event_oracle import CORE_TYPES, MATCH_WINDOW_S, pooled
    from cdf.evaluation.provenance import provenance
    from cdf.reconstruction.config import load_config
    runs = [str(run) for run in args.runs if (run / "reconstruction" / "evaluation" / "evaluation.json").exists()]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(one_run, runs))
    done = [r for r in results if "error" not in r]
    failed = [{"run": r["run"], "error": r["error"]} for r in results if "error" in r]
    record = {"definition": "core perception events of the reconstruction against the ground-truth event oracle "
                            "(cdf.evaluation.event_oracle); privileged evaluation",
              "label": args.label, "match_window_s": MATCH_WINDOW_S, "event_types": list(CORE_TYPES),
              "provenance": provenance(load_config().to_dict(), [r["run"] for r in done]),
              "runs": len(done), "failed": failed, "pooled": pooled(done),
              "pooled_pre_contact": pooled(done, "comparison_pre_contact")}
    args.results.mkdir(parents=True, exist_ok=True)
    base = args.results / "event_oracle_{0}".format(args.label)
    base.with_suffix(".json").write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    base.with_suffix(".md").write_text(markdown(record), encoding="utf-8")
    with base.with_suffix(".csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["window", "comparison", "event", "found", "expected", "matched", "precision", "recall",
                         "delta_median_s", "delta_p05_s", "delta_p95_s", "abs_delta_median_s"])
        for window, name in (("pooled_pre_contact", "pre_contact"), ("pooled", "whole")):
            for comparison, rows in record[window].items():
                for event_type, row in rows.items():
                    writer.writerow([name, comparison, event_type, row["found"], row["expected"], row["matched"],
                                     row["precision"], row["recall"], row["delta_median_s"], row["delta_p05_s"],
                                     row["delta_p95_s"], row["abs_delta_median_s"]])
    figure(record, done, args.results / "figures" / "event_oracle_{0}".format(args.label), "comparison_pre_contact")
    print(markdown(record))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
