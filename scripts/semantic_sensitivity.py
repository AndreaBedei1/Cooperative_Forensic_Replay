#!/usr/bin/env python3
"""One-at-a-time sensitivity of the core events to the semantic thresholds (privileged: evaluation side).

    python scripts/semantic_sensitivity.py traces/S*/run_* --label canonical [--workers 12]

For every threshold of ``VARIANTS`` and each of its alternative values (the others at their nominal value):

* the reconstruction's core events: the recorder's own tracks (tracked once, the tracker does not depend
  on these thresholds) through the same calls as ``cdf.reconstruction.local.reconstruct_vehicle``
  (``mark_occlusions``, ``contact_partners``, ``track_events``);
* the ground-truth oracle's events (``cdf.evaluation.event_oracle``) under the same definition: a definitional
  threshold changes the oracle too, a perception threshold (the nominal target box, the estimate gates) only
  the reconstruction.

Reported, before each recorder's first contact (the pre-crash window): the reconstruction against the
COVERAGE oracle (precision, recall, time differences) under each value, and how far the oracle's own events
move against the nominal definition (the definitional sensitivity: what the threshold choice alone does to
the "true" event).  Results: ``results/semantics/sensitivity_<label>.{json,md,csv}``.
"""

from __future__ import annotations

import argparse
import csv
import dataclasses
import json
import math
import statistics
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

# (threshold, alternative values, definitional): a definitional threshold is part of the event definition
# and changes the oracle as well; otherwise it is a perception assumption of the reconstruction only.
VARIANTS: List[Tuple[str, List[Any], bool]] = [
    ("critical_reaction_time_s", [0.7, 1.5], True),
    ("critical_deceleration_mps2", [5.0, 8.0], True),
    ("critical_release_ratio", [0.6, 0.9], True),
    ("critical_min_following_distance_m", [1.0, 3.0], True),
    ("critical_time_gap_table", ["x0.8", "x1.2"], True),
    ("path_half_width_m", [1.25, 1.75], True),
    ("cut_in_lateral_speed_mps", [0.2, 0.5], True),
    ("cut_in_persistence_s", [0.3, 0.8], True),
    ("cut_in_outside_margin_m", [0.3, 0.8], True),
    ("cut_in_horizon_s", [2.0, 4.0], True),
    ("target_length_m", [4.2, 5.0], False),
    ("max_position_std_m", [0.5, 1.5], False),
]


def variant_semantics(base: Any, name: str, value: Any) -> Any:
    if name == "critical_time_gap_table":
        factor = float(str(value)[1:])
        table = [[speed, round(gap * factor, 3)] for speed, gap in base.critical_time_gap_table]
        return dataclasses.replace(base, critical_time_gap_table=table)
    return dataclasses.replace(base, **{name: value})


def _reconstruction_events(locals_: Dict[str, Any], contacts: Dict[str, Any], identity: Dict[str, Optional[str]],
                           semantics: Any, cfg: Any, body_based: bool = True) -> Dict[str, List[Dict[str, Any]]]:
    from cdf.evaluation.event_oracle import _type
    from cdf.reconstruction.local import contact_partners, mark_occlusions, sample_period, track_events
    out: Dict[str, List[Dict[str, Any]]] = {}
    for owner, rec in locals_.items():
        mark_occlusions(rec.tracks, rec.ego, rec.footprint, semantics)
        partners = contact_partners(contacts[owner], rec.tracks, sample_period(rec.ego), semantics,
                                    cfg.fusion.touching_clearance_m)
        events = []
        for track in rec.tracks:
            for event in track_events(owner, track, rec.ego.end, semantics, rec.ego, None, rec.footprint,
                                      partners.get(track.track_id, ()), body_based=body_based):
                family = _type(event.type)
                if family is not None:
                    events.append({"type": family, "side": event.type, "t_local": round(event.t_local, 4),
                                   "subject": identity.get("{0}:{1}".format(owner, track.track_id)),
                                   "track": track.track_id})
        out[owner] = events
    return out


