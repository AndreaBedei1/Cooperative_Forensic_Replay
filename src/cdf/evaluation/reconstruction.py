"""Privileged evaluation of a finished reconstruction.

Runs only after ``<run>/reconstruction/`` has been written.  It reads those
files plus ``<run>/ground_truth/`` and writes ``reconstruction/evaluation/``;
it never changes the reconstruction.  ``cdf.reconstruction`` never imports
this module.

Privileged assumption used only here: in these CARLA recordings every
recorder's raw clock is the simulator clock, so ``t_local + clock origin`` is
simulator time and can be compared with ``ground_truth/``.
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np

from ..reconstruction.config import ReconstructionConfig, config_from_mapping
from ..reconstruction.fusion import group_recontacts
from ..reconstruction.local import reconstruct_vehicle
from ..reconstruction.pipeline import fuse_recorders, read_incident_context, run_title
from ..reconstruction.render import write_json, write_text

# A track "is" a vehicle when its median distance to that vehicle's box is below this.
IDENTITY_MAX_BOX_DISTANCE_M = 1.5
# The clock-robustness check makes one recorder's local clock read this much later.
CLOCK_SHIFT_S = 0.73
# Ground-truth callbacks of one pair closer than this are one true contact, and a
# reconstructed COLLISION reproduces a true contact only if reported within this of it.
TRUTH_CONTACT_GAP_S = 0.5
# A later contact of the same pair is a recontact of the true collision it follows (one collision, not two) when
# it starts at most RECONTACT_MAX_PAUSE_S after the previous one and the two true boxes never parted by more than
# RECONTACT_MAX_SEPARATION_M in between: the reconstruction's rule (FusionConfig defaults) on the true geometry.
RECONTACT_MAX_PAUSE_S = 2.0
RECONTACT_MAX_SEPARATION_M = 1.0


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


class TruthTrack:
    """Ground-truth states of one participant, looked up by simulator time."""

    def __init__(self, states: Sequence[Dict[str, Any]]) -> None:
        self.states = sorted(states, key=lambda state: state["timestamp"])
        self.times = np.array([state["timestamp"] for state in self.states])

    def at(self, sim_time: float) -> Optional[Dict[str, Any]]:
        index = int(np.clip(np.searchsorted(self.times, sim_time), 0, len(self.times) - 1))
        if index > 0 and abs(self.times[index - 1] - sim_time) < abs(self.times[index] - sim_time):
            index -= 1
        return self.states[index] if abs(self.times[index] - sim_time) <= 0.03 else None


def _box_distance(point: Tuple[float, float], state: Dict[str, Any]) -> float:
    """2-D distance from a point to the vehicle's oriented bounding box (0 inside)."""
    along, across, extent = _in_box_frame(point, state)
    return math.hypot(max(abs(along) - extent["x"], 0.0), max(abs(across) - extent["y"], 0.0))


def _surface_distance(point: Tuple[float, float], state: Dict[str, Any]) -> float:
    """2-D distance from a point to the box outline: what a radar return lies on."""
    along, across, extent = _in_box_frame(point, state)
    outside = _box_distance(point, state)
    if outside > 0.0:
        return outside
    return min(extent["x"] - abs(along), extent["y"] - abs(across))


def _in_box_frame(point: Tuple[float, float], state: Dict[str, Any]) -> Tuple[float, float, Dict[str, float]]:
    transform = state["transform"]
    extent = state.get("bbox_extent") or {"x": 2.4, "y": 1.0}
    yaw = math.radians(transform["yaw_deg"])
    dx, dy = point[0] - transform["x"], point[1] - transform["y"]
    return math.cos(yaw) * dx + math.sin(yaw) * dy, -math.sin(yaw) * dx + math.cos(yaw) * dy, extent


