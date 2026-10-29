"""Post-hoc validation of a reconstructed run against its ground truth: the conflict
events and their intervals, the relevance of the timeline to each collision, the proximity of the reconstructed road
users at each impact, the recovery of the tracks that approach a collision partner, and the phantoms.

Privileged: ground truth is read here only, never by the reconstruction.  The reused pieces keep their definitions:
``event_oracle`` (oracles, one-to-one ``match``, 2.0 s window), the 1.5 m identity rule, the 8 s warning window."""

from __future__ import annotations

import dataclasses
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import numpy as np

from ..reconstruction.local import track_events
from ..reconstruction.tracking import LocalTrack
from . import event_oracle as eo
from .gt_audit import truth_of
from .reconstruction import IDENTITY_MAX_BOX_DISTANCE_M, _box_distance, _to_world
from .scorecard import WARNING_WINDOW_S

FAMILIES = {"CRITICAL_TTC": ("CRITICAL_TTC_START", "CRITICAL_TTC_END"),
            "EGO_PATH": ("EGO_PATH_ENTRY", "EGO_PATH_EXIT"),
            "CUT_IN_LEFT": ("CUT_IN_FROM_LEFT_START", "CUT_IN_FROM_LEFT_END"),
            "CUT_IN_RIGHT": ("CUT_IN_FROM_RIGHT_START", "CUT_IN_FROM_RIGHT_END")}
START_OF = {start: family for family, (start, _) in FAMILIES.items()}
END_OF = {end: family for family, (_, end) in FAMILIES.items()}
MATCH_WINDOW_S = eo.MATCH_WINDOW_S  # 2.0 s
IDENTITY_M = IDENTITY_MAX_BOX_DISTANCE_M  # 1.5 m
STATE_GAP_S = 0.15  # a track state this close to an instant stands for it
SUPPORT_S, SUPPORT_GAP_S = 0.25, 0.15  # established support: >= 0.25 s of support, gaps <= 0.15 s
IMMEDIATE_S = 1.0  # "immediately before the contact"
GRID_S = 0.05
ENTITY_AT_S = 0.051  # an entity state within this of the impact (10 Hz output)
BINS = (("<=2 m", 2.0), ("(2,4] m", 4.0), ("(4,5] m", 5.0), (">5 m", math.inf))
ZONES_M = (5.0, 4.0, 2.0)
CLASSES = ("correct", "wrong vehicle", "unsupported", "duplicate", "not evaluable")


# ----------------------------------------------------------------------------------------------------------------
# geometry
# ----------------------------------------------------------------------------------------------------------------

def _corners(cx: float, cy: float, yaw: float, hx: float, hy: float) -> np.ndarray:
    c, s = math.cos(yaw), math.sin(yaw)
    local = np.array([[hx, hy], [hx, -hy], [-hx, -hy], [-hx, hy]])
    return np.column_stack([cx + c * local[:, 0] - s * local[:, 1], cy + s * local[:, 0] + c * local[:, 1]])


def _separated(a: np.ndarray, b: np.ndarray) -> bool:
    for poly in (a, b):
        for i in range(4):
            edge = poly[(i + 1) % 4] - poly[i]
            axis = np.array([-edge[1], edge[0]])
            pa, pb = a @ axis, b @ axis
            if pa.max() < pb.min() or pb.max() < pa.min():
                return True
    return False


def _point_segment(p: np.ndarray, a: np.ndarray, b: np.ndarray) -> float:
    ab = b - a
    t = float(np.clip(((p - a) @ ab) / max(float(ab @ ab), 1e-12), 0.0, 1.0))
    return float(np.hypot(*(p - (a + t * ab))))


def rect_gap(a: Tuple[float, float, float, float, float], b: Tuple[float, float, float, float, float]) -> float:
    """Exact 2-D distance between two oriented rectangles (cx, cy, yaw rad, half length, half width); 0 when they
    touch or overlap."""
    ca, cb = _corners(*a), _corners(*b)
    if not _separated(ca, cb):
        return 0.0
    best = math.inf
    for poly, other in ((ca, cb), (cb, ca)):
        for p in poly:
            for i in range(4):
                best = min(best, _point_segment(p, other[i], other[(i + 1) % 4]))
    return best


def true_rect(state: Mapping[str, Any]) -> Tuple[float, float, float, float, float]:
    tf, ext = state["transform"], state.get("bbox_extent") or {"x": 2.4, "y": 1.0}
    return float(tf["x"]), float(tf["y"]), math.radians(float(tf["yaw_deg"])), float(ext["x"]), float(ext["y"])


