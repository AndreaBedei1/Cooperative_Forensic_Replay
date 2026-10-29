#!/usr/bin/env python3
"""PRIVILEGED EVALUATION / DEBUG TOOL: when could each recorder's radar see each other vehicle?

    python scripts/audit_radar_visibility.py traces/S10/run_0_single_impact [more runs] [--json out.json]

Ground truth (``ground_truth/states.jsonl``: true poses and boxes of every
vehicle) is read here ONLY to explain sensor coverage and to compare the
reconstruction with what was observable.  Nothing in the reconstruction
imports this script, and nothing it computes is fed back.

Per recorder R and per other true vehicle V, all times in R's own local clock
(seconds since R's first ego sample):

  in range       first sweep with any part of V's body within the range of one of
                 R's radars, whatever the field of view
  inside FOV     first sweep with part of V's body inside the horizontal and vertical
                 field of view and range of at least one of R's radars (front, left,
                 right: each from its own mount, radar/<id>/metadata.json); directly
                 behind R lies the blind zone between the side radars' fields
  raw return     first sweep with a radar return on V's body (box + 0.5 m)
  usable return  first such return passing the tracker's own height filter and
                 moving-speed test (the only returns that can start a track)
  track born     first sample of a reconstructed track lying on V (tentative start)
  confirmed      first measurement of that track with ``min_track_support_s`` of support and
                 ``min_track_updates`` measurements (the tracker's confirmation rule: its id)
  lost           last sample of the track(s) on V, with V's visibility at that time
  occluded       sweeps in V's field of view without a return on V, split by why:
                 "vehicle" (the line of sight to V crosses another vehicle's box),
                 "static" (returns inside V's angular span come back from shorter
                 range: scenery such as buildings stands in between), "edge" (less
                 than a quarter of V's angular extent lies inside the field of
                 view), or "sparse" (no ray hit V's small angular extent)

The delay of the first confirmed track is attributed to the dominant stage:
FOV (outside the field of view while in range), OCCLUSION (vehicle/static) or
RAW_SENSOR (edge/sparse) while inside the field of view without a return,
FILTER (returns, none usable), TRACKER (usable returns before birth /
confirmation).  For TRACKER the longest run of consecutive sweeps with usable
returns and the target's true speed meanwhile tell whether the tracker was
never given enough consecutive moving sweeps for a confirmation (e.g. a target
standing still: its returns are static by design) or failed despite them.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cdf.recording.compact_observations import load_radar_observations  # noqa: E402
from cdf.reconstruction.config import load_config  # noqa: E402
from cdf.reconstruction.local import read_jsonl, reconstruct_vehicle  # noqa: E402
from cdf.replay.model import Pose, local_to_world, rotation_axes  # noqa: E402

BOX_MARGIN_M = 0.5  # a raw return within this distance of V's box is "on V"
TRACK_MARGIN_M = 1.5  # a smoothed track point within this distance of V's box is "on V"


def _rotation(yaw: float, pitch: float, roll: float) -> np.ndarray:
    """Columns: world-frame forward, right, up of a CARLA rotation (degrees)."""
    forward, right, up = rotation_axes(yaw, pitch, roll)
    return np.array([forward, right, up]).T


class Box:
    """A vehicle's oriented bounding box (centre at the body's mid height)."""

    def __init__(self, state: Dict[str, Any]):
        tf, ext = state["transform"], state["bbox_extent"]
        self.rot = _rotation(tf["yaw_deg"], tf["pitch_deg"], tf["roll_deg"])
        self.extent = np.array([ext["x"], ext["y"], ext["z"]])
        self.centre = np.array([tf["x"], tf["y"], tf["z"]]) + self.rot @ np.array([0.0, 0.0, ext["z"]])

    def local(self, points: np.ndarray) -> np.ndarray:
        return (points - self.centre) @ self.rot

    def contains(self, points: np.ndarray, margin: float) -> np.ndarray:
        return np.all(np.abs(self.local(points)) <= self.extent + margin, axis=1)

    def distance_2d(self, points: np.ndarray) -> np.ndarray:
        local = self.local(points)[:, :2]
        outside = np.maximum(np.abs(local) - self.extent[:2], 0.0)
        return np.hypot(outside[:, 0], outside[:, 1])

    def surface_points(self) -> np.ndarray:
        steps = [-1.0, 0.0, 1.0]
        grid = np.array([[a, b, c] for a in steps for b in steps for c in steps if (a, b, c) != (0.0, 0.0, 0.0)])
        return self.centre + (grid * self.extent) @ self.rot.T

    def blocks(self, start: np.ndarray, end: np.ndarray) -> bool:
        """Does the horizontal segment start-end pass through this box (2-D)?"""
        a, b = self.local(start[None])[0][:2], self.local(end[None])[0][:2]
        t0, t1 = 0.0, 1.0
        d = b - a
        for axis in (0, 1):
            if abs(d[axis]) < 1e-9:
                if abs(a[axis]) > self.extent[axis]:
                    return False
                continue
            lo = (-self.extent[axis] - a[axis]) / d[axis]
            hi = (self.extent[axis] - a[axis]) / d[axis]
            lo, hi = min(lo, hi), max(lo, hi)
            t0, t1 = max(t0, lo), min(t1, hi)
            if t0 > t1:
                return False
        return t1 > 0.02 and t0 < 0.98


def _first(times: Sequence[float], flags: Sequence[bool]) -> Optional[float]:
    return next((t for t, flag in zip(times, flags) if flag), None)


def audit_run(run_dir: Path) -> List[Dict[str, Any]]:
    cfg = load_config()
    states = read_jsonl(run_dir / "ground_truth" / "states.jsonl")
    by_frame: Dict[int, Dict[str, Dict[str, Any]]] = {}
    for state in states:
        by_frame.setdefault(int(state["frame"]), {})[state["participant_id"]] = state
    participants = sorted({state["participant_id"] for state in states})
    rows = []
    for owner in participants:
        vehicle_dir = run_dir / "vehicles" / owner
        if not (vehicle_dir / "radar").exists():
            continue
        radars = []
        for observations in load_radar_observations(vehicle_dir):
            meta = observations.metadata
            mount = meta.get("sensor_transform") or {}
            radars.append({"id": str(meta.get("sensor_id", "radar")), "obs": observations,
                           "pos": np.array([mount.get("x", 0.0), mount.get("y", 0.0), mount.get("z", 0.6)]),
                           "rot": _rotation(mount.get("yaw_deg", 0.0), mount.get("pitch_deg", 0.0), 0.0),
                           "half_h": math.radians(float(meta.get("horizontal_fov_deg", 150.0))) / 2.0,
                           "half_v": math.radians(float(meta.get("vertical_fov_deg", 20.0))) / 2.0,
                           "range": float(meta.get("range_m", 90.0)),
                           "index": {int(frame): i for i, frame in enumerate(observations.frames)},
                           "previous": None})
        fov_label = ", ".join("{0} {1:.0f}".format(r["id"], math.degrees(2 * r["half_h"])) for r in radars)
        rec = reconstruct_vehicle(vehicle_dir, cfg)  # the recorder's own reconstruction (local data only)
        origin = rec.clock_origin
        first_ego = read_jsonl(vehicle_dir / "ego.jsonl")[0]
        frame_origin = Pose(float(first_ego["x"]), float(first_ego["y"]), float(first_ego["z"]), float(first_ego["yaw_deg"]))
        collisions = [n.t_local for n in rec.graph.nodes if n.event_type == "COLLISION"]

        per_target: Dict[str, Dict[str, List[Any]]] = {}
        frames = sorted(set().union(*[set(r["index"]) for r in radars])) if radars else []
        for frame in frames:
            world = by_frame.get(int(frame), {})
            own = world.get(owner)
            if own is None:
                continue
            tf = own["transform"]
            own_rot = _rotation(tf["yaw_deg"], tf["pitch_deg"], tf["roll_deg"])
            own_pos = np.array([tf["x"], tf["y"], tf["z"]])
            seen, all_points, all_usable, timestamp = [], [], [], None
            for r in radars:
                sensor = own_pos + own_rot @ r["pos"]
                sensor_rot = own_rot @ r["rot"]
                # The radar's own velocity, as CARLA measures it: its displacement over the tick.
                velocity = ((sensor - r["previous"]) / 0.05 if r["previous"] is not None else
                            np.array([own["velocity"]["x"], own["velocity"]["y"], own["velocity"]["z"]]))
                r["previous"] = sensor
                index = r["index"].get(int(frame))
                if index is None:
                    continue
                timestamp = float(r["obs"].timestamps[index])
                rows4 = np.asarray(r["obs"].frame_detections(index), dtype=float).reshape(-1, 4)
                depth, azimuth, altitude, range_rate = rows4.T
                los = np.column_stack([np.cos(altitude) * np.cos(azimuth), np.cos(altitude) * np.sin(azimuth),
                                       np.sin(altitude)]) @ sensor_rot.T
                points = sensor + los * depth[:, None]
                radial_speed = range_rate + los @ velocity
                height = r["pos"][2] + depth * np.sin(altitude)
                all_points.append(points)
                all_usable.append((height >= cfg.tracking.min_height_m) & (height <= cfg.tracking.max_height_m)
                                  & (np.abs(radial_speed) >= cfg.tracking.moving_speed_mps))
                seen.append((r, sensor, sensor_rot, azimuth, altitude, depth))
            if timestamp is None:
                continue
            t = round(timestamp - origin, 4)
            points = np.concatenate(all_points) if all_points else np.empty((0, 3))
            usable = np.concatenate(all_usable) if all_usable else np.empty(0, dtype=bool)
            boxes = {pid: Box(state) for pid, state in world.items()}
            for target, box in boxes.items():
                if target == owner:
                    continue
                entry = per_target.setdefault(target, {k: [] for k in
                                                       ("t", "range", "fov", "raw", "usable", "occluded", "why",
                                                        "speed")})
                in_range_any, inside_any, occluded_all, best = False, False, True, None
                for r, sensor, sensor_rot, rays_az, rays_el, depth in seen:
                    local = (box.surface_points() - sensor) @ sensor_rot
                    dist = np.linalg.norm(local, axis=1)
                    az = np.arctan2(local[:, 1], local[:, 0])
                    el = np.arctan2(local[:, 2], np.hypot(local[:, 0], local[:, 1]))
                    in_range = dist <= r["range"]
                    inside = in_range & (np.abs(az) <= r["half_h"]) & (np.abs(el) <= r["half_v"])
                    in_range_any |= bool(in_range.any())
                    if not inside.any():
                        continue
                    inside_any = True
                    blocked = any(other.blocks(sensor, box.centre) for pid, other in boxes.items()
                                  if pid not in (owner, target))
                    occluded_all &= blocked
                    share = float(inside.mean())
                    if best is None or share > best[0]:
                        best = (share, r, az, el, dist, rays_az, rays_el, depth, blocked)
                occluded = inside_any and occluded_all
                on_target = box.contains(points, BOX_MARGIN_M) if len(points) else np.zeros(0, bool)
                why = ""
                if inside_any and not on_target.any():
                    _, r, az, el, dist, rays_az, rays_el, depth, blocked = best
                    az_in = np.clip(az, -r["half_h"], r["half_h"])
                    inside_share = (az_in.max() - az_in.min()) / max(az.max() - az.min(), 1e-6)
                    span = ((rays_az >= az.min()) & (rays_az <= az.max())
                            & (rays_el >= el.min()) & (rays_el <= el.max()))
                    closer = span & (depth < dist.min() - 1.0)
                    why = ("vehicle" if occluded else
                           "static" if closer.any() and closer.sum() >= 0.5 * span.sum() else
                           "edge" if inside_share < 0.25 else "sparse")
                entry["t"].append(t)
                entry["range"].append(in_range_any)
                entry["fov"].append(inside_any)
                entry["raw"].append(int(on_target.sum()))
                entry["usable"].append(int((on_target & usable).sum()))
                entry["occluded"].append(occluded)
                entry["why"].append(why)
                velocity_t = world[target]["velocity"]
                entry["speed"].append(math.hypot(velocity_t["x"], velocity_t["y"]))

        # Reconstructed tracks lying on each true vehicle.
        gt_times = {round(float(s["timestamp"]) - origin, 4): s for s in states if s["participant_id"] != owner}
        on_vehicle: Dict[str, List[Tuple[str, float, float, float]]] = {}
        for track in rec.tracks:
            votes: Dict[str, int] = {}
            for sample in track.samples:
                world_xy = np.array(local_to_world(frame_origin, sample.x_m, sample.y_m) + (0.0,))
                frame_states = [s for s in states if abs(float(s["timestamp"]) - origin - sample.t_local) < 0.026
                                and s["participant_id"] != owner]
                for state in frame_states:
                    box = Box(state)
                    world_xy[2] = box.centre[2]
                    if box.distance_2d(world_xy[None])[0] <= TRACK_MARGIN_M:
                        votes[state["participant_id"]] = votes.get(state["participant_id"], 0) + 1
            if votes:
                target, count = max(votes.items(), key=lambda item: item[1])
                if count >= 0.5 * len(track.samples):
                    measured = [s.t_local for s in track.samples if s.measured]
                    confirmed = next((t for k, t in enumerate(measured)
                                      if t - measured[0] >= cfg.tracking.min_track_support_s - 1e-6
                                      and k + 1 >= cfg.tracking.min_track_updates), measured[-1])
                    on_vehicle.setdefault(target, []).append((track.track_id, track.first_t, confirmed, track.last_t))

        for target, entry in sorted(per_target.items()):
            t = entry["t"]
            tracks = sorted(on_vehicle.get(target, []), key=lambda item: item[1])
            row = {"run": run_dir.parent.name + "/" + run_dir.name, "recorder": owner, "target": target,
                   "fov_deg": fov_label,
                   "in_range": _first(t, entry["range"]), "inside_fov": _first(t, entry["fov"]),
                   "raw_return": _first(t, [n > 0 for n in entry["raw"]]),
                   "usable_return": _first(t, [n > 0 for n in entry["usable"]]),
                   "track_born": tracks[0][1] if tracks else None,
                   "confirmed": tracks[0][2] if tracks else None,
                   "tracks": [{"track": tid, "born": born, "confirmed": conf, "lost": last} for tid, born, conf, last in tracks],
                   "collision": collisions[0] if collisions else None,
                   "fov_s": round(0.05 * sum(entry["fov"]), 2)}
            before = [w for ti, w in zip(t, entry["why"]) if w and (row["raw_return"] is None or ti < row["raw_return"])]
            row["no_return_in_fov_before_first_return"] = {w: round(0.05 * before.count(w), 2) for w in sorted(set(before))}
            for track in row["tracks"]:
                after = [i for i, ti in enumerate(t) if ti > track["lost"] + 1e-6][:1]
                if after and track["lost"] < t[-1] - 0.06:
                    i = after[0]
                    track["after_loss"] = ("outside FOV" if not entry["fov"][i] else
                                           "no return: " + entry["why"][i] if entry["raw"][i] == 0 else
                                           "in FOV, returns only static/filtered" if entry["usable"][i] == 0 else
                                           "in FOV with usable returns (tracker dropped it)")
            if row["usable_return"] is not None:
                until = row["confirmed"] if row["confirmed"] is not None else t[-1]
                window = [i for i, ti in enumerate(t) if row["usable_return"] - 1e-6 <= ti <= until + 1e-6]
                runs, current = [], 0
                for i in window:
                    current = current + 1 if entry["usable"][i] > 0 else 0
                    runs.append(current)
                speeds = [entry["speed"][i] for i in window]
                row["tracker_input"] = {
                    "usable_sweeps": sum(1 for i in window if entry["usable"][i] > 0),
                    "sweeps": len(window), "longest_usable_run": max(runs) if runs else 0,
                    "target_speed_mps": [round(min(speeds), 2), round(max(speeds), 2)] if speeds else None}
            row["delay_cause"] = _classify(row, entry, confirmation_sweeps(cfg.tracking))
            rows.append(row)
    return rows


def confirmation_sweeps(tracking: Any) -> int:
    """Consecutive 20 Hz sweeps a confirmation needs: min_track_support_s of support, min_track_updates updates."""
    return max(tracking.min_track_updates, int(round(tracking.min_track_support_s / 0.05)) + 1)


def _tracker_detail(row: Dict[str, Any], min_frames: int) -> str:
    info = row.get("tracker_input") or {}
    if not info:
        return ""
    speeds = info.get("target_speed_mps") or [0.0, 0.0]
    longest = info["longest_usable_run"]
    reason = ("never {0} consecutive usable sweeps".format(min_frames) if longest < min_frames
              else "usable runs long enough: association/gating")
    return "; {0} of {1} sweeps usable, longest run {2}; target {3:.1f}-{4:.1f} m/s: {5}".format(
        info["usable_sweeps"], info["sweeps"], longest, speeds[0], speeds[1], reason)


def _classify(row: Dict[str, Any], entry: Dict[str, List[Any]], min_frames: int = 5) -> str:
    if row["in_range"] is None:
        return "never within radar range"
    if row["inside_fov"] is None:
        return "FOV (never inside the field of view)"
    why = row["no_return_in_fov_before_first_return"]
    blind = max(why.items(), key=lambda item: item[1])[0] if why else ""
    blind_cause = {"vehicle": "OCCLUSION(vehicle)", "static": "OCCLUSION(static)"}.get(blind, "RAW_SENSOR(" + (blind or "?") + ")")
    if row["confirmed"] is None:
        if row["raw_return"] is None:
            return blind_cause + " (no return while in FOV)"
        if row["usable_return"] is None:
            return "FILTER (returns, none moving/usable)"
        return "TRACKER (usable returns, no confirmed track{0})".format(_tracker_detail(row, min_frames))
    stages = [("FOV", row["inside_fov"] - row["in_range"]),
              ("RAW_SENSOR", (row["raw_return"] or row["inside_fov"]) - row["inside_fov"]),
              ("FILTER", (row["usable_return"] or row["raw_return"] or 0) - (row["raw_return"] or 0)),
              ("TRACKER", row["confirmed"] - (row["usable_return"] or row["confirmed"]))]
    cause, delay = max(stages, key=lambda item: item[1])
    if cause == "RAW_SENSOR":
        cause = blind_cause
    if delay <= 0.15:
        return "none (prompt)"
    detail = _tracker_detail(row, min_frames) if cause == "TRACKER" and delay > 0.5 else ""
    return "{0} (+{1:.2f} s{2})".format(cause, delay, detail)


def _fmt(value: Optional[float]) -> str:
    return "   -  " if value is None else "{0:6.2f}".format(value)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="PRIVILEGED radar visibility audit (evaluation/debug only)")
    parser.add_argument("runs", nargs="+")
    parser.add_argument("--json", default=None, help="also write the rows to this JSON file")
    args = parser.parse_args(argv)
    all_rows = []
    print("PRIVILEGED EVALUATION: uses ground_truth/ to explain radar coverage; never used by reconstruction.")
    print("times in the recorder's local clock [s]; '-' = never")
    header = "{0:28s} {1:3s} {2:3s} {3:>6s} {4:>6s} {5:>6s} {6:>6s} {7:>6s} {8:>6s} {9:>6s}  {10}".format(
        "run", "rec", "veh", "range", "FOV", "raw", "usable", "born", "conf", "coll", "first-detection delay / tracks")
    print(header)
    for run in args.runs:
        rows = audit_run(Path(run))
        all_rows.extend(rows)
        if rows:
            print("{0}: radars (horizontal FOV, deg) {1}".format(rows[0]["run"], rows[0]["fov_deg"]))
        for row in rows:
            tracks = "; ".join("{0} {1:.2f}-{2:.2f}{3}".format(t["track"], t["born"], t["lost"],
                                                            " (" + t["after_loss"] + ")" if "after_loss" in t else "")
                               for t in row["tracks"])
            print("{0:28s} {1:3s} {2:3s} {4} {5} {6} {7} {8} {9} {10}  {11} | {12}{13}".format(
                row["run"], row["recorder"], row["target"], None, _fmt(row["in_range"]), _fmt(row["inside_fov"]),
                _fmt(row["raw_return"]), _fmt(row["usable_return"]), _fmt(row["track_born"]), _fmt(row["confirmed"]),
                _fmt(row["collision"]), row["delay_cause"], tracks or "no track",
                "  | in FOV w/o return before 1st: " + ", ".join("{0} {1:.2f}s".format(k, v) for k, v in
                                                               row["no_return_in_fov_before_first_return"].items())
                if row["no_return_in_fov_before_first_return"] else ""))
    if args.json:
        Path(args.json).write_text(json.dumps(all_rows, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
