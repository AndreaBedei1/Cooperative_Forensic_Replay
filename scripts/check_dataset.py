#!/usr/bin/env python3
"""Integrity of a recorded dataset of the 22 canonical runs (raw data only, no reconstruction).

    python scripts/check_dataset.py --root F:/.../canonical_A [--out report.json]

Per run: the run, ground-truth and vehicle metadata exist; the ground-truth states cover every participant at
every frame with a constant step equal to ``fixed_delta_seconds`` and no frame missing; every recorder's
``ego.jsonl``, ``controls.jsonl`` and ``lights.jsonl`` hold one sample per recorded frame (the same frames as the
ground truth); each radar holds one sweep per frame with strictly increasing timestamps; the RGB camera wrote one
frame per ``sensor_tick`` with no queue drop or duplicate; no depth camera stream exists (disabled in the current
protocol); every collision a recorder logged is in the ground truth at the same frame; and
``late_impact_notifications`` is 0 (the post-impact controls did not depend on callback timing).
Exit status 1 when any run fails.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from cdf.recording.compact_observations import load_radar_observations  # noqa: E402
from validate_canonical import CANONICAL  # noqa: E402

TOL = 1e-6


def _jsonl(path: Path) -> List[Dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def check_run(run: Path) -> Dict[str, Any]:
    problems: List[str] = []
    info: Dict[str, Any] = {"run": "{0}/{1}".format(run.parent.name, run.name)}
    meta = json.loads((run / "metadata.json").read_text(encoding="utf-8"))
    dt = float(meta["fixed_delta_seconds"])
    info["duration_s"] = round(float(meta.get("recorded_duration_s", 0.0)), 3)
    info["late_impact_notifications"] = meta.get("late_impact_notifications")
    if meta.get("late_impact_notifications") != 0:
        problems.append("late_impact_notifications = {0}".format(meta.get("late_impact_notifications")))
    gt_meta = json.loads((run / "ground_truth" / "metadata.json").read_text(encoding="utf-8"))
    participants = [p["participant_id"] for p in gt_meta.get("participants", [])]
    recorders = [p["participant_id"] for p in gt_meta.get("participants", []) if p.get("record")]
    states = _jsonl(run / "ground_truth" / "states.jsonl")
    frames: Dict[str, List[int]] = defaultdict(list)
    times: Dict[int, float] = {}
    for s in states:
        frames[s["participant_id"]].append(int(s["frame"]))
        times[int(s["frame"])] = float(s["timestamp"])
    all_frames = sorted(times)
    info["frames"] = len(all_frames)
    if sorted(frames) != sorted(participants):
        problems.append("ground truth participants {0} != metadata {1}".format(sorted(frames), participants))
    if all_frames and all_frames[-1] - all_frames[0] + 1 != len(all_frames):
        problems.append("ground truth frames not contiguous")
    steps = [times[b] - times[a] for a, b in zip(all_frames, all_frames[1:])]
    if steps and (max(steps) - dt > 1e-4 or dt - min(steps) > 1e-4):
        problems.append("ground truth step {0:.5f}..{1:.5f} != {2}".format(min(steps), max(steps), dt))
    for pid, fs in frames.items():
        if fs != all_frames:
            problems.append("{0}: {1} ground-truth frames of {2}".format(pid, len(fs), len(all_frames)))
    gt_collisions = {(c["participant_id"], int(c["frame"])) for c in _jsonl(run / "ground_truth" / "collisions.jsonl")}
    info["vehicles"] = {}
    for r in recorders:
        vdir = run / "vehicles" / r
        v: Dict[str, Any] = {}
        for name in ("ego.jsonl", "controls.jsonl", "lights.jsonl"):
            rows = _jsonl(vdir / name)
            got = [int(x["frame"]) for x in rows]
            v[name] = len(got)
            if got != all_frames:
                problems.append("{0}/{1}: frames differ from the ground truth ({2} vs {3})".format(
                    r, name, len(got), len(all_frames)))
        vmeta = json.loads((vdir / "metadata.json").read_text(encoding="utf-8"))
        if (vmeta.get("pose_sensor") or {}).get("profile") != "G0":
            problems.append("{0}: metadata does not declare the G0 pose sensor".format(r))
        if vmeta.get("depth_camera") is not None or (vdir / "depth").exists():
            problems.append("{0}: a depth camera stream exists".format(r))
        radars = load_radar_observations(vdir)
        v["radars"] = {}
        for obs in radars:
            fs = [int(f) for f in obs.frames]
            ts = [float(t) for t in obs.timestamps]
            sid = str(obs.metadata.get("sensor_id"))
            v["radars"][sid] = len(fs)
            if fs != all_frames:
                problems.append("{0}/radar {1}: {2} sweeps for {3} frames".format(r, sid, len(fs), len(all_frames)))
            if any(b <= a for a, b in zip(ts, ts[1:])):
                problems.append("{0}/radar {1}: timestamps not increasing".format(r, sid))
        cam = json.loads((vdir / "camera" / "metadata.json").read_text(encoding="utf-8")) \
            if (vdir / "camera" / "metadata.json").exists() else None
        if cam is None:
            problems.append("{0}: no camera metadata".format(r))
        else:
            stats = cam
            tick = float((vmeta.get("camera") or {}).get("sensor_tick_s", 0.1))
            expected = int(round(len(all_frames) * dt / tick))
            written = stats.get("frames_written")
            v["camera_frames"] = written
            if stats.get("queue_drops") or stats.get("duplicate_callbacks"):
                problems.append("{0}/camera: drops {1}, duplicates {2}".format(
                    r, stats.get("queue_drops"), stats.get("duplicate_callbacks")))
            if written is None or abs(int(written) - expected) > 1:
                problems.append("{0}/camera: {1} frames, {2} expected".format(r, written, expected))
        for c in _jsonl(vdir / "collisions.jsonl"):
            if (r, int(c["frame"])) not in gt_collisions:
                problems.append("{0}: collision at frame {1} missing from the ground truth".format(r, c["frame"]))
        info["vehicles"][r] = v
    info["problems"] = problems
    info["status"] = "PASS" if not problems else "FAIL"
    return info


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    results = []
    for scenario, variants in sorted(CANONICAL.items()):
        for variant in variants:
            run = args.root / scenario / ("run_0_" + variant)
            if not (run / "metadata.json").exists():
                results.append({"run": "{0}/run_0_{1}".format(scenario, variant), "status": "MISSING",
                                "problems": ["not recorded"]})
                continue
            results.append(check_run(run))
    for r in results:
        print("{0:32s} {1}  {2}".format(r["run"], r["status"], "; ".join(r["problems"][:3])))
    passed = sum(r["status"] == "PASS" for r in results)
    print("{0}/{1} runs pass".format(passed, len(results)))
    if args.out:
        args.out.write_text(json.dumps(results, indent=1), encoding="utf-8")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
