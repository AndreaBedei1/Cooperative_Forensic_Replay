# Reconstruction report - S14/run_0_surrounded

Inputs: `vehicles/A/`, `vehicles/B/` (vehicle-local files) and the supplied `incident_context.json`. `ground_truth/` and the run's `metadata.json` were not read; the privileged comparison, if run, is in `evaluation/`.

Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.

Pipeline: raw log -> local trace -> local graph (each recorder alone, own clock, own frame) -> graph-level alignment -> identity association -> road users in the common frame of the recorders' own pose streams -> global graph.

## Local reconstructions

| Recorder | Duration (local) | Trace frames | Graph nodes | Graph edges | Radar tracks | Collision reports (local time) |
|----------|-----------------:|-------------:|------------:|------------:|-------------:|-------------------------------|
| A | 11.95 s | 121 | 29 | 49 | 9 | A:e17 @ 7.75 s |
| B | 11.95 s | 121 | 32 | 61 | 14 | B:e23 @ 7.75 s |

## Graph alignment

Reference event: `collision_001` (t_global = 0); `t_global = t_local + offset_to_global`. A graph that did not report it is aligned through the chain of matched collisions linking it to the reference (multi-hop); its anchor is its own report of the last collision of that chain.

| Graph | Status | Anchor node | Anchor local time | Offset to global | Note |
|-------|--------|-------------|------------------:|-----------------:|------|
| A | ALIGNED | A:e17 | 7.75 | -7.75 | reported the reference collision collision_001 |
| B | ALIGNED | B:e23 | 7.75 | -7.75 | reported the reference collision collision_001 |

Estimated relative clock offsets: B - A = +0.000 s

Matched `collision_001`: A and B both recorded a collision; peak impulses 255.03 vs 255.03 N*s (similarity 1.000, tolerance 0.10); no competing report within tolerance; the two bodies touch at their reports (0.00 m apart, tolerance 1.0 m); independent relative impulse std 0.100; combined z 0.000 (gate 3.0); engineering assumption; pre-contact radar view of each recorder checked against the candidate partner's own speed: not contradicted

## Identity associations

