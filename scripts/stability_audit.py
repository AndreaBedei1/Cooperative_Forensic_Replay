#!/usr/bin/env python3
"""Stability audit of the reconstruction (PRIVILEGED evaluation: ground truth is read here only).

    python scripts/stability_audit.py [runs ...] [--json out.json] [--md out.md]

The acceptance validator (``validate_canonical.py``) checks collisions, identities and the replay; it does not see
whether the local semantic trace is temporally coherent.  This audit measures, per run and recorder, what a
reviewer sees in the replay, against ground truth and against physical plausibility, without re-using the
reconstruction's own semantic definitions where they could hide their own defects:

* TRACKS: confirmed local tracks (segments included), births and losses; every TRACK_LOST is classified with
  ground truth: the true road user still covered by the recorder's radars over the next 0.5 s ("fragmentation",
  a tracker decision) or not ("visibility loss", a sensing fact); tracks on no true vehicle ("phantom"); two
  simultaneous tracks of one recorder on the same true road user ("duplicate", seconds of overlap).
* EGO_PATH: ENTRY / EXIT per (recorder, true road user), merged over all its tracks; transitions undone within
  ``SHORT_S`` (three radar sweeps), which no vehicle manoeuvre produces ("oscillation").
* REFERENCE PATH continuity: the path frame of the recorder's corridor at probe points 10 / 20 / 30 m straight
  ahead; a lateral jump of more than ``PATH_JUMP_M`` between consecutive sweeps is a discontinuity of the
  reference path itself (the recorder moves ~0.6 m per sweep).
* CUT_IN against an independent truth (ground-truth poses and boxes, the map's lanes): the target moves across
  ITS lane toward the recorder by at least ``CUT_TRUE_M`` within 3 s (its own manoeuvre, whatever the recorder
  does), and within 3 s of the onset its body enters the recorder's corridor (``path_half_width_m`` either side
  of the recorder's centre line) ahead of the recorder's front edge, from outside it -- also when contact ends
  the manoeuvre there.  True positives, false positives, misses and onset errors.
* CRITICAL_TTC: episodes per (recorder, true road user); the collision closure (no same-pair episode starting
  after their contact while touching).
* TRAJECTORY: implausible jumps of local track positions between consecutive samples (implied acceleration above
  ``JUMP_ACCEL_MPS2`` away from the recorder's own collisions).
* FUSION: wrong recorder links, false / missed merges (``fusion_metrics``).
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]

from cdf.evaluation.event_oracle import _to_local, prepare_truth  # noqa: E402
from cdf.evaluation.visibility import frames_by_participant  # noqa: E402
from cdf.reconstruction.config import load_config  # noqa: E402
from cdf.reconstruction.local import read_jsonl  # noqa: E402
from cdf.reconstruction.pipeline import read_incident_context  # noqa: E402
from cdf.reconstruction.road import RoadFrame, road_for_positions  # noqa: E402
from cdf.reconstruction.tracking import RadarMount, RadarStream, ego_trajectory, radar_sweeps  # noqa: E402
from cdf.recording.compact_observations import load_radar_observations  # noqa: E402

SHORT_S = 0.15  # an ENTRY/EXIT undone within three 20 Hz sweeps
LOSS_LOOKAHEAD_S = 0.5
PATH_JUMP_M = 1.0
CUT_TRUE_M = 1.5
JUMP_ACCEL_MPS2 = 40.0


def canonical_runs():
    from validate_canonical import canonical_runs as runs
    return runs()


def _events(run, owner):
    path = run / "reconstruction" / owner / "local_graph.json"
    return json.loads(path.read_text(encoding="utf-8"))["nodes"] if path.exists() else []


def _tracks(run, owner):
    out = defaultdict(list)
    path = run / "reconstruction" / owner / "local_tracks.jsonl"
    if path.exists():
        for row in read_jsonl(path):
            out[row["track_id"]].append(row)
    return out


def _identities(run):
    path = run / "reconstruction" / "evaluation" / "fusion_metrics.json"
    if not path.exists():
        return {}, {}
    fm = json.loads(path.read_text(encoding="utf-8"))
    return {d["track"]: d.get("true_identity") for d in fm["track_decisions"]}, fm


def _visible(truth, owner, target, t0, t1):
    entry = truth["ideal"].get(owner, {}).get(target)
    if entry is None:
        return 0.0
    flags = [v for s, v in zip(entry["samples"], entry["visible"]) if t0 < s.t_local <= t1 + 1e-9]
    return sum(flags) / len(flags) if flags else 0.0


def body_returns(run, owner, truth, frames):
    """(sweep times, {target: returns on its true body per sweep}) of one recorder: the raw evidence a tracker
    had (box grown by 0.5 m), independent of any tracker decision."""
    rec = truth["recorders"].get(owner)
    vehicle_dir = run / "vehicles" / owner
    if rec is None or not (vehicle_dir / "radar").exists():
        return [], {}
    cfg = load_config()
    streams = [RadarStream(RadarMount.from_metadata(o.metadata), o) for o in load_radar_observations(vehicle_dir)]
    sweeps = radar_sweeps(streams, rec.ego, rec.clock_origin, cfg.tracking, rec.footprint)
    frame_of = {round(t, 4): f for f, t in rec.sweeps}
    counts = defaultdict(list)
    times = []
    for sweep in sweeps:
        times.append(sweep.t_local)
        world = frames.get(frame_of.get(round(sweep.t_local, 4)), {})
        for target, state in world.items():
            if target == owner:
                continue
            tf, ext = state["transform"], state["bbox_extent"]
            centre = _to_local(rec, tf["x"], tf["y"])
            h = math.radians(tf["yaw_deg"]) - rec.origin[2]
            rel = sweep.points - centre
            along = rel @ np.array([math.cos(h), math.sin(h)])
            across = rel @ np.array([-math.sin(h), math.cos(h)])
            while len(counts[target]) < len(times) - 1:
                counts[target].append(0)
            counts[target].append(int(((np.abs(along) <= ext["x"] + 0.5) & (np.abs(across) <= ext["y"] + 0.5)).sum()))
    for target in counts:
        while len(counts[target]) < len(times):
            counts[target].append(0)
    return times, counts


def _support(times, counts, target, t0, t1):
    """Share of the sweeps in (t0, t1] with at least one return on the target's true body."""
    values = [c for t, c in zip(times, counts.get(target, [])) if t0 < t <= t1 + 1e-9]
    return sum(1 for c in values if c > 0) / len(values) if values else 0.0


