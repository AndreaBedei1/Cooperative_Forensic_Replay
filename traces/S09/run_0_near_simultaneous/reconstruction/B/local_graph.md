# Local graph - vehicle B

All times are B's own local clock: `t_local` = seconds since B's first ego sample (raw clock reading 1970.0582870952785 at `t_local` = 0). Only files under `vehicles/B/` were read; external objects are anonymous radar tracks.

- Local frame: origin = first ego position; x = first heading; y = to the right of the first heading (CARLA convention)
- Trace: 130 frames at 10 Hz in `local_trace.jsonl`, the last one at the recording end (12.85 s)
- Anonymous radar tracks: 1 (10 Hz samples in `local_tracks.jsonl`)
- Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.
- Nodes: 26; edges: 47 (PRECEDES 39, SAME_TRACK 8)

## Nodes

| Id | Local time | Type | Actor | Subject | Source | Details |
|----|-----------:|------|-------|---------|--------|---------|
| B:e01 | 0.00 | MOVING_START | B | - | ego | active_at_first_observation=True |
| B:e02 | 0.00 | THROTTLE_START | B | - | controls | active_at_first_observation=True |
| B:e03 | 0.80 | STOP_SIGN_DETECTED_START | B | sign-0 | camera | relevant_to_ego_path=True |
| B:e04 | 2.50 | THROTTLE_END | B | - | controls |  |
| B:e05 | 2.50 | BRAKE_START | B | - | controls |  |
| B:e06 | 2.50 | TRACK_APPEARED_RIGHT | B | track_001 | radar | initial_in_ego_path=False |
| B:e07 | 2.50 | CLOSING_START | B | track_001 | radar | active_at_first_observation=True |
| B:e08 | 2.75 | STOP_SIGN_DETECTED_END | B | sign-0 | camera |  |
| B:e09 | 3.60 | MOVING_END | B | - | ego |  |
| B:e10 | 3.60 | STOP_START | B | - | ego |  |
| B:e11 | 3.70 | CLOSING_END | B | track_001 | radar |  |
| B:e12 | 4.70 | BRAKE_END | B | - | controls |  |
| B:e13 | 4.70 | THROTTLE_START | B | - | controls |  |
| B:e14 | 5.15 | STOP_END | B | - | ego |  |
| B:e15 | 5.15 | MOVING_START | B | - | ego |  |
| B:e16 | 5.15 | CLOSING_START | B | track_001 | radar |  |
| B:e17 | 6.10 | CRITICAL_TTC_START | B | track_001 | radar |  |
| B:e18 | 6.45 | EGO_PATH_ENTRY | B | track_001 | radar | occupancy_evidence=returns; occupancy_margin_m=0.55; occupancy_sigma_m=0.25; cause=TARGET_LATERAL; geometry=estimated_body |
| B:e19 | 7.15 | COLLISION | B | - | collision_sensor | peak_impulse=7661.46 |
| B:e20 | 7.15 | CRITICAL_TTC_END | B | track_001 | radar |  |
| B:e21 | 7.20 | CLOSING_END | B | track_001 | radar |  |
| B:e22 | 7.20 | THROTTLE_END | B | - | controls |  |
| B:e23 | 7.20 | BRAKE_START | B | - | controls |  |
| B:e24 | 7.35 | EGO_PATH_EXIT | B | track_001 | radar | occupancy_evidence=returns; occupancy_margin_m=-0.59; occupancy_sigma_m=0.25; cause=MUTUAL_LATERAL; geometry=estimated_body |
| B:e25 | 7.45 | MOVING_END | B | - | ego |  |
| B:e26 | 7.45 | STOP_START | B | - | ego |  |

Events are state transitions; the quantities behind them (speed, pedals, ranges, TTC, relative motion, closest approach) are facts in `local_trace.jsonl`. Events with equal times are simultaneous at the recorder's resolution: PRECEDES links only different times. SAME_TRACK links a track's TRACK_APPEARED_* to every other event about the same local track (grouping only, no order).

## Edges

