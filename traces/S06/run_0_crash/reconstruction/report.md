# Reconstruction report - S06/run_0_crash

Inputs: `vehicles/A/`, `vehicles/B/`, `vehicles/C/` (vehicle-local files) and the supplied `incident_context.json`. `ground_truth/` and the run's `metadata.json` were not read; the privileged comparison, if run, is in `evaluation/`.

Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.

Pipeline: raw log -> local trace -> local graph (each recorder alone, own clock, own frame) -> graph-level alignment -> identity association -> road users in the common frame of the recorders' own pose streams -> global graph.

## Local reconstructions

| Recorder | Duration (local) | Trace frames | Graph nodes | Graph edges | Radar tracks | Collision reports (local time) |
|----------|-----------------:|-------------:|------------:|------------:|-------------:|-------------------------------|
| A | 15.15 s | 153 | 20 | 39 | 2 | A:e09 @ 4.10 s |
| B | 15.15 s | 153 | 20 | 44 | 2 | B:e09 @ 4.10 s |
| C | 15.15 s | 153 | 14 | 27 | 2 | none |

## Graph alignment

Reference event: `collision_001` (t_global = 0); `t_global = t_local + offset_to_global`. A graph that did not report it is aligned through the chain of matched collisions linking it to the reference (multi-hop); its anchor is its own report of the last collision of that chain.

| Graph | Status | Anchor node | Anchor local time | Offset to global | Note |
|-------|--------|-------------|------------------:|-----------------:|------|
| A | ALIGNED | A:e09 | 4.10 | -4.10 | reported the reference collision collision_001 |
| B | ALIGNED | B:e09 | 4.10 | -4.10 | reported the reference collision collision_001 |
| C | ALIGNED | - | - | -4.15 | aligned through observed trajectories: the near surfaces of A:track_001, B:track_001, C:track_001 on A, C:track_002 on B lie where their lines of sight enter the body (pooled median 0.59 sigma) at this offset; offsets within 2.00 sigma span [-4.20, -4.00] s and nothing else fits |

Estimated relative clock offsets: B - A = +0.000 s, C - A = +0.050 s, C - B = +0.050 s

Matched `collision_001`: A and B both recorded a collision; peak impulses 12137.59 vs 12137.59 N*s (similarity 1.000, tolerance 0.10); no competing report within tolerance; the two bodies touch at their reports (0.00 m apart, tolerance 1.0 m); independent relative impulse std 0.100; combined z 0.000 (gate 3.0); engineering assumption; pre-contact radar view of each recorder checked against the candidate partner's own speed: not contradicted

## Identity associations

| Local track | Global entity | Status | Confidence | Evidence |
|-------------|---------------|--------|-----------:|----------|
| A:track_001 | C | ASSOCIATED | 0.99 | A and B both reported collision_001 (peak impulse 12137.59 vs 12137.59 N*s)<br>tracked for 4.10 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 21.7 m -> 11.7 m over the last 1.0 s<br>track motion contradicts B's own speed in the observed direction (3 sigma; full-speed RMSE 8.44 m/s for reference)<br>clearance at the contact 11.68 m (beyond 3.50 m: confidence factor 0.02)<br>common frame: its returns lie on C's own footprint (median 0.00 m, 0.00 sigma of the relative uncertainty, over 302 samples; 99% within 3 sigma) at C's own velocity |
| A:track_002 | B | ASSOCIATED | 0.96 | A and B both reported collision_001 (peak impulse 12137.59 vs 12137.59 N*s)<br>tracked for 2.05 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 14.9 m -> 0.0 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 0.41 m/s for reference)<br>clearance at the contact 0.00 m<br>the only track of A compatible with the contact |
| B:track_001 | C | ASSOCIATED | 1.00 | B and A both reported collision_001 (peak impulse 12137.59 vs 12137.59 N*s)<br>tracked for 2.00 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 18.4 m -> 10.8 m over the last 1.0 s<br>track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 7.78 m/s for reference)<br>clearance at the contact 10.75 m (beyond 3.50 m: confidence factor 0.05)<br>common frame: its returns lie on C's own footprint (median 0.00 m, 0.00 sigma of the relative uncertainty, over 261 samples; 100% within 3 sigma) at C's own velocity |
| B:track_002 | A | ASSOCIATED | 0.95 | B and A both reported collision_001 (peak impulse 12137.59 vs 12137.59 N*s)<br>tracked for 2.00 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 14.9 m -> 1.1 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 0.48 m/s for reference)<br>clearance at the contact 0.62 m<br>the only track of B compatible with the contact |
| C:track_001 | A | ASSOCIATED | 1.00 | no matched collision of C names a partner<br>common frame: its returns lie on A's own footprint (median 0.00 m, 0.00 sigma of the relative uncertainty, over 79 samples; 100% within 3 sigma) at A's own velocity |
| C:track_002 | U1 | ANONYMOUS | - | no matched collision of C names a partner<br>anonymous road user U1: C:track_002 |

