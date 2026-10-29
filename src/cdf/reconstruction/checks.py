"""Read-only queries over one local graph, for validation and reports.

They describe the observed order of events in one recorder's own clock; they
are not legal or causal judgements.  For example ``sign_windows`` says whether
a STOP_START of the recorder lies inside a STOP-sign detection window, from
which a later reasoning layer may derive NO_STOP_AFTER_STOP_SIGN.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from .models import GraphNode, LocalGraph, transition_of


def open_states(graph: LocalGraph) -> List[Dict[str, Any]]:
    """States that started and never ended: still active when observation ended.

    Observation of a track's states ends at its TRACK_LOST; of everything else
    at the end of the recording.  No END is inferred in either case.
    """
    active: Dict[Tuple[str, Optional[str]], GraphNode] = {}
    lost: Dict[Optional[str], float] = {}
    for node in graph.nodes:
        if node.event_type == "TRACK_LOST":
            lost[node.subject_id] = node.t_local
        transition = transition_of(node.event_type)
        if transition is None:
            continue
        name, starts = transition
        if starts:
            active[(name, node.subject_id)] = node
        else:
            active.pop((name, node.subject_id), None)
    return [{"state": name, "subject": subject, "since_node": node.node_id, "since_t_local": node.t_local,
             "observed_until": "TRACK_LOST" if subject in lost else "recording end",
             "observed_until_t_local": lost.get(subject, graph.recorder.get("end_t_local"))}
            for (name, subject), node in sorted(active.items(), key=lambda item: item[1].node_id)]


def _stopped_at(graph: LocalGraph, t_local: float) -> bool:
    """Whether the recorder was in the STOP state at ``t_local`` (strictly before any later change)."""
    stopped = False
    for node in graph.nodes:
        if node.t_local >= t_local:
            break
        if node.event_type == "STOP_START":
            stopped = True
        elif node.event_type == "STOP_END":
            stopped = False
    return stopped


def sign_windows(graph: LocalGraph, sign: str = "STOP_SIGN_DETECTED") -> List[Dict[str, Any]]:
    """Each detection window of a sign, and the recorder's STOP_START events inside it.

    Inside means strictly after the window's START and strictly before its END
    (equal times are simultaneous, hence unresolved).  A window without END (the
    sign still in view when the recording ended) lasts until the recording end.
    A reacquired sign has several windows; each START pairs with the next END
    of the same sign.
    """
    stops = [node for node in graph.nodes if node.event_type == "STOP_START"]
    recording_end = float(graph.recorder.get("end_t_local", float("inf")))
    pairs: List[Tuple[GraphNode, Optional[GraphNode]]] = []
    open_: Dict[Optional[str], int] = {}
    for node in graph.nodes:
        if node.event_type == sign + "_START":
            open_[node.subject_id] = len(pairs)
            pairs.append((node, None))
        elif node.event_type == sign + "_END" and node.subject_id in open_:
            index = open_.pop(node.subject_id)
            pairs[index] = (pairs[index][0], node)
    windows = []
    for start, end in pairs:
        if end is not None:
            inside = [stop for stop in stops if start.t_local < stop.t_local < end.t_local]
        else:
            inside = [stop for stop in stops if start.t_local < stop.t_local <= recording_end]
        windows.append({"sign": start.subject_id, "start_node": start.node_id, "start_t_local": start.t_local,
                        "end_node": None if end is None else end.node_id,
                        "end_t_local": None if end is None else end.t_local,
                        "relevant_to_ego_path": start.attributes.get("relevant_to_ego_path"),
                        "reacquired": bool(start.attributes.get("reacquired")),
                        "stop_starts_inside": [stop.node_id for stop in inside],
                        "already_stopped_at_start": _stopped_at(graph, start.t_local)})
    return windows


CUT_IN_STARTS = ("CUT_IN_FROM_LEFT_START", "CUT_IN_FROM_RIGHT_START")


def _round(value: Optional[float]) -> Optional[float]:
    return None if value is None else round(value, 3)


def temporal_safety_relations(graph: LocalGraph,
                              partner_collisions: Optional[Mapping[str, Sequence[float]]] = None
                              ) -> List[Dict[str, Any]]:
    """Order of a track's cut-in, critical TTC and path entry, and the recorder's collision.

    One entry per local track with a CUT_IN_*_START, CRITICAL_TTC_START or
    EGO_PATH_ENTRY, in the recorder's own clock.  These are temporal properties
    only, not causal claims.  The cut-in is compared with the critical-TTC
    episode active at its start: ``CRITICAL_TTC_ALREADY_ACTIVE`` when that
    episode started at or before the cut-in (CRITICAL_TTC_START <= CUT_IN_START),
    otherwise ``CUT_IN_BEFORE_CRITICAL_TTC`` with the next CRITICAL_TTC_START, or
    ``NO_CRITICAL_TTC_AFTER_CUT_IN``.  ``chain`` states
    ``CUT_IN_* < CRITICAL_TTC_START < COLLISION`` when all three hold in that order.

    A recorder can collide more than once, so ``collision`` is its first
    COLLISION at or after the track's critical TTC start (without one, after
    the track's cut-in or path entry), or None.  ``partner_collisions`` (track
    -> local times), known only after fusion has identified a track, limits the
    choice to the recorder's collisions with that entity.
    """
    collisions = sorted(node.t_local for node in graph.nodes if node.event_type == "COLLISION")
    subjects: Dict[str, List[GraphNode]] = {}
    for node in graph.nodes:
        if node.subject_id and node.subject_id.startswith("track_"):
            subjects.setdefault(node.subject_id, []).append(node)
    out = []
    for subject in sorted(subjects):
        nodes = subjects[subject]
        cut_in = next((node for node in nodes if node.event_type in CUT_IN_STARTS), None)
        entry = next((node.t_local for node in nodes if node.event_type == "EGO_PATH_ENTRY"), None)
        episodes: List[Tuple[float, Optional[float]]] = []
        for node in nodes:
            if node.event_type == "CRITICAL_TTC_START":
                episodes.append((node.t_local, None))
            elif node.event_type == "CRITICAL_TTC_END" and episodes and episodes[-1][1] is None:
                episodes[-1] = (episodes[-1][0], node.t_local)
        if cut_in is None and not episodes and entry is None:
            continue
        critical = episodes[0][0] if episodes else None
        relation, later = None, None
        if cut_in is not None:
            t_cut = cut_in.t_local
            active = next((start for start, end in episodes if start <= t_cut + 1e-6 and (end is None or end > t_cut + 1e-6)),
                          None)
            later = next((start for start, _ in episodes if start > t_cut + 1e-6), None)
            if active is not None:
                critical, relation = active, "CRITICAL_TTC_ALREADY_ACTIVE"
            elif later is not None:
                critical, relation = later, "CUT_IN_BEFORE_CRITICAL_TTC"
            else:
                relation = "NO_CRITICAL_TTC_AFTER_CUT_IN"
        start = critical if critical is not None else min(
            t for t in (None if cut_in is None else cut_in.t_local, entry) if t is not None)
        candidates = collisions if partner_collisions is None or subject not in partner_collisions \
            else sorted(partner_collisions[subject])
        collision = next((t for t in candidates if t >= start - 1e-6), None)
        item: Dict[str, Any] = {
            "track": subject, "cut_in": None if cut_in is None else {"type": cut_in.event_type, "t_local": cut_in.t_local},
            "critical_ttc_start": critical, "ego_path_entry": entry, "collision": collision,
            "cut_in_vs_critical_ttc": relation, "chain": None, "ego_path_entry_vs_critical_ttc": None, "deltas_s": {}}
        if relation == "CRITICAL_TTC_ALREADY_ACTIVE":
            item["deltas_s"]["cut_in_minus_critical_ttc_start"] = _round(cut_in.t_local - critical)
        elif relation == "CUT_IN_BEFORE_CRITICAL_TTC":
            item["deltas_s"]["critical_ttc_start_minus_cut_in"] = _round(later - cut_in.t_local)
            if collision is not None and collision > later + 1e-6:
                item["chain"] = "{0} < CRITICAL_TTC_START < COLLISION".format(cut_in.event_type)
                item["deltas_s"]["collision_minus_critical_ttc_start"] = _round(collision - later)
        if entry is not None and critical is not None:
            delta = entry - critical
            item["ego_path_entry_vs_critical_ttc"] = ("SAME_TIME" if abs(delta) < 1e-6
                                                      else "BEFORE" if delta < 0 else "AFTER")
            item["deltas_s"]["ego_path_entry_minus_critical_ttc_start"] = _round(delta)
        if collision is not None and critical is not None and "collision_minus_critical_ttc_start" not in item["deltas_s"]:
            item["deltas_s"]["collision_minus_critical_ttc_start"] = _round(collision - critical)
        out.append(item)
    return out


def _collision_text(item: Dict[str, Any]) -> str:
    """'COLLISION 5.25', or 'COLLISION with B 5.25' once fusion has identified the track."""
    partner = item.get("collision_with")
    return "COLLISION{0} {1:.2f}".format(" with " + partner if partner else "", item["collision"])


def describe_temporal_relation(item: Dict[str, Any]) -> str:
    """One compact line, e.g. 'CUT_IN_FROM_LEFT_START 3.90 < CRITICAL_TTC_START 4.20 (+0.30 s) < COLLISION 5.25 (+1.05 s)'."""
    parts = []
    deltas = item["deltas_s"]
    cut_in, critical, collision = item["cut_in"], item["critical_ttc_start"], item["collision"]
    relation = item["cut_in_vs_critical_ttc"]
    if relation == "CRITICAL_TTC_ALREADY_ACTIVE":
        parts.append("critical TTC already active before the cut-in: CRITICAL_TTC_START {0:.2f} <= {1} {2:.2f} "
                     "(+{3:.2f} s)".format(critical, cut_in["type"], cut_in["t_local"],
                                           deltas["cut_in_minus_critical_ttc_start"]))
    elif relation == "CUT_IN_BEFORE_CRITICAL_TTC":
        text = "cut-in started before critical TTC: {0} {1:.2f} < CRITICAL_TTC_START {2:.2f} (+{3:.2f} s)".format(
            cut_in["type"], cut_in["t_local"], critical, deltas["critical_ttc_start_minus_cut_in"])
        if item["chain"]:
            text += " < {0} (+{1:.2f} s)".format(_collision_text(item), deltas["collision_minus_critical_ttc_start"])
        parts.append(text)
    elif relation == "NO_CRITICAL_TTC_AFTER_CUT_IN":
        parts.append("{0} {1:.2f}, no critical TTC after it".format(cut_in["type"], cut_in["t_local"]))
    elif critical is not None:
        parts.append("CRITICAL_TTC_START {0:.2f}{1}".format(
            critical, "" if collision is None or "collision_minus_critical_ttc_start" not in deltas
            else ", {0} (+{1:.2f} s)".format(_collision_text(item), deltas["collision_minus_critical_ttc_start"])))
    entry = item["ego_path_entry_vs_critical_ttc"]
    if entry is not None:
        parts.append("EGO_PATH_ENTRY {0:.2f} {1} critical TTC ({2:+.2f} s)".format(
            item["ego_path_entry"], {"BEFORE": "before", "AFTER": "after", "SAME_TIME": "together with"}[entry],
            deltas["ego_path_entry_minus_critical_ttc_start"]))
    elif item["ego_path_entry"] is not None:
        parts.append("EGO_PATH_ENTRY {0:.2f}, no critical TTC".format(item["ego_path_entry"]))
    return "; ".join(parts)
