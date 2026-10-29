# Global graph - S02/run_0_crash

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
| A | ALIGNED | A:e11 | 5.25 | -5.25 | reported the reference collision collision_001 |
| B | ALIGNED | B:e07 | 5.25 | -5.25 | reported the reference collision collision_001 |

Estimated relative clock offsets: B - A = +0.000 s

Matched `collision_001`: A and B both recorded a collision; peak impulses 2604.14 vs 2604.14 N*s (similarity 1.000, tolerance 0.10); no competing report within tolerance; the two bodies touch at their reports (0.00 m apart, tolerance 1.0 m); independent relative impulse std 0.100; combined z 0.000 (gate 3.0); engineering assumption; pre-contact radar view of each recorder checked against the candidate partner's own speed: not contradicted

## Identity associations

| Local track | Global entity | Status | Confidence | Evidence |
|-------------|---------------|--------|-----------:|----------|
| A:track_001 | B | ASSOCIATED | 0.99 | A and B both reported collision_001 (peak impulse 2604.14 vs 2604.14 N*s)<br>tracked for 5.00 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 6.2 m -> 0.1 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 0.16 m/s for reference)<br>clearance at the contact 0.06 m<br>the only track of A compatible with the contact |

## Nodes

| Id | Global time | Type | Actor | Subject / participants | Observed by (local node @ local time) | Details |
|----|------------:|------|-------|------------------------|----------------------------------------|---------|
| g01 | -5.25 | MOVING_START | A | - | A:e01 @ 0.00 | active_at_first_observation=True |
| g02 | -5.25 | MOVING_START | B | - | B:e01 @ 0.00 | active_at_first_observation=True |
| g03 | -5.25 | THROTTLE_START | A | - | A:e02 @ 0.00 | active_at_first_observation=True |
| g04 | -5.25 | THROTTLE_START | B | - | B:e02 @ 0.00 | active_at_first_observation=True |
| g05 | -5.00 | TRACK_APPEARED_LEFT | A | B | A:e03 @ 0.25 | initial_in_ego_path=False; source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g06 | -5.00 | CLOSING_START | A | B | A:e04 @ 0.25, A:e13 @ 5.25 | active_at_first_observation=True; source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g07 | -4.35 | CUT_IN_FROM_LEFT_START | A | B | A:e05 @ 0.90, A:e08 @ 4.05 | geometry=estimated_body; source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g08 | -3.50 | EGO_PATH_ENTRY | A | B | A:e06 @ 1.75 | occupancy_evidence=box; occupancy_margin_m=0.53; occupancy_sigma_m=0.28; cause=TARGET_LATERAL; geometry=estimated_body; source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g09 | -3.40 | CRITICAL_TTC_START | A | B | A:e07 @ 1.85, A:e12 @ 5.25 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g10 | -2.10 | THROTTLE_END | B | - | B:e03 @ 3.15 |  |
| g11 | -2.10 | BRAKE_START | B | - | B:e04 @ 3.15 |  |
| g12 | -1.60 | BRAKE_END | B | - | B:e05 @ 3.65 |  |
| g13 | -1.50 | THROTTLE_START | B | - | B:e06 @ 3.75 |  |
| g14 | -1.20 | CUT_IN_FROM_LEFT_END | A | B | A:e08 @ 4.05 | geometry=estimated_body; source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g15 | -0.80 | THROTTLE_END | A | - | A:e09 @ 4.45 |  |
| g16 | -0.80 | BRAKE_START | A | - | A:e10 @ 4.45 |  |
| g17 | 0.00 | COLLISION | - | A, B | A:e11 @ 5.25, B:e07 @ 5.25 | matched_event=collision_001; reference_event=True; peak_impulse=A 2604.14, B 2604.14 |
| g18 | 0.00 | CRITICAL_TTC_END | A | B | A:e12 @ 5.25 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g19 | 0.00 | CLOSING_END | A | B | A:e13 @ 5.25 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g20 | 0.00 | THROTTLE_END | B | - | B:e08 @ 5.25 |  |
| g21 | 0.00 | BRAKE_START | B | - | B:e09 @ 5.25 |  |
| g22 | 0.40 | MOVING_END | A | - | A:e14 @ 5.65 |  |
| g23 | 0.40 | STOP_START | A | - | A:e15 @ 5.65 |  |
| g24 | 0.55 | MOVING_END | B | - | B:e10 @ 5.80 |  |
| g25 | 0.55 | STOP_START | B | - | B:e11 @ 5.80 |  |

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
    g06 --PRECEDES--> g07
    g07 --PRECEDES--> g08
    g08 --PRECEDES--> g09
    g09 --PRECEDES--> g10
    g09 --PRECEDES--> g11
    g10 --PRECEDES--> g12
    g11 --PRECEDES--> g12
    g12 --PRECEDES--> g13
    g13 --PRECEDES--> g14
    g14 --PRECEDES--> g15
    g14 --PRECEDES--> g16
    g15 --PRECEDES--> g17
    g15 --PRECEDES--> g18
    g15 --PRECEDES--> g19
    g15 --PRECEDES--> g20
    g15 --PRECEDES--> g21
    g16 --PRECEDES--> g17
    g16 --PRECEDES--> g18
    g16 --PRECEDES--> g19
    g16 --PRECEDES--> g20
    g16 --PRECEDES--> g21
    g17 --PRECEDES--> g22
    g17 --PRECEDES--> g23
    g18 --PRECEDES--> g22
    g18 --PRECEDES--> g23
    g19 --PRECEDES--> g22
    g19 --PRECEDES--> g23
    g20 --PRECEDES--> g22
    g20 --PRECEDES--> g23
    g21 --PRECEDES--> g22
    g21 --PRECEDES--> g23
    g22 --PRECEDES--> g24
    g22 --PRECEDES--> g25
    g23 --PRECEDES--> g24
    g23 --PRECEDES--> g25
    g05 --SAME_TRACK--> g06
    g05 --SAME_TRACK--> g07
    g05 --SAME_TRACK--> g08
    g05 --SAME_TRACK--> g09
    g05 --SAME_TRACK--> g14
    g05 --SAME_TRACK--> g18
    g05 --SAME_TRACK--> g19
