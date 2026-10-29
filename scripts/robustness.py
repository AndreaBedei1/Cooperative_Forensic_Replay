from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
import statistics
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from scenarios import scenario_runs

FAMILIES: Dict[str, Tuple[List[Tuple[str, Any]], bool]] = {
    "baseline": ([("none", None)], False),
    "radar": ([("low", "low"), ("nominal", "nominal"), ("high", "high")], True),
    "gnss": ([("rtk", "rtk"), ("degraded", "degraded")], True),
    "gnss_refined": ([("rtk", "rtk"), ("degraded", "degraded")], True),
    "gnss_correlated": ([("degraded common 0.5", 0.5), ("degraded common 0.9", 0.9),
                          ("degraded common 1.0", 1.0)], True),
    "combined": ([("exact + 10%", ('ideal',0.0)), ("RTK + 10%", ('rtk',0.0)),
                   ("degraded independent + 10%", ('degraded',0.0)),
                   ("degraded common 0.9 + 10%", ('degraded',0.9))], True),
    "radar_gnss_combined": ([("gnss {0} + radar {1}".format(g, r), (g, r))
                             for g in ("rtk", "degraded") for r in ("low", "nominal", "high")], True),
    "impulse": ([("2%", 0.02), ("5%", 0.05), ("10%", 0.10), ("20%", 0.20)], True),
    "radar_v3": ([("nominal", "nominal"), ("severe", "severe"), ("extreme", "extreme")], True),
    "radar_asym": ([("nominal", "nominal"), ("severe", "severe"), ("extreme", "extreme")], True),
    "radar_gnss_v3": ([("gnss {0} + radar {1}".format(g, r), (g, r))
                       for g in ("rtk", "degraded") for r in ("nominal", "severe")], True),
    "radar_asym_gnss": ([("gnss degraded + radar {0}".format(r), ("degraded", r)) for r in ("nominal", "severe")],
                        True),
    "clock": ([("offsets", None)], False),
    "downsample": ([("10 Hz", 2), ("5 Hz", 4)], False),
    "dropout": ([("one recorder", None)], False),
    "outage": ([("1 s radar outage", 1.0)], False),
}
V3_FAMILIES = ("baseline", "gnss", "radar_v3", "radar_asym", "radar_gnss_v3", "radar_asym_gnss")
TOLERANCES = {"association_accuracy": 0.02, "collision_recall": 0.02, "event_recall": 0.02,
              "fused_centre_error_m": 0.05, "runs_aligned": 0.02,
              "collisions_identified_rate": 0.02, "represented_rate": 0.02}


