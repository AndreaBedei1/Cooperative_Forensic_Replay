# Global graph - S04/run_0_b_rear_first

Global time `t_global` is 0 at the reference collision. The local graphs were not modified: every node lists the local node(s) and local time(s) it comes from.

Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.

## Entities

| Entity | Kind | Details |
|--------|------|---------|
| A | recorder | clock ALIGNED; observed by others as: - |
| B | recorder | clock ALIGNED; observed by others as: A:track_001 |
| C | recorder | clock ALIGNED; observed by others as: B:track_001 |

## Graph alignment

Reference event: `collision_001` (t_global = 0); `t_global = t_local + offset_to_global`. A graph that did not report it is aligned through the chain of matched collisions linking it to the reference (multi-hop); its anchor is its own report of the last collision of that chain.

| Graph | Status | Anchor node | Anchor local time | Offset to global | Note |
|-------|--------|-------------|------------------:|-----------------:|------|
| A | ALIGNED | A:e08 | 6.25 | -6.25 | reported the reference collision collision_001 |
| B | ALIGNED | B:e13 | 6.25 | -6.25 | reported the reference collision collision_001 |
| C | ALIGNED | C:e07 | 4.70 | -6.25 | shares collision_002 with B, aligned through collision_001 -> collision_002 |

Estimated relative clock offsets: B - A = +0.000 s, C - A = +0.000 s, C - B = +0.000 s

Matched `collision_001`: A and B both recorded a collision; peak impulses 31706.31 vs 31706.31 N*s (similarity 1.000, tolerance 0.10); 1 competing report(s) within tolerance; best match kept; the two bodies touch at their reports (0.01 m apart, tolerance 1.0 m); independent relative impulse std 0.100; combined z 0.000 (gate 3.0); engineering assumption; pre-contact radar view of each recorder checked against the candidate partner's own speed: not contradicted

Matched `collision_002`: B and C both recorded a collision; peak impulses 21842.46 vs 21842.46 N*s (similarity 1.000, tolerance 0.10); 2 competing report(s) within tolerance; best match kept; the two bodies touch at their reports (0.00 m apart, tolerance 1.0 m); independent relative impulse std 0.100; combined z 0.000 (gate 3.0); engineering assumption; pre-contact radar view of each recorder checked against the candidate partner's own speed: not contradicted

## Identity associations

| Local track | Global entity | Status | Confidence | Evidence |
|-------------|---------------|--------|-----------:|----------|
| A:track_001 | B | ASSOCIATED | 1.00 | A and B both reported collision_001 (peak impulse 31706.31 vs 31706.31 N*s)<br>tracked for 6.25 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 13.0 m -> 0.1 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 0.12 m/s for reference)<br>clearance at the contact 0.00 m<br>the only track of A compatible with the contact |
| B:track_001 | C | ASSOCIATED | 0.99 | B and C both reported collision_002 at 4.70 s (peak impulse 21842.46 vs 21842.46 N*s)<br>tracked for 4.70 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 12.0 m -> 0.1 m over the last 1.0 s<br>track motion compatible with C's own speed in the observed direction (3 sigma; full-speed RMSE 0.17 m/s for reference)<br>clearance at the contact 0.10 m<br>the only track of B compatible with the contact<br>collision_001 with A at 6.25 s: not compatible (track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 11.92 m/s for reference)) |

## Nodes

