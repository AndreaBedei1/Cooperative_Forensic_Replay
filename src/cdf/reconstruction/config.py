"""Reconstruction parameters and their defaults; ``configs/reconstruction.yaml`` sets the values used."""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Tuple

UNECE_R157_TIME_GAP = ((7.2, 1.0), (10.0, 1.1), (20.0, 1.2), (30.0, 1.3), (40.0, 1.4), (50.0, 1.5), (60.0, 1.6))


@dataclass
class CollisionConfig:
    merge_gap_s: float = 0.5
    new_impact_ratio: float = 0.75
    min_impact_ratio: float = 0.25
    min_new_impact_impulse: float = 1000.0
    impact_acceleration_mps2: float = 20.0
    reversal_angle_deg: float = 90.0
    undirected_impact_ratio: float = 0.5


@dataclass
class TrackingConfig:
    min_height_m: float = 0.3
    max_height_m: float = 2.5
    moving_speed_mps: float = 1.0
    cluster_distance_m: float = 2.0
    max_track_gap_s: float = 0.5
    min_track_frames: int = 5
    measurement_std_m: float = 0.5
    radial_speed_std_mps: float = 0.3
    acceleration_std_mps2: float = 6.0
    smoothing_innovation_sigma: float = 3.0
    max_braking_mps2: float = 30.0
    contact_clearance_m: float = 1.0
    lane_heading_std_deg: float = 10.0
    identity_body_width_m: float = 2.5
    gate_probability: float = 0.99
    body_length_m: float = 4.6
    body_width_m: float = 1.9
    radar_range_std_m: float = 0.25
    radar_azimuth_std_deg: float = 0.5
    min_track_support_s: float = 0.2
    min_track_updates: int = 3
    gap_cap_s: float = 2.0
    nominal_vehicle_mass_kg: float = 1500.0
    position_cap_m: float = 10.0
    doppler_cap_mps: float = 10.0
    return_likelihood_ratio: float = 20.0
    yaw_rate_std_rps: float = 0.3


@dataclass
class SemanticsConfig:
    brake_onset_threshold: float = 0.1
    throttle_on_threshold: float = 0.10
    throttle_off_threshold: float = 0.05
    throttle_release_debounce_s: float = 0.2
    full_stop_speed_mps: float = 0.3
    speed_limit_hysteresis_kmh: float = 1.0
    closing_speed_threshold_mps: float = 1.0
    critical_reaction_time_s: float = 1.0
    critical_deceleration_mps2: float = 6.0
    critical_standstill_margin_m: float = 1.0
    critical_lateral_margin_m: float = 0.3
    critical_release_ratio: float = 0.75
    prediction_horizon_s: float = 6.0
    prediction_time_step_s: float = 0.05
    target_length_m: float = 4.6
    target_width_m: float = 1.9
    target_braking_min_mps2: float = 1.0
    critical_min_track_age_s: float = 0.5
    critical_time_gap_table: Tuple[Tuple[float, float], ...] = UNECE_R157_TIME_GAP
    critical_min_following_distance_m: float = 2.0
    critical_forward_min_speed_mps: float = 1.0
    critical_front_lateral_margin_m: float = 1.0
    critical_front_lateral_speed_mps: float = 0.3
    critical_forward_release_factor: float = 1.10
    occlusion_margin_m: float = 0.5
    turn_yaw_rate_window_s: float = 0.2
    turn_yaw_rate_on_dps: float = 10.0
    turn_yaw_rate_off_dps: float = 5.0
    turn_min_speed_mps: float = 1.0
    turn_release_debounce_s: float = 0.3
    turn_min_duration_s: float = 0.5
    turn_min_heading_change_deg: float = 15.0
    path_half_width_m: float = 1.5
    path_hysteresis_m: float = 0.5
    path_edge_std_m: float = 0.25
    path_occupancy_quantile: float = 1.645
    path_min_definite_samples: int = 2
    track_appeared_front_deg: float = 5.0
    max_position_std_m: float = 1.0
    max_velocity_std_mps: float = 1.0
    cut_in_max_heading_deg: float = 25.0
    cut_in_min_target_speed_mps: float = 2.0
    cut_in_lateral_speed_mps: float = 0.3
    cut_in_persistence_s: float = 0.5
    cut_in_outside_margin_m: float = 0.5
    cut_in_min_displacement_m: float = 0.5
    cut_in_horizon_s: float = 3.0
    cut_in_preentry_margin_m: float = 1.0
    cut_in_settle_speed_mps: float = 0.2
    cut_in_settle_s: float = 0.3


