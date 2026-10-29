# Global graph - S03/run_0_crash

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
| A | ALIGNED | A:e07 | 4.10 | -4.10 | reported the reference collision collision_001 |
| B | ALIGNED | B:e07 | 4.10 | -4.10 | reported the reference collision collision_001 |

Estimated relative clock offsets: B - A = +0.000 s

Matched `collision_001`: A and B both recorded a collision; peak impulses 12137.59 vs 12137.59 N*s (similarity 1.000, tolerance 0.10); no competing report within tolerance; the two bodies touch at their reports (0.00 m apart, tolerance 1.0 m); independent relative impulse std 0.100; combined z 0.000 (gate 3.0); engineering assumption; pre-contact radar view of each recorder checked against the candidate partner's own speed: not contradicted

## Identity associations

| Local track | Global entity | Status | Confidence | Evidence |
|-------------|---------------|--------|-----------:|----------|
| A:track_001 | B | ASSOCIATED | 0.96 | A and B both reported collision_001 (peak impulse 12137.59 vs 12137.59 N*s)<br>tracked for 2.05 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 14.9 m -> 0.0 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 0.41 m/s for reference)<br>clearance at the contact 0.00 m<br>the only track of A compatible with the contact |
| B:track_001 | A | ASSOCIATED | 0.95 | B and A both reported collision_001 (peak impulse 12137.59 vs 12137.59 N*s)<br>tracked for 2.00 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 14.9 m -> 1.1 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 0.48 m/s for reference)<br>clearance at the contact 0.62 m<br>the only track of B compatible with the contact |

## Nodes

| Id | Global time | Type | Actor | Subject / participants | Observed by (local node @ local time) | Details |
|----|------------:|------|-------|------------------------|----------------------------------------|---------|
| g01 | -4.10 | MOVING_START | A | - | A:e01 @ 0.00 | active_at_first_observation=True |
| g02 | -4.10 | MOVING_START | B | - | B:e01 @ 0.00 | active_at_first_observation=True |
| g03 | -4.10 | THROTTLE_START | A | - | A:e02 @ 0.00 | active_at_first_observation=True |
| g04 | -4.10 | THROTTLE_START | B | - | B:e02 @ 0.00 | active_at_first_observation=True |
| g05 | -2.05 | TRACK_APPEARED_RIGHT | A | B | A:e03 @ 2.05 | initial_in_ego_path=False; source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g06 | -2.05 | CLOSING_START | A | B | A:e04 @ 2.05, A:e09 @ 4.10 | active_at_first_observation=True; source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g07 | -2.00 | TRACK_APPEARED_LEFT | B | A | B:e03 @ 2.10 | initial_in_ego_path=False; source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g08 | -2.00 | CLOSING_START | B | A | B:e04 @ 2.10, B:e09 @ 4.10 | active_at_first_observation=True; source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g09 | -1.55 | CRITICAL_TTC_START | A | B | A:e05 @ 2.55, A:e08 @ 4.10 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g10 | -1.50 | CRITICAL_TTC_START | B | A | B:e05 @ 2.60, B:e08 @ 4.10 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g11 | -0.10 | EGO_PATH_ENTRY | B | A | B:e06 @ 4.00 | occupancy_evidence=returns; occupancy_margin_m=0.78; occupancy_sigma_m=0.25; cause=TARGET_LATERAL; geometry=estimated_body; source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g12 | -0.05 | EGO_PATH_ENTRY | A | B | A:e06 @ 4.05 | occupancy_evidence=returns; occupancy_margin_m=0.57; occupancy_sigma_m=0.25; cause=TARGET_LATERAL; geometry=estimated_body; source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g13 | 0.00 | COLLISION | - | A, B | A:e07 @ 4.10, B:e07 @ 4.10 | matched_event=collision_001; reference_event=True; peak_impulse=A 12137.59, B 12137.59 |
| g14 | 0.00 | CRITICAL_TTC_END | A | B | A:e08 @ 4.10 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g15 | 0.00 | CRITICAL_TTC_END | B | A | B:e08 @ 4.10 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g16 | 0.00 | CLOSING_END | A | B | A:e09 @ 4.10 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g17 | 0.00 | CLOSING_END | B | A | B:e09 @ 4.10 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g18 | 0.00 | TURN_LEFT_START | A | - | A:e10 @ 4.10 |  |
| g19 | 0.00 | TURN_RIGHT_START | B | - | B:e10 @ 4.10 |  |
| g20 | 0.05 | THROTTLE_END | A | - | A:e11 @ 4.15 |  |
| g21 | 0.05 | THROTTLE_END | B | - | B:e11 @ 4.15 |  |
| g22 | 0.05 | BRAKE_START | A | - | A:e12 @ 4.15 |  |
| g23 | 0.05 | BRAKE_START | B | - | B:e12 @ 4.15 |  |
| g24 | 0.10 | CLOSING_START | B | A | B:e13 @ 4.20, B:e17 @ 4.75 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g25 | 0.15 | CLOSING_START | A | B | A:e13 @ 4.25, A:e14 @ 4.55 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g26 | 0.45 | CLOSING_END | A | B | A:e14 @ 4.55 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g27 | 0.50 | TURN_RIGHT_END | B | - | B:e14 @ 4.60 |  |
| g28 | 0.50 | MOVING_END | B | - | B:e15 @ 4.60 |  |
| g29 | 0.50 | STOP_START | B | - | B:e16 @ 4.60 |  |
| g30 | 0.60 | TURN_LEFT_END | A | - | A:e15 @ 4.70 |  |
| g31 | 0.65 | CLOSING_END | B | A | B:e17 @ 4.75 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g32 | 0.65 | MOVING_END | A | - | A:e16 @ 4.75 |  |
| g33 | 0.65 | STOP_START | A | - | A:e17 @ 4.75 |  |