def _outline(state: Dict[str, Any], step: float = 0.1) -> List[Tuple[float, float]]:
    """Points every ``step`` metres along a vehicle box's 2-D outline (world frame)."""
    transform = state["transform"]
    extent = state.get("bbox_extent") or {"x": 2.4, "y": 1.0}
    yaw = math.radians(transform["yaw_deg"])
    c, s = math.cos(yaw), math.sin(yaw)
    ex, ey = extent["x"], extent["y"]
    local = [(x, side * ey) for x in np.arange(-ex, ex + 1e-9, step) for side in (-1.0, 1.0)]
    local += [(side * ex, y) for y in np.arange(-ey, ey + 1e-9, step) for side in (-1.0, 1.0)]
    return [(transform["x"] + c * x - s * y, transform["y"] + s * x + c * y) for x, y in local]


def box_gap(first: Dict[str, Any], second: Dict[str, Any]) -> float:
    """2-D distance between two vehicles' boxes (0 when they touch or overlap), to about 0.05 m."""
    return min(min(_box_distance(point, first) for point in _outline(second)),
               min(_box_distance(point, second) for point in _outline(first)))


def _speed(state: Dict[str, Any]) -> float:
    return math.hypot(state["velocity"]["x"], state["velocity"]["y"])


def _rmse(values: Sequence[float]) -> Optional[float]:
    return round(math.sqrt(sum(v * v for v in values) / len(values)), 3) if values else None


def _to_world(first_pose: Dict[str, Any], x: float, y: float) -> Tuple[float, float]:
    """Local frame of a recorder -> CARLA world (evaluation only).

    ``first_pose`` is the recorder's TRUE first pose (``ego.jsonl``, G0), also when the reconstruction ran on a
    perturbed GNSS/INS: which vehicle a radar track followed is a physical fact, so a recorder's own pose error must
    not turn a real vehicle into a phantom or into another vehicle.  The error of the positions the reconstruction
    gives its road users is measured separately, on its own pose streams (``fusion_metrics`` state errors)."""
    yaw = math.radians(first_pose["yaw_deg"])
    return (first_pose["x"] + math.cos(yaw) * x - math.sin(yaw) * y,
            first_pose["y"] + math.sin(yaw) * x + math.cos(yaw) * y)


def truth_separation(states: Sequence[Dict[str, Any]]) -> Callable[[Sequence[str], float, float], Optional[float]]:
    """``separation(pair, t1, t2)`` on the ground truth (``fusion.group_recontacts``): the largest gap between the
    two true boxes between two simulator times; None for a static object or a vehicle without states."""
    frames: Dict[str, Dict[int, Dict[str, Any]]] = defaultdict(dict)
    for state in states:
        frames[state["participant_id"]][state["frame"]] = state

    def separation(pair: Sequence[str], t1: float, t2: float) -> Optional[float]:
        if len(pair) != 2 or any(name not in frames for name in pair):
            return None
        first, second = frames[pair[0]], frames[pair[1]]
        gaps = [box_gap(state, second[frame]) for frame, state in first.items()
                if frame in second and t1 - 1e-6 <= state["timestamp"] <= t2 + 1e-6]
        return max(gaps) if gaps else None
    return separation


def _truth_contacts(collisions: Sequence[Dict[str, Any]], actor_to_participant: Dict[int, str],
                    separation: Optional[Callable[[Sequence[str], float, float], Optional[float]]] = None
                    ) -> List[Dict[str, Any]]:
    """Ground-truth contacts between participants, first callback per pair and episode.

    ``actor_to_participant`` may include participants that are not recorders
    (``record: false``); their contacts can only be reported by the recorder
    involved.  With ``separation`` (``truth_separation``), a recontact is kept in the
    contact it follows (``recontacts``: its start and peak impulse) instead of being a
    contact of its own."""
    contacts: List[Dict[str, Any]] = []
    for record in sorted(collisions, key=lambda item: item["timestamp"]):
        other = actor_to_participant.get(record.get("other_actor_id"))
        pair = sorted([record["participant_id"], other]) if other else [record["participant_id"], "static/unrecorded"]
        previous = next((contact for contact in contacts if contact["participants"] == pair
                         and record["timestamp"] - contact["last_time"] <= TRUTH_CONTACT_GAP_S), None)
        if previous is None:
            contacts.append({"participants": pair, "sim_time": record["timestamp"], "last_time": record["timestamp"],
                             "peak_impulse": record["impulse"]})
        else:
            previous["last_time"] = record["timestamp"]
            previous["peak_impulse"] = max(previous["peak_impulse"], record["impulse"])
    for contact in contacts:
        contact.pop("last_time")
    if separation is None:
        return contacts
    grouped = []
    for contact, recontacts in group_recontacts(contacts, lambda c: tuple(c["participants"]), lambda c: c["sim_time"],
                                                separation, RECONTACT_MAX_PAUSE_S, RECONTACT_MAX_SEPARATION_M):
        contact["recontacts"] = [{"sim_time": r["sim_time"], "peak_impulse": r["peak_impulse"]} for r in recontacts]
        grouped.append(contact)
    return grouped