## Road users in the common frame

- Observed-trajectory alignment of C: accepted (offset -4.15, pooled median 0.59 sigma, interval [-4.2, -4.0]).
- A:track_001 is C: its returns lie on C's own footprint (median 0.00 m over 302 samples, 99% within 3 sigma) at C's velocity.
- B:track_001 is C: its returns lie on C's own footprint (median 0.00 m over 261 samples, 100% within 3 sigma) at C's velocity.
- C:track_001 is A: its returns lie on A's own footprint (median 0.00 m over 79 samples, 100% within 3 sigma) at A's velocity.
- U1 (anonymous, -2.05 to 11.00 s): C:track_002; footprint 4.60 x 1.90 m (prior/prior); fusion box_fit+covariance_intersection.

## Global graph

53 nodes, 162 edges; 11 merged node(s): g03 TRACK_APPEARED_FRONT(C,A) from C:e03 + C:e14, g10 CLOSING_START(A,C) from A:e04 + A:e18, g13 CLOSING_START(A,B) from A:e06 + A:e11, g14 CLOSING_START(C,U1) from C:e06 + C:e13, g17 CLOSING_START(B,A) from B:e06 + B:e11, g18 CLOSING_START(B,C) from B:e05 + B:e16, g21 CRITICAL_TTC_START(A,B) from A:e07 + A:e10, g22 CRITICAL_TTC_START(B,A) from B:e07 + B:e10, g29 COLLISION(A,B) from A:e09 + B:e09, g40 CLOSING_START(B,A) from B:e15 + B:e20, g41 CLOSING_START(A,B) from A:e15 + A:e16.

### Event sequence (global time)

- `-4.15` MOVING_START(C); THROTTLE_START(C); TRACK_APPEARED_FRONT(C,A); CLOSING_START(C,A)
- `-4.10` MOVING_START(A); MOVING_START(B); THROTTLE_START(A); THROTTLE_START(B); TRACK_APPEARED_FRONT(A,C); CLOSING_START(A,C)
- `-2.05` TRACK_APPEARED_LEFT(C,U1); TRACK_APPEARED_RIGHT(A,B); CLOSING_START(A,B); CLOSING_START(C,U1)
- `-2.00` TRACK_APPEARED_LEFT(B,A); TRACK_APPEARED_RIGHT(B,C); CLOSING_START(B,A); CLOSING_START(B,C)
- `-1.80` THROTTLE_END(C); BRAKE_START(C)
- `-1.55` CRITICAL_TTC_START(A,B)
- `-1.50` CRITICAL_TTC_START(B,A)
- `-1.25` MOVING_END(C); STOP_START(C)
- `-0.25` EGO_PATH_ENTRY(C,U1)
- `-0.20` EGO_PATH_ENTRY(C,A)
- `-0.10` EGO_PATH_ENTRY(B,A)
- `-0.05` EGO_PATH_ENTRY(A,B)
- `+0.00` COLLISION(A,B); CRITICAL_TTC_END(A,B); CRITICAL_TTC_END(B,A); CLOSING_END(A,B); CLOSING_END(B,A); TURN_LEFT_START(A); TURN_RIGHT_START(B)
- `+0.05` THROTTLE_END(A); THROTTLE_END(B); BRAKE_START(A); BRAKE_START(B)
- `+0.10` CLOSING_START(B,A)
- `+0.15` CLOSING_START(A,B)
- `+0.40` CLOSING_END(C,U1); TRACK_LOST(C,A)
- `+0.45` CLOSING_END(A,B)
- `+0.50` CLOSING_END(B,C); TURN_RIGHT_END(B); MOVING_END(B); STOP_START(B)
- `+0.60` TURN_LEFT_END(A)
- `+0.65` CLOSING_END(A,C); CLOSING_END(B,A); MOVING_END(A); STOP_START(A)

