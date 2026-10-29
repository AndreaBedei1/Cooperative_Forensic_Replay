# Global graph - S11/run_0_consequential

Global time `t_global` is 0 at the reference collision. The local graphs were not modified: every node lists the local node(s) and local time(s) it comes from.

Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.

## Entities

| Entity | Kind | Details |
|--------|------|---------|
| A | recorder | clock ALIGNED; observed by others as: B:track_001, C:track_001 |
| B | recorder | clock ALIGNED; observed by others as: - |
| C | recorder | clock ALIGNED; observed by others as: A:track_001, B:track_002 |

## Graph alignment

Reference event: `collision_001` (t_global = 0); `t_global = t_local + offset_to_global`. A graph that did not report it is aligned through the chain of matched collisions linking it to the reference (multi-hop); its anchor is its own report of the last collision of that chain.

| Graph | Status | Anchor node | Anchor local time | Offset to global | Note |
|-------|--------|-------------|------------------:|-----------------:|------|
| A | ALIGNED | A:e10 | 5.55 | -5.55 | reported the reference collision collision_001 |
| B | ALIGNED | B:e10 | 5.55 | -5.55 | reported the reference collision collision_001 |
| C | ALIGNED | C:e09 | 6.60 | -5.55 | shares collision_002 with A, aligned through collision_001 -> collision_002 |

Estimated relative clock offsets: B - A = +0.000 s, C - A = +0.000 s, C - B = +0.000 s

Matched `collision_001`: A and B both recorded a collision; peak impulses 4243.51 vs 4243.51 N*s (similarity 1.000, tolerance 0.10); no competing report within tolerance; the two bodies touch at their reports (0.00 m apart, tolerance 1.0 m); independent relative impulse std 0.100; combined z 0.000 (gate 3.0); engineering assumption; pre-contact radar view of each recorder checked against the candidate partner's own speed: not contradicted

Matched `collision_002`: A and C both recorded a collision; peak impulses 839.68 vs 839.68 N*s (similarity 1.000, tolerance 0.10); no competing report within tolerance; the two bodies touch at their reports (0.00 m apart, tolerance 1.0 m); independent relative impulse std 0.100; combined z 0.000 (gate 3.0); engineering assumption; pre-contact radar view of each recorder checked against the candidate partner's own speed: not contradicted

## Identity associations

| Local track | Global entity | Status | Confidence | Evidence |
|-------------|---------------|--------|-----------:|----------|
| A:track_001 | C | ASSOCIATED | 1.00 | A and C both reported collision_002 at 6.60 s (peak impulse 839.68 vs 839.68 N*s)<br>tracked for 6.60 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 1.2 m -> 0.0 m over the last 1.0 s<br>track motion compatible with C's own speed in the observed direction (3 sigma; full-speed RMSE 0.03 m/s for reference)<br>clearance at the contact 0.00 m<br>the only track of A compatible with the contact<br>collision_001 with B at 5.55 s: not compatible (track motion contradicts B's own speed in the observed direction (3 sigma; full-speed RMSE 3.46 m/s for reference)) |
| B:track_001 | A | ASSOCIATED | 0.98 | B and A both reported collision_001 (peak impulse 4243.51 vs 4243.51 N*s)<br>tracked for 5.55 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 4.3 m -> 0.1 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 0.31 m/s for reference)<br>clearance at the contact 0.07 m<br>the only track of B compatible with the contact |
| B:track_002 | C | ASSOCIATED | 1.00 | B and A both reported collision_001 (peak impulse 4243.51 vs 4243.51 N*s)<br>tracked for 5.55 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 9.1 m -> 6.1 m over the last 1.0 s<br>track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 2.32 m/s for reference)<br>clearance at the contact 6.09 m (beyond 3.50 m: confidence factor 0.69)<br>common frame: its returns lie on C's own footprint (median 0.00 m, 0.00 sigma of the relative uncertainty, over 122 samples; 100% within 3 sigma) at C's own velocity |
| C:track_001 | A | ASSOCIATED | 1.00 | C and A both reported collision_002 (peak impulse 839.68 vs 839.68 N*s)<br>tracked for 3.95 s before the matched collision<br>continuous up to the contact: last observed 0.15 s before it (window 1.00 s)<br>approaching before the contact: clearance 2.2 m -> 1.0 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 0.09 m/s for reference)<br>clearance at the contact 1.04 m<br>the only track of C compatible with the contact |

