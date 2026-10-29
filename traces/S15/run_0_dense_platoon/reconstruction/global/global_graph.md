# Global graph - S15/run_0_dense_platoon

Global time `t_global` is 0 at the reference collision. The local graphs were not modified: every node lists the local node(s) and local time(s) it comes from.

Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.

## Entities

| Entity | Kind | Details |
|--------|------|---------|
| A | recorder | clock ALIGNED; observed by others as: B:track_007 |
| B | recorder | clock ALIGNED; observed by others as: - |
| U1 | anonymous_road_user | anonymous; observed by A, B as A:track_001, B:track_005 |
| U2 | anonymous_road_user | anonymous; observed by A as A:track_002 |
| U3 | anonymous_road_user | anonymous; observed by A, B as A:track_003, B:track_004 |
| U4 | anonymous_road_user | anonymous; observed by A, B as A:track_004, B:track_006 |
| U5 | anonymous_road_user | anonymous; observed by A, B as A:track_005, B:track_002, B:track_008 |
| U6 | anonymous_road_user | anonymous; observed by A, B as A:track_006, B:track_001 |
| U7 | anonymous_road_user | anonymous; observed by A, B as A:track_007, B:track_003 |
| U9 | anonymous_road_user | anonymous; observed by A as A:track_008 |
| U10 | anonymous_road_user | anonymous; observed by A as A:track_009 |
| U11 | anonymous_road_user | anonymous; observed by A as A:track_010 |
| U8 | anonymous_road_user | anonymous; observed by B as B:track_009 |

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

## Nodes

