#!/usr/bin/env python3
"""Effective association gates of the uncertainty-normalised tracker, from the model only.

    python scripts/uncertainty_tables.py [--out results/final_hardening/uncertainty_tables.md]

No recording and no ground truth: a target is simulated noise-free at a given range, geometry and speed, and the
tracker's own Kalman filter (``tracking.kf_predict_speed`` / ``kf_update`` with the measurement model of
``tracking._measurement_model``) runs on it for 2 s of 20 Hz sweeps.  Reported, for the steady-state track:

* position: the radar's polar 1-sigma (along / across the line of sight), the track point's innovation
  1-sigma (along / across) and the 99 % chi-square gate semi-axes, for the track's own point and for a
  single return (adds 2 x the box spread: a return and the track point are two points of one 4.6 x 1.9 m body);
* the same after 0.5 s without a measurement (prediction growth);
* Doppler: the radial residual sigma and the 99 % gate half-width along the line of sight.

"front": the target moves along the line of sight (a car ahead); "crossing": it moves across it.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.cdf.reconstruction.config import TrackingConfig  # noqa: E402
from src.cdf.reconstruction.tracking import (TrackMeasurement, _measurement_model, body_covariance,  # noqa: E402
                                             chi2_quantile, kf_predict_speed, kf_update, polar_covariances)

RANGES = (5, 10, 20, 40, 60, 80)
SPEEDS = {"low": 2.0, "medium": 10.0, "high": 25.0}


def steady_track(cfg: TrackingConfig, rng: float, geometry: str, speed: float, n_returns: int = 8):
    """Filter state after 2 s of noise-free sweeps; returns (x, P, origin, line of sight)."""
    origin = np.zeros(2)
    los = np.array([1.0, 0.0])
    velocity = speed * (los if geometry == "front" else np.array([0.0, 1.0]))
    dt = 0.05
    x = P = None
    for k in range(41):
        t = k * dt
        # At range rng at the end; a front target approaches along the line of sight (never through the radar).
        centre = np.array([rng, 0.0]) + (velocity if geometry == "crossing" else -velocity) * (t - 2.0)
        points = centre[None, :] + np.column_stack([np.zeros(n_returns), np.linspace(-0.8, 0.8, n_returns)])
        line = centre / np.linalg.norm(centre)
        m = TrackMeasurement(t_local=t, xy=centre.copy(), dopplers=[(line, float(line @ velocity))],
                             n_returns=n_returns, points=points, origins=np.tile(origin, (n_returns, 1)))
        if x is None:
            x = np.array([centre[0], centre[1], line @ velocity * line[0], line @ velocity * line[1]])
            P = np.diag([cfg.measurement_std_m ** 2] * 2 + [10.0 ** 2] * 2)
            continue
        x, P = kf_predict_speed(x, P, dt, cfg.acceleration_std_mps2, cfg.yaw_rate_std_rps)
        H, z, R = _measurement_model(m, cfg)
        x, P = kf_update(x, P, z, H, R)
    return x, P, origin, los


def axes(cov: np.ndarray, los: np.ndarray):
    """1-sigma along and across the line of sight."""
    across = np.array([-los[1], los[0]])
    return math.sqrt(los @ cov @ los), math.sqrt(across @ cov @ across)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=ROOT / "results" / "final_hardening" / "uncertainty_tables.md")
    args = parser.parse_args()
    cfg = TrackingConfig()
    k2, k1 = math.sqrt(chi2_quantile(cfg.gate_probability, 2)), math.sqrt(chi2_quantile(cfg.gate_probability, 1))
    lines = ["# Effective gates of the uncertainty-normalised tracker (model only, no ground truth)", "",
             "`scripts/uncertainty_tables.py`.  Radar: range sigma {0} m, azimuth sigma {1} deg; Doppler sigma {2} m/s; "
             "process noise {3} m/s^2 along the track, plus (v x {4} rad/s)^2 across it; 99 % gates "
             "(2-D: {5:.2f} sigma, 1-D: {6:.2f} sigma).  Steady state after 2 s of 20 Hz sweeps with 8 returns "
             "on a 1.6 m face; target speed 10 m/s for the position table.  Values in metres (position) and m/s "
             "(Doppler); along / across = along / across the line of sight.".format(
                 cfg.radar_range_std_m, cfg.radar_azimuth_std_deg, cfg.radial_speed_std_mps, cfg.acceleration_std_mps2,
                 cfg.yaw_rate_std_rps, k2, k1), "",
             "## Position", "",
             "| geometry | range [m] | radar 1-sigma along / across | track point: innovation 1-sigma along / across | "
             "track point: 99 % gate along / across | single return: 99 % gate along / across | after 0.5 s without "
             "data: track point gate along / across |",
             "|---|--:|---|---|---|---|---|"]
    for geometry in ("front", "crossing"):
        for rng in RANGES:
            x, P, origin, los = steady_track(cfg, rng, geometry, 10.0)
            polar = polar_covariances(x[None, :2], origin[None, :], cfg)[0]
            m = TrackMeasurement(t_local=0.0, xy=x[:2].copy(), dopplers=[], n_returns=8,
                                 points=x[:2][None, :] + np.column_stack([np.zeros(8), np.linspace(-0.8, 0.8, 8)]),
                                 origins=np.zeros((8, 2)))
            R = _measurement_model(m, cfg)[2][:2, :2]
            S = P[:2, :2] + R
            single = P[:2, :2] + 2.0 * body_covariance(x, cfg) + polar  # as covariance_gate
            xg, Pg = x, P
            for _ in range(10):
                xg, Pg = kf_predict_speed(xg, Pg, 0.05, cfg.acceleration_std_mps2, cfg.yaw_rate_std_rps)
            gap = Pg[:2, :2] + R
            f = lambda pair, scale=1.0: "{0:.2f} / {1:.2f}".format(pair[0] * scale, pair[1] * scale)
            lines.append("| {0} | {1} | {2} | {3} | {4} | {5} | {6} |".format(
                geometry, rng, f(axes(polar, los)), f(axes(S, los)), f(axes(S, los), k2), f(axes(single, los), k2),
                f(axes(gap, los), k2)))
    lines += ["", "## Doppler (radial residual along the return's line of sight)", "",
              "| geometry | relative speed | radial speed measured | track velocity 1-sigma along LOS | residual 1-sigma | "
              "99 % gate half-width | tangential velocity 1-sigma (not tested by Doppler) |",
              "|---|---|--:|--:|--:|--:|--:|"]
    for geometry in ("front", "crossing"):
        for label, speed in SPEEDS.items():
            x, P, origin, los = steady_track(cfg, 20.0, geometry, speed)
            pv_along = math.sqrt(los @ P[2:, 2:] @ los)
            across = np.array([-los[1], los[0]])
            sigma = math.sqrt(los @ P[2:, 2:] @ los + cfg.radial_speed_std_mps ** 2)
            radial = speed if geometry == "front" else 0.0
            lines.append("| {0} | {1} ({2:.0f} m/s) | {3:.1f} | {4:.2f} | {5:.2f} | {6:.2f} | {7:.2f} |".format(
                geometry, label, speed, radial, pv_along, sigma, k1 * sigma, math.sqrt(across @ P[2:, 2:] @ across)))
    lines.append("")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
