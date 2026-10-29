# Local graph - vehicle A

All times are A's own local clock: `t_local` = seconds since A's first ego sample (raw clock reading 1987.095780223608 at `t_local` = 0). Only files under `vehicles/A/` were read; external objects are anonymous radar tracks.

- Local frame: origin = first ego position; x = first heading; y = to the right of the first heading (CARLA convention)
- Trace: 141 frames at 10 Hz in `local_trace.jsonl`, the last one at the recording end (13.95 s)
- Anonymous radar tracks: 2 (10 Hz samples in `local_tracks.jsonl`)
- Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.
- Nodes: 19; edges: 36 (PRECEDES 28, SAME_TRACK 8)

## Nodes

| Id | Local time | Type | Actor | Subject | Source | Details |
|----|-----------:|------|-------|---------|--------|---------|
| A:e01 | 0.00 | MOVING_START | A | - | ego | active_at_first_observation=True |
| A:e02 | 0.00 | THROTTLE_START | A | - | controls | active_at_first_observation=True |
| A:e03 | 0.00 | TRACK_APPEARED_FRONT | A | track_001 | radar | initial_in_ego_path=False |
| A:e04 | 0.00 | CLOSING_START | A | track_001 | radar | active_at_first_observation=True |
| A:e05 | 2.05 | TRACK_APPEARED_RIGHT | A | track_002 | radar | initial_in_ego_path=False |
| A:e06 | 2.05 | CLOSING_START | A | track_002 | radar | active_at_first_observation=True |
| A:e07 | 2.55 | CRITICAL_TTC_START | A | track_002 | radar |  |
| A:e08 | 3.75 | CRITICAL_TTC_START | A | track_001 | radar |  |
| A:e09 | 3.80 | COLLISION | A | - | collision_sensor | peak_impulse=10358.22 |
| A:e10 | 3.80 | CRITICAL_TTC_END | A | track_002 | radar |  |
| A:e11 | 3.80 | CLOSING_END | A | track_002 | radar |  |
| A:e12 | 3.85 | THROTTLE_END | A | - | controls |  |
| A:e13 | 3.85 | TURN_LEFT_START | A | - | ego |  |
| A:e14 | 4.65 | CLOSING_END | A | track_001 | radar |  |
| A:e15 | 4.70 | COLLISION | A | - | collision_sensor | peak_impulse=2250.28; merged_bursts=[[4.8, 765.39], [6.1, 3.03], [6.75, 0.2]] |
| A:e16 | 4.70 | CRITICAL_TTC_END | A | track_001 | radar |  |
| A:e17 | 5.15 | TURN_LEFT_END | A | - | ego |  |
| A:e18 | 5.25 | MOVING_END | A | - | ego |  |
| A:e19 | 5.25 | STOP_START | A | - | ego |  |

Events are state transitions; the quantities behind them (speed, pedals, ranges, TTC, relative motion, closest approach) are facts in `local_trace.jsonl`. Events with equal times are simultaneous at the recorder's resolution: PRECEDES links only different times. SAME_TRACK links a track's TRACK_APPEARED_* to every other event about the same local track (grouping only, no order).

## Edges

```
    A:e01 --PRECEDES--> A:e05
    A:e01 --PRECEDES--> A:e06
    A:e02 --PRECEDES--> A:e05
    A:e02 --PRECEDES--> A:e06
    A:e03 --PRECEDES--> A:e05
    A:e03 --PRECEDES--> A:e06
    A:e04 --PRECEDES--> A:e05
    A:e04 --PRECEDES--> A:e06
    A:e05 --PRECEDES--> A:e07
    A:e06 --PRECEDES--> A:e07
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
    A:e17 --PRECEDES--> A:e19
    A:e03 --SAME_TRACK--> A:e04
    A:e05 --SAME_TRACK--> A:e06
    A:e05 --SAME_TRACK--> A:e07
    A:e03 --SAME_TRACK--> A:e08
    A:e05 --SAME_TRACK--> A:e10
    A:e05 --SAME_TRACK--> A:e11
    A:e03 --SAME_TRACK--> A:e14
    A:e03 --SAME_TRACK--> A:e16
```

## Perceived state before each event

Each row is the state just BEFORE its events (none of them applied): events at one time are simultaneous and share it. True states are named, unknown ones end with `?`, false ones are omitted; a lost track's states are UNKNOWN, never ended. Facts: the trace frame at the time shown.