| Local track | Global entity | Status | Confidence | Evidence |
|-------------|---------------|--------|-----------:|----------|
| A:track_001 | U1 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 255.03 vs 255.03 N*s)<br>tracked for 7.75 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 2.2 m -> 2.1 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 0.53 m/s for reference)<br>clearance at the contact 2.08 m<br>ambiguous: 4 persistent tracks of A are compatible with the contact (track_001, track_002, track_003, track_004)<br>anonymous road user U1: A:track_001, B:track_003 |
| A:track_002 | U2 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 255.03 vs 255.03 N*s)<br>tracked for 7.75 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 11.7 m -> 11.0 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 0.51 m/s for reference)<br>clearance at the contact 10.95 m (beyond 3.50 m: confidence factor 0.05)<br>ambiguous: 4 persistent tracks of A are compatible with the contact (track_001, track_002, track_003, track_004)<br>anonymous road user U2: A:track_002, B:track_005 |
| A:track_003 | B | ASSOCIATED | 0.99 | A and B both reported collision_001 (peak impulse 255.03 vs 255.03 N*s)<br>tracked for 7.75 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 1.4 m -> 0.1 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 0.22 m/s for reference)<br>clearance at the contact 0.12 m<br>the only compatible track of A touching it at the contact (clearance 0.12 m; track_001, track_002, track_004 at 2.08 m, 11.05 m, 10.16 m) |
| A:track_004 | U3 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 255.03 vs 255.03 N*s)<br>tracked for 7.70 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 10.2 m -> 10.2 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 0.47 m/s for reference)<br>clearance at the contact 10.11 m (beyond 3.50 m: confidence factor 0.09)<br>ambiguous: 4 persistent tracks of A are compatible with the contact (track_001, track_002, track_003, track_004)<br>anonymous road user U3: B:track_001, A:track_004 |
| A:track_005 | U9 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 255.03 vs 255.03 N*s)<br>tracked for 0.70 s before the matched collision (needs 1.00 s)<br>continuous up to the contact: last observed 0.05 s before it (window 1.00 s)<br>approaching before the contact: clearance 42.1 m -> 42.0 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 0.33 m/s for reference)<br>clearance at the contact 41.88 m (beyond 3.50 m: confidence factor 0.00)<br>anonymous road user U9: A:track_005 |
| A:track_006 | U7 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 255.03 vs 255.03 N*s)<br>tracked for 0.35 s before the matched collision (needs 1.00 s)<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 26.3 m -> 26.3 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 0.58 m/s for reference)<br>clearance at the contact 26.27 m (beyond 3.50 m: confidence factor 0.00)<br>anonymous road user U7: B:track_008, B:track_009, A:track_006 |
| A:track_007 | U5 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 255.03 vs 255.03 N*s)<br>tracked for 0.10 s before the matched collision (needs 1.00 s)<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>not approaching before the contact: clearance 10.7 m -> 10.8 m over the last 1.0 s<br>speed not comparable with B's own speed before the collision<br>clearance at the contact 10.72 m (beyond 3.50 m: confidence factor 0.06)<br>anonymous road user U5: B:track_006, A:track_007 |
| A:track_008 | U4 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 255.03 vs 255.03 N*s)<br>tracked for 0.00 s before the matched collision (needs 1.00 s)<br>first seen 0.70 s after the matched collision<br>range trend before the contact not measurable<br>speed not comparable with B's own speed before the collision<br>anonymous road user U4: B:track_004, B:track_010, A:track_008 |
| A:track_009 | U11 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 255.03 vs 255.03 N*s)<br>tracked for 0.00 s before the matched collision (needs 1.00 s)<br>first seen 1.75 s after the matched collision<br>range trend before the contact not measurable<br>speed not comparable with B's own speed before the collision<br>anonymous road user U11: B:track_013, A:track_009 |
| B:track_001 | U3 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 255.03 vs 255.03 N*s)<br>tracked for 7.75 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 10.5 m -> 9.9 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 0.04 m/s for reference)<br>clearance at the contact 9.92 m (beyond 3.50 m: confidence factor 0.10)<br>ambiguous: 8 persistent tracks of B are compatible with the contact (track_001, track_002, track_003, track_005, track_006, track_009, track_010, track_011)<br>anonymous road user U3: B:track_001, A:track_004 |
| B:track_002 | A | ASSOCIATED | 1.00 | B and A both reported collision_001 (peak impulse 255.03 vs 255.03 N*s)<br>tracked for 7.75 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 1.8 m -> 0.8 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 0.08 m/s for reference)<br>clearance at the contact 0.82 m<br>ambiguous: 8 persistent tracks of B are compatible with the contact (track_001, track_002, track_003, track_005, track_006, track_009, track_010, track_011)<br>common frame: its returns lie on A's own footprint (median 0.00 m, 0.00 sigma of the relative uncertainty, over 240 samples; 100% within 3 sigma) at A's own velocity |
| B:track_003 | U1 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 255.03 vs 255.03 N*s)<br>tracked for 7.75 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 3.2 m -> 2.8 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 0.07 m/s for reference)<br>clearance at the contact 2.77 m<br>ambiguous: 8 persistent tracks of B are compatible with the contact (track_001, track_002, track_003, track_005, track_006, track_009, track_010, track_011)<br>anonymous road user U1: A:track_001, B:track_003 |
| B:track_004 | U4 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 255.03 vs 255.03 N*s)<br>tracked for 7.75 s before the matched collision<br>lost 4.10 s before the matched collision (window 1.00 s)<br>approaching before the contact: clearance 28.8 m -> 28.5 m over the last 1.0 s<br>speed not comparable with A's own speed before the collision<br>retrospective: identity resolved from later evidence at -1.35 s (entity seen by several observers), carried back 2.75 s with the motion model; posterior 0.959 against 1 candidate(s) and a new road user; observation times unchanged<br>anonymous road user U4: B:track_004, B:track_010, A:track_008 |
| B:track_005 | U2 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 255.03 vs 255.03 N*s)<br>tracked for 7.70 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 11.1 m -> 10.6 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 0.07 m/s for reference)<br>clearance at the contact 10.53 m (beyond 3.50 m: confidence factor 0.06)<br>ambiguous: 8 persistent tracks of B are compatible with the contact (track_001, track_002, track_003, track_005, track_006, track_009, track_010, track_011)<br>anonymous road user U2: A:track_002, B:track_005 |
| B:track_006 | U5 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 255.03 vs 255.03 N*s)<br>tracked for 7.70 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 11.5 m -> 11.2 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 0.06 m/s for reference)<br>clearance at the contact 11.12 m (beyond 3.50 m: confidence factor 0.04)<br>ambiguous: 8 persistent tracks of B are compatible with the contact (track_001, track_002, track_003, track_005, track_006, track_009, track_010, track_011)<br>anonymous road user U5: B:track_006, A:track_007 |
| B:track_007 | U6 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 255.03 vs 255.03 N*s)<br>tracked for 7.70 s before the matched collision<br>lost 5.55 s before the matched collision (window 1.00 s)<br>approaching before the contact: clearance 44.6 m -> 44.2 m over the last 1.0 s<br>speed not comparable with A's own speed before the collision<br>anonymous road user U6: B:track_007 |
| B:track_008 | U7 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 255.03 vs 255.03 N*s)<br>tracked for 6.95 s before the matched collision<br>lost 3.95 s before the matched collision (window 1.00 s)<br>approaching before the contact: clearance 28.5 m -> 28.0 m over the last 1.0 s<br>speed not comparable with A's own speed before the collision<br>retrospective: identity resolved from later evidence at -1.40 s (entity seen by several observers), carried back 2.55 s with the motion model; posterior 0.953 against 2 candidate(s) and a new road user; observation times unchanged<br>anonymous road user U7: B:track_008, B:track_009, A:track_006 |
| B:track_009 | U7 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 255.03 vs 255.03 N*s)<br>tracked for 1.40 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 26.8 m -> 26.2 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 0.09 m/s for reference)<br>clearance at the contact 26.18 m (beyond 3.50 m: confidence factor 0.00)<br>ambiguous: 8 persistent tracks of B are compatible with the contact (track_001, track_002, track_003, track_005, track_006, track_009, track_010, track_011)<br>anonymous road user U7: B:track_008, B:track_009, A:track_006 |
| B:track_010 | U4 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 255.03 vs 255.03 N*s)<br>tracked for 1.35 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 26.8 m -> 26.7 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 0.10 m/s for reference)<br>clearance at the contact 26.71 m (beyond 3.50 m: confidence factor 0.00)<br>ambiguous: 8 persistent tracks of B are compatible with the contact (track_001, track_002, track_003, track_005, track_006, track_009, track_010, track_011)<br>anonymous road user U4: B:track_004, B:track_010, A:track_008 |
| B:track_011 | U8 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 255.03 vs 255.03 N*s)<br>tracked for 1.15 s before the matched collision<br>continuous up to the contact: last observed 0.75 s before it (window 1.00 s)<br>approaching before the contact: clearance 42.7 m -> 42.6 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 0.04 m/s for reference)<br>clearance at the contact 42.56 m (beyond 3.50 m: confidence factor 0.00)<br>ambiguous: 8 persistent tracks of B are compatible with the contact (track_001, track_002, track_003, track_005, track_006, track_009, track_010, track_011)<br>anonymous road user U8: B:track_011 |
| B:track_012 | U10 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 255.03 vs 255.03 N*s)<br>tracked for 0.40 s before the matched collision (needs 1.00 s)<br>continuous up to the contact: last observed 0.10 s before it (window 1.00 s)<br>approaching before the contact: clearance 41.9 m -> 41.7 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 0.09 m/s for reference)<br>clearance at the contact 41.72 m (beyond 3.50 m: confidence factor 0.00)<br>anonymous road user U10: B:track_012 |
| B:track_013 | U11 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 255.03 vs 255.03 N*s)<br>tracked for 0.00 s before the matched collision (needs 1.00 s)<br>first seen 0.30 s after the matched collision<br>range trend before the contact not measurable<br>speed not comparable with A's own speed before the collision<br>anonymous road user U11: B:track_013, A:track_009 |
| B:track_014 | U12 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 255.03 vs 255.03 N*s)<br>tracked for 0.00 s before the matched collision (needs 1.00 s)<br>first seen 3.60 s after the matched collision<br>range trend before the contact not measurable<br>speed not comparable with A's own speed before the collision<br>anonymous road user U12: B:track_014 |

