# Reconstruction report - S11/run_0_consequential

Inputs: `vehicles/A/`, `vehicles/B/`, `vehicles/C/` (vehicle-local files) and the supplied `incident_context.json`. `ground_truth/` and the run's `metadata.json` were not read; the privileged comparison, if run, is in `evaluation/`.

Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.

Pipeline: raw log -> local trace -> local graph (each recorder alone, own clock, own frame) -> graph-level alignment -> identity association -> road users in the common frame of the recorders' own pose streams -> global graph.

## Local reconstructions

| Recorder | Duration (local) | Trace frames | Graph nodes | Graph edges | Radar tracks | Collision reports (local time) |
|----------|-----------------:|-------------:|------------:|------------:|-------------:|-------------------------------|
| A | 11.95 s | 121 | 22 | 42 | 1 | A:e10 @ 5.55 s, A:e17 @ 6.60 s |
| B | 11.95 s | 121 | 15 | 23 | 2 | B:e10 @ 5.55 s |
| C | 11.95 s | 121 | 13 | 22 | 1 | C:e09 @ 6.60 s |

## Graph alignment

Reference event: `collision_001` (t_global = 0); `t_global = t_local + offset_to_global`. A graph that did not report it is aligned through the chain of matched collisions linking it to the reference (multi-hop); its anchor is its own report of the last collision of that chain.

| Graph | Status | Anchor node | Anchor local time | Offset to global | Note |
|-------|--------|-------------|------------------:|-----------------:|------|
| A | ALIGNED | A:e10 | 5.55 | -5.55 | reported the reference collision collision_001 |
| B | ALIGNED | B:e10 | 5.55 | -5.55 | reported the reference collision collision_001 |
| C | ALIGNED | C:e09 | 6.60 | -5.55 | shares collision_002 with A, aligned through collision_001 -> collision_002 |

Estimated relative clock offsets: B - A = +0.000 s, C - A = +0.000 s, C - B = +0.000 s

Matched `collision_001`: A and B both recorded a collision; peak impulses 4243.51 vs 4243.51 N*s (similarity 1.000, tolerance 0.10); no competing report within tolerance; the two bodies touch at their reports (0.00 m apart, tolerance 1.0 m); independent relative impulse std 0.100; combined z 0.000 (gate 3.0); engineering assumption; pre-contact radar view of each recorder checked against the candidate partner's own speed: not contradicted

Matched `collision_002`: A and C both recorded a collision; peak impulses 839.68 vs 839.68 N*s (similarity 1.000, tolerance 0.10); no competing report within tolerance; the two bodies touch at their reports (0.00 m apart, tolerance 1.0 m); independent relative impulse std 0.100; combined z 0.000 (gate 3.0); engineering assumption; pre-contact radar view of each recorder checked against the candidate partner's own speed: not contradicted

## Identity associations

| Local track | Global entity | Status | Confidence | Evidence |
|-------------|---------------|--------|-----------:|----------|
| A:track_001 | C | ASSOCIATED | 1.00 | A and C both reported collision_002 at 6.60 s (peak impulse 839.68 vs 839.68 N*s)<br>tracked for 6.60 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 1.2 m -> 0.0 m over the last 1.0 s<br>track motion compatible with C's own speed in the observed direction (3 sigma; full-speed RMSE 0.03 m/s for reference)<br>clearance at the contact 0.00 m<br>the only track of A compatible with the contact<br>collision_001 with B at 5.55 s: not compatible (track motion contradicts B's own speed in the observed direction (3 sigma; full-speed RMSE 3.46 m/s for reference)) |
| B:track_001 | A | ASSOCIATED | 0.98 | B and A both reported collision_001 (peak impulse 4243.51 vs 4243.51 N*s)<br>tracked for 5.55 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 4.3 m -> 0.1 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 0.31 m/s for reference)<br>clearance at the contact 0.07 m<br>the only track of B compatible with the contact |
| B:track_002 | C | ASSOCIATED | 1.00 | B and A both reported collision_001 (peak impulse 4243.51 vs 4243.51 N*s)<br>tracked for 5.55 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 9.1 m -> 6.1 m over the last 1.0 s<br>track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 2.32 m/s for reference)<br>clearance at the contact 6.09 m (beyond 3.50 m: confidence factor 0.69)<br>common frame: its returns lie on C's own footprint (median 0.00 m, 0.00 sigma of the relative uncertainty, over 122 samples; 100% within 3 sigma) at C's own velocity |
| C:track_001 | A | ASSOCIATED | 1.00 | C and A both reported collision_002 (peak impulse 839.68 vs 839.68 N*s)<br>tracked for 3.95 s before the matched collision<br>continuous up to the contact: last observed 0.15 s before it (window 1.00 s)<br>approaching before the contact: clearance 2.2 m -> 1.0 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 0.09 m/s for reference)<br>clearance at the contact 1.04 m<br>the only track of C compatible with the contact |

## Road users in the common frame

