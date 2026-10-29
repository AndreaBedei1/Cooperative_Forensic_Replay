"""Breakdowns of the existing fusion and collision evaluation for the robustness campaign.

PRIVILEGED evaluation only (ground truth is read here, never by the reconstruction).  Nothing here defines a new
event or identity criterion: every verdict is the one ``fusion_metrics.evaluate_fusion`` and
``reconstruction.evaluate_run`` already give; this module only groups them.

* Distance band of a local track: the median radar range (``range_m`` of ``local_tracks.jsonl``, the
  reconstruction's own measurement) over the track's measured samples, in ``BANDS``.  A track never measured is
  ``unmeasured``.  An anonymous entity or a true vehicle takes the band of its nearest track (smallest median
  range): a road user one recorder saw close counts as close.  A pair of tracks (merge verdicts) takes the
  band of its nearer track.
* Incident participants: the vehicles of the true vehicle-vehicle contacts (``ground_truth/collisions.jsonl``,
  recorders and non-recording vehicles alike).  A causal vehicle that never touches anybody (S12's B) is not in
  this set: no criterion for causal involvement exists in the evaluation.
* Collisions: a true contact is DETECTED when the reconstruction holds a collision node for it
  (``reconstructed_as``) and IDENTIFIED when that node names exactly its participants (``participants_correct``).
"""

from __future__ import annotations

import json
import statistics
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

BANDS = ((10.0, "0-10 m"), (25.0, "10-25 m"), (float("inf"), ">25 m"))
BAND_NAMES = [name for _, name in BANDS] + ["unmeasured"]


def band_of(range_m: Optional[float]) -> str:
    if range_m is None:
        return "unmeasured"
    for limit, name in BANDS:
        if range_m < limit:
            return name
    return BANDS[-1][1]


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _stats(values: Iterable[float]) -> Dict[str, Optional[float]]:
    data = sorted(float(v) for v in values)
    if not data:
        return {"n": 0, "median": None, "p95": None, "max": None}
    return {"n": len(data), "median": round(statistics.median(data), 4),
            "p95": round(data[min(len(data) - 1, int(round(0.95 * (len(data) - 1))))], 4),
            "max": round(data[-1], 4)}


def track_ranges(run_dir: Path) -> Dict[str, Optional[float]]:
    """``recorder:track`` -> median measured radar range [m] (None: never measured)."""
    out: Dict[str, Optional[float]] = {}
    rec = Path(run_dir) / "reconstruction"
    for path in sorted(rec.glob("*/local_tracks.jsonl")):
        ranges = defaultdict(list)
        seen = set()
        for row in _read_jsonl(path):
            seen.add(row["track_id"])
            if row.get("measured") and row.get("range_m") is not None:
                ranges[row["track_id"]].append(float(row["range_m"]))
        for track in seen:
            values = ranges.get(track)
            out[path.parent.name + ":" + track] = round(statistics.median(values), 3) if values else None
    return out


