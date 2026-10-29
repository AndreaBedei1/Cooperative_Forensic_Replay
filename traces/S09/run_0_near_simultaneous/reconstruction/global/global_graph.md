# Global graph - S09/run_0_near_simultaneous

Global time `t_global` is 0 at the reference collision. The local graphs were not modified: every node lists the local node(s) and local time(s) it comes from.

Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.

## Entities

| Entity | Kind | Details |
|--------|------|---------|
| A | recorder | clock ALIGNED; observed by others as: B:track_001 |
| B | recorder | clock ALIGNED; observed by others as: A:track_001 |

## Graph alignment

Reference event: `collision_001` (t_global = 0); `t_global = t_local + offset_to_global`. A graph that did not report it is aligned through the chain of matched collisions linking it to the reference (multi-hop); its anchor is its own report of the last collision of that chain.

| Graph | Status | Anchor node | Anchor local time | Offset to global | Note |
|-------|--------|-------------|------------------:|-----------------:|------|
| A | ALIGNED | A:e19 | 7.15 | -7.15 | reported the reference collision collision_001 |
| B | ALIGNED | B:e19 | 7.15 | -7.15 | reported the reference collision collision_001 |

Estimated relative clock offsets: B - A = +0.000 s

Matched `collision_001`: A and B both recorded a collision; peak impulses 7661.46 vs 7661.46 N*s (similarity 1.000, tolerance 0.10); no competing report within tolerance; the two bodies touch at their reports (0.00 m apart, tolerance 1.0 m); independent relative impulse std 0.100; combined z 0.000 (gate 3.0); engineering assumption; pre-contact radar view of each recorder checked against the candidate partner's own speed: not contradicted

## Identity associations

| Local track | Global entity | Status | Confidence | Evidence |
|-------------|---------------|--------|-----------:|----------|
| A:track_001 | B | ASSOCIATED | 0.96 | A and B both reported collision_001 (peak impulse 7661.46 vs 7661.46 N*s)<br>tracked for 4.65 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 12.1 m -> 0.6 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 0.42 m/s for reference)<br>clearance at the contact 0.62 m<br>the only track of A compatible with the contact |
| B:track_001 | A | ASSOCIATED | 0.98 | B and A both reported collision_001 (peak impulse 7661.46 vs 7661.46 N*s)<br>tracked for 4.65 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 11.9 m -> 0.1 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 0.34 m/s for reference)<br>clearance at the contact 0.10 m<br>the only track of B compatible with the contact |

## Nodes

