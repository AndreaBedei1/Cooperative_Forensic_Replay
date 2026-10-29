#!/usr/bin/env python3
"""Preliminary or frozen manifest for the active RTK/5G-transport GNSS protocol on 22 canonical runs.

    python scripts/campaign_manifest.py [--out results/robustness/rtk5g_current/manifest.json]
    campaign v3 (docs/CAMPAIGN_V3.md), from the worktree of the tag ``campaign-v3``:
    set CDF_CAMPAIGN_VERSION_TAG=campaign-v3
    python scripts/campaign_manifest.py --reconstruction-tag campaign-v3 --name "campaign v3" ^
        --families baseline,gnss,radar_v3,radar_asym,radar_gnss_v3,radar_asym_gnss ^
        --scope "Robustness campaign v3 on the 22 canonical runs S01..S19 (docs/CAMPAIGN_V3.md)" ^
        --launcher "scripts/campaign_v3.bat start|status|pause|resume, from the worktree of the tag" ^
        --results results/robustness/campaign_v3 --out results/robustness/campaign_v3/manifest.json

It records what a reproduction must match: the frozen reconstruction (commit of the tag
``pre-robustness-campaign``, configuration hash, and a hash of the reconstruction sources computed both at that
commit and now, which must be equal), the current protocol code hash, hashes of the driver and evaluation scripts,
raw-data hashes for the 22 canonical runs, active perturbation profiles, the experiment matrix, seed schedule, and
software versions.  A manifest generated before a clean, approved commit and protocol tag is marked preliminary.
The historical manifest at ``results/robustness_campaign_manifest.json`` is left intact.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]

FROZEN_TAG = "pre-robustness-campaign"
SCRIPTS = ["robustness.py", "campaign_controller.py", "campaign_report.py", "campaign_manifest.py", "stability_audit.py",
           "validate_canonical.py", "reconstruct_run.py"]
# The reconstruction under test: these sources and the configuration are those of the frozen tag.
RECONSTRUCTION_SOURCES = ("src/cdf/reconstruction", "src/cdf/common", "src/cdf/recording", "src/cdf/perception",
                          "configs/reconstruction.yaml")


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def tree_hash(paths: List[Path], root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.relative_to(root).as_posix().encode("utf-8") + b"\0")
        digest.update(path.read_bytes() + b"\0")
    return digest.hexdigest()


def raw_hash(run: Path) -> Dict[str, Any]:
    """SHA-256 over the raw recording (vehicles/, ground_truth/, metadata.json, incident_context.json)."""
    files = [p for p in run.rglob("*") if p.is_file() and p.relative_to(run).parts[0] in
             ("vehicles", "ground_truth", "metadata.json", "incident_context.json")]
    return {"files": len(files), "bytes": sum(p.stat().st_size for p in files), "sha256": tree_hash(files, run)}


def _git(*args: str) -> Optional[str]:
    out = subprocess.run(["git", *args], cwd=str(ROOT), capture_output=True)
    return out.stdout.decode("utf-8", "replace").strip() if out.returncode == 0 else None


def reconstruction_hash(commit: Optional[str] = None) -> str:
    """SHA-256 over the reconstruction sources (path and content, line endings normalised), from the working tree
    or from a commit's Git objects."""
    digest = hashlib.sha256()
    if commit is None:
        names = []
        for item in RECONSTRUCTION_SOURCES:
            path = ROOT / item
            names += [p.relative_to(ROOT).as_posix() for p in (path.rglob("*.py") if path.is_dir() else [path])]
        contents = {n: (ROOT / n).read_bytes() for n in names}
    else:
        listing = _git("ls-tree", "-r", "--name-only", commit, "--", *RECONSTRUCTION_SOURCES) or ""
        names = [n for n in listing.splitlines() if n.endswith(".py") or n.endswith(".yaml")]
        contents = {}
        for n in names:
            out = subprocess.run(["git", "show", commit + ":" + n], cwd=str(ROOT), capture_output=True)
            contents[n] = out.stdout
    for name in sorted(contents):
        digest.update(name.encode("utf-8") + b"\0")
        digest.update(contents[name].replace(b"\r\n", b"\n") + b"\0")
    return digest.hexdigest()


def _code_hash_at(commit: Optional[str]) -> Optional[str]:
    if commit is None:
        return None
    from cdf.evaluation.provenance import commit_code_hash
    return commit_code_hash(commit)


