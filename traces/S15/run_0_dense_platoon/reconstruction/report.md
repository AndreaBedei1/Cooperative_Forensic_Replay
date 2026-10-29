# Reconstruction report - S15/run_0_dense_platoon

Inputs: `vehicles/A/`, `vehicles/B/` (vehicle-local files) and the supplied `incident_context.json`. `ground_truth/` and the run's `metadata.json` were not read; the privileged comparison, if run, is in `evaluation/`.

Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.

Pipeline: raw log -> local trace -> local graph (each recorder alone, own clock, own frame) -> graph-level alignment -> identity association -> road users in the common frame of the recorders' own pose streams -> global graph.

## Local reconstructions

| Recorder | Duration (local) | Trace frames | Graph nodes | Graph edges | Radar tracks | Collision reports (local time) |
|----------|-----------------:|-------------:|------------:|------------:|-------------:|-------------------------------|
| A | 11.95 s | 121 | 31 | 44 | 10 | A:e20 @ 7.45 s |
| B | 11.95 s | 121 | 25 | 45 | 9 | B:e20 @ 7.45 s |

## Graph alignment

Reference event: `collision_001` (t_global = 0); `t_global = t_local + offset_to_global`. A graph that did not report it is aligned through the chain of matched collisions linking it to the reference (multi-hop); its anchor is its own report of the last collision of that chain.

| Graph | Status | Anchor node | Anchor local time | Offset to global | Note |
|-------|--------|-------------|------------------:|-----------------:|------|
| A | ALIGNED | A:e20 | 7.45 | -7.45 | reported the reference collision collision_001 |
| B | ALIGNED | B:e20 | 7.45 | -7.45 | reported the reference collision collision_001 |

Estimated relative clock offsets: B - A = +0.000 s

Matched `collision_001`: A and B both recorded a collision; peak impulses 34836.87 vs 34836.87 N*s (similarity 1.000, tolerance 0.10); no competing report within tolerance; the two bodies touch at their reports (0.00 m apart, tolerance 1.0 m); independent relative impulse std 0.100; combined z 0.000 (gate 3.0); engineering assumption; pre-contact radar view of each recorder checked against the candidate partner's own speed: not contradicted

## Identity associations

