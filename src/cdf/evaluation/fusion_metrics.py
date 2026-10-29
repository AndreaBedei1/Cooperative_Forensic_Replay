
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict

import numpy as np
from itertools import combinations
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from ..reconstruction.render import write_json, write_text
from ..replay.model import ReplayRun
from .gt_audit import stats, truth_of
from .reconstruction import _box_distance, _to_world

IDENTITY_MAX_BOX_DISTANCE_M = 1.5
HEADING_MIN_SPEED_MPS = 2.0
EXPECTED_WITHIN = {"1_sigma": 1.0 - math.exp(-0.5), "2_sigma": 1.0 - math.exp(-2.0), "3_sigma": 1.0 - math.exp(-4.5)}


def _read_json(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    path = Path(path)
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _yaw_error(a: float, b: float) -> float:
    return abs((a - b + 180.0) % 360.0 - 180.0)


def evaluate_fusion(run_dir: Path, write: bool = True, pose_factory: Any = None) -> Dict[str, Any]:
    run_dir = Path(run_dir)
    rec = run_dir / "reconstruction"
    alignment = _read_json(rec / "global" / "alignment.json")
    associations = _read_json(rec / "global" / "associations.json")
    road_users = _read_json(rec / "global" / "anonymous_entities.json")
    recorders = sorted(alignment["graphs"])
    origins = {name: _read_json(rec / name / "local_graph.json")["recorder"]["clock"]["origin_source_timestamp"]
               for name in recorders}
    first_poses = {name: _read_jsonl(run_dir / "vehicles" / name / "ego.jsonl")[0] for name in recorders}
    replay = ReplayRun.load(run_dir, pose_factory=pose_factory)
    paths = {(pid, path.track_id): path for pid, items in replay.tracks.items() for path in items}
    truth, _ = truth_of(run_dir)
    aligned = {name for name, clock in alignment["graphs"].items() if clock["status"] == "ALIGNED"}

    reference_sim = None
    for name in recorders:
        clock = alignment["graphs"][name]
        if clock["status"] == "ALIGNED" and clock.get("method", "matched_collisions") in ("matched_collisions",
                                                                                         "reference_recorder"):
            reference_sim = -clock["offset_to_global"] + origins[name]
            break

    decision = {(a["local_graph"], a["local_track"]): a for a in associations}
    samples_of: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for name in recorders:
        for row in _read_jsonl(rec / name / "local_tracks.jsonl"):
            point = _to_world(first_poses[name], row["x_m"], row["y_m"])
            sim = row["t_local"] + origins[name]
            states = {pid: track.at(sim) for pid, track in truth.items() if pid != name}
            distances = {pid: _box_distance(point, state) for pid, state in states.items() if state is not None}
            best = min(distances, key=distances.get) if distances else None
            identity = best if best is not None and distances[best] <= IDENTITY_MAX_BOX_DISTANCE_M else None
            samples_of[name + ":" + row["track_id"]].append(dict(row, recorder=name, world=point, sim=sim,
                                                                identity=identity,
                                                                nearest_m=None if best is None else distances[best]))
    track_identity = {}
    for key, rows in samples_of.items():
        votes = Counter(row["identity"] for row in rows if row["measured"])
        track_identity[key] = votes.most_common(1)[0][0] if votes else None

    decisions = []
    for (owner, track_id), item in sorted(decision.items()):
        if owner not in aligned:
            continue
        key = owner + ":" + track_id
        identity = track_identity.get(key)
        rows = samples_of.get(key, [])
        purity = (sum(row["identity"] == identity for row in rows if row["measured"])
                  / max(sum(row["measured"] for row in rows), 1))
        if item["status"] == "ASSOCIATED":
            verdict = "correct link" if item["global_entity"] == identity else "WRONG link"
        elif identity in recorders:
            verdict = "missed link (true identity {0})".format(identity)
        elif identity is None:
            verdict = "anonymous (clutter: no true vehicle)"
        else:
            verdict = "anonymous (non-recording road user {0})".format(identity)
        common_frame = any(str(line).startswith("common frame:") for line in item.get("evidence", []))
        decisions.append({"track": key, "decision": item["global_entity"], "status": item["status"],
                          "by": "common_frame" if common_frame else ("collision" if item["status"] == "ASSOCIATED"
                                                                    else None),
                          "true_identity": identity, "purity": round(purity, 3), "verdict": verdict})

    entity_rows, merge = [], {"correct": 0, "false": 0, "missed": 0}
    member_of = {}
    for entity in road_users.get("entities", []):
        for name in entity["source_tracks"]:
            member_of[name] = entity["id"]
    for entity in road_users.get("entities", []):
        rows = [row for name in entity["source_tracks"] for row in samples_of.get(name, []) if row["measured"]]
        votes = Counter(row["identity"] for row in rows)
        majority = votes.most_common(1)[0][0] if votes else None
        nearest = [row["nearest_m"] for row in rows if row["nearest_m"] is not None]
        entity_rows.append({"id": entity["id"], "source_tracks": entity["source_tracks"],
                            "observers": entity["observers"], "true_identity": majority,
                            "identity_is_recorder": majority in recorders,
                            "purity": round(votes[majority] / len(rows), 3) if rows else None,
                            "nearest_vehicle_m": (round(float(np.median(nearest)), 3)
                                                  if majority is None and nearest else None),
                            "track_identities": {name: track_identity.get(name) for name in entity["source_tracks"]}})
    tracks = sorted(member_of)
    for first, second in combinations(tracks, 2):
        same_entity = member_of[first] == member_of[second]
        a, b = track_identity.get(first), track_identity.get(second)
        same_truth = a is not None and a == b
        if same_entity and same_truth:
            merge["correct"] += 1
        elif same_entity:
            merge["false"] += 1
        elif same_truth:
            merge["missed"] += 1
    fragmentation = {}
    for name in tracks:
        identity = track_identity.get(name)
        if identity is not None:
            fragmentation.setdefault(identity, set()).add(member_of[name])
    fragmentation = {pid: sorted(ids) for pid, ids in sorted(fragmentation.items())}

    errors: Dict[str, List[float]] = defaultdict(list)
    road_user_errors: Dict[str, List[float]] = defaultdict(list)
    by_method: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
    within = Counter()
    states_compared = impure_states = 0
    entity_errors = []
    paired_states = []
    for entity, row in zip(road_users.get("entities", []), entity_rows):
        identity = row["true_identity"]
        if identity is None or identity not in truth or reference_sim is None:
            continue
        own: Dict[str, List[float]] = defaultdict(list)
        impure = 0
        for state in entity["trajectory"]:
            true = truth[identity].at(reference_sim + state["t_global"])
            if true is None:
                continue
            on = []
            for name in entity["source_tracks"]:
                owner = name.split(":", 1)[0]
                t_local = state["t_global"] - alignment["graphs"][owner]["offset_to_global"]
                near = [r for r in samples_of.get(name, []) if abs(r["t_local"] - t_local) <= 0.051]
                if near:
                    on.append(min(near, key=lambda r: abs(r["t_local"] - t_local))["identity"])
            if any(who != identity for who in on):
                impure += 1
                continue
            states_compared += 1
            centre = math.hypot(state["x"] - true["transform"]["x"], state["y"] - true["transform"]["y"])
            velocity = math.hypot(state["vx"] - true["velocity"]["x"], state["vy"] - true["velocity"]["y"])
            speed = math.hypot(state["vx"], state["vy"]) - math.hypot(true["velocity"]["x"], true["velocity"]["y"])
            values = {"centre_error_m": centre, "velocity_error_mps": velocity, "speed_error_mps": abs(speed)}
            true_speed = math.hypot(true["velocity"]["x"], true["velocity"]["y"])
            if state["heading_deg"] is not None and true_speed >= HEADING_MIN_SPEED_MPS:
                values["heading_error_deg"] = _yaw_error(state["heading_deg"], true["transform"]["yaw_deg"])
            for key, value in values.items():
                errors[key].append(value)
                own[key].append(value)
                by_method[state["method"]][key].append(value)
                if not row["identity_is_recorder"]:
                    road_user_errors[key].append(value)
            if state["pos_std_m"] and state["pos_std_m"] > 0:
                ratio = centre / state["pos_std_m"]
                errors["normalised_centre_error"].append(ratio)
                for k in (1, 2, 3):
                    within["{0}_sigma".format(k)] += ratio <= k
            single_errors = []
            for name in entity["source_tracks"]:
                owner, track_id = name.split(":", 1)
                path = paths.get((owner, track_id))
                if path is None:
                    continue
                t_replay = (state["t_global"] - alignment["graphs"][owner]["offset_to_global"]
                            + replay.clock_origins[owner] - replay.start)
                ghost = path.state_at(t_replay)
                if ghost is not None:
                    single_errors.append(math.hypot(ghost.centre[0] - true["transform"]["x"],
                                                    ghost.centre[1] - true["transform"]["y"]))
            if single_errors:
                errors['single_track_nominal_centre_error_m'].append(float(np.median(single_errors)))
            paired_states.append({'t_global': state['t_global'], 'sim_timestamp': round(reference_sim+state['t_global'],4),
                'true_identity': identity, 'entity': entity['id'], 'method': state['method'],
                'source_tracks': list(entity['source_tracks']), 'centre_error_m': centre, 'velocity_error_mps': velocity,
                'single_track_centre_errors_m': single_errors,
                'single_track_error_median_m': float(np.median(single_errors)) if single_errors else None,
                'fragments_for_identity': sum(row['true_identity']==identity for row in entity_rows)})
        extent = truth[identity].states[0].get("bbox_extent") or {}
        footprint = entity["footprint"]
        dims = {}
        if extent:
            dims = {"length_error_m": round(footprint["length_m"] - 2.0 * extent["x"], 3),
                    "width_error_m": round(footprint["width_m"] - 2.0 * extent["y"], 3),
                    "length_source": footprint["length"]["source"], "width_source": footprint["width"]["source"],
                    "true_length_m": round(2.0 * extent["x"], 3), "true_width_m": round(2.0 * extent["y"], 3)}
            errors["length_error_m"].append(abs(dims["length_error_m"]))
            errors["width_error_m"].append(abs(dims["width_error_m"]))
        span = entity["time_span"][1] - entity["time_span"][0]
        errors["coverage_s"].append(span)
        impure_states += impure
        entity_errors.append(dict({"id": entity["id"], "true_identity": identity, "coverage_s": round(span, 3),
                                   "states": len(own.get("centre_error_m", [])), "impure_states": impure},
                                  **{key: stats(values) for key, values in own.items()}, **dims))

    observed_alignment = []
    for item in road_users.get("observed_alignment", []):
        if item.get("method") != "observed_trajectories":
            continue
        name = item["recorder"]
        clock = alignment["graphs"][name]
        true_offset = None
        if reference_sim is not None:
            true_offset = round(-(reference_sim - origins[name]), 4)
        estimated = item.get("offset_to_global")
        observed_alignment.append({"recorder": name, "accepted": item["accepted"], "estimated_offset_s": estimated,
                                   "true_offset_s": true_offset,
                                   "error_s": None if estimated is None or true_offset is None
                                   else round(estimated - true_offset, 4),
                                   "interval": item.get("interval"), "status": clock["status"]})

    counts = Counter(row["verdict"].split(" (")[0] for row in decisions)
    result = {
        "run": "{0}/{1}".format(run_dir.parent.name, run_dir.name),
        "privileged_assumptions": ["recorder raw clocks are CARLA simulator time",
                                   "a vehicle box is centred on its origin in the horizontal plane"],
        "identity_max_box_distance_m": IDENTITY_MAX_BOX_DISTANCE_M,
        "track_decisions": decisions,
        "decision_counts": dict(sorted(counts.items())),
        "entities": entity_rows,
        "merges": merge,
        "fragmentation": fragmentation,
        "state_errors": {key: stats(values) for key, values in sorted(errors.items())},
        "road_user_state_errors": {key: stats(values) for key, values in sorted(road_user_errors.items())},
        "state_errors_by_method": {method: {key: stats(values) for key, values in sorted(values.items())}
                                   for method, values in sorted(by_method.items())},
        "calibration": {"states": len(errors.get("normalised_centre_error", [])),
                        "observed_within": {key: round(within[key] / max(len(errors.get("normalised_centre_error", [])), 1), 3)
                                            for key in EXPECTED_WITHIN},
                        "expected_within_gaussian": {key: round(value, 3) for key, value in EXPECTED_WITHIN.items()}},
        "entity_errors": entity_errors,
        "observed_alignment": observed_alignment,
        "states_compared": states_compared,
        "impure_states": impure_states,
    }
    if write:
        write_json(rec / "evaluation" / "fusion_metrics.json", result)
        write_text(rec / "evaluation" / "fusion_metrics.md", fusion_markdown(result))
    result["_raw"] = {"errors": {key: list(values) for key, values in errors.items()},
                      "road_user_errors": {key: list(values) for key, values in road_user_errors.items()},
                       'paired_states': paired_states,
                      "by_method": {method: {key: list(values) for key, values in table.items()}
                                    for method, table in by_method.items()}}
    return result


def _cell(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return "{0:.3f}".format(value)
    return str(value)


def stats_lines(table: Dict[str, Dict[str, Any]]) -> List[str]:
    lines = ["| Quantity | n | median | q25 | q75 | IQR | p90 | p95 | max |",
             "|----------|--:|-------:|----:|----:|----:|----:|----:|----:|"]
    for key, row in table.items():
        lines.append("| {0} | {1} | {2} | {3} | {4} | {5} | {6} | {7} | {8} |".format(
            key, row["n"], *(_cell(row[k]) for k in ("median", "q25", "q75", "iqr", "p90", "p95", "max"))))
    return lines


def fusion_markdown(result: Dict[str, Any]) -> str:
    lines = ["# Road-user fusion against ground truth - " + result["run"], "",
             "Privileged evaluation (ground truth used here only). Assumptions: " +
             "; ".join(result["privileged_assumptions"]) + ".", "",
             "## Track identity decisions (aligned recorders)", "",
             "| Track | Decision | Status | By | True identity | Purity | Verdict |",
             "|-------|----------|--------|----|---------------|-------:|---------|"]
    for row in result["track_decisions"]:
        lines.append("| {0} | {1} | {2} | {3} | {4} | {5} | {6} |".format(
            row["track"], row["decision"], row["status"], _cell(row["by"]), _cell(row["true_identity"]),
            _cell(row["purity"]), row["verdict"]))
    lines += ["", "Counts: " + ", ".join("{0}: {1}".format(k, v) for k, v in result["decision_counts"].items()), "",
              "## Anonymous entities", "",
              "| Entity | Source tracks | True identity | Recorder? | Purity |",
              "|--------|---------------|---------------|-----------|-------:|"]
    for row in result["entities"]:
        lines.append("| {0} | {1} | {2} | {3} | {4} |".format(
            row["id"], ", ".join(row["source_tracks"]), _cell(row["true_identity"]),
            "yes" if row["identity_is_recorder"] else "no", _cell(row["purity"])))
    merges = result["merges"]
    lines += ["", "Merges over pairs of anonymous tracks: correct {0}, false {1}, missed {2}.".format(
        merges["correct"], merges["false"], merges["missed"]),
              "Fragmentation (true road user -> entities): " + (", ".join(
                  "{0} -> {1}".format(pid, "/".join(ids)) for pid, ids in result["fragmentation"].items()) or "none"),
              "", "## Fused state errors (against the majority identity, {0} pure states; {1} impure states "
                  "where a source track was on another body, excluded)".format(
                      result["states_compared"], result["impure_states"]), ""]
    lines += stats_lines(result["state_errors"])
    for method, table in result["state_errors_by_method"].items():
        lines += ["", "### Method: " + method, ""] + stats_lines(table)
    calibration = result["calibration"]
    lines += ["", "Calibration of pos_std_m over {0} states: within 1/2/3 sigma {1} (Gaussian: {2}).".format(
        calibration["states"], "/".join(_cell(calibration["observed_within"][k]) for k in EXPECTED_WITHIN),
        "/".join(_cell(calibration["expected_within_gaussian"][k]) for k in EXPECTED_WITHIN))]
    if result["observed_alignment"]:
        lines += ["", "## Observed-trajectory alignment", "",
                  "| Recorder | Accepted | Estimated offset | True offset | Error | Interval |",
                  "|----------|----------|-----------------:|------------:|------:|----------|"]
        for row in result["observed_alignment"]:
            lines.append("| {0} | {1} | {2} | {3} | {4} | {5} |".format(
                row["recorder"], row["accepted"], _cell(row["estimated_offset_s"]), _cell(row["true_offset_s"]),
                _cell(row["error_s"]), _cell(row["interval"])))
    return "\n".join(lines) + "\n"
