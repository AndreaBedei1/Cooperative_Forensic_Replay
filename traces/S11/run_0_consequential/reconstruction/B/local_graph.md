# Local graph - vehicle B

All times are B's own local clock: `t_local` = seconds since B's first ego sample (raw clock reading 2005.8708217665553 at `t_local` = 0). Only files under `vehicles/B/` were read; external objects are anonymous radar tracks.

- Local frame: origin = first ego position; x = first heading; y = to the right of the first heading (CARLA convention)
- Trace: 121 frames at 10 Hz in `local_trace.jsonl`, the last one at the recording end (11.95 s)
- Anonymous radar tracks: 2 (10 Hz samples in `local_tracks.jsonl`)
- Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.
- Nodes: 15; edges: 23 (PRECEDES 17, SAME_TRACK 6)

## Nodes

| Id | Local time | Type | Actor | Subject | Source | Details |
|----|-----------:|------|-------|---------|--------|---------|
| B:e01 | 0.00 | MOVING_START | B | - | ego | active_at_first_observation=True |
| B:e02 | 0.00 | THROTTLE_START | B | - | controls | active_at_first_observation=True |
| B:e03 | 0.00 | TRACK_APPEARED_FRONT | B | track_001 | radar | initial_in_ego_path=True |
| B:e04 | 0.00 | TRACK_APPEARED_LEFT | B | track_002 | radar | initial_in_ego_path=False |
| B:e05 | 0.00 | CLOSING_START | B | track_002 | radar | active_at_first_observation=True |
| B:e06 | 0.50 | CRITICAL_TTC_START | B | track_001 | radar |  |
| B:e07 | 4.10 | CLOSING_START | B | track_001 | radar |  |
| B:e08 | 5.40 | THROTTLE_END | B | - | controls |  |
| B:e09 | 5.40 | BRAKE_START | B | - | controls |  |
| B:e10 | 5.55 | COLLISION | B | - | collision_sensor | peak_impulse=4243.51 |
| B:e11 | 5.55 | CRITICAL_TTC_END | B | track_001 | radar |  |
| B:e12 | 5.60 | CLOSING_END | B | track_001 | radar |  |
| B:e13 | 5.80 | CLOSING_END | B | track_002 | radar |  |
| B:e14 | 6.20 | MOVING_END | B | - | ego |  |
| B:e15 | 6.20 | STOP_START | B | - | ego |  |

Events are state transitions; the quantities behind them (speed, pedals, ranges, TTC, relative motion, closest approach) are facts in `local_trace.jsonl`. Events with equal times are simultaneous at the recorder's resolution: PRECEDES links only different times. SAME_TRACK links a track's TRACK_APPEARED_* to every other event about the same local track (grouping only, no order).

## Edges

```
    B:e01 --PRECEDES--> B:e06
    B:e02 --PRECEDES--> B:e06
    B:e03 --PRECEDES--> B:e06
    B:e04 --PRECEDES--> B:e06
    B:e05 --PRECEDES--> B:e06
    B:e06 --PRECEDES--> B:e07
    B:e07 --PRECEDES--> B:e08
    B:e07 --PRECEDES--> B:e09
    B:e08 --PRECEDES--> B:e10
    B:e08 --PRECEDES--> B:e11
    B:e09 --PRECEDES--> B:e10
    B:e09 --PRECEDES--> B:e11
    B:e10 --PRECEDES--> B:e12
    B:e11 --PRECEDES--> B:e12
    B:e12 --PRECEDES--> B:e13
    B:e13 --PRECEDES--> B:e14
    B:e13 --PRECEDES--> B:e15
    B:e04 --SAME_TRACK--> B:e05
    B:e03 --SAME_TRACK--> B:e06
    B:e03 --SAME_TRACK--> B:e07
    B:e03 --SAME_TRACK--> B:e11
    B:e03 --SAME_TRACK--> B:e12
    B:e04 --SAME_TRACK--> B:e13
```

## Perceived state before each event