```
    B:e01 --PRECEDES--> B:e03
    B:e02 --PRECEDES--> B:e03
    B:e03 --PRECEDES--> B:e04
    B:e03 --PRECEDES--> B:e05
    B:e03 --PRECEDES--> B:e06
    B:e03 --PRECEDES--> B:e07
    B:e04 --PRECEDES--> B:e08
    B:e05 --PRECEDES--> B:e08
    B:e06 --PRECEDES--> B:e08
    B:e07 --PRECEDES--> B:e08
    B:e08 --PRECEDES--> B:e09
    B:e08 --PRECEDES--> B:e10
    B:e09 --PRECEDES--> B:e11
    B:e10 --PRECEDES--> B:e11
    B:e11 --PRECEDES--> B:e12
    B:e11 --PRECEDES--> B:e13
    B:e12 --PRECEDES--> B:e14
    B:e12 --PRECEDES--> B:e15
    B:e12 --PRECEDES--> B:e16
    B:e13 --PRECEDES--> B:e14
    B:e13 --PRECEDES--> B:e15
    B:e13 --PRECEDES--> B:e16
    B:e14 --PRECEDES--> B:e17
    B:e15 --PRECEDES--> B:e17
    B:e16 --PRECEDES--> B:e17
    B:e17 --PRECEDES--> B:e18
    B:e18 --PRECEDES--> B:e19
    B:e18 --PRECEDES--> B:e20
    B:e19 --PRECEDES--> B:e21
    B:e19 --PRECEDES--> B:e22
    B:e19 --PRECEDES--> B:e23
    B:e20 --PRECEDES--> B:e21
    B:e20 --PRECEDES--> B:e22
    B:e20 --PRECEDES--> B:e23
    B:e21 --PRECEDES--> B:e24
    B:e22 --PRECEDES--> B:e24
    B:e23 --PRECEDES--> B:e24
    B:e24 --PRECEDES--> B:e25
    B:e24 --PRECEDES--> B:e26
    B:e06 --SAME_TRACK--> B:e07
    B:e06 --SAME_TRACK--> B:e11
    B:e06 --SAME_TRACK--> B:e16
    B:e06 --SAME_TRACK--> B:e17
    B:e06 --SAME_TRACK--> B:e18
    B:e06 --SAME_TRACK--> B:e20
    B:e06 --SAME_TRACK--> B:e21
    B:e06 --SAME_TRACK--> B:e24
```

## Perceived state before each event

Each row is the state just BEFORE its events (none of them applied): events at one time are simultaneous and share it. True states are named, unknown ones end with `?`, false ones are omitted; a lost track's states are UNKNOWN, never ended. Facts: the trace frame at the time shown.

| Local time | Events | Perceived state just before | Facts at |
|-----------:|--------|-----------------------------|---------:|
| 0.00 | B:e01 MOVING_START<br>B:e02 THROTTLE_START | ego: not yet observed | - |
| 0.80 | B:e03 STOP_SIGN_DETECTED_START sign-0 | ego: MOVING, THROTTLE | 0.70 |
| 2.50 | B:e04 THROTTLE_END<br>B:e05 BRAKE_START<br>B:e06 TRACK_APPEARED_RIGHT track_001<br>B:e07 CLOSING_START track_001 | ego: MOVING, THROTTLE<br>sign-0: STOP sign known, relevant to the path | 2.40 |
| 2.75 | B:e08 STOP_SIGN_DETECTED_END sign-0 | ego: MOVING, BRAKE<br>track_001: CLOSING, CRITICAL_TTC?<br>sign-0: STOP sign known, relevant to the path | 2.70 |
| 3.60 | B:e09 MOVING_END<br>B:e10 STOP_START | ego: MOVING, BRAKE<br>track_001: CLOSING<br>sign-0: STOP sign known, relevant to the path | 3.50 |
| 3.70 | B:e11 CLOSING_END track_001 | ego: STOP, BRAKE<br>track_001: CLOSING<br>sign-0: STOP sign known, relevant to the path | 3.60 |
| 4.70 | B:e12 BRAKE_END<br>B:e13 THROTTLE_START | ego: STOP, BRAKE<br>track_001: no active state<br>sign-0: STOP sign known, relevant to the path | 4.60 |
| 5.15 | B:e14 STOP_END<br>B:e15 MOVING_START<br>B:e16 CLOSING_START track_001 | ego: STOP, THROTTLE<br>track_001: no active state<br>sign-0: STOP sign known, relevant to the path | 5.10 |
| 6.10 | B:e17 CRITICAL_TTC_START track_001 | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>sign-0: STOP sign known, relevant to the path | 6.00 |
| 6.45 | B:e18 EGO_PATH_ENTRY track_001 | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC<br>sign-0: STOP sign known, relevant to the path | 6.40 |
| 7.15 | B:e19 COLLISION<br>B:e20 CRITICAL_TTC_END track_001 | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH<br>sign-0: STOP sign known, relevant to the path | 7.10 |
| 7.20 | B:e21 CLOSING_END track_001<br>B:e22 THROTTLE_END<br>B:e23 BRAKE_START | ego: MOVING, THROTTLE<br>track_001: CLOSING, IN_EGO_PATH<br>sign-0: STOP sign known, relevant to the path | 7.10 |
| 7.35 | B:e24 EGO_PATH_EXIT track_001 | ego: MOVING, BRAKE<br>track_001: IN_EGO_PATH<br>sign-0: STOP sign known, relevant to the path | 7.30 |
| 7.45 | B:e25 MOVING_END<br>B:e26 STOP_START | ego: MOVING, BRAKE<br>track_001: no active state<br>sign-0: STOP sign known, relevant to the path | 7.40 |