def track_metrics(run, owner, truth, identity, evidence):
    times, counts = evidence
    tracks = _tracks(run, owner)
    nodes = _events(run, owner)
    spans = {k: (rows[0]["t_local"], rows[-1]["t_local"]) for k, rows in tracks.items()}
    ident = {k: identity.get(owner + ":" + k) for k in tracks}
    losses = []
    for n in nodes:
        if n["event_type"] != "TRACK_LOST":
            continue
        k, t = n["subject_id"], n["t_local"]
        v = ident.get(k)
        if v is None:
            losses.append({"track": k, "t": t, "kind": "phantom"})
            continue
        share = _visible(truth, owner, v, t, t + LOSS_LOOKAHEAD_S)
        support = _support(times, counts, v, t, t + LOSS_LOOKAHEAD_S)
        later = [o for o, (a, _) in spans.items() if o != k and ident.get(o) == v and t - 1e-6 <= a <= t + 2.0]
        # A tracker decision when the radar kept measuring the body; sparse returns when it did only now and
        # then; a sensing fact when it measured nothing on it.
        kind = ("fragmentation" if support >= 0.5 else "sparse returns" if support > 0.0 else "visibility loss")
        losses.append({"track": k, "t": t, "true": v, "kind": kind, "visible_after": round(share, 2),
                       "returns_after": round(support, 2), "reacquired_as": later})
    phantoms = [{"track": k, "from": a, "to": b, "duration_s": round(b - a, 2)}
                for k, (a, b) in spans.items() if ident.get(k) is None]
    by_true = defaultdict(list)
    for k, v in ident.items():
        if v is not None:
            by_true[v].append(k)
    duplicates = []
    for v, ks in by_true.items():
        for i, a in enumerate(ks):
            for b in ks[i + 1:]:
                lo, hi = max(spans[a][0], spans[b][0]), min(spans[a][1], spans[b][1])
                if hi - lo > 0.1:
                    duplicates.append({"true": v, "tracks": [a, b], "overlap_s": round(hi - lo, 2)})
    births = sum(1 for n in nodes if n["event_type"].startswith("TRACK_APPEARED"))
    return {"tracks": len(tracks), "births": births, "losses": losses, "phantoms": phantoms,
            "duplicates": duplicates, "tracks_per_true": {v: len(ks) for v, ks in sorted(by_true.items())}}


