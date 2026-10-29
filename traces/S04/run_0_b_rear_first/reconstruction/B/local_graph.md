# Local graph - vehicle B

All times are B's own local clock: `t_local` = seconds since B's first ego sample (raw clock reading 1892.6789430752397 at `t_local` = 0). Only files under `vehicles/B/` were read; external objects are anonymous radar tracks.

- Local frame: origin = first ego position; x = first heading; y = to the right of the first heading (CARLA convention)
- Trace: 143 frames at 10 Hz in `local_trace.jsonl`, the last one at the recording end (14.15 s)
- Anonymous radar tracks: 1 (10 Hz samples in `local_tracks.jsonl`)
- Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.
- Nodes: 13; edges: 23 (PRECEDES 19, SAME_TRACK 4)

## Nodes

| Id | Local time | Type | Actor | Subject | Source | Details |
|----|-----------:|------|-------|---------|--------|---------|
| B:e01 | 0.00 | MOVING_START | B | - | ego | active_at_first_observation=True |
| B:e02 | 0.00 | THROTTLE_START | B | - | controls | active_at_first_observation=True |
| B:e03 | 0.00 | TRACK_APPEARED_FRONT | B | track_001 | radar | initial_in_ego_path=True |
| B:e04 | 0.50 | CRITICAL_TTC_START | B | track_001 | radar |  |
| B:e05 | 3.20 | CLOSING_START | B | track_001 | radar |  |
| B:e06 | 4.70 | COLLISION | B | - | collision_sensor | peak_impulse=21842.46 |
| B:e07 | 4.70 | CRITICAL_TTC_END | B | track_001 | radar |  |
| B:e08 | 4.70 | CLOSING_END | B | track_001 | radar |  |
| B:e09 | 4.75 | THROTTLE_END | B | - | controls |  |
| B:e10 | 4.75 | BRAKE_START | B | - | controls |  |
| B:e11 | 4.85 | MOVING_END | B | - | ego |  |
| B:e12 | 4.85 | STOP_START | B | - | ego |  |
| B:e13 | 6.25 | COLLISION | B | - | collision_sensor | peak_impulse=31706.31 |

Events are state transitions; the quantities behind them (speed, pedals, ranges, TTC, relative motion, closest approach) are facts in `local_trace.jsonl`. Events with equal times are simultaneous at the recorder's resolution: PRECEDES links only different times. SAME_TRACK links a track's TRACK_APPEARED_* to every other event about the same local track (grouping only, no order).

## Edges

```
    B:e01 --PRECEDES--> B:e04
    B:e02 --PRECEDES--> B:e04
    B:e03 --PRECEDES--> B:e04
    B:e04 --PRECEDES--> B:e05
    B:e05 --PRECEDES--> B:e06
    B:e05 --PRECEDES--> B:e07
    B:e05 --PRECEDES--> B:e08
    B:e06 --PRECEDES--> B:e09
    B:e06 --PRECEDES--> B:e10
    B:e07 --PRECEDES--> B:e09
    B:e07 --PRECEDES--> B:e10
    B:e08 --PRECEDES--> B:e09
    B:e08 --PRECEDES--> B:e10
    B:e09 --PRECEDES--> B:e11
    B:e09 --PRECEDES--> B:e12
    B:e10 --PRECEDES--> B:e11
    B:e10 --PRECEDES--> B:e12
    B:e11 --PRECEDES--> B:e13
    B:e12 --PRECEDES--> B:e13
    B:e03 --SAME_TRACK--> B:e04
    B:e03 --SAME_TRACK--> B:e05
    B:e03 --SAME_TRACK--> B:e07
    B:e03 --SAME_TRACK--> B:e08
```

## Perceived state before each event

Each row is the state just BEFORE its events (none of them applied): events at one time are simultaneous and share it. True states are named, unknown ones end with `?`, false ones are omitted; a lost track's states are UNKNOWN, never ended. Facts: the trace frame at the time shown.

| Local time | Events | Perceived state just before | Facts at |
|-----------:|--------|-----------------------------|---------:|
| 0.00 | B:e01 MOVING_START<br>B:e02 THROTTLE_START<br>B:e03 TRACK_APPEARED_FRONT track_001 | ego: not yet observed | - |
| 0.50 | B:e04 CRITICAL_TTC_START track_001 | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH, CRITICAL_TTC? | 0.40 |
| 3.20 | B:e05 CLOSING_START track_001 | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH | 3.10 |
| 4.70 | B:e06 COLLISION<br>B:e07 CRITICAL_TTC_END track_001<br>B:e08 CLOSING_END track_001 | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH | 4.60 |
| 4.75 | B:e09 THROTTLE_END<br>B:e10 BRAKE_START | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH | 4.70 |
| 4.85 | B:e11 MOVING_END<br>B:e12 STOP_START | ego: MOVING, BRAKE<br>track_001: IN_EGO_PATH | 4.80 |
| 6.25 | B:e13 COLLISION | ego: STOP, BRAKE<br>track_001: IN_EGO_PATH | 6.20 |

## States still active when observation ended

- BRAKE, since B:e10 (t = 4.75 s)
- STOP, since B:e12 (t = 4.85 s)

## Tracks lost

- no track was lost

## Temporal safety relations

Order of each track's cut-in, critical TTC and path entry and of the collision report, in local time. Temporal properties only, not causes.

- track_001: CRITICAL_TTC_START 0.50, COLLISION 4.70 (+4.20 s)

## Sign detection windows

- none

An END means this recorder stopped detecting the sign, not that its obligation ended.

## Anonymous radar tracks

| Track | First seen | Last seen | Measured sweeps | First range / bearing | Min range (at) | Last range / bearing | Max speed |
|-------|-----------:|----------:|----------------:|----------------------|----------------|---------------------|----------:|
| track_001 | 0.00 | 14.15 | 284 | 13.5 m / +0 deg | 0.05 m (4.70) | 0.2 m / +0 deg | 13.8 m/s |

Bearing: positive = to B's right. Ranges are measured from the radar to the visible surface of the object.

## Plain-language reading

- t = 0.00 s: B started moving (already the case when first observed).
- t = 0.00 s: B pressed the accelerator (already the case when first observed).
- t = 0.00 s: B's radar started tracking track_001, which appeared in front of it.
- t = 0.50 s: B's time-to-contact with track_001 became critical.
- t = 3.20 s: B observed track_001 start closing in.
- t = 4.70 s: B's collision sensor recorded a contact (peak impulse 21842 N*s).
- t = 4.70 s: B's time-to-contact with track_001 stopped being critical.
- t = 4.70 s: B observed track_001 stop closing in.
- t = 4.75 s: B released the accelerator.
- t = 4.75 s: B started braking.
- t = 4.85 s: B stopped moving.
- t = 4.85 s: B came to a stop.
- t = 6.25 s: B's collision sensor recorded a contact (peak impulse 31706 N*s).
