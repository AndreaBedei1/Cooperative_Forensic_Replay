# Local graph - vehicle A

All times are A's own local clock: `t_local` = seconds since A's first ego sample (raw clock reading 1949.6870362199843 at `t_local` = 0). Only files under `vehicles/A/` were read; external objects are anonymous radar tracks.

- Local frame: origin = first ego position; x = first heading; y = to the right of the first heading (CARLA convention)
- Trace: 161 frames at 10 Hz in `local_trace.jsonl`, the last one at the recording end (15.95 s)
- Anonymous radar tracks: 1 (10 Hz samples in `local_tracks.jsonl`)
- Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.
- Nodes: 22; edges: 38 (PRECEDES 33, SAME_TRACK 5)

## Nodes

| Id | Local time | Type | Actor | Subject | Source | Details |
|----|-----------:|------|-------|---------|--------|---------|
| A:e01 | 0.00 | MOVING_START | A | - | ego | active_at_first_observation=True |
| A:e02 | 0.00 | THROTTLE_START | A | - | controls | active_at_first_observation=True |
| A:e03 | 0.50 | INDICATOR_LEFT_START | A | - | lights |  |
| A:e04 | 1.00 | STOP_SIGN_DETECTED_START | A | sign-0 | camera | relevant_to_ego_path=True |
| A:e05 | 1.95 | THROTTLE_END | A | - | controls |  |
| A:e06 | 1.95 | BRAKE_START | A | - | controls |  |
| A:e07 | 2.60 | TRACK_APPEARED_LEFT | A | track_001 | radar | initial_in_ego_path=False |
| A:e08 | 2.60 | CLOSING_START | A | track_001 | radar | active_at_first_observation=True |
| A:e09 | 2.80 | STOP_SIGN_DETECTED_END | A | sign-0 | camera |  |
| A:e10 | 2.85 | BRAKE_END | A | - | controls |  |
| A:e11 | 2.85 | THROTTLE_START | A | - | controls |  |
| A:e12 | 3.35 | CRITICAL_TTC_START | A | track_001 | radar |  |
| A:e13 | 3.70 | TURN_LEFT_START | A | - | ego |  |
| A:e14 | 4.15 | EGO_PATH_ENTRY | A | track_001 | radar | occupancy_evidence=box; occupancy_margin_m=0.46; occupancy_sigma_m=0.27; cause=RECORDER_LATERAL; geometry=estimated_body |
| A:e15 | 5.40 | COLLISION | A | - | collision_sensor | peak_impulse=12940.27 |
| A:e16 | 5.40 | CRITICAL_TTC_END | A | track_001 | radar |  |
| A:e17 | 5.40 | CLOSING_END | A | track_001 | radar |  |
| A:e18 | 5.40 | TURN_LEFT_END | A | - | ego |  |
| A:e19 | 5.45 | THROTTLE_END | A | - | controls |  |
| A:e20 | 5.45 | BRAKE_START | A | - | controls |  |
| A:e21 | 5.50 | MOVING_END | A | - | ego |  |
| A:e22 | 5.50 | STOP_START | A | - | ego |  |

Events are state transitions; the quantities behind them (speed, pedals, ranges, TTC, relative motion, closest approach) are facts in `local_trace.jsonl`. Events with equal times are simultaneous at the recorder's resolution: PRECEDES links only different times. SAME_TRACK links a track's TRACK_APPEARED_* to every other event about the same local track (grouping only, no order).

## Edges

