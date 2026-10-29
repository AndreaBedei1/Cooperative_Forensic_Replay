# Reconstruction report - S19/run_0_highway_curve

Inputs: `vehicles/A/`, `vehicles/B/` (vehicle-local files) and the supplied `incident_context.json`. `ground_truth/` and the run's `metadata.json` were not read; the privileged comparison, if run, is in `evaluation/`.

Speed limit 90 km/h, supplied as incident context: known a priori, not perceived and not ground truth.

Pipeline: raw log -> local trace -> local graph (each recorder alone, own clock, own frame) -> graph-level alignment -> identity association -> road users in the common frame of the recorders' own pose streams -> global graph.

## Local reconstructions

| Recorder | Duration (local) | Trace frames | Graph nodes | Graph edges | Radar tracks | Collision reports (local time) |
|----------|-----------------:|-------------:|------------:|------------:|-------------:|-------------------------------|
| A | 11.95 s | 121 | 38 | 69 | 11 | A:e24 @ 7.50 s |
| B | 11.95 s | 121 | 32 | 53 | 7 | B:e21 @ 7.50 s |

## Graph alignment

Reference event: `collision_001` (t_global = 0); `t_global = t_local + offset_to_global`. A graph that did not report it is aligned through the chain of matched collisions linking it to the reference (multi-hop); its anchor is its own report of the last collision of that chain.

| Graph | Status | Anchor node | Anchor local time | Offset to global | Note |
|-------|--------|-------------|------------------:|-----------------:|------|
| A | ALIGNED | A:e24 | 7.50 | -7.50 | reported the reference collision collision_001 |
| B | ALIGNED | B:e21 | 7.50 | -7.50 | reported the reference collision collision_001 |

Estimated relative clock offsets: B - A = +0.000 s

Matched `collision_001`: A and B both recorded a collision; peak impulses 7479.37 vs 7479.37 N*s (similarity 1.000, tolerance 0.10); no competing report within tolerance; the two bodies touch at their reports (0.00 m apart, tolerance 1.0 m); independent relative impulse std 0.100; combined z 0.000 (gate 3.0); engineering assumption; pre-contact radar view of each recorder checked against the candidate partner's own speed: not contradicted

## Identity associations