| Local track | Global entity | Status | Confidence | Evidence |
|-------------|---------------|--------|-----------:|----------|
| A:track_001 | U1 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 34836.87 vs 34836.87 N*s)<br>tracked for 7.45 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>not approaching before the contact: clearance 2.3 m -> 9.7 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 1.73 m/s for reference)<br>clearance at the contact 2.35 m<br>anonymous road user U1: A:track_001, B:track_005 |
| A:track_002 | U2 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 34836.87 vs 34836.87 N*s)<br>tracked for 7.45 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>not approaching before the contact: clearance 7.9 m -> 15.8 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 1.74 m/s for reference)<br>clearance at the contact 7.87 m (beyond 3.50 m: confidence factor 0.35)<br>anonymous road user U2: A:track_002 |
| A:track_003 | U3 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 34836.87 vs 34836.87 N*s)<br>tracked for 7.45 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>not approaching before the contact: clearance 4.9 m -> 12.8 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 1.74 m/s for reference)<br>clearance at the contact 4.92 m (beyond 3.50 m: confidence factor 0.89)<br>anonymous road user U3: A:track_003, B:track_004 |
| A:track_004 | U4 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 34836.87 vs 34836.87 N*s)<br>tracked for 7.45 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>not approaching before the contact: clearance 16.6 m -> 24.4 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 1.76 m/s for reference)<br>clearance at the contact 16.63 m (beyond 3.50 m: confidence factor 0.00)<br>anonymous road user U4: A:track_004, B:track_006 |
| A:track_005 | U5 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 34836.87 vs 34836.87 N*s)<br>tracked for 7.45 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>not approaching before the contact: clearance 14.5 m -> 22.3 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 1.76 m/s for reference)<br>clearance at the contact 14.54 m (beyond 3.50 m: confidence factor 0.00)<br>anonymous road user U5: A:track_005, B:track_002, B:track_008 |
| A:track_006 | U6 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 34836.87 vs 34836.87 N*s)<br>tracked for 7.45 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 3.1 m -> 1.7 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 1.72 m/s for reference)<br>clearance at the contact 1.72 m<br>ambiguous: 2 persistent tracks of A are compatible with the contact (track_006, track_007)<br>anonymous road user U6: A:track_006, B:track_001 |
| A:track_007 | U7 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 34836.87 vs 34836.87 N*s)<br>tracked for 7.45 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 2.2 m -> 1.8 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 1.74 m/s for reference)<br>clearance at the contact 1.65 m<br>ambiguous: 2 persistent tracks of A are compatible with the contact (track_006, track_007)<br>anonymous road user U7: A:track_007, B:track_003 |
| A:track_008 | U9 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 34836.87 vs 34836.87 N*s)<br>tracked for 0.00 s before the matched collision (needs 1.00 s)<br>first seen 0.45 s after the matched collision<br>range trend before the contact not measurable<br>speed not comparable with B's own speed before the collision<br>anonymous road user U9: A:track_008 |
| A:track_009 | U10 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 34836.87 vs 34836.87 N*s)<br>tracked for 0.00 s before the matched collision (needs 1.00 s)<br>first seen 2.60 s after the matched collision<br>range trend before the contact not measurable<br>speed not comparable with B's own speed before the collision<br>anonymous road user U10: A:track_009 |
| A:track_010 | U11 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 34836.87 vs 34836.87 N*s)<br>tracked for 0.00 s before the matched collision (needs 1.00 s)<br>first seen 2.95 s after the matched collision<br>range trend before the contact not measurable<br>speed not comparable with B's own speed before the collision<br>anonymous road user U11: A:track_010 |
| B:track_001 | U6 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 34836.87 vs 34836.87 N*s)<br>tracked for 7.45 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>not approaching before the contact: clearance 2.4 m -> 2.7 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 5.14 m/s for reference)<br>clearance at the contact 2.40 m<br>anonymous road user U6: A:track_006, B:track_001 |
| B:track_002 | U5 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 34836.87 vs 34836.87 N*s)<br>tracked for 7.45 s before the matched collision<br>lost 3.75 s before the matched collision (window 1.00 s)<br>not approaching before the contact: clearance 25.7 m -> 25.9 m over the last 1.0 s<br>speed not comparable with A's own speed before the collision<br>anonymous road user U5: A:track_005, B:track_002, B:track_008 |
| B:track_003 | U7 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 34836.87 vs 34836.87 N*s)<br>tracked for 7.45 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>not approaching before the contact: clearance 3.2 m -> 3.6 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 5.15 m/s for reference)<br>clearance at the contact 3.14 m<br>anonymous road user U7: A:track_007, B:track_003 |
| B:track_004 | U3 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 34836.87 vs 34836.87 N*s)<br>tracked for 7.45 s before the matched collision<br>continuous up to the contact: last observed 0.05 s before it (window 1.00 s)<br>not approaching before the contact: clearance 16.7 m -> 16.9 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 4.76 m/s for reference)<br>clearance at the contact 16.67 m (beyond 3.50 m: confidence factor 0.00)<br>anonymous road user U3: A:track_003, B:track_004 |
| B:track_005 | U1 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 34836.87 vs 34836.87 N*s)<br>tracked for 7.45 s before the matched collision<br>continuous up to the contact: last observed 0.05 s before it (window 1.00 s)<br>not approaching before the contact: clearance 13.3 m -> 13.4 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 4.78 m/s for reference)<br>clearance at the contact 13.32 m (beyond 3.50 m: confidence factor 0.00)<br>anonymous road user U1: A:track_001, B:track_005 |
| B:track_006 | U4 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 34836.87 vs 34836.87 N*s)<br>tracked for 7.45 s before the matched collision<br>lost 3.90 s before the matched collision (window 1.00 s)<br>not approaching before the contact: clearance 27.8 m -> 27.9 m over the last 1.0 s<br>speed not comparable with A's own speed before the collision<br>anonymous road user U4: A:track_004, B:track_006 |
| B:track_007 | A | ASSOCIATED | 1.00 | B and A both reported collision_001 (peak impulse 34836.87 vs 34836.87 N*s)<br>tracked for 7.40 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 7.4 m -> 0.2 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 0.10 m/s for reference)<br>clearance at the contact 0.21 m<br>the only track of B compatible with the contact |
| B:track_008 | U5 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 34836.87 vs 34836.87 N*s)<br>tracked for 1.30 s before the matched collision<br>continuous up to the contact: last observed 0.70 s before it (window 1.00 s)<br>approaching before the contact: clearance 26.3 m -> 26.3 m over the last 1.0 s<br>track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 3.08 m/s for reference)<br>clearance at the contact 26.22 m (beyond 3.50 m: confidence factor 0.00)<br>anonymous road user U5: A:track_005, B:track_002, B:track_008 |
| B:track_009 | U8 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 34836.87 vs 34836.87 N*s)<br>tracked for 1.10 s before the matched collision<br>continuous up to the contact: last observed 0.85 s before it (window 1.00 s)<br>not approaching before the contact: clearance 28.1 m -> 28.3 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 2.71 m/s for reference)<br>clearance at the contact 28.17 m (beyond 3.50 m: confidence factor 0.00)<br>anonymous road user U8: B:track_009 |

