# Global graph - S08/run_0_rolls_through

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
| A | ALIGNED | A:e15 | 5.40 | -5.40 | reported the reference collision collision_001 |
| B | ALIGNED | B:e07 | 5.40 | -5.40 | reported the reference collision collision_001 |

Estimated relative clock offsets: B - A = +0.000 s

Matched `collision_001`: A and B both recorded a collision; peak impulses 12940.27 vs 12940.27 N*s (similarity 1.000, tolerance 0.10); no competing report within tolerance; the two bodies touch at their reports (0.00 m apart, tolerance 1.0 m); independent relative impulse std 0.100; combined z 0.000 (gate 3.0); engineering assumption; pre-contact radar view of each recorder checked against the candidate partner's own speed: not contradicted

## Identity associations

| Local track | Global entity | Status | Confidence | Evidence |
|-------------|---------------|--------|-----------:|----------|
| A:track_001 | B | ASSOCIATED | 1.00 | A and B both reported collision_001 (peak impulse 12940.27 vs 12940.27 N*s)<br>tracked for 2.80 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 12.6 m -> 0.0 m over the last 1.0 s<br>track motion compatible with B's own speed in the observed direction (3 sigma; full-speed RMSE 0.15 m/s for reference)<br>clearance at the contact 0.01 m<br>the only track of A compatible with the contact |
| B:track_001 | A | ASSOCIATED | 0.74 | B and A both reported collision_001 (peak impulse 12940.27 vs 12940.27 N*s)<br>tracked for 2.70 s before the matched collision<br>continuous up to the contact: last observed 0.00 s before it (window 1.00 s)<br>approaching before the contact: clearance 12.5 m -> 0.2 m over the last 1.0 s<br>track motion compatible with A's own speed in the observed direction (3 sigma; full-speed RMSE 1.17 m/s for reference)<br>clearance at the contact 0.16 m<br>the only track of B compatible with the contact |

## Nodes