| Id | Global time | Type | Actor | Subject / participants | Observed by (local node @ local time) | Details |
|----|------------:|------|-------|------------------------|----------------------------------------|---------|
| g01 | -6.25 | MOVING_START | A | - | A:e01 @ 0.00 | active_at_first_observation=True |
| g02 | -6.25 | MOVING_START | B | - | B:e01 @ 0.00 | active_at_first_observation=True |
| g03 | -6.25 | MOVING_START | C | - | C:e01 @ 0.00 | active_at_first_observation=True |
| g04 | -6.25 | THROTTLE_START | A | - | A:e02 @ 0.00 | active_at_first_observation=True |
| g05 | -6.25 | THROTTLE_START | B | - | B:e02 @ 0.00 | active_at_first_observation=True |
| g06 | -6.25 | THROTTLE_START | C | - | C:e02 @ 0.00 | active_at_first_observation=True |
| g07 | -6.25 | TRACK_APPEARED_FRONT | A | B | A:e03 @ 0.00 | initial_in_ego_path=True; source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g08 | -6.25 | TRACK_APPEARED_FRONT | B | C | B:e03 @ 0.00 | initial_in_ego_path=True; source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g09 | -5.75 | CRITICAL_TTC_START | B | C | B:e04 @ 0.50, B:e07 @ 4.70 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g10 | -3.30 | THROTTLE_END | C | - | C:e03 @ 2.95 |  |
| g11 | -3.30 | BRAKE_START | C | - | C:e04 @ 2.95 |  |
| g12 | -3.05 | CLOSING_START | B | C | B:e05 @ 3.20, B:e08 @ 4.70 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g13 | -2.20 | MOVING_END | C | - | C:e05 @ 4.05 |  |
| g14 | -2.20 | STOP_START | C | - | C:e06 @ 4.05 |  |
| g15 | -1.55 | COLLISION | - | B, C | B:e06 @ 4.70, C:e07 @ 4.70 | matched_event=collision_002; reference_event=False; peak_impulse=B 21842.46, C 21842.46 |
| g16 | -1.55 | CRITICAL_TTC_END | B | C | B:e07 @ 4.70 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g17 | -1.55 | CLOSING_END | B | C | B:e08 @ 4.70 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g18 | -1.55 | CLOSING_START | A | B | A:e04 @ 4.70, A:e10 @ 6.25 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g19 | -1.55 | CRITICAL_TTC_START | A | B | A:e05 @ 4.70, A:e09 @ 6.25 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g20 | -1.50 | THROTTLE_END | B | - | B:e09 @ 4.75 |  |
| g21 | -1.50 | BRAKE_START | B | - | B:e10 @ 4.75 |  |
| g22 | -1.40 | MOVING_END | B | - | B:e11 @ 4.85 |  |
| g23 | -1.40 | STOP_START | B | - | B:e12 @ 4.85 |  |
| g24 | -0.10 | THROTTLE_END | A | - | A:e06 @ 6.15 |  |
| g25 | -0.10 | BRAKE_START | A | - | A:e07 @ 6.15 |  |
| g26 | 0.00 | COLLISION | - | A, B | A:e08 @ 6.25, B:e13 @ 6.25 | matched_event=collision_001; reference_event=True; peak_impulse=A 31706.31, B 31706.31 |
| g27 | 0.00 | CRITICAL_TTC_END | A | B | A:e09 @ 6.25 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g28 | 0.00 | CLOSING_END | A | B | A:e10 @ 6.25 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g29 | 0.10 | MOVING_END | A | - | A:e11 @ 6.35 |  |
| g30 | 0.10 | STOP_START | A | - | A:e12 @ 6.35 |  |

## Edges

```
    g01 --PRECEDES--> g09
    g02 --PRECEDES--> g09
    g03 --PRECEDES--> g09
    g04 --PRECEDES--> g09
    g05 --PRECEDES--> g09
    g06 --PRECEDES--> g09
    g07 --PRECEDES--> g09
    g08 --PRECEDES--> g09
    g09 --PRECEDES--> g10
    g09 --PRECEDES--> g11
    g10 --PRECEDES--> g12
    g11 --PRECEDES--> g12
    g12 --PRECEDES--> g13
    g12 --PRECEDES--> g14
    g13 --PRECEDES--> g15
    g13 --PRECEDES--> g16
    g13 --PRECEDES--> g17
    g13 --PRECEDES--> g18
    g13 --PRECEDES--> g19
    g14 --PRECEDES--> g15
    g14 --PRECEDES--> g16
    g14 --PRECEDES--> g17
    g14 --PRECEDES--> g18
    g14 --PRECEDES--> g19
    g15 --PRECEDES--> g20
    g15 --PRECEDES--> g21
    g16 --PRECEDES--> g20
    g16 --PRECEDES--> g21
    g17 --PRECEDES--> g20
    g17 --PRECEDES--> g21
    g18 --PRECEDES--> g20
    g18 --PRECEDES--> g21
    g19 --PRECEDES--> g20
    g19 --PRECEDES--> g21
    g20 --PRECEDES--> g22
    g20 --PRECEDES--> g23
    g21 --PRECEDES--> g22
    g21 --PRECEDES--> g23
    g22 --PRECEDES--> g24
    g22 --PRECEDES--> g25
    g23 --PRECEDES--> g24
    g23 --PRECEDES--> g25
    g24 --PRECEDES--> g26
    g24 --PRECEDES--> g27
    g24 --PRECEDES--> g28
    g25 --PRECEDES--> g26
    g25 --PRECEDES--> g27
    g25 --PRECEDES--> g28
    g26 --PRECEDES--> g29
    g26 --PRECEDES--> g30
    g27 --PRECEDES--> g29
    g27 --PRECEDES--> g30
    g28 --PRECEDES--> g29
    g28 --PRECEDES--> g30
    g07 --SAME_TRACK--> g18
    g07 --SAME_TRACK--> g19
    g07 --SAME_TRACK--> g27
    g07 --SAME_TRACK--> g28
    g08 --SAME_TRACK--> g09
    g08 --SAME_TRACK--> g12
    g08 --SAME_TRACK--> g16
    g08 --SAME_TRACK--> g17
```

