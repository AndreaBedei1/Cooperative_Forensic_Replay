# Global graph - S10/run_0_deflected_into_c

Global time `t_global` is 0 at the reference collision. The local graphs were not modified: every node lists the local node(s) and local time(s) it comes from.

Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.

## Entities

| Entity | Kind | Details |
|--------|------|---------|
| A | recorder | clock ALIGNED; observed by others as: B:track_002, C:track_001 |
| B | recorder | clock ALIGNED; observed by others as: A:track_002, C:track_002 |
| C | recorder | clock ALIGNED; observed by others as: A:track_001, B:track_001 |

## Graph alignment

Reference event: `collision_001` (t_global = 0); `t_global = t_local + offset_to_global`. A graph that did not report it is aligned through the chain of matched collisions linking it to the reference (multi-hop); its anchor is its own report of the last collision of that chain.

| Graph | Status | Anchor node | Anchor local time | Offset to global | Note |
|-------|--------|-------------|------------------:|-----------------:|------|
| A | ALIGNED | A:e09 | 3.80 | -3.80 | reported the reference collision collision_001 |
| B | ALIGNED | B:e15 | 3.80 | -3.80 | reported the reference collision collision_001 |
| C | ALIGNED | C:e09 | 4.70 | -3.80 | shares collision_002 with A, aligned through collision_001 -> collision_002 |

Estimated relative clock offsets: B - A = +0.000 s, C - A = +0.000 s, C - B = +0.000 s

Matched `collision_001`: A and B both recorded a collision; peak impulses 10358.22 vs 10358.22 N*s (similarity 1.000, tolerance 0.10); no competing report within tolerance; the two bodies touch at their reports (0.00 m apart, tolerance 1.0 m); independent relative impulse std 0.100; combined z 0.000 (gate 3.0); engineering assumption; pre-contact radar view of each recorder checked against the candidate partner's own speed: not contradicted

Matched `collision_002`: A and C both recorded a collision; peak impulses 2250.28 vs 2250.28 N*s (similarity 1.000, tolerance 0.10); no competing report within tolerance; the two bodies touch at their reports (0.00 m apart, tolerance 1.0 m); independent relative impulse std 0.100; combined z 0.000 (gate 3.0); engineering assumption; pre-contact radar view of each recorder checked against the candidate partner's own speed: not contradicted

## Identity associations

| Local track | Global entity | Status | Confidence | Evidence |
|-------------|---------------|--------|-----------:|----------|
| A:track_001 | C | ASSOCIATED | 1.00 | A and C both reported collision_002 at 4.70 s (peak impulse 2250.28 vs 2250.28 N*s)<br>tracked for 4.70 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 11.0 m -> 0.0 m over the last 1.0 s<br>track motion compatible with C's own speed in the observed direction (3 sigma; full-speed RMSE 0.13 m/s for reference)<br>clearance at the contact 0.00 m<br>the only track of A compatible with the contact<br>collision_001 with B at 3.80 s: not compatible (track motion contradicts B's own speed in the observed direction (3 sigma; full-speed RMSE 3.70 m/s for reference)) |
| A:track_002 | B | ASSOCIATED | 0.91 | A and B both reported collision_001 at 3.80 s (peak impulse 10358.22 vs 10358.22 N*s)<br>tracked for 1.75 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 15.5 m -> 1.1 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 0.65 m/s for reference)<br>clearance at the contact 0.82 m<br>the only track of A compatible with the contact<br>collision_002 with C at 4.70 s: not compatible (not approaching before the contact: clearance 1.3 m -> 1.4 m over the last 1.0 s) |
| B:track_001 | C | ASSOCIATED | 1.00 | B and A both reported collision_001 (peak impulse 10358.22 vs 10358.22 N*s)<br>tracked for 2.10 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 14.4 m -> 9.5 m over the last 1.0 s<br>track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 5.00 m/s for reference)<br>clearance at the contact 9.51 m (beyond 3.50 m: confidence factor 0.13)<br>common frame: its returns lie on C's own footprint (median 0.00 m, 0.00 sigma of the relative uncertainty, over 60 samples; 100% within 3 sigma) at C's own velocity |
| B:track_002 | A | ASSOCIATED | 0.94 | B and A both reported collision_001 (peak impulse 10358.22 vs 10358.22 N*s)<br>tracked for 1.80 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 16.6 m -> 1.5 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 0.52 m/s for reference)<br>clearance at the contact 1.46 m<br>the only track of B compatible with the contact |
| C:track_001 | A | ASSOCIATED | 0.95 | C and A both reported collision_002 (peak impulse 2250.28 vs 2250.28 N*s)<br>tracked for 4.70 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 11.3 m -> 0.0 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 0.48 m/s for reference)<br>clearance at the contact 0.00 m<br>the only track of C compatible with the contact |
| C:track_002 | B | ASSOCIATED | 1.00 | C and A both reported collision_002 (peak impulse 2250.28 vs 2250.28 N*s)<br>tracked for 4.55 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 9.3 m -> 5.0 m over the last 1.0 s<br>track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 3.78 m/s for reference)<br>clearance at the contact 4.95 m (beyond 3.50 m: confidence factor 0.89)<br>common frame: its returns lie on B's own footprint (median 0.00 m, 0.00 sigma of the relative uncertainty, over 72 samples; 100% within 3 sigma) at B's own velocity |