def path_metrics(run, owner, identity):
    nodes = _events(run, owner)
    per = defaultdict(list)
    for n in nodes:
        if n["event_type"] in ("EGO_PATH_ENTRY", "EGO_PATH_EXIT"):
            v = identity.get(owner + ":" + str(n["subject_id"])) or ("?" + str(n["subject_id"]))
            per[v].append((n["t_local"], n["event_type"], n["subject_id"]))
    out = {}
    for v, events in per.items():
        events.sort()
        short = sum(1 for (t0, e0, _), (t1, e1, _) in zip(events, events[1:]) if e0 != e1 and t1 - t0 <= SHORT_S + 1e-6)
        out[v] = {"entries": sum(1 for e in events if e[1] == "EGO_PATH_ENTRY"),
                  "exits": sum(1 for e in events if e[1] == "EGO_PATH_EXIT"), "oscillations": short,
                  "tracks": sorted({str(e[2]) for e in events})}
    return out


def reference_path_jumps(run, owner):
    """Discontinuities of the reference path itself: the previous sweep's path points 10 / 20 / 30 m ahead of
    the recorder (world frame) against the new path; a lateral distance beyond ``PATH_JUMP_M`` is a jump (a
    recorder's rotation does not count: the points are on the path, not fixed to the vehicle).  A jump undone
    within 1 s is a flip-flop (an independent per-sweep lane choice), the others are lane switches."""
    records = read_jsonl(run / "vehicles" / owner / "ego.jsonl")
    ego = ego_trajectory(records, float(records[0]["timestamp"]))
    road = RoadFrame.from_ego_records(records, map_name=read_incident_context(run).get("map"))
    if road is None:
        return {"road": None}
    jumps, previous, t, checked = [], None, ego.start, 0
    while t <= ego.end + 1e-9:
        state = road.path_at(ego, t)
        if state is not None and previous is not None:
            old_path, old_s0 = previous
            probes = []
            for ahead in (10.0, 20.0, 30.0):
                s = old_s0 + ahead
                if s <= old_path.cumulative[-1]:
                    k = int(np.clip(np.searchsorted(old_path.cumulative, s), 1, len(old_path.points) - 1))
                    f = (s - old_path.cumulative[k - 1]) / max(old_path.lengths[k - 1], 1e-9)
                    probes.append(old_path.points[k - 1] + f * (old_path.points[k] - old_path.points[k - 1]))
            if probes:
                checked += 1
                lateral = np.abs(state[0].project(np.array(probes))[:, 1])
                if float(np.max(lateral)) > PATH_JUMP_M:
                    jumps.append((round(t, 2), round(float(np.max(lateral)), 2)))
        previous = None if state is None else (state[0], state[1])
        t = round(t + 0.05, 4)
    flips = sum(1 for (a, _), (b, _) in zip(jumps, jumps[1:]) if b - a <= 1.0)
    return {"road": road.road.name, "checked": checked, "jumps": len(jumps), "flip_flops": flips,
            "examples": jumps[:6]}


def _lane_toward(road, states, v, r, t):
    """V's lane-relative lateral velocity toward R at simulator time t (world frame; None off lanes)."""
    sv, sr = states[v], states[r]
    k = int(np.argmin(np.abs(sv["t"] - t)))
    j = int(np.argmin(np.abs(sr["t"] - t)))
    x, y, vx, vy = sv["x"][k], sv["y"][k], sv["vx"][k], sv["vy"][k]
    if math.hypot(vx, vy) < 1.0:
        return None
    h = road.direction(x, y)
    if h is None:
        return None
    dx, dy = math.cos(h), math.sin(h)
    if vx * dx + vy * dy < 0:
        dx, dy = -dx, -dy
    nx, ny = -dy, dx
    side = (sr["x"][j] - x) * nx + (sr["y"][j] - y) * ny
    return (vx * nx + vy * ny) * (1.0 if side > 0 else -1.0)