def match_collisions(contacts: Sequence[Dict[str, Any]], collision_nodes: Sequence[Dict[str, Any]],
                     recorders: Sequence[str], origins: Mapping[str, float]
                     ) -> Tuple[List[Dict[str, Any]], set]:
    """Each true collision against the reconstruction's COLLISION nodes, every node used once: (rows, used nodes).

    1. IDENTIFIED: the node naming exactly the collision's recorders (a collision with a static object or with a
       vehicle that records nothing is reported by the recorders involved only) that every observer reported
       within ``TRUTH_CONTACT_GAP_S`` of it, the closest one;
    2. else DETECTED with the wrong participants: a node that one of the collision's own recorders reported within
       ``TRUTH_CONTACT_GAP_S`` of it (its collision sensor felt it), whatever participants the node names;
    3. else MISSED.
    Every collision gets its exact match before any is matched the second way."""
    def report_error(node: Dict[str, Any], contact: Dict[str, Any]) -> float:
        return max(abs(obs["t_local"] + origins[obs["graph"]] - contact["sim_time"]) for obs in node["observations"])

    def own_report_error(node: Dict[str, Any], contact: Dict[str, Any]) -> Optional[float]:
        errors = [abs(obs["t_local"] + origins[obs["graph"]] - contact["sim_time"]) for obs in node["observations"]
                  if obs["graph"] in contact["participants"]]
        return min(errors) if errors else None

    used: set = set()
    matches: Dict[int, Tuple[Dict[str, Any], float, bool]] = {}
    for index, contact in enumerate(contacts):
        expected = sorted(name for name in contact["participants"] if name in recorders)
        options = [node for node in collision_nodes if sorted(node["participants"]) == expected
                   and node["node_id"] not in used and report_error(node, contact) <= TRUTH_CONTACT_GAP_S]
        if options:
            match = min(options, key=lambda node: report_error(node, contact))
            used.add(match["node_id"])
            matches[index] = (match, report_error(match, contact), True)
    for index, contact in enumerate(contacts):
        if index in matches:
            continue
        options = [(own_report_error(node, contact), node) for node in collision_nodes if node["node_id"] not in used]
        options = [(error, node) for error, node in options if error is not None and error <= TRUTH_CONTACT_GAP_S]
        if options:
            error, match = min(options, key=lambda item: item[0])
            used.add(match["node_id"])
            matches[index] = (match, error, False)
    rows = []
    for index, contact in enumerate(contacts):
        match, error, exact = matches.get(index, (None, None, False))
        rows.append({"participants": contact["participants"], "sim_time": contact["sim_time"],
                     "peak_impulse": contact["peak_impulse"], "recontacts": contact.get("recontacts", []),
                     "reconstructed_as": None if match is None else match["node_id"],
                     "reconstructed_participants": None if match is None else sorted(match["participants"]),
                     "participants_correct": exact,
                     "report_timing_error_s": None if error is None else round(error, 4)})
    return rows, used


