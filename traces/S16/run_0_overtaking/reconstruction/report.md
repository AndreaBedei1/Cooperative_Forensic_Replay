# Reconstruction report - S16/run_0_overtaking

Inputs: `vehicles/A/`, `vehicles/B/` (vehicle-local files) and the supplied `incident_context.json`. `ground_truth/` and the run's `metadata.json` were not read; the privileged comparison, if run, is in `evaluation/`.

Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.

Pipeline: raw log -> local trace -> local graph (each recorder alone, own clock, own frame) -> graph-level alignment -> identity association -> road users in the common frame of the recorders' own pose streams -> global graph.

## Local reconstructions

| Recorder | Duration (local) | Trace frames | Graph nodes | Graph edges | Radar tracks | Collision reports (local time) |
|----------|-----------------:|-------------:|------------:|------------:|-------------:|-------------------------------|
| A | 11.95 s | 121 | 42 | 90 | 11 | A:e25 @ 6.75 s |
| B | 11.95 s | 121 | 40 | 84 | 10 | B:e23 @ 6.75 s |

## Graph alignment

Reference event: `collision_001` (t_global = 0); `t_global = t_local + offset_to_global`. A graph that did not report it is aligned through the chain of matched collisions linking it to the reference (multi-hop); its anchor is its own report of the last collision of that chain.

| Graph | Status | Anchor node | Anchor local time | Offset to global | Note |
|-------|--------|-------------|------------------:|-----------------:|------|
| A | ALIGNED | A:e25 | 6.75 | -6.75 | reported the reference collision collision_001 |
| B | ALIGNED | B:e23 | 6.75 | -6.75 | reported the reference collision collision_001 |

Estimated relative clock offsets: B - A = +0.000 s

Matched `collision_001`: A and B both recorded a collision; peak impulses 191.84 vs 191.84 N*s (similarity 1.000, tolerance 0.10); no competing report within tolerance; the two bodies touch at their reports (0.00 m apart, tolerance 1.0 m); independent relative impulse std 0.100; combined z 0.000 (gate 3.0); engineering assumption; pre-contact radar view of each recorder checked against the candidate partner's own speed: not contradicted

## Identity associations

