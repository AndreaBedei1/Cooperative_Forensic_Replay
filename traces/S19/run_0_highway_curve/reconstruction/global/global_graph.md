# Global graph - S19/run_0_highway_curve

Global time `t_global` is 0 at the reference collision. The local graphs were not modified: every node lists the local node(s) and local time(s) it comes from.

Speed limit 90 km/h, supplied as incident context: known a priori, not perceived and not ground truth.

## Entities

| Entity | Kind | Details |
|--------|------|---------|
| A | recorder | clock ALIGNED; observed by others as: B:track_005 |
| B | recorder | clock ALIGNED; observed by others as: A:track_006 |
| U1 | anonymous_road_user | anonymous; observed by A, B as A:track_001, B:track_003 |
| U2 | anonymous_road_user | anonymous; observed by A, B as A:track_002, B:track_004 |
| U3 | anonymous_road_user | anonymous; observed by A, B as A:track_003, B:track_001 |
| U4 | anonymous_road_user | anonymous; observed by A as A:track_004 |
| U6 | anonymous_road_user | anonymous; observed by A as A:track_005 |
| U5 | anonymous_road_user | anonymous; observed by A, B as A:track_007, A:track_008, A:track_009, B:track_002 |
| U7 | anonymous_road_user | anonymous; observed by A as A:track_010 |
| U8 | anonymous_road_user | anonymous; observed by A, B as A:track_011, B:track_007 |
| U9 | anonymous_road_user | anonymous; observed by B as B:track_006 |

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

## Nodes