| Id | Global time | Type | Actor | Subject / participants | Observed by (local node @ local time) | Details |
|----|------------:|------|-------|------------------------|----------------------------------------|---------|
| g01 | -7.15 | MOVING_START | A | - | A:e01 @ 0.00 | active_at_first_observation=True |
| g02 | -7.15 | MOVING_START | B | - | B:e01 @ 0.00 | active_at_first_observation=True |
| g03 | -7.15 | THROTTLE_START | A | - | A:e02 @ 0.00 | active_at_first_observation=True |
| g04 | -7.15 | THROTTLE_START | B | - | B:e02 @ 0.00 | active_at_first_observation=True |
| g05 | -6.95 | STOP_SIGN_DETECTED_START | A | A:sign-0 | A:e03 @ 0.20 | relevant_to_ego_path=True |
| g06 | -6.35 | STOP_SIGN_DETECTED_START | B | B:sign-0 | B:e03 @ 0.80 | relevant_to_ego_path=True |
| g07 | -4.75 | THROTTLE_END | A | - | A:e04 @ 2.40 |  |
| g08 | -4.75 | BRAKE_START | A | - | A:e05 @ 2.40 |  |
| g09 | -4.65 | THROTTLE_END | B | - | B:e04 @ 2.50 |  |
| g10 | -4.65 | BRAKE_START | B | - | B:e05 @ 2.50 |  |
| g11 | -4.65 | TRACK_APPEARED_LEFT | A | B | A:e06 @ 2.50 | initial_in_ego_path=False; source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g12 | -4.65 | TRACK_APPEARED_RIGHT | B | A | B:e06 @ 2.50 | initial_in_ego_path=False; source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g13 | -4.65 | CLOSING_START | A | B | A:e07 @ 2.50, A:e09 @ 3.70 | active_at_first_observation=True; source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g14 | -4.65 | CLOSING_START | B | A | B:e07 @ 2.50, B:e11 @ 3.70 | active_at_first_observation=True; source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g15 | -4.40 | STOP_SIGN_DETECTED_END | A | A:sign-0 | A:e08 @ 2.75 |  |
| g16 | -4.40 | STOP_SIGN_DETECTED_END | B | B:sign-0 | B:e08 @ 2.75 |  |
| g17 | -3.55 | MOVING_END | B | - | B:e09 @ 3.60 |  |
| g18 | -3.55 | STOP_START | B | - | B:e10 @ 3.60 |  |
| g19 | -3.45 | CLOSING_END | A | B | A:e09 @ 3.70 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g20 | -3.45 | CLOSING_END | B | A | B:e11 @ 3.70 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g21 | -3.45 | MOVING_END | A | - | A:e10 @ 3.70 |  |
| g22 | -3.45 | STOP_START | A | - | A:e11 @ 3.70 |  |
| g23 | -2.45 | BRAKE_END | B | - | B:e12 @ 4.70 |  |
| g24 | -2.45 | THROTTLE_START | B | - | B:e13 @ 4.70 |  |
| g25 | -2.30 | BRAKE_END | A | - | A:e12 @ 4.85 |  |
| g26 | -2.30 | THROTTLE_START | A | - | A:e13 @ 4.85 |  |
| g27 | -2.05 | CLOSING_START | A | B | A:e14 @ 5.10, A:e21 @ 7.15 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g28 | -2.00 | STOP_END | B | - | B:e14 @ 5.15 |  |
| g29 | -2.00 | MOVING_START | B | - | B:e15 @ 5.15 |  |
| g30 | -2.00 | CLOSING_START | B | A | B:e16 @ 5.15, B:e21 @ 7.20 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g31 | -1.95 | STOP_END | A | - | A:e15 @ 5.20 |  |
| g32 | -1.95 | MOVING_START | A | - | A:e16 @ 5.20 |  |
| g33 | -1.20 | CRITICAL_TTC_START | A | B | A:e17 @ 5.95, A:e20 @ 7.15 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g34 | -1.05 | CRITICAL_TTC_START | B | A | B:e17 @ 6.10, B:e20 @ 7.15 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g35 | -1.00 | TURN_LEFT_START | A | - | A:e18 @ 6.15 |  |
| g36 | -0.70 | EGO_PATH_ENTRY | B | A | B:e18 @ 6.45, B:e24 @ 7.35 | occupancy_evidence=returns; occupancy_margin_m=0.55; occupancy_sigma_m=0.25; cause=TARGET_LATERAL; geometry=estimated_body; source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g37 | 0.00 | COLLISION | - | A, B | A:e19 @ 7.15, B:e19 @ 7.15 | matched_event=collision_001; reference_event=True; peak_impulse=A 7661.46, B 7661.46 |
| g38 | 0.00 | CRITICAL_TTC_END | A | B | A:e20 @ 7.15 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g39 | 0.00 | CRITICAL_TTC_END | B | A | B:e20 @ 7.15 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g40 | 0.00 | CLOSING_END | A | B | A:e21 @ 7.15 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g41 | 0.05 | CLOSING_END | B | A | B:e21 @ 7.20 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g42 | 0.05 | THROTTLE_END | A | - | A:e22 @ 7.20 |  |
| g43 | 0.05 | THROTTLE_END | B | - | B:e22 @ 7.20 |  |
| g44 | 0.05 | BRAKE_START | A | - | A:e23 @ 7.20 |  |
| g45 | 0.05 | BRAKE_START | B | - | B:e23 @ 7.20 |  |
| g46 | 0.20 | EGO_PATH_EXIT | B | A | B:e24 @ 7.35 | occupancy_evidence=returns; occupancy_margin_m=-0.59; occupancy_sigma_m=0.25; cause=MUTUAL_LATERAL; geometry=estimated_body; source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g47 | 0.30 | MOVING_END | B | - | B:e25 @ 7.45 |  |
| g48 | 0.30 | STOP_START | B | - | B:e26 @ 7.45 |  |
| g49 | 0.50 | TURN_LEFT_END | A | - | A:e24 @ 7.65 |  |
| g50 | 0.50 | MOVING_END | A | - | A:e25 @ 7.65 |  |
| g51 | 0.50 | STOP_START | A | - | A:e26 @ 7.65 |  |

