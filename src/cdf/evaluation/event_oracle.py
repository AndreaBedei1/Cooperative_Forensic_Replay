
from __future__ import annotations

import dataclasses
import json
import math
import statistics
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np

from ..reconstruction.config import ReconstructionConfig, SemanticsConfig
from ..reconstruction.local import read_jsonl, track_events, vehicle_metadata
from ..reconstruction.pipeline import read_incident_context
from ..reconstruction.road import RoadFrame
from ..reconstruction.tracking import EgoFootprint, EgoTrajectory, LocalTrack, TrackSample, ego_trajectory
from .visibility import Box, coverage, frames_by_participant, radar_views

CORE_TYPES = ("TRACK_APPEARED", "EGO_PATH_ENTRY", "CUT_IN_FROM_LEFT_START", "CUT_IN_FROM_RIGHT_START",
              "CRITICAL_TTC_START", "CRITICAL_TTC_END")
ORACLES = ("PERFECT", "COVERAGE", "COVERAGE_TRACKED")
COMPARISONS = (("RECONSTRUCTION", "COVERAGE"), ("RECONSTRUCTION", "COVERAGE_TRACKED"), ("RECONSTRUCTION", "PERFECT"),
               ("COVERAGE_TRACKED", "COVERAGE"), ("COVERAGE", "PERFECT"))
MATCH_WINDOW_S = 2.0
IDEAL_STD = 0.05
OUTLINE_STEP_M = 0.05
CONTACT_GAP_S = 0.5


def _type(event_type: str) -> Optional[str]:
    if event_type.startswith("TRACK_APPEARED_"):
        return "TRACK_APPEARED"
    return event_type if event_type in CORE_TYPES else None


def _outline(centre: np.ndarray, heading: float, half: Tuple[float, float]) -> Tuple[np.ndarray, np.ndarray]:
    hx, hy = half
    xs = np.arange(-hx, hx + 1e-9, OUTLINE_STEP_M)
    ys = np.arange(-hy, hy + 1e-9, OUTLINE_STEP_M)
    local = np.vstack([np.column_stack([xs, np.full(len(xs), -hy)]), np.column_stack([xs, np.full(len(xs), hy)]),
                       np.column_stack([np.full(len(ys), -hx), ys]), np.column_stack([np.full(len(ys), hx), ys])])
    normals = np.vstack([np.tile([0.0, -1.0], (len(xs), 1)), np.tile([0.0, 1.0], (len(xs), 1)),
                         np.tile([-1.0, 0.0], (len(ys), 1)), np.tile([1.0, 0.0], (len(ys), 1))])
    c, s = math.cos(heading), math.sin(heading)

    def rotate(v: np.ndarray) -> np.ndarray:
        return np.column_stack([c * v[:, 0] - s * v[:, 1], s * v[:, 0] + c * v[:, 1]])

    return centre + rotate(local), rotate(normals)


def _rect_distance(points: np.ndarray, fp: EgoFootprint) -> np.ndarray:
    dx = np.maximum(np.maximum(fp.x_min - points[:, 0], 0.0), points[:, 0] - fp.x_max)
    dy = np.maximum(np.maximum(fp.y_min - points[:, 1], 0.0), points[:, 1] - fp.y_max)
    return np.hypot(dx, dy)


@dataclasses.dataclass
class RecorderTruth:

    owner: str
    clock_origin: float
    origin: Tuple[float, float, float]
    ego: EgoTrajectory
    footprint: EgoFootprint
    radars: List[Any]
    sweeps: List[Tuple[int, float]]
    road: Optional[Any] = None


def recorder_truth(run_dir: Path, owner: str, frames: Mapping[int, Mapping[str, Any]]) -> Optional[RecorderTruth]:
    vehicle_dir = Path(run_dir) / "vehicles" / owner
    if not (vehicle_dir / "radar").exists():
        return None
    ego_records = read_jsonl(vehicle_dir / "ego.jsonl")
    clock_origin = float(ego_records[0]["timestamp"])
    first = ego_records[0]
    footprint = EgoFootprint.from_metadata(vehicle_metadata(vehicle_dir).get("ego_footprint")) \
        or EgoFootprint(-2.3, 2.3, -0.95, 0.95)
    views = radar_views(vehicle_dir)
    sweep_frames: Dict[int, float] = {}
    for _, obs in views:
        for frame, timestamp in zip(obs.frames, obs.timestamps):
            sweep_frames.setdefault(int(frame), float(timestamp))
    sweeps = [(frame, round(t - clock_origin, 4)) for frame, t in sorted(sweep_frames.items()) if frame in frames]
    return RecorderTruth(owner, clock_origin, (float(first["x"]), float(first["y"]), math.radians(float(first["yaw_deg"]))),
                         ego_trajectory(ego_records, clock_origin), footprint, [view for view, _ in views], sweeps,
                         RoadFrame.from_ego_records(ego_records, map_name=read_incident_context(run_dir).get("map")))


