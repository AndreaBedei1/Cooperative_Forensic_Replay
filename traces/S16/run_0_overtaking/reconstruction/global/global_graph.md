# Global graph - S16/run_0_overtaking

Global time `t_global` is 0 at the reference collision. The local graphs were not modified: every node lists the local node(s) and local time(s) it comes from.

Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.

## Entities

| Entity | Kind | Details |
|--------|------|---------|
| A | recorder | clock ALIGNED; observed by others as: B:track_001 |
| B | recorder | clock ALIGNED; observed by others as: A:track_006 |
| U1 | anonymous_road_user | anonymous; observed by A, B as A:track_001, B:track_005 |
| U2 | anonymous_road_user | anonymous; observed by A as A:track_002 |
| U3 | anonymous_road_user | anonymous; observed by A, B as A:track_003, B:track_002 |
| U4 | anonymous_road_user | anonymous; observed by A, B as A:track_004, A:track_007, B:track_006 |
| U5 | anonymous_road_user | anonymous; observed by A as A:track_005 |
| U8 | anonymous_road_user | anonymous; observed by A, B as A:track_008, B:track_007 |
| U10 | anonymous_road_user | anonymous; observed by A as A:track_009 |
| U12 | anonymous_road_user | anonymous; observed by A, B as A:track_010, B:track_010 |
| U11 | anonymous_road_user | anonymous; observed by A, B as A:track_011, B:track_009 |
| U6 | anonymous_road_user | anonymous; observed by B as B:track_003 |
| U7 | anonymous_road_user | anonymous; observed by B as B:track_004 |
| U9 | anonymous_road_user | anonymous; observed by B as B:track_008 |

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

## Nodes