def _clock_shift_check(run_dir: Path, graph: Dict[str, Any], alignment: Dict[str, Any],
                       config: ReconstructionConfig) -> Dict[str, Any]:
    """Would the global graph change if one recorder's clock had started differently?

    The last recorder is rebuilt with its local clock reading ``CLOCK_SHIFT_S``
    later, then alignment and fusion are rerun in memory.  Uses no ground truth.
    """
    locals_ = []
    context = read_incident_context(run_dir)
    shifted = sorted(alignment["graphs"])[-1]
    for vehicle_dir in sorted(path for path in (run_dir / "vehicles").iterdir() if path.is_dir()):
        origin = None
        if vehicle_dir.name == shifted:
            origin = _read_jsonl(vehicle_dir / "ego.jsonl")[0]["timestamp"] - CLOCK_SHIFT_S
        locals_.append(reconstruct_vehicle(vehicle_dir, config, clock_origin=origin, context=context))
    shifted_alignment, _, _, shifted_graph = fuse_recorders(run_dir, locals_, config)

    def signature(nodes: List[Tuple[Any, ...]]) -> List[Tuple[Any, ...]]:
        return [(kind, actor, subject, None if t is None else round(t, 3)) for kind, actor, subject, t in nodes]

    before_nodes = signature([(n["event_type"], n["actor_id"], n["subject_id"], n["t_global"]) for n in graph["nodes"]])
    after_nodes = signature([(n.event_type, n.actor_id, n.subject_id, n.t_global) for n in shifted_graph.nodes])
    shifted_local = next(local for local in locals_ if local.owner == shifted)
    before = alignment["graphs"][shifted]["offset_to_global"]
    after = shifted_alignment.graphs[shifted].offset_to_global
    return {"shifted_recorder": shifted, "shift_s": CLOCK_SHIFT_S,
            "shifted_local_collision_times": [node.t_local for node in shifted_local.graph.nodes
                                              if node.event_type == "COLLISION"],
            "global_graph_identical": before_nodes == after_nodes,
            "offset_to_global_before": before, "offset_to_global_after": after,
            "offset_change_s": None if before is None or after is None else round(after - before, 4)}


