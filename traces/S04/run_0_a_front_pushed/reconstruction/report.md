# Reconstruction report - S04/run_0_a_front_pushed

Inputs: `vehicles/A/`, `vehicles/B/`, `vehicles/C/` (vehicle-local files) and the supplied `incident_context.json`. `ground_truth/` and the run's `metadata.json` were not read; the privileged comparison, if run, is in `evaluation/`.

Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.

Pipeline: raw log -> local trace -> local graph (each recorder alone, own clock, own frame) -> graph-level alignment -> identity association -> road users in the common frame of the recorders' own pose streams -> global graph.

## Local reconstructions

| Recorder | Duration (local) | Trace frames | Graph nodes | Graph edges | Radar tracks | Collision reports (local time) |
|----------|-----------------:|-------------:|------------:|------------:|-------------:|-------------------------------|
| A | 13.70 s | 138 | 13 | 24 | 1 | A:e08 @ 4.80 s, A:e13 @ 5.45 s |
| B | 13.70 s | 138 | 15 | 25 | 1 | B:e08 @ 4.80 s, B:e10 @ 5.30 s |
| C | 13.70 s | 138 | 7 | 10 | 0 | C:e07 @ 5.30 s |

## Graph alignment

Reference event: `collision_001` (t_global = 0); `t_global = t_local + offset_to_global`. A graph that did not report it is aligned through the chain of matched collisions linking it to the reference (multi-hop); its anchor is its own report of the last collision of that chain.

| Graph | Status | Anchor node | Anchor local time | Offset to global | Note |
|-------|--------|-------------|------------------:|-----------------:|------|
| A | ALIGNED | A:e08 | 4.80 | -4.80 | reported the reference collision collision_001 |
| B | ALIGNED | B:e08 | 4.80 | -4.80 | reported the reference collision collision_001 |
| C | ALIGNED | C:e07 | 5.30 | -4.80 | shares collision_003 with B, aligned through collision_001 -> collision_003 |

Estimated relative clock offsets: B - A = +0.000 s, C - A = +0.000 s, C - B = +0.000 s

Matched `collision_001`: A and B both recorded a collision; peak impulses 10281.41 vs 10281.41 N*s (similarity 1.000, tolerance 0.10); 1 competing report(s) within tolerance; best match kept; the two bodies touch at their reports (0.00 m apart, tolerance 1.0 m); independent relative impulse std 0.100; combined z 0.000 (gate 3.0); engineering assumption; pre-contact radar view of each recorder checked against the candidate partner's own speed: not contradicted

Matched `collision_002`: A recorded a collision; B recorded the same impulse as a burst within its contact B:e10, merged there by its own sensor; peak impulses 1509.76 vs 1509.76 N*s (similarity 1.000, tolerance 0.10); consistent with the clock offset between A and B that earlier matches fix (+0.000 s, tolerance 0.10 s); pre-contact radar view of each recorder checked against the candidate partner's own speed: not contradicted

Matched `collision_003`: B and C both recorded a collision; peak impulses 8788.05 vs 8788.05 N*s (similarity 1.000, tolerance 0.10); 1 competing report(s) within tolerance; best match kept; the two bodies touch at their reports (0.00 m apart, tolerance 1.0 m); independent relative impulse std 0.100; combined z 0.000 (gate 3.0); engineering assumption; pre-contact radar view of each recorder checked against the candidate partner's own speed: not contradicted

## Identity associations

| Local track | Global entity | Status | Confidence | Evidence |
|-------------|---------------|--------|-----------:|----------|
| A:track_001 | B | ASSOCIATED | 0.99 | A and B both reported collision_001 at 4.80 s (peak impulse 10281.41 vs 10281.41 N*s)<br>tracked for 4.80 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 4.5 m -> 0.0 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 0.18 m/s for reference)<br>clearance at the contact 0.00 m<br>the only track of A compatible with the contact<br>collision_002 with B at 5.45 s: also compatible |
| B:track_001 | C | ASSOCIATED | 0.99 | B and C both reported collision_003 at 5.30 s (peak impulse 8788.05 vs 8788.05 N*s)<br>tracked for 5.30 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 6.4 m -> 0.1 m over the last 1.0 s<br>track motion compatible with C's own speed in the observed direction (3 sigma; full-speed RMSE 0.17 m/s for reference)<br>clearance at the contact 0.06 m<br>the only track of B compatible with the contact<br>collision_001 with A at 4.80 s: not compatible (track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 7.54 m/s for reference))<br>collision_002 with A at 5.45 s: not compatible (track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 7.90 m/s for reference)) |

## Road users in the common frame

- no anonymous track of an aligned recorder

## Global graph

32 nodes, 64 edges; 6 merged node(s): g09 CRITICAL_TTC_START(A,B) from A:e04 + A:e09, g10 CRITICAL_TTC_START(B,C) from B:e04 + B:e11, g13 CLOSING_START(B,C) from B:e05 + B:e12, g16 CLOSING_START(A,B) from A:e05 + A:e10, g21 COLLISION(A,B) from A:e08 + B:e08, g25 COLLISION(B,C) from B:e10 + C:e07.

### Event sequence (global time)

