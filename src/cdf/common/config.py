
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
    return Path(__file__).resolve().parents[3]


def configs_dir() -> Path:
    return repo_root() / "configs"




def load_yaml(path: Union[str, Path]) -> Dict[str, Any]:
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
    out: Dict[str, Any] = copy.deepcopy(dict(base))
    for key, value in override.items():
        if key in out and isinstance(out[key], dict) and isinstance(value, Mapping):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


def config_hash(config: Mapping[str, Any]) -> str:
    payload = json.dumps(_normalise(config), sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def _normalise(obj: Any) -> Any:
    if isinstance(obj, Mapping):
        return {str(k): _normalise(v) for k, v in sorted(obj.items())}
    if isinstance(obj, (list, tuple)):
        return [_normalise(v) for v in obj]
    if isinstance(obj, float):
        return round(obj, 9)
    return obj


def parse_override(text: str) -> Dict[str, Any]:
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




class Config:

    __slots__ = ("_data", "_hash", "_sources")

    def __init__(self, data: Mapping[str, Any], sources: Optional[Sequence[str]] = None) -> None:
        self._data: Dict[str, Any] = copy.deepcopy(dict(data))
        self._hash: str = config_hash(self._data)
        self._sources: List[str] = list(sources or [])


    @property
    def data(self) -> Dict[str, Any]:
        return copy.deepcopy(self._data)

    @property
    def hash(self) -> str:
        return self._hash

    @property
    def sources(self) -> List[str]:
        return list(self._sources)

    def get(self, dotted: str, default: Any = None) -> Any:
        node: Any = self._data
        for part in dotted.split("."):
            if not isinstance(node, Mapping) or part not in node:
                return default
            node = node[part]
        return copy.deepcopy(node)

    def require(self, dotted: str) -> Any:
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
        value = self.get(dotted, {})
        if not isinstance(value, Mapping):
            raise TypeError("configuration section {0!r} is not a mapping".format(dotted))
        return Config(value, self._sources)

    def with_overrides(self, overrides: Mapping[str, Any]) -> "Config":
        return Config(deep_merge(self._data, overrides), self._sources + ["<override>"])

    def __contains__(self, dotted: str) -> bool:
        sentinel = object()
        return self.get(dotted, sentinel) is not sentinel

    def __repr__(self) -> str:
        return "Config(hash={0}, keys={1})".format(self._hash, sorted(self._data.keys()))




def load_run_config(
    scenario_id: Optional[str] = None,
    sensor_profile: Optional[str] = None,
    overrides: Optional[Iterable[str]] = None,
    config_root: Optional[Union[str, Path]] = None,
) -> Config:
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
    root = Path(config_root) if config_root is not None else configs_dir()
    out: List[str] = []
    for path in sorted((root / "scenarios").glob("*.yaml")):
        stem = path.stem
        out.append(stem.split("_")[0].upper())
    return out