| Local track | Global entity | Status | Confidence | Evidence |
|-------------|---------------|--------|-----------:|----------|
| A:track_001 | U1 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 7479.37 vs 7479.37 N*s)<br>tracked for 7.50 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>not approaching before the contact: clearance 10.3 m -> 14.4 m over the last 1.0 s<br>track motion contradicts B's own speed in the observed direction (3 sigma; full-speed RMSE 6.84 m/s for reference)<br>clearance at the contact 10.27 m (beyond 3.50 m: confidence factor 0.08)<br>anonymous road user U1: A:track_001, B:track_003 |
| A:track_002 | U2 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 7479.37 vs 7479.37 N*s)<br>tracked for 7.50 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 5.9 m -> 5.1 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 1.89 m/s for reference)<br>clearance at the contact 5.04 m (beyond 3.50 m: confidence factor 0.88)<br>ambiguous: 2 persistent tracks of A are compatible with the contact (track_002, track_006)<br>anonymous road user U2: A:track_002, B:track_004 |
| A:track_003 | U3 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 7479.37 vs 7479.37 N*s)<br>tracked for 7.50 s before the matched collision<br>lost 1.30 s before the matched collision (window 1.00 s)<br>not approaching before the contact: clearance 63.9 m -> 67.9 m over the last 1.0 s<br>track motion contradicts B's own speed in the observed direction (3 sigma; full-speed RMSE 5.77 m/s for reference)<br>anonymous road user U3: A:track_003, B:track_001 |
| A:track_004 | U4 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 7479.37 vs 7479.37 N*s)<br>tracked for 7.50 s before the matched collision<br>lost 5.15 s before the matched collision (window 1.00 s)<br>not approaching before the contact: clearance 12.3 m -> 15.3 m over the last 1.0 s<br>speed not comparable with B's own speed before the collision<br>anonymous road user U4: A:track_004 |
| A:track_005 | U6 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 7479.37 vs 7479.37 N*s)<br>tracked for 7.45 s before the matched collision<br>lost 6.90 s before the matched collision (window 1.00 s)<br>approaching before the contact: clearance 84.2 m -> 83.9 m over the last 1.0 s<br>speed not comparable with B's own speed before the collision<br>anonymous road user U6: A:track_005 |
| A:track_006 | B | ASSOCIATED | 1.00 | A and B both reported collision_001 (peak impulse 7479.37 vs 7479.37 N*s)<br>tracked for 7.20 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 5.0 m -> 0.2 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 0.09 m/s for reference)<br>clearance at the contact 0.16 m<br>the only compatible track of A touching it at the contact (clearance 0.16 m; track_002 at 5.09 m) |
| A:track_007 | U5 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 7479.37 vs 7479.37 N*s)<br>tracked for 6.10 s before the matched collision<br>lost 5.45 s before the matched collision (window 1.00 s)<br>not approaching before the contact: clearance 84.9 m -> 84.9 m over the last 1.0 s<br>speed not comparable with B's own speed before the collision<br>anonymous road user U5: B:track_002, A:track_007, A:track_008, A:track_009 |
| A:track_008 | U5 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 7479.37 vs 7479.37 N*s)<br>tracked for 5.00 s before the matched collision<br>lost 4.50 s before the matched collision (window 1.00 s)<br>not approaching before the contact: clearance 85.2 m -> 85.2 m over the last 1.0 s<br>speed not comparable with B's own speed before the collision<br>anonymous road user U5: B:track_002, A:track_007, A:track_008, A:track_009 |
| A:track_009 | U5 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 7479.37 vs 7479.37 N*s)<br>tracked for 4.15 s before the matched collision<br>lost 3.80 s before the matched collision (window 1.00 s)<br>not approaching before the contact: clearance 85.6 m -> 85.7 m over the last 1.0 s<br>speed not comparable with B's own speed before the collision<br>anonymous road user U5: B:track_002, A:track_007, A:track_008, A:track_009 |
| A:track_010 | U7 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 7479.37 vs 7479.37 N*s)<br>tracked for 0.00 s before the matched collision (needs 1.00 s)<br>first seen 0.25 s after the matched collision<br>range trend before the contact not measurable<br>speed not comparable with B's own speed before the collision<br>anonymous road user U7: A:track_010 |
| A:track_011 | U8 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 7479.37 vs 7479.37 N*s)<br>tracked for 0.00 s before the matched collision (needs 1.00 s)<br>first seen 1.20 s after the matched collision<br>range trend before the contact not measurable<br>speed not comparable with B's own speed before the collision<br>anonymous road user U8: A:track_011, B:track_007 |
| B:track_001 | U3 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 7479.37 vs 7479.37 N*s)<br>tracked for 7.50 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>not approaching before the contact: clearance 60.4 m -> 69.1 m over the last 1.0 s<br>track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 4.05 m/s for reference)<br>clearance at the contact 60.41 m (beyond 3.50 m: confidence factor 0.00)<br>anonymous road user U3: A:track_003, B:track_001 |
| B:track_002 | U5 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 7479.37 vs 7479.37 N*s)<br>tracked for 7.50 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>not approaching before the contact: clearance 75.2 m -> 79.8 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 1.02 m/s for reference)<br>clearance at the contact 75.19 m (beyond 3.50 m: confidence factor 0.00)<br>anonymous road user U5: B:track_002, A:track_007, A:track_008, A:track_009 |
| B:track_003 | U1 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 7479.37 vs 7479.37 N*s)<br>tracked for 7.50 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>not approaching before the contact: clearance 3.3 m -> 10.6 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 3.56 m/s for reference)<br>clearance at the contact 3.31 m<br>anonymous road user U1: A:track_001, B:track_003 |
| B:track_004 | U2 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 7479.37 vs 7479.37 N*s)<br>tracked for 7.50 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>not approaching before the contact: clearance 2.8 m -> 4.5 m over the last 1.0 s<br>track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 2.47 m/s for reference)<br>clearance at the contact 2.84 m<br>anonymous road user U2: A:track_002, B:track_004 |
| B:track_005 | A | ASSOCIATED | 0.90 | B and A both reported collision_001 (peak impulse 7479.37 vs 7479.37 N*s)<br>tracked for 2.05 s before the matched collision<br>continuous up to the contact: last observed 0.90 s before it (window 1.00 s)<br>approaching before the contact: clearance 7.9 m -> 4.8 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 0.07 m/s for reference)<br>clearance at the contact 4.85 m (beyond 3.50 m: confidence factor 0.90)<br>the only track of B compatible with the contact |
| B:track_006 | U9 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 7479.37 vs 7479.37 N*s)<br>tracked for 0.00 s before the matched collision (needs 1.00 s)<br>first seen 1.25 s after the matched collision<br>range trend before the contact not measurable<br>speed not comparable with A's own speed before the collision<br>anonymous road user U9: B:track_006 |
| B:track_007 | U8 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 7479.37 vs 7479.37 N*s)<br>tracked for 0.00 s before the matched collision (needs 1.00 s)<br>first seen 2.00 s after the matched collision<br>range trend before the contact not measurable<br>speed not comparable with A's own speed before the collision<br>anonymous road user U8: A:track_011, B:track_007 |