## Nodes

| Id | Global time | Type | Actor | Subject / participants | Observed by (local node @ local time) | Details |
|----|------------:|------|-------|------------------------|----------------------------------------|---------|
| g01 | -5.55 | MOVING_START | A | - | A:e01 @ 0.00 | active_at_first_observation=True |
| g02 | -5.55 | MOVING_START | B | - | B:e01 @ 0.00 | active_at_first_observation=True |
| g03 | -5.55 | MOVING_START | C | - | C:e01 @ 0.00 | active_at_first_observation=True |
| g04 | -5.55 | THROTTLE_START | A | - | A:e02 @ 0.00 | active_at_first_observation=True |
| g05 | -5.55 | THROTTLE_START | B | - | B:e02 @ 0.00 | active_at_first_observation=True |
| g06 | -5.55 | THROTTLE_START | C | - | C:e02 @ 0.00 | active_at_first_observation=True |
| g07 | -5.55 | TRACK_APPEARED_FRONT | B | A | B:e03 @ 0.00 | initial_in_ego_path=True; source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g08 | -5.55 | TRACK_APPEARED_LEFT | A | C | A:e03 @ 0.00 | initial_in_ego_path=False; source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g09 | -5.55 | TRACK_APPEARED_LEFT | B | C | B:e04 @ 0.00 | initial_in_ego_path=False; source_track=track_002; aggregation=entity_state_union; source_tracks=['B:track_002'] |
| g10 | -5.55 | CLOSING_START | A | C | A:e04 @ 0.00, A:e07 @ 4.40 | active_at_first_observation=True; source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g11 | -5.55 | CLOSING_START | B | C | B:e05 @ 0.00, B:e13 @ 5.80 | active_at_first_observation=True; source_track=track_002; aggregation=entity_state_union; source_tracks=['B:track_002'] |
| g12 | -5.05 | CRITICAL_TTC_START | B | A | B:e06 @ 0.50, B:e11 @ 5.55 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g13 | -2.90 | TRACK_APPEARED_RIGHT | C | A | C:e03 @ 2.65, C:e08 @ 6.45 | initial_in_ego_path=False; source_track=track_001; aggregation=entity_state_union; source_tracks=['C:track_001'] |
| g14 | -2.90 | CLOSING_START | C | A | C:e04 @ 2.65, C:e05 @ 4.35 | active_at_first_observation=True; source_track=track_001; aggregation=entity_state_union; source_tracks=['C:track_001'] |
| g15 | -1.60 | THROTTLE_END | A | - | A:e05 @ 3.95 |  |
| g16 | -1.60 | BRAKE_START | A | - | A:e06 @ 3.95 |  |
| g17 | -1.45 | CLOSING_START | B | A | B:e07 @ 4.10, B:e12 @ 5.60 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g18 | -1.20 | CLOSING_END | C | A | C:e05 @ 4.35 | source_track=track_001; aggregation=entity_state_union; source_tracks=['C:track_001'] |
| g19 | -1.15 | CLOSING_END | A | C | A:e07 @ 4.40 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g20 | -1.00 | BRAKE_END | A | - | A:e08 @ 4.55 |  |
| g21 | -0.90 | THROTTLE_START | A | - | A:e09 @ 4.65 |  |
| g22 | -0.15 | THROTTLE_END | B | - | B:e08 @ 5.40 |  |
| g23 | -0.15 | BRAKE_START | B | - | B:e09 @ 5.40 |  |
| g24 | 0.00 | COLLISION | - | A, B | A:e10 @ 5.55, B:e10 @ 5.55 | matched_event=collision_001; reference_event=True; peak_impulse=A 4243.51, B 4243.51 |
| g25 | 0.00 | CRITICAL_TTC_END | B | A | B:e11 @ 5.55 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g26 | 0.00 | THROTTLE_END | A | - | A:e11 @ 5.55 |  |
| g27 | 0.00 | BRAKE_START | A | - | A:e12 @ 5.55 |  |
| g28 | 0.00 | CLOSING_START | A | C | A:e13 @ 5.55, A:e19 @ 6.60 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g29 | 0.00 | CLOSING_START | C | A | C:e06 @ 5.55 | source_track=track_001; aggregation=entity_state_union; source_tracks=['C:track_001'] |
| g30 | 0.00 | CRITICAL_TTC_START | A | C | A:e14 @ 5.55, A:e18 @ 6.60 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g31 | 0.00 | CRITICAL_TTC_START | C | A | C:e07 @ 5.55 | source_track=track_001; aggregation=entity_state_union; source_tracks=['C:track_001'] |
| g32 | 0.05 | CLOSING_END | B | A | B:e12 @ 5.60 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g33 | 0.05 | BRAKE_END | A | - | A:e15 @ 5.60 |  |
| g34 | 0.25 | CLOSING_END | B | C | B:e13 @ 5.80 | source_track=track_002; aggregation=entity_state_union; source_tracks=['B:track_002'] |
| g35 | 0.35 | EGO_PATH_ENTRY | A | C | A:e16 @ 5.90 | occupancy_evidence=box; occupancy_margin_m=0.58; occupancy_sigma_m=0.26; cause=RECORDER_LATERAL; geometry=estimated_body; source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g36 | 0.65 | MOVING_END | B | - | B:e14 @ 6.20 |  |
| g37 | 0.65 | STOP_START | B | - | B:e15 @ 6.20 |  |
| g38 | 0.90 | TRACK_LOST | C | A | C:e08 @ 6.45 | source_track=track_001; aggregation=entity_state_union; source_tracks=['C:track_001'] |
| g39 | 1.05 | COLLISION | - | A, C | A:e17 @ 6.60, C:e09 @ 6.60 | matched_event=collision_002; reference_event=False; peak_impulse=A 839.68, C 839.68 |
| g40 | 1.05 | CRITICAL_TTC_END | A | C | A:e18 @ 6.60 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g41 | 1.05 | CRITICAL_TTC_END | C | A | C:e09 @ 6.60 | closed_by_contact=collision_002 |
| g42 | 1.05 | CLOSING_END | A | C | A:e19 @ 6.60 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g43 | 1.10 | THROTTLE_END | C | - | C:e10 @ 6.65 |  |
| g44 | 1.10 | BRAKE_START | C | - | C:e11 @ 6.65 |  |
| g45 | 1.90 | MOVING_END | A | - | A:e20 @ 7.45 |  |
| g46 | 1.90 | MOVING_END | C | - | C:e12 @ 7.45 |  |
| g47 | 1.90 | STOP_START | A | - | A:e21 @ 7.45 |  |
| g48 | 1.90 | STOP_START | C | - | C:e13 @ 7.45 |  |
| g49 | 1.90 | BRAKE_START | A | - | A:e22 @ 7.45 |  |

