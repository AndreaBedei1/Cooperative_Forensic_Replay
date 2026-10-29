from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional, Sequence

_DEFAULT_ROOT_CANDIDATES: Sequence[str] = (
    r"C:\CARLA_0.9.15\WindowsNoEditor",
    r"C:\carla\WindowsNoEditor",
    "/opt/carla-simulator",
    str(Path.home() / "carla"),
)


def find_carla_root(configured: Optional[str] = None) -> Optional[Path]:
    candidates: List[str] = []
    if configured:
        candidates.append(configured)
    env = os.environ.get("CARLA_ROOT")
    if env:
        candidates.append(env)
    candidates.extend(_DEFAULT_ROOT_CANDIDATES)

    for cand in candidates:
        root = Path(cand)
        if not root.exists():
            continue
        if _server_executable(root) is not None:
            return root
    return None


def _server_executable(root: Path) -> Optional[Path]:
    for name in ("CarlaUE4.exe", "CarlaUE4.sh"):
        exe = root / name
        if exe.exists():
            return exe
    return None