## Road users in the common frame

- B:track_002 is A: its returns lie on A's own footprint (median 0.00 m over 240 samples, 100% within 3 sigma) at A's velocity.
- U1 (anonymous, -7.75 to 4.20 s): A:track_001, B:track_003 joined by same box A:track_001-B:track_003 (100% of 240 instants); footprint 4.60 x 1.90 m (prior/prior); fusion box_fit.
- U2 (anonymous, -7.75 to 4.20 s): A:track_002, B:track_005 joined by same box A:track_002-B:track_005 (100% of 239 instants); footprint 4.60 x 1.90 m (prior/prior); fusion box_fit.
- U3 (anonymous, -7.75 to 4.20 s): B:track_001, A:track_004 joined by same box A:track_004-B:track_001 (100% of 237 instants); footprint 4.60 x 1.90 m (prior/prior); fusion box_fit.
- U4 (anonymous, -7.75 to 4.20 s): B:track_004, B:track_010, A:track_008 joined by same box A:track_008-B:track_010 (100% of 12 instants); footprint 4.60 x 1.90 m (prior/prior); fusion box_fit+covariance_intersection.
- U5 (anonymous, -7.70 to 4.20 s): B:track_006, A:track_007 joined by same box A:track_007-B:track_006 (100% of 86 instants); footprint 4.60 x 1.90 m (prior/prior); fusion box_fit+covariance_intersection.
- U6 (anonymous, -7.70 to -5.55 s): B:track_007; footprint 4.60 x 1.90 m (prior/prior); fusion covariance_intersection.
- U7 (anonymous, -6.95 to 4.20 s): B:track_008, B:track_009, A:track_006 joined by same box A:track_006-B:track_009 (100% of 19 instants); footprint 4.60 x 1.90 m (prior/prior); fusion box_fit+covariance_intersection.
- U8 (anonymous, -1.15 to -0.75 s): B:track_011; footprint 4.60 x 1.90 m (prior/prior); fusion covariance_intersection.
- U9 (anonymous, -0.70 to -0.05 s): A:track_005; footprint 4.60 x 1.90 m (prior/prior); fusion covariance_intersection.
- U10 (anonymous, -0.40 to -0.10 s): B:track_012; footprint 4.60 x 1.90 m (prior/prior); fusion covariance_intersection.
- U11 (anonymous, 0.30 to 4.20 s): B:track_013, A:track_009 joined by same box A:track_009-B:track_013 (100% of 9 instants); footprint 4.60 x 1.90 m (prior/prior); fusion box_fit+covariance_intersection.
- U12 (anonymous, 3.60 to 3.90 s): B:track_014; footprint 4.60 x 1.90 m (prior/prior); fusion covariance_intersection.