```
    A:e01 --PRECEDES--> A:e03
    A:e02 --PRECEDES--> A:e03
    A:e03 --PRECEDES--> A:e04
    A:e04 --PRECEDES--> A:e05
    A:e04 --PRECEDES--> A:e06
    A:e05 --PRECEDES--> A:e07
    A:e05 --PRECEDES--> A:e08
    A:e06 --PRECEDES--> A:e07
    A:e06 --PRECEDES--> A:e08
    A:e07 --PRECEDES--> A:e09
    A:e08 --PRECEDES--> A:e09
    A:e09 --PRECEDES--> A:e10
    A:e09 --PRECEDES--> A:e11
    A:e10 --PRECEDES--> A:e12
    A:e11 --PRECEDES--> A:e12
    A:e12 --PRECEDES--> A:e13
    A:e13 --PRECEDES--> A:e14
    A:e14 --PRECEDES--> A:e15
    A:e14 --PRECEDES--> A:e16
    A:e14 --PRECEDES--> A:e17
    A:e14 --PRECEDES--> A:e18
    A:e15 --PRECEDES--> A:e19
    A:e15 --PRECEDES--> A:e20
    A:e16 --PRECEDES--> A:e19
    A:e16 --PRECEDES--> A:e20
    A:e17 --PRECEDES--> A:e19
    A:e17 --PRECEDES--> A:e20
    A:e18 --PRECEDES--> A:e19
    A:e18 --PRECEDES--> A:e20
    A:e19 --PRECEDES--> A:e21
    A:e19 --PRECEDES--> A:e22
    A:e20 --PRECEDES--> A:e21
    A:e20 --PRECEDES--> A:e22
    A:e07 --SAME_TRACK--> A:e08
    A:e07 --SAME_TRACK--> A:e12
    A:e07 --SAME_TRACK--> A:e14
    A:e07 --SAME_TRACK--> A:e16
    A:e07 --SAME_TRACK--> A:e17
```

## Perceived state before each event

Each row is the state just BEFORE its events (none of them applied): events at one time are simultaneous and share it. True states are named, unknown ones end with `?`, false ones are omitted; a lost track's states are UNKNOWN, never ended. Facts: the trace frame at the time shown.

| Local time | Events | Perceived state just before | Facts at |
|-----------:|--------|-----------------------------|---------:|
| 0.00 | A:e01 MOVING_START<br>A:e02 THROTTLE_START | ego: not yet observed | - |
| 0.50 | A:e03 INDICATOR_LEFT_START | ego: MOVING, THROTTLE | 0.40 |
| 1.00 | A:e04 STOP_SIGN_DETECTED_START sign-0 | ego: MOVING, THROTTLE, INDICATOR_LEFT | 0.90 |
| 1.95 | A:e05 THROTTLE_END<br>A:e06 BRAKE_START | ego: MOVING, THROTTLE, INDICATOR_LEFT<br>sign-0: STOP sign known, relevant to the path | 1.90 |
| 2.60 | A:e07 TRACK_APPEARED_LEFT track_001<br>A:e08 CLOSING_START track_001 | ego: MOVING, BRAKE, INDICATOR_LEFT<br>sign-0: STOP sign known, relevant to the path | 2.50 |
| 2.80 | A:e09 STOP_SIGN_DETECTED_END sign-0 | ego: MOVING, BRAKE, INDICATOR_LEFT<br>track_001: CLOSING, CRITICAL_TTC?<br>sign-0: STOP sign known, relevant to the path | 2.70 |
| 2.85 | A:e10 BRAKE_END<br>A:e11 THROTTLE_START | ego: MOVING, BRAKE, INDICATOR_LEFT<br>track_001: CLOSING, CRITICAL_TTC?<br>sign-0: STOP sign known, relevant to the path | 2.80 |
| 3.35 | A:e12 CRITICAL_TTC_START track_001 | ego: MOVING, THROTTLE, INDICATOR_LEFT<br>track_001: CLOSING<br>sign-0: STOP sign known, relevant to the path | 3.30 |
| 3.70 | A:e13 TURN_LEFT_START | ego: MOVING, THROTTLE, INDICATOR_LEFT<br>track_001: CLOSING, CRITICAL_TTC<br>sign-0: STOP sign known, relevant to the path | 3.60 |
| 4.15 | A:e14 EGO_PATH_ENTRY track_001 | ego: MOVING, THROTTLE, TURN_LEFT, INDICATOR_LEFT<br>track_001: CLOSING, CRITICAL_TTC<br>sign-0: STOP sign known, relevant to the path | 4.10 |
| 5.40 | A:e15 COLLISION<br>A:e16 CRITICAL_TTC_END track_001<br>A:e17 CLOSING_END track_001<br>A:e18 TURN_LEFT_END | ego: MOVING, THROTTLE, TURN_LEFT, INDICATOR_LEFT<br>track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH<br>sign-0: STOP sign known, relevant to the path | 5.30 |
| 5.45 | A:e19 THROTTLE_END<br>A:e20 BRAKE_START | ego: MOVING, THROTTLE, INDICATOR_LEFT<br>track_001: IN_EGO_PATH<br>sign-0: STOP sign known, relevant to the path | 5.40 |
| 5.50 | A:e21 MOVING_END<br>A:e22 STOP_START | ego: MOVING, BRAKE, INDICATOR_LEFT<br>track_001: IN_EGO_PATH<br>sign-0: STOP sign known, relevant to the path | 5.40 |

