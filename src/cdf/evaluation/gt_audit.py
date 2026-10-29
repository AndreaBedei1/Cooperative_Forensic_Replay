
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from ..replay.model import ReplayRun
from .reconstruction import TruthTrack, _box_distance, _surface_distance, _to_world, box_gap

CORRIDOR_HALF_WIDTH_M = 1.5
IDENTITY_MAX_DISTANCE_M = 3.0
HEADING_MIN_SPEED_MPS = 2.0
ERROR_KEYS = ("centre_error_m", "surface_error_m", "speed_error_mps", "velocity_error_mps", "heading_error_deg")


def _read_json(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    path = Path(path)
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def stats(values: Iterable[float]) -> Dict[str, Optional[float]]:
    data = sorted(float(v) for v in values if v is not None and not math.isnan(float(v)))
    if not data:
        return {"n": 0, "median": None, "q25": None, "q75": None, "iqr": None, "p90": None, "p95": None,
                "max": None, "mean": None, "rmse": None}

    def q(p: float) -> float:
        position = p * (len(data) - 1)
        low = int(math.floor(position))
        high = min(low + 1, len(data) - 1)
        return data[low] + (data[high] - data[low]) * (position - low)
    out = {"n": len(data), "median": q(0.5), "q25": q(0.25), "q75": q(0.75), "p90": q(0.9), "p95": q(0.95),
           "max": data[-1], "mean": sum(data) / len(data), "rmse": math.sqrt(sum(v * v for v in data) / len(data))}
    out["iqr"] = out["q75"] - out["q25"]
    return {key: (round(value, 4) if isinstance(value, float) else value) for key, value in out.items()}


def truth_of(run_dir: Path) -> Tuple[Dict[str, TruthTrack], Dict[int, str]]:
    by_participant: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    actors: Dict[int, str] = {}
    for state in _read_jsonl(Path(run_dir) / "ground_truth" / "states.jsonl"):
        by_participant[state["participant_id"]].append(state)
        actors[int(state["actor_id"])] = state["participant_id"]
    return {pid: TruthTrack(states) for pid, states in by_participant.items()}, actors


def _yaw_error(a: float, b: float) -> float:
    return abs((a - b + 180.0) % 360.0 - 180.0)


def _vehicle_frame(state: Dict[str, Any], point: Tuple[float, float]) -> Tuple[float, float]:
    yaw = math.radians(state["transform"]["yaw_deg"])
    dx, dy = point[0] - state["transform"]["x"], point[1] - state["transform"]["y"]
    return math.cos(yaw) * dx + math.sin(yaw) * dy, -math.sin(yaw) * dx + math.cos(yaw) * dy


def _corners(state: Dict[str, Any]) -> List[Tuple[float, float]]:
    transform, extent = state["transform"], state.get("bbox_extent") or {"x": 2.4, "y": 1.0}
    yaw = math.radians(transform["yaw_deg"])
    c, s = math.cos(yaw), math.sin(yaw)
    return [(transform["x"] + c * x - s * y, transform["y"] + s * x + c * y)
            for x, y in ((extent["x"], extent["y"]), (extent["x"], -extent["y"]),
                         (-extent["x"], -extent["y"]), (-extent["x"], extent["y"]))]


def true_forward_geometry(observer: Dict[str, Any], target: Dict[str, Any]) -> Dict[str, float]:
    front = (observer.get("bbox_extent") or {"x": 2.4})["x"]
    points = [_vehicle_frame(observer, corner) for corner in _corners(target)]
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    gap = max(min(ys) - CORRIDOR_HALF_WIDTH_M, -CORRIDOR_HALF_WIDTH_M - max(ys), 0.0)
    return {"clearance_m": min(xs) - front, "lateral_body_gap_m": gap,
            "bumper_gap_m": box_gap(observer, target)}


def _identity(point: Tuple[float, float], states: Dict[str, Dict[str, Any]]) -> Tuple[Optional[str], float]:
    distances = {pid: _box_distance(point, state) for pid, state in states.items()}
    if not distances:
        return None, math.inf
    best = min(distances, key=distances.get)
    return (best if distances[best] <= IDENTITY_MAX_DISTANCE_M else None), distances[best]


def audit_tracks(run_dir: Path, truth: Dict[str, TruthTrack]) -> List[Dict[str, Any]]:
    run = ReplayRun.load(run_dir)
    out = []
    for participant in run.participants:
        pid = participant.participant_id
        first = _read_jsonl(Path(run_dir) / "vehicles" / pid / "ego.jsonl")[0]
        rows_by_track: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for row in _read_jsonl(Path(run_dir) / "reconstruction" / pid / "local_tracks.jsonl"):
            rows_by_track[str(row["track_id"])].append(row)
        graph = _read_json(Path(run_dir) / "reconstruction" / pid / "local_graph.json")
        origin = float(graph["recorder"]["clock"]["origin_source_timestamp"])
        paths = {track.track_id: track for track in run.tracks.get(pid, [])}
        yaw0 = math.radians(first["yaw_deg"])
        for track_id, rows in sorted(rows_by_track.items()):
            rows.sort(key=lambda row: float(row["t_local"]))
            path = paths.get(track_id)
            identities, centre, surface, speed, velocity, heading = [], [], [], [], [], []
            for index, row in enumerate(rows):
                sim = origin + float(row["t_local"])
                states = {other: track.at(sim) for other, track in truth.items() if other != pid}
                states = {other: state for other, state in states.items() if state is not None}
                point = _to_world(first, float(row["x_m"]), float(row["y_m"]))
                who, _ = _identity(point, states)
                identities.append(who)
                if who is None:
                    continue
                state = states[who]
                surface.append(_surface_distance(point, state))
                if path is not None and index < len(path.samples):
                    sample = path.samples[index]
                    centre.append(math.hypot(sample.centre[0] - state["transform"]["x"],
                                             sample.centre[1] - state["transform"]["y"]))
                    true_speed = math.hypot(state["velocity"]["x"], state["velocity"]["y"])
                    if sample.heading == "velocity" and true_speed >= HEADING_MIN_SPEED_MPS:
                        heading.append(_yaw_error(sample.yaw, state["transform"]["yaw_deg"]))
                vx, vy = float(row.get("vx_mps") or 0.0), float(row.get("vy_mps") or 0.0)
                wvx, wvy = math.cos(yaw0) * vx - math.sin(yaw0) * vy, math.sin(yaw0) * vx + math.cos(yaw0) * vy
                speed.append(abs(math.hypot(vx, vy) - math.hypot(state["velocity"]["x"], state["velocity"]["y"])))
                velocity.append(math.hypot(wvx - state["velocity"]["x"], wvy - state["velocity"]["y"]))
            known = [who for who in identities if who is not None]
            majority, count = Counter(known).most_common(1)[0] if known else (None, 0)
            switches = sum(1 for a, b in zip(known, known[1:]) if a != b)
            out.append({"track": "{0}:{1}".format(pid, track_id), "samples": len(rows),
                        "identity": majority, "purity": round(count / len(known), 4) if known else None,
                        "identities": dict(Counter(known)), "unmatched_samples": len(identities) - len(known),
                        "identity_switches": switches,
                        "centre_error_m": stats(centre), "surface_error_m": stats(surface),
                        "speed_error_mps": stats(speed), "velocity_error_mps": stats(velocity),
                        "heading_error_deg": stats(heading),
                        "_raw": {"centre_error_m": centre, "surface_error_m": surface, "speed_error_mps": speed,
                                 "velocity_error_mps": velocity, "heading_error_deg": heading}})
    return out


def _fact_at(trace: Sequence[Dict[str, Any]], t_local: float, subject: str) -> Optional[Dict[str, Any]]:
    best = None
    for frame in trace:
        if frame["t_local"] > t_local + 1e-6:
            break
        for fact in frame["facts"]:
            if fact["type"] == "TRACK_STATE" and fact.get("subject_id") == subject:
                best = dict(fact["attributes"], t_local=frame["t_local"])
    return best


def audit_events(run_dir: Path, truth: Dict[str, TruthTrack], tracks: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    identity = {item["track"]: item["identity"] for item in tracks}
    critical, cut_ins = [], []
    for graph_path in sorted((Path(run_dir) / "reconstruction").glob("*/local_graph.json")):
        pid = graph_path.parent.name
        if pid not in truth:
            continue
        graph = _read_json(graph_path)
        origin = float(graph["recorder"]["clock"]["origin_source_timestamp"])
        trace = _read_jsonl(graph_path.parent / "local_trace.jsonl")
        for node in graph["nodes"]:
            kind, subject = node["event_type"], node.get("subject_id")
            if kind not in ("CRITICAL_TTC_START", "CUT_IN_FROM_LEFT_START", "CUT_IN_FROM_RIGHT_START") or not subject:
                continue
            who = identity.get("{0}:{1}".format(pid, subject))
            fact = _fact_at(trace, node["t_local"], subject) or {}
            observer, target = truth[pid].at(origin + node["t_local"]), truth[who].at(origin + node["t_local"]) if who in truth else None
            row = {"recorder": pid, "track": subject, "true_identity": who, "t_local": node["t_local"]}
            if observer is not None and target is not None:
                geometry = true_forward_geometry(observer, target)
                if kind == "CRITICAL_TTC_START":
                    row.update(reason=fact.get("critical_reason"),
                               clearance_m=fact.get("longitudinal_clearance_m"), true_clearance_m=round(geometry["clearance_m"], 3),
                               body_gap_m=fact.get("lateral_body_gap_m"), true_body_gap_m=round(geometry["lateral_body_gap_m"], 3),
                               true_bumper_gap_m=round(geometry["bumper_gap_m"], 3),
                               d_min_m=fact.get("required_safe_distance_m"))
                    if row["clearance_m"] is not None:
                        row["clearance_error_m"] = round(row["clearance_m"] - row["true_clearance_m"], 3)
                    critical.append(row)
                else:
                    yaw = math.radians(observer["transform"]["yaw_deg"])
                    dvx = target["velocity"]["x"] - observer["velocity"]["x"]
                    dvy = target["velocity"]["y"] - observer["velocity"]["y"]
                    true_lateral_speed = -math.sin(yaw) * dvx + math.cos(yaw) * dvy
                    row.update(direction=kind.replace("_START", ""), body_gap_m=fact.get("lateral_body_gap_m"),
                               true_body_gap_m=round(geometry["lateral_body_gap_m"], 3),
                               lateral_speed_mps=fact.get("relative_lateral_speed_mps"),
                               true_lateral_speed_mps=round(true_lateral_speed, 3))
                    cut_ins.append(row)
            else:
                (critical if kind == "CRITICAL_TTC_START" else cut_ins).append(row)
    return {"critical_ttc_starts": critical, "cut_in_starts": cut_ins}


def gt_audit_run(run_dir: Path) -> Dict[str, Any]:
    run_dir = Path(run_dir)
    truth, _ = truth_of(run_dir)
    tracks = audit_tracks(run_dir, truth)
    events = audit_events(run_dir, truth, tracks)
    evaluation = _read_json(run_dir / "reconstruction" / "evaluation" / "evaluation.json")
    raw = {key: [v for item in tracks for v in item["_raw"][key]] for key in ERROR_KEYS}
    anonymous = {item["track"] for item in evaluation.get("tracks", []) if item.get("status") == "ANONYMOUS"}
    raw_anonymous = {key: [v for item in tracks if item["track"] in anonymous for v in item["_raw"][key]]
                     for key in ERROR_KEYS}
    for item in tracks:
        item.pop("_raw")
    return {"run": "{0}/{1}".format(run_dir.parent.name, run_dir.name),
            "privileged": "ground truth used for evaluation only",
            "collisions": evaluation.get("collisions"), "extra_collisions": evaluation.get("extra_collisions"),
            "event_timing": evaluation.get("event_timing"), "associations": evaluation.get("tracks"),
            "tracks": tracks, "pooled_track_errors": {key: stats(values) for key, values in raw.items()},
            "pooled_anonymous_track_errors": {key: stats(values) for key, values in raw_anonymous.items()},
            "_raw": raw, "_raw_anonymous": raw_anonymous, **events}