## Road users in the common frame

- U1 (anonymous, -7.50 to 3.65 s): A:track_001, B:track_003 joined by same box A:track_001-B:track_003 (98% of 147 instants); footprint 4.54 x 1.90 m (fitted/prior); fusion box_fit+covariance_intersection.
- U2 (anonymous, -7.50 to 4.45 s): A:track_002, B:track_004 joined by same box A:track_002-B:track_004 (100% of 178 instants); footprint 4.34 x 1.90 m (fitted/prior); fusion box_fit+covariance_intersection.
- U3 (anonymous, -7.50 to 0.20 s): A:track_003, B:track_001 joined by same box A:track_003-B:track_001 (100% of 26 instants); footprint 4.60 x 1.90 m (prior/prior); fusion box_fit+covariance_intersection.
- U4 (anonymous, -7.50 to -5.15 s): A:track_004; footprint 4.60 x 1.90 m (prior/prior); fusion box_fit+covariance_intersection.
- U5 (anonymous, -7.50 to 0.20 s): B:track_002, A:track_007, A:track_008, A:track_009 joined by stitch A:track_007-A:track_008 (100% of 1 instants); same box A:track_008-B:track_002 (100% of 8 instants); stitch A:track_008-A:track_009 (100% of 1 instants); footprint 4.60 x 1.90 m (prior/prior); fusion box_fit+covariance_intersection.
- U6 (anonymous, -7.45 to -6.90 s): A:track_005; footprint 4.60 x 1.90 m (prior/prior); fusion covariance_intersection.
- U7 (anonymous, 0.25 to 0.95 s): A:track_010; footprint 4.60 x 1.90 m (prior/prior); fusion covariance_intersection.
- U8 (anonymous, 1.20 to 4.45 s): A:track_011, B:track_007 joined by same box A:track_011-B:track_007 (96% of 22 instants); footprint 4.49 x 1.90 m (fitted/prior); fusion box_fit+covariance_intersection.
- U9 (anonymous, 1.25 to 1.50 s): B:track_006; footprint 4.60 x 1.90 m (prior/prior); fusion covariance_intersection.

## Global graph

