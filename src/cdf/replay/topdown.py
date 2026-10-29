"""Headless top-down rendering of a replay, for keyframe export and visual QA (reconstruction only).

``render_frame`` draws what ``ReplayRun`` holds at one instant of the replay clock (t_global): the
recorders at the poses of their pose source with their own footprints and a short trail; every anonymous
road user of the fusion (U1, U2, ...) once, as a box of its fitted footprint at the fused position and
heading (solid while measured, dashed while only predicted) with a dotted circle of twice its position
uncertainty when that exceeds 0.3 m, and the radar points of the tracks it fuses as small dots in their
observers' colours; a track the fusion associated with a recorder as a dot linked to its observer, never
a second body; a track that is neither (none after the fusion) as a ghost box of the nominal size; the
recorders' states of the paper's core view
(CRITICAL_TTC red, CUT_IN orange, IN_EGO_PATH yellow, BRAKE), exact at event instants from the local
graphs' START/END events; the reconstructed core events of the
last half second and the collisions.  The driving lanes come from the public OpenDRIVE geometry of the
recognised map when lanes are given (``lanes_from_map``), marked on their boundaries: dashed between
adjacent lanes, solid at the road edge.

The inputs are those of ``ReplayRun`` only: nothing privileged is read.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from ..common.opendrive import LaneSample
from ..reconstruction.models import PAPER_CORE_EVENTS
from .model import DEFAULT_FOOTPRINT, HEADING_UNKNOWN, ReplayRun, rotate
from .presentation import anonymous_row, subject_label

RECORDER_COLOURS = ("#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd", "#8c564b", "#e377c2", "#17becf", "#bcbd22")
ROAD_USER_COLOUR = "#3a3a3a"  # an anonymous road user belongs to no observer
UNCERTAINTY_MIN_M = 0.3  # the 2-sigma circle is drawn only when it says something
STATE_COLOURS = {"CRITICAL_TTC": "#d62728", "CUT_IN_FROM_LEFT": "#f4a100", "CUT_IN_FROM_RIGHT": "#f4a100",
                 "IN_EGO_PATH": "#e9c46a"}
TRACK_HIGHLIGHTS = ("CRITICAL_TTC", "CUT_IN_FROM_LEFT", "CUT_IN_FROM_RIGHT", "IN_EGO_PATH")
EVENT_WINDOW_S = 0.5  # core events shown: those of the last half second
TRAIL_S = 2.0  # recorded path drawn behind each recorder
KEY_STARTS = ("CRITICAL_TTC_START", "CUT_IN_FROM_LEFT_START", "CUT_IN_FROM_RIGHT_START", "EGO_PATH_ENTRY")


def lanes_from_map(carla_map: Any, spacing: float = 2.0) -> List[LaneSample]:
    """Driving-lane stretches of a client-side ``carla.Map`` (the public OpenDRIVE geometry)."""
    lanes = []
    for waypoint in carla_map.generate_waypoints(spacing):
        transform = waypoint.transform
        lanes.append(LaneSample(transform.location.x, transform.location.y, transform.rotation.yaw,
                                float(waypoint.lane_width), spacing * 1.2))
    return lanes


@dataclass(frozen=True)
class Keyframe:
    label: str
    time: float  # replay time


def keyframes(run: ReplayRun, lead_s: float = 3.0, after_s: float = 0.5, before_s: float = 0.2,
              merge_s: float = 0.01) -> List[Keyframe]:
    """Instants worth looking at, from the reconstructed events only: a few seconds before the first
    important event, every CRITICAL_TTC / CUT_IN start and end and EGO_PATH_ENTRY up to one second after
    the last collision, and each collision just before, at and just after it."""
    collisions = sorted(run.collisions, key=lambda mark: mark.time)
    horizon = collisions[-1].time + 1.0 if collisions else run.duration
    marks: List[Tuple[str, float]] = []
    for event in run.display_events():
        if event.time > horizon + 1e-6:
            continue
        if event.event_type in KEY_STARTS or event.event_type in ("CRITICAL_TTC_END", "CUT_IN_FROM_LEFT_END",
                                                                  "CUT_IN_FROM_RIGHT_END"):
            subject = run.subject_name(event.actor, event.subject)
            marks.append(("{0}({1}{2})".format(event.event_type, event.actor, "," + subject if subject else ""),
                          event.time))
    for mark in collisions:
        names = ",".join(mark.participants)
        marks += [("before COLLISION({0})".format(names), mark.time - before_s),
                  ("COLLISION({0})".format(names), mark.time), ("after COLLISION({0})".format(names), mark.time + after_s)]
    if marks:
        marks.append(("lead-in", min(time for _, time in marks) - lead_s))
    merged: List[Tuple[str, float]] = []
    for label, time in sorted(((label, min(max(time, 0.0), run.duration)) for label, time in marks),
                              key=lambda item: item[1]):
        if merged and time - merged[-1][1] <= merge_s + 1e-6:
            merged[-1] = (merged[-1][0] + "; " + label, merged[-1][1])
        else:
            merged.append((label, time))
    return [Keyframe(label, round(time, 6)) for label, time in merged]


def _footprint_world(pose: Any, footprint: Any) -> List[Tuple[float, float]]:
    fp = footprint or DEFAULT_FOOTPRINT
    corners = ((fp.x_max, fp.y_min), (fp.x_max, fp.y_max), (fp.x_min, fp.y_max), (fp.x_min, fp.y_min))
    out = []
    for x, y in corners:
        dx, dy = rotate(x, y, pose.yaw)
        out.append((pose.x + dx, pose.y + dy))
    return out


def _box(centre: Tuple[float, float], yaw: float, length: float, width: float) -> List[Tuple[float, float]]:
    out = []
    for x, y in ((length / 2, -width / 2), (length / 2, width / 2), (-length / 2, width / 2), (-length / 2, -width / 2)):
        dx, dy = rotate(x, y, yaw)
        out.append((centre[0] + dx, centre[1] + dy))
    return out


def lane_markings(lanes: Sequence[LaneSample], line_width: float = 0.12,
                  dash: float = 0.5) -> Tuple[List[List[Tuple[float, float]]], List[List[Tuple[float, float]]]]:
    """White markings on the lane boundaries, not the centres: (dashed between adjacent lanes, solid road edges).

    A boundary is shared when another lane's centre lies one lane width beyond it on that side."""
    dashed, solid = [], []
    for lane in lanes:
        for side in (1.0, -1.0):
            ox, oy = rotate(0.0, side * lane.width / 2.0, lane.yaw)
            beyond_x, beyond_y = lane.x + 2.0 * ox, lane.y + 2.0 * oy
            shared = any(other is not lane and math.hypot(other.x - beyond_x, other.y - beyond_y) < 0.35 * lane.width
                         for other in lanes)
            centre = (lane.x + ox, lane.y + oy)
            if shared:
                dashed.append(_box(centre, lane.yaw, lane.length * dash, line_width))
            else:
                solid.append(_box(centre, lane.yaw, lane.length, line_width))
    return dashed, solid