| Id | Global time | Type | Actor | Subject / participants | Observed by (local node @ local time) | Details |
|----|------------:|------|-------|------------------------|----------------------------------------|---------|
| g01 | -7.50 | MOVING_START | A | - | A:e01 @ 0.00 | active_at_first_observation=True |
| g02 | -7.50 | MOVING_START | B | - | B:e01 @ 0.00 | active_at_first_observation=True |
| g03 | -7.50 | THROTTLE_START | A | - | A:e02 @ 0.00 | active_at_first_observation=True |
| g04 | -7.50 | THROTTLE_START | B | - | B:e02 @ 0.00 | active_at_first_observation=True |
| g05 | -7.50 | TRACK_APPEARED_LEFT | A | U1 | A:e03 @ 0.00, A:e31 @ 8.45 | initial_in_ego_path=False; source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g06 | -7.50 | TRACK_APPEARED_LEFT | A | U3 | A:e04 @ 0.00, A:e21 @ 6.20 | initial_in_ego_path=False; source_track=track_003; aggregation=entity_state_union; source_tracks=['A:track_003'] |
| g07 | -7.50 | TRACK_APPEARED_LEFT | B | U1 | B:e05 @ 0.00, B:e32 @ 11.15 | initial_in_ego_path=False; source_track=track_003; aggregation=entity_state_union; source_tracks=['B:track_003'] |
| g08 | -7.50 | TRACK_APPEARED_LEFT | B | U3 | B:e03 @ 0.00, B:e23 @ 7.70 | initial_in_ego_path=False; source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g09 | -7.50 | TRACK_APPEARED_LEFT | B | U5 | B:e04 @ 0.00, B:e24 @ 7.70 | initial_in_ego_path=False; source_track=track_002; aggregation=entity_state_union; source_tracks=['B:track_002'] |
| g10 | -7.50 | TRACK_APPEARED_RIGHT | A | U2 | A:e05 @ 0.00, A:e38 @ 11.90 | initial_in_ego_path=False; source_track=track_002; aggregation=entity_state_union; source_tracks=['A:track_002'] |
| g11 | -7.50 | TRACK_APPEARED_RIGHT | A | U4 | A:e06 @ 0.00, A:e14 @ 2.35 | initial_in_ego_path=False; source_track=track_004; aggregation=entity_state_union; source_tracks=['A:track_004'] |
| g12 | -7.50 | TRACK_APPEARED_RIGHT | B | U2 | B:e06 @ 0.00 | initial_in_ego_path=False; source_track=track_004; aggregation=entity_state_union; source_tracks=['B:track_004'] |
| g13 | -7.50 | CLOSING_START | A | U2 | A:e07 @ 0.00, A:e23 @ 7.40 | active_at_first_observation=True; source_track=track_002; aggregation=entity_state_union; source_tracks=['A:track_002'] |
| g14 | -7.50 | CLOSING_START | B | U1 | B:e07 @ 0.00, B:e08 @ 5.35 | active_at_first_observation=True; source_track=track_003; aggregation=entity_state_union; source_tracks=['B:track_003'] |
| g15 | -7.45 | TRACK_APPEARED_LEFT | A | U6 | A:e08 @ 0.05, A:e11 @ 0.60 | initial_in_ego_path=True; source_track=track_005; aggregation=entity_state_union; source_tracks=['A:track_005'] |
| g16 | -7.20 | TRACK_APPEARED_FRONT | A | B | A:e09 @ 0.30 | initial_in_ego_path=False; source_track=track_006; aggregation=entity_state_union; source_tracks=['A:track_006'] |
| g17 | -7.20 | CLOSING_START | A | B | A:e10 @ 0.30, A:e26 @ 7.50 | active_at_first_observation=True; source_track=track_006; aggregation=entity_state_union; source_tracks=['A:track_006'] |
| g18 | -6.90 | TRACK_LOST | A | U6 | A:e11 @ 0.60 | source_track=track_005; aggregation=entity_state_union; source_tracks=['A:track_005'] |
| g19 | -6.10 | TRACK_APPEARED_LEFT | A | U5 | A:e12 @ 1.40, A:e13 @ 2.05 | initial_in_ego_path=True; source_track=track_007; aggregation=entity_state_union; source_tracks=['A:track_007'] |
| g20 | -5.45 | TRACK_LOST | A | U5 | A:e13 @ 2.05 | source_track=track_007; aggregation=entity_state_union; source_tracks=['A:track_007'] |
| g21 | -5.15 | TRACK_LOST | A | U4 | A:e14 @ 2.35 | source_track=track_004; aggregation=entity_state_union; source_tracks=['A:track_004'] |
| g22 | -5.00 | TRACK_APPEARED_LEFT | A | U5 | A:e15 @ 2.50, A:e16 @ 3.00 | initial_in_ego_path=True; source_track=track_008; aggregation=entity_state_union; source_tracks=['A:track_008'] |
| g23 | -4.50 | TRACK_LOST | A | U5 | A:e16 @ 3.00 | source_track=track_008; aggregation=entity_state_union; source_tracks=['A:track_008'] |
| g24 | -4.15 | TRACK_APPEARED_LEFT | A | U5 | A:e17 @ 3.35, A:e18 @ 3.70 | initial_in_ego_path=True; source_track=track_009; aggregation=entity_state_union; source_tracks=['A:track_009'] |
| g25 | -3.80 | TRACK_LOST | A | U5 | A:e18 @ 3.70 | source_track=track_009; aggregation=entity_state_union; source_tracks=['A:track_009'] |
| g26 | -2.15 | CLOSING_END | B | U1 | B:e08 @ 5.35 | source_track=track_003; aggregation=entity_state_union; source_tracks=['B:track_003'] |
| g27 | -2.05 | TRACK_APPEARED_LEFT | B | A | B:e09 @ 5.45, B:e19 @ 6.60 | initial_in_ego_path=False; source_track=track_005; aggregation=entity_state_union; source_tracks=['B:track_005'] |
| g28 | -2.05 | CLOSING_START | B | A | B:e10 @ 5.45 | active_at_first_observation=True; source_track=track_005; aggregation=entity_state_union; source_tracks=['B:track_005'] |
| g29 | -2.00 | TURN_LEFT_START | B | - | B:e11 @ 5.50 |  |
| g30 | -2.00 | CRITICAL_TTC_START | A | B | A:e19 @ 5.50, A:e25 @ 7.50 | source_track=track_006; aggregation=entity_state_union; source_tracks=['A:track_006'] |
| g31 | -2.00 | CUT_IN_FROM_RIGHT_START | A | B | A:e20 @ 5.50, A:e30 @ 8.35 | geometry=estimated_body; source_track=track_006; aggregation=entity_state_union; source_tracks=['A:track_006'] |
| g32 | -1.85 | CLOSING_START | B | U1 | B:e12 @ 5.65, B:e15 @ 6.35 | source_track=track_003; aggregation=entity_state_union; source_tracks=['B:track_003'] |
| g33 | -1.55 | CRITICAL_TTC_START | B | A | B:e13 @ 5.95 | source_track=track_005; aggregation=entity_state_union; source_tracks=['B:track_005'] |
| g34 | -1.45 | EGO_PATH_ENTRY | B | U5 | B:e14 @ 6.05 | occupancy_evidence=box; occupancy_margin_m=0.52; occupancy_sigma_m=0.30; cause=RECORDER_LATERAL; geometry=estimated_body; source_track=track_002; aggregation=entity_state_union; source_tracks=['B:track_002'] |
| g35 | -1.30 | TRACK_LOST | A | U3 | A:e21 @ 6.20 | source_track=track_003; aggregation=entity_state_union; source_tracks=['A:track_003'] |
| g36 | -1.20 | EGO_PATH_ENTRY | A | B | A:e22 @ 6.30 | occupancy_evidence=box; occupancy_margin_m=0.56; occupancy_sigma_m=0.26; cause=TARGET_LATERAL; geometry=estimated_body; source_track=track_006; aggregation=entity_state_union; source_tracks=['A:track_006'] |
| g37 | -1.15 | CLOSING_END | B | U1 | B:e15 @ 6.35 | source_track=track_003; aggregation=entity_state_union; source_tracks=['B:track_003'] |
| g38 | -1.00 | TURN_LEFT_END | B | - | B:e16 @ 6.50 |  |
| g39 | -0.95 | THROTTLE_END | B | - | B:e17 @ 6.55 |  |
| g40 | -0.95 | BRAKE_START | B | - | B:e18 @ 6.55 |  |
| g41 | -0.90 | TRACK_LOST | B | A | B:e19 @ 6.60 | source_track=track_005; aggregation=entity_state_union; source_tracks=['B:track_005'] |
| g42 | -0.10 | CLOSING_END | A | U2 | A:e23 @ 7.40 | source_track=track_002; aggregation=entity_state_union; source_tracks=['A:track_002'] |
| g43 | -0.10 | THROTTLE_START | B | - | B:e20 @ 7.40 |  |
| g44 | 0.00 | COLLISION | - | A, B | A:e24 @ 7.50, B:e21 @ 7.50 | matched_event=collision_001; reference_event=True; peak_impulse=A 7479.37, B 7479.37 |
| g45 | 0.00 | CRITICAL_TTC_END | A | B | A:e25 @ 7.50 | source_track=track_006; aggregation=entity_state_union; source_tracks=['A:track_006'] |
| g46 | 0.00 | CRITICAL_TTC_END | B | A | B:e21 @ 7.50 | closed_by_contact=collision_001 |
| g47 | 0.00 | CLOSING_END | A | B | A:e26 @ 7.50 | source_track=track_006; aggregation=entity_state_union; source_tracks=['A:track_006'] |
| g48 | 0.00 | THROTTLE_END | B | - | B:e22 @ 7.50 |  |
| g49 | 0.05 | THROTTLE_END | A | - | A:e27 @ 7.55 |  |
| g50 | 0.05 | BRAKE_START | A | - | A:e28 @ 7.55 |  |
| g51 | 0.20 | TRACK_LOST | B | U3 | B:e23 @ 7.70 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g52 | 0.20 | TRACK_LOST | B | U5 | B:e24 @ 7.70 | source_track=track_002; aggregation=entity_state_union; source_tracks=['B:track_002'] |
| g53 | 0.25 | TRACK_APPEARED_LEFT | A | U7 | A:e29 @ 7.75, A:e32 @ 8.45 | initial_in_ego_path=False; source_track=track_010; aggregation=entity_state_union; source_tracks=['A:track_010'] |
| g54 | 0.85 | CUT_IN_FROM_RIGHT_END | A | B | A:e30 @ 8.35 | geometry=estimated_body; source_track=track_006; aggregation=entity_state_union; source_tracks=['A:track_006'] |
| g55 | 0.95 | TRACK_LOST | A | U1 | A:e31 @ 8.45 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g56 | 0.95 | TRACK_LOST | A | U7 | A:e32 @ 8.45 | source_track=track_010; aggregation=entity_state_union; source_tracks=['A:track_010'] |
| g57 | 1.20 | TRACK_APPEARED_RIGHT | A | U8 | A:e33 @ 8.70 | initial_in_ego_path=False; source_track=track_011; aggregation=entity_state_union; source_tracks=['A:track_011'] |
| g58 | 1.20 | CLOSING_START | A | U8 | A:e34 @ 8.70, A:e37 @ 10.30 | active_at_first_observation=True; source_track=track_011; aggregation=entity_state_union; source_tracks=['A:track_011'] |
| g59 | 1.25 | TRACK_APPEARED_LEFT | B | U9 | B:e25 @ 8.75, B:e26 @ 9.00 | initial_in_ego_path=False; source_track=track_006; aggregation=entity_state_union; source_tracks=['B:track_006'] |
| g60 | 1.45 | MOVING_END | A | - | A:e35 @ 8.95 |  |
| g61 | 1.45 | STOP_START | A | - | A:e36 @ 8.95 |  |
| g62 | 1.50 | TRACK_LOST | B | U9 | B:e26 @ 9.00 | source_track=track_006; aggregation=entity_state_union; source_tracks=['B:track_006'] |
| g63 | 1.55 | MOVING_END | B | - | B:e27 @ 9.05 |  |
| g64 | 1.55 | STOP_START | B | - | B:e28 @ 9.05 |  |
| g65 | 2.00 | TRACK_APPEARED_RIGHT | B | U8 | B:e29 @ 9.50 | initial_in_ego_path=False; source_track=track_007; aggregation=entity_state_union; source_tracks=['B:track_007'] |
| g66 | 2.00 | CLOSING_START | B | U8 | B:e30 @ 9.50, B:e31 @ 10.35 | active_at_first_observation=True; source_track=track_007; aggregation=entity_state_union; source_tracks=['B:track_007'] |
| g67 | 2.80 | CLOSING_END | A | U8 | A:e37 @ 10.30 | source_track=track_011; aggregation=entity_state_union; source_tracks=['A:track_011'] |
| g68 | 2.85 | CLOSING_END | B | U8 | B:e31 @ 10.35 | source_track=track_007; aggregation=entity_state_union; source_tracks=['B:track_007'] |
| g69 | 3.65 | TRACK_LOST | B | U1 | B:e32 @ 11.15 | source_track=track_003; aggregation=entity_state_union; source_tracks=['B:track_003'] |
| g70 | 4.40 | TRACK_LOST | A | U2 | A:e38 @ 11.90 | source_track=track_002; aggregation=entity_state_union; source_tracks=['A:track_002'] |