def cut_in_truth(run, recorders, footprints):
    """(recorder, target, onset simulator time) of every true cut-in (module docstring)."""
    rows = read_jsonl(run / "ground_truth" / "states.jsonl")
    states = defaultdict(lambda: defaultdict(list))
    for r in rows:
        s = states[r["participant_id"]]
        s["t"].append(r["timestamp"])
        s["x"].append(r["transform"]["x"])
        s["y"].append(r["transform"]["y"])
        s["yaw"].append(math.radians(r["transform"]["yaw_deg"]))
        s["vx"].append(r["velocity"]["x"])
        s["vy"].append(r["velocity"]["y"])
        s["ext"] = [(r["bbox_extent"]["x"], r["bbox_extent"]["y"])]
    states = {p: {k: np.array(v) for k, v in s.items()} for p, s in states.items()}
    half = load_config().semantics.path_half_width_m

    def in_corridor(r, v, u, front):
        """V's ground-truth body ahead of R's front edge and overlapping R's corridor at simulator time u."""
        sr, sv = states[r], states[v]
        xr, yr, hr = (float(np.interp(u, sr["t"], sr[k])) for k in ("x", "y", "yaw"))
        xv, yv, hv = (float(np.interp(u, sv["t"], sv[k])) for k in ("x", "y", "yaw"))
        ex, ey = sv["ext"][0]
        corners = np.array([[xv + math.cos(hv) * a - math.sin(hv) * b, yv + math.sin(hv) * a + math.cos(hv) * b]
                            for a in (-ex, ex) for b in (-ey, ey)]) - np.array([xr, yr])
        along = corners @ np.array([math.cos(hr), math.sin(hr)])
        across = corners @ np.array([-math.sin(hr), math.cos(hr)])
        return float(along.max()) > front and min(float(across.max()), half) - max(float(across.min()), -half) > 0
    road = road_for_positions([(float(x), float(y)) for s in states.values() for x, y in zip(s["x"][::20], s["y"][::20])])
    if road is None:
        return [], None
    truth = []
    for r in recorders:
        sr = states[r]
        front = footprints[r][1]
        for v, sv in states.items():
            if v == r:
                continue
            t, end, last = max(sr["t"][0], sv["t"][0]) + 1.0, min(sr["t"][-1], sv["t"][-1]) - 3.0, -1e9
            while t < end:
                yaw_r = float(np.interp(t, sr["t"], sr["yaw"]))
                yaw_v = float(np.interp(t, sv["t"], sv["yaw"]))
                if abs((math.degrees(yaw_v - yaw_r) + 180.0) % 360.0 - 180.0) <= 45.0 and t - last > 3.0:
                    moved, u, onset = 0.0, t, None
                    while u < t + 3.0:
                        w = _lane_toward(road, states, v, r, u) or 0.0
                        if onset is None and w >= 0.3:
                            onset = u
                        moved += w * 0.05
                        u += 0.05
                    if moved >= CUT_TRUE_M and onset is not None and not in_corridor(r, v, onset, front):
                        steps = np.arange(onset, min(onset + 3.0, end + 3.0), 0.05)
                        if any(in_corridor(r, v, float(u), front) for u in steps):
                            truth.append((r, v, onset))
                            last = t
                t += 0.25
    return truth, road


def cut_in_metrics(run, identity, recorders, footprints, origins):
    truth, road = cut_in_truth(run, recorders, footprints)
    found = []
    for r in recorders:
        for n in _events(run, r):
            if n["event_type"] in ("CUT_IN_FROM_LEFT_START", "CUT_IN_FROM_RIGHT_START"):
                found.append((r, identity.get(r + ":" + str(n["subject_id"])), n["t_local"] + origins[r]))
    matched, onset_errors = set(), []
    tp = 0
    for r, v, t in found:
        best = None
        for i, (tr, tv, tt) in enumerate(truth):
            if i not in matched and tr == r and tv == v and abs(t - tt) <= 3.0:
                if best is None or abs(t - tt) < abs(t - truth[best][2]):
                    best = i
        if best is not None:
            matched.add(best)
            tp += 1
            onset_errors.append(round(t - truth[best][2], 2))
    fp = [(r, v, round(t - origins[r], 2)) for r, v, t in found
          if not any(tr == r and tv == v and abs(t - tt) <= 3.0 for tr, tv, tt in truth)]
    missed = [(r, v, round(t - origins[r], 2)) for i, (r, v, t) in enumerate(truth) if i not in matched]
    return {"found": len(found), "true": len(truth), "tp": tp, "fp": fp, "missed": missed, "onset_errors_s": onset_errors}