| Id | Global time | Type | Actor | Subject / participants | Observed by (local node @ local time) | Details |
|----|------------:|------|-------|------------------------|----------------------------------------|---------|
| g01 | -6.75 | MOVING_START | A | - | A:e01 @ 0.00 | active_at_first_observation=True |
| g02 | -6.75 | MOVING_START | B | - | B:e01 @ 0.00 | active_at_first_observation=True |
| g03 | -6.75 | THROTTLE_START | A | - | A:e02 @ 0.00 | active_at_first_observation=True |
| g04 | -6.75 | THROTTLE_START | B | - | B:e02 @ 0.00 | active_at_first_observation=True |
| g05 | -6.75 | TRACK_APPEARED_FRONT | A | U3 | A:e03 @ 0.00 | initial_in_ego_path=True; source_track=track_003; aggregation=entity_state_union; source_tracks=['A:track_003'] |
| g06 | -6.75 | TRACK_APPEARED_LEFT | A | U1 | A:e04 @ 0.00, A:e41 @ 11.20 | initial_in_ego_path=False; source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g07 | -6.75 | TRACK_APPEARED_LEFT | A | U2 | A:e05 @ 0.00, A:e13 @ 3.60 | initial_in_ego_path=False; source_track=track_002; aggregation=entity_state_union; source_tracks=['A:track_002'] |
| g08 | -6.75 | TRACK_APPEARED_RIGHT | A | U4 | A:e06 @ 0.00, A:e14 @ 3.60 | initial_in_ego_path=False; source_track=track_004; aggregation=entity_state_union; source_tracks=['A:track_004'] |
| g09 | -6.75 | TRACK_APPEARED_RIGHT | A | U5 | A:e07 @ 0.00, A:e12 @ 0.50 | initial_in_ego_path=False; source_track=track_005; aggregation=entity_state_union; source_tracks=['A:track_005'] |
| g10 | -6.75 | TRACK_APPEARED_RIGHT | B | A | B:e03 @ 0.00 | initial_in_ego_path=False; source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g11 | -6.75 | TRACK_APPEARED_RIGHT | B | U3 | B:e04 @ 0.00 | initial_in_ego_path=False; source_track=track_002; aggregation=entity_state_union; source_tracks=['B:track_002'] |
| g12 | -6.75 | TRACK_APPEARED_RIGHT | B | U6 | B:e05 @ 0.00, B:e14 @ 5.20 | initial_in_ego_path=False; source_track=track_003; aggregation=entity_state_union; source_tracks=['B:track_003'] |
| g13 | -6.75 | CLOSING_START | A | U4 | A:e08 @ 0.00 | active_at_first_observation=True; source_track=track_004; aggregation=entity_state_union; source_tracks=['A:track_004'] |
| g14 | -6.75 | CLOSING_START | B | A | B:e06 @ 0.00, B:e13 @ 4.10 | active_at_first_observation=True; source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g15 | -6.75 | CLOSING_START | B | U3 | B:e07 @ 0.00, B:e29 @ 7.10 | active_at_first_observation=True; source_track=track_002; aggregation=entity_state_union; source_tracks=['B:track_002'] |
| g16 | -6.55 | TRACK_APPEARED_FRONT | B | U7 | B:e08 @ 0.20, B:e12 @ 3.10 | initial_in_ego_path=False; source_track=track_004; aggregation=entity_state_union; source_tracks=['B:track_004'] |
| g17 | -6.55 | CLOSING_START | B | U7 | B:e09 @ 0.20 | active_at_first_observation=True; source_track=track_004; aggregation=entity_state_union; source_tracks=['B:track_004'] |
| g18 | -6.40 | TRACK_APPEARED_FRONT | B | U1 | B:e10 @ 0.35, B:e39 @ 11.10 | initial_in_ego_path=True; source_track=track_005; aggregation=entity_state_union; source_tracks=['B:track_005'] |
| g19 | -6.35 | TRACK_APPEARED_LEFT | A | B | A:e09 @ 0.40 | initial_in_ego_path=False; source_track=track_006; aggregation=entity_state_union; source_tracks=['A:track_006'] |
| g20 | -6.35 | CLOSING_START | A | B | A:e10 @ 0.40, A:e15 @ 4.05 | active_at_first_observation=True; source_track=track_006; aggregation=entity_state_union; source_tracks=['A:track_006'] |
| g21 | -6.25 | CRITICAL_TTC_START | A | U3 | A:e11 @ 0.50, A:e31 @ 7.45 | source_track=track_003; aggregation=entity_state_union; source_tracks=['A:track_003'] |
| g22 | -6.25 | TRACK_LOST | A | U5 | A:e12 @ 0.50 | source_track=track_005; aggregation=entity_state_union; source_tracks=['A:track_005'] |
| g23 | -5.90 | CRITICAL_TTC_START | B | U1 | B:e11 @ 0.85, B:e32 @ 7.55 | source_track=track_005; aggregation=entity_state_union; source_tracks=['B:track_005'] |
| g24 | -3.65 | TRACK_LOST | B | U7 | B:e12 @ 3.10 | source_track=track_004; aggregation=entity_state_union; source_tracks=['B:track_004'] |
| g25 | -3.15 | TRACK_LOST | A | U2 | A:e13 @ 3.60 | source_track=track_002; aggregation=entity_state_union; source_tracks=['A:track_002'] |
| g26 | -3.15 | TRACK_LOST | A | U4 | A:e14 @ 3.60 | source_track=track_004; aggregation=entity_state_union; source_tracks=['A:track_004'] |
| g27 | -2.70 | CLOSING_END | A | B | A:e15 @ 4.05 | source_track=track_006; aggregation=entity_state_union; source_tracks=['A:track_006'] |
| g28 | -2.65 | CLOSING_END | B | A | B:e13 @ 4.10 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g29 | -1.60 | CRITICAL_TTC_START | A | B | A:e16 @ 5.15, A:e26 @ 6.75 | source_track=track_006; aggregation=entity_state_union; source_tracks=['A:track_006'] |
| g30 | -1.55 | TRACK_LOST | B | U6 | B:e14 @ 5.20 | source_track=track_003; aggregation=entity_state_union; source_tracks=['B:track_003'] |
| g31 | -1.45 | TRACK_APPEARED_RIGHT | A | U4 | A:e17 @ 5.30 | initial_in_ego_path=False; source_track=track_007; aggregation=entity_state_union; source_tracks=['A:track_007'] |
| g32 | -1.45 | CLOSING_START | A | U4 | A:e18 @ 5.30, A:e30 @ 7.20 | active_at_first_observation=True; source_track=track_007; aggregation=entity_state_union; source_tracks=['A:track_007'] |
| g33 | -1.10 | TRACK_APPEARED_RIGHT | B | U4 | B:e15 @ 5.65 | initial_in_ego_path=False; source_track=track_006; aggregation=entity_state_union; source_tracks=['B:track_006'] |
| g34 | -1.10 | CLOSING_START | B | U4 | B:e16 @ 5.65, B:e30 @ 7.35 | active_at_first_observation=True; source_track=track_006; aggregation=entity_state_union; source_tracks=['B:track_006'] |
| g35 | -1.10 | CRITICAL_TTC_START | B | A | B:e17 @ 5.65, B:e24 @ 6.75 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g36 | -0.85 | TRACK_APPEARED_FRONT | A | U8 | A:e19 @ 5.90, A:e42 @ 11.85 | initial_in_ego_path=False; source_track=track_008; aggregation=entity_state_union; source_tracks=['A:track_008'] |
| g37 | -0.85 | TRACK_APPEARED_RIGHT | B | U8 | B:e18 @ 5.90, B:e40 @ 11.55 | initial_in_ego_path=False; source_track=track_007; aggregation=entity_state_union; source_tracks=['B:track_007'] |
| g38 | -0.85 | CLOSING_START | A | B | A:e20 @ 5.90, A:e27 @ 6.80 | source_track=track_006; aggregation=entity_state_union; source_tracks=['A:track_006'] |
| g39 | -0.85 | CLOSING_START | B | U8 | B:e19 @ 5.90, B:e28 @ 7.05 | active_at_first_observation=True; source_track=track_007; aggregation=entity_state_union; source_tracks=['B:track_007'] |
| g40 | -0.65 | CLOSING_START | B | A | B:e20 @ 6.10, B:e27 @ 6.85 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g41 | -0.55 | TRACK_APPEARED_RIGHT | B | U9 | B:e21 @ 6.20, B:e33 @ 7.55 | initial_in_ego_path=False; source_track=track_008; aggregation=entity_state_union; source_tracks=['B:track_008'] |
| g42 | -0.55 | CLOSING_START | B | U9 | B:e22 @ 6.20, B:e31 @ 7.35 | active_at_first_observation=True; source_track=track_008; aggregation=entity_state_union; source_tracks=['B:track_008'] |
| g43 | -0.45 | EGO_PATH_ENTRY | A | U1 | A:e21 @ 6.30 | occupancy_evidence=box; occupancy_margin_m=0.47; occupancy_sigma_m=0.27; cause=MUTUAL_LATERAL; geometry=estimated_body; source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g44 | -0.45 | CRITICAL_TTC_START | A | U1 | A:e22 @ 6.30 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g45 | -0.30 | EGO_PATH_ENTRY | A | B | A:e23 @ 6.45 | occupancy_evidence=returns; occupancy_margin_m=0.42; occupancy_sigma_m=0.25; cause=RECORDER_LATERAL; geometry=estimated_body; source_track=track_006; aggregation=entity_state_union; source_tracks=['A:track_006'] |
| g46 | -0.25 | EGO_PATH_ENTRY | A | U8 | A:e24 @ 6.50 | occupancy_evidence=box; occupancy_margin_m=0.60; occupancy_sigma_m=0.28; cause=RECORDER_LATERAL; geometry=estimated_body; source_track=track_008; aggregation=entity_state_union; source_tracks=['A:track_008'] |
| g47 | 0.00 | COLLISION | - | A, B | A:e25 @ 6.75, B:e23 @ 6.75 | matched_event=collision_001; reference_event=True; peak_impulse=A 191.84, B 191.84 |
| g48 | 0.00 | CRITICAL_TTC_END | A | B | A:e26 @ 6.75 | source_track=track_006; aggregation=entity_state_union; source_tracks=['A:track_006'] |
| g49 | 0.00 | CRITICAL_TTC_END | B | A | B:e24 @ 6.75 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g50 | 0.05 | CLOSING_END | A | B | A:e27 @ 6.80 | source_track=track_006; aggregation=entity_state_union; source_tracks=['A:track_006'] |
| g51 | 0.05 | THROTTLE_END | A | - | A:e28 @ 6.80 |  |
| g52 | 0.05 | THROTTLE_END | B | - | B:e25 @ 6.80 |  |
| g53 | 0.05 | BRAKE_START | A | - | A:e29 @ 6.80 |  |
| g54 | 0.05 | BRAKE_START | B | - | B:e26 @ 6.80 |  |
| g55 | 0.10 | CLOSING_END | B | A | B:e27 @ 6.85 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g56 | 0.30 | CLOSING_END | B | U8 | B:e28 @ 7.05 | source_track=track_007; aggregation=entity_state_union; source_tracks=['B:track_007'] |
| g57 | 0.35 | CLOSING_END | B | U3 | B:e29 @ 7.10 | source_track=track_002; aggregation=entity_state_union; source_tracks=['B:track_002'] |
| g58 | 0.45 | CLOSING_END | A | U4 | A:e30 @ 7.20 | source_track=track_007; aggregation=entity_state_union; source_tracks=['A:track_007'] |
| g59 | 0.60 | CLOSING_END | B | U4 | B:e30 @ 7.35 | source_track=track_006; aggregation=entity_state_union; source_tracks=['B:track_006'] |
| g60 | 0.60 | CLOSING_END | B | U9 | B:e31 @ 7.35 | source_track=track_008; aggregation=entity_state_union; source_tracks=['B:track_008'] |
| g61 | 0.70 | CRITICAL_TTC_END | A | U3 | A:e31 @ 7.45 | source_track=track_003; aggregation=entity_state_union; source_tracks=['A:track_003'] |
| g62 | 0.80 | CRITICAL_TTC_END | B | U1 | B:e32 @ 7.55 | source_track=track_005; aggregation=entity_state_union; source_tracks=['B:track_005'] |
| g63 | 0.80 | TRACK_LOST | B | U9 | B:e33 @ 7.55 | source_track=track_008; aggregation=entity_state_union; source_tracks=['B:track_008'] |
| g64 | 1.15 | MOVING_END | B | - | B:e34 @ 7.90 |  |
| g65 | 1.15 | STOP_START | B | - | B:e35 @ 7.90 |  |
| g66 | 1.15 | TRACK_APPEARED_FRONT | A | U10 | A:e32 @ 7.90 | initial_in_ego_path=False; source_track=track_009; aggregation=entity_state_union; source_tracks=['A:track_009'] |
| g67 | 1.20 | MOVING_END | A | - | A:e33 @ 7.95 |  |
| g68 | 1.20 | STOP_START | A | - | A:e34 @ 7.95 |  |
| g69 | 1.50 | TRACK_APPEARED_LEFT | B | U11 | B:e36 @ 8.25, B:e37 @ 9.70 | initial_in_ego_path=True; source_track=track_009; aggregation=entity_state_union; source_tracks=['B:track_009'] |
| g70 | 1.55 | TRACK_APPEARED_RIGHT | A | U12 | A:e35 @ 8.30 | initial_in_ego_path=False; source_track=track_010; aggregation=entity_state_union; source_tracks=['A:track_010'] |
| g71 | 1.55 | CLOSING_START | A | U12 | A:e36 @ 8.30, A:e40 @ 10.35 | active_at_first_observation=True; source_track=track_010; aggregation=entity_state_union; source_tracks=['A:track_010'] |
| g72 | 1.80 | TRACK_APPEARED_LEFT | A | U11 | A:e37 @ 8.55, A:e39 @ 9.95 | initial_in_ego_path=False; source_track=track_011; aggregation=entity_state_union; source_tracks=['A:track_011'] |
| g73 | 2.45 | EGO_PATH_ENTRY | A | U11 | A:e38 @ 9.20 | occupancy_evidence=box; occupancy_margin_m=0.57; occupancy_sigma_m=0.33; cause=TARGET_LATERAL; geometry=estimated_body; source_track=track_011; aggregation=entity_state_union; source_tracks=['A:track_011'] |
| g74 | 2.95 | TRACK_LOST | B | U11 | B:e37 @ 9.70 | source_track=track_009; aggregation=entity_state_union; source_tracks=['B:track_009'] |
| g75 | 3.20 | TRACK_LOST | A | U11 | A:e39 @ 9.95 | source_track=track_011; aggregation=entity_state_union; source_tracks=['A:track_011'] |
| g76 | 3.45 | TRACK_APPEARED_RIGHT | B | U12 | B:e38 @ 10.20 | initial_in_ego_path=False; source_track=track_010; aggregation=entity_state_union; source_tracks=['B:track_010'] |
| g77 | 3.60 | CLOSING_END | A | U12 | A:e40 @ 10.35 | source_track=track_010; aggregation=entity_state_union; source_tracks=['A:track_010'] |
| g78 | 4.35 | TRACK_LOST | B | U1 | B:e39 @ 11.10 | source_track=track_005; aggregation=entity_state_union; source_tracks=['B:track_005'] |
| g79 | 4.45 | TRACK_LOST | A | U1 | A:e41 @ 11.20 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g80 | 4.80 | TRACK_LOST | B | U8 | B:e40 @ 11.55 | source_track=track_007; aggregation=entity_state_union; source_tracks=['B:track_007'] |
| g81 | 5.10 | TRACK_LOST | A | U8 | A:e42 @ 11.85 | source_track=track_008; aggregation=entity_state_union; source_tracks=['A:track_008'] |

