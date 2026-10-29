from __future__ import annotations

import argparse
import gzip
import json
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JOBS = ROOT / "results" / "robustness" / "campaign_v3" / "jobs.jsonl.gz"
_CODE: Optional[Path] = None


def read_records(path: Path) -> List[Dict[str, Any]]:
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(str(path), "rt", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def canonical(card: Any) -> str:
    return json.dumps(card, sort_keys=True)


def _init(code: str) -> None:
    global _CODE
    _CODE = Path(code)
    for path in (str(_CODE / "scripts"), str(_CODE / "src")):
        sys.path.insert(0, path)
    os.chdir(str(_CODE))
    commit = subprocess.run(["git", "rev-parse", "--verify", "--quiet", "campaign-v3^{commit}"], cwd=str(_CODE),
                            capture_output=True, text=True).stdout.strip()
    os.environ.update({"CDF_ANALYSIS_FREEZE_COMMIT": commit, "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
                       "OPENBLAS_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1"})


def job_of(record: Dict[str, Any], code: Path) -> Dict[str, Any]:
    run = Path(record["run"])
    job = {k: record[k] for k in ("family", "level", "parameter", "seed") if k in record}
    if record.get("recorder"):
        job["recorder"] = record["recorder"]
    job["run"] = str(code / "traces" / run.parent.name / run.name)
    return job


def _restore_parameter(job: Dict[str, Any]) -> Any:
    import robustness
    for label, parameter in robustness.FAMILIES[job["family"]][0]:
        if label == job["level"]:
            return parameter
    raise KeyError((job["family"], job["level"]))


def _run(record: Dict[str, Any], out: str) -> Dict[str, Any]:
    import robustness
    job = job_of(record, _CODE)
    job["parameter"] = _restore_parameter(job)
    result = robustness.run_job(job, out, True)
    perturbation, _ = robustness.build(job)
    tag = perturbation.name + ("_" + job["recorder"] if job.get("recorder") else "")
    kept = Path(out) / tag / "seed{0}".format(job["seed"]) / Path(job["run"]).parent.name / Path(job["run"]).name
    return {"family": job["family"], "level": job["level"], "recorder": job.get("recorder"), "seed": job["seed"],
            "run": "{0}/{1}".format(Path(job["run"]).parent.name, Path(job["run"]).name), "kept": str(kept),
            "status": result.get("status"), "error": result.get("error"),
            "scorecard_identical": canonical(result.get("scorecard")) == canonical(record.get("scorecard")),
            "provenance_commit": (result.get("provenance") or {}).get("git_commit"), "wall_s": result.get("wall_s")}


def key(r: Dict[str, Any]) -> tuple:
    run = Path(r["run"])
    return ("{0}/{1}".format(run.parent.name, run.name) if run.parent.name else r["run"], r["family"], r["level"],
            r.get("recorder") or None, int(r["seed"]))


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--code", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--jobs", type=Path, default=DEFAULT_JOBS)
    parser.add_argument("--families", default="baseline,radar_v3")
    parser.add_argument("--workers", type=int, default=20)
    parser.add_argument("--limit", type=int, default=None, help="run at most this many jobs (a check)")
    args = parser.parse_args(argv)
    families = set(args.families.split(","))
    records = [r for r in read_records(args.jobs) if r.get("status") == "complete" and r["family"] in families]
    args.out.mkdir(parents=True, exist_ok=True)
    log = args.out / "regenerated.jsonl"
    done = {key(r) for r in read_records(log)} if log.exists() else set()
    todo = [r for r in records if key(r) not in done]
    todo.sort(key=lambda r: -float(r.get("wall_s") or 0.0))
    if args.limit is not None:
        todo = sorted(todo, key=lambda r: float(r.get("wall_s") or 0.0))[:args.limit]
    print("{0} jobs of {1}; {2} already regenerated; {3} to run".format(len(records), sorted(families), len(done),
                                                                     len(todo)), flush=True)
    with ProcessPoolExecutor(max_workers=args.workers, initializer=_init, initargs=(str(args.code),)) as pool:
        futures = [pool.submit(_run, r, str(args.out)) for r in todo]
        for n, future in enumerate(as_completed(futures), 1):
            line = future.result()
            with log.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(line) + "\n")
            print("{0}/{1} {2} {3} {4} seed {5} {6} identical={7}".format(
                n, len(todo), line["run"], line["family"], line["level"], line["seed"], line["status"],
                line["scorecard_identical"]), flush=True)
    lines = read_records(log)
    print("regenerated {0}; scorecard identical {1}; failed {2}".format(
        len(lines), sum(l["scorecard_identical"] for l in lines), sum(l["status"] != "complete" for l in lines)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