| Local time | Events | Perceived state just before | Facts at |
|-----------:|--------|-----------------------------|---------:|
| 0.00 | A:e01 MOVING_START<br>A:e02 THROTTLE_START<br>A:e03 TRACK_APPEARED_FRONT track_001<br>A:e04 CLOSING_START track_001 | ego: not yet observed | - |
| 2.05 | A:e05 TRACK_APPEARED_RIGHT track_002<br>A:e06 CLOSING_START track_002 | ego: MOVING, THROTTLE<br>track_001: CLOSING | 2.00 |
| 2.55 | A:e07 CRITICAL_TTC_START track_002 | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>track_002: CLOSING, CRITICAL_TTC? | 2.50 |
| 3.75 | A:e08 CRITICAL_TTC_START track_001 | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>track_002: CLOSING, CRITICAL_TTC | 3.70 |
| 3.80 | A:e09 COLLISION<br>A:e10 CRITICAL_TTC_END track_002<br>A:e11 CLOSING_END track_002 | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC<br>track_002: CLOSING, CRITICAL_TTC | 3.70 |
| 3.85 | A:e12 THROTTLE_END<br>A:e13 TURN_LEFT_START | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC<br>track_002: no active state | 3.80 |
| 4.65 | A:e14 CLOSING_END track_001 | ego: MOVING, TURN_LEFT<br>track_001: CLOSING, CRITICAL_TTC<br>track_002: no active state | 4.60 |
| 4.70 | A:e15 COLLISION<br>A:e16 CRITICAL_TTC_END track_001 | ego: MOVING, TURN_LEFT<br>track_001: CRITICAL_TTC<br>track_002: no active state | 4.60 |
| 5.15 | A:e17 TURN_LEFT_END | ego: MOVING, TURN_LEFT<br>track_001: no active state<br>track_002: no active state | 5.10 |
| 5.25 | A:e18 MOVING_END<br>A:e19 STOP_START | ego: MOVING<br>track_001: no active state<br>track_002: no active state | 5.20 |

## States still active when observation ended

- STOP, since A:e19 (t = 5.25 s)

## Tracks lost

- no track was lost

## Temporal safety relations

Order of each track's cut-in, critical TTC and path entry and of the collision report, in local time. Temporal properties only, not causes.

- track_001: CRITICAL_TTC_START 3.75, COLLISION 3.80 (+0.05 s)
- track_002: CRITICAL_TTC_START 2.55, COLLISION 3.80 (+1.25 s)

## Sign detection windows

- none

An END means this recorder stopped detecting the sign, not that its obligation ended.

## Anonymous radar tracks

| Track | First seen | Last seen | Measured sweeps | First range / bearing | Min range (at) | Last range / bearing | Max speed |
|-------|-----------:|----------:|----------------:|----------------------|----------------|---------------------|----------:|
| track_001 | 0.00 | 13.95 | 278 | 73.8 m / -3 deg | 0.15 m (13.45) | 0.1 m / -88 deg | 6.1 m/s |
| track_002 | 2.05 | 13.95 | 239 | 28.6 m / +31 deg | 1.79 m (4.25) | 5.0 m / +141 deg | 9.8 m/s |

Bearing: positive = to A's right. Ranges are measured from the radar to the visible surface of the object.

## Plain-language reading

- t = 0.00 s: A started moving (already the case when first observed).
- t = 0.00 s: A pressed the accelerator (already the case when first observed).
- t = 0.00 s: A's radar started tracking track_001, which appeared in front of it.
- t = 0.00 s: A observed track_001 start closing in (already the case when first observed).
- t = 2.05 s: A's radar started tracking track_002, which appeared on its right.
- t = 2.05 s: A observed track_002 start closing in (already the case when first observed).
- t = 2.55 s: A's time-to-contact with track_002 became critical.
- t = 3.75 s: A's time-to-contact with track_001 became critical.
- t = 3.80 s: A's collision sensor recorded a contact (peak impulse 10358 N*s).
- t = 3.80 s: A's time-to-contact with track_002 stopped being critical.
- t = 3.80 s: A observed track_002 stop closing in.
- t = 3.85 s: A released the accelerator.
- t = 3.85 s: A started turning left.
- t = 4.65 s: A observed track_001 stop closing in.
- t = 4.70 s: A's collision sensor recorded a contact (peak impulse 2250 N*s).
- t = 4.70 s: A's time-to-contact with track_001 stopped being critical.
- t = 5.15 s: A stopped turning left.
- t = 5.25 s: A stopped moving.
- t = 5.25 s: A came to a stop.