def one_run(run: str) -> Dict[str, Any]:
    from cdf.evaluation.event_oracle import compare_run, prepare_truth
    from cdf.reconstruction.config import load_config
    from cdf.reconstruction.local import collision_contacts, read_jsonl, reconstruct_vehicle
    try:
        run_dir = Path(run)
        cfg = load_config()
        truth = prepare_truth(run_dir, cfg)
        evaluation = json.loads((run_dir / "reconstruction" / "evaluation" / "evaluation.json").read_text(encoding="utf-8"))
        identity = {row["track"]: row.get("true_identity") for row in evaluation["tracks"]}
        locals_, contacts = {}, {}
        for vehicle_dir in sorted(p for p in (run_dir / "vehicles").iterdir() if (p / "ego.jsonl").exists()):
            rec = reconstruct_vehicle(vehicle_dir, cfg)
            locals_[rec.owner] = rec
            contacts[rec.owner] = collision_contacts(read_jsonl(vehicle_dir / "collisions.jsonl"), rec.clock_origin,
                                                     cfg.collision, rec.ego)
        out = {"run": run, "variants": {}}
        settings = [("nominal", None, True)] + [(name, value, definitional) for name, values, definitional in VARIANTS
                                                for value in values]
        for name, value, definitional in settings:
            semantics = cfg.semantics if value is None else variant_semantics(cfg.semantics, name, value)
            varied = dataclasses.replace(cfg, semantics=semantics)
            oracle_cfg = varied if definitional else cfg
            reconstructed = _reconstruction_events(locals_, contacts, identity, semantics, cfg)
            result = compare_run(run_dir, oracle_cfg, truth, reconstructed)
            key = "nominal" if value is None else "{0}={1}".format(name, value)
            out["variants"][key] = {"comparison_pre_contact": result["comparison_pre_contact"],
                                    "events": result["events"], "first_contact": result["first_contact_t_local"]}
        return out
    except Exception as exc:  # recorded; the study goes on
        import traceback
        return {"run": run, "error": repr(exc), "trace": traceback.format_exc()[-2000:]}


def _shift(nominal: Dict[str, Any], varied: Dict[str, Any], contact: Dict[str, float]) -> Dict[str, Any]:
    """The COVERAGE oracle's own events under the varied definition against the nominal one (pre-contact)."""
    from cdf.evaluation.event_oracle import CORE_TYPES, match
    rows: Dict[str, Dict[str, Any]] = {t: {"nominal": 0, "varied": 0, "matched": 0, "deltas": []} for t in CORE_TYPES}
    for owner in sorted(set(nominal) | set(varied)):
        cut = contact.get(owner, math.inf)
        a = [e for e in varied.get(owner, []) if e["t_local"] < cut]
        b = [e for e in nominal.get(owner, []) if e["t_local"] < cut]
        pairs, _, _ = match(a, b)
        for e in a:
            rows[e["type"]]["varied"] += 1
        for e in b:
            rows[e["type"]]["nominal"] += 1
        for i, j in pairs:
            rows[a[i]["type"]]["matched"] += 1
            rows[a[i]["type"]]["deltas"].append(round(a[i]["t_local"] - b[j]["t_local"], 4))
    return rows


