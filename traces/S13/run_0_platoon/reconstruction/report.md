# Reconstruction report - S13/run_0_platoon

Inputs: `vehicles/A/`, `vehicles/B/` (vehicle-local files) and the supplied `incident_context.json`. `ground_truth/` and the run's `metadata.json` were not read; the privileged comparison, if run, is in `evaluation/`.

Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.

Pipeline: raw log -> local trace -> local graph (each recorder alone, own clock, own frame) -> graph-level alignment -> identity association -> road users in the common frame of the recorders' own pose streams -> global graph.

## Local reconstructions

| Recorder | Duration (local) | Trace frames | Graph nodes | Graph edges | Radar tracks | Collision reports (local time) |
|----------|-----------------:|-------------:|------------:|------------:|-------------:|-------------------------------|
| A | 11.45 s | 116 | 19 | 33 | 3 | A:e09 @ 6.20 s |
| B | 11.45 s | 116 | 24 | 41 | 4 | B:e13 @ 6.20 s |

## Graph alignment

Reference event: `collision_001` (t_global = 0); `t_global = t_local + offset_to_global`. A graph that did not report it is aligned through the chain of matched collisions linking it to the reference (multi-hop); its anchor is its own report of the last collision of that chain.

| Graph | Status | Anchor node | Anchor local time | Offset to global | Note |
|-------|--------|-------------|------------------:|-----------------:|------|
| A | ALIGNED | A:e09 | 6.20 | -6.20 | reported the reference collision collision_001 |
| B | ALIGNED | B:e13 | 6.20 | -6.20 | reported the reference collision collision_001 |

Estimated relative clock offsets: B - A = +0.000 s

Matched `collision_001`: A and B both recorded a collision; peak impulses 1093.08 vs 1093.08 N*s (similarity 1.000, tolerance 0.10); no competing report within tolerance; the two bodies touch at their reports (0.00 m apart, tolerance 1.0 m); independent relative impulse std 0.100; combined z 0.000 (gate 3.0); engineering assumption; pre-contact radar view of each recorder checked against the candidate partner's own speed: not contradicted

## Identity associations

| Local track | Global entity | Status | Confidence | Evidence |
|-------------|---------------|--------|-----------:|----------|
| A:track_001 | B | ASSOCIATED | 0.99 | A and B both reported collision_001 (peak impulse 1093.08 vs 1093.08 N*s)<br>tracked for 6.20 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 1.7 m -> 0.2 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 0.17 m/s for reference)<br>clearance at the contact 0.23 m<br>the only track of A compatible with the contact |
| A:track_002 | U1 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 1093.08 vs 1093.08 N*s)<br>tracked for 5.40 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>not approaching before the contact: clearance 12.8 m -> 12.9 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 0.99 m/s for reference)<br>clearance at the contact 12.76 m (beyond 3.50 m: confidence factor 0.01)<br>anonymous road user U1: B:track_002, A:track_002 |
| A:track_003 | U2 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 1093.08 vs 1093.08 N*s)<br>tracked for 0.00 s before the matched collision (needs 1.00 s)<br>first seen 0.05 s after the matched collision<br>range trend before the contact not measurable<br>speed not comparable with B's own speed before the collision<br>anonymous road user U2: B:track_003, A:track_003, B:track_004 |
| B:track_001 | A | ASSOCIATED | 1.00 | B and A both reported collision_001 (peak impulse 1093.08 vs 1093.08 N*s)<br>tracked for 6.20 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 1.7 m -> 0.3 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 0.13 m/s for reference)<br>clearance at the contact 0.34 m<br>the only compatible track of B touching it at the contact (clearance 0.34 m; track_002 at 14.01 m) |
| B:track_002 | U1 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 1093.08 vs 1093.08 N*s)<br>tracked for 6.20 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 14.7 m -> 14.0 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 0.11 m/s for reference)<br>clearance at the contact 14.01 m (beyond 3.50 m: confidence factor 0.00)<br>ambiguous: 2 persistent tracks of B are compatible with the contact (track_001, track_002)<br>anonymous road user U1: B:track_002, A:track_002 |
| B:track_003 | U2 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 1093.08 vs 1093.08 N*s)<br>tracked for 6.20 s before the matched collision<br>lost 1.65 s before the matched collision (window 1.00 s)<br>approaching before the contact: clearance 25.4 m -> 24.5 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 0.06 m/s for reference)<br>retrospective: identity resolved from later evidence at +0.05 s (entity seen by several observers), carried back 1.70 s with the motion model; posterior 0.988 against 1 candidate(s) and a new road user; observation times unchanged<br>anonymous road user U2: B:track_003, A:track_003, B:track_004 |
| B:track_004 | U2 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 1093.08 vs 1093.08 N*s)<br>tracked for 0.00 s before the matched collision (needs 1.00 s)<br>first seen 0.30 s after the matched collision<br>range trend before the contact not measurable<br>speed not comparable with A's own speed before the collision<br>anonymous road user U2: B:track_003, A:track_003, B:track_004 |