## Global trace

Events in one row are simultaneous at 0.05 s resolution: their order is unresolved.

| t_global | Events |
|---------:|--------|
| -6.25 | MOVING_START(A); MOVING_START(B); MOVING_START(C); THROTTLE_START(A); THROTTLE_START(B); THROTTLE_START(C); TRACK_APPEARED_FRONT(A,B); TRACK_APPEARED_FRONT(B,C) |
| -5.75 | CRITICAL_TTC_START(B,C) |
| -3.30 | THROTTLE_END(C); BRAKE_START(C) |
| -3.05 | CLOSING_START(B,C) |
| -2.20 | MOVING_END(C); STOP_START(C) |
| -1.55 | COLLISION(B,C); CRITICAL_TTC_END(B,C); CLOSING_END(B,C); CLOSING_START(A,B); CRITICAL_TTC_START(A,B) |
| -1.50 | THROTTLE_END(B); BRAKE_START(B) |
| -1.40 | MOVING_END(B); STOP_START(B) |
| -0.10 | THROTTLE_END(A); BRAKE_START(A) |
| +0.00 | COLLISION(A,B); CRITICAL_TTC_END(A,B); CLOSING_END(A,B) |
| +0.10 | MOVING_END(A); STOP_START(A) |

## Temporal safety relations

Per track: does the cut-in start before the critical TTC, or was the critical TTC already active? Is the path entry before or after it? Temporal properties only, not causes.

- A's track_001 (B): CRITICAL_TTC_START 4.70, COLLISION with B 6.25 (+1.55 s) [local times; t_global: critical_ttc_start -1.55, collision +0.00]
- B's track_001 (C): CRITICAL_TTC_START 0.50, COLLISION with C 4.70 (+4.20 s) [local times; t_global: critical_ttc_start -5.75, collision -1.55]

## Perceived state before each event, per observing recorder

Each recorder's own belief just before its events, in its own local names (track_001, ...): fusion does not rewrite it. True states are named, unknown ones end with `?`.

