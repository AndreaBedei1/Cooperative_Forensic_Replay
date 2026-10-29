
from __future__ import annotations

import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

from .visibility import Box, coverage, frames_by_participant, RadarView

WARNING_WINDOW_S = 8.0
MATCH_WINDOW_S = 2.0
PHANTOM_NEAR_M = 3.0
INTRUSION_TYPES = ("EGO_PATH_ENTRY", "CUT_IN_FROM_LEFT_START", "CUT_IN_FROM_RIGHT_START")


def _manoeuvres(times: List[float]) -> List[List[float]]:
    groups: List[List[float]] = []
    for t in sorted(times):
        if groups and t - groups[-1][-1] < MATCH_WINDOW_S:
            groups[-1].append(t)
        else:
            groups.append([t])
    return groups


def match_intrusions(oracle: List[float], reconstruction: List[float]) -> Dict[str, Any]:
    near = lambda group, others: any(abs(a - b) <= MATCH_WINDOW_S for a in group for b in others)
    expected, found = _manoeuvres(oracle), _manoeuvres(reconstruction)
    hits = [group for group in expected if near(group, reconstruction)]
    return {"expected": len(expected), "found": len(hits),
            "missed": [group[0] for group in expected if not near(group, reconstruction)],
            "extra": [group[0] for group in found if not near(group, oracle)]}


