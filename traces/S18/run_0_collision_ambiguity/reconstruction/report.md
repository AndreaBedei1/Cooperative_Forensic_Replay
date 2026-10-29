# Reconstruction report - S18/run_0_collision_ambiguity

Inputs: `vehicles/A/`, `vehicles/B/` (vehicle-local files) and the supplied `incident_context.json`. `ground_truth/` and the run's `metadata.json` were not read; the privileged comparison, if run, is in `evaluation/`.

Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.

Pipeline: raw log -> local trace -> local graph (each recorder alone, own clock, own frame) -> graph-level alignment -> identity association -> road users in the common frame of the recorders' own pose streams -> global graph.

## Local reconstructions

| Recorder | Duration (local) | Trace frames | Graph nodes | Graph edges | Radar tracks | Collision reports (local time) |
|----------|-----------------:|-------------:|------------:|------------:|-------------:|-------------------------------|
| A | 11.95 s | 121 | 39 | 89 | 10 | A:e20 @ 7.65 s |
| B | 11.95 s | 121 | 19 | 30 | 6 | B:e08 @ 7.65 s |

## Graph alignment

Reference event: `collision_001` (t_global = 0); `t_global = t_local + offset_to_global`. A graph that did not report it is aligned through the chain of matched collisions linking it to the reference (multi-hop); its anchor is its own report of the last collision of that chain.

| Graph | Status | Anchor node | Anchor local time | Offset to global | Note |
|-------|--------|-------------|------------------:|-----------------:|------|
| A | ALIGNED | A:e20 | 7.65 | -7.65 | reported the reference collision collision_001 |
| B | ALIGNED | B:e08 | 7.65 | -7.65 | reported the reference collision collision_001 |

Estimated relative clock offsets: B - A = +0.000 s

Matched `collision_001`: A and B both recorded a collision; peak impulses 1168.63 vs 1168.63 N*s (similarity 1.000, tolerance 0.10); no competing report within tolerance; the two bodies touch at their reports (0.00 m apart, tolerance 1.0 m); independent relative impulse std 0.100; combined z 0.000 (gate 3.0); engineering assumption; pre-contact radar view of each recorder checked against the candidate partner's own speed: not contradicted

## Identity associations

