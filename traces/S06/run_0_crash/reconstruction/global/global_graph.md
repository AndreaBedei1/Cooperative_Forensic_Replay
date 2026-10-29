# Global graph - S06/run_0_crash

Global time `t_global` is 0 at the reference collision. The local graphs were not modified: every node lists the local node(s) and local time(s) it comes from.

Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.

## Entities

| Entity | Kind | Details |
|--------|------|---------|
| A | recorder | clock ALIGNED; observed by others as: B:track_002, C:track_001 |
| B | recorder | clock ALIGNED; observed by others as: A:track_002 |
| C | recorder | clock ALIGNED; observed by others as: A:track_001, B:track_001 |
| U1 | anonymous_road_user | anonymous; observed by C as C:track_002 |

## Graph alignment

Reference event: `collision_001` (t_global = 0); `t_global = t_local + offset_to_global`. A graph that did not report it is aligned through the chain of matched collisions linking it to the reference (multi-hop); its anchor is its own report of the last collision of that chain.

| Graph | Status | Anchor node | Anchor local time | Offset to global | Note |
|-------|--------|-------------|------------------:|-----------------:|------|
| A | ALIGNED | A:e09 | 4.10 | -4.10 | reported the reference collision collision_001 |
| B | ALIGNED | B:e09 | 4.10 | -4.10 | reported the reference collision collision_001 |
| C | ALIGNED | - | - | -4.15 | aligned through observed trajectories: the near surfaces of A:track_001, B:track_001, C:track_001 on A, C:track_002 on B lie where their lines of sight enter the body (pooled median 0.59 sigma) at this offset; offsets within 2.00 sigma span [-4.20, -4.00] s and nothing else fits |

Estimated relative clock offsets: B - A = +0.000 s, C - A = +0.050 s, C - B = +0.050 s

Matched `collision_001`: A and B both recorded a collision; peak impulses 12137.59 vs 12137.59 N*s (similarity 1.000, tolerance 0.10); no competing report within tolerance; the two bodies touch at their reports (0.00 m apart, tolerance 1.0 m); independent relative impulse std 0.100; combined z 0.000 (gate 3.0); engineering assumption; pre-contact radar view of each recorder checked against the candidate partner's own speed: not contradicted

## Identity associations

| Local track | Global entity | Status | Confidence | Evidence |
|-------------|---------------|--------|-----------:|----------|
| A:track_001 | C | ASSOCIATED | 0.99 | A and B both reported collision_001 (peak impulse 12137.59 vs 12137.59 N*s)<br>tracked for 4.10 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 21.7 m -> 11.7 m over the last 1.0 s<br>track motion contradicts B's own speed in the observed direction (3 sigma; full-speed RMSE 8.44 m/s for reference)<br>clearance at the contact 11.68 m (beyond 3.50 m: confidence factor 0.02)<br>common frame: its returns lie on C's own footprint (median 0.00 m, 0.00 sigma of the relative uncertainty, over 302 samples; 99% within 3 sigma) at C's own velocity |
| A:track_002 | B | ASSOCIATED | 0.96 | A and B both reported collision_001 (peak impulse 12137.59 vs 12137.59 N*s)<br>tracked for 2.05 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 14.9 m -> 0.0 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 0.41 m/s for reference)<br>clearance at the contact 0.00 m<br>the only track of A compatible with the contact |
| B:track_001 | C | ASSOCIATED | 1.00 | B and A both reported collision_001 (peak impulse 12137.59 vs 12137.59 N*s)<br>tracked for 2.00 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 18.4 m -> 10.8 m over the last 1.0 s<br>track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 7.78 m/s for reference)<br>clearance at the contact 10.75 m (beyond 3.50 m: confidence factor 0.05)<br>common frame: its returns lie on C's own footprint (median 0.00 m, 0.00 sigma of the relative uncertainty, over 261 samples; 100% within 3 sigma) at C's own velocity |
| B:track_002 | A | ASSOCIATED | 0.95 | B and A both reported collision_001 (peak impulse 12137.59 vs 12137.59 N*s)<br>tracked for 2.00 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 14.9 m -> 1.1 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 0.48 m/s for reference)<br>clearance at the contact 0.62 m<br>the only track of B compatible with the contact |
| C:track_001 | A | ASSOCIATED | 1.00 | no matched collision of C names a partner<br>common frame: its returns lie on A's own footprint (median 0.00 m, 0.00 sigma of the relative uncertainty, over 79 samples; 100% within 3 sigma) at A's own velocity |
| C:track_002 | U1 | ANONYMOUS | - | no matched collision of C names a partner<br>anonymous road user U1: C:track_002 |

