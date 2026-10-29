#!/usr/bin/env python3
"""Privileged summary of a scenario run and of its offline counterfactual runs (S12 worked example).

    python scripts/run_scenario.py --scenario S12 --variant crash --seed 0 --output <scratch>/without_C \
        --no-autostart --override simulation.port=3000 --override simulation.traffic_manager_port=8100 \
        --without-participant C
    python scripts/run_scenario.py ... --output <scratch>/swerve_disabled --disable-action A_evasive_swerve_left
    python scripts/counterfactuals.py traces/S12/run_0_crash without_C=<scratch>/without_C/<run> \
        swerve_disabled=<scratch>/swerve_disabled/<run>

PRIVILEGED: reads only ``ground_truth/`` of each run and writes ``<factual run>/ground_truth/counterfactuals.json``
(read by ``cdf.evaluation.worked_example``, never by the reconstruction).  Per run: the participants, the
recorded duration, the scripted triggers that fired, the smallest gap between the true boxes of each pair of
vehicles (and when, seconds from the run's first ground-truth state) and the vehicle-vehicle contacts per pair
(first and last callback, peak impulse).  Box gaps use the true footprints (centred on the vehicle origin) and
``cdf.reconstruction.common_frame.footprint_gap`` (about 0.05 m resolution).
"""

from __future__ import annotations

import itertools
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cdf.reconstruction.common_frame import WorldPose, footprint_gap  # noqa: E402
from cdf.reconstruction.tracking import EgoFootprint  # noqa: E402

NOTICE = ("PRIVILEGED - NOT ADMISSIBLE INPUT. Simulator ground truth of offline counterfactual runs; never read by "
          "the reconstruction, never given to an LLM.")


def _jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def run_summary(run_dir: Path) -> Dict[str, Any]:
    gt = Path(run_dir) / "ground_truth"
    states = _jsonl(gt / "states.jsonl")
    start = min(float(s["timestamp"]) for s in states)
    actors = {int(s["actor_id"]): str(s["participant_id"]) for s in states}
    metadata = json.loads((gt / "metadata.json").read_text(encoding="utf-8"))
    participants = [str(p["participant_id"]) for p in metadata.get("participants", [])] or sorted(set(actors.values()))
    by_time: Dict[float, Dict[str, Dict[str, Any]]] = defaultdict(dict)
    for s in states:
        by_time[round(float(s["timestamp"]), 4)][str(s["participant_id"])] = s

    def pose_box(state: Dict[str, Any]):
        t, e = state["transform"], state["bbox_extent"]
        return (WorldPose(float(t["x"]), float(t["y"]), math.radians(float(t["yaw_deg"]))),
                EgoFootprint(-float(e["x"]), float(e["x"]), -float(e["y"]), float(e["y"])))

    gaps: Dict[str, Dict[str, float]] = {}
    for stamp in sorted(by_time):
        world = by_time[stamp]
        for a, b in itertools.combinations(sorted(world), 2):
            gap = max(0.0, footprint_gap(*pose_box(world[a]), *pose_box(world[b])))
            key = "{0}-{1}".format(a, b)
            if key not in gaps or gap < gaps[key]["min_box_gap_m"]:
                gaps[key] = {"at_s": round(stamp - start, 2), "min_box_gap_m": round(gap, 2)}
    contacts: Dict[str, Dict[str, float]] = {}
    for row in _jsonl(gt / "collisions.jsonl"):
        other = actors.get(int(row["other_actor_id"]))
        if other is None:  # not a vehicle of the scenario (a prop, the road...)
            continue
        key = "-".join(sorted((str(row["participant_id"]), other)))
        t, impulse = round(float(row["timestamp"]) - start, 2), float(row["impulse"])
        entry = contacts.setdefault(key, {"first_s": t, "last_s": t, "peak_impulse_Ns": impulse})
        entry["first_s"], entry["last_s"] = min(entry["first_s"], t), max(entry["last_s"], t)
        entry["peak_impulse_Ns"] = round(max(entry["peak_impulse_Ns"], impulse), 1)
    triggers = [{key: row[key] for key in ("action_id", "participant_id", "t_scenario", "action_t_start", "measured")
                 if key in row} for row in _jsonl(gt / "triggers.jsonl")]
    summary = {"participants": participants,
               "recorded_duration_s": round(max(float(s["timestamp"]) for s in states) - start, 2),
               "triggers_fired": triggers, "box_gaps": gaps, "collisions": contacts}
    # Each vehicle's largest lateral departure, to its left and to its right, from the straight line of its first
    # state (CARLA axes: y to the right of the heading).
    first: Dict[str, Dict[str, Any]] = {}
    departures: Dict[str, List[float]] = defaultdict(lambda: [0.0, 0.0])
    for stamp in sorted(by_time):
        for pid, state in by_time[stamp].items():
            origin = first.setdefault(pid, state)["transform"]
            yaw = math.radians(float(origin["yaw_deg"]))
            dx = float(state["transform"]["x"]) - float(origin["x"])
            dy = float(state["transform"]["y"]) - float(origin["y"])
            lateral = -math.sin(yaw) * dx + math.cos(yaw) * dy
            departures[pid][0] = max(departures[pid][0], -lateral)
            departures[pid][1] = max(departures[pid][1], lateral)
    for pid, (left, right) in sorted(departures.items()):
        summary["{0}_max_left_departure_m".format(pid)] = round(left, 2)
        summary["{0}_max_right_departure_m".format(pid)] = round(right, 2)
    return summary


def main(argv: List[str]) -> int:
    if len(argv) < 1:
        print(__doc__)
        return 2
    factual = Path(argv[0])
    record: Dict[str, Any] = {"_notice": NOTICE, "scenario": "{0} {1}".format(factual.parent.name, factual.name),
                              "factual": run_summary(factual), "counterfactuals": {}}
    for item in argv[1:]:
        name, path = item.split("=", 1)
        summary = run_summary(Path(path))
        marker = Path(path) / "ground_truth" / "counterfactual.json"
        if marker.exists():
            summary["counterfactual"] = json.loads(marker.read_text(encoding="utf-8"))
        record["counterfactuals"][name] = summary
    out = factual / "ground_truth" / "counterfactuals.json"
    out.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