| Local track | Global entity | Status | Confidence | Evidence |
|-------------|---------------|--------|-----------:|----------|
| A:track_001 | U1 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 191.84 vs 191.84 N*s)<br>tracked for 6.75 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>not approaching before the contact: clearance 10.5 m -> 12.5 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 0.10 m/s for reference)<br>clearance at the contact 10.48 m (beyond 3.50 m: confidence factor 0.07)<br>anonymous road user U1: A:track_001, B:track_005 |
| A:track_002 | U2 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 191.84 vs 191.84 N*s)<br>tracked for 6.75 s before the matched collision<br>lost 3.15 s before the matched collision (window 1.00 s)<br>not approaching before the contact: clearance 21.4 m -> 23.5 m over the last 1.0 s<br>speed not comparable with B's own speed before the collision<br>anonymous road user U2: A:track_002 |
| A:track_003 | U3 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 191.84 vs 191.84 N*s)<br>tracked for 6.75 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>not approaching before the contact: clearance 11.9 m -> 12.3 m over the last 1.0 s<br>track motion contradicts B's own speed in the observed direction (3 sigma; full-speed RMSE 1.94 m/s for reference)<br>clearance at the contact 11.91 m (beyond 3.50 m: confidence factor 0.02)<br>anonymous road user U3: A:track_003, B:track_002 |
| A:track_004 | U4 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 191.84 vs 191.84 N*s)<br>tracked for 6.75 s before the matched collision<br>lost 3.15 s before the matched collision (window 1.00 s)<br>approaching before the contact: clearance 26.6 m -> 24.7 m over the last 1.0 s<br>speed not comparable with B's own speed before the collision<br>retrospective: identity resolved from later evidence at -1.45 s (entity seen by several observers), carried back 1.70 s with the motion model; posterior 0.976 against 2 candidate(s) and a new road user; observation times unchanged<br>anonymous road user U4: A:track_004, A:track_007, B:track_006 |
| A:track_005 | U5 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 191.84 vs 191.84 N*s)<br>tracked for 6.75 s before the matched collision<br>lost 6.25 s before the matched collision (window 1.00 s)<br>not approaching before the contact: clearance 6.4 m -> 7.4 m over the last 1.0 s<br>speed not comparable with B's own speed before the collision<br>anonymous road user U5: A:track_005 |
| A:track_006 | B | ASSOCIATED | 0.93 | A and B both reported collision_001 (peak impulse 191.84 vs 191.84 N*s)<br>tracked for 6.35 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 1.4 m -> 0.2 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 0.58 m/s for reference)<br>clearance at the contact 0.24 m<br>the only track of A compatible with the contact |
| A:track_007 | U4 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 191.84 vs 191.84 N*s)<br>tracked for 1.45 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 20.6 m -> 19.2 m over the last 1.0 s<br>track motion contradicts B's own speed in the observed direction (3 sigma; full-speed RMSE 4.03 m/s for reference)<br>clearance at the contact 19.20 m (beyond 3.50 m: confidence factor 0.00)<br>anonymous road user U4: A:track_004, A:track_007, B:track_006 |
| A:track_008 | U8 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 191.84 vs 191.84 N*s)<br>tracked for 0.85 s before the matched collision (needs 1.00 s)<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>not approaching before the contact: clearance 28.3 m -> 29.7 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 0.07 m/s for reference)<br>clearance at the contact 28.33 m (beyond 3.50 m: confidence factor 0.00)<br>anonymous road user U8: A:track_008, B:track_007 |
| A:track_009 | U10 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 191.84 vs 191.84 N*s)<br>tracked for 0.00 s before the matched collision (needs 1.00 s)<br>first seen 1.15 s after the matched collision<br>range trend before the contact not measurable<br>speed not comparable with B's own speed before the collision<br>anonymous road user U10: A:track_009 |
| A:track_010 | U12 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 191.84 vs 191.84 N*s)<br>tracked for 0.00 s before the matched collision (needs 1.00 s)<br>first seen 1.55 s after the matched collision<br>range trend before the contact not measurable<br>speed not comparable with B's own speed before the collision<br>anonymous road user U12: A:track_010, B:track_010 |
| A:track_011 | U11 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 191.84 vs 191.84 N*s)<br>tracked for 0.00 s before the matched collision (needs 1.00 s)<br>first seen 1.80 s after the matched collision<br>range trend before the contact not measurable<br>speed not comparable with B's own speed before the collision<br>anonymous road user U11: B:track_009, A:track_011 |
| B:track_001 | A | ASSOCIATED | 0.93 | B and A both reported collision_001 (peak impulse 191.84 vs 191.84 N*s)<br>tracked for 6.75 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 1.3 m -> 0.3 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 0.56 m/s for reference)<br>clearance at the contact 0.30 m<br>the only compatible track of B touching it at the contact (clearance 0.30 m; track_002 at 10.52 m) |
| B:track_002 | U3 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 191.84 vs 191.84 N*s)<br>tracked for 6.75 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 12.4 m -> 10.5 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 0.11 m/s for reference)<br>clearance at the contact 10.52 m (beyond 3.50 m: confidence factor 0.06)<br>ambiguous: 2 persistent tracks of B are compatible with the contact (track_001, track_002)<br>anonymous road user U3: A:track_003, B:track_002 |
| B:track_003 | U6 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 191.84 vs 191.84 N*s)<br>tracked for 6.75 s before the matched collision<br>lost 1.55 s before the matched collision (window 1.00 s)<br>not approaching before the contact: clearance 12.3 m -> 16.2 m over the last 1.0 s<br>track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 1.62 m/s for reference)<br>anonymous road user U6: B:track_003 |
| B:track_004 | U7 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 191.84 vs 191.84 N*s)<br>tracked for 6.55 s before the matched collision<br>lost 3.65 s before the matched collision (window 1.00 s)<br>approaching before the contact: clearance 35.1 m -> 33.1 m over the last 1.0 s<br>speed not comparable with A's own speed before the collision<br>anonymous road user U7: B:track_004 |
| B:track_005 | U1 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 191.84 vs 191.84 N*s)<br>tracked for 6.40 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 10.3 m -> 10.3 m over the last 1.0 s<br>track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 1.94 m/s for reference)<br>clearance at the contact 10.30 m (beyond 3.50 m: confidence factor 0.08)<br>anonymous road user U1: A:track_001, B:track_005 |
| B:track_006 | U4 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 191.84 vs 191.84 N*s)<br>tracked for 1.10 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 21.8 m -> 17.9 m over the last 1.0 s<br>track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 2.04 m/s for reference)<br>clearance at the contact 17.92 m (beyond 3.50 m: confidence factor 0.00)<br>anonymous road user U4: A:track_004, A:track_007, B:track_006 |
| B:track_007 | U8 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 191.84 vs 191.84 N*s)<br>tracked for 0.85 s before the matched collision (needs 1.00 s)<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 28.0 m -> 26.3 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 0.02 m/s for reference)<br>clearance at the contact 26.27 m (beyond 3.50 m: confidence factor 0.00)<br>anonymous road user U8: A:track_008, B:track_007 |
| B:track_008 | U9 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 191.84 vs 191.84 N*s)<br>tracked for 0.55 s before the matched collision (needs 1.00 s)<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 35.8 m -> 33.7 m over the last 1.0 s<br>track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 1.97 m/s for reference)<br>clearance at the contact 33.45 m (beyond 3.50 m: confidence factor 0.00)<br>anonymous road user U9: B:track_008 |
| B:track_009 | U11 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 191.84 vs 191.84 N*s)<br>tracked for 0.00 s before the matched collision (needs 1.00 s)<br>first seen 1.50 s after the matched collision<br>range trend before the contact not measurable<br>speed not comparable with A's own speed before the collision<br>anonymous road user U11: B:track_009, A:track_011 |
| B:track_010 | U12 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 191.84 vs 191.84 N*s)<br>tracked for 0.00 s before the matched collision (needs 1.00 s)<br>first seen 3.45 s after the matched collision<br>range trend before the contact not measurable<br>speed not comparable with A's own speed before the collision<br>anonymous road user U12: A:track_010, B:track_010 |