## Nodes

| Id | Global time | Type | Actor | Subject / participants | Observed by (local node @ local time) | Details |
|----|------------:|------|-------|------------------------|----------------------------------------|---------|
| g01 | -3.80 | MOVING_START | A | - | A:e01 @ 0.00 | active_at_first_observation=True |
| g02 | -3.80 | MOVING_START | B | - | B:e01 @ 0.00 | active_at_first_observation=True |
| g03 | -3.80 | MOVING_START | C | - | C:e01 @ 0.00 | active_at_first_observation=True |
| g04 | -3.80 | THROTTLE_START | A | - | A:e02 @ 0.00 | active_at_first_observation=True |
| g05 | -3.80 | THROTTLE_START | B | - | B:e02 @ 0.00 | active_at_first_observation=True |
| g06 | -3.80 | THROTTLE_START | C | - | C:e02 @ 0.00 | active_at_first_observation=True |
| g07 | -3.80 | TRACK_APPEARED_FRONT | A | C | A:e03 @ 0.00 | initial_in_ego_path=False; source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g08 | -3.80 | TRACK_APPEARED_FRONT | C | A | C:e03 @ 0.00 | initial_in_ego_path=False; source_track=track_001; aggregation=entity_state_union; source_tracks=['C:track_001'] |
| g09 | -3.80 | CLOSING_START | A | C | A:e04 @ 0.00, A:e14 @ 4.65 | active_at_first_observation=True; source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g10 | -3.80 | CLOSING_START | C | A | C:e04 @ 0.00, C:e11 @ 4.70 | active_at_first_observation=True; source_track=track_001; aggregation=entity_state_union; source_tracks=['C:track_001'] |
| g11 | -3.65 | TRACK_APPEARED_LEFT | C | B | C:e05 @ 0.15 | initial_in_ego_path=False; source_track=track_002; aggregation=entity_state_union; source_tracks=['C:track_002'] |
| g12 | -3.65 | CLOSING_START | C | B | C:e06 @ 0.15, C:e14 @ 5.05 | active_at_first_observation=True; source_track=track_002; aggregation=entity_state_union; source_tracks=['C:track_002'] |
| g13 | -2.70 | STOP_SIGN_DETECTED_START | B | B:sign-0 | B:e03 @ 1.10 | relevant_to_ego_path=True |
| g14 | -2.10 | TRACK_APPEARED_RIGHT | B | C | B:e04 @ 1.70 | initial_in_ego_path=False; source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g15 | -2.10 | CLOSING_START | B | C | B:e05 @ 1.70, B:e24 @ 5.00 | active_at_first_observation=True; source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g16 | -1.80 | TRACK_APPEARED_LEFT | B | A | B:e06 @ 2.00 | initial_in_ego_path=True; source_track=track_002; aggregation=entity_state_union; source_tracks=['B:track_002'] |
| g17 | -1.80 | CLOSING_START | B | A | B:e07 @ 2.00, B:e21 @ 4.15 | active_at_first_observation=True; source_track=track_002; aggregation=entity_state_union; source_tracks=['B:track_002'] |
| g18 | -1.75 | TRACK_APPEARED_RIGHT | A | B | A:e05 @ 2.05 | initial_in_ego_path=False; source_track=track_002; aggregation=entity_state_union; source_tracks=['A:track_002'] |
| g19 | -1.75 | CLOSING_START | A | B | A:e06 @ 2.05, A:e11 @ 3.80 | active_at_first_observation=True; source_track=track_002; aggregation=entity_state_union; source_tracks=['A:track_002'] |
| g20 | -1.50 | STOP_SIGN_DETECTED_END | B | B:sign-0 | B:e08 @ 2.30 |  |
| g21 | -1.50 | TURN_LEFT_START | B | - | B:e09 @ 2.30 |  |
| g22 | -1.30 | CRITICAL_TTC_START | B | A | B:e10 @ 2.50, B:e22 @ 4.60 | source_track=track_002; aggregation=entity_state_union; source_tracks=['B:track_002'] |
| g23 | -1.25 | CRITICAL_TTC_START | A | B | A:e07 @ 2.55, A:e10 @ 3.80 | source_track=track_002; aggregation=entity_state_union; source_tracks=['A:track_002'] |
| g24 | -0.85 | THROTTLE_END | B | - | B:e11 @ 2.95 |  |
| g25 | -0.85 | BRAKE_START | B | - | B:e12 @ 2.95 |  |
| g26 | -0.30 | BRAKE_END | B | - | B:e13 @ 3.50 |  |
| g27 | -0.15 | THROTTLE_START | B | - | B:e14 @ 3.65 |  |
| g28 | -0.15 | CRITICAL_TTC_START | C | A | C:e07 @ 3.65, C:e10 @ 4.70 | source_track=track_001; aggregation=entity_state_union; source_tracks=['C:track_001'] |
| g29 | -0.05 | CRITICAL_TTC_START | A | C | A:e08 @ 3.75, A:e16 @ 4.70 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g30 | 0.00 | COLLISION | - | A, B | A:e09 @ 3.80, B:e15 @ 3.80 | matched_event=collision_001; reference_event=True; peak_impulse=A 10358.22, B 10358.22 |
| g31 | 0.00 | CRITICAL_TTC_END | A | B | A:e10 @ 3.80 | source_track=track_002; aggregation=entity_state_union; source_tracks=['A:track_002'] |
| g32 | 0.00 | CRITICAL_TTC_END | B | A | B:e15 @ 3.80 | closed_by_contact=collision_001 |
| g33 | 0.00 | CLOSING_END | A | B | A:e11 @ 3.80 | source_track=track_002; aggregation=entity_state_union; source_tracks=['A:track_002'] |
| g34 | 0.00 | TURN_LEFT_END | B | - | B:e16 @ 3.80 |  |
| g35 | 0.05 | THROTTLE_END | A | - | A:e12 @ 3.85 |  |
| g36 | 0.05 | THROTTLE_END | B | - | B:e17 @ 3.85 |  |
| g37 | 0.05 | BRAKE_START | B | - | B:e18 @ 3.85 |  |
| g38 | 0.05 | TURN_LEFT_START | A | - | A:e13 @ 3.85 |  |
| g39 | 0.20 | MOVING_END | B | - | B:e19 @ 4.00 |  |
| g40 | 0.20 | STOP_START | B | - | B:e20 @ 4.00 |  |
| g41 | 0.35 | CLOSING_END | B | A | B:e21 @ 4.15 | source_track=track_002; aggregation=entity_state_union; source_tracks=['B:track_002'] |
| g42 | 0.40 | EGO_PATH_ENTRY | C | A | C:e08 @ 4.20 | occupancy_evidence=box; occupancy_margin_m=0.48; occupancy_sigma_m=0.27; cause=TARGET_LATERAL; geometry=estimated_body; source_track=track_001; aggregation=entity_state_union; source_tracks=['C:track_001'] |
| g43 | 0.85 | CLOSING_END | A | C | A:e14 @ 4.65 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g44 | 0.90 | COLLISION | - | A, C | A:e15 @ 4.70, C:e09 @ 4.70 | matched_event=collision_002; reference_event=False; peak_impulse=A 2250.28, C 2250.28 |
| g45 | 0.90 | CRITICAL_TTC_END | A | C | A:e16 @ 4.70 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g46 | 0.90 | CRITICAL_TTC_END | C | A | C:e10 @ 4.70 | source_track=track_001; aggregation=entity_state_union; source_tracks=['C:track_001'] |
| g47 | 0.90 | CLOSING_END | C | A | C:e11 @ 4.70 | source_track=track_001; aggregation=entity_state_union; source_tracks=['C:track_001'] |
| g48 | 0.95 | THROTTLE_END | C | - | C:e12 @ 4.75 |  |
| g49 | 0.95 | BRAKE_START | C | - | C:e13 @ 4.75 |  |
| g50 | 1.05 | EGO_PATH_EXIT | B | A | B:e23 @ 4.85 | occupancy_evidence=returns; occupancy_margin_m=-0.47; occupancy_sigma_m=0.25; cause=TARGET_LATERAL; geometry=estimated_body; source_track=track_002; aggregation=entity_state_union; source_tracks=['B:track_002'] |
| g51 | 1.20 | CLOSING_END | B | C | B:e24 @ 5.00 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g52 | 1.25 | CLOSING_END | C | B | C:e14 @ 5.05 | source_track=track_002; aggregation=entity_state_union; source_tracks=['C:track_002'] |
| g53 | 1.30 | MOVING_END | C | - | C:e15 @ 5.10 |  |
| g54 | 1.30 | STOP_START | C | - | C:e16 @ 5.10 |  |
| g55 | 1.35 | TURN_LEFT_END | A | - | A:e17 @ 5.15 |  |
| g56 | 1.45 | MOVING_END | A | - | A:e18 @ 5.25 |  |
| g57 | 1.45 | STOP_START | A | - | A:e19 @ 5.25 |  |