def _to_local(rec: RecorderTruth, x: float, y: float) -> np.ndarray:
    x0, y0, yaw0 = rec.origin
    c0, s0 = math.cos(yaw0), math.sin(yaw0)
    dx, dy = x - x0, y - y0
    return np.array([c0 * dx + s0 * dy, -s0 * dx + c0 * dy])


def _vector_local(rec: RecorderTruth, vx: float, vy: float) -> np.ndarray:
    c0, s0 = math.cos(rec.origin[2]), math.sin(rec.origin[2])
    return np.array([c0 * vx + s0 * vy, -s0 * vx + c0 * vy])


def ideal_samples(rec: RecorderTruth, target: str, frames: Mapping[int, Mapping[str, Any]],
                  tracked: bool = False) -> List[TrackSample]:
    rows = []
    for frame, t in rec.sweeps:
        state = frames[frame].get(target)
        if state is None or t < rec.ego.start - 1e-6 or t > rec.ego.end + 1e-6:
            continue
        own = rec.ego.at(t)
        tf, ext, vel = state["transform"], state["bbox_extent"], state["velocity"]
        centre = _to_local(rec, tf["x"], tf["y"])
        heading = math.radians(tf["yaw_deg"]) - rec.origin[2]
        outline, normals = _outline(centre, heading, (ext["x"], ext["y"]))
        c, s = math.cos(own.heading), math.sin(own.heading)
        rel = outline - np.array([own.x, own.y])
        vehicle = np.column_stack([c * rel[:, 0] + s * rel[:, 1], -s * rel[:, 0] + c * rel[:, 1]])
        distance = _rect_distance(vehicle, rec.footprint)
        nearest = int(np.argmin(distance))
        near_v, near_l = vehicle[nearest], outline[nearest]
        depth = 0.0
        if tracked:
            facing_normals = np.column_stack([c * normals[:, 0] + s * normals[:, 1], -s * normals[:, 0] + c * normals[:, 1]])
            facing = np.zeros(len(vehicle), dtype=bool)
            for view in rec.radars or []:
                facing |= np.sum((vehicle - view.position[:2]) * facing_normals, axis=1) < 0.0
            if facing.any():
                point_v = np.median(vehicle[facing], axis=0)
                depth = max(0.0, float(_rect_distance(point_v[None], rec.footprint)[0]) - float(distance[nearest]))
                near_v = point_v
                near_l = np.array([own.x, own.y]) + np.array([c * point_v[0] - s * point_v[1], s * point_v[0] + c * point_v[1]])
        velocity = _vector_local(rec, vel["x"], vel["y"])
        speed = float(np.hypot(*velocity))
        acc = state.get("acceleration") or {}
        acceleration = 0.0
        if speed > 0.5:
            a_world = np.array([acc.get("x", 0.0), acc.get("y", 0.0)])
            v_world = np.array([vel["x"], vel["y"]])
            acceleration = float(a_world @ v_world / max(float(np.hypot(*v_world)), 1e-9))
        relative = velocity - np.array([own.vx, own.vy])
        mounts = [view.position[:2] for view in rec.radars] or [np.zeros(2)]
        rows.append({"t": t, "near_l": near_l, "near_v": near_v, "clearance": float(distance[nearest]), "depth": depth,
                     "velocity": velocity, "speed": speed, "acceleration": acceleration,
                     "relative": np.array([c * relative[0] + s * relative[1], -s * relative[0] + c * relative[1]]),
                     "range": float(min(np.hypot(*(near_v - m)) for m in mounts)),
                     "dims": (2.0 * ext["x"], 2.0 * ext["y"]),
                     "body": (float(centre[0]), float(centre[1]), heading, 2.0 * ext['x'], 2.0 * ext['y'])})
    samples = []
    for i, row in enumerate(rows):
        before, after = rows[max(i - 1, 0)], rows[min(i + 1, len(rows) - 1)]
        dt = after["t"] - before["t"]
        closing = -(after["clearance"] - before["clearance"]) / dt if dt > 1e-6 else 0.0
        ttc = row["clearance"] / closing if closing > 1e-3 else None
        near_v, near_l = row["near_v"], row["near_l"]
        samples.append(TrackSample(
            t_local=row["t"], x_m=float(near_l[0]), y_m=float(near_l[1]), vx_mps=float(row["velocity"][0]),
            vy_mps=float(row["velocity"][1]), speed_mps=row["speed"], pos_std_m=IDEAL_STD, vel_std_mps=IDEAL_STD,
            range_m=row["range"], bearing_deg=math.degrees(math.atan2(near_v[1], near_v[0])),
            longitudinal_m=float(near_v[0]), lateral_m=float(near_v[1]), closing_speed_mps=closing,
            closing_ttc_s=None if ttc is None else round(ttc, 3), measured=True, n_returns=10,
            meas_x_m=float(near_l[0]), meas_y_m=float(near_l[1]), clearance_m=row["clearance"],
            ahead_m=float(near_v[0]) - rec.footprint.x_max, surface_offset_m=row["depth"],
            acceleration_mps2=row["acceleration"],
            body_estimate=row['body'],
            relative_vx_mps=float(row["relative"][0]), relative_vy_mps=float(row["relative"][1])))
    return samples