| Id | Global time | Type | Actor | Subject / participants | Observed by (local node @ local time) | Details |
|----|------------:|------|-------|------------------------|----------------------------------------|---------|
| g01 | -7.45 | MOVING_START | A | - | A:e01 @ 0.00 | active_at_first_observation=True |
| g02 | -7.45 | MOVING_START | B | - | B:e01 @ 0.00 | active_at_first_observation=True |
| g03 | -7.45 | THROTTLE_START | A | - | A:e02 @ 0.00 | active_at_first_observation=True |
| g04 | -7.45 | THROTTLE_START | B | - | B:e02 @ 0.00 | active_at_first_observation=True |
| g05 | -7.45 | TRACK_APPEARED_FRONT | A | U2 | A:e03 @ 0.00, A:e30 @ 11.85 | initial_in_ego_path=True; source_track=track_002; aggregation=entity_state_union; source_tracks=['A:track_002'] |
| g06 | -7.45 | TRACK_APPEARED_LEFT | A | U1 | A:e04 @ 0.00, A:e25 @ 9.55 | initial_in_ego_path=False; source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g07 | -7.45 | TRACK_APPEARED_LEFT | A | U5 | A:e05 @ 0.00, A:e24 @ 8.95 | initial_in_ego_path=False; source_track=track_005; aggregation=entity_state_union; source_tracks=['A:track_005'] |
| g08 | -7.45 | TRACK_APPEARED_LEFT | A | U6 | A:e06 @ 0.00 | initial_in_ego_path=False; source_track=track_006; aggregation=entity_state_union; source_tracks=['A:track_006'] |
| g09 | -7.45 | TRACK_APPEARED_LEFT | B | U1 | B:e05 @ 0.00, B:e19 @ 7.40 | initial_in_ego_path=False; source_track=track_005; aggregation=entity_state_union; source_tracks=['B:track_005'] |
| g10 | -7.45 | TRACK_APPEARED_LEFT | B | U5 | B:e04 @ 0.00, B:e12 @ 3.70 | initial_in_ego_path=False; source_track=track_002; aggregation=entity_state_union; source_tracks=['B:track_002'] |
| g11 | -7.45 | TRACK_APPEARED_LEFT | B | U6 | B:e03 @ 0.00, B:e23 @ 7.45 | initial_in_ego_path=False; source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g12 | -7.45 | TRACK_APPEARED_RIGHT | A | U3 | A:e07 @ 0.00, A:e31 @ 11.90 | initial_in_ego_path=False; source_track=track_003; aggregation=entity_state_union; source_tracks=['A:track_003'] |
| g13 | -7.45 | TRACK_APPEARED_RIGHT | A | U4 | A:e08 @ 0.00 | initial_in_ego_path=False; source_track=track_004; aggregation=entity_state_union; source_tracks=['A:track_004'] |
| g14 | -7.45 | TRACK_APPEARED_RIGHT | A | U7 | A:e09 @ 0.00 | initial_in_ego_path=False; source_track=track_007; aggregation=entity_state_union; source_tracks=['A:track_007'] |
| g15 | -7.45 | TRACK_APPEARED_RIGHT | B | U3 | B:e07 @ 0.00, B:e18 @ 7.40 | initial_in_ego_path=False; source_track=track_004; aggregation=entity_state_union; source_tracks=['B:track_004'] |
| g16 | -7.45 | TRACK_APPEARED_RIGHT | B | U4 | B:e08 @ 0.00, B:e11 @ 3.55 | initial_in_ego_path=False; source_track=track_006; aggregation=entity_state_union; source_tracks=['B:track_006'] |
| g17 | -7.45 | TRACK_APPEARED_RIGHT | B | U7 | B:e06 @ 0.00, B:e24 @ 7.45 | initial_in_ego_path=False; source_track=track_003; aggregation=entity_state_union; source_tracks=['B:track_003'] |
| g18 | -7.40 | TRACK_APPEARED_FRONT | B | A | B:e09 @ 0.05 | initial_in_ego_path=True; source_track=track_007; aggregation=entity_state_union; source_tracks=['B:track_007'] |
| g19 | -6.95 | CRITICAL_TTC_START | A | U2 | A:e10 @ 0.50, A:e15 @ 6.80 | source_track=track_002; aggregation=entity_state_union; source_tracks=['A:track_002'] |
| g20 | -6.90 | CRITICAL_TTC_START | B | A | B:e10 @ 0.55, B:e21 @ 7.45 | source_track=track_007; aggregation=entity_state_union; source_tracks=['B:track_007'] |
| g21 | -3.90 | TRACK_LOST | B | U4 | B:e11 @ 3.55 | source_track=track_006; aggregation=entity_state_union; source_tracks=['B:track_006'] |
| g22 | -3.75 | TRACK_LOST | B | U5 | B:e12 @ 3.70 | source_track=track_002; aggregation=entity_state_union; source_tracks=['B:track_002'] |
| g23 | -1.50 | THROTTLE_END | A | - | A:e11 @ 5.95 |  |
| g24 | -1.50 | BRAKE_START | A | - | A:e12 @ 5.95 |  |
| g25 | -1.30 | TRACK_APPEARED_LEFT | B | U5 | B:e13 @ 6.15, B:e17 @ 6.75 | initial_in_ego_path=False; source_track=track_008; aggregation=entity_state_union; source_tracks=['B:track_008'] |
| g26 | -1.25 | CLOSING_START | B | A | B:e14 @ 6.20, B:e22 @ 7.45 | source_track=track_007; aggregation=entity_state_union; source_tracks=['B:track_007'] |
| g27 | -1.15 | CLOSING_START | A | U6 | A:e13 @ 6.30, A:e17 @ 7.05 | source_track=track_006; aggregation=entity_state_union; source_tracks=['A:track_006'] |
| g28 | -1.10 | TRACK_APPEARED_RIGHT | B | U8 | B:e15 @ 6.35, B:e16 @ 6.60 | initial_in_ego_path=False; source_track=track_009; aggregation=entity_state_union; source_tracks=['B:track_009'] |
| g29 | -1.10 | CLOSING_START | A | U7 | A:e14 @ 6.35, A:e16 @ 6.90 | source_track=track_007; aggregation=entity_state_union; source_tracks=['A:track_007'] |
| g30 | -0.85 | TRACK_LOST | B | U8 | B:e16 @ 6.60 | source_track=track_009; aggregation=entity_state_union; source_tracks=['B:track_009'] |
| g31 | -0.70 | TRACK_LOST | B | U5 | B:e17 @ 6.75 | source_track=track_008; aggregation=entity_state_union; source_tracks=['B:track_008'] |
| g32 | -0.65 | CRITICAL_TTC_END | A | U2 | A:e15 @ 6.80 | source_track=track_002; aggregation=entity_state_union; source_tracks=['A:track_002'] |
| g33 | -0.55 | CLOSING_END | A | U7 | A:e16 @ 6.90 | source_track=track_007; aggregation=entity_state_union; source_tracks=['A:track_007'] |
| g34 | -0.40 | CLOSING_END | A | U6 | A:e17 @ 7.05 | source_track=track_006; aggregation=entity_state_union; source_tracks=['A:track_006'] |
| g35 | -0.30 | MOVING_END | A | - | A:e18 @ 7.15 |  |
| g36 | -0.30 | STOP_START | A | - | A:e19 @ 7.15 |  |
| g37 | -0.05 | TRACK_LOST | B | U1 | B:e19 @ 7.40 | source_track=track_005; aggregation=entity_state_union; source_tracks=['B:track_005'] |
| g38 | -0.05 | TRACK_LOST | B | U3 | B:e18 @ 7.40 | source_track=track_004; aggregation=entity_state_union; source_tracks=['B:track_004'] |
| g39 | 0.00 | COLLISION | - | A, B | A:e20 @ 7.45, B:e20 @ 7.45 | matched_event=collision_001; reference_event=True; peak_impulse=A 34836.87, B 34836.87 |
| g40 | 0.00 | CRITICAL_TTC_END | B | A | B:e21 @ 7.45 | source_track=track_007; aggregation=entity_state_union; source_tracks=['B:track_007'] |
| g41 | 0.00 | CLOSING_END | B | A | B:e22 @ 7.45 | source_track=track_007; aggregation=entity_state_union; source_tracks=['B:track_007'] |
| g42 | 0.00 | TRACK_LOST | B | U6 | B:e23 @ 7.45 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g43 | 0.00 | TRACK_LOST | B | U7 | B:e24 @ 7.45 | source_track=track_003; aggregation=entity_state_union; source_tracks=['B:track_003'] |
| g44 | 0.05 | BRAKE_END | A | - | A:e21 @ 7.50 |  |
| g45 | 0.05 | THROTTLE_END | B | - | B:e25 @ 7.50 |  |
| g46 | 0.45 | TRACK_APPEARED_FRONT | A | U9 | A:e22 @ 7.90, A:e27 @ 10.25 | initial_in_ego_path=True; source_track=track_008; aggregation=entity_state_union; source_tracks=['A:track_008'] |
| g47 | 0.55 | BRAKE_START | A | - | A:e23 @ 8.00 |  |
| g48 | 1.50 | TRACK_LOST | A | U5 | A:e24 @ 8.95 | source_track=track_005; aggregation=entity_state_union; source_tracks=['A:track_005'] |
| g49 | 2.10 | TRACK_LOST | A | U1 | A:e25 @ 9.55 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g50 | 2.60 | TRACK_APPEARED_LEFT | A | U10 | A:e26 @ 10.05, A:e29 @ 11.35 | initial_in_ego_path=False; source_track=track_009; aggregation=entity_state_union; source_tracks=['A:track_009'] |
| g51 | 2.80 | TRACK_LOST | A | U9 | A:e27 @ 10.25 | source_track=track_008; aggregation=entity_state_union; source_tracks=['A:track_008'] |
| g52 | 2.95 | TRACK_APPEARED_LEFT | A | U11 | A:e28 @ 10.40 | initial_in_ego_path=False; source_track=track_010; aggregation=entity_state_union; source_tracks=['A:track_010'] |
| g53 | 3.90 | TRACK_LOST | A | U10 | A:e29 @ 11.35 | source_track=track_009; aggregation=entity_state_union; source_tracks=['A:track_009'] |
| g54 | 4.40 | TRACK_LOST | A | U2 | A:e30 @ 11.85 | source_track=track_002; aggregation=entity_state_union; source_tracks=['A:track_002'] |
| g55 | 4.45 | TRACK_LOST | A | U3 | A:e31 @ 11.90 | source_track=track_003; aggregation=entity_state_union; source_tracks=['A:track_003'] |