## Edges

```
    g01 --PRECEDES--> g11
    g01 --PRECEDES--> g12
    g02 --PRECEDES--> g11
    g02 --PRECEDES--> g12
    g03 --PRECEDES--> g11
    g03 --PRECEDES--> g12
    g04 --PRECEDES--> g11
    g04 --PRECEDES--> g12
    g05 --PRECEDES--> g11
    g05 --PRECEDES--> g12
    g06 --PRECEDES--> g11
    g06 --PRECEDES--> g12
    g07 --PRECEDES--> g11
    g07 --PRECEDES--> g12
    g08 --PRECEDES--> g11
    g08 --PRECEDES--> g12
    g09 --PRECEDES--> g11
    g09 --PRECEDES--> g12
    g10 --PRECEDES--> g11
    g10 --PRECEDES--> g12
    g11 --PRECEDES--> g13
    g12 --PRECEDES--> g13
    g13 --PRECEDES--> g14
    g13 --PRECEDES--> g15
    g14 --PRECEDES--> g16
    g14 --PRECEDES--> g17
    g15 --PRECEDES--> g16
    g15 --PRECEDES--> g17
    g16 --PRECEDES--> g18
    g16 --PRECEDES--> g19
    g17 --PRECEDES--> g18
    g17 --PRECEDES--> g19
    g18 --PRECEDES--> g20
    g18 --PRECEDES--> g21
    g19 --PRECEDES--> g20
    g19 --PRECEDES--> g21
    g20 --PRECEDES--> g22
    g21 --PRECEDES--> g22
    g22 --PRECEDES--> g23
    g23 --PRECEDES--> g24
    g23 --PRECEDES--> g25
    g24 --PRECEDES--> g26
    g25 --PRECEDES--> g26
    g26 --PRECEDES--> g27
    g26 --PRECEDES--> g28
    g27 --PRECEDES--> g29
    g28 --PRECEDES--> g29
    g29 --PRECEDES--> g30
    g29 --PRECEDES--> g31
    g29 --PRECEDES--> g32
    g29 --PRECEDES--> g33
    g29 --PRECEDES--> g34
    g30 --PRECEDES--> g35
    g30 --PRECEDES--> g36
    g30 --PRECEDES--> g37
    g30 --PRECEDES--> g38
    g31 --PRECEDES--> g35
    g31 --PRECEDES--> g36
    g31 --PRECEDES--> g37
    g31 --PRECEDES--> g38
    g32 --PRECEDES--> g35
    g32 --PRECEDES--> g36
    g32 --PRECEDES--> g37
    g32 --PRECEDES--> g38
    g33 --PRECEDES--> g35
    g33 --PRECEDES--> g36
    g33 --PRECEDES--> g37
    g33 --PRECEDES--> g38
    g34 --PRECEDES--> g35
    g34 --PRECEDES--> g36
    g34 --PRECEDES--> g37
    g34 --PRECEDES--> g38
    g35 --PRECEDES--> g39
    g35 --PRECEDES--> g40
    g36 --PRECEDES--> g39
    g36 --PRECEDES--> g40
    g37 --PRECEDES--> g39
    g37 --PRECEDES--> g40
    g38 --PRECEDES--> g39
    g38 --PRECEDES--> g40
    g39 --PRECEDES--> g41
    g40 --PRECEDES--> g41
    g41 --PRECEDES--> g42
    g42 --PRECEDES--> g43
    g43 --PRECEDES--> g44
    g43 --PRECEDES--> g45
    g43 --PRECEDES--> g46
    g43 --PRECEDES--> g47
    g44 --PRECEDES--> g48
    g44 --PRECEDES--> g49
    g45 --PRECEDES--> g48
    g45 --PRECEDES--> g49
    g46 --PRECEDES--> g48
    g46 --PRECEDES--> g49
    g47 --PRECEDES--> g48
    g47 --PRECEDES--> g49
    g48 --PRECEDES--> g50
    g49 --PRECEDES--> g50
    g50 --PRECEDES--> g51
    g51 --PRECEDES--> g52
    g52 --PRECEDES--> g53
    g52 --PRECEDES--> g54
    g53 --PRECEDES--> g55
    g54 --PRECEDES--> g55
    g55 --PRECEDES--> g56
    g55 --PRECEDES--> g57
    g07 --SAME_TRACK--> g09
    g18 --SAME_TRACK--> g19
    g18 --SAME_TRACK--> g23
    g07 --SAME_TRACK--> g29
    g18 --SAME_TRACK--> g31
    g18 --SAME_TRACK--> g33
    g07 --SAME_TRACK--> g43
    g07 --SAME_TRACK--> g45
    g14 --SAME_TRACK--> g15
    g16 --SAME_TRACK--> g17
    g16 --SAME_TRACK--> g22
    g16 --SAME_TRACK--> g41
    g16 --SAME_TRACK--> g50
    g14 --SAME_TRACK--> g51
    g08 --SAME_TRACK--> g10
    g11 --SAME_TRACK--> g12
    g08 --SAME_TRACK--> g28
    g08 --SAME_TRACK--> g42
    g08 --SAME_TRACK--> g46
    g08 --SAME_TRACK--> g47
    g11 --SAME_TRACK--> g52
```

