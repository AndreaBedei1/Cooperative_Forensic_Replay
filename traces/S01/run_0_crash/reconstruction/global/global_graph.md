# Global graph - S01/run_0_crash

Global time `t_global` is 0 at the reference collision. The local graphs were not modified: every node lists the local node(s) and local time(s) it comes from.

Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.

## Entities

| Entity | Kind | Details |
|--------|------|---------|
| A | recorder | clock ALIGNED; observed by others as: - |
| B | recorder | clock ALIGNED; observed by others as: A:track_001 |

## Graph alignment

Reference event: `collision_001` (t_global = 0); `t_global = t_local + offset_to_global`. A graph that did not report it is aligned through the chain of matched collisions linking it to the reference (multi-hop); its anchor is its own report of the last collision of that chain.

| Graph | Status | Anchor node | Anchor local time | Offset to global | Note |
|-------|--------|-------------|------------------:|-----------------:|------|
| A | ALIGNED | A:e08 | 6.75 | -6.75 | reported the reference collision collision_001 |
| B | ALIGNED | B:e07 | 6.75 | -6.75 | reported the reference collision collision_001 |

Estimated relative clock offsets: B - A = +0.000 s

Matched `collision_001`: A and B both recorded a collision; peak impulses 14394.11 vs 14394.11 N*s (similarity 1.000, tolerance 0.10); no competing report within tolerance; the two bodies touch at their reports (0.00 m apart, tolerance 1.0 m); independent relative impulse std 0.100; combined z 0.000 (gate 3.0); engineering assumption; pre-contact radar view of each recorder checked against the candidate partner's own speed: not contradicted

## Identity associations

| Local track | Global entity | Status | Confidence | Evidence |
|-------------|---------------|--------|-----------:|----------|
| A:track_001 | B | ASSOCIATED | 1.00 | A and B both reported collision_001 (peak impulse 14394.11 vs 14394.11 N*s)<br>tracked for 6.75 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 9.3 m -> 0.2 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 0.10 m/s for reference)<br>clearance at the contact 0.24 m<br>the only track of A compatible with the contact |

## Nodes

| Id | Global time | Type | Actor | Subject / participants | Observed by (local node @ local time) | Details |
|----|------------:|------|-------|------------------------|----------------------------------------|---------|
| g01 | -6.75 | MOVING_START | A | - | A:e01 @ 0.00 | active_at_first_observation=True |
| g02 | -6.75 | MOVING_START | B | - | B:e01 @ 0.00 | active_at_first_observation=True |
| g03 | -6.75 | THROTTLE_START | A | - | A:e02 @ 0.00 | active_at_first_observation=True |
| g04 | -6.75 | THROTTLE_START | B | - | B:e02 @ 0.00 | active_at_first_observation=True |
| g05 | -6.75 | TRACK_APPEARED_FRONT | A | B | A:e03 @ 0.00 | initial_in_ego_path=True; source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g06 | -2.80 | THROTTLE_END | B | - | B:e03 @ 3.95 |  |
| g07 | -2.80 | BRAKE_START | B | - | B:e04 @ 3.95 |  |
| g08 | -2.55 | CLOSING_START | A | B | A:e04 @ 4.20, A:e10 @ 6.75 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g09 | -2.35 | CRITICAL_TTC_START | A | B | A:e05 @ 4.40, A:e09 @ 6.75 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g10 | -1.60 | MOVING_END | B | - | B:e05 @ 5.15 |  |
| g11 | -1.60 | STOP_START | B | - | B:e06 @ 5.15 |  |
| g12 | -1.20 | THROTTLE_END | A | - | A:e06 @ 5.55 |  |
| g13 | -1.20 | BRAKE_START | A | - | A:e07 @ 5.55 |  |
| g14 | 0.00 | COLLISION | - | A, B | A:e08 @ 6.75, B:e07 @ 6.75 | matched_event=collision_001; reference_event=True; peak_impulse=A 14394.11, B 14394.11 |
| g15 | 0.00 | CRITICAL_TTC_END | A | B | A:e09 @ 6.75 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g16 | 0.00 | CLOSING_END | A | B | A:e10 @ 6.75 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g17 | 0.05 | MOVING_END | A | - | A:e11 @ 6.80 |  |
| g18 | 0.05 | STOP_START | A | - | A:e12 @ 6.80 |  |

## Edges

```
    g01 --PRECEDES--> g06
    g01 --PRECEDES--> g07
    g02 --PRECEDES--> g06
    g02 --PRECEDES--> g07
    g03 --PRECEDES--> g06
    g03 --PRECEDES--> g07
    g04 --PRECEDES--> g06
    g04 --PRECEDES--> g07
    g05 --PRECEDES--> g06
    g05 --PRECEDES--> g07
    g06 --PRECEDES--> g08
    g07 --PRECEDES--> g08
    g08 --PRECEDES--> g09
    g09 --PRECEDES--> g10
    g09 --PRECEDES--> g11
    g10 --PRECEDES--> g12
    g10 --PRECEDES--> g13
    g11 --PRECEDES--> g12
    g11 --PRECEDES--> g13
    g12 --PRECEDES--> g14
    g12 --PRECEDES--> g15
    g12 --PRECEDES--> g16
    g13 --PRECEDES--> g14
    g13 --PRECEDES--> g15
    g13 --PRECEDES--> g16
    g14 --PRECEDES--> g17
    g14 --PRECEDES--> g18
    g15 --PRECEDES--> g17
    g15 --PRECEDES--> g18
    g16 --PRECEDES--> g17
    g16 --PRECEDES--> g18
    g05 --SAME_TRACK--> g08
    g05 --SAME_TRACK--> g09
    g05 --SAME_TRACK--> g15
    g05 --SAME_TRACK--> g16
```

