#!/usr/bin/env python3
"""Identity report of reconstructed dense runs (privileged evaluation, after the reconstruction).

    python scripts/dense_identity_report.py <reconstructed run> ... --out <file.md>

Per run: physical road users seen, local tracks, global entities, unresolved (anonymous single-track) and
retrospectively resolved entities; per physical car its local tracks (observer:track, time span, samples,
share inside the relevance envelope) and the entities they ended in; fragmentation counted separately for the
samples INSIDE the relevance envelope (``identity.relevance_range``: a car that matters) and OUTSIDE it (a
distant car that never matters).  The reconstruction's files are read as written; the true identity of each
sample comes from ``identity_timeline.identity_samples`` (ground truth, evaluation only).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.cdf.evaluation.identity_timeline import identity_samples  # noqa: E402


def report(run: Path) -> list:
    rec = run / "reconstruction"
    entities = json.loads((rec / "global" / "anonymous_entities.json").read_text(encoding="utf-8"))["entities"]
    associations = json.loads((rec / "global" / "associations.json").read_text(encoding="utf-8"))
    recorders = sorted(p.name for p in (run / "vehicles").iterdir() if p.is_dir())
    rows = identity_samples(run)["samples"]
    by_track = defaultdict(list)
    for r in rows:
        by_track[r["track"]].append(r)
    truth = {}
    for track, rs in by_track.items():
        votes = Counter(r["true"] for r in rs if r["true"] is not None)
        truth[track] = votes.most_common(1)[0][0] if votes else None
    assigned = {a["local_graph"] + ":" + a["local_track"]: a for a in associations}
    physical = sorted({v for v in truth.values() if v is not None})
    retro = [a for a in associations if a.get("retrospective")]
    unresolved = [e for e in entities if len(e["source_tracks"]) == 1]
    out = ["## {0}/{1}".format(run.parent.name, run.name), "",
           "| physical road users seen | recorders | local tracks | global anonymous entities | single-track entities "
           "(unresolved) | tracks resolved retrospectively |", "|--:|---|--:|--:|--:|--:|",
           "| {0} | {1} | {2} | {3} | {4} | {5} |".format(len([p for p in physical if p not in recorders]),
                                                        ",".join(recorders), len(by_track), len(entities),
                                                        len(unresolved), len(retro)), ""]
    frag = ["| car | entities (relevant samples) | entities (non-relevant samples) | relevant samples | "
            "non-relevant samples | wrong samples |", "|---|--:|--:|--:|--:|--:|"]
    detail = []
    for car in physical:
        tracks = sorted((t for t, v in truth.items() if v == car), key=lambda t: by_track[t][0]["t_global"])
        samples = [r for t in tracks for r in by_track[t] if r["true"] == car]
        rel = [r for r in samples if r["relevant"]]
        non = [r for r in samples if not r["relevant"]]
        ent = lambda rs: len({r["assigned"] for r in rs if r["assigned"] is not None})
        wrong = sum(1 for t in by_track for r in by_track[t] if r["true"] == car and r.get("outcome") == "wrong")
        frag.append("| {0}{1} | {2} | {3} | {4} | {5} | {6} |".format(car, " (recorder)" if car in recorders else "",
                                                                    ent(rel), ent(non), len(rel), len(non), wrong))
        detail.append("**{0}**{1}".format(car, " (recorder)" if car in recorders else ""))
        for t in tracks:
            rs = by_track[t]
            a = assigned.get(t, {})
            share = sum(r["relevant"] for r in rs) / len(rs)
            detail.append("- `{0}` {1:+.2f} .. {2:+.2f} s, {3} samples, {4:.0%} relevant, min range {5:.0f} m -> {6}{7}{8}".format(
                t, rs[0]["t_global"], rs[-1]["t_global"], len(rs), share, min(r["range_m"] for r in rs),
                a.get("global_entity"), " (resolved from {0:+.2f} s)".format(a["identity_resolved_from"])
                if a.get("identity_resolved_from") is not None else "", " RETRO" if a.get("retrospective") else ""))
        detail.append("")
    return out + ["Fragmentation inside vs outside the relevance envelope:", ""] + frag + ["", "Local tracks per car:", ""] + detail


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("runs", nargs="+", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    lines = ["# Identity report of the dense scenarios (evaluation only)", "",
             "Times t_global [s], 0 = the collision.  `entities (relevant samples)`: how many global entities carry "
             "the car's samples while it is inside an observer's relevance envelope (1 = not fragmented where it "
             "matters); `non-relevant`: the same outside it.", ""]
    for run in args.runs:
        lines += report(run)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
