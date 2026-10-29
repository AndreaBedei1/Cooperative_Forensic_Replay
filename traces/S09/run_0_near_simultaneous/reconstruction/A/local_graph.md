# Local graph - vehicle A

All times are A's own local clock: `t_local` = seconds since A's first ego sample (raw clock reading 1970.0582870952785 at `t_local` = 0). Only files under `vehicles/A/` were read; external objects are anonymous radar tracks.

- Local frame: origin = first ego position; x = first heading; y = to the right of the first heading (CARLA convention)
- Trace: 130 frames at 10 Hz in `local_trace.jsonl`, the last one at the recording end (12.85 s)
- Anonymous radar tracks: 1 (10 Hz samples in `local_tracks.jsonl`)
- Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.
- Nodes: 26; edges: 47 (PRECEDES 41, SAME_TRACK 6)

## Nodes

| Id | Local time | Type | Actor | Subject | Source | Details |
|----|-----------:|------|-------|---------|--------|---------|
| A:e01 | 0.00 | MOVING_START | A | - | ego | active_at_first_observation=True |
| A:e02 | 0.00 | THROTTLE_START | A | - | controls | active_at_first_observation=True |
| A:e03 | 0.20 | STOP_SIGN_DETECTED_START | A | sign-0 | camera | relevant_to_ego_path=True |
| A:e04 | 2.40 | THROTTLE_END | A | - | controls |  |
| A:e05 | 2.40 | BRAKE_START | A | - | controls |  |
| A:e06 | 2.50 | TRACK_APPEARED_LEFT | A | track_001 | radar | initial_in_ego_path=False |
| A:e07 | 2.50 | CLOSING_START | A | track_001 | radar | active_at_first_observation=True |
| A:e08 | 2.75 | STOP_SIGN_DETECTED_END | A | sign-0 | camera |  |
| A:e09 | 3.70 | CLOSING_END | A | track_001 | radar |  |
| A:e10 | 3.70 | MOVING_END | A | - | ego |  |
| A:e11 | 3.70 | STOP_START | A | - | ego |  |
| A:e12 | 4.85 | BRAKE_END | A | - | controls |  |
| A:e13 | 4.85 | THROTTLE_START | A | - | controls |  |
| A:e14 | 5.10 | CLOSING_START | A | track_001 | radar |  |
| A:e15 | 5.20 | STOP_END | A | - | ego |  |
| A:e16 | 5.20 | MOVING_START | A | - | ego |  |
| A:e17 | 5.95 | CRITICAL_TTC_START | A | track_001 | radar |  |
| A:e18 | 6.15 | TURN_LEFT_START | A | - | ego |  |
| A:e19 | 7.15 | COLLISION | A | - | collision_sensor | peak_impulse=7661.46 |
| A:e20 | 7.15 | CRITICAL_TTC_END | A | track_001 | radar |  |
| A:e21 | 7.15 | CLOSING_END | A | track_001 | radar |  |
| A:e22 | 7.20 | THROTTLE_END | A | - | controls |  |
| A:e23 | 7.20 | BRAKE_START | A | - | controls |  |
| A:e24 | 7.65 | TURN_LEFT_END | A | - | ego |  |
| A:e25 | 7.65 | MOVING_END | A | - | ego |  |
| A:e26 | 7.65 | STOP_START | A | - | ego |  |

Events are state transitions; the quantities behind them (speed, pedals, ranges, TTC, relative motion, closest approach) are facts in `local_trace.jsonl`. Events with equal times are simultaneous at the recorder's resolution: PRECEDES links only different times. SAME_TRACK links a track's TRACK_APPEARED_* to every other event about the same local track (grouping only, no order).

## Edges

