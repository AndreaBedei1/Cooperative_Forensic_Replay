
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from functools import lru_cache
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence

ROOT = Path(__file__).resolve().parents[3]


def _git(*args: str) -> Optional[str]:
    try:
        out = subprocess.run(["git", *args], cwd=str(ROOT), capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def config_hash(config: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(config, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def code_hash() -> str:
    digest = hashlib.sha256()
    files = sorted(list((ROOT / "src" / "cdf").rglob("*.py")) + list((ROOT / "configs").glob("*.yaml")))
    for path in files:
        digest.update(path.relative_to(ROOT).as_posix().encode("utf-8") + b"\0")
        digest.update(path.read_bytes().replace(b"\r\n", b"\n") + b"\0")
    return digest.hexdigest()


@lru_cache(maxsize=None)
def commit_code_hash(commit: str) -> Optional[str]:
    listing = _git('ls-tree', '-r', '--name-only', commit, '--', 'src/cdf', 'configs')
    if listing is None:
        return None
    names = sorted(name for name in listing.splitlines()
                   if (name.startswith('src/cdf/') and name.endswith('.py'))
                   or (name.startswith('configs/') and name.count('/') == 1 and name.endswith('.yaml')))
    digest = hashlib.sha256()
    for name in names:
        proc = subprocess.run(['git', 'show', commit + ':' + name], cwd=str(ROOT), capture_output=True)
        if proc.returncode:
            return None
        digest.update(name.encode('utf-8') + b'\0')
        digest.update(proc.stdout.replace(b'\r\n', b'\n') + b'\0')
    return digest.hexdigest()


def verify_equivalence(record: Mapping[str, Any], commits: Sequence[str]) -> Dict[str, Any]:
    result = dict(record)
    value = result.get('code_sha256')
    result['analysis_code_sha256'] = value
    for commit in commits:
        full = _git('rev-parse', commit)
        if full and value is not None and commit_code_hash(full) == value:
            result['equivalent_clean_commit'] = full
            result['equivalence_verified'] = 'SHA-256 of Git path/content objects; src/cdf/**/*.py and configs/*.yaml'
            break
    return result


def provenance(config: Optional[Mapping[str, Any]] = None, runs: Sequence[str] = (),
               perturbation: Optional[str] = None, seed: Optional[int] = None,
               extra: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    status = _git("status", "--porcelain", "--untracked-files=no")
    record: Dict[str, Any] = {
        "git_commit": _git("rev-parse", "HEAD"),
        "git_dirty": None if status is None else bool(status),
        "code_sha256": code_hash(),
        "config_sha256": None if config is None else config_hash(config),
        "runs": list(runs),
        "perturbation_profile": perturbation,
        "seed": seed,
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "python": sys.version.split()[0],
    }
    freeze = os.environ.get('CDF_ANALYSIS_FREEZE_COMMIT')
    if freeze:
        if record['git_commit'] != freeze or record['git_dirty']:
            raise RuntimeError('frozen analysis requires the named commit and a clean execution tree')
        record['analysis_commit'] = freeze
        record['analysis_started_from_clean_tree'] = True
    record['analysis_code_sha256'] = record['code_sha256']
    if record['git_commit'] and commit_code_hash(record['git_commit']) == record['code_sha256']:
        record['equivalent_clean_commit'] = record['git_commit']
        record['final_analysis_commit'] = record['git_commit']
    if extra:
        record.update(extra)
    return record