Each row is the state just BEFORE its events (none of them applied): events at one time are simultaneous and share it. True states are named, unknown ones end with `?`, false ones are omitted; a lost track's states are UNKNOWN, never ended. Facts: the trace frame at the time shown.

| Local time | Events | Perceived state just before | Facts at |
|-----------:|--------|-----------------------------|---------:|
| 0.00 | B:e01 MOVING_START<br>B:e02 THROTTLE_START<br>B:e03 TRACK_APPEARED_FRONT track_001<br>B:e04 TRACK_APPEARED_LEFT track_002<br>B:e05 CLOSING_START track_002 | ego: not yet observed | - |
| 0.50 | B:e06 CRITICAL_TTC_START track_001 | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH, CRITICAL_TTC?<br>track_002: CLOSING, CRITICAL_TTC? | 0.40 |
| 4.10 | B:e07 CLOSING_START track_001 | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: CLOSING | 4.00 |
| 5.40 | B:e08 THROTTLE_END<br>B:e09 BRAKE_START | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH<br>track_002: CLOSING | 5.30 |
| 5.55 | B:e10 COLLISION<br>B:e11 CRITICAL_TTC_END track_001 | ego: MOVING, BRAKE<br>track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH<br>track_002: CLOSING | 5.50 |
| 5.60 | B:e12 CLOSING_END track_001 | ego: MOVING, BRAKE<br>track_001: CLOSING, IN_EGO_PATH<br>track_002: CLOSING | 5.50 |
| 5.80 | B:e13 CLOSING_END track_002 | ego: MOVING, BRAKE<br>track_001: IN_EGO_PATH<br>track_002: CLOSING | 5.70 |
| 6.20 | B:e14 MOVING_END<br>B:e15 STOP_START | ego: MOVING, BRAKE<br>track_001: IN_EGO_PATH<br>track_002: no active state | 6.10 |

## States still active when observation ended

- BRAKE, since B:e09 (t = 5.40 s)
- STOP, since B:e15 (t = 6.20 s)

## Tracks lost

- no track was lost

## Temporal safety relations

Order of each track's cut-in, critical TTC and path entry and of the collision report, in local time. Temporal properties only, not causes.

- track_001: CRITICAL_TTC_START 0.50, COLLISION 5.55 (+5.05 s)

## Sign detection windows

- none

An END means this recorder stopped detecting the sign, not that its obligation ended.

## Anonymous radar tracks

| Track | First seen | Last seen | Measured sweeps | First range / bearing | Min range (at) | Last range / bearing | Max speed |
|-------|-----------:|----------:|----------------:|----------------------|----------------|---------------------|----------:|
| track_001 | 0.00 | 11.95 | 240 | 7.4 m / +0 deg | 0.28 m (5.50) | 12.6 m / -8 deg | 11.9 m/s |
| track_002 | 0.00 | 11.95 | 230 | 25.5 m / -8 deg | 6.65 m (5.55) | 16.7 m / -11 deg | 9.4 m/s |

Bearing: positive = to B's right. Ranges are measured from the radar to the visible surface of the object.

## Plain-language reading

- t = 0.00 s: B started moving (already the case when first observed).
- t = 0.00 s: B pressed the accelerator (already the case when first observed).
- t = 0.00 s: B's radar started tracking track_001, which appeared in front of it.
- t = 0.00 s: B's radar started tracking track_002, which appeared on its left.
- t = 0.00 s: B observed track_002 start closing in (already the case when first observed).
- t = 0.50 s: B's time-to-contact with track_001 became critical.
- t = 4.10 s: B observed track_001 start closing in.
- t = 5.40 s: B released the accelerator.
- t = 5.40 s: B started braking.
- t = 5.55 s: B's collision sensor recorded a contact (peak impulse 4244 N*s).
- t = 5.55 s: B's time-to-contact with track_001 stopped being critical.
- t = 5.60 s: B observed track_001 stop closing in.
- t = 5.80 s: B observed track_002 stop closing in.
- t = 6.20 s: B stopped moving.
- t = 6.20 s: B came to a stop.