## Global trace

Events in one row are simultaneous at 0.05 s resolution: their order is unresolved.

| t_global | Events |
|---------:|--------|
| -3.80 | MOVING_START(A); MOVING_START(B); MOVING_START(C); THROTTLE_START(A); THROTTLE_START(B); THROTTLE_START(C); TRACK_APPEARED_FRONT(A,C); TRACK_APPEARED_FRONT(C,A); CLOSING_START(A,C); CLOSING_START(C,A) |
| -3.65 | TRACK_APPEARED_LEFT(C,B); CLOSING_START(C,B) |
| -2.70 | STOP_SIGN_DETECTED_START(B,B:sign-0) |
| -2.10 | TRACK_APPEARED_RIGHT(B,C); CLOSING_START(B,C) |
| -1.80 | TRACK_APPEARED_LEFT(B,A); CLOSING_START(B,A) |
| -1.75 | TRACK_APPEARED_RIGHT(A,B); CLOSING_START(A,B) |
| -1.50 | STOP_SIGN_DETECTED_END(B,B:sign-0); TURN_LEFT_START(B) |
| -1.30 | CRITICAL_TTC_START(B,A) |
| -1.25 | CRITICAL_TTC_START(A,B) |
| -0.85 | THROTTLE_END(B); BRAKE_START(B) |
| -0.30 | BRAKE_END(B) |
| -0.15 | THROTTLE_START(B); CRITICAL_TTC_START(C,A) |
| -0.05 | CRITICAL_TTC_START(A,C) |
| +0.00 | COLLISION(A,B); CRITICAL_TTC_END(A,B); CRITICAL_TTC_END(B,A); CLOSING_END(A,B); TURN_LEFT_END(B) |
| +0.05 | THROTTLE_END(A); THROTTLE_END(B); BRAKE_START(B); TURN_LEFT_START(A) |
| +0.20 | MOVING_END(B); STOP_START(B) |
| +0.35 | CLOSING_END(B,A) |
| +0.40 | EGO_PATH_ENTRY(C,A) |
| +0.85 | CLOSING_END(A,C) |
| +0.90 | COLLISION(A,C); CRITICAL_TTC_END(A,C); CRITICAL_TTC_END(C,A); CLOSING_END(C,A) |
| +0.95 | THROTTLE_END(C); BRAKE_START(C) |
| +1.05 | EGO_PATH_EXIT(B,A) |
| +1.20 | CLOSING_END(B,C) |
| +1.25 | CLOSING_END(C,B) |
| +1.30 | MOVING_END(C); STOP_START(C) |
| +1.35 | TURN_LEFT_END(A) |
| +1.45 | MOVING_END(A); STOP_START(A) |