## Nodes

| Id | Global time | Type | Actor | Subject / participants | Observed by (local node @ local time) | Details |
|----|------------:|------|-------|------------------------|----------------------------------------|---------|
| g01 | -4.15 | MOVING_START | C | - | C:e01 @ 0.00 | active_at_first_observation=True |
| g02 | -4.15 | THROTTLE_START | C | - | C:e02 @ 0.00 | active_at_first_observation=True |
| g03 | -4.15 | TRACK_APPEARED_FRONT | C | A | C:e03 @ 0.00, C:e14 @ 4.55 | initial_in_ego_path=False; source_track=track_001; aggregation=entity_state_union; source_tracks=['C:track_001'] |
| g04 | -4.15 | CLOSING_START | C | A | C:e04 @ 0.00 | active_at_first_observation=True; source_track=track_001; aggregation=entity_state_union; source_tracks=['C:track_001'] |
| g05 | -4.10 | MOVING_START | A | - | A:e01 @ 0.00 | active_at_first_observation=True |
| g06 | -4.10 | MOVING_START | B | - | B:e01 @ 0.00 | active_at_first_observation=True |
| g07 | -4.10 | THROTTLE_START | A | - | A:e02 @ 0.00 | active_at_first_observation=True |
| g08 | -4.10 | THROTTLE_START | B | - | B:e02 @ 0.00 | active_at_first_observation=True |
| g09 | -4.10 | TRACK_APPEARED_FRONT | A | C | A:e03 @ 0.00 | initial_in_ego_path=False; source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g10 | -4.10 | CLOSING_START | A | C | A:e04 @ 0.00, A:e18 @ 4.75 | active_at_first_observation=True; source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g11 | -2.05 | TRACK_APPEARED_LEFT | C | U1 | C:e05 @ 2.10 | initial_in_ego_path=False; source_track=track_002; aggregation=entity_state_union; source_tracks=['C:track_002'] |
| g12 | -2.05 | TRACK_APPEARED_RIGHT | A | B | A:e05 @ 2.05 | initial_in_ego_path=False; source_track=track_002; aggregation=entity_state_union; source_tracks=['A:track_002'] |
| g13 | -2.05 | CLOSING_START | A | B | A:e06 @ 2.05, A:e11 @ 4.10 | active_at_first_observation=True; source_track=track_002; aggregation=entity_state_union; source_tracks=['A:track_002'] |
| g14 | -2.05 | CLOSING_START | C | U1 | C:e06 @ 2.10, C:e13 @ 4.55 | active_at_first_observation=True; source_track=track_002; aggregation=entity_state_union; source_tracks=['C:track_002'] |
| g15 | -2.00 | TRACK_APPEARED_LEFT | B | A | B:e03 @ 2.10 | initial_in_ego_path=False; source_track=track_002; aggregation=entity_state_union; source_tracks=['B:track_002'] |
| g16 | -2.00 | TRACK_APPEARED_RIGHT | B | C | B:e04 @ 2.10 | initial_in_ego_path=False; source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g17 | -2.00 | CLOSING_START | B | A | B:e06 @ 2.10, B:e11 @ 4.10 | active_at_first_observation=True; source_track=track_002; aggregation=entity_state_union; source_tracks=['B:track_002'] |
| g18 | -2.00 | CLOSING_START | B | C | B:e05 @ 2.10, B:e16 @ 4.60 | active_at_first_observation=True; source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g19 | -1.80 | THROTTLE_END | C | - | C:e07 @ 2.35 |  |
| g20 | -1.80 | BRAKE_START | C | - | C:e08 @ 2.35 |  |
| g21 | -1.55 | CRITICAL_TTC_START | A | B | A:e07 @ 2.55, A:e10 @ 4.10 | source_track=track_002; aggregation=entity_state_union; source_tracks=['A:track_002'] |
| g22 | -1.50 | CRITICAL_TTC_START | B | A | B:e07 @ 2.60, B:e10 @ 4.10 | source_track=track_002; aggregation=entity_state_union; source_tracks=['B:track_002'] |
| g23 | -1.25 | MOVING_END | C | - | C:e09 @ 2.90 |  |
| g24 | -1.25 | STOP_START | C | - | C:e10 @ 2.90 |  |
| g25 | -0.25 | EGO_PATH_ENTRY | C | U1 | C:e11 @ 3.90 | occupancy_evidence=returns; occupancy_margin_m=0.51; occupancy_sigma_m=0.25; cause=TARGET_LATERAL; geometry=estimated_body; source_track=track_002; aggregation=entity_state_union; source_tracks=['C:track_002'] |
| g26 | -0.20 | EGO_PATH_ENTRY | C | A | C:e12 @ 3.95 | occupancy_evidence=box; occupancy_margin_m=0.47; occupancy_sigma_m=0.28; cause=TARGET_LATERAL; geometry=estimated_body; source_track=track_001; aggregation=entity_state_union; source_tracks=['C:track_001'] |
| g27 | -0.10 | EGO_PATH_ENTRY | B | A | B:e08 @ 4.00 | occupancy_evidence=returns; occupancy_margin_m=0.78; occupancy_sigma_m=0.25; cause=TARGET_LATERAL; geometry=estimated_body; source_track=track_002; aggregation=entity_state_union; source_tracks=['B:track_002'] |
| g28 | -0.05 | EGO_PATH_ENTRY | A | B | A:e08 @ 4.05 | occupancy_evidence=returns; occupancy_margin_m=0.57; occupancy_sigma_m=0.25; cause=TARGET_LATERAL; geometry=estimated_body; source_track=track_002; aggregation=entity_state_union; source_tracks=['A:track_002'] |
| g29 | 0.00 | COLLISION | - | A, B | A:e09 @ 4.10, B:e09 @ 4.10 | matched_event=collision_001; reference_event=True; peak_impulse=A 12137.59, B 12137.59 |
| g30 | 0.00 | CRITICAL_TTC_END | A | B | A:e10 @ 4.10 | source_track=track_002; aggregation=entity_state_union; source_tracks=['A:track_002'] |
| g31 | 0.00 | CRITICAL_TTC_END | B | A | B:e10 @ 4.10 | source_track=track_002; aggregation=entity_state_union; source_tracks=['B:track_002'] |
| g32 | 0.00 | CLOSING_END | A | B | A:e11 @ 4.10 | source_track=track_002; aggregation=entity_state_union; source_tracks=['A:track_002'] |
| g33 | 0.00 | CLOSING_END | B | A | B:e11 @ 4.10 | source_track=track_002; aggregation=entity_state_union; source_tracks=['B:track_002'] |
| g34 | 0.00 | TURN_LEFT_START | A | - | A:e12 @ 4.10 |  |
| g35 | 0.00 | TURN_RIGHT_START | B | - | B:e12 @ 4.10 |  |
| g36 | 0.05 | THROTTLE_END | A | - | A:e13 @ 4.15 |  |
| g37 | 0.05 | THROTTLE_END | B | - | B:e13 @ 4.15 |  |
| g38 | 0.05 | BRAKE_START | A | - | A:e14 @ 4.15 |  |
| g39 | 0.05 | BRAKE_START | B | - | B:e14 @ 4.15 |  |
| g40 | 0.10 | CLOSING_START | B | A | B:e15 @ 4.20, B:e20 @ 4.75 | source_track=track_002; aggregation=entity_state_union; source_tracks=['B:track_002'] |
| g41 | 0.15 | CLOSING_START | A | B | A:e15 @ 4.25, A:e16 @ 4.55 | source_track=track_002; aggregation=entity_state_union; source_tracks=['A:track_002'] |
| g42 | 0.40 | CLOSING_END | C | U1 | C:e13 @ 4.55 | source_track=track_002; aggregation=entity_state_union; source_tracks=['C:track_002'] |
| g43 | 0.40 | TRACK_LOST | C | A | C:e14 @ 4.55 | source_track=track_001; aggregation=entity_state_union; source_tracks=['C:track_001'] |
| g44 | 0.45 | CLOSING_END | A | B | A:e16 @ 4.55 | source_track=track_002; aggregation=entity_state_union; source_tracks=['A:track_002'] |
| g45 | 0.50 | CLOSING_END | B | C | B:e16 @ 4.60 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g46 | 0.50 | TURN_RIGHT_END | B | - | B:e17 @ 4.60 |  |
| g47 | 0.50 | MOVING_END | B | - | B:e18 @ 4.60 |  |
| g48 | 0.50 | STOP_START | B | - | B:e19 @ 4.60 |  |
| g49 | 0.60 | TURN_LEFT_END | A | - | A:e17 @ 4.70 |  |
| g50 | 0.65 | CLOSING_END | A | C | A:e18 @ 4.75 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g51 | 0.65 | CLOSING_END | B | A | B:e20 @ 4.75 | source_track=track_002; aggregation=entity_state_union; source_tracks=['B:track_002'] |
| g52 | 0.65 | MOVING_END | A | - | A:e19 @ 4.75 |  |
| g53 | 0.65 | STOP_START | A | - | A:e20 @ 4.75 |  |