- B:track_002 is C: its returns lie on C's own footprint (median 0.00 m over 122 samples, 100% within 3 sigma) at C's velocity.

## Global graph

49 nodes, 104 edges; 10 merged node(s): g10 CLOSING_START(A,C) from A:e04 + A:e07, g11 CLOSING_START(B,C) from B:e05 + B:e13, g12 CRITICAL_TTC_START(B,A) from B:e06 + B:e11, g13 TRACK_APPEARED_RIGHT(C,A) from C:e03 + C:e08, g14 CLOSING_START(C,A) from C:e04 + C:e05, g17 CLOSING_START(B,A) from B:e07 + B:e12, g24 COLLISION(A,B) from A:e10 + B:e10, g28 CLOSING_START(A,C) from A:e13 + A:e19, g30 CRITICAL_TTC_START(A,C) from A:e14 + A:e18, g39 COLLISION(A,C) from A:e17 + C:e09.

### Event sequence (global time)

- `-5.55` MOVING_START(A); MOVING_START(B); MOVING_START(C); THROTTLE_START(A); THROTTLE_START(B); THROTTLE_START(C); TRACK_APPEARED_FRONT(B,A); TRACK_APPEARED_LEFT(A,C); TRACK_APPEARED_LEFT(B,C); CLOSING_START(A,C); CLOSING_START(B,C)
- `-5.05` CRITICAL_TTC_START(B,A)
- `-2.90` TRACK_APPEARED_RIGHT(C,A); CLOSING_START(C,A)
- `-1.60` THROTTLE_END(A); BRAKE_START(A)
- `-1.45` CLOSING_START(B,A)
- `-1.20` CLOSING_END(C,A)
- `-1.15` CLOSING_END(A,C)
- `-1.00` BRAKE_END(A)
- `-0.90` THROTTLE_START(A)
- `-0.15` THROTTLE_END(B); BRAKE_START(B)
- `+0.00` COLLISION(A,B); CRITICAL_TTC_END(B,A); THROTTLE_END(A); BRAKE_START(A); CLOSING_START(A,C); CLOSING_START(C,A); CRITICAL_TTC_START(A,C); CRITICAL_TTC_START(C,A)
- `+0.05` CLOSING_END(B,A); BRAKE_END(A)
- `+0.25` CLOSING_END(B,C)
- `+0.35` EGO_PATH_ENTRY(A,C)
- `+0.65` MOVING_END(B); STOP_START(B)
- `+0.90` TRACK_LOST(C,A)
- `+1.05` COLLISION(A,C); CRITICAL_TTC_END(A,C); CRITICAL_TTC_END(C,A); CLOSING_END(A,C)
- `+1.10` THROTTLE_END(C); BRAKE_START(C)
- `+1.90` MOVING_END(A); MOVING_END(C); STOP_START(A); STOP_START(C); BRAKE_START(A)

### What happened, in plain language

- 5.55 s before the reference collision, A started moving (already the case when first observed).
- 5.55 s before the reference collision, B started moving (already the case when first observed).
- 5.55 s before the reference collision, C started moving (already the case when first observed).
- 5.55 s before the reference collision, A pressed the accelerator (already the case when first observed).
- 5.55 s before the reference collision, B pressed the accelerator (already the case when first observed).
- 5.55 s before the reference collision, C pressed the accelerator (already the case when first observed).
- 5.55 s before the reference collision, B's radar started tracking A, which appeared in front of it.
- 5.55 s before the reference collision, A's radar started tracking C, which appeared on its left.
- 5.55 s before the reference collision, B's radar started tracking C, which appeared on its left.
- 5.55 s before the reference collision, A observed C start closing in (already the case when first observed).
- 5.55 s before the reference collision, B observed C start closing in (already the case when first observed).
- 5.05 s before the reference collision, B's time-to-contact with A became critical.
- 2.90 s before the reference collision, C's radar started tracking A, which appeared on its right.
- 2.90 s before the reference collision, C observed A start closing in (already the case when first observed).
- 1.60 s before the reference collision, A released the accelerator.
- 1.60 s before the reference collision, A started braking.
- 1.45 s before the reference collision, B observed A start closing in.
- 1.20 s before the reference collision, C observed A stop closing in.
- 1.15 s before the reference collision, A observed C stop closing in.
- 1.00 s before the reference collision, A released the brake.
- 0.90 s before the reference collision, A pressed the accelerator.
- 0.15 s before the reference collision, B released the accelerator.
- 0.15 s before the reference collision, B started braking.
- At the reference collision, A and B both recorded this same collision (peak impulses A: 4244, B: 4244 N*s).
- At the reference collision, B's time-to-contact with A stopped being critical.
- At the reference collision, A released the accelerator.
- At the reference collision, A started braking.
- At the reference collision, A observed C start closing in.
- At the reference collision, C observed A start closing in.
- At the reference collision, A's time-to-contact with C became critical.
- At the reference collision, C's time-to-contact with A became critical.
- 0.05 s after the reference collision, B observed A stop closing in.
- 0.05 s after the reference collision, A released the brake.
- 0.25 s after the reference collision, B observed C stop closing in.
- 0.35 s after the reference collision, A observed C enter its forward path corridor.
- 0.65 s after the reference collision, B stopped moving.
- 0.65 s after the reference collision, B came to a stop.
- 0.90 s after the reference collision, C's radar lost A (its states are UNKNOWN from then on, not ended).
- 1.05 s after the reference collision, A and C both recorded this same collision (peak impulses A: 840, C: 840 N*s).
- 1.05 s after the reference collision, A's time-to-contact with C stopped being critical.
- 1.05 s after the reference collision, C's time-to-contact with A stopped being critical.
- 1.05 s after the reference collision, A observed C stop closing in.
- 1.10 s after the reference collision, C released the accelerator.
- 1.10 s after the reference collision, C started braking.
- 1.90 s after the reference collision, A stopped moving.
- 1.90 s after the reference collision, C stopped moving.
- 1.90 s after the reference collision, A came to a stop.
- 1.90 s after the reference collision, C came to a stop.
- 1.90 s after the reference collision, A started braking.