## Edges

```
    g01 --PRECEDES--> g18
    g02 --PRECEDES--> g18
    g03 --PRECEDES--> g18
    g04 --PRECEDES--> g18
    g05 --PRECEDES--> g18
    g06 --PRECEDES--> g18
    g07 --PRECEDES--> g18
    g08 --PRECEDES--> g18
    g09 --PRECEDES--> g18
    g10 --PRECEDES--> g18
    g11 --PRECEDES--> g18
    g12 --PRECEDES--> g18
    g13 --PRECEDES--> g18
    g14 --PRECEDES--> g18
    g15 --PRECEDES--> g18
    g16 --PRECEDES--> g18
    g17 --PRECEDES--> g18
    g18 --PRECEDES--> g19
    g19 --PRECEDES--> g20
    g20 --PRECEDES--> g21
    g21 --PRECEDES--> g22
    g22 --PRECEDES--> g23
    g22 --PRECEDES--> g24
    g23 --PRECEDES--> g25
    g24 --PRECEDES--> g25
    g25 --PRECEDES--> g26
    g26 --PRECEDES--> g27
    g27 --PRECEDES--> g28
    g27 --PRECEDES--> g29
    g28 --PRECEDES--> g30
    g29 --PRECEDES--> g30
    g30 --PRECEDES--> g31
    g31 --PRECEDES--> g32
    g32 --PRECEDES--> g33
    g33 --PRECEDES--> g34
    g34 --PRECEDES--> g35
    g34 --PRECEDES--> g36
    g35 --PRECEDES--> g37
    g35 --PRECEDES--> g38
    g36 --PRECEDES--> g37
    g36 --PRECEDES--> g38
    g37 --PRECEDES--> g39
    g37 --PRECEDES--> g40
    g37 --PRECEDES--> g41
    g37 --PRECEDES--> g42
    g37 --PRECEDES--> g43
    g38 --PRECEDES--> g39
    g38 --PRECEDES--> g40
    g38 --PRECEDES--> g41
    g38 --PRECEDES--> g42
    g38 --PRECEDES--> g43
    g39 --PRECEDES--> g44
    g39 --PRECEDES--> g45
    g40 --PRECEDES--> g44
    g40 --PRECEDES--> g45
    g41 --PRECEDES--> g44
    g41 --PRECEDES--> g45
    g42 --PRECEDES--> g44
    g42 --PRECEDES--> g45
    g43 --PRECEDES--> g44
    g43 --PRECEDES--> g45
    g44 --PRECEDES--> g46
    g45 --PRECEDES--> g46
    g46 --PRECEDES--> g47
    g47 --PRECEDES--> g48
    g48 --PRECEDES--> g49
    g49 --PRECEDES--> g50
    g50 --PRECEDES--> g51
    g51 --PRECEDES--> g52
    g52 --PRECEDES--> g53
    g53 --PRECEDES--> g54
    g54 --PRECEDES--> g55
    g05 --SAME_TRACK--> g19
    g08 --SAME_TRACK--> g27
    g14 --SAME_TRACK--> g29
    g05 --SAME_TRACK--> g32
    g14 --SAME_TRACK--> g33
    g08 --SAME_TRACK--> g34
    g07 --SAME_TRACK--> g48
    g06 --SAME_TRACK--> g49
    g46 --SAME_TRACK--> g51
    g50 --SAME_TRACK--> g53
    g05 --SAME_TRACK--> g54
    g12 --SAME_TRACK--> g55
    g18 --SAME_TRACK--> g20
    g16 --SAME_TRACK--> g21
    g10 --SAME_TRACK--> g22
    g18 --SAME_TRACK--> g26
    g28 --SAME_TRACK--> g30
    g25 --SAME_TRACK--> g31
    g15 --SAME_TRACK--> g38
    g09 --SAME_TRACK--> g37
    g18 --SAME_TRACK--> g40
    g18 --SAME_TRACK--> g41
    g11 --SAME_TRACK--> g42
    g17 --SAME_TRACK--> g43
```

