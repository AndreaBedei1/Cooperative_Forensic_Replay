# Global graph - S14/run_0_surrounded

Global time `t_global` is 0 at the reference collision. The local graphs were not modified: every node lists the local node(s) and local time(s) it comes from.

Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.

## Entities

| Entity | Kind | Details |
|--------|------|---------|
| A | recorder | clock ALIGNED; observed by others as: B:track_002 |
| B | recorder | clock ALIGNED; observed by others as: A:track_003 |
| U1 | anonymous_road_user | anonymous; observed by A, B as A:track_001, B:track_003 |
| U2 | anonymous_road_user | anonymous; observed by A, B as A:track_002, B:track_005 |
| U3 | anonymous_road_user | anonymous; observed by A, B as A:track_004, B:track_001 |
| U9 | anonymous_road_user | anonymous; observed by A as A:track_005 |
| U7 | anonymous_road_user | anonymous; observed by A, B as A:track_006, B:track_008, B:track_009 |
| U5 | anonymous_road_user | anonymous; observed by A, B as A:track_007, B:track_006 |
| U4 | anonymous_road_user | anonymous; observed by A, B as A:track_008, B:track_004, B:track_010 |
| U11 | anonymous_road_user | anonymous; observed by A, B as A:track_009, B:track_013 |
| U6 | anonymous_road_user | anonymous; observed by B as B:track_007 |
| U8 | anonymous_road_user | anonymous; observed by B as B:track_011 |
| U10 | anonymous_road_user | anonymous; observed by B as B:track_012 |
| U12 | anonymous_road_user | anonymous; observed by B as B:track_014 |

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

## Nodes