## Edges

```
    g01 --PRECEDES--> g16
    g01 --PRECEDES--> g17
    g02 --PRECEDES--> g16
    g02 --PRECEDES--> g17
    g03 --PRECEDES--> g16
    g03 --PRECEDES--> g17
    g04 --PRECEDES--> g16
    g04 --PRECEDES--> g17
    g05 --PRECEDES--> g16
    g05 --PRECEDES--> g17
    g06 --PRECEDES--> g16
    g06 --PRECEDES--> g17
    g07 --PRECEDES--> g16
    g07 --PRECEDES--> g17
    g08 --PRECEDES--> g16
    g08 --PRECEDES--> g17
    g09 --PRECEDES--> g16
    g09 --PRECEDES--> g17
    g10 --PRECEDES--> g16
    g10 --PRECEDES--> g17
    g11 --PRECEDES--> g16
    g11 --PRECEDES--> g17
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
    g18 --PRECEDES--> g20
    g19 --PRECEDES--> g21
    g19 --PRECEDES--> g22
    g20 --PRECEDES--> g21
    g20 --PRECEDES--> g22
    g21 --PRECEDES--> g23
    g22 --PRECEDES--> g23
    g23 --PRECEDES--> g24
    g24 --PRECEDES--> g25
    g24 --PRECEDES--> g26
    g25 --PRECEDES--> g27
    g26 --PRECEDES--> g27
    g27 --PRECEDES--> g28
    g28 --PRECEDES--> g29
    g29 --PRECEDES--> g30
    g30 --PRECEDES--> g31
    g30 --PRECEDES--> g32
    g31 --PRECEDES--> g33
    g31 --PRECEDES--> g34
    g31 --PRECEDES--> g35
    g32 --PRECEDES--> g33
    g32 --PRECEDES--> g34
    g32 --PRECEDES--> g35
    g33 --PRECEDES--> g36
    g33 --PRECEDES--> g37
    g33 --PRECEDES--> g38
    g33 --PRECEDES--> g39
    g34 --PRECEDES--> g36
    g34 --PRECEDES--> g37
    g34 --PRECEDES--> g38
    g34 --PRECEDES--> g39
    g35 --PRECEDES--> g36
    g35 --PRECEDES--> g37
    g35 --PRECEDES--> g38
    g35 --PRECEDES--> g39
    g36 --PRECEDES--> g40
    g37 --PRECEDES--> g40
    g38 --PRECEDES--> g40
    g39 --PRECEDES--> g40
    g40 --PRECEDES--> g41
    g40 --PRECEDES--> g42
    g41 --PRECEDES--> g43
    g41 --PRECEDES--> g44
    g42 --PRECEDES--> g43
    g42 --PRECEDES--> g44
    g43 --PRECEDES--> g45
    g44 --PRECEDES--> g45
    g45 --PRECEDES--> g46
    g46 --PRECEDES--> g47
    g46 --PRECEDES--> g48
    g46 --PRECEDES--> g49
    g47 --PRECEDES--> g50
    g47 --PRECEDES--> g51
    g47 --PRECEDES--> g52
    g47 --PRECEDES--> g53
    g47 --PRECEDES--> g54
    g48 --PRECEDES--> g50
    g48 --PRECEDES--> g51
    g48 --PRECEDES--> g52
    g48 --PRECEDES--> g53
    g48 --PRECEDES--> g54
    g49 --PRECEDES--> g50
    g49 --PRECEDES--> g51
    g49 --PRECEDES--> g52
    g49 --PRECEDES--> g53
    g49 --PRECEDES--> g54
    g50 --PRECEDES--> g55
    g51 --PRECEDES--> g55
    g52 --PRECEDES--> g55
    g53 --PRECEDES--> g55
    g54 --PRECEDES--> g55
    g55 --PRECEDES--> g56
    g56 --PRECEDES--> g57
    g57 --PRECEDES--> g58
    g58 --PRECEDES--> g59
    g58 --PRECEDES--> g60
    g59 --PRECEDES--> g61
    g60 --PRECEDES--> g61
    g61 --PRECEDES--> g62
    g61 --PRECEDES--> g63
    g62 --PRECEDES--> g64
    g62 --PRECEDES--> g65
    g62 --PRECEDES--> g66
    g63 --PRECEDES--> g64
    g63 --PRECEDES--> g65
    g63 --PRECEDES--> g66
    g64 --PRECEDES--> g67
    g64 --PRECEDES--> g68
    g65 --PRECEDES--> g67
    g65 --PRECEDES--> g68
    g66 --PRECEDES--> g67
    g66 --PRECEDES--> g68
    g67 --PRECEDES--> g69
    g68 --PRECEDES--> g69
    g69 --PRECEDES--> g70
    g69 --PRECEDES--> g71
    g70 --PRECEDES--> g72
    g71 --PRECEDES--> g72
    g72 --PRECEDES--> g73
    g73 --PRECEDES--> g74
    g74 --PRECEDES--> g75
    g75 --PRECEDES--> g76
    g76 --PRECEDES--> g77
    g77 --PRECEDES--> g78
    g78 --PRECEDES--> g79
    g79 --PRECEDES--> g80
    g80 --PRECEDES--> g81
    g08 --SAME_TRACK--> g13
    g19 --SAME_TRACK--> g20
    g05 --SAME_TRACK--> g21
    g09 --SAME_TRACK--> g22
    g07 --SAME_TRACK--> g25
    g08 --SAME_TRACK--> g26
    g19 --SAME_TRACK--> g27
    g19 --SAME_TRACK--> g29
    g31 --SAME_TRACK--> g32
    g19 --SAME_TRACK--> g38
    g06 --SAME_TRACK--> g43
    g06 --SAME_TRACK--> g44
    g19 --SAME_TRACK--> g45
    g36 --SAME_TRACK--> g46
    g19 --SAME_TRACK--> g48
    g19 --SAME_TRACK--> g50
    g31 --SAME_TRACK--> g58
    g05 --SAME_TRACK--> g61
    g70 --SAME_TRACK--> g71
    g72 --SAME_TRACK--> g73
    g72 --SAME_TRACK--> g75
    g70 --SAME_TRACK--> g77
    g06 --SAME_TRACK--> g79
    g36 --SAME_TRACK--> g81
    g10 --SAME_TRACK--> g14
    g11 --SAME_TRACK--> g15
    g16 --SAME_TRACK--> g17
    g18 --SAME_TRACK--> g23
    g16 --SAME_TRACK--> g24
    g10 --SAME_TRACK--> g28
    g12 --SAME_TRACK--> g30
    g33 --SAME_TRACK--> g34
    g10 --SAME_TRACK--> g35
    g37 --SAME_TRACK--> g39
    g10 --SAME_TRACK--> g40
    g41 --SAME_TRACK--> g42
    g10 --SAME_TRACK--> g49
    g10 --SAME_TRACK--> g55
    g37 --SAME_TRACK--> g56
    g11 --SAME_TRACK--> g57
    g33 --SAME_TRACK--> g59
    g41 --SAME_TRACK--> g60
    g18 --SAME_TRACK--> g62
    g41 --SAME_TRACK--> g63
    g69 --SAME_TRACK--> g74
    g18 --SAME_TRACK--> g78
    g37 --SAME_TRACK--> g80
```

