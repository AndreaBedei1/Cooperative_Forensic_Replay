"""Privileged per-sample identity evaluation (ground truth is used here only).

For every measured sample of every local track of an aligned recorder (``<recorder>/local_tracks.jsonl``, at
the trace rate) the true identity of its point (the true vehicle box nearest it within
``fusion_metrics.IDENTITY_MAX_BOX_DISTANCE_M``, else clutter) is compared with the identity the
reconstruction gave its track (``global/associations.json``): a recorder name, an anonymous road user
U1, U2, ... (``global/anonymous_entities.json``) or the track's own anonymous name.

Per sample (clutter excluded):

* ``correct``: a recorder link to its true vehicle; or an anonymous entity that is the PRIMARY entity of its
  true vehicle (the entity holding most of that vehicle's samples) and whose majority is that vehicle;
* ``wrong``: a recorder link to another vehicle, or an entity whose majority is another vehicle;
* ``unresolved``: the sample's vehicle is right but its track sits in a secondary fragment of it (a
  missed merge or a missed recorder link): it is not wrong, it is not joined.

``relevant``: the sample lies within the observer's reconstruction relevance range
(``cdf.reconstruction.identity.relevance_range``: safe following distance + possible closure over the prediction
horizon + 3 sigma), computed from the track's own fields and the recorder's own speed.

Each sample also carries its range from the observing radar, its time before the observer's first matched
contact (else before t_global = 0) and, when the reconstruction recorded them, the identity's confidence,
the time its identity was resolved from and whether it was resolved retrospectively.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from .fusion_metrics import IDENTITY_MAX_BOX_DISTANCE_M
from .gt_audit import truth_of
from .reconstruction import _box_distance, _to_world

DISTANCE_BINS = (0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, float("inf"))
TIME_BINS = (0.0, 0.5, 1.0, 2.0, 4.0, float("inf"))


def _read_json(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    path = Path(path)
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def bin_label(value: Optional[float], edges) -> Optional[str]:
    if value is None:
        return None
    for lo, hi in zip(edges, edges[1:]):
        if lo <= value < hi:
            return "{0:g}+".format(lo) if hi == float("inf") else "{0:g}-{1:g}".format(lo, hi)
    return None


def identity_samples(run_dir: Path) -> Dict[str, Any]:
    """Per-sample identity outcome of one reconstructed run (module docstring)."""
    run_dir = Path(run_dir)
    rec = run_dir / "reconstruction"
    alignment = _read_json(rec / "global" / "alignment.json")
    associations = _read_json(rec / "global" / "associations.json")
    road_users = _read_json(rec / "global" / "anonymous_entities.json")
    recorders = sorted(alignment["graphs"])
    clocks = alignment["graphs"]
    aligned = {name for name, clock in clocks.items() if clock["status"] == "ALIGNED"}
    origins = {name: _read_json(rec / name / "local_graph.json")["recorder"]["clock"]["origin_source_timestamp"]
               for name in recorders}
    first_poses = {name: _read_jsonl(run_dir / "vehicles" / name / "ego.jsonl")[0] for name in recorders}
    truth, _ = truth_of(run_dir)
    decision = {(a["local_graph"], a["local_track"]): a for a in associations}
    contacts: Dict[str, float] = {}
    for event in alignment.get("matched_events", []):
        for graph in event["graphs"]:
            clock = clocks[graph]
            if clock["status"] == "ALIGNED":
                t = event["t_local"][graph] + clock["offset_to_global"]
                contacts[graph] = min(contacts.get(graph, t), t)

    from ..reconstruction.config import load_config
    from ..reconstruction.identity import relevance_range
    cfg = load_config()
    import numpy as np
    rows: List[Dict[str, Any]] = []
    for name in sorted(aligned):
        offset = clocks[name]["offset_to_global"]
        ego = _read_jsonl(run_dir / "vehicles" / name / "ego.jsonl")
        ego_t = np.array([float(r["timestamp"]) for r in ego])
        ego_v = np.array([float(np.hypot(r["velocity"]["x"], r["velocity"]["y"])) for r in ego])
        for row in _read_jsonl(rec / name / "local_tracks.jsonl"):
            if not row["measured"]:
                continue
            point = _to_world(first_poses[name], row["x_m"], row["y_m"])
            sim = row["t_local"] + origins[name]
            distances = {pid: _box_distance(point, state) for pid, track in truth.items() if pid != name
                         for state in [track.at(sim)] if state is not None}
            best = min(distances, key=distances.get) if distances else None
            identity = best if best is not None and distances[best] <= IDENTITY_MAX_BOX_DISTANCE_M else None
            item = decision.get((name, row["track_id"]), {})
            t_global = round(row["t_local"] + offset, 4)
            rows.append({"observer": name, "track": name + ":" + row["track_id"], "t_global": t_global,
                         "range_m": row["range_m"], "true": identity,
                         "assigned": item.get("global_entity"), "status": item.get("status"),
                         "time_before_contact_s": round(contacts.get(name, 0.0) - t_global, 4),
                         "confidence": item.get("identity_confidence", item.get("confidence")),
                         "resolved_from_t_global": item.get("identity_resolved_from"),
                         "retrospective": bool(item.get("retrospective")),
                         "relevant": bool(row.get("clearance_m") is not None and row["clearance_m"] <= relevance_range(
                             float(np.interp(sim, ego_t, ego_v)), float(row.get("closing_speed_mps") or 0.0),
                             float(row.get("vel_std_mps") or 0.0), float(row.get("pos_std_m") or 0.0), cfg))})

    # Entity majority and primary entity of every true vehicle.
    by_entity: Dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        if row["true"] is not None and row["assigned"] is not None:
            by_entity[row["assigned"]][row["true"]] += 1
    majority = {entity: votes.most_common(1)[0][0] for entity, votes in by_entity.items()}
    primary: Dict[str, str] = {}
    for vehicle in {row["true"] for row in rows if row["true"] is not None}:
        if vehicle in recorders:
            primary[vehicle] = vehicle
            continue
        held = Counter({entity: votes[vehicle] for entity, votes in by_entity.items()
                        if entity not in recorders and majority.get(entity) == vehicle})
        if held:
            primary[vehicle] = held.most_common(1)[0][0]
    for row in rows:
        if row["true"] is None:
            row["outcome"] = "clutter"
            continue
        assigned = row["assigned"]
        if assigned in recorders:
            row["outcome"] = "correct" if assigned == row["true"] else "wrong"
        elif majority.get(assigned) not in (None, row["true"]):
            row["outcome"] = "wrong"
        elif primary.get(row["true"]) == assigned:
            row["outcome"] = "correct"
        else:
            row["outcome"] = "unresolved"
        row["distance_bin"] = bin_label(row["range_m"], DISTANCE_BINS)
        tbc = row["time_before_contact_s"]
        row["time_bin"] = bin_label(tbc, TIME_BINS) if tbc is not None and tbc >= 0 else "after contact"
    entities = {entity["id"]: entity["source_tracks"] for entity in road_users.get("entities", [])}
    return {"run": "{0}/{1}".format(run_dir.parent.name, run_dir.name), "samples": rows,
            "entity_majority": majority, "primary_entity": primary, "entities": entities}


def summarize(rows: List[Dict[str, Any]], key: Optional[str] = None) -> Dict[str, Any]:
    """Counts and shares of correct / wrong / unresolved samples, overall or per ``key`` bin."""
    def block(items: List[Dict[str, Any]]) -> Dict[str, Any]:
        counts = Counter(row["outcome"] for row in items if row["outcome"] != "clutter")
        total = sum(counts.values())
        return {"samples": total, **{k: counts.get(k, 0) for k in ("correct", "wrong", "unresolved")},
                **{k + "_share": (round(counts.get(k, 0) / total, 4) if total else None)
                   for k in ("correct", "wrong", "unresolved")}}
    if key is None:
        return block(rows)
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["outcome"] != "clutter" and row.get(key) is not None:
            groups[row[key]].append(row)
    return {label: block(items) for label, items in sorted(groups.items())}