def versions() -> Dict[str, Any]:
    out: Dict[str, Any] = {"python": sys.version, "platform": platform.platform()}
    try:
        from importlib import metadata
        out["packages"] = {d.metadata["Name"]: d.version for d in sorted(metadata.distributions(),
                                                                        key=lambda d: d.metadata["Name"].lower())}
    except Exception as exc:  # pragma: no cover
        out["packages_error"] = repr(exc)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=ROOT / "results" / "robustness" / "rtk5g_current" / "manifest.json")
    parser.add_argument("--reconstruction-tag", default=FROZEN_TAG,
                        help="the tag whose reconstruction sources the campaign tests (default: " + FROZEN_TAG + ")")
    parser.add_argument("--name", default="RTK GNSS with correction transport via 5G: current robustness protocol")
    parser.add_argument("--families", default="", help="the families the campaign schedules (default: all)")
    parser.add_argument("--results", default="results/robustness/rtk5g_current")
    parser.add_argument("--scope", default="New GNSS perturbation protocol on the 22 manually reviewed canonical runs "
                                           "(S01..S19). This protocol is distinct from the preregistered 2026-10-15 "
                                           "study and does not replace its results.")
    parser.add_argument("--launcher", default="scripts/campaign_controller.py (scripts\\campaign.bat "
                                              "start|status|pause|resume)")
    args = parser.parse_args()
    from cdf.evaluation.provenance import code_hash, config_hash
    from cdf.reconstruction.config import load_config
    from cdf.robustness.perturb import GNSS_PROFILES, RADAR_PROFILES
    import robustness
    from validate_canonical import CANONICAL, canonical_runs
    reconstruction_tag = args.reconstruction_tag
    frozen = _git("rev-parse", reconstruction_tag + "^{commit}")
    head = _git("rev-parse", "HEAD")
    worktree_status = _git("status", "--porcelain", "--untracked-files=no") or ""
    version_tag = os.environ.get("CDF_CAMPAIGN_VERSION_TAG", "rtk5g-current")
    version_commit = _git("rev-parse", version_tag + "^{commit}")
    preliminary = bool(worktree_status or not version_commit or version_commit != head)
    recon_now, recon_frozen = reconstruction_hash(), reconstruction_hash(frozen) if frozen else None
    if recon_frozen is not None and recon_now != recon_frozen:
        raise SystemExit("the reconstruction sources differ from the frozen tag: not this campaign")
    runs = [Path(r) for r in canonical_runs()]
    cfg = load_config()
    scheduled = [f for f in args.families.split(",") if f] or list(robustness.FAMILIES)
    unknown = [f for f in scheduled if f not in robustness.FAMILIES]
    if unknown:
        raise SystemExit("unknown families: " + ", ".join(unknown))
    matrix = {}
    for family, (levels, stochastic) in robustness.FAMILIES.items():
        jobs3 = sum(len(robustness.jobs_for(ROOT / run, family, [0, 1, 2])) for run in runs)
        jobs8 = sum(len(robustness.jobs_for(ROOT / run, family, list(range(8)))) for run in runs)
        matrix[family] = {"levels": [{"label": label, "parameter": parameter} for label, parameter in levels],
                          "stochastic": stochastic, "jobs_initial": jobs3, "jobs_max": jobs8 if stochastic else jobs3,
                          "configuration": "ablation_mutual_refinement" if family == "gnss_refined" else "frozen"}
    manifest = {
        "name": args.name,
        "protocol": {"version_tag": version_tag, "version_tag_commit": version_commit,
                     "status": "PRELIMINARY" if preliminary else "FROZEN",
                     "preliminary": preliminary, "generated_at": datetime.now(timezone.utc).isoformat(),
                     "head_commit": head, "worktree_status": worktree_status},
        "scope": args.scope,
        "frozen_reconstruction": {"tag": reconstruction_tag, "commit": frozen,
                                  "reconstruction_sources": list(RECONSTRUCTION_SOURCES),
                                  "reconstruction_sources_sha256": recon_now,
                                  "reconstruction_sources_sha256_at_tag": recon_frozen,
                                  "reconstruction_config_sha256": config_hash(cfg.to_dict()),
                                  "code_sha256_at_tag": (
                                      "ac2cb70ad595af1cc12aeb7bd7c89c364baf861dec991599257f9bac4d76f5df"
                                      if reconstruction_tag == FROZEN_TAG else _code_hash_at(frozen))},
        "code_sha256": code_hash(),
        "reconstruction_config_sha256": config_hash(cfg.to_dict()),
        "reconstruction_config": cfg.to_dict(),
        "scripts_sha256": {name: file_hash(ROOT / "scripts" / name) for name in SCRIPTS},
        "sensor_configs_sha256": tree_hash(list((ROOT / "configs" / "sensors").glob("*.yaml")), ROOT),
        "canonical_manifest": {"set": "S01..S19, 22 runs", "variants": CANONICAL,
                               "runs": {(ROOT / run).resolve().relative_to(ROOT.resolve()).as_posix(): raw_hash(ROOT / run)
                                        for run in runs}},
        "robustness": {
            "launcher": args.launcher,
            "radar_profiles": {k: dataclasses.asdict(v) for k, v in RADAR_PROFILES.items()},
            "gnss_profiles": {k: dataclasses.asdict(v) for k, v in GNSS_PROFILES.items()},
            "profile_documentation": "docs/robustness_profiles.md",
            "matrix": matrix,
            "scheduled_families": scheduled,
            "conditions": sum(len(matrix[f]["levels"]) for f in scheduled),
            "jobs_initial_total": sum(matrix[f]["jobs_initial"] for f in scheduled),
            "jobs_max_total": sum(matrix[f]["jobs_max"] for f in scheduled),
            "seed_schedule": {"stochastic": "seeds 0, 1, 2 first; then 3, 4, ... up to 7 while the standard error over "
                                            "seeds of any pooled metric exceeds its tolerance (robustness.TOLERANCES), "
                                            "decided per (family, level)",
                              "tolerances": robustness.TOLERANCES, "deterministic": "seed 0 only",
                              "streams": "SHA-256 of (seed, sensor, profile, recorder, axis/radar): independent of "
                                         "family, worker and execution order, shared by all runs of a seed"},
            "max_attempts_per_job": 2,
        },
        "results": {"jobs": args.results.rstrip("/") + "/jobs.jsonl", "report": args.results.rstrip("/") + "/report/"},
        "software": versions(),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(manifest, indent=1, default=str) + "\n", encoding="utf-8")
    print("conditions", manifest["robustness"]["conditions"], "jobs initial", manifest["robustness"]["jobs_initial_total"],
          "max", manifest["robustness"]["jobs_max_total"], "| reconstruction unchanged since", reconstruction_tag,
          recon_now == recon_frozen, "| code", manifest["code_sha256"][:16])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