## Global graph

60 nodes, 143 edges; 16 merged node(s): g09 TRACK_APPEARED_LEFT(B,U4) from B:e04 + B:e13, g12 TRACK_APPEARED_FRONT(B,U6) from B:e07 + B:e12, g16 CRITICAL_TTC_START(A,U1) from A:e07 + A:e23, g18 TRACK_APPEARED_RIGHT(B,U7) from B:e11 + B:e14, g22 TRACK_APPEARED_RIGHT(B,U7) from B:e15 + B:e28, g23 CRITICAL_TTC_START(A,B) from A:e08 + A:e18, g24 TRACK_APPEARED_LEFT(B,U4) from B:e16 + B:e29, g25 TRACK_APPEARED_FRONT(B,U8) from B:e17 + B:e19, g26 CLOSING_START(A,B) from A:e09 + A:e21, g27 CRITICAL_TTC_START(B,A) from B:e18 + B:e24, g29 TRACK_APPEARED_FRONT(A,U9) from A:e10 + A:e16, g30 CLOSING_START(B,A) from B:e20 + B:e25, g31 TRACK_APPEARED_FRONT(B,U10) from B:e21 + B:e22, g39 COLLISION(A,B) from A:e17 + B:e23, g52 TRACK_APPEARED_LEFT(A,U11) from A:e24 + A:e28, g58 TRACK_APPEARED_LEFT(B,U12) from B:e31 + B:e32.

### Event sequence (global time)