## Road users in the common frame

- U1 (anonymous, -6.20 to 4.30 s): B:track_002, A:track_002 joined by same box A:track_002-B:track_002 (100% of 115 instants); footprint 4.60 x 1.90 m (prior/prior); fusion box_fit+covariance_intersection.
- U2 (anonymous, -6.20 to 3.35 s): B:track_003, A:track_003, B:track_004 joined by same box A:track_003-B:track_004 (100% of 12 instants); footprint 4.60 x 1.90 m (prior/prior); fusion box_fit+covariance_intersection.

## Global graph

42 nodes, 83 edges; 13 merged node(s): g07 TRACK_APPEARED_RIGHT(B,U1) from B:e04 + B:e24, g08 TRACK_APPEARED_RIGHT(B,U2) from B:e05 + B:e08, g09 CLOSING_START(B,U1) from B:e06 + B:e17, g11 TRACK_APPEARED_FRONT(A,U1) from A:e04 + A:e19, g12 CRITICAL_TTC_START(A,U1) from A:e05 + A:e08, g14 CRITICAL_TTC_START(A,B) from A:e06 + A:e10, g15 CUT_IN_FROM_RIGHT_START(B,A) from B:e09 + B:e20, g16 CRITICAL_TTC_START(B,A) from B:e10 + B:e14, g17 CLOSING_START(A,B) from A:e07 + A:e15, g18 CLOSING_START(B,A) from B:e11 + B:e18, g21 COLLISION(A,B) from A:e09 + B:e13, g28 TRACK_APPEARED_RIGHT(A,U2) from A:e13 + A:e18, g33 TRACK_APPEARED_RIGHT(B,U2) from B:e19 + B:e23.

### Event sequence (global time)

- `-6.20` MOVING_START(A); MOVING_START(B); THROTTLE_START(A); THROTTLE_START(B); TRACK_APPEARED_LEFT(A,B); TRACK_APPEARED_RIGHT(B,A); TRACK_APPEARED_RIGHT(B,U1); TRACK_APPEARED_RIGHT(B,U2); CLOSING_START(B,U1); CLOSING_START(B,U2)
- `-5.40` TRACK_APPEARED_FRONT(A,U1)
- `-4.90` CRITICAL_TTC_START(A,U1)
- `-1.65` TRACK_LOST(B,U2)
- `-1.00` CRITICAL_TTC_START(A,B)
- `-0.90` CUT_IN_FROM_RIGHT_START(B,A)
- `-0.75` CRITICAL_TTC_START(B,A)
- `-0.70` CLOSING_START(A,B)
- `-0.65` CLOSING_START(B,A)
- `-0.35` CRITICAL_TTC_END(A,U1)
- `-0.25` EGO_PATH_ENTRY(B,A)
- `+0.00` COLLISION(A,B); CRITICAL_TTC_END(A,B); CRITICAL_TTC_END(B,A)
- `+0.05` THROTTLE_END(A); THROTTLE_END(B); BRAKE_START(A); BRAKE_START(B); TRACK_APPEARED_RIGHT(A,U2)
- `+0.10` EGO_PATH_ENTRY(A,B)
- `+0.15` CLOSING_END(A,B); CLOSING_END(B,U1)
- `+0.20` CLOSING_END(B,A)
- `+0.30` TRACK_APPEARED_RIGHT(B,U2)
- `+1.05` CUT_IN_FROM_RIGHT_END(B,A); MOVING_END(B); STOP_START(B)
- `+1.15` MOVING_END(A); STOP_START(A)
- `+2.35` TRACK_LOST(B,U2)
- `+2.90` TRACK_LOST(B,U1)
- `+3.35` TRACK_LOST(A,U2)
- `+4.30` TRACK_LOST(A,U1)