| t_global | Recorder | Events (local node) | Perceived state just before |
|---------:|----------|---------------------|-----------------------------|
| -6.25 | A | g01 MOVING_START(A) (A:e01)<br>g04 THROTTLE_START(A) (A:e02)<br>g07 TRACK_APPEARED_FRONT(A,B) (A:e03) | ego: not yet observed |
| -6.25 | B | g02 MOVING_START(B) (B:e01)<br>g05 THROTTLE_START(B) (B:e02)<br>g08 TRACK_APPEARED_FRONT(B,C) (B:e03) | ego: not yet observed |
| -6.25 | C | g03 MOVING_START(C) (C:e01)<br>g06 THROTTLE_START(C) (C:e02) | ego: not yet observed |
| -5.75 | B | g09 CRITICAL_TTC_START(B,C) (B:e04) | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH, CRITICAL_TTC? |
| -5.75 | B | g09 CRITICAL_TTC_START(B,C) (B:e04)<br>g12 CLOSING_START(B,C) (B:e05)<br>g15 COLLISION(B,C) (B:e06)<br>g16 CRITICAL_TTC_END(B,C) (B:e07)<br>g17 CLOSING_END(B,C) (B:e08) | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH, CRITICAL_TTC? |
| -3.30 | C | g10 THROTTLE_END(C) (C:e03)<br>g11 BRAKE_START(C) (C:e04) | ego: MOVING, THROTTLE |
| -3.05 | B | g12 CLOSING_START(B,C) (B:e05) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH |
| -2.20 | C | g13 MOVING_END(C) (C:e05)<br>g14 STOP_START(C) (C:e06) | ego: MOVING, BRAKE |
| -1.55 | C | g15 COLLISION(B,C) (C:e07) | ego: STOP, BRAKE |
| -1.55 | A | g18 CLOSING_START(A,B) (A:e04)<br>g19 CRITICAL_TTC_START(A,B) (A:e05) | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH |
| -1.55 | A | g18 CLOSING_START(A,B) (A:e04)<br>g19 CRITICAL_TTC_START(A,B) (A:e05)<br>g26 COLLISION(A,B) (A:e08)<br>g27 CRITICAL_TTC_END(A,B) (A:e09)<br>g28 CLOSING_END(A,B) (A:e10) | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH |
| -1.50 | B | g20 THROTTLE_END(B) (B:e09)<br>g21 BRAKE_START(B) (B:e10) | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH |
| -1.40 | B | g22 MOVING_END(B) (B:e11)<br>g23 STOP_START(B) (B:e12) | ego: MOVING, BRAKE<br>track_001: IN_EGO_PATH |
| -0.10 | A | g24 THROTTLE_END(A) (A:e06)<br>g25 BRAKE_START(A) (A:e07) | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH |
| +0.00 | B | g26 COLLISION(A,B) (B:e13) | ego: STOP, BRAKE<br>track_001: IN_EGO_PATH |
| +0.10 | A | g29 MOVING_END(A) (A:e11)<br>g30 STOP_START(A) (A:e12) | ego: MOVING, BRAKE<br>track_001: IN_EGO_PATH |

## Plain-language reading

- 6.25 s before the reference collision, A started moving (already the case when first observed).
- 6.25 s before the reference collision, B started moving (already the case when first observed).
- 6.25 s before the reference collision, C started moving (already the case when first observed).
- 6.25 s before the reference collision, A pressed the accelerator (already the case when first observed).
- 6.25 s before the reference collision, B pressed the accelerator (already the case when first observed).
- 6.25 s before the reference collision, C pressed the accelerator (already the case when first observed).
- 6.25 s before the reference collision, A's radar started tracking B, which appeared in front of it.
- 6.25 s before the reference collision, B's radar started tracking C, which appeared in front of it.
- 5.75 s before the reference collision, B's time-to-contact with C became critical.
- 3.30 s before the reference collision, C released the accelerator.
- 3.30 s before the reference collision, C started braking.
- 3.05 s before the reference collision, B observed C start closing in.
- 2.20 s before the reference collision, C stopped moving.
- 2.20 s before the reference collision, C came to a stop.
- 1.55 s before the reference collision, B and C both recorded this same collision (peak impulses B: 21842, C: 21842 N*s).
- 1.55 s before the reference collision, B's time-to-contact with C stopped being critical.
- 1.55 s before the reference collision, B observed C stop closing in.
- 1.55 s before the reference collision, A observed B start closing in.
- 1.55 s before the reference collision, A's time-to-contact with B became critical.
- 1.50 s before the reference collision, B released the accelerator.
- 1.50 s before the reference collision, B started braking.
- 1.40 s before the reference collision, B stopped moving.
- 1.40 s before the reference collision, B came to a stop.
- 0.10 s before the reference collision, A released the accelerator.
- 0.10 s before the reference collision, A started braking.
- At the reference collision, A and B both recorded this same collision (peak impulses A: 31706, B: 31706 N*s).
- At the reference collision, A's time-to-contact with B stopped being critical.
- At the reference collision, A observed B stop closing in.
- 0.10 s after the reference collision, A stopped moving.
- 0.10 s after the reference collision, A came to a stop.