## Global trace

Events in one row are simultaneous at 0.05 s resolution: their order is unresolved.

| t_global | Events |
|---------:|--------|
| -6.75 | MOVING_START(A); MOVING_START(B); THROTTLE_START(A); THROTTLE_START(B); TRACK_APPEARED_FRONT(A,U3); TRACK_APPEARED_LEFT(A,U1); TRACK_APPEARED_LEFT(A,U2); TRACK_APPEARED_RIGHT(A,U4); TRACK_APPEARED_RIGHT(A,U5); TRACK_APPEARED_RIGHT(B,A); TRACK_APPEARED_RIGHT(B,U3); TRACK_APPEARED_RIGHT(B,U6); CLOSING_START(A,U4); CLOSING_START(B,A); CLOSING_START(B,U3) |
| -6.55 | TRACK_APPEARED_FRONT(B,U7); CLOSING_START(B,U7) |
| -6.40 | TRACK_APPEARED_FRONT(B,U1) |
| -6.35 | TRACK_APPEARED_LEFT(A,B); CLOSING_START(A,B) |
| -6.25 | CRITICAL_TTC_START(A,U3); TRACK_LOST(A,U5) |
| -5.90 | CRITICAL_TTC_START(B,U1) |
| -3.65 | TRACK_LOST(B,U7) |
| -3.15 | TRACK_LOST(A,U2); TRACK_LOST(A,U4) |
| -2.70 | CLOSING_END(A,B) |
| -2.65 | CLOSING_END(B,A) |
| -1.60 | CRITICAL_TTC_START(A,B) |
| -1.55 | TRACK_LOST(B,U6) |
| -1.45 | TRACK_APPEARED_RIGHT(A,U4); CLOSING_START(A,U4) |
| -1.10 | TRACK_APPEARED_RIGHT(B,U4); CLOSING_START(B,U4); CRITICAL_TTC_START(B,A) |
| -0.85 | TRACK_APPEARED_FRONT(A,U8); TRACK_APPEARED_RIGHT(B,U8); CLOSING_START(A,B); CLOSING_START(B,U8) |
| -0.65 | CLOSING_START(B,A) |
| -0.55 | TRACK_APPEARED_RIGHT(B,U9); CLOSING_START(B,U9) |
| -0.45 | EGO_PATH_ENTRY(A,U1); CRITICAL_TTC_START(A,U1) |
| -0.30 | EGO_PATH_ENTRY(A,B) |
| -0.25 | EGO_PATH_ENTRY(A,U8) |
| +0.00 | COLLISION(A,B); CRITICAL_TTC_END(A,B); CRITICAL_TTC_END(B,A) |
| +0.05 | CLOSING_END(A,B); THROTTLE_END(A); THROTTLE_END(B); BRAKE_START(A); BRAKE_START(B) |
| +0.10 | CLOSING_END(B,A) |
| +0.30 | CLOSING_END(B,U8) |
| +0.35 | CLOSING_END(B,U3) |
| +0.45 | CLOSING_END(A,U4) |
| +0.60 | CLOSING_END(B,U4); CLOSING_END(B,U9) |
| +0.70 | CRITICAL_TTC_END(A,U3) |
| +0.80 | CRITICAL_TTC_END(B,U1); TRACK_LOST(B,U9) |
| +1.15 | MOVING_END(B); STOP_START(B); TRACK_APPEARED_FRONT(A,U10) |
| +1.20 | MOVING_END(A); STOP_START(A) |
| +1.50 | TRACK_APPEARED_LEFT(B,U11) |
| +1.55 | TRACK_APPEARED_RIGHT(A,U12); CLOSING_START(A,U12) |
| +1.80 | TRACK_APPEARED_LEFT(A,U11) |
| +2.45 | EGO_PATH_ENTRY(A,U11) |
| +2.95 | TRACK_LOST(B,U11) |
| +3.20 | TRACK_LOST(A,U11) |
| +3.45 | TRACK_APPEARED_RIGHT(B,U12) |
| +3.60 | CLOSING_END(A,U12) |
| +4.35 | TRACK_LOST(B,U1) |
| +4.45 | TRACK_LOST(A,U1) |
| +4.80 | TRACK_LOST(B,U8) |
| +5.10 | TRACK_LOST(A,U8) |