## Road users in the common frame

- U1 (anonymous, -6.75 to 4.45 s): A:track_001, B:track_005 joined by same box A:track_001-B:track_005 (100% of 145 instants); footprint 4.60 x 1.90 m (prior/prior); fusion box_fit+covariance_intersection.
- U2 (anonymous, -6.75 to -3.15 s): A:track_002; footprint 4.60 x 1.90 m (prior/prior); fusion box_fit+covariance_intersection.
- U3 (anonymous, -6.75 to 5.20 s): A:track_003, B:track_002 joined by same box A:track_003-B:track_002 (100% of 141 instants); footprint 4.60 x 1.90 m (prior/prior); fusion box_fit+covariance_intersection.
- U4 (anonymous, -6.75 to 5.20 s): A:track_004, A:track_007, B:track_006 joined by same box A:track_007-B:track_006 (100% of 30 instants); footprint 4.60 x 1.90 m (prior/prior); fusion box_fit+covariance_intersection.
- U5 (anonymous, -6.75 to -6.25 s): A:track_005; footprint 4.60 x 1.90 m (prior/prior); fusion covariance_intersection.
- U6 (anonymous, -6.75 to -1.55 s): B:track_003; footprint 4.60 x 1.90 m (prior/prior); fusion box_fit+covariance_intersection.
- U7 (anonymous, -6.55 to -3.65 s): B:track_004; footprint 4.60 x 1.90 m (prior/prior); fusion covariance_intersection.
- U8 (anonymous, -0.85 to 5.10 s): A:track_008, B:track_007 joined by same box A:track_008-B:track_007 (71% of 69 instants); footprint 4.60 x 1.90 m (prior/prior); fusion box_fit+covariance_intersection.
- U9 (anonymous, -0.55 to 0.80 s): B:track_008; footprint 4.60 x 1.90 m (prior/prior); fusion covariance_intersection.
- U10 (anonymous, 1.15 to 5.20 s): A:track_009; footprint 4.60 x 1.90 m (prior/prior); fusion covariance_intersection.
- U11 (anonymous, 1.50 to 3.20 s): B:track_009, A:track_011 joined by same box A:track_011-B:track_009 (100% of 12 instants); footprint 4.60 x 1.90 m (prior/prior); fusion box_fit+covariance_intersection.
- U12 (anonymous, 1.55 to 5.20 s): A:track_010, B:track_010 joined by same box A:track_010-B:track_010 (100% of 36 instants); footprint 4.60 x 1.90 m (prior/prior); fusion box_fit+covariance_intersection.

## Global graph