def entity_rect(state: Mapping[str, Any], footprint: Mapping[str, Any]) -> Tuple[float, float, float, float, float]:
    heading = state.get("heading_deg")
    if heading is None:
        vx, vy = float(state.get("vx") or 0.0), float(state.get("vy") or 0.0)
        heading = math.degrees(math.atan2(vy, vx)) if math.hypot(vx, vy) > 0.5 else 0.0
    length = state.get("length_m") or footprint.get("length_m") or 4.6
    width = state.get("width_m") or footprint.get("width_m") or 1.9
    return float(state["x"]), float(state["y"]), math.radians(float(heading)), float(length) / 2.0, float(width) / 2.0


def bin_of(distance: Optional[float]) -> str:
    if distance is None:
        return "absent"
    for label, upper in BINS:
        if distance <= upper:
            return label
    return BINS[-1][0]


# ----------------------------------------------------------------------------------------------------------------
# intervals
# ----------------------------------------------------------------------------------------------------------------

def intervals_from_events(events: Iterable[Tuple[str, float]], last_t: float, recorder: str, subject: Optional[str],
                          track: str) -> List[Dict[str, Any]]:
    """START/END events of one track -> intervals per family; an interval without END closes at ``last_t`` and is
    marked open."""
    out, opened = [], {}
    for event_type, t in sorted(events, key=lambda e: e[1]):
        if event_type in START_OF:
            opened.setdefault(START_OF[event_type], t)
        elif event_type in END_OF and END_OF[event_type] in opened:
            family = END_OF[event_type]
            out.append({"recorder": recorder, "family": family, "subject": subject, "track": track,
                        "start": opened.pop(family), "end": t, "open_end": False})
    for family, start in opened.items():
        out.append({"recorder": recorder, "family": family, "subject": subject, "track": track, "start": start,
                    "end": max(last_t, start), "open_end": True})
    return sorted(out, key=lambda iv: iv["start"])


def _track_event_list(rec: Any, samples: Sequence[Any], semantics: Any, contacts: Any, track_id: str,
                      impact: Optional[float]) -> List[Tuple[str, float]]:
    if len(samples) < 2:
        return []
    track = LocalTrack(track_id=track_id, samples=list(samples))
    return [(e.type, round(float(e.t_local), 4)) for e in
            track_events(rec.owner, track, rec.ego.end, semantics, rec.ego, None, rec.footprint, contacts,
                         road=rec.road, impact_from=impact)]


def truth_intervals(run_dir: Path, cfg: Any = None) -> Dict[str, Any]:
    """The true intervals of every recorder: PERFECT (the true state of every vehicle) and COVERAGE (while a radar
    of the recorder could see it), START and END kept for every family (``event_oracle`` keeps only the starts of
    the path and cut-in events)."""
    from ..reconstruction.config import load_config
    cfg = cfg or load_config()
    truth = eo.prepare_truth(Path(run_dir), cfg)
    out: Dict[str, Any] = {"PERFECT": defaultdict(list), "COVERAGE": defaultdict(list)}
    for owner, per_target in truth["ideal"].items():
        rec, impact = truth["recorders"][owner], truth["first_contact"].get(owner)
        for target, item in per_target.items():
            if not item["samples"] or item["dims"] is None:
                continue
            semantics = dataclasses.replace(cfg.semantics, target_length_m=item["dims"][0],
                                            target_width_m=item["dims"][1])
            events = _track_event_list(rec, item["samples"], semantics, item["contacts"], target + "#all", impact)
            out["PERFECT"][owner] += intervals_from_events(events, item["samples"][-1].t_local, owner, target,
                                                           target + "#all")
            for n, piece in enumerate(eo._pieces(item["samples"], item["visible"], cfg.tracking.max_track_gap_s,
                                                 cfg.tracking.min_track_frames), 1):
                track = "{0}#{1}".format(target, n)
                events = _track_event_list(rec, piece, semantics, item["contacts"], track, impact)
                out["COVERAGE"][owner] += intervals_from_events(events, piece[-1].t_local, owner, target, track)
    recorders = {owner: {"first_sweep": rec.sweeps[0][1] if rec.sweeps else 0.0, "end": float(rec.ego.end),
                         "clock_origin": float(rec.clock_origin)} for owner, rec in truth["recorders"].items()}
    return {"PERFECT": dict(out["PERFECT"]), "COVERAGE": dict(out["COVERAGE"]), "recorders": recorders}


# ----------------------------------------------------------------------------------------------------------------
# a reconstructed run
# ----------------------------------------------------------------------------------------------------------------

