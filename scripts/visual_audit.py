#!/usr/bin/env python3
"""Visual / semantic audit of reconstructed runs (evaluation side).

    python scripts/visual_audit.py traces/S*/run_* --name visual_audit_baseline --verdicts VERDICTS.json

For each run: the replay's headless top-down keyframes (``scripts/replay_run.py --export``: what the
reconstruction knows, no ground truth) are written to ``<run>/reconstruction/evaluation/<name>/``, the
automatic QA checks (``cdf.replay.qa``) flag what deserves a look, and
``<run>/reconstruction/evaluation/<name>.md`` records the reviewer's verdict per run and per finding
(PASS / WARN / FAIL, time, problem, frame, solution) from ``--verdicts``; ``traces/<name>.md`` indexes
the campaign.  The reviewer looks at every frame; a flag is a reason to look, not a verdict.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cdf.replay.model import ReplayRun  # noqa: E402
from cdf.replay.qa import check_run, flags_as_dicts  # noqa: E402


def _viewer():
    spec = importlib.util.spec_from_file_location("replay_run", str(ROOT / "scripts" / "replay_run.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True, text=True,
                              check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def run_name(run_dir: Path) -> str:
    return "{0}/{1}".format(run_dir.parent.name, run_dir.name)


def audit_run(viewer: Any, run_dir: Path, name: str, render: bool = True) -> Dict[str, Any]:
    out = run_dir / "reconstruction" / "evaluation" / name
    frames: List[Dict[str, Any]] = []
    if render:
        for old in out.glob("*.png"):
            old.unlink()
        frames = viewer.export_run(run_dir, out)
    elif (out / "audit.json").exists():
        frames = json.loads((out / "audit.json").read_text(encoding="utf-8"))["frames"]
    run = ReplayRun.load(run_dir)
    flags = flags_as_dicts(check_run(run))
    record = {"run": run_name(run_dir), "clock": run.clock, "frames": frames, "flags": flags,
              "reconstruction_commit": _commit(),
              "note": "frames and flags are reconstruction-only (ReplayRun inputs); verdicts by the reviewer"}
    out.mkdir(parents=True, exist_ok=True)
    (out / "audit.json").write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    return record


def write_markdown(run_dir: Path, name: str, record: Dict[str, Any], verdict: Dict[str, Any]) -> None:
    scenario = run_dir.parent.name
    lines = ["# Visual audit ({0}): {1}".format(name, record["run"]), "",
             "Reconstruction-only frames (top-down replay: recorded recorder poses, radar tracks as drawn by the "
             "replay, reconstructed events and states); no ground truth.  Reviewer verdict per finding.", "",
             "Run verdict: **{0}**".format(verdict.get("verdict", "PENDING")), ""]
    if verdict.get("summary"):
        lines += [verdict["summary"], ""]
    lines += ["| scenario | run | verdict | t_global [s] | problem | frame | solution |", "|---|---|---|---|---|---|---|"]
    findings = verdict.get("findings") or [{"verdict": verdict.get("verdict", "PENDING"), "time": "", "problem": "-",
                                            "frame": "", "solution": "-"}]
    for item in findings:
        frame = item.get("frame", "")
        link = "[{0}]({1}/{0})".format(frame, name) if frame else ""
        lines.append("| {0} | {1} | {2} | {3} | {4} | {5} | {6} |".format(
            scenario, run_dir.name, item.get("verdict", ""), item.get("time", ""), item.get("problem", ""), link,
            item.get("solution", "")))
    lines += ["", "## Frames", "", "| frame | t_global [s] | content |", "|---|---|---|"]
    for frame in record["frames"]:
        lines.append("| [{0}]({1}/{0}) | {2:+.2f} | {3} |".format(frame["file"], name, frame["display_time"],
                                                                frame["label"].replace("|", "/")))
    lines += ["", "## Automatic flags (reasons to look, not verdicts)", ""]
    if record["flags"]:
        lines += ["| check | t_global [s] | subject | detail |", "|---|---|---|---|"]
        lines += ["| {0} | {1:+.2f} | {2} | {3} |".format(f["check"], f["display_time"], f["subject"], f["detail"])
                  for f in record["flags"]]
    else:
        lines.append("none")
    lines += ["", "Reconstruction commit: `{0}`.".format(record["reconstruction_commit"]), ""]
    (run_dir / "reconstruction" / "evaluation" / (name + ".md")).write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Visual / semantic audit of reconstructed runs (evaluation side)")
    parser.add_argument("runs", nargs="+", type=Path)
    parser.add_argument("--name", default="visual_audit_baseline")
    parser.add_argument("--verdicts", type=Path, default=None, help="reviewer verdicts, JSON {run: {...}}")
    parser.add_argument("--no-render", action="store_true", help="keep the frames already exported")
    parser.add_argument("--index", type=Path, default=ROOT / "traces", help="folder of the campaign index")
    args = parser.parse_args()
    viewer = _viewer()
    verdicts = json.loads(args.verdicts.read_text(encoding="utf-8")) if args.verdicts else {}
    index = ["# Visual audit ({0})".format(args.name), "",
             "One row per run: the reviewer's verdict on the reconstruction-only replay frames "
             "(details and frames in each run's reconstruction/evaluation/{0}.md).".format(args.name), "",
             "| scenario | run | verdict | frames | automatic flags | summary |", "|---|---|---|---|---|---|"]
    for run_dir in args.runs:
        record = audit_run(viewer, run_dir, args.name, render=not args.no_render)
        verdict = verdicts.get(record["run"], {})
        write_markdown(run_dir, args.name, record, verdict)
        index.append("| {0} | {1} | {2} | {3} | {4} | {5} |".format(
            run_dir.parent.name, run_dir.name, verdict.get("verdict", "PENDING"), len(record["frames"]),
            len(record["flags"]), (verdict.get("summary") or "").replace("|", "/")))
        print(record["run"], len(record["frames"]), "frames,", len(record["flags"]), "flags,",
              verdict.get("verdict", "PENDING"))
    args.index.mkdir(parents=True, exist_ok=True)
    (args.index / (args.name + ".md")).write_text("\n".join(index) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
