from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from canonical import canonical_runs


def server_line(extra) -> str:
    for k, arg in enumerate(extra):
        if arg == "--port" and k + 1 < len(extra):
            return "CARLA server at port {0}".format(extra[k + 1])
        if arg.startswith("--port="):
            return "CARLA server at port {0}".format(arg.split("=", 1)[1])
    return "CARLA server at the port of configs/default.yaml (simulation.port)"


def clock_offset(run: Path) -> float:
    rec = Path(run) / "reconstruction"
    alignment = json.loads((rec / "global" / "alignment.json").read_text(encoding="utf-8"))
    reference = None
    for name, clock in sorted(alignment["graphs"].items()):
        if clock["status"] == "ALIGNED" and clock.get("method", "matched_collisions") in ("matched_collisions",
                                                                                         "reference_recorder"):
            graph = json.loads((rec / name / "local_graph.json").read_text(encoding="utf-8"))
            reference = float(graph["recorder"]["clock"]["origin_source_timestamp"]) - float(clock["offset_to_global"])
            break
    gt = Path(run) / "ground_truth"
    with (gt / "states.jsonl").open(encoding="utf-8") as handle:
        actors = {json.loads(line)["actor_id"] for line in handle if line.strip()}
    with (gt / "collisions.jsonl").open(encoding="utf-8") as handle:
        contacts = [float(row["timestamp"]) for row in map(json.loads, filter(str.strip, handle))
                    if row["other_actor_id"] in actors]
    if reference is None or not contacts:
        return 0.0
    return round(reference - min(contacts), 3)


def clock_note(run: Path) -> Optional[str]:
    offset = clock_offset(run)
    if abs(offset) < 0.01:
        return None
    return ("note: the two clocks differ in this run: t_contact = t_global {0:+.2f} s (the reconstruction anchors "
            "t_global on its strongest matched contact, not on the first contact)").format(offset).replace(
                "t_global +", "t_global + ").replace("t_global -", "t_global - ")


def _option(extra: List[str], name: str) -> Tuple[Optional[str], List[str]]:
    rest, value, skip = [], None, False
    for k, arg in enumerate(extra):
        if skip:
            skip = False
        elif arg == name and k + 1 < len(extra):
            value, skip = extra[k + 1], True
        elif arg.startswith(name + "="):
            value = arg.split("=", 1)[1]
        else:
            rest.append(arg)
    return value, rest


def side_by_side(run: Path, extra: Sequence[str], gt_port: int, rec_port: int, sync_port: int
                 ) -> List[Tuple[List[str], Dict[str, str]]]:
    _, rest = _option(list(extra), "--port")
    res, _ = _option(rest, "--res")
    width = int((res or "1280x720").lower().split("x")[0])
    target = str(Path(run).relative_to(ROOT)) if Path(run).is_absolute() else str(run)
    views = []
    for script, port, sync, x in (("view_ground_truth.py", gt_port, ["--sync-lead", str(sync_port)], 0),
                                  ("replay_run.py", rec_port, ["--sync-follow", str(sync_port)], width + 10)):
        command = [sys.executable, str(ROOT / "scripts" / script), target, "--port", str(port)] + sync + rest
        views.append((command, dict(os.environ, SDL_VIDEO_WINDOW_POS="{0},40".format(x))))
    return views


def menu(runs, extra=(), gt_port=None):
    if gt_port:
        print("\nCanonical development runs (side by side: GROUND TRUTH on port {0} leading, RECONSTRUCTION on the {1} "
              "following):".format(gt_port, server_line(list(extra))))
    else:
        print("\nCanonical development runs (replay on the {0}):".format(server_line(list(extra))))
    for number, run in enumerate(runs, 1):
        label = "{0} {1}".format(run.parent.name, run.name[len("run_0_"):])
        missing = "" if (run / "reconstruction").is_dir() else "   (no reconstruction!)"
        print("  {0:2d}  {1}{2}".format(number, label, missing))
    both = "both side by side, synchronised" if gt_port else "ground truth, then reconstruction"
    print("   N  {0}    Ng  ground truth only    Nr  reconstruction only    q  quit".format(both))


def main() -> int:
    runs = canonical_runs()
    gt_port, extra = _option(sys.argv[1:], "--gt-port")
    sync_port, extra = _option(extra, "--sync-port")
    while True:
        menu(runs, extra, gt_port)
        try:
            choice = input("run number: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if choice in ("q", "quit", "exit", ""):
            return 0
        views = {"g": [True], "r": [False]}.get(choice[-1:], [True, False])
        number = choice[:-1] if choice[-1:] in ("g", "r") else choice
        if not number.isdigit() or not 1 <= int(number) <= len(runs):
            print("choose 1-{0} (optionally followed by g or r) or q".format(len(runs)))
            continue
        run = runs[int(number) - 1]
        if gt_port and views == [True, False]:
            rec_port, _ = _option(extra, "--port")
            processes = []
            for command, env in side_by_side(run, extra, int(gt_port), int(rec_port or 3000), int(sync_port or 47811)):
                print(" ".join(command))
                processes.append(subprocess.Popen(command, cwd=str(ROOT), env=env))
            for process in processes:
                process.wait()
            continue
        note = clock_note(run)
        if note:
            print(note)
        for ground_truth in views:
            script = "view_ground_truth.py" if ground_truth else "replay_run.py"
            command = [sys.executable, str(ROOT / "scripts" / script), str(run.relative_to(ROOT))] + extra
            print(" ".join(command))
            subprocess.call(command, cwd=str(ROOT))


if __name__ == "__main__":
    raise SystemExit(main())