## Edges

```
    g01 --PRECEDES--> g12
    g02 --PRECEDES--> g12
    g03 --PRECEDES--> g12
    g04 --PRECEDES--> g12
    g05 --PRECEDES--> g12
    g06 --PRECEDES--> g12
    g07 --PRECEDES--> g12
    g08 --PRECEDES--> g12
    g09 --PRECEDES--> g12
    g10 --PRECEDES--> g12
    g11 --PRECEDES--> g12
    g12 --PRECEDES--> g13
    g12 --PRECEDES--> g14
    g13 --PRECEDES--> g15
    g13 --PRECEDES--> g16
    g14 --PRECEDES--> g15
    g14 --PRECEDES--> g16
    g15 --PRECEDES--> g17
    g16 --PRECEDES--> g17
    g17 --PRECEDES--> g18
    g18 --PRECEDES--> g19
    g19 --PRECEDES--> g20
    g20 --PRECEDES--> g21
    g21 --PRECEDES--> g22
    g21 --PRECEDES--> g23
    g22 --PRECEDES--> g24
    g22 --PRECEDES--> g25
    g22 --PRECEDES--> g26
    g22 --PRECEDES--> g27
    g22 --PRECEDES--> g28
    g22 --PRECEDES--> g29
    g22 --PRECEDES--> g30
    g22 --PRECEDES--> g31
    g23 --PRECEDES--> g24
    g23 --PRECEDES--> g25
    g23 --PRECEDES--> g26
    g23 --PRECEDES--> g27
    g23 --PRECEDES--> g28
    g23 --PRECEDES--> g29
    g23 --PRECEDES--> g30
    g23 --PRECEDES--> g31
    g24 --PRECEDES--> g32
    g24 --PRECEDES--> g33
    g25 --PRECEDES--> g32
    g25 --PRECEDES--> g33
    g26 --PRECEDES--> g32
    g26 --PRECEDES--> g33
    g27 --PRECEDES--> g32
    g27 --PRECEDES--> g33
    g28 --PRECEDES--> g32
    g28 --PRECEDES--> g33
    g29 --PRECEDES--> g32
    g29 --PRECEDES--> g33
    g30 --PRECEDES--> g32
    g30 --PRECEDES--> g33
    g31 --PRECEDES--> g32
    g31 --PRECEDES--> g33
    g32 --PRECEDES--> g34
    g33 --PRECEDES--> g34
    g34 --PRECEDES--> g35
    g35 --PRECEDES--> g36
    g35 --PRECEDES--> g37
    g36 --PRECEDES--> g38
    g37 --PRECEDES--> g38
    g38 --PRECEDES--> g39
    g38 --PRECEDES--> g40
    g38 --PRECEDES--> g41
    g38 --PRECEDES--> g42
    g39 --PRECEDES--> g43
    g39 --PRECEDES--> g44
    g40 --PRECEDES--> g43
    g40 --PRECEDES--> g44
    g41 --PRECEDES--> g43
    g41 --PRECEDES--> g44
    g42 --PRECEDES--> g43
    g42 --PRECEDES--> g44
    g43 --PRECEDES--> g45
    g43 --PRECEDES--> g46
    g43 --PRECEDES--> g47
    g43 --PRECEDES--> g48
    g43 --PRECEDES--> g49
    g44 --PRECEDES--> g45
    g44 --PRECEDES--> g46
    g44 --PRECEDES--> g47
    g44 --PRECEDES--> g48
    g44 --PRECEDES--> g49
    g08 --SAME_TRACK--> g10
    g08 --SAME_TRACK--> g19
    g08 --SAME_TRACK--> g28
    g08 --SAME_TRACK--> g30
    g08 --SAME_TRACK--> g35
    g08 --SAME_TRACK--> g40
    g08 --SAME_TRACK--> g42
    g09 --SAME_TRACK--> g11
    g07 --SAME_TRACK--> g12
    g07 --SAME_TRACK--> g17
    g07 --SAME_TRACK--> g25
    g07 --SAME_TRACK--> g32
    g09 --SAME_TRACK--> g34
    g13 --SAME_TRACK--> g14
    g13 --SAME_TRACK--> g18
    g13 --SAME_TRACK--> g29
    g13 --SAME_TRACK--> g31
    g13 --SAME_TRACK--> g38
```