### What happened, in plain language

- 4.15 s before the reference collision, C started moving (already the case when first observed).
- 4.15 s before the reference collision, C pressed the accelerator (already the case when first observed).
- 4.15 s before the reference collision, C's radar started tracking A, which appeared in front of it.
- 4.15 s before the reference collision, C observed A start closing in (already the case when first observed).
- 4.10 s before the reference collision, A started moving (already the case when first observed).
- 4.10 s before the reference collision, B started moving (already the case when first observed).
- 4.10 s before the reference collision, A pressed the accelerator (already the case when first observed).
- 4.10 s before the reference collision, B pressed the accelerator (already the case when first observed).
- 4.10 s before the reference collision, A's radar started tracking C, which appeared in front of it.
- 4.10 s before the reference collision, A observed C start closing in (already the case when first observed).
- 2.05 s before the reference collision, C's radar started tracking anonymous road user U1, which appeared on its left.
- 2.05 s before the reference collision, A's radar started tracking B, which appeared on its right.
- 2.05 s before the reference collision, A observed B start closing in (already the case when first observed).
- 2.05 s before the reference collision, C observed anonymous road user U1 start closing in (already the case when first observed).
- 2.00 s before the reference collision, B's radar started tracking A, which appeared on its left.
- 2.00 s before the reference collision, B's radar started tracking C, which appeared on its right.
- 2.00 s before the reference collision, B observed A start closing in (already the case when first observed).
- 2.00 s before the reference collision, B observed C start closing in (already the case when first observed).
- 1.80 s before the reference collision, C released the accelerator.
- 1.80 s before the reference collision, C started braking.
- 1.55 s before the reference collision, A's time-to-contact with B became critical.
- 1.50 s before the reference collision, B's time-to-contact with A became critical.
- 1.25 s before the reference collision, C stopped moving.
- 1.25 s before the reference collision, C came to a stop.
- 0.25 s before the reference collision, C observed anonymous road user U1 enter its forward path corridor.
- 0.20 s before the reference collision, C observed A enter its forward path corridor.
- 0.10 s before the reference collision, B observed A enter its forward path corridor.
- 0.05 s before the reference collision, A observed B enter its forward path corridor.
- At the reference collision, A and B both recorded this same collision (peak impulses A: 12138, B: 12138 N*s).
- At the reference collision, A's time-to-contact with B stopped being critical.
- At the reference collision, B's time-to-contact with A stopped being critical.
- At the reference collision, A observed B stop closing in.
- At the reference collision, B observed A stop closing in.
- At the reference collision, A started turning left.
- At the reference collision, B started turning right.
- 0.05 s after the reference collision, A released the accelerator.
- 0.05 s after the reference collision, B released the accelerator.
- 0.05 s after the reference collision, A started braking.
- 0.05 s after the reference collision, B started braking.
- 0.10 s after the reference collision, B observed A start closing in.
- 0.15 s after the reference collision, A observed B start closing in.
- 0.40 s after the reference collision, C observed anonymous road user U1 stop closing in.
- 0.40 s after the reference collision, C's radar lost A (its states are UNKNOWN from then on, not ended).
- 0.45 s after the reference collision, A observed B stop closing in.
- 0.50 s after the reference collision, B observed C stop closing in.
- 0.50 s after the reference collision, B stopped turning right.
- 0.50 s after the reference collision, B stopped moving.
- 0.50 s after the reference collision, B came to a stop.
- 0.60 s after the reference collision, A stopped turning left.
- 0.65 s after the reference collision, A observed C stop closing in.
- 0.65 s after the reference collision, B observed A stop closing in.
- 0.65 s after the reference collision, A stopped moving.
- 0.65 s after the reference collision, A came to a stop.