70 nodes, 133 edges; 23 merged node(s): g05 TRACK_APPEARED_LEFT(A,U1) from A:e03 + A:e31, g06 TRACK_APPEARED_LEFT(A,U3) from A:e04 + A:e21, g07 TRACK_APPEARED_LEFT(B,U1) from B:e05 + B:e32, g08 TRACK_APPEARED_LEFT(B,U3) from B:e03 + B:e23, g09 TRACK_APPEARED_LEFT(B,U5) from B:e04 + B:e24, g10 TRACK_APPEARED_RIGHT(A,U2) from A:e05 + A:e38, g11 TRACK_APPEARED_RIGHT(A,U4) from A:e06 + A:e14, g13 CLOSING_START(A,U2) from A:e07 + A:e23, g14 CLOSING_START(B,U1) from B:e07 + B:e08, g15 TRACK_APPEARED_LEFT(A,U6) from A:e08 + A:e11, g17 CLOSING_START(A,B) from A:e10 + A:e26, g19 TRACK_APPEARED_LEFT(A,U5) from A:e12 + A:e13, g22 TRACK_APPEARED_LEFT(A,U5) from A:e15 + A:e16, g24 TRACK_APPEARED_LEFT(A,U5) from A:e17 + A:e18, g27 TRACK_APPEARED_LEFT(B,A) from B:e09 + B:e19, g30 CRITICAL_TTC_START(A,B) from A:e19 + A:e25, g31 CUT_IN_FROM_RIGHT_START(A,B) from A:e20 + A:e30, g32 CLOSING_START(B,U1) from B:e12 + B:e15, g44 COLLISION(A,B) from A:e24 + B:e21, g53 TRACK_APPEARED_LEFT(A,U7) from A:e29 + A:e32, g58 CLOSING_START(A,U8) from A:e34 + A:e37, g59 TRACK_APPEARED_LEFT(B,U9) from B:e25 + B:e26, g66 CLOSING_START(B,U8) from B:e30 + B:e31.

### Event sequence (global time)

- `-7.50` MOVING_START(A); MOVING_START(B); THROTTLE_START(A); THROTTLE_START(B); TRACK_APPEARED_LEFT(A,U1); TRACK_APPEARED_LEFT(A,U3); TRACK_APPEARED_LEFT(B,U1); TRACK_APPEARED_LEFT(B,U3); TRACK_APPEARED_LEFT(B,U5); TRACK_APPEARED_RIGHT(A,U2); TRACK_APPEARED_RIGHT(A,U4); TRACK_APPEARED_RIGHT(B,U2); CLOSING_START(A,U2); CLOSING_START(B,U1)
- `-7.45` TRACK_APPEARED_LEFT(A,U6)
- `-7.20` TRACK_APPEARED_FRONT(A,B); CLOSING_START(A,B)
- `-6.90` TRACK_LOST(A,U6)
- `-6.10` TRACK_APPEARED_LEFT(A,U5)
- `-5.45` TRACK_LOST(A,U5)
- `-5.15` TRACK_LOST(A,U4)
- `-5.00` TRACK_APPEARED_LEFT(A,U5)
- `-4.50` TRACK_LOST(A,U5)
- `-4.15` TRACK_APPEARED_LEFT(A,U5)
- `-3.80` TRACK_LOST(A,U5)
- `-2.15` CLOSING_END(B,U1)
- `-2.05` TRACK_APPEARED_LEFT(B,A); CLOSING_START(B,A)
- `-2.00` TURN_LEFT_START(B); CRITICAL_TTC_START(A,B); CUT_IN_FROM_RIGHT_START(A,B)
- `-1.85` CLOSING_START(B,U1)
- `-1.55` CRITICAL_TTC_START(B,A)
- `-1.45` EGO_PATH_ENTRY(B,U5)
- `-1.30` TRACK_LOST(A,U3)
- `-1.20` EGO_PATH_ENTRY(A,B)
- `-1.15` CLOSING_END(B,U1)
- `-1.00` TURN_LEFT_END(B)
- `-0.95` THROTTLE_END(B); BRAKE_START(B)
- `-0.90` TRACK_LOST(B,A)
- `-0.10` CLOSING_END(A,U2); THROTTLE_START(B)
- `+0.00` COLLISION(A,B); CRITICAL_TTC_END(A,B); CRITICAL_TTC_END(B,A); CLOSING_END(A,B); THROTTLE_END(B)
- `+0.05` THROTTLE_END(A); BRAKE_START(A)
- `+0.20` TRACK_LOST(B,U3); TRACK_LOST(B,U5)
- `+0.25` TRACK_APPEARED_LEFT(A,U7)
- `+0.85` CUT_IN_FROM_RIGHT_END(A,B)
- `+0.95` TRACK_LOST(A,U1); TRACK_LOST(A,U7)
- `+1.20` TRACK_APPEARED_RIGHT(A,U8); CLOSING_START(A,U8)
- `+1.25` TRACK_APPEARED_LEFT(B,U9)
- `+1.45` MOVING_END(A); STOP_START(A)
- `+1.50` TRACK_LOST(B,U9)
- `+1.55` MOVING_END(B); STOP_START(B)
- `+2.00` TRACK_APPEARED_RIGHT(B,U8); CLOSING_START(B,U8)
- `+2.80` CLOSING_END(A,U8)
- `+2.85` CLOSING_END(B,U8)
- `+3.65` TRACK_LOST(B,U1)
- `+4.40` TRACK_LOST(A,U2)