## Global trace

Events in one row are simultaneous at 0.05 s resolution: their order is unresolved.

| t_global | Events |
|---------:|--------|
| -5.55 | MOVING_START(A); MOVING_START(B); MOVING_START(C); THROTTLE_START(A); THROTTLE_START(B); THROTTLE_START(C); TRACK_APPEARED_FRONT(B,A); TRACK_APPEARED_LEFT(A,C); TRACK_APPEARED_LEFT(B,C); CLOSING_START(A,C); CLOSING_START(B,C) |
| -5.05 | CRITICAL_TTC_START(B,A) |
| -2.90 | TRACK_APPEARED_RIGHT(C,A); CLOSING_START(C,A) |
| -1.60 | THROTTLE_END(A); BRAKE_START(A) |
| -1.45 | CLOSING_START(B,A) |
| -1.20 | CLOSING_END(C,A) |
| -1.15 | CLOSING_END(A,C) |
| -1.00 | BRAKE_END(A) |
| -0.90 | THROTTLE_START(A) |
| -0.15 | THROTTLE_END(B); BRAKE_START(B) |
| +0.00 | COLLISION(A,B); CRITICAL_TTC_END(B,A); THROTTLE_END(A); BRAKE_START(A); CLOSING_START(A,C); CLOSING_START(C,A); CRITICAL_TTC_START(A,C); CRITICAL_TTC_START(C,A) |
| +0.05 | CLOSING_END(B,A); BRAKE_END(A) |
| +0.25 | CLOSING_END(B,C) |
| +0.35 | EGO_PATH_ENTRY(A,C) |
| +0.65 | MOVING_END(B); STOP_START(B) |
| +0.90 | TRACK_LOST(C,A) |
| +1.05 | COLLISION(A,C); CRITICAL_TTC_END(A,C); CRITICAL_TTC_END(C,A); CLOSING_END(A,C) |
| +1.10 | THROTTLE_END(C); BRAKE_START(C) |
| +1.90 | MOVING_END(A); MOVING_END(C); STOP_START(A); STOP_START(C); BRAKE_START(A) |