## Edges

```
    g01 --PRECEDES--> g15
    g02 --PRECEDES--> g15
    g03 --PRECEDES--> g15
    g04 --PRECEDES--> g15
    g05 --PRECEDES--> g15
    g06 --PRECEDES--> g15
    g07 --PRECEDES--> g15
    g08 --PRECEDES--> g15
    g09 --PRECEDES--> g15
    g10 --PRECEDES--> g15
    g11 --PRECEDES--> g15
    g12 --PRECEDES--> g15
    g13 --PRECEDES--> g15
    g14 --PRECEDES--> g15
    g15 --PRECEDES--> g16
    g15 --PRECEDES--> g17
    g16 --PRECEDES--> g18
    g17 --PRECEDES--> g18
    g18 --PRECEDES--> g19
    g19 --PRECEDES--> g20
    g20 --PRECEDES--> g21
    g21 --PRECEDES--> g22
    g22 --PRECEDES--> g23
    g23 --PRECEDES--> g24
    g24 --PRECEDES--> g25
    g25 --PRECEDES--> g26
    g26 --PRECEDES--> g27
    g26 --PRECEDES--> g28
    g27 --PRECEDES--> g29
    g27 --PRECEDES--> g30
    g27 --PRECEDES--> g31
    g28 --PRECEDES--> g29
    g28 --PRECEDES--> g30
    g28 --PRECEDES--> g31
    g29 --PRECEDES--> g32
    g30 --PRECEDES--> g32
    g31 --PRECEDES--> g32
    g32 --PRECEDES--> g33
    g33 --PRECEDES--> g34
    g34 --PRECEDES--> g35
    g35 --PRECEDES--> g36
    g36 --PRECEDES--> g37
    g37 --PRECEDES--> g38
    g38 --PRECEDES--> g39
    g38 --PRECEDES--> g40
    g39 --PRECEDES--> g41
    g40 --PRECEDES--> g41
    g41 --PRECEDES--> g42
    g41 --PRECEDES--> g43
    g42 --PRECEDES--> g44
    g42 --PRECEDES--> g45
    g42 --PRECEDES--> g46
    g42 --PRECEDES--> g47
    g42 --PRECEDES--> g48
    g43 --PRECEDES--> g44
    g43 --PRECEDES--> g45
    g43 --PRECEDES--> g46
    g43 --PRECEDES--> g47
    g43 --PRECEDES--> g48
    g44 --PRECEDES--> g49
    g44 --PRECEDES--> g50
    g45 --PRECEDES--> g49
    g45 --PRECEDES--> g50
    g46 --PRECEDES--> g49
    g46 --PRECEDES--> g50
    g47 --PRECEDES--> g49
    g47 --PRECEDES--> g50
    g48 --PRECEDES--> g49
    g48 --PRECEDES--> g50
    g49 --PRECEDES--> g51
    g49 --PRECEDES--> g52
    g50 --PRECEDES--> g51
    g50 --PRECEDES--> g52
    g51 --PRECEDES--> g53
    g52 --PRECEDES--> g53
    g53 --PRECEDES--> g54
    g54 --PRECEDES--> g55
    g54 --PRECEDES--> g56
    g55 --PRECEDES--> g57
    g55 --PRECEDES--> g58
    g56 --PRECEDES--> g57
    g56 --PRECEDES--> g58
    g57 --PRECEDES--> g59
    g58 --PRECEDES--> g59
    g59 --PRECEDES--> g60
    g59 --PRECEDES--> g61
    g60 --PRECEDES--> g62
    g61 --PRECEDES--> g62
    g62 --PRECEDES--> g63
    g62 --PRECEDES--> g64
    g63 --PRECEDES--> g65
    g63 --PRECEDES--> g66
    g64 --PRECEDES--> g65
    g64 --PRECEDES--> g66
    g65 --PRECEDES--> g67
    g66 --PRECEDES--> g67
    g67 --PRECEDES--> g68
    g68 --PRECEDES--> g69
    g69 --PRECEDES--> g70
    g10 --SAME_TRACK--> g13
    g16 --SAME_TRACK--> g17
    g15 --SAME_TRACK--> g18
    g19 --SAME_TRACK--> g20
    g11 --SAME_TRACK--> g21
    g22 --SAME_TRACK--> g23
    g24 --SAME_TRACK--> g25
    g16 --SAME_TRACK--> g30
    g16 --SAME_TRACK--> g31
    g06 --SAME_TRACK--> g35
    g16 --SAME_TRACK--> g36
    g10 --SAME_TRACK--> g42
    g16 --SAME_TRACK--> g45
    g16 --SAME_TRACK--> g47
    g16 --SAME_TRACK--> g54
    g05 --SAME_TRACK--> g55
    g53 --SAME_TRACK--> g56
    g57 --SAME_TRACK--> g58
    g57 --SAME_TRACK--> g67
    g10 --SAME_TRACK--> g70
    g07 --SAME_TRACK--> g14
    g07 --SAME_TRACK--> g26
    g27 --SAME_TRACK--> g28
    g07 --SAME_TRACK--> g32
    g27 --SAME_TRACK--> g33
    g09 --SAME_TRACK--> g34
    g07 --SAME_TRACK--> g37
    g27 --SAME_TRACK--> g41
    g08 --SAME_TRACK--> g51
    g09 --SAME_TRACK--> g52
    g59 --SAME_TRACK--> g62
    g65 --SAME_TRACK--> g66
    g65 --SAME_TRACK--> g68
    g07 --SAME_TRACK--> g69
```