```

## Global trace

Events in one row are simultaneous at 0.05 s resolution: their order is unresolved.

| t_global | Events |
|---------:|--------|
| -5.25 | MOVING_START(A); MOVING_START(B); THROTTLE_START(A); THROTTLE_START(B) |
| -5.00 | TRACK_APPEARED_LEFT(A,B); CLOSING_START(A,B) |
| -4.35 | CUT_IN_FROM_LEFT_START(A,B) |
| -3.50 | EGO_PATH_ENTRY(A,B) |
| -3.40 | CRITICAL_TTC_START(A,B) |
| -2.10 | THROTTLE_END(B); BRAKE_START(B) |
| -1.60 | BRAKE_END(B) |
| -1.50 | THROTTLE_START(B) |
| -1.20 | CUT_IN_FROM_LEFT_END(A,B) |
| -0.80 | THROTTLE_END(A); BRAKE_START(A) |
| +0.00 | COLLISION(A,B); CRITICAL_TTC_END(A,B); CLOSING_END(A,B); THROTTLE_END(B); BRAKE_START(B) |
| +0.40 | MOVING_END(A); STOP_START(A) |
| +0.55 | MOVING_END(B); STOP_START(B) |

## Temporal safety relations

Per track: does the cut-in start before the critical TTC, or was the critical TTC already active? Is the path entry before or after it? Temporal properties only, not causes.

- A's track_001 (B): cut-in started before critical TTC: CUT_IN_FROM_LEFT_START 0.90 < CRITICAL_TTC_START 1.85 (+0.95 s) < COLLISION with B 5.25 (+3.40 s); EGO_PATH_ENTRY 1.75 before critical TTC (-0.10 s) [local times; t_global: cut_in -4.35, critical_ttc_start -3.40, ego_path_entry -3.50, collision +0.00]

## Perceived state before each event, per observing recorder

Each recorder's own belief just before its events, in its own local names (track_001, ...): fusion does not rewrite it. True states are named, unknown ones end with `?`.

| t_global | Recorder | Events (local node) | Perceived state just before |
|---------:|----------|---------------------|-----------------------------|
| -5.25 | A | g01 MOVING_START(A) (A:e01)<br>g03 THROTTLE_START(A) (A:e02) | ego: not yet observed |
| -5.25 | B | g02 MOVING_START(B) (B:e01)<br>g04 THROTTLE_START(B) (B:e02) | ego: not yet observed |
| -5.00 | A | g05 TRACK_APPEARED_LEFT(A,B) (A:e03)<br>g06 CLOSING_START(A,B) (A:e04) | ego: MOVING, THROTTLE |
| -5.00 | A | g06 CLOSING_START(A,B) (A:e04)<br>g09 CRITICAL_TTC_START(A,B) (A:e07)<br>g17 COLLISION(A,B) (A:e11)<br>g18 CRITICAL_TTC_END(A,B) (A:e12)<br>g19 CLOSING_END(A,B) (A:e13) | ego: MOVING, THROTTLE |
| -4.35 | A | g07 CUT_IN_FROM_LEFT_START(A,B) (A:e05) | ego: MOVING, THROTTLE<br>track_001: CLOSING |
| -4.35 | A | g07 CUT_IN_FROM_LEFT_START(A,B) (A:e05)<br>g14 CUT_IN_FROM_LEFT_END(A,B) (A:e08) | ego: MOVING, THROTTLE<br>track_001: CLOSING |
| -3.50 | A | g08 EGO_PATH_ENTRY(A,B) (A:e06) | ego: MOVING, THROTTLE<br>track_001: CLOSING, CUT_IN_FROM_LEFT |
| -3.40 | A | g09 CRITICAL_TTC_START(A,B) (A:e07) | ego: MOVING, THROTTLE<br>track_001: CLOSING, IN_EGO_PATH, CUT_IN_FROM_LEFT |
| -2.10 | B | g10 THROTTLE_END(B) (B:e03)<br>g11 BRAKE_START(B) (B:e04) | ego: MOVING, THROTTLE |
| -1.60 | B | g12 BRAKE_END(B) (B:e05) | ego: MOVING, BRAKE |
| -1.50 | B | g13 THROTTLE_START(B) (B:e06) | ego: MOVING |
| -0.80 | A | g15 THROTTLE_END(A) (A:e09)<br>g16 BRAKE_START(A) (A:e10) | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH |
| +0.00 | B | g17 COLLISION(A,B) (B:e07)<br>g20 THROTTLE_END(B) (B:e08)<br>g21 BRAKE_START(B) (B:e09) | ego: MOVING, THROTTLE |
| +0.40 | A | g22 MOVING_END(A) (A:e14)<br>g23 STOP_START(A) (A:e15) | ego: MOVING, BRAKE<br>track_001: IN_EGO_PATH |
| +0.55 | B | g24 MOVING_END(B) (B:e10)<br>g25 STOP_START(B) (B:e11) | ego: MOVING, BRAKE |

## Plain-language reading

- 5.25 s before the reference collision, A started moving (already the case when first observed).
- 5.25 s before the reference collision, B started moving (already the case when first observed).
- 5.25 s before the reference collision, A pressed the accelerator (already the case when first observed).
- 5.25 s before the reference collision, B pressed the accelerator (already the case when first observed).
- 5.00 s before the reference collision, A's radar started tracking B, which appeared on its left.
- 5.00 s before the reference collision, A observed B start closing in (already the case when first observed).
- 4.35 s before the reference collision, A observed B cutting in from the left.
- 3.50 s before the reference collision, A observed B enter its forward path corridor.
- 3.40 s before the reference collision, A's time-to-contact with B became critical.
- 2.10 s before the reference collision, B released the accelerator.
- 2.10 s before the reference collision, B started braking.
- 1.60 s before the reference collision, B released the brake.
- 1.50 s before the reference collision, B pressed the accelerator.
- 1.20 s before the reference collision, A observed B's cut-in from the left settle.
- 0.80 s before the reference collision, A released the accelerator.
- 0.80 s before the reference collision, A started braking.
- At the reference collision, A and B both recorded this same collision (peak impulses A: 2604, B: 2604 N*s).
- At the reference collision, A's time-to-contact with B stopped being critical.
- At the reference collision, A observed B stop closing in.
- At the reference collision, B released the accelerator.
- At the reference collision, B started braking.
- 0.40 s after the reference collision, A stopped moving.
- 0.40 s after the reference collision, A came to a stop.
- 0.55 s after the reference collision, B stopped moving.
- 0.55 s after the reference collision, B came to a stop.
