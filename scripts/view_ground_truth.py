#!/usr/bin/env python3
"""GROUND TRUTH viewer of a recorded run: what CARLA simulated, to compare with the reconstruction.

    python scripts/view_ground_truth.py traces/S10/run_0_deflected_into_c --port 3000 [--speed 0.25]
    python scripts/view_ground_truth.py traces/S10/run_0_deflected_into_c --export DIR [--at T ...]

PRIVILEGED: reads only ``<run>/ground_truth/`` (cdf.replay.ground_truth): every vehicle, recorder or not, on its
true trajectory, and the physical contact episodes (COLLISION banner, CONTACT_START / CONTACT_END in the
vehicles' panels).  Nothing of the reconstruction is read or drawn.  Same window, camera, keys, speeds and
timeline as the RECONSTRUCTION viewer (scripts/replay_run.py, whose options it accepts); the clock shown is
``t_contact``, seconds from the first true vehicle-vehicle contact, which is where the reconstruction's
``t_global`` is anchored when it aligns the recorders on that collision.
"""

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
