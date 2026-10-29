#!/usr/bin/env python3
"""Paired audit of historical and reacquired CARLA runs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.check_scenario_run import box_gap  # noqa: E402
from scripts.validate_canonical import CANONICAL  # noqa: E402


def rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _error_stats(prefix: str, values: np.ndarray, unit: str) -> dict:
    return {
        f"{prefix}_p50_{unit}": float(np.percentile(values, 50)),
        f"{prefix}_p95_{unit}": float(np.percentile(values, 95)),
        f"{prefix}_p99_{unit}": float(np.percentile(values, 99)),
        f"{prefix}_p995_{unit}": float(np.percentile(values, 99.5)),
        f"{prefix}_max_{unit}": float(np.max(values)),
        f"{prefix}_rms_{unit}": float(np.sqrt(np.mean(values * values))),
    }


def trajectory_metrics(old_rows: list[dict], old_t0: float,
                       new_rows: list[dict], new_t0: float, dt_s: float = 0.05) -> dict:
    """Compare one participant on relative scenario time; expose spawn offset separately from motion."""
    if not old_rows or not new_rows:
        return {"common_samples": 0, "common_duration_s": 0.0}

    def series(records: list[dict], t0: float) -> tuple[np.ndarray, dict[str, np.ndarray]]:
        records = sorted(records, key=lambda item: item["timestamp"])
        t = np.asarray([item["timestamp"] - t0 for item in records], dtype=np.float64)
        values = {
            "x": np.asarray([item["transform"]["x"] for item in records], dtype=np.float64),
            "y": np.asarray([item["transform"]["y"] for item in records], dtype=np.float64),
            "vx": np.asarray([item["velocity"]["x"] for item in records], dtype=np.float64),
            "vy": np.asarray([item["velocity"]["y"] for item in records], dtype=np.float64),
            "yaw": np.unwrap(np.deg2rad([item["transform"]["yaw_deg"] for item in records])),
        }
        return t, values

    old_t, old = series(old_rows, old_t0)
    new_t, new = series(new_rows, new_t0)
    lo, hi = max(old_t[0], new_t[0]), min(old_t[-1], new_t[-1])
    if hi < lo:
        return {"common_samples": 0, "common_duration_s": 0.0}
    grid = np.arange(lo, hi + dt_s * 0.25, dt_s, dtype=np.float64)
    grid = grid[grid <= hi + 1e-9]
    sampled = {
        side: {key: np.interp(grid, t, values[key]) for key in values}
        for side, (t, values) in (("old", (old_t, old)), ("new", (new_t, new)))
    }
    old_s, new_s = sampled["old"], sampled["new"]
    world_position = np.hypot(new_s["x"] - old_s["x"], new_s["y"] - old_s["y"])
    old_displacement = np.column_stack((old_s["x"] - old_s["x"][0], old_s["y"] - old_s["y"][0]))
    new_displacement = np.column_stack((new_s["x"] - new_s["x"][0], new_s["y"] - new_s["y"][0]))
    motion_position = np.linalg.norm(new_displacement - old_displacement, axis=1)
    velocity = np.hypot(new_s["vx"] - old_s["vx"], new_s["vy"] - old_s["vy"])
    speed = np.abs(np.hypot(new_s["vx"], new_s["vy"]) - np.hypot(old_s["vx"], old_s["vy"]))
    yaw_delta = np.rad2deg(new_s["yaw"] - old_s["yaw"])
    heading = np.abs((yaw_delta + 180.0) % 360.0 - 180.0)
    result = {"common_samples": int(len(grid)), "common_duration_s": float(hi - lo), "grid_dt_s": float(dt_s)}
    result.update(_error_stats("position_world", world_position, "m"))
    result.update(_error_stats("position_from_start", motion_position, "m"))
    result.update(_error_stats("velocity_2d", velocity, "mps"))
    result.update(_error_stats("speed_2d", speed, "mps"))
    result.update(_error_stats("heading_abs", heading, "deg"))
    return result


def collision_events(records: list[dict], actor_to_participant: dict[int, str], t0: float) -> list[dict]:
    """Normalize simulator IDs and collapse reciprocal callbacks from the same physics frame."""
    grouped: dict[tuple[str, object], dict] = {}
    for item in records:
        a = item.get("participant_id") or actor_to_participant.get(item.get("actor_id"))
        other = item.get("other_participant_id") or actor_to_participant.get(item.get("other_actor_id"))
        if other is None:
            other = item.get("other_type_id") or "actor:{0}".format(item.get("other_actor_id", "unknown"))
        pair = "-".join(sorted((str(a or "unknown"), str(other))))
        relative_time = round(float(item["timestamp"] - t0), 6)
        frame = item.get("frame")
        key = (pair, frame if frame is not None else round(float(item["timestamp"]), 6))
        event = grouped.setdefault(key, {
            "pair": pair, "t_rel_s": relative_time,
            "frame": frame, "callback_count": 0, "impulse_sum": 0.0,
        })
        event["callback_count"] += 1
        event["impulse_sum"] += float(item.get("impulse", 0.0))
        event["t_rel_s"] = min(event["t_rel_s"], relative_time)
    return sorted(grouped.values(), key=lambda event: (event["t_rel_s"], event["pair"]))


def collision_episodes(events: list[dict], dt_s: float = 0.05) -> list[dict]:
    """Group callbacks into one contact episode across gaps of at most two ticks."""
    by_pair: dict[str, list[dict]] = defaultdict(list)
    for event in events:
        by_pair[str(event["pair"])].append(event)
    episodes = []
    max_gap_s = dt_s * 2.5
    for pair, pair_events in sorted(by_pair.items()):
        groups: list[list[dict]] = []
        for event in sorted(pair_events, key=lambda item: item["t_rel_s"]):
            if not groups or event["t_rel_s"] - groups[-1][-1]["t_rel_s"] > max_gap_s:
                groups.append([event])
            else:
                groups[-1].append(event)
        for group in groups:
            impulses = [float(event.get("impulse_sum", 0.0)) for event in group]
            episodes.append({
                "pair": pair,
                "start_t_rel_s": float(group[0]["t_rel_s"]),
                "end_t_rel_s": float(group[-1]["t_rel_s"]),
                "contact_ticks": len(group),
                "impulse_sum": float(sum(impulses)),
                "peak_tick_impulse": float(max(impulses)),
            })
    return sorted(episodes, key=lambda event: (event["start_t_rel_s"], event["pair"]))


def _load_run(run: Path) -> dict:
    metadata = json.loads((run / "metadata.json").read_text(encoding="utf-8"))
    truth_metadata = json.loads((run / "ground_truth" / "metadata.json").read_text(encoding="utf-8"))
    states = rows(run / "ground_truth" / "states.jsonl")
    if not states:
        raise ValueError("no ground-truth states in {0}".format(run))
    t0 = float(metadata.get("simulation_start_timestamp", min(s["timestamp"] for s in states)))
    actors = {int(s["actor_id"]): str(s["participant_id"]) for s in states}
    grouped_states: dict[str, list[dict]] = defaultdict(list)
    for state in states:
        grouped_states[str(state["participant_id"])].append(state)
    recorders = sorted(p.name for p in (run / "vehicles").iterdir() if p.is_dir())
    participants = truth_metadata.get("participants", [])
    if participants:
        participant_roles = {
            str(p["participant_id"]): bool(p.get("record", False)) if isinstance(p, dict) else str(p) in recorders
            for p in participants
        }
    else:
        # Older recordings list only recorders in metadata; ground truth still has every physical participant.
        participant_roles = {pid: pid in recorders for pid in grouped_states}
    return {
        "path": run, "metadata": metadata, "truth_metadata": truth_metadata,
        "states": states, "states_by_participant": grouped_states,
        "controls": rows(run / "ground_truth" / "controls.jsonl"),
        "t0": t0, "actors": actors, "recorders": recorders,
        "participant_roles": participant_roles,
        "collisions": collision_events(rows(run / "ground_truth" / "collisions.jsonl"), actors, t0),
        "triggers": rows(run / "ground_truth" / "triggers.jsonl"),
    }


_DYNAMIC_SENSOR_KEYS = {
    "callbacks_received", "frames_delivered", "frames_without_measurement", "frames_written",
    "missing_frame_count", "queue_drops", "duplicate_callbacks", "returns_beyond_range_dropped",
    "first_frame", "last_frame", "pre_timeline_callbacks", "candidate_sign_detections", "candidate_stop_detections",
    "candidate_yield_detections", "confirmed_sign_tracks", "confirmed_stop_tracks",
    "confirmed_yield_tracks", "rejected_short_tracks", "radial_velocity",
}


def _sensor_inventory(run: Path, duration_s: float) -> dict[str, dict]:
    out = {}
    for rec in sorted((run / "vehicles").glob("*")):
        if not rec.is_dir():
            continue
        paths = [("rgb", rec / "camera" / "metadata.json"), ("depth", rec / "depth" / "metadata.json")]
        paths.extend(("radar", p) for p in sorted((rec / "radar").glob("*/metadata.json")))
        for kind, meta_path in paths:
            if not meta_path.exists():
                continue
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            npz_path = meta_path.parent / "observations.npz"
            frames = np.asarray([], dtype=np.int64)
            timestamps = np.asarray([], dtype=np.float64)
            if npz_path.exists():
                with np.load(npz_path, allow_pickle=False) as data:
                    frames = data["frames"] if "frames" in data else frames
                    timestamps = data["timestamps"] if "timestamps" in data else timestamps
            tick = float(meta.get("sensor_tick_s", 0.0) or 0.0)
            delta = np.diff(timestamps) if len(timestamps) > 1 else np.asarray([], dtype=np.float64)
            sensor_id = meta.get("sensor_id", meta_path.parent.name)
            key = "{0}/{1}/{2}".format(rec.name, "radar" if kind == "radar" else kind, sensor_id)
            dynamic = {k: v for k, v in meta.items() if k in _DYNAMIC_SENSOR_KEYS}
            out[key] = {
                "recorder": rec.name, "kind": kind, "sensor_id": sensor_id,
                "sensor_tick_s": tick, "expected_hz": (1.0 / tick if tick else None),
                "duration_s": duration_s,
                "expected_frames_approx": (duration_s / tick if tick else None),
                "frames": int(len(frames) if npz_path.exists() else meta.get("frames_written", 0)),
                "frames_written": int(meta.get("frames_written", 0)),
                "callbacks_received": int(meta.get("callbacks_received", 0)),
                "queue_drops": int(meta.get("queue_drops", 0)),
                "missing_frame_count": int(meta.get("missing_frame_count", 0)),
                "frames_without_measurement": int(meta.get("frames_without_measurement", 0)),
                "duplicate_callbacks": int(meta.get("duplicate_callbacks", 0)),
                "median_interval_s": float(np.median(delta)) if len(delta) else None,
                "measured_hz": (float(1.0 / np.median(delta)) if len(delta) and np.median(delta) > 0 else None),
                "timestamp_gaps_over_1_5_ticks": int(np.sum(delta > tick * 1.5)) if len(delta) and tick else 0,
                "timestamps_monotonic": bool(np.all(delta > 0)) if len(delta) else None,
                "static_config": {k: v for k, v in meta.items() if k not in _DYNAMIC_SENSOR_KEYS},
                "runtime_counts": dynamic,
                "complete": not any(int(meta.get(k, 0) or 0) > 0 for k in (
                    "queue_drops", "missing_frame_count", "frames_without_measurement")),
            }
    return out


def _control_summary(records: list[dict], t0: float) -> dict:
    if not records:
        return {"samples": 0}
    ordered = sorted(records, key=lambda item: item["timestamp"])
    brakes = [float(r.get("brake", 0.0)) for r in ordered]
    positive = [r for r in ordered if float(r.get("brake", 0.0)) > 0.0]
    return {
        "samples": len(ordered), "brake_samples": len(positive),
        "brake_duration_approx_s": len(positive) * 0.05,
        "brake_first_t_rel_s": (float(positive[0]["timestamp"] - t0) if positive else None),
        "brake_last_t_rel_s": (float(positive[-1]["timestamp"] - t0) if positive else None),
        "max_brake": max(brakes),
        "max_throttle": max(float(r.get("throttle", 0.0)) for r in ordered),
        "max_abs_steer": max(abs(float(r.get("steer", 0.0))) for r in ordered),
    }


def _acceleration_summary(records: list[dict]) -> dict:
    if not records:
        return {"samples": 0}
    planar = []
    longitudinal = []
    for row in records:
        a, v = row["acceleration"], row["velocity"]
        ax, ay = float(a["x"]), float(a["y"])
        vx, vy = float(v["x"]), float(v["y"])
        planar.append(math.hypot(ax, ay))
        speed = math.hypot(vx, vy)
        if speed > 1e-6:
            longitudinal.append((ax * vx + ay * vy) / speed)
    return {
        "samples": len(records), "max_planar_acceleration_mps2": max(planar),
        "p95_planar_acceleration_mps2": float(np.percentile(planar, 95)),
        "min_longitudinal_acceleration_mps2": min(longitudinal) if longitudinal else None,
        "max_longitudinal_acceleration_mps2": max(longitudinal) if longitudinal else None,
    }


def _minimum_gaps(states: list[dict], t0: float) -> dict:
    frames: dict[int, dict[str, dict]] = defaultdict(dict)
    for state in states:
        frames[int(state["frame"])][str(state["participant_id"])] = state
    best = {}
    for frame in sorted(frames):
        present = frames[frame]
        timestamp = next(iter(present.values()))["timestamp"]
        for a, b in combinations(sorted(present), 2):
            pair = "-".join((a, b))
            sa, sb = present[a], present[b]
            ta, tb = sa["transform"], sb["transform"]
            centre = math.hypot(ta["x"] - tb["x"], ta["y"] - tb["y"])
            gap = box_gap(sa, sb)
            if pair not in best or gap < best[pair]["box_gap_m"]:
                best[pair] = {"box_gap_m": float(gap), "centre_distance_m": centre,
                              "t_rel_s": float(timestamp - t0), "frame_offset": frame - min(frames)}
    return best


def _events_for_pair(info: dict) -> tuple[list[dict], list[dict]]:
    triggers = sorted(info["triggers"], key=lambda item: item.get("timestamp", 0.0))
    normalized = [{"participant": item.get("participant_id"), "action_id": item.get("action_id"),
                   "t_rel_s": float(item["timestamp"] - info["t0"])} for item in triggers]
    return info["collisions"], normalized


def _static_sensor_equal(old: dict, new: dict) -> bool:
    return old.get("static_config") == new.get("static_config")


def _incomplete_sensor_ids(sensor_rows: list[dict], dataset: str = "new", required_only: bool = False) -> list[str]:
    present_key, complete_key = dataset + "_present", dataset + "_complete"
    return [row["sensor"] for row in sensor_rows
            if (not required_only or row.get("kind") in ("radar", "rgb"))
            and (not row.get(present_key, False) or row.get(complete_key) is False)]


def _sensor_quality(sensor_rows: list[dict]) -> dict:
    old_incomplete = _incomplete_sensor_ids(sensor_rows, "old")
    new_incomplete = _incomplete_sensor_ids(sensor_rows, "new")
    old_required = _incomplete_sensor_ids(sensor_rows, "old", required_only=True)
    new_required = _incomplete_sensor_ids(sensor_rows, "new", required_only=True)
    required_incomplete = sorted(set(old_required + new_required))
    old_depth = [row["sensor"] for row in sensor_rows if row.get("kind") == "depth"
                 and (not row.get("old_present", False) or row.get("old_complete") is False)]
    new_depth = [row["sensor"] for row in sensor_rows if row.get("kind") == "depth"
                 and (not row.get("new_present", False) or row.get("new_complete") is False)]
    return {
        "required_incomplete_sensors": required_incomplete,
        "old_incomplete_sensors": old_incomplete,
        "new_incomplete_sensors": new_incomplete,
        "old_required_incomplete_sensors": old_required,
        "new_required_incomplete_sensors": new_required,
        "old_depth_advisory_incomplete_sensors": old_depth,
        "new_depth_advisory_incomplete_sensors": new_depth,
        "required_sensor_static_match": all(row["static_config_equal"] for row in sensor_rows
                                             if row.get("kind") in ("radar", "rgb")),
        "sensor_gate": "PASS" if not required_incomplete else "FAIL",
    }


def _vehicle_configurations(run: Path) -> dict[str, dict]:
    return {
        path.parent.name: json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((run / "vehicles").glob("*/metadata.json"))
    }


def _config_digest(value: dict | None) -> str | None:
    if value is None:
        return None
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _write_csv(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not records:
        path.write_text("", encoding="utf-8")
        return
    keys = list(dict.fromkeys(key for record in records for key in record))
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def _markdown_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |",
             "|" + "|".join("---" for _ in headers) + "|"]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return lines


def _plot_pair(old: dict, new: dict, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 6), constrained_layout=True)
    pids = sorted(set(old["states_by_participant"]) | set(new["states_by_participant"]))
    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    for i, pid in enumerate(pids):
        color = colors[i % len(colors)]
        for label, info, style in (("OLD", old, "--"), ("NEW", new, "-")):
            seq = sorted(info["states_by_participant"].get(pid, []), key=lambda s: s["timestamp"])
            if not seq:
                continue
            ax.plot([s["transform"]["x"] for s in seq], [s["transform"]["y"] for s in seq],
                    linestyle=style, color=color, linewidth=1.4, label="{0} {1}".format(label, pid))
            ax.scatter(seq[0]["transform"]["x"], seq[0]["transform"]["y"], color=color, marker="o", s=14)
    ax.set_title("{0}/{1}: OLD dashed, NEW solid".format(old["path"].parent.name, old["path"].name))
    ax.set_xlabel("world x [m]")
    ax.set_ylabel("world y [m]")
    ax.axis("equal")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8, ncol=2)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=110)
    plt.close(fig)


def compare_pair(old_path: Path, new_path: Path, plot_path: Path) -> dict:
    old, new = _load_run(old_path), _load_run(new_path)
    old_meta, new_meta = old["metadata"], new["metadata"]
    old_map, new_map = old["truth_metadata"].get("map"), new["truth_metadata"].get("map")
    old_pairs, old_triggers = _events_for_pair(old)
    new_pairs, new_triggers = _events_for_pair(new)
    dt_s = float(new_meta.get("fixed_delta_seconds") or old_meta.get("fixed_delta_seconds") or 0.05)
    old_episodes = collision_episodes(old_pairs, dt_s)
    new_episodes = collision_episodes(new_pairs, dt_s)
    old_signature = [event["pair"] for event in old_episodes]
    new_signature = [event["pair"] for event in new_episodes]
    collision_timing_deltas = [
        {"pair": before["pair"], "start_delta_s": after["start_t_rel_s"] - before["start_t_rel_s"],
         "end_delta_s": after["end_t_rel_s"] - before["end_t_rel_s"]}
        for before, after in zip(old_episodes, new_episodes)
    ] if len(old_episodes) == len(new_episodes) else None
    old_trigger_signature = [(event["participant"], event["action_id"]) for event in old_triggers]
    new_trigger_signature = [(event["participant"], event["action_id"]) for event in new_triggers]
    trigger_time_deltas = [after["t_rel_s"] - before["t_rel_s"]
                           for before, after in zip(old_triggers, new_triggers)] \
        if len(old_triggers) == len(new_triggers) else None
    trigger_timing_match = (trigger_time_deltas is not None and all(abs(delta) <= 0.10 for delta in trigger_time_deltas))
    old_roles, new_roles = old["participant_roles"], new["participant_roles"]
    same_participants = old_roles == new_roles
    same_recorders = old["recorders"] == new["recorders"]
    old_vehicle_configs = _vehicle_configurations(old_path)
    new_vehicle_configs = _vehicle_configurations(new_path)
    vehicle_config_rows = []
    for pid in sorted(set(old_vehicle_configs) | set(new_vehicle_configs)):
        before, after = old_vehicle_configs.get(pid), new_vehicle_configs.get(pid)
        vehicle_config_rows.append({
            "participant": pid, "old_present": before is not None, "new_present": after is not None,
            "equal": before == after, "old_configuration": before, "new_configuration": after,
        })
    vehicle_config_equal = all(row["equal"] for row in vehicle_config_rows)
    old_duration = float(old_meta.get("recorded_duration_s", 0.0))
    new_duration = float(new_meta.get("recorded_duration_s", 0.0))
    trajectory_rows = []
    for pid in sorted(set(old["states_by_participant"]) | set(new["states_by_participant"])):
        metrics = trajectory_metrics(old["states_by_participant"].get(pid, []), old["t0"],
                                     new["states_by_participant"].get(pid, []), new["t0"])
        trajectory_rows.append({"participant": pid, "old_samples": len(old["states_by_participant"].get(pid, [])),
                                "new_samples": len(new["states_by_participant"].get(pid, [])),
                                "old_actor_ids": sorted({s["actor_id"] for s in old["states_by_participant"].get(pid, [])}),
                                "new_actor_ids": sorted({s["actor_id"] for s in new["states_by_participant"].get(pid, [])}),
                                **metrics})
    old_sensors = _sensor_inventory(old_path, old_duration)
    new_sensors = _sensor_inventory(new_path, new_duration)
    sensor_rows = []
    for key in sorted(set(old_sensors) | set(new_sensors)):
        a, b = old_sensors.get(key, {}), new_sensors.get(key, {})
        sensor_rows.append({
            "sensor": key, "old_present": bool(a), "new_present": bool(b),
            "kind": b.get("kind", a.get("kind")), "static_config_equal": _static_sensor_equal(a, b) if a and b else False,
            "old_tick_s": a.get("sensor_tick_s"), "new_tick_s": b.get("sensor_tick_s"),
            "old_frames": a.get("frames"), "new_frames": b.get("frames"),
            "old_frames_written": a.get("frames_written"), "new_frames_written": b.get("frames_written"),
            "old_measured_hz": a.get("measured_hz"), "new_measured_hz": b.get("measured_hz"),
            "old_queue_drops": a.get("queue_drops"), "new_queue_drops": b.get("queue_drops"),
            "old_missing_frames": a.get("missing_frame_count"), "new_missing_frames": b.get("missing_frame_count"),
            "old_duplicate_callbacks": a.get("duplicate_callbacks"), "new_duplicate_callbacks": b.get("duplicate_callbacks"),
            "old_gaps_over_1_5_ticks": a.get("timestamp_gaps_over_1_5_ticks"),
            "new_gaps_over_1_5_ticks": b.get("timestamp_gaps_over_1_5_ticks"),
            "old_complete": a.get("complete"), "new_complete": b.get("complete"),
        })
    sensor_quality = _sensor_quality(sensor_rows)
    sensor_static_match = sensor_quality["required_sensor_static_match"]
    collision_equal = old_signature == new_signature
    collision_timing_match = (collision_timing_deltas is not None and all(
        abs(delta["start_delta_s"]) <= 0.10 and abs(delta["end_delta_s"]) <= 0.10
        for delta in collision_timing_deltas))
    trigger_equal = old_trigger_signature == new_trigger_signature
    config_equal = (old_map == new_map and same_participants and same_recorders and sensor_static_match
                    and vehicle_config_equal
                    and old_meta.get("variant") == new_meta.get("variant")
                    and old_meta.get("seed") == new_meta.get("seed"))
    behavior_equal = collision_equal and collision_timing_match and trigger_equal and trigger_timing_match
    physical_gate = "PASS" if config_equal and behavior_equal else "FAIL"
    sensor_gate = sensor_quality["sensor_gate"]
    gate = "PASS" if physical_gate == "PASS" and sensor_gate == "PASS" else "FAIL"
    gap_old, gap_new = _minimum_gaps(old["states"], old["t0"]), _minimum_gaps(new["states"], new["t0"])
    controls = []
    for pid in sorted(set(old_roles) | set(new_roles)):
        before = _control_summary([r for r in old["controls"] if r.get("participant_id") == pid], old["t0"])
        after = _control_summary([r for r in new["controls"] if r.get("participant_id") == pid], new["t0"])
        acc_before = _acceleration_summary(old["states_by_participant"].get(pid, []))
        acc_after = _acceleration_summary(new["states_by_participant"].get(pid, []))
        controls.append({"participant": pid, "old_controls": before, "new_controls": after,
                         "old_acceleration": acc_before, "new_acceleration": acc_after})
    _plot_pair(old, new, plot_path)
    trajectory_max = max((r.get("position_from_start_max_m", 0.0) for r in trajectory_rows), default=0.0)
    trajectory_p95 = max((r.get("position_from_start_p95_m", 0.0) for r in trajectory_rows), default=0.0)
    summary = {
        "scenario": old_path.parent.name, "variant": old_meta.get("variant"),
        "old_path": str(old_path), "new_path": str(new_path),
        "map_old": old_map, "map_new": new_map, "map_equal": old_map == new_map,
        "participants_old": old_roles, "participants_new": new_roles,
        "recorders_old": old["recorders"], "recorders_new": new["recorders"],
        "same_participants": same_participants, "same_recorders": same_recorders,
        "vehicle_configuration_equal": vehicle_config_equal,
        "vehicle_configuration_differences": [row["participant"] for row in vehicle_config_rows if not row["equal"]],
        "actor_ids_are_run_local": True,
        "duration_old_s": old_duration, "duration_new_s": new_duration,
        "duration_delta_s": new_duration - old_duration,
        "state_frames_old": len(old["states"]), "state_frames_new": len(new["states"]),
        "collision_events_old": old_pairs, "collision_events_new": new_pairs,
        "collision_episodes_old": old_episodes, "collision_episodes_new": new_episodes,
        "collision_signature_equal": collision_equal,
        "collision_timing_match": collision_timing_match,
        "collision_timing_deltas": collision_timing_deltas,
        "collision_time_deltas_s": ([d["start_delta_s"] for d in collision_timing_deltas]
                                    if collision_timing_deltas is not None else None),
        "trigger_events_old": old_triggers, "trigger_events_new": new_triggers,
        "trigger_signature_equal": trigger_equal,
        "trigger_timing_match": trigger_timing_match,
        "trigger_time_deltas_s": trigger_time_deltas,
        "sensor_rows": sensor_rows, **sensor_quality,
        "vehicle_config_rows": vehicle_config_rows,
        "physical_gate": physical_gate, "sensor_gate": sensor_gate,
        "minimum_box_gaps_old": gap_old, "minimum_box_gaps_new": gap_new,
        "controls_and_acceleration": controls,
        "trajectory_metrics": trajectory_rows,
        "max_position_from_start_error_m": trajectory_max,
        "max_position_from_start_p95_m": trajectory_p95,
        "configuration_equal": config_equal,
        "behavior_signature_equal": behavior_equal,
        "gate": gate,
        "plot": str(plot_path),
    }
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old-root", type=Path, default=ROOT / "traces")
    parser.add_argument("--new-root", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    comparisons, trajectory_rows, sensor_rows = [], [], []
    collision_rows, collision_episode_rows, maneuver_rows = [], [], []
    trigger_rows, minimum_gap_rows, vehicle_config_rows = [], [], []
    missing = []
    for scenario, variants in sorted(CANONICAL.items()):
        for variant in variants:
            rel = Path(scenario) / ("run_0_" + variant)
            old_path, new_path = args.old_root / rel, args.new_root / rel
            if not old_path.is_dir() or not new_path.is_dir():
                missing.append({"scenario": scenario, "variant": variant,
                                "old_present": old_path.is_dir(), "new_present": new_path.is_dir()})
                continue
            plot_path = args.out_dir / "trajectories" / (scenario + "_" + variant + ".png")
            item = compare_pair(old_path, new_path, plot_path)
            comparisons.append(item)
            for row in item["trajectory_metrics"]:
                trajectory_rows.append({"scenario": scenario, "variant": variant, **row})
            for row in item["sensor_rows"]:
                sensor_rows.append({"scenario": scenario, "variant": variant, **row})
            for side in ("old", "new"):
                for event in item["collision_events_" + side]:
                    collision_rows.append({"scenario": scenario, "variant": variant, "dataset": side.upper(), **event})
                for event in item["collision_episodes_" + side]:
                    collision_episode_rows.append({"scenario": scenario, "variant": variant,
                                                   "dataset": side.upper(), **event})
                for event in item["trigger_events_" + side]:
                    trigger_rows.append({"scenario": scenario, "variant": variant, "dataset": side.upper(), **event})
            for pair in sorted(set(item["minimum_box_gaps_old"]) | set(item["minimum_box_gaps_new"])):
                before, after = item["minimum_box_gaps_old"].get(pair, {}), item["minimum_box_gaps_new"].get(pair, {})
                minimum_gap_rows.append({
                    "scenario": scenario, "variant": variant, "pair": pair,
                    **{"old_" + key: value for key, value in before.items()},
                    **{"new_" + key: value for key, value in after.items()},
                })
            for config in item["vehicle_config_rows"]:
                before, after = config["old_configuration"], config["new_configuration"]
                keys = sorted(set(before or {}) | set(after or {}))
                vehicle_config_rows.append({
                    "scenario": scenario, "variant": variant, "participant": config["participant"],
                    "equal": config["equal"], "old_sha256": _config_digest(before),
                    "new_sha256": _config_digest(after),
                    "old_blueprint": (before or {}).get("blueprint"),
                    "new_blueprint": (after or {}).get("blueprint"),
                    "old_sensor_profile": (before or {}).get("sensor_profile"),
                    "new_sensor_profile": (after or {}).get("sensor_profile"),
                    "old_spawn_transform": json.dumps((before or {}).get("vehicle_transform"), sort_keys=True),
                    "new_spawn_transform": json.dumps((after or {}).get("vehicle_transform"), sort_keys=True),
                    "changed_top_level_fields": json.dumps([key for key in keys
                                                             if (before or {}).get(key) != (after or {}).get(key)]),
                })
            for row in item["controls_and_acceleration"]:
                maneuver_rows.append({"scenario": scenario, "variant": variant, **row})

    _write_csv(args.out_dir / "run_comparison.csv", [{k: v for k, v in item.items()
                if k not in ("trajectory_metrics", "sensor_rows", "controls_and_acceleration",
                             "collision_events_old", "collision_events_new", "trigger_events_old",
                             "trigger_events_new", "collision_episodes_old", "collision_episodes_new",
                             "vehicle_config_rows", "minimum_box_gaps_old", "minimum_box_gaps_new")}
                for item in comparisons])
    _write_csv(args.out_dir / "trajectory_metrics.csv", trajectory_rows)
    _write_csv(args.out_dir / "sensor_comparison.csv", sensor_rows)
    _write_csv(args.out_dir / "collision_events.csv", collision_rows)
    _write_csv(args.out_dir / "collision_episodes.csv", collision_episode_rows)
    _write_csv(args.out_dir / "trigger_events.csv", trigger_rows)
    _write_csv(args.out_dir / "minimum_gap_comparison.csv", minimum_gap_rows)
    _write_csv(args.out_dir / "vehicle_config_comparison.csv", vehicle_config_rows)
    _write_csv(args.out_dir / "maneuver_comparison.csv", maneuver_rows)
    summary = {
        "old_root": str(args.old_root.resolve()), "new_root": str(args.new_root.resolve()),
        "expected_runs": sum(len(v) for v in CANONICAL.values()),
        "compared_runs": len(comparisons), "missing_pairs": missing,
        "comparison_complete": len(comparisons) == sum(len(v) for v in CANONICAL.values()) and not missing,
        "pass_runs": sum(item["gate"] == "PASS" for item in comparisons),
        "physical_pass_runs": sum(item["physical_gate"] == "PASS" for item in comparisons),
        "sensor_pass_runs": sum(item["sensor_gate"] == "PASS" for item in comparisons),
        "fail_runs": ["{0}/{1}".format(item["scenario"], item["variant"])
                      for item in comparisons if item["gate"] != "PASS"],
        "physical_fail_runs": ["{0}/{1}".format(item["scenario"], item["variant"])
                               for item in comparisons if item["physical_gate"] != "PASS"],
        "sensor_fail_runs": ["{0}/{1}".format(item["scenario"], item["variant"])
                             for item in comparisons if item["sensor_gate"] != "PASS"],
        "non_physical_differences": ["actor IDs and absolute CARLA frame/timestamp origins are run-local; comparison uses participant IDs, relative scenario time, and relative frame offsets"],
        "comparison_method": "20 Hz time-aligned ground truth; world position and displacement-from-first-recorded-state are both reported; wrapped yaw differences; reciprocal callbacks deduplicated within a CARLA frame and participant pair; contact episodes group callbacks for one pair when gaps are at most 2.5 fixed ticks; episode start/end timing tolerance is 0.10 s; radar and RGB block on missing samples, queue drops, unmeasured frames, or absent channel; depth-channel completeness is reported as advisory and is not a campaign gate; duplicate callback counts are reported separately; vehicle metadata, required sensor configuration, controls and minimum oriented box gaps are compared.",
    }
    (args.out_dir / "comparison_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    lines = ["# OLD vs NEW CARLA reacquisition comparison", "",
             "Trajectory overlays: OLD dashed, NEW solid. Physical contacts are listed separately in `collision_events.csv`; actor IDs, absolute frame numbers and absolute timestamp origins are run-local and are not treated as behavior changes.", "",
             "| Run | Map | Participants / recorders | Duration delta [s] | Physical gate | OLD/NEW contact episodes | Trigger signature/time | Max path error [m] | Sensor gate | Plot |",
             "|---|---|---|---:|---|---|---|---:|---|---|"]
    for item in comparisons:
        plot_rel = Path(item["plot"]).relative_to(args.out_dir).as_posix()
        lines.append("| {0}/{1} | {2} | {3} / {4} | {5:+.3f} | {6} | {7}/{8} | {9}/{10} | {11:.3f} | {12} | [overlay]({13}) |".format(
            item["scenario"], item["variant"], item["map_new"], ",".join(item["participants_new"]),
            ",".join(item["recorders_new"]), item["duration_delta_s"], item["physical_gate"],
            len(item["collision_episodes_old"]), len(item["collision_episodes_new"]),
            "same" if item["trigger_signature_equal"] else "DIFFERENT",
            "same" if item["trigger_timing_match"] else "DIFF",
            item["max_position_from_start_error_m"], item["sensor_gate"], plot_rel))
    if missing:
        lines += ["", "## Missing run pairs", ""]
        lines += ["- {0}/{1}: old={2}, new={3}".format(m["scenario"], m["variant"], m["old_present"], m["new_present"])
                  for m in missing]
    (args.out_dir / "comparison_index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    detail = ["# Per-run OLD vs NEW details", "",
              "Relative times are measured from each run's first scenario state. Position reports both world-coordinate and displacement-from-start errors. See `trajectory_metrics.csv`, `sensor_comparison.csv`, `collision_events.csv`, `collision_episodes.csv`, `trigger_events.csv`, `minimum_gap_comparison.csv`, and `maneuver_comparison.csv` for row-level values.", ""]
    for item in comparisons:
        detail.extend(["## {0}/{1}".format(item["scenario"], item["variant"]), "",
                       "[Trajectory overlay]({0})".format(Path(item["plot"]).relative_to(args.out_dir).as_posix()), ""])
        detail.extend(_markdown_table(
            ["Configuration / coverage", "OLD", "NEW", "Comparison"], [
                ["Map", str(item["map_old"]), str(item["map_new"]), "same" if item["map_equal"] else "DIFFERENT"],
                ["Participants", str(item["participants_old"]), str(item["participants_new"]),
                 "same" if item["same_participants"] else "DIFFERENT"],
                ["Recorders", ", ".join(item["recorders_old"]), ", ".join(item["recorders_new"]),
                 "same" if item["same_recorders"] else "DIFFERENT"],
                ["Vehicle metadata", "see config CSV", "see config CSV",
                 "same" if item["vehicle_configuration_equal"] else "DIFFERENT"],
                ["Duration [s]", "{0:.3f}".format(item["duration_old_s"]),
                 "{0:.3f}".format(item["duration_new_s"]), "delta {0:+.3f}s".format(item["duration_delta_s"])],
                ["Ground-truth state rows", str(item["state_frames_old"]), str(item["state_frames_new"]),
                 "same" if item["state_frames_old"] == item["state_frames_new"] else "DIFFERENT"],
                ["Physical behavior gate", item["physical_gate"], item["physical_gate"],
                 "same" if item["physical_gate"] == "PASS" else "CHECK"],
                ["Required incomplete radar/RGB", ", ".join(item["old_required_incomplete_sensors"]) or "none",
                 ", ".join(item["new_required_incomplete_sensors"]) or "none",
                 "same" if item["old_required_incomplete_sensors"] == item["new_required_incomplete_sensors"] else "DIFFERENT"],
                ["Advisory incomplete depth", ", ".join(item["old_depth_advisory_incomplete_sensors"]) or "none",
                 ", ".join(item["new_depth_advisory_incomplete_sensors"]) or "none", "reported; not blocking"],
            ]))
        detail.extend(["", "### Trajectory error over relative time", ""])
        trajectory = []
        for row in item["trajectory_metrics"]:
            trajectory.append([
                row["participant"], "{0}/{1}".format(row.get("old_samples", 0), row.get("new_samples", 0)),
                "{0:.4f}/{1:.4f}".format(row.get("position_world_p95_m", 0.0), row.get("position_world_max_m", 0.0)),
                "{0:.4f}/{1:.4f}".format(row.get("position_from_start_p95_m", 0.0), row.get("position_from_start_max_m", 0.0)),
                "{0:.4f}/{1:.4f}".format(row.get("velocity_2d_p95_mps", 0.0), row.get("velocity_2d_max_mps", 0.0)),
                "{0:.4f}/{1:.4f}".format(row.get("heading_abs_p95_deg", 0.0), row.get("heading_abs_max_deg", 0.0)),
            ])
        detail.extend(_markdown_table(["Participant", "OLD/NEW samples", "World position error p95/max [m]",
                                       "From-start motion error p95/max [m]",
                                       "Velocity 2D p95/max [m/s]", "Heading p95/max [deg]"], trajectory))
        detail.extend(["", "### Collision episodes and triggers", ""])
        contacts = []
        for side in ("old", "new"):
            for event in item["collision_episodes_" + side]:
                contacts.append([side.upper(), event["pair"],
                                 "{0:.2f}–{1:.2f}".format(event["start_t_rel_s"], event["end_t_rel_s"]),
                                 str(event["contact_ticks"]), "{0:.1f}".format(event["impulse_sum"])])
        detail.extend(_markdown_table(["Dataset", "Pair", "Start–end [s]", "Contact ticks", "Impulse sum [N·s]"],
                                      contacts or [["OLD/NEW", "none", "—", "0", "0"]]))
        trigger_rows = []
        for side in ("old", "new"):
            for event in item["trigger_events_" + side]:
                trigger_rows.append([side.upper(), str(event["participant"]), str(event["action_id"]),
                                     "{0:.3f}".format(event["t_rel_s"])])
        detail.extend(["", "Trigger signatures: {0}; trigger timing: {1}.".format(
            "same" if item["trigger_signature_equal"] else "DIFFERENT",
            "same within 0.10 s" if item["trigger_timing_match"] else "DIFFERENT"), ""])
        detail.extend(_markdown_table(["Dataset", "Participant", "Action", "t relative [s]"],
                                      trigger_rows or [["OLD/NEW", "—", "none", "—"]]))
        detail.extend(["", "### Sensor channels", ""])
        sensor_summary = []
        for kind in ("radar", "rgb", "depth"):
            channels = [row for row in item["sensor_rows"] if row["kind"] == kind]
            old_complete = sum(row["old_complete"] is True for row in channels)
            new_complete = sum(row["new_complete"] is True for row in channels)
            ticks = sorted({str(row["new_tick_s"]) for row in channels if row["new_tick_s"] is not None})
            sensor_summary.append([kind, str(len(channels)), "{0}/{1}".format(old_complete, len(channels)),
                                   "{0}/{1}".format(new_complete, len(channels)), ", ".join(ticks) or "—"])
        detail.extend(_markdown_table(["Sensor", "Channels", "OLD complete", "NEW complete", "NEW tick [s]"],
                                      sensor_summary))
        detail.extend(["", "Row-level sensor frame counts, measured rates, missing frames, queue drops, duplicate callbacks and static configuration are in `sensor_comparison.csv`.", ""])
        detail.extend(["### Maneuvers and minimum distances", "",
                       "OLD/NEW brake, throttle, steer and acceleration summaries are in `maneuver_comparison.csv`; minimum oriented box gaps and relative times are in `minimum_gap_comparison.csv`.", ""])
    (args.out_dir / "comparison_details.md").write_text("\n".join(detail), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if summary["comparison_complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