### Temporal safety relations

CUT_IN_START < CRITICAL_TTC_START < COLLISION, or CRITICAL_TTC_START <= CUT_IN_START (critical TTC already active), and EGO_PATH_ENTRY before/after the critical TTC. Temporal order only, not causes.

- A's track_002 (B): CRITICAL_TTC_START 2.55, COLLISION with B 4.10 (+1.55 s); EGO_PATH_ENTRY 4.05 after critical TTC (+1.50 s) [local times; t_global: critical_ttc_start -1.55, ego_path_entry -0.05, collision +0.00]
- B's track_002 (A): CRITICAL_TTC_START 2.60, COLLISION with A 4.10 (+1.50 s); EGO_PATH_ENTRY 4.00 after critical TTC (+1.40 s) [local times; t_global: critical_ttc_start -1.50, ego_path_entry -0.10, collision +0.00]
- C's track_001 (A): EGO_PATH_ENTRY 3.95, no critical TTC [local times; t_global: ego_path_entry -0.20]
- C's track_002 (unidentified U1): EGO_PATH_ENTRY 3.90, no critical TTC [local times; t_global: ego_path_entry -0.25]

### Simultaneous events (order unresolved at 0.05 s)

- MOVING_START(C); THROTTLE_START(C); TRACK_APPEARED_FRONT(C,A); CLOSING_START(C,A)
- MOVING_START(A); MOVING_START(B); THROTTLE_START(A); THROTTLE_START(B); TRACK_APPEARED_FRONT(A,C); CLOSING_START(A,C)
- TRACK_APPEARED_LEFT(C,U1); TRACK_APPEARED_RIGHT(A,B); CLOSING_START(A,B); CLOSING_START(C,U1)
- TRACK_APPEARED_LEFT(B,A); TRACK_APPEARED_RIGHT(B,C); CLOSING_START(B,A); CLOSING_START(B,C)
- THROTTLE_END(C); BRAKE_START(C)
- MOVING_END(C); STOP_START(C)
- COLLISION(A,B); CRITICAL_TTC_END(A,B); CRITICAL_TTC_END(B,A); CLOSING_END(A,B); CLOSING_END(B,A); TURN_LEFT_START(A); TURN_RIGHT_START(B)
- THROTTLE_END(A); THROTTLE_END(B); BRAKE_START(A); BRAKE_START(B)
- CLOSING_END(C,U1); TRACK_LOST(C,A)
- CLOSING_END(B,C); TURN_RIGHT_END(B); MOVING_END(B); STOP_START(B)
- CLOSING_END(A,C); CLOSING_END(B,A); MOVING_END(A); STOP_START(A)

### States still active when observation ended

A:
- EGO_PATH of track_002, since A:e08 (t = 4.05 s)
- BRAKE, since A:e14 (t = 4.15 s)
- STOP, since A:e20 (t = 4.75 s)
B:
- EGO_PATH of track_002, since B:e08 (t = 4.00 s)
- BRAKE, since B:e14 (t = 4.15 s)
- STOP, since B:e19 (t = 4.60 s)
C:
- CLOSING of track_001, since C:e04 (t = 0.00 s); the track was lost at 4.55 s
- BRAKE, since C:e08 (t = 2.35 s)
- STOP, since C:e10 (t = 2.90 s)
- EGO_PATH of track_002, since C:e11 (t = 3.90 s)
- EGO_PATH of track_001, since C:e12 (t = 3.95 s); the track was lost at 4.55 s