| Id | Global time | Type | Actor | Subject / participants | Observed by (local node @ local time) | Details |
|----|------------:|------|-------|------------------------|----------------------------------------|---------|
| g01 | -7.75 | MOVING_START | A | - | A:e01 @ 0.00 | active_at_first_observation=True |
| g02 | -7.75 | MOVING_START | B | - | B:e01 @ 0.00 | active_at_first_observation=True |
| g03 | -7.75 | THROTTLE_START | A | - | A:e02 @ 0.00 | active_at_first_observation=True |
| g04 | -7.75 | THROTTLE_START | B | - | B:e02 @ 0.00 | active_at_first_observation=True |
| g05 | -7.75 | TRACK_APPEARED_FRONT | A | U1 | A:e03 @ 0.00 | initial_in_ego_path=True; source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g06 | -7.75 | TRACK_APPEARED_FRONT | B | U3 | B:e03 @ 0.00 | initial_in_ego_path=True; source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g07 | -7.75 | TRACK_APPEARED_LEFT | A | B | A:e05 @ 0.00 | initial_in_ego_path=False; source_track=track_003; aggregation=entity_state_union; source_tracks=['A:track_003'] |
| g08 | -7.75 | TRACK_APPEARED_LEFT | A | U2 | A:e04 @ 0.00 | initial_in_ego_path=False; source_track=track_002; aggregation=entity_state_union; source_tracks=['A:track_002'] |
| g09 | -7.75 | TRACK_APPEARED_LEFT | B | U4 | B:e04 @ 0.00, B:e13 @ 3.65 | initial_in_ego_path=False; source_track=track_004; aggregation=entity_state_union; source_tracks=['B:track_004'] |
| g10 | -7.75 | TRACK_APPEARED_RIGHT | B | A | B:e05 @ 0.00 | initial_in_ego_path=False; source_track=track_002; aggregation=entity_state_union; source_tracks=['B:track_002'] |
| g11 | -7.75 | TRACK_APPEARED_RIGHT | B | U1 | B:e06 @ 0.00 | initial_in_ego_path=False; source_track=track_003; aggregation=entity_state_union; source_tracks=['B:track_003'] |
| g12 | -7.70 | TRACK_APPEARED_FRONT | B | U6 | B:e07 @ 0.05, B:e12 @ 2.20 | initial_in_ego_path=False; source_track=track_007; aggregation=entity_state_union; source_tracks=['B:track_007'] |
| g13 | -7.70 | TRACK_APPEARED_LEFT | A | U3 | A:e06 @ 0.05 | initial_in_ego_path=False; source_track=track_004; aggregation=entity_state_union; source_tracks=['A:track_004'] |
| g14 | -7.70 | TRACK_APPEARED_LEFT | B | U2 | B:e08 @ 0.05 | initial_in_ego_path=False; source_track=track_005; aggregation=entity_state_union; source_tracks=['B:track_005'] |
| g15 | -7.70 | TRACK_APPEARED_RIGHT | B | U5 | B:e09 @ 0.05 | initial_in_ego_path=False; source_track=track_006; aggregation=entity_state_union; source_tracks=['B:track_006'] |
| g16 | -7.25 | CRITICAL_TTC_START | A | U1 | A:e07 @ 0.50, A:e23 @ 9.00 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g17 | -7.25 | CRITICAL_TTC_START | B | U3 | B:e10 @ 0.50 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g18 | -6.95 | TRACK_APPEARED_RIGHT | B | U7 | B:e11 @ 0.80, B:e14 @ 3.80 | initial_in_ego_path=False; source_track=track_008; aggregation=entity_state_union; source_tracks=['B:track_008'] |
| g19 | -5.55 | TRACK_LOST | B | U6 | B:e12 @ 2.20 | source_track=track_007; aggregation=entity_state_union; source_tracks=['B:track_007'] |
| g20 | -4.10 | TRACK_LOST | B | U4 | B:e13 @ 3.65 | source_track=track_004; aggregation=entity_state_union; source_tracks=['B:track_004'] |
| g21 | -3.95 | TRACK_LOST | B | U7 | B:e14 @ 3.80 | source_track=track_008; aggregation=entity_state_union; source_tracks=['B:track_008'] |
| g22 | -1.40 | TRACK_APPEARED_RIGHT | B | U7 | B:e15 @ 6.35, B:e28 @ 8.85 | initial_in_ego_path=False; source_track=track_009; aggregation=entity_state_union; source_tracks=['B:track_009'] |
| g23 | -1.40 | CRITICAL_TTC_START | A | B | A:e08 @ 6.35, A:e18 @ 7.75 | source_track=track_003; aggregation=entity_state_union; source_tracks=['A:track_003'] |
| g24 | -1.35 | TRACK_APPEARED_LEFT | B | U4 | B:e16 @ 6.40, B:e29 @ 9.35 | initial_in_ego_path=False; source_track=track_010; aggregation=entity_state_union; source_tracks=['B:track_010'] |
| g25 | -1.15 | TRACK_APPEARED_FRONT | B | U8 | B:e17 @ 6.60, B:e19 @ 7.00 | initial_in_ego_path=False; source_track=track_011; aggregation=entity_state_union; source_tracks=['B:track_011'] |
| g26 | -0.80 | CLOSING_START | A | B | A:e09 @ 6.95, A:e21 @ 7.85 | source_track=track_003; aggregation=entity_state_union; source_tracks=['A:track_003'] |
| g27 | -0.75 | CRITICAL_TTC_START | B | A | B:e18 @ 7.00, B:e24 @ 7.75 | source_track=track_002; aggregation=entity_state_union; source_tracks=['B:track_002'] |
| g28 | -0.75 | TRACK_LOST | B | U8 | B:e19 @ 7.00 | source_track=track_011; aggregation=entity_state_union; source_tracks=['B:track_011'] |
| g29 | -0.70 | TRACK_APPEARED_FRONT | A | U9 | A:e10 @ 7.05, A:e16 @ 7.70 | initial_in_ego_path=False; source_track=track_005; aggregation=entity_state_union; source_tracks=['A:track_005'] |
| g30 | -0.60 | CLOSING_START | B | A | B:e20 @ 7.15, B:e25 @ 7.80 | source_track=track_002; aggregation=entity_state_union; source_tracks=['B:track_002'] |
| g31 | -0.40 | TRACK_APPEARED_FRONT | B | U10 | B:e21 @ 7.35, B:e22 @ 7.65 | initial_in_ego_path=False; source_track=track_012; aggregation=entity_state_union; source_tracks=['B:track_012'] |
| g32 | -0.35 | TRACK_APPEARED_RIGHT | A | U7 | A:e11 @ 7.40 | initial_in_ego_path=True; source_track=track_006; aggregation=entity_state_union; source_tracks=['A:track_006'] |
| g33 | -0.35 | EGO_PATH_ENTRY | A | U3 | A:e12 @ 7.40 | occupancy_evidence=box; occupancy_margin_m=0.56; occupancy_sigma_m=0.27; cause=MUTUAL_LATERAL; geometry=estimated_body; source_track=track_004; aggregation=entity_state_union; source_tracks=['A:track_004'] |
| g34 | -0.35 | CRITICAL_TTC_START | A | U3 | A:e13 @ 7.40 | source_track=track_004; aggregation=entity_state_union; source_tracks=['A:track_004'] |
| g35 | -0.25 | EGO_PATH_ENTRY | A | U9 | A:e14 @ 7.50 | occupancy_evidence=box; occupancy_margin_m=0.67; occupancy_sigma_m=0.34; cause=MUTUAL_LATERAL; geometry=estimated_body; source_track=track_005; aggregation=entity_state_union; source_tracks=['A:track_005'] |
| g36 | -0.10 | TRACK_APPEARED_RIGHT | A | U5 | A:e15 @ 7.65 | initial_in_ego_path=True; source_track=track_007; aggregation=entity_state_union; source_tracks=['A:track_007'] |
| g37 | -0.10 | TRACK_LOST | B | U10 | B:e22 @ 7.65 | source_track=track_012; aggregation=entity_state_union; source_tracks=['B:track_012'] |
| g38 | -0.05 | TRACK_LOST | A | U9 | A:e16 @ 7.70 | source_track=track_005; aggregation=entity_state_union; source_tracks=['A:track_005'] |
| g39 | 0.00 | COLLISION | - | A, B | A:e17 @ 7.75, B:e23 @ 7.75 | matched_event=collision_001; reference_event=True; peak_impulse=A 255.03, B 255.03 |
| g40 | 0.00 | CRITICAL_TTC_END | A | B | A:e18 @ 7.75 | source_track=track_003; aggregation=entity_state_union; source_tracks=['A:track_003'] |
| g41 | 0.00 | CRITICAL_TTC_END | B | A | B:e24 @ 7.75 | source_track=track_002; aggregation=entity_state_union; source_tracks=['B:track_002'] |
| g42 | 0.05 | CLOSING_END | B | A | B:e25 @ 7.80 | source_track=track_002; aggregation=entity_state_union; source_tracks=['B:track_002'] |
| g43 | 0.05 | THROTTLE_END | A | - | A:e19 @ 7.80 |  |
| g44 | 0.05 | THROTTLE_END | B | - | B:e26 @ 7.80 |  |
| g45 | 0.05 | EGO_PATH_ENTRY | A | B | A:e20 @ 7.80 | occupancy_evidence=box; occupancy_margin_m=0.45; occupancy_sigma_m=0.26; cause=RECORDER_LATERAL; geometry=estimated_body; source_track=track_003; aggregation=entity_state_union; source_tracks=['A:track_003'] |
| g46 | 0.10 | CLOSING_END | A | B | A:e21 @ 7.85 | source_track=track_003; aggregation=entity_state_union; source_tracks=['A:track_003'] |
| g47 | 0.30 | TRACK_APPEARED_FRONT | B | U11 | B:e27 @ 8.05 | initial_in_ego_path=True; source_track=track_013; aggregation=entity_state_union; source_tracks=['B:track_013'] |
| g48 | 0.70 | TRACK_APPEARED_LEFT | A | U4 | A:e22 @ 8.45 | initial_in_ego_path=False; source_track=track_008; aggregation=entity_state_union; source_tracks=['A:track_008'] |
| g49 | 1.10 | TRACK_LOST | B | U7 | B:e28 @ 8.85 | source_track=track_009; aggregation=entity_state_union; source_tracks=['B:track_009'] |
| g50 | 1.25 | CRITICAL_TTC_END | A | U1 | A:e23 @ 9.00 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g51 | 1.60 | TRACK_LOST | B | U4 | B:e29 @ 9.35 | source_track=track_010; aggregation=entity_state_union; source_tracks=['B:track_010'] |
| g52 | 1.75 | TRACK_APPEARED_LEFT | A | U11 | A:e24 @ 9.50, A:e28 @ 11.15 | initial_in_ego_path=True; source_track=track_009; aggregation=entity_state_union; source_tracks=['A:track_009'] |
| g53 | 2.10 | EGO_PATH_EXIT | A | U7 | A:e25 @ 9.85 | occupancy_evidence=box; occupancy_margin_m=-0.49; occupancy_sigma_m=0.28; cause=MUTUAL_LATERAL; geometry=estimated_body; source_track=track_006; aggregation=entity_state_union; source_tracks=['A:track_006'] |
| g54 | 2.40 | CRITICAL_TTC_START | A | U5 | A:e26 @ 10.15 | source_track=track_007; aggregation=entity_state_union; source_tracks=['A:track_007'] |
| g55 | 2.70 | CRITICAL_TTC_START | A | U1 | A:e27 @ 10.45 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g56 | 3.30 | CLOSING_START | B | U1 | B:e30 @ 11.05 | source_track=track_003; aggregation=entity_state_union; source_tracks=['B:track_003'] |
| g57 | 3.40 | TRACK_LOST | A | U11 | A:e28 @ 11.15 | source_track=track_009; aggregation=entity_state_union; source_tracks=['A:track_009'] |
| g58 | 3.60 | TRACK_APPEARED_LEFT | B | U12 | B:e31 @ 11.35, B:e32 @ 11.65 | initial_in_ego_path=False; source_track=track_014; aggregation=entity_state_union; source_tracks=['B:track_014'] |
| g59 | 3.60 | EGO_PATH_ENTRY | A | U7 | A:e29 @ 11.35 | occupancy_evidence=returns; occupancy_margin_m=0.49; occupancy_sigma_m=0.25; cause=MUTUAL_LATERAL; geometry=estimated_body; source_track=track_006; aggregation=entity_state_union; source_tracks=['A:track_006'] |
| g60 | 3.90 | TRACK_LOST | B | U12 | B:e32 @ 11.65 | source_track=track_014; aggregation=entity_state_union; source_tracks=['B:track_014'] |

