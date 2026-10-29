# Global graph - S05/run_0_crash

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
| A | ALIGNED | A:e08 | 5.90 | -5.90 | reported the reference collision collision_001 |
| B | ALIGNED | B:e12 | 5.90 | -5.90 | reported the reference collision collision_001 |
| C | ALIGNED | - | - | -5.95 | aligned through observed trajectories: the near surfaces of B:track_001 lie where their lines of sight enter the body (pooled median 0.64 sigma) at this offset; offsets within 2.00 sigma span [-5.95, -5.90] s and nothing else fits |

Estimated relative clock offsets: B - A = +0.000 s, C - A = +0.050 s, C - B = +0.050 s

Matched `collision_001`: A and B both recorded a collision; peak impulses 22183.35 vs 22183.35 N*s (similarity 1.000, tolerance 0.10); no competing report within tolerance; the two bodies touch at their reports (0.00 m apart, tolerance 1.0 m); independent relative impulse std 0.100; combined z 0.000 (gate 3.0); engineering assumption; pre-contact radar view of each recorder checked against the candidate partner's own speed: not contradicted

## Identity associations

| Local track | Global entity | Status | Confidence | Evidence |
|-------------|---------------|--------|-----------:|----------|
| A:track_001 | B | ASSOCIATED | 1.00 | A and B both reported collision_001 (peak impulse 22183.35 vs 22183.35 N*s)<br>tracked for 5.90 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 12.5 m -> 0.1 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 0.15 m/s for reference)<br>clearance at the contact 0.12 m<br>the only track of A compatible with the contact |
| B:track_001 | C | ASSOCIATED | 1.00 | B and A both reported collision_001 (peak impulse 22183.35 vs 22183.35 N*s)<br>tracked for 5.55 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 14.2 m -> 14.1 m over the last 1.0 s<br>track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 9.88 m/s for reference)<br>clearance at the contact 14.09 m (beyond 3.50 m: confidence factor 0.00)<br>common frame: its returns lie on C's own footprint (median 0.00 m, 0.00 sigma of the relative uncertainty, over 265 samples; 100% within 3 sigma) at C's own velocity |

## Nodes

| Id | Global time | Type | Actor | Subject / participants | Observed by (local node @ local time) | Details |
|----|------------:|------|-------|------------------------|----------------------------------------|---------|
| g01 | -5.95 | MOVING_START | C | - | C:e01 @ 0.00 | active_at_first_observation=True |
| g02 | -5.95 | THROTTLE_START | C | - | C:e02 @ 0.00 | active_at_first_observation=True |
| g03 | -5.90 | MOVING_START | A | - | A:e01 @ 0.00 | active_at_first_observation=True |
| g04 | -5.90 | MOVING_START | B | - | B:e01 @ 0.00 | active_at_first_observation=True |
| g05 | -5.90 | THROTTLE_START | A | - | A:e02 @ 0.00 | active_at_first_observation=True |
| g06 | -5.90 | THROTTLE_START | B | - | B:e02 @ 0.00 | active_at_first_observation=True |
| g07 | -5.90 | TRACK_APPEARED_FRONT | A | B | A:e03 @ 0.00 | initial_in_ego_path=True; source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g08 | -5.55 | TRACK_APPEARED_FRONT | B | C | B:e03 @ 0.35 | initial_in_ego_path=True; source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g09 | -5.40 | CRITICAL_TTC_START | A | B | A:e04 @ 0.50, A:e09 @ 5.90 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g10 | -3.00 | THROTTLE_END | C | - | C:e03 @ 2.95 |  |
| g11 | -3.00 | BRAKE_START | C | - | C:e04 @ 2.95 |  |
| g12 | -2.70 | CLOSING_START | B | C | B:e04 @ 3.20, B:e09 @ 4.85 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g13 | -2.50 | CRITICAL_TTC_START | B | C | B:e05 @ 3.40, B:e08 @ 4.40 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g14 | -2.25 | THROTTLE_END | B | - | B:e06 @ 3.65 |  |
| g15 | -2.25 | BRAKE_START | B | - | B:e07 @ 3.65 |  |
| g16 | -2.05 | CLOSING_START | A | B | A:e05 @ 3.85, A:e10 @ 5.90 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g17 | -1.60 | MOVING_END | C | - | C:e05 @ 4.35 |  |
| g18 | -1.60 | STOP_START | C | - | C:e06 @ 4.35 |  |
| g19 | -1.50 | CRITICAL_TTC_END | B | C | B:e08 @ 4.40 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g20 | -1.05 | CLOSING_END | B | C | B:e09 @ 4.85 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g21 | -1.05 | MOVING_END | B | - | B:e10 @ 4.85 |  |
| g22 | -1.05 | STOP_START | B | - | B:e11 @ 4.85 |  |
| g23 | -0.65 | THROTTLE_END | A | - | A:e06 @ 5.25 |  |
| g24 | -0.65 | BRAKE_START | A | - | A:e07 @ 5.25 |  |
| g25 | 0.00 | COLLISION | - | A, B | A:e08 @ 5.90, B:e12 @ 5.90 | matched_event=collision_001; reference_event=True; peak_impulse=A 22183.35, B 22183.35 |
| g26 | 0.00 | CRITICAL_TTC_END | A | B | A:e09 @ 5.90 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g27 | 0.00 | CLOSING_END | A | B | A:e10 @ 5.90 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g28 | 0.10 | MOVING_END | A | - | A:e11 @ 6.00 |  |
| g29 | 0.10 | STOP_START | A | - | A:e12 @ 6.00 |  |