def _contacts(rec: RecorderTruth, target_actors: set, collisions: Sequence[Mapping[str, Any]]) -> List[Tuple[float, float]]:
    times = sorted(float(row["timestamp"]) - rec.clock_origin for row in collisions
                   if row["participant_id"] == rec.owner and row["other_actor_id"] in target_actors)
    out: List[List[float]] = []
    for t in times:
        if out and t - out[-1][1] <= CONTACT_GAP_S:
            out[-1][1] = t
        else:
            out.append([t, t])
    return [(round(a, 4), round(b, 4)) for a, b in out]


def _events(rec: RecorderTruth, target: str, samples: Sequence[TrackSample], semantics: SemanticsConfig,
            contacts: Sequence[Tuple[float, float]], track_id: str,
            impact_from: Optional[float] = None) -> List[Dict[str, Any]]:
    if len(samples) < 2:
        return []
    track = LocalTrack(track_id=track_id, samples=list(samples))
    out = []
    for event in track_events(rec.owner, track, rec.ego.end, semantics, rec.ego, None, rec.footprint, contacts,
                              road=rec.road, impact_from=impact_from):
        family = _type(event.type)
        if family is not None:
            out.append({"type": family, "side": event.type, "subject": target, "t_local": round(event.t_local, 4),
                        "track": track_id})
    return out


def _pieces(samples: Sequence[TrackSample], visible: Sequence[bool], gap_s: float, min_frames: int) -> List[List[TrackSample]]:
    pieces: List[List[TrackSample]] = []
    current: List[TrackSample] = []
    for sample, seen in zip(samples, visible):
        if not seen:
            continue
        if current and sample.t_local - current[-1].t_local > gap_s + 1e-6:
            pieces.append(current)
            current = []
        current.append(sample)
    if current:
        pieces.append(current)
    return [piece for piece in pieces if len(piece) >= min_frames]


def oracle_events(run_dir: Path, cfg: ReconstructionConfig,
                  truth: Optional[Dict[str, Any]] = None) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    truth = truth or prepare_truth(run_dir, cfg)
    out: Dict[str, Dict[str, List[Dict[str, Any]]]] = {name: {} for name in ORACLES}
    for owner, per_target in truth["ideal"].items():
        rec = truth["recorders"][owner]
        for name in ORACLES:
            out[name].setdefault(owner, [])
        for target, item in per_target.items():
            semantics = dataclasses.replace(cfg.semantics, target_length_m=item["dims"][0], target_width_m=item["dims"][1])
            impact = truth["first_contact"].get(owner)
            perfect = [e for e in _events(rec, target, item["samples"], semantics, item["contacts"], target + "#all",
                                          impact) if e["type"] != "TRACK_APPEARED"]
            out["PERFECT"][owner] += perfect
            for name, samples in (("COVERAGE", item["samples"]), ("COVERAGE_TRACKED", item["tracked"])):
                for n, piece in enumerate(_pieces(samples, item["visible"], cfg.tracking.max_track_gap_s,
                                                  cfg.tracking.min_track_frames), 1):
                    out[name][owner] += _events(rec, target, piece, semantics, item["contacts"],
                                                "{0}#{1}".format(target, n), impact)
    return out