81 nodes, 187 edges; 27 merged node(s): g06 TRACK_APPEARED_LEFT(A,U1) from A:e04 + A:e41, g07 TRACK_APPEARED_LEFT(A,U2) from A:e05 + A:e13, g08 TRACK_APPEARED_RIGHT(A,U4) from A:e06 + A:e14, g09 TRACK_APPEARED_RIGHT(A,U5) from A:e07 + A:e12, g12 TRACK_APPEARED_RIGHT(B,U6) from B:e05 + B:e14, g14 CLOSING_START(B,A) from B:e06 + B:e13, g15 CLOSING_START(B,U3) from B:e07 + B:e29, g16 TRACK_APPEARED_FRONT(B,U7) from B:e08 + B:e12, g18 TRACK_APPEARED_FRONT(B,U1) from B:e10 + B:e39, g20 CLOSING_START(A,B) from A:e10 + A:e15, g21 CRITICAL_TTC_START(A,U3) from A:e11 + A:e31, g23 CRITICAL_TTC_START(B,U1) from B:e11 + B:e32, g29 CRITICAL_TTC_START(A,B) from A:e16 + A:e26, g32 CLOSING_START(A,U4) from A:e18 + A:e30, g34 CLOSING_START(B,U4) from B:e16 + B:e30, g35 CRITICAL_TTC_START(B,A) from B:e17 + B:e24, g36 TRACK_APPEARED_FRONT(A,U8) from A:e19 + A:e42, g37 TRACK_APPEARED_RIGHT(B,U8) from B:e18 + B:e40, g38 CLOSING_START(A,B) from A:e20 + A:e27, g39 CLOSING_START(B,U8) from B:e19 + B:e28, g40 CLOSING_START(B,A) from B:e20 + B:e27, g41 TRACK_APPEARED_RIGHT(B,U9) from B:e21 + B:e33, g42 CLOSING_START(B,U9) from B:e22 + B:e31, g47 COLLISION(A,B) from A:e25 + B:e23, g69 TRACK_APPEARED_LEFT(B,U11) from B:e36 + B:e37, g71 CLOSING_START(A,U12) from A:e36 + A:e40, g72 TRACK_APPEARED_LEFT(A,U11) from A:e37 + A:e39.

### Event sequence (global time)

- `-6.75` MOVING_START(A); MOVING_START(B); THROTTLE_START(A); THROTTLE_START(B); TRACK_APPEARED_FRONT(A,U3); TRACK_APPEARED_LEFT(A,U1); TRACK_APPEARED_LEFT(A,U2); TRACK_APPEARED_RIGHT(A,U4); TRACK_APPEARED_RIGHT(A,U5); TRACK_APPEARED_RIGHT(B,A); TRACK_APPEARED_RIGHT(B,U3); TRACK_APPEARED_RIGHT(B,U6); CLOSING_START(A,U4); CLOSING_START(B,A); CLOSING_START(B,U3)
- `-6.55` TRACK_APPEARED_FRONT(B,U7); CLOSING_START(B,U7)
- `-6.40` TRACK_APPEARED_FRONT(B,U1)
- `-6.35` TRACK_APPEARED_LEFT(A,B); CLOSING_START(A,B)
- `-6.25` CRITICAL_TTC_START(A,U3); TRACK_LOST(A,U5)
- `-5.90` CRITICAL_TTC_START(B,U1)
- `-3.65` TRACK_LOST(B,U7)
- `-3.15` TRACK_LOST(A,U2); TRACK_LOST(A,U4)
- `-2.70` CLOSING_END(A,B)
- `-2.65` CLOSING_END(B,A)
- `-1.60` CRITICAL_TTC_START(A,B)
- `-1.55` TRACK_LOST(B,U6)
- `-1.45` TRACK_APPEARED_RIGHT(A,U4); CLOSING_START(A,U4)
- `-1.10` TRACK_APPEARED_RIGHT(B,U4); CLOSING_START(B,U4); CRITICAL_TTC_START(B,A)
- `-0.85` TRACK_APPEARED_FRONT(A,U8); TRACK_APPEARED_RIGHT(B,U8); CLOSING_START(A,B); CLOSING_START(B,U8)
- `-0.65` CLOSING_START(B,A)
- `-0.55` TRACK_APPEARED_RIGHT(B,U9); CLOSING_START(B,U9)
- `-0.45` EGO_PATH_ENTRY(A,U1); CRITICAL_TTC_START(A,U1)
- `-0.30` EGO_PATH_ENTRY(A,B)
- `-0.25` EGO_PATH_ENTRY(A,U8)
- `+0.00` COLLISION(A,B); CRITICAL_TTC_END(A,B); CRITICAL_TTC_END(B,A)
- `+0.05` CLOSING_END(A,B); THROTTLE_END(A); THROTTLE_END(B); BRAKE_START(A); BRAKE_START(B)
- `+0.10` CLOSING_END(B,A)
- `+0.30` CLOSING_END(B,U8)
- `+0.35` CLOSING_END(B,U3)
- `+0.45` CLOSING_END(A,U4)
- `+0.60` CLOSING_END(B,U4); CLOSING_END(B,U9)
- `+0.70` CRITICAL_TTC_END(A,U3)
- `+0.80` CRITICAL_TTC_END(B,U1); TRACK_LOST(B,U9)
- `+1.15` MOVING_END(B); STOP_START(B); TRACK_APPEARED_FRONT(A,U10)
- `+1.20` MOVING_END(A); STOP_START(A)
- `+1.50` TRACK_APPEARED_LEFT(B,U11)
- `+1.55` TRACK_APPEARED_RIGHT(A,U12); CLOSING_START(A,U12)
- `+1.80` TRACK_APPEARED_LEFT(A,U11)
- `+2.45` EGO_PATH_ENTRY(A,U11)
- `+2.95` TRACK_LOST(B,U11)
- `+3.20` TRACK_LOST(A,U11)
- `+3.45` TRACK_APPEARED_RIGHT(B,U12)
- `+3.60` CLOSING_END(A,U12)
- `+4.35` TRACK_LOST(B,U1)
- `+4.45` TRACK_LOST(A,U1)
- `+4.80` TRACK_LOST(B,U8)
- `+5.10` TRACK_LOST(A,U8)