def _read_json(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    with Path(path).open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


class RunData:
    """The reconstruction of one run (canonical or a campaign job) with what the analysis needs of its truth."""

    def __init__(self, run_dir: Path) -> None:
        run_dir = Path(run_dir)
        rec = run_dir / "reconstruction"
        self.run_dir = run_dir
        self.alignment = _read_json(rec / "global" / "alignment.json")
        graphs = {p.parent.name: _read_json(p) for p in sorted(rec.glob("*/local_graph.json"))}
        self.recorders = sorted(graphs)
        self.origins = {r: float(g["recorder"]["clock"]["origin_source_timestamp"]) for r, g in graphs.items()}
        self.nodes = {r: g["nodes"] for r, g in graphs.items()}
        self.first_pose = {r: _read_jsonl(run_dir / "vehicles" / r / "ego.jsonl")[0] for r in self.recorders}
        self.truth, _ = truth_of(run_dir)
        evaluation = _read_json(rec / "evaluation" / "evaluation.json")
        self.track_identity = {row["track"]: row.get("true_identity") for row in evaluation["tracks"]}
        self.collisions = evaluation["collisions"]
        fusion = _read_json(rec / "evaluation" / "fusion_metrics.json")
        self.entity_identity = {row["id"]: row.get("true_identity") for row in fusion.get("entities", [])}
        self.entities = _read_json(rec / "global" / "anonymous_entities.json").get("entities", [])
        self.associations = {(a["local_graph"], a["local_track"]): a for a in _read_json(rec / "global" / "associations.json")}
        self.reference_sim = None
        for name in self.recorders:
            clock = self.alignment["graphs"].get(name, {})
            if clock.get("status") == "ALIGNED" and clock.get("method", "matched_collisions") in (
                    "matched_collisions", "reference_recorder"):
                self.reference_sim = -float(clock["offset_to_global"]) + self.origins[name]
                break
        self.samples: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for r in self.recorders:
            path = rec / r / "local_tracks.jsonl"
            if not path.exists():
                continue
            for row in _read_jsonl(path):
                row["world"] = _to_world(self.first_pose[r], row["x_m"], row["y_m"])
                row["sim"] = row["t_local"] + self.origins[r]
                self.samples["{0}:{1}".format(r, row["track_id"])].append(row)
        for rows in self.samples.values():
            rows.sort(key=lambda row: row["t_local"])
        self._times = {key: np.array([row["t_local"] for row in rows]) for key, rows in self.samples.items()}

    # truth lookups
    def true_state(self, vehicle: str, sim: float) -> Optional[Dict[str, Any]]:
        track = self.truth.get(vehicle)
        return None if track is None else track.at(sim)

    def distance_to(self, row: Mapping[str, Any], vehicle: str) -> Optional[float]:
        state = self.true_state(vehicle, row["sim"])
        return None if state is None else _box_distance(row["world"], state)

    def nearest_vehicle(self, row: Mapping[str, Any], owner: str) -> Tuple[Optional[str], Optional[float]]:
        best, best_d = None, None
        for vehicle in self.truth:
            if vehicle == owner:
                continue
            d = self.distance_to(row, vehicle)
            if d is not None and (best_d is None or d < best_d):
                best, best_d = vehicle, d
        return best, best_d

    def state_near(self, key: str, t_local: float, gap: float = STATE_GAP_S) -> Optional[Dict[str, Any]]:
        times = self._times.get(key)
        if times is None or not len(times):
            return None
        i = int(np.argmin(np.abs(times - t_local)))
        return self.samples[key][i] if abs(times[i] - t_local) <= gap + 1e-9 else None

    def last_before(self, key: str, t_local: float, gap: float = STATE_GAP_S) -> Optional[Dict[str, Any]]:
        rows = [row for row in self.samples.get(key, []) if t_local - gap - 1e-9 <= row["t_local"] <= t_local + 1e-9]
        return rows[-1] if rows else None

    def subject_at(self, owner: str, track: str, t_local: float) -> Dict[str, Any]:
        """The vehicle a track's event is about (module docstring of the doc): its identity, else the vehicle within
        1.5 m at the event, else none; with the position error of the track at the event."""
        key = "{0}:{1}".format(owner, track)
        row = self.state_near(key, t_local)
        identity = self.track_identity.get(key)
        instant, instant_d = (self.nearest_vehicle(row, owner) if row is not None else (None, None))
        if instant_d is not None and instant_d > IDENTITY_M:
            instant = None
        subject, how = (identity, "track identity") if identity is not None else \
            ((instant, "position at the event") if instant is not None else (None, "none"))
        error = self.distance_to(row, subject) if (row is not None and subject is not None) else None
        return {"subject": subject, "subject_from": how, "instant_identity": instant,
                "position_error_m": None if error is None else round(error, 3),
                "state_dt_s": None if row is None else round(abs(row["t_local"] - t_local), 3),
                "measured": None if row is None else bool(row["measured"])}

    def contacts(self) -> List[Dict[str, Any]]:
        """True contacts (later impacts of a chain included), with each recorder's local contact time."""
        out = []
        for k, c in enumerate(self.collisions):
            sim = float(c["sim_time"])
            out.append({"index": k, "pair": list(c["participants"]), "sim": sim,
                        "t_local": {r: round(sim - self.origins[r], 4) for r in self.recorders},
                        "participants_correct": c.get("participants_correct"),
                        "reconstructed_participants": c.get("reconstructed_participants")})
        return out


def reconstruction_intervals(data: RunData) -> Dict[str, List[Dict[str, Any]]]:
    out: Dict[str, List[Dict[str, Any]]] = {}
    for r, nodes in data.nodes.items():
        per_track: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
        for node in nodes:
            event_type = node.get("event_type", "")
            if (event_type in START_OF or event_type in END_OF) and node.get("subject_id"):
                per_track[str(node["subject_id"])].append((event_type, round(float(node["t_local"]), 4)))
        out[r] = []
        for track, events in sorted(per_track.items()):
            rows = data.samples.get("{0}:{1}".format(r, track), [])
            last = rows[-1]["t_local"] if rows else max(t for _, t in events)
            out[r] += intervals_from_events(events, last, r, None, track)
    return out


# ----------------------------------------------------------------------------------------------------------------
# 1. events: classes and counts
# ----------------------------------------------------------------------------------------------------------------

def classify(predictions: List[Dict[str, Any]], truths: List[Dict[str, Any]],
             window: float = MATCH_WINDOW_S) -> None:
    """Sets ``class`` (and the matched truth) on every evaluable prediction and ``matched`` on every truth, in
    place.  Predictions and truths: dicts with ``type``, ``subject``, ``t_local``; a prediction already carrying a
    ``class`` (not evaluable) is left out."""
    evaluable = [p for p in predictions if "class" not in p]
    pairs, unmatched_f, unmatched_e = eo.match(evaluable, truths, window)
    matched = set()
    for i, j in pairs:
        evaluable[i]["class"], evaluable[i]["truth_t"] = "correct", truths[j]["t_local"]
        matched.add(j)
    rest = [evaluable[i] for i in unmatched_f]
    for p in rest:
        if p["subject"] is not None and any(truths[j]["type"] == p["type"] and truths[j]["subject"] == p["subject"]
                                            and abs(truths[j]["t_local"] - p["t_local"]) <= window for j in matched):
            p["class"] = "duplicate"
    rest = [p for p in rest if "class" not in p]
    candidates = sorted((abs(p["t_local"] - truths[j]["t_local"]), i, j) for i, p in enumerate(rest)
                        for j in unmatched_e if truths[j]["type"] == p["type"] and truths[j]["subject"] != p["subject"]
                        and abs(truths[j]["t_local"] - p["t_local"]) <= window)
    used_p, used_t = set(), set()
    for _, i, j in candidates:
        if i in used_p or j in used_t:
            continue
        used_p.add(i)
        used_t.add(j)
        rest[i]["class"], rest[i]["true_subject"], rest[i]["truth_t"] = "wrong vehicle", truths[j]["subject"], \
            truths[j]["t_local"]
        truths[j]["claimed_by_wrong_vehicle"] = True
    for p in rest:
        if "class" not in p:
            p["class"] = "unsupported"
            p["reason"] = ("subject is no vehicle" if p["subject"] is None
                           else "no such condition of this vehicle within {0} s".format(window))
    for j, t in enumerate(truths):
        t["matched"] = j in matched


def event_rows(data: RunData, truth_iv: Mapping[str, Any], recon_iv: Mapping[str, List[Dict[str, Any]]]
               ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    predictions_all, truths_all = [], []
    first_contact = {}
    for c in data.contacts():
        for r in c["pair"]:
            if r in c["t_local"]:
                first_contact[r] = min(first_contact.get(r, math.inf), c["t_local"][r])
    for r in data.recorders:
        meta = truth_iv["recorders"].get(r)
        contact = first_contact.get(r)

        def phase(t: float) -> str:
            return "no contact" if contact is None else ("before contact" if t < contact else "after contact")
        predictions = []
        for iv in recon_iv.get(r, []):
            row = {"recorder": r, "family": iv["family"], "type": FAMILIES[iv["family"]][0], "t_local": iv["start"],
                   "end": iv["end"], "open_end": iv["open_end"], "track": iv["track"], "phase": phase(iv["start"])}
            row.update(data.subject_at(r, iv["track"], iv["start"]))
            if meta is None:
                row["class"], row["reason"] = "not evaluable", "no ground truth for the recorder"
            elif row["state_dt_s"] is None:
                row["class"], row["reason"] = "not evaluable", "no track state within {0} s of the event".format(STATE_GAP_S)
            elif row["t_local"] > meta["end"] + 1e-6:
                row["class"], row["reason"] = "not evaluable", "after the end of the recorder's ground truth"
            predictions.append(row)
        truths = [{"recorder": r, "family": iv["family"], "type": FAMILIES[iv["family"]][0], "t_local": iv["start"],
                   "end": iv["end"], "open_end": iv["open_end"], "subject": iv["subject"], "phase": phase(iv["start"])}
                  for iv in truth_iv["PERFECT"].get(r, [])]
        coverage = truth_iv["COVERAGE"].get(r, [])
        for t in truths:
            t["observable"] = any(c["family"] == t["family"] and c["subject"] == t["subject"]
                                  and abs(c["start"] - t["t_local"]) <= MATCH_WINDOW_S for c in coverage)
        classify(predictions, truths)
        for p in predictions:  # durations of the matched events
            if p["class"] != "correct":
                continue
            t = next(t for t in truths if t["type"] == p["type"] and t["subject"] == p["subject"]
                     and t["t_local"] == p["truth_t"])
            p["onset_error_s"] = round(p["t_local"] - t["t_local"], 3)
            if not p["open_end"] and not t["open_end"]:
                p["end_error_s"] = round(p["end"] - t["end"], 3)
                p["duration_error_s"] = round((p["end"] - p["t_local"]) - (t["end"] - t["t_local"]), 3)
            inter = max(0.0, min(p["end"], t["end"]) - max(p["t_local"], t["t_local"]))
            union = max(p["end"], t["end"]) - min(p["t_local"], t["t_local"])
            p["overlap_iou"] = round(inter / union, 3) if union > 0 else 1.0
        predictions_all += predictions
        truths_all += truths
    return predictions_all, truths_all


# ----------------------------------------------------------------------------------------------------------------
# 2. active states and saved states
# ----------------------------------------------------------------------------------------------------------------

def _active(intervals: Iterable[Tuple[float, float]], grid: np.ndarray) -> np.ndarray:
    mask = np.zeros(len(grid), dtype=bool)
    for start, end in intervals:
        mask |= (grid >= start - 1e-9) & (grid <= end + 1e-9)
    return mask


def active_states(data: RunData, truth_iv: Mapping[str, Any], predictions: Sequence[Mapping[str, Any]],
                  contacts: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    """Per recorder, on a 0.05 s grid: time with a spurious active condition (reconstruction, not true), with a
    missing one (true and observable, not reconstructed), and the 1.0 s before each of its contacts."""
    out: Dict[str, Any] = {"recorders": {}, "before_contact": []}
    for r in data.recorders:
        meta = truth_iv["recorders"].get(r)
        if meta is None:
            continue
        grid = np.arange(meta["first_sweep"], meta["end"] + 1e-9, GRID_S)
        recon: Dict[Tuple[str, str], List[Tuple[float, float]]] = defaultdict(list)
        for p in predictions:
            if p["recorder"] == r and p["class"] != "not evaluable":
                subject = p["subject"] if p["subject"] is not None else "phantom:" + p["track"]
                recon[(p["family"], subject)].append((p["t_local"], p["end"]))
        perfect: Dict[Tuple[str, str], List[Tuple[float, float]]] = defaultdict(list)
        for iv in truth_iv["PERFECT"].get(r, []):
            perfect[(iv["family"], iv["subject"])].append((iv["start"], iv["end"]))
        cover: Dict[Tuple[str, str], List[Tuple[float, float]]] = defaultdict(list)
        for iv in truth_iv["COVERAGE"].get(r, []):
            cover[(iv["family"], iv["subject"])].append((iv["start"], iv["end"]))
        spurious = np.zeros(len(grid), dtype=bool)
        spurious_phantom = np.zeros(len(grid), dtype=bool)
        for k, ivs in recon.items():  # merged per (family, subject): duplicates do not count twice
            extra = _active(ivs, grid) & ~_active(perfect.get(k, []), grid)
            spurious |= extra
            if k[1].startswith("phantom:"):
                spurious_phantom |= extra
        missing = np.zeros(len(grid), dtype=bool)
        for k, ivs in cover.items():
            missing |= _active(ivs, grid) & ~_active(recon.get(k, []), grid)
        own = [c["t_local"][r] for c in contacts if r in c["pair"]]
        pre = grid < (min(own) if own else math.inf)
        out["recorders"][r] = {"grid_s": GRID_S, "n": int(len(grid)), "n_pre_contact": int(pre.sum()),
                               "spurious": int(spurious.sum()), "spurious_phantom": int(spurious_phantom.sum()),
                               "missing": int(missing.sum()), "incorrect": int((spurious | missing).sum()),
                               "spurious_pre": int((spurious & pre).sum()), "missing_pre": int((missing & pre).sum()),
                               "incorrect_pre": int(((spurious | missing) & pre).sum())}
        for c in contacts:
            if r not in c["pair"]:
                continue
            tc = c["t_local"][r]
            window = (grid >= tc - IMMEDIATE_S - 1e-9) & (grid < tc)
            last = np.where(grid < tc)[0]
            # Incorrect context: a wrong-vehicle or unsupported event active in the second before the contact
            # (an event of the right vehicle raised a little early is a timing error, counted in the grid only).
            wrong = [p for p in predictions if p["recorder"] == r and p["class"] in ("wrong vehicle", "unsupported")
                     and p["t_local"] < tc and p["end"] >= tc - IMMEDIATE_S]
            out["before_contact"].append({
                "contact": c["index"], "recorder": r, "n": int(window.sum()),
                "spurious": int((spurious & window).sum()), "spurious_phantom": int((spurious_phantom & window).sum()),
                "missing": int((missing & window).sum()),
                "spurious_at_last_state": bool(spurious[last[-1]]) if len(last) else None,
                "incorrect_events_active": len(wrong),
                "incorrect_events_active_phantom": sum(p["subject"] is None for p in wrong),
                "incorrect_event_families": sorted({p["family"] for p in wrong})})
    return out


def saved_state_errors(data: RunData) -> Dict[str, np.ndarray]:
    """Every saved state against the truth: local track samples (distance of the track point to its vehicle's true
    box) and global road-user states (centre error), measured and predicted apart."""
    track = {"measured": [], "predicted": []}
    for key, rows in data.samples.items():
        owner = key.split(":", 1)[0]
        identity = data.track_identity.get(key)
        if identity is None:
            continue
        for row in rows:
            d = data.distance_to(row, identity)
            if d is not None:
                track["measured" if row["measured"] else "predicted"].append(d)
    entity = {"measured": [], "predicted": []}
    if data.reference_sim is not None:
        for e in data.entities:
            identity = data.entity_identity.get(e["id"])
            if identity is None or identity not in data.truth:
                continue
            for state in e.get("trajectory", []):
                true = data.true_state(identity, data.reference_sim + float(state["t_global"]))
                if true is None:
                    continue
                d = math.hypot(state["x"] - true["transform"]["x"], state["y"] - true["transform"]["y"])
                entity["measured" if state.get("measured_by") else "predicted"].append(d)
    out = {"track_" + k: np.array(v, dtype=np.float32) for k, v in track.items()}
    out.update({"entity_" + k: np.array(v, dtype=np.float32) for k, v in entity.items()})
    return out


# ----------------------------------------------------------------------------------------------------------------
# 3. relevance per collision
# ----------------------------------------------------------------------------------------------------------------

def relevance(data: RunData, contacts: Sequence[Mapping[str, Any]], predictions: Sequence[Mapping[str, Any]],
              truths: Sequence[Mapping[str, Any]] = ()) -> List[Dict[str, Any]]:
    out = []
    for c in contacts:
        for r in data.recorders:
            tc = c["t_local"][r]
            partner = next((p for p in c["pair"] if p != r), None) if r in c["pair"] else None
            window = [p for p in predictions if p["recorder"] == r and tc - WARNING_WINDOW_S <= p["t_local"] <= tc]
            true_warnings = [t for t in truths if partner is not None and t["recorder"] == r
                             and t["family"] == "CRITICAL_TTC" and t["subject"] == partner
                             and tc - WARNING_WINDOW_S <= t["t_local"] < tc]
            counts = {k: sum(p["class"] == k for p in window) for k in CLASSES}
            about_pair = [p for p in window if p["subject"] in c["pair"]]
            warned = any(p["family"] == "CRITICAL_TTC" and p["class"] == "correct" and p["subject"] == partner
                         and p["t_local"] < tc for p in window) if partner else None
            alive = []
            for key in data.samples:
                if not key.startswith(r + ":"):
                    continue
                row = data.last_before(key, tc)
                if row is None:
                    continue
                instant, instant_d = data.nearest_vehicle(row, r)
                alive.append({"track": key, "identity": data.track_identity.get(key),
                              "instant_identity": instant if instant_d is not None and instant_d <= IDENTITY_M else None,
                              "error_to_partner_m": (None if partner is None else
                                                     _round(data.distance_to(row, partner))),
                              "measured": bool(row["measured"])})
            on_partner = [a for a in alive if partner is not None and a["error_to_partner_m"] is not None
                          and a["error_to_partner_m"] <= IDENTITY_M]
            out.append({"contact": c["index"], "pair": "-".join(c["pair"]), "recorder": r,
                        "role": "participant" if partner else "third party", "partner": partner,
                        "participants_correct": c["participants_correct"],
                        "events_in_window": len(window), **{"events_" + k.replace(" ", "_"): v for k, v in counts.items()},
                        "events_about_pair": len(about_pair),
                        "incorrect_about_pair": sum(p["class"] in ("wrong vehicle", "unsupported") for p in about_pair),
                        "source_tracks": sorted({p["track"] for p in window}),
                        "correct_warning_about_partner": warned,
                        "true_warning_about_partner": (bool(true_warnings) if partner else None),
                        "observable_true_warning_about_partner": (any(t["observable"] for t in true_warnings)
                                                                  if partner else None),
                        "tracks_alive_before_impact": len(alive),
                        "partner_tracked_before_impact": (bool(on_partner) if partner else None),
                        "best_error_to_partner_m": (min((a["error_to_partner_m"] for a in alive
                                                         if a["error_to_partner_m"] is not None), default=None)
                                                    if partner else None)})
    return out


def _round(value: Optional[float], digits: int = 3) -> Optional[float]:
    return None if value is None else round(float(value), digits)


# ----------------------------------------------------------------------------------------------------------------
# 4. proximity at impact, 6. phantoms
# ----------------------------------------------------------------------------------------------------------------

def proximity(data: RunData, contacts: Sequence[Mapping[str, Any]],
              predictions: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    bad_tracks = {"{0}:{1}".format(p["recorder"], p["track"]) for p in predictions
                  if p["class"] in ("wrong vehicle", "unsupported")}
    out = []
    if data.reference_sim is None:
        return out
    for c in contacts:
        sim_c = c["sim"]
        pair_states = {}
        for v in c["pair"]:
            pair_states[v] = data.truth[v] if v in data.truth else None
        for e in data.entities:
            identity = data.entity_identity.get(e["id"])
            kind = ("phantom" if identity is None else
                    "ghost of a colliding recorder" if identity in data.recorders and identity in c["pair"] else
                    "ghost of another recorder" if identity in data.recorders else
                    "colliding vehicle" if identity in c["pair"] else "other vehicle")
            closest_all, closest_before, at_impact, near_window = None, None, None, False
            for state in e.get("trajectory", []):
                sim = data.reference_sim + float(state["t_global"])
                rect = entity_rect(state, e.get("footprint") or {})
                gaps = []
                for v, track in pair_states.items():
                    true = None if track is None else track.at(sim)
                    if true is not None:
                        gaps.append(rect_gap(rect, true_rect(true)))
                if not gaps:
                    continue
                gap = min(gaps)
                closest_all = gap if closest_all is None else min(closest_all, gap)
                if sim < sim_c:
                    closest_before = gap if closest_before is None else min(closest_before, gap)
                    if sim >= sim_c - WARNING_WINDOW_S and gap <= 5.0:
                        near_window = True
                if abs(sim - sim_c) <= ENTITY_AT_S:
                    at_impact = gap if at_impact is None else min(at_impact, gap)
            if closest_all is None:
                continue
            out.append({"contact": c["index"], "pair": "-".join(c["pair"]), "entity": e["id"], "kind": kind,
                        "identity": identity, "observers": list(e.get("observers") or []),
                        "clearance_at_impact_m": _round(at_impact), "bin_at_impact": bin_of(at_impact),
                        "closest_before_impact_m": _round(closest_before), "closest_over_recording_m": _round(closest_all),
                        "within_5m_in_8s_before": near_window,
                        "incorrect_event": any(t in bad_tracks for t in e.get("source_tracks", []))})
    return out


# ----------------------------------------------------------------------------------------------------------------
# 5. recovery
# ----------------------------------------------------------------------------------------------------------------

def runs_of(times: Sequence[float], flags: Sequence[bool], min_s: float = SUPPORT_S,
            max_gap_s: float = SUPPORT_GAP_S) -> List[Tuple[float, float, float]]:
    """Runs of True samples (a gap above ``max_gap_s`` or a False sample breaks a run) lasting at least ``min_s``:
    (start, established, end), ``established`` = start + min_s."""
    out, start, prev = [], None, None
    for t, flag in zip(times, flags):
        if flag and start is not None and t - prev <= max_gap_s + 1e-9:
            prev = t
            continue
        if start is not None and prev - start >= min_s - 1e-9:
            out.append((start, start + min_s, prev))
        start, prev = (t, t) if flag else (None, None)
    if start is not None and prev - start >= min_s - 1e-9:
        out.append((start, start + min_s, prev))
    return out


def zone_entries(data: RunData, pair: Sequence[str], sim_c: float, step: float = 0.05) -> Dict[float, Optional[float]]:
    """Per zone, the simulator time at which the final approach enters it: the start of the last continuous stay of
    the colliding pair's true box gap within the zone that ends at the contact (the recording's first instant when
    the pair is within it from the start; see ``zone_from_start``)."""
    a, b = (data.truth.get(v) for v in pair)
    out: Dict[float, Optional[float]] = {z: None for z in ZONES_M}
    if a is None or b is None:
        return out
    start = max(a.times[0], b.times[0])
    times, gaps = [], []
    for sim in np.arange(start, sim_c + 1e-9, step):
        sa, sb = a.at(sim), b.at(sim)
        if sa is not None and sb is not None:
            times.append(float(sim))
            gaps.append(rect_gap(true_rect(sa), true_rect(sb)))
    for z in ZONES_M:
        i = len(gaps) - 1
        while i >= 0 and gaps[i] <= z:
            i -= 1
        if i < len(gaps) - 1:
            out[z] = times[i + 1]
    return out


def zone_from_start(data: RunData, pair: Sequence[str], entries: Mapping[float, Optional[float]]) -> Dict[float, bool]:
    a, b = (data.truth.get(v) for v in pair)
    start = None if a is None or b is None else max(a.times[0], b.times[0])
    return {z: bool(start is not None and entry is not None and entry - start <= 0.051) for z, entry in entries.items()}


def recovery(data: RunData, contacts: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for c in contacts:
        entries = zone_entries(data, c["pair"], c["sim"])
        from_start = zone_from_start(data, c["pair"], entries)
        for observer in c["pair"]:
            if observer not in data.recorders:
                continue
            partner = next(v for v in c["pair"] if v != observer)
            for key, rows in data.samples.items():
                if not key.startswith(observer + ":"):
                    continue
                times = [row["sim"] for row in rows]
                if times[0] >= c["sim"]:
                    continue  # born after the impact: not an approach
                distances = [data.distance_to(row, partner) for row in rows]
                on = [d is not None and d <= IDENTITY_M for d in distances]
                support = runs_of(times, on)
                identity = data.track_identity.get(key)
                if identity != partner and not (identity is None and any(s[1] <= c["sim"] for s in support)):
                    continue  # a track of another vehicle (or of no vehicle that never held the partner)
                off = [d is not None and d > IDENTITY_M for d in distances]
                episodes = runs_of(times, off)
                if not episodes:
                    continue  # never a sustained unmatched episode
                a = data.associations.get((observer, key.split(":", 1)[1]))
                association = ("linked to the partner" if a and a["status"] == "ASSOCIATED" and a["global_entity"] == partner
                               else "linked to another" if a and a["status"] == "ASSOCIATED" else "not linked")
                row = {"contact": c["index"], "pair": "-".join(c["pair"]), "observer": observer, "partner": partner,
                       "track": key, "identity": data.track_identity.get(key), "association": association,
                       "track_start_s": round(times[0] - c["sim"], 3), "track_end_s": round(times[-1] - c["sim"], 3),
                       "unmatched_episodes": len(episodes),
                       "first_support_s": round(support[0][1] - c["sim"], 3) if support else None}
                for z in ZONES_M:
                    entry = entries[z]
                    row["zone_{0:g}m".format(z)] = _zone_class(entry, c["sim"], support, times)
                    row["zone_{0:g}m_entry_s".format(z)] = None if entry is None else round(entry - c["sim"], 3)
                    row["zone_{0:g}m_from_start".format(z)] = from_start[z]
                out.append(row)
    return out


def _zone_class(entry: Optional[float], sim_c: float, support: Sequence[Tuple[float, float, float]],
                times: Sequence[float]) -> str:
    if entry is None:
        return "zone not entered"
    if any(established <= entry + 1e-9 and end >= entry - SUPPORT_GAP_S for _, established, end in support):
        return "supported before entry"
    later = [established for _, established, _ in support if established > entry + 1e-9]
    if later and min(later) <= sim_c + 1e-9:
        return "established after entry, before impact"
    if later:
        return "established only after impact"
    if times[-1] < entry:
        return "never: track ended before entry"
    if times[-1] - entry < SUPPORT_S:
        return "never: insufficient follow-up"
    return "never: still incorrect"


# ----------------------------------------------------------------------------------------------------------------
# a run
# ----------------------------------------------------------------------------------------------------------------

def analyse(run_dir: Path, truth_iv: Mapping[str, Any]) -> Dict[str, Any]:
    data = RunData(Path(run_dir))
    recon_iv = reconstruction_intervals(data)
    predictions, truths = event_rows(data, truth_iv, recon_iv)
    contacts = data.contacts()
    return {"predictions": predictions, "truths": truths, "contacts": contacts,
            "active": active_states(data, truth_iv, predictions, contacts),
            "relevance": relevance(data, contacts, predictions, truths),
            "proximity": proximity(data, contacts, predictions),
            "recovery": recovery(data, contacts),
            "phantom_entities": sum(1 for e in data.entities if data.entity_identity.get(e["id"]) is None),
            "entities": len(data.entities),
            "states": saved_state_errors(data)}