| Local track | Global entity | Status | Confidence | Evidence |
|-------------|---------------|--------|-----------:|----------|
| A:track_001 | U1 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 1168.63 vs 1168.63 N*s)<br>tracked for 7.65 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 3.4 m -> 2.2 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 0.12 m/s for reference)<br>clearance at the contact 2.19 m<br>ambiguous: 3 persistent tracks of A are compatible with the contact (track_001, track_002, track_005)<br>anonymous road user U1: A:track_001, B:track_002 |
| A:track_002 | B | ASSOCIATED | 1.00 | A and B both reported collision_001 (peak impulse 1168.63 vs 1168.63 N*s)<br>tracked for 7.65 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 2.1 m -> 0.0 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 0.07 m/s for reference)<br>clearance at the contact 0.00 m<br>ambiguous: 3 persistent tracks of A are compatible with the contact (track_001, track_002, track_005)<br>common frame: its returns lie on B's own footprint (median 0.00 m, 0.00 sigma of the relative uncertainty, over 240 samples; 100% within 3 sigma) at B's own velocity |
| A:track_003 | U2 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 1168.63 vs 1168.63 N*s)<br>tracked for 7.65 s before the matched collision<br>lost 1.30 s before the matched collision (window 1.00 s)<br>not approaching before the contact: clearance 5.1 m -> 7.2 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 0.32 m/s for reference)<br>anonymous road user U2: A:track_003 |
| A:track_004 | U3 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 1168.63 vs 1168.63 N*s)<br>tracked for 7.65 s before the matched collision<br>lost 2.00 s before the matched collision (window 1.00 s)<br>not approaching before the contact: clearance 5.4 m -> 7.4 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 0.17 m/s for reference)<br>anonymous road user U3: A:track_004 |
| A:track_005 | U5 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 1168.63 vs 1168.63 N*s)<br>tracked for 7.60 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 2.1 m -> 1.6 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 0.13 m/s for reference)<br>clearance at the contact 1.51 m<br>ambiguous: 3 persistent tracks of A are compatible with the contact (track_001, track_002, track_005)<br>anonymous road user U5: B:track_003, A:track_005 |
| A:track_006 | U6 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 1168.63 vs 1168.63 N*s)<br>tracked for 7.25 s before the matched collision<br>lost 3.05 s before the matched collision (window 1.00 s)<br>approaching before the contact: clearance 28.4 m -> 26.4 m over the last 1.0 s<br>speed not comparable with B's own speed before the collision<br>anonymous road user U6: A:track_006, B:track_004, A:track_007 |
| A:track_007 | U6 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 1168.63 vs 1168.63 N*s)<br>tracked for 0.05 s before the matched collision (needs 1.00 s)<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 20.2 m -> 19.8 m over the last 1.0 s<br>speed not comparable with B's own speed before the collision<br>clearance at the contact 19.83 m (beyond 3.50 m: confidence factor 0.00)<br>anonymous road user U6: A:track_006, B:track_004, A:track_007 |
| A:track_008 | U4 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 1168.63 vs 1168.63 N*s)<br>tracked for 0.05 s before the matched collision (needs 1.00 s)<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 18.6 m -> 18.5 m over the last 1.0 s<br>speed not comparable with B's own speed before the collision<br>clearance at the contact 18.47 m (beyond 3.50 m: confidence factor 0.00)<br>anonymous road user U4: B:track_001, A:track_008 |
| A:track_009 | U7 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 1168.63 vs 1168.63 N*s)<br>tracked for 0.00 s before the matched collision (needs 1.00 s)<br>first seen 1.05 s after the matched collision<br>range trend before the contact not measurable<br>speed not comparable with B's own speed before the collision<br>anonymous road user U7: A:track_009, B:track_005 |
| A:track_010 | U8 | ANONYMOUS | - | A and B both reported collision_001 (peak impulse 1168.63 vs 1168.63 N*s)<br>tracked for 0.00 s before the matched collision (needs 1.00 s)<br>first seen 1.20 s after the matched collision<br>range trend before the contact not measurable<br>speed not comparable with B's own speed before the collision<br>anonymous road user U8: A:track_010 |
| B:track_001 | U4 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 1168.63 vs 1168.63 N*s)<br>tracked for 7.65 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>not approaching before the contact: clearance 13.8 m -> 13.8 m over the last 1.0 s<br>track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 1.96 m/s for reference)<br>clearance at the contact 13.76 m (beyond 3.50 m: confidence factor 0.00)<br>anonymous road user U4: B:track_001, A:track_008 |
| B:track_002 | U1 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 1168.63 vs 1168.63 N*s)<br>tracked for 7.65 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>not approaching before the contact: clearance 1.5 m -> 1.5 m over the last 1.0 s<br>track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 2.08 m/s for reference)<br>clearance at the contact 1.49 m<br>anonymous road user U1: A:track_001, B:track_002 |
| B:track_003 | U5 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 1168.63 vs 1168.63 N*s)<br>tracked for 7.65 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>not approaching before the contact: clearance 1.5 m -> 1.5 m over the last 1.0 s<br>track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 2.19 m/s for reference)<br>clearance at the contact 1.49 m<br>anonymous road user U5: B:track_003, A:track_005 |
| B:track_004 | U6 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 1168.63 vs 1168.63 N*s)<br>tracked for 7.25 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>not approaching before the contact: clearance 15.2 m -> 15.4 m over the last 1.0 s<br>track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 1.99 m/s for reference)<br>clearance at the contact 15.24 m (beyond 3.50 m: confidence factor 0.00)<br>anonymous road user U6: A:track_006, B:track_004, A:track_007 |
| B:track_005 | U7 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 1168.63 vs 1168.63 N*s)<br>tracked for 0.00 s before the matched collision (needs 1.00 s)<br>first seen 1.55 s after the matched collision<br>range trend before the contact not measurable<br>speed not comparable with A's own speed before the collision<br>anonymous road user U7: A:track_009, B:track_005 |
| B:track_006 | U9 | ANONYMOUS | - | B and A both reported collision_001 (peak impulse 1168.63 vs 1168.63 N*s)<br>tracked for 0.00 s before the matched collision (needs 1.00 s)<br>first seen 1.70 s after the matched collision<br>range trend before the contact not measurable<br>speed not comparable with A's own speed before the collision<br>anonymous road user U9: B:track_006 |

## Road users in the common frame