- `-4.80` MOVING_START(A); MOVING_START(B); MOVING_START(C); THROTTLE_START(A); THROTTLE_START(B); THROTTLE_START(C); TRACK_APPEARED_FRONT(A,B); TRACK_APPEARED_FRONT(B,C)
- `-4.30` CRITICAL_TTC_START(A,B); CRITICAL_TTC_START(B,C)
- `-1.85` THROTTLE_END(C); BRAKE_START(C)
- `-1.60` CLOSING_START(B,C)
- `-1.10` THROTTLE_END(B); BRAKE_START(B)
- `-0.90` CLOSING_START(A,B)
- `-0.75` MOVING_END(C); STOP_START(C)
- `-0.25` THROTTLE_END(A); BRAKE_START(A)
- `+0.00` COLLISION(A,B); CRITICAL_TTC_END(A,B); CLOSING_END(A,B)
- `+0.05` BRAKE_END(B)
- `+0.50` COLLISION(B,C); CRITICAL_TTC_END(B,C); CLOSING_END(B,C)
- `+0.55` MOVING_END(A); STOP_START(A)
- `+0.65` MOVING_END(B); STOP_START(B); BRAKE_START(B)

### What happened, in plain language

- 4.80 s before the reference collision, A started moving (already the case when first observed).
- 4.80 s before the reference collision, B started moving (already the case when first observed).
- 4.80 s before the reference collision, C started moving (already the case when first observed).
- 4.80 s before the reference collision, A pressed the accelerator (already the case when first observed).
- 4.80 s before the reference collision, B pressed the accelerator (already the case when first observed).
- 4.80 s before the reference collision, C pressed the accelerator (already the case when first observed).
- 4.80 s before the reference collision, A's radar started tracking B, which appeared in front of it.
- 4.80 s before the reference collision, B's radar started tracking C, which appeared in front of it.
- 4.30 s before the reference collision, A's time-to-contact with B became critical.
- 4.30 s before the reference collision, B's time-to-contact with C became critical.
- 1.85 s before the reference collision, C released the accelerator.
- 1.85 s before the reference collision, C started braking.
- 1.60 s before the reference collision, B observed C start closing in.
- 1.10 s before the reference collision, B released the accelerator.
- 1.10 s before the reference collision, B started braking.
- 0.90 s before the reference collision, A observed B start closing in.
- 0.75 s before the reference collision, C stopped moving.
- 0.75 s before the reference collision, C came to a stop.
- 0.25 s before the reference collision, A released the accelerator.
- 0.25 s before the reference collision, A started braking.
- At the reference collision, A and B both recorded this same collision (peak impulses A: 10281, B: 10281 N*s).
- At the reference collision, A's time-to-contact with B stopped being critical.
- At the reference collision, A observed B stop closing in.
- 0.05 s after the reference collision, B released the brake.
- 0.50 s after the reference collision, B and C both recorded this same collision (peak impulses B: 8788, C: 8788 N*s).
- 0.50 s after the reference collision, B's time-to-contact with C stopped being critical.
- 0.50 s after the reference collision, B observed C stop closing in.
- 0.55 s after the reference collision, A stopped moving.
- 0.55 s after the reference collision, A came to a stop.
- 0.65 s after the reference collision, B stopped moving.
- 0.65 s after the reference collision, B came to a stop.
- 0.65 s after the reference collision, B started braking.

### Temporal safety relations

CUT_IN_START < CRITICAL_TTC_START < COLLISION, or CRITICAL_TTC_START <= CUT_IN_START (critical TTC already active), and EGO_PATH_ENTRY before/after the critical TTC. Temporal order only, not causes.

- A's track_001 (B): CRITICAL_TTC_START 0.50, COLLISION with B 4.80 (+4.30 s) [local times; t_global: critical_ttc_start -4.30, collision +0.00]
- B's track_001 (C): CRITICAL_TTC_START 0.50, COLLISION with C 5.30 (+4.80 s) [local times; t_global: critical_ttc_start -4.30, collision +0.50]

### Simultaneous events (order unresolved at 0.05 s)

- MOVING_START(A); MOVING_START(B); MOVING_START(C); THROTTLE_START(A); THROTTLE_START(B); THROTTLE_START(C); TRACK_APPEARED_FRONT(A,B); TRACK_APPEARED_FRONT(B,C)
- CRITICAL_TTC_START(A,B); CRITICAL_TTC_START(B,C)
- THROTTLE_END(C); BRAKE_START(C)
- THROTTLE_END(B); BRAKE_START(B)
- MOVING_END(C); STOP_START(C)
- THROTTLE_END(A); BRAKE_START(A)
- COLLISION(A,B); CRITICAL_TTC_END(A,B); CLOSING_END(A,B)
- COLLISION(B,C); CRITICAL_TTC_END(B,C); CLOSING_END(B,C)
- MOVING_END(A); STOP_START(A)
- MOVING_END(B); STOP_START(B); BRAKE_START(B)

### States still active when observation ended

A:
- BRAKE, since A:e07 (t = 4.55 s)
- STOP, since A:e12 (t = 5.35 s)
B:
- STOP, since B:e14 (t = 5.45 s)
- BRAKE, since B:e15 (t = 5.45 s)
C:
- BRAKE, since C:e04 (t = 2.95 s)
- STOP, since C:e06 (t = 4.05 s)

### Sign detection windows

A:
- none
B:
- none
C:
- none

### Perceived state just before each collision report

- A A:e08 at 4.80 s (local): ego: MOVING, BRAKE; track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH
- A A:e13 at 5.45 s (local): ego: STOP, BRAKE; track_001: IN_EGO_PATH
- B B:e08 at 4.80 s (local): ego: MOVING, BRAKE; track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH
- B B:e10 at 5.30 s (local): ego: MOVING; track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH
- C C:e07 at 5.30 s (local): ego: STOP, BRAKE

### Tracks lost while a state was active

A lost track's states become UNKNOWN: the recorder can no longer tell whether they ended.

A:
- no track was lost
B:
- no track was lost
C:
- no track was lost

## Uncertainty and limitations

- C built no radar track: nothing moving stayed in its radar view long enough, so C has no perception of the others.
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
