#!/usr/bin/env python3
from __future__ import annotations

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from cdf.replay.ground_truth import load_ground_truth_run  # noqa: E402
import replay_run  # noqa: E402


def main(argv=None) -> int:
    args = replay_run.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    run = load_ground_truth_run(Path(args.run_dir))
    if args.export:
        for frame in replay_run.export_run(Path(args.run_dir), Path(args.export), args.at, args.format,
                                           args.map or run.map_name, run=run):
            logging.getLogger("view_ground_truth").info("%s  %s", frame["file"], frame["label"])
        return 0
    return replay_run.view(run, args)


if __name__ == "__main__":
    raise SystemExit(main())