## Edges

```
    g01 --PRECEDES--> g05
    g02 --PRECEDES--> g05
    g03 --PRECEDES--> g05
    g04 --PRECEDES--> g05
    g05 --PRECEDES--> g06
    g06 --PRECEDES--> g07
    g06 --PRECEDES--> g08
    g07 --PRECEDES--> g09
    g07 --PRECEDES--> g10
    g07 --PRECEDES--> g11
    g07 --PRECEDES--> g12
    g07 --PRECEDES--> g13
    g07 --PRECEDES--> g14
    g08 --PRECEDES--> g09
    g08 --PRECEDES--> g10
    g08 --PRECEDES--> g11
    g08 --PRECEDES--> g12
    g08 --PRECEDES--> g13
    g08 --PRECEDES--> g14
    g09 --PRECEDES--> g15
    g09 --PRECEDES--> g16
    g10 --PRECEDES--> g15
    g10 --PRECEDES--> g16
    g11 --PRECEDES--> g15
    g11 --PRECEDES--> g16
    g12 --PRECEDES--> g15
    g12 --PRECEDES--> g16
    g13 --PRECEDES--> g15
    g13 --PRECEDES--> g16
    g14 --PRECEDES--> g15
    g14 --PRECEDES--> g16
    g15 --PRECEDES--> g17
    g15 --PRECEDES--> g18
    g16 --PRECEDES--> g17
    g16 --PRECEDES--> g18
    g17 --PRECEDES--> g19
    g17 --PRECEDES--> g20
    g17 --PRECEDES--> g21
    g17 --PRECEDES--> g22
    g18 --PRECEDES--> g19
    g18 --PRECEDES--> g20
    g18 --PRECEDES--> g21
    g18 --PRECEDES--> g22
    g19 --PRECEDES--> g23
    g19 --PRECEDES--> g24
    g20 --PRECEDES--> g23
    g20 --PRECEDES--> g24
    g21 --PRECEDES--> g23
    g21 --PRECEDES--> g24
    g22 --PRECEDES--> g23
    g22 --PRECEDES--> g24
    g23 --PRECEDES--> g25
    g23 --PRECEDES--> g26
    g24 --PRECEDES--> g25
    g24 --PRECEDES--> g26
    g25 --PRECEDES--> g27
    g26 --PRECEDES--> g27
    g27 --PRECEDES--> g28
    g27 --PRECEDES--> g29
    g27 --PRECEDES--> g30
    g28 --PRECEDES--> g31
    g28 --PRECEDES--> g32
    g29 --PRECEDES--> g31
    g29 --PRECEDES--> g32
    g30 --PRECEDES--> g31
    g30 --PRECEDES--> g32
    g31 --PRECEDES--> g33
    g32 --PRECEDES--> g33
    g33 --PRECEDES--> g34
    g34 --PRECEDES--> g35
    g35 --PRECEDES--> g36
    g36 --PRECEDES--> g37
    g36 --PRECEDES--> g38
    g36 --PRECEDES--> g39
    g36 --PRECEDES--> g40
    g37 --PRECEDES--> g41
    g37 --PRECEDES--> g42
    g37 --PRECEDES--> g43
    g37 --PRECEDES--> g44
    g37 --PRECEDES--> g45
    g38 --PRECEDES--> g41
    g38 --PRECEDES--> g42
    g38 --PRECEDES--> g43
    g38 --PRECEDES--> g44
    g38 --PRECEDES--> g45
    g39 --PRECEDES--> g41
    g39 --PRECEDES--> g42
    g39 --PRECEDES--> g43
    g39 --PRECEDES--> g44
    g39 --PRECEDES--> g45
    g40 --PRECEDES--> g41
    g40 --PRECEDES--> g42
    g40 --PRECEDES--> g43
    g40 --PRECEDES--> g44
    g40 --PRECEDES--> g45
    g41 --PRECEDES--> g46
    g42 --PRECEDES--> g46
    g43 --PRECEDES--> g46
    g44 --PRECEDES--> g46
    g45 --PRECEDES--> g46
    g46 --PRECEDES--> g47
    g46 --PRECEDES--> g48
    g47 --PRECEDES--> g49
    g47 --PRECEDES--> g50
    g47 --PRECEDES--> g51
    g48 --PRECEDES--> g49
    g48 --PRECEDES--> g50
    g48 --PRECEDES--> g51
    g11 --SAME_TRACK--> g13
    g11 --SAME_TRACK--> g19
    g11 --SAME_TRACK--> g27
    g11 --SAME_TRACK--> g33
    g11 --SAME_TRACK--> g38
    g11 --SAME_TRACK--> g40
    g12 --SAME_TRACK--> g14
    g12 --SAME_TRACK--> g20
    g12 --SAME_TRACK--> g30
    g12 --SAME_TRACK--> g34
    g12 --SAME_TRACK--> g36
    g12 --SAME_TRACK--> g39
    g12 --SAME_TRACK--> g41
    g12 --SAME_TRACK--> g46
```

