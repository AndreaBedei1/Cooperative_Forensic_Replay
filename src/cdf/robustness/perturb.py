from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np

from ..reconstruction.common_frame import RecordedPoseSource
from ..reconstruction.tracking import RadarMount


def stream_seed(seed: int, *labels: Any) -> int:
    """A 64-bit seed for one random stream (run seed, recorder, sensor, quantity), independent of the order
    in which the streams are drawn."""
    digest = hashlib.sha256(":".join([str(seed)] + [str(label) for label in labels]).encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


# --------------------------------------------------------------------------
# Radar
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class RadarProfile:
    name: str
    sigma_range_m: float = 0.0
    sigma_azimuth_deg: float = 0.0
    sigma_elevation_deg: float = 0.0
    sigma_velocity_mps: float = 0.0
    p_drop: float = 0.0
    clutter_per_sweep: float = 0.0  # Poisson mean of false returns per sweep of one radar


# Accuracies taken as 1-sigma (vendors do not say: an engineering assumption, conservative if they are 2-sigma).
RADAR_PROFILES: Dict[str, RadarProfile] = {
    "ideal": RadarProfile("ideal"),
    # Best stated accuracies (Continental ARS 408-21 near range, Bosch premium, AUMOVIO ARS540); residual losses.
    "low": RadarProfile("low", 0.10, 0.1, 0.1, 0.03, 0.05, 1.0),
    # Range at the median stated accuracy of production radars, azimuth and radial velocity above their medians
    # (off-boresight crash geometry); the values used to perturb CARLA radar in DC-Loc (ICRA 2022);
    # p_drop = 1 - 0.8 (Scheel & Dietmayer, T-ITS 2019); clutter from the Radar Ghost Dataset (IROS 2021).
    # Sources and the engineering assumptions per value: docs/robustness_profiles.md.
    "nominal": RadarProfile("nominal", 0.25, 0.5, 0.5, 0.10, 0.20, 3.0),
    # Worst stated accuracies (long-range modes, field-of-view edges); clutter lambda_C = 30 of T-ITS 2019.
    "high": RadarProfile("high", 0.50, 2.0, 2.0, 0.20, 0.40, 30.0),
    # Campaign v3 levels (docs/robustness_profiles.md, "Radar levels v3"): each value labelled there as
    # specification, derived from a measurement, or engineering assumption.
    # severe: measurement quality at the field-of-view edge / long range (azimuth 2 deg: RadarScenes edge
    # specification), twice the nominal misses, the measured urban ghost rate kept.
    "severe": RadarProfile("severe", 0.50, 2.0, 2.0, 0.20, 0.40, 3.0),
    # extreme: the severe accuracies with dense clutter lambda = 30 per sweep, a tracker design value of T-ITS
    # 2019, not a measured rate: a stress test beyond typical automotive radar (equal to the historical "high").
    "extreme": RadarProfile("extreme", 0.50, 2.0, 2.0, 0.20, 0.40, 30.0),
}


def perturb_sweeps(frames: np.ndarray, timestamps: np.ndarray, offsets: np.ndarray, detections: np.ndarray,
                   metadata: Mapping[str, Any], profile: RadarProfile, rng: np.random.Generator,
                   speed_at: Any, keep: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """One radar's compact observations perturbed (columns: depth, azimuth, altitude, radial velocity).

    ``keep`` selects the sweeps that survive (downsampling, outages); ``speed_at(timestamp)`` is the
    vehicle's own recorded speed (for the static-world Doppler of clutter)."""
    keep = np.arange(len(frames)) if keep is None else np.asarray(keep, dtype=int)
    hfov = math.radians(float(metadata.get("horizontal_fov_deg", 30.0)))
    vfov = math.radians(float(metadata.get("vertical_fov_deg", 30.0)))
    reach = float(metadata.get("range_m", 100.0))
    mount = RadarMount.from_metadata(metadata)
    out, starts = [], [0]
    for index in keep:
        sweep = detections[offsets[index]:offsets[index + 1]].astype(np.float64)
        if profile.p_drop > 0.0 and len(sweep):
            sweep = sweep[rng.random(len(sweep)) >= profile.p_drop]
        n = len(sweep)
        if n:
            if profile.sigma_range_m:
                sweep[:, 0] = np.maximum(sweep[:, 0] + rng.normal(0.0, profile.sigma_range_m, n), 0.1)
            if profile.sigma_azimuth_deg:
                sweep[:, 1] += rng.normal(0.0, math.radians(profile.sigma_azimuth_deg), n)
            if profile.sigma_elevation_deg:
                sweep[:, 2] += rng.normal(0.0, math.radians(profile.sigma_elevation_deg), n)
            if profile.sigma_velocity_mps:
                sweep[:, 3] += rng.normal(0.0, profile.sigma_velocity_mps, n)
        count = int(rng.poisson(profile.clutter_per_sweep)) if profile.clutter_per_sweep > 0.0 else 0
        if count:
            azimuth = rng.uniform(-hfov / 2.0, hfov / 2.0, count)
            altitude = rng.uniform(-vfov / 2.0, vfov / 2.0, count)
            depth = rng.uniform(1.0, reach, count)
            # Static world seen from the moving vehicle: v_r = -(v_vehicle . u) along the line of sight
            # (positive away from the sensor); the vehicle moves along its own x axis.
            forward, _, _ = mount.directions(azimuth, altitude)
            velocity = -float(speed_at(float(timestamps[index]))) * forward
            mirrored = rng.random(count) < 0.5
            if n:
                velocity = np.where(mirrored, sweep[rng.integers(0, n, count), 3], velocity)
            sweep = np.vstack([sweep, np.column_stack([depth, azimuth, altitude, velocity])])
        out.append(sweep)
        starts.append(starts[-1] + len(sweep))
    detections_out = np.vstack(out).astype(np.float32) if out else np.zeros((0, 4), np.float32)
    return frames[keep], timestamps[keep], np.asarray(starts, dtype=np.int64), detections_out


# --------------------------------------------------------------------------
# GNSS
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class GnssProfile:
    """Per-axis error e(t) = b + g(t) + w(t), drawn at the receiver rate and interpolated."""

    name: str
    bias_m: float = 0.0
    markov_m: float = 0.0
    tau_s: float = 60.0
    white_m: float = 0.0
    rate_hz: float = 1.0
    yaw_bias_deg: float = 0.0
    yaw_markov_deg: float = 0.0
    yaw_tau_s: float = 30.0
    yaw_white_deg: float = 0.0
    velocity_white_mps: float = 0.0
    # Fraction of slow horizontal-position variance shared within a local run.
    # Sensitivity parameter, not a universally calibrated receiver property.
    common_fraction: float = 0.0
    velocity_bias_mps: float = 0.0
    velocity_markov_mps: float = 0.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.common_fraction <= 1.0:
            raise ValueError('common_fraction must be in [0, 1]')

    @property
    def position_std_m(self) -> float:
        return math.sqrt(self.bias_m ** 2 + self.markov_m ** 2 + self.white_m ** 2)

    @property
    def yaw_std_deg(self) -> float:
        return math.sqrt(self.yaw_bias_deg ** 2 + self.yaw_markov_deg ** 2 + self.yaw_white_deg ** 2)

    @property
    def velocity_std_mps(self) -> float:
        return math.sqrt(self.velocity_bias_mps ** 2 + self.velocity_markov_mps ** 2 +
                         self.velocity_white_mps ** 2)


GNSS_PROFILES: Dict[str, GnssProfile] = {
    "ideal": GnssProfile("ideal"),
    # Position and heading preserve the earlier b:g:w ratios; velocity keeps white receiver-epoch noise.
    "rtk": GnssProfile("rtk", bias_m=0.0089732414, markov_m=0.0134598621, tau_s=60.0,
                       white_m=0.0026919724, rate_hz=10.0, yaw_bias_deg=0.0385369084,
                       yaw_markov_deg=0.0578053625, yaw_tau_s=30.0, yaw_white_deg=0.0192684542,
                       velocity_white_mps=0.0073178670),
    "degraded": GnssProfile("degraded", bias_m=0.0852794874, markov_m=0.1279192311, tau_s=30.0,
                            white_m=0.0142132479, rate_hz=1.0, yaw_bias_deg=0.0371302794,
                            yaw_markov_deg=0.2079295648, yaw_tau_s=5.0, yaw_white_deg=0.0742605588,
                            velocity_white_mps=0.0722666351),
}

# Retained for the earlier retrospective analyses; never scheduled by the current campaign.
HISTORICAL_GNSS_PROFILES: Dict[str, GnssProfile] = {
    "consumer": GnssProfile("consumer", 1.5, 0.7, 60.0, 0.05, 1.0, 0.3, 0.9, 10.0, 0.3, 0.10),
}


def _error_series(times: np.ndarray, bias: float, markov: float, tau: float, white: float, rate: float,
                  rng: np.random.Generator) -> np.ndarray:
    """Bias + Gauss-Markov + white noise drawn at ``rate`` and interpolated linearly at ``times``."""
    if not (bias or markov or white):
        return np.zeros_like(times)
    step = 1.0 / rate
    epochs = np.arange(times[0] - step, times[-1] + 2.0 * step, step)
    phi = math.exp(-step / tau) if tau > 0 else 0.0
    g = np.empty(len(epochs))
    g[0] = rng.normal(0.0, markov) if markov else 0.0
    innovations = rng.normal(0.0, 1.0, len(epochs))
    for k in range(1, len(epochs)):
        g[k] = phi * g[k - 1] + math.sqrt(1.0 - phi * phi) * markov * innovations[k]
    series = rng.normal(0.0, bias) + g + (rng.normal(0.0, white, len(epochs)) if white else 0.0)
    return np.interp(times, epochs, series)


class PerturbedPoseSource(RecordedPoseSource):
    """The recorded GNSS-like stream with a profile's errors (position, heading, velocity), declaring the
    profile's accuracy as a receiver reports its own estimate."""

    def __init__(self, records: Sequence[Mapping[str, Any]], clock_origin: float, profile: GnssProfile, seed: int,
                 recorder: str, common: Optional[Mapping[str, Any]] = None) -> None:
        super().__init__(records, clock_origin)
        self.name = "gnss_" + profile.name
        self.profile = profile
        self.position_std_m = profile.position_std_m
        self.yaw_std_rad = math.radians(profile.yaw_std_deg)
        self.velocity_std_mps = profile.velocity_std_mps
        rng = lambda label: np.random.default_rng(stream_seed(seed, "gnss", profile.name, recorder, label))  # noqa: E731
        t = self.times
        independent = math.sqrt(1-profile.common_fraction)
        def position_error(axis: str) -> np.ndarray:
            values = _error_series(t, profile.bias_m*independent, profile.markov_m*independent,
                                   profile.tau_s, profile.white_m, profile.rate_hz, rng(axis))
            if profile.common_fraction:
                if common is None:
                    common_times = t+clock_origin
                    shared = _error_series(common_times, profile.bias_m, profile.markov_m, profile.tau_s,
                                           0.0, profile.rate_hz,
                                           np.random.default_rng(stream_seed(seed,'gnss',profile.name,'common',axis)))
                else:
                    common_times, shared = common[axis]
                values += math.sqrt(profile.common_fraction)*np.interp(t+clock_origin,common_times,shared)
            return values
        self.x = self.x + position_error('x')
        self.y = self.y + position_error('y')
        self.yaw = self.yaw + np.radians(_error_series(t, profile.yaw_bias_deg, profile.yaw_markov_deg, profile.yaw_tau_s,
                                                       profile.yaw_white_deg, profile.rate_hz, rng("yaw")))
        self.vx = self.vx + _error_series(t, profile.velocity_bias_mps, profile.velocity_markov_mps, profile.tau_s,
                                          profile.velocity_white_mps, profile.rate_hz, rng("vx"))
        self.vy = self.vy + _error_series(t, profile.velocity_bias_mps, profile.velocity_markov_mps, profile.tau_s,
                                          profile.velocity_white_mps, profile.rate_hz, rng("vy"))

    @classmethod
    def factory(cls, profile: GnssProfile, seed: int):
        """A ``pose_factory(vehicle_dir, clock_origin)`` for the reconstruction and the replay."""
        common: Dict[str, Any] = {}
        def make(vehicle_dir: Path, clock_origin: float) -> "PerturbedPoseSource":
            path = Path(vehicle_dir) / "ego.jsonl"
            with path.open(encoding="utf-8") as handle:
                records = [json.loads(line) for line in handle if line.strip()]
            if profile.common_fraction and not common:
                timestamps = []
                for peer in Path(vehicle_dir).parent.glob('*/ego.jsonl'):
                    with peer.open(encoding='utf-8') as handle:
                        timestamps += [float(json.loads(line)['timestamp']) for line in handle if line.strip()]
                step = 1/profile.rate_hz
                times = np.arange(math.floor(min(timestamps)/step)*step-step,max(timestamps)+2*step,step)
                for axis in ['x','y']:
                    common[axis] = (times,_error_series(times,profile.bias_m,profile.markov_m,profile.tau_s,
                                     0.0,profile.rate_hz,
                                     np.random.default_rng(stream_seed(seed,'gnss',profile.name,'common',axis))))
            return cls(records, clock_origin, profile, seed, Path(vehicle_dir).name, common or None)
        return make


# --------------------------------------------------------------------------
# Collision reports, clock, sampling, dropout: the copy of a run
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class CollisionPerturbation:
    impulse_rel_std: float = 0.0  # multiplicative noise per callback
    p_drop: float = 0.0  # each callback lost with this probability
    # Crash-recorder-like reports (``_crash_recorder_reports``): callbacks at most burst_gap_s apart are one burst.
    burst_rel_std: float = 0.0  # multiplicative delta-V noise per burst
    mass_rel_std: float = 0.0  # multiplicative mass error per recorder (reported impulse = mass x delta-V)
    burst_jitter_s: float = 0.0  # uniform time shift per burst within +-this
    burst_gap_s: float = 0.075


@dataclass(frozen=True)
class Perturbation:
    """One perturbed condition of a run (anything left at its default is unchanged)."""

    name: str
    radar: RadarProfile = RADAR_PROFILES["ideal"]
    gnss: GnssProfile = GNSS_PROFILES["ideal"]
    collisions: CollisionPerturbation = CollisionPerturbation()
    clock_offsets_s: Tuple[Tuple[str, float], ...] = ()  # (recorder, offset): every timestamp it wrote
    downsample: int = 1  # keep every n-th ego / control / radar sample
    drop_recorders: Tuple[str, ...] = ()
    radar_outage: Optional[Tuple[str, float, float]] = None  # (recorder, start, end) in its local time [s]
    # The recorders whose radars get the radar profile; empty: every recorder.  The random stream of a recorder's
    # radar is keyed by (seed, profile, recorder, radar), so a recorder degraded alone gets exactly the errors it
    # gets when every recorder is degraded (paired asymmetric comparisons).
    radar_recorders: Tuple[str, ...] = ()

    def radar_profile_of(self, recorder: str) -> "RadarProfile":
        if self.radar_recorders and recorder not in self.radar_recorders:
            return RADAR_PROFILES["ideal"]
        return self.radar

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _link_or_copy(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(str(source), str(target))
    except OSError:
        shutil.copyfile(str(source), str(target))


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _write_jsonl(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


TIMED_STREAMS = ("ego.jsonl", "controls.jsonl", "collisions.jsonl", "traffic_signs.jsonl")


def perturbed_copy(run_dir: Path, target: Path, perturbation: Perturbation, seed: int) -> Path:
    """Write the perturbed copy of ``run_dir`` to ``target`` (which must not exist) and return it."""
    run_dir, target = Path(run_dir), Path(target)
    if target.exists():
        raise FileExistsError("a perturbed copy is never overwritten: " + str(target))
    offsets = dict(perturbation.clock_offsets_s)
    for path in sorted(run_dir.rglob("*")):
        relative = path.relative_to(run_dir)
        parts = relative.parts
        if path.is_dir() or parts[0] == "reconstruction":
            continue
        if parts[0] == "vehicles" and len(parts) > 1 and parts[1] in perturbation.drop_recorders:
            continue
        if parts[0] != "vehicles" or len(parts) < 3:
            _link_or_copy(path, target / relative)  # ground truth, run metadata, incident context
            continue
        recorder = parts[1]
        shifted = recorder in offsets
        if parts[2] in TIMED_STREAMS and (shifted or (perturbation.downsample > 1 and parts[2] in ("ego.jsonl", "controls.jsonl"))
                                          or (parts[2] == "collisions.jsonl"
                                              and perturbation.collisions != CollisionPerturbation())):
            _write_jsonl(target / relative, _perturb_stream(path, recorder, parts[2], perturbation, offsets, seed))
        elif parts[2] == "radar" and path.name == "observations.npz" and (
                shifted or perturbation.radar_profile_of(recorder).name != "ideal" or perturbation.downsample > 1
                or (perturbation.radar_outage is not None and perturbation.radar_outage[0] == recorder)):
            _perturb_radar_file(path, target / relative, run_dir / "vehicles" / recorder, recorder, perturbation,
                                offsets, seed)
        elif path.name == "metadata.json" and len(parts) == 4 and shifted:
            # Sensor metadata may carry timestamps of its own: shift the obvious ones.
            data = json.loads(path.read_text(encoding="utf-8"))
            for key in ("first_timestamp", "last_timestamp"):
                if isinstance(data.get(key), (int, float)):
                    data[key] = data[key] + offsets[recorder]
            (target / relative).parent.mkdir(parents=True, exist_ok=True)
            (target / relative).write_text(json.dumps(data, indent=2), encoding="utf-8")
        else:
            _link_or_copy(path, target / relative)
    record = {"source_run": str(run_dir), "seed": seed, "perturbation": perturbation.to_dict(),
              "note": "privileged bookkeeping of the robustness study: the reconstruction never reads this file"}
    (target / "perturbation.json").write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    return target


def _perturb_stream(path: Path, recorder: str, name: str, perturbation: Perturbation, offsets: Mapping[str, float],
                    seed: int) -> List[Dict[str, Any]]:
    rows = _read_jsonl(path)
    shift = offsets.get(recorder, 0.0)
    if name in ("ego.jsonl", "controls.jsonl") and perturbation.downsample > 1:
        rows = rows[::perturbation.downsample]
    if name == "collisions.jsonl":
        c = perturbation.collisions
        rng = np.random.default_rng(stream_seed(seed, "collisions", recorder))
        kept = []
        for row in rows:
            if c.p_drop and rng.random() < c.p_drop:
                continue
            row = dict(row)
            if c.impulse_rel_std:
                row["impulse"] = float(row["impulse"]) * max(0.0, 1.0 + rng.normal(0.0, c.impulse_rel_std))
            kept.append(row)
        rows = kept
        if c.burst_rel_std or c.mass_rel_std or c.burst_jitter_s:
            # Keyed by the run too: a recorder draws only a few errors, which must differ between runs.
            run = "{0}/{1}".format(path.parents[3].name, path.parents[2].name)
            rows = _crash_recorder_reports(rows, c, np.random.default_rng(stream_seed(seed, "crash_recorder", run,
                                                                                        recorder)))
    if shift:
        # Every time the recorder wrote: "timestamp", and the "timestamp_first" / "_confirmed" / "_last" of a
        # traffic-sign track.
        rows = [{key: (float(value) + shift if _is_time(key) and value is not None else value)
                 for key, value in row.items()} for row in rows]
    return rows


def _crash_recorder_reports(rows: Sequence[Mapping[str, Any]], c: CollisionPerturbation,
                            rng: np.random.Generator) -> List[Dict[str, Any]]:
    """Collision callbacks as a crash recorder reports them: the reported impulse is mass x delta-V, so every
    callback of a burst shares one delta-V error and every burst of the recorder one mass error, and a burst's
    callbacks move together by one timing error."""
    bursts: List[List[Dict[str, Any]]] = []
    for row in sorted(rows, key=lambda r: float(r["timestamp"])):
        if bursts and float(row["timestamp"]) - float(bursts[-1][-1]["timestamp"]) <= c.burst_gap_s:
            bursts[-1].append(dict(row))
        else:
            bursts.append([dict(row)])
    mass = max(0.0, 1.0 + rng.normal(0.0, c.mass_rel_std)) if c.mass_rel_std else 1.0
    kept = []
    for burst in bursts:
        factor = mass * (max(0.0, 1.0 + rng.normal(0.0, c.burst_rel_std)) if c.burst_rel_std else 1.0)
        shift = float(rng.uniform(-c.burst_jitter_s, c.burst_jitter_s)) if c.burst_jitter_s else 0.0
        for row in burst:
            row["impulse"] = float(row["impulse"]) * factor
            row["timestamp"] = float(row["timestamp"]) + shift
            kept.append(row)
    return kept


def _is_time(key: str) -> bool:
    return key == "timestamp" or key.startswith("timestamp_") or key.endswith("_timestamp")


def _perturb_radar_file(path: Path, target: Path, vehicle_dir: Path, recorder: str, perturbation: Perturbation,
                        offsets: Mapping[str, float], seed: int) -> None:
    with np.load(str(path)) as data:  # closed at once: Windows keeps an open file from being linked or removed
        frames, timestamps, starts, detections = (np.array(data["frames"]), np.array(data["timestamps"]),
                                                  np.array(data["offsets"]), np.array(data["detections"]))
    metadata = json.loads((path.parent / "metadata.json").read_text(encoding="utf-8"))
    ego = _read_jsonl(vehicle_dir / "ego.jsonl")
    ego_t = np.array([float(row["timestamp"]) for row in ego])
    ego_v = np.array([math.hypot(float((row.get("velocity") or {}).get("x", 0.0)),
                                 float((row.get("velocity") or {}).get("y", 0.0))) for row in ego])
    keep = np.arange(len(frames))[::max(perturbation.downsample, 1)]
    if perturbation.radar_outage is not None and perturbation.radar_outage[0] == recorder:
        _, start, end = perturbation.radar_outage
        local = timestamps - ego_t[0]
        keep = np.array([k for k in keep if not (start <= local[k] <= end)], dtype=int)
    profile = perturbation.radar_profile_of(recorder)
    rng = np.random.default_rng(stream_seed(seed, "radar", profile.name, recorder, path.parent.name))
    frames, timestamps, starts, detections = perturb_sweeps(
        frames, timestamps, starts, detections, metadata, profile, rng,
        lambda t: float(np.interp(t, ego_t, ego_v)), keep)
    timestamps = timestamps + offsets.get(recorder, 0.0)
    target.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(str(target), frames=frames, timestamps=timestamps, offsets=starts, detections=detections)
