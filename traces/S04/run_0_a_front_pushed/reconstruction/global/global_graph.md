# Global graph - S04/run_0_a_front_pushed

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
| A | ALIGNED | A:e08 | 4.80 | -4.80 | reported the reference collision collision_001 |
| B | ALIGNED | B:e08 | 4.80 | -4.80 | reported the reference collision collision_001 |
| C | ALIGNED | C:e07 | 5.30 | -4.80 | shares collision_003 with B, aligned through collision_001 -> collision_003 |

Estimated relative clock offsets: B - A = +0.000 s, C - A = +0.000 s, C - B = +0.000 s

Matched `collision_001`: A and B both recorded a collision; peak impulses 10281.41 vs 10281.41 N*s (similarity 1.000, tolerance 0.10); 1 competing report(s) within tolerance; best match kept; the two bodies touch at their reports (0.00 m apart, tolerance 1.0 m); independent relative impulse std 0.100; combined z 0.000 (gate 3.0); engineering assumption; pre-contact radar view of each recorder checked against the candidate partner's own speed: not contradicted

Matched `collision_002`: A recorded a collision; B recorded the same impulse as a burst within its contact B:e10, merged there by its own sensor; peak impulses 1509.76 vs 1509.76 N*s (similarity 1.000, tolerance 0.10); consistent with the clock offset between A and B that earlier matches fix (+0.000 s, tolerance 0.10 s); pre-contact radar view of each recorder checked against the candidate partner's own speed: not contradicted

Matched `collision_003`: B and C both recorded a collision; peak impulses 8788.05 vs 8788.05 N*s (similarity 1.000, tolerance 0.10); 1 competing report(s) within tolerance; best match kept; the two bodies touch at their reports (0.00 m apart, tolerance 1.0 m); independent relative impulse std 0.100; combined z 0.000 (gate 3.0); engineering assumption; pre-contact radar view of each recorder checked against the candidate partner's own speed: not contradicted

## Identity associations

| Local track | Global entity | Status | Confidence | Evidence |
|-------------|---------------|--------|-----------:|----------|
| A:track_001 | B | ASSOCIATED | 0.99 | A and B both reported collision_001 at 4.80 s (peak impulse 10281.41 vs 10281.41 N*s)<br>tracked for 4.80 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 4.5 m -> 0.0 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 0.18 m/s for reference)<br>clearance at the contact 0.00 m<br>the only track of A compatible with the contact<br>collision_002 with B at 5.45 s: also compatible |
| B:track_001 | C | ASSOCIATED | 0.99 | B and C both reported collision_003 at 5.30 s (peak impulse 8788.05 vs 8788.05 N*s)<br>tracked for 5.30 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 6.4 m -> 0.1 m over the last 1.0 s<br>track motion compatible with C's own speed in the observed direction (3 sigma; full-speed RMSE 0.17 m/s for reference)<br>clearance at the contact 0.06 m<br>the only track of B compatible with the contact<br>collision_001 with A at 4.80 s: not compatible (track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 7.54 m/s for reference))<br>collision_002 with A at 5.45 s: not compatible (track motion contradicts A's own speed in the observed direction (3 sigma; full-speed RMSE 7.90 m/s for reference)) |

## Nodes