### What happened, in plain language

- 6.75 s before the reference collision, A started moving (already the case when first observed).
- 6.75 s before the reference collision, B started moving (already the case when first observed).
- 6.75 s before the reference collision, A pressed the accelerator (already the case when first observed).
- 6.75 s before the reference collision, B pressed the accelerator (already the case when first observed).
- 6.75 s before the reference collision, A's radar started tracking anonymous road user U3, which appeared in front of it.
- 6.75 s before the reference collision, A's radar started tracking anonymous road user U1, which appeared on its left.
- 6.75 s before the reference collision, A's radar started tracking anonymous road user U2, which appeared on its left.
- 6.75 s before the reference collision, A's radar started tracking anonymous road user U4, which appeared on its right.
- 6.75 s before the reference collision, A's radar started tracking anonymous road user U5, which appeared on its right.
- 6.75 s before the reference collision, B's radar started tracking A, which appeared on its right.
- 6.75 s before the reference collision, B's radar started tracking anonymous road user U3, which appeared on its right.
- 6.75 s before the reference collision, B's radar started tracking anonymous road user U6, which appeared on its right.
- 6.75 s before the reference collision, A observed anonymous road user U4 start closing in (already the case when first observed).
- 6.75 s before the reference collision, B observed A start closing in (already the case when first observed).
- 6.75 s before the reference collision, B observed anonymous road user U3 start closing in (already the case when first observed).
- 6.55 s before the reference collision, B's radar started tracking anonymous road user U7, which appeared in front of it.
- 6.55 s before the reference collision, B observed anonymous road user U7 start closing in (already the case when first observed).
- 6.40 s before the reference collision, B's radar started tracking anonymous road user U1, which appeared in front of it.
- 6.35 s before the reference collision, A's radar started tracking B, which appeared on its left.
- 6.35 s before the reference collision, A observed B start closing in (already the case when first observed).
- 6.25 s before the reference collision, A's time-to-contact with anonymous road user U3 became critical.
- 6.25 s before the reference collision, A's radar lost anonymous road user U5 (its states are UNKNOWN from then on, not ended).
- 5.90 s before the reference collision, B's time-to-contact with anonymous road user U1 became critical.
- 3.65 s before the reference collision, B's radar lost anonymous road user U7 (its states are UNKNOWN from then on, not ended).
- 3.15 s before the reference collision, A's radar lost anonymous road user U2 (its states are UNKNOWN from then on, not ended).
- 3.15 s before the reference collision, A's radar lost anonymous road user U4 (its states are UNKNOWN from then on, not ended).
- 2.70 s before the reference collision, A observed B stop closing in.
- 2.65 s before the reference collision, B observed A stop closing in.
- 1.60 s before the reference collision, A's time-to-contact with B became critical.
- 1.55 s before the reference collision, B's radar lost anonymous road user U6 (its states are UNKNOWN from then on, not ended).
- 1.45 s before the reference collision, A's radar started tracking anonymous road user U4, which appeared on its right.
- 1.45 s before the reference collision, A observed anonymous road user U4 start closing in (already the case when first observed).
- 1.10 s before the reference collision, B's radar started tracking anonymous road user U4, which appeared on its right.
- 1.10 s before the reference collision, B observed anonymous road user U4 start closing in (already the case when first observed).
- 1.10 s before the reference collision, B's time-to-contact with A became critical.
- 0.85 s before the reference collision, A's radar started tracking anonymous road user U8, which appeared in front of it.
- 0.85 s before the reference collision, B's radar started tracking anonymous road user U8, which appeared on its right.
- 0.85 s before the reference collision, A observed B start closing in.
- 0.85 s before the reference collision, B observed anonymous road user U8 start closing in (already the case when first observed).
- 0.65 s before the reference collision, B observed A start closing in.
- 0.55 s before the reference collision, B's radar started tracking anonymous road user U9, which appeared on its right.
- 0.55 s before the reference collision, B observed anonymous road user U9 start closing in (already the case when first observed).
- 0.45 s before the reference collision, A observed anonymous road user U1 enter its forward path corridor.
- 0.45 s before the reference collision, A's time-to-contact with anonymous road user U1 became critical.
- 0.30 s before the reference collision, A observed B enter its forward path corridor.
- 0.25 s before the reference collision, A observed anonymous road user U8 enter its forward path corridor.
- At the reference collision, A and B both recorded this same collision (peak impulses A: 192, B: 192 N*s).
- At the reference collision, A's time-to-contact with B stopped being critical.
- At the reference collision, B's time-to-contact with A stopped being critical.
- 0.05 s after the reference collision, A observed B stop closing in.
- 0.05 s after the reference collision, A released the accelerator.
- 0.05 s after the reference collision, B released the accelerator.
- 0.05 s after the reference collision, A started braking.
- 0.05 s after the reference collision, B started braking.
- 0.10 s after the reference collision, B observed A stop closing in.
- 0.30 s after the reference collision, B observed anonymous road user U8 stop closing in.
- 0.35 s after the reference collision, B observed anonymous road user U3 stop closing in.
- 0.45 s after the reference collision, A observed anonymous road user U4 stop closing in.
- 0.60 s after the reference collision, B observed anonymous road user U4 stop closing in.
- 0.60 s after the reference collision, B observed anonymous road user U9 stop closing in.
- 0.70 s after the reference collision, A's time-to-contact with anonymous road user U3 stopped being critical.
- 0.80 s after the reference collision, B's time-to-contact with anonymous road user U1 stopped being critical.
- 0.80 s after the reference collision, B's radar lost anonymous road user U9 (its states are UNKNOWN from then on, not ended).
- 1.15 s after the reference collision, B stopped moving.
- 1.15 s after the reference collision, B came to a stop.
- 1.15 s after the reference collision, A's radar started tracking anonymous road user U10, which appeared in front of it.
- 1.20 s after the reference collision, A stopped moving.
- 1.20 s after the reference collision, A came to a stop.
- 1.50 s after the reference collision, B's radar started tracking anonymous road user U11, which appeared on its left.
- 1.55 s after the reference collision, A's radar started tracking anonymous road user U12, which appeared on its right.
- 1.55 s after the reference collision, A observed anonymous road user U12 start closing in (already the case when first observed).
- 1.80 s after the reference collision, A's radar started tracking anonymous road user U11, which appeared on its left.
- 2.45 s after the reference collision, A observed anonymous road user U11 enter its forward path corridor.
- 2.95 s after the reference collision, B's radar lost anonymous road user U11 (its states are UNKNOWN from then on, not ended).
- 3.20 s after the reference collision, A's radar lost anonymous road user U11 (its states are UNKNOWN from then on, not ended).
- 3.45 s after the reference collision, B's radar started tracking anonymous road user U12, which appeared on its right.
- 3.60 s after the reference collision, A observed anonymous road user U12 stop closing in.
- 4.35 s after the reference collision, B's radar lost anonymous road user U1 (its states are UNKNOWN from then on, not ended).
- 4.45 s after the reference collision, A's radar lost anonymous road user U1 (its states are UNKNOWN from then on, not ended).
- 4.80 s after the reference collision, B's radar lost anonymous road user U8 (its states are UNKNOWN from then on, not ended).
- 5.10 s after the reference collision, A's radar lost anonymous road user U8 (its states are UNKNOWN from then on, not ended).