### What happened, in plain language

- 7.50 s before the reference collision, A started moving (already the case when first observed).
- 7.50 s before the reference collision, B started moving (already the case when first observed).
- 7.50 s before the reference collision, A pressed the accelerator (already the case when first observed).
- 7.50 s before the reference collision, B pressed the accelerator (already the case when first observed).
- 7.50 s before the reference collision, A's radar started tracking anonymous road user U1, which appeared on its left.
- 7.50 s before the reference collision, A's radar started tracking anonymous road user U3, which appeared on its left.
- 7.50 s before the reference collision, B's radar started tracking anonymous road user U1, which appeared on its left.
- 7.50 s before the reference collision, B's radar started tracking anonymous road user U3, which appeared on its left.
- 7.50 s before the reference collision, B's radar started tracking anonymous road user U5, which appeared on its left.
- 7.50 s before the reference collision, A's radar started tracking anonymous road user U2, which appeared on its right.
- 7.50 s before the reference collision, A's radar started tracking anonymous road user U4, which appeared on its right.
- 7.50 s before the reference collision, B's radar started tracking anonymous road user U2, which appeared on its right.
- 7.50 s before the reference collision, A observed anonymous road user U2 start closing in (already the case when first observed).
- 7.50 s before the reference collision, B observed anonymous road user U1 start closing in (already the case when first observed).
- 7.45 s before the reference collision, A's radar started tracking anonymous road user U6, which appeared on its left.
- 7.20 s before the reference collision, A's radar started tracking B, which appeared in front of it.
- 7.20 s before the reference collision, A observed B start closing in (already the case when first observed).
- 6.90 s before the reference collision, A's radar lost anonymous road user U6 (its states are UNKNOWN from then on, not ended).
- 6.10 s before the reference collision, A's radar started tracking anonymous road user U5, which appeared on its left.
- 5.45 s before the reference collision, A's radar lost anonymous road user U5 (its states are UNKNOWN from then on, not ended).
- 5.15 s before the reference collision, A's radar lost anonymous road user U4 (its states are UNKNOWN from then on, not ended).
- 5.00 s before the reference collision, A's radar started tracking anonymous road user U5, which appeared on its left.
- 4.50 s before the reference collision, A's radar lost anonymous road user U5 (its states are UNKNOWN from then on, not ended).
- 4.15 s before the reference collision, A's radar started tracking anonymous road user U5, which appeared on its left.
- 3.80 s before the reference collision, A's radar lost anonymous road user U5 (its states are UNKNOWN from then on, not ended).
- 2.15 s before the reference collision, B observed anonymous road user U1 stop closing in.
- 2.05 s before the reference collision, B's radar started tracking A, which appeared on its left.
- 2.05 s before the reference collision, B observed A start closing in (already the case when first observed).
- 2.00 s before the reference collision, B started turning left.
- 2.00 s before the reference collision, A's time-to-contact with B became critical.
- 2.00 s before the reference collision, A observed B cutting in from the right.
- 1.85 s before the reference collision, B observed anonymous road user U1 start closing in.
- 1.55 s before the reference collision, B's time-to-contact with A became critical.
- 1.45 s before the reference collision, B observed anonymous road user U5 enter its forward path corridor.
- 1.30 s before the reference collision, A's radar lost anonymous road user U3 (its states are UNKNOWN from then on, not ended).
- 1.20 s before the reference collision, A observed B enter its forward path corridor.
- 1.15 s before the reference collision, B observed anonymous road user U1 stop closing in.
- 1.00 s before the reference collision, B stopped turning left.
- 0.95 s before the reference collision, B released the accelerator.
- 0.95 s before the reference collision, B started braking.
- 0.90 s before the reference collision, B's radar lost A (its states are UNKNOWN from then on, not ended).
- 0.10 s before the reference collision, A observed anonymous road user U2 stop closing in.
- 0.10 s before the reference collision, B pressed the accelerator.
- At the reference collision, A and B both recorded this same collision (peak impulses A: 7479, B: 7479 N*s).
- At the reference collision, A's time-to-contact with B stopped being critical.
- At the reference collision, B's time-to-contact with A stopped being critical.
- At the reference collision, A observed B stop closing in.
- At the reference collision, B released the accelerator.
- 0.05 s after the reference collision, A released the accelerator.
- 0.05 s after the reference collision, A started braking.
- 0.20 s after the reference collision, B's radar lost anonymous road user U3 (its states are UNKNOWN from then on, not ended).
- 0.20 s after the reference collision, B's radar lost anonymous road user U5 (its states are UNKNOWN from then on, not ended).
- 0.25 s after the reference collision, A's radar started tracking anonymous road user U7, which appeared on its left.
- 0.85 s after the reference collision, A observed B's cut-in from the right settle.
- 0.95 s after the reference collision, A's radar lost anonymous road user U1 (its states are UNKNOWN from then on, not ended).
- 0.95 s after the reference collision, A's radar lost anonymous road user U7 (its states are UNKNOWN from then on, not ended).
- 1.20 s after the reference collision, A's radar started tracking anonymous road user U8, which appeared on its right.
- 1.20 s after the reference collision, A observed anonymous road user U8 start closing in (already the case when first observed).
- 1.25 s after the reference collision, B's radar started tracking anonymous road user U9, which appeared on its left.
- 1.45 s after the reference collision, A stopped moving.
- 1.45 s after the reference collision, A came to a stop.
- 1.50 s after the reference collision, B's radar lost anonymous road user U9 (its states are UNKNOWN from then on, not ended).
- 1.55 s after the reference collision, B stopped moving.
- 1.55 s after the reference collision, B came to a stop.
- 2.00 s after the reference collision, B's radar started tracking anonymous road user U8, which appeared on its right.
- 2.00 s after the reference collision, B observed anonymous road user U8 start closing in (already the case when first observed).
- 2.80 s after the reference collision, A observed anonymous road user U8 stop closing in.
- 2.85 s after the reference collision, B observed anonymous road user U8 stop closing in.
- 3.65 s after the reference collision, B's radar lost anonymous road user U1 (its states are UNKNOWN from then on, not ended).
- 4.40 s after the reference collision, A's radar lost anonymous road user U2 (its states are UNKNOWN from then on, not ended).

