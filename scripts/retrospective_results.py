#!/usr/bin/env python3
"""Aggregate the identity study (privileged evaluation): results/retrospective/summary<tag>.{json,md}.

    python scripts/retrospective_results.py --tag _S13_heldout

Per condition and variant (baseline, or a sensitivity variant; counts per draw = per run and seed, averaged over seeds and summed over runs):
merges (correct / false / missed), recorder links (wrong / missed), duplicate entities, sample identity
(correct / wrong / unresolved shares; also before the first contact by more than 2 s = early identity),
retrospective resolutions (made, correct), collisions (recall, wrong pairings, unmatched, ambiguous
refusals, recorders aligned).  Breakdowns by range and by time before the observer's first contact,
confidence calibration (stated association score against empirical accuracy) and the backward decisions
by gap.  Every number is traceable to the job lines (commit, config hash, variant, seed, perturbation, run).
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "baseline"
CONF_BINS = (0.0, 0.5, 0.8, 0.9, 0.95, 0.99, 1.0001)
GAP_BINS = (0.0, 0.5, 1.0, 2.0, 4.0, 1e9)
DIST_ORDER = ["0-10", "10-20", "20-30", "30-40", "40-50", "50-60", "60+"]
TIME_ORDER = ["0-0.5", "0.5-1", "1-2", "2-4", "4+", "after contact"]


def load(tag: str, base: Path = ROOT / "results" / "retrospective") -> Dict[str, List[Dict[str, Any]]]:
    """Jobs per variant folder (the baseline first)."""
    out = {}
    folders = sorted((p for p in base.iterdir() if p.is_dir()), key=lambda p: (p.name != BASELINE, p.name)) if base.exists() else []
    for folder in folders:
        path = folder / "jobs{0}.jsonl".format(tag)
        if path.exists():
            out[folder.name] = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return out


def bin_of(value, edges):
    for lo, hi in zip(edges, edges[1:]):
        if lo <= value < hi:
            return "{0:g}-{1:g}".format(lo, hi) if hi < 1e8 else "{0:g}+".format(lo)
    return None


def track_correct(track: Dict[str, Any]) -> bool:
    outcomes = {k: v for k, v in track["outcomes"].items() if k != "clutter"}
    return bool(outcomes) and max(outcomes, key=outcomes.get) == "correct"


def condition_table(jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_condition: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for job in jobs:
        if job["status"] == "complete":
            by_condition[job["condition"]].append(job)
    table = {}
    for condition, items in sorted(by_condition.items()):
        seeds = len({j["seed"] for j in items})
        per = lambda f: round(sum(f(j) for j in items) / max(seeds, 1), 2)
        samples = Counter()
        early = Counter()
        for j in items:
            for k in ("correct", "wrong", "unresolved"):
                samples[k] += j["identity"]["all"][k]
                early[k] += j["identity"]["early_2s"][k]
        total, etotal = sum(samples.values()), sum(early.values())
        retro = [d for j in items for d in (j.get("retrospective_decisions") or []) if d.get("resolved")]
        truth = {}
        for j in items:
            for t in j["tracks"]:
                truth[(j["run"], j["seed"], t["track"])] = t["true"]
        correct_retro = 0
        for j in items:
            for d in j.get("retrospective_decisions") or []:
                if not d.get("resolved"):
                    continue
                old = {truth.get((j["run"], j["seed"], n)) for n in d["earlier"]} - {None}
                new = Counter(truth.get((j["run"], j["seed"], n)) for n in d["later"])
                new.pop(None, None)
                if old and new and old == {new.most_common(1)[0][0]}:
                    correct_retro += 1
        failed = [j for j in items if j["status"] != "complete"]
        table[condition] = {
            "jobs": len(items), "seeds": seeds, "failed": len(failed),
            "merges_correct": per(lambda j: j["merges"]["correct"]), "merges_false": per(lambda j: j["merges"]["false"]),
            "merges_missed": per(lambda j: j["merges"]["missed"]),
            "links_wrong": per(lambda j: j["metrics"]["links_wrong"]),
            "links_missed": per(lambda j: j["verdicts"].get("missed link", 0)),
            "duplicate_entities": per(lambda j: j["duplicate_entities"]),
            "cannot_links": per(lambda j: j.get("cannot_links", 0)),
            "samples": total,
            "correct_share": round(samples["correct"] / total, 4) if total else None,
            "wrong_share": round(samples["wrong"] / total, 4) if total else None,
            "unresolved_share": round(samples["unresolved"] / total, 4) if total else None,
            "early_correct_share": round(early["correct"] / etotal, 4) if etotal else None,
            "early_wrong_share": round(early["wrong"] / etotal, 4) if etotal else None,
            "early_unresolved_share": round(early["unresolved"] / etotal, 4) if etotal else None,
            "retrospective_resolved": len(retro), "retrospective_correct": correct_retro,
            "collisions_reconstructed": sum(j["metrics"]["collisions_reconstructed"] for j in items),
            "collisions_true": sum(j["metrics"]["collisions_true"] for j in items),
            "collision_wrong": sum(j["metrics"]["false_collision_matches"] for j in items),
            "collision_unmatched": sum(j["collision_unmatched"] for j in items),
            "ambiguous_refusals": sum(j["ambiguous_refusals"] for j in items),
            "recorders_aligned": sum(j["metrics"]["recorders_aligned"] for j in items),
            "recorders": sum(j["metrics"]["recorders"] for j in items)}
    return table


def breakdown(jobs: List[Dict[str, Any]], key: str, conditions) -> Dict[str, Dict[str, Any]]:
    pooled: Dict[str, Counter] = defaultdict(Counter)
    for j in jobs:
        if j["status"] != "complete" or j["condition"] not in conditions:
            continue
        for label, block in j["identity"][key].items():
            for k in ("correct", "wrong", "unresolved"):
                pooled[label][k] += block[k]
    out = {}
    for label, c in pooled.items():
        n = sum(c.values())
        out[label] = {"samples": n, **{k + "_share": round(c[k] / n, 4) if n else None for k in ("correct", "wrong", "unresolved")}}
    return out


def calibration(jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
    bins: Dict[str, List[bool]] = defaultdict(list)
    by_distance: Dict[str, List[float]] = defaultdict(list)
    by_time: Dict[str, List[float]] = defaultdict(list)
    for j in jobs:
        if j["status"] != "complete":
            continue
        for t in j["tracks"]:
            c = t.get("confidence")
            if c is None or t.get("true") is None:
                continue
            ok = track_correct(t)
            bins[bin_of(c, CONF_BINS)].append(ok)
            by_distance[bin_of(t["min_range_m"], (0, 10, 20, 30, 40, 50, 60, 1e9))].append(c)
            tb = t.get("time_before_contact_s")
            if tb is not None and tb >= 0:
                by_time[bin_of(tb, (0, 0.5, 1, 2, 4, 1e9))].append(c)
    return {"reliability": {k: {"tracks": len(v), "stated_mid": None, "empirical_accuracy": round(sum(v) / len(v), 4)}
                            for k, v in sorted(bins.items())},
            "confidence_by_min_range": {k: {"tracks": len(v), "median": round(statistics.median(v), 4)} for k, v in sorted(by_distance.items())},
            "confidence_by_time_before_contact": {k: {"tracks": len(v), "median": round(statistics.median(v), 4)} for k, v in sorted(by_time.items())}}


def gaps(jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
    truth = {}
    for j in jobs:
        for t in j.get("tracks", []):
            truth[(j["run"], j["seed"], j["condition"], t["track"])] = t["true"]
    out: Dict[str, Counter] = defaultdict(Counter)
    for j in jobs:
        for d in j.get("retrospective_decisions") or []:
            label = bin_of(d["gap_s"], GAP_BINS)
            old = {truth.get((j["run"], j["seed"], j["condition"], n)) for n in d["earlier"]} - {None}
            new = Counter(truth.get((j["run"], j["seed"], j["condition"], n)) for n in d["later"])
            new.pop(None, None)
            same = bool(old and new and old == {new.most_common(1)[0][0]})
            if d.get("resolved"):
                out[label]["resolved_correct" if same else "resolved_wrong"] += 1
            else:
                out[label]["unresolved_same_vehicle" if same else "unresolved_other_vehicle"] += 1
    return {k: dict(v) for k, v in sorted(out.items())}


def markdown(record: Dict[str, Any]) -> str:
    variants = list(record["variants"])
    lines = ["# Identity study ({0})".format(record["tag"]), "",
             "Privileged evaluation of `scripts/retrospective_study.py`; provenance at the end.  Counts per draw "
             "(summed over runs, averaged over seeds); shares over all measured samples.", ""]
    cols = ["merges_correct", "merges_false", "merges_missed", "links_wrong", "links_missed", "duplicate_entities",
            "correct_share", "wrong_share", "unresolved_share", "early_correct_share", "early_wrong_share",
            "retrospective_resolved", "retrospective_correct"]
    lines += ["| condition | variant | seeds | " + " | ".join(cols) + " |", "|---|---|--:|" + "--:|" * len(cols)]
    conditions = sorted({c for m in record["variants"].values() for c in m["conditions"]})
    for condition in conditions:
        for variant in variants:
            row = record["variants"][variant].get("conditions", {}).get(condition)
            if row:
                lines.append("| {0} | {1} | {2} | ".format(condition, variant, row["seeds"]) +
                             " | ".join(str(row[c]) for c in cols) + " |")
    lines += ["", "## Collisions", "",
              "| condition | variant | recall | wrong pairings | unmatched true contacts | ambiguous refusals | recorders aligned |",
              "|---|---|---|--:|--:|--:|---|"]
    for condition in conditions:
        for variant in variants:
            row = record["variants"][variant].get("conditions", {}).get(condition)
            if row:
                lines.append("| {0} | {1} | {2}/{3} | {4} | {5} | {6} | {7}/{8} |".format(
                    condition, variant, row["collisions_reconstructed"], row["collisions_true"], row["collision_wrong"],
                    row["collision_unmatched"], row["ambiguous_refusals"], row["recorders_aligned"], row["recorders"]))
    for name, key, order in (("Range from the observing radar", "by_distance", DIST_ORDER),
                             ("Time before the observer's first contact", "by_time", TIME_ORDER)):
        for group, label in (("exact_like", "exact and RTK"), ("consumer_like", "consumer and correlated consumer")):
            lines += ["", "## {0} ({1})".format(name, label), "",
                      "| bin [m or s] | " + " | ".join("{0} correct / wrong / unresolved (samples)".format(v) for v in variants) + " |",
                      "|---|" + "---|" * len(variants)]
            for b in order:
                cells = []
                for variant in variants:
                    block = record["variants"][variant].get(key, {}).get(group, {}).get(b)
                    cells.append("-" if not block else "{0} / {1} / {2} ({3}{4})".format(
                        block["correct_share"], block["wrong_share"], block["unresolved_share"], block["samples"],
                        ", few" if block["samples"] < 50 else ""))
                lines.append("| {0} | ".format(b) + " | ".join(cells) + " |")
    lines += ["", "## Confidence calibration (tracks with an association score)", "",
              "| variant | score bin | tracks | empirical accuracy |", "|---|---|--:|--:|"]
    for variant in variants:
        for b, v in record["variants"][variant].get("calibration", {}).get("reliability", {}).items():
            lines.append("| {0} | {1} | {2} | {3} |".format(variant, b, v["tracks"], v["empirical_accuracy"]))
    lines += ["", "## Backward decisions by gap (baseline)", "", "| gap [s] | outcome counts |", "|---|---|"]
    for b, v in record["variants"].get(BASELINE, {}).get("gaps", {}).items():
        lines.append("| {0} | {1} |".format(b, ", ".join("{0} {1}".format(k, n) for k, n in sorted(v.items()))))
    lines += ["", "## Provenance", "", "```", json.dumps(record["provenance"], indent=1), "```", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--results", type=Path, default=ROOT / "results" / "retrospective",
                        help="folder of the <variant>/jobs<tag>.jsonl files; the summary is written there")
    args = parser.parse_args()
    data = load(args.tag, args.results)
    exact_like = {"exact", "rtk", "exact_impulse10", "rtk_impulse10"}
    record: Dict[str, Any] = {"tag": args.tag, "variants": {}}
    commits, configs, seeds, conditions, runs = set(), set(), set(), set(), set()
    for variant, jobs in data.items():
        all_conditions = {j["condition"] for j in jobs}
        record["variants"][variant] = {
            "conditions": condition_table(jobs),
            "by_distance": {"exact_like": breakdown(jobs, "by_distance", exact_like),
                            "consumer_like": breakdown(jobs, "by_distance", all_conditions - exact_like - {"degraded"})},
            "by_time": {"exact_like": breakdown(jobs, "by_time", exact_like),
                        "consumer_like": breakdown(jobs, "by_time", all_conditions - exact_like - {"degraded"})},
            "calibration": calibration(jobs), "gaps": gaps(jobs),
            "failed": [{"run": j["run"], "condition": j["condition"], "seed": j["seed"], "error": j.get("error")}
                       for j in jobs if j["status"] != "complete"]}
        for j in jobs:
            p = j["provenance"]
            commits.add((p.get("git_commit"), p.get("git_dirty"), p.get("code_sha256")))
            configs.add(p.get("config_sha256"))
            seeds.add(j["seed"]); conditions.add(j["condition"]); runs.add(Path(j["run"]).parent.name + "/" + Path(j["run"]).name)
    record["provenance"] = {"commits": [list(c) for c in sorted(commits, key=str)], "config_sha256": sorted(str(c) for c in configs),
                            "seeds": sorted(seeds), "conditions": sorted(conditions), "runs": sorted(runs),
                            "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    out = args.results / "summary{0}".format(args.tag)
    out.with_suffix(".json").write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    out.with_suffix(".md").write_text(markdown(record), encoding="utf-8")
    print(out.with_suffix(".md"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