## Edges

```
    g01 --PRECEDES--> g05
    g01 --PRECEDES--> g06
    g01 --PRECEDES--> g07
    g01 --PRECEDES--> g08
    g01 --PRECEDES--> g09
    g01 --PRECEDES--> g10
    g02 --PRECEDES--> g05
    g02 --PRECEDES--> g06
    g02 --PRECEDES--> g07
    g02 --PRECEDES--> g08
    g02 --PRECEDES--> g09
    g02 --PRECEDES--> g10
    g03 --PRECEDES--> g05
    g03 --PRECEDES--> g06
    g03 --PRECEDES--> g07
    g03 --PRECEDES--> g08
    g03 --PRECEDES--> g09
    g03 --PRECEDES--> g10
    g04 --PRECEDES--> g05
    g04 --PRECEDES--> g06
    g04 --PRECEDES--> g07
    g04 --PRECEDES--> g08
    g04 --PRECEDES--> g09
    g04 --PRECEDES--> g10
    g05 --PRECEDES--> g11
    g05 --PRECEDES--> g12
    g05 --PRECEDES--> g13
    g05 --PRECEDES--> g14
    g06 --PRECEDES--> g11
    g06 --PRECEDES--> g12
    g06 --PRECEDES--> g13
    g06 --PRECEDES--> g14
    g07 --PRECEDES--> g11
    g07 --PRECEDES--> g12
    g07 --PRECEDES--> g13
    g07 --PRECEDES--> g14
    g08 --PRECEDES--> g11
    g08 --PRECEDES--> g12
    g08 --PRECEDES--> g13
    g08 --PRECEDES--> g14
    g09 --PRECEDES--> g11
    g09 --PRECEDES--> g12
    g09 --PRECEDES--> g13
    g09 --PRECEDES--> g14
    g10 --PRECEDES--> g11
    g10 --PRECEDES--> g12
    g10 --PRECEDES--> g13
    g10 --PRECEDES--> g14
    g11 --PRECEDES--> g15
    g11 --PRECEDES--> g16
    g11 --PRECEDES--> g17
    g11 --PRECEDES--> g18
    g12 --PRECEDES--> g15
    g12 --PRECEDES--> g16
    g12 --PRECEDES--> g17
    g12 --PRECEDES--> g18
    g13 --PRECEDES--> g15
    g13 --PRECEDES--> g16
    g13 --PRECEDES--> g17
    g13 --PRECEDES--> g18
    g14 --PRECEDES--> g15
    g14 --PRECEDES--> g16
    g14 --PRECEDES--> g17
    g14 --PRECEDES--> g18
    g15 --PRECEDES--> g19
    g15 --PRECEDES--> g20
    g16 --PRECEDES--> g19
    g16 --PRECEDES--> g20
    g17 --PRECEDES--> g19
    g17 --PRECEDES--> g20
    g18 --PRECEDES--> g19
    g18 --PRECEDES--> g20
    g19 --PRECEDES--> g21
    g20 --PRECEDES--> g21
    g21 --PRECEDES--> g22
    g22 --PRECEDES--> g23
    g22 --PRECEDES--> g24
    g23 --PRECEDES--> g25
    g24 --PRECEDES--> g25
    g25 --PRECEDES--> g26
    g26 --PRECEDES--> g27
    g27 --PRECEDES--> g28
    g28 --PRECEDES--> g29
    g28 --PRECEDES--> g30
    g28 --PRECEDES--> g31
    g28 --PRECEDES--> g32
    g28 --PRECEDES--> g33
    g28 --PRECEDES--> g34
    g28 --PRECEDES--> g35
    g29 --PRECEDES--> g36
    g29 --PRECEDES--> g37
    g29 --PRECEDES--> g38
    g29 --PRECEDES--> g39
    g30 --PRECEDES--> g36
    g30 --PRECEDES--> g37
    g30 --PRECEDES--> g38
    g30 --PRECEDES--> g39
    g31 --PRECEDES--> g36
    g31 --PRECEDES--> g37
    g31 --PRECEDES--> g38
    g31 --PRECEDES--> g39
    g32 --PRECEDES--> g36
    g32 --PRECEDES--> g37
    g32 --PRECEDES--> g38
    g32 --PRECEDES--> g39
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
    g41 --PRECEDES--> g42
    g41 --PRECEDES--> g43
    g42 --PRECEDES--> g44
    g43 --PRECEDES--> g44
    g44 --PRECEDES--> g45
    g44 --PRECEDES--> g46
    g44 --PRECEDES--> g47
    g44 --PRECEDES--> g48
    g45 --PRECEDES--> g49
    g46 --PRECEDES--> g49
    g47 --PRECEDES--> g49
    g48 --PRECEDES--> g49
    g49 --PRECEDES--> g50
    g49 --PRECEDES--> g51
    g49 --PRECEDES--> g52
    g49 --PRECEDES--> g53
    g09 --SAME_TRACK--> g10
    g12 --SAME_TRACK--> g13
    g12 --SAME_TRACK--> g21
    g12 --SAME_TRACK--> g28
    g12 --SAME_TRACK--> g30
    g12 --SAME_TRACK--> g32
    g12 --SAME_TRACK--> g41
    g12 --SAME_TRACK--> g44
    g09 --SAME_TRACK--> g50
    g16 --SAME_TRACK--> g18
    g15 --SAME_TRACK--> g17
    g15 --SAME_TRACK--> g22
    g15 --SAME_TRACK--> g27
    g15 --SAME_TRACK--> g31
    g15 --SAME_TRACK--> g33
    g15 --SAME_TRACK--> g40
    g16 --SAME_TRACK--> g45
    g15 --SAME_TRACK--> g51
    g03 --SAME_TRACK--> g04
    g11 --SAME_TRACK--> g14
    g11 --SAME_TRACK--> g25
    g03 --SAME_TRACK--> g26
    g11 --SAME_TRACK--> g42
    g03 --SAME_TRACK--> g43
```