## Edges

```
    g01 --PRECEDES--> g03
    g01 --PRECEDES--> g04
    g01 --PRECEDES--> g05
    g01 --PRECEDES--> g06
    g01 --PRECEDES--> g07
    g02 --PRECEDES--> g03
    g02 --PRECEDES--> g04
    g02 --PRECEDES--> g05
    g02 --PRECEDES--> g06
    g02 --PRECEDES--> g07
    g03 --PRECEDES--> g08
    g04 --PRECEDES--> g08
    g05 --PRECEDES--> g08
    g06 --PRECEDES--> g08
    g07 --PRECEDES--> g08
    g08 --PRECEDES--> g09
    g09 --PRECEDES--> g10
    g09 --PRECEDES--> g11
    g10 --PRECEDES--> g12
    g11 --PRECEDES--> g12
    g12 --PRECEDES--> g13
    g13 --PRECEDES--> g14
    g13 --PRECEDES--> g15
    g14 --PRECEDES--> g16
    g15 --PRECEDES--> g16
    g16 --PRECEDES--> g17
    g16 --PRECEDES--> g18
    g17 --PRECEDES--> g19
    g18 --PRECEDES--> g19
    g19 --PRECEDES--> g20
    g19 --PRECEDES--> g21
    g19 --PRECEDES--> g22
    g20 --PRECEDES--> g23
    g20 --PRECEDES--> g24
    g21 --PRECEDES--> g23
    g21 --PRECEDES--> g24
    g22 --PRECEDES--> g23
    g22 --PRECEDES--> g24
    g23 --PRECEDES--> g25
    g23 --PRECEDES--> g26
    g23 --PRECEDES--> g27
    g24 --PRECEDES--> g25
    g24 --PRECEDES--> g26
    g24 --PRECEDES--> g27
    g25 --PRECEDES--> g28
    g25 --PRECEDES--> g29
    g26 --PRECEDES--> g28
    g26 --PRECEDES--> g29
    g27 --PRECEDES--> g28
    g27 --PRECEDES--> g29
    g07 --SAME_TRACK--> g09
    g07 --SAME_TRACK--> g16
    g07 --SAME_TRACK--> g26
    g07 --SAME_TRACK--> g27
    g08 --SAME_TRACK--> g12
    g08 --SAME_TRACK--> g13
    g08 --SAME_TRACK--> g19
    g08 --SAME_TRACK--> g20
```

## Global trace

Events in one row are simultaneous at 0.05 s resolution: their order is unresolved.

| t_global | Events |
|---------:|--------|
| -5.95 | MOVING_START(C); THROTTLE_START(C) |
| -5.90 | MOVING_START(A); MOVING_START(B); THROTTLE_START(A); THROTTLE_START(B); TRACK_APPEARED_FRONT(A,B) |
| -5.55 | TRACK_APPEARED_FRONT(B,C) |
| -5.40 | CRITICAL_TTC_START(A,B) |
| -3.00 | THROTTLE_END(C); BRAKE_START(C) |
| -2.70 | CLOSING_START(B,C) |
| -2.50 | CRITICAL_TTC_START(B,C) |
| -2.25 | THROTTLE_END(B); BRAKE_START(B) |
| -2.05 | CLOSING_START(A,B) |
| -1.60 | MOVING_END(C); STOP_START(C) |
| -1.50 | CRITICAL_TTC_END(B,C) |
| -1.05 | CLOSING_END(B,C); MOVING_END(B); STOP_START(B) |
| -0.65 | THROTTLE_END(A); BRAKE_START(A) |
| +0.00 | COLLISION(A,B); CRITICAL_TTC_END(A,B); CLOSING_END(A,B) |
| +0.10 | MOVING_END(A); STOP_START(A) |

## Temporal safety relations

Per track: does the cut-in start before the critical TTC, or was the critical TTC already active? Is the path entry before or after it? Temporal properties only, not causes.

- A's track_001 (B): CRITICAL_TTC_START 0.50, COLLISION with B 5.90 (+5.40 s) [local times; t_global: critical_ttc_start -5.40, collision +0.00]
- B's track_001 (C): CRITICAL_TTC_START 3.40 [local times; t_global: critical_ttc_start -2.50]

## Perceived state before each event, per observing recorder

Each recorder's own belief just before its events, in its own local names (track_001, ...): fusion does not rewrite it. True states are named, unknown ones end with `?`.

