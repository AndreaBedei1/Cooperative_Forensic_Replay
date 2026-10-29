# Global graph - S07/run_0_merge_conflict

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
| A | ALIGNED | A:e10 | 19.25 | -19.25 | reported the reference collision collision_001 |
| B | ALIGNED | B:e11 | 19.25 | -19.25 | reported the reference collision collision_001 |

Estimated relative clock offsets: B - A = +0.000 s

Matched `collision_001`: A and B both recorded a collision; peak impulses 1928.22 vs 1928.22 N*s (similarity 1.000, tolerance 0.10); no competing report within tolerance; the two bodies touch at their reports (0.00 m apart, tolerance 1.0 m); independent relative impulse std 0.100; combined z 0.000 (gate 3.0); engineering assumption; pre-contact radar view of each recorder checked against the candidate partner's own speed: not contradicted

## Identity associations

| Local track | Global entity | Status | Confidence | Evidence |
|-------------|---------------|--------|-----------:|----------|
| A:track_001 | B | ASSOCIATED | 0.98 | A and B both reported collision_001 (peak impulse 1928.22 vs 1928.22 N*s)<br>tracked for 7.60 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 3.4 m -> 0.4 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 0.26 m/s for reference)<br>clearance at the contact 0.36 m<br>the only track of A compatible with the contact |
| B:track_001 | A | ASSOCIATED | 0.98 | B and A both reported collision_001 (peak impulse 1928.22 vs 1928.22 N*s)<br>tracked for 6.95 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 2.7 m -> 0.1 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 0.31 m/s for reference)<br>clearance at the contact 0.07 m<br>the only track of B compatible with the contact |

## Nodes

| Id | Global time | Type | Actor | Subject / participants | Observed by (local node @ local time) | Details |
|----|------------:|------|-------|------------------------|----------------------------------------|---------|
| g01 | -19.25 | MOVING_START | A | - | A:e01 @ 0.00 | active_at_first_observation=True |
| g02 | -19.25 | MOVING_START | B | - | B:e01 @ 0.00 | active_at_first_observation=True |
| g03 | -19.25 | THROTTLE_START | A | - | A:e02 @ 0.00 | active_at_first_observation=True |
| g04 | -19.25 | THROTTLE_START | B | - | B:e02 @ 0.00 | active_at_first_observation=True |
| g05 | -18.25 | INDICATOR_LEFT_START | A | - | A:e03 @ 1.00 |  |
| g06 | -16.00 | TURN_RIGHT_START | A | - | A:e04 @ 3.25 |  |
| g07 | -14.05 | TURN_RIGHT_END | A | - | A:e05 @ 5.20 |  |
| g08 | -12.90 | TURN_LEFT_START | A | - | A:e06 @ 6.35 |  |
| g09 | -7.60 | TRACK_APPEARED_LEFT | A | B | A:e07 @ 11.65 | initial_in_ego_path=False; source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g10 | -7.60 | CLOSING_START | A | B | A:e08 @ 11.65, A:e12 @ 19.25 | active_at_first_observation=True; source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g11 | -6.95 | TRACK_APPEARED_LEFT | B | A | B:e03 @ 12.30 | initial_in_ego_path=False; source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g12 | -6.95 | CLOSING_START | B | A | B:e04 @ 12.30, B:e13 @ 19.25 | active_at_first_observation=True; source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g13 | -6.25 | INDICATOR_RIGHT_START | B | - | B:e05 @ 13.00 |  |
| g14 | -3.75 | CRITICAL_TTC_START | B | A | B:e06 @ 15.50, B:e12 @ 19.25 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g15 | -3.40 | CRITICAL_TTC_START | A | B | A:e09 @ 15.85, A:e11 @ 19.25 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g16 | -2.35 | TURN_RIGHT_START | B | - | B:e07 @ 16.90 |  |
| g17 | -0.30 | TURN_RIGHT_END | B | - | B:e08 @ 18.95 |  |
| g18 | -0.15 | INDICATOR_RIGHT_END | B | - | B:e09 @ 19.10 |  |
| g19 | -0.15 | EGO_PATH_ENTRY | B | A | B:e10 @ 19.10 | occupancy_evidence=returns; occupancy_margin_m=0.44; occupancy_sigma_m=0.25; cause=MUTUAL_LATERAL; geometry=estimated_body; source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g20 | 0.00 | COLLISION | - | A, B | A:e10 @ 19.25, B:e11 @ 19.25 | matched_event=collision_001; reference_event=True; peak_impulse=A 1928.22, B 1928.22 |
| g21 | 0.00 | CRITICAL_TTC_END | A | B | A:e11 @ 19.25 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g22 | 0.00 | CRITICAL_TTC_END | B | A | B:e12 @ 19.25 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g23 | 0.00 | CLOSING_END | A | B | A:e12 @ 19.25 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g24 | 0.00 | CLOSING_END | B | A | B:e13 @ 19.25 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g25 | 0.05 | THROTTLE_END | A | - | A:e13 @ 19.30 |  |
| g26 | 0.05 | THROTTLE_END | B | - | B:e14 @ 19.30 |  |
| g27 | 0.05 | BRAKE_START | A | - | A:e14 @ 19.30 |  |
| g28 | 0.05 | BRAKE_START | B | - | B:e15 @ 19.30 |  |
| g29 | 0.25 | TURN_LEFT_END | A | - | A:e15 @ 19.50 |  |
| g30 | 0.75 | MOVING_END | B | - | B:e16 @ 20.00 |  |
| g31 | 0.75 | STOP_START | B | - | B:e17 @ 20.00 |  |
| g32 | 0.80 | MOVING_END | A | - | A:e16 @ 20.05 |  |
| g33 | 0.80 | STOP_START | A | - | A:e17 @ 20.05 |  |

