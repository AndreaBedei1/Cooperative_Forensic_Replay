#!/usr/bin/env python3
"""Privileged scenario check (ground truth; the SCENARIO, not the reconstruction): how much traffic surrounds
the recorders before the first contact.

    python scripts/scenario_density.py traces/S14/run_0_surrounded ... [--out results/.../density.md]

Per run, over the time before the first vehicle contact (10 Hz): non-recorder vehicles within 15 / 30 / 50 m of
any recorder (mean and max), by position relative to the nearest recorder in its own frame (ahead / behind /
alongside: within a car length longitudinally, beside it), the closest approach of a non-recorder to a recorder,
the vehicles that go from far (> 40 m) to near (< 20 m), and those never within 50 m.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path


def rows(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def analyse(run: Path):
    states = rows(run / "ground_truth" / "states.jsonl")
    contacts = rows(run / "ground_truth" / "collisions.jsonl")
    recorders = sorted(p.name for p in (run / "vehicles").iterdir() if p.is_dir())
    frames = defaultdict(dict)
    for s in states:
        frames[s["frame"]][s["participant_id"]] = s
    order = sorted(frames)
    t0 = min(s["timestamp"] for s in states)
    t_contact = min(c["timestamp"] for c in contacts) if contacts else max(s["timestamp"] for s in states)
    others = sorted({s["participant_id"] for s in states} - set(recorders))
    counts = {15: [], 30: [], 50: []}
    rel = defaultdict(int)
    closest = math.inf
    first_far, near_after_far, ever_within = {}, set(), set()
    step = max(1, len(order) // int((t_contact - t0) * 10 + 1)) if t_contact > t0 else 1
    for f in order[::step]:
        fr = frames[f]
        any_rec = next(iter(fr.values()))
        if any_rec["timestamp"] > t_contact:
            break
        for radius in counts:
            counts[radius].append(0)
        for o in others:
            if o not in fr:
                continue
            best, best_rec = math.inf, None
            for r in recorders:
                if r not in fr:
                    continue
                d = math.hypot(fr[o]["transform"]["x"] - fr[r]["transform"]["x"], fr[o]["transform"]["y"] - fr[r]["transform"]["y"])
                if d < best:
                    best, best_rec = d, r
            if best_rec is None:
                continue
            for radius in counts:
                if best <= radius:
                    counts[radius][-1] += 1
            closest = min(closest, best)
            if best <= 50:
                ever_within.add(o)
            if best > 40:
                first_far.setdefault(o, fr[o]["timestamp"])
            elif best < 20 and o in first_far:
                near_after_far.add(o)
            if best <= 30:
                rt = fr[best_rec]["transform"]
                yaw = math.radians(rt["yaw_deg"])
                dx, dy = fr[o]["transform"]["x"] - rt["x"], fr[o]["transform"]["y"] - rt["y"]
                along, across = math.cos(yaw) * dx + math.sin(yaw) * dy, -math.sin(yaw) * dx + math.cos(yaw) * dy
                rel["alongside" if abs(along) <= 4.6 and abs(across) > 1.5 else "ahead" if along > 0 else "behind"] += 1
    n = max(len(counts[15]), 1)
    total = sum(rel.values()) or 1
    return {"run": "{0}/{1}".format(run.parent.name, run.name), "vehicles": len(others) + len(recorders),
            "recorders": recorders, "seconds_before_contact": round(t_contact - t0, 2),
            "within_15m": (round(sum(counts[15]) / n, 2), max(counts[15] or [0])),
            "within_30m": (round(sum(counts[30]) / n, 2), max(counts[30] or [0])),
            "within_50m": (round(sum(counts[50]) / n, 2), max(counts[50] or [0])),
            "relative_within_30m": {k: round(v / total, 2) for k, v in sorted(rel.items())},
            "closest_m": round(closest, 1), "far_to_near": sorted(near_after_far),
            "never_within_50m": sorted(set(others) - ever_within)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("runs", nargs="+", type=Path)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    lines = ["| run | vehicles | recorders | s before contact | within 15 m mean/max | within 30 m mean/max | "
             "within 50 m mean/max | relative position (within 30 m) | closest non-recorder [m] | far -> near | "
             "never within 50 m |", "|---|--:|---|--:|---|---|---|---|--:|---|---|"]
    for run in args.runs:
        r = analyse(run)
        lines.append("| {run} | {vehicles} | {rec} | {seconds_before_contact} | {a[0]} / {a[1]} | {b[0]} / {b[1]} | "
                     "{c[0]} / {c[1]} | {rel} | {closest_m} | {fn} | {nv} |".format(
                         **r, rec=",".join(r["recorders"]), a=r["within_15m"], b=r["within_30m"], c=r["within_50m"],
                         rel=", ".join("{0} {1:.0%}".format(k, v) for k, v in r["relative_within_30m"].items()),
                         fn=",".join(r["far_to_near"]) or "-", nv=",".join(r["never_within_50m"]) or "-"))
    text = "\n".join(lines) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