- `-7.75` MOVING_START(A); MOVING_START(B); THROTTLE_START(A); THROTTLE_START(B); TRACK_APPEARED_FRONT(A,U1); TRACK_APPEARED_FRONT(B,U3); TRACK_APPEARED_LEFT(A,B); TRACK_APPEARED_LEFT(A,U2); TRACK_APPEARED_LEFT(B,U4); TRACK_APPEARED_RIGHT(B,A); TRACK_APPEARED_RIGHT(B,U1)
- `-7.70` TRACK_APPEARED_FRONT(B,U6); TRACK_APPEARED_LEFT(A,U3); TRACK_APPEARED_LEFT(B,U2); TRACK_APPEARED_RIGHT(B,U5)
- `-7.25` CRITICAL_TTC_START(A,U1); CRITICAL_TTC_START(B,U3)
- `-6.95` TRACK_APPEARED_RIGHT(B,U7)
- `-5.55` TRACK_LOST(B,U6)
- `-4.10` TRACK_LOST(B,U4)
- `-3.95` TRACK_LOST(B,U7)
- `-1.40` TRACK_APPEARED_RIGHT(B,U7); CRITICAL_TTC_START(A,B)
- `-1.35` TRACK_APPEARED_LEFT(B,U4)
- `-1.15` TRACK_APPEARED_FRONT(B,U8)
- `-0.80` CLOSING_START(A,B)
- `-0.75` CRITICAL_TTC_START(B,A); TRACK_LOST(B,U8)
- `-0.70` TRACK_APPEARED_FRONT(A,U9)
- `-0.60` CLOSING_START(B,A)
- `-0.40` TRACK_APPEARED_FRONT(B,U10)
- `-0.35` TRACK_APPEARED_RIGHT(A,U7); EGO_PATH_ENTRY(A,U3); CRITICAL_TTC_START(A,U3)
- `-0.25` EGO_PATH_ENTRY(A,U9)
- `-0.10` TRACK_APPEARED_RIGHT(A,U5); TRACK_LOST(B,U10)
- `-0.05` TRACK_LOST(A,U9)
- `+0.00` COLLISION(A,B); CRITICAL_TTC_END(A,B); CRITICAL_TTC_END(B,A)
- `+0.05` CLOSING_END(B,A); THROTTLE_END(A); THROTTLE_END(B); EGO_PATH_ENTRY(A,B)
- `+0.10` CLOSING_END(A,B)
- `+0.30` TRACK_APPEARED_FRONT(B,U11)
- `+0.70` TRACK_APPEARED_LEFT(A,U4)
- `+1.10` TRACK_LOST(B,U7)
- `+1.25` CRITICAL_TTC_END(A,U1)
- `+1.60` TRACK_LOST(B,U4)
- `+1.75` TRACK_APPEARED_LEFT(A,U11)
- `+2.10` EGO_PATH_EXIT(A,U7)
- `+2.40` CRITICAL_TTC_START(A,U5)
- `+2.70` CRITICAL_TTC_START(A,U1)
- `+3.30` CLOSING_START(B,U1)
- `+3.40` TRACK_LOST(A,U11)
- `+3.60` TRACK_APPEARED_LEFT(B,U12); EGO_PATH_ENTRY(A,U7)
- `+3.90` TRACK_LOST(B,U12)

### What happened, in plain language