## Road users in the common frame

- U1 (anonymous, -7.45 to 2.10 s): A:track_001, B:track_005 joined by same box A:track_001-B:track_005 (100% of 144 instants); footprint 4.60 x 1.90 m (prior/prior); fusion box_fit+covariance_intersection.
- U2 (anonymous, -7.45 to 4.40 s): A:track_002; footprint 4.60 x 1.90 m (prior/prior); fusion box_fit+covariance_intersection.
- U3 (anonymous, -7.45 to 4.45 s): A:track_003, B:track_004 joined by same box A:track_003-B:track_004 (100% of 129 instants); footprint 4.60 x 1.90 m (prior/prior); fusion box_fit+covariance_intersection.
- U4 (anonymous, -7.45 to 4.50 s): A:track_004, B:track_006 joined by same box A:track_004-B:track_006 (100% of 58 instants); footprint 4.60 x 1.90 m (prior/prior); fusion box_fit+covariance_intersection.
- U5 (anonymous, -7.45 to 1.50 s): A:track_005, B:track_002, B:track_008 joined by same box A:track_005-B:track_002 (100% of 67 instants); same box A:track_005-B:track_008 (100% of 10 instants); footprint 4.60 x 1.90 m (prior/prior); fusion box_fit+covariance_intersection.
- U6 (anonymous, -7.45 to 4.50 s): A:track_006, B:track_001 joined by same box A:track_006-B:track_001 (100% of 150 instants); footprint 4.06 x 1.90 m (fitted/prior); fusion box_fit+covariance_intersection.
- U7 (anonymous, -7.45 to 4.50 s): A:track_007, B:track_003 joined by same box A:track_007-B:track_003 (99% of 150 instants); footprint 4.32 x 1.90 m (fitted/prior); fusion box_fit+covariance_intersection.
- U8 (anonymous, -1.10 to -0.85 s): B:track_009; footprint 4.60 x 1.90 m (prior/prior); fusion covariance_intersection.
- U9 (anonymous, 0.45 to 2.80 s): A:track_008; footprint 4.60 x 1.90 m (prior/prior); fusion covariance_intersection.
- U10 (anonymous, 2.60 to 3.90 s): A:track_009; footprint 4.60 x 1.90 m (prior/prior); fusion covariance_intersection.
- U11 (anonymous, 2.95 to 4.50 s): A:track_010; footprint 4.60 x 1.90 m (prior/prior); fusion covariance_intersection.

## Global graph