### Sign detection windows

A:
- none
B:
- none
C:
- none

### Perceived state just before each collision report

- A A:e09 at 4.10 s (local): ego: MOVING, THROTTLE; track_001: CLOSING; track_002: CLOSING, CRITICAL_TTC, IN_EGO_PATH
- B B:e09 at 4.10 s (local): ego: MOVING, THROTTLE; track_001: CLOSING; track_002: CLOSING, CRITICAL_TTC, IN_EGO_PATH

### Tracks lost while a state was active

A lost track's states become UNKNOWN: the recorder can no longer tell whether they ended.

A:
- no track was lost
B:
- no track was lost
C:
- track_001 at 4.55 s (C:e14): CLOSING, IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)

## Uncertainty and limitations

- C:track_002 stays anonymous (U1): no matched collision of C names a partner.
- Global time rests on matched collisions (t_global = 0 at the reference one) and a constant offset per recorder; clock drift is not modelled, so timing uncertainty grows away from the collisions that align each recorder.
- Radar tracks follow the visible surface of an object, not its centre, and a straight-ahead corridor is used for 'in path'.

## Files

- Local: `<recorder>/local_trace.jsonl`, `local_tracks.jsonl`, `local_graph.json|md|dot`
- Global: `global/alignment.json`, `associations.json`, `anonymous_entities.json`, `global_trace.jsonl`, `global_graph.json|md|dot`

## Parameters