## Global trace

Events in one row are simultaneous at 0.05 s resolution: their order is unresolved.

| t_global | Events |
|---------:|--------|
| -7.50 | MOVING_START(A); MOVING_START(B); THROTTLE_START(A); THROTTLE_START(B); TRACK_APPEARED_LEFT(A,U1); TRACK_APPEARED_LEFT(A,U3); TRACK_APPEARED_LEFT(B,U1); TRACK_APPEARED_LEFT(B,U3); TRACK_APPEARED_LEFT(B,U5); TRACK_APPEARED_RIGHT(A,U2); TRACK_APPEARED_RIGHT(A,U4); TRACK_APPEARED_RIGHT(B,U2); CLOSING_START(A,U2); CLOSING_START(B,U1) |
| -7.45 | TRACK_APPEARED_LEFT(A,U6) |
| -7.20 | TRACK_APPEARED_FRONT(A,B); CLOSING_START(A,B) |
| -6.90 | TRACK_LOST(A,U6) |
| -6.10 | TRACK_APPEARED_LEFT(A,U5) |
| -5.45 | TRACK_LOST(A,U5) |
| -5.15 | TRACK_LOST(A,U4) |
| -5.00 | TRACK_APPEARED_LEFT(A,U5) |
| -4.50 | TRACK_LOST(A,U5) |
| -4.15 | TRACK_APPEARED_LEFT(A,U5) |
| -3.80 | TRACK_LOST(A,U5) |
| -2.15 | CLOSING_END(B,U1) |
| -2.05 | TRACK_APPEARED_LEFT(B,A); CLOSING_START(B,A) |
| -2.00 | TURN_LEFT_START(B); CRITICAL_TTC_START(A,B); CUT_IN_FROM_RIGHT_START(A,B) |
| -1.85 | CLOSING_START(B,U1) |
| -1.55 | CRITICAL_TTC_START(B,A) |
| -1.45 | EGO_PATH_ENTRY(B,U5) |
| -1.30 | TRACK_LOST(A,U3) |
| -1.20 | EGO_PATH_ENTRY(A,B) |
| -1.15 | CLOSING_END(B,U1) |
| -1.00 | TURN_LEFT_END(B) |
| -0.95 | THROTTLE_END(B); BRAKE_START(B) |
| -0.90 | TRACK_LOST(B,A) |
| -0.10 | CLOSING_END(A,U2); THROTTLE_START(B) |
| +0.00 | COLLISION(A,B); CRITICAL_TTC_END(A,B); CRITICAL_TTC_END(B,A); CLOSING_END(A,B); THROTTLE_END(B) |
| +0.05 | THROTTLE_END(A); BRAKE_START(A) |
| +0.20 | TRACK_LOST(B,U3); TRACK_LOST(B,U5) |
| +0.25 | TRACK_APPEARED_LEFT(A,U7) |
| +0.85 | CUT_IN_FROM_RIGHT_END(A,B) |
| +0.95 | TRACK_LOST(A,U1); TRACK_LOST(A,U7) |
| +1.20 | TRACK_APPEARED_RIGHT(A,U8); CLOSING_START(A,U8) |
| +1.25 | TRACK_APPEARED_LEFT(B,U9) |
| +1.45 | MOVING_END(A); STOP_START(A) |
| +1.50 | TRACK_LOST(B,U9) |
| +1.55 | MOVING_END(B); STOP_START(B) |
| +2.00 | TRACK_APPEARED_RIGHT(B,U8); CLOSING_START(B,U8) |
| +2.80 | CLOSING_END(A,U8) |
| +2.85 | CLOSING_END(B,U8) |
| +3.65 | TRACK_LOST(B,U1) |
| +4.40 | TRACK_LOST(A,U2) |