| Id | Global time | Type | Actor | Subject / participants | Observed by (local node @ local time) | Details |
|----|------------:|------|-------|------------------------|----------------------------------------|---------|
| g01 | -5.40 | MOVING_START | A | - | A:e01 @ 0.00 | active_at_first_observation=True |
| g02 | -5.40 | MOVING_START | B | - | B:e01 @ 0.00 | active_at_first_observation=True |
| g03 | -5.40 | THROTTLE_START | A | - | A:e02 @ 0.00 | active_at_first_observation=True |
| g04 | -5.40 | THROTTLE_START | B | - | B:e02 @ 0.00 | active_at_first_observation=True |
| g05 | -4.90 | INDICATOR_LEFT_START | A | - | A:e03 @ 0.50 |  |
| g06 | -4.40 | STOP_SIGN_DETECTED_START | A | A:sign-0 | A:e04 @ 1.00 | relevant_to_ego_path=True |
| g07 | -3.45 | THROTTLE_END | A | - | A:e05 @ 1.95 |  |
| g08 | -3.45 | BRAKE_START | A | - | A:e06 @ 1.95 |  |
| g09 | -2.80 | TRACK_APPEARED_LEFT | A | B | A:e07 @ 2.60 | initial_in_ego_path=False; source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g10 | -2.80 | CLOSING_START | A | B | A:e08 @ 2.60, A:e17 @ 5.40 | active_at_first_observation=True; source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g11 | -2.70 | TRACK_APPEARED_RIGHT | B | A | B:e03 @ 2.70 | initial_in_ego_path=False; source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g12 | -2.70 | CLOSING_START | B | A | B:e04 @ 2.70, B:e09 @ 5.40 | active_at_first_observation=True; source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g13 | -2.60 | STOP_SIGN_DETECTED_END | A | A:sign-0 | A:e09 @ 2.80 |  |
| g14 | -2.55 | BRAKE_END | A | - | A:e10 @ 2.85 |  |
| g15 | -2.55 | THROTTLE_START | A | - | A:e11 @ 2.85 |  |
| g16 | -2.05 | CRITICAL_TTC_START | A | B | A:e12 @ 3.35, A:e16 @ 5.40 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g17 | -1.85 | CRITICAL_TTC_START | B | A | B:e05 @ 3.55, B:e08 @ 5.40 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g18 | -1.70 | TURN_LEFT_START | A | - | A:e13 @ 3.70 |  |
| g19 | -1.25 | EGO_PATH_ENTRY | A | B | A:e14 @ 4.15 | occupancy_evidence=box; occupancy_margin_m=0.46; occupancy_sigma_m=0.27; cause=RECORDER_LATERAL; geometry=estimated_body; source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g20 | -0.40 | EGO_PATH_ENTRY | B | A | B:e06 @ 5.00 | occupancy_evidence=returns; occupancy_margin_m=0.44; occupancy_sigma_m=0.25; cause=TARGET_LATERAL; geometry=estimated_body; source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g21 | 0.00 | COLLISION | - | A, B | A:e15 @ 5.40, B:e07 @ 5.40 | matched_event=collision_001; reference_event=True; peak_impulse=A 12940.27, B 12940.27 |
| g22 | 0.00 | CRITICAL_TTC_END | A | B | A:e16 @ 5.40 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g23 | 0.00 | CRITICAL_TTC_END | B | A | B:e08 @ 5.40 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g24 | 0.00 | CLOSING_END | A | B | A:e17 @ 5.40 | source_track=track_001; aggregation=entity_state_union; source_tracks=['A:track_001'] |
| g25 | 0.00 | CLOSING_END | B | A | B:e09 @ 5.40 | source_track=track_001; aggregation=entity_state_union; source_tracks=['B:track_001'] |
| g26 | 0.00 | TURN_LEFT_END | A | - | A:e18 @ 5.40 |  |
| g27 | 0.05 | THROTTLE_END | A | - | A:e19 @ 5.45 |  |
| g28 | 0.05 | THROTTLE_END | B | - | B:e10 @ 5.45 |  |
| g29 | 0.05 | BRAKE_START | A | - | A:e20 @ 5.45 |  |
| g30 | 0.05 | BRAKE_START | B | - | B:e11 @ 5.45 |  |
| g31 | 0.10 | MOVING_END | A | - | A:e21 @ 5.50 |  |
| g32 | 0.10 | STOP_START | A | - | A:e22 @ 5.50 |  |
| g33 | 0.20 | MOVING_END | B | - | B:e12 @ 5.60 |  |
| g34 | 0.20 | STOP_START | B | - | B:e13 @ 5.60 |  |

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
    g17 --PRECEDES--> g18
    g18 --PRECEDES--> g19
    g19 --PRECEDES--> g20
    g20 --PRECEDES--> g21
    g20 --PRECEDES--> g22
    g20 --PRECEDES--> g23
    g20 --PRECEDES--> g24
    g20 --PRECEDES--> g25
    g20 --PRECEDES--> g26
    g21 --PRECEDES--> g27
    g21 --PRECEDES--> g28
    g21 --PRECEDES--> g29
    g21 --PRECEDES--> g30
    g22 --PRECEDES--> g27
    g22 --PRECEDES--> g28
    g22 --PRECEDES--> g29
    g22 --PRECEDES--> g30
    g23 --PRECEDES--> g27
    g23 --PRECEDES--> g28
    g23 --PRECEDES--> g29
    g23 --PRECEDES--> g30
    g24 --PRECEDES--> g27
    g24 --PRECEDES--> g28
    g24 --PRECEDES--> g29
    g24 --PRECEDES--> g30
    g25 --PRECEDES--> g27
    g25 --PRECEDES--> g28
    g25 --PRECEDES--> g29
    g25 --PRECEDES--> g30
    g26 --PRECEDES--> g27
    g26 --PRECEDES--> g28
    g26 --PRECEDES--> g29
    g26 --PRECEDES--> g30
    g27 --PRECEDES--> g31
    g27 --PRECEDES--> g32
    g28 --PRECEDES--> g31
    g28 --PRECEDES--> g32
    g29 --PRECEDES--> g31
    g29 --PRECEDES--> g32
    g30 --PRECEDES--> g31
    g30 --PRECEDES--> g32
    g31 --PRECEDES--> g33
    g31 --PRECEDES--> g34
    g32 --PRECEDES--> g33
    g32 --PRECEDES--> g34
    g09 --SAME_TRACK--> g10
    g09 --SAME_TRACK--> g16
    g09 --SAME_TRACK--> g19
    g09 --SAME_TRACK--> g22
    g09 --SAME_TRACK--> g24
    g11 --SAME_TRACK--> g12
    g11 --SAME_TRACK--> g17
    g11 --SAME_TRACK--> g20
    g11 --SAME_TRACK--> g23
    g11 --SAME_TRACK--> g25