## Edges

```
    g01 --PRECEDES--> g05
    g01 --PRECEDES--> g06
    g02 --PRECEDES--> g05
    g02 --PRECEDES--> g06
    g03 --PRECEDES--> g05
    g03 --PRECEDES--> g06
    g04 --PRECEDES--> g05
    g04 --PRECEDES--> g06
    g05 --PRECEDES--> g07
    g05 --PRECEDES--> g08
    g06 --PRECEDES--> g07
    g06 --PRECEDES--> g08
    g07 --PRECEDES--> g09
    g08 --PRECEDES--> g09
    g09 --PRECEDES--> g10
    g10 --PRECEDES--> g11
    g11 --PRECEDES--> g12
    g12 --PRECEDES--> g13
    g12 --PRECEDES--> g14
    g12 --PRECEDES--> g15
    g12 --PRECEDES--> g16
    g12 --PRECEDES--> g17
    g12 --PRECEDES--> g18
    g12 --PRECEDES--> g19
    g13 --PRECEDES--> g20
    g13 --PRECEDES--> g21
    g13 --PRECEDES--> g22
    g13 --PRECEDES--> g23
    g14 --PRECEDES--> g20
    g14 --PRECEDES--> g21
    g14 --PRECEDES--> g22
    g14 --PRECEDES--> g23
    g15 --PRECEDES--> g20
    g15 --PRECEDES--> g21
    g15 --PRECEDES--> g22
    g15 --PRECEDES--> g23
    g16 --PRECEDES--> g20
    g16 --PRECEDES--> g21
    g16 --PRECEDES--> g22
    g16 --PRECEDES--> g23
    g17 --PRECEDES--> g20
    g17 --PRECEDES--> g21
    g17 --PRECEDES--> g22
    g17 --PRECEDES--> g23
    g18 --PRECEDES--> g20
    g18 --PRECEDES--> g21
    g18 --PRECEDES--> g22
    g18 --PRECEDES--> g23
    g19 --PRECEDES--> g20
    g19 --PRECEDES--> g21
    g19 --PRECEDES--> g22
    g19 --PRECEDES--> g23
    g20 --PRECEDES--> g24
    g21 --PRECEDES--> g24
    g22 --PRECEDES--> g24
    g23 --PRECEDES--> g24
    g24 --PRECEDES--> g25
    g25 --PRECEDES--> g26
    g26 --PRECEDES--> g27
    g26 --PRECEDES--> g28
    g26 --PRECEDES--> g29
    g27 --PRECEDES--> g30
    g28 --PRECEDES--> g30
    g29 --PRECEDES--> g30
    g30 --PRECEDES--> g31
    g30 --PRECEDES--> g32
    g30 --PRECEDES--> g33
    g05 --SAME_TRACK--> g06
    g05 --SAME_TRACK--> g09
    g05 --SAME_TRACK--> g12
    g05 --SAME_TRACK--> g14
    g05 --SAME_TRACK--> g16
    g05 --SAME_TRACK--> g25
    g05 --SAME_TRACK--> g26
    g07 --SAME_TRACK--> g08
    g07 --SAME_TRACK--> g10
    g07 --SAME_TRACK--> g11
    g07 --SAME_TRACK--> g15
    g07 --SAME_TRACK--> g17
    g07 --SAME_TRACK--> g24
    g07 --SAME_TRACK--> g31
```