## Temporal safety relations

Per track: does the cut-in start before the critical TTC, or was the critical TTC already active? Is the path entry before or after it? Temporal properties only, not causes.

- A's track_006 (B): critical TTC already active before the cut-in: CRITICAL_TTC_START 5.50 <= CUT_IN_FROM_RIGHT_START 5.50 (+0.00 s); EGO_PATH_ENTRY 6.30 after critical TTC (+0.80 s) [local times; t_global: cut_in -2.00, critical_ttc_start -2.00, ego_path_entry -1.20, collision +0.00]
- B's track_002 (unidentified U5): EGO_PATH_ENTRY 6.05, no critical TTC [local times; t_global: ego_path_entry -1.45, collision +0.00]
- B's track_005 (A): CRITICAL_TTC_START 5.95, COLLISION with A 7.50 (+1.55 s) [local times; t_global: critical_ttc_start -1.55, collision +0.00]

## Perceived state before each event, per observing recorder

Each recorder's own belief just before its events, in its own local names (track_001, ...): fusion does not rewrite it. True states are named, unknown ones end with `?`.

| t_global | Recorder | Events (local node) | Perceived state just before |
|---------:|----------|---------------------|-----------------------------|
| -7.50 | A | g01 MOVING_START(A) (A:e01)<br>g03 THROTTLE_START(A) (A:e02)<br>g05 TRACK_APPEARED_LEFT(A,U1) (A:e03)<br>g06 TRACK_APPEARED_LEFT(A,U3) (A:e04)<br>g10 TRACK_APPEARED_RIGHT(A,U2) (A:e05)<br>g11 TRACK_APPEARED_RIGHT(A,U4) (A:e06)<br>g13 CLOSING_START(A,U2) (A:e07) | ego: not yet observed |
| -7.50 | B | g02 MOVING_START(B) (B:e01)<br>g04 THROTTLE_START(B) (B:e02)<br>g07 TRACK_APPEARED_LEFT(B,U1) (B:e05)<br>g08 TRACK_APPEARED_LEFT(B,U3) (B:e03)<br>g09 TRACK_APPEARED_LEFT(B,U5) (B:e04)<br>g12 TRACK_APPEARED_RIGHT(B,U2) (B:e06)<br>g14 CLOSING_START(B,U1) (B:e07) | ego: not yet observed |
| -7.50 | A | g05 TRACK_APPEARED_LEFT(A,U1) (A:e03)<br>g53 TRACK_APPEARED_LEFT(A,U7) (A:e29)<br>g55 TRACK_LOST(A,U1) (A:e31)<br>g56 TRACK_LOST(A,U7) (A:e32) | ego: not yet observed |
| -7.50 | A | g06 TRACK_APPEARED_LEFT(A,U3) (A:e04)<br>g35 TRACK_LOST(A,U3) (A:e21) | ego: not yet observed |
| -7.50 | B | g07 TRACK_APPEARED_LEFT(B,U1) (B:e05)<br>g69 TRACK_LOST(B,U1) (B:e32) | ego: not yet observed |
| -7.50 | B | g08 TRACK_APPEARED_LEFT(B,U3) (B:e03)<br>g09 TRACK_APPEARED_LEFT(B,U5) (B:e04)<br>g51 TRACK_LOST(B,U3) (B:e23)<br>g52 TRACK_LOST(B,U5) (B:e24) | ego: not yet observed |
| -7.50 | A | g10 TRACK_APPEARED_RIGHT(A,U2) (A:e05)<br>g70 TRACK_LOST(A,U2) (A:e38) | ego: not yet observed |
| -7.50 | A | g11 TRACK_APPEARED_RIGHT(A,U4) (A:e06)<br>g21 TRACK_LOST(A,U4) (A:e14) | ego: not yet observed |
| -7.50 | A | g13 CLOSING_START(A,U2) (A:e07)<br>g42 CLOSING_END(A,U2) (A:e23) | ego: not yet observed |
| -7.50 | B | g14 CLOSING_START(B,U1) (B:e07)<br>g26 CLOSING_END(B,U1) (B:e08) | ego: not yet observed |
| -7.45 | A | g15 TRACK_APPEARED_LEFT(A,U6) (A:e08) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC?<br>track_002: CLOSING, CRITICAL_TTC?<br>track_003: CRITICAL_TTC?<br>track_004: CRITICAL_TTC? |
| -7.45 | A | g15 TRACK_APPEARED_LEFT(A,U6) (A:e08)<br>g18 TRACK_LOST(A,U6) (A:e11) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC?<br>track_002: CLOSING, CRITICAL_TTC?<br>track_003: CRITICAL_TTC?<br>track_004: CRITICAL_TTC? |
| -7.20 | A | g16 TRACK_APPEARED_FRONT(A,B) (A:e09)<br>g17 CLOSING_START(A,B) (A:e10) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC?<br>track_002: CLOSING, CRITICAL_TTC?<br>track_003: CRITICAL_TTC?<br>track_004: CRITICAL_TTC?<br>track_005: IN_EGO_PATH, CRITICAL_TTC?, CUT_IN_FROM_LEFT?, CUT_IN_FROM_RIGHT? |
| -7.20 | A | g17 CLOSING_START(A,B) (A:e10)<br>g30 CRITICAL_TTC_START(A,B) (A:e19)<br>g44 COLLISION(A,B) (A:e24)<br>g45 CRITICAL_TTC_END(A,B) (A:e25)<br>g47 CLOSING_END(A,B) (A:e26) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC?<br>track_002: CLOSING, CRITICAL_TTC?<br>track_003: CRITICAL_TTC?<br>track_004: CRITICAL_TTC?<br>track_005: IN_EGO_PATH, CRITICAL_TTC?, CUT_IN_FROM_LEFT?, CUT_IN_FROM_RIGHT? |
| -6.10 | A | g19 TRACK_APPEARED_LEFT(A,U5) (A:e12) | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: CLOSING<br>track_003: no active state<br>track_004: no active state<br>track_006: CLOSING<br>track lost, states UNKNOWN: track_005 |
| -6.10 | A | g19 TRACK_APPEARED_LEFT(A,U5) (A:e12)<br>g20 TRACK_LOST(A,U5) (A:e13) | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: CLOSING<br>track_003: no active state<br>track_004: no active state<br>track_006: CLOSING<br>track lost, states UNKNOWN: track_005 |
| -5.00 | A | g22 TRACK_APPEARED_LEFT(A,U5) (A:e15) | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: CLOSING<br>track_003: no active state<br>track_006: CLOSING<br>track lost, states UNKNOWN: track_004, track_005, track_007 |
| -5.00 | A | g22 TRACK_APPEARED_LEFT(A,U5) (A:e15)<br>g23 TRACK_LOST(A,U5) (A:e16) | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: CLOSING<br>track_003: no active state<br>track_006: CLOSING<br>track lost, states UNKNOWN: track_004, track_005, track_007 |
| -4.15 | A | g24 TRACK_APPEARED_LEFT(A,U5) (A:e17) | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: CLOSING<br>track_003: no active state<br>track_006: CLOSING<br>track lost, states UNKNOWN: track_004, track_005, track_007, track_008 |
| -4.15 | A | g24 TRACK_APPEARED_LEFT(A,U5) (A:e17)<br>g25 TRACK_LOST(A,U5) (A:e18) | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: CLOSING<br>track_003: no active state<br>track_006: CLOSING<br>track lost, states UNKNOWN: track_004, track_005, track_007, track_008 |
| -2.05 | B | g27 TRACK_APPEARED_LEFT(B,A) (B:e09)<br>g28 CLOSING_START(B,A) (B:e10) | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: no active state<br>track_003: no active state<br>track_004: no active state |
| -2.05 | B | g27 TRACK_APPEARED_LEFT(B,A) (B:e09)<br>g41 TRACK_LOST(B,A) (B:e19) | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: no active state<br>track_003: no active state<br>track_004: no active state |
| -2.00 | B | g29 TURN_LEFT_START(B) (B:e11) | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: no active state<br>track_003: no active state<br>track_004: no active state<br>track_005: CLOSING, CRITICAL_TTC? |
| -2.00 | A | g30 CRITICAL_TTC_START(A,B) (A:e19)<br>g31 CUT_IN_FROM_RIGHT_START(A,B) (A:e20) | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: CLOSING<br>track_003: no active state<br>track_006: CLOSING<br>track lost, states UNKNOWN: track_004, track_005, track_007, track_008, track_009 |
| -2.00 | A | g31 CUT_IN_FROM_RIGHT_START(A,B) (A:e20)<br>g54 CUT_IN_FROM_RIGHT_END(A,B) (A:e30) | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: CLOSING<br>track_003: no active state<br>track_006: CLOSING<br>track lost, states UNKNOWN: track_004, track_005, track_007, track_008, track_009 |
| -1.85 | B | g32 CLOSING_START(B,U1) (B:e12) | ego: MOVING, THROTTLE, TURN_LEFT<br>track_001: no active state<br>track_002: no active state<br>track_003: no active state<br>track_004: no active state<br>track_005: CLOSING, CRITICAL_TTC? |
| -1.85 | B | g32 CLOSING_START(B,U1) (B:e12)<br>g37 CLOSING_END(B,U1) (B:e15) | ego: MOVING, THROTTLE, TURN_LEFT<br>track_001: no active state<br>track_002: no active state<br>track_003: no active state<br>track_004: no active state<br>track_005: CLOSING, CRITICAL_TTC? |
| -1.55 | B | g33 CRITICAL_TTC_START(B,A) (B:e13) | ego: MOVING, THROTTLE, TURN_LEFT<br>track_001: no active state<br>track_002: no active state<br>track_003: CLOSING<br>track_004: no active state<br>track_005: CLOSING, CRITICAL_TTC? |
| -1.45 | B | g34 EGO_PATH_ENTRY(B,U5) (B:e14) | ego: MOVING, THROTTLE, TURN_LEFT<br>track_001: no active state<br>track_002: no active state<br>track_003: CLOSING<br>track_004: no active state<br>track_005: CLOSING, CRITICAL_TTC |
| -1.20 | A | g36 EGO_PATH_ENTRY(A,B) (A:e22) | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: CLOSING<br>track_006: CLOSING, CRITICAL_TTC, CUT_IN_FROM_RIGHT<br>track lost, states UNKNOWN: track_003, track_004, track_005, track_007, track_008, track_009 |
| -1.00 | B | g38 TURN_LEFT_END(B) (B:e16) | ego: MOVING, THROTTLE, TURN_LEFT<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_005: CLOSING, CRITICAL_TTC |
| -0.95 | B | g39 THROTTLE_END(B) (B:e17)<br>g40 BRAKE_START(B) (B:e18) | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_005: CLOSING, CRITICAL_TTC |
| -0.10 | B | g43 THROTTLE_START(B) (B:e20) | ego: MOVING, BRAKE<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track lost, states UNKNOWN: track_005 |
| +0.00 | B | g44 COLLISION(A,B) (B:e21)<br>g46 CRITICAL_TTC_END(B,A) (B:e21)<br>g48 THROTTLE_END(B) (B:e22) | ego: MOVING, BRAKE, THROTTLE<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track lost, states UNKNOWN: track_005 |
| +0.05 | A | g49 THROTTLE_END(A) (A:e27)<br>g50 BRAKE_START(A) (A:e28) | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: no active state<br>track_006: IN_EGO_PATH, CUT_IN_FROM_RIGHT<br>track lost, states UNKNOWN: track_003, track_004, track_005, track_007, track_008, track_009 |
| +0.25 | A | g53 TRACK_APPEARED_LEFT(A,U7) (A:e29) | ego: MOVING, BRAKE<br>track_001: no active state<br>track_002: no active state<br>track_006: IN_EGO_PATH, CUT_IN_FROM_RIGHT<br>track lost, states UNKNOWN: track_003, track_004, track_005, track_007, track_008, track_009 |
| +1.20 | A | g57 TRACK_APPEARED_RIGHT(A,U8) (A:e33)<br>g58 CLOSING_START(A,U8) (A:e34) | ego: MOVING, BRAKE<br>track_002: no active state<br>track_006: IN_EGO_PATH<br>track lost, states UNKNOWN: track_001, track_003, track_004, track_005, track_007, track_008, track_009, track_010 |
| +1.20 | A | g58 CLOSING_START(A,U8) (A:e34)<br>g67 CLOSING_END(A,U8) (A:e37) | ego: MOVING, BRAKE<br>track_002: no active state<br>track_006: IN_EGO_PATH<br>track lost, states UNKNOWN: track_001, track_003, track_004, track_005, track_007, track_008, track_009, track_010 |
| +1.25 | B | g59 TRACK_APPEARED_LEFT(B,U9) (B:e25) | ego: MOVING, BRAKE<br>track_003: no active state<br>track_004: no active state<br>track lost, states UNKNOWN: track_001, track_002, track_005 |
| +1.25 | B | g59 TRACK_APPEARED_LEFT(B,U9) (B:e25)<br>g62 TRACK_LOST(B,U9) (B:e26) | ego: MOVING, BRAKE<br>track_003: no active state<br>track_004: no active state<br>track lost, states UNKNOWN: track_001, track_002, track_005 |
| +1.45 | A | g60 MOVING_END(A) (A:e35)<br>g61 STOP_START(A) (A:e36) | ego: MOVING, BRAKE<br>track_002: no active state<br>track_006: IN_EGO_PATH<br>track_011: CLOSING, CRITICAL_TTC?<br>track lost, states UNKNOWN: track_001, track_003, track_004, track_005, track_007, track_008, track_009, track_010 |
| +1.55 | B | g63 MOVING_END(B) (B:e27)<br>g64 STOP_START(B) (B:e28) | ego: MOVING, BRAKE<br>track_003: no active state<br>track_004: no active state<br>track lost, states UNKNOWN: track_001, track_002, track_005, track_006 |
| +2.00 | B | g65 TRACK_APPEARED_RIGHT(B,U8) (B:e29)<br>g66 CLOSING_START(B,U8) (B:e30) | ego: STOP, BRAKE<br>track_003: no active state<br>track_004: no active state<br>track lost, states UNKNOWN: track_001, track_002, track_005, track_006 |
| +2.00 | B | g66 CLOSING_START(B,U8) (B:e30)<br>g68 CLOSING_END(B,U8) (B:e31) | ego: STOP, BRAKE<br>track_003: no active state<br>track_004: no active state<br>track lost, states UNKNOWN: track_001, track_002, track_005, track_006 |

## Plain-language reading

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
