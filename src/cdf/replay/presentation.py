
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Sequence, Tuple


HELP_LINES = (
    "SPACE play/pause   ←/→ seek   N/P event   C camera (overview, each vehicle, free)",
    "TAB vehicle (full panel)   F focus its panel   PgUp/PgDn its events (older/newer)",
    "T tracks   G ghosts   H help   ESC quit",
)

MAX_PANEL_LINES = 8
EVENT, ALERT, STATE, EGO, ANONYMOUS, ROAD_USER, MORE = "event", "alert", "state", "ego", "anonymous", "road_user", "more"
UNKNOWN = "UNKNOWN"
TRACK_ALERTS = ("CRITICAL_TTC", "CUT_IN_FROM_LEFT", "CUT_IN_FROM_RIGHT")
PRIORITY = {EGO: 0, ALERT: 1, EVENT: 2, STATE: 3, ANONYMOUS: 4, ROAD_USER: 5}


def anonymous_row(entity_id: str, observers: Sequence[str]) -> str:
    return "{0}   seen by {1}".format(entity_id, ",".join(sorted(set(observers))))


def subject_label(run, actor: str, subject) -> str:
    if subject is None:
        return ""
    return run.road_users.get((actor, subject), run.identities.get((actor, subject), subject))


def _true(states) -> List[str]:
    return [name for name, value in states.items() if value is True]


def perceived_state_lines(run, actor: str, t: float) -> Optional[List[Tuple[str, str]]]:
    perceived = (getattr(run, "perceived", None) or {}).get(actor)
    if perceived is None:
        return None
    snapshot = perceived.state_at(t)
    if not snapshot:
        return []
    lines: List[Tuple[str, str]] = []
    ego = snapshot.get("ego") or {}
    true = _true(ego)
    if true:
        lines.append(("ego: " + ", ".join(true), EGO))
    elif ego and not any(value == UNKNOWN for value in ego.values()):
        lines.append(("ego: no active state", EGO))
    for track_id, states in (snapshot.get("external") or {}).items():
        true = _true(states)
        if not true:
            continue
        name = run.subject_name(actor, track_id)
        lines.append(("{0}: {1}".format(name, ", ".join(true)), ALERT if set(true) & set(TRACK_ALERTS) else STATE))
    for sign_id, sign in (snapshot.get("signs") or {}).items():
        lines.append(("{0}: {1} sign known{2}".format(sign_id, sign.get("class"), ", relevant to the path"
                                                       if sign.get("relevant_to_ego_path") is True else ""), STATE))
    return lines


def standard_panel_lines(run, actor: str, t: float, window: float,
                         max_lines: int = MAX_PANEL_LINES) -> List[Tuple[str, str]]:
    lines = perceived_state_lines(run, actor, t)
    if lines is None:
        lines = []
        for state in run.active_states(actor, t):
            subject = run.subject_name(actor, state.subject)
            lines.append((state.state + (" → " + subject if subject else ""),
                          ALERT if state.state in TRACK_ALERTS else STATE))
    anonymous = run.anonymous_at(actor, t) if hasattr(run, "anonymous_at") else []
    if anonymous:
        lines.append(("anonymous tracks: " + ", ".join(track.name for track, _ in anonymous), ANONYMOUS))
    tracks = (getattr(run, "tracks", None) or {}).get(actor, [])
    seen = sorted({track.road_user for track in tracks if track.road_user is not None and track.state_at(t) is not None})
    for entity_id in seen:
        entity = run.entity(entity_id)
        if entity is not None and entity.identity_ambiguous:
            continue
        state = entity.state_at(t) if entity is not None else None
        lines.append((anonymous_row(entity_id, state.observers if state else [actor]), ROAD_USER))
    for event in reversed(run.recent_events(actor, t, window)):
        subject = subject_label(run, actor, event.subject)
        lines.append(("» " + event.event_type + (" → " + subject if subject else ""), EVENT))
    if len(lines) <= max_lines:
        return lines
    keep = sorted(sorted(range(len(lines)), key=lambda i: (PRIORITY.get(lines[i][1], len(PRIORITY)), i))[:max_lines])
    return [lines[i] for i in keep] + [("... +{0} more".format(len(lines) - max_lines), MORE)]