## Edges

```
    g01 --PRECEDES--> g12
    g01 --PRECEDES--> g13
    g01 --PRECEDES--> g14
    g01 --PRECEDES--> g15
    g02 --PRECEDES--> g12
    g02 --PRECEDES--> g13
    g02 --PRECEDES--> g14
    g02 --PRECEDES--> g15
    g03 --PRECEDES--> g12
    g03 --PRECEDES--> g13
    g03 --PRECEDES--> g14
    g03 --PRECEDES--> g15
    g04 --PRECEDES--> g12
    g04 --PRECEDES--> g13
    g04 --PRECEDES--> g14
    g04 --PRECEDES--> g15
    g05 --PRECEDES--> g12
    g05 --PRECEDES--> g13
    g05 --PRECEDES--> g14
    g05 --PRECEDES--> g15
    g06 --PRECEDES--> g12
    g06 --PRECEDES--> g13
    g06 --PRECEDES--> g14
    g06 --PRECEDES--> g15
    g07 --PRECEDES--> g12
    g07 --PRECEDES--> g13
    g07 --PRECEDES--> g14
    g07 --PRECEDES--> g15
    g08 --PRECEDES--> g12
    g08 --PRECEDES--> g13
    g08 --PRECEDES--> g14
    g08 --PRECEDES--> g15
    g09 --PRECEDES--> g12
    g09 --PRECEDES--> g13
    g09 --PRECEDES--> g14
    g09 --PRECEDES--> g15
    g10 --PRECEDES--> g12
    g10 --PRECEDES--> g13
    g10 --PRECEDES--> g14
    g10 --PRECEDES--> g15
    g11 --PRECEDES--> g12
    g11 --PRECEDES--> g13
    g11 --PRECEDES--> g14
    g11 --PRECEDES--> g15
    g12 --PRECEDES--> g16
    g12 --PRECEDES--> g17
    g13 --PRECEDES--> g16
    g13 --PRECEDES--> g17
    g14 --PRECEDES--> g16
    g14 --PRECEDES--> g17
    g15 --PRECEDES--> g16
    g15 --PRECEDES--> g17
    g16 --PRECEDES--> g18
    g17 --PRECEDES--> g18
    g18 --PRECEDES--> g19
    g19 --PRECEDES--> g20
    g20 --PRECEDES--> g21
    g21 --PRECEDES--> g22
    g21 --PRECEDES--> g23
    g22 --PRECEDES--> g24
    g23 --PRECEDES--> g24
    g24 --PRECEDES--> g25
    g25 --PRECEDES--> g26
    g26 --PRECEDES--> g27
    g26 --PRECEDES--> g28
    g27 --PRECEDES--> g29
    g28 --PRECEDES--> g29
    g29 --PRECEDES--> g30
    g30 --PRECEDES--> g31
    g31 --PRECEDES--> g32
    g31 --PRECEDES--> g33
    g31 --PRECEDES--> g34
    g32 --PRECEDES--> g35
    g33 --PRECEDES--> g35
    g34 --PRECEDES--> g35
    g35 --PRECEDES--> g36
    g35 --PRECEDES--> g37
    g36 --PRECEDES--> g38
    g37 --PRECEDES--> g38
    g38 --PRECEDES--> g39
    g38 --PRECEDES--> g40
    g38 --PRECEDES--> g41
    g39 --PRECEDES--> g42
    g39 --PRECEDES--> g43
    g39 --PRECEDES--> g44
    g39 --PRECEDES--> g45
    g40 --PRECEDES--> g42
    g40 --PRECEDES--> g43
    g40 --PRECEDES--> g44
    g40 --PRECEDES--> g45
    g41 --PRECEDES--> g42
    g41 --PRECEDES--> g43
    g41 --PRECEDES--> g44
    g41 --PRECEDES--> g45
    g42 --PRECEDES--> g46
    g43 --PRECEDES--> g46
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
    g55 --PRECEDES--> g56
    g56 --PRECEDES--> g57
    g57 --PRECEDES--> g58
    g57 --PRECEDES--> g59
    g58 --PRECEDES--> g60
    g59 --PRECEDES--> g60
    g05 --SAME_TRACK--> g16
    g07 --SAME_TRACK--> g23
    g07 --SAME_TRACK--> g26
    g13 --SAME_TRACK--> g33
    g13 --SAME_TRACK--> g34
    g29 --SAME_TRACK--> g35
    g29 --SAME_TRACK--> g38
    g07 --SAME_TRACK--> g40
    g07 --SAME_TRACK--> g45
    g07 --SAME_TRACK--> g46
    g05 --SAME_TRACK--> g50
    g32 --SAME_TRACK--> g53
    g36 --SAME_TRACK--> g54
    g05 --SAME_TRACK--> g55
    g52 --SAME_TRACK--> g57
    g32 --SAME_TRACK--> g59
    g06 --SAME_TRACK--> g17
    g12 --SAME_TRACK--> g19
    g09 --SAME_TRACK--> g20
    g18 --SAME_TRACK--> g21
    g10 --SAME_TRACK--> g27
    g25 --SAME_TRACK--> g28
    g10 --SAME_TRACK--> g30
    g31 --SAME_TRACK--> g37
    g10 --SAME_TRACK--> g41
    g10 --SAME_TRACK--> g42
    g22 --SAME_TRACK--> g49
    g24 --SAME_TRACK--> g51
    g11 --SAME_TRACK--> g56
    g58 --SAME_TRACK--> g60
```