```
    A:e01 --PRECEDES--> A:e03
    A:e02 --PRECEDES--> A:e03
    A:e03 --PRECEDES--> A:e04
    A:e03 --PRECEDES--> A:e05
    A:e04 --PRECEDES--> A:e06
    A:e04 --PRECEDES--> A:e07
    A:e05 --PRECEDES--> A:e06
    A:e05 --PRECEDES--> A:e07
    A:e06 --PRECEDES--> A:e08
    A:e07 --PRECEDES--> A:e08
    A:e08 --PRECEDES--> A:e09
    A:e08 --PRECEDES--> A:e10
    A:e08 --PRECEDES--> A:e11
    A:e09 --PRECEDES--> A:e12
    A:e09 --PRECEDES--> A:e13
    A:e10 --PRECEDES--> A:e12
    A:e10 --PRECEDES--> A:e13
    A:e11 --PRECEDES--> A:e12
    A:e11 --PRECEDES--> A:e13
    A:e12 --PRECEDES--> A:e14
    A:e13 --PRECEDES--> A:e14
    A:e14 --PRECEDES--> A:e15
    A:e14 --PRECEDES--> A:e16
    A:e15 --PRECEDES--> A:e17
    A:e16 --PRECEDES--> A:e17
    A:e17 --PRECEDES--> A:e18
    A:e18 --PRECEDES--> A:e19
    A:e18 --PRECEDES--> A:e20
    A:e18 --PRECEDES--> A:e21
    A:e19 --PRECEDES--> A:e22
    A:e19 --PRECEDES--> A:e23
    A:e20 --PRECEDES--> A:e22
    A:e20 --PRECEDES--> A:e23
    A:e21 --PRECEDES--> A:e22
    A:e21 --PRECEDES--> A:e23
    A:e22 --PRECEDES--> A:e24
    A:e22 --PRECEDES--> A:e25
    A:e22 --PRECEDES--> A:e26
    A:e23 --PRECEDES--> A:e24
    A:e23 --PRECEDES--> A:e25
    A:e23 --PRECEDES--> A:e26
    A:e06 --SAME_TRACK--> A:e07
    A:e06 --SAME_TRACK--> A:e09
    A:e06 --SAME_TRACK--> A:e14
    A:e06 --SAME_TRACK--> A:e17
    A:e06 --SAME_TRACK--> A:e20
    A:e06 --SAME_TRACK--> A:e21
```

## Perceived state before each event

Each row is the state just BEFORE its events (none of them applied): events at one time are simultaneous and share it. True states are named, unknown ones end with `?`, false ones are omitted; a lost track's states are UNKNOWN, never ended. Facts: the trace frame at the time shown.

| Local time | Events | Perceived state just before | Facts at |
|-----------:|--------|-----------------------------|---------:|
| 0.00 | A:e01 MOVING_START<br>A:e02 THROTTLE_START | ego: not yet observed | - |
| 0.20 | A:e03 STOP_SIGN_DETECTED_START sign-0 | ego: MOVING, THROTTLE | 0.10 |
| 2.40 | A:e04 THROTTLE_END<br>A:e05 BRAKE_START | ego: MOVING, THROTTLE<br>sign-0: STOP sign known, relevant to the path | 2.30 |
| 2.50 | A:e06 TRACK_APPEARED_LEFT track_001<br>A:e07 CLOSING_START track_001 | ego: MOVING, BRAKE<br>sign-0: STOP sign known, relevant to the path | 2.40 |
| 2.75 | A:e08 STOP_SIGN_DETECTED_END sign-0 | ego: MOVING, BRAKE<br>track_001: CLOSING, CRITICAL_TTC?<br>sign-0: STOP sign known, relevant to the path | 2.70 |
| 3.70 | A:e09 CLOSING_END track_001<br>A:e10 MOVING_END<br>A:e11 STOP_START | ego: MOVING, BRAKE<br>track_001: CLOSING<br>sign-0: STOP sign known, relevant to the path | 3.60 |
| 4.85 | A:e12 BRAKE_END<br>A:e13 THROTTLE_START | ego: STOP, BRAKE<br>track_001: no active state<br>sign-0: STOP sign known, relevant to the path | 4.80 |
| 5.10 | A:e14 CLOSING_START track_001 | ego: STOP, THROTTLE<br>track_001: no active state<br>sign-0: STOP sign known, relevant to the path | 5.00 |
| 5.20 | A:e15 STOP_END<br>A:e16 MOVING_START | ego: STOP, THROTTLE<br>track_001: CLOSING<br>sign-0: STOP sign known, relevant to the path | 5.10 |
| 5.95 | A:e17 CRITICAL_TTC_START track_001 | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>sign-0: STOP sign known, relevant to the path | 5.90 |
| 6.15 | A:e18 TURN_LEFT_START | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC<br>sign-0: STOP sign known, relevant to the path | 6.10 |
| 7.15 | A:e19 COLLISION<br>A:e20 CRITICAL_TTC_END track_001<br>A:e21 CLOSING_END track_001 | ego: MOVING, THROTTLE, TURN_LEFT<br>track_001: CLOSING, CRITICAL_TTC<br>sign-0: STOP sign known, relevant to the path | 7.10 |
| 7.20 | A:e22 THROTTLE_END<br>A:e23 BRAKE_START | ego: MOVING, THROTTLE, TURN_LEFT<br>track_001: no active state<br>sign-0: STOP sign known, relevant to the path | 7.10 |
| 7.65 | A:e24 TURN_LEFT_END<br>A:e25 MOVING_END<br>A:e26 STOP_START | ego: MOVING, BRAKE, TURN_LEFT<br>track_001: no active state<br>sign-0: STOP sign known, relevant to the path | 7.60 |