def states_at(run: ReplayRun, recorder: str, t: float) -> Tuple[List[str], Dict[str, List[str]]]:
    """(own states, track id -> states) of a recorder active at ``t``, from the START/END (ENTRY/EXIT)
    events of its local graph: exact at event instants, where the 10 Hz perceived-state trace is not."""
    own: List[str] = []
    tracks: Dict[str, List[str]] = {}
    for interval in run.active_states(recorder, t):
        name = "IN_EGO_PATH" if interval.state == "EGO_PATH" else interval.state
        if interval.subject is None:
            own.append(name)
        else:
            tracks.setdefault(interval.subject, []).append(name)
    return own, tracks


def frame_items(run: ReplayRun, t: float) -> Dict[str, Any]:
    """What a frame at ``t`` shows, as plain data (also used by the QA checks)."""
    recorders, ghosts, associated, members, entities = [], [], [], [], []
    for index, participant in enumerate(run.participants):
        pid = participant.participant_id
        pose = participant.trajectory.pose_at(run.start + t)  # trajectories run on the clock, t is replay time
        own, external = states_at(run, pid, t)
        recorders.append({"id": pid, "colour": RECORDER_COLOURS[index % len(RECORDER_COLOURS)], "pose": pose,
                          "body": _footprint_world(pose, participant.footprint), "states": own})
        for track in run.tracks.get(pid, []):
            point = track.state_at(t)
            if point is None:
                continue
            flags = [name for name in TRACK_HIGHLIGHTS if name in external.get(track.track_id, [])]
            item = {"observer": pid, "track": track, "point": point, "states": flags,
                    "colour": RECORDER_COLOURS[index % len(RECORDER_COLOURS)]}
            if track.road_user is not None:
                members.append(item)  # drawn through its road user's single box
            elif track.ghost:
                item["box"] = _box(point.centre, point.yaw, run.geometry.length, run.geometry.width)
                ghosts.append(item)
            else:
                associated.append(item)
    poses = {r["id"]: r["pose"] for r in recorders}
    for entity, state in run.entities_at(t):
        own = [m for m in members if m["track"].road_user == entity.entity_id]
        flags = [name for name in TRACK_HIGHLIGHTS if any(name in m["states"] for m in own)]
        yaw = state.yaw
        if yaw is None:  # no heading known: parallel to its first observer, as the CRITICAL_TTC model takes it
            yaw = next((poses[o].yaw for o in state.observers if o in poses), 0.0)
        entities.append({"entity": entity, "state": state, "yaw": yaw, "states": flags,
                         "box": _box(state.centre, yaw, entity.length, entity.width),
                         "observers": sorted({m["observer"] for m in own})})
    return {"recorders": recorders, "ghosts": ghosts, "associated": associated, "members": members,
            "entities": entities}


