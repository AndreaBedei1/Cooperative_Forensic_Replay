"""Per-run numbers pooled by the sweeps and the robustness study (privileged: evaluation side only).

``run_metrics`` reads a run's evaluation results (``cdf.evaluation.reconstruction``,
``cdf.evaluation.fusion_metrics``); ``core_event_diff`` compares the core events of two reconstructions of
the same run (a perturbed one against the unperturbed one) without ground truth.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from ..reconstruction.models import PAPER_CORE_EVENTS

# The core events a perturbed reconstruction is expected to keep: instants, not durations.
DIFF_EVENTS = ("COLLISION", "BRAKE_START", "CRITICAL_TTC_START", "CUT_IN_FROM_LEFT_START", "CUT_IN_FROM_RIGHT_START",
               "EGO_PATH_ENTRY")
MATCH_WINDOW_S = 1.0


def _read_json(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def run_metrics(run_dir: Path, evaluation: Dict[str, Any], fusion: Dict[str, Any]) -> Dict[str, Any]:
    alignment = _read_json(Path(run_dir) / "reconstruction" / "global" / "alignment.json")
    decided = [row for row in evaluation["tracks"] if row["status"] == "ASSOCIATED"]
    between = [row for row in evaluation["collisions"] if "static/unrecorded" not in row["participants"]
               and all(name in alignment["graphs"] for name in row["participants"])]
    counts = fusion["decision_counts"]
    errors = fusion["state_errors"]
    # The fused road users' centre error leaves recorder ghosts out (an anonymous road user that is in truth a
    # recorder is not a road-user estimate); results written before that split have every road user.
    road_users = fusion["road_user_state_errors"] if "road_user_state_errors" in fusion else errors
    relative = [abs(row["error_s"]) for row in evaluation.get("relative_clock_offsets", []) if row.get("error_s") is not None]
    return {"recorders": len(alignment["graphs"]),
            "recorders_aligned": sum(1 for clock in alignment["graphs"].values() if clock["status"] == "ALIGNED"),
            "alignment_methods": sorted({clock.get("method") for clock in alignment["graphs"].values() if clock.get("method")}),
            "collisions_reconstructed": sum(bool(row["participants_correct"]) for row in between),
            "collisions_true": len(between),
            "false_collision_matches": sum(len(row.get('participants', [])) > 1
                                           for row in evaluation.get('extra_collisions', [])),
            "associations_correct": sum(row["verdict"] == "correct" for row in decided),
            "associations_decided": len(decided),
            "anonymous_tracks": sum(row["status"] != "ASSOCIATED" for row in evaluation["tracks"]),
            "max_abs_t_global_error_s": evaluation["event_timing"]["max_abs_error_s"],
            "max_abs_relative_offset_error_s": round(max(relative), 4) if relative else None,
            "links_correct": counts.get("correct link", 0), "links_wrong": counts.get("WRONG link", 0),
            "links_missed": counts.get("missed link", 0),
            "merges_correct": fusion["merges"]["correct"], "merges_false": fusion["merges"]["false"],
            "merges_missed": fusion["merges"]["missed"], "entities": len(fusion["entities"]),
            "entities_without_vehicle": sum(1 for e in fusion["entities"] if e["true_identity"] is None),
            "entity_purity_min": min((e["purity"] for e in fusion["entities"] if e["purity"] is not None), default=None),
            "fused_centre_error_median_m": (road_users.get("centre_error_m") or {}).get("median"),
            "single_track_centre_error_median_m": (errors.get("single_track_nominal_centre_error_m") or {}).get("median"),
            "observed_alignment_errors_s": [row["error_s"] for row in fusion["observed_alignment"] if row["accepted"]]}


def _events(graph: Dict[str, Any], keep_recorders: Optional[Iterable[str]] = None) -> List[Tuple[Tuple[Any, ...], float]]:
    """(key, t_global) of the instant core events; a subject is the recorder it was identified with, or just
    'anonymous' (track and road-user numbers are not stable under perturbation).  A recorder outside
    ``keep_recorders`` (dropped) is expected as an anonymous road user."""
    recorders = {e["entity_id"] for e in graph.get("entities", []) if e.get("kind") == "recorder"}
    keep = set(keep_recorders) if keep_recorders is not None else recorders
    out = []
    for node in graph["nodes"]:
        if node["event_type"] not in DIFF_EVENTS or node.get("t_global") is None:
            continue
        if node["event_type"] == "COLLISION":
            parties = tuple(sorted(p for p in node.get("participants") or [] if p in keep))
            if parties:
                out.append((("COLLISION", parties), float(node["t_global"])))
            continue
        if node.get("actor_id") not in keep:
            continue
        subject = node.get("subject_id")
        subject = subject if subject in recorders and subject in keep else ("anonymous" if subject else None)
        out.append(((node["event_type"], node["actor_id"], subject), float(node["t_global"])))
    return out


def core_event_diff(base_graph: Dict[str, Any], new_graph: Dict[str, Any],
                    keep_recorders: Optional[Iterable[str]] = None) -> Dict[str, Any]:
    """Core instant events of ``base_graph`` found again in ``new_graph`` (same type, actor and subject
    class within MATCH_WINDOW_S, nearest first), missing ones, extra ones, and the time differences."""
    base = sorted(_events(base_graph, keep_recorders), key=lambda item: item[1])
    new = sorted(_events(new_graph, keep_recorders), key=lambda item: item[1])
    # The zero of the global clock is a choice (the reference collision, or a reference recorder's own clock
    # when no collision is matched): the shift that lines up most events is removed first.
    candidates = sorted({round(t2 - t, 2) for key, t in base for k2, t2 in new if k2 == key} | {0.0}, key=abs)
    origin = max(candidates, key=lambda d: (sum(1 for key, t in base if any(k2 == key and abs(t2 - d - t) <= 0.06
                                                                           for k2, t2 in new)), -abs(d)))
    new = [(key, t - origin) for key, t in new]
    used = set()
    deltas: List[float] = []
    missing: List[str] = []
    for key, t in base:
        options = [(abs(t2 - t), i) for i, (k2, t2) in enumerate(new) if k2 == key and i not in used
                   and abs(t2 - t) <= MATCH_WINDOW_S]
        if options:
            _, i = min(options)
            used.add(i)
            deltas.append(round(new[i][1] - t, 4))
        else:
            missing.append("{0} @ {1:+.2f}".format("/".join(str(part) for part in key if part), t))
    extra = ["{0} @ {1:+.2f}".format("/".join(str(part) for part in key if part), t)
             for i, (key, t) in enumerate(new) if i not in used]
    identical = (len(base) == len(new) and not missing and not extra and all(abs(d) < 1e-9 for d in deltas)
                 and abs(origin) < 1e-9)
    return {"base_events": len(base), "matched": len(deltas), "missing": missing, "extra": extra,
            "time_deltas_s": deltas, "clock_origin_shift_s": origin, "identical": identical}


def graph_signature(graph: Dict[str, Any]) -> List[Tuple[Any, ...]]:
    """Every node of a global graph as (type, actor, subject, participants, t_global): for identity checks."""
    return [(n["event_type"], n.get("actor_id"), n.get("subject_id"), tuple(n.get("participants") or ()),
             None if n.get("t_global") is None else round(float(n["t_global"]), 4)) for n in graph["nodes"]]