### Temporal safety relations

CUT_IN_START < CRITICAL_TTC_START < COLLISION, or CRITICAL_TTC_START <= CUT_IN_START (critical TTC already active), and EGO_PATH_ENTRY before/after the critical TTC. Temporal order only, not causes.

- A's track_001 (unidentified U1): CRITICAL_TTC_START 6.30, COLLISION 6.75 (+0.45 s); EGO_PATH_ENTRY 6.30 together with critical TTC (+0.00 s) [local times; t_global: critical_ttc_start -0.45, ego_path_entry -0.45, collision +0.00]
- A's track_003 (unidentified U3): CRITICAL_TTC_START 0.50, COLLISION 6.75 (+6.25 s) [local times; t_global: critical_ttc_start -6.25, collision +0.00]
- A's track_006 (B): CRITICAL_TTC_START 5.15, COLLISION with B 6.75 (+1.60 s); EGO_PATH_ENTRY 6.45 after critical TTC (+1.30 s) [local times; t_global: critical_ttc_start -1.60, ego_path_entry -0.30, collision +0.00]
- A's track_008 (unidentified U8): EGO_PATH_ENTRY 6.50, no critical TTC [local times; t_global: ego_path_entry -0.25, collision +0.00]
- A's track_011 (unidentified U11): EGO_PATH_ENTRY 9.20, no critical TTC [local times; t_global: ego_path_entry +2.45]
- B's track_001 (A): CRITICAL_TTC_START 5.65, COLLISION with A 6.75 (+1.10 s) [local times; t_global: critical_ttc_start -1.10, collision +0.00]
- B's track_005 (unidentified U1): CRITICAL_TTC_START 0.85, COLLISION 6.75 (+5.90 s) [local times; t_global: critical_ttc_start -5.90, collision +0.00]