- A:track_002 is B: its returns lie on B's own footprint (median 0.00 m over 240 samples, 100% within 3 sigma) at B's velocity.
- U1 (anonymous, -7.65 to 4.30 s): A:track_001, B:track_002 joined by same box A:track_001-B:track_002 (100% of 180 instants); footprint 4.60 x 1.90 m (prior/prior); fusion box_fit+covariance_intersection.
- U2 (anonymous, -7.65 to -1.30 s): A:track_003; footprint 4.60 x 1.90 m (prior/prior); fusion box_fit+covariance_intersection.
- U3 (anonymous, -7.65 to -2.00 s): A:track_004; footprint 4.60 x 1.90 m (prior/prior); fusion box_fit+covariance_intersection.
- U4 (anonymous, -7.65 to 4.30 s): B:track_001, A:track_008 joined by same box A:track_008-B:track_001 (100% of 12 instants); footprint 4.60 x 1.90 m (prior/prior); fusion box_fit+covariance_intersection.
- U5 (anonymous, -7.65 to 4.30 s): B:track_003, A:track_005 joined by same box A:track_005-B:track_003 (100% of 182 instants); footprint 4.60 x 1.90 m (prior/prior); fusion box_fit+covariance_intersection.
- U6 (anonymous, -7.25 to 4.30 s): A:track_006, B:track_004, A:track_007 joined by same box A:track_006-B:track_004 (100% of 82 instants); same box A:track_007-B:track_004 (100% of 12 instants); footprint 4.60 x 1.90 m (prior/prior); fusion box_fit+covariance_intersection.
- U7 (anonymous, 1.05 to 4.30 s): A:track_009, B:track_005 joined by same box A:track_009-B:track_005 (90% of 29 instants); footprint 4.25 x 1.90 m (fitted/prior); fusion box_fit+covariance_intersection.
- U8 (anonymous, 1.20 to 3.10 s): A:track_010; footprint 4.60 x 1.90 m (prior/prior); fusion box_fit+covariance_intersection.
- U9 (anonymous, 1.70 to 4.30 s): B:track_006; footprint 4.60 x 1.90 m (prior/prior); fusion box_fit+covariance_intersection.

## Global graph

57 nodes, 135 edges; 19 merged node(s): g07 TRACK_APPEARED_LEFT(A,U1) from A:e04 + A:e34, g08 TRACK_APPEARED_LEFT(A,U2) from A:e05 + A:e16, g10 TRACK_APPEARED_RIGHT(A,U3) from A:e06 + A:e15, g12 CLOSING_START(A,B) from A:e08 + A:e23, g13 CLOSING_START(A,U1) from A:e07 + A:e22, g14 TRACK_APPEARED_RIGHT(A,U5) from A:e09 + A:e35, g15 CLOSING_START(A,U5) from A:e10 + A:e17, g16 TRACK_APPEARED_FRONT(A,U6) from A:e11 + A:e14, g19 CRITICAL_TTC_START(A,B) from A:e13 + A:e21, g20 CRITICAL_TTC_START(B,U4) from B:e07 + B:e11, g25 TRACK_APPEARED_FRONT(A,U4) from A:e18 + A:e27, g26 TRACK_APPEARED_LEFT(A,U6) from A:e19 + A:e26, g27 COLLISION(A,B) from A:e20 + B:e08, g38 TRACK_APPEARED_LEFT(A,U7) from A:e28 + A:e38, g39 CLOSING_START(A,U7) from A:e29 + A:e36, g42 TRACK_APPEARED_RIGHT(A,U8) from A:e32 + A:e39, g43 CLOSING_START(A,U8) from A:e33 + A:e37, g49 CLOSING_START(B,U7) from B:e15 + B:e18, g51 CLOSING_START(B,U9) from B:e17 + B:e19.

### Event sequence (global time)