## Temporal safety relations

Per track: does the cut-in start before the critical TTC, or was the critical TTC already active? Is the path entry before or after it? Temporal properties only, not causes.

- A's track_001 (C): CRITICAL_TTC_START 3.75, COLLISION with C 4.70 (+0.95 s) [local times; t_global: critical_ttc_start -0.05, collision +0.90]
- A's track_002 (B): CRITICAL_TTC_START 2.55, COLLISION with B 3.80 (+1.25 s) [local times; t_global: critical_ttc_start -1.25, collision +0.00]
- B's track_002 (A): CRITICAL_TTC_START 2.50, COLLISION with A 3.80 (+1.30 s) [local times; t_global: critical_ttc_start -1.30, collision +0.00]
- C's track_001 (A): CRITICAL_TTC_START 3.65, COLLISION with A 4.70 (+1.05 s); EGO_PATH_ENTRY 4.20 after critical TTC (+0.55 s) [local times; t_global: critical_ttc_start -0.15, ego_path_entry +0.40, collision +0.90]

## Perceived state before each event, per observing recorder

Each recorder's own belief just before its events, in its own local names (track_001, ...): fusion does not rewrite it. True states are named, unknown ones end with `?`.

| t_global | Recorder | Events (local node) | Perceived state just before |
|---------:|----------|---------------------|-----------------------------|
| -3.80 | A | g01 MOVING_START(A) (A:e01)<br>g04 THROTTLE_START(A) (A:e02)<br>g07 TRACK_APPEARED_FRONT(A,C) (A:e03)<br>g09 CLOSING_START(A,C) (A:e04) | ego: not yet observed |
| -3.80 | B | g02 MOVING_START(B) (B:e01)<br>g05 THROTTLE_START(B) (B:e02) | ego: not yet observed |
| -3.80 | C | g03 MOVING_START(C) (C:e01)<br>g06 THROTTLE_START(C) (C:e02)<br>g08 TRACK_APPEARED_FRONT(C,A) (C:e03)<br>g10 CLOSING_START(C,A) (C:e04) | ego: not yet observed |
| -3.80 | A | g09 CLOSING_START(A,C) (A:e04)<br>g43 CLOSING_END(A,C) (A:e14) | ego: not yet observed |
| -3.80 | C | g10 CLOSING_START(C,A) (C:e04)<br>g28 CRITICAL_TTC_START(C,A) (C:e07)<br>g44 COLLISION(A,C) (C:e09)<br>g46 CRITICAL_TTC_END(C,A) (C:e10)<br>g47 CLOSING_END(C,A) (C:e11) | ego: not yet observed |
| -3.65 | C | g11 TRACK_APPEARED_LEFT(C,B) (C:e05)<br>g12 CLOSING_START(C,B) (C:e06) | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC? |
| -3.65 | C | g12 CLOSING_START(C,B) (C:e06)<br>g52 CLOSING_END(C,B) (C:e14) | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC? |
| -2.70 | B | g13 STOP_SIGN_DETECTED_START(B,B:sign-0) (B:e03) | ego: MOVING, THROTTLE |
| -2.10 | B | g14 TRACK_APPEARED_RIGHT(B,C) (B:e04)<br>g15 CLOSING_START(B,C) (B:e05) | ego: MOVING, THROTTLE<br>sign-0: STOP sign known, relevant to the path |
| -2.10 | B | g15 CLOSING_START(B,C) (B:e05)<br>g51 CLOSING_END(B,C) (B:e24) | ego: MOVING, THROTTLE<br>sign-0: STOP sign known, relevant to the path |
| -1.80 | B | g16 TRACK_APPEARED_LEFT(B,A) (B:e06)<br>g17 CLOSING_START(B,A) (B:e07) | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC?<br>sign-0: STOP sign known, relevant to the path |
| -1.80 | B | g17 CLOSING_START(B,A) (B:e07)<br>g41 CLOSING_END(B,A) (B:e21) | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC?<br>sign-0: STOP sign known, relevant to the path |
| -1.75 | A | g18 TRACK_APPEARED_RIGHT(A,B) (A:e05)<br>g19 CLOSING_START(A,B) (A:e06) | ego: MOVING, THROTTLE<br>track_001: CLOSING |
| -1.75 | A | g19 CLOSING_START(A,B) (A:e06)<br>g23 CRITICAL_TTC_START(A,B) (A:e07)<br>g30 COLLISION(A,B) (A:e09)<br>g31 CRITICAL_TTC_END(A,B) (A:e10)<br>g33 CLOSING_END(A,B) (A:e11) | ego: MOVING, THROTTLE<br>track_001: CLOSING |
| -1.50 | B | g20 STOP_SIGN_DETECTED_END(B,B:sign-0) (B:e08)<br>g21 TURN_LEFT_START(B) (B:e09) | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>track_002: CLOSING, IN_EGO_PATH, CRITICAL_TTC?<br>sign-0: STOP sign known, relevant to the path |
| -1.30 | B | g22 CRITICAL_TTC_START(B,A) (B:e10) | ego: MOVING, THROTTLE, TURN_LEFT<br>track_001: CLOSING<br>track_002: CLOSING, IN_EGO_PATH, CRITICAL_TTC?<br>sign-0: STOP sign known, relevant to the path |
| -1.30 | B | g22 CRITICAL_TTC_START(B,A) (B:e10) | ego: MOVING, THROTTLE, TURN_LEFT<br>track_001: CLOSING<br>track_002: CLOSING, IN_EGO_PATH, CRITICAL_TTC?<br>sign-0: STOP sign known, relevant to the path |
| -1.25 | A | g23 CRITICAL_TTC_START(A,B) (A:e07) | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>track_002: CLOSING, CRITICAL_TTC? |
| -0.85 | B | g24 THROTTLE_END(B) (B:e11)<br>g25 BRAKE_START(B) (B:e12) | ego: MOVING, THROTTLE, TURN_LEFT<br>track_001: CLOSING<br>track_002: CLOSING, CRITICAL_TTC, IN_EGO_PATH<br>sign-0: STOP sign known, relevant to the path |
| -0.30 | B | g26 BRAKE_END(B) (B:e13) | ego: MOVING, BRAKE, TURN_LEFT<br>track_001: CLOSING<br>track_002: CLOSING, CRITICAL_TTC, IN_EGO_PATH<br>sign-0: STOP sign known, relevant to the path |
| -0.15 | B | g27 THROTTLE_START(B) (B:e14) | ego: MOVING, TURN_LEFT<br>track_001: CLOSING<br>track_002: CLOSING, CRITICAL_TTC, IN_EGO_PATH<br>sign-0: STOP sign known, relevant to the path |
| -0.15 | C | g28 CRITICAL_TTC_START(C,A) (C:e07) | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>track_002: CLOSING |
| -0.05 | A | g29 CRITICAL_TTC_START(A,C) (A:e08) | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>track_002: CLOSING, CRITICAL_TTC |
| -0.05 | A | g29 CRITICAL_TTC_START(A,C) (A:e08)<br>g44 COLLISION(A,C) (A:e15)<br>g45 CRITICAL_TTC_END(A,C) (A:e16) | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>track_002: CLOSING, CRITICAL_TTC |
| +0.00 | B | g30 COLLISION(A,B) (B:e15)<br>g32 CRITICAL_TTC_END(B,A) (B:e15)<br>g34 TURN_LEFT_END(B) (B:e16) | ego: MOVING, THROTTLE, TURN_LEFT<br>track_001: CLOSING<br>track_002: CLOSING, CRITICAL_TTC, IN_EGO_PATH<br>sign-0: STOP sign known, relevant to the path |
| +0.05 | A | g35 THROTTLE_END(A) (A:e12)<br>g38 TURN_LEFT_START(A) (A:e13) | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC<br>track_002: no active state |
| +0.05 | B | g36 THROTTLE_END(B) (B:e17)<br>g37 BRAKE_START(B) (B:e18) | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>track_002: CLOSING, CRITICAL_TTC, IN_EGO_PATH<br>sign-0: STOP sign known, relevant to the path |
| +0.20 | B | g39 MOVING_END(B) (B:e19)<br>g40 STOP_START(B) (B:e20) | ego: MOVING, BRAKE<br>track_001: CLOSING<br>track_002: CLOSING, CRITICAL_TTC, IN_EGO_PATH<br>sign-0: STOP sign known, relevant to the path |
| +0.40 | C | g42 EGO_PATH_ENTRY(C,A) (C:e08) | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC<br>track_002: CLOSING |
| +0.95 | C | g48 THROTTLE_END(C) (C:e12)<br>g49 BRAKE_START(C) (C:e13) | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH<br>track_002: CLOSING |
| +1.05 | B | g50 EGO_PATH_EXIT(B,A) (B:e23) | ego: STOP, BRAKE<br>track_001: CLOSING<br>track_002: IN_EGO_PATH<br>sign-0: STOP sign known, relevant to the path |
| +1.30 | C | g53 MOVING_END(C) (C:e15)<br>g54 STOP_START(C) (C:e16) | ego: MOVING, BRAKE<br>track_001: IN_EGO_PATH<br>track_002: no active state |
| +1.35 | A | g55 TURN_LEFT_END(A) (A:e17) | ego: MOVING, TURN_LEFT<br>track_001: no active state<br>track_002: no active state |
| +1.45 | A | g56 MOVING_END(A) (A:e18)<br>g57 STOP_START(A) (A:e19) | ego: MOVING<br>track_001: no active state<br>track_002: no active state |