- 7.75 s before the reference collision, A started moving (already the case when first observed).
- 7.75 s before the reference collision, B started moving (already the case when first observed).
- 7.75 s before the reference collision, A pressed the accelerator (already the case when first observed).
- 7.75 s before the reference collision, B pressed the accelerator (already the case when first observed).
- 7.75 s before the reference collision, A's radar started tracking anonymous road user U1, which appeared in front of it.
- 7.75 s before the reference collision, B's radar started tracking anonymous road user U3, which appeared in front of it.
- 7.75 s before the reference collision, A's radar started tracking B, which appeared on its left.
- 7.75 s before the reference collision, A's radar started tracking anonymous road user U2, which appeared on its left.
- 7.75 s before the reference collision, B's radar started tracking anonymous road user U4, which appeared on its left.
- 7.75 s before the reference collision, B's radar started tracking A, which appeared on its right.
- 7.75 s before the reference collision, B's radar started tracking anonymous road user U1, which appeared on its right.
- 7.70 s before the reference collision, B's radar started tracking anonymous road user U6, which appeared in front of it.
- 7.70 s before the reference collision, A's radar started tracking anonymous road user U3, which appeared on its left.
- 7.70 s before the reference collision, B's radar started tracking anonymous road user U2, which appeared on its left.
- 7.70 s before the reference collision, B's radar started tracking anonymous road user U5, which appeared on its right.
- 7.25 s before the reference collision, A's time-to-contact with anonymous road user U1 became critical.
- 7.25 s before the reference collision, B's time-to-contact with anonymous road user U3 became critical.
- 6.95 s before the reference collision, B's radar started tracking anonymous road user U7, which appeared on its right.
- 5.55 s before the reference collision, B's radar lost anonymous road user U6 (its states are UNKNOWN from then on, not ended).
- 4.10 s before the reference collision, B's radar lost anonymous road user U4 (its states are UNKNOWN from then on, not ended).
- 3.95 s before the reference collision, B's radar lost anonymous road user U7 (its states are UNKNOWN from then on, not ended).
- 1.40 s before the reference collision, B's radar started tracking anonymous road user U7, which appeared on its right.
- 1.40 s before the reference collision, A's time-to-contact with B became critical.
- 1.35 s before the reference collision, B's radar started tracking anonymous road user U4, which appeared on its left.
- 1.15 s before the reference collision, B's radar started tracking anonymous road user U8, which appeared in front of it.
- 0.80 s before the reference collision, A observed B start closing in.
- 0.75 s before the reference collision, B's time-to-contact with A became critical.
- 0.75 s before the reference collision, B's radar lost anonymous road user U8 (its states are UNKNOWN from then on, not ended).
- 0.70 s before the reference collision, A's radar started tracking anonymous road user U9, which appeared in front of it.
- 0.60 s before the reference collision, B observed A start closing in.
- 0.40 s before the reference collision, B's radar started tracking anonymous road user U10, which appeared in front of it.
- 0.35 s before the reference collision, A's radar started tracking anonymous road user U7, which appeared on its right.
- 0.35 s before the reference collision, A observed anonymous road user U3 enter its forward path corridor.
- 0.35 s before the reference collision, A's time-to-contact with anonymous road user U3 became critical.
- 0.25 s before the reference collision, A observed anonymous road user U9 enter its forward path corridor.
- 0.10 s before the reference collision, A's radar started tracking anonymous road user U5, which appeared on its right.
- 0.10 s before the reference collision, B's radar lost anonymous road user U10 (its states are UNKNOWN from then on, not ended).
- 0.05 s before the reference collision, A's radar lost anonymous road user U9 (its states are UNKNOWN from then on, not ended).
- At the reference collision, A and B both recorded this same collision (peak impulses A: 255, B: 255 N*s).
- At the reference collision, A's time-to-contact with B stopped being critical.
- At the reference collision, B's time-to-contact with A stopped being critical.
- 0.05 s after the reference collision, B observed A stop closing in.
- 0.05 s after the reference collision, A released the accelerator.
- 0.05 s after the reference collision, B released the accelerator.
- 0.05 s after the reference collision, A observed B enter its forward path corridor.
- 0.10 s after the reference collision, A observed B stop closing in.
- 0.30 s after the reference collision, B's radar started tracking anonymous road user U11, which appeared in front of it.
- 0.70 s after the reference collision, A's radar started tracking anonymous road user U4, which appeared on its left.
- 1.10 s after the reference collision, B's radar lost anonymous road user U7 (its states are UNKNOWN from then on, not ended).
- 1.25 s after the reference collision, A's time-to-contact with anonymous road user U1 stopped being critical.
- 1.60 s after the reference collision, B's radar lost anonymous road user U4 (its states are UNKNOWN from then on, not ended).
- 1.75 s after the reference collision, A's radar started tracking anonymous road user U11, which appeared on its left.
- 2.10 s after the reference collision, A observed anonymous road user U7 leave its forward path corridor.
- 2.40 s after the reference collision, A's time-to-contact with anonymous road user U5 became critical.
- 2.70 s after the reference collision, A's time-to-contact with anonymous road user U1 became critical.
- 3.30 s after the reference collision, B observed anonymous road user U1 start closing in.
- 3.40 s after the reference collision, A's radar lost anonymous road user U11 (its states are UNKNOWN from then on, not ended).
- 3.60 s after the reference collision, B's radar started tracking anonymous road user U12, which appeared on its left.
- 3.60 s after the reference collision, A observed anonymous road user U7 enter its forward path corridor.
- 3.90 s after the reference collision, B's radar lost anonymous road user U12 (its states are UNKNOWN from then on, not ended).

### Temporal safety relations

CUT_IN_START < CRITICAL_TTC_START < COLLISION, or CRITICAL_TTC_START <= CUT_IN_START (critical TTC already active), and EGO_PATH_ENTRY before/after the critical TTC. Temporal order only, not causes.