def _read_json(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _recorders(run_dir: Path) -> List[str]:
    return sorted(p.name for p in (run_dir / "vehicles").iterdir() if (p / "ego.jsonl").exists())


def _first_collision_t_local(run_dir: Path, recorder: str) -> Optional[float]:
    ego = (run_dir / "vehicles" / recorder / "ego.jsonl").read_text(encoding="utf-8").splitlines()
    origin = json.loads(ego[0])["timestamp"]
    lines = [json.loads(line) for line in (run_dir / "vehicles" / recorder / "collisions.jsonl")
             .read_text(encoding="utf-8").splitlines() if line.strip()]
    return None if not lines else float(lines[0]["timestamp"]) - float(origin)


def asym_subsets(recorders: Sequence[str]) -> List[str]:
    recorders = sorted(recorders)
    if len(recorders) < 2:
        return []
    subsets = {(r,) for r in recorders}
    if len(recorders) >= 3:
        subsets |= {tuple(x for x in recorders if x != r) for r in recorders}
    return sorted("+".join(subset) for subset in subsets)


def jobs_for(run_dir: Path, family: str, seeds: Sequence[int]) -> List[Dict[str, Any]]:
    levels, stochastic = FAMILIES[family]
    recorders = _recorders(run_dir)
    out = []
    for label, parameter in levels:
        variants: List[Dict[str, Any]] = [{}]
        if family in ("dropout", "outage"):
            variants = [{"recorder": recorder} for recorder in recorders if family == "outage" or len(recorders) > 1]
        elif family in ("radar_asym", "radar_asym_gnss"):
            variants = [{"recorder": subset} for subset in asym_subsets(recorders)]
        for variant in variants:
            for seed in (seeds if stochastic else [0]):
                out.append(dict(variant, run=str(run_dir), family=family, level=label, parameter=parameter, seed=seed))
    return out


def build(job: Dict[str, Any]):
    from cdf.robustness.perturb import (GNSS_PROFILES, HISTORICAL_GNSS_PROFILES, RADAR_PROFILES, CollisionPerturbation, Perturbation,
                                        PerturbedPoseSource)
    profiles = dict(GNSS_PROFILES, **HISTORICAL_GNSS_PROFILES)
    run_dir, family, parameter = Path(job["run"]), job["family"], job["parameter"]
    recorders = _recorders(run_dir)
    name = "{0}_{1}".format(family, job["level"]).replace(" ", "_").replace("%", "pct").replace("+", "and")
    pose = None
    if family == "baseline":
        perturbation = Perturbation(name)
    elif family in ("radar", "radar_v3"):
        perturbation = Perturbation(name, radar=RADAR_PROFILES[parameter])
    elif family == "radar_asym":
        perturbation = Perturbation(name, radar=RADAR_PROFILES[parameter],
                                    radar_recorders=tuple(job["recorder"].split("+")))
    elif family in ("gnss", "gnss_refined"):
        perturbation = Perturbation(name, gnss=profiles[parameter])
        pose = PerturbedPoseSource.factory(profiles[parameter], int(job["seed"]))
    elif family in ('gnss_correlated','combined'):
        import dataclasses
        base, fraction = ("consumer" if "consumer" in str(job["level"]) else "degraded", float(parameter)) \
            if family == 'gnss_correlated' else parameter
        profile = dataclasses.replace(profiles[base],common_fraction=float(fraction))
        perturbation = Perturbation(name,gnss=profile,
                     collisions=CollisionPerturbation(impulse_rel_std=.10 if family=='combined' else 0.0))
        pose = PerturbedPoseSource.factory(profile,int(job['seed']))
    elif family in ("radar_gnss_combined", "radar_gnss_v3"):
        gnss, radar = parameter
        perturbation = Perturbation(name, radar=RADAR_PROFILES[radar], gnss=profiles[gnss])
        pose = PerturbedPoseSource.factory(profiles[gnss], int(job["seed"]))
    elif family == "radar_asym_gnss":
        gnss, radar = parameter
        perturbation = Perturbation(name, radar=RADAR_PROFILES[radar], gnss=profiles[gnss],
                                    radar_recorders=tuple(job["recorder"].split("+")))
        pose = PerturbedPoseSource.factory(profiles[gnss], int(job["seed"]))
    elif family == "impulse":
        perturbation = Perturbation(name, collisions=CollisionPerturbation(impulse_rel_std=parameter))
    elif family == "clock":
        perturbation = Perturbation(name, clock_offsets_s=tuple((r, round(7.31 * (i + 1) * (-1) ** i, 2))
                                                                 for i, r in enumerate(recorders)))
    elif family == "downsample":
        perturbation = Perturbation(name, downsample=int(parameter))
    elif family == "dropout":
        perturbation = Perturbation(name, drop_recorders=(job["recorder"],))
    elif family == "outage":
        recorder = job["recorder"]
        t = _first_collision_t_local(run_dir, recorder)
        if t is None:
            ego = (run_dir / "vehicles" / recorder / "ego.jsonl").read_text(encoding="utf-8").splitlines()
            t = (json.loads(ego[-1])["timestamp"] - json.loads(ego[0])["timestamp"]) / 2.0 + 1.0
        perturbation = Perturbation(name, radar_outage=(recorder, round(t - 1.0 - float(parameter), 3), round(t - 1.0, 3)))
    else:
        raise ValueError(family)
    return perturbation, pose


def run_job(job: Dict[str, Any], work: str, keep: bool) -> Dict[str, Any]:
    from cdf.evaluation.fusion_metrics import evaluate_fusion
    from cdf.evaluation.reconstruction import evaluate_run
    from cdf.evaluation.run_metrics import core_event_diff, graph_signature, run_metrics
    from cdf.reconstruction.pipeline import reconstruct_run
    from cdf.robustness.perturb import perturbed_copy
    run_dir = Path(job["run"])
    perturbation, pose = build(job)
    tag = perturbation.name + ("_" + job["recorder"] if job.get("recorder") else "")
    target = Path(work) / tag / "seed{0}".format(job["seed"]) / run_dir.parent.name / run_dir.name
    resolved = target.resolve()
    if Path(work).resolve() not in resolved.parents or resolved == run_dir.resolve():
        raise ValueError('perturbed target must remain inside the dedicated work directory')
    if target.exists():
        shutil.rmtree(str(target))
    result = {k: v for k, v in job.items()}
    result["perturbation"] = perturbation.to_dict()
    result["configuration"] = "ablation_mutual_refinement" if job["family"] == "gnss_refined" else "frozen"
    start = time.monotonic()
    from cdf.evaluation.provenance import provenance
    from cdf.reconstruction.config import load_config
    cfg = load_config()
    if job['family']=='gnss_refined':
        import dataclasses
        cfg=dataclasses.replace(cfg,fusion=dataclasses.replace(cfg.fusion,mutual_refinement=True))
    result['provenance'] = provenance(cfg.to_dict(),runs=[str(run_dir)],
                                      perturbation=perturbation.name,seed=int(job['seed']))
    try:
        perturbed_copy(run_dir, target, perturbation, int(job["seed"]))
        reconstruct_run(target, cfg, pose_factory=pose)
        base = _read_json(run_dir / "reconstruction" / "global" / "global_graph.json")
        new = _read_json(target / "reconstruction" / "global" / "global_graph.json")
        keep_recorders = [r for r in _recorders(run_dir) if r not in perturbation.drop_recorders]
        result["events"] = core_event_diff(base, new, keep_recorders)
        result["identical_graph"] = graph_signature(base) == graph_signature(new)
        if job["family"] != "clock":
            evaluation = evaluate_run(target, clock_shift_check=False)
            fusion = evaluate_fusion(target, write=True, pose_factory=pose)
            fusion_full = dict(fusion)
            fusion.pop("_raw", None)
            result["metrics"] = run_metrics(target, evaluation, fusion)
            result['collision_unmatched'] = sum(c.get('reconstructed_as') is None for c in evaluation['collisions'])
            alignment = _read_json(target/'reconstruction/global/alignment.json')
            result['ambiguous_candidate_refusals'] = sum('ambig' in str(e).lower() for e in alignment['rejected_matches'])
            from cdf.evaluation.pose_errors import pose_errors
            result['pose_errors'] = pose_errors(target,pose)
            result.update(extra_evaluation(target, evaluation, fusion_full))
            result["road_user_errors_raw"] = raw_errors(fusion_full)
            if job["family"] in V3_FAMILIES:
                from cdf.evaluation.scorecard import scorecard
                try:
                    card = scorecard(target, oracle=result.pop("_oracle_full", None))
                    for vehicle in card["completeness"]["vehicles"]:
                        vehicle.pop("road_users", None)
                    result["scorecard"] = card
                except Exception:
                    import traceback
                    result.setdefault("evaluation_errors", {})["scorecard"] = traceback.format_exc()[-2000:]
            result.pop("_oracle_full", None)
        result["status"] = "complete"
    except Exception as exc:
        import traceback
        result["status"] = "failed"
        result["error"] = repr(exc)
        result["trace"] = traceback.format_exc()[-3000:]
    result["wall_s"] = round(time.monotonic() - start, 2)
    result["resources"] = _resources()
    if not keep and target.exists():
        shutil.rmtree(str(target), ignore_errors=True)
    return result


def raw_errors(fusion: Dict[str, Any]) -> Dict[str, List[float]]:
    raw = (fusion.get("_raw") or {}).get("road_user_errors") or {}
    return {key: [round(float(v), 4) for v in raw.get(key, [])] for key in ("centre_error_m", "speed_error_mps")}


def _resources() -> Dict[str, Any]:
    import os
    try:
        import psutil
        info = psutil.Process().memory_info()
        return {"pid": os.getpid(), "rss_mb": round(info.rss / 2 ** 20, 1),
                "peak_mb": round(getattr(info, "peak_wset", info.rss) / 2 ** 20, 1)}
    except Exception:
        return {"pid": os.getpid()}


def extra_evaluation(target: Path, evaluation: Dict[str, Any], fusion: Dict[str, Any]) -> Dict[str, Any]:
    import traceback
    from cdf.evaluation.campaign_metrics import campaign_metrics
    from cdf.evaluation.event_oracle import compare_run
    from cdf.reconstruction.config import load_config
    out: Dict[str, Any] = {}
    failures: Dict[str, str] = {}
    errors = fusion.get("state_errors", {})
    out["trajectory"] = {key: errors.get(key) for key in ("centre_error_m", "velocity_error_mps", "speed_error_mps",
                                                           "heading_error_deg", "coverage_s")}
    out["trajectory"]["calibration"] = fusion.get("calibration")
    try:
        out["campaign"] = campaign_metrics(target, fusion, evaluation)
        out["campaign"].pop("track_ranges_m", None)
    except Exception:
        failures["campaign_metrics"] = traceback.format_exc()[-2000:]
    try:
        oracle = compare_run(Path(target), load_config())
        out["_oracle_full"] = oracle
        out["event_oracle"] = {pair: {kind: {k: v for k, v in row.items() if k in ("found", "expected", "matched", "deltas")}
                                      for kind, row in table.items()}
                               for pair, table in oracle["comparison"].items() if pair.startswith("RECONSTRUCTION vs")}
    except Exception:
        failures["event_oracle"] = traceback.format_exc()[-2000:]
    if failures:
        out["evaluation_errors"] = failures
    return out


def job_key(job: Dict[str, Any]) -> Tuple[Any, ...]:
    return (job["run"], job["family"], job["level"], job.get("recorder"), int(job["seed"]))


def latest_results(results: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    chosen: Dict[Tuple[Any, ...], Dict[str, Any]] = {}
    for r in results:
        k = job_key(r)
        if k not in chosen or chosen[k].get("status") != "complete":
            chosen[k] = r
    return list(chosen.values())


def pooled(results: Sequence[Dict[str, Any]]) -> Dict[str, Optional[float]]:
    done = [r for r in results if r.get("status") == "complete"]
    with_metrics = [r["metrics"] for r in done if "metrics" in r]

    def ratio(num: str, den: str) -> Optional[float]:
        total = sum(m[den] for m in with_metrics)
        return None if not total else sum(m[num] for m in with_metrics) / total

    events_base = sum(r["events"]["base_events"] for r in done)
    centre = [m["fused_centre_error_median_m"] for m in with_metrics if m.get("fused_centre_error_median_m") is not None]
    deltas = [abs(d) for r in done for d in r["events"]["time_deltas_s"]]
    from cdf.evaluation.scorecard import _numbers
    cards = [_numbers(r["scorecard"]) for r in done if r.get("scorecard")]

    def card_ratio(num: str, den: str) -> Optional[float]:
        total = sum(c[den] for c in cards)
        return None if not total else sum(c[num] for c in cards) / total

    return {"runs": len(done), "failed": len(results) - len(done),
            "collisions_identified_rate": card_ratio("identified", "reportable"),
            "represented_rate": card_ratio("represented", "observable"),
            "association_accuracy": ratio("associations_correct", "associations_decided"),
            'absolute_pose_rms_m': statistics.median([r['pose_errors']['absolute_position_m']['rms'] for r in done
                                   if r.get('pose_errors')]) if any(r.get('pose_errors') for r in done) else None,
            'relative_pose_rms_m': statistics.median([r['pose_errors']['relative_position_m']['rms'] for r in done
                                   if r.get('pose_errors') and r['pose_errors']['relative_position_m']['rms'] is not None])
                                   if any(r.get('pose_errors') and r['pose_errors']['relative_position_m']['rms'] is not None for r in done) else None,
            "collision_recall": ratio("collisions_reconstructed", "collisions_true"),
            "false_collision_matches": sum(m.get('false_collision_matches', 0) for m in with_metrics),
            "collision_unmatched": sum(r.get('collision_unmatched',0) for r in done),
            "ambiguous_candidate_refusals": sum(r.get('ambiguous_candidate_refusals',0) for r in done),
            "runs_aligned": (sum(1 for m in with_metrics if m["recorders_aligned"] == m["recorders"]) / len(with_metrics)
                             if with_metrics else None),
            "wrong_links": sum(m["links_wrong"] for m in with_metrics) if with_metrics else None,
            "missed_links": sum(m["links_missed"] for m in with_metrics) if with_metrics else None,
            "false_merges": sum(m["merges_false"] for m in with_metrics) if with_metrics else None,
            "entities_without_vehicle": sum(m["entities_without_vehicle"] for m in with_metrics) if with_metrics else None,
            "fused_centre_error_m": statistics.median(centre) if centre else None,
            "event_recall": (sum(r["events"]["matched"] for r in done) / events_base) if events_base else None,
            "extra_events": sum(len(r["events"]["extra"]) for r in done),
            "event_time_delta_median_s": statistics.median(deltas) if deltas else None,
            "event_time_delta_p95_s": sorted(deltas)[int(0.95 * (len(deltas) - 1))] if deltas else None,
            "max_relative_offset_error_s": max((m["max_abs_relative_offset_error_s"] or 0.0) for m in with_metrics)
            if with_metrics else None,
            "identical_graphs": (sum(1 for r in done if r.get("identical_graph")) if any("identical_graph" in r for r in done)
                                 else None)}


def summarize(all_results: Sequence[Dict[str, Any]], results_dir: Path) -> Dict[str, Any]:
    from cdf.evaluation.provenance import provenance
    from cdf.reconstruction.config import load_config
    groups: Dict[Tuple[str, str], Dict[int, List[Dict[str, Any]]]] = {}
    attempts = len(all_results)
    all_results = latest_results(all_results)
    for r in all_results:
        groups.setdefault((r["family"], r["level"]), {}).setdefault(int(r["seed"]), []).append(r)
    rows = []
    for (family, level), by_seed in sorted(groups.items(), key=lambda item: (list(FAMILIES).index(item[0][0]),
                                                                              [l for l, _ in FAMILIES[item[0][0]][0]].index(item[0][1]))):
        per_seed = {seed: pooled(results) for seed, results in sorted(by_seed.items())}
        keys = [k for k in next(iter(per_seed.values())) if k not in ("runs", "failed")]
        row: Dict[str, Any] = {"family": family, "level": level, "seeds": len(per_seed),
                               "runs": sum(p["runs"] for p in per_seed.values()),
                               "failed": sum(p["failed"] for p in per_seed.values())}
        for key in keys:
            values = [p[key] for p in per_seed.values() if p[key] is not None]
            row[key] = round(statistics.fmean(values), 4) if values else None
            row[key + "_sd"] = round(statistics.stdev(values), 4) if len(values) > 1 else None
        rows.append(row)
    record = {"definition": "robustness of the reconstruction: every condition applied to every run (seeds for "
                            "stochastic ones), pooled per seed over runs, then mean and SD over seeds",
              "provenance": provenance(load_config().to_dict(), sorted({Path(r["run"]).parent.name + "/" +
                                                                        Path(r["run"]).name for r in all_results})),
              "tolerances_for_seeds": TOLERANCES, "attempts": attempts, "jobs": len(all_results),
              "jobs_failed": sum(1 for r in all_results if r.get("status") != "complete"), "rows": rows}
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "summary.json").write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    columns = list(rows[0].keys()) if rows else []
    with (results_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    (results_dir / "summary.md").write_text(markdown(record), encoding="utf-8")
    figures(record, results_dir / "figures")
    if any(r.get("scorecard") for r in all_results):
        from cdf.evaluation.scorecard import campaign_markdown, campaign_rows, condition_table
        job_rows = campaign_rows([r for r in all_results if r["family"] in V3_FAMILIES])
        table = condition_table(job_rows)
        (results_dir / "campaign_v3.json").write_text(json.dumps({"conditions": table, "jobs": job_rows}, indent=1)
                                                      + "\n", encoding="utf-8")
        (results_dir / "campaign_v3_conditions.md").write_text(
            campaign_markdown(table, "Campaign v3: reconstruction quality per condition"), encoding="utf-8")
        keys = sorted({k for row in job_rows for k in row}, key=lambda k: (k.startswith("d_"), k))
        with (results_dir / "campaign_v3_jobs.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=keys)
            writer.writeheader()
            writer.writerows(job_rows)
    return record


TABLE = [("association_accuracy", "assoc. acc.", 3), ("collision_recall", "coll. recall", 3),
         ("runs_aligned", "runs aligned", 3), ("event_recall", "event recall", 3), ("extra_events", "extra events", 1),
         ("event_time_delta_p95_s", "event dt p95 [s]", 3), ("fused_centre_error_m", "centre err. [m]", 3),
         ("wrong_links", "wrong links", 1), ("missed_links", "missed links", 1), ("false_merges", "false merges", 1),
         ("entities_without_vehicle", "spurious U", 1)]


def _cell(row: Dict[str, Any], key: str, decimals: int) -> str:
    value = row.get(key)
    if value is None:
        return "-"
    sd = row.get(key + "_sd")
    text = "{0:.{1}f}".format(value, decimals)
    return text if not sd else "{0} +- {1:.{2}f}".format(text, sd, decimals)


def markdown(record: Dict[str, Any]) -> str:
    prov = record["provenance"]
    lines = ["# Robustness of the reconstruction", "",
             "Every condition applied to every selected run (`scripts/robustness.py`, `cdf.robustness.perturb`); "
             "stochastic conditions over seeds (3 at least, more until the standard error of every pooled metric is "
             "below its tolerance, 8 at most).  Per seed the metrics are pooled over the runs (counts: sums over the "
             "runs of one draw); the table gives the mean over seeds +- their standard deviation.  Ground truth is "
             "used only here, for the evaluation; the reconstruction under test never sees it.", "",
             "Columns: identity association accuracy over the decided tracks; true vehicle-vehicle collisions "
             "reconstructed; share of runs with every recorder on the global clock; core instant events of the "
             "unperturbed reconstruction found again (same type, actor and subject class within 1 s, after removing "
             "a shift of the clock origin) and those added; 95th percentile of their time differences; median fused "
             "centre error of the anonymous road users (map frame of the pose streams: a GNSS error common to all "
             "recorders stays in it); recorder links wrong or missed; false merges of anonymous tracks; anonymous "
             "entities that are no vehicle (clutter).", "",
             "Provenance: code `{0}`, configuration `{1}`, commit `{2}`{3}, {4}.".format(
                 prov["code_sha256"][:16], (prov.get("config_sha256") or "")[:16], prov["git_commit"],
                 " (uncommitted changes)" if prov["git_dirty"] else "", prov["generated_utc"]), "",
             "| family | level | seeds | runs | failed | " + " | ".join(h for _, h, _ in TABLE) + " | identical graphs |",
             "|---|---|--:|--:|--:|" + "---:|" * len(TABLE) + "---:|"]
    for row in record["rows"]:
        lines.append("| {0} | {1} | {2} | {3} | {4} | {5} | {6} |".format(
            row["family"], row["level"], row["seeds"], row["runs"], row["failed"],
            " | ".join(_cell(row, key, decimals) for key, _, decimals in TABLE),
            "-" if row.get("identical_graphs") is None else "{0:.0f}/{1}".format(row["identical_graphs"], row["runs"])))
    return "\n".join(lines) + "\n"


PLOTS = {"radar": "ideal", "gnss": "ideal", "impulse": "0%", "downsample": "20 Hz"}
GENERAL = [("association_accuracy", "association accuracy"), ("event_recall", "core event recall"),
           ("fused_centre_error_m", "fused centre error [m]"), ("errors", "wrong links + false merges")]
PANELS = {"radar": GENERAL, "gnss": GENERAL,
          "impulse": [("collision_recall", "collisions reconstructed"), ("runs_aligned", "runs fully aligned"),
                      ("event_recall", "core event recall"), ("fused_centre_error_m", "fused centre error [m]")],
          "downsample": [("collision_recall", "collisions reconstructed"), ("association_accuracy", "association accuracy"),
                         ("event_recall", "core event recall"), ("fused_centre_error_m", "fused centre error [m]")]}
RATIOS = ("association_accuracy", "event_recall", "collision_recall", "runs_aligned")


def baseline_for_family(record: Dict[str, Any], family: str) -> Optional[Dict[str, Any]]:
    baseline = next((r for r in record['rows'] if r['family'] == 'baseline'), None)
    versions = record.get('family_provenance', {})
    family_hash = versions.get(family, {}).get('code_sha256')
    baseline_hash = versions.get('baseline', {}).get('code_sha256')
    if family_hash and baseline_hash and family_hash != baseline_hash:
        for past in record.get('analysis_history', []):
            if past.get('provenance', {}).get('code_sha256') == family_hash:
                historical = next((r for r in past.get('rows', []) if r['family'] == 'baseline'), None)
                if historical is not None:
                    return historical
        raise ValueError('No version-compatible baseline retained for ' + family)
    return baseline


def figures(record: Dict[str, Any], out_dir: Path) -> List[Path]:
    from cdf.evaluation.figures import DOUBLE_COLUMN_IN, paper_style
    plt = paper_style()
    rows = record["rows"]
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []

    def series(family: str) -> List[Dict[str, Any]]:
        baseline = baseline_for_family(record, family)
        own = [row for row in rows if row["family"] == family]
        return ([dict(baseline, level=PLOTS.get(family.replace("_refined", ""), "none"))] if baseline else []) + own

    def value(row: Dict[str, Any], key: str) -> Tuple[Optional[float], float]:
        if key == "errors":
            parts = [row.get("wrong_links"), row.get("false_merges")]
            if all(part is None for part in parts):
                return None, 0.0
            sds = [row.get("wrong_links_sd") or 0.0, row.get("false_merges_sd") or 0.0]
            return sum(part or 0.0 for part in parts), math.sqrt(sum(sd * sd for sd in sds))
        return row.get(key), row.get(key + "_sd") or 0.0

    for family in PLOTS:
        groups = [(family, series(family))]
        if family == "gnss" and any(row["family"] == "gnss_refined" for row in rows):
            groups.append(("gnss_refined", series("gnss_refined")))
        if len(groups[0][1]) < 2:
            continue
        panels = PANELS[family]
        fig, grid = plt.subplots(2, 2, figsize=(DOUBLE_COLUMN_IN, 4.2))
        axes = list(grid.flat)
        for axis, (key, title) in zip(axes, panels):
            for index, (name, items) in enumerate(groups):
                xs = list(range(len(items)))
                points = [value(row, key) for row in items]
                ys = [math.nan if v is None else v for v, _ in points]
                es = [e for _, e in points]
                axis.errorbar([x + 0.08 * index for x in xs], ys, yerr=es, marker="os"[index % 2], capsize=3,
                              linewidth=1.2, markersize=4,
                              label={"gnss": "plain", "gnss_refined": "mutual refinement"}.get(name, name))
            axis.set_xticks(range(len(groups[0][1])))
            axis.set_xticklabels([row["level"] for row in groups[0][1]], rotation=30)
            axis.set_title(title)
            axis.grid(alpha=0.3)
            if key in RATIOS:
                axis.set_ylim(-0.02, 1.02)
        if len(groups) > 1:
            axes[0].legend()
        title = {"radar": "Radar noise, missed detections and clutter", "gnss": "GNSS position and heading errors",
                       "impulse": "Collision impulse noise", "downsample": "Recording rate"}[family]
        if record.get('family_provenance', {}).get(family) != record.get('family_provenance', {}).get('baseline'):
            title += ' (historical study)'
        fig.suptitle(title)
        fig.tight_layout()
        for suffix in ("svg", "pdf"):
            path = out_dir / "{0}.{1}".format(family, suffix)
            fig.savefig(str(path))
            written.append(path)
        plt.close(fig)
    return written


def need_more_seeds(results: Sequence[Dict[str, Any]], family: str, level: str) -> bool:
    by_seed: Dict[int, List[Dict[str, Any]]] = {}
    for r in latest_results(results):
        if r["family"] == family and r["level"] == level:
            by_seed.setdefault(int(r["seed"]), []).append(r)
    per_seed = [pooled(rs) for rs in by_seed.values()]
    for key, tolerance in TOLERANCES.items():
        values = [p[key] for p in per_seed if p.get(key) is not None]
        if len(values) >= 2 and statistics.stdev(values) / math.sqrt(len(values)) > tolerance:
            return True
    return False


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Robustness study over saved recordings (non-destructive)")
    parser.add_argument("runs", nargs="*", type=Path)
    parser.add_argument("--scenarios", action="store_true")
    parser.add_argument("--families", default=",".join(FAMILIES))
    parser.add_argument("--work", default=str(ROOT / "robustness"))
    parser.add_argument("--results", type=Path, default=ROOT / "results" / "robustness")
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--min-seeds", type=int, default=3)
    parser.add_argument("--max-seeds", type=int, default=8)
    parser.add_argument("--keep", action="store_true", help="keep the perturbed copies and their reconstructions")
    parser.add_argument("--max-attempts", type=int, default=2, help="attempts of a failing job in all (resumes too)")
    parser.add_argument("--summarize", action="store_true", help="only rewrite the summary from jobs.jsonl")
    args = parser.parse_args(argv)
    if args.scenarios and args.runs:
        parser.error("--scenarios cannot be combined with positional run directories")
    if args.scenarios:
        args.runs = scenario_runs()
    if not args.runs and not args.summarize:
        parser.error("no runs: give run directories or --scenarios")
    if Path(args.work).resolve() == (ROOT / "traces").resolve():
        parser.error("perturbed copies never go into traces/")
    args.results.mkdir(parents=True, exist_ok=True)
    jobs_file = args.results / "jobs.jsonl"
    done: List[Dict[str, Any]] = []
    if jobs_file.exists():
        done = [json.loads(line) for line in jobs_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not args.summarize:
        runs = [run for run in args.runs if (run / "reconstruction" / "global" / "global_graph.json").exists()]
        families = [f for f in args.families.split(",") if f]

        key = job_key
        finished = {key(r) for r in done if r.get("status") == "complete"}
        attempts: Dict[Tuple[Any, ...], int] = {}
        for r in done:
            attempts[key(r)] = attempts.get(key(r), 0) + 1
        seeds = {(f, label): list(range(args.min_seeds)) for f in families for label, _ in FAMILIES[f][0]}
        while True:
            pending = [job for f in families for run in runs for job in jobs_for(run, f, sorted({s for (ff, _), ss in seeds.items()
                                                                                                  if ff == f for s in ss}))
                       if job["seed"] in seeds[(f, job["level"])] and key(job) not in finished
                       and attempts.get(key(job), 0) < args.max_attempts]
            if not pending:
                more = False
                for (f, label), ss in seeds.items():
                    if FAMILIES[f][1] and len(ss) < args.max_seeds and need_more_seeds(done, f, label):
                        ss.append(len(ss))
                        more = True
                if not more:
                    break
                continue
            print("{0} jobs ({1} workers)".format(len(pending), args.workers), flush=True)
            with ProcessPoolExecutor(max_workers=args.workers) as pool, jobs_file.open("a", encoding="utf-8") as handle:
                futures = [pool.submit(run_job, job, args.work, args.keep) for job in pending]
                for future in as_completed(futures):
                    result = future.result()
                    result["attempt"] = attempts.get(key(result), 0) + 1
                    attempts[key(result)] = result["attempt"]
                    handle.write(json.dumps(result) + "\n")
                    handle.flush()
                    done.append(result)
                    if result.get("status") == "complete":
                        finished.add(key(result))
                    else:
                        print("FAILED", result["family"], result["level"], result["run"], result.get("error"), flush=True)
    record = summarize(done, args.results)
    for row in record["rows"]:
        print("{0:10s} {1:16s} seeds {2} runs {3:3d} assoc {4} coll {5} aligned {6} events {7} centre {8} false merges {9}".format(
            row["family"], row["level"], row["seeds"], row["runs"], row.get("association_accuracy"),
            row.get("collision_recall"), row.get("runs_aligned"), row.get("event_recall"),
            row.get("fused_centre_error_m"), row.get("false_merges")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
