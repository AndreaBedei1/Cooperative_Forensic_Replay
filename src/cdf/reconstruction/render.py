
from __future__ import annotations

import json
import math
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from .checks import describe_temporal_relation, open_states, sign_windows, temporal_safety_relations
from .fusion import ASSOCIATED, short_label
from .models import (Alignment, Association, GlobalGraph, GlobalNode, GraphNode, LocalGraph,
                     is_anonymous_entity)
from .world_state import TRACK_STATES, compact_state

KIND_COLOURS = {"ACTION": "#fde68a", "PERCEPTION": "#bfdbfe", "FACT": "#e5e7eb", "OUTCOME": "#fca5a5"}


def _plain(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    if hasattr(value, "item") and not isinstance(value, (str, bytes)):
        value = value.item()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_plain(data), indent=2, allow_nan=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(_plain(row), allow_nan=False) + "\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def render_svg(dot_path: Path) -> Optional[Path]:
    executable = shutil.which("dot")
    if executable is None:
        return None
    svg_path = dot_path.with_suffix(".svg")
    subprocess.run([executable, "-Tsvg", str(dot_path), "-o", str(svg_path)], check=True)
    return svg_path



def _object(subject: Optional[str]) -> str:
    if subject is None:
        return "an unknown object"
    if ":" in subject:
        return "unidentified object " + subject
    if is_anonymous_entity(subject):
        return "anonymous road user " + subject
    return subject


SENTENCES = {
    "BRAKE_START": "{actor} started braking",
    "BRAKE_END": "{actor} released the brake",
    "THROTTLE_START": "{actor} pressed the accelerator",
    "THROTTLE_END": "{actor} released the accelerator",
    "TURN_LEFT_START": "{actor} started turning left",
    "TURN_LEFT_END": "{actor} stopped turning left",
    "TURN_RIGHT_START": "{actor} started turning right",
    "TURN_RIGHT_END": "{actor} stopped turning right",
    "INDICATOR_LEFT_START": "{actor} switched on its left turn indicator",
    "INDICATOR_LEFT_END": "{actor} switched off its left turn indicator",
    "INDICATOR_RIGHT_START": "{actor} switched on its right turn indicator",
    "INDICATOR_RIGHT_END": "{actor} switched off its right turn indicator",
    "MOVING_START": "{actor} started moving",
    "MOVING_END": "{actor} stopped moving",
    "STOP_START": "{actor} came to a stop",
    "STOP_END": "{actor} left its stop",
    "SPEED_LIMIT_EXCEEDED_START": "{actor} began exceeding the speed limit",
    "SPEED_LIMIT_EXCEEDED_END": "{actor} returned within the speed limit",
    "TRACK_APPEARED_FRONT": "{actor}'s radar started tracking {subject}, which appeared in front of it",
    "TRACK_APPEARED_LEFT": "{actor}'s radar started tracking {subject}, which appeared on its left",
    "TRACK_APPEARED_RIGHT": "{actor}'s radar started tracking {subject}, which appeared on its right",
    "TRACK_LOST": "{actor}'s radar lost {subject} (its states are UNKNOWN from then on, not ended)",
    "CLOSING_START": "{actor} observed {subject} start closing in",
    "CLOSING_END": "{actor} observed {subject} stop closing in",
    "CRITICAL_TTC_START": "{actor}'s time-to-contact with {subject} became critical",
    "CRITICAL_TTC_END": "{actor}'s time-to-contact with {subject} stopped being critical",
    "EGO_PATH_ENTRY": "{actor} observed {subject} enter its forward path corridor",
    "EGO_PATH_EXIT": "{actor} observed {subject} leave its forward path corridor",
    "CUT_IN_FROM_LEFT_START": "{actor} observed {subject} cutting in from the left",
    "CUT_IN_FROM_LEFT_END": "{actor} observed {subject}'s cut-in from the left settle",
    "CUT_IN_FROM_RIGHT_START": "{actor} observed {subject} cutting in from the right",
    "CUT_IN_FROM_RIGHT_END": "{actor} observed {subject}'s cut-in from the right settle",
    "STOP_SIGN_DETECTED_START": "{actor}'s camera established a STOP sign detection ({subject})",
    "STOP_SIGN_DETECTED_END": "{actor}'s camera stopped detecting STOP sign {subject}",
    "YIELD_SIGN_DETECTED_START": "{actor}'s camera established a YIELD sign detection ({subject})",
    "YIELD_SIGN_DETECTED_END": "{actor}'s camera stopped detecting YIELD sign {subject}",
}


def sentence(event_type: str, actor: Optional[str], subject: Optional[str],
             attributes: Dict[str, Any], participants: Sequence[str] = ()) -> str:
    if event_type == "COLLISION":
        peaks = attributes["peak_impulse"]
        if actor is None:
            return "{0} both recorded this same collision (peak impulses {1} N*s)".format(
                " and ".join(participants),
                ", ".join("{0}: {1:.0f}".format(name, value) for name, value in sorted(peaks.items())))
        return "{0}'s collision sensor recorded a contact (peak impulse {1:.0f} N*s)".format(actor, peaks)
    template = SENTENCES.get(event_type)
    if template is None:
        return "{0}: {1}{2}".format(actor, event_type, " " + _object(subject) if subject else "")
    text = template.format(actor=actor, subject=_object(subject))
    if attributes.get("active_at_first_observation"):
        text += " (already the case when first observed)"
    if attributes.get("relevant_to_ego_path") is False:
        text += " (the detector judged it not relevant to its path)"
    if attributes.get("reacquired"):
        text += " (the same sign reacquired, as camera track {0})".format(attributes.get("sign_track"))
    return text


def _when(t_global: float) -> str:
    if abs(t_global) < 0.005:
        return "At the reference collision"
    if t_global < 0:
        return "{0:.2f} s before the reference collision".format(-t_global)
    return "{0:.2f} s after the reference collision".format(t_global)


def global_sentence(node: GlobalNode) -> str:
    text = sentence(node.event_type, node.actor_id, node.subject_id, node.attributes, node.participants)
    if node.t_global is None:
        return "(unaligned, {0} local time {1:.2f} s) {2}.".format(
            node.observations[0].graph, node.observations[0].t_local, text)
    return "{0}, {1}.".format(_when(node.t_global), text)



def _cell(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return "{0:.2f}".format(value)
    return str(value).replace("|", "/")


def _details(event_type: str, attributes: Dict[str, Any]) -> str:
    parts = []
    for key, value in attributes.items():
        if key in ('estimated_body_corners_vehicle_m','path_frame_heading_rad','target_lateral_speed_mps',
                   'source_local_nodes','semantic_state','initial_state_unannounced'):
            continue
        if isinstance(value, dict):
            value = ", ".join("{0} {1}".format(name, _cell(item)) for name, item in sorted(value.items()))
        parts.append("{0}={1}".format(key, _cell(value)))
    return "; ".join(parts)


def _edge_lines(edges: Iterable[Any]) -> List[str]:
    return ["    {0} --{1}--> {2}".format(edge.from_node, edge.relation, edge.to_node) for edge in edges]


def _final_frame_note(recorder: Dict[str, Any]) -> str:
    end, hz = recorder.get("end_t_local"), recorder.get("trace_hz", 10)
    if end is None or abs(end * hz - round(end * hz)) < 1e-3:
        return ""
    return ", the last one at the recording end ({0:.2f} s)".format(end)


def _context_line(context: Optional[Mapping[str, Any]]) -> str:
    limit = (context or {}).get("speed_limit_kmh")
    if limit is None:
        return "No speed limit was supplied as incident context, so SPEED_LIMIT_EXCEEDED cannot be derived."
    return ("Speed limit {0:g} km/h, supplied as incident context: known a priori, "
            "not perceived and not ground truth.".format(limit))


def _open_state_lines(graph: LocalGraph) -> List[str]:
    lines = ["- {0}{1}, since {2} (t = {3:.2f} s){4}".format(
        item["state"], " of " + item["subject"] if item["subject"] else "", item["since_node"],
        item["since_t_local"], "; the track was lost at {0:.2f} s".format(item["observed_until_t_local"])
        if item["observed_until"] == "TRACK_LOST" else "") for item in open_states(graph)]
    return lines or ["- none"]


def _sign_window_lines(graph: LocalGraph) -> List[str]:
    lines = []
    for sign in ("STOP_SIGN_DETECTED", "YIELD_SIGN_DETECTED"):
        for window in sign_windows(graph, sign):
            end = ("the end of the recording (still in view)" if window["end_t_local"] is None
                   else "{0:.2f} s".format(window["end_t_local"]))
            lines.append("- {0} sign {1}: detected {2:.2f} s -> {3}; relevant to the path: {4}; "
                         "STOP_START inside: {5}{6}".format(
                             sign.split("_")[0], window["sign"], window["start_t_local"], end,
                             window["relevant_to_ego_path"], ", ".join(window["stop_starts_inside"]) or "none",
                             "; already stopped when the window opened" if window["already_stopped_at_start"] else ""))
    return lines or ["- none"]


def _state_cell(state: Optional[Dict[str, Any]]) -> str:
    return "<br>".join(compact_state(state)) or "-"


def _groups(nodes: Sequence[Any], time_of) -> List[List[Any]]:
    groups: List[List[Any]] = []
    for node in nodes:
        if groups and abs(time_of(node) - time_of(groups[-1][0])) < 1e-6:
            groups[-1].append(node)
        else:
            groups.append([node])
    return groups


def _event_names(nodes: Sequence[Any]) -> str:
    return "<br>".join("{0} {1}{2}".format(node.node_id, node.event_type,
                                           " " + node.subject_id if node.subject_id else "") for node in nodes)


def _perceived_state_lines(graph: LocalGraph) -> List[str]:
    lines = ["Each row is the state just BEFORE its events (none of them applied): events at one time are "
             "simultaneous and share it. True states are named, unknown ones end with `?`, false ones are "
             "omitted; a lost track's states are UNKNOWN, never ended. Facts: the trace frame at the time shown.", "",
             "| Local time | Events | Perceived state just before | Facts at |",
             "|-----------:|--------|-----------------------------|---------:|"]
    for group in _groups(graph.nodes, lambda node: node.t_local):
        state = group[0].perceived_state_before
        lines.append("| {0:.2f} | {1} | {2} | {3} |".format(
            group[0].t_local, _event_names(group), _state_cell(state), _cell((state or {}).get("facts_t_local"))))
    return lines


def lost_while_active(graph: LocalGraph) -> List[Dict[str, Any]]:
    out = []
    for node in graph.nodes:
        if node.event_type != "TRACK_LOST":
            continue
        state = ((node.perceived_state_before or {}).get("external") or {}).get(node.subject_id) or {}
        out.append({"node": node.node_id, "track": node.subject_id, "t_local": node.t_local,
                    "active": [name for name in TRACK_STATES if state.get(name) is True]})
    return out


def _lost_lines(graph: LocalGraph) -> List[str]:
    lost = lost_while_active(graph)
    lines = ["- {0} at {1:.2f} s ({2}): {3} were true; they are UNKNOWN afterwards (no END recorded)".format(
        item["track"], item["t_local"], item["node"], ", ".join(item["active"]))
        for item in lost if item["active"]]
    quiet = [item["track"] for item in lost if not item["active"]]
    if quiet:
        lines.append("- lost with no state active: " + ", ".join(quiet))
    return lines or ["- no track was lost"]


def local_graph_markdown(graph: LocalGraph) -> str:
    owner = graph.owner
    clock = graph.recorder.get("clock", {})
    relations: Dict[str, int] = {}
    for edge in graph.edges:
        relations[edge.relation] = relations.get(edge.relation, 0) + 1
    lines = [
        "# Local graph - vehicle {0}".format(owner), "",
        "All times are {0}'s own local clock: `t_local` = seconds since {0}'s first ego sample "
        "(raw clock reading {1} at `t_local` = 0). Only files under `vehicles/{0}/` were read; "
        "external objects are anonymous radar tracks.".format(owner, clock.get("origin_source_timestamp")), "",
        "- Local frame: " + graph.recorder.get("frame", {}).get("definition", "-"),
        "- Trace: {0} frames at {1:g} Hz in `local_trace.jsonl`{2}".format(
            graph.recorder.get("trace_frames"), graph.recorder.get("trace_hz", 10), _final_frame_note(graph.recorder)),
        "- Anonymous radar tracks: {0} (10 Hz samples in `local_tracks.jsonl`)".format(len(graph.tracks)),
        "- " + _context_line(graph.recorder.get("incident_context")),
        "- Nodes: {0}; edges: {1} ({2})".format(len(graph.nodes), len(graph.edges), ", ".join(
            "{0} {1}".format(name, count) for name, count in sorted(relations.items())) or "none"),
        "", "## Nodes", "",
        "| Id | Local time | Type | Actor | Subject | Source | Details |",
        "|----|-----------:|------|-------|---------|--------|---------|",
    ]
    for node in graph.nodes:
        lines.append("| {0} | {1:.2f} | {2} | {3} | {4} | {5} | {6} |".format(
            node.node_id, node.t_local, node.event_type, node.actor_id, _cell(node.subject_id),
            node.source, _details(node.event_type, node.attributes)))
    lines += ["", "Events are state transitions; the quantities behind them (speed, pedals, ranges, TTC, "
              "relative motion, closest approach) are facts in `local_trace.jsonl`. Events with equal times are "
              "simultaneous at the recorder's resolution: PRECEDES links only different times. SAME_TRACK links "
              "a track's TRACK_APPEARED_* to every other event about the same local track (grouping only, no order)."]
    lines += ["", "## Edges", "", "```"] + (_edge_lines(graph.edges) or ["    (none)"]) + ["```", ""]
    lines += ["## Perceived state before each event", ""] + _perceived_state_lines(graph)
    lines += ["", "## States still active when observation ended", ""] + _open_state_lines(graph)
    lines += ["", "## Tracks lost", ""] + _lost_lines(graph)
    lines += ["", "## Temporal safety relations", "",
              "Order of each track's cut-in, critical TTC and path entry and of the collision report, in local "
              "time. Temporal properties only, not causes.", ""]
    relations = temporal_safety_relations(graph)
    lines += ["- {0}: {1}".format(item["track"], describe_temporal_relation(item)) for item in relations] or ["- none"]
    lines += ["", "## Sign detection windows", ""] + _sign_window_lines(graph)
    lines += ["", "An END means this recorder stopped detecting the sign, not that its obligation ended.", ""]
    lines += ["## Anonymous radar tracks", ""]
    if graph.tracks:
        lines += ["| Track | First seen | Last seen | Measured sweeps | First range / bearing | Min range (at) | Last range / bearing | Max speed |",
                  "|-------|-----------:|----------:|----------------:|----------------------|----------------|---------------------|----------:|"]
        for track in graph.tracks:
            lines.append("| {0} | {1:.2f} | {2:.2f} | {3} | {4:.1f} m / {5:+.0f} deg | {6:.2f} m ({7:.2f}) | {8:.1f} m / {9:+.0f} deg | {10:.1f} m/s |".format(
                track["track_id"], track["first_seen_t_local"], track["last_seen_t_local"],
                track["measured_sweeps"], track["first_range_m"], track["first_bearing_deg"],
                track["min_range_m"], track["min_range_t_local"], track["last_range_m"],
                track["last_bearing_deg"], track["max_speed_mps"]))
        lines.append("")
        lines.append("Bearing: positive = to {0}'s right. Ranges are measured from the radar "
                     "to the visible surface of the object.".format(owner))
    else:
        lines.append("No radar track: nothing moving stayed in {0}'s radar view long enough.".format(owner))
    lines += ["", "## Plain-language reading", ""]
    for node in graph.nodes:
        lines.append("- t = {0:.2f} s: {1}.".format(
            node.t_local, sentence(node.event_type, node.actor_id, node.subject_id, node.attributes)))
    if not graph.nodes:
        lines.append("- Nothing noteworthy was recorded.")
    return "\n".join(lines) + "\n"


def _alignment_lines(alignment: Alignment) -> List[str]:
    if alignment.reference_event is None:
        head = ("No collision was matched across recorders, so no local graph could be aligned; every "
                "event keeps only its local time (radar-only alignment is not implemented).")
    else:
        head = ("Reference event: `{0}` (t_global = 0); `t_global = t_local + offset_to_global`. A graph that did "
                "not report it is aligned through the chain of matched collisions linking it to the reference "
                "(multi-hop); its anchor is its own report of the last collision of that chain.".format(
                    alignment.reference_event))
    lines = [head, "",
             "| Graph | Status | Anchor node | Anchor local time | Offset to global | Note |",
             "|-------|--------|-------------|------------------:|-----------------:|------|"]
    for name in sorted(alignment.graphs):
        clock = alignment.graphs[name]
        lines.append("| {0} | {1} | {2} | {3} | {4} | {5} |".format(
            name, clock.status, _cell(clock.anchor_node), _cell(clock.anchor_t_local),
            _cell(clock.offset_to_global), clock.reason))
    offsets = alignment.to_dict()["relative_clock_offsets_s"]
    if offsets:
        lines += ["", "Estimated relative clock offsets: " + ", ".join(
            "{0} = {1:+.3f} s".format(name, value) for name, value in offsets.items())]
    for event in alignment.matched_events:
        lines += ["", "Matched `{0}`: {1}".format(event["event_id"], "; ".join(event["evidence"]))]
    for item in alignment.rejected_matches:
        lines += ["", "Rejected match {0}: impulses agree, but {1}".format(
            " / ".join("{0}:{1}".format(graph, node) for graph, node in sorted(item["nodes"].items())),
            item["reason"])]
    return lines


def _association_lines(associations: Sequence[Association]) -> List[str]:
    if not associations:
        return ["No anonymous track to associate."]
    lines = ["| Local track | Global entity | Status | Confidence | Evidence |",
             "|-------------|---------------|--------|-----------:|----------|"]
    for item in associations:
        lines.append("| {0}:{1} | {2} | {3} | {4} | {5} |".format(
            item.local_graph, item.local_track, item.global_entity, item.status,
            _cell(item.confidence), "<br>".join(item.evidence)))
    return lines


def _relation_lines(relations: Optional[Sequence[Dict[str, Any]]]) -> List[str]:
    lines = []
    for item in relations or []:
        who = item["entity"] if item["association"] == ASSOCIATED else "unidentified " + item["entity"]
        when = ", ".join("{0} {1:+.2f}".format(key, value) for key, value in item.get("t_global", {}).items())
        lines.append("- {0}'s {1} ({2}): {3}{4}".format(
            item["recorder"], item["track"], who, describe_temporal_relation(item),
            " [local times; t_global: {0}]".format(when) if when else " [local times]"))
    return lines or ["- none"]


def global_graph_markdown(title: str, graph: GlobalGraph, alignment: Alignment,
                          associations: Sequence[Association], trace: Sequence[Dict[str, Any]],
                          context: Optional[Mapping[str, Any]] = None,
                          relations: Optional[Sequence[Dict[str, Any]]] = None) -> str:
    lines = ["# Global graph - " + title, "",
             "Global time `t_global` is 0 at the reference collision. The local graphs were "
             "not modified: every node lists the local node(s) and local time(s) it comes from.", "",
             _context_line(context), "",
             "## Entities", "", "| Entity | Kind | Details |", "|--------|------|---------|"]
    for entity in graph.entities:
        if entity["kind"] == "recorder":
            detail = "clock {0}; observed by others as: {1}".format(
                entity["clock"], ", ".join(entity["observed_as"]) or "-")
        else:
            detail = "anonymous; observed by {0} as {1}".format(", ".join(entity["observed_by"]),
                                                                ", ".join(entity["observed_as"]))
        lines.append("| {0} | {1} | {2} |".format(entity["entity_id"], entity["kind"], detail))
    lines += ["", "## Graph alignment", ""] + _alignment_lines(alignment)
    lines += ["", "## Identity associations", ""] + _association_lines(associations)
    lines += ["", "## Nodes", "",
              "| Id | Global time | Type | Actor | Subject / participants | Observed by (local node @ local time) | Details |",
              "|----|------------:|------|-------|------------------------|----------------------------------------|---------|"]
    for node in graph.nodes:
        subject = ", ".join(node.participants) if node.actor_id is None else _cell(node.subject_id)
        provenance = ", ".join("{0} @ {1:.2f}".format(obs.local_node, obs.t_local) for obs in node.observations)
        lines.append("| {0} | {1} | {2} | {3} | {4} | {5} | {6} |".format(
            node.node_id, _cell(node.t_global), node.event_type, _cell(node.actor_id), subject,
            provenance, _details(node.event_type, node.attributes)))
    lines += ["", "## Edges", "", "```"] + (_edge_lines(graph.edges) or ["    (none)"]) + ["```"]
    lines += ["", "## Global trace", "",
              "Events in one row are simultaneous at 0.05 s resolution: their order is unresolved.", "",
              "| t_global | Events |", "|---------:|--------|"]
    for row in trace:
        lines.append("| {0:+.2f} | {1} |".format(row["t_global"], row["text"]))
    lines += ["", "## Temporal safety relations", "",
              "Per track: does the cut-in start before the critical TTC, or was the critical TTC already active? "
              "Is the path entry before or after it? Temporal properties only, not causes.", ""]
    lines += _relation_lines(relations)
    lines += ["", "## Perceived state before each event, per observing recorder", "",
              "Each recorder's own belief just before its events, in its own local names (track_001, ...): "
              "fusion does not rewrite it. True states are named, unknown ones end with `?`.", "",
              "| t_global | Recorder | Events (local node) | Perceived state just before |",
              "|---------:|----------|---------------------|-----------------------------|"]
    for t_global, recorder, nodes in _belief_rows(graph):
        lines.append("| {0} | {1} | {2} | {3} |".format(
            "-" if t_global is None else "{0:+.2f}".format(t_global), recorder,
            "<br>".join("{0} {1} ({2})".format(node.node_id, short_label(node), next(
                obs.local_node for obs in node.observations if obs.graph == recorder)) for node in nodes),
            _state_cell(nodes[0].perceived_state_before.get(recorder))))
    lines += ["", "## Plain-language reading", ""]
    lines += ["- " + global_sentence(node) for node in graph.nodes] or ["- Nothing to report."]
    return "\n".join(lines) + "\n"


def _belief_rows(graph: GlobalGraph) -> List[Any]:
    rows: List[Any] = []
    index: Dict[Any, int] = {}
    for node in graph.nodes:
        for obs in node.observations:
            if obs.graph not in node.perceived_state_before:
                continue
            key = (obs.graph, round(obs.t_local, 4))
            if key not in index:
                index[key] = len(rows)
                rows.append((node.t_global, obs.graph, []))
            rows[index[key]][2].append(node)
    return rows



def _quote(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _dot(name: str, title: str, nodes: Sequence[Dict[str, Any]], edges: Iterable[Any]) -> str:
    lines = ["digraph {0} {{".format(_quote(name)),
             "  graph [rankdir=LR, labelloc=t, fontname=Helvetica, label={0}];".format(_quote(title)),
             "  node [shape=box, style=\"rounded,filled\", fontname=Helvetica, fontsize=10];",
             "  edge [fontname=Helvetica, fontsize=8];"]
    same_time: Dict[str, List[str]] = {}
    for node in nodes:
        extra = ", peripheries=2" if node.get("merged") else ""
        lines.append("  {0} [label={1}, fillcolor={2}{3}];".format(
            _quote(node["id"]), _quote("\n".join(node["label"])).replace("\n", "\\n"),
            _quote(KIND_COLOURS.get(node["kind"], "#ffffff")), extra))
        if node.get("time") is not None:
            same_time.setdefault(node["time"], []).append(node["id"])
    for ids in same_time.values():
        if len(ids) > 1:
            lines.append("  {{rank=same; {0};}}".format("; ".join(_quote(item) for item in ids)))
    for edge in edges:
        style = "" if edge.relation == "PRECEDES" else ", style=dashed, color=\"#2563eb\", constraint=false"
        lines.append("  {0} -> {1} [label={2}{3}];".format(
            _quote(edge.from_node), _quote(edge.to_node), _quote(edge.relation), style))
    lines.append("}")
    return "\n".join(lines) + "\n"


def _dot_label(event_type: str, who: str, when: Optional[str], attributes: Dict[str, Any]) -> List[str]:
    return [event_type, who, "unaligned" if when is None else "t=" + when]


def local_graph_dot(graph: LocalGraph) -> str:
    nodes = []
    for node in graph.nodes:
        who = node.actor_id + (" -> " + node.subject_id if node.subject_id else "")
        nodes.append({"id": node.node_id, "kind": node.kind, "time": "{0:.4f}".format(node.t_local),
                      "label": _dot_label(node.event_type, who, "{0:.2f}".format(node.t_local), node.attributes)})
    return _dot("local_" + graph.owner, "Local graph - vehicle {0} (local time)".format(graph.owner),
                nodes, graph.edges)


def global_graph_dot(title: str, graph: GlobalGraph) -> str:
    nodes = []
    for node in graph.nodes:
        who = " + ".join(node.participants) if node.actor_id is None else (
            node.actor_id + (" -> " + node.subject_id if node.subject_id else ""))
        when = None if node.t_global is None else "{0:+.2f}".format(node.t_global)
        nodes.append({"id": node.node_id, "kind": node.kind,
                      "time": None if node.t_global is None else "{0:.4f}".format(node.t_global),
                      "label": _dot_label(node.event_type, who, when, node.attributes),
                      "merged": len(node.observations) > 1})
    return _dot("global", "Global graph - {0} (t=0 at the reference collision)".format(title), nodes, graph.edges)



def _road_user_lines(road_users: Optional[Mapping[str, Any]]) -> List[str]:
    if not road_users:
        return ["Not computed."]
    lines = []
    for item in road_users.get("observed_alignment", []):
        if item.get("method") == "reference_recorder":
            lines.append("- No matched collision: {0}'s own clock defines t_global.".format(item["recorder"]))
            continue
        lines.append("- Observed-trajectory alignment of {0}: {1} (offset {2}, pooled median {3} sigma{4}){5}.".format(
            item["recorder"], "accepted" if item["accepted"] else "refused", _cell(item.get("offset_to_global")),
            _cell(item.get("median_distance_sigma")),
            ", interval {0}".format(item["interval"]) if item.get("interval") else "",
            "" if item["accepted"] else ": " + item.get("reason", "")))
    for link in road_users.get("recorder_links", []):
        lines.append("- {0} is {1}: its returns lie on {1}'s own footprint (median {2:.2f} m over {3} samples, "
                     "{4:.0%} within 3 sigma) at {1}'s velocity.".format(
                         link["track"], link["recorder"], link["median_distance_m"], link["samples"],
                         link["fraction_within"]))
    for entity in road_users.get("entities", []):
        links = entity["association"]["links"]
        lines.append("- {0} (anonymous, {1} to {2} s): {3}{4}; footprint {5:.2f} x {6:.2f} m ({7}/{8}); "
                     "fusion {9}.".format(
                         entity["id"], _cell(entity["time_span"][0]), _cell(entity["time_span"][1]),
                         ", ".join(entity["source_tracks"]),
                         "" if not links else " joined by " + "; ".join(
                             "{0} {1}-{2} ({3:.0%} of {4} instants)".format(
                                 "stitch" if link["kind"] == "stitch" else "same box",
                                 link["a"], link["b"], link["passed"], link["compared"]) for link in links),
                         entity["footprint"]["length_m"], entity["footprint"]["width_m"],
                         entity["footprint"]["length"]["source"], entity["footprint"]["width"]["source"],
                         entity["fusion_method"]))
    return lines or ["- no anonymous track of an aligned recorder"]


def report_markdown(title: str, locals_: Sequence[Any], alignment: Alignment,
                    associations: Sequence[Association], graph: GlobalGraph,
                    trace: Sequence[Dict[str, Any]], config: Dict[str, Any],
                    context: Optional[Mapping[str, Any]] = None,
                    relations: Optional[Sequence[Dict[str, Any]]] = None,
                    road_users: Optional[Mapping[str, Any]] = None) -> str:
    lines = ["# Reconstruction report - " + title, "",
             "Inputs: `vehicles/{0}/` (vehicle-local files) and the supplied `incident_context.json`. "
             "`ground_truth/` and the run's `metadata.json` were not read; the privileged comparison, "
             "if run, is in `evaluation/`.".format("/`, `vehicles/".join(local.owner for local in locals_)), "",
             _context_line(context), "",
             "Pipeline: raw log -> local trace -> local graph (each recorder alone, own clock, own frame) "
             "-> graph-level alignment -> identity association -> road users in the common frame of the "
             "recorders' own pose streams -> global graph.", "",
             "## Local reconstructions", "",
             "| Recorder | Duration (local) | Trace frames | Graph nodes | Graph edges | Radar tracks | Collision reports (local time) |",
             "|----------|-----------------:|-------------:|------------:|------------:|-------------:|-------------------------------|"]
    for local in locals_:
        collisions = ["{0} @ {1:.2f} s".format(node.node_id, node.t_local)
                      for node in local.graph.nodes if node.event_type == "COLLISION"]
        lines.append("| {0} | {1:.2f} s | {2} | {3} | {4} | {5} | {6} |".format(
            local.owner, local.ego.end - local.ego.start, len(local.trace), len(local.graph.nodes), len(local.graph.edges),
            len(local.tracks), ", ".join(collisions) or "none"))
    lines += ["", "## Graph alignment", ""] + _alignment_lines(alignment)
    lines += ["", "## Identity associations", ""] + _association_lines(associations)
    lines += ["", "## Road users in the common frame", ""] + _road_user_lines(road_users)
    merged = [node for node in graph.nodes if len(node.observations) > 1]
    lines += ["", "## Global graph", "",
              "{0} nodes, {1} edges; {2} merged node(s): {3}.".format(
                  len(graph.nodes), len(graph.edges), len(merged),
                  ", ".join("{0} {1} from {2}".format(node.node_id, short_label(node), " + ".join(
                      obs.local_node for obs in node.observations)) for node in merged) or "none"),
              "", "### Event sequence (global time)", ""]
    lines += ["- `{0:+.2f}` {1}".format(row["t_global"], row["text"]) for row in trace] or ["- (none)"]
    lines += ["", "### What happened, in plain language", ""]
    lines += ["- " + global_sentence(node) for node in graph.nodes] or ["- Nothing to report."]
    simultaneous = [row["text"] for row in trace if len(row["events"]) > 1]
    lines += ["", "### Temporal safety relations", "",
              "CUT_IN_START < CRITICAL_TTC_START < COLLISION, or CRITICAL_TTC_START <= CUT_IN_START (critical TTC "
              "already active), and EGO_PATH_ENTRY before/after the critical TTC. Temporal order only, not causes.", ""]
    lines += _relation_lines(relations)
    lines += ["", "### Simultaneous events (order unresolved at 0.05 s)", ""]
    lines += ["- " + text for text in simultaneous] or ["- none"]
    lines += ["", "### States still active when observation ended", ""]
    for local in locals_:
        lines += ["{0}:".format(local.owner)] + _open_state_lines(local.graph)
    lines += ["", "### Sign detection windows", ""]
    for local in locals_:
        lines += ["{0}:".format(local.owner)] + _sign_window_lines(local.graph)
    lines += ["", "### Perceived state just before each collision report", ""]
    reported = False
    for local in locals_:
        for node in local.graph.nodes:
            if node.event_type == "COLLISION":
                reported = True
                lines.append("- {0} {1} at {2:.2f} s (local): {3}".format(
                    local.owner, node.node_id, node.t_local, "; ".join(compact_state(node.perceived_state_before))))
    if not reported:
        lines.append("- no collision was reported")
    lines += ["", "### Tracks lost while a state was active", "",
              "A lost track's states become UNKNOWN: the recorder can no longer tell whether they ended.", ""]
    for local in locals_:
        lines += ["{0}:".format(local.owner)] + _lost_lines(local.graph)

    notes = []
    for local in locals_:
        if not local.tracks:
            notes.append("{0} built no radar track: nothing moving stayed in its radar view "
                         "long enough, so {0} has no perception of the others.".format(local.owner))
    for item in associations:
        if item.status != ASSOCIATED:
            notes.append("{0}:{1} stays anonymous{2}: {3}.".format(
                item.local_graph, item.local_track,
                " ({0})".format(item.global_entity) if item.global_entity != item.local_graph + ":" + item.local_track
                else "", "; ".join(item.blocking) or "insufficient evidence"))
    for name in sorted(alignment.graphs):
        if alignment.graphs[name].status != "ALIGNED":
            notes.append("{0} is UNALIGNED: {1}.".format(name, alignment.graphs[name].reason))
    notes.append("Global time rests on matched collisions (t_global = 0 at the reference one) and a constant "
                 "offset per recorder; clock drift is not modelled, so timing uncertainty grows away from the "
                 "collisions that align each recorder.")
    notes.append("Radar tracks follow the visible surface of an object, not its centre, and a "
                 "straight-ahead corridor is used for 'in path'.")
    lines += ["", "## Uncertainty and limitations", ""] + ["- " + note for note in notes]

    lines += ["", "## Files", "",
              "- Local: `<recorder>/local_trace.jsonl`, `local_tracks.jsonl`, `local_graph.json|md|dot`",
              "- Global: `global/alignment.json`, `associations.json`, `anonymous_entities.json`, "
              "`global_trace.jsonl`, `global_graph.json|md|dot`", "",
              "## Parameters", "", "```", json.dumps(config, indent=2), "```"]
    return "\n".join(lines) + "\n"