### Temporal safety relations

CUT_IN_START < CRITICAL_TTC_START < COLLISION, or CRITICAL_TTC_START <= CUT_IN_START (critical TTC already active), and EGO_PATH_ENTRY before/after the critical TTC. Temporal order only, not causes.

- A's track_006 (B): critical TTC already active before the cut-in: CRITICAL_TTC_START 5.50 <= CUT_IN_FROM_RIGHT_START 5.50 (+0.00 s); EGO_PATH_ENTRY 6.30 after critical TTC (+0.80 s) [local times; t_global: cut_in -2.00, critical_ttc_start -2.00, ego_path_entry -1.20, collision +0.00]
- B's track_002 (unidentified U5): EGO_PATH_ENTRY 6.05, no critical TTC [local times; t_global: ego_path_entry -1.45, collision +0.00]
- B's track_005 (A): CRITICAL_TTC_START 5.95, COLLISION with A 7.50 (+1.55 s) [local times; t_global: critical_ttc_start -1.55, collision +0.00]

### Simultaneous events (order unresolved at 0.05 s)

- MOVING_START(A); MOVING_START(B); THROTTLE_START(A); THROTTLE_START(B); TRACK_APPEARED_LEFT(A,U1); TRACK_APPEARED_LEFT(A,U3); TRACK_APPEARED_LEFT(B,U1); TRACK_APPEARED_LEFT(B,U3); TRACK_APPEARED_LEFT(B,U5); TRACK_APPEARED_RIGHT(A,U2); TRACK_APPEARED_RIGHT(A,U4); TRACK_APPEARED_RIGHT(B,U2); CLOSING_START(A,U2); CLOSING_START(B,U1)
- TRACK_APPEARED_FRONT(A,B); CLOSING_START(A,B)
- TRACK_APPEARED_LEFT(B,A); CLOSING_START(B,A)
- TURN_LEFT_START(B); CRITICAL_TTC_START(A,B); CUT_IN_FROM_RIGHT_START(A,B)
- THROTTLE_END(B); BRAKE_START(B)
- CLOSING_END(A,U2); THROTTLE_START(B)
- COLLISION(A,B); CRITICAL_TTC_END(A,B); CRITICAL_TTC_END(B,A); CLOSING_END(A,B); THROTTLE_END(B)
- THROTTLE_END(A); BRAKE_START(A)
- TRACK_LOST(B,U3); TRACK_LOST(B,U5)
- TRACK_LOST(A,U1); TRACK_LOST(A,U7)
- TRACK_APPEARED_RIGHT(A,U8); CLOSING_START(A,U8)
- MOVING_END(A); STOP_START(A)
- MOVING_END(B); STOP_START(B)
- TRACK_APPEARED_RIGHT(B,U8); CLOSING_START(B,U8)

