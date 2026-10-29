
from __future__ import annotations

from bisect import bisect_left, bisect_right
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

UNKNOWN = "UNKNOWN"
EGO_STATES = ("MOVING", "STOP", "BRAKE", "THROTTLE", "TURN_LEFT", "TURN_RIGHT", "INDICATOR_LEFT", "INDICATOR_RIGHT",
              "SPEED_LIMIT_EXCEEDED")
TRACK_STATES = ("CLOSING", "CRITICAL_TTC", "IN_EGO_PATH", "CUT_IN_FROM_LEFT", "CUT_IN_FROM_RIGHT")
_EPS = 1e-6

Span = Tuple[int, Optional[int]]


class Timeline:

    def __init__(self) -> None:
        self.times: List[float] = []
        self.values: List[Any] = []

    def set(self, t: float, value: Any) -> None:
        if self.times and t < self.times[-1] - _EPS:
            raise ValueError("timeline changes must be set in time order")
        if self.times and abs(self.times[-1] - t) < _EPS:
            self.values[-1] = value
            if len(self.values) > 1 and self.values[-2] == value:
                self.times.pop()
                self.values.pop()
            return
        if self.values and self.values[-1] == value:
            return
        self.times.append(float(t))
        self.values.append(value)

    def value(self, t: float, before: bool = True) -> Any:
        index = (bisect_left(self.times, t - _EPS) if before else bisect_right(self.times, t + _EPS)) - 1
        return None if index < 0 else self.values[index]


def timeline_from_samples(times: Sequence[float], values: Sequence[Any]) -> Timeline:
    timeline = Timeline()
    for t, value in zip(times, values):
        timeline.set(t, value)
    return timeline


def span_values(count: int, spans: Sequence[Span], unknown_before: int = 0) -> List[Any]:
    values: List[Any] = [False] * count
    for start, end in spans:
        for index in range(start, count if end is None else end):
            values[index] = True
    for index in range(min(unknown_before, count)):
        values[index] = UNKNOWN
    return values


def _json(value: Any) -> Any:
    return UNKNOWN if value is None else value


def track_lost(state: Mapping[str, Any]) -> bool:
    return bool(state) and all(value == UNKNOWN for value in state.values())


class PerceivedWorld:

    def __init__(self) -> None:
        self.ego: Dict[str, Timeline] = {}
        self.tracks: Dict[str, Dict[str, Timeline]] = {}
        self.track_first: Dict[str, float] = {}
        self.signs: Dict[str, Dict[str, Any]] = {}


    def add_ego_state(self, name: str, times: Sequence[float], spans: Sequence[Span]) -> None:
        self.ego[name] = timeline_from_samples(times, span_values(len(times), spans))

    def add_ego_unknown(self, name: str, t: float) -> None:
        timeline = Timeline()
        timeline.set(t, UNKNOWN)
        self.ego[name] = timeline

    def add_track(self, track_id: str, times: Sequence[float], states: Dict[str, Sequence[Any]],
                  lost_at: Optional[float]) -> None:
        timelines = {name: timeline_from_samples(times, values) for name, values in states.items()}
        if lost_at is not None:
            for timeline in timelines.values():
                timeline.set(lost_at, UNKNOWN)
        self.tracks[track_id] = timelines
        self.track_first[track_id] = float(times[0])

    def add_sign(self, sign_id: str, sign_class: str, start: float, relevant: Optional[bool]) -> None:
        sign = self.signs.setdefault(sign_id, {"class": sign_class, "relevant": Timeline(), "first": start})
        sign["first"] = min(sign["first"], start)
        sign["relevant"].set(start, UNKNOWN if relevant is None else bool(relevant))


    def snapshot(self, t: float, before: bool = True) -> Dict[str, Any]:
        def seen(first: float) -> bool:
            return first < t - _EPS if before else first <= t + _EPS

        ego = {name: _json(self.ego[name].value(t, before)) for name in EGO_STATES if name in self.ego}
        external: Dict[str, Any] = {}
        for track_id in sorted(self.tracks):
            if not seen(self.track_first[track_id]):
                continue
            timelines = self.tracks[track_id]
            external[track_id] = {name: _json(timelines[name].value(t, before))
                                  for name in TRACK_STATES if name in timelines}
        signs: Dict[str, Any] = {}
        for sign_id in sorted(self.signs):
            sign = self.signs[sign_id]
            if not seen(sign["first"]):
                continue
            signs[sign_id] = {"class": sign["class"], "known": True,
                              "relevant_to_ego_path": _json(sign["relevant"].value(t, before))}
        return {"ego": ego, "external": external, "signs": signs}


def compact_state(snapshot: Optional[Dict[str, Any]], name_of: Optional[Callable[[str], str]] = None) -> List[str]:
    if not snapshot:
        return []
    name_of = name_of or (lambda name: name)
    lines = []
    ego = snapshot.get("ego", {})
    if ego and all(value == UNKNOWN for value in ego.values()):
        lines.append("ego: not yet observed")
    elif ego:
        true = [name for name, value in ego.items() if value is True]
        unknown = [name + "?" for name, value in ego.items() if value == UNKNOWN and name != "SPEED_LIMIT_EXCEEDED"]
        lines.append("ego: " + (", ".join(true + unknown) or "no active state"))
    lost = []
    for track_id, state in snapshot.get("external", {}).items():
        if track_lost(state):
            lost.append(name_of(track_id))
            continue
        shown = ([name for name in TRACK_STATES if state.get(name) is True]
                 + [name + "?" for name in TRACK_STATES if state.get(name) == UNKNOWN])
        lines.append("{0}: {1}".format(name_of(track_id), ", ".join(shown) or "no active state"))
    if lost:
        lines.append("track lost, states UNKNOWN: " + ", ".join(lost))
    for sign_id, sign in snapshot.get("signs", {}).items():
        lines.append("{0}: {1} sign known{2}".format(
            sign_id, sign.get("class"), ", relevant to the path" if sign.get("relevant_to_ego_path") is True else ""))
    return lines
