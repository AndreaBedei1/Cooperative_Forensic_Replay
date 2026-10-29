#!/usr/bin/env python3
"""Privileged sanity check of a recorded scenario run (ground truth; evaluation of the SCENARIO, not of the
reconstruction): vehicles, contacts, closest approaches, accelerations, cars standing on the carriageway.

    python scripts/check_scenario_run.py <run dir> [--expect A-B]
"""
import argparse
import json
import math
from collections import defaultdict
from itertools import combinations
from pathlib import Path


def rows(path):
    p = Path(path)
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []


def box_gap(a, b):
    """Approximate gap between two oriented boxes (sampled outline of a against box of b)."""
    def corners(s):
        t, e = s["transform"], s["bbox_extent"]
        yaw = math.radians(t["yaw_deg"]); c, sn = math.cos(yaw), math.sin(yaw)
        pts = []
        for i in range(21):
            u = -1 + 2 * i / 20
            for x, y in ((u * e["x"], e["y"]), (u * e["x"], -e["y"]), (e["x"], u * e["y"]), (-e["x"], u * e["y"])):
                pts.append((t["x"] + c * x - sn * y, t["y"] + sn * x + c * y))
        return pts

    def inside_dist(p, s):
        t, e = s["transform"], s["bbox_extent"]
        yaw = math.radians(t["yaw_deg"]); dx, dy = p[0] - t["x"], p[1] - t["y"]
        lx, ly = math.cos(yaw) * dx + math.sin(yaw) * dy, -math.sin(yaw) * dx + math.cos(yaw) * dy
        return math.hypot(max(abs(lx) - e["x"], 0), max(abs(ly) - e["y"], 0))
    return min(min(inside_dist(p, b) for p in corners(a)), min(inside_dist(p, a) for p in corners(b)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    parser.add_argument("--expect", default=None, help="the intended contact, e.g. A-B")
    args = parser.parse_args()
    run = args.run
    meta = json.loads((run / "metadata.json").read_text(encoding="utf-8"))
    states = rows(run / "ground_truth" / "states.jsonl")
    frames = defaultdict(dict)
    for s in states:
        frames[s["frame"]][s["participant_id"]] = s
    order = sorted(frames)
    t0 = frames[order[0]][next(iter(frames[order[0]]))]["timestamp"]
    ids = sorted({p for f in frames.values() for p in f})
    recorders = sorted(p.name for p in (run / "vehicles").iterdir() if p.is_dir())
    contacts = rows(run / "ground_truth" / "collisions.jsonl")
    actor = {s["actor_id"]: s["participant_id"] for s in states}
    pairs = defaultdict(list)
    for c in contacts:
        a = c.get("participant_id") or actor.get(c.get("actor_id"))
        b = c.get("other_participant_id") or actor.get(c.get("other_actor_id"))
        key = "-".join(sorted([str(a), str(b)]))
        pairs[key].append(round(c["timestamp"] - t0, 2))
    print("run", run, "| map", meta.get("map"), "| vehicles", len(ids), ids, "| recorders", recorders)
    print("contacts (ground truth):", {k: (v[0], len(v)) for k, v in sorted(pairs.items())})
    if args.expect:
        bad = [k for k in pairs if k != "-".join(sorted(args.expect.split("-")))]
        print("EXPECTED", args.expect, "present" if "-".join(sorted(args.expect.split("-"))) in pairs else "MISSING",
              "| other contacts:", bad or "none")
    closest = {}
    for f in order[::4]:
        fr = frames[f]
        for a, b in combinations(sorted(fr), 2):
            g = box_gap(fr[a], fr[b])
            if g < closest.get((a, b), (1e9,))[0]:
                closest[(a, b)] = (round(g, 2), round(fr[a]["timestamp"] - t0, 2))
    near = sorted((v, k) for k, v in closest.items() if v[0] < 1.5)
    print("closest approaches < 1.5 m:", [(f"{a}-{b}", g, t) for (g, t), (a, b) in near])
    accel, stopped = {}, defaultdict(float)
    for p in ids:
        seq = [frames[f][p] for f in order if p in frames[f]]
        for s0, s1 in zip(seq, seq[1:]):
            dt = s1["timestamp"] - s0["timestamp"]
            if dt <= 0:
                continue
            a = math.hypot(s1["velocity"]["x"] - s0["velocity"]["x"], s1["velocity"]["y"] - s0["velocity"]["y"]) / dt
            accel[p] = max(accel.get(p, 0.0), a)
            if math.hypot(s1["velocity"]["x"], s1["velocity"]["y"]) < 0.5:
                stopped[p] += dt
    print("max |dv|/dt [m/s^2]:", {p: round(v, 1) for p, v in sorted(accel.items())})
    print("time standing (< 0.5 m/s) [s]:", {p: round(v, 1) for p, v in sorted(stopped.items()) if v > 0})
    print("duration [s]:", round(frames[order[-1]][next(iter(frames[order[-1]]))]["timestamp"] - t0, 2))


if __name__ == "__main__":
    main()