## Global trace

Events in one row are simultaneous at 0.05 s resolution: their order is unresolved.

| t_global | Events |
|---------:|--------|
| -7.15 | MOVING_START(A); MOVING_START(B); THROTTLE_START(A); THROTTLE_START(B) |
| -6.95 | STOP_SIGN_DETECTED_START(A,A:sign-0) |
| -6.35 | STOP_SIGN_DETECTED_START(B,B:sign-0) |
| -4.75 | THROTTLE_END(A); BRAKE_START(A) |
| -4.65 | THROTTLE_END(B); BRAKE_START(B); TRACK_APPEARED_LEFT(A,B); TRACK_APPEARED_RIGHT(B,A); CLOSING_START(A,B); CLOSING_START(B,A) |
| -4.40 | STOP_SIGN_DETECTED_END(A,A:sign-0); STOP_SIGN_DETECTED_END(B,B:sign-0) |
| -3.55 | MOVING_END(B); STOP_START(B) |
| -3.45 | CLOSING_END(A,B); CLOSING_END(B,A); MOVING_END(A); STOP_START(A) |
| -2.45 | BRAKE_END(B); THROTTLE_START(B) |
| -2.30 | BRAKE_END(A); THROTTLE_START(A) |
| -2.05 | CLOSING_START(A,B) |
| -2.00 | STOP_END(B); MOVING_START(B); CLOSING_START(B,A) |
| -1.95 | STOP_END(A); MOVING_START(A) |
| -1.20 | CRITICAL_TTC_START(A,B) |
| -1.05 | CRITICAL_TTC_START(B,A) |
| -1.00 | TURN_LEFT_START(A) |
| -0.70 | EGO_PATH_ENTRY(B,A) |
| +0.00 | COLLISION(A,B); CRITICAL_TTC_END(A,B); CRITICAL_TTC_END(B,A); CLOSING_END(A,B) |
| +0.05 | CLOSING_END(B,A); THROTTLE_END(A); THROTTLE_END(B); BRAKE_START(A); BRAKE_START(B) |
| +0.20 | EGO_PATH_EXIT(B,A) |
| +0.30 | MOVING_END(B); STOP_START(B) |
| +0.50 | TURN_LEFT_END(A); MOVING_END(A); STOP_START(A) |