## Temporal safety relations

Per track: does the cut-in start before the critical TTC, or was the critical TTC already active? Is the path entry before or after it? Temporal properties only, not causes.

- A's track_001 (unidentified U1): CRITICAL_TTC_START 6.30, COLLISION 6.75 (+0.45 s); EGO_PATH_ENTRY 6.30 together with critical TTC (+0.00 s) [local times; t_global: critical_ttc_start -0.45, ego_path_entry -0.45, collision +0.00]
- A's track_003 (unidentified U3): CRITICAL_TTC_START 0.50, COLLISION 6.75 (+6.25 s) [local times; t_global: critical_ttc_start -6.25, collision +0.00]
- A's track_006 (B): CRITICAL_TTC_START 5.15, COLLISION with B 6.75 (+1.60 s); EGO_PATH_ENTRY 6.45 after critical TTC (+1.30 s) [local times; t_global: critical_ttc_start -1.60, ego_path_entry -0.30, collision +0.00]
- A's track_008 (unidentified U8): EGO_PATH_ENTRY 6.50, no critical TTC [local times; t_global: ego_path_entry -0.25, collision +0.00]
- A's track_011 (unidentified U11): EGO_PATH_ENTRY 9.20, no critical TTC [local times; t_global: ego_path_entry +2.45]
- B's track_001 (A): CRITICAL_TTC_START 5.65, COLLISION with A 6.75 (+1.10 s) [local times; t_global: critical_ttc_start -1.10, collision +0.00]
- B's track_005 (unidentified U1): CRITICAL_TTC_START 0.85, COLLISION 6.75 (+5.90 s) [local times; t_global: critical_ttc_start -5.90, collision +0.00]