| Id | Global time | Type | Actor | Subject / participants | Observed by (local node @ local time) | Details |
|----|------------:|------|-------|------------------------|----------------------------------------|---------|
| g01 | -4.80 | MOVING_START | A | - | A:e01 @ 0.00 | active_at_first_observation=True |
| g02 | -4.80 | MOVING_START | B | - | B:e01 @ 0.00 | active_at_first_observation=True |
| g03 | -4.80 | MOVING_START | C | - | C:e01 @ 0.00 | active_at_first_observation=True |
| g04 | -4.80 | THROTTLE_START | A | - | A:e02 @ 0.00 | active_at_first_observation=True |
| g05 | -4.80 | THROTTLE_START | B | - | B:e02 @ 0.00 | active_at_first_observation=True |
| g06 | -4.80 | THROTTLE_START | C | - | C:e02 @ 0.00 | active_at_first_observation=True |
| g07 | -4.80 | TRACK_APPEARED_FRONT | A | B | A:e03 @ 0.00 | initial_in_ego_path=True; source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g08 | -4.80 | TRACK_APPEARED_FRONT | B | C | B:e03 @ 0.00 | initial_in_ego_path=True; source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g09 | -4.30 | CRITICAL_TTC_START | A | B | A:e04 @ 0.50, A:e09 @ 4.80 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g10 | -4.30 | CRITICAL_TTC_START | B | C | B:e04 @ 0.50, B:e11 @ 5.30 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g11 | -1.85 | THROTTLE_END | C | - | C:e03 @ 2.95 |  |
| g12 | -1.85 | BRAKE_START | C | - | C:e04 @ 2.95 |  |
| g13 | -1.60 | CLOSING_START | B | C | B:e05 @ 3.20, B:e12 @ 5.30 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g14 | -1.10 | THROTTLE_END | B | - | B:e06 @ 3.70 |  |
| g15 | -1.10 | BRAKE_START | B | - | B:e07 @ 3.70 |  |
| g16 | -0.90 | CLOSING_START | A | B | A:e05 @ 3.90, A:e10 @ 4.80 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g17 | -0.75 | MOVING_END | C | - | C:e05 @ 4.05 |  |
| g18 | -0.75 | STOP_START | C | - | C:e06 @ 4.05 |  |
| g19 | -0.25 | THROTTLE_END | A | - | A:e06 @ 4.55 |  |
| g20 | -0.25 | BRAKE_START | A | - | A:e07 @ 4.55 |  |
| g21 | 0.00 | COLLISION | - | A, B | A:e08 @ 4.80, B:e08 @ 4.80 | matched_event=collision_001; reference_event=True; peak_impulse=A 10281.41, B 10281.41; recontacts=[{'t_global': 0.65, 'matched_event': 'collision_002', 'peak_impulse': {'A': 1509.76, 'B': 1509.76}, 'observations': [['A', 'A:e13', 5.45], ['B', 'B:e10', 5.45]]}] |
| g22 | 0.00 | CRITICAL_TTC_END | A | B | A:e09 @ 4.80 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g23 | 0.00 | CLOSING_END | A | B | A:e10 @ 4.80 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g24 | 0.05 | BRAKE_END | B | - | B:e09 @ 4.85 |  |
| g25 | 0.50 | COLLISION | - | B, C | B:e10 @ 5.30, C:e07 @ 5.30 | matched_event=collision_003; reference_event=False; peak_impulse=B 8788.05, C 8788.05 |
| g26 | 0.50 | CRITICAL_TTC_END | B | C | B:e11 @ 5.30 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g27 | 0.50 | CLOSING_END | B | C | B:e12 @ 5.30 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g28 | 0.55 | MOVING_END | A | - | A:e11 @ 5.35 |  |
| g29 | 0.55 | STOP_START | A | - | A:e12 @ 5.35 |  |
| g30 | 0.65 | MOVING_END | B | - | B:e13 @ 5.45 |  |
| g31 | 0.65 | STOP_START | B | - | B:e14 @ 5.45 |  |
| g32 | 0.65 | BRAKE_START | B | - | B:e15 @ 5.45 |  |

## Edges

```
    g01 --PRECEDES--> g09
    g01 --PRECEDES--> g10
    g02 --PRECEDES--> g09
    g02 --PRECEDES--> g10
    g03 --PRECEDES--> g09
    g03 --PRECEDES--> g10
    g04 --PRECEDES--> g09
    g04 --PRECEDES--> g10
    g05 --PRECEDES--> g09
    g05 --PRECEDES--> g10
    g06 --PRECEDES--> g09
    g06 --PRECEDES--> g10
    g07 --PRECEDES--> g09
    g07 --PRECEDES--> g10
    g08 --PRECEDES--> g09
    g08 --PRECEDES--> g10
    g09 --PRECEDES--> g11
    g09 --PRECEDES--> g12
    g10 --PRECEDES--> g11
    g10 --PRECEDES--> g12
    g11 --PRECEDES--> g13
    g12 --PRECEDES--> g13
    g13 --PRECEDES--> g14
    g13 --PRECEDES--> g15
    g14 --PRECEDES--> g16
    g15 --PRECEDES--> g16
    g16 --PRECEDES--> g17
    g16 --PRECEDES--> g18
    g17 --PRECEDES--> g19
    g17 --PRECEDES--> g20
    g18 --PRECEDES--> g19
    g18 --PRECEDES--> g20
    g19 --PRECEDES--> g21
    g19 --PRECEDES--> g22
    g19 --PRECEDES--> g23
    g20 --PRECEDES--> g21
    g20 --PRECEDES--> g22
    g20 --PRECEDES--> g23
    g21 --PRECEDES--> g24
    g22 --PRECEDES--> g24
    g23 --PRECEDES--> g24
    g24 --PRECEDES--> g25
    g24 --PRECEDES--> g26
    g24 --PRECEDES--> g27
    g25 --PRECEDES--> g28
    g25 --PRECEDES--> g29
    g26 --PRECEDES--> g28
    g26 --PRECEDES--> g29
    g27 --PRECEDES--> g28
    g27 --PRECEDES--> g29
    g28 --PRECEDES--> g30
    g28 --PRECEDES--> g31
    g28 --PRECEDES--> g32
    g29 --PRECEDES--> g30
    g29 --PRECEDES--> g31
    g29 --PRECEDES--> g32
    g07 --SAME_TRACK--> g09
    g07 --SAME_TRACK--> g16
    g07 --SAME_TRACK--> g22
    g07 --SAME_TRACK--> g23
    g08 --SAME_TRACK--> g10
    g08 --SAME_TRACK--> g13
    g08 --SAME_TRACK--> g26
    g08 --SAME_TRACK--> g27
```

