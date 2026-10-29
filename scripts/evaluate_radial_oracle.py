#!/usr/bin/env python3
"""Privileged, offline target-centre radial-velocity oracle.

This module is intentionally outside the acquisition path.  It uses only the
ground-truth state trace to assign anonymous radar/depth returns to physical
participants and compares each sensor independently with a target-centre
closing speed.  Radar and depth store opposite signs, so both are converted
with ``closing_speed`` (positive = approaching) before they are scored.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cdf.recording.compact_observations import closing_speed, load_observation_stream  # noqa: E402


def _rotation(roll: float, pitch: float, yaw: float) -> np.ndarray:
    """Vehicle-to-world rotation for CARLA angles in radians.

    CARLA/Unreal is left-handed: positive pitch lifts the nose and positive
    roll lowers the right side, so both enter the right-handed elementary
    rotations below with a minus sign (the result equals Unreal's
    FRotationMatrix).  Without it, a 7 degree climb looked 14 degrees off.
    """
    cr, sr = math.cos(-roll), math.sin(-roll)
    cp, sp = math.cos(-pitch), math.sin(-pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)
    rx = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]])
    ry = np.array([[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]])
    rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]])
    return rz @ ry @ rx


def _state_at(states: List[Dict[str, Any]], timestamp: float) -> Optional[Dict[str, Any]]:
    if not states or timestamp < states[0]["timestamp"] or timestamp > states[-1]["timestamp"]:
        return None
    times = np.asarray([s["timestamp"] for s in states], dtype=float)
    right = int(np.searchsorted(times, timestamp, side="left"))
    if right == 0:
        return states[0]
    if right == len(states):
        return states[-1]
    left = right - 1; a, b = states[left], states[right]
    if abs(float(b["timestamp"]) - float(a["timestamp"])) < 1e-12:
        return a
    u = (timestamp - float(a["timestamp"])) / (float(b["timestamp"]) - float(a["timestamp"]))
    out = dict(a); ta, tb = a["transform"], b["transform"]
    transform = {}
    for key in ("x", "y", "z"):
        transform[key] = float(ta[key]) + u * (float(tb[key]) - float(ta[key]))
    # Unwrapped interpolation avoids the +/-180 degree discontinuity.
    for key in ("roll_deg", "pitch_deg", "yaw_deg"):
        av, bv = float(ta[key]), float(tb[key]); delta = (bv - av + 180.0) % 360.0 - 180.0
        transform[key] = av + u * delta
    out["timestamp"] = float(timestamp); out["transform"] = transform
    if a.get("bbox_extent") and b.get("bbox_extent"):
        out["bbox_extent"] = {k: float(a["bbox_extent"][k]) + u * (float(b["bbox_extent"][k]) - float(a["bbox_extent"][k])) for k in ("x", "y", "z")}
    return out


def _sensor_origin(observer: Dict[str, Any], extrinsic: Dict[str, Any]) -> np.ndarray:
    tf = observer["transform"]
    ego_r = _rotation(math.radians(tf.get("roll_deg", 0)), math.radians(tf.get("pitch_deg", 0)), math.radians(tf.get("yaw_deg", 0)))
    local = np.array([extrinsic.get("x", 0.0), extrinsic.get("y", 0.0), extrinsic.get("z", 0.0)], dtype=float)
    return np.array([tf["x"], tf["y"], tf["z"]], dtype=float) + ego_r @ local


def _local_point(observer: Dict[str, Any], extrinsic: Dict[str, Any], world: np.ndarray) -> np.ndarray:
    tf = observer["transform"]
    ego_r = _rotation(math.radians(tf.get("roll_deg", 0)), math.radians(tf.get("pitch_deg", 0)), math.radians(tf.get("yaw_deg", 0)))
    origin = _sensor_origin(observer, extrinsic)
    sensor_r = _rotation(math.radians(extrinsic.get("roll_deg", 0)), math.radians(extrinsic.get("pitch_deg", 0)), math.radians(extrinsic.get("yaw_deg", 0)))
    return sensor_r.T @ ego_r.T @ (world - origin)


def _extent(state: Dict[str, Any]) -> np.ndarray:
    e = state.get("bbox_extent")
    if e:
        return np.array([float(e["x"]), float(e["y"]), float(e["z"])])
    # Conservative fallback for traces produced before privileged extents were added.
    return np.array([2.4, 1.1, 0.8])


def _target_envelope(observer: Dict[str, Any], target: Dict[str, Any], extrinsic: Dict[str, Any], margin_m: float) -> Tuple[float, float, float, float, float, float]:
    tf = target["transform"]; centre = np.array([tf["x"], tf["y"], tf["z"]], dtype=float)
    yaw = math.radians(float(tf.get("yaw_deg", 0))); r = _rotation(0.0, 0.0, yaw); e = _extent(target) + margin_m
    points = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (-1, 1):
                points.append(_local_point(observer, extrinsic, centre + r @ np.array([sx * e[0], sy * e[1], sz * e[2]])))
    points = np.asarray(points); ranges = np.linalg.norm(points, axis=1)
    az = np.arctan2(points[:, 1], points[:, 0]); alt = np.arctan2(points[:, 2], np.maximum(1e-6, np.hypot(points[:, 0], points[:, 1])))
    return float(ranges.min()), float(ranges.max()), float(az.min()), float(az.max()), float(alt.min()), float(alt.max())


def _oracle_velocity(observer_states: List[Dict[str, Any]], target_states: List[Dict[str, Any]], extrinsic: Dict[str, Any], t: float) -> Optional[float]:
    """Closing speed of the target centre: positive while the range shrinks."""
    def radius(at: float) -> Optional[float]:
        obs, target = _state_at(observer_states, at), _state_at(target_states, at)
        if obs is None or target is None:
            return None
        return float(np.linalg.norm(_sensor_origin(obs, extrinsic) - np.array([target["transform"][k] for k in ("x", "y", "z")], dtype=float)))
    times = [float(s["timestamp"]) for s in observer_states]
    i = int(np.searchsorted(times, t)); i = max(0, min(len(times) - 1, i))
    if len(times) == 1:
        return None
    if 0 < i < len(times) - 1:
        ta, tb = times[i - 1], times[i + 1]; ra, rb = radius(ta), radius(tb)
    elif i == 0:
        ta, tb = times[0], times[1]; ra, rb = radius(ta), radius(tb)
    else:
        ta, tb = times[-2], times[-1]; ra, rb = radius(ta), radius(tb)
    if ra is None or rb is None or tb <= ta:
        return None
    return float((ra - rb) / (tb - ta))


def _metrics(values: List[Tuple[float, float]], deadband: float, available: int) -> Dict[str, Any]:
    if not values:
        return {"target_frame_samples": 0, "target_frame_available": int(available), "coverage_percentage": 0.0}
    arr = np.asarray(values, dtype=float); err = arr[:, 0] - arr[:, 1]
    sign = lambda x: np.where(x > deadband, 1, np.where(x < -deadband, -1, 0))
    return {"target_frame_samples": int(len(arr)), "target_frame_available": int(available),
            "coverage_percentage": float(100.0 * len(arr) / available) if available else 0.0,
            "sign_agreement_percentage": float(100 * np.mean(sign(arr[:, 0]) == sign(arr[:, 1]))),
            "pearson": float(np.corrcoef(arr[:, 0], arr[:, 1])[0, 1]) if len(arr) > 1 else 0.0,
            "median_absolute_error": float(np.median(np.abs(err))), "mae": float(np.mean(np.abs(err))),
            "rmse": float(np.sqrt(np.mean(err * err))), "bias": float(np.mean(err))}


def evaluate(run_root: Path, observer_id: str, target_id: str, deadband: float = 0.5, margin_m: float = 1.0) -> Dict[str, Any]:
    gt: Dict[str, List[Dict[str, Any]]] = {}
    for line in (run_root / "ground_truth" / "states.jsonl").read_text(encoding="utf-8").splitlines():
        state = json.loads(line); gt.setdefault(state["participant_id"], []).append(state)
    for states in gt.values():
        states.sort(key=lambda s: float(s["timestamp"]))
    results: Dict[str, Any] = {"observer": observer_id, "target": target_id, "margin_m": margin_m, "sign_deadband_mps": deadband}
    for source, folder in (("radar", "radar"), ("depth", "depth")):
        vehicle = run_root / "vehicles" / observer_id
        stream = load_observation_stream(vehicle, source=source)
        metadata = json.loads((vehicle / folder / "metadata.json").read_text(encoding="utf-8"))
        extrinsic = metadata.get("sensor_transform", {})
        pairs: List[Tuple[float, float]] = []
        available = 0
        for index, timestamp in enumerate(stream.timestamps):
            t = float(timestamp); obs = _state_at(gt[observer_id], t); target = _state_at(gt[target_id], t)
            if obs is None or target is None:
                continue
            envelope = _target_envelope(obs, target, extrinsic, margin_m)
            oracle = _oracle_velocity(gt[observer_id], gt[target_id], extrinsic, t)
            if oracle is None:
                continue
            available += 1
            lo, hi, amin, amax, zmin, zmax = envelope
            candidates = []
            for detection in stream.frame_detections(index):
                if not np.isfinite(detection[3]):
                    continue
                depth, az, alt = map(float, detection[:3])
                if lo <= depth <= hi and amin <= az <= amax and zmin <= alt <= zmax:
                    candidates.append(float(closing_speed(detection[3], source)))
            if candidates:
                pairs.append((float(np.median(candidates)), oracle))
        results[source] = _metrics(pairs, deadband, available)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate radar/depth against a privileged target-centre oracle")
    parser.add_argument("run_root", type=Path); parser.add_argument("--observer", default="A"); parser.add_argument("--target", default="B")
    parser.add_argument("--sign-deadband-mps", type=float, default=0.5); parser.add_argument("--margin-m", type=float, default=1.0)
    args = parser.parse_args(); print(json.dumps(evaluate(args.run_root, args.observer, args.target, args.sign_deadband_mps, args.margin_m), indent=2, sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