## Global trace

Events in one row are simultaneous at 0.05 s resolution: their order is unresolved.

| t_global | Events |
|---------:|--------|
| -6.75 | MOVING_START(A); MOVING_START(B); THROTTLE_START(A); THROTTLE_START(B); TRACK_APPEARED_FRONT(A,B) |
| -2.80 | THROTTLE_END(B); BRAKE_START(B) |
| -2.55 | CLOSING_START(A,B) |
| -2.35 | CRITICAL_TTC_START(A,B) |
| -1.60 | MOVING_END(B); STOP_START(B) |
| -1.20 | THROTTLE_END(A); BRAKE_START(A) |
| +0.00 | COLLISION(A,B); CRITICAL_TTC_END(A,B); CLOSING_END(A,B) |
| +0.05 | MOVING_END(A); STOP_START(A) |

## Temporal safety relations

Per track: does the cut-in start before the critical TTC, or was the critical TTC already active? Is the path entry before or after it? Temporal properties only, not causes.

- A's track_001 (B): CRITICAL_TTC_START 4.40, COLLISION with B 6.75 (+2.35 s) [local times; t_global: critical_ttc_start -2.35, collision +0.00]

## Perceived state before each event, per observing recorder

Each recorder's own belief just before its events, in its own local names (track_001, ...): fusion does not rewrite it. True states are named, unknown ones end with `?`.

| t_global | Recorder | Events (local node) | Perceived state just before |
|---------:|----------|---------------------|-----------------------------|
| -6.75 | A | g01 MOVING_START(A) (A:e01)<br>g03 THROTTLE_START(A) (A:e02)<br>g05 TRACK_APPEARED_FRONT(A,B) (A:e03) | ego: not yet observed |
| -6.75 | B | g02 MOVING_START(B) (B:e01)<br>g04 THROTTLE_START(B) (B:e02) | ego: not yet observed |
| -2.80 | B | g06 THROTTLE_END(B) (B:e03)<br>g07 BRAKE_START(B) (B:e04) | ego: MOVING, THROTTLE |
| -2.55 | A | g08 CLOSING_START(A,B) (A:e04) | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH |
| -2.55 | A | g08 CLOSING_START(A,B) (A:e04)<br>g09 CRITICAL_TTC_START(A,B) (A:e05)<br>g14 COLLISION(A,B) (A:e08)<br>g15 CRITICAL_TTC_END(A,B) (A:e09)<br>g16 CLOSING_END(A,B) (A:e10) | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH |
| -2.35 | A | g09 CRITICAL_TTC_START(A,B) (A:e05) | ego: MOVING, THROTTLE<br>track_001: CLOSING, IN_EGO_PATH |
| -1.60 | B | g10 MOVING_END(B) (B:e05)<br>g11 STOP_START(B) (B:e06) | ego: MOVING, BRAKE |
| -1.20 | A | g12 THROTTLE_END(A) (A:e06)<br>g13 BRAKE_START(A) (A:e07) | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH |
| +0.00 | B | g14 COLLISION(A,B) (B:e07) | ego: STOP, BRAKE |
| +0.05 | A | g17 MOVING_END(A) (A:e11)<br>g18 STOP_START(A) (A:e12) | ego: MOVING, BRAKE<br>track_001: IN_EGO_PATH |

## Plain-language reading

- 6.75 s before the reference collision, A started moving (already the case when first observed).
- 6.75 s before the reference collision, B started moving (already the case when first observed).
- 6.75 s before the reference collision, A pressed the accelerator (already the case when first observed).
- 6.75 s before the reference collision, B pressed the accelerator (already the case when first observed).
- 6.75 s before the reference collision, A's radar started tracking B, which appeared in front of it.
- 2.80 s before the reference collision, B released the accelerator.
- 2.80 s before the reference collision, B started braking.
- 2.55 s before the reference collision, A observed B start closing in.
- 2.35 s before the reference collision, A's time-to-contact with B became critical.
- 1.60 s before the reference collision, B stopped moving.
- 1.60 s before the reference collision, B came to a stop.
- 1.20 s before the reference collision, A released the accelerator.
- 1.20 s before the reference collision, A started braking.
- At the reference collision, A and B both recorded this same collision (peak impulses A: 14394, B: 14394 N*s).
- At the reference collision, A's time-to-contact with B stopped being critical.
- At the reference collision, A observed B stop closing in.
- 0.05 s after the reference collision, A stopped moving.
- 0.05 s after the reference collision, A came to a stop.