def evaluate_run(run_dir: Path, clock_shift_check: bool = True) -> Dict[str, Any]:
    run_dir = Path(run_dir)
    rec = run_dir / "reconstruction"
    alignment = _read_json(rec / "global" / "alignment.json")
    associations = _read_json(rec / "global" / "associations.json")
    graph = _read_json(rec / "global" / "global_graph.json")
    recorders = sorted(alignment["graphs"])
    local_graphs = {name: _read_json(rec / name / "local_graph.json") for name in recorders}
    origins = {name: local_graphs[name]["recorder"]["clock"]["origin_source_timestamp"] for name in recorders}
    first_poses = {name: _read_jsonl(run_dir / "vehicles" / name / "ego.jsonl")[0] for name in recorders}

    # Privileged inputs.
    states = _read_jsonl(run_dir / "ground_truth" / "states.jsonl")
    truth = {name: TruthTrack([s for s in states if s["participant_id"] == name])
             for name in sorted({s["participant_id"] for s in states})}
    actor_to_participant = {s["actor_id"]: s["participant_id"] for s in states}
    contacts = _truth_contacts(_read_jsonl(run_dir / "ground_truth" / "collisions.jsonl"), actor_to_participant,
                               truth_separation(states))
    recontacts = [{"participants": c["participants"], "sim_time": r["sim_time"]}
                  for c in contacts for r in c["recontacts"]]
    collision_nodes = [node for node in graph["nodes"] if node["event_type"] == "COLLISION"]
    # The true contact (or recontact) behind the reference collision, the matched collision that defines
    # t_global = 0.
    reference = next((event for event in alignment["matched_events"]
                      if event["event_id"] == alignment["reference_event"]), None)
    reference_truth = None
    if reference is not None:
        first = sorted(reference["graphs"])[0]
        reported_at = reference["t_local"][first] + origins[first]
        candidates = [c for c in contacts + recontacts if c["participants"] == sorted(reference["graphs"])]
        if candidates:
            reference_truth = min(candidates, key=lambda c: abs(c["sim_time"] - reported_at))
    # Simulator time of the true t_global = 0: the true contact behind the reference collision node or,
    # when no collision was matched (a near miss), the reference recorder's own clock origin (its clock is
    # the global one by definition); None when nothing is on a global clock.
    reference_recorder = next((name for name in recorders
                               if alignment["graphs"][name].get("method") == "reference_recorder"), None)
    if reference_truth is not None:
        zero_sim: Optional[float] = reference_truth["sim_time"]
    elif reference_recorder is not None:
        zero_sim = origins[reference_recorder]
    else:
        zero_sim = None

    # 1. Collisions: each true collision identified, detected with the wrong participants, or missed
    #    (match_collisions); every node is used once.
    def report_error(node: Dict[str, Any], contact: Dict[str, Any]) -> float:
        return max(abs(obs["t_local"] + origins[obs["graph"]] - contact["sim_time"]) for obs in node["observations"])

    collision_rows, used = match_collisions(contacts, collision_nodes, recorders, origins)
    # Reconstructed collisions that reproduce no true contact (e.g. one contact split in two); ``true_recontact``
    # when the node is a true recontact reported as a collision of its own.
    def is_recontact(node: Dict[str, Any]) -> bool:
        return any(sorted(node["participants"]) == sorted(name for name in r["participants"] if name in recorders)
                   and report_error(node, r) <= TRUTH_CONTACT_GAP_S for r in recontacts)

    extra_collisions = [{"node": node["node_id"], "participants": node["participants"], "t_global": node["t_global"],
                         "true_recontact": is_recontact(node)}
                        for node in collision_nodes if node["node_id"] not in used]

    # 2. Alignment accuracy: per recorder, the local time at which t_global = 0 (-offset_to_global)
    #    against the true local time of the reference contact, whatever chain aligned it.
    alignment_rows = []
    for name in recorders:
        clock = alignment["graphs"][name]
        true_reference = None if zero_sim is None else round(zero_sim - origins[name], 4)
        estimated = None if clock["offset_to_global"] is None else round(-clock["offset_to_global"], 4)
        error = None if estimated is None or true_reference is None else round(estimated - true_reference, 4)
        alignment_rows.append({"graph": name, "status": clock["status"], "method": clock.get("method"),
                               "chain": clock.get("chain", []),
                               "estimated_reference_t_local": estimated,
                               "true_reference_t_local": true_reference, "error_s": error})
    relative = []
    for name, estimated in alignment["relative_clock_offsets_s"].items():
        second, first = [part.strip() for part in name.split(" - ")]
        true_offset = round(origins[first] - origins[second], 4)
        relative.append({"pair": name, "estimated_s": estimated, "true_s": true_offset,
                         "error_s": round(estimated - true_offset, 4)})

    # 3. Global event times and order.
    timed = [node for node in graph["nodes"] if node["t_global"] is not None]
    time_errors = []
    true_times = []
    for node in timed if zero_sim is not None else []:
        observation = node["observations"][0]
        true_global = observation["t_local"] + origins[observation["graph"]] - zero_sim
        true_times.append(true_global)
        time_errors.append(node["t_global"] - true_global)
    timed = timed if zero_sim is not None else []
    concordant = total = 0
    for i in range(len(timed)):
        for j in range(i + 1, len(timed)):
            if abs(timed[i]["t_global"] - timed[j]["t_global"]) < 1e-9 or abs(true_times[i] - true_times[j]) < 1e-9:
                continue
            total += 1
            concordant += (timed[i]["t_global"] < timed[j]["t_global"]) == (true_times[i] < true_times[j])

    # 4-5. Track identities and trajectory accuracy.
    track_rows = []
    for item in associations:
        owner, track_id = item["local_graph"], item["local_track"]
        samples = [row for row in _read_jsonl(rec / owner / "local_tracks.jsonl") if row["track_id"] == track_id]
        distances: Dict[str, List[float]] = {}
        for sample in samples:
            point = _to_world(first_poses[owner], sample["x_m"], sample["y_m"])
            for name, track in truth.items():
                if name == owner:
                    continue
                state = track.at(sample["t_local"] + origins[owner])
                if state is not None:
                    distances.setdefault(name, []).append(_box_distance(point, state))
        medians = {name: float(np.median(values)) for name, values in distances.items() if values}
        best = min(medians, key=medians.get) if medians else None
        identity = best if best is not None and medians[best] <= IDENTITY_MAX_BOX_DISTANCE_M else None
        if item["status"] == "ASSOCIATED":
            verdict = "correct" if item["global_entity"] == identity else "WRONG"
        else:
            verdict = ("correctly left anonymous" if identity not in recorders
                       else "left anonymous (true identity {0})".format(identity))
        row = {"track": owner + ":" + track_id, "decision": item["global_entity"], "status": item["status"],
               "true_identity": identity, "median_box_distance_m": {k: round(v, 2) for k, v in medians.items()},
               "verdict": verdict}
        if identity is not None:
            raw, smooth, centre, speed, raw_speed = [], [], [], [], []
            previous = None
            for sample in samples:
                state = truth[identity].at(sample["t_local"] + origins[owner])
                if state is None or not sample["measured"]:
                    previous = None
                    continue  # compare raw and smoothed on the same sweeps
                point = _to_world(first_poses[owner], sample["x_m"], sample["y_m"])
                measured = _to_world(first_poses[owner], sample["meas_x_m"], sample["meas_y_m"])
                smooth.append(_surface_distance(point, state))
                raw.append(_surface_distance(measured, state))
                centre.append(math.hypot(point[0] - state["transform"]["x"], point[1] - state["transform"]["y"]))
                speed.append(sample["speed_mps"] - _speed(state))
                # Speed from consecutive raw returns: what one gets without the filter.
                if previous is not None and sample["t_local"] - previous[0] < 0.11:
                    dt = sample["t_local"] - previous[0]
                    raw_speed.append(math.hypot(measured[0] - previous[1][0], measured[1] - previous[1][1]) / dt
                                     - _speed(state))
                previous = (sample["t_local"], measured)
            row.update({"samples": len(smooth), "raw_rmse_to_surface_m": _rmse(raw),
                        "smoothed_rmse_to_surface_m": _rmse(smooth), "smoothed_rmse_to_centre_m": _rmse(centre),
                        "raw_difference_speed_rmse_mps": _rmse(raw_speed), "speed_rmse_mps": _rmse(speed)})
        track_rows.append(row)

    # 6. Clearance at each true vehicle contact: per recorder, its track lying on the partner
    #    (tracked point within IDENTITY_MAX_BOX_DISTANCE_M of the partner's box) at the last 10 Hz
    #    sample at or before the contact, against the true gap between the two boxes then.
    samples_of: Dict[str, List[Dict[str, Any]]] = {}
    for name in recorders:
        for sample in _read_jsonl(rec / name / "local_tracks.jsonl"):
            samples_of.setdefault(name + ":" + sample["track_id"], []).append(sample)
    contact_clearances = []
    for contact in contacts:
        if "static/unrecorded" in contact["participants"]:
            continue
        for owner in contact["participants"]:
            if owner not in recorders:
                continue  # a vehicle that records nothing has no tracks
            partner = next(name for name in contact["participants"] if name != owner)
            t_contact = contact["sim_time"] - origins[owner]
            best = None
            for key, samples in samples_of.items():
                if not key.startswith(owner + ":"):
                    continue
                before = [s for s in samples if s["t_local"] <= t_contact + 0.051]
                if not before or t_contact - before[-1]["t_local"] > 1.0:
                    continue
                sample = before[-1]
                state = truth[partner].at(sample["t_local"] + origins[owner]) if partner in truth else None
                point = _to_world(first_poses[owner], sample["x_m"], sample["y_m"])
                if state is None or _box_distance(point, state) > IDENTITY_MAX_BOX_DISTANCE_M:
                    continue
                if best is None or (sample["t_local"], -sample["clearance_m"]) > (best[1]["t_local"], -best[1]["clearance_m"]):
                    best = (key, sample)
            row = {"contact": " + ".join(contact["participants"]), "recorder": owner, "partner": partner,
                   "track": None if best is None else best[0]}
            if best is not None:
                sample = best[1]
                sim = sample["t_local"] + origins[owner]
                own_state, partner_state = truth[owner].at(sim), truth[partner].at(sim)
                gap = None if own_state is None or partner_state is None else round(box_gap(own_state, partner_state), 3)
                row.update(seen_s_before_contact=round(t_contact - sample["t_local"], 3),
                           clearance_m=sample.get("clearance_m"), true_gap_m=gap,
                           error_m=None if gap is None or sample.get("clearance_m") is None
                           else round(sample["clearance_m"] - gap, 3),
                           range_m=sample.get("range_m"), ttc_s=sample.get("ttc_s"))
            contact_clearances.append(row)

    robustness = None
    if clock_shift_check and alignment["reference_event"] is not None:
        config = config_from_mapping(graph.get("reconstruction_config"))
        robustness = _clock_shift_check(run_dir, graph, alignment, config)

    between = [row for row in collision_rows if all(name in recorders for name in row["participants"])]
    merged = [node for node in collision_nodes if node["actor_id"] is None]
    if between:
        collision_text = "{0} ({1}/{2} vehicle contacts{3})".format(
            "yes" if all(row["participants_correct"] for row in between) and not extra_collisions else "NO",
            sum(row["participants_correct"] for row in between), len(between),
            "" if not extra_collisions else ", {0} extra collision node(s)".format(len(extra_collisions)))
    else:
        collision_text = "no vehicle-vehicle collision in ground truth" + (
            "" if not merged else ", but {0} merged collision node(s) reconstructed".format(len(merged)))
    decided = [row for row in track_rows if row["status"] == "ASSOCIATED"]
    headline = "collision reconstructed: {0}; associations correct: {1}/{2}; anonymous: {3}; max |t_global error| {4} s".format(
        collision_text,
        sum(row["verdict"] == "correct" for row in decided), len(decided),
        sum(row["status"] != "ASSOCIATED" for row in track_rows),
        None if not time_errors else round(max(abs(e) for e in time_errors), 4))
    result = {"run": run_title(run_dir), "headline": headline,
              "privileged_assumption": "recorder raw clocks are CARLA simulator time",
              "collisions": collision_rows, "extra_collisions": extra_collisions,
              "alignment": alignment_rows, "relative_clock_offsets": relative,
              "event_timing": {"nodes": len(timed),
                               "max_abs_error_s": None if not time_errors else round(max(abs(e) for e in time_errors), 4),
                               "order_pairs": total, "order_concordant": concordant},
              "tracks": track_rows, "contact_clearances": contact_clearances, "clock_shift_check": robustness}
    write_json(rec / "evaluation" / "evaluation.json", result)
    write_text(rec / "evaluation" / "evaluation.md", evaluation_markdown(result))
    return result