### What happened, in plain language

- 6.20 s before the reference collision, A started moving (already the case when first observed).
- 6.20 s before the reference collision, B started moving (already the case when first observed).
- 6.20 s before the reference collision, A pressed the accelerator (already the case when first observed).
- 6.20 s before the reference collision, B pressed the accelerator (already the case when first observed).
- 6.20 s before the reference collision, A's radar started tracking B, which appeared on its left.
- 6.20 s before the reference collision, B's radar started tracking A, which appeared on its right.
- 6.20 s before the reference collision, B's radar started tracking anonymous road user U1, which appeared on its right.
- 6.20 s before the reference collision, B's radar started tracking anonymous road user U2, which appeared on its right.
- 6.20 s before the reference collision, B observed anonymous road user U1 start closing in (already the case when first observed).
- 6.20 s before the reference collision, B observed anonymous road user U2 start closing in (already the case when first observed).
- 5.40 s before the reference collision, A's radar started tracking anonymous road user U1, which appeared in front of it.
- 4.90 s before the reference collision, A's time-to-contact with anonymous road user U1 became critical.
- 1.65 s before the reference collision, B's radar lost anonymous road user U2 (its states are UNKNOWN from then on, not ended).
- 1.00 s before the reference collision, A's time-to-contact with B became critical.
- 0.90 s before the reference collision, B observed A cutting in from the right.
- 0.75 s before the reference collision, B's time-to-contact with A became critical.
- 0.70 s before the reference collision, A observed B start closing in.
- 0.65 s before the reference collision, B observed A start closing in.
- 0.35 s before the reference collision, A's time-to-contact with anonymous road user U1 stopped being critical.
- 0.25 s before the reference collision, B observed A enter its forward path corridor.
- At the reference collision, A and B both recorded this same collision (peak impulses A: 1093, B: 1093 N*s).
- At the reference collision, A's time-to-contact with B stopped being critical.
- At the reference collision, B's time-to-contact with A stopped being critical.
- 0.05 s after the reference collision, A released the accelerator.
- 0.05 s after the reference collision, B released the accelerator.
- 0.05 s after the reference collision, A started braking.
- 0.05 s after the reference collision, B started braking.
- 0.05 s after the reference collision, A's radar started tracking anonymous road user U2, which appeared on its right.
- 0.10 s after the reference collision, A observed B enter its forward path corridor.
- 0.15 s after the reference collision, A observed B stop closing in.
- 0.15 s after the reference collision, B observed anonymous road user U1 stop closing in.
- 0.20 s after the reference collision, B observed A stop closing in.
- 0.30 s after the reference collision, B's radar started tracking anonymous road user U2, which appeared on its right.
- 1.05 s after the reference collision, B observed A's cut-in from the right settle.
- 1.05 s after the reference collision, B stopped moving.
- 1.05 s after the reference collision, B came to a stop.
- 1.15 s after the reference collision, A stopped moving.
- 1.15 s after the reference collision, A came to a stop.
- 2.35 s after the reference collision, B's radar lost anonymous road user U2 (its states are UNKNOWN from then on, not ended).
- 2.90 s after the reference collision, B's radar lost anonymous road user U1 (its states are UNKNOWN from then on, not ended).
- 3.35 s after the reference collision, A's radar lost anonymous road user U2 (its states are UNKNOWN from then on, not ended).
- 4.30 s after the reference collision, A's radar lost anonymous road user U1 (its states are UNKNOWN from then on, not ended).

### Temporal safety relations

CUT_IN_START < CRITICAL_TTC_START < COLLISION, or CRITICAL_TTC_START <= CUT_IN_START (critical TTC already active), and EGO_PATH_ENTRY before/after the critical TTC. Temporal order only, not causes.