## Global trace

Events in one row are simultaneous at 0.05 s resolution: their order is unresolved.

| t_global | Events |
|---------:|--------|
| -7.45 | MOVING_START(A); MOVING_START(B); THROTTLE_START(A); THROTTLE_START(B); TRACK_APPEARED_FRONT(A,U2); TRACK_APPEARED_LEFT(A,U1); TRACK_APPEARED_LEFT(A,U5); TRACK_APPEARED_LEFT(A,U6); TRACK_APPEARED_LEFT(B,U1); TRACK_APPEARED_LEFT(B,U5); TRACK_APPEARED_LEFT(B,U6); TRACK_APPEARED_RIGHT(A,U3); TRACK_APPEARED_RIGHT(A,U4); TRACK_APPEARED_RIGHT(A,U7); TRACK_APPEARED_RIGHT(B,U3); TRACK_APPEARED_RIGHT(B,U4); TRACK_APPEARED_RIGHT(B,U7) |
| -7.40 | TRACK_APPEARED_FRONT(B,A) |
| -6.95 | CRITICAL_TTC_START(A,U2) |
| -6.90 | CRITICAL_TTC_START(B,A) |
| -3.90 | TRACK_LOST(B,U4) |
| -3.75 | TRACK_LOST(B,U5) |
| -1.50 | THROTTLE_END(A); BRAKE_START(A) |
| -1.30 | TRACK_APPEARED_LEFT(B,U5) |
| -1.25 | CLOSING_START(B,A) |
| -1.15 | CLOSING_START(A,U6) |
| -1.10 | TRACK_APPEARED_RIGHT(B,U8); CLOSING_START(A,U7) |
| -0.85 | TRACK_LOST(B,U8) |
| -0.70 | TRACK_LOST(B,U5) |
| -0.65 | CRITICAL_TTC_END(A,U2) |
| -0.55 | CLOSING_END(A,U7) |
| -0.40 | CLOSING_END(A,U6) |
| -0.30 | MOVING_END(A); STOP_START(A) |
| -0.05 | TRACK_LOST(B,U1); TRACK_LOST(B,U3) |
| +0.00 | COLLISION(A,B); CRITICAL_TTC_END(B,A); CLOSING_END(B,A); TRACK_LOST(B,U6); TRACK_LOST(B,U7) |
| +0.05 | BRAKE_END(A); THROTTLE_END(B) |
| +0.45 | TRACK_APPEARED_FRONT(A,U9) |
| +0.55 | BRAKE_START(A) |
| +1.50 | TRACK_LOST(A,U5) |
| +2.10 | TRACK_LOST(A,U1) |
| +2.60 | TRACK_APPEARED_LEFT(A,U10) |
| +2.80 | TRACK_LOST(A,U9) |
| +2.95 | TRACK_APPEARED_LEFT(A,U11) |
| +3.90 | TRACK_LOST(A,U10) |
| +4.40 | TRACK_LOST(A,U2) |
| +4.45 | TRACK_LOST(A,U3) |