def summarize(results: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    from cdf.evaluation.event_oracle import CORE_TYPES, pooled
    keys = list(results[0]["variants"]) if results else []
    out: Dict[str, Any] = {}
    for key in keys:
        both = pooled([r["variants"][key] for r in results], "comparison_pre_contact")
        agreement = both["RECONSTRUCTION vs COVERAGE"]
        agreement_tracked = both["RECONSTRUCTION vs COVERAGE_TRACKED"]
        shift: Dict[str, Dict[str, Any]] = {t: {"nominal": 0, "varied": 0, "matched": 0, "deltas": []} for t in CORE_TYPES}
        for r in results:
            rows = _shift(r["variants"]["nominal"]["events"]["COVERAGE"], r["variants"][key]["events"]["COVERAGE"],
                          r["variants"]["nominal"]["first_contact"])
            for t in CORE_TYPES:
                for field in ("nominal", "varied", "matched"):
                    shift[t][field] += rows[t][field]
                shift[t]["deltas"] += rows[t]["deltas"]
        out[key] = {"agreement": agreement, "agreement_tracked_point": agreement_tracked,
                    "oracle_shift": {t: {"nominal": v["nominal"], "varied": v["varied"], "matched": v["matched"],
                                         "moved": sum(1 for d in v["deltas"] if abs(d) > 1e-9),
                                         "delta_median_s": round(statistics.median(v["deltas"]), 3) if v["deltas"] else None,
                                         "abs_delta_max_s": round(max(abs(d) for d in v["deltas"]), 3) if v["deltas"] else None}
                                     for t, v in shift.items()}}
    return out


SHOWN = ("EGO_PATH_ENTRY", "CUT_IN_FROM_LEFT_START", "CUT_IN_FROM_RIGHT_START", "CRITICAL_TTC_START", "CRITICAL_TTC_END")
SHORT = {"EGO_PATH_ENTRY": "path entry", "CUT_IN_FROM_LEFT_START": "cut-in L", "CUT_IN_FROM_RIGHT_START": "cut-in R",
         "CRITICAL_TTC_START": "CTTC start", "CRITICAL_TTC_END": "CTTC end"}


def markdown(record: Dict[str, Any]) -> str:
    prov = record["provenance"]
    lines = ["# Sensitivity of the core events to the semantic thresholds ({0})".format(record["label"]), "",
             "One threshold at a time (`scripts/semantic_sensitivity.py`), before each recorder's first contact.  "
             "Agreement: the reconstruction against the COVERAGE oracle under the same definition, as recall / "
             "precision / median time difference [s].  Oracle shift: the COVERAGE oracle's own events under the "
             "varied definition against the nominal one, as events (varied / nominal) and median shift of the "
             "matched ones [s]: what the choice of threshold alone does to the reference events.  A perception "
             "threshold (the nominal target box, the estimate gates) leaves the oracle unchanged.", "",
             "Runs: {0} ({1} failed).  Provenance: code `{2}`, configuration `{3}`, commit `{4}`{5}, {6}.".format(
                 record["runs"], len(record["failed"]), prov["code_sha256"][:16], (prov.get("config_sha256") or "")[:16],
                 prov["git_commit"], " (uncommitted changes)" if prov["git_dirty"] else "", prov["generated_utc"]), "",
             "| setting | " + " | ".join("{0}: agreement".format(SHORT[t]) for t in SHOWN) + " | "
             + " | ".join("{0}: oracle shift".format(SHORT[t]) for t in SHOWN) + " |",
             "|---|" + "---|" * (2 * len(SHOWN))]
    for key, row in record["variants"].items():
        cells = []
        for t in SHOWN:
            a = row["agreement"][t]
            cells.append("-" if a["expected"] == 0 and a["found"] == 0 else "{0} / {1} / {2}".format(
                "-" if a["recall"] is None else "{0:.2f}".format(a["recall"]),
                "-" if a["precision"] is None else "{0:.2f}".format(a["precision"]),
                "-" if a["delta_median_s"] is None else "{0:+.2f}".format(a["delta_median_s"])))
        for t in SHOWN:
            s = row["oracle_shift"][t]
            cells.append("{0}/{1}, {2}".format(s["varied"], s["nominal"],
                                               "-" if s["delta_median_s"] is None else "{0:+.2f}".format(s["delta_median_s"])))
        lines.append("| {0} | {1} |".format(key, " | ".join(cells)))
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("runs", nargs="+", type=Path)
    parser.add_argument("--label", required=True)
    parser.add_argument("--results", type=Path, default=ROOT / "results" / "semantics")
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args(argv)
    from cdf.evaluation.provenance import provenance
    from cdf.reconstruction.config import load_config
    runs = [str(run) for run in args.runs if (run / "reconstruction" / "evaluation" / "evaluation.json").exists()]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(one_run, runs))
    done = [r for r in results if "error" not in r]
    failed = [{"run": r["run"], "error": r["error"]} for r in results if "error" in r]
    record = {"definition": "one-at-a-time sensitivity of the core events to the semantic thresholds; privileged "
                            "evaluation (ground-truth event oracle)",
              "label": args.label, "variants_tested": [[n, v, d] for n, v, d in VARIANTS],
              "provenance": provenance(load_config().to_dict(), [r["run"] for r in done]),
              "runs": len(done), "failed": failed, "variants": summarize(done)}
    args.results.mkdir(parents=True, exist_ok=True)
    base = args.results / "sensitivity_{0}".format(args.label)
    base.with_suffix(".json").write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    base.with_suffix(".md").write_text(markdown(record), encoding="utf-8")
    with base.with_suffix(".csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["setting", "event", "recall", "precision", "delta_median_s", "oracle_varied", "oracle_nominal",
                         "oracle_shift_median_s", "oracle_shift_abs_max_s"])
        for key, row in record["variants"].items():
            for t in row["agreement"]:
                a, s = row["agreement"][t], row["oracle_shift"][t]
                writer.writerow([key, t, a["recall"], a["precision"], a["delta_median_s"], s["varied"], s["nominal"],
                                 s["delta_median_s"], s["abs_delta_max_s"]])
    print(markdown(record))
    for item in failed:
        print("FAILED", item["run"], item["error"])
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