- `-7.65` MOVING_START(A); MOVING_START(B); THROTTLE_START(A); THROTTLE_START(B); TRACK_APPEARED_FRONT(A,B); TRACK_APPEARED_FRONT(B,U4); TRACK_APPEARED_LEFT(A,U1); TRACK_APPEARED_LEFT(A,U2); TRACK_APPEARED_LEFT(B,U1); TRACK_APPEARED_RIGHT(A,U3); TRACK_APPEARED_RIGHT(B,U5); CLOSING_START(A,B); CLOSING_START(A,U1)
- `-7.60` TRACK_APPEARED_RIGHT(A,U5); CLOSING_START(A,U5)
- `-7.25` TRACK_APPEARED_FRONT(A,U6); TRACK_APPEARED_LEFT(B,U6); CLOSING_START(A,U6)
- `-7.15` CRITICAL_TTC_START(A,B); CRITICAL_TTC_START(B,U4)
- `-3.05` TRACK_LOST(A,U6)
- `-2.00` TRACK_LOST(A,U3)
- `-1.30` TRACK_LOST(A,U2)
- `-0.45` CLOSING_END(A,U5)
- `-0.05` TRACK_APPEARED_FRONT(A,U4); TRACK_APPEARED_LEFT(A,U6)
- `+0.00` COLLISION(A,B); CRITICAL_TTC_END(A,B); CLOSING_END(A,B); CLOSING_END(A,U1)
- `+0.05` THROTTLE_END(A); THROTTLE_END(B); BRAKE_START(A); BRAKE_START(B)
- `+0.50` CRITICAL_TTC_END(B,U4)
- `+0.70` TRACK_LOST(A,U4); TRACK_LOST(A,U6)
- `+1.05` TRACK_APPEARED_LEFT(A,U7); CLOSING_START(A,U7)
- `+1.10` MOVING_END(A); STOP_START(A)
- `+1.20` TRACK_APPEARED_RIGHT(A,U8); CLOSING_START(A,U8)
- `+1.25` MOVING_END(B); STOP_START(B)
- `+1.30` TRACK_LOST(A,U1)
- `+1.45` TRACK_LOST(A,U5)
- `+1.55` TRACK_APPEARED_LEFT(B,U7); CLOSING_START(B,U7)
- `+1.70` TRACK_APPEARED_RIGHT(B,U9); CLOSING_START(B,U9)
- `+1.80` CLOSING_END(A,U7)
- `+1.95` CLOSING_END(A,U8)
- `+2.35` CLOSING_END(B,U7)
- `+2.45` CLOSING_END(B,U9)
- `+2.95` TRACK_LOST(A,U7)
- `+3.10` TRACK_LOST(A,U8)

### What happened, in plain language

- 7.65 s before the reference collision, A started moving (already the case when first observed).
- 7.65 s before the reference collision, B started moving (already the case when first observed).
- 7.65 s before the reference collision, A pressed the accelerator (already the case when first observed).
- 7.65 s before the reference collision, B pressed the accelerator (already the case when first observed).
- 7.65 s before the reference collision, A's radar started tracking B, which appeared in front of it.
- 7.65 s before the reference collision, B's radar started tracking anonymous road user U4, which appeared in front of it.
- 7.65 s before the reference collision, A's radar started tracking anonymous road user U1, which appeared on its left.
- 7.65 s before the reference collision, A's radar started tracking anonymous road user U2, which appeared on its left.
- 7.65 s before the reference collision, B's radar started tracking anonymous road user U1, which appeared on its left.
- 7.65 s before the reference collision, A's radar started tracking anonymous road user U3, which appeared on its right.
- 7.65 s before the reference collision, B's radar started tracking anonymous road user U5, which appeared on its right.
- 7.65 s before the reference collision, A observed B start closing in (already the case when first observed).
- 7.65 s before the reference collision, A observed anonymous road user U1 start closing in (already the case when first observed).
- 7.60 s before the reference collision, A's radar started tracking anonymous road user U5, which appeared on its right.
- 7.60 s before the reference collision, A observed anonymous road user U5 start closing in (already the case when first observed).
- 7.25 s before the reference collision, A's radar started tracking anonymous road user U6, which appeared in front of it.
- 7.25 s before the reference collision, B's radar started tracking anonymous road user U6, which appeared on its left.
- 7.25 s before the reference collision, A observed anonymous road user U6 start closing in (already the case when first observed).
- 7.15 s before the reference collision, A's time-to-contact with B became critical.
- 7.15 s before the reference collision, B's time-to-contact with anonymous road user U4 became critical.
- 3.05 s before the reference collision, A's radar lost anonymous road user U6 (its states are UNKNOWN from then on, not ended).
- 2.00 s before the reference collision, A's radar lost anonymous road user U3 (its states are UNKNOWN from then on, not ended).
- 1.30 s before the reference collision, A's radar lost anonymous road user U2 (its states are UNKNOWN from then on, not ended).
- 0.45 s before the reference collision, A observed anonymous road user U5 stop closing in.
- 0.05 s before the reference collision, A's radar started tracking anonymous road user U4, which appeared in front of it.
- 0.05 s before the reference collision, A's radar started tracking anonymous road user U6, which appeared on its left.
- At the reference collision, A and B both recorded this same collision (peak impulses A: 1169, B: 1169 N*s).
- At the reference collision, A's time-to-contact with B stopped being critical.
- At the reference collision, A observed B stop closing in.
- At the reference collision, A observed anonymous road user U1 stop closing in.
- 0.05 s after the reference collision, A released the accelerator.
- 0.05 s after the reference collision, B released the accelerator.
- 0.05 s after the reference collision, A started braking.
- 0.05 s after the reference collision, B started braking.
- 0.50 s after the reference collision, B's time-to-contact with anonymous road user U4 stopped being critical.
- 0.70 s after the reference collision, A's radar lost anonymous road user U4 (its states are UNKNOWN from then on, not ended).
- 0.70 s after the reference collision, A's radar lost anonymous road user U6 (its states are UNKNOWN from then on, not ended).
- 1.05 s after the reference collision, A's radar started tracking anonymous road user U7, which appeared on its left.
- 1.05 s after the reference collision, A observed anonymous road user U7 start closing in (already the case when first observed).
- 1.10 s after the reference collision, A stopped moving.
- 1.10 s after the reference collision, A came to a stop.
- 1.20 s after the reference collision, A's radar started tracking anonymous road user U8, which appeared on its right.
- 1.20 s after the reference collision, A observed anonymous road user U8 start closing in (already the case when first observed).
- 1.25 s after the reference collision, B stopped moving.
- 1.25 s after the reference collision, B came to a stop.
- 1.30 s after the reference collision, A's radar lost anonymous road user U1 (its states are UNKNOWN from then on, not ended).
- 1.45 s after the reference collision, A's radar lost anonymous road user U5 (its states are UNKNOWN from then on, not ended).
- 1.55 s after the reference collision, B's radar started tracking anonymous road user U7, which appeared on its left.
- 1.55 s after the reference collision, B observed anonymous road user U7 start closing in (already the case when first observed).
- 1.70 s after the reference collision, B's radar started tracking anonymous road user U9, which appeared on its right.
- 1.70 s after the reference collision, B observed anonymous road user U9 start closing in (already the case when first observed).
- 1.80 s after the reference collision, A observed anonymous road user U7 stop closing in.
- 1.95 s after the reference collision, A observed anonymous road user U8 stop closing in.
- 2.35 s after the reference collision, B observed anonymous road user U7 stop closing in.
- 2.45 s after the reference collision, B observed anonymous road user U9 stop closing in.
- 2.95 s after the reference collision, A's radar lost anonymous road user U7 (its states are UNKNOWN from then on, not ended).
- 3.10 s after the reference collision, A's radar lost anonymous road user U8 (its states are UNKNOWN from then on, not ended).