def _extent(items: Dict[str, Any], minimum: float = 22.0, margin: float = 10.0) -> Tuple[float, float, float]:
    xs = ([r["pose"].x for r in items["recorders"]] + [g["point"].centre[0] for g in items["ghosts"]]
          + [e["state"].centre[0] for e in items.get("entities", [])])
    ys = ([r["pose"].y for r in items["recorders"]] + [g["point"].centre[1] for g in items["ghosts"]]
          + [e["state"].centre[1] for e in items.get("entities", [])])
    cx, cy = (min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0
    half = max(minimum, (max(xs) - min(xs)) / 2.0 + margin, (max(ys) - min(ys)) / 2.0 + margin)
    return cx, cy, half


def render_frame(run: ReplayRun, t: float, path: Path, lanes: Optional[Sequence[LaneSample]] = None,
                 label: str = "", extent: Optional[Tuple[float, float, float]] = None, dpi: int = 100) -> Dict[str, Any]:
    """Draw the replay at replay time ``t`` into ``path`` (PNG, SVG or PDF by suffix); returns the items."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    from matplotlib.patches import Circle, Polygon

    items = frame_items(run, t)
    cx, cy, half = extent or _extent(items)
    figure = plt.figure(figsize=(15.0, 8.4), dpi=dpi)
    ax = figure.add_axes([0.01, 0.03, 0.60, 0.88])
    panel = figure.add_axes([0.62, 0.03, 0.37, 0.88])
    panel.axis("off")
    ax.set_facecolor("#f4f1ea")
    if lanes:
        near = [lane for lane in lanes if abs(lane.x - cx) <= half + 5 and abs(lane.y - cy) <= half + 5]
        ax.add_collection(PolyCollection([_box((lane.x, lane.y), lane.yaw, lane.length, lane.width) for lane in near],
                                         facecolors="#cfcfcf", edgecolors="none", zorder=0))
        dashed, solid = lane_markings(near)
        ax.add_collection(PolyCollection(dashed + solid, facecolors="#ffffff", edgecolors="none", zorder=1))
    for participant, recorder in zip(run.participants, items["recorders"]):
        trail = [participant.trajectory.pose_at(run.start + t - TRAIL_S * k / 20.0) for k in range(21)]
        ax.plot([p.x for p in trail], [p.y for p in trail], color=recorder["colour"], lw=1.0, alpha=0.5, zorder=2)
        ax.add_patch(Polygon(recorder["body"], closed=True, facecolor=recorder["colour"], edgecolor="black",
                             lw=1.2, alpha=0.9, zorder=5))
        pose = recorder["pose"]
        hx, hy = rotate(3.2, 0.0, pose.yaw)
        ax.annotate("", xy=(pose.x + hx, pose.y + hy), xytext=(pose.x, pose.y),
                    arrowprops=dict(arrowstyle="->", color="black", lw=1.2), zorder=6)
        ax.text(pose.x, pose.y, recorder["id"], ha="center", va="center", fontsize=11, fontweight="bold",
                color="white", zorder=7)
    for ghost in items["ghosts"]:
        point, colour = ghost["point"], ghost["colour"]
        edge = STATE_COLOURS["CRITICAL_TTC"] if "CRITICAL_TTC" in ghost["states"] else (
            STATE_COLOURS["CUT_IN_FROM_LEFT"] if any(s.startswith("CUT_IN") for s in ghost["states"]) else colour)
        ax.add_patch(Polygon(ghost["box"], closed=True, fill=False, edgecolor=edge,
                             lw=3.0 if edge != colour else 1.6, ls="-" if point.measured else "--", zorder=4))
        if "IN_EGO_PATH" in ghost["states"]:
            ax.add_patch(Polygon(ghost["box"], closed=True, facecolor=STATE_COLOURS["IN_EGO_PATH"], alpha=0.25,
                                 edgecolor="none", zorder=3))
        if point.heading != HEADING_UNKNOWN:
            hx, hy = rotate(2.6, 0.0, point.yaw)
            ax.annotate("", xy=(point.centre[0] + hx, point.centre[1] + hy), xytext=point.centre,
                        arrowprops=dict(arrowstyle="->", color=colour, lw=1.0), zorder=4)
        ax.text(point.centre[0], point.centre[1] - 1.8, ghost["track"].name, ha="center", fontsize=7, color=colour,
                zorder=8)
    for item in items["entities"]:
        entity, state = item["entity"], item["state"]
        edge = STATE_COLOURS["CRITICAL_TTC"] if "CRITICAL_TTC" in item["states"] else (
            STATE_COLOURS["CUT_IN_FROM_LEFT"] if any(name.startswith("CUT_IN") for name in item["states"])
            else ROAD_USER_COLOUR)
        ax.add_patch(Polygon(item["box"], closed=True, facecolor="#9a9a9a", alpha=0.35, edgecolor="none", zorder=3))
        if "IN_EGO_PATH" in item["states"]:
            ax.add_patch(Polygon(item["box"], closed=True, facecolor=STATE_COLOURS["IN_EGO_PATH"], alpha=0.35,
                                 edgecolor="none", zorder=3))
        ax.add_patch(Polygon(item["box"], closed=True, fill=False, edgecolor=edge,
                             lw=3.0 if edge != ROAD_USER_COLOUR else 1.8, ls="-" if state.measured else "--", zorder=4))
        if state.heading != HEADING_UNKNOWN and state.yaw is not None:
            hx, hy = rotate(entity.length / 2.0 + 1.2, 0.0, state.yaw)
            ax.annotate("", xy=(state.centre[0] + hx, state.centre[1] + hy), xytext=state.centre,
                        arrowprops=dict(arrowstyle="->", color=ROAD_USER_COLOUR, lw=1.2), zorder=4)
        ax.text(state.centre[0], state.centre[1], entity.entity_id, ha="center", va="center", fontsize=10,
                fontweight="bold", color=ROAD_USER_COLOUR, zorder=8)
    for item in items["members"]:
        ax.plot([item["point"].position[0]], [item["point"].position[1]], marker="o", ms=3.5, color=item["colour"],
                markeredgecolor="white", markeredgewidth=0.5, alpha=0.9 if item["point"].measured else 0.4, zorder=7)
    for item in items["associated"]:
        point, colour = item["point"], item["colour"]
        observer = next(r["pose"] for r in items["recorders"] if r["id"] == item["observer"])
        critical = "CRITICAL_TTC" in item["states"]
        ax.plot([observer.x, point.position[0]], [observer.y, point.position[1]],
                color=STATE_COLOURS["CRITICAL_TTC"] if critical else colour, lw=2.4 if critical else 0.8,
                ls="-" if critical else ":", zorder=3)
        ax.plot([point.position[0]], [point.position[1]], marker="o", ms=4, color=colour, zorder=8)
    now = [mark for mark in run.collisions if abs(mark.time - t) <= 0.05 + 1e-6]
    for mark in now:
        poses = [r["pose"] for r in items["recorders"] if r["id"] in mark.participants]
        if poses:
            ax.plot([sum(p.x for p in poses) / len(poses)], [sum(p.y for p in poses) / len(poses)], marker="*",
                    ms=26, color="#d62728", markeredgecolor="black", zorder=9)
    ax.plot([cx - half + 3, cx - half + 13], [cy + half - 3, cy + half - 3], color="black", lw=2.5, zorder=9)
    ax.text(cx - half + 8, cy + half - 4.2, "10 m", ha="center", fontsize=8, zorder=9)
    ax.set_xlim(cx - half, cx + half)
    ax.set_ylim(cy + half, cy - half)  # CARLA's y points to the right of x: drawn downwards
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])

    clock = "t_global" if run.clock == "t_global" else "t"
    lines = [(run.name, "black", "bold"), ("{0} = {1:+.2f} s".format(clock, run.display_time(t)), "black", "bold")]
    if label:
        lines += [(text.strip(), "#555555", "normal") for text in _wrap(label, 62)]
    if now:
        lines.append(("COLLISION " + ", ".join(",".join(m.participants) for m in now), "#d62728", "bold"))
    lines.append(("", "black", "normal"))
    for recorder in items["recorders"]:
        pid = recorder["id"]
        states = [name for name in recorder["states"] if name == "BRAKE"]
        tracked = [(g["track"].track_id, g["states"]) for g in items["ghosts"] + items["associated"] + items["members"]
                   if g["observer"] == pid and g["states"]]
        lines.append(("{0}: {1}".format(pid, ", ".join(states) or "-"), recorder["colour"], "bold"))
        entity_states = {}
        for track_id, states_of in tracked:
            entity_states.setdefault(subject_label(run,pid,track_id),set()).update(states_of)
        for entity_id, states_of in sorted(entity_states.items()):
            lines.append(("   {0}: {1}".format(entity_id, ", ".join(sorted(states_of))),
                          STATE_COLOURS["CRITICAL_TTC"] if "CRITICAL_TTC" in states_of else "black", "normal"))
    if items["entities"]:
        lines.append(("", "black", "normal"))
        lines.append(("anonymous road users:", ROAD_USER_COLOUR, "bold"))
        for item in items["entities"]:
            entity, state = item["entity"], item["state"]
            lines.append((anonymous_row(entity.entity_id, state.observers), ROAD_USER_COLOUR, "normal"))
    if run.hidden:
        lines.append(("not on the global timeline: " + ", ".join(run.hidden), "#555555", "normal"))
    recent = [event for event in run.display_events()
              if t - EVENT_WINDOW_S < event.time <= t + 1e-6 and event.event_type in PAPER_CORE_EVENTS]
    if recent:
        lines.append(("", "black", "normal"))
        lines.append(("core events of the last {0:.1f} s:".format(EVENT_WINDOW_S), "black", "bold"))
        for event in recent[-12:]:
            subject = subject_label(run, event.actor, event.subject)
            lines.append(("  {0:+.2f} {1} {2}{3}".format(run.display_time(event.time), event.event_type, event.actor,
                                                         " -> " + subject if subject else ""), "black", "normal"))
    y = 1.0
    for text, colour, weight in lines:
        panel.text(0.0, y, text, fontsize=9.5, color=colour, fontweight=weight, va="top", family="monospace")
        y -= 0.037
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(str(path), dpi=dpi)
    plt.close(figure)
    return items


def _wrap(text: str, width: int) -> List[str]:
    words, lines, current = text.split(" "), [], ""
    for word in words:
        if current and len(current) + 1 + len(word) > width:
            lines.append(current)
            current = word
        else:
            current = (current + " " + word).strip()
    if current:
        lines.append(current)
    return lines


def export_keyframes(run: ReplayRun, directory: Path, lanes: Optional[Sequence[LaneSample]] = None,
                     times: Optional[Sequence[Tuple[str, float]]] = None, suffix: str = ".png") -> List[Dict[str, Any]]:
    """Render ``times`` ((label, replay time) pairs; by default ``keyframes``) into ``directory``."""
    frames = [Keyframe(label, time) for label, time in times] if times is not None else keyframes(run)
    out = []
    for index, frame in enumerate(frames, 1):
        name = "{0:02d}_tg{1:+07.2f}{2}".format(index, run.display_time(frame.time), suffix).replace("+", "p").replace("-", "m")
        render_frame(run, frame.time, Path(directory) / name, lanes=lanes, label=frame.label)
        out.append({"file": name, "label": frame.label, "replay_time": frame.time,
                    "display_time": run.display_time(frame.time)})
    return out