def critical_metrics(run, owner, identity):
    nodes = _events(run, owner)
    per = Counter()
    for n in nodes:
        if n["event_type"] == "CRITICAL_TTC_START":
            per[identity.get(owner + ":" + str(n["subject_id"])) or "?"] += 1
    return dict(per)


def closure_violations(run):
    path = run / "reconstruction" / "global" / "global_graph.json"
    if not path.exists():
        return None
    nodes = json.loads(path.read_text(encoding="utf-8"))["nodes"]
    out = 0
    for c in (n for n in nodes if n["event_type"] == "COLLISION" and n.get("participants")):
        if c.get("t_global") is None:
            continue  # a collision not on the global clock: its closure is undefined (campaign revision v2)
        pair = set(c["participants"])
        out += sum(1 for n in nodes if n["event_type"] == "CRITICAL_TTC_START" and n.get("t_global") is not None
                   and n["t_global"] > c["t_global"] and {n["actor_id"], n["subject_id"]} == pair)
    return out


def trajectory_jumps(run, owner):
    collisions = read_jsonl(run / "vehicles" / owner / "collisions.jsonl")
    records = read_jsonl(run / "vehicles" / owner / "ego.jsonl")
    origin = float(records[0]["timestamp"])
    impacts = [float(c["timestamp"]) - origin for c in collisions]
    count, worst = 0, 0.0
    for k, rows in _tracks(run, owner).items():
        for a, b, c in zip(rows, rows[1:], rows[2:]):
            dt1, dt2 = b["t_local"] - a["t_local"], c["t_local"] - b["t_local"]
            if dt1 <= 0 or dt2 <= 0 or any(abs(b["t_local"] - t) < 0.3 for t in impacts):
                continue
            v1 = np.array([b["x_m"] - a["x_m"], b["y_m"] - a["y_m"]]) / dt1
            v2 = np.array([c["x_m"] - b["x_m"], c["y_m"] - b["y_m"]]) / dt2
            accel = float(np.hypot(*(v2 - v1))) / (0.5 * (dt1 + dt2))
            worst = max(worst, accel)
            if accel > JUMP_ACCEL_MPS2:
                count += 1
    return {"implausible_steps": count, "max_implied_accel_mps2": round(worst, 1)}


def audit_run(run):
    cfg = load_config()
    identity, fm = _identities(run)
    truth = prepare_truth(run, cfg)
    recorders = sorted(p.name for p in (run / "vehicles").iterdir() if (p / "ego.jsonl").exists())
    origins, footprints = {}, {}
    for r in recorders:
        first = json.loads((run / "vehicles" / r / "ego.jsonl").open(encoding="utf-8").readline())
        origins[r] = float(first["timestamp"])
        fp = truth["recorders"][r].footprint if "recorders" in truth and r in truth["recorders"] else None
        footprints[r] = (fp.x_min, fp.x_max) if fp is not None else (-2.3, 2.3)
    out = {"run": run.parent.name + "/" + run.name, "recorders": {}}
    frames = frames_by_participant(read_jsonl(run / "ground_truth" / "states.jsonl"))
    for r in recorders:
        out["recorders"][r] = {"tracks": track_metrics(run, r, truth, identity, body_returns(run, r, truth, frames)),
                               "ego_path": path_metrics(run, r, identity),
                               "reference_path": reference_path_jumps(run, r),
                               "critical": critical_metrics(run, r, identity),
                               "trajectory": trajectory_jumps(run, r)}
    out["cut_in"] = cut_in_metrics(run, identity, recorders, footprints, origins)
    out["closure_violations"] = closure_violations(run)
    if fm:
        verdicts = Counter(d.get("verdict", "").split(" (")[0] for d in fm["track_decisions"])
        out["fusion"] = {"merges": fm.get("merges"), "wrong_links": verdicts.get("WRONG link", 0),
                         "missed_links": verdicts.get("missed link", 0)}
    return out