- A's track_001 (B): CRITICAL_TTC_START 5.20, COLLISION with B 6.20 (+1.00 s); EGO_PATH_ENTRY 6.30 after critical TTC (+1.10 s) [local times; t_global: critical_ttc_start -1.00, ego_path_entry +0.10, collision +0.00]
- A's track_002 (unidentified U1): CRITICAL_TTC_START 1.30, COLLISION 6.20 (+4.90 s) [local times; t_global: critical_ttc_start -4.90, collision +0.00]
- B's track_001 (A): cut-in started before critical TTC: CUT_IN_FROM_RIGHT_START 5.30 < CRITICAL_TTC_START 5.45 (+0.15 s) < COLLISION with A 6.20 (+0.75 s); EGO_PATH_ENTRY 5.95 after critical TTC (+0.50 s) [local times; t_global: cut_in -0.90, critical_ttc_start -0.75, ego_path_entry -0.25, collision +0.00]

### Simultaneous events (order unresolved at 0.05 s)

- MOVING_START(A); MOVING_START(B); THROTTLE_START(A); THROTTLE_START(B); TRACK_APPEARED_LEFT(A,B); TRACK_APPEARED_RIGHT(B,A); TRACK_APPEARED_RIGHT(B,U1); TRACK_APPEARED_RIGHT(B,U2); CLOSING_START(B,U1); CLOSING_START(B,U2)
- COLLISION(A,B); CRITICAL_TTC_END(A,B); CRITICAL_TTC_END(B,A)
- THROTTLE_END(A); THROTTLE_END(B); BRAKE_START(A); BRAKE_START(B); TRACK_APPEARED_RIGHT(A,U2)
- CLOSING_END(A,B); CLOSING_END(B,U1)
- CUT_IN_FROM_RIGHT_END(B,A); MOVING_END(B); STOP_START(B)
- MOVING_END(A); STOP_START(A)

### States still active when observation ended

A:
- BRAKE, since A:e12 (t = 6.25 s)
- EGO_PATH of track_001, since A:e14 (t = 6.30 s)
- STOP, since A:e17 (t = 7.35 s)
B:
- CLOSING of track_003, since B:e07 (t = 0.00 s); the track was lost at 4.55 s
- EGO_PATH of track_001, since B:e12 (t = 5.95 s)
- BRAKE, since B:e16 (t = 6.25 s)
- STOP, since B:e22 (t = 7.25 s)

### Sign detection windows

A:
- none
B:
- none

### Perceived state just before each collision report

- A A:e09 at 6.20 s (local): ego: MOVING, THROTTLE; track_001: CLOSING, CRITICAL_TTC; track_002: IN_EGO_PATH
- B B:e13 at 6.20 s (local): ego: MOVING, THROTTLE; track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH, CUT_IN_FROM_RIGHT; track_002: CLOSING; track lost, states UNKNOWN: track_003

### Tracks lost while a state was active

A lost track's states become UNKNOWN: the recorder can no longer tell whether they ended.

A:
- track_003 at 9.55 s (A:e18): IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)
- track_002 at 10.50 s (A:e19): IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)
B:
- track_003 at 4.55 s (B:e08): CLOSING were true; they are UNKNOWN afterwards (no END recorded)
- lost with no state active: track_004, track_002

## Uncertainty and limitations

- A:track_002 stays anonymous (U1): not approaching before the contact: clearance 12.8 m -> 12.9 m over the last 1.0 s.
- A:track_003 stays anonymous (U2): tracked for 0.00 s before the matched collision (needs 1.00 s); first seen 0.05 s after the matched collision; range trend before the contact not measurable; speed not comparable with B's own speed before the collision.
- B:track_002 stays anonymous (U1): ambiguous: 2 persistent tracks of B are compatible with the contact (track_001, track_002).
- B:track_003 stays anonymous (U2): lost 1.65 s before the matched collision (window 1.00 s).
- B:track_004 stays anonymous (U2): tracked for 0.00 s before the matched collision (needs 1.00 s); first seen 0.30 s after the matched collision; range trend before the contact not measurable; speed not comparable with A's own speed before the collision.
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
