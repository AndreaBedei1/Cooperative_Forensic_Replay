#!/usr/bin/env python3
"""Source-agnostic depth/radar inspection and validation metrics.

This module is intentionally post-acquisition only: radar is never passed to
the depth estimator.  It is useful for the S01/S10 reports requested by the
acquisition task and for manually switching a consumer between sources.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
import sys
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cdf.recording.compact_observations import CompactObservations, closing_speed, load_observation_stream  # noqa: E402


# The depth camera looks forward: radar is compared through the front radar of the
# three body radars (vehicles/X/radar/front/).
RADAR_SENSOR = "front"


def _radar_sensor(vehicle_dir: Path) -> Optional[str]:
    return RADAR_SENSOR if (Path(vehicle_dir) / "radar" / RADAR_SENSOR).exists() else None


def source_switch_demo(vehicle_dir: Path, source: str = "radar") -> Dict[str, float]:
    """Run the same tiny consumer against either source selection."""
    stream = load_observation_stream(vehicle_dir, source=source,
                                     sensor_id=_radar_sensor(vehicle_dir) if source == "radar" else None)
    total = finite_velocity = 0
    for observation_frame in stream:
        detections = observation_frame["detections"]
        total += len(detections)
        if len(detections):
            finite_velocity += int(np.isfinite(detections[:, 3]).sum())
    return {
        "frames": float(len(stream.frames)),
        "detections": float(total),
        "finite_radial_velocity": float(finite_velocity),
    }


def _nearest_timestamp(stream: CompactObservations, timestamp: float, tolerance_s: float) -> Optional[int]:
    if not len(stream.timestamps):
        return None
    index = int(np.argmin(np.abs(stream.timestamps - timestamp)))
    return index if abs(float(stream.timestamps[index]) - timestamp) <= tolerance_s else None


def _deadband_sign(values: np.ndarray, deadband_mps: float) -> np.ndarray:
    return np.where(values > deadband_mps, 1, np.where(values < -deadband_mps, -1, 0))


def radar_depth_metrics(vehicle_dir: Path, timestamp_tolerance_s: float = 0.03,
                        azimuth_tolerance_deg: float = 4.0,
                        altitude_tolerance_deg: float = 4.0,
                        range_tolerance_m: float = 3.0,
                        sign_deadband_mps: float = 0.5) -> Dict[str, float]:
    """Compare compatible post-acquisition returns in the common FOV.

    Radar (range rate) and depth (closing speed) store opposite signs, so both
    are compared as closing speed: positive = approaching.
    """
    radar = load_observation_stream(vehicle_dir, source="radar", common_region=True,
                                    sensor_id=_radar_sensor(vehicle_dir))
    depth = load_observation_stream(vehicle_dir, source="depth", common_region=True)
    pairs: List[Tuple[float, float]] = []
    azimuth_tolerance = math.radians(azimuth_tolerance_deg)
    altitude_tolerance = math.radians(altitude_tolerance_deg)
    for depth_index, timestamp in enumerate(depth.timestamps):
        radar_index = _nearest_timestamp(radar, float(timestamp), timestamp_tolerance_s)
        if radar_index is None:
            continue
        radar_detections = radar.frame_detections(radar_index)
        if not len(radar_detections):
            continue
        for depth_detection in depth.frame_detections(depth_index):
            if not math.isfinite(float(depth_detection[3])):
                continue
            compatible = radar_detections[
                (np.abs(radar_detections[:, 1] - depth_detection[1]) <= azimuth_tolerance)
                & (np.abs(radar_detections[:, 2] - depth_detection[2]) <= altitude_tolerance)
                & (np.abs(radar_detections[:, 0] - depth_detection[0]) <= range_tolerance_m)
                & np.isfinite(radar_detections[:, 3])
            ]
            if len(compatible):
                radar_detection = compatible[int(np.argmin(np.abs(compatible[:, 0] - depth_detection[0])))]
                pairs.append((float(closing_speed(radar_detection[3], "radar")),
                              float(closing_speed(depth_detection[3], "depth"))))
    if not pairs:
        return {"matched_pairs": 0.0, "depth_finite_coverage_percentage": _coverage(depth)}
    values = np.asarray(pairs, dtype=np.float64)
    error = values[:, 1] - values[:, 0]
    return {
        "matched_pairs": float(len(values)),
        "depth_finite_coverage_percentage": _coverage(depth),
        "sign_agreement_percentage": float(100.0 * np.mean(_deadband_sign(values[:, 0], sign_deadband_mps) == _deadband_sign(values[:, 1], sign_deadband_mps))),
        "pearson_correlation": float(np.corrcoef(values[:, 0], values[:, 1])[0, 1]) if len(values) > 1 else 0.0,
        "mae_mps": float(np.mean(np.abs(error))),
        "median_absolute_error_mps": float(np.median(np.abs(error))),
        "rmse_mps": float(np.sqrt(np.mean(error * error))),
        "bias_mps": float(np.mean(error)),
        "median_radar_closing_speed_mps": float(np.median(values[:, 0])),
        "median_depth_closing_speed_mps": float(np.median(values[:, 1])),
    }


def _coverage(stream: CompactObservations) -> float:
    total = int(len(stream.detections))
    return float(100.0 * np.isfinite(stream.detections[:, 3]).sum() / total) if total else 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate compact radar/depth observations")
    parser.add_argument("vehicle_dir", type=Path)
    parser.add_argument("--source", choices=("radar", "depth"), default="depth")
    parser.add_argument("--metrics", action="store_true", help="also compute post-acquisition radar/depth metrics")
    parser.add_argument("--timestamp-tolerance-s", type=float, default=0.03)
    parser.add_argument("--azimuth-tolerance-deg", type=float, default=4.0)
    parser.add_argument("--altitude-tolerance-deg", type=float, default=4.0)
    parser.add_argument("--range-tolerance-m", type=float, default=3.0)
    parser.add_argument("--sign-deadband-mps", type=float, default=0.5)
    args = parser.parse_args()
    print({"source": args.source, **source_switch_demo(args.vehicle_dir, args.source)})
    if args.metrics:
        parameters = {"timestamp_tolerance_s": args.timestamp_tolerance_s,
                      "azimuth_tolerance_deg": args.azimuth_tolerance_deg,
                      "altitude_tolerance_deg": args.altitude_tolerance_deg,
                      "range_tolerance_m": args.range_tolerance_m,
                      "sign_deadband_mps": args.sign_deadband_mps}
        print({"parameters": parameters,
               "metrics": radar_depth_metrics(args.vehicle_dir, **parameters)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