## Global trace

Events in one row are simultaneous at 0.05 s resolution: their order is unresolved.

| t_global | Events |
|---------:|--------|
| -7.75 | MOVING_START(A); MOVING_START(B); THROTTLE_START(A); THROTTLE_START(B); TRACK_APPEARED_FRONT(A,U1); TRACK_APPEARED_FRONT(B,U3); TRACK_APPEARED_LEFT(A,B); TRACK_APPEARED_LEFT(A,U2); TRACK_APPEARED_LEFT(B,U4); TRACK_APPEARED_RIGHT(B,A); TRACK_APPEARED_RIGHT(B,U1) |
| -7.70 | TRACK_APPEARED_FRONT(B,U6); TRACK_APPEARED_LEFT(A,U3); TRACK_APPEARED_LEFT(B,U2); TRACK_APPEARED_RIGHT(B,U5) |
| -7.25 | CRITICAL_TTC_START(A,U1); CRITICAL_TTC_START(B,U3) |
| -6.95 | TRACK_APPEARED_RIGHT(B,U7) |
| -5.55 | TRACK_LOST(B,U6) |
| -4.10 | TRACK_LOST(B,U4) |
| -3.95 | TRACK_LOST(B,U7) |
| -1.40 | TRACK_APPEARED_RIGHT(B,U7); CRITICAL_TTC_START(A,B) |
| -1.35 | TRACK_APPEARED_LEFT(B,U4) |
| -1.15 | TRACK_APPEARED_FRONT(B,U8) |
| -0.80 | CLOSING_START(A,B) |
| -0.75 | CRITICAL_TTC_START(B,A); TRACK_LOST(B,U8) |
| -0.70 | TRACK_APPEARED_FRONT(A,U9) |
| -0.60 | CLOSING_START(B,A) |
| -0.40 | TRACK_APPEARED_FRONT(B,U10) |
| -0.35 | TRACK_APPEARED_RIGHT(A,U7); EGO_PATH_ENTRY(A,U3); CRITICAL_TTC_START(A,U3) |
| -0.25 | EGO_PATH_ENTRY(A,U9) |
| -0.10 | TRACK_APPEARED_RIGHT(A,U5); TRACK_LOST(B,U10) |
| -0.05 | TRACK_LOST(A,U9) |
| +0.00 | COLLISION(A,B); CRITICAL_TTC_END(A,B); CRITICAL_TTC_END(B,A) |
| +0.05 | CLOSING_END(B,A); THROTTLE_END(A); THROTTLE_END(B); EGO_PATH_ENTRY(A,B) |
| +0.10 | CLOSING_END(A,B) |
| +0.30 | TRACK_APPEARED_FRONT(B,U11) |
| +0.70 | TRACK_APPEARED_LEFT(A,U4) |
| +1.10 | TRACK_LOST(B,U7) |
| +1.25 | CRITICAL_TTC_END(A,U1) |
| +1.60 | TRACK_LOST(B,U4) |
| +1.75 | TRACK_APPEARED_LEFT(A,U11) |
| +2.10 | EGO_PATH_EXIT(A,U7) |
| +2.40 | CRITICAL_TTC_START(A,U5) |
| +2.70 | CRITICAL_TTC_START(A,U1) |
| +3.30 | CLOSING_START(B,U1) |
| +3.40 | TRACK_LOST(A,U11) |
| +3.60 | TRACK_APPEARED_LEFT(B,U12); EGO_PATH_ENTRY(A,U7) |
| +3.90 | TRACK_LOST(B,U12) |