```
{
  "trace_hz": 10.0,
  "collision": {
    "merge_gap_s": 0.5,
    "new_impact_ratio": 0.75,
    "min_impact_ratio": 0.25,
    "min_new_impact_impulse": 1000.0,
    "impact_acceleration_mps2": 20.0,
    "reversal_angle_deg": 90.0,
    "undirected_impact_ratio": 0.5
  },
  "tracking": {
    "min_height_m": 0.3,
    "max_height_m": 2.5,
    "moving_speed_mps": 1.0,
    "cluster_distance_m": 2.0,
    "max_track_gap_s": 0.5,
    "min_track_frames": 5,
    "measurement_std_m": 0.5,
    "radial_speed_std_mps": 0.3,
    "acceleration_std_mps2": 6.0,
    "smoothing_innovation_sigma": 3.0,
    "max_braking_mps2": 30.0,
    "contact_clearance_m": 1.0,
    "lane_heading_std_deg": 10.0,
    "identity_body_width_m": 2.5,
    "gate_probability": 0.99,
    "body_length_m": 4.6,
    "body_width_m": 1.9,
    "radar_range_std_m": 0.25,
    "radar_azimuth_std_deg": 0.5,
    "min_track_support_s": 0.2,
    "min_track_updates": 3,
    "gap_cap_s": 2.0,
    "nominal_vehicle_mass_kg": 1500.0,
    "position_cap_m": 10.0,
    "doppler_cap_mps": 10.0,
    "return_likelihood_ratio": 20.0,
    "yaw_rate_std_rps": 0.3
  },
  "semantics": {
    "brake_onset_threshold": 0.1,
    "throttle_on_threshold": 0.1,
    "throttle_off_threshold": 0.05,
    "throttle_release_debounce_s": 0.2,
    "full_stop_speed_mps": 0.3,
    "speed_limit_hysteresis_kmh": 1.0,
    "closing_speed_threshold_mps": 1.0,
    "critical_reaction_time_s": 1.0,
    "critical_deceleration_mps2": 6.0,
    "critical_standstill_margin_m": 1.0,
    "critical_lateral_margin_m": 0.3,
    "critical_release_ratio": 0.75,
    "prediction_horizon_s": 6.0,
    "prediction_time_step_s": 0.05,
    "target_length_m": 4.6,
    "target_width_m": 1.9,
    "target_braking_min_mps2": 1.0,
    "critical_min_track_age_s": 0.5,
    "critical_time_gap_table": [
      [
        7.2,
        1.0
      ],
      [
        10.0,
        1.1
      ],
      [
        20.0,
        1.2
      ],
      [
        30.0,
        1.3
      ],
      [
        40.0,
        1.4
      ],
      [
        50.0,
        1.5
      ],
      [
        60.0,
        1.6
      ]
    ],
    "critical_min_following_distance_m": 2.0,
    "critical_forward_min_speed_mps": 1.0,
    "critical_front_lateral_margin_m": 1.0,
    "critical_front_lateral_speed_mps": 0.3,
    "critical_forward_release_factor": 1.1,
    "occlusion_margin_m": 0.5,
    "turn_yaw_rate_window_s": 0.2,
    "turn_yaw_rate_on_dps": 10.0,
    "turn_yaw_rate_off_dps": 5.0,
    "turn_min_speed_mps": 1.0,
    "turn_release_debounce_s": 0.3,
    "turn_min_duration_s": 0.5,
    "turn_min_heading_change_deg": 15.0,
    "path_half_width_m": 1.5,
    "path_hysteresis_m": 0.5,
    "path_edge_std_m": 0.25,
    "path_occupancy_quantile": 1.645,
    "path_min_definite_samples": 2,
    "track_appeared_front_deg": 5.0,
    "max_position_std_m": 1.0,
    "max_velocity_std_mps": 1.0,
    "cut_in_max_heading_deg": 25.0,
    "cut_in_min_target_speed_mps": 2.0,
    "cut_in_lateral_speed_mps": 0.3,
    "cut_in_persistence_s": 0.5,
    "cut_in_outside_margin_m": 0.5,
    "cut_in_min_displacement_m": 0.5,
    "cut_in_horizon_s": 3.0,
    "cut_in_preentry_margin_m": 1.0,
    "cut_in_settle_speed_mps": 0.2,
    "cut_in_settle_s": 0.3
  },
  "fusion": {
    "impulse_tolerance": 0.1,
    "impulse_relative_std": 0.1,
    "impulse_sigma_gate": 3.0,
    "contact_consistency_m": 1.0,
    "recontact_max_pause_s": 2.0,
    "recontact_max_separation_m": 1.0,
    "clock_tolerance_s": 0.1,
    "contact_window_s": 1.0,
    "contact_range_m": 3.5,
    "contact_range_scale_m": 3.0,
    "approach_window_s": 1.0,
    "min_track_persistence_s": 1.0,
    "speed_consistency_mps": 1.5,
    "touching_clearance_m": 1.0,
    "rival_clearance_m": 2.0,
    "observed_alignment_step_s": 0.05,
    "observed_alignment_min_samples": 10,
    "observed_alignment_min_speed_mps": 2.0,
    "observed_alignment_uniqueness_ratio": 3.0,
    "link_min_samples": 10,
    "link_min_fraction": 0.8,
    "anonymous_gate_probability": 0.99,
    "anonymous_min_shared_samples": 10,
    "anonymous_pass_fraction": 0.8,
    "stitch_max_gap_s": 1.5,
    "box_face_std_m": 0.25,
    "box_length_std_m": 0.7,
    "box_width_std_m": 0.2,
    "entity_output_rate_hz": 10.0,
    "mutual_refinement": false,
    "mutual_refinement_iterations": 3,
    "radar_range_std_m": 0.25,
    "radar_azimuth_std_deg": 0.5,
    "assignment_likelihood_ratio": 20.0,
    "retrospective_new_target_density": 3.57e-05,
    "retrospective_min_posterior": 0.95
  }
}
```
