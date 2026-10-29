from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[1]
CONDITIONS: Sequence[Tuple[str, str, str, str, int]] = (
    ("G0", "baseline", "none", "all", 22),
    ("G1", "gnss", "rtk", "all", 66),
    ("G2", "gnss", "degraded", "all", 66),
    ("radar nominal", "radar_v3", "nominal", "all", 66),
    ("radar severe", "radar_v3", "severe", "all", 66),
    ("radar extreme", "radar_v3", "extreme", "all", 110),
    ("one recorder severe", "radar_asym", "severe", "alone", 150),
    ("one recorder extreme", "radar_asym", "extreme", "alone", 250),
    ("G2 + radar severe", "radar_gnss_v3", "gnss degraded + radar severe", "all", 66),
)


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _number(value: str) -> Optional[float]:
    return float(value) if value else None


def _interval(value: str) -> Optional[List[float]]:
    return json.loads(value) if value else None


def _run_name(value: str) -> str:
    return "/".join([part for part in value.replace("\\", "/").split("/") if part][-2:])


def extract() -> Dict[str, Any]:
    conditions_path = ROOT / "results/campaign_v3/conditions.csv"
    scorecards_path = ROOT / "results/g0_final/scorecard.json"
    jobs_path = ROOT / "results/robustness/campaign_v3/campaign_v3_jobs.csv"
    archive_path = ROOT / "results/robustness/campaign_v3/jobs.jsonl.gz"
    fusion_paths = sorted(ROOT.glob("traces/*/run_*/reconstruction/evaluation/fusion_metrics.json"))
    input_paths = [conditions_path, scorecards_path, jobs_path, archive_path] + fusion_paths
    with conditions_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    with jobs_path.open(encoding="utf-8", newline="") as handle:
        job_rows = list(csv.DictReader(handle))
    scorecards = json.loads(scorecards_path.read_text(encoding="utf-8"))
    fusions = [json.loads(path.read_text(encoding="utf-8")) for path in fusion_paths]

    fusion_runs = {result["run"] for result in fusions}
    assert len(fusions) == len(fusion_runs) == len(scorecards) == 22
    assert fusion_runs == {card["run"] for card in scorecards}

    conditions = []
    gnss_changes = []
    for label, family, level, subset, expected_jobs in CONDITIONS:
        matches = [row for row in rows if (row["family"], row["level"], row["subset"], row["recorders"])
                   == (family, level, subset, "all")]
        assert len(matches) == 1, (label, len(matches))
        row = matches[0]
        assert int(row["jobs"]) == expected_jobs and int(row["failed"]) == 0
        conditions.append({
            "condition": label,
            "family": family,
            "level": level,
            "subset": subset,
            "jobs": int(row["jobs"]),
            "seeds": int(row["seeds"]),
            "collision_identification": float(row["identified_rate"]),
            "collision_identification_ci95": _interval(row["identified_rate_ci"]),
            "phantoms_per_job": float(row["phantoms_per_job"]),
            "recorder_ghosts_per_job": float(row["rec_ghosts_per_job"]),
            "wrong_links_per_job": float(row["wrong_links_per_job"]),
            "false_merges_per_job": float(row["false_merges_per_job"]),
            "position_p95_m": _number(row["pos_p95"]),
            "position_p95_ci95_m": _interval(row["pos_p95_ci"]),
            "archived_span_coverage": _number(row["coverage_mean"]),
            "legacy_warning_in_time": float(row["ttc_in_time_rate"]),
        })
        if family == "gnss":
            gnss_changes.append({
                "condition": label,
                "paired_position_p95_change_m": float(row["d_pos_p95"]),
                "ci95_m": _interval(row["d_pos_p95_ci"]),
            })
    assert len(conditions) == 9

    assert len(job_rows) == 1816 and all(row["status"] == "complete" for row in job_rows)
    csv_totals = {key: sum(int(row[key]) for row in job_rows)
                  for key in ("contacts", "reportable", "detected", "identified", "invented", "recontact_splits")}
    archive_totals: Counter = Counter()
    complete_keys = set()
    csv_keys = {(row["family"], row["level"], tuple(sorted(row["recorder"].split("+")))
                 if row["recorder"] else (), int(row["seed"]), row["run"]) for row in job_rows}
    assert len(csv_keys) == len(job_rows)
    extra_nodes = []
    attempts = 0
    with gzip.open(str(archive_path), "rt", encoding="utf-8") as handle:
        for line in handle:
            attempts += 1
            job = json.loads(line)
            if job.get("status") != "complete":
                continue
            degraded = tuple(sorted(job.get("perturbation", {}).get("radar_recorders") or ()))
            run = _run_name(job["run"])
            key = (job["family"], job["level"], degraded, int(job["seed"]), run)
            assert key not in complete_keys, ("duplicate complete archive job", key)
            complete_keys.add(key)
            collision = job["scorecard"]["collisions"]
            archive_totals.update({
                "contacts": collision["true"], "reportable": collision["reportable"],
                "detected": collision["detected"], "identified": collision["identified"],
                "invented": collision["invented"], "recontact_splits": collision["recontact_splits"],
            })
            assert len(collision["invented_list"]) == collision["invented"]
            for node in collision["invented_list"]:
                extra_nodes.append({"run": run, "family": job["family"], "level": job["level"],
                                    "degraded_recorders": list(degraded), "seed": job["seed"], **node})
    assert len(complete_keys) == 1816 and complete_keys == csv_keys and dict(archive_totals) == csv_totals
    assert (csv_totals["contacts"], csv_totals["detected"], csv_totals["identified"],
            csv_totals["invented"], csv_totals["recontact_splits"]) == (2344, 2344, 2322, 22, 0)
    assert len(extra_nodes) == 22
    assert all(len(node["participants"]) == 1 and not node["true_recontact"] for node in extra_nodes)
    full_campaign = {
        "completed_unique_jobs": len(complete_keys),
        "archive_attempt_records": attempts,
        "incomplete_attempt_records_excluded": attempts - len(complete_keys),
        "distinct_canonical_contacts": sum(card["collisions"]["true"] for card in scorecards),
        "true_contact_instances": csv_totals["contacts"],
        "detected_contact_instances": csv_totals["detected"],
        "correctly_identified_contact_instances": csv_totals["identified"],
        "misattributed_contact_instances": csv_totals["detected"] - csv_totals["identified"],
        "missed_contact_instances": csv_totals["reportable"] - csv_totals["detected"],
        "extra_impact_nodes": len(extra_nodes),
        "extra_single_recorder_nodes": sum(len(node["participants"]) == 1 for node in extra_nodes),
        "extra_nodes_matching_true_recontacts": sum(node["true_recontact"] for node in extra_nodes),
        "recontact_splits": csv_totals["recontact_splits"],
        "extra_node_details": extra_nodes,
    }
    assert full_campaign["distinct_canonical_contacts"] == 26

    decisions: Counter = Counter()
    merges: Counter = Counter()
    entities = []
    for result in fusions:
        decisions.update(result["decision_counts"])
        merges.update(result["merges"])
        entities.extend({"run": result["run"], **entity} for entity in result["entities"])
    pure = [entity for entity in entities if entity.get("purity") == 1.0]
    association = {
        "runs": len(fusions),
        "correct_recorder_links": decisions["correct link"],
        "wrong_recorder_links": decisions["WRONG link"],
        "missed_recorder_links": decisions["missed link"],
        "anonymous_entities": len(entities),
        "unit_purity_entities": len(pure),
        "below_unit_purity_entities": [
            {key: entity[key] for key in ("run", "id", "true_identity", "purity")}
            for entity in entities if entity.get("purity") is not None and entity["purity"] < 1.0
        ],
        "merge_pairs": {key: merges[key] for key in ("correct", "false", "missed")},
        "pure_compared_states": sum(result["states_compared"] for result in fusions),
        "impure_states_counted_separately": sum(result["impure_states"] for result in fusions),
        "duplicates": sum(card["completeness"]["duplicates"] for card in scorecards),
        "recorder_ghosts": sum(len(card["completeness"]["recorder_ghosts"]) for card in scorecards),
        "observable_non_recorders": sum(
            vehicle["observable"] for card in scorecards for vehicle in card["completeness"]["vehicles"]
            if vehicle["role"] == "non-recorder"),
        "represented_observable_non_recorders": sum(
            vehicle["observable"] and vehicle["represented"]
            for card in scorecards for vehicle in card["completeness"]["vehicles"]
            if vehicle["role"] == "non-recorder"),
    }
    assert (association["correct_recorder_links"], association["wrong_recorder_links"],
            association["missed_recorder_links"]) == (49, 0, 1)
    assert (association["anonymous_entities"], association["unit_purity_entities"],
            association["duplicates"]) == (66, 64, 20)
    assert association["observable_non_recorders"] == association["represented_observable_non_recorders"] == 45

    s19 = next(result for result in fusions if result["run"] == "S19/run_0_highway_curve")
    reference = s19["state_errors"]["single_track_nominal_centre_error_m"]
    reconstructed = s19["state_errors"]["centre_error_m"]
    assert reference["n"] == reconstructed["n"] == 461
    geometry = {
        "run": s19["run"],
        "compared_states": reference["n"],
        "nominal_single_track_box_median_centre_error_m": reference["median"],
        "reconstruction_median_centre_error_m": reconstructed["median"],
        "nominal_single_track_box_p95_centre_error_m": reference["p95"],
        "reconstruction_p95_centre_error_m": reconstructed["p95"],
        "population": "Same truth-associated, pure reconstructed entity instants; no impure states.",
        "reference_definition": (
            "At each entity instant, median centre error over available nominal source-track boxes. "
            "This compares combined surface reconstruction and fusion, not multi-observer fusion alone."
        ),
    }
    return {
        "schema_version": 1,
        "scope": "Archived campaign-v3 reconstruction evidence; no estimator rerun or altered canonical metrics.",
        "derivation": {"script": "scripts/paper_reconstruction_metrics.py", "sha256": _hash(Path(__file__))},
        "inputs": [{"path": path.relative_to(ROOT).as_posix(), "sha256": _hash(path)}
                   for path in sorted(input_paths)],
        "aggregation": {
            "conditions": "Archived per-seed means, with seed-based 95% Student t intervals where present.",
            "g0_association": "Counts over 22 canonical runs; purity is the share of measured source samples.",
            "archived_span_coverage": (
                "Capped sum of truth-associated entity trajectory spans divided by ideal visible duration; "
                "averaged over observable non-recording vehicles. Not a pointwise 1.5 m coverage test."
            ),
            "legacy_warning_in_time": (
                "Among contact sides with a COVERAGE-oracle partner warning in the preceding 8 s, "
                "fraction having any reconstructed CRITICAL_TTC_START about that partner before contact. "
                "This is the archived scorecard population, not the later matched-event relevance score."
            ),
        },
        "conditions": conditions,
        "full_campaign_contacts": full_campaign,
        "gnss_paired_position_p95_changes": gnss_changes,
        "g0_association": association,
        "same_state_geometric_reference": geometry,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "results/paper_evaluation/reconstruction_metrics.json")
    args = parser.parse_args()
    result = extract()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print("Wrote {0}: {1} conditions, {2} canonical runs, {3} hashed inputs.".format(
        args.out, len(result["conditions"]), result["g0_association"]["runs"], len(result["inputs"])))


if __name__ == "__main__":
    main()