### States still active when observation ended

A:
- EGO_PATH of track_006, since A:e22 (t = 6.30 s)
- BRAKE, since A:e28 (t = 7.55 s)
- STOP, since A:e36 (t = 8.95 s)
B:
- CLOSING of track_005, since B:e10 (t = 5.45 s); the track was lost at 6.60 s
- CRITICAL_TTC of track_005, since B:e13 (t = 5.95 s); the track was lost at 6.60 s
- EGO_PATH of track_002, since B:e14 (t = 6.05 s); the track was lost at 7.70 s
- BRAKE, since B:e18 (t = 6.55 s)
- STOP, since B:e28 (t = 9.05 s)

### Sign detection windows

A:
- none
B:
- none

### Perceived state just before each collision report

- A A:e24 at 7.50 s (local): ego: MOVING, THROTTLE; track_001: no active state; track_002: no active state; track_006: CLOSING, CRITICAL_TTC, IN_EGO_PATH, CUT_IN_FROM_RIGHT; track lost, states UNKNOWN: track_003, track_004, track_005, track_007, track_008, track_009
- B B:e21 at 7.50 s (local): ego: MOVING, BRAKE, THROTTLE; track_001: no active state; track_002: IN_EGO_PATH; track_003: no active state; track_004: no active state; track lost, states UNKNOWN: track_005

### Tracks lost while a state was active

