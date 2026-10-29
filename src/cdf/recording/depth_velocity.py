"""Transparent temporal association for compact depth observations.

The estimator deliberately has no knowledge of actors, world state, radar, or
semantic labels.  It matches only adjacent compact geometric observations and
derives the sensor-relative closing speed, (previous - current range) / dt:
positive while the range shrinks, the opposite sign of a range rate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

import numpy as np


ALGORITHM_VERSION = "temporal_geometric_association_v1"


@dataclass(frozen=True)
class DepthRadialVelocityConfig:
    enabled: bool = True
    max_dt_s: float = 0.20
    max_azimuth_difference_deg: float = 6.0
    max_altitude_difference_deg: float = 4.0
    max_abs_radial_velocity_mps: float = 60.0
    range_gate_margin_m: float = 0.50
    require_mutual_match: bool = True
    max_velocity_jump_mps: Optional[float] = 20.0

    @property
    def max_azimuth_difference_rad(self) -> float:
        return math.radians(self.max_azimuth_difference_deg)

    @property
    def max_altitude_difference_rad(self) -> float:
        return math.radians(self.max_altitude_difference_deg)

    def as_metadata(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "algorithm_version": ALGORITHM_VERSION,
            "max_dt_s": self.max_dt_s,
            "max_azimuth_difference_deg": self.max_azimuth_difference_deg,
            "max_altitude_difference_deg": self.max_altitude_difference_deg,
            "max_abs_radial_velocity_mps": self.max_abs_radial_velocity_mps,
            "range_gate_margin_m": self.range_gate_margin_m,
            "mutual_match": self.require_mutual_match,
            "max_velocity_jump_mps": self.max_velocity_jump_mps,
        }


def depth_radial_velocity_config_from_mapping(mapping: Mapping[str, Any]) -> DepthRadialVelocityConfig:
    """Build config from YAML values without allowing malformed gates."""
    data = dict(mapping or {})
    jump = data.get("max_velocity_jump_mps", 20.0)
    return DepthRadialVelocityConfig(
        enabled=bool(data.get("enabled", True)),
        max_dt_s=float(data.get("max_dt_s", 0.20)),
        max_azimuth_difference_deg=float(data.get("max_azimuth_difference_deg", 6.0)),
        max_altitude_difference_deg=float(data.get("max_altitude_difference_deg", 4.0)),
        max_abs_radial_velocity_mps=float(data.get("max_abs_radial_velocity_mps", 60.0)),
        range_gate_margin_m=float(data.get("range_gate_margin_m", 0.50)),
        require_mutual_match=bool(data.get("require_mutual_match", True)),
        max_velocity_jump_mps=None if jump is None else float(jump),
    )


@dataclass
class DepthAssociationStats:
    total_detections: int = 0
    estimated_detections: int = 0
    first_frame: int = 0
    dt_too_large: int = 0
    non_increasing_timestamp: int = 0
    no_angular_candidate: int = 0
    range_gate_failure: int = 0
    non_mutual_association: int = 0
    velocity_gate_failure: int = 0
    invalid_range: int = 0

    def as_dict(self) -> Dict[str, Any]:
        result = {key: int(value) for key, value in self.__dict__.items()}
        result["coverage_percentage"] = (
            100.0 * self.estimated_detections / self.total_detections
            if self.total_detections else 0.0
        )
        return result


@dataclass
class _PreviousFrame:
    timestamp: float
    detections: List[Dict[str, Any]]


class DepthRadialVelocityEstimator:
    """Associate one ordered depth frame at a time and attach radial rates."""

    def __init__(self, config: Optional[Any] = None) -> None:
        if config is None:
            config = DepthRadialVelocityConfig()
        elif isinstance(config, Mapping):
            config = depth_radial_velocity_config_from_mapping(config)
        if not isinstance(config, DepthRadialVelocityConfig):
            raise TypeError("config must be DepthRadialVelocityConfig or a mapping")
        self.config = config
        self.stats = DepthAssociationStats()
        self._previous: Optional[_PreviousFrame] = None

    @staticmethod
    def _value(detection: Mapping[str, Any], *names: str) -> float:
        for name in names:
            if name in detection:
                try:
                    return float(detection[name])
                except (TypeError, ValueError):
                    return float("nan")
        return float("nan")

    @classmethod
    def _geometry(cls, detection: Mapping[str, Any]) -> tuple:
        return (
            cls._value(detection, "depth", "depth_m"),
            cls._value(detection, "azimuth", "azimuth_rad"),
            cls._value(detection, "altitude", "altitude_rad"),
        )

    @staticmethod
    def _set_velocity(detection: Dict[str, Any], velocity: float) -> None:
        # Keep the acquisition dict schema used by the compact writer.
        detection["radial_velocity"] = float(velocity) if math.isfinite(velocity) else None
        if "radial_velocity_mps" in detection:
            detection["radial_velocity_mps"] = float(velocity) if math.isfinite(velocity) else None

    @classmethod
    def _copy_detection(cls, detection: Any) -> Dict[str, Any]:
        if isinstance(detection, Mapping):
            return dict(detection)
        row = np.asarray(detection, dtype=np.float64)
        if row.shape != (4,):
            raise ValueError("depth detection must be a mapping or a numeric row of shape (4,)")
        return {
            "depth": float(row[0]), "azimuth": float(row[1]),
            "altitude": float(row[2]), "radial_velocity": float(row[3]),
        }

    def _candidate_costs(self, previous: Sequence[Mapping[str, Any]], current: Sequence[Mapping[str, Any]],
                         dt: float) -> tuple:
        cfg = self.config
        az_gate = cfg.max_azimuth_difference_rad
        al_gate = cfg.max_altitude_difference_rad
        range_gate = cfg.max_abs_radial_velocity_mps * dt + cfg.range_gate_margin_m
        costs: List[List[float]] = [[math.inf] * len(current) for _ in previous]
        valid_by_previous: List[List[int]] = [[] for _ in previous]
        valid_by_current: List[List[int]] = [[] for _ in current]
        for pi, prev in enumerate(previous):
            pr, paz, pal = self._geometry(prev)
            if not (math.isfinite(pr) and math.isfinite(paz) and math.isfinite(pal)):
                continue
            for ci, cur in enumerate(current):
                cr, caz, cal = self._geometry(cur)
                if not (math.isfinite(cr) and math.isfinite(caz) and math.isfinite(cal)):
                    continue
                daz, dal, dr = abs(paz - caz), abs(pal - cal), abs(pr - cr)
                if daz > az_gate or dal > al_gate:
                    continue
                if dr > range_gate:
                    continue
                cost = daz / az_gate + dal / al_gate + dr / max(range_gate, 1e-12)
                costs[pi][ci] = cost
                valid_by_previous[pi].append(ci)
                valid_by_current[ci].append(pi)
        return costs, valid_by_previous, valid_by_current

    @staticmethod
    def _unique_best(values: Sequence[float], candidates: Sequence[int]) -> Optional[int]:
        if not candidates:
            return None
        ordered = sorted(candidates, key=lambda i: (values[i], i))
        if len(ordered) > 1 and math.isclose(values[ordered[0]], values[ordered[1]], rel_tol=0.0, abs_tol=1e-12):
            return None
        return ordered[0]

    def process(self, frame: int, timestamp: float, detections: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
        """Return a new detection list; callers must provide timestamp order."""
        current = [self._copy_detection(detection) for detection in detections]
        for detection in current:
            self._set_velocity(detection, float("nan"))
        self.stats.total_detections += len(current)
        current_timestamp = float(timestamp)

        if not self.config.enabled:
            self._previous = _PreviousFrame(current_timestamp, current)
            return current
        if self._previous is None:
            self.stats.first_frame += len(current)
            self._previous = _PreviousFrame(current_timestamp, current)
            return current
        dt = current_timestamp - self._previous.timestamp
        if dt <= 0.0:
            # An out-of-order callback must not corrupt temporal state.
            self.stats.non_increasing_timestamp += len(current)
            return current
        if dt > self.config.max_dt_s:
            self.stats.dt_too_large += len(current)
            self._previous = _PreviousFrame(current_timestamp, current)
            return current

        previous = self._previous.detections
        costs, valid_by_previous, valid_by_current = self._candidate_costs(previous, current, dt)
        previous_choice = [self._unique_best(costs[pi], candidates)
                           for pi, candidates in enumerate(valid_by_previous)]
        current_choice = []
        for ci, candidates in enumerate(valid_by_current):
            values = [costs[pi][ci] for pi in range(len(previous))]
            current_choice.append(self._unique_best(values, candidates))

        for ci, candidates in enumerate(valid_by_current):
            if not candidates:
                # Distinguish no angular/range candidate for aggregate diagnostics.
                cr, caz, cal = self._geometry(current[ci])
                if not (math.isfinite(cr) and math.isfinite(caz) and math.isfinite(cal)):
                    self.stats.invalid_range += 1
                else:
                    has_angular = False
                    has_range = False
                    for prev_detection in previous:
                        pr, paz, pal = self._geometry(prev_detection)
                        if not (math.isfinite(pr) and math.isfinite(paz) and math.isfinite(pal)):
                            continue
                        if abs(paz - caz) <= self.config.max_azimuth_difference_rad and abs(pal - cal) <= self.config.max_altitude_difference_rad:
                            has_angular = True
                            if abs(pr - cr) <= self.config.max_abs_radial_velocity_mps * dt + self.config.range_gate_margin_m:
                                has_range = True
                    if has_angular and not has_range:
                        self.stats.range_gate_failure += 1
                    else:
                        self.stats.no_angular_candidate += 1
                continue
            pi = current_choice[ci]
            if pi is None or (self.config.require_mutual_match and previous_choice[pi] != ci):
                self.stats.non_mutual_association += 1
                continue
            pr, _, _ = self._geometry(previous[pi])
            cr, _, _ = self._geometry(current[ci])
            velocity = (pr - cr) / dt
            if abs(velocity) > self.config.max_abs_radial_velocity_mps:
                self.stats.velocity_gate_failure += 1
                continue
            previous_velocity = self._value(previous[pi], "radial_velocity", "radial_velocity_mps")
            if (self.config.max_velocity_jump_mps is not None and math.isfinite(previous_velocity)
                    and abs(velocity - previous_velocity) > self.config.max_velocity_jump_mps):
                self.stats.velocity_gate_failure += 1
                continue
            self._set_velocity(current[ci], velocity)
            self.stats.estimated_detections += 1

        self._previous = _PreviousFrame(current_timestamp, current)
        return current