## Temporal safety relations

Per track: does the cut-in start before the critical TTC, or was the critical TTC already active? Is the path entry before or after it? Temporal properties only, not causes.

- A's track_001 (B): CRITICAL_TTC_START 5.95, COLLISION with B 7.15 (+1.20 s) [local times; t_global: critical_ttc_start -1.20, collision +0.00]
- B's track_001 (A): CRITICAL_TTC_START 6.10, COLLISION with A 7.15 (+1.05 s); EGO_PATH_ENTRY 6.45 after critical TTC (+0.35 s) [local times; t_global: critical_ttc_start -1.05, ego_path_entry -0.70, collision +0.00]

## Perceived state before each event, per observing recorder

Each recorder's own belief just before its events, in its own local names (track_001, ...): fusion does not rewrite it. True states are named, unknown ones end with `?`.

| t_global | Recorder | Events (local node) | Perceived state just before |
|---------:|----------|---------------------|-----------------------------|
| -7.15 | A | g01 MOVING_START(A) (A:e01)<br>g03 THROTTLE_START(A) (A:e02) | ego: not yet observed |
| -7.15 | B | g02 MOVING_START(B) (B:e01)<br>g04 THROTTLE_START(B) (B:e02) | ego: not yet observed |
| -6.95 | A | g05 STOP_SIGN_DETECTED_START(A,A:sign-0) (A:e03) | ego: MOVING, THROTTLE |
| -6.35 | B | g06 STOP_SIGN_DETECTED_START(B,B:sign-0) (B:e03) | ego: MOVING, THROTTLE |
| -4.75 | A | g07 THROTTLE_END(A) (A:e04)<br>g08 BRAKE_START(A) (A:e05) | ego: MOVING, THROTTLE<br>sign-0: STOP sign known, relevant to the path |
| -4.65 | B | g09 THROTTLE_END(B) (B:e04)<br>g10 BRAKE_START(B) (B:e05)<br>g12 TRACK_APPEARED_RIGHT(B,A) (B:e06)<br>g14 CLOSING_START(B,A) (B:e07) | ego: MOVING, THROTTLE<br>sign-0: STOP sign known, relevant to the path |
| -4.65 | A | g11 TRACK_APPEARED_LEFT(A,B) (A:e06)<br>g13 CLOSING_START(A,B) (A:e07) | ego: MOVING, BRAKE<br>sign-0: STOP sign known, relevant to the path |
| -4.65 | A | g13 CLOSING_START(A,B) (A:e07)<br>g19 CLOSING_END(A,B) (A:e09)<br>g21 MOVING_END(A) (A:e10)<br>g22 STOP_START(A) (A:e11) | ego: MOVING, BRAKE<br>sign-0: STOP sign known, relevant to the path |
| -4.65 | B | g14 CLOSING_START(B,A) (B:e07)<br>g20 CLOSING_END(B,A) (B:e11) | ego: MOVING, THROTTLE<br>sign-0: STOP sign known, relevant to the path |
| -4.40 | A | g15 STOP_SIGN_DETECTED_END(A,A:sign-0) (A:e08) | ego: MOVING, BRAKE<br>track_001: CLOSING, CRITICAL_TTC?<br>sign-0: STOP sign known, relevant to the path |
| -4.40 | B | g16 STOP_SIGN_DETECTED_END(B,B:sign-0) (B:e08) | ego: MOVING, BRAKE<br>track_001: CLOSING, CRITICAL_TTC?<br>sign-0: STOP sign known, relevant to the path |
| -3.55 | B | g17 MOVING_END(B) (B:e09)<br>g18 STOP_START(B) (B:e10) | ego: MOVING, BRAKE<br>track_001: CLOSING<br>sign-0: STOP sign known, relevant to the path |
| -2.45 | B | g23 BRAKE_END(B) (B:e12)<br>g24 THROTTLE_START(B) (B:e13) | ego: STOP, BRAKE<br>track_001: no active state<br>sign-0: STOP sign known, relevant to the path |
| -2.30 | A | g25 BRAKE_END(A) (A:e12)<br>g26 THROTTLE_START(A) (A:e13) | ego: STOP, BRAKE<br>track_001: no active state<br>sign-0: STOP sign known, relevant to the path |
| -2.05 | A | g27 CLOSING_START(A,B) (A:e14) | ego: STOP, THROTTLE<br>track_001: no active state<br>sign-0: STOP sign known, relevant to the path |
| -2.05 | A | g27 CLOSING_START(A,B) (A:e14)<br>g33 CRITICAL_TTC_START(A,B) (A:e17)<br>g37 COLLISION(A,B) (A:e19)<br>g38 CRITICAL_TTC_END(A,B) (A:e20)<br>g40 CLOSING_END(A,B) (A:e21) | ego: STOP, THROTTLE<br>track_001: no active state<br>sign-0: STOP sign known, relevant to the path |
| -2.00 | B | g28 STOP_END(B) (B:e14)<br>g29 MOVING_START(B) (B:e15)<br>g30 CLOSING_START(B,A) (B:e16) | ego: STOP, THROTTLE<br>track_001: no active state<br>sign-0: STOP sign known, relevant to the path |
| -2.00 | B | g30 CLOSING_START(B,A) (B:e16)<br>g41 CLOSING_END(B,A) (B:e21)<br>g43 THROTTLE_END(B) (B:e22)<br>g45 BRAKE_START(B) (B:e23) | ego: STOP, THROTTLE<br>track_001: no active state<br>sign-0: STOP sign known, relevant to the path |
| -1.95 | A | g31 STOP_END(A) (A:e15)<br>g32 MOVING_START(A) (A:e16) | ego: STOP, THROTTLE<br>track_001: CLOSING<br>sign-0: STOP sign known, relevant to the path |
| -1.20 | A | g33 CRITICAL_TTC_START(A,B) (A:e17) | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>sign-0: STOP sign known, relevant to the path |
| -1.05 | B | g34 CRITICAL_TTC_START(B,A) (B:e17) | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>sign-0: STOP sign known, relevant to the path |
| -1.05 | B | g34 CRITICAL_TTC_START(B,A) (B:e17)<br>g37 COLLISION(A,B) (B:e19)<br>g39 CRITICAL_TTC_END(B,A) (B:e20) | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>sign-0: STOP sign known, relevant to the path |
| -1.00 | A | g35 TURN_LEFT_START(A) (A:e18) | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC<br>sign-0: STOP sign known, relevant to the path |
| -0.70 | B | g36 EGO_PATH_ENTRY(B,A) (B:e18) | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC<br>sign-0: STOP sign known, relevant to the path |
| -0.70 | B | g36 EGO_PATH_ENTRY(B,A) (B:e18)<br>g46 EGO_PATH_EXIT(B,A) (B:e24) | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC<br>sign-0: STOP sign known, relevant to the path |
| +0.05 | A | g42 THROTTLE_END(A) (A:e22)<br>g44 BRAKE_START(A) (A:e23) | ego: MOVING, THROTTLE, TURN_LEFT<br>track_001: no active state<br>sign-0: STOP sign known, relevant to the path |
| +0.30 | B | g47 MOVING_END(B) (B:e25)<br>g48 STOP_START(B) (B:e26) | ego: MOVING, BRAKE<br>track_001: no active state<br>sign-0: STOP sign known, relevant to the path |
| +0.50 | A | g49 TURN_LEFT_END(A) (A:e24)<br>g50 MOVING_END(A) (A:e25)<br>g51 STOP_START(A) (A:e26) | ego: MOVING, BRAKE, TURN_LEFT<br>track_001: no active state<br>sign-0: STOP sign known, relevant to the path |