MAX_STATE_LINES = 8
MAX_EVENT_LINES = 15
CAUSE_TEXT = {"TARGET_LATERAL": "by the target", "RECORDER_LATERAL": "by own lateral motion",
              "MUTUAL_LATERAL": "both moving sideways", "LONGITUDINAL": "along the path"}


@dataclass
class RecorderPanel:

    states: List[Tuple[str, str]] = field(default_factory=list)
    events: List[Tuple[str, str]] = field(default_factory=list)
    events_total: int = 0


def recorder_panel(run, actor: str, t: float, max_events: int = MAX_EVENT_LINES,
                   max_states: int = MAX_STATE_LINES) -> RecorderPanel:
    states = [line for line in standard_panel_lines(run, actor, t, 0.0, max_lines=10 ** 6) if line[1] != EVENT]
    if len(states) > max_states:
        hidden = len(states) - max_states
        keep = sorted(sorted(range(len(states)), key=lambda i: (PRIORITY.get(states[i][1], len(PRIORITY)), i))[:max_states])
        states = [states[i] for i in keep] + [("... +{0} more".format(hidden), MORE)]
    history = [e for e in run.display_events() if e.actor == actor and e.time <= t + 1e-6]
    events = []
    for event in reversed(history[-max_events:] if max_events else []):
        subject = subject_label(run, actor, event.subject)
        cause = CAUSE_TEXT.get((getattr(event, "attributes", None) or {}).get("cause"))
        events.append(("{0:+.1f} s  {1}{2}{3}".format(event.time - t, event.event_type,
                                                       " → " + subject if subject else "",
                                                       " ({0})".format(cause) if cause else ""), EVENT))
    return RecorderPanel(states, events, len(history))


def wrap_text(text: str, measure: Callable[[str], int], width: int, indent: str = "    ") -> List[str]:
    if measure(text) <= width:
        return [text]
    pieces, current = [], ""
    for word in text.split(" "):
        candidate = word if not current else current + " " + word
        if not current.strip() or measure(candidate) <= width:
            current = candidate
            continue
        pieces.append(current)
        current = indent + word
    pieces.append(current)
    out = []
    for piece in pieces:
        while measure(piece) > width and len(piece.strip()) > 1:
            cut = len(piece) - 1
            while cut > 1 and measure(piece[:cut]) > width:
                cut -= 1
            out.append(piece[:cut])
            piece = indent + piece[cut:]
        out.append(piece)
    return out


def event_window(event_rows: Sequence[int], room: int, scroll: int,
                 max_events: int = MAX_EVENT_LINES) -> Tuple[int, int, int]:
    n = len(event_rows)
    if n == 0:
        return 0, 0, 0
    if sum(event_rows) <= room and n <= max_events:
        return 0, n, 0
    avail = max(1, room - 1)

    def end_from(start: int) -> int:
        end, used = start, 0
        while end < n and end - start < max_events and (end == start or used + event_rows[end] <= avail):
            used += event_rows[end]
            end += 1
        return end

    last = n - 1
    while last > 0 and end_from(last - 1) == n:
        last -= 1
    scroll = max(0, min(int(scroll), last))
    return scroll, end_from(scroll), scroll


def event_line(run, event) -> str:
    subject = subject_label(run, event.actor, event.subject)
    return "{0} {1}{2}".format(event.actor, event.event_type, (" " + subject) if subject else "")


def camera_cycle(recorders: Sequence[str]) -> List[Tuple[str, Optional[str]]]:
    return [("overview", None)] + [("follow", pid) for pid in recorders] + [("free", None)]


def next_camera(recorders: Sequence[str], mode: str, selected: Optional[str]) -> Tuple[str, Optional[str]]:
    cycle = camera_cycle(recorders)
    key = (mode, selected if mode == "follow" else None)
    index = cycle.index(key) if key in cycle else 0
    return cycle[(index + 1) % len(cycle)]