def evaluation_markdown(result: Dict[str, Any]) -> str:
    def cell(value: Any) -> str:
        return "-" if value is None else str(value)

    lines = ["# Privileged evaluation - " + result["run"], "",
             "This compares the finished reconstruction with `ground_truth/` (simulator state). The "
             "reconstruction never read it and was not changed by this evaluation.", "",
             "**" + result["headline"] + "**", "",
             "Privileged assumption: " + result["privileged_assumption"] + ".", "",
             "## Collisions", "",
             "| True contact | Sim time | Peak impulse | Reconstructed as | Participants correct | Report timing error |",
             "|--------------|---------:|-------------:|------------------|----------------------|--------------------:|"]
    for row in result["collisions"]:
        lines.append("| {0} | {1:.3f} | {2:.1f} | {3} | {4} | {5} s |".format(
            " + ".join(row["participants"]), row["sim_time"], row["peak_impulse"], cell(row["reconstructed_as"]),
            "yes" if row["participants_correct"] else "NO", cell(row["report_timing_error_s"])))
    extra = result.get("extra_collisions") or []
    lines += ["", "Reconstructed COLLISION nodes that reproduce no true contact: " + (", ".join(
        "{0} ({1}, t_global {2})".format(item["node"], " + ".join(item["participants"]), cell(item["t_global"]))
        for item in extra) or "none") + "."]
    lines += ["", "## Graph alignment accuracy", "",
              "Local time at which each graph reads t_global = 0, against the true local time of the "
              "reference contact; the chain lists the matched collisions that aligned the graph.", "",
              "| Graph | Status | Chain | Estimated (local) | True (local) | Error |",
              "|-------|--------|-------|------------------:|-------------:|------:|"]
    for row in result["alignment"]:
        lines.append("| {0} | {1} | {2} | {3} | {4} | {5} s |".format(
            row["graph"], row["status"], " -> ".join(row["chain"]) or "-", cell(row["estimated_reference_t_local"]),
            cell(row["true_reference_t_local"]), cell(row["error_s"])))
    for row in result["relative_clock_offsets"]:
        lines.append("")
        lines.append("Relative clock offset {0}: estimated {1:+.3f} s, true {2:+.3f} s (error {3:+.3f} s).".format(
            row["pair"], row["estimated_s"], row["true_s"], row["error_s"]))
    timing = result["event_timing"]
    lines += ["", "## Global event times", "",
              "{0} timed global nodes; max |t_global - true global time| = {1} s; event order agrees "
              "with the truth for {2}/{3} pairs.".format(timing["nodes"], cell(timing["max_abs_error_s"]),
                                                          timing["order_concordant"], timing["order_pairs"])]
    lines += ["", "## Anonymous tracks: identity and trajectory", "",
              "| Track | Decision | True identity | Verdict | Samples | Position RMSE to surface: raw / smoothed | Smoothed RMSE to centre | Speed RMSE: raw differences / smoothed |",
              "|-------|----------|---------------|---------|--------:|------------------------------------------|------------------------:|----------------------------------------|"]
    for row in result["tracks"]:
        lines.append("| {0} | {1} | {2} | {3} | {4} | {5} / {6} m | {7} m | {8} / {9} m/s |".format(
            row["track"], row["decision"], cell(row["true_identity"]), row["verdict"], cell(row.get("samples")),
            cell(row.get("raw_rmse_to_surface_m")), cell(row.get("smoothed_rmse_to_surface_m")),
            cell(row.get("smoothed_rmse_to_centre_m")), cell(row.get("raw_difference_speed_rmse_mps")),
            cell(row.get("speed_rmse_mps"))))
    lines += ["", "## Clearance at the true contacts", "",
              "Per recorder, its track lying on the partner at the last 10 Hz sample at or before the contact: "
              "clearance (free distance from the recorder's footprint to the track's near surface), the true gap "
              "between the two vehicles' boxes at that instant, and the raw range from the radar.", "",
              "| Contact | Recorder | Partner | Track | Seen before contact | Clearance | True gap | Error | Range |",
              "|---------|----------|---------|-------|--------------------:|----------:|---------:|------:|------:|"]
    for row in result.get("contact_clearances") or []:
        lines.append("| {0} | {1} | {2} | {3} | {4} s | {5} m | {6} m | {7} m | {8} m |".format(
            row["contact"], row["recorder"], row["partner"], cell(row["track"]), cell(row.get("seen_s_before_contact")),
            cell(row.get("clearance_m")), cell(row.get("true_gap_m")), cell(row.get("error_m")),
            cell(row.get("range_m"))))
    lines += ["", "Surface distance = distance from a track point to the outline of the true vehicle's "
              "bounding box, i.e. where radar returns lie. Raw = median radar return of that sweep; "
              "smoothed = Kalman + RTS estimate; both on the same measured 10 Hz sweeps. Raw returns lie on "
              "the surface by construction, so smoothing cannot be expected to bring the position closer to "
              "it; its gain shows in the speed (raw differences of consecutive returns vs smoothed "
              "velocity). The distance to the centre includes the surface-to-centre offset. True identity = "
              "the vehicle whose box is closest (median <= {0} m).".format(IDENTITY_MAX_BOX_DISTANCE_M)]
    check = result["clock_shift_check"]
    if check:
        lines += ["", "## Clock-shift check (uses no ground truth)", "",
                  "Recorder {0} was rebuilt with its local clock reading {1:+.2f} s later (its collision is then "
                  "at local time {2}), and alignment and fusion were rerun. Global graph identical: **{3}**. "
                  "{0}'s offset_to_global changed by {4} s (expected {5:+.2f} s).".format(
                      check["shifted_recorder"], check["shift_s"],
                      ", ".join("{0:.2f} s".format(t) for t in check["shifted_local_collision_times"]) or "-",
                      "yes" if check["global_graph_identical"] else "NO",
                      cell(check["offset_change_s"]), -check["shift_s"])]
    return "\n".join(lines) + "\n"