## Global trace

Events in one row are simultaneous at 0.05 s resolution: their order is unresolved.

| t_global | Events |
|---------:|--------|
| -4.15 | MOVING_START(C); THROTTLE_START(C); TRACK_APPEARED_FRONT(C,A); CLOSING_START(C,A) |
| -4.10 | MOVING_START(A); MOVING_START(B); THROTTLE_START(A); THROTTLE_START(B); TRACK_APPEARED_FRONT(A,C); CLOSING_START(A,C) |
| -2.05 | TRACK_APPEARED_LEFT(C,U1); TRACK_APPEARED_RIGHT(A,B); CLOSING_START(A,B); CLOSING_START(C,U1) |
| -2.00 | TRACK_APPEARED_LEFT(B,A); TRACK_APPEARED_RIGHT(B,C); CLOSING_START(B,A); CLOSING_START(B,C) |
| -1.80 | THROTTLE_END(C); BRAKE_START(C) |
| -1.55 | CRITICAL_TTC_START(A,B) |
| -1.50 | CRITICAL_TTC_START(B,A) |
| -1.25 | MOVING_END(C); STOP_START(C) |
| -0.25 | EGO_PATH_ENTRY(C,U1) |
| -0.20 | EGO_PATH_ENTRY(C,A) |
| -0.10 | EGO_PATH_ENTRY(B,A) |
| -0.05 | EGO_PATH_ENTRY(A,B) |
| +0.00 | COLLISION(A,B); CRITICAL_TTC_END(A,B); CRITICAL_TTC_END(B,A); CLOSING_END(A,B); CLOSING_END(B,A); TURN_LEFT_START(A); TURN_RIGHT_START(B) |
| +0.05 | THROTTLE_END(A); THROTTLE_END(B); BRAKE_START(A); BRAKE_START(B) |
| +0.10 | CLOSING_START(B,A) |
| +0.15 | CLOSING_START(A,B) |
| +0.40 | CLOSING_END(C,U1); TRACK_LOST(C,A) |
| +0.45 | CLOSING_END(A,B) |
| +0.50 | CLOSING_END(B,C); TURN_RIGHT_END(B); MOVING_END(B); STOP_START(B) |
| +0.60 | TURN_LEFT_END(A) |
| +0.65 | CLOSING_END(A,C); CLOSING_END(B,A); MOVING_END(A); STOP_START(A) |