@dataclass
class FusionConfig:
    impulse_tolerance: float = 0.10
    impulse_relative_std: float = 0.10
    impulse_sigma_gate: float = 3.0
    contact_consistency_m: float = 1.0
    recontact_max_pause_s: float = 2.0
    recontact_max_separation_m: float = 1.0
    clock_tolerance_s: float = 0.1
    contact_window_s: float = 1.0
    contact_range_m: float = 3.5
    contact_range_scale_m: float = 3.0
    approach_window_s: float = 1.0
    min_track_persistence_s: float = 1.0
    speed_consistency_mps: float = 1.5
    touching_clearance_m: float = 1.0
    rival_clearance_m: float = 2.0
    observed_alignment_step_s: float = 0.05
    observed_alignment_min_samples: int = 10
    observed_alignment_min_speed_mps: float = 2.0
    observed_alignment_uniqueness_ratio: float = 3.0
    link_min_samples: int = 10
    link_min_fraction: float = 0.8
    anonymous_gate_probability: float = 0.99
    anonymous_min_shared_samples: int = 10
    anonymous_pass_fraction: float = 0.8
    stitch_max_gap_s: float = 1.5
    box_face_std_m: float = 0.25
    box_length_std_m: float = 0.7
    box_width_std_m: float = 0.2
    entity_output_rate_hz: float = 10.0
    mutual_refinement: bool = False
    mutual_refinement_iterations: int = 3
    radar_range_std_m: float = 0.25
    radar_azimuth_std_deg: float = 0.5
    assignment_likelihood_ratio: float = 20.0
    retrospective_new_target_density: float = 3.57e-5
    retrospective_min_posterior: float = 0.95


@dataclass
class ReconstructionConfig:
    trace_hz: float = 10.0
    collision: CollisionConfig = field(default_factory=CollisionConfig)
    tracking: TrackingConfig = field(default_factory=TrackingConfig)
    semantics: SemanticsConfig = field(default_factory=SemanticsConfig)
    fusion: FusionConfig = field(default_factory=FusionConfig)

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"trace_hz": self.trace_hz}
        for section in ("collision", "tracking", "semantics", "fusion"):
            value = getattr(self, section)
            out[section] = {item.name: getattr(value, item.name) for item in fields(value)}
        return out


def _section(cls, values: Optional[Mapping[str, Any]]):
    values = dict(values or {})
    known = {item.name for item in fields(cls)}
    unknown = sorted(set(values) - known)
    if unknown:
        raise ValueError("unknown {0} parameters: {1}".format(cls.__name__, ", ".join(unknown)))
    return cls(**values)


def config_from_mapping(data: Optional[Mapping[str, Any]]) -> ReconstructionConfig:
    """Build a config from the ``reconstruction:`` mapping, rejecting typos."""
    data = dict(data or {})
    unknown = sorted(set(data) - {"trace_hz", "collision", "tracking", "semantics", "fusion"})
    if unknown:
        raise ValueError("unknown reconstruction sections: " + ", ".join(unknown))
    return ReconstructionConfig(
        trace_hz=float(data.get("trace_hz", 10.0)),
        collision=_section(CollisionConfig, data.get("collision")),
        tracking=_section(TrackingConfig, data.get("tracking")),
        semantics=_section(SemanticsConfig, data.get("semantics")),
        fusion=_section(FusionConfig, data.get("fusion")),
    )


def load_config(path: Optional[Path] = None) -> ReconstructionConfig:
    """Load ``configs/reconstruction.yaml`` (or ``path``); defaults if absent."""
    if path is None:
        path = Path(__file__).resolve().parents[3] / "configs" / "reconstruction.yaml"
    path = Path(path)
    if not path.exists():
        return ReconstructionConfig()
    import yaml

    document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return config_from_mapping(document.get("reconstruction", {}))