55 nodes, 96 edges; 20 merged node(s): g05 TRACK_APPEARED_FRONT(A,U2) from A:e03 + A:e30, g06 TRACK_APPEARED_LEFT(A,U1) from A:e04 + A:e25, g07 TRACK_APPEARED_LEFT(A,U5) from A:e05 + A:e24, g09 TRACK_APPEARED_LEFT(B,U1) from B:e05 + B:e19, g10 TRACK_APPEARED_LEFT(B,U5) from B:e04 + B:e12, g11 TRACK_APPEARED_LEFT(B,U6) from B:e03 + B:e23, g12 TRACK_APPEARED_RIGHT(A,U3) from A:e07 + A:e31, g15 TRACK_APPEARED_RIGHT(B,U3) from B:e07 + B:e18, g16 TRACK_APPEARED_RIGHT(B,U4) from B:e08 + B:e11, g17 TRACK_APPEARED_RIGHT(B,U7) from B:e06 + B:e24, g19 CRITICAL_TTC_START(A,U2) from A:e10 + A:e15, g20 CRITICAL_TTC_START(B,A) from B:e10 + B:e21, g25 TRACK_APPEARED_LEFT(B,U5) from B:e13 + B:e17, g26 CLOSING_START(B,A) from B:e14 + B:e22, g27 CLOSING_START(A,U6) from A:e13 + A:e17, g28 TRACK_APPEARED_RIGHT(B,U8) from B:e15 + B:e16, g29 CLOSING_START(A,U7) from A:e14 + A:e16, g39 COLLISION(A,B) from A:e20 + B:e20, g46 TRACK_APPEARED_FRONT(A,U9) from A:e22 + A:e27, g50 TRACK_APPEARED_LEFT(A,U10) from A:e26 + A:e29.

### Event sequence (global time)

- `-7.45` MOVING_START(A); MOVING_START(B); THROTTLE_START(A); THROTTLE_START(B); TRACK_APPEARED_FRONT(A,U2); TRACK_APPEARED_LEFT(A,U1); TRACK_APPEARED_LEFT(A,U5); TRACK_APPEARED_LEFT(A,U6); TRACK_APPEARED_LEFT(B,U1); TRACK_APPEARED_LEFT(B,U5); TRACK_APPEARED_LEFT(B,U6); TRACK_APPEARED_RIGHT(A,U3); TRACK_APPEARED_RIGHT(A,U4); TRACK_APPEARED_RIGHT(A,U7); TRACK_APPEARED_RIGHT(B,U3); TRACK_APPEARED_RIGHT(B,U4); TRACK_APPEARED_RIGHT(B,U7)
- `-7.40` TRACK_APPEARED_FRONT(B,A)
- `-6.95` CRITICAL_TTC_START(A,U2)
- `-6.90` CRITICAL_TTC_START(B,A)
- `-3.90` TRACK_LOST(B,U4)
- `-3.75` TRACK_LOST(B,U5)
- `-1.50` THROTTLE_END(A); BRAKE_START(A)
- `-1.30` TRACK_APPEARED_LEFT(B,U5)
- `-1.25` CLOSING_START(B,A)
- `-1.15` CLOSING_START(A,U6)
- `-1.10` TRACK_APPEARED_RIGHT(B,U8); CLOSING_START(A,U7)
- `-0.85` TRACK_LOST(B,U8)
- `-0.70` TRACK_LOST(B,U5)
- `-0.65` CRITICAL_TTC_END(A,U2)
- `-0.55` CLOSING_END(A,U7)
- `-0.40` CLOSING_END(A,U6)
- `-0.30` MOVING_END(A); STOP_START(A)
- `-0.05` TRACK_LOST(B,U1); TRACK_LOST(B,U3)
- `+0.00` COLLISION(A,B); CRITICAL_TTC_END(B,A); CLOSING_END(B,A); TRACK_LOST(B,U6); TRACK_LOST(B,U7)
- `+0.05` BRAKE_END(A); THROTTLE_END(B)
- `+0.45` TRACK_APPEARED_FRONT(A,U9)
- `+0.55` BRAKE_START(A)
- `+1.50` TRACK_LOST(A,U5)
- `+2.10` TRACK_LOST(A,U1)
- `+2.60` TRACK_APPEARED_LEFT(A,U10)
- `+2.80` TRACK_LOST(A,U9)
- `+2.95` TRACK_APPEARED_LEFT(A,U11)
- `+3.90` TRACK_LOST(A,U10)
- `+4.40` TRACK_LOST(A,U2)
- `+4.45` TRACK_LOST(A,U3)

