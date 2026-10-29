#!/usr/bin/env python3
"""Side-by-side review frames of a reconstructed run: reconstruction-only replay (left) and ground truth (right,
EVALUATION ONLY: true vehicle boxes and names, for a human to check the scenario and the reconstruction).

    python scripts/review_frames.py <reconstructed run> --at "label=t" ... --out <dir>

t is the displayed time (t_global, 0 = the reconstructed collision); the ground-truth panel is drawn at the
true first contact + t.  Lanes from the public OpenDRIVE file (``cdf.replay.opendrive``).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Polygon  # noqa: E402
from PIL import Image  # noqa: E402

from cdf.replay.model import ReplayRun  # noqa: E402


def rows(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def truth_panel(run_dir: Path, t_display: float, lanes, out: Path, label: str) -> None:
    states = rows(run_dir / "ground_truth" / "states.jsonl")
    contacts = rows(run_dir / "ground_truth" / "collisions.jsonl")
    t0 = min(s["timestamp"] for s in states)
    t_contact = min(c["timestamp"] for c in contacts) if contacts else t0
    target = t_contact + t_display
    recorders = sorted(p.name for p in (run_dir / "vehicles").iterdir() if p.is_dir())
    nearest = {}
    for s in states:
        pid = s["participant_id"]
        if pid not in nearest or abs(s["timestamp"] - target) < abs(nearest[pid]["timestamp"] - target):
            nearest[pid] = s
    xs = [nearest[r]["transform"]["x"] for r in recorders if r in nearest]
    ys = [nearest[r]["transform"]["y"] for r in recorders if r in nearest]
    cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
    half = 45.0
    fig, ax = plt.subplots(figsize=(7.5, 7.5), dpi=110)
    for lane in lanes or []:
        if abs(lane.x - cx) > half + 10 or abs(lane.y - cy) > half + 10:
            continue
        yaw = math.radians(lane.yaw)
        f, r = (math.cos(yaw), math.sin(yaw)), (-math.sin(yaw), math.cos(yaw))
        pts = [(lane.x + a * f[0] * lane.length / 2 + b * r[0] * lane.width / 2,
                lane.y + a * f[1] * lane.length / 2 + b * r[1] * lane.width / 2) for a, b in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
        ax.add_patch(Polygon(pts, closed=True, facecolor="#d9d9d9", edgecolor="none"))
    colours = {"A": "#1f77b4", "B": "#ff7f0e", "C": "#2ca02c"}
    for pid, s in sorted(nearest.items()):
        t, e = s["transform"], s["bbox_extent"]
        yaw = math.radians(t["yaw_deg"])
        c, sn = math.cos(yaw), math.sin(yaw)
        pts = [(t["x"] + c * a * e["x"] - sn * b * e["y"], t["y"] + sn * a * e["x"] + c * b * e["y"])
               for a, b in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
        rec = pid in recorders
        ax.add_patch(Polygon(pts, closed=True, facecolor=colours.get(pid, "#555555") if rec else "#bbbbbb",
                             edgecolor="black", linewidth=1.2 if rec else 0.8))
        ax.annotate("", xy=(t["x"] + c * e["x"] * 1.4, t["y"] + sn * e["x"] * 1.4), xytext=(t["x"], t["y"]),
                    arrowprops=dict(arrowstyle="->", lw=0.8))
        ax.text(t["x"], t["y"], pid, ha="center", va="center", fontsize=8, weight="bold",
                color="white" if rec else "black")
    ax.set_xlim(cx - half, cx + half)
    ax.set_ylim(cy + half, cy - half)  # CARLA y points to the right of x: flip to look from above
    ax.set_aspect("equal")
    ax.set_title("GROUND TRUTH (evaluation only)  t = {0:+.2f} s  {1}".format(t_display, label), fontsize=9)
    ax.tick_params(labelsize=6)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("run", type=Path)
    parser.add_argument("--at", action="append", default=[], help='"label=t" (displayed time)')
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("replay_run", str(ROOT / "scripts" / "replay_run.py"))
    viewer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(viewer)
    run = ReplayRun.load(args.run)
    _, lanes = viewer.export_lanes(run)
    pairs = [(item.split("=")[0], float(item.split("=")[1])) for item in args.at]
    offset = run.display_time(0.0)
    from cdf.replay.topdown import export_keyframes
    args.out.mkdir(parents=True, exist_ok=True)
    frames = export_keyframes(run, args.out, lanes=lanes, times=[(label, t - offset) for label, t in pairs])
    for (label, t), frame in zip(pairs, frames):
        left = args.out / frame["file"]
        right = args.out / ("gt_" + frame["file"])
        truth_panel(args.run, t, lanes, right, label)
        a, b = Image.open(left).convert("RGB"), Image.open(right).convert("RGB")
        h = max(a.height, b.height)
        b = b.resize((int(b.width * h / b.height), h))
        sheet = Image.new("RGB", (a.width + b.width, h), "white")
        sheet.paste(a, (0, 0))
        sheet.paste(b, (a.width, 0))
        sheet.save(args.out / ("pair_" + frame["file"]))
        right.unlink()
        left.unlink()
    print(args.out, len(frames), "frames")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