## Global trace

Events in one row are simultaneous at 0.05 s resolution: their order is unresolved.

| t_global | Events |
|---------:|--------|
| -4.10 | MOVING_START(A); MOVING_START(B); THROTTLE_START(A); THROTTLE_START(B) |
| -2.05 | TRACK_APPEARED_RIGHT(A,B); CLOSING_START(A,B) |
| -2.00 | TRACK_APPEARED_LEFT(B,A); CLOSING_START(B,A) |
| -1.55 | CRITICAL_TTC_START(A,B) |
| -1.50 | CRITICAL_TTC_START(B,A) |
| -0.10 | EGO_PATH_ENTRY(B,A) |
| -0.05 | EGO_PATH_ENTRY(A,B) |
| +0.00 | COLLISION(A,B); CRITICAL_TTC_END(A,B); CRITICAL_TTC_END(B,A); CLOSING_END(A,B); CLOSING_END(B,A); TURN_LEFT_START(A); TURN_RIGHT_START(B) |
| +0.05 | THROTTLE_END(A); THROTTLE_END(B); BRAKE_START(A); BRAKE_START(B) |
| +0.10 | CLOSING_START(B,A) |
| +0.15 | CLOSING_START(A,B) |
| +0.45 | CLOSING_END(A,B) |
| +0.50 | TURN_RIGHT_END(B); MOVING_END(B); STOP_START(B) |
| +0.60 | TURN_LEFT_END(A) |
| +0.65 | CLOSING_END(B,A); MOVING_END(A); STOP_START(A) |

## Temporal safety relations

Per track: does the cut-in start before the critical TTC, or was the critical TTC already active? Is the path entry before or after it? Temporal properties only, not causes.

- A's track_001 (B): CRITICAL_TTC_START 2.55, COLLISION with B 4.10 (+1.55 s); EGO_PATH_ENTRY 4.05 after critical TTC (+1.50 s) [local times; t_global: critical_ttc_start -1.55, ego_path_entry -0.05, collision +0.00]
- B's track_001 (A): CRITICAL_TTC_START 2.60, COLLISION with A 4.10 (+1.50 s); EGO_PATH_ENTRY 4.00 after critical TTC (+1.40 s) [local times; t_global: critical_ttc_start -1.50, ego_path_entry -0.10, collision +0.00]

## Perceived state before each event, per observing recorder

Each recorder's own belief just before its events, in its own local names (track_001, ...): fusion does not rewrite it. True states are named, unknown ones end with `?`.