| t_global | Recorder | Events (local node) | Perceived state just before |
|---------:|----------|---------------------|-----------------------------|
| -5.95 | C | g01 MOVING_START(C) (C:e01)<br>g02 THROTTLE_START(C) (C:e02) | ego: not yet observed |
| -5.90 | A | g03 MOVING_START(A) (A:e01)<br>g05 THROTTLE_START(A) (A:e02)<br>g07 TRACK_APPEARED_FRONT(A,B) (A:e03) | ego: not yet observed |
| -5.90 | B | g04 MOVING_START(B) (B:e01)<br>g06 THROTTLE_START(B) (B:e02) | ego: not yet observed |
| -5.55 | B | g08 TRACK_APPEARED_FRONT(B,C) (B:e03) | ego: MOVING, THROTTLE |
| -5.40 | A | g09 CRITICAL_TTC_START(A,B) (A:e04) | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH, CRITICAL_TTC? |
| -5.40 | A | g09 CRITICAL_TTC_START(A,B) (A:e04)<br>g16 CLOSING_START(A,B) (A:e05)<br>g25 COLLISION(A,B) (A:e08)<br>g26 CRITICAL_TTC_END(A,B) (A:e09)<br>g27 CLOSING_END(A,B) (A:e10) | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH, CRITICAL_TTC? |
| -3.00 | C | g10 THROTTLE_END(C) (C:e03)<br>g11 BRAKE_START(C) (C:e04) | ego: MOVING, THROTTLE |
| -2.70 | B | g12 CLOSING_START(B,C) (B:e04) | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH |
| -2.70 | B | g12 CLOSING_START(B,C) (B:e04)<br>g20 CLOSING_END(B,C) (B:e09)<br>g21 MOVING_END(B) (B:e10)<br>g22 STOP_START(B) (B:e11) | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH |
| -2.50 | B | g13 CRITICAL_TTC_START(B,C) (B:e05) | ego: MOVING, THROTTLE<br>track_001: CLOSING, IN_EGO_PATH |
| -2.50 | B | g13 CRITICAL_TTC_START(B,C) (B:e05)<br>g19 CRITICAL_TTC_END(B,C) (B:e08) | ego: MOVING, THROTTLE<br>track_001: CLOSING, IN_EGO_PATH |
| -2.25 | B | g14 THROTTLE_END(B) (B:e06)<br>g15 BRAKE_START(B) (B:e07) | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH |
| -2.05 | A | g16 CLOSING_START(A,B) (A:e05) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH |
| -1.60 | C | g17 MOVING_END(C) (C:e05)<br>g18 STOP_START(C) (C:e06) | ego: MOVING, BRAKE |
| -0.65 | A | g23 THROTTLE_END(A) (A:e06)<br>g24 BRAKE_START(A) (A:e07) | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH |
| +0.00 | B | g25 COLLISION(A,B) (B:e12) | ego: STOP, BRAKE<br>track_001: IN_EGO_PATH |
| +0.10 | A | g28 MOVING_END(A) (A:e11)<br>g29 STOP_START(A) (A:e12) | ego: MOVING, BRAKE<br>track_001: IN_EGO_PATH |

## Plain-language reading

- 5.95 s before the reference collision, C started moving (already the case when first observed).
- 5.95 s before the reference collision, C pressed the accelerator (already the case when first observed).
- 5.90 s before the reference collision, A started moving (already the case when first observed).
- 5.90 s before the reference collision, B started moving (already the case when first observed).
- 5.90 s before the reference collision, A pressed the accelerator (already the case when first observed).
- 5.90 s before the reference collision, B pressed the accelerator (already the case when first observed).
- 5.90 s before the reference collision, A's radar started tracking B, which appeared in front of it.
- 5.55 s before the reference collision, B's radar started tracking C, which appeared in front of it.
- 5.40 s before the reference collision, A's time-to-contact with B became critical.
- 3.00 s before the reference collision, C released the accelerator.
- 3.00 s before the reference collision, C started braking.
- 2.70 s before the reference collision, B observed C start closing in.
- 2.50 s before the reference collision, B's time-to-contact with C became critical.
- 2.25 s before the reference collision, B released the accelerator.
- 2.25 s before the reference collision, B started braking.
- 2.05 s before the reference collision, A observed B start closing in.
- 1.60 s before the reference collision, C stopped moving.
- 1.60 s before the reference collision, C came to a stop.
- 1.50 s before the reference collision, B's time-to-contact with C stopped being critical.
- 1.05 s before the reference collision, B observed C stop closing in.
- 1.05 s before the reference collision, B stopped moving.
- 1.05 s before the reference collision, B came to a stop.
- 0.65 s before the reference collision, A released the accelerator.
- 0.65 s before the reference collision, A started braking.
- At the reference collision, A and B both recorded this same collision (peak impulses A: 22183, B: 22183 N*s).
- At the reference collision, A's time-to-contact with B stopped being critical.
- At the reference collision, A observed B stop closing in.
- 0.10 s after the reference collision, A stopped moving.
- 0.10 s after the reference collision, A came to a stop.
