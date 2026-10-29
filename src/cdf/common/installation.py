"""Where the simulator is installed (file system only: nothing is imported from it).

Shared by the simulation client and by the reconstruction, which reads the public OpenDRIVE map files of the
installation (``reconstruction.road``).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional, Sequence

_DEFAULT_ROOT_CANDIDATES: Sequence[str] = (
    r"C:\Users\andrea.bedei3\Desktop\Carla9_15\WindowsNoEditor",
    r"C:\CARLA_0.9.15\WindowsNoEditor",
    r"C:\carla\WindowsNoEditor",
    "/opt/carla-simulator",
    str(Path.home() / "carla"),
)


def find_carla_root(configured: Optional[str] = None) -> Optional[Path]:
    """Locate a packaged CARLA installation.

    Resolution order: the explicit argument, ``$CARLA_ROOT``, then a short list
    of conventional locations. Returns ``None`` when nothing plausible is found,
    leaving the caller to decide whether that is fatal.
    """
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
    """The simulator executable inside ``root``, if present."""
    for name in ("CarlaUE4.exe", "CarlaUE4.sh"):
        exe = root / name
        if exe.exists():
            return exe
    return None


# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------


# The project's private CARLA server (configs/default.yaml simulation.port); port 2000 is left to other users.