### Temporal safety relations

CUT_IN_START < CRITICAL_TTC_START < COLLISION, or CRITICAL_TTC_START <= CUT_IN_START (critical TTC already active), and EGO_PATH_ENTRY before/after the critical TTC. Temporal order only, not causes.

- A's track_002 (B): CRITICAL_TTC_START 0.50, COLLISION with B 7.65 (+7.15 s) [local times; t_global: critical_ttc_start -7.15, collision +0.00]
- B's track_001 (unidentified U4): CRITICAL_TTC_START 0.50, COLLISION 7.65 (+7.15 s) [local times; t_global: critical_ttc_start -7.15, collision +0.00]

### Simultaneous events (order unresolved at 0.05 s)

- MOVING_START(A); MOVING_START(B); THROTTLE_START(A); THROTTLE_START(B); TRACK_APPEARED_FRONT(A,B); TRACK_APPEARED_FRONT(B,U4); TRACK_APPEARED_LEFT(A,U1); TRACK_APPEARED_LEFT(A,U2); TRACK_APPEARED_LEFT(B,U1); TRACK_APPEARED_RIGHT(A,U3); TRACK_APPEARED_RIGHT(B,U5); CLOSING_START(A,B); CLOSING_START(A,U1)
- TRACK_APPEARED_RIGHT(A,U5); CLOSING_START(A,U5)
- TRACK_APPEARED_FRONT(A,U6); TRACK_APPEARED_LEFT(B,U6); CLOSING_START(A,U6)
- CRITICAL_TTC_START(A,B); CRITICAL_TTC_START(B,U4)
- TRACK_APPEARED_FRONT(A,U4); TRACK_APPEARED_LEFT(A,U6)
- COLLISION(A,B); CRITICAL_TTC_END(A,B); CLOSING_END(A,B); CLOSING_END(A,U1)
- THROTTLE_END(A); THROTTLE_END(B); BRAKE_START(A); BRAKE_START(B)
- TRACK_LOST(A,U4); TRACK_LOST(A,U6)
- TRACK_APPEARED_LEFT(A,U7); CLOSING_START(A,U7)
- MOVING_END(A); STOP_START(A)
- TRACK_APPEARED_RIGHT(A,U8); CLOSING_START(A,U8)
- MOVING_END(B); STOP_START(B)
- TRACK_APPEARED_LEFT(B,U7); CLOSING_START(B,U7)
- TRACK_APPEARED_RIGHT(B,U9); CLOSING_START(B,U9)