## States still active when observation ended

- INDICATOR_LEFT, since A:e03 (t = 0.50 s)
- EGO_PATH of track_001, since A:e14 (t = 4.15 s)
- BRAKE, since A:e20 (t = 5.45 s)
- STOP, since A:e22 (t = 5.50 s)

## Tracks lost

- no track was lost

## Temporal safety relations

Order of each track's cut-in, critical TTC and path entry and of the collision report, in local time. Temporal properties only, not causes.

- track_001: CRITICAL_TTC_START 3.35, COLLISION 5.40 (+2.05 s); EGO_PATH_ENTRY 4.15 after critical TTC (+0.80 s)

## Sign detection windows

- STOP sign sign-0: detected 1.00 s -> 2.80 s; relevant to the path: True; STOP_START inside: none

An END means this recorder stopped detecting the sign, not that its obligation ended.

## Anonymous radar tracks

| Track | First seen | Last seen | Measured sweeps | First range / bearing | Min range (at) | Last range / bearing | Max speed |
|-------|-----------:|----------:|----------------:|----------------------|----------------|---------------------|----------:|
| track_001 | 2.60 | 15.95 | 268 | 35.8 m / -66 deg | 0.26 m (9.30) | 0.3 m / -3 deg | 10.1 m/s |

Bearing: positive = to A's right. Ranges are measured from the radar to the visible surface of the object.

## Plain-language reading

- t = 0.00 s: A started moving (already the case when first observed).
- t = 0.00 s: A pressed the accelerator (already the case when first observed).
- t = 0.50 s: A switched on its left turn indicator.
- t = 1.00 s: A's camera established a STOP sign detection (sign-0).
- t = 1.95 s: A released the accelerator.
- t = 1.95 s: A started braking.
- t = 2.60 s: A's radar started tracking track_001, which appeared on its left.
- t = 2.60 s: A observed track_001 start closing in (already the case when first observed).
- t = 2.80 s: A's camera stopped detecting STOP sign sign-0.
- t = 2.85 s: A released the brake.
- t = 2.85 s: A pressed the accelerator.
- t = 3.35 s: A's time-to-contact with track_001 became critical.
- t = 3.70 s: A started turning left.
- t = 4.15 s: A observed track_001 enter its forward path corridor.
- t = 5.40 s: A's collision sensor recorded a contact (peak impulse 12940 N*s).
- t = 5.40 s: A's time-to-contact with track_001 stopped being critical.
- t = 5.40 s: A observed track_001 stop closing in.
- t = 5.40 s: A stopped turning left.
- t = 5.45 s: A released the accelerator.
- t = 5.45 s: A started braking.
- t = 5.50 s: A stopped moving.
- t = 5.50 s: A came to a stop.