## States still active when observation ended

- BRAKE, since A:e23 (t = 7.20 s)
- STOP, since A:e26 (t = 7.65 s)

## Tracks lost

- no track was lost

## Temporal safety relations

Order of each track's cut-in, critical TTC and path entry and of the collision report, in local time. Temporal properties only, not causes.

- track_001: CRITICAL_TTC_START 5.95, COLLISION 7.15 (+1.20 s)

## Sign detection windows

- STOP sign sign-0: detected 0.20 s -> 2.75 s; relevant to the path: True; STOP_START inside: none

An END means this recorder stopped detecting the sign, not that its obligation ended.

## Anonymous radar tracks

| Track | First seen | Last seen | Measured sweeps | First range / bearing | Min range (at) | Last range / bearing | Max speed |
|-------|-----------:|----------:|----------------:|----------------------|----------------|---------------------|----------:|
| track_001 | 2.50 | 12.85 | 208 | 28.4 m / -53 deg | 0.70 m (7.15) | 1.5 m / -96 deg | 9.8 m/s |

Bearing: positive = to A's right. Ranges are measured from the radar to the visible surface of the object.

## Plain-language reading

- t = 0.00 s: A started moving (already the case when first observed).
- t = 0.00 s: A pressed the accelerator (already the case when first observed).
- t = 0.20 s: A's camera established a STOP sign detection (sign-0).
- t = 2.40 s: A released the accelerator.
- t = 2.40 s: A started braking.
- t = 2.50 s: A's radar started tracking track_001, which appeared on its left.
- t = 2.50 s: A observed track_001 start closing in (already the case when first observed).
- t = 2.75 s: A's camera stopped detecting STOP sign sign-0.
- t = 3.70 s: A observed track_001 stop closing in.
- t = 3.70 s: A stopped moving.
- t = 3.70 s: A came to a stop.
- t = 4.85 s: A released the brake.
- t = 4.85 s: A pressed the accelerator.
- t = 5.10 s: A observed track_001 start closing in.
- t = 5.20 s: A left its stop.
- t = 5.20 s: A started moving.
- t = 5.95 s: A's time-to-contact with track_001 became critical.
- t = 6.15 s: A started turning left.
- t = 7.15 s: A's collision sensor recorded a contact (peak impulse 7661 N*s).
- t = 7.15 s: A's time-to-contact with track_001 stopped being critical.
- t = 7.15 s: A observed track_001 stop closing in.
- t = 7.20 s: A released the accelerator.
- t = 7.20 s: A started braking.
- t = 7.65 s: A stopped turning left.
- t = 7.65 s: A stopped moving.
- t = 7.65 s: A came to a stop.
