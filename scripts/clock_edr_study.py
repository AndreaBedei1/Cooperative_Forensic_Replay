from __future__ import annotations

import argparse
import json
import math
import shutil
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from scenarios import scenario_runs

CLOCK_RESIDUAL_S = 0.05
EDR_LEVELS = {"dv5": 0.05, "dv10": 0.10}
MASS_REL_STD = 0.05
JITTER_S = 0.010
TRIGGER_DELTA_V_MPS = 8.0 / 3.6
TRIGGER_WINDOW_S = 0.15
NOMINAL_MASS_KG = 1500.0
CONDITIONS = {"G0": (None, None), "G2+severe": ("degraded", "severe")}
CONTACT_WINDOW_S = 0.5


def _json(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _jsonl(path: Path) -> List[Dict[str, Any]]:
    if not Path(path).exists():
        return []
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def _run_name(run_dir: Path) -> str:
    return "{0}/{1}".format(run_dir.parent.name, run_dir.name)


def _relative(run: Path) -> str:
    path = Path(run).resolve()
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def _recorders(run_dir: Path) -> List[Path]:
    return sorted(p for p in (run_dir / "vehicles").iterdir() if (p / "ego.jsonl").exists())


def job_key(job: Dict[str, Any]) -> Tuple[Any, ...]:
    return (job["run"], job["study"], job["condition"], job["level"], int(job["seed"]))


def trigger_census(runs: Sequence[Path]) -> List[Dict[str, Any]]:
    import numpy as np
    rows = []
    for run in runs:
        evaluation = _json(run / "reconstruction" / "evaluation" / "evaluation.json")
        for contact in evaluation.get("collisions", []):
            t = float(contact["sim_time"])
            recorders = {}
            for name in contact["participants"]:
                vehicle = run / "vehicles" / name
                if not (vehicle / "ego.jsonl").exists():
                    continue
                calls = [r for r in _jsonl(vehicle / "collisions.jsonl") if abs(float(r["timestamp"]) - t) <= CONTACT_WINDOW_S]
                if not calls:
                    recorders[name] = None
                    continue
                t0 = min(float(r["timestamp"]) for r in calls)
                impulse = sum(float(r["impulse"]) for r in calls if float(r["timestamp"]) <= t0 + TRIGGER_WINDOW_S + 1e-6)
                ego = _jsonl(vehicle / "ego.jsonl")
                times = np.array([float(r["timestamp"]) for r in ego])
                speed = np.array([[float((r.get("velocity") or {}).get(a, 0.0)) for a in ("x", "y")] for r in ego])
                before = np.nonzero(times < t0 - 1e-6)[0]
                window = np.nonzero((times >= t0 - 1e-6) & (times <= t0 + TRIGGER_WINDOW_S + 1e-6))[0]
                jump = None
                if len(before) and len(window):
                    d = speed[window] - speed[before[-1]]
                    jump = float(np.max(np.hypot(d[:, 0], d[:, 1])))
                recorders[name] = {"delta_v_impulse_kmh": round(3.6 * impulse / NOMINAL_MASS_KG, 2),
                                   "delta_v_recorded_kmh": None if jump is None else round(3.6 * jump, 2)}
            rows.append({"run": _run_name(run), "participants": contact["participants"], "sim_time": t,
                         "recorders": recorders})
    return rows


def census_summary(rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    threshold = 3.6 * TRIGGER_DELTA_V_MPS
    out: Dict[str, Any] = {"contacts": len(rows), "threshold_kmh": round(threshold, 2)}
    for key in ("delta_v_impulse_kmh", "delta_v_recorded_kmh"):
        values = [[(v or {}).get(key) for v in r["recorders"].values()] for r in rows]
        both = sum(all(x is not None and x >= threshold for x in vs) for vs in values)
        one = sum(any(x is not None and x >= threshold for x in vs) for vs in values)
        out[key] = {"all_recorders_trigger": both, "some_recorder_triggers": one, "none_triggers": len(rows) - one,
                    "below": sorted("{0} {1}".format(r["run"], "-".join(r["participants"]))
                                    for r, vs in zip(rows, values)
                                    if not all(x is not None and x >= threshold for x in vs))}
    return out


def _copy(job: Dict[str, Any], work: Path, collisions: Any = None) -> Tuple[Path, Any]:
    from cdf.robustness.perturb import GNSS_PROFILES, RADAR_PROFILES, PerturbedPoseSource, Perturbation, perturbed_copy
    run_dir = ROOT / job["run"]
    gnss, radar = CONDITIONS[job["condition"]]
    target = work / job["study"] / job["condition"].replace("+", "_") / job["level"] / "seed{0}".format(job["seed"]) \
        / run_dir.parent.name / run_dir.name
    resolved = target.resolve()
    if work.resolve() not in resolved.parents or (ROOT / "traces").resolve() in resolved.parents:
        raise ValueError("perturbed copies stay inside the work directory, never traces/")
    if target.exists():
        shutil.rmtree(str(target))
    kwargs: Dict[str, Any] = {}
    if radar:
        kwargs["radar"] = RADAR_PROFILES[radar]
    if gnss:
        kwargs["gnss"] = GNSS_PROFILES[gnss]
    if collisions is not None:
        kwargs["collisions"] = collisions
    perturbed_copy(run_dir, target, Perturbation(job["study"] + "_" + job["level"], **kwargs), int(job["seed"]))
    pose = PerturbedPoseSource.factory(GNSS_PROFILES[gnss], int(job["seed"])) if gnss else None
    return target, pose


def _road_maps(locals_: Sequence[Any]) -> Dict[str, Optional[str]]:
    return {local.owner: (local.graph.recorder.get("road_map") or {}).get("name") for local in locals_}


def _node_times(graph: Any, recorders: Sequence[str], recorders_only: bool) -> Dict[Tuple[Any, ...], Optional[float]]:
    def name(value: Optional[str]) -> Optional[str]:
        return value if value is None or value in recorders else "U"
    out: Dict[Tuple[Any, ...], Optional[float]] = {}
    seen: Dict[Tuple[Any, ...], int] = {}
    nodes = [n for n in graph.nodes if not recorders_only or (name(n.actor_id) != "U" and name(n.subject_id) != "U")]
    for node in sorted(nodes, key=lambda n: (n.event_type, str(name(n.actor_id)), str(name(n.subject_id)),
                                             -1e9 if n.t_global is None else n.t_global)):
        base = (node.event_type, name(node.actor_id), name(node.subject_id))
        seen[base] = seen.get(base, 0) + 1
        out[base + (seen[base],)] = node.t_global
    return out


def _order_changes(before: Dict[Tuple[Any, ...], Optional[float]], after: Dict[Tuple[Any, ...], Optional[float]]
                   ) -> Dict[str, Any]:
    keys = sorted(k for k in before if k in after and before[k] is not None and after[k] is not None)
    flips = pairs = 0
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            d0, d1 = before[a] - before[b], after[a] - after[b]
            if abs(d0) < 1e-6 and abs(d1) < 1e-6:
                continue
            pairs += 1
            if d0 * d1 < 0 or (abs(d0) < 1e-6) != (abs(d1) < 1e-6):
                flips += 1
    moves = [abs(after[k] - before[k]) for k in keys]
    return {"nodes_before": len(before), "nodes_after": len(after), "nodes_common": len(keys),
            "same_nodes": sorted(before) == sorted(after), "ordered_pairs": pairs, "order_changes": flips,
            "max_node_move_s": round(max(moves), 4) if moves else None}


def clock_job(job: Dict[str, Any], work: Path) -> Dict[str, Any]:
    import numpy as np
    from cdf.reconstruction.config import load_config
    from cdf.reconstruction.local import reconstruct_vehicle
    from cdf.reconstruction.pipeline import fuse_recorders, measured_ego_records, read_incident_context
    from cdf.robustness.perturb import stream_seed
    cfg = load_config()
    run_dir = ROOT / job["run"]
    data_dir, pose, target = run_dir, None, None
    if CONDITIONS[job["condition"]] != (None, None):
        target, pose = _copy(job, work)
        data_dir = target
    context = read_incident_context(data_dir)
    vehicles = _recorders(data_dir)
    residual = {p.name: float(np.random.default_rng(stream_seed(int(job["seed"]), "clock_residual", _run_name(run_dir),
                                                                  p.name)).uniform(-CLOCK_RESIDUAL_S, CLOCK_RESIDUAL_S))
                for p in vehicles}
    first = {p.name: float(_jsonl(p / "ego.jsonl")[0]["timestamp"]) for p in vehicles}

    def same_errors(vehicle_dir: Path, clock_origin: float):
        source = pose(vehicle_dir, first[Path(vehicle_dir).name])
        source.times = source.times + (first[Path(vehicle_dir).name] - clock_origin)
        return source

    def build(shifted: bool):
        locals_ = [reconstruct_vehicle(p, cfg, clock_origin=(first[p.name] - residual[p.name]) if shifted else None,
                                       context=context, ego_records=measured_ego_records(p, pose))
                   for p in vehicles]
        alignment, _, _, graph = fuse_recorders(data_dir, locals_, cfg, same_errors if pose else None)
        return locals_, alignment, graph

    locals0, align0, graph0 = build(False)
    locals1, align1, graph1 = build(True)
    offsets0 = {n: c.offset_to_global for n, c in align0.graphs.items() if c.status == "ALIGNED"}
    offsets1 = {n: c.offset_to_global for n, c in align1.graphs.items() if c.status == "ALIGNED"}
    pairs = []
    common = sorted(set(offsets0) & set(offsets1))
    if common:
        ref = common[0]
        for name in sorted(offsets1):
            if name == ref:
                continue
            truth = -(residual[name] - residual[ref])
            estimate = offsets1[name] - offsets1[ref]
            row = {"recorder": name, "reference": ref, "injected_relative_s": round(truth, 6),
                   "estimated_relative_s": round(estimate, 6), "error_vs_truth_s": round(estimate - truth, 6)}
            if name in offsets0:
                row["error_vs_unshifted_s"] = round(estimate - (offsets0[name] - offsets0[ref]) - truth, 6)
            pairs.append(row)
    result: Dict[str, Any] = {
        "residual_s": {k: round(v, 6) for k, v in residual.items()},
        "recorders": len(vehicles), "aligned_unshifted": len(offsets0), "aligned_shifted": len(offsets1),
        "pairs": pairs,
        "order": _order_changes(_node_times(graph0, list(first), False), _node_times(graph1, list(first), False)),
        "order_recorders": _order_changes(_node_times(graph0, list(first), True), _node_times(graph1, list(first), True)),
        "road_maps": _road_maps(locals0), "incident_map": context.get("map")}
    if target is None:
        committed = _json(run_dir / "reconstruction" / "global" / "alignment.json")["graphs"]
        result["reproduces_committed_alignment"] = all(
            (committed[n]["status"] == c.status) and (c.offset_to_global is None or committed[n]["offset_to_global"] is None
                                                      or abs(committed[n]["offset_to_global"] - c.offset_to_global) < 1e-6)
            for n, c in align0.graphs.items())
        committed_nodes = sorted((n["event_type"], n["actor_id"], n["subject_id"],
                                  None if n["t_global"] is None else round(n["t_global"], 3))
                                 for n in _json(run_dir / "reconstruction" / "global" / "global_graph.json")["nodes"])
        ours = sorted((n.event_type, n.actor_id, n.subject_id, None if n.t_global is None else round(n.t_global, 3))
                      for n in graph0.nodes)
        result["reproduces_committed_graph"] = committed_nodes == ours
    else:
        shutil.rmtree(str(target))
    return result


def edr_job(job: Dict[str, Any], work: Path) -> Dict[str, Any]:
    from cdf.evaluation.reconstruction import evaluate_run
    from cdf.evaluation.scorecard import collision_score
    from cdf.reconstruction.config import load_config
    from cdf.reconstruction.pipeline import reconstruct_run
    from cdf.robustness.perturb import CollisionPerturbation
    cfg = load_config()
    run_dir = ROOT / job["run"]
    collisions = CollisionPerturbation(burst_rel_std=EDR_LEVELS[job["level"]], mass_rel_std=MASS_REL_STD,
                                       burst_jitter_s=JITTER_S)
    target, pose = _copy(job, work, collisions)
    names = [p.name for p in _recorders(run_dir)]
    reconstruct_run(target, cfg, pose_factory=pose)
    evaluation = evaluate_run(target, clock_shift_check=False)
    score = collision_score(evaluation, names)
    alignment = _json(target / "reconstruction" / "global" / "alignment.json")
    similarity = []
    for event in alignment.get("matched_events") or []:
        values = [float(v) for v in (event.get("peak_impulse") or {}).values()]
        if len(values) == 2 and max(values) > 0:
            similarity.append(round(min(values) / max(values), 4))
    relative = [abs(v) for v in (alignment.get("relative_clock_offsets_s") or {}).values() if v is not None]
    maps = {name: (_json(target / "reconstruction" / name / "local_graph.json")["recorder"].get("road_map") or {})
            .get("name") for name in names if (target / "reconstruction" / name / "local_graph.json").exists()}
    result = {"true": score["true"], "reportable": score["reportable"],
              "detected": score["detected"], "identified": score["identified"], "invented": score["invented"],
              "matched_events": len(alignment.get("matched_events") or []), "impulse_ratio": similarity,
              "rejected_matches": len(alignment.get("rejected_matches") or []),
              "unaligned": sorted(n for n, g in alignment["graphs"].items() if g["status"] != "ALIGNED"),
              "max_abs_relative_offset_s": round(max(relative), 4) if relative else None,
              "road_maps": maps, "incident_map": (_json(run_dir / "incident_context.json") or {}).get("map")}
    shutil.rmtree(str(target))
    return result


def use_maps(maps: Optional[str]) -> Dict[str, str]:
    from cdf.reconstruction import road
    if maps:
        road._SOURCES = {path.stem: path.read_text(encoding="utf-8", errors="replace")
                         for path in sorted(Path(maps).glob("*.xodr"))}
    return road._opendrive_sources()


def run_job(job: Dict[str, Any], work: str, maps: Optional[str] = None) -> Dict[str, Any]:
    from cdf.evaluation.provenance import provenance
    from cdf.reconstruction.config import load_config
    use_maps(maps)
    result = dict(job)
    start = time.monotonic()
    result["provenance"] = provenance(load_config().to_dict(), runs=[job["run"]],
                                      perturbation="{study}:{condition}:{level}".format(**job), seed=int(job["seed"]))
    try:
        result.update((clock_job if job["study"] == "clock" else edr_job)(job, Path(work)))
        result["status"] = "complete"
    except Exception as exc:
        result.update(status="failed", error=repr(exc), traceback=traceback.format_exc())
    result["wall_s"] = round(time.monotonic() - start, 2)
    return result


def jobs_for(runs: Sequence[Path], studies: Sequence[str], seeds: int) -> List[Dict[str, Any]]:
    jobs = []
    for study in studies:
        levels = ["residual_50ms"] if study == "clock" else list(EDR_LEVELS)
        for condition in CONDITIONS:
            for level in levels:
                for seed in range(seeds):
                    for run in runs:
                        jobs.append({"run": _relative(run), "study": study, "condition": condition, "level": level,
                                     "seed": seed})
    return jobs


def _pct(values: Sequence[float], q: float) -> Optional[float]:
    if not values:
        return None
    ordered = sorted(values)
    k = (len(ordered) - 1) * q
    lo, hi = math.floor(k), math.ceil(k)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (k - lo)


def summarize(results: Sequence[Dict[str, Any]], out_dir: Path, runs: Sequence[Path] = ()) -> Dict[str, Any]:
    latest: Dict[Tuple[Any, ...], Dict[str, Any]] = {}
    for r in results:
        if r.get("status") == "complete" or job_key(r) not in latest or latest[job_key(r)].get("status") != "complete":
            latest[job_key(r)] = r
    groups: Dict[Tuple[str, str, str], List[Dict[str, Any]]] = {}
    for r in latest.values():
        groups.setdefault((r["study"], r["condition"], r["level"]), []).append(r)
    rows = []
    for (study, condition, level), rs in sorted(groups.items()):
        ok = [r for r in rs if r["status"] == "complete"]
        row: Dict[str, Any] = {"study": study, "condition": condition, "level": level, "jobs": len(rs),
                               "failed": len(rs) - len(ok), "runs": len({r["run"] for r in ok}),
                               "seeds": len({r["seed"] for r in ok}),
                               "missing_road_map": sum(1 for r in ok for m in r["road_maps"].values()
                                                       if m is None and r.get("incident_map"))}
        if study == "clock":
            truth = [abs(p["error_vs_truth_s"]) * 1000 for r in ok for p in r["pairs"]]
            shift = [abs(p["error_vs_unshifted_s"]) * 1000 for r in ok for p in r["pairs"] if "error_vs_unshifted_s" in p]
            row.update({"pairs": len(truth),
                        "error_vs_truth_ms": {"median": _pct(truth, 0.5), "p95": _pct(truth, 0.95),
                                              "max": max(truth) if truth else None},
                        "within_50ms": sum(e <= 50.0 + 1e-6 for e in truth),
                        "error_vs_unshifted_ms": {"median": _pct(shift, 0.5), "p95": _pct(shift, 0.95),
                                                  "max": max(shift) if shift else None},
                        "recorders": sum(r["recorders"] for r in ok),
                        "unaligned_unshifted": sum(r["recorders"] - r["aligned_unshifted"] for r in ok),
                        "unaligned_shifted": sum(r["recorders"] - r["aligned_shifted"] for r in ok),
                        "max_node_move_s": max((r["order"]["max_node_move_s"] or 0.0) for r in ok) if ok else None})
            for key in ("order", "order_recorders"):
                row[key] = {"jobs_same_nodes": sum(bool(r[key]["same_nodes"]) for r in ok),
                            "order_changes": sum(r[key]["order_changes"] for r in ok),
                            "ordered_pairs": sum(r[key]["ordered_pairs"] for r in ok),
                            "jobs_with_order_change": sum(r[key]["order_changes"] > 0 for r in ok),
                            "max_node_move_s": max((r[key]["max_node_move_s"] or 0.0) for r in ok) if ok else None}
            if condition == "G0":
                row["reproduces_committed"] = sum(bool(r.get("reproduces_committed_alignment"))
                                                  and bool(r.get("reproduces_committed_graph")) for r in ok)
        else:
            total = lambda key: sum(r[key] for r in ok)
            row.update({key: total(key) for key in ("true", "reportable", "detected", "identified", "invented",
                                                    "matched_events", "rejected_matches")})
            row["identified_rate"] = row["identified"] / row["reportable"] if row["reportable"] else None
            ratios = [x for r in ok for x in r["impulse_ratio"]]
            row["impulse_ratio"] = {"min": min(ratios) if ratios else None, "p05": _pct(ratios, 0.05),
                                    "median": _pct(ratios, 0.5)}
            row["unaligned"] = sum(len(r["unaligned"]) for r in ok)
            offsets = [r["max_abs_relative_offset_s"] for r in ok if r["max_abs_relative_offset_s"] is not None]
            row["max_abs_relative_offset_ms"] = round(1000 * max(offsets), 1) if offsets else None
        rows.append(row)
    record = {"definition": __doc__.strip().split("\n\n", 2)[2] if __doc__ else "",
              "parameters": {"clock_residual_s": CLOCK_RESIDUAL_S, "edr_delta_v_rel_std": EDR_LEVELS,
                             "mass_rel_std": MASS_REL_STD, "jitter_s": JITTER_S,
                             "trigger_delta_v_mps": round(TRIGGER_DELTA_V_MPS, 4), "trigger_window_s": TRIGGER_WINDOW_S,
                             "nominal_mass_kg": NOMINAL_MASS_KG,
                             "conditions": {k: {"gnss": v[0], "radar": v[1]} for k, v in CONDITIONS.items()}},
              "rows": rows}
    if runs:
        census = trigger_census(runs)
        record["trigger_census"] = census_summary(census)
        record["trigger_census"]["contacts_detail"] = census
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    (out_dir / "summary.md").write_text(markdown(rows, record.get("trigger_census")), encoding="utf-8")
    return record


def markdown(rows: Sequence[Dict[str, Any]], census: Optional[Dict[str, Any]] = None) -> str:
    def f(v: Any, nd: int = 1) -> str:
        return "-" if v is None else ("{0:.{1}f}".format(v, nd) if isinstance(v, float) else str(v))
    lines = ["# Clock residuals and crash-recorder reports", "",
             "## Residual clock offsets (uniform within +-{0:.0f} ms per recorder)".format(CLOCK_RESIDUAL_S * 1000), "",
             "| condition | jobs | failed | pairs | error median / P95 / max [ms] | within 50 ms | unaligned (unshifted / shifted) "
             "| recorder events: jobs unchanged, order changes / pairs | all events: jobs unchanged, order changes / pairs "
             "| reproduces committed |",
             "|---|--:|--:|--:|---|--:|---|---|---|--:|"]
    for r in rows:
        if r["study"] != "clock":
            continue
        e, a, b = r["error_vs_truth_ms"], r["order_recorders"], r["order"]
        lines.append("| {0} | {1} | {2} | {3} | {4} / {5} / {6} | {7} | {8} / {9} | {10}, {11} / {12} | {13}, {14} / {15} "
                     "| {16} |".format(
                         r["condition"], r["jobs"], r["failed"], r["pairs"], f(e["median"]), f(e["p95"]), f(e["max"]),
                         r["within_50ms"], r["unaligned_unshifted"], r["unaligned_shifted"],
                         a["jobs_same_nodes"], a["order_changes"], a["ordered_pairs"],
                         b["jobs_same_nodes"], b["order_changes"], b["ordered_pairs"], r.get("reproduces_committed", "-")))
    lines += ["", "## Crash-recorder-like collision reports (delta-V and mass errors, +-{0:.0f} ms timing)".format(
                  JITTER_S * 1000), "",
              "| condition | delta-V 1-sigma | jobs | failed | identified / reportable | invented | matched events "
              "| impulse ratio min / P5 / median | unaligned | max relative offset [ms] |",
              "|---|---|--:|--:|---|--:|--:|---|--:|--:|"]
    for r in rows:
        if r["study"] != "edr":
            continue
        q = r["impulse_ratio"]
        lines.append("| {0} | {1:.0f} % | {2} | {3} | {4} / {5} ({6}) | {7} | {8} | {9} / {10} / {11} | {12} | {13} |".format(
            r["condition"], 100 * EDR_LEVELS[r["level"]], r["jobs"], r["failed"], r["identified"], r["reportable"],
            f(r["identified_rate"], 3), r["invented"], r["matched_events"], f(q["min"], 3), f(q["p05"], 3),
            f(q["median"], 3), r["unaligned"], f(r["max_abs_relative_offset_ms"])))
    if census:
        lines += ["", "## Trigger census ({0} true contacts; trigger {1} km/h within {2:.0f} ms)".format(
                      census["contacts"], census["threshold_kmh"], TRIGGER_WINDOW_S * 1000), "",
                  "| delta-V from | every recorder triggers | at least one recorder triggers | none triggers |", "|---|--:|--:|--:|"]
        for key, label in (("delta_v_impulse_kmh", "impulse / {0:.0f} kg".format(NOMINAL_MASS_KG)),
                           ("delta_v_recorded_kmh", "recorded velocity")):
            c = census[key]
            lines.append("| {0} | {1} | {2} | {3} |".format(label, c["all_recorders_trigger"], c["some_recorder_triggers"],
                                                          c["none_triggers"]))
    missing = sum(r["missing_road_map"] for r in rows)
    lines += ["", "Recorders without a road map although the incident names one: {0}.".format(missing), ""]
    return "\n".join(lines)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0] if __doc__ else None)
    parser.add_argument("runs", nargs="*", type=Path)
    parser.add_argument("--studies", default="clock,edr")
    parser.add_argument("--seeds", type=int, default=3)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--work", type=Path, default=ROOT / "scratch" / "clock_edr")
    parser.add_argument("--results", type=Path, default=ROOT / "results" / "robustness" / "clock_edr")
    parser.add_argument("--max-attempts", type=int, default=2)
    parser.add_argument("--maps", help="folder of the CARLA OpenDRIVE files (*.xodr) if no installation is found")
    parser.add_argument("--summarize", action="store_true", help="only rewrite the summary from jobs.jsonl")
    args = parser.parse_args(argv)
    if (ROOT / "traces").resolve() in [args.work.resolve()] + list(args.work.resolve().parents):
        parser.error("perturbed copies never go into traces/")
    if not args.summarize and not use_maps(args.maps):
        parser.error("no OpenDRIVE maps found (--maps or a CARLA installation): no road model")
    runs = [Path(r) for r in args.runs] or scenario_runs()
    args.results.mkdir(parents=True, exist_ok=True)
    jobs_file = args.results / "jobs.jsonl"
    done = _jsonl(jobs_file)
    jobs = jobs_for(runs, [s for s in args.studies.split(",") if s], args.seeds)
    if not args.summarize:
        finished = {job_key(r) for r in done if r.get("status") == "complete"}
        attempts: Dict[Tuple[Any, ...], int] = {}
        for r in done:
            attempts[job_key(r)] = attempts.get(job_key(r), 0) + 1
        pending = [j for j in jobs
                   if job_key(j) not in finished and attempts.get(job_key(j), 0) < args.max_attempts]
        pending.sort(key=lambda j: j["condition"] == "G0")
        print("{0} jobs ({1} workers)".format(len(pending), args.workers), flush=True)
        with ProcessPoolExecutor(max_workers=args.workers) as pool, jobs_file.open("a", encoding="utf-8") as handle:
            futures = [pool.submit(run_job, job, str(args.work), args.maps) for job in pending]
            for n, future in enumerate(as_completed(futures), 1):
                result = future.result()
                result["attempt"] = attempts.get(job_key(result), 0) + 1
                handle.write(json.dumps(result) + "\n")
                handle.flush()
                done.append(result)
                print("{0}/{1} {2} {3} {4} {5} seed{6} {7} {8:.0f} s".format(
                    n, len(pending), result["status"], result["study"], result["condition"], result["level"],
                    result["seed"], _run_name(Path(result["run"])), result["wall_s"]), flush=True)
    wanted = {job_key(j) for j in jobs}
    record = summarize([r for r in done if job_key(r) in wanted], args.results, runs)
    print(markdown(record["rows"], record.get("trigger_census")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