## Temporal safety relations

Per track: does the cut-in start before the critical TTC, or was the critical TTC already active? Is the path entry before or after it? Temporal properties only, not causes.

- A's track_001 (C): CRITICAL_TTC_START 5.55, COLLISION with C 6.60 (+1.05 s); EGO_PATH_ENTRY 5.90 after critical TTC (+0.35 s) [local times; t_global: critical_ttc_start +0.00, ego_path_entry +0.35, collision +1.05]
- B's track_001 (A): CRITICAL_TTC_START 0.50, COLLISION with A 5.55 (+5.05 s) [local times; t_global: critical_ttc_start -5.05, collision +0.00]
- C's track_001 (A): CRITICAL_TTC_START 5.55, COLLISION with A 6.60 (+1.05 s) [local times; t_global: critical_ttc_start +0.00, collision +1.05]

## Perceived state before each event, per observing recorder

Each recorder's own belief just before its events, in its own local names (track_001, ...): fusion does not rewrite it. True states are named, unknown ones end with `?`.

| t_global | Recorder | Events (local node) | Perceived state just before |
|---------:|----------|---------------------|-----------------------------|
| -5.55 | A | g01 MOVING_START(A) (A:e01)<br>g04 THROTTLE_START(A) (A:e02)<br>g08 TRACK_APPEARED_LEFT(A,C) (A:e03)<br>g10 CLOSING_START(A,C) (A:e04) | ego: not yet observed |
| -5.55 | B | g02 MOVING_START(B) (B:e01)<br>g05 THROTTLE_START(B) (B:e02)<br>g07 TRACK_APPEARED_FRONT(B,A) (B:e03)<br>g09 TRACK_APPEARED_LEFT(B,C) (B:e04)<br>g11 CLOSING_START(B,C) (B:e05) | ego: not yet observed |
| -5.55 | C | g03 MOVING_START(C) (C:e01)<br>g06 THROTTLE_START(C) (C:e02) | ego: not yet observed |
| -5.55 | A | g10 CLOSING_START(A,C) (A:e04)<br>g19 CLOSING_END(A,C) (A:e07) | ego: not yet observed |
| -5.55 | B | g11 CLOSING_START(B,C) (B:e05)<br>g34 CLOSING_END(B,C) (B:e13) | ego: not yet observed |
| -5.05 | B | g12 CRITICAL_TTC_START(B,A) (B:e06) | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH, CRITICAL_TTC?<br>track_002: CLOSING, CRITICAL_TTC? |
| -5.05 | B | g12 CRITICAL_TTC_START(B,A) (B:e06)<br>g24 COLLISION(A,B) (B:e10)<br>g25 CRITICAL_TTC_END(B,A) (B:e11) | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH, CRITICAL_TTC?<br>track_002: CLOSING, CRITICAL_TTC? |
| -2.90 | C | g13 TRACK_APPEARED_RIGHT(C,A) (C:e03)<br>g14 CLOSING_START(C,A) (C:e04) | ego: MOVING, THROTTLE |
| -2.90 | C | g13 TRACK_APPEARED_RIGHT(C,A) (C:e03)<br>g38 TRACK_LOST(C,A) (C:e08) | ego: MOVING, THROTTLE |
| -2.90 | C | g14 CLOSING_START(C,A) (C:e04)<br>g18 CLOSING_END(C,A) (C:e05) | ego: MOVING, THROTTLE |
| -1.60 | A | g15 THROTTLE_END(A) (A:e05)<br>g16 BRAKE_START(A) (A:e06) | ego: MOVING, THROTTLE<br>track_001: CLOSING |
| -1.45 | B | g17 CLOSING_START(B,A) (B:e07) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: CLOSING |
| -1.45 | B | g17 CLOSING_START(B,A) (B:e07)<br>g32 CLOSING_END(B,A) (B:e12) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: CLOSING |
| -1.00 | A | g20 BRAKE_END(A) (A:e08) | ego: MOVING, BRAKE<br>track_001: no active state |
| -0.90 | A | g21 THROTTLE_START(A) (A:e09) | ego: MOVING<br>track_001: no active state |
| -0.15 | B | g22 THROTTLE_END(B) (B:e08)<br>g23 BRAKE_START(B) (B:e09) | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH<br>track_002: CLOSING |
| +0.00 | A | g24 COLLISION(A,B) (A:e10)<br>g26 THROTTLE_END(A) (A:e11)<br>g27 BRAKE_START(A) (A:e12)<br>g28 CLOSING_START(A,C) (A:e13)<br>g30 CRITICAL_TTC_START(A,C) (A:e14) | ego: MOVING, THROTTLE<br>track_001: no active state |
| +0.00 | A | g28 CLOSING_START(A,C) (A:e13)<br>g30 CRITICAL_TTC_START(A,C) (A:e14)<br>g39 COLLISION(A,C) (A:e17)<br>g40 CRITICAL_TTC_END(A,C) (A:e18)<br>g42 CLOSING_END(A,C) (A:e19) | ego: MOVING, THROTTLE<br>track_001: no active state |
| +0.00 | C | g29 CLOSING_START(C,A) (C:e06)<br>g31 CRITICAL_TTC_START(C,A) (C:e07) | ego: MOVING, THROTTLE<br>track_001: no active state |
| +0.05 | A | g33 BRAKE_END(A) (A:e15) | ego: MOVING, BRAKE<br>track_001: CLOSING, CRITICAL_TTC |
| +0.35 | A | g35 EGO_PATH_ENTRY(A,C) (A:e16) | ego: MOVING<br>track_001: CLOSING, CRITICAL_TTC |
| +0.65 | B | g36 MOVING_END(B) (B:e14)<br>g37 STOP_START(B) (B:e15) | ego: MOVING, BRAKE<br>track_001: IN_EGO_PATH<br>track_002: no active state |
| +1.05 | C | g39 COLLISION(A,C) (C:e09)<br>g41 CRITICAL_TTC_END(C,A) (C:e09) | ego: MOVING, THROTTLE<br>track lost, states UNKNOWN: track_001 |
| +1.10 | C | g43 THROTTLE_END(C) (C:e10)<br>g44 BRAKE_START(C) (C:e11) | ego: MOVING, THROTTLE<br>track lost, states UNKNOWN: track_001 |
| +1.90 | A | g45 MOVING_END(A) (A:e20)<br>g47 STOP_START(A) (A:e21)<br>g49 BRAKE_START(A) (A:e22) | ego: MOVING<br>track_001: IN_EGO_PATH |
| +1.90 | C | g46 MOVING_END(C) (C:e12)<br>g48 STOP_START(C) (C:e13) | ego: MOVING, BRAKE<br>track lost, states UNKNOWN: track_001 |