## Plain-language reading

- 3.80 s before the reference collision, A started moving (already the case when first observed).
- 3.80 s before the reference collision, B started moving (already the case when first observed).
- 3.80 s before the reference collision, C started moving (already the case when first observed).
- 3.80 s before the reference collision, A pressed the accelerator (already the case when first observed).
- 3.80 s before the reference collision, B pressed the accelerator (already the case when first observed).
- 3.80 s before the reference collision, C pressed the accelerator (already the case when first observed).
- 3.80 s before the reference collision, A's radar started tracking C, which appeared in front of it.
- 3.80 s before the reference collision, C's radar started tracking A, which appeared in front of it.
- 3.80 s before the reference collision, A observed C start closing in (already the case when first observed).
- 3.80 s before the reference collision, C observed A start closing in (already the case when first observed).
- 3.65 s before the reference collision, C's radar started tracking B, which appeared on its left.
- 3.65 s before the reference collision, C observed B start closing in (already the case when first observed).
- 2.70 s before the reference collision, B's camera established a STOP sign detection (unidentified object B:sign-0).
- 2.10 s before the reference collision, B's radar started tracking C, which appeared on its right.
- 2.10 s before the reference collision, B observed C start closing in (already the case when first observed).
- 1.80 s before the reference collision, B's radar started tracking A, which appeared on its left.
- 1.80 s before the reference collision, B observed A start closing in (already the case when first observed).
- 1.75 s before the reference collision, A's radar started tracking B, which appeared on its right.
- 1.75 s before the reference collision, A observed B start closing in (already the case when first observed).
- 1.50 s before the reference collision, B's camera stopped detecting STOP sign unidentified object B:sign-0.
- 1.50 s before the reference collision, B started turning left.
- 1.30 s before the reference collision, B's time-to-contact with A became critical.
- 1.25 s before the reference collision, A's time-to-contact with B became critical.
- 0.85 s before the reference collision, B released the accelerator.
- 0.85 s before the reference collision, B started braking.
- 0.30 s before the reference collision, B released the brake.
- 0.15 s before the reference collision, B pressed the accelerator.
- 0.15 s before the reference collision, C's time-to-contact with A became critical.
- 0.05 s before the reference collision, A's time-to-contact with C became critical.
- At the reference collision, A and B both recorded this same collision (peak impulses A: 10358, B: 10358 N*s).
- At the reference collision, A's time-to-contact with B stopped being critical.
- At the reference collision, B's time-to-contact with A stopped being critical.
- At the reference collision, A observed B stop closing in.
- At the reference collision, B stopped turning left.
- 0.05 s after the reference collision, A released the accelerator.
- 0.05 s after the reference collision, B released the accelerator.
- 0.05 s after the reference collision, B started braking.
- 0.05 s after the reference collision, A started turning left.
- 0.20 s after the reference collision, B stopped moving.
- 0.20 s after the reference collision, B came to a stop.
- 0.35 s after the reference collision, B observed A stop closing in.
- 0.40 s after the reference collision, C observed A enter its forward path corridor.
- 0.85 s after the reference collision, A observed C stop closing in.
- 0.90 s after the reference collision, A and C both recorded this same collision (peak impulses A: 2250, C: 2250 N*s).
- 0.90 s after the reference collision, A's time-to-contact with C stopped being critical.
- 0.90 s after the reference collision, C's time-to-contact with A stopped being critical.
- 0.90 s after the reference collision, C observed A stop closing in.
- 0.95 s after the reference collision, C released the accelerator.
- 0.95 s after the reference collision, C started braking.
- 1.05 s after the reference collision, B observed A leave its forward path corridor.
- 1.20 s after the reference collision, B observed C stop closing in.
- 1.25 s after the reference collision, C observed B stop closing in.
- 1.30 s after the reference collision, C stopped moving.
- 1.30 s after the reference collision, C came to a stop.
- 1.35 s after the reference collision, A stopped turning left.
- 1.45 s after the reference collision, A stopped moving.
- 1.45 s after the reference collision, A came to a stop.