def summary_rows(results):
    rows = []
    for res in results:
        for r, m in res["recorders"].items():
            t = m["tracks"]
            kinds = Counter(l["kind"] for l in t["losses"])
            osc = sum(v["oscillations"] for v in m["ego_path"].values())
            ent = sum(v["entries"] for v in m["ego_path"].values())
            ex = sum(v["exits"] for v in m["ego_path"].values())
            rows.append({"run": res["run"], "rec": r, "tracks": t["tracks"], "births": t["births"],
                         "lost": len(t["losses"]), "frag": kinds["fragmentation"], "sparse": kinds["sparse returns"],
                         "vis": kinds["visibility loss"],
                         "phantom": len(t["phantoms"]), "dup_s": round(sum(d["overlap_s"] for d in t["duplicates"]), 2),
                         "entry": ent, "exit": ex, "osc": osc, "path_jumps": m["reference_path"].get("jumps"),
                         "traj_jumps": m["trajectory"]["implausible_steps"]})
    return rows


def markdown(results):
    lines = ["# Stability audit (privileged: ground truth used for evaluation only)", "",
             "Track losses: *fragm.* = the radar kept measuring the true body in at least half of the next 0.5 s "
             "(a tracker decision), *sparse* = it measured it only now and then, *no returns* = a sensing loss.", "",
             "| run | rec | tracks | births | lost | fragm. | sparse | no returns | phantom | dup s | ENTRY | EXIT "
             "| osc. | path jumps | traj. jumps |", "|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|"]
    tot = Counter()
    for row in summary_rows(results):
        lines.append("| {run} | {rec} | {tracks} | {births} | {lost} | {frag} | {sparse} | {vis} | {phantom} | {dup_s} "
                     "| {entry} | {exit} | {osc} | {path_jumps} | {traj_jumps} |".format(**row))
        for k in ("tracks", "births", "lost", "frag", "sparse", "vis", "phantom", "entry", "exit", "osc", "traj_jumps"):
            tot[k] += row[k] or 0
        tot["dup_s"] += row["dup_s"]
        tot["path_jumps"] += row["path_jumps"] or 0
    lines.append("| **total** | | {tracks} | {births} | {lost} | {frag} | {sparse} | {vis} | {phantom} | {dup:.2f} "
                 "| {entry} | {exit} | {osc} | {path_jumps} | {traj_jumps} |".format(dup=tot["dup_s"], **tot))
    lines += ["", "| run | CUT_IN found | true | TP | FP | missed | onset errors (s) | closure violations | wrong links "
              "| false merges | missed merges |", "|---|--:|--:|--:|---|---|---|--:|--:|--:|--:|"]
    for res in results:
        c, f = res["cut_in"], res.get("fusion") or {}
        merges = f.get("merges") or {}
        lines.append("| {0} | {1} | {2} | {3} | {4} | {5} | {6} | {7} | {8} | {9} | {10} |".format(
            res["run"], c["found"], c["true"], c["tp"], c["fp"] or "-", c["missed"] or "-",
            c["onset_errors_s"] or "-", res["closure_violations"], f.get("wrong_links"), merges.get("false"),
            merges.get("missed")))
    lines += ["", "Losses, phantoms, duplicates and oscillations in detail: the JSON output."]
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("runs", nargs="*")
    parser.add_argument("--json", default=None)
    parser.add_argument("--md", default=None)
    parser.add_argument("--no-write-evaluation", dest="write_evaluation", action="store_false",
                        help="do not write <run>/reconstruction/evaluation/stability.json")
    args = parser.parse_args(argv)
    runs = [Path(r) for r in args.runs] if args.runs else canonical_runs()
    results = []
    for run in runs:
        results.append(audit_run(run))
        evaluation = run / "reconstruction" / "evaluation"
        if args.write_evaluation and evaluation.is_dir():
            # The per-run result beside the other evaluation files (``validate_canonical`` reads it).
            (evaluation / "stability.json").write_text(json.dumps(results[-1], indent=1, default=str), encoding="utf-8")
        row = [r for r in summary_rows(results[-1:])]
        print(results[-1]["run"], " | ".join("{rec}: tracks {tracks} lost {lost} (frag {frag}) phantom {phantom} "
                                              "dup {dup_s}s entry/exit {entry}/{exit} osc {osc} pathjumps {path_jumps}"
                                              .format(**x) for x in row), flush=True)
    if args.json:
        Path(args.json).write_text(json.dumps(results, indent=1, default=str), encoding="utf-8")
    text = markdown(results)
    if args.md:
        Path(args.md).write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
