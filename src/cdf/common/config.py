"""Layered YAML configuration with deterministic hashing.

Configuration is resolved by deep-merging, in order:

1. ``configs/default.yaml``      -- pipeline-wide defaults
2. ``configs/sensors/<profile>.yaml`` -- the selected radar profile
3. ``configs/scenarios/<id>.yaml``    -- the scenario definition
4. explicit overrides passed on the command line

The fully merged mapping is hashed (:func:`config_hash`) so each run can be
tied back to the exact parameter set that produced it.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Union

import yaml


__all__ = [
    "Config",
    "load_yaml",
    "deep_merge",
    "config_hash",
    "repo_root",
    "configs_dir",
    "load_run_config",
    "parse_override",
]


def repo_root() -> Path:
    """Repository root, derived from this file's location."""
    return Path(__file__).resolve().parents[3]


def configs_dir() -> Path:
    """The ``configs/`` directory of the repository."""
    return repo_root() / "configs"


# ---------------------------------------------------------------------------
# Merging / loading
# ---------------------------------------------------------------------------


def load_yaml(path: Union[str, Path]) -> Dict[str, Any]:
    """Load a YAML mapping, returning ``{}`` for an empty document."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError("configuration file not found: {0}".format(p))
    with open(str(p), "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError("configuration root must be a mapping: {0}".format(p))
    return data


def deep_merge(base: Mapping[str, Any], override: Mapping[str, Any]) -> Dict[str, Any]:
    """Recursively merge ``override`` into ``base`` without mutating either.

    Mappings merge key-wise; every other type (including lists) is replaced
    wholesale, which keeps list-valued settings such as participant definitions
    predictable.
    """
    out: Dict[str, Any] = copy.deepcopy(dict(base))
    for key, value in override.items():
        if key in out and isinstance(out[key], dict) and isinstance(value, Mapping):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


def config_hash(config: Mapping[str, Any]) -> str:
    """Deterministic 16-hex-character digest of a resolved configuration."""
    payload = json.dumps(_normalise(config), sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def _normalise(obj: Any) -> Any:
    """Round floats so that insignificant float noise cannot change the hash."""
    if isinstance(obj, Mapping):
        return {str(k): _normalise(v) for k, v in sorted(obj.items())}
    if isinstance(obj, (list, tuple)):
        return [_normalise(v) for v in obj]
    if isinstance(obj, float):
        return round(obj, 9)
    return obj


def parse_override(text: str) -> Dict[str, Any]:
    """Parse a ``dotted.key=value`` override into a nested mapping.

    The value is parsed as YAML, so ``a.b=3``, ``a.b=true`` and ``a.b=[1,2]`` all
    behave as expected.
    """
    if "=" not in text:
        raise ValueError("override must look like key.path=value, got {0!r}".format(text))
    key, _, raw = text.partition("=")
    value = yaml.safe_load(raw)
    node: Dict[str, Any] = {}
    cur = node
    parts = [p for p in key.strip().split(".") if p]
    if not parts:
        raise ValueError("override key is empty in {0!r}".format(text))
    for part in parts[:-1]:
        cur[part] = {}
        cur = cur[part]
    cur[parts[-1]] = value
    return node


# ---------------------------------------------------------------------------
# Config object
# ---------------------------------------------------------------------------


class Config:
    """Read-only view over a resolved configuration mapping.

    Supports dotted lookups with defaults, which keeps call sites readable::

        cfg.get("simulation.fixed_delta_seconds", 0.05)
        cfg.require("sensors.profile")
    """

    __slots__ = ("_data", "_hash", "_sources")

    def __init__(self, data: Mapping[str, Any], sources: Optional[Sequence[str]] = None) -> None:
        self._data: Dict[str, Any] = copy.deepcopy(dict(data))
        self._hash: str = config_hash(self._data)
        self._sources: List[str] = list(sources or [])

    # -- access -----------------------------------------------------------

    @property
    def data(self) -> Dict[str, Any]:
        """A deep copy of the underlying mapping."""
        return copy.deepcopy(self._data)

    @property
    def hash(self) -> str:
        """Deterministic hash of the resolved configuration."""
        return self._hash

    @property
    def sources(self) -> List[str]:
        """The files and overrides this configuration was assembled from."""
        return list(self._sources)

    def get(self, dotted: str, default: Any = None) -> Any:
        """Look up ``dotted`` (e.g. ``"radar.range_m"``), returning ``default``."""
        node: Any = self._data
        for part in dotted.split("."):
            if not isinstance(node, Mapping) or part not in node:
                return default
            node = node[part]
        return copy.deepcopy(node)

    def require(self, dotted: str) -> Any:
        """Like :meth:`get` but raises when the key is absent.

        Used for values that have no sensible default: a missing one is a
        configuration bug and must fail loudly rather than silently degrade.
        """
        sentinel = object()
        value = self.get(dotted, sentinel)
        if value is sentinel:
            raise KeyError(
                "required configuration key {0!r} is missing (sources: {1})".format(
                    dotted, ", ".join(self._sources) or "<inline>"
                )
            )
        return value

    def section(self, dotted: str) -> "Config":
        """A :class:`Config` view of a sub-mapping (empty when absent)."""
        value = self.get(dotted, {})
        if not isinstance(value, Mapping):
            raise TypeError("configuration section {0!r} is not a mapping".format(dotted))
        return Config(value, self._sources)

    def with_overrides(self, overrides: Mapping[str, Any]) -> "Config":
        """A new :class:`Config` with ``overrides`` deep-merged in."""
        return Config(deep_merge(self._data, overrides), self._sources + ["<override>"])

    def __contains__(self, dotted: str) -> bool:
        sentinel = object()
        return self.get(dotted, sentinel) is not sentinel

    def __repr__(self) -> str:
        return "Config(hash={0}, keys={1})".format(self._hash, sorted(self._data.keys()))


# ---------------------------------------------------------------------------
# High-level loader
# ---------------------------------------------------------------------------


def load_run_config(
    scenario_id: Optional[str] = None,
    sensor_profile: Optional[str] = None,
    overrides: Optional[Iterable[str]] = None,
    config_root: Optional[Union[str, Path]] = None,
) -> Config:
    """Resolve the configuration for one run.

    Parameters
    ----------
    scenario_id:
        e.g. ``"S01"``. The scenario file is located case-insensitively by its
        ``sXX_`` filename prefix, so callers need not know the full filename.
    sensor_profile:
        Radar profile name under ``configs/sensors/``. When omitted the value of
        ``sensors.profile`` from the merged configuration is used.
    overrides:
        ``dotted.key=value`` strings applied last.
    """
    root = Path(config_root) if config_root is not None else configs_dir()
    sources: List[str] = []

    default_path = root / "default.yaml"
    merged = load_yaml(default_path)
    sources.append(str(default_path))

    scenario_data: Dict[str, Any] = {}
    if scenario_id:
        spath = find_scenario_file(scenario_id, root)
        scenario_data = load_yaml(spath)
        sources.append(str(spath))

    # The scenario may pin its own sensor profile; an explicit argument wins.
    profile = (
        sensor_profile
        or scenario_data.get("sensors", {}).get("profile")
        or merged.get("sensors", {}).get("profile")
        or "radar_baseline"
    )
    spath_sensor = root / "sensors" / "{0}.yaml".format(profile)
    if spath_sensor.exists():
        merged = deep_merge(merged, {"radar": load_yaml(spath_sensor).get("radar", {})})
        merged = deep_merge(merged, {"sensors": {"profile": profile}})
        sources.append(str(spath_sensor))
    else:
        raise FileNotFoundError("unknown sensor profile {0!r} ({1})".format(profile, spath_sensor))

    if scenario_data:
        merged = deep_merge(merged, scenario_data)

    for item in overrides or []:
        merged = deep_merge(merged, parse_override(item))
        sources.append("override:{0}".format(item))

    return Config(merged, sources)


def find_scenario_file(scenario_id: str, config_root: Optional[Union[str, Path]] = None) -> Path:
    """Locate a scenario YAML from an id such as ``"S01"``, ``"s1"`` or ``"S01_rear_end"``."""
    root = Path(config_root) if config_root is not None else configs_dir()
    sdir = root / "scenarios"
    token = scenario_id.strip().lower()
    if token.startswith("s") and token[1:].isdigit():
        token = "s{0:02d}".format(int(token[1:]))

    candidates = sorted(sdir.glob("*.yaml"))
    for path in candidates:
        name = path.stem.lower()
        if name == token or name.startswith(token + "_"):
            return path
    raise FileNotFoundError(
        "no scenario config matching {0!r} in {1} (available: {2})".format(
            scenario_id, sdir, ", ".join(p.stem for p in candidates)
        )
    )


def available_scenarios(config_root: Optional[Union[str, Path]] = None) -> List[str]:
    """Sorted scenario ids discovered under ``configs/scenarios/``."""
    root = Path(config_root) if config_root is not None else configs_dir()
    out: List[str] = []
    for path in sorted((root / "scenarios").glob("*.yaml")):
        stem = path.stem
        out.append(stem.split("_")[0].upper())
    return out
