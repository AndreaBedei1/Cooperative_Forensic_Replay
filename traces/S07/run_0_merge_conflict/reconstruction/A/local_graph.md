# Local graph - vehicle A

All times are A's own local clock: `t_local` = seconds since A's first ego sample (raw clock reading 28.253541942685843 at `t_local` = 0). Only files under `vehicles/A/` were read; external objects are anonymous radar tracks.

- Local frame: origin = first ego position; x = first heading; y = to the right of the first heading (CARLA convention)
- Trace: 325 frames at 10 Hz in `local_trace.jsonl`, the last one at the recording end (32.35 s)
- Anonymous radar tracks: 1 (10 Hz samples in `local_tracks.jsonl`)
- Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.
- Nodes: 17; edges: 26 (PRECEDES 22, SAME_TRACK 4)

## Nodes

| Id | Local time | Type | Actor | Subject | Source | Details |
|----|-----------:|------|-------|---------|--------|---------|
| A:e01 | 0.00 | MOVING_START | A | - | ego | active_at_first_observation=True |
| A:e02 | 0.00 | THROTTLE_START | A | - | controls | active_at_first_observation=True |
| A:e03 | 1.00 | INDICATOR_LEFT_START | A | - | lights |  |
| A:e04 | 3.25 | TURN_RIGHT_START | A | - | ego |  |
| A:e05 | 5.20 | TURN_RIGHT_END | A | - | ego |  |
| A:e06 | 6.35 | TURN_LEFT_START | A | - | ego |  |
| A:e07 | 11.65 | TRACK_APPEARED_LEFT | A | track_001 | radar | initial_in_ego_path=False |
| A:e08 | 11.65 | CLOSING_START | A | track_001 | radar | active_at_first_observation=True |
| A:e09 | 15.85 | CRITICAL_TTC_START | A | track_001 | radar |  |
| A:e10 | 19.25 | COLLISION | A | - | collision_sensor | peak_impulse=1928.22; merged_bursts=[[19.85, 6.8]] |
| A:e11 | 19.25 | CRITICAL_TTC_END | A | track_001 | radar |  |
| A:e12 | 19.25 | CLOSING_END | A | track_001 | radar |  |
| A:e13 | 19.30 | THROTTLE_END | A | - | controls |  |
| A:e14 | 19.30 | BRAKE_START | A | - | controls |  |
| A:e15 | 19.50 | TURN_LEFT_END | A | - | ego |  |
| A:e16 | 20.05 | MOVING_END | A | - | ego |  |
| A:e17 | 20.05 | STOP_START | A | - | ego |  |

Events are state transitions; the quantities behind them (speed, pedals, ranges, TTC, relative motion, closest approach) are facts in `local_trace.jsonl`. Events with equal times are simultaneous at the recorder's resolution: PRECEDES links only different times. SAME_TRACK links a track's TRACK_APPEARED_* to every other event about the same local track (grouping only, no order).

## Edges

```
    A:e01 --PRECEDES--> A:e03
    A:e02 --PRECEDES--> A:e03
    A:e03 --PRECEDES--> A:e04
    A:e04 --PRECEDES--> A:e05
    A:e05 --PRECEDES--> A:e06
    A:e06 --PRECEDES--> A:e07
    A:e06 --PRECEDES--> A:e08
    A:e07 --PRECEDES--> A:e09
    A:e08 --PRECEDES--> A:e09
    A:e09 --PRECEDES--> A:e10
    A:e09 --PRECEDES--> A:e11
    A:e09 --PRECEDES--> A:e12
    A:e10 --PRECEDES--> A:e13
    A:e10 --PRECEDES--> A:e14
    A:e11 --PRECEDES--> A:e13
    A:e11 --PRECEDES--> A:e14
    A:e12 --PRECEDES--> A:e13
    A:e12 --PRECEDES--> A:e14
    A:e13 --PRECEDES--> A:e15
    A:e14 --PRECEDES--> A:e15
    A:e15 --PRECEDES--> A:e16
    A:e15 --PRECEDES--> A:e17
    A:e07 --SAME_TRACK--> A:e08
    A:e07 --SAME_TRACK--> A:e09
    A:e07 --SAME_TRACK--> A:e11
    A:e07 --SAME_TRACK--> A:e12
```

## Perceived state before each event

Each row is the state just BEFORE its events (none of them applied): events at one time are simultaneous and share it. True states are named, unknown ones end with `?`, false ones are omitted; a lost track's states are UNKNOWN, never ended. Facts: the trace frame at the time shown.