## States still active when observation ended

- BRAKE, since B:e23 (t = 7.20 s)
- STOP, since B:e26 (t = 7.45 s)

## Tracks lost

- no track was lost

## Temporal safety relations

Order of each track's cut-in, critical TTC and path entry and of the collision report, in local time. Temporal properties only, not causes.

- track_001: CRITICAL_TTC_START 6.10, COLLISION 7.15 (+1.05 s); EGO_PATH_ENTRY 6.45 after critical TTC (+0.35 s)

## Sign detection windows

- STOP sign sign-0: detected 0.80 s -> 2.75 s; relevant to the path: True; STOP_START inside: none

An END means this recorder stopped detecting the sign, not that its obligation ended.

## Anonymous radar tracks

| Track | First seen | Last seen | Measured sweeps | First range / bearing | Min range (at) | Last range / bearing | Max speed |
|-------|-----------:|----------:|----------------:|----------------------|----------------|---------------------|----------:|
| track_001 | 2.50 | 12.85 | 208 | 28.4 m / +34 deg | 0.99 m (7.10) | 1.7 m / -32 deg | 8.2 m/s |

Bearing: positive = to B's right. Ranges are measured from the radar to the visible surface of the object.

## Plain-language reading

- t = 0.00 s: B started moving (already the case when first observed).
- t = 0.00 s: B pressed the accelerator (already the case when first observed).
- t = 0.80 s: B's camera established a STOP sign detection (sign-0).
- t = 2.50 s: B released the accelerator.
- t = 2.50 s: B started braking.
- t = 2.50 s: B's radar started tracking track_001, which appeared on its right.
- t = 2.50 s: B observed track_001 start closing in (already the case when first observed).
- t = 2.75 s: B's camera stopped detecting STOP sign sign-0.
- t = 3.60 s: B stopped moving.
- t = 3.60 s: B came to a stop.
- t = 3.70 s: B observed track_001 stop closing in.
- t = 4.70 s: B released the brake.
- t = 4.70 s: B pressed the accelerator.
- t = 5.15 s: B left its stop.
- t = 5.15 s: B started moving.
- t = 5.15 s: B observed track_001 start closing in.
- t = 6.10 s: B's time-to-contact with track_001 became critical.
- t = 6.45 s: B observed track_001 enter its forward path corridor.
- t = 7.15 s: B's collision sensor recorded a contact (peak impulse 7661 N*s).
- t = 7.15 s: B's time-to-contact with track_001 stopped being critical.
- t = 7.20 s: B observed track_001 stop closing in.
- t = 7.20 s: B released the accelerator.
- t = 7.20 s: B started braking.
- t = 7.35 s: B observed track_001 leave its forward path corridor.
- t = 7.45 s: B stopped moving.
- t = 7.45 s: B came to a stop.