### Simultaneous events (order unresolved at 0.05 s)

- MOVING_START(A); MOVING_START(B); THROTTLE_START(A); THROTTLE_START(B); TRACK_APPEARED_FRONT(A,U3); TRACK_APPEARED_LEFT(A,U1); TRACK_APPEARED_LEFT(A,U2); TRACK_APPEARED_RIGHT(A,U4); TRACK_APPEARED_RIGHT(A,U5); TRACK_APPEARED_RIGHT(B,A); TRACK_APPEARED_RIGHT(B,U3); TRACK_APPEARED_RIGHT(B,U6); CLOSING_START(A,U4); CLOSING_START(B,A); CLOSING_START(B,U3)
- TRACK_APPEARED_FRONT(B,U7); CLOSING_START(B,U7)
- TRACK_APPEARED_LEFT(A,B); CLOSING_START(A,B)
- CRITICAL_TTC_START(A,U3); TRACK_LOST(A,U5)
- TRACK_LOST(A,U2); TRACK_LOST(A,U4)
- TRACK_APPEARED_RIGHT(A,U4); CLOSING_START(A,U4)
- TRACK_APPEARED_RIGHT(B,U4); CLOSING_START(B,U4); CRITICAL_TTC_START(B,A)
- TRACK_APPEARED_FRONT(A,U8); TRACK_APPEARED_RIGHT(B,U8); CLOSING_START(A,B); CLOSING_START(B,U8)
- TRACK_APPEARED_RIGHT(B,U9); CLOSING_START(B,U9)
- EGO_PATH_ENTRY(A,U1); CRITICAL_TTC_START(A,U1)
- COLLISION(A,B); CRITICAL_TTC_END(A,B); CRITICAL_TTC_END(B,A)
- CLOSING_END(A,B); THROTTLE_END(A); THROTTLE_END(B); BRAKE_START(A); BRAKE_START(B)
- CLOSING_END(B,U4); CLOSING_END(B,U9)
- CRITICAL_TTC_END(B,U1); TRACK_LOST(B,U9)
- MOVING_END(B); STOP_START(B); TRACK_APPEARED_FRONT(A,U10)
- MOVING_END(A); STOP_START(A)
- TRACK_APPEARED_RIGHT(A,U12); CLOSING_START(A,U12)

### States still active when observation ended

A:
- CLOSING of track_004, since A:e08 (t = 0.00 s); the track was lost at 3.60 s
- EGO_PATH of track_001, since A:e21 (t = 6.30 s); the track was lost at 11.20 s
- CRITICAL_TTC of track_001, since A:e22 (t = 6.30 s); the track was lost at 11.20 s
- EGO_PATH of track_006, since A:e23 (t = 6.45 s)
- EGO_PATH of track_008, since A:e24 (t = 6.50 s); the track was lost at 11.85 s
- BRAKE, since A:e29 (t = 6.80 s)
- STOP, since A:e34 (t = 7.95 s)
- EGO_PATH of track_011, since A:e38 (t = 9.20 s); the track was lost at 9.95 s
B:
- CLOSING of track_004, since B:e09 (t = 0.20 s); the track was lost at 3.10 s
- BRAKE, since B:e26 (t = 6.80 s)
- STOP, since B:e35 (t = 7.90 s)

### Sign detection windows

A:
- none
B:
- none

### Perceived state just before each collision report