def prepare_truth(run_dir: Path, cfg: ReconstructionConfig) -> Dict[str, Any]:
    run_dir = Path(run_dir)
    states = read_jsonl(run_dir / "ground_truth" / "states.jsonl")
    collisions = read_jsonl(run_dir / "ground_truth" / "collisions.jsonl")
    frames = frames_by_participant(states)
    actors: Dict[str, set] = {}
    for state in states:
        actors.setdefault(state["participant_id"], set()).add(state["actor_id"])
    participants = sorted(actors)
    recorders: Dict[str, RecorderTruth] = {}
    ideal: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for owner in sorted(p.name for p in (run_dir / "vehicles").iterdir() if (p / "ego.jsonl").exists()):
        rec = recorder_truth(run_dir, owner, frames)
        if rec is None:
            continue
        recorders[owner] = rec
        ideal[owner] = {}
        for target in participants:
            if target == owner:
                continue
            samples = ideal_samples(rec, target, frames)
            if not samples:
                continue
            by_t = {round(t, 4): frame for frame, t in rec.sweeps}
            visible = []
            for sample in samples:
                world = frames[by_t[round(sample.t_local, 4)]]
                own = world.get(owner)
                visible.append(own is not None and coverage(own, target, world, rec.radars,
                                                            {pid: Box(s) for pid, s in world.items()}).visible)
            dims = None
            for frame, _ in rec.sweeps:
                if target in frames[frame]:
                    e = frames[frame][target]["bbox_extent"]
                    dims = (2.0 * e["x"], 2.0 * e["y"])
                    break
            tracked = ideal_samples(rec, target, frames, tracked=True)
            ideal[owner][target] = {"samples": samples, "tracked": tracked, "visible": visible, "dims": dims,
                                    "contacts": _contacts(rec, actors[target], collisions)}
    first_contact = {}
    for owner, rec in recorders.items():
        times = [float(row["timestamp"]) - rec.clock_origin for row in collisions if row["participant_id"] == owner]
        if times:
            first_contact[owner] = round(min(times), 4)
    return {"recorders": recorders, "ideal": ideal, "first_contact": first_contact}


def reconstruction_events(run_dir: Path) -> Dict[str, List[Dict[str, Any]]]:
    run_dir = Path(run_dir)
    evaluation = json.loads((run_dir / "reconstruction" / "evaluation" / "evaluation.json").read_text(encoding="utf-8"))
    identity = {row["track"]: row.get("true_identity") for row in evaluation["tracks"]}
    out: Dict[str, List[Dict[str, Any]]] = {}
    for graph_path in sorted((run_dir / "reconstruction").glob("*/local_graph.json")):
        graph = json.loads(graph_path.read_text(encoding="utf-8"))
        owner = graph["owner"]
        out[owner] = []
        for node in graph["nodes"]:
            family = _type(node["event_type"])
            if family is None or not node.get("subject_id"):
                continue
            track = "{0}:{1}".format(owner, node["subject_id"])
            out[owner].append({"type": family, "side": node["event_type"], "subject": identity.get(track),
                               "t_local": round(float(node["t_local"]), 4), "track": node["subject_id"]})
    return out


def match(found: Sequence[Mapping[str, Any]], expected: Sequence[Mapping[str, Any]],
          window_s: float = MATCH_WINDOW_S) -> Tuple[List[Tuple[int, int]], List[int], List[int]]:
    candidates = sorted((abs(f["t_local"] - e["t_local"]), i, j) for i, f in enumerate(found)
                        for j, e in enumerate(expected)
                        if f["type"] == e["type"] and f["subject"] == e["subject"] and f["subject"] is not None
                        and abs(f["t_local"] - e["t_local"]) <= window_s)
    used_f, used_e, pairs = set(), set(), []
    for _, i, j in candidates:
        if i in used_f or j in used_e:
            continue
        used_f.add(i)
        used_e.add(j)
        pairs.append((i, j))
    return pairs, [i for i in range(len(found)) if i not in used_f], [j for j in range(len(expected)) if j not in used_e]


