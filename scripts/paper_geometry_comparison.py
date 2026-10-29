#!/usr/bin/env python3
"""Derive paired geometric comparisons from the canonical G0 reconstructions.

The estimator is not rerun. ``evaluate_fusion(write=False)`` reads existing
reconstructions and ground truth; this script writes only the requested JSON
and Markdown publication summaries. Run from any directory with the project's
Python dependencies installed.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import platform
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Sequence


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cdf.evaluation.fusion_metrics import evaluate_fusion  # noqa: E402
from cdf.evaluation.gt_audit import stats  # noqa: E402


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _manifest(paths: Sequence[Path]) -> List[Dict[str, str]]:
    return [{"path": path.relative_to(ROOT).as_posix(), "sha256": _hash(path)}
            for path in sorted(set(paths))]


def _summarize(states: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    reference = [state["single_track_error_median_m"] for state in states]
    reconstructed = [state["centre_error_m"] for state in states]
    assert len(reference) == len(reconstructed)
    assert all(math.isfinite(value) and value >= 0 for value in reference + reconstructed)
    improved = sum(after < before for before, after in zip(reference, reconstructed))
    worsened = sum(after > before for before, after in zip(reference, reconstructed))
    equal = sum(after == before for before, after in zip(reference, reconstructed))
    assert improved + worsened + equal == len(states)
    return {
        "paired_states": len(states),
        "nominal_source_boxes_centre_error_m": stats(reference),
        "body_reconstruction_and_fusion_centre_error_m": stats(reconstructed),
        "paired_error_change_m": stats(after - before for before, after in zip(reference, reconstructed)),
        "states_improved": improved,
        "states_worsened": worsened,
        "states_equal": equal,
        "fraction_states_improved": improved / len(states) if states else None,
        "reconstruction_methods": dict(sorted(Counter(state["method"] for state in states).items())),
        "available_nominal_boxes_per_state": {
            str(key): count for key, count in sorted(
                Counter(len(state["single_track_centre_errors_m"]) for state in states).items())
        },
    }


def extract() -> Dict[str, Any]:
    canonical_path = ROOT / "results/g0_final/scorecard.json"
    canonical = json.loads(canonical_path.read_text(encoding="utf-8"))
    names = sorted(card["run"] for card in canonical)
    assert len(names) == len(set(names)) == 22
    runs = [ROOT / "traces" / name for name in names]
    reconstruction_paths = [path for run in runs for path in (run / "reconstruction").rglob("*")
                            if path.is_file()]
    before = _manifest(reconstruction_paths)
    input_paths = [canonical_path, ROOT / "configs/reconstruction.yaml"]
    for run in runs:
        input_paths.append(run / "ground_truth/states.jsonl")
        input_paths.extend(path for path in (run / "reconstruction").rglob("*")
                           if path.is_file() and path.suffix in (".json", ".jsonl"))
        input_paths.extend(path for path in (run / "vehicles").glob("*/*.json*")
                           if path.name in ("ego.jsonl", "metadata.json"))

    pooled: List[Dict[str, Any]] = []
    rows = []
    counts: Counter = Counter()
    for run in runs:
        result = evaluate_fusion(run, write=False)
        entity_rows = {entity["id"]: entity for entity in result["entities"]}
        eligible_ids = {key for key, entity in entity_rows.items()
                        if entity["true_identity"] is not None and not entity["identity_is_recorder"]}
        pure_states = result["_raw"]["paired_states"]
        assert len(pure_states) == result["states_compared"]
        ghost_states = [state for state in pure_states
                        if entity_rows[state["entity"]]["identity_is_recorder"]]
        road_user_states = [state for state in pure_states if state["entity"] in eligible_ids]
        paired = [state for state in road_user_states if state["single_track_error_median_m"] is not None]
        assert len(paired) == len({(state["entity"], state["t_global"]) for state in paired})
        assert len(ghost_states) + len(road_user_states) == len(pure_states)
        anonymous = json.loads((run / "reconstruction/global/anonymous_entities.json").read_text())
        run_counts = {
            "anonymous_entities": len(entity_rows),
            "truth_associated_non_recording_entities": len(eligible_ids),
            "paired_entities": len({state["entity"] for state in paired}),
            "paired_physical_non_recording_vehicles": len({state["true_identity"] for state in paired}),
            "anonymous_trajectory_states": sum(len(entity["trajectory"]) for entity in anonymous["entities"]),
            "source_consistent_truth_associated_states": len(pure_states),
            "excluded_source_inconsistent_states": result["impure_states"],
            "excluded_source_consistent_recorder_ghost_states": len(ghost_states),
            "source_consistent_non_recording_states": len(road_user_states),
            "excluded_non_recording_states_without_nominal_reference": len(road_user_states) - len(paired),
        }
        counts.update(run_counts)
        pooled.extend(paired)
        rows.append({"run": result["run"], "counts": run_counts, **_summarize(paired)})

    assert before == _manifest(reconstruction_paths), "The derivation changed reconstruction files"
    assert sorted(path.relative_to(ROOT).as_posix() for run in runs
                  for path in (run / "reconstruction").rglob("*") if path.is_file()) == [
                      item["path"] for item in before], "The derivation changed reconstruction file membership"
    assert counts["source_consistent_truth_associated_states"] == 4538
    assert counts["excluded_source_inconsistent_states"] == 40
    assert counts["excluded_source_consistent_recorder_ghost_states"] == 106
    assert counts["source_consistent_non_recording_states"] == 4432
    assert counts["excluded_non_recording_states_without_nominal_reference"] == 56
    assert counts["paired_physical_non_recording_vehicles"] == 45
    assert counts["paired_entities"] == 65
    assert len(pooled) == 4376
    contributing = [row for row in rows if row["paired_states"]]
    assert len(contributing) == 10
    summary = _summarize(pooled)
    assert summary["states_improved"] == 3563
    assert summary["states_worsened"] == 813
    assert summary["nominal_source_boxes_centre_error_m"]["median"] == 0.4836
    assert summary["body_reconstruction_and_fusion_centre_error_m"]["median"] == 0.2395
    return {
        "schema_version": 1,
        "scope": "G0 paired geometric reference on the 22 canonical campaign-v3 reconstructions; no estimator rerun.",
        "definition": {
            "population": "Truth-associated non-recording entities at source-consistent reconstructed instants with at least one available nominal source-track box.",
            "nominal_reference": "At each eligible entity instant, median centre error over the available nominal source-track boxes drawn by the phase-0 replay. No body-surface correction or cross-observer body reconstruction is applied to this reference.",
            "reconstruction": "Centre error of the existing body-reconstructed and fused entity at exactly the same instant and against the same physical vehicle.",
            "weighting": "One pair per entity instant; additional source tracks do not add weight. Pooled statistics weight entity instants equally, not runs or vehicles equally; temporal samples are not independent trials.",
            "bounds": "Combined body reconstruction and fusion comparison, not an isolated multi-observer or smoothing ablation. Identity errors, recorder ghosts and missing entities are assessed separately.",
            "source_consistency": "The fusion evaluator excludes instants where an available source-track identity differs from the entity's majority physical identity; ground truth is used only in evaluation.",
            "input_manifest": "Hashes cover the canonical run list, configuration, ground truth, recorder ego/metadata files and all reconstruction JSON/JSONL files, including a superset of the files read by the evaluator and replay model.",
        },
        "derivation": {
            "script": "scripts/paper_geometry_comparison.py",
            "sha256": _hash(Path(__file__)),
            "evaluation_entry_point": "cdf.evaluation.fusion_metrics.evaluate_fusion(write=False)",
            "reconstruction_files_unchanged": True,
            "reconstruction_files_checked": len(before),
            "source_files": _manifest(list((ROOT / "src/cdf").rglob("*.py"))),
        },
        "environment": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "numpy": importlib.metadata.version("numpy"),
            "PyYAML": importlib.metadata.version("PyYAML"),
        },
        "inputs": _manifest(input_paths),
        "counts": {"canonical_runs": len(runs), "contributing_runs": len(contributing), **dict(counts)},
        "pooled": summary,
        "runs_with_lower_median": sum(row["body_reconstruction_and_fusion_centre_error_m"]["median"]
                                      < row["nominal_source_boxes_centre_error_m"]["median"] for row in contributing),
        "runs_with_lower_p95": sum(row["body_reconstruction_and_fusion_centre_error_m"]["p95"]
                                   < row["nominal_source_boxes_centre_error_m"]["p95"] for row in contributing),
        "runs": rows,
    }


def markdown(result: Dict[str, Any]) -> str:
    counts = result["counts"]
    pooled = result["pooled"]
    lines = [
        "# Paired geometric comparison used by the paper", "",
        "Read-only derivation from the existing canonical G0 reconstructions; no estimator rerun.", "",
        f"The {counts['canonical_runs']} canonical runs provide {pooled['paired_states']} paired entity instants "
        f"in {counts['contributing_runs']} runs, covering {counts['paired_physical_non_recording_vehicles']} "
        f"physical non-recording vehicles and {counts['paired_entities']} reconstructed entities.", "",
        result["definition"]["nominal_reference"], "", result["definition"]["reconstruction"], "",
        result["definition"]["weighting"], "", result["definition"]["bounds"], "",
        "| Estimate | Paired instants | Median centre error [m] | P95 [m] | RMSE [m] |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, key in (("Nominal source-track boxes", "nominal_source_boxes_centre_error_m"),
                      ("Body reconstruction and fusion", "body_reconstruction_and_fusion_centre_error_m")):
        values = pooled[key]
        lines.append(f"| {name} | {values['n']} | {values['median']:.4f} | {values['p95']:.4f} | {values['rmse']:.4f} |")
    lines += ["", f"Pointwise error decreases in {pooled['states_improved']} instants "
              f"({100 * pooled['fraction_states_improved']:.1f}%) and increases in {pooled['states_worsened']}. "
              f"All {result['runs_with_lower_median']} contributing runs have lower median and P95 error; "
              "this does not imply improvement at every instant.", "",
              "| Run | Paired instants | Nominal median [m] | Reconstructed median [m] | Nominal P95 [m] | Reconstructed P95 [m] |",
              "|---|---:|---:|---:|---:|---:|"]
    for row in result["runs"]:
        if row["paired_states"]:
            before = row["nominal_source_boxes_centre_error_m"]
            after = row["body_reconstruction_and_fusion_centre_error_m"]
            lines.append(f"| {row['run']} | {row['paired_states']} | {before['median']:.4f} | "
                         f"{after['median']:.4f} | {before['p95']:.4f} | {after['p95']:.4f} |")
    lines += ["", "Exclusions are counted before pairing: "
              f"{counts['excluded_source_inconsistent_states']} source-inconsistent instants; "
              f"{counts['excluded_source_consistent_recorder_ghost_states']} source-consistent recorder-ghost instants; "
              f"{counts['excluded_non_recording_states_without_nominal_reference']} otherwise eligible non-recording "
              "instants lacking a nominal reference. The remaining 12 runs supply no paired non-recording states.", "",
              "The JSON retains all run counts, distribution summaries, configuration/input/source SHA-256 hashes "
              "and Python/dependency versions. Reconstruction files were checked before and after evaluation "
              "and remained unchanged.", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "results/paper_evaluation")
    args = parser.parse_args()
    result = extract()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "geometry_comparison.json").write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    (args.out_dir / "geometry_comparison.md").write_text(markdown(result), encoding="utf-8")
    print(f"Wrote paired geometry comparison: {result['pooled']['paired_states']} instants, "
          f"{result['counts']['contributing_runs']} contributing runs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
