#!/usr/bin/env python3
"""Physical reproducibility of repeated CARLA acquisitions of the same scenario.

    python scripts/repro_check.py --runs DIR1 DIR2 [DIR3 ...] [--json out.json]

Each DIR is one run directory (``.../Sxx/run_0_<variant>``) recorded with the same scenario, seed and
configuration.  The first run is the reference.  Only privileged ground truth is read
(``ground_truth/states.jsonl``, ``controls.jsonl``, ``collisions.jsonl``): this checks the simulation,
not the acquisition or the reconstruction.

Frames are aligned on the first recorded frame (absolute frame numbers and actor ids are run-local).
Reported for each repeat against the reference:

* the largest planar position / speed / yaw difference of any participant over the whole run,
  and the first scenario time at which a participant's position differs by more than 1 mm;
* the first time any participant's control input (throttle, brake, steer) differs;
* the collision callback signature: the set of (relative frame, participant, other participant), and
  the contact episodes (callbacks of one pair no more than 2 ticks apart);
* ``late_impact_notifications`` reported by the run metadata (collision callbacks delivered too late for
  the deterministic reaction tick; recordings made before that counter existed report ``None``).

Nothing is tuned to make runs agree: a difference is reported with its time and size.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.is_file():
        return []
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def load_run(run: Path) -> Dict[str, Any]:
    gt = run / "ground_truth"
    states = _jsonl(gt / "states.jsonl")
    if not states:
        raise SystemExit("no ground_truth/states.jsonl in {0}".format(run))
    frame0 = min(int(s["frame"]) for s in states)
    dt = None
    actor_to_pid = {}
    by_pid: Dict[str, Dict[int, Dict[str, float]]] = {}
    for s in states:
        actor_to_pid[int(s["actor_id"])] = s["participant_id"]
        tf, v = s["transform"], s["velocity"]
        by_pid.setdefault(s["participant_id"], {})[int(s["frame"]) - frame0] = {
            "x": float(tf["x"]), "y": float(tf["y"]), "yaw": float(tf["yaw_deg"]),
            "speed": math.hypot(float(v["x"]), float(v["y"])), "t": float(s["timestamp"])}
    frames = sorted(next(iter(by_pid.values())))
    if len(frames) > 1:
        first = next(iter(by_pid.values()))
        dt = first[frames[1]]["t"] - first[frames[0]]["t"]
    controls: Dict[str, Dict[int, Tuple[float, float, float]]] = {}
    for c in _jsonl(gt / "controls.jsonl"):
        controls.setdefault(c["participant_id"], {})[int(c["frame"]) - frame0] = (
            float(c["throttle"]), float(c["brake"]), float(c["steer"]))
    callbacks = set()
    for c in _jsonl(gt / "collisions.jsonl"):
        other = actor_to_pid.get(int(c.get("other_actor_id", -1)), c.get("other_type_id", "static"))
        callbacks.add((int(c["frame"]) - frame0, c["participant_id"], str(other)))
    metadata = {}
    for path in (run / "metadata.json",):
        if path.is_file():
            metadata = json.loads(path.read_text(encoding="utf-8"))
    return {"run": str(run), "states": by_pid, "controls": controls, "callbacks": callbacks,
            "dt": dt or 0.05, "frames": len(frames), "metadata": metadata}


def episodes(callbacks, gap_ticks: int = 2) -> List[Tuple[str, int, int, int]]:
    """Contact episodes of each unordered vehicle pair: (pair, first frame, last frame, callbacks)."""
    per_pair: Dict[str, List[int]] = {}
    for frame, pid, other in callbacks:
        pair = "-".join(sorted((pid, other)))
        per_pair.setdefault(pair, []).append(frame)
    out = []
    for pair, frames in sorted(per_pair.items()):
        frames = sorted(set(frames))
        start = prev = frames[0]; count = 1
        for f in frames[1:]:
            if f - prev > gap_ticks:
                out.append((pair, start, prev, count)); start = f; count = 0
            prev = f; count += 1
        out.append((pair, start, prev, count))
    return out


def compare(ref: Dict[str, Any], rep: Dict[str, Any], tol_m: float = 1e-3) -> Dict[str, Any]:
    dt = ref["dt"]
    worst = {"position_m": 0.0, "speed_mps": 0.0, "yaw_deg": 0.0}
    first_pos = None; per_participant = {}
    missing = sorted(set(ref["states"]) ^ set(rep["states"]))
    for pid in sorted(set(ref["states"]) & set(rep["states"])):
        a, b = ref["states"][pid], rep["states"][pid]
        pmax = 0.0; pfirst = None
        for k in sorted(set(a) & set(b)):
            d = math.hypot(a[k]["x"] - b[k]["x"], a[k]["y"] - b[k]["y"])
            dyaw = abs((a[k]["yaw"] - b[k]["yaw"] + 180.0) % 360.0 - 180.0)
            worst["position_m"] = max(worst["position_m"], d)
            worst["speed_mps"] = max(worst["speed_mps"], abs(a[k]["speed"] - b[k]["speed"]))
            worst["yaw_deg"] = max(worst["yaw_deg"], dyaw)
            pmax = max(pmax, d)
            if d > tol_m and pfirst is None:
                pfirst = k * dt
        per_participant[pid] = {"max_position_diff_m": pmax, "first_divergence_s": pfirst}
        if pfirst is not None and (first_pos is None or pfirst < first_pos):
            first_pos = pfirst
    first_control = None
    for pid in sorted(set(ref["controls"]) & set(rep["controls"])):
        a, b = ref["controls"][pid], rep["controls"][pid]
        for k in sorted(set(a) & set(b)):
            if any(abs(x - y) > 1e-9 for x, y in zip(a[k], b[k])):
                t = k * dt
                if first_control is None or t < first_control[0]:
                    first_control = (t, pid)
                break
    ep_ref, ep_rep = episodes(ref["callbacks"]), episodes(rep["callbacks"])
    return {
        "run": rep["run"], "frames_ref": ref["frames"], "frames_rep": rep["frames"],
        "participants_mismatch": missing,
        "max_position_diff_m": worst["position_m"], "max_speed_diff_mps": worst["speed_mps"],
        "max_yaw_diff_deg": worst["yaw_deg"], "first_position_divergence_s": first_pos,
        "first_control_divergence": None if first_control is None else
        {"t_s": first_control[0], "participant": first_control[1]},
        "per_participant": per_participant,
        "collision_callbacks_identical": ref["callbacks"] == rep["callbacks"],
        "collision_callbacks_ref": len(ref["callbacks"]), "collision_callbacks_rep": len(rep["callbacks"]),
        "contact_episodes_identical": ep_ref == ep_rep,
        "contact_episodes_ref": [[p, s * dt, e * dt, n] for p, s, e, n in ep_ref],
        "contact_episodes_rep": [[p, s * dt, e * dt, n] for p, s, e, n in ep_rep],
        "late_impact_notifications": rep["metadata"].get("late_impact_notifications"),
        "bitwise_identical_states": worst["position_m"] == 0.0 and worst["speed_mps"] == 0.0
        and worst["yaw_deg"] == 0.0 and ref["frames"] == rep["frames"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--runs", nargs="+", type=Path, required=True)
    parser.add_argument("--json", type=Path, default=None)
    args = parser.parse_args()
    runs = [load_run(r) for r in args.runs]
    ref = runs[0]
    rows = [compare(ref, rep) for rep in runs[1:]]
    report = {"reference": ref["run"], "reference_late_impact_notifications":
              ref["metadata"].get("late_impact_notifications"), "repeats": rows}
    text = json.dumps(report, indent=2)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(text, encoding="utf-8")
    for r in rows:
        print("{0}: max pos {1:.4f} m, speed {2:.4f} m/s, first div {3}, control div {4}, callbacks identical {5}, "
              "episodes identical {6}, bitwise {7}".format(
                  Path(r["run"]).parent.parent.name + "/" + Path(r["run"]).name, r["max_position_diff_m"],
                  r["max_speed_diff_mps"], r["first_position_divergence_s"], r["first_control_divergence"],
                  r["collision_callbacks_identical"], r["contact_episodes_identical"],
                  r["bitwise_identical_states"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