## Temporal safety relations

Per track: does the cut-in start before the critical TTC, or was the critical TTC already active? Is the path entry before or after it? Temporal properties only, not causes.

- A's track_002 (B): CRITICAL_TTC_START 2.55, COLLISION with B 4.10 (+1.55 s); EGO_PATH_ENTRY 4.05 after critical TTC (+1.50 s) [local times; t_global: critical_ttc_start -1.55, ego_path_entry -0.05, collision +0.00]
- B's track_002 (A): CRITICAL_TTC_START 2.60, COLLISION with A 4.10 (+1.50 s); EGO_PATH_ENTRY 4.00 after critical TTC (+1.40 s) [local times; t_global: critical_ttc_start -1.50, ego_path_entry -0.10, collision +0.00]
- C's track_001 (A): EGO_PATH_ENTRY 3.95, no critical TTC [local times; t_global: ego_path_entry -0.20]
- C's track_002 (unidentified U1): EGO_PATH_ENTRY 3.90, no critical TTC [local times; t_global: ego_path_entry -0.25]

## Perceived state before each event, per observing recorder

Each recorder's own belief just before its events, in its own local names (track_001, ...): fusion does not rewrite it. True states are named, unknown ones end with `?`.

| t_global | Recorder | Events (local node) | Perceived state just before |
|---------:|----------|---------------------|-----------------------------|
| -4.15 | C | g01 MOVING_START(C) (C:e01)<br>g02 THROTTLE_START(C) (C:e02)<br>g03 TRACK_APPEARED_FRONT(C,A) (C:e03)<br>g04 CLOSING_START(C,A) (C:e04) | ego: not yet observed |
| -4.15 | C | g03 TRACK_APPEARED_FRONT(C,A) (C:e03)<br>g14 CLOSING_START(C,U1) (C:e06)<br>g42 CLOSING_END(C,U1) (C:e13)<br>g43 TRACK_LOST(C,A) (C:e14) | ego: not yet observed |
| -4.10 | A | g05 MOVING_START(A) (A:e01)<br>g07 THROTTLE_START(A) (A:e02)<br>g09 TRACK_APPEARED_FRONT(A,C) (A:e03)<br>g10 CLOSING_START(A,C) (A:e04) | ego: not yet observed |
| -4.10 | B | g06 MOVING_START(B) (B:e01)<br>g08 THROTTLE_START(B) (B:e02) | ego: not yet observed |
| -4.10 | A | g10 CLOSING_START(A,C) (A:e04)<br>g50 CLOSING_END(A,C) (A:e18)<br>g52 MOVING_END(A) (A:e19)<br>g53 STOP_START(A) (A:e20) | ego: not yet observed |
| -2.05 | C | g11 TRACK_APPEARED_LEFT(C,U1) (C:e05)<br>g14 CLOSING_START(C,U1) (C:e06) | ego: MOVING, THROTTLE<br>track_001: CLOSING |
| -2.05 | A | g12 TRACK_APPEARED_RIGHT(A,B) (A:e05)<br>g13 CLOSING_START(A,B) (A:e06) | ego: MOVING, THROTTLE<br>track_001: CLOSING |
| -2.05 | A | g13 CLOSING_START(A,B) (A:e06)<br>g21 CRITICAL_TTC_START(A,B) (A:e07)<br>g29 COLLISION(A,B) (A:e09)<br>g30 CRITICAL_TTC_END(A,B) (A:e10)<br>g32 CLOSING_END(A,B) (A:e11)<br>g34 TURN_LEFT_START(A) (A:e12) | ego: MOVING, THROTTLE<br>track_001: CLOSING |
| -2.00 | B | g15 TRACK_APPEARED_LEFT(B,A) (B:e03)<br>g16 TRACK_APPEARED_RIGHT(B,C) (B:e04)<br>g17 CLOSING_START(B,A) (B:e06)<br>g18 CLOSING_START(B,C) (B:e05) | ego: MOVING, THROTTLE |
| -2.00 | B | g17 CLOSING_START(B,A) (B:e06)<br>g22 CRITICAL_TTC_START(B,A) (B:e07)<br>g29 COLLISION(A,B) (B:e09)<br>g31 CRITICAL_TTC_END(B,A) (B:e10)<br>g33 CLOSING_END(B,A) (B:e11)<br>g35 TURN_RIGHT_START(B) (B:e12) | ego: MOVING, THROTTLE |
| -2.00 | B | g18 CLOSING_START(B,C) (B:e05)<br>g45 CLOSING_END(B,C) (B:e16)<br>g46 TURN_RIGHT_END(B) (B:e17)<br>g47 MOVING_END(B) (B:e18)<br>g48 STOP_START(B) (B:e19) | ego: MOVING, THROTTLE |
| -1.80 | C | g19 THROTTLE_END(C) (C:e07)<br>g20 BRAKE_START(C) (C:e08) | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>track_002: CLOSING, CRITICAL_TTC? |
| -1.55 | A | g21 CRITICAL_TTC_START(A,B) (A:e07) | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>track_002: CLOSING, CRITICAL_TTC? |
| -1.50 | B | g22 CRITICAL_TTC_START(B,A) (B:e07) | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC?<br>track_002: CLOSING, CRITICAL_TTC? |
| -1.25 | C | g23 MOVING_END(C) (C:e09)<br>g24 STOP_START(C) (C:e10) | ego: MOVING, BRAKE<br>track_001: CLOSING<br>track_002: CLOSING |
| -0.25 | C | g25 EGO_PATH_ENTRY(C,U1) (C:e11) | ego: STOP, BRAKE<br>track_001: CLOSING<br>track_002: CLOSING |
| -0.20 | C | g26 EGO_PATH_ENTRY(C,A) (C:e12) | ego: STOP, BRAKE<br>track_001: CLOSING<br>track_002: CLOSING, IN_EGO_PATH |
| -0.10 | B | g27 EGO_PATH_ENTRY(B,A) (B:e08) | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>track_002: CLOSING, CRITICAL_TTC |
| -0.05 | A | g28 EGO_PATH_ENTRY(A,B) (A:e08) | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>track_002: CLOSING, CRITICAL_TTC |
| +0.05 | A | g36 THROTTLE_END(A) (A:e13)<br>g38 BRAKE_START(A) (A:e14) | ego: MOVING, THROTTLE, TURN_LEFT<br>track_001: CLOSING<br>track_002: IN_EGO_PATH |
| +0.05 | B | g37 THROTTLE_END(B) (B:e13)<br>g39 BRAKE_START(B) (B:e14) | ego: MOVING, THROTTLE, TURN_RIGHT<br>track_001: CLOSING<br>track_002: IN_EGO_PATH |
| +0.10 | B | g40 CLOSING_START(B,A) (B:e15) | ego: MOVING, BRAKE, TURN_RIGHT<br>track_001: CLOSING<br>track_002: IN_EGO_PATH |
| +0.10 | B | g40 CLOSING_START(B,A) (B:e15)<br>g51 CLOSING_END(B,A) (B:e20) | ego: MOVING, BRAKE, TURN_RIGHT<br>track_001: CLOSING<br>track_002: IN_EGO_PATH |
| +0.15 | A | g41 CLOSING_START(A,B) (A:e15) | ego: MOVING, BRAKE, TURN_LEFT<br>track_001: CLOSING<br>track_002: IN_EGO_PATH |
| +0.15 | A | g41 CLOSING_START(A,B) (A:e15)<br>g44 CLOSING_END(A,B) (A:e16) | ego: MOVING, BRAKE, TURN_LEFT<br>track_001: CLOSING<br>track_002: IN_EGO_PATH |
| +0.60 | A | g49 TURN_LEFT_END(A) (A:e17) | ego: MOVING, BRAKE, TURN_LEFT<br>track_001: CLOSING<br>track_002: IN_EGO_PATH |

