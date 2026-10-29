#!/usr/bin/env python3
"""Deterministic worked example of a reconstructed run (default: S12), no model call.

    python scripts/worked_example.py traces/S12/run_0_crash [--observer A] [--track track_001]

Writes ``<run>/reconstruction/evaluation/<scenario>_worked_example.md`` (a privileged evaluation artifact):
part 1 from the recorders' own files and the reconstruction outputs only (under a file audit), part 2,
separated, against the ground truth; an isolation check reconstructs the run again without the privileged
files and requires byte-identical outputs.  See ``cdf.evaluation.worked_example``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cdf.evaluation.worked_example import write_worked_example  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run_dir", type=Path, nargs="?", default=ROOT / "traces" / "S12" / "run_0_crash")
    parser.add_argument("--observer", default="A")
    parser.add_argument("--track", default="track_001", help="the observer's local track to follow")
    args = parser.parse_args()
    print(write_worked_example(args.run_dir, args.observer, args.track))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