### What happened, in plain language

- 7.45 s before the reference collision, A started moving (already the case when first observed).
- 7.45 s before the reference collision, B started moving (already the case when first observed).
- 7.45 s before the reference collision, A pressed the accelerator (already the case when first observed).
- 7.45 s before the reference collision, B pressed the accelerator (already the case when first observed).
- 7.45 s before the reference collision, A's radar started tracking anonymous road user U2, which appeared in front of it.
- 7.45 s before the reference collision, A's radar started tracking anonymous road user U1, which appeared on its left.
- 7.45 s before the reference collision, A's radar started tracking anonymous road user U5, which appeared on its left.
- 7.45 s before the reference collision, A's radar started tracking anonymous road user U6, which appeared on its left.
- 7.45 s before the reference collision, B's radar started tracking anonymous road user U1, which appeared on its left.
- 7.45 s before the reference collision, B's radar started tracking anonymous road user U5, which appeared on its left.
- 7.45 s before the reference collision, B's radar started tracking anonymous road user U6, which appeared on its left.
- 7.45 s before the reference collision, A's radar started tracking anonymous road user U3, which appeared on its right.
- 7.45 s before the reference collision, A's radar started tracking anonymous road user U4, which appeared on its right.
- 7.45 s before the reference collision, A's radar started tracking anonymous road user U7, which appeared on its right.
- 7.45 s before the reference collision, B's radar started tracking anonymous road user U3, which appeared on its right.
- 7.45 s before the reference collision, B's radar started tracking anonymous road user U4, which appeared on its right.
- 7.45 s before the reference collision, B's radar started tracking anonymous road user U7, which appeared on its right.
- 7.40 s before the reference collision, B's radar started tracking A, which appeared in front of it.
- 6.95 s before the reference collision, A's time-to-contact with anonymous road user U2 became critical.
- 6.90 s before the reference collision, B's time-to-contact with A became critical.
- 3.90 s before the reference collision, B's radar lost anonymous road user U4 (its states are UNKNOWN from then on, not ended).
- 3.75 s before the reference collision, B's radar lost anonymous road user U5 (its states are UNKNOWN from then on, not ended).
- 1.50 s before the reference collision, A released the accelerator.
- 1.50 s before the reference collision, A started braking.
- 1.30 s before the reference collision, B's radar started tracking anonymous road user U5, which appeared on its left.
- 1.25 s before the reference collision, B observed A start closing in.
- 1.15 s before the reference collision, A observed anonymous road user U6 start closing in.
- 1.10 s before the reference collision, B's radar started tracking anonymous road user U8, which appeared on its right.
- 1.10 s before the reference collision, A observed anonymous road user U7 start closing in.
- 0.85 s before the reference collision, B's radar lost anonymous road user U8 (its states are UNKNOWN from then on, not ended).
- 0.70 s before the reference collision, B's radar lost anonymous road user U5 (its states are UNKNOWN from then on, not ended).
- 0.65 s before the reference collision, A's time-to-contact with anonymous road user U2 stopped being critical.
- 0.55 s before the reference collision, A observed anonymous road user U7 stop closing in.
- 0.40 s before the reference collision, A observed anonymous road user U6 stop closing in.
- 0.30 s before the reference collision, A stopped moving.
- 0.30 s before the reference collision, A came to a stop.
- 0.05 s before the reference collision, B's radar lost anonymous road user U1 (its states are UNKNOWN from then on, not ended).
- 0.05 s before the reference collision, B's radar lost anonymous road user U3 (its states are UNKNOWN from then on, not ended).
- At the reference collision, A and B both recorded this same collision (peak impulses A: 34837, B: 34837 N*s).
- At the reference collision, B's time-to-contact with A stopped being critical.
- At the reference collision, B observed A stop closing in.
- At the reference collision, B's radar lost anonymous road user U6 (its states are UNKNOWN from then on, not ended).
- At the reference collision, B's radar lost anonymous road user U7 (its states are UNKNOWN from then on, not ended).
- 0.05 s after the reference collision, A released the brake.
- 0.05 s after the reference collision, B released the accelerator.
- 0.45 s after the reference collision, A's radar started tracking anonymous road user U9, which appeared in front of it.
- 0.55 s after the reference collision, A started braking.
- 1.50 s after the reference collision, A's radar lost anonymous road user U5 (its states are UNKNOWN from then on, not ended).
- 2.10 s after the reference collision, A's radar lost anonymous road user U1 (its states are UNKNOWN from then on, not ended).
- 2.60 s after the reference collision, A's radar started tracking anonymous road user U10, which appeared on its left.
- 2.80 s after the reference collision, A's radar lost anonymous road user U9 (its states are UNKNOWN from then on, not ended).
- 2.95 s after the reference collision, A's radar started tracking anonymous road user U11, which appeared on its left.
- 3.90 s after the reference collision, A's radar lost anonymous road user U10 (its states are UNKNOWN from then on, not ended).
- 4.40 s after the reference collision, A's radar lost anonymous road user U2 (its states are UNKNOWN from then on, not ended).
- 4.45 s after the reference collision, A's radar lost anonymous road user U3 (its states are UNKNOWN from then on, not ended).