- A's track_001 (unidentified U1): CRITICAL_TTC_START 0.50, COLLISION 7.75 (+7.25 s) [local times; t_global: critical_ttc_start -7.25, collision +0.00]
- A's track_003 (B): CRITICAL_TTC_START 6.35, COLLISION with B 7.75 (+1.40 s); EGO_PATH_ENTRY 7.80 after critical TTC (+1.45 s) [local times; t_global: critical_ttc_start -1.40, ego_path_entry +0.05, collision +0.00]
- A's track_004 (unidentified U3): CRITICAL_TTC_START 7.40, COLLISION 7.75 (+0.35 s); EGO_PATH_ENTRY 7.40 together with critical TTC (+0.00 s) [local times; t_global: critical_ttc_start -0.35, ego_path_entry -0.35, collision +0.00]
- A's track_005 (unidentified U9): EGO_PATH_ENTRY 7.50, no critical TTC [local times; t_global: ego_path_entry -0.25, collision +0.00]
- A's track_006 (unidentified U7): EGO_PATH_ENTRY 11.35, no critical TTC [local times; t_global: ego_path_entry +3.60]
- A's track_007 (unidentified U5): CRITICAL_TTC_START 10.15 [local times; t_global: critical_ttc_start +2.40]
- B's track_001 (unidentified U3): CRITICAL_TTC_START 0.50, COLLISION 7.75 (+7.25 s) [local times; t_global: critical_ttc_start -7.25, collision +0.00]
- B's track_002 (A): CRITICAL_TTC_START 7.00, COLLISION with A 7.75 (+0.75 s) [local times; t_global: critical_ttc_start -0.75, collision +0.00]

### Simultaneous events (order unresolved at 0.05 s)

- MOVING_START(A); MOVING_START(B); THROTTLE_START(A); THROTTLE_START(B); TRACK_APPEARED_FRONT(A,U1); TRACK_APPEARED_FRONT(B,U3); TRACK_APPEARED_LEFT(A,B); TRACK_APPEARED_LEFT(A,U2); TRACK_APPEARED_LEFT(B,U4); TRACK_APPEARED_RIGHT(B,A); TRACK_APPEARED_RIGHT(B,U1)
- TRACK_APPEARED_FRONT(B,U6); TRACK_APPEARED_LEFT(A,U3); TRACK_APPEARED_LEFT(B,U2); TRACK_APPEARED_RIGHT(B,U5)
- CRITICAL_TTC_START(A,U1); CRITICAL_TTC_START(B,U3)
- TRACK_APPEARED_RIGHT(B,U7); CRITICAL_TTC_START(A,B)
- CRITICAL_TTC_START(B,A); TRACK_LOST(B,U8)
- TRACK_APPEARED_RIGHT(A,U7); EGO_PATH_ENTRY(A,U3); CRITICAL_TTC_START(A,U3)
- TRACK_APPEARED_RIGHT(A,U5); TRACK_LOST(B,U10)
- COLLISION(A,B); CRITICAL_TTC_END(A,B); CRITICAL_TTC_END(B,A)
- CLOSING_END(B,A); THROTTLE_END(A); THROTTLE_END(B); EGO_PATH_ENTRY(A,B)
- TRACK_APPEARED_LEFT(B,U12); EGO_PATH_ENTRY(A,U7)

### States still active when observation ended

A:
- MOVING, since A:e01 (t = 0.00 s)
- EGO_PATH of track_004, since A:e12 (t = 7.40 s)
- CRITICAL_TTC of track_004, since A:e13 (t = 7.40 s)
- EGO_PATH of track_005, since A:e14 (t = 7.50 s); the track was lost at 7.70 s
- EGO_PATH of track_003, since A:e20 (t = 7.80 s)
- CRITICAL_TTC of track_007, since A:e26 (t = 10.15 s)
- CRITICAL_TTC of track_001, since A:e27 (t = 10.45 s)
- EGO_PATH of track_006, since A:e29 (t = 11.35 s)
B:
- MOVING, since B:e01 (t = 0.00 s)
- CRITICAL_TTC of track_001, since B:e10 (t = 0.50 s)
- CLOSING of track_003, since B:e30 (t = 11.05 s)

### Sign detection windows

A:
- none
B:
- none

### Perceived state just before each collision report

- A A:e17 at 7.75 s (local): ego: MOVING, THROTTLE; track_001: CRITICAL_TTC, IN_EGO_PATH; track_002: no active state; track_003: CLOSING, CRITICAL_TTC; track_004: CRITICAL_TTC, IN_EGO_PATH; track_006: IN_EGO_PATH, CRITICAL_TTC?; track_007: IN_EGO_PATH, CRITICAL_TTC?; track lost, states UNKNOWN: track_005
- B B:e23 at 7.75 s (local): ego: MOVING, THROTTLE; track_001: CRITICAL_TTC, IN_EGO_PATH; track_002: CLOSING, CRITICAL_TTC; track_003: no active state; track_005: no active state; track_006: no active state; track_009: no active state; track_010: no active state; track lost, states UNKNOWN: track_004, track_007, track_008, track_011, track_012