## Temporal safety relations

Per track: does the cut-in start before the critical TTC, or was the critical TTC already active? Is the path entry before or after it? Temporal properties only, not causes.

- A's track_002 (unidentified U2): CRITICAL_TTC_START 0.50, COLLISION 7.45 (+6.95 s) [local times; t_global: critical_ttc_start -6.95, collision +0.00]
- B's track_007 (A): CRITICAL_TTC_START 0.55, COLLISION with A 7.45 (+6.90 s) [local times; t_global: critical_ttc_start -6.90, collision +0.00]

## Perceived state before each event, per observing recorder

Each recorder's own belief just before its events, in its own local names (track_001, ...): fusion does not rewrite it. True states are named, unknown ones end with `?`.

| t_global | Recorder | Events (local node) | Perceived state just before |
|---------:|----------|---------------------|-----------------------------|
| -7.45 | A | g01 MOVING_START(A) (A:e01)<br>g03 THROTTLE_START(A) (A:e02)<br>g05 TRACK_APPEARED_FRONT(A,U2) (A:e03)<br>g06 TRACK_APPEARED_LEFT(A,U1) (A:e04)<br>g07 TRACK_APPEARED_LEFT(A,U5) (A:e05)<br>g08 TRACK_APPEARED_LEFT(A,U6) (A:e06)<br>g12 TRACK_APPEARED_RIGHT(A,U3) (A:e07)<br>g13 TRACK_APPEARED_RIGHT(A,U4) (A:e08)<br>g14 TRACK_APPEARED_RIGHT(A,U7) (A:e09) | ego: not yet observed |
| -7.45 | B | g02 MOVING_START(B) (B:e01)<br>g04 THROTTLE_START(B) (B:e02)<br>g09 TRACK_APPEARED_LEFT(B,U1) (B:e05)<br>g10 TRACK_APPEARED_LEFT(B,U5) (B:e04)<br>g11 TRACK_APPEARED_LEFT(B,U6) (B:e03)<br>g15 TRACK_APPEARED_RIGHT(B,U3) (B:e07)<br>g16 TRACK_APPEARED_RIGHT(B,U4) (B:e08)<br>g17 TRACK_APPEARED_RIGHT(B,U7) (B:e06) | ego: not yet observed |
| -7.45 | A | g05 TRACK_APPEARED_FRONT(A,U2) (A:e03)<br>g54 TRACK_LOST(A,U2) (A:e30) | ego: not yet observed |
| -7.45 | A | g06 TRACK_APPEARED_LEFT(A,U1) (A:e04)<br>g49 TRACK_LOST(A,U1) (A:e25) | ego: not yet observed |
| -7.45 | A | g07 TRACK_APPEARED_LEFT(A,U5) (A:e05)<br>g48 TRACK_LOST(A,U5) (A:e24) | ego: not yet observed |
| -7.45 | B | g09 TRACK_APPEARED_LEFT(B,U1) (B:e05)<br>g15 TRACK_APPEARED_RIGHT(B,U3) (B:e07)<br>g37 TRACK_LOST(B,U1) (B:e19)<br>g38 TRACK_LOST(B,U3) (B:e18) | ego: not yet observed |
| -7.45 | B | g10 TRACK_APPEARED_LEFT(B,U5) (B:e04)<br>g22 TRACK_LOST(B,U5) (B:e12) | ego: not yet observed |
| -7.45 | B | g11 TRACK_APPEARED_LEFT(B,U6) (B:e03)<br>g17 TRACK_APPEARED_RIGHT(B,U7) (B:e06)<br>g20 CRITICAL_TTC_START(B,A) (B:e10)<br>g26 CLOSING_START(B,A) (B:e14)<br>g39 COLLISION(A,B) (B:e20)<br>g40 CRITICAL_TTC_END(B,A) (B:e21)<br>g41 CLOSING_END(B,A) (B:e22)<br>g42 TRACK_LOST(B,U6) (B:e23)<br>g43 TRACK_LOST(B,U7) (B:e24) | ego: not yet observed |
| -7.45 | A | g12 TRACK_APPEARED_RIGHT(A,U3) (A:e07)<br>g55 TRACK_LOST(A,U3) (A:e31) | ego: not yet observed |
| -7.45 | B | g16 TRACK_APPEARED_RIGHT(B,U4) (B:e08)<br>g21 TRACK_LOST(B,U4) (B:e11) | ego: not yet observed |
| -7.40 | B | g18 TRACK_APPEARED_FRONT(B,A) (B:e09) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC?<br>track_002: CRITICAL_TTC?<br>track_003: CRITICAL_TTC?<br>track_004: CRITICAL_TTC?<br>track_005: CRITICAL_TTC?<br>track_006: CRITICAL_TTC? |
| -6.95 | A | g19 CRITICAL_TTC_START(A,U2) (A:e10) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC?<br>track_002: IN_EGO_PATH, CRITICAL_TTC?<br>track_003: CRITICAL_TTC?<br>track_004: CRITICAL_TTC?<br>track_005: CRITICAL_TTC?<br>track_006: CRITICAL_TTC?<br>track_007: CRITICAL_TTC? |
| -6.95 | A | g19 CRITICAL_TTC_START(A,U2) (A:e10)<br>g32 CRITICAL_TTC_END(A,U2) (A:e15) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC?<br>track_002: IN_EGO_PATH, CRITICAL_TTC?<br>track_003: CRITICAL_TTC?<br>track_004: CRITICAL_TTC?<br>track_005: CRITICAL_TTC?<br>track_006: CRITICAL_TTC?<br>track_007: CRITICAL_TTC? |
| -6.90 | B | g20 CRITICAL_TTC_START(B,A) (B:e10) | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: no active state<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_006: no active state<br>track_007: IN_EGO_PATH, CRITICAL_TTC? |
| -1.50 | A | g23 THROTTLE_END(A) (A:e11)<br>g24 BRAKE_START(A) (A:e12) | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: CRITICAL_TTC, IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_006: no active state<br>track_007: no active state |
| -1.30 | B | g25 TRACK_APPEARED_LEFT(B,U5) (B:e13) | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_007: CRITICAL_TTC, IN_EGO_PATH<br>track lost, states UNKNOWN: track_002, track_006 |
| -1.30 | B | g25 TRACK_APPEARED_LEFT(B,U5) (B:e13)<br>g31 TRACK_LOST(B,U5) (B:e17) | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_007: CRITICAL_TTC, IN_EGO_PATH<br>track lost, states UNKNOWN: track_002, track_006 |
| -1.25 | B | g26 CLOSING_START(B,A) (B:e14) | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_007: CRITICAL_TTC, IN_EGO_PATH<br>track_008: CRITICAL_TTC?<br>track lost, states UNKNOWN: track_002, track_006 |
| -1.15 | A | g27 CLOSING_START(A,U6) (A:e13) | ego: MOVING, BRAKE<br>track_001: no active state<br>track_002: CRITICAL_TTC, IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_006: no active state<br>track_007: no active state |
| -1.15 | A | g27 CLOSING_START(A,U6) (A:e13)<br>g34 CLOSING_END(A,U6) (A:e17) | ego: MOVING, BRAKE<br>track_001: no active state<br>track_002: CRITICAL_TTC, IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_006: no active state<br>track_007: no active state |
| -1.10 | B | g28 TRACK_APPEARED_RIGHT(B,U8) (B:e15) | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_007: CLOSING, CRITICAL_TTC, IN_EGO_PATH<br>track_008: CRITICAL_TTC?<br>track lost, states UNKNOWN: track_002, track_006 |
| -1.10 | B | g28 TRACK_APPEARED_RIGHT(B,U8) (B:e15)<br>g30 TRACK_LOST(B,U8) (B:e16) | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_007: CLOSING, CRITICAL_TTC, IN_EGO_PATH<br>track_008: CRITICAL_TTC?<br>track lost, states UNKNOWN: track_002, track_006 |
| -1.10 | A | g29 CLOSING_START(A,U7) (A:e14) | ego: MOVING, BRAKE<br>track_001: no active state<br>track_002: CRITICAL_TTC, IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_006: CLOSING<br>track_007: no active state |
| -1.10 | A | g29 CLOSING_START(A,U7) (A:e14)<br>g33 CLOSING_END(A,U7) (A:e16) | ego: MOVING, BRAKE<br>track_001: no active state<br>track_002: CRITICAL_TTC, IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_006: CLOSING<br>track_007: no active state |
| -0.30 | A | g35 MOVING_END(A) (A:e18)<br>g36 STOP_START(A) (A:e19) | ego: MOVING, BRAKE<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_006: no active state<br>track_007: no active state |
| +0.00 | A | g39 COLLISION(A,B) (A:e20) | ego: STOP, BRAKE<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_006: no active state<br>track_007: no active state |
| +0.05 | A | g44 BRAKE_END(A) (A:e21) | ego: STOP, BRAKE<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_006: no active state<br>track_007: no active state |
| +0.05 | B | g45 THROTTLE_END(B) (B:e25) | ego: MOVING, THROTTLE<br>track_007: IN_EGO_PATH<br>track lost, states UNKNOWN: track_001, track_002, track_003, track_004, track_005, track_006, track_008, track_009 |
| +0.45 | A | g46 TRACK_APPEARED_FRONT(A,U9) (A:e22) | ego: STOP<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_006: no active state<br>track_007: no active state |
| +0.45 | A | g46 TRACK_APPEARED_FRONT(A,U9) (A:e22)<br>g51 TRACK_LOST(A,U9) (A:e27) | ego: STOP<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_006: no active state<br>track_007: no active state |
| +0.55 | A | g47 BRAKE_START(A) (A:e23) | ego: STOP<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_006: no active state<br>track_007: no active state<br>track_008: IN_EGO_PATH, CRITICAL_TTC? |
| +2.60 | A | g50 TRACK_APPEARED_LEFT(A,U10) (A:e26) | ego: STOP, BRAKE<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_006: no active state<br>track_007: no active state<br>track_008: IN_EGO_PATH<br>track lost, states UNKNOWN: track_001, track_005 |
| +2.60 | A | g50 TRACK_APPEARED_LEFT(A,U10) (A:e26)<br>g53 TRACK_LOST(A,U10) (A:e29) | ego: STOP, BRAKE<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_006: no active state<br>track_007: no active state<br>track_008: IN_EGO_PATH<br>track lost, states UNKNOWN: track_001, track_005 |
| +2.95 | A | g52 TRACK_APPEARED_LEFT(A,U11) (A:e28) | ego: STOP, BRAKE<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_006: no active state<br>track_007: no active state<br>track_009: CRITICAL_TTC?<br>track lost, states UNKNOWN: track_001, track_005, track_008 |

## Plain-language reading

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