## Plain-language reading

- 5.55 s before the reference collision, A started moving (already the case when first observed).
- 5.55 s before the reference collision, B started moving (already the case when first observed).
- 5.55 s before the reference collision, C started moving (already the case when first observed).
- 5.55 s before the reference collision, A pressed the accelerator (already the case when first observed).
- 5.55 s before the reference collision, B pressed the accelerator (already the case when first observed).
- 5.55 s before the reference collision, C pressed the accelerator (already the case when first observed).
- 5.55 s before the reference collision, B's radar started tracking A, which appeared in front of it.
- 5.55 s before the reference collision, A's radar started tracking C, which appeared on its left.
- 5.55 s before the reference collision, B's radar started tracking C, which appeared on its left.
- 5.55 s before the reference collision, A observed C start closing in (already the case when first observed).
- 5.55 s before the reference collision, B observed C start closing in (already the case when first observed).
- 5.05 s before the reference collision, B's time-to-contact with A became critical.
- 2.90 s before the reference collision, C's radar started tracking A, which appeared on its right.
- 2.90 s before the reference collision, C observed A start closing in (already the case when first observed).
- 1.60 s before the reference collision, A released the accelerator.
- 1.60 s before the reference collision, A started braking.
- 1.45 s before the reference collision, B observed A start closing in.
- 1.20 s before the reference collision, C observed A stop closing in.
- 1.15 s before the reference collision, A observed C stop closing in.
- 1.00 s before the reference collision, A released the brake.
- 0.90 s before the reference collision, A pressed the accelerator.
- 0.15 s before the reference collision, B released the accelerator.
- 0.15 s before the reference collision, B started braking.
- At the reference collision, A and B both recorded this same collision (peak impulses A: 4244, B: 4244 N*s).
- At the reference collision, B's time-to-contact with A stopped being critical.
- At the reference collision, A released the accelerator.
- At the reference collision, A started braking.
- At the reference collision, A observed C start closing in.
- At the reference collision, C observed A start closing in.
- At the reference collision, A's time-to-contact with C became critical.
- At the reference collision, C's time-to-contact with A became critical.
- 0.05 s after the reference collision, B observed A stop closing in.
- 0.05 s after the reference collision, A released the brake.
- 0.25 s after the reference collision, B observed C stop closing in.
- 0.35 s after the reference collision, A observed C enter its forward path corridor.
- 0.65 s after the reference collision, B stopped moving.
- 0.65 s after the reference collision, B came to a stop.
- 0.90 s after the reference collision, C's radar lost A (its states are UNKNOWN from then on, not ended).
- 1.05 s after the reference collision, A and C both recorded this same collision (peak impulses A: 840, C: 840 N*s).
- 1.05 s after the reference collision, A's time-to-contact with C stopped being critical.
- 1.05 s after the reference collision, C's time-to-contact with A stopped being critical.
- 1.05 s after the reference collision, A observed C stop closing in.
- 1.10 s after the reference collision, C released the accelerator.
- 1.10 s after the reference collision, C started braking.
- 1.90 s after the reference collision, A stopped moving.
- 1.90 s after the reference collision, C stopped moving.
- 1.90 s after the reference collision, A came to a stop.
- 1.90 s after the reference collision, C came to a stop.
- 1.90 s after the reference collision, A started braking.