## Global trace

Events in one row are simultaneous at 0.05 s resolution: their order is unresolved.

| t_global | Events |
|---------:|--------|
| -4.80 | MOVING_START(A); MOVING_START(B); MOVING_START(C); THROTTLE_START(A); THROTTLE_START(B); THROTTLE_START(C); TRACK_APPEARED_FRONT(A,B); TRACK_APPEARED_FRONT(B,C) |
| -4.30 | CRITICAL_TTC_START(A,B); CRITICAL_TTC_START(B,C) |
| -1.85 | THROTTLE_END(C); BRAKE_START(C) |
| -1.60 | CLOSING_START(B,C) |
| -1.10 | THROTTLE_END(B); BRAKE_START(B) |
| -0.90 | CLOSING_START(A,B) |
| -0.75 | MOVING_END(C); STOP_START(C) |
| -0.25 | THROTTLE_END(A); BRAKE_START(A) |
| +0.00 | COLLISION(A,B); CRITICAL_TTC_END(A,B); CLOSING_END(A,B) |
| +0.05 | BRAKE_END(B) |
| +0.50 | COLLISION(B,C); CRITICAL_TTC_END(B,C); CLOSING_END(B,C) |
| +0.55 | MOVING_END(A); STOP_START(A) |
| +0.65 | MOVING_END(B); STOP_START(B); BRAKE_START(B) |

## Temporal safety relations

Per track: does the cut-in start before the critical TTC, or was the critical TTC already active? Is the path entry before or after it? Temporal properties only, not causes.

- A's track_001 (B): CRITICAL_TTC_START 0.50, COLLISION with B 4.80 (+4.30 s) [local times; t_global: critical_ttc_start -4.30, collision +0.00]
- B's track_001 (C): CRITICAL_TTC_START 0.50, COLLISION with C 5.30 (+4.80 s) [local times; t_global: critical_ttc_start -4.30, collision +0.50]

## Perceived state before each event, per observing recorder

Each recorder's own belief just before its events, in its own local names (track_001, ...): fusion does not rewrite it. True states are named, unknown ones end with `?`.