- A A:e25 at 6.75 s (local): ego: MOVING, THROTTLE; track_001: CRITICAL_TTC, IN_EGO_PATH; track_003: CRITICAL_TTC, IN_EGO_PATH; track_006: CLOSING, CRITICAL_TTC, IN_EGO_PATH; track_007: CLOSING; track_008: IN_EGO_PATH; track lost, states UNKNOWN: track_002, track_004, track_005
- B B:e23 at 6.75 s (local): ego: MOVING, THROTTLE; track_001: CLOSING, CRITICAL_TTC; track_002: CLOSING; track_005: CRITICAL_TTC, IN_EGO_PATH; track_006: CLOSING; track_007: CLOSING; track_008: CLOSING; track lost, states UNKNOWN: track_003, track_004

### Tracks lost while a state was active

A lost track's states become UNKNOWN: the recorder can no longer tell whether they ended.

A:
- track_004 at 3.60 s (A:e14): CLOSING were true; they are UNKNOWN afterwards (no END recorded)
- track_011 at 9.95 s (A:e39): IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)
- track_001 at 11.20 s (A:e41): CRITICAL_TTC, IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)
- track_008 at 11.85 s (A:e42): IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)
- lost with no state active: track_005, track_002
B:
- track_004 at 3.10 s (B:e12): CLOSING were true; they are UNKNOWN afterwards (no END recorded)
- track_009 at 9.70 s (B:e37): IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)
- track_005 at 11.10 s (B:e39): IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)
- lost with no state active: track_003, track_008, track_007

## Uncertainty and limitations

- A:track_001 stays anonymous (U1): not approaching before the contact: clearance 10.5 m -> 12.5 m over the last 1.0 s.
- A:track_002 stays anonymous (U2): lost 3.15 s before the matched collision (window 1.00 s); not approaching before the contact: clearance 21.4 m -> 23.5 m over the last 1.0 s; speed not comparable with B's own speed before the collision.
- A:track_003 stays anonymous (U3): not approaching before the contact: clearance 11.9 m -> 12.3 m over the last 1.0 s; track motion contradicts B's own speed in the observed direction (3 sigma; full-speed RMSE 1.94 m/s for reference).
- A:track_004 stays anonymous (U4): lost 3.15 s before the matched collision (window 1.00 s); speed not comparable with B's own speed before the collision.
- A:track_005 stays anonymous (U5): lost 6.25 s before the matched collision (window 1.00 s); not approaching before the contact: clearance 6.4 m -> 7.4 m over the last 1.0 s; speed not comparable with B's own speed before the collision.
- A:track_007 stays anonymous (U4): track motion contradicts B's own speed in the observed direction (3 sigma; full-speed RMSE 4.03 m/s for reference).
- A:track_008 stays anonymous (U8): tracked for 0.85 s before the matched collision (needs 1.00 s); not approaching before the contact: clearance 28.3 m -> 29.7 m over the last 1.0 s.
- A:track_009 stays anonymous (U10): tracked for 0.00 s before the matched collision (needs 1.00 s); first seen 1.15 s after the matched collision; range trend before the contact not measurable; speed not comparable with B's own speed before the collision.
- A:track_010 stays anonymous (U12): tracked for 0.00 s before the matched collision (needs 1.00 s); first seen 1.55 s after the matched collision; range trend before the contact not measurable; speed not comparable with B's own speed before the collision.
- A:track_011 stays anonymous (U11): tracked for 0.00 s before the matched collision (needs 1.00 s); first seen 1.80 s after the matched collision; range trend before the contact not measurable; speed not comparable with B's own speed before the collision.
- B:track_002 stays anonymous (U3): ambiguous: 2 persistent tracks of B are compatible with the contact (track_001, track_002).
- B:track_003 stays anonymous (U6): lost 1.55 s before the matched collision (window 1.00 s); not approaching before the contact: clearance 12.3 m -> 16.2 m over the last 1.0 s; track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 1.62 m/s for reference).
- B:track_004 stays anonymous (U7): lost 3.65 s before the matched collision (window 1.00 s); speed not comparable with A's own speed before the collision.
- B:track_005 stays anonymous (U1): track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 1.94 m/s for reference).
- B:track_006 stays anonymous (U4): track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 2.04 m/s for reference).
- B:track_007 stays anonymous (U8): tracked for 0.85 s before the matched collision (needs 1.00 s).
- B:track_008 stays anonymous (U9): tracked for 0.55 s before the matched collision (needs 1.00 s); track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 1.97 m/s for reference).
- B:track_009 stays anonymous (U11): tracked for 0.00 s before the matched collision (needs 1.00 s); first seen 1.50 s after the matched collision; range trend before the contact not measurable; speed not comparable with A's own speed before the collision.
- B:track_010 stays anonymous (U12): tracked for 0.00 s before the matched collision (needs 1.00 s); first seen 3.45 s after the matched collision; range trend before the contact not measurable; speed not comparable with A's own speed before the collision.
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