```

## Global trace

Events in one row are simultaneous at 0.05 s resolution: their order is unresolved.

| t_global | Events |
|---------:|--------|
| -5.40 | MOVING_START(A); MOVING_START(B); THROTTLE_START(A); THROTTLE_START(B) |
| -4.90 | INDICATOR_LEFT_START(A) |
| -4.40 | STOP_SIGN_DETECTED_START(A,A:sign-0) |
| -3.45 | THROTTLE_END(A); BRAKE_START(A) |
| -2.80 | TRACK_APPEARED_LEFT(A,B); CLOSING_START(A,B) |
| -2.70 | TRACK_APPEARED_RIGHT(B,A); CLOSING_START(B,A) |
| -2.60 | STOP_SIGN_DETECTED_END(A,A:sign-0) |
| -2.55 | BRAKE_END(A); THROTTLE_START(A) |
| -2.05 | CRITICAL_TTC_START(A,B) |
| -1.85 | CRITICAL_TTC_START(B,A) |
| -1.70 | TURN_LEFT_START(A) |
| -1.25 | EGO_PATH_ENTRY(A,B) |
| -0.40 | EGO_PATH_ENTRY(B,A) |
| +0.00 | COLLISION(A,B); CRITICAL_TTC_END(A,B); CRITICAL_TTC_END(B,A); CLOSING_END(A,B); CLOSING_END(B,A); TURN_LEFT_END(A) |
| +0.05 | THROTTLE_END(A); THROTTLE_END(B); BRAKE_START(A); BRAKE_START(B) |
| +0.10 | MOVING_END(A); STOP_START(A) |
| +0.20 | MOVING_END(B); STOP_START(B) |

## Temporal safety relations

Per track: does the cut-in start before the critical TTC, or was the critical TTC already active? Is the path entry before or after it? Temporal properties only, not causes.

- A's track_001 (B): CRITICAL_TTC_START 3.35, COLLISION with B 5.40 (+2.05 s); EGO_PATH_ENTRY 4.15 after critical TTC (+0.80 s) [local times; t_global: critical_ttc_start -2.05, ego_path_entry -1.25, collision +0.00]
- B's track_001 (A): CRITICAL_TTC_START 3.55, COLLISION with A 5.40 (+1.85 s); EGO_PATH_ENTRY 5.00 after critical TTC (+1.45 s) [local times; t_global: critical_ttc_start -1.85, ego_path_entry -0.40, collision +0.00]

## Perceived state before each event, per observing recorder

Each recorder's own belief just before its events, in its own local names (track_001, ...): fusion does not rewrite it. True states are named, unknown ones end with `?`.

| t_global | Recorder | Events (local node) | Perceived state just before |
|---------:|----------|---------------------|-----------------------------|
| -5.40 | A | g01 MOVING_START(A) (A:e01)<br>g03 THROTTLE_START(A) (A:e02) | ego: not yet observed |
| -5.40 | B | g02 MOVING_START(B) (B:e01)<br>g04 THROTTLE_START(B) (B:e02) | ego: not yet observed |
| -4.90 | A | g05 INDICATOR_LEFT_START(A) (A:e03) | ego: MOVING, THROTTLE |
| -4.40 | A | g06 STOP_SIGN_DETECTED_START(A,A:sign-0) (A:e04) | ego: MOVING, THROTTLE, INDICATOR_LEFT |
| -3.45 | A | g07 THROTTLE_END(A) (A:e05)<br>g08 BRAKE_START(A) (A:e06) | ego: MOVING, THROTTLE, INDICATOR_LEFT<br>sign-0: STOP sign known, relevant to the path |
| -2.80 | A | g09 TRACK_APPEARED_LEFT(A,B) (A:e07)<br>g10 CLOSING_START(A,B) (A:e08) | ego: MOVING, BRAKE, INDICATOR_LEFT<br>sign-0: STOP sign known, relevant to the path |
| -2.80 | A | g10 CLOSING_START(A,B) (A:e08)<br>g16 CRITICAL_TTC_START(A,B) (A:e12)<br>g21 COLLISION(A,B) (A:e15)<br>g22 CRITICAL_TTC_END(A,B) (A:e16)<br>g24 CLOSING_END(A,B) (A:e17)<br>g26 TURN_LEFT_END(A) (A:e18) | ego: MOVING, BRAKE, INDICATOR_LEFT<br>sign-0: STOP sign known, relevant to the path |
| -2.70 | B | g11 TRACK_APPEARED_RIGHT(B,A) (B:e03)<br>g12 CLOSING_START(B,A) (B:e04) | ego: MOVING, THROTTLE |
| -2.70 | B | g12 CLOSING_START(B,A) (B:e04)<br>g17 CRITICAL_TTC_START(B,A) (B:e05)<br>g21 COLLISION(A,B) (B:e07)<br>g23 CRITICAL_TTC_END(B,A) (B:e08)<br>g25 CLOSING_END(B,A) (B:e09) | ego: MOVING, THROTTLE |
| -2.60 | A | g13 STOP_SIGN_DETECTED_END(A,A:sign-0) (A:e09) | ego: MOVING, BRAKE, INDICATOR_LEFT<br>track_001: CLOSING, CRITICAL_TTC?<br>sign-0: STOP sign known, relevant to the path |
| -2.55 | A | g14 BRAKE_END(A) (A:e10)<br>g15 THROTTLE_START(A) (A:e11) | ego: MOVING, BRAKE, INDICATOR_LEFT<br>track_001: CLOSING, CRITICAL_TTC?<br>sign-0: STOP sign known, relevant to the path |
| -2.05 | A | g16 CRITICAL_TTC_START(A,B) (A:e12) | ego: MOVING, THROTTLE, INDICATOR_LEFT<br>track_001: CLOSING<br>sign-0: STOP sign known, relevant to the path |
| -1.85 | B | g17 CRITICAL_TTC_START(B,A) (B:e05) | ego: MOVING, THROTTLE<br>track_001: CLOSING |
| -1.70 | A | g18 TURN_LEFT_START(A) (A:e13) | ego: MOVING, THROTTLE, INDICATOR_LEFT<br>track_001: CLOSING, CRITICAL_TTC<br>sign-0: STOP sign known, relevant to the path |
| -1.25 | A | g19 EGO_PATH_ENTRY(A,B) (A:e14) | ego: MOVING, THROTTLE, TURN_LEFT, INDICATOR_LEFT<br>track_001: CLOSING, CRITICAL_TTC<br>sign-0: STOP sign known, relevant to the path |
| -0.40 | B | g20 EGO_PATH_ENTRY(B,A) (B:e06) | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC |
| +0.05 | A | g27 THROTTLE_END(A) (A:e19)<br>g29 BRAKE_START(A) (A:e20) | ego: MOVING, THROTTLE, INDICATOR_LEFT<br>track_001: IN_EGO_PATH<br>sign-0: STOP sign known, relevant to the path |
| +0.05 | B | g28 THROTTLE_END(B) (B:e10)<br>g30 BRAKE_START(B) (B:e11) | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH |
| +0.10 | A | g31 MOVING_END(A) (A:e21)<br>g32 STOP_START(A) (A:e22) | ego: MOVING, BRAKE, INDICATOR_LEFT<br>track_001: IN_EGO_PATH<br>sign-0: STOP sign known, relevant to the path |
| +0.20 | B | g33 MOVING_END(B) (B:e12)<br>g34 STOP_START(B) (B:e13) | ego: MOVING, BRAKE<br>track_001: IN_EGO_PATH |

## Plain-language reading

- 5.40 s before the reference collision, A started moving (already the case when first observed).
- 5.40 s before the reference collision, B started moving (already the case when first observed).
- 5.40 s before the reference collision, A pressed the accelerator (already the case when first observed).
- 5.40 s before the reference collision, B pressed the accelerator (already the case when first observed).
- 4.90 s before the reference collision, A switched on its left turn indicator.
- 4.40 s before the reference collision, A's camera established a STOP sign detection (unidentified object A:sign-0).
- 3.45 s before the reference collision, A released the accelerator.
- 3.45 s before the reference collision, A started braking.
- 2.80 s before the reference collision, A's radar started tracking B, which appeared on its left.
- 2.80 s before the reference collision, A observed B start closing in (already the case when first observed).
- 2.70 s before the reference collision, B's radar started tracking A, which appeared on its right.
- 2.70 s before the reference collision, B observed A start closing in (already the case when first observed).
- 2.60 s before the reference collision, A's camera stopped detecting STOP sign unidentified object A:sign-0.
- 2.55 s before the reference collision, A released the brake.
- 2.55 s before the reference collision, A pressed the accelerator.
- 2.05 s before the reference collision, A's time-to-contact with B became critical.
- 1.85 s before the reference collision, B's time-to-contact with A became critical.
- 1.70 s before the reference collision, A started turning left.
- 1.25 s before the reference collision, A observed B enter its forward path corridor.
- 0.40 s before the reference collision, B observed A enter its forward path corridor.
- At the reference collision, A and B both recorded this same collision (peak impulses A: 12940, B: 12940 N*s).
- At the reference collision, A's time-to-contact with B stopped being critical.
- At the reference collision, B's time-to-contact with A stopped being critical.
- At the reference collision, A observed B stop closing in.
- At the reference collision, B observed A stop closing in.
- At the reference collision, A stopped turning left.
- 0.05 s after the reference collision, A released the accelerator.
- 0.05 s after the reference collision, B released the accelerator.
- 0.05 s after the reference collision, A started braking.
- 0.05 s after the reference collision, B started braking.
- 0.10 s after the reference collision, A stopped moving.
- 0.10 s after the reference collision, A came to a stop.
- 0.20 s after the reference collision, B stopped moving.
- 0.20 s after the reference collision, B came to a stop.