| t_global | Recorder | Events (local node) | Perceived state just before |
|---------:|----------|---------------------|-----------------------------|
| -4.80 | A | g01 MOVING_START(A) (A:e01)<br>g04 THROTTLE_START(A) (A:e02)<br>g07 TRACK_APPEARED_FRONT(A,B) (A:e03) | ego: not yet observed |
| -4.80 | B | g02 MOVING_START(B) (B:e01)<br>g05 THROTTLE_START(B) (B:e02)<br>g08 TRACK_APPEARED_FRONT(B,C) (B:e03) | ego: not yet observed |
| -4.80 | C | g03 MOVING_START(C) (C:e01)<br>g06 THROTTLE_START(C) (C:e02) | ego: not yet observed |
| -4.30 | A | g09 CRITICAL_TTC_START(A,B) (A:e04) | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH, CRITICAL_TTC? |
| -4.30 | A | g09 CRITICAL_TTC_START(A,B) (A:e04)<br>g16 CLOSING_START(A,B) (A:e05)<br>g21 COLLISION(A,B) (A:e08)<br>g22 CRITICAL_TTC_END(A,B) (A:e09)<br>g23 CLOSING_END(A,B) (A:e10) | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH, CRITICAL_TTC? |
| -4.30 | B | g10 CRITICAL_TTC_START(B,C) (B:e04) | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH, CRITICAL_TTC? |
| -4.30 | B | g10 CRITICAL_TTC_START(B,C) (B:e04)<br>g13 CLOSING_START(B,C) (B:e05)<br>g25 COLLISION(B,C) (B:e10)<br>g26 CRITICAL_TTC_END(B,C) (B:e11)<br>g27 CLOSING_END(B,C) (B:e12) | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH, CRITICAL_TTC? |
| -1.85 | C | g11 THROTTLE_END(C) (C:e03)<br>g12 BRAKE_START(C) (C:e04) | ego: MOVING, THROTTLE |
| -1.60 | B | g13 CLOSING_START(B,C) (B:e05) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH |
| -1.10 | B | g14 THROTTLE_END(B) (B:e06)<br>g15 BRAKE_START(B) (B:e07) | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH |
| -0.90 | A | g16 CLOSING_START(A,B) (A:e05) | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH |
| -0.75 | C | g17 MOVING_END(C) (C:e05)<br>g18 STOP_START(C) (C:e06) | ego: MOVING, BRAKE |
| -0.25 | A | g19 THROTTLE_END(A) (A:e06)<br>g20 BRAKE_START(A) (A:e07) | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH |
| +0.00 | B | g21 COLLISION(A,B) (B:e08) | ego: MOVING, BRAKE<br>track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH |
| +0.05 | B | g24 BRAKE_END(B) (B:e09) | ego: MOVING, BRAKE<br>track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH |
| +0.50 | C | g25 COLLISION(B,C) (C:e07) | ego: STOP, BRAKE |
| +0.55 | A | g28 MOVING_END(A) (A:e11)<br>g29 STOP_START(A) (A:e12) | ego: MOVING, BRAKE<br>track_001: IN_EGO_PATH |
| +0.65 | B | g30 MOVING_END(B) (B:e13)<br>g31 STOP_START(B) (B:e14)<br>g32 BRAKE_START(B) (B:e15) | ego: MOVING<br>track_001: IN_EGO_PATH |

## Plain-language reading

- 4.80 s before the reference collision, A started moving (already the case when first observed).
- 4.80 s before the reference collision, B started moving (already the case when first observed).
- 4.80 s before the reference collision, C started moving (already the case when first observed).
- 4.80 s before the reference collision, A pressed the accelerator (already the case when first observed).
- 4.80 s before the reference collision, B pressed the accelerator (already the case when first observed).
- 4.80 s before the reference collision, C pressed the accelerator (already the case when first observed).
- 4.80 s before the reference collision, A's radar started tracking B, which appeared in front of it.
- 4.80 s before the reference collision, B's radar started tracking C, which appeared in front of it.
- 4.30 s before the reference collision, A's time-to-contact with B became critical.
- 4.30 s before the reference collision, B's time-to-contact with C became critical.
- 1.85 s before the reference collision, C released the accelerator.
- 1.85 s before the reference collision, C started braking.
- 1.60 s before the reference collision, B observed C start closing in.
- 1.10 s before the reference collision, B released the accelerator.
- 1.10 s before the reference collision, B started braking.
- 0.90 s before the reference collision, A observed B start closing in.
- 0.75 s before the reference collision, C stopped moving.
- 0.75 s before the reference collision, C came to a stop.
- 0.25 s before the reference collision, A released the accelerator.
- 0.25 s before the reference collision, A started braking.
- At the reference collision, A and B both recorded this same collision (peak impulses A: 10281, B: 10281 N*s).
- At the reference collision, A's time-to-contact with B stopped being critical.
- At the reference collision, A observed B stop closing in.
- 0.05 s after the reference collision, B released the brake.
- 0.50 s after the reference collision, B and C both recorded this same collision (peak impulses B: 8788, C: 8788 N*s).
- 0.50 s after the reference collision, B's time-to-contact with C stopped being critical.
- 0.50 s after the reference collision, B observed C stop closing in.
- 0.55 s after the reference collision, A stopped moving.
- 0.55 s after the reference collision, A came to a stop.
- 0.65 s after the reference collision, B stopped moving.
- 0.65 s after the reference collision, B came to a stop.
- 0.65 s after the reference collision, B started braking.