## Perceived state before each event, per observing recorder

Each recorder's own belief just before its events, in its own local names (track_001, ...): fusion does not rewrite it. True states are named, unknown ones end with `?`.

| t_global | Recorder | Events (local node) | Perceived state just before |
|---------:|----------|---------------------|-----------------------------|
| -6.75 | A | g01 MOVING_START(A) (A:e01)<br>g03 THROTTLE_START(A) (A:e02)<br>g05 TRACK_APPEARED_FRONT(A,U3) (A:e03)<br>g06 TRACK_APPEARED_LEFT(A,U1) (A:e04)<br>g07 TRACK_APPEARED_LEFT(A,U2) (A:e05)<br>g08 TRACK_APPEARED_RIGHT(A,U4) (A:e06)<br>g09 TRACK_APPEARED_RIGHT(A,U5) (A:e07)<br>g13 CLOSING_START(A,U4) (A:e08) | ego: not yet observed |
| -6.75 | B | g02 MOVING_START(B) (B:e01)<br>g04 THROTTLE_START(B) (B:e02)<br>g10 TRACK_APPEARED_RIGHT(B,A) (B:e03)<br>g11 TRACK_APPEARED_RIGHT(B,U3) (B:e04)<br>g12 TRACK_APPEARED_RIGHT(B,U6) (B:e05)<br>g14 CLOSING_START(B,A) (B:e06)<br>g15 CLOSING_START(B,U3) (B:e07) | ego: not yet observed |
| -6.75 | A | g06 TRACK_APPEARED_LEFT(A,U1) (A:e04)<br>g79 TRACK_LOST(A,U1) (A:e41) | ego: not yet observed |
| -6.75 | A | g07 TRACK_APPEARED_LEFT(A,U2) (A:e05)<br>g08 TRACK_APPEARED_RIGHT(A,U4) (A:e06)<br>g25 TRACK_LOST(A,U2) (A:e13)<br>g26 TRACK_LOST(A,U4) (A:e14) | ego: not yet observed |
| -6.75 | A | g09 TRACK_APPEARED_RIGHT(A,U5) (A:e07)<br>g21 CRITICAL_TTC_START(A,U3) (A:e11)<br>g22 TRACK_LOST(A,U5) (A:e12) | ego: not yet observed |
| -6.75 | B | g12 TRACK_APPEARED_RIGHT(B,U6) (B:e05)<br>g30 TRACK_LOST(B,U6) (B:e14) | ego: not yet observed |
| -6.75 | B | g14 CLOSING_START(B,A) (B:e06)<br>g28 CLOSING_END(B,A) (B:e13) | ego: not yet observed |
| -6.75 | B | g15 CLOSING_START(B,U3) (B:e07)<br>g57 CLOSING_END(B,U3) (B:e29) | ego: not yet observed |
| -6.55 | B | g16 TRACK_APPEARED_FRONT(B,U7) (B:e08)<br>g17 CLOSING_START(B,U7) (B:e09) | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC?<br>track_002: CLOSING, CRITICAL_TTC?<br>track_003: CRITICAL_TTC? |
| -6.55 | B | g16 TRACK_APPEARED_FRONT(B,U7) (B:e08)<br>g24 TRACK_LOST(B,U7) (B:e12) | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC?<br>track_002: CLOSING, CRITICAL_TTC?<br>track_003: CRITICAL_TTC? |
| -6.40 | B | g18 TRACK_APPEARED_FRONT(B,U1) (B:e10) | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC?<br>track_002: CLOSING, CRITICAL_TTC?<br>track_003: CRITICAL_TTC?<br>track_004: CLOSING, CRITICAL_TTC? |
| -6.40 | B | g18 TRACK_APPEARED_FRONT(B,U1) (B:e10)<br>g78 TRACK_LOST(B,U1) (B:e39) | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC?<br>track_002: CLOSING, CRITICAL_TTC?<br>track_003: CRITICAL_TTC?<br>track_004: CLOSING, CRITICAL_TTC? |
| -6.35 | A | g19 TRACK_APPEARED_LEFT(A,B) (A:e09)<br>g20 CLOSING_START(A,B) (A:e10) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC?<br>track_002: CRITICAL_TTC?<br>track_003: IN_EGO_PATH, CRITICAL_TTC?<br>track_004: CLOSING, CRITICAL_TTC?<br>track_005: CRITICAL_TTC? |
| -6.35 | A | g20 CLOSING_START(A,B) (A:e10)<br>g27 CLOSING_END(A,B) (A:e15) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC?<br>track_002: CRITICAL_TTC?<br>track_003: IN_EGO_PATH, CRITICAL_TTC?<br>track_004: CLOSING, CRITICAL_TTC?<br>track_005: CRITICAL_TTC? |
| -6.25 | A | g21 CRITICAL_TTC_START(A,U3) (A:e11)<br>g61 CRITICAL_TTC_END(A,U3) (A:e31) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC?<br>track_002: CRITICAL_TTC?<br>track_003: IN_EGO_PATH, CRITICAL_TTC?<br>track_004: CLOSING, CRITICAL_TTC?<br>track_005: CRITICAL_TTC?<br>track_006: CLOSING, CRITICAL_TTC? |
| -5.90 | B | g23 CRITICAL_TTC_START(B,U1) (B:e11) | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>track_002: CLOSING<br>track_003: no active state<br>track_004: CLOSING<br>track_005: IN_EGO_PATH, CRITICAL_TTC? |
| -5.90 | B | g23 CRITICAL_TTC_START(B,U1) (B:e11)<br>g41 TRACK_APPEARED_RIGHT(B,U9) (B:e21)<br>g62 CRITICAL_TTC_END(B,U1) (B:e32)<br>g63 TRACK_LOST(B,U9) (B:e33) | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>track_002: CLOSING<br>track_003: no active state<br>track_004: CLOSING<br>track_005: IN_EGO_PATH, CRITICAL_TTC? |
| -1.60 | A | g29 CRITICAL_TTC_START(A,B) (A:e16) | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_003: CRITICAL_TTC, IN_EGO_PATH<br>track_006: no active state<br>track lost, states UNKNOWN: track_002, track_004, track_005 |
| -1.60 | A | g29 CRITICAL_TTC_START(A,B) (A:e16)<br>g47 COLLISION(A,B) (A:e25)<br>g48 CRITICAL_TTC_END(A,B) (A:e26) | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_003: CRITICAL_TTC, IN_EGO_PATH<br>track_006: no active state<br>track lost, states UNKNOWN: track_002, track_004, track_005 |
| -1.45 | A | g31 TRACK_APPEARED_RIGHT(A,U4) (A:e17)<br>g32 CLOSING_START(A,U4) (A:e18) | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_003: CRITICAL_TTC, IN_EGO_PATH<br>track_006: CRITICAL_TTC<br>track lost, states UNKNOWN: track_002, track_004, track_005 |
| -1.45 | A | g32 CLOSING_START(A,U4) (A:e18)<br>g58 CLOSING_END(A,U4) (A:e30) | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_003: CRITICAL_TTC, IN_EGO_PATH<br>track_006: CRITICAL_TTC<br>track lost, states UNKNOWN: track_002, track_004, track_005 |
| -1.10 | B | g33 TRACK_APPEARED_RIGHT(B,U4) (B:e15)<br>g34 CLOSING_START(B,U4) (B:e16)<br>g35 CRITICAL_TTC_START(B,A) (B:e17) | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: CLOSING<br>track_005: CRITICAL_TTC, IN_EGO_PATH<br>track lost, states UNKNOWN: track_003, track_004 |
| -1.10 | B | g34 CLOSING_START(B,U4) (B:e16)<br>g42 CLOSING_START(B,U9) (B:e22)<br>g59 CLOSING_END(B,U4) (B:e30)<br>g60 CLOSING_END(B,U9) (B:e31) | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: CLOSING<br>track_005: CRITICAL_TTC, IN_EGO_PATH<br>track lost, states UNKNOWN: track_003, track_004 |
| -1.10 | B | g35 CRITICAL_TTC_START(B,A) (B:e17)<br>g47 COLLISION(A,B) (B:e23)<br>g49 CRITICAL_TTC_END(B,A) (B:e24) | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: CLOSING<br>track_005: CRITICAL_TTC, IN_EGO_PATH<br>track lost, states UNKNOWN: track_003, track_004 |
| -0.85 | A | g36 TRACK_APPEARED_FRONT(A,U8) (A:e19)<br>g38 CLOSING_START(A,B) (A:e20) | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_003: CRITICAL_TTC, IN_EGO_PATH<br>track_006: CRITICAL_TTC<br>track_007: CLOSING<br>track lost, states UNKNOWN: track_002, track_004, track_005 |
| -0.85 | A | g36 TRACK_APPEARED_FRONT(A,U8) (A:e19)<br>g81 TRACK_LOST(A,U8) (A:e42) | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_003: CRITICAL_TTC, IN_EGO_PATH<br>track_006: CRITICAL_TTC<br>track_007: CLOSING<br>track lost, states UNKNOWN: track_002, track_004, track_005 |
| -0.85 | B | g37 TRACK_APPEARED_RIGHT(B,U8) (B:e18)<br>g39 CLOSING_START(B,U8) (B:e19) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC<br>track_002: CLOSING<br>track_005: CRITICAL_TTC, IN_EGO_PATH<br>track_006: CLOSING, CRITICAL_TTC?<br>track lost, states UNKNOWN: track_003, track_004 |
| -0.85 | B | g37 TRACK_APPEARED_RIGHT(B,U8) (B:e18)<br>g80 TRACK_LOST(B,U8) (B:e40) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC<br>track_002: CLOSING<br>track_005: CRITICAL_TTC, IN_EGO_PATH<br>track_006: CLOSING, CRITICAL_TTC?<br>track lost, states UNKNOWN: track_003, track_004 |
| -0.85 | A | g38 CLOSING_START(A,B) (A:e20)<br>g50 CLOSING_END(A,B) (A:e27)<br>g51 THROTTLE_END(A) (A:e28)<br>g53 BRAKE_START(A) (A:e29) | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_003: CRITICAL_TTC, IN_EGO_PATH<br>track_006: CRITICAL_TTC<br>track_007: CLOSING<br>track lost, states UNKNOWN: track_002, track_004, track_005 |
| -0.85 | B | g39 CLOSING_START(B,U8) (B:e19)<br>g56 CLOSING_END(B,U8) (B:e28) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC<br>track_002: CLOSING<br>track_005: CRITICAL_TTC, IN_EGO_PATH<br>track_006: CLOSING, CRITICAL_TTC?<br>track lost, states UNKNOWN: track_003, track_004 |
| -0.65 | B | g40 CLOSING_START(B,A) (B:e20) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC<br>track_002: CLOSING<br>track_005: CRITICAL_TTC, IN_EGO_PATH<br>track_006: CLOSING, CRITICAL_TTC?<br>track_007: CLOSING, CRITICAL_TTC?<br>track lost, states UNKNOWN: track_003, track_004 |
| -0.65 | B | g40 CLOSING_START(B,A) (B:e20)<br>g55 CLOSING_END(B,A) (B:e27) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC<br>track_002: CLOSING<br>track_005: CRITICAL_TTC, IN_EGO_PATH<br>track_006: CLOSING, CRITICAL_TTC?<br>track_007: CLOSING, CRITICAL_TTC?<br>track lost, states UNKNOWN: track_003, track_004 |
| -0.55 | B | g41 TRACK_APPEARED_RIGHT(B,U9) (B:e21)<br>g42 CLOSING_START(B,U9) (B:e22) | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC<br>track_002: CLOSING<br>track_005: CRITICAL_TTC, IN_EGO_PATH<br>track_006: CLOSING<br>track_007: CLOSING, CRITICAL_TTC?<br>track lost, states UNKNOWN: track_003, track_004 |
| -0.45 | A | g43 EGO_PATH_ENTRY(A,U1) (A:e21)<br>g44 CRITICAL_TTC_START(A,U1) (A:e22) | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_003: CRITICAL_TTC, IN_EGO_PATH<br>track_006: CLOSING, CRITICAL_TTC<br>track_007: CLOSING<br>track_008: CRITICAL_TTC?<br>track lost, states UNKNOWN: track_002, track_004, track_005 |
| -0.30 | A | g45 EGO_PATH_ENTRY(A,B) (A:e23) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_003: CRITICAL_TTC, IN_EGO_PATH<br>track_006: CLOSING, CRITICAL_TTC<br>track_007: CLOSING<br>track_008: no active state<br>track lost, states UNKNOWN: track_002, track_004, track_005 |
| -0.25 | A | g46 EGO_PATH_ENTRY(A,U8) (A:e24) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_003: CRITICAL_TTC, IN_EGO_PATH<br>track_006: CLOSING, CRITICAL_TTC, IN_EGO_PATH<br>track_007: CLOSING<br>track_008: no active state<br>track lost, states UNKNOWN: track_002, track_004, track_005 |
| +0.05 | B | g52 THROTTLE_END(B) (B:e25)<br>g54 BRAKE_START(B) (B:e26) | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>track_002: CLOSING<br>track_005: CRITICAL_TTC, IN_EGO_PATH<br>track_006: CLOSING<br>track_007: CLOSING<br>track_008: CLOSING<br>track lost, states UNKNOWN: track_003, track_004 |
| +1.15 | B | g64 MOVING_END(B) (B:e34)<br>g65 STOP_START(B) (B:e35) | ego: MOVING, BRAKE<br>track_001: no active state<br>track_002: no active state<br>track_005: IN_EGO_PATH<br>track_006: no active state<br>track_007: no active state<br>track lost, states UNKNOWN: track_003, track_004, track_008 |
| +1.15 | A | g66 TRACK_APPEARED_FRONT(A,U10) (A:e32) | ego: MOVING, BRAKE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_003: IN_EGO_PATH<br>track_006: IN_EGO_PATH<br>track_007: no active state<br>track_008: IN_EGO_PATH<br>track lost, states UNKNOWN: track_002, track_004, track_005 |
| +1.20 | A | g67 MOVING_END(A) (A:e33)<br>g68 STOP_START(A) (A:e34) | ego: MOVING, BRAKE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_003: IN_EGO_PATH<br>track_006: IN_EGO_PATH<br>track_007: no active state<br>track_008: IN_EGO_PATH<br>track_009: CRITICAL_TTC?<br>track lost, states UNKNOWN: track_002, track_004, track_005 |
| +1.50 | B | g69 TRACK_APPEARED_LEFT(B,U11) (B:e36) | ego: STOP, BRAKE<br>track_001: no active state<br>track_002: no active state<br>track_005: IN_EGO_PATH<br>track_006: no active state<br>track_007: no active state<br>track lost, states UNKNOWN: track_003, track_004, track_008 |
| +1.50 | B | g69 TRACK_APPEARED_LEFT(B,U11) (B:e36)<br>g74 TRACK_LOST(B,U11) (B:e37) | ego: STOP, BRAKE<br>track_001: no active state<br>track_002: no active state<br>track_005: IN_EGO_PATH<br>track_006: no active state<br>track_007: no active state<br>track lost, states UNKNOWN: track_003, track_004, track_008 |
| +1.55 | A | g70 TRACK_APPEARED_RIGHT(A,U12) (A:e35)<br>g71 CLOSING_START(A,U12) (A:e36) | ego: STOP, BRAKE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_003: IN_EGO_PATH<br>track_006: IN_EGO_PATH<br>track_007: no active state<br>track_008: IN_EGO_PATH<br>track_009: CRITICAL_TTC?<br>track lost, states UNKNOWN: track_002, track_004, track_005 |
| +1.55 | A | g71 CLOSING_START(A,U12) (A:e36)<br>g77 CLOSING_END(A,U12) (A:e40) | ego: STOP, BRAKE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_003: IN_EGO_PATH<br>track_006: IN_EGO_PATH<br>track_007: no active state<br>track_008: IN_EGO_PATH<br>track_009: CRITICAL_TTC?<br>track lost, states UNKNOWN: track_002, track_004, track_005 |
| +1.80 | A | g72 TRACK_APPEARED_LEFT(A,U11) (A:e37) | ego: STOP, BRAKE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_003: IN_EGO_PATH<br>track_006: IN_EGO_PATH<br>track_007: no active state<br>track_008: IN_EGO_PATH<br>track_009: no active state<br>track_010: CLOSING, CRITICAL_TTC?<br>track lost, states UNKNOWN: track_002, track_004, track_005 |
| +1.80 | A | g72 TRACK_APPEARED_LEFT(A,U11) (A:e37)<br>g75 TRACK_LOST(A,U11) (A:e39) | ego: STOP, BRAKE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_003: IN_EGO_PATH<br>track_006: IN_EGO_PATH<br>track_007: no active state<br>track_008: IN_EGO_PATH<br>track_009: no active state<br>track_010: CLOSING, CRITICAL_TTC?<br>track lost, states UNKNOWN: track_002, track_004, track_005 |
| +2.45 | A | g73 EGO_PATH_ENTRY(A,U11) (A:e38) | ego: STOP, BRAKE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_003: IN_EGO_PATH<br>track_006: IN_EGO_PATH<br>track_007: no active state<br>track_008: IN_EGO_PATH<br>track_009: no active state<br>track_010: CLOSING<br>track_011: no active state<br>track lost, states UNKNOWN: track_002, track_004, track_005 |
| +3.45 | B | g76 TRACK_APPEARED_RIGHT(B,U12) (B:e38) | ego: STOP, BRAKE<br>track_001: no active state<br>track_002: no active state<br>track_005: IN_EGO_PATH<br>track_006: no active state<br>track_007: no active state<br>track lost, states UNKNOWN: track_003, track_004, track_008, track_009 |

## Plain-language reading

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