## Edges

```
    g01 --PRECEDES--> g05
    g02 --PRECEDES--> g05
    g03 --PRECEDES--> g05
    g04 --PRECEDES--> g05
    g05 --PRECEDES--> g06
    g06 --PRECEDES--> g07
    g07 --PRECEDES--> g08
    g08 --PRECEDES--> g09
    g08 --PRECEDES--> g10
    g09 --PRECEDES--> g11
    g09 --PRECEDES--> g12
    g10 --PRECEDES--> g11
    g10 --PRECEDES--> g12
    g11 --PRECEDES--> g13
    g12 --PRECEDES--> g13
    g13 --PRECEDES--> g14
    g14 --PRECEDES--> g15
    g15 --PRECEDES--> g16
    g16 --PRECEDES--> g17
    g17 --PRECEDES--> g18
    g17 --PRECEDES--> g19
    g18 --PRECEDES--> g20
    g18 --PRECEDES--> g21
    g18 --PRECEDES--> g22
    g18 --PRECEDES--> g23
    g18 --PRECEDES--> g24
    g19 --PRECEDES--> g20
    g19 --PRECEDES--> g21
    g19 --PRECEDES--> g22
    g19 --PRECEDES--> g23
    g19 --PRECEDES--> g24
    g20 --PRECEDES--> g25
    g20 --PRECEDES--> g26
    g20 --PRECEDES--> g27
    g20 --PRECEDES--> g28
    g21 --PRECEDES--> g25
    g21 --PRECEDES--> g26
    g21 --PRECEDES--> g27
    g21 --PRECEDES--> g28
    g22 --PRECEDES--> g25
    g22 --PRECEDES--> g26
    g22 --PRECEDES--> g27
    g22 --PRECEDES--> g28
    g23 --PRECEDES--> g25
    g23 --PRECEDES--> g26
    g23 --PRECEDES--> g27
    g23 --PRECEDES--> g28
    g24 --PRECEDES--> g25
    g24 --PRECEDES--> g26
    g24 --PRECEDES--> g27
    g24 --PRECEDES--> g28
    g25 --PRECEDES--> g29
    g26 --PRECEDES--> g29
    g27 --PRECEDES--> g29
    g28 --PRECEDES--> g29
    g29 --PRECEDES--> g30
    g29 --PRECEDES--> g31
    g30 --PRECEDES--> g32
    g30 --PRECEDES--> g33
    g31 --PRECEDES--> g32
    g31 --PRECEDES--> g33
    g09 --SAME_TRACK--> g10
    g09 --SAME_TRACK--> g15
    g09 --SAME_TRACK--> g21
    g09 --SAME_TRACK--> g23
    g11 --SAME_TRACK--> g12
    g11 --SAME_TRACK--> g14
    g11 --SAME_TRACK--> g19
    g11 --SAME_TRACK--> g22
    g11 --SAME_TRACK--> g24
```

## Global trace

Events in one row are simultaneous at 0.05 s resolution: their order is unresolved.