def incident_participants(run_dir: Path) -> List[str]:
    """Participants of the true vehicle-vehicle contacts (ground truth)."""
    run_dir = Path(run_dir)
    actor_to_pid = {}
    with (run_dir / "ground_truth" / "states.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            actor_to_pid.setdefault(row["actor_id"], row["participant_id"])
            if len(actor_to_pid) > 64:
                break
    out = set()
    for row in _read_jsonl(run_dir / "ground_truth" / "collisions.jsonl"):
        other = actor_to_pid.get(row.get("other_actor_id"))
        if other is not None and str(row.get("other_type_id", "")).startswith("vehicle."):
            out.update((row["participant_id"], other))
    return sorted(out)


def _category(verdict: str) -> str:
    head = verdict.split(" (")[0]
    if head.startswith("anonymous"):
        return "clutter" if "clutter" in verdict else "anonymous"
    return head  # "correct link", "WRONG link", "missed link"


def campaign_metrics(run_dir: Path, fusion: Mapping[str, Any], evaluation: Mapping[str, Any]) -> Dict[str, Any]:
    """The banded and incident-restricted counts of one reconstructed run (module docstring)."""
    run_dir = Path(run_dir)
    ranges = track_ranges(run_dir)
    incident = set(incident_participants(run_dir))
    decisions = fusion.get("track_decisions", [])

    by_band: Dict[str, Counter] = {name: Counter() for name in BAND_NAMES}
    incident_decisions: Counter = Counter()
    for row in decisions:
        category = _category(row["verdict"])
        by_band[band_of(ranges.get(row["track"]))][category] += 1
        if row.get("true_identity") in incident:
            incident_decisions[category] += 1

    # Merge verdicts over pairs of tracks in anonymous entities, exactly as evaluate_fusion counts them.
    entities = fusion.get("entities", [])
    member_of = {name: e["id"] for e in entities for name in e["source_tracks"]}
    identity = {row["track"]: row.get("true_identity") for row in decisions}
    for e in entities:
        for name, who in (e.get("track_identities") or {}).items():
            identity.setdefault(name, who)
    merges = {name: Counter() for name in BAND_NAMES}
    incident_merges: Counter = Counter()
    for first, second in combinations(sorted(member_of), 2):
        same_entity = member_of[first] == member_of[second]
        a, b = identity.get(first), identity.get(second)
        same_truth = a is not None and a == b
        verdict = ("correct" if same_entity and same_truth else "false" if same_entity
                   else "missed" if same_truth else None)
        if verdict is None:
            continue
        near = [r for r in (ranges.get(first), ranges.get(second)) if r is not None]
        merges[band_of(min(near) if near else None)][verdict] += 1
        if a in incident or b in incident:
            incident_merges[verdict] += 1

    def entity_range(source_tracks: Iterable[str]) -> Optional[float]:
        values = [ranges[name] for name in source_tracks if ranges.get(name) is not None]
        return min(values) if values else None

    entity_band = {e["id"]: band_of(entity_range(e["source_tracks"])) for e in entities}
    phantoms = Counter(entity_band[e["id"]] for e in entities if e.get("true_identity") is None)
    duplicates, incident_duplicates = Counter(), 0
    for who, ids in (fusion.get("fragmentation") or {}).items():
        if len(ids) < 2:
            continue
        tracks = [name for name in member_of if member_of[name] in ids]
        duplicates[band_of(entity_range(tracks))] += len(ids) - 1
        incident_duplicates += (len(ids) - 1) if who in incident else 0

    centre, velocity = defaultdict(list), defaultdict(list)
    incident_centre, incident_velocity = [], []
    for state in (fusion.get("_raw") or {}).get("paired_states", []):
        band = entity_band.get(state["entity"], "unmeasured")
        centre[band].append(state["centre_error_m"])
        if state.get("velocity_error_mps") is not None:
            velocity[band].append(state["velocity_error_mps"])
        if state.get("true_identity") in incident:
            incident_centre.append(state["centre_error_m"])
            if state.get("velocity_error_mps") is not None:
                incident_velocity.append(state["velocity_error_mps"])

    contacts = [row for row in evaluation.get("collisions", []) if "static/unrecorded" not in row["participants"]]
    timing = [abs(row["report_timing_error_s"]) for row in contacts
              if row.get("reconstructed_as") is not None and row.get("report_timing_error_s") is not None]
    return {
        "definition": "privileged breakdown of the existing fusion / collision verdicts (campaign_metrics docstring)",
        "incident_participants": sorted(incident),
        "track_ranges_m": ranges,
        "decisions_by_band": {band: dict(counts) for band, counts in by_band.items()},
        "decisions_incident": dict(incident_decisions),
        "merges_by_band": {band: dict(counts) for band, counts in merges.items()},
        "merges_incident": dict(incident_merges),
        "phantom_entities_by_band": dict(phantoms),
        "duplicate_hypotheses_by_band": dict(duplicates),
        "duplicate_hypotheses_incident": incident_duplicates,
        "centre_error_by_band_m": {band: _stats(values) for band, values in centre.items()},
        "velocity_error_by_band_mps": {band: _stats(values) for band, values in velocity.items()},
        "centre_error_incident_m": _stats(incident_centre),
        "velocity_error_incident_mps": _stats(incident_velocity),
        "collisions": {"true_contacts": len(contacts),
                       "detected": sum(row.get("reconstructed_as") is not None for row in contacts),
                       "identified": sum(bool(row.get("participants_correct")) for row in contacts),
                       "missed": sum(row.get("reconstructed_as") is None for row in contacts),
                       "detected_wrong_participants": sum(row.get("reconstructed_as") is not None
                                                          and not row.get("participants_correct") for row in contacts),
                       "extra_reconstructed": len(evaluation.get("extra_collisions", [])),
                       "extra_reconstructed_vehicle_pairs": sum(len(row.get("participants", [])) > 1
                                                                for row in evaluation.get("extra_collisions", [])),
                       "timing_error_s": _stats(timing)},
    }