## Temporal safety relations

Per track: does the cut-in start before the critical TTC, or was the critical TTC already active? Is the path entry before or after it? Temporal properties only, not causes.

- A's track_001 (unidentified U1): CRITICAL_TTC_START 0.50, COLLISION 7.75 (+7.25 s) [local times; t_global: critical_ttc_start -7.25, collision +0.00]
- A's track_003 (B): CRITICAL_TTC_START 6.35, COLLISION with B 7.75 (+1.40 s); EGO_PATH_ENTRY 7.80 after critical TTC (+1.45 s) [local times; t_global: critical_ttc_start -1.40, ego_path_entry +0.05, collision +0.00]
- A's track_004 (unidentified U3): CRITICAL_TTC_START 7.40, COLLISION 7.75 (+0.35 s); EGO_PATH_ENTRY 7.40 together with critical TTC (+0.00 s) [local times; t_global: critical_ttc_start -0.35, ego_path_entry -0.35, collision +0.00]
- A's track_005 (unidentified U9): EGO_PATH_ENTRY 7.50, no critical TTC [local times; t_global: ego_path_entry -0.25, collision +0.00]
- A's track_006 (unidentified U7): EGO_PATH_ENTRY 11.35, no critical TTC [local times; t_global: ego_path_entry +3.60]
- A's track_007 (unidentified U5): CRITICAL_TTC_START 10.15 [local times; t_global: critical_ttc_start +2.40]
- B's track_001 (unidentified U3): CRITICAL_TTC_START 0.50, COLLISION 7.75 (+7.25 s) [local times; t_global: critical_ttc_start -7.25, collision +0.00]
- B's track_002 (A): CRITICAL_TTC_START 7.00, COLLISION with A 7.75 (+0.75 s) [local times; t_global: critical_ttc_start -0.75, collision +0.00]