| t_global | Events |
|---------:|--------|
| -19.25 | MOVING_START(A); MOVING_START(B); THROTTLE_START(A); THROTTLE_START(B) |
| -18.25 | INDICATOR_LEFT_START(A) |
| -16.00 | TURN_RIGHT_START(A) |
| -14.05 | TURN_RIGHT_END(A) |
| -12.90 | TURN_LEFT_START(A) |
| -7.60 | TRACK_APPEARED_LEFT(A,B); CLOSING_START(A,B) |
| -6.95 | TRACK_APPEARED_LEFT(B,A); CLOSING_START(B,A) |
| -6.25 | INDICATOR_RIGHT_START(B) |
| -3.75 | CRITICAL_TTC_START(B,A) |
| -3.40 | CRITICAL_TTC_START(A,B) |
| -2.35 | TURN_RIGHT_START(B) |
| -0.30 | TURN_RIGHT_END(B) |
| -0.15 | INDICATOR_RIGHT_END(B); EGO_PATH_ENTRY(B,A) |
| +0.00 | COLLISION(A,B); CRITICAL_TTC_END(A,B); CRITICAL_TTC_END(B,A); CLOSING_END(A,B); CLOSING_END(B,A) |
| +0.05 | THROTTLE_END(A); THROTTLE_END(B); BRAKE_START(A); BRAKE_START(B) |
| +0.25 | TURN_LEFT_END(A) |
| +0.75 | MOVING_END(B); STOP_START(B) |
| +0.80 | MOVING_END(A); STOP_START(A) |

## Temporal safety relations

Per track: does the cut-in start before the critical TTC, or was the critical TTC already active? Is the path entry before or after it? Temporal properties only, not causes.

- A's track_001 (B): CRITICAL_TTC_START 15.85, COLLISION with B 19.25 (+3.40 s) [local times; t_global: critical_ttc_start -3.40, collision +0.00]
- B's track_001 (A): CRITICAL_TTC_START 15.50, COLLISION with A 19.25 (+3.75 s); EGO_PATH_ENTRY 19.10 after critical TTC (+3.60 s) [local times; t_global: critical_ttc_start -3.75, ego_path_entry -0.15, collision +0.00]

## Perceived state before each event, per observing recorder

Each recorder's own belief just before its events, in its own local names (track_001, ...): fusion does not rewrite it. True states are named, unknown ones end with `?`.

| t_global | Recorder | Events (local node) | Perceived state just before |
|---------:|----------|---------------------|-----------------------------|
| -19.25 | A | g01 MOVING_START(A) (A:e01)<br>g03 THROTTLE_START(A) (A:e02) | ego: not yet observed |
| -19.25 | B | g02 MOVING_START(B) (B:e01)<br>g04 THROTTLE_START(B) (B:e02) | ego: not yet observed |
| -18.25 | A | g05 INDICATOR_LEFT_START(A) (A:e03) | ego: MOVING, THROTTLE |
| -16.00 | A | g06 TURN_RIGHT_START(A) (A:e04) | ego: MOVING, THROTTLE, INDICATOR_LEFT |
| -14.05 | A | g07 TURN_RIGHT_END(A) (A:e05) | ego: MOVING, THROTTLE, TURN_RIGHT, INDICATOR_LEFT |
| -12.90 | A | g08 TURN_LEFT_START(A) (A:e06) | ego: MOVING, THROTTLE, INDICATOR_LEFT |
| -7.60 | A | g09 TRACK_APPEARED_LEFT(A,B) (A:e07)<br>g10 CLOSING_START(A,B) (A:e08) | ego: MOVING, THROTTLE, TURN_LEFT, INDICATOR_LEFT |
| -7.60 | A | g10 CLOSING_START(A,B) (A:e08)<br>g15 CRITICAL_TTC_START(A,B) (A:e09)<br>g20 COLLISION(A,B) (A:e10)<br>g21 CRITICAL_TTC_END(A,B) (A:e11)<br>g23 CLOSING_END(A,B) (A:e12) | ego: MOVING, THROTTLE, TURN_LEFT, INDICATOR_LEFT |
| -6.95 | B | g11 TRACK_APPEARED_LEFT(B,A) (B:e03)<br>g12 CLOSING_START(B,A) (B:e04) | ego: MOVING, THROTTLE |
| -6.95 | B | g12 CLOSING_START(B,A) (B:e04)<br>g14 CRITICAL_TTC_START(B,A) (B:e06)<br>g20 COLLISION(A,B) (B:e11)<br>g22 CRITICAL_TTC_END(B,A) (B:e12)<br>g24 CLOSING_END(B,A) (B:e13) | ego: MOVING, THROTTLE |
| -6.25 | B | g13 INDICATOR_RIGHT_START(B) (B:e05) | ego: MOVING, THROTTLE<br>track_001: CLOSING |
| -3.75 | B | g14 CRITICAL_TTC_START(B,A) (B:e06) | ego: MOVING, THROTTLE, INDICATOR_RIGHT<br>track_001: CLOSING |
| -3.40 | A | g15 CRITICAL_TTC_START(A,B) (A:e09) | ego: MOVING, THROTTLE, TURN_LEFT, INDICATOR_LEFT<br>track_001: CLOSING |
| -2.35 | B | g16 TURN_RIGHT_START(B) (B:e07) | ego: MOVING, THROTTLE, INDICATOR_RIGHT<br>track_001: CLOSING, CRITICAL_TTC |
| -0.30 | B | g17 TURN_RIGHT_END(B) (B:e08) | ego: MOVING, THROTTLE, TURN_RIGHT, INDICATOR_RIGHT<br>track_001: CLOSING, CRITICAL_TTC |
| -0.15 | B | g18 INDICATOR_RIGHT_END(B) (B:e09)<br>g19 EGO_PATH_ENTRY(B,A) (B:e10) | ego: MOVING, THROTTLE, INDICATOR_RIGHT<br>track_001: CLOSING, CRITICAL_TTC |
| +0.05 | A | g25 THROTTLE_END(A) (A:e13)<br>g27 BRAKE_START(A) (A:e14) | ego: MOVING, THROTTLE, TURN_LEFT, INDICATOR_LEFT<br>track_001: no active state |
| +0.05 | B | g26 THROTTLE_END(B) (B:e14)<br>g28 BRAKE_START(B) (B:e15) | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH |
| +0.25 | A | g29 TURN_LEFT_END(A) (A:e15) | ego: MOVING, BRAKE, TURN_LEFT, INDICATOR_LEFT<br>track_001: no active state |
| +0.75 | B | g30 MOVING_END(B) (B:e16)<br>g31 STOP_START(B) (B:e17) | ego: MOVING, BRAKE<br>track_001: IN_EGO_PATH |
| +0.80 | A | g32 MOVING_END(A) (A:e16)<br>g33 STOP_START(A) (A:e17) | ego: MOVING, BRAKE, INDICATOR_LEFT<br>track_001: no active state |