### Temporal safety relations

CUT_IN_START < CRITICAL_TTC_START < COLLISION, or CRITICAL_TTC_START <= CUT_IN_START (critical TTC already active), and EGO_PATH_ENTRY before/after the critical TTC. Temporal order only, not causes.

- A's track_001 (C): CRITICAL_TTC_START 5.55, COLLISION with C 6.60 (+1.05 s); EGO_PATH_ENTRY 5.90 after critical TTC (+0.35 s) [local times; t_global: critical_ttc_start +0.00, ego_path_entry +0.35, collision +1.05]
- B's track_001 (A): CRITICAL_TTC_START 0.50, COLLISION with A 5.55 (+5.05 s) [local times; t_global: critical_ttc_start -5.05, collision +0.00]
- C's track_001 (A): CRITICAL_TTC_START 5.55, COLLISION with A 6.60 (+1.05 s) [local times; t_global: critical_ttc_start +0.00, collision +1.05]

### Simultaneous events (order unresolved at 0.05 s)

- MOVING_START(A); MOVING_START(B); MOVING_START(C); THROTTLE_START(A); THROTTLE_START(B); THROTTLE_START(C); TRACK_APPEARED_FRONT(B,A); TRACK_APPEARED_LEFT(A,C); TRACK_APPEARED_LEFT(B,C); CLOSING_START(A,C); CLOSING_START(B,C)
- TRACK_APPEARED_RIGHT(C,A); CLOSING_START(C,A)
- THROTTLE_END(A); BRAKE_START(A)
- THROTTLE_END(B); BRAKE_START(B)
- COLLISION(A,B); CRITICAL_TTC_END(B,A); THROTTLE_END(A); BRAKE_START(A); CLOSING_START(A,C); CLOSING_START(C,A); CRITICAL_TTC_START(A,C); CRITICAL_TTC_START(C,A)
- CLOSING_END(B,A); BRAKE_END(A)
- MOVING_END(B); STOP_START(B)
- COLLISION(A,C); CRITICAL_TTC_END(A,C); CRITICAL_TTC_END(C,A); CLOSING_END(A,C)
- THROTTLE_END(C); BRAKE_START(C)
- MOVING_END(A); MOVING_END(C); STOP_START(A); STOP_START(C); BRAKE_START(A)

### States still active when observation ended

A:
- EGO_PATH of track_001, since A:e16 (t = 5.90 s)
- STOP, since A:e21 (t = 7.45 s)
- BRAKE, since A:e22 (t = 7.45 s)
B:
- BRAKE, since B:e09 (t = 5.40 s)
- STOP, since B:e15 (t = 6.20 s)
C:
- CLOSING of track_001, since C:e06 (t = 5.55 s); the track was lost at 6.45 s
- CRITICAL_TTC of track_001, since C:e07 (t = 5.55 s); the track was lost at 6.45 s
- BRAKE, since C:e11 (t = 6.65 s)
- STOP, since C:e13 (t = 7.45 s)

### Sign detection windows

A:
- none
B:
- none
C:
- none

### Perceived state just before each collision report

- A A:e10 at 5.55 s (local): ego: MOVING, THROTTLE; track_001: no active state
- A A:e17 at 6.60 s (local): ego: MOVING; track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH
- B B:e10 at 5.55 s (local): ego: MOVING, BRAKE; track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH; track_002: CLOSING
- C C:e09 at 6.60 s (local): ego: MOVING, THROTTLE; track lost, states UNKNOWN: track_001

### Tracks lost while a state was active

A lost track's states become UNKNOWN: the recorder can no longer tell whether they ended.

A:
- no track was lost
B:
- no track was lost
C:
- track_001 at 6.45 s (C:e08): CLOSING, CRITICAL_TTC were true; they are UNKNOWN afterwards (no END recorded)

## Uncertainty and limitations

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