A lost track's states become UNKNOWN: the recorder can no longer tell whether they ended.

A:
- track_005 at 0.60 s (A:e11): IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)
- track_007 at 2.05 s (A:e13): IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)
- track_008 at 3.00 s (A:e16): IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)
- track_009 at 3.70 s (A:e18): IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)
- lost with no state active: track_004, track_003, track_001, track_010, track_002
B:
- track_005 at 6.60 s (B:e19): CLOSING, CRITICAL_TTC were true; they are UNKNOWN afterwards (no END recorded)
- track_002 at 7.70 s (B:e24): IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)
- lost with no state active: track_001, track_006, track_003

## Uncertainty and limitations

- A:track_001 stays anonymous (U1): not approaching before the contact: clearance 10.3 m -> 14.4 m over the last 1.0 s; track motion contradicts B's own speed in the observed direction (3 sigma; full-speed RMSE 6.84 m/s for reference).
- A:track_002 stays anonymous (U2): ambiguous: 2 persistent tracks of A are compatible with the contact (track_002, track_006).
- A:track_003 stays anonymous (U3): lost 1.30 s before the matched collision (window 1.00 s); not approaching before the contact: clearance 63.9 m -> 67.9 m over the last 1.0 s; track motion contradicts B's own speed in the observed direction (3 sigma; full-speed RMSE 5.77 m/s for reference).
- A:track_004 stays anonymous (U4): lost 5.15 s before the matched collision (window 1.00 s); not approaching before the contact: clearance 12.3 m -> 15.3 m over the last 1.0 s; speed not comparable with B's own speed before the collision.
- A:track_005 stays anonymous (U6): lost 6.90 s before the matched collision (window 1.00 s); speed not comparable with B's own speed before the collision.
- A:track_007 stays anonymous (U5): lost 5.45 s before the matched collision (window 1.00 s); not approaching before the contact: clearance 84.9 m -> 84.9 m over the last 1.0 s; speed not comparable with B's own speed before the collision.
- A:track_008 stays anonymous (U5): lost 4.50 s before the matched collision (window 1.00 s); not approaching before the contact: clearance 85.2 m -> 85.2 m over the last 1.0 s; speed not comparable with B's own speed before the collision.
- A:track_009 stays anonymous (U5): lost 3.80 s before the matched collision (window 1.00 s); not approaching before the contact: clearance 85.6 m -> 85.7 m over the last 1.0 s; speed not comparable with B's own speed before the collision.
- A:track_010 stays anonymous (U7): tracked for 0.00 s before the matched collision (needs 1.00 s); first seen 0.25 s after the matched collision; range trend before the contact not measurable; speed not comparable with B's own speed before the collision.
- A:track_011 stays anonymous (U8): tracked for 0.00 s before the matched collision (needs 1.00 s); first seen 1.20 s after the matched collision; range trend before the contact not measurable; speed not comparable with B's own speed before the collision.
- B:track_001 stays anonymous (U3): not approaching before the contact: clearance 60.4 m -> 69.1 m over the last 1.0 s; track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 4.05 m/s for reference).
- B:track_002 stays anonymous (U5): not approaching before the contact: clearance 75.2 m -> 79.8 m over the last 1.0 s.
- B:track_003 stays anonymous (U1): not approaching before the contact: clearance 3.3 m -> 10.6 m over the last 1.0 s.
- B:track_004 stays anonymous (U2): not approaching before the contact: clearance 2.8 m -> 4.5 m over the last 1.0 s; track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 2.47 m/s for reference).
- B:track_006 stays anonymous (U9): tracked for 0.00 s before the matched collision (needs 1.00 s); first seen 1.25 s after the matched collision; range trend before the contact not measurable; speed not comparable with A's own speed before the collision.
- B:track_007 stays anonymous (U8): tracked for 0.00 s before the matched collision (needs 1.00 s); first seen 2.00 s after the matched collision; range trend before the contact not measurable; speed not comparable with A's own speed before the collision.
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