## Plain-language reading

- 19.25 s before the reference collision, A started moving (already the case when first observed).
- 19.25 s before the reference collision, B started moving (already the case when first observed).
- 19.25 s before the reference collision, A pressed the accelerator (already the case when first observed).
- 19.25 s before the reference collision, B pressed the accelerator (already the case when first observed).
- 18.25 s before the reference collision, A switched on its left turn indicator.
- 16.00 s before the reference collision, A started turning right.
- 14.05 s before the reference collision, A stopped turning right.
- 12.90 s before the reference collision, A started turning left.
- 7.60 s before the reference collision, A's radar started tracking B, which appeared on its left.
- 7.60 s before the reference collision, A observed B start closing in (already the case when first observed).
- 6.95 s before the reference collision, B's radar started tracking A, which appeared on its left.
- 6.95 s before the reference collision, B observed A start closing in (already the case when first observed).
- 6.25 s before the reference collision, B switched on its right turn indicator.
- 3.75 s before the reference collision, B's time-to-contact with A became critical.
- 3.40 s before the reference collision, A's time-to-contact with B became critical.
- 2.35 s before the reference collision, B started turning right.
- 0.30 s before the reference collision, B stopped turning right.
- 0.15 s before the reference collision, B switched off its right turn indicator.
- 0.15 s before the reference collision, B observed A enter its forward path corridor.
- At the reference collision, A and B both recorded this same collision (peak impulses A: 1928, B: 1928 N*s).
- At the reference collision, A's time-to-contact with B stopped being critical.
- At the reference collision, B's time-to-contact with A stopped being critical.
- At the reference collision, A observed B stop closing in.
- At the reference collision, B observed A stop closing in.
- 0.05 s after the reference collision, A released the accelerator.
- 0.05 s after the reference collision, B released the accelerator.
- 0.05 s after the reference collision, A started braking.
- 0.05 s after the reference collision, B started braking.
- 0.25 s after the reference collision, A stopped turning left.
- 0.75 s after the reference collision, B stopped moving.
- 0.75 s after the reference collision, B came to a stop.
- 0.80 s after the reference collision, A stopped moving.
- 0.80 s after the reference collision, A came to a stop.