## Plain-language reading

- 4.15 s before the reference collision, C started moving (already the case when first observed).
- 4.15 s before the reference collision, C pressed the accelerator (already the case when first observed).
- 4.15 s before the reference collision, C's radar started tracking A, which appeared in front of it.
- 4.15 s before the reference collision, C observed A start closing in (already the case when first observed).
- 4.10 s before the reference collision, A started moving (already the case when first observed).
- 4.10 s before the reference collision, B started moving (already the case when first observed).
- 4.10 s before the reference collision, A pressed the accelerator (already the case when first observed).
- 4.10 s before the reference collision, B pressed the accelerator (already the case when first observed).
- 4.10 s before the reference collision, A's radar started tracking C, which appeared in front of it.
- 4.10 s before the reference collision, A observed C start closing in (already the case when first observed).
- 2.05 s before the reference collision, C's radar started tracking anonymous road user U1, which appeared on its left.
- 2.05 s before the reference collision, A's radar started tracking B, which appeared on its right.
- 2.05 s before the reference collision, A observed B start closing in (already the case when first observed).
- 2.05 s before the reference collision, C observed anonymous road user U1 start closing in (already the case when first observed).
- 2.00 s before the reference collision, B's radar started tracking A, which appeared on its left.
- 2.00 s before the reference collision, B's radar started tracking C, which appeared on its right.
- 2.00 s before the reference collision, B observed A start closing in (already the case when first observed).
- 2.00 s before the reference collision, B observed C start closing in (already the case when first observed).
- 1.80 s before the reference collision, C released the accelerator.
- 1.80 s before the reference collision, C started braking.
- 1.55 s before the reference collision, A's time-to-contact with B became critical.
- 1.50 s before the reference collision, B's time-to-contact with A became critical.
- 1.25 s before the reference collision, C stopped moving.
- 1.25 s before the reference collision, C came to a stop.
- 0.25 s before the reference collision, C observed anonymous road user U1 enter its forward path corridor.
- 0.20 s before the reference collision, C observed A enter its forward path corridor.
- 0.10 s before the reference collision, B observed A enter its forward path corridor.
- 0.05 s before the reference collision, A observed B enter its forward path corridor.
- At the reference collision, A and B both recorded this same collision (peak impulses A: 12138, B: 12138 N*s).
- At the reference collision, A's time-to-contact with B stopped being critical.
- At the reference collision, B's time-to-contact with A stopped being critical.
- At the reference collision, A observed B stop closing in.
- At the reference collision, B observed A stop closing in.
- At the reference collision, A started turning left.
- At the reference collision, B started turning right.
- 0.05 s after the reference collision, A released the accelerator.
- 0.05 s after the reference collision, B released the accelerator.
- 0.05 s after the reference collision, A started braking.
- 0.05 s after the reference collision, B started braking.
- 0.10 s after the reference collision, B observed A start closing in.
- 0.15 s after the reference collision, A observed B start closing in.
- 0.40 s after the reference collision, C observed anonymous road user U1 stop closing in.
- 0.40 s after the reference collision, C's radar lost A (its states are UNKNOWN from then on, not ended).
- 0.45 s after the reference collision, A observed B stop closing in.
- 0.50 s after the reference collision, B observed C stop closing in.
- 0.50 s after the reference collision, B stopped turning right.
- 0.50 s after the reference collision, B stopped moving.
- 0.50 s after the reference collision, B came to a stop.
- 0.60 s after the reference collision, A stopped turning left.
- 0.65 s after the reference collision, A observed C stop closing in.
- 0.65 s after the reference collision, B observed A stop closing in.
- 0.65 s after the reference collision, A stopped moving.
- 0.65 s after the reference collision, A came to a stop.