## Perceived state before each event, per observing recorder

Each recorder's own belief just before its events, in its own local names (track_001, ...): fusion does not rewrite it. True states are named, unknown ones end with `?`.

| t_global | Recorder | Events (local node) | Perceived state just before |
|---------:|----------|---------------------|-----------------------------|
| -7.75 | A | g01 MOVING_START(A) (A:e01)<br>g03 THROTTLE_START(A) (A:e02)<br>g05 TRACK_APPEARED_FRONT(A,U1) (A:e03)<br>g07 TRACK_APPEARED_LEFT(A,B) (A:e05)<br>g08 TRACK_APPEARED_LEFT(A,U2) (A:e04) | ego: not yet observed |
| -7.75 | B | g02 MOVING_START(B) (B:e01)<br>g04 THROTTLE_START(B) (B:e02)<br>g06 TRACK_APPEARED_FRONT(B,U3) (B:e03)<br>g09 TRACK_APPEARED_LEFT(B,U4) (B:e04)<br>g10 TRACK_APPEARED_RIGHT(B,A) (B:e05)<br>g11 TRACK_APPEARED_RIGHT(B,U1) (B:e06) | ego: not yet observed |
| -7.75 | B | g09 TRACK_APPEARED_LEFT(B,U4) (B:e04)<br>g20 TRACK_LOST(B,U4) (B:e13) | ego: not yet observed |
| -7.70 | B | g12 TRACK_APPEARED_FRONT(B,U6) (B:e07)<br>g14 TRACK_APPEARED_LEFT(B,U2) (B:e08)<br>g15 TRACK_APPEARED_RIGHT(B,U5) (B:e09) | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH, CRITICAL_TTC?<br>track_002: CRITICAL_TTC?<br>track_003: CRITICAL_TTC?<br>track_004: CRITICAL_TTC? |
| -7.70 | B | g12 TRACK_APPEARED_FRONT(B,U6) (B:e07)<br>g19 TRACK_LOST(B,U6) (B:e12) | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH, CRITICAL_TTC?<br>track_002: CRITICAL_TTC?<br>track_003: CRITICAL_TTC?<br>track_004: CRITICAL_TTC? |
| -7.70 | A | g13 TRACK_APPEARED_LEFT(A,U3) (A:e06) | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH, CRITICAL_TTC?<br>track_002: CRITICAL_TTC?<br>track_003: CRITICAL_TTC? |
| -7.25 | A | g16 CRITICAL_TTC_START(A,U1) (A:e07) | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH, CRITICAL_TTC?<br>track_002: CRITICAL_TTC?<br>track_003: CRITICAL_TTC?<br>track_004: CRITICAL_TTC? |
| -7.25 | A | g16 CRITICAL_TTC_START(A,U1) (A:e07)<br>g50 CRITICAL_TTC_END(A,U1) (A:e23) | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH, CRITICAL_TTC?<br>track_002: CRITICAL_TTC?<br>track_003: CRITICAL_TTC?<br>track_004: CRITICAL_TTC? |
| -7.25 | B | g17 CRITICAL_TTC_START(B,U3) (B:e10) | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH, CRITICAL_TTC?<br>track_002: CRITICAL_TTC?<br>track_003: CRITICAL_TTC?<br>track_004: CRITICAL_TTC?<br>track_005: CRITICAL_TTC?<br>track_006: CRITICAL_TTC?<br>track_007: CRITICAL_TTC? |
| -6.95 | B | g18 TRACK_APPEARED_RIGHT(B,U7) (B:e11) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_006: no active state<br>track_007: no active state |
| -6.95 | B | g18 TRACK_APPEARED_RIGHT(B,U7) (B:e11)<br>g21 TRACK_LOST(B,U7) (B:e14) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_006: no active state<br>track_007: no active state |
| -1.40 | B | g22 TRACK_APPEARED_RIGHT(B,U7) (B:e15) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: no active state<br>track_005: no active state<br>track_006: no active state<br>track lost, states UNKNOWN: track_004, track_007, track_008 |
| -1.40 | B | g22 TRACK_APPEARED_RIGHT(B,U7) (B:e15)<br>g49 TRACK_LOST(B,U7) (B:e28) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: no active state<br>track_005: no active state<br>track_006: no active state<br>track lost, states UNKNOWN: track_004, track_007, track_008 |
| -1.40 | A | g23 CRITICAL_TTC_START(A,B) (A:e08) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: no active state<br>track_004: no active state |
| -1.40 | A | g23 CRITICAL_TTC_START(A,B) (A:e08)<br>g39 COLLISION(A,B) (A:e17)<br>g40 CRITICAL_TTC_END(A,B) (A:e18) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: no active state<br>track_004: no active state |
| -1.35 | B | g24 TRACK_APPEARED_LEFT(B,U4) (B:e16) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: no active state<br>track_005: no active state<br>track_006: no active state<br>track_009: CRITICAL_TTC?<br>track lost, states UNKNOWN: track_004, track_007, track_008 |
| -1.35 | B | g24 TRACK_APPEARED_LEFT(B,U4) (B:e16)<br>g51 TRACK_LOST(B,U4) (B:e29) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: no active state<br>track_005: no active state<br>track_006: no active state<br>track_009: CRITICAL_TTC?<br>track lost, states UNKNOWN: track_004, track_007, track_008 |
| -1.15 | B | g25 TRACK_APPEARED_FRONT(B,U8) (B:e17) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: no active state<br>track_005: no active state<br>track_006: no active state<br>track_009: CRITICAL_TTC?<br>track_010: CRITICAL_TTC?<br>track lost, states UNKNOWN: track_004, track_007, track_008 |
| -1.15 | B | g25 TRACK_APPEARED_FRONT(B,U8) (B:e17)<br>g27 CRITICAL_TTC_START(B,A) (B:e18)<br>g28 TRACK_LOST(B,U8) (B:e19) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: no active state<br>track_005: no active state<br>track_006: no active state<br>track_009: CRITICAL_TTC?<br>track_010: CRITICAL_TTC?<br>track lost, states UNKNOWN: track_004, track_007, track_008 |
| -0.80 | A | g26 CLOSING_START(A,B) (A:e09) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: CRITICAL_TTC<br>track_004: no active state |
| -0.80 | A | g26 CLOSING_START(A,B) (A:e09)<br>g46 CLOSING_END(A,B) (A:e21) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: CRITICAL_TTC<br>track_004: no active state |
| -0.75 | B | g27 CRITICAL_TTC_START(B,A) (B:e18)<br>g39 COLLISION(A,B) (B:e23)<br>g41 CRITICAL_TTC_END(B,A) (B:e24) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: no active state<br>track_005: no active state<br>track_006: no active state<br>track_009: no active state<br>track_010: no active state<br>track_011: CRITICAL_TTC?, CUT_IN_FROM_LEFT?, CUT_IN_FROM_RIGHT?<br>track lost, states UNKNOWN: track_004, track_007, track_008 |
| -0.70 | A | g29 TRACK_APPEARED_FRONT(A,U9) (A:e10) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: CLOSING, CRITICAL_TTC<br>track_004: no active state |
| -0.70 | A | g29 TRACK_APPEARED_FRONT(A,U9) (A:e10)<br>g38 TRACK_LOST(A,U9) (A:e16) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: CLOSING, CRITICAL_TTC<br>track_004: no active state |
| -0.60 | B | g30 CLOSING_START(B,A) (B:e20) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: CRITICAL_TTC<br>track_003: no active state<br>track_005: no active state<br>track_006: no active state<br>track_009: no active state<br>track_010: no active state<br>track lost, states UNKNOWN: track_004, track_007, track_008, track_011 |
| -0.60 | B | g30 CLOSING_START(B,A) (B:e20)<br>g42 CLOSING_END(B,A) (B:e25)<br>g44 THROTTLE_END(B) (B:e26) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: CRITICAL_TTC<br>track_003: no active state<br>track_005: no active state<br>track_006: no active state<br>track_009: no active state<br>track_010: no active state<br>track lost, states UNKNOWN: track_004, track_007, track_008, track_011 |
| -0.40 | B | g31 TRACK_APPEARED_FRONT(B,U10) (B:e21) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: CLOSING, CRITICAL_TTC<br>track_003: no active state<br>track_005: no active state<br>track_006: no active state<br>track_009: no active state<br>track_010: no active state<br>track lost, states UNKNOWN: track_004, track_007, track_008, track_011 |
| -0.40 | B | g31 TRACK_APPEARED_FRONT(B,U10) (B:e21)<br>g37 TRACK_LOST(B,U10) (B:e22) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: CLOSING, CRITICAL_TTC<br>track_003: no active state<br>track_005: no active state<br>track_006: no active state<br>track_009: no active state<br>track_010: no active state<br>track lost, states UNKNOWN: track_004, track_007, track_008, track_011 |
| -0.35 | A | g32 TRACK_APPEARED_RIGHT(A,U7) (A:e11)<br>g33 EGO_PATH_ENTRY(A,U3) (A:e12)<br>g34 CRITICAL_TTC_START(A,U3) (A:e13) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: CLOSING, CRITICAL_TTC<br>track_004: no active state<br>track_005: CRITICAL_TTC? |
| -0.25 | A | g35 EGO_PATH_ENTRY(A,U9) (A:e14) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: CLOSING, CRITICAL_TTC<br>track_004: CRITICAL_TTC, IN_EGO_PATH<br>track_005: CRITICAL_TTC?<br>track_006: IN_EGO_PATH, CRITICAL_TTC? |
| -0.10 | A | g36 TRACK_APPEARED_RIGHT(A,U5) (A:e15) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: CLOSING, CRITICAL_TTC<br>track_004: CRITICAL_TTC, IN_EGO_PATH<br>track_005: IN_EGO_PATH<br>track_006: IN_EGO_PATH, CRITICAL_TTC? |
| +0.05 | A | g43 THROTTLE_END(A) (A:e19)<br>g45 EGO_PATH_ENTRY(A,B) (A:e20) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: CLOSING<br>track_004: CRITICAL_TTC, IN_EGO_PATH<br>track_006: IN_EGO_PATH, CRITICAL_TTC?<br>track_007: IN_EGO_PATH, CRITICAL_TTC?<br>track lost, states UNKNOWN: track_005 |
| +0.30 | B | g47 TRACK_APPEARED_FRONT(B,U11) (B:e27) | ego: MOVING<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: no active state<br>track_005: no active state<br>track_006: no active state<br>track_009: no active state<br>track_010: no active state<br>track lost, states UNKNOWN: track_004, track_007, track_008, track_011, track_012 |
| +0.70 | A | g48 TRACK_APPEARED_LEFT(A,U4) (A:e22) | ego: MOVING<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: IN_EGO_PATH<br>track_004: CRITICAL_TTC, IN_EGO_PATH<br>track_006: IN_EGO_PATH<br>track_007: IN_EGO_PATH<br>track lost, states UNKNOWN: track_005 |
| +1.75 | A | g52 TRACK_APPEARED_LEFT(A,U11) (A:e24) | ego: MOVING<br>track_001: IN_EGO_PATH<br>track_002: no active state<br>track_003: IN_EGO_PATH<br>track_004: CRITICAL_TTC, IN_EGO_PATH<br>track_006: IN_EGO_PATH<br>track_007: IN_EGO_PATH<br>track_008: no active state<br>track lost, states UNKNOWN: track_005 |
| +1.75 | A | g52 TRACK_APPEARED_LEFT(A,U11) (A:e24)<br>g57 TRACK_LOST(A,U11) (A:e28) | ego: MOVING<br>track_001: IN_EGO_PATH<br>track_002: no active state<br>track_003: IN_EGO_PATH<br>track_004: CRITICAL_TTC, IN_EGO_PATH<br>track_006: IN_EGO_PATH<br>track_007: IN_EGO_PATH<br>track_008: no active state<br>track lost, states UNKNOWN: track_005 |
| +2.10 | A | g53 EGO_PATH_EXIT(A,U7) (A:e25) | ego: MOVING<br>track_001: IN_EGO_PATH<br>track_002: no active state<br>track_003: IN_EGO_PATH<br>track_004: CRITICAL_TTC, IN_EGO_PATH<br>track_006: IN_EGO_PATH<br>track_007: IN_EGO_PATH<br>track_008: no active state<br>track_009: IN_EGO_PATH, CRITICAL_TTC?<br>track lost, states UNKNOWN: track_005 |
| +2.40 | A | g54 CRITICAL_TTC_START(A,U5) (A:e26) | ego: MOVING<br>track_001: IN_EGO_PATH<br>track_002: no active state<br>track_003: IN_EGO_PATH<br>track_004: CRITICAL_TTC, IN_EGO_PATH<br>track_006: no active state<br>track_007: IN_EGO_PATH<br>track_008: no active state<br>track_009: IN_EGO_PATH<br>track lost, states UNKNOWN: track_005 |
| +2.70 | A | g55 CRITICAL_TTC_START(A,U1) (A:e27) | ego: MOVING<br>track_001: IN_EGO_PATH<br>track_002: no active state<br>track_003: IN_EGO_PATH<br>track_004: CRITICAL_TTC, IN_EGO_PATH<br>track_006: no active state<br>track_007: CRITICAL_TTC, IN_EGO_PATH<br>track_008: no active state<br>track_009: IN_EGO_PATH<br>track lost, states UNKNOWN: track_005 |
| +3.30 | B | g56 CLOSING_START(B,U1) (B:e30) | ego: MOVING<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: no active state<br>track_005: no active state<br>track_006: no active state<br>track_013: IN_EGO_PATH<br>track lost, states UNKNOWN: track_004, track_007, track_008, track_009, track_010, track_011, track_012 |
| +3.60 | B | g58 TRACK_APPEARED_LEFT(B,U12) (B:e31) | ego: MOVING<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: CLOSING<br>track_005: no active state<br>track_006: no active state<br>track_013: IN_EGO_PATH<br>track lost, states UNKNOWN: track_004, track_007, track_008, track_009, track_010, track_011, track_012 |
| +3.60 | B | g58 TRACK_APPEARED_LEFT(B,U12) (B:e31)<br>g60 TRACK_LOST(B,U12) (B:e32) | ego: MOVING<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: CLOSING<br>track_005: no active state<br>track_006: no active state<br>track_013: IN_EGO_PATH<br>track lost, states UNKNOWN: track_004, track_007, track_008, track_009, track_010, track_011, track_012 |
| +3.60 | A | g59 EGO_PATH_ENTRY(A,U7) (A:e29) | ego: MOVING<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: IN_EGO_PATH<br>track_004: CRITICAL_TTC, IN_EGO_PATH<br>track_006: no active state<br>track_007: CRITICAL_TTC, IN_EGO_PATH<br>track_008: no active state<br>track lost, states UNKNOWN: track_005, track_009 |

## Plain-language reading

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
