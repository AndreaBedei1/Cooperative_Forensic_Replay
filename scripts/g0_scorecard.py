from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from cdf.evaluation.scorecard import markdown, scorecard


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("runs", nargs="*", type=Path)
    parser.add_argument("--canonical", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT / "traces")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--title", default="G0 scorecard")
    args = parser.parse_args()
    runs = list(args.runs)
    if args.canonical:
        from canonical import CANONICAL
        runs += [args.root / s / ("run_0_" + v) for s, vs in sorted(CANONICAL.items()) for v in vs]
    cards = []
    for run in runs:
        card = scorecard(run)
        cards.append(card)
        c = card["collisions"]
        print("{0}: contacts {1}, identified {2}, invented {3}, missed observable {4}".format(
            card["run"], c["true"], c["identified"], c["invented"], card["completeness"]["missed_observable"]))
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "scorecard.json").write_text(json.dumps(cards, indent=1), encoding="utf-8")
    (args.out / "scorecard.md").write_text(markdown(cards, args.title), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