def _json(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _jsonl(path: Path) -> List[Dict[str, Any]]:
    with Path(path).open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _radar_views(vehicle_dir: Path) -> List[RadarView]:
    views = []
    radar = Path(vehicle_dir) / "radar"
    for meta in sorted(radar.glob("*/metadata.json")) if radar.is_dir() else []:
        views.append(RadarView.from_metadata(_json(meta)))
    return views


def observable_seconds(run_dir: Path, recorders: List[str], min_frames: int, step: int = 1
                       ) -> Dict[str, Dict[str, Any]]:
    states = _jsonl(Path(run_dir) / "ground_truth" / "states.jsonl")
    frames = frames_by_participant(states)
    ordered = sorted(frames)
    dt = 0.05
    if len(ordered) > 1:
        a, b = frames[ordered[0]], frames[ordered[1]]
        dt = float(next(iter(b.values()))["timestamp"]) - float(next(iter(a.values()))["timestamp"])
    views = {r: _radar_views(Path(run_dir) / "vehicles" / r) for r in recorders}
    others = sorted({s["participant_id"] for s in states} - set(recorders))
    seen = {pid: 0 for pid in others}
    for frame in ordered[::step]:
        world = frames[frame]
        boxes = {pid: Box(state) for pid, state in world.items()}
        for pid in others:
            if pid not in world:
                continue
            if any(r in world and views[r] and coverage(world[r], pid, world, views[r], boxes).visible
                   for r in recorders):
                seen[pid] += step
    return {pid: {"visible_s": round(n * dt, 3), "observable": n >= min_frames} for pid, n in seen.items()}


def _origins(run_dir: Path, recorders: List[str]) -> Dict[str, float]:
    out = {}
    for r in recorders:
        path = Path(run_dir) / "vehicles" / r / "ego.jsonl"
        with path.open(encoding="utf-8") as handle:
            out[r] = float(json.loads(handle.readline())["timestamp"])
    return out


def _stat(block: Optional[Mapping[str, Any]]) -> Dict[str, Optional[float]]:
    block = block or {}
    return {"n": block.get("n", 0), "median": block.get("median"), "p95": block.get("p95"), "mean": block.get("mean"),
            "rmse": block.get("rmse")}


def run_min_track_frames(run_dir: Path) -> int:
    graph = _json(Path(run_dir) / "reconstruction" / "global" / "global_graph.json")
    return int(((graph.get("reconstruction_config") or {}).get("tracking") or {}).get("min_track_frames", 5))


def collision_score(evaluation: Mapping[str, Any], recorders: List[str]) -> Dict[str, Any]:
    contacts = []
    for c in evaluation.get("collisions", []):
        pair = tuple(sorted(c["participants"]))
        contacts.append({"pair": "-".join(pair), "sim_time": c["sim_time"],
                         "involves_recorder": any(p in recorders for p in pair),
                         "recontacts": len(c.get("recontacts") or []),
                         "detected": c.get("reconstructed_as") is not None,
                         "participants_correct": bool(c.get("participants_correct")),
                         "timing_error_s": c.get("report_timing_error_s")})
    n_true = len(contacts)
    reportable = sum(c["involves_recorder"] for c in contacts)
    detected = sum(c["detected"] for c in contacts)
    identified = sum(c["detected"] and c["participants_correct"] for c in contacts)
    extras = list(evaluation.get("extra_collisions", []))
    splits = [e for e in extras if e.get("true_recontact")]
    invented = [e for e in extras if not e.get("true_recontact")]
    claimed = detected + len(invented) + len(splits)
    timing = [abs(c["timing_error_s"]) for c in contacts if c["detected"] and c["timing_error_s"] is not None]
    return {"true": n_true, "reportable": reportable, "detected": detected, "identified": identified,
            "invented": len(invented), "recontact_splits": len(splits),
            "recall": detected / reportable if reportable else None,
            "participants_correct_rate": identified / reportable if reportable else None,
            "precision": identified / claimed if claimed else None,
            "max_abs_timing_error_s": max(timing) if timing else None, "contacts": contacts,
            "invented_list": invented, "recontact_split_list": splits}


def association_score(fusion: Mapping[str, Any], phantoms: List[str]) -> Dict[str, Any]:
    counts = fusion.get("decision_counts", {})
    return {"decisions": counts, "wrong_links": counts.get("WRONG link", 0), "missed_links": counts.get("missed link", 0),
            "merges": fusion.get("merges", {}),
            "fragmented_vehicles": {k: v for k, v in (fusion.get("fragmentation") or {}).items() if len(v) > 1},
            "phantoms": len(phantoms)}


def scorecard(run_dir: Path, min_track_frames: Optional[int] = None,
              oracle: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    run_dir = Path(run_dir)
    ev_dir = run_dir / "reconstruction" / "evaluation"
    evaluation = _json(ev_dir / "evaluation.json")
    fusion = _json(ev_dir / "fusion_metrics.json")
    if oracle is None and (ev_dir / "event_oracle.json").exists():
        oracle = _json(ev_dir / "event_oracle.json")
    gt_meta = _json(run_dir / "ground_truth" / "metadata.json")
    recorders = [p["participant_id"] for p in gt_meta.get("participants", []) if p.get("record")]
    all_vehicles = [p["participant_id"] for p in gt_meta.get("participants", [])]
    if not all_vehicles:
        with (run_dir / "ground_truth" / "states.jsonl").open(encoding="utf-8") as handle:
            all_vehicles = sorted({json.loads(line)["participant_id"] for line in handle if line.strip()})
        recorders = sorted(p.name for p in (run_dir / "vehicles").iterdir() if (p / "ego.jsonl").exists())

    collisions = collision_score(evaluation, recorders)
    contacts = collisions["contacts"]

    if min_track_frames is None:
        min_track_frames = run_min_track_frames(run_dir)
    visibility = observable_seconds(run_dir, recorders, min_track_frames)
    entities = fusion.get("entities", [])
    per_truth: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    phantoms, phantoms_near = [], []
    for e in entities:
        if e.get("true_identity") is None:
            phantoms.append(e["id"])
            if e.get("nearest_vehicle_m") is not None and e["nearest_vehicle_m"] <= PHANTOM_NEAR_M:
                phantoms_near.append(e["id"])
        else:
            per_truth[e["true_identity"]].append(e)
    entity_cov = {e["id"]: e.get("coverage_s", 0.0) for e in fusion.get("entity_errors", [])}
    vehicles = []
    for pid in all_vehicles:
        if pid in recorders:
            vehicles.append({"vehicle": pid, "role": "recorder", "observable": True, "represented": True,
                             "road_users": [], "coverage": 1.0})
            continue
        vis = visibility.get(pid, {"visible_s": 0.0, "observable": False})
        mine = [e for e in per_truth.get(pid, []) if not e.get("identity_is_recorder")]
        represented_s = sum(entity_cov.get(e["id"], 0.0) for e in mine)
        cov = min(1.0, represented_s / vis["visible_s"]) if vis["visible_s"] > 0 else None
        vehicles.append({"vehicle": pid, "role": "non-recorder", "observable": vis["observable"],
                         "visible_s": vis["visible_s"], "represented": bool(mine),
                         "road_users": [e["id"] for e in mine], "coverage": None if cov is None else round(cov, 3)})
    observable = [v for v in vehicles if v["observable"]]
    duplicates = sum(max(0, len(v["road_users"]) - 1) for v in vehicles)
    recorder_ghosts = sorted(e["id"] for e in entities if e.get("identity_is_recorder"))
    completeness = {"true_vehicles": len(vehicles), "recorders": len(recorders),
                    "observable": len(observable), "represented_observable": sum(v["represented"] for v in observable),
                    "unobservable": [v["vehicle"] for v in vehicles if not v["observable"]],
                    "missed_observable": [v["vehicle"] for v in observable if not v["represented"]],
                    "represented_unobservable": [v["vehicle"] for v in vehicles
                                                 if not v["observable"] and v["represented"]],
                    "duplicates": duplicates, "recorder_ghosts": recorder_ghosts, "phantoms": phantoms,
                    "phantoms_near": phantoms_near, "phantoms_far": [p for p in phantoms if p not in phantoms_near],
                    "min_track_frames": min_track_frames, "vehicles": vehicles}

    se = fusion.get("road_user_state_errors", fusion.get("state_errors", {}))
    errors = {"centre_error_m": _stat(se.get("centre_error_m")), "speed_error_mps": _stat(se.get("speed_error_mps")),
              "velocity_error_mps": _stat(se.get("velocity_error_mps")),
              "heading_error_deg_diagnostic": _stat(se.get("heading_error_deg"))}

    association = association_score(fusion, phantoms)

    semantics: Dict[str, Any] = {"available": oracle is not None}
    if oracle is not None:
        origins = _origins(run_dir, recorders)
        rec_events = oracle["events"].get("RECONSTRUCTION", {})
        cov_events = oracle["events"].get("COVERAGE", {})

        def starts(events: Mapping[str, List[Dict[str, Any]]], r: str, s: str, kinds: Tuple[str, ...]) -> List[float]:
            return sorted(float(e["t_local"]) for e in events.get(r, []) if e["type"] in kinds and e["subject"] == s)

        warnings = []
        contact_local: Dict[Tuple[str, str], List[float]] = defaultdict(list)
        for c in contacts:
            a, b = c["pair"].split("-")
            for r, s in ((a, b), (b, a)):
                if r not in recorders:
                    continue
                tc = float(c["sim_time"]) - origins[r]
                contact_local[(r, s)].append(tc)
                window = lambda ts: [t for t in ts if tc - WARNING_WINDOW_S <= t <= tc]
                rec = window(starts(rec_events, r, s, ("CRITICAL_TTC_START",)))
                ora = window(starts(cov_events, r, s, ("CRITICAL_TTC_START",)))
                warnings.append({"recorder": r, "partner": s, "contact_t_local": round(tc, 3),
                                 "warned": bool(rec), "in_time": bool([t for t in rec if t < tc]),
                                 "lead_time_s": round(tc - rec[0], 3) if rec else None,
                                 "justified": bool(ora), "oracle_lead_time_s": round(tc - ora[0], 3) if ora else None})
        intrusions = {"expected": 0, "found": 0, "missed": [], "extra": []}
        for r in recorders:
            subjects = {e["subject"] for e in cov_events.get(r, []) + rec_events.get(r, [])
                        if e["type"] in INTRUSION_TYPES}
            for s in sorted(subjects, key=str):
                m = match_intrusions(starts(cov_events, r, s, INTRUSION_TYPES), starts(rec_events, r, s, INTRUSION_TYPES))
                intrusions["expected"] += m["expected"]
                intrusions["found"] += m["found"]
                intrusions["missed"] += ["{0}/{1}@{2:.2f}".format(r, s, t) for t in m["missed"]]
                intrusions["extra"] += ["{0}/{1}@{2:.2f}".format(r, s, t) for t in m["extra"]]
        unconfirmed = []
        for r in recorders:
            for e in rec_events.get(r, []):
                if e["type"] != "CRITICAL_TTC_START" or e["subject"] is None:
                    continue
                t, s = float(e["t_local"]), e["subject"]
                if any(abs(t - u) <= MATCH_WINDOW_S for u in starts(cov_events, r, s, ("CRITICAL_TTC_START",))):
                    continue
                if any(0.0 <= tc - t <= WARNING_WINDOW_S for tc in contact_local.get((r, s), [])):
                    continue
                unconfirmed.append("{0}/{1}@{2:.2f}".format(r, s, t))
        in_time = [w for w in warnings if w["justified"]]
        semantics.update({
            "critical_ttc_warnings": warnings,
            "justified_warnings": len(in_time),
            "justified_warned_in_time": sum(w["in_time"] for w in in_time),
            "lead_time_s": [w["lead_time_s"] for w in in_time if w["in_time"]],
            "path_intrusions": intrusions,
            "unconfirmed_critical_ttc": unconfirmed})
    return {"run": "{0}/{1}".format(run_dir.parent.name, run_dir.name), "recorders": recorders,
            "collisions": collisions, "completeness": completeness, "errors": errors,
            "association": association, "semantics": semantics}


def _fmt(v: Any) -> str:
    if v is None:
        return "–"
    if isinstance(v, float):
        return "{0:.3f}".format(v)
    return str(v)


def summary_rows(cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for c in cards:
        col, com, err, ass, sem = (c["collisions"], c["completeness"], c["errors"], c["association"], c["semantics"])
        rows.append({
            "run": c["run"], "contacts": col["true"], "detected": col["detected"], "identified": col["identified"],
            "invented": col["invented"], "recontact_splits": col.get("recontact_splits", 0),
            "max_dt_s": col["max_abs_timing_error_s"],
            "vehicles": com["true_vehicles"], "observable": com["observable"],
            "represented": com["represented_observable"], "missed": ",".join(com["missed_observable"]),
            "duplicates": com["duplicates"], "rec_ghosts": len(com.get("recorder_ghosts", [])),
            "phantoms": len(com["phantoms"]), "phantoms_near": len(com.get("phantoms_near", [])),
            "pos_med_m": err["centre_error_m"]["median"], "pos_p95_m": err["centre_error_m"]["p95"],
            "pos_rmse_m": err["centre_error_m"].get("rmse"),
            "spd_med_mps": err["speed_error_mps"]["median"], "spd_p95_mps": err["speed_error_mps"]["p95"],
            "wrong_links": ass["wrong_links"], "missed_links": ass.get("missed_links"),
            "missed_merges": (ass["merges"] or {}).get("missed"), "false_merges": (ass["merges"] or {}).get("false"),
            "ttc_justified": sem.get("justified_warnings"), "ttc_in_time": sem.get("justified_warned_in_time"),
            "intrusions": "{0}/{1}".format((sem.get("path_intrusions") or {}).get("found"),
                                           (sem.get("path_intrusions") or {}).get("expected")),
            "unconfirmed_ttc": (None if "unconfirmed_critical_ttc" not in sem
                                else len(sem["unconfirmed_critical_ttc"])),
        })
    return rows


def markdown(cards: List[Dict[str, Any]], title: str) -> str:
    rows = summary_rows(cards)
    keys = list(rows[0]) if rows else []
    out = ["# " + title, "", "| " + " | ".join(keys) + " |", "|" + "---|" * len(keys)]
    out += ["| " + " | ".join(_fmt(r[k]) for k in keys) + " |" for r in rows]
    tot = lambda k: sum(r[k] or 0 for r in rows)
    out += ["", "Totals: contacts {0}, detected {1}, identified {2}, invented {3}; observable vehicles {4}, "
            "represented {5}, duplicates {6}, recorder ghosts {12}, phantoms {7}; wrong links {8}; justified "
            "CRITICAL_TTC warnings {9}, in time {10}; unconfirmed alarms {11}.".format(
                tot("contacts"), tot("detected"), tot("identified"), tot("invented"), tot("observable"),
                tot("represented"), tot("duplicates"), tot("phantoms"), tot("wrong_links"), tot("ttc_justified"),
                tot("ttc_in_time"), tot("unconfirmed_ttc"), tot("rec_ghosts"))]
    return "\n".join(out) + "\n"


PAIRED = ("identified", "invented", "represented", "missed_observable", "duplicates", "rec_ghosts", "phantoms",
          "pos_med_m")


def _numbers(card: Mapping[str, Any]) -> Dict[str, Any]:
    col, com, err, ass, sem = (card["collisions"], card["completeness"], card["errors"], card["association"],
                               card.get("semantics") or {})
    intrusions = sem.get("path_intrusions") or {}
    if "vehicles" in com:
        others = [v for v in com["vehicles"] if v.get("role") != "recorder" and v.get("observable")]
        observable, represented = len(others), sum(1 for v in others if v.get("represented"))
    else:
        n_recorders = len(card.get("recorders") or [])
        observable, represented = com["observable"] - n_recorders, com["represented_observable"] - n_recorders
    phantoms_near = com.get("phantoms_near")
    return {"contacts": col["true"], "reportable": col.get("reportable", col["true"]), "detected": col["detected"],
            "identified": col["identified"], "invented": col["invented"],
            "recontact_splits": col.get("recontact_splits", 0), "max_dt_s": col.get("max_abs_timing_error_s"),
            "observable": observable, "represented": represented,
            "missed_observable": len(com["missed_observable"]), "duplicates": com["duplicates"],
            "rec_ghosts": len(com.get("recorder_ghosts", [])), "phantoms": len(com["phantoms"]),
            "phantoms_near": None if phantoms_near is None else len(phantoms_near),
            "phantoms_far": None if phantoms_near is None else len(com["phantoms"]) - len(phantoms_near),
            "pos_med_m": err["centre_error_m"]["median"], "pos_p95_m": err["centre_error_m"]["p95"],
            "pos_rmse_m": err["centre_error_m"].get("rmse"),
            "spd_med_mps": err["speed_error_mps"]["median"], "spd_p95_mps": err["speed_error_mps"]["p95"],
            "spd_rmse_mps": err["speed_error_mps"].get("rmse"),
            "wrong_links": ass["wrong_links"], "missed_links": ass.get("missed_links"),
            "missed_merges": (ass.get("merges") or {}).get("missed"),
            "false_merges": (ass.get("merges") or {}).get("false"),
            "ttc_justified": sem.get("justified_warnings"), "ttc_in_time": sem.get("justified_warned_in_time"),
            "intrusions_found": intrusions.get("found"), "intrusions_expected": intrusions.get("expected"),
            "unconfirmed_ttc": (None if "unconfirmed_critical_ttc" not in sem
                                else len(sem["unconfirmed_critical_ttc"]))}


def _run_name(run: str) -> str:
    path = Path(str(run).replace("\\", "/"))
    return "{0}/{1}".format(path.parent.name, path.name)


def campaign_rows(records: List[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    baselines = {_run_name(r["run"]): _numbers(r["scorecard"]) for r in records
                 if r.get("family") == "baseline" and r.get("status") == "complete" and r.get("scorecard")}
    run_recorders = {_run_name(r["run"]): len(r["scorecard"].get("recorders") or []) for r in records
                     if r.get("status") == "complete" and r.get("scorecard")}
    rows = []
    for r in records:
        row: Dict[str, Any] = {"run": _run_name(r["run"]), "family": r["family"], "level": r["level"],
                               "seed": int(r["seed"]), "recorder": r.get("recorder"), "status": r.get("status")}
        card = r.get("scorecard")
        if r.get("status") != "complete" or not card:
            row["error"] = r.get("error") or (r.get("evaluation_errors") or {}).get("scorecard")
            row["recorders"] = run_recorders.get(row["run"])
            rows.append(row)
            continue
        n_recorders = len(card.get("recorders") or [])
        row["recorders"] = n_recorders
        row["degraded"] = len(r["recorder"].split("+")) if r.get("recorder") else n_recorders
        numbers = _numbers(card)
        row.update(numbers)
        base = baselines.get(row["run"])
        for key in PAIRED:
            value = numbers[key]
            row["d_" + key] = (None if base is None or value is None or base[key] is None
                               else round(value - base[key], 6))
        rows.append(row)
    return rows


def _subset(row: Mapping[str, Any]) -> str:
    if row["family"] not in ("radar_asym", "radar_asym_gnss") or not row.get("recorder"):
        return "all"
    return "alone" if len(row["recorder"].split("+")) == 1 else "all but one"


def condition_table(rows: List[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    groups: Dict[Tuple[str, str, str, Optional[int]], List[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(row["family"], row["level"], _subset(row), row.get("recorders"))].append(row)
    table = []
    for (family, level, subset, recorders), members in groups.items():
        done = [m for m in members if m["status"] == "complete" and "identified" in m]
        per_seed: Dict[int, List[Mapping[str, Any]]] = defaultdict(list)
        for m in done:
            per_seed[m["seed"]].append(m)
        pooled = []
        for _, ms in sorted(per_seed.items()):
            total = lambda key: sum(m[key] or 0 for m in ms)
            per_job = lambda key: total(key) / len(ms)
            paired = lambda key: (statistics.fmean([m["d_" + key] for m in ms if m.get("d_" + key) is not None])
                                  if any(m.get("d_" + key) is not None for m in ms) else None)
            positions = [m["pos_med_m"] for m in ms if m["pos_med_m"] is not None]
            pooled.append({
                "collisions_identified_rate": (total("identified") / total("reportable")
                                               if total("reportable") else None),
                "collisions_detected_rate": total("detected") / total("reportable") if total("reportable") else None,
                "invented": per_job("invented"),
                "represented_rate": total("represented") / total("observable") if total("observable") else None,
                "duplicates": per_job("duplicates"), "rec_ghosts": per_job("rec_ghosts"), "phantoms": per_job("phantoms"),
                "pos_med_m": statistics.median(positions) if positions else None,
                "d_identified": paired("identified"), "d_invented": paired("invented"),
                "d_represented": paired("represented"), "d_duplicates": paired("duplicates"),
                "d_phantoms": paired("phantoms")})
        row: Dict[str, Any] = {"family": family, "level": level, "subset": subset, "recorders": recorders,
                               "seeds": len(pooled),
                               "jobs": len(members), "failed": len(members) - len(done)}
        for key in (pooled[0] if pooled else {}):
            values = [p[key] for p in pooled if p[key] is not None]
            row[key] = round(statistics.fmean(values), 4) if values else None
            row[key + "_sd"] = round(statistics.stdev(values), 4) if len(values) > 1 else None
        table.append(row)
    order = ("baseline", "gnss", "radar_v3", "radar_asym", "radar_gnss_v3", "radar_asym_gnss")
    table.sort(key=lambda r: (order.index(r["family"]) if r["family"] in order else len(order), r["family"],
                              r["recorders"] or 0))
    return table


CONDITION_COLUMNS = (("collisions_identified_rate", "collisions identified", 3), ("invented", "invented", 1),
                     ("represented_rate", "observable represented", 3), ("duplicates", "duplicates", 1),
                     ("rec_ghosts", "recorder ghosts", 1), ("phantoms", "phantoms", 1),
                     ("pos_med_m", "median of the per-job position medians [m]", 3), ("d_identified", "paired d identified", 2),
                     ("d_represented", "paired d represented", 2), ("d_phantoms", "paired d phantoms", 1))


def campaign_markdown(table: List[Mapping[str, Any]], title: str) -> str:
    def cell(row: Mapping[str, Any], key: str, decimals: int) -> str:
        value = row.get(key)
        if value is None:
            return "-"
        sd = row.get(key + "_sd")
        text = "{0:.{1}f}".format(value, decimals)
        return text + (" +- {0:.{1}f}".format(sd, decimals) if sd else "")
    head = ["family", "level", "degraded", "recorders", "seeds", "jobs", "failed"] + [h for _, h, _ in CONDITION_COLUMNS]
    out = ["# " + title, "",
           "Per seed the jobs are pooled: rates are ratios of sums; counts and paired changes from the G0 baseline "
           "of the same run are means per job.  Then the mean over seeds +- SD.  Represented: observable road users "
           "that record nothing.  Definitions: `cdf.evaluation.scorecard`.", "",
           "| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for row in table:
        out.append("| " + " | ".join([row["family"], row["level"], row["subset"], str(row["recorders"]),
                                      str(row["seeds"]), str(row["jobs"]),
                                      str(row["failed"])] + [cell(row, k, d) for k, _, d in CONDITION_COLUMNS]) + " |")
    return "\n".join(out) + "\n"