### Tracks lost while a state was active

A lost track's states become UNKNOWN: the recorder can no longer tell whether they ended.

A:
- track_005 at 7.70 s (A:e16): IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)
- track_009 at 11.15 s (A:e28): IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)
B:
- lost with no state active: track_007, track_004, track_008, track_011, track_012, track_009, track_010, track_014

## Uncertainty and limitations

- A:track_001 stays anonymous (U1): ambiguous: 4 persistent tracks of A are compatible with the contact (track_001, track_002, track_003, track_004).
- A:track_002 stays anonymous (U2): ambiguous: 4 persistent tracks of A are compatible with the contact (track_001, track_002, track_003, track_004).
- A:track_004 stays anonymous (U3): ambiguous: 4 persistent tracks of A are compatible with the contact (track_001, track_002, track_003, track_004).
- A:track_005 stays anonymous (U9): tracked for 0.70 s before the matched collision (needs 1.00 s).
- A:track_006 stays anonymous (U7): tracked for 0.35 s before the matched collision (needs 1.00 s).
- A:track_007 stays anonymous (U5): tracked for 0.10 s before the matched collision (needs 1.00 s); not approaching before the contact: clearance 10.7 m -> 10.8 m over the last 1.0 s; speed not comparable with B's own speed before the collision.
- A:track_008 stays anonymous (U4): tracked for 0.00 s before the matched collision (needs 1.00 s); first seen 0.70 s after the matched collision; range trend before the contact not measurable; speed not comparable with B's own speed before the collision.
- A:track_009 stays anonymous (U11): tracked for 0.00 s before the matched collision (needs 1.00 s); first seen 1.75 s after the matched collision; range trend before the contact not measurable; speed not comparable with B's own speed before the collision.
- B:track_001 stays anonymous (U3): ambiguous: 8 persistent tracks of B are compatible with the contact (track_001, track_002, track_003, track_005, track_006, track_009, track_010, track_011).
- B:track_003 stays anonymous (U1): ambiguous: 8 persistent tracks of B are compatible with the contact (track_001, track_002, track_003, track_005, track_006, track_009, track_010, track_011).
- B:track_004 stays anonymous (U4): lost 4.10 s before the matched collision (window 1.00 s); speed not comparable with A's own speed before the collision.
- B:track_005 stays anonymous (U2): ambiguous: 8 persistent tracks of B are compatible with the contact (track_001, track_002, track_003, track_005, track_006, track_009, track_010, track_011).
- B:track_006 stays anonymous (U5): ambiguous: 8 persistent tracks of B are compatible with the contact (track_001, track_002, track_003, track_005, track_006, track_009, track_010, track_011).
- B:track_007 stays anonymous (U6): lost 5.55 s before the matched collision (window 1.00 s); speed not comparable with A's own speed before the collision.
- B:track_008 stays anonymous (U7): lost 3.95 s before the matched collision (window 1.00 s); speed not comparable with A's own speed before the collision.
- B:track_009 stays anonymous (U7): ambiguous: 8 persistent tracks of B are compatible with the contact (track_001, track_002, track_003, track_005, track_006, track_009, track_010, track_011).
- B:track_010 stays anonymous (U4): ambiguous: 8 persistent tracks of B are compatible with the contact (track_001, track_002, track_003, track_005, track_006, track_009, track_010, track_011).
- B:track_011 stays anonymous (U8): ambiguous: 8 persistent tracks of B are compatible with the contact (track_001, track_002, track_003, track_005, track_006, track_009, track_010, track_011).
- B:track_012 stays anonymous (U10): tracked for 0.40 s before the matched collision (needs 1.00 s).
- B:track_013 stays anonymous (U11): tracked for 0.00 s before the matched collision (needs 1.00 s); first seen 0.30 s after the matched collision; range trend before the contact not measurable; speed not comparable with A's own speed before the collision.
- B:track_014 stays anonymous (U12): tracked for 0.00 s before the matched collision (needs 1.00 s); first seen 3.60 s after the matched collision; range trend before the contact not measurable; speed not comparable with A's own speed before the collision.
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