### States still active when observation ended

A:
- CLOSING of track_006, since A:e12 (t = 0.40 s); the track was lost at 4.60 s
- BRAKE, since A:e25 (t = 7.70 s)
- STOP, since A:e31 (t = 8.75 s)
B:
- BRAKE, since B:e10 (t = 7.70 s)
- STOP, since B:e13 (t = 8.90 s)

### Sign detection windows

A:
- none
B:
- none

### Perceived state just before each collision report

- A A:e20 at 7.65 s (local): ego: MOVING, THROTTLE; track_001: CLOSING; track_002: CLOSING, CRITICAL_TTC, IN_EGO_PATH; track_005: no active state; track_007: CRITICAL_TTC?; track_008: IN_EGO_PATH, CRITICAL_TTC?; track lost, states UNKNOWN: track_003, track_004, track_006
- B B:e08 at 7.65 s (local): ego: MOVING, THROTTLE; track_001: CRITICAL_TTC, IN_EGO_PATH; track_002: no active state; track_003: no active state; track_004: no active state

### Tracks lost while a state was active

A lost track's states become UNKNOWN: the recorder can no longer tell whether they ended.

A:
- track_006 at 4.60 s (A:e14): CLOSING were true; they are UNKNOWN afterwards (no END recorded)
- track_008 at 8.35 s (A:e27): IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)
- lost with no state active: track_004, track_003, track_007, track_001, track_005, track_009, track_010
B:
- no track was lost

## Uncertainty and limitations

- A:track_001 stays anonymous (U1): ambiguous: 3 persistent tracks of A are compatible with the contact (track_001, track_002, track_005).
- A:track_003 stays anonymous (U2): lost 1.30 s before the matched collision (window 1.00 s); not approaching before the contact: clearance 5.1 m -> 7.2 m over the last 1.0 s.
- A:track_004 stays anonymous (U3): lost 2.00 s before the matched collision (window 1.00 s); not approaching before the contact: clearance 5.4 m -> 7.4 m over the last 1.0 s.
- A:track_005 stays anonymous (U5): ambiguous: 3 persistent tracks of A are compatible with the contact (track_001, track_002, track_005).
- A:track_006 stays anonymous (U6): lost 3.05 s before the matched collision (window 1.00 s); speed not comparable with B's own speed before the collision.
- A:track_007 stays anonymous (U6): tracked for 0.05 s before the matched collision (needs 1.00 s); speed not comparable with B's own speed before the collision.
- A:track_008 stays anonymous (U4): tracked for 0.05 s before the matched collision (needs 1.00 s); speed not comparable with B's own speed before the collision.
- A:track_009 stays anonymous (U7): tracked for 0.00 s before the matched collision (needs 1.00 s); first seen 1.05 s after the matched collision; range trend before the contact not measurable; speed not comparable with B's own speed before the collision.
- A:track_010 stays anonymous (U8): tracked for 0.00 s before the matched collision (needs 1.00 s); first seen 1.20 s after the matched collision; range trend before the contact not measurable; speed not comparable with B's own speed before the collision.
- B:track_001 stays anonymous (U4): not approaching before the contact: clearance 13.8 m -> 13.8 m over the last 1.0 s; track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 1.96 m/s for reference).
- B:track_002 stays anonymous (U1): not approaching before the contact: clearance 1.5 m -> 1.5 m over the last 1.0 s; track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 2.08 m/s for reference).
- B:track_003 stays anonymous (U5): not approaching before the contact: clearance 1.5 m -> 1.5 m over the last 1.0 s; track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 2.19 m/s for reference).
- B:track_004 stays anonymous (U6): not approaching before the contact: clearance 15.2 m -> 15.4 m over the last 1.0 s; track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 1.99 m/s for reference).
- B:track_005 stays anonymous (U7): tracked for 0.00 s before the matched collision (needs 1.00 s); first seen 1.55 s after the matched collision; range trend before the contact not measurable; speed not comparable with A's own speed before the collision.
- B:track_006 stays anonymous (U9): tracked for 0.00 s before the matched collision (needs 1.00 s); first seen 1.70 s after the matched collision; range trend before the contact not measurable; speed not comparable with A's own speed before the collision.
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