| Local time | Events | Perceived state just before | Facts at |
|-----------:|--------|-----------------------------|---------:|
| 0.00 | A:e01 MOVING_START<br>A:e02 THROTTLE_START | ego: not yet observed | - |
| 1.00 | A:e03 INDICATOR_LEFT_START | ego: MOVING, THROTTLE | 0.90 |
| 3.25 | A:e04 TURN_RIGHT_START | ego: MOVING, THROTTLE, INDICATOR_LEFT | 3.20 |
| 5.20 | A:e05 TURN_RIGHT_END | ego: MOVING, THROTTLE, TURN_RIGHT, INDICATOR_LEFT | 5.10 |
| 6.35 | A:e06 TURN_LEFT_START | ego: MOVING, THROTTLE, INDICATOR_LEFT | 6.30 |
| 11.65 | A:e07 TRACK_APPEARED_LEFT track_001<br>A:e08 CLOSING_START track_001 | ego: MOVING, THROTTLE, TURN_LEFT, INDICATOR_LEFT | 11.60 |
| 15.85 | A:e09 CRITICAL_TTC_START track_001 | ego: MOVING, THROTTLE, TURN_LEFT, INDICATOR_LEFT<br>track_001: CLOSING | 15.80 |
| 19.25 | A:e10 COLLISION<br>A:e11 CRITICAL_TTC_END track_001<br>A:e12 CLOSING_END track_001 | ego: MOVING, THROTTLE, TURN_LEFT, INDICATOR_LEFT<br>track_001: CLOSING, CRITICAL_TTC | 19.20 |
| 19.30 | A:e13 THROTTLE_END<br>A:e14 BRAKE_START | ego: MOVING, THROTTLE, TURN_LEFT, INDICATOR_LEFT<br>track_001: no active state | 19.20 |
| 19.50 | A:e15 TURN_LEFT_END | ego: MOVING, BRAKE, TURN_LEFT, INDICATOR_LEFT<br>track_001: no active state | 19.40 |
| 20.05 | A:e16 MOVING_END<br>A:e17 STOP_START | ego: MOVING, BRAKE, INDICATOR_LEFT<br>track_001: no active state | 20.00 |

## States still active when observation ended

- INDICATOR_LEFT, since A:e03 (t = 1.00 s)
- BRAKE, since A:e14 (t = 19.30 s)
- STOP, since A:e17 (t = 20.05 s)

## Tracks lost

- no track was lost

## Temporal safety relations

Order of each track's cut-in, critical TTC and path entry and of the collision report, in local time. Temporal properties only, not causes.

- track_001: CRITICAL_TTC_START 15.85, COLLISION 19.25 (+3.40 s)

## Sign detection windows

- none

An END means this recorder stopped detecting the sign, not that its obligation ended.

## Anonymous radar tracks

| Track | First seen | Last seen | Measured sweeps | First range / bearing | Min range (at) | Last range / bearing | Max speed |
|-------|-----------:|----------:|----------------:|----------------------|----------------|---------------------|----------:|
| track_001 | 11.65 | 32.35 | 407 | 88.1 m / -44 deg | 0.06 m (31.80) | 0.1 m / +90 deg | 10.0 m/s |

Bearing: positive = to A's right. Ranges are measured from the radar to the visible surface of the object.

## Plain-language reading

- t = 0.00 s: A started moving (already the case when first observed).
- t = 0.00 s: A pressed the accelerator (already the case when first observed).
- t = 1.00 s: A switched on its left turn indicator.
- t = 3.25 s: A started turning right.
- t = 5.20 s: A stopped turning right.
- t = 6.35 s: A started turning left.
- t = 11.65 s: A's radar started tracking track_001, which appeared on its left.
- t = 11.65 s: A observed track_001 start closing in (already the case when first observed).
- t = 15.85 s: A's time-to-contact with track_001 became critical.
- t = 19.25 s: A's collision sensor recorded a contact (peak impulse 1928 N*s).
- t = 19.25 s: A's time-to-contact with track_001 stopped being critical.
- t = 19.25 s: A observed track_001 stop closing in.
- t = 19.30 s: A released the accelerator.
- t = 19.30 s: A started braking.
- t = 19.50 s: A stopped turning left.
- t = 20.05 s: A stopped moving.
- t = 20.05 s: A came to a stop.