## Plain-language reading

- 7.15 s before the reference collision, A started moving (already the case when first observed).
- 7.15 s before the reference collision, B started moving (already the case when first observed).
- 7.15 s before the reference collision, A pressed the accelerator (already the case when first observed).
- 7.15 s before the reference collision, B pressed the accelerator (already the case when first observed).
- 6.95 s before the reference collision, A's camera established a STOP sign detection (unidentified object A:sign-0).
- 6.35 s before the reference collision, B's camera established a STOP sign detection (unidentified object B:sign-0).
- 4.75 s before the reference collision, A released the accelerator.
- 4.75 s before the reference collision, A started braking.
- 4.65 s before the reference collision, B released the accelerator.
- 4.65 s before the reference collision, B started braking.
- 4.65 s before the reference collision, A's radar started tracking B, which appeared on its left.
- 4.65 s before the reference collision, B's radar started tracking A, which appeared on its right.
- 4.65 s before the reference collision, A observed B start closing in (already the case when first observed).
- 4.65 s before the reference collision, B observed A start closing in (already the case when first observed).
- 4.40 s before the reference collision, A's camera stopped detecting STOP sign unidentified object A:sign-0.
- 4.40 s before the reference collision, B's camera stopped detecting STOP sign unidentified object B:sign-0.
- 3.55 s before the reference collision, B stopped moving.
- 3.55 s before the reference collision, B came to a stop.
- 3.45 s before the reference collision, A observed B stop closing in.
- 3.45 s before the reference collision, B observed A stop closing in.
- 3.45 s before the reference collision, A stopped moving.
- 3.45 s before the reference collision, A came to a stop.
- 2.45 s before the reference collision, B released the brake.
- 2.45 s before the reference collision, B pressed the accelerator.
- 2.30 s before the reference collision, A released the brake.
- 2.30 s before the reference collision, A pressed the accelerator.
- 2.05 s before the reference collision, A observed B start closing in.
- 2.00 s before the reference collision, B left its stop.
- 2.00 s before the reference collision, B started moving.
- 2.00 s before the reference collision, B observed A start closing in.
- 1.95 s before the reference collision, A left its stop.
- 1.95 s before the reference collision, A started moving.
- 1.20 s before the reference collision, A's time-to-contact with B became critical.
- 1.05 s before the reference collision, B's time-to-contact with A became critical.
- 1.00 s before the reference collision, A started turning left.
- 0.70 s before the reference collision, B observed A enter its forward path corridor.
- At the reference collision, A and B both recorded this same collision (peak impulses A: 7661, B: 7661 N*s).
- At the reference collision, A's time-to-contact with B stopped being critical.
- At the reference collision, B's time-to-contact with A stopped being critical.
- At the reference collision, A observed B stop closing in.
- 0.05 s after the reference collision, B observed A stop closing in.
- 0.05 s after the reference collision, A released the accelerator.
- 0.05 s after the reference collision, B released the accelerator.
- 0.05 s after the reference collision, A started braking.
- 0.05 s after the reference collision, B started braking.
- 0.20 s after the reference collision, B observed A leave its forward path corridor.
- 0.30 s after the reference collision, B stopped moving.
- 0.30 s after the reference collision, B came to a stop.
- 0.50 s after the reference collision, A stopped turning left.
- 0.50 s after the reference collision, A stopped moving.
- 0.50 s after the reference collision, A came to a stop.