| t_global | Recorder | Events (local node) | Perceived state just before |
|---------:|----------|---------------------|-----------------------------|
| -4.10 | A | g01 MOVING_START(A) (A:e01)<br>g03 THROTTLE_START(A) (A:e02) | ego: not yet observed |
| -4.10 | B | g02 MOVING_START(B) (B:e01)<br>g04 THROTTLE_START(B) (B:e02) | ego: not yet observed |
| -2.05 | A | g05 TRACK_APPEARED_RIGHT(A,B) (A:e03)<br>g06 CLOSING_START(A,B) (A:e04) | ego: MOVING, THROTTLE |
| -2.05 | A | g06 CLOSING_START(A,B) (A:e04)<br>g09 CRITICAL_TTC_START(A,B) (A:e05)<br>g13 COLLISION(A,B) (A:e07)<br>g14 CRITICAL_TTC_END(A,B) (A:e08)<br>g16 CLOSING_END(A,B) (A:e09)<br>g18 TURN_LEFT_START(A) (A:e10) | ego: MOVING, THROTTLE |
| -2.00 | B | g07 TRACK_APPEARED_LEFT(B,A) (B:e03)<br>g08 CLOSING_START(B,A) (B:e04) | ego: MOVING, THROTTLE |
| -2.00 | B | g08 CLOSING_START(B,A) (B:e04)<br>g10 CRITICAL_TTC_START(B,A) (B:e05)<br>g13 COLLISION(A,B) (B:e07)<br>g15 CRITICAL_TTC_END(B,A) (B:e08)<br>g17 CLOSING_END(B,A) (B:e09)<br>g19 TURN_RIGHT_START(B) (B:e10) | ego: MOVING, THROTTLE |
| -1.55 | A | g09 CRITICAL_TTC_START(A,B) (A:e05) | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC? |
| -1.50 | B | g10 CRITICAL_TTC_START(B,A) (B:e05) | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC? |
| -0.10 | B | g11 EGO_PATH_ENTRY(B,A) (B:e06) | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC |
| -0.05 | A | g12 EGO_PATH_ENTRY(A,B) (A:e06) | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC |
| +0.05 | A | g20 THROTTLE_END(A) (A:e11)<br>g22 BRAKE_START(A) (A:e12) | ego: MOVING, THROTTLE, TURN_LEFT<br>track_001: IN_EGO_PATH |
| +0.05 | B | g21 THROTTLE_END(B) (B:e11)<br>g23 BRAKE_START(B) (B:e12) | ego: MOVING, THROTTLE, TURN_RIGHT<br>track_001: IN_EGO_PATH |
| +0.10 | B | g24 CLOSING_START(B,A) (B:e13) | ego: MOVING, BRAKE, TURN_RIGHT<br>track_001: IN_EGO_PATH |
| +0.10 | B | g24 CLOSING_START(B,A) (B:e13)<br>g31 CLOSING_END(B,A) (B:e17) | ego: MOVING, BRAKE, TURN_RIGHT<br>track_001: IN_EGO_PATH |
| +0.15 | A | g25 CLOSING_START(A,B) (A:e13) | ego: MOVING, BRAKE, TURN_LEFT<br>track_001: IN_EGO_PATH |
| +0.15 | A | g25 CLOSING_START(A,B) (A:e13)<br>g26 CLOSING_END(A,B) (A:e14) | ego: MOVING, BRAKE, TURN_LEFT<br>track_001: IN_EGO_PATH |
| +0.50 | B | g27 TURN_RIGHT_END(B) (B:e14)<br>g28 MOVING_END(B) (B:e15)<br>g29 STOP_START(B) (B:e16) | ego: MOVING, BRAKE, TURN_RIGHT<br>track_001: CLOSING, IN_EGO_PATH |
| +0.60 | A | g30 TURN_LEFT_END(A) (A:e15) | ego: MOVING, BRAKE, TURN_LEFT<br>track_001: IN_EGO_PATH |
| +0.65 | A | g32 MOVING_END(A) (A:e16)<br>g33 STOP_START(A) (A:e17) | ego: MOVING, BRAKE<br>track_001: IN_EGO_PATH |

## Plain-language reading

- 4.10 s before the reference collision, A started moving (already the case when first observed).
- 4.10 s before the reference collision, B started moving (already the case when first observed).
- 4.10 s before the reference collision, A pressed the accelerator (already the case when first observed).
- 4.10 s before the reference collision, B pressed the accelerator (already the case when first observed).
- 2.05 s before the reference collision, A's radar started tracking B, which appeared on its right.
- 2.05 s before the reference collision, A observed B start closing in (already the case when first observed).
- 2.00 s before the reference collision, B's radar started tracking A, which appeared on its left.
- 2.00 s before the reference collision, B observed A start closing in (already the case when first observed).
- 1.55 s before the reference collision, A's time-to-contact with B became critical.
- 1.50 s before the reference collision, B's time-to-contact with A became critical.
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
- 0.45 s after the reference collision, A observed B stop closing in.
- 0.50 s after the reference collision, B stopped turning right.
- 0.50 s after the reference collision, B stopped moving.
- 0.50 s after the reference collision, B came to a stop.
- 0.60 s after the reference collision, A stopped turning left.
- 0.65 s after the reference collision, B observed A stop closing in.
- 0.65 s after the reference collision, A stopped moving.
- 0.65 s after the reference collision, A came to a stop.