### Temporal safety relations

CUT_IN_START < CRITICAL_TTC_START < COLLISION, or CRITICAL_TTC_START <= CUT_IN_START (critical TTC already active), and EGO_PATH_ENTRY before/after the critical TTC. Temporal order only, not causes.

- A's track_002 (unidentified U2): CRITICAL_TTC_START 0.50, COLLISION 7.45 (+6.95 s) [local times; t_global: critical_ttc_start -6.95, collision +0.00]
- B's track_007 (A): CRITICAL_TTC_START 0.55, COLLISION with A 7.45 (+6.90 s) [local times; t_global: critical_ttc_start -6.90, collision +0.00]

### Simultaneous events (order unresolved at 0.05 s)

- MOVING_START(A); MOVING_START(B); THROTTLE_START(A); THROTTLE_START(B); TRACK_APPEARED_FRONT(A,U2); TRACK_APPEARED_LEFT(A,U1); TRACK_APPEARED_LEFT(A,U5); TRACK_APPEARED_LEFT(A,U6); TRACK_APPEARED_LEFT(B,U1); TRACK_APPEARED_LEFT(B,U5); TRACK_APPEARED_LEFT(B,U6); TRACK_APPEARED_RIGHT(A,U3); TRACK_APPEARED_RIGHT(A,U4); TRACK_APPEARED_RIGHT(A,U7); TRACK_APPEARED_RIGHT(B,U3); TRACK_APPEARED_RIGHT(B,U4); TRACK_APPEARED_RIGHT(B,U7)
- THROTTLE_END(A); BRAKE_START(A)
- TRACK_APPEARED_RIGHT(B,U8); CLOSING_START(A,U7)
- MOVING_END(A); STOP_START(A)
- TRACK_LOST(B,U1); TRACK_LOST(B,U3)
- COLLISION(A,B); CRITICAL_TTC_END(B,A); CLOSING_END(B,A); TRACK_LOST(B,U6); TRACK_LOST(B,U7)
- BRAKE_END(A); THROTTLE_END(B)

### States still active when observation ended

A:
- STOP, since A:e19 (t = 7.15 s)
- BRAKE, since A:e23 (t = 8.00 s)
B:
- MOVING, since B:e01 (t = 0.00 s)