def compare(sets: Mapping[str, Mapping[str, Sequence[Mapping[str, Any]]]]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for found_name, expected_name in COMPARISONS:
        rows: Dict[str, Dict[str, Any]] = {t: {"found": 0, "expected": 0, "matched": 0, "deltas": [], "side_agree": 0,
                                                "missed": [], "extra": []} for t in CORE_TYPES}
        for owner in sorted(set(sets[found_name]) | set(sets[expected_name])):
            found, expected = list(sets[found_name].get(owner, [])), list(sets[expected_name].get(owner, []))
            if expected_name == "PERFECT":
                found = [e for e in found if e["type"] != "TRACK_APPEARED"]
            pairs, extra, missed = match(found, expected)
            for event in found:
                rows[event["type"]]["found"] += 1
            for event in expected:
                rows[event["type"]]["expected"] += 1
            for i, j in pairs:
                row = rows[found[i]["type"]]
                row["matched"] += 1
                row["deltas"].append(round(found[i]["t_local"] - expected[j]["t_local"], 4))
                row["side_agree"] += found[i]["side"] == expected[j]["side"]
            for j in missed:
                rows[expected[j]["type"]]["missed"].append("{0}/{1}@{2:.2f}".format(owner, expected[j]["subject"],
                                                                                   expected[j]["t_local"]))
            for i in extra:
                rows[found[i]["type"]]["extra"].append("{0}/{1}@{2:.2f}".format(owner, found[i]["subject"],
                                                                               found[i]["t_local"]))
        out["{0} vs {1}".format(found_name, expected_name)] = rows
    return out


def compare_run(run_dir: Path, cfg: ReconstructionConfig, truth: Optional[Dict[str, Any]] = None,
                reconstructed: Optional[Dict[str, List[Dict[str, Any]]]] = None) -> Dict[str, Any]:
    truth = truth or prepare_truth(run_dir, cfg)
    oracles = oracle_events(run_dir, cfg, truth)
    sets = dict(oracles, RECONSTRUCTION=reconstructed if reconstructed is not None else reconstruction_events(run_dir))
    first_sweep = {owner: rec.sweeps[0][1] if rec.sweeps else 0.0 for owner, rec in truth["recorders"].items()}
    sets = {name: {owner: [e for e in events if not (e["type"] == "TRACK_APPEARED"
                                                    and e["t_local"] <= first_sweep.get(owner, 0.0) + 0.1)]
                   for owner, events in per_owner.items()} for name, per_owner in sets.items()}
    contact = truth["first_contact"]
    pre = {name: {owner: [e for e in events if e["t_local"] < contact.get(owner, math.inf)]
                  for owner, events in per_owner.items()} for name, per_owner in sets.items()}
    return {"run": "{0}/{1}".format(Path(run_dir).parent.name, Path(run_dir).name), "events": sets,
            "first_contact_t_local": contact, "comparison": compare(sets), "comparison_pre_contact": compare(pre)}


def pooled(results: Sequence[Mapping[str, Any]], window: str = "comparison") -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for found_name, expected_name in COMPARISONS:
        key = "{0} vs {1}".format(found_name, expected_name)
        out[key] = {}
        for event_type in CORE_TYPES:
            if expected_name == "PERFECT" and event_type == "TRACK_APPEARED":
                continue
            rows = [r[window][key][event_type] for r in results]
            found = sum(r["found"] for r in rows)
            expected = sum(r["expected"] for r in rows)
            matched = sum(r["matched"] for r in rows)
            deltas = sorted(d for r in rows for d in r["deltas"])
            out[key][event_type] = {
                "found": found, "expected": expected, "matched": matched,
                "precision": None if not found else round(matched / found, 4),
                "recall": None if not expected else round(matched / expected, 4),
                "delta_median_s": round(statistics.median(deltas), 3) if deltas else None,
                "delta_p05_s": round(float(np.percentile(deltas, 5)), 3) if deltas else None,
                "delta_p95_s": round(float(np.percentile(deltas, 95)), 3) if deltas else None,
                "abs_delta_median_s": round(statistics.median(abs(d) for d in deltas), 3) if deltas else None,
                "side_agreement": (round(sum(r["side_agree"] for r in rows) / matched, 4)
                                   if matched and event_type == "TRACK_APPEARED" else None)}
    return out