### Sign detection windows

A:
- none
B:
- none

### Perceived state just before each collision report

- A A:e20 at 7.45 s (local): ego: STOP, BRAKE; track_001: no active state; track_002: IN_EGO_PATH; track_003: no active state; track_004: no active state; track_005: no active state; track_006: no active state; track_007: no active state
- B B:e20 at 7.45 s (local): ego: MOVING, THROTTLE; track_001: no active state; track_003: no active state; track_007: CLOSING, CRITICAL_TTC, IN_EGO_PATH; track lost, states UNKNOWN: track_002, track_004, track_005, track_006, track_008, track_009

### Tracks lost while a state was active

A lost track's states become UNKNOWN: the recorder can no longer tell whether they ended.

A:
- track_008 at 10.25 s (A:e27): IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)
- track_002 at 11.85 s (A:e30): IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)
- lost with no state active: track_005, track_001, track_009, track_003
B:
- lost with no state active: track_006, track_002, track_009, track_008, track_004, track_005, track_001, track_003

## Uncertainty and limitations

- A:track_001 stays anonymous (U1): not approaching before the contact: clearance 2.3 m -> 9.7 m over the last 1.0 s.
- A:track_002 stays anonymous (U2): not approaching before the contact: clearance 7.9 m -> 15.8 m over the last 1.0 s.
- A:track_003 stays anonymous (U3): not approaching before the contact: clearance 4.9 m -> 12.8 m over the last 1.0 s.
- A:track_004 stays anonymous (U4): not approaching before the contact: clearance 16.6 m -> 24.4 m over the last 1.0 s.
- A:track_005 stays anonymous (U5): not approaching before the contact: clearance 14.5 m -> 22.3 m over the last 1.0 s.
- A:track_006 stays anonymous (U6): ambiguous: 2 persistent tracks of A are compatible with the contact (track_006, track_007).
- A:track_007 stays anonymous (U7): ambiguous: 2 persistent tracks of A are compatible with the contact (track_006, track_007).
- A:track_008 stays anonymous (U9): tracked for 0.00 s before the matched collision (needs 1.00 s); first seen 0.45 s after the matched collision; range trend before the contact not measurable; speed not comparable with B's own speed before the collision.
- A:track_009 stays anonymous (U10): tracked for 0.00 s before the matched collision (needs 1.00 s); first seen 2.60 s after the matched collision; range trend before the contact not measurable; speed not comparable with B's own speed before the collision.
- A:track_010 stays anonymous (U11): tracked for 0.00 s before the matched collision (needs 1.00 s); first seen 2.95 s after the matched collision; range trend before the contact not measurable; speed not comparable with B's own speed before the collision.
- B:track_001 stays anonymous (U6): not approaching before the contact: clearance 2.4 m -> 2.7 m over the last 1.0 s.
- B:track_002 stays anonymous (U5): lost 3.75 s before the matched collision (window 1.00 s); not approaching before the contact: clearance 25.7 m -> 25.9 m over the last 1.0 s; speed not comparable with A's own speed before the collision.
- B:track_003 stays anonymous (U7): not approaching before the contact: clearance 3.2 m -> 3.6 m over the last 1.0 s.
- B:track_004 stays anonymous (U3): not approaching before the contact: clearance 16.7 m -> 16.9 m over the last 1.0 s.
- B:track_005 stays anonymous (U1): not approaching before the contact: clearance 13.3 m -> 13.4 m over the last 1.0 s.
- B:track_006 stays anonymous (U4): lost 3.90 s before the matched collision (window 1.00 s); not approaching before the contact: clearance 27.8 m -> 27.9 m over the last 1.0 s; speed not comparable with A's own speed before the collision.
- B:track_008 stays anonymous (U5): track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 3.08 m/s for reference).
- B:track_009 stays anonymous (U8): not approaching before the contact: clearance 28.1 m -> 28.3 m over the last 1.0 s.
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
