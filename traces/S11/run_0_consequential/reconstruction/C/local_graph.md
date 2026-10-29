# Local graph - vehicle C

All times are C's own local clock: `t_local` = seconds since C's first ego sample (raw clock reading 2005.8708217665553 at `t_local` = 0). Only files under `vehicles/C/` were read; external objects are anonymous radar tracks.

- Local frame: origin = first ego position; x = first heading; y = to the right of the first heading (CARLA convention)
- Trace: 121 frames at 10 Hz in `local_trace.jsonl`, the last one at the recording end (11.95 s)
- Anonymous radar tracks: 1 (10 Hz samples in `local_tracks.jsonl`)
- Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.
- Nodes: 13; edges: 22 (PRECEDES 17, SAME_TRACK 5)

## Nodes

| Id | Local time | Type | Actor | Subject | Source | Details |
|----|-----------:|------|-------|---------|--------|---------|
| C:e01 | 0.00 | MOVING_START | C | - | ego | active_at_first_observation=True |
| C:e02 | 0.00 | THROTTLE_START | C | - | controls | active_at_first_observation=True |
| C:e03 | 2.65 | TRACK_APPEARED_RIGHT | C | track_001 | radar | initial_in_ego_path=False |
| C:e04 | 2.65 | CLOSING_START | C | track_001 | radar | active_at_first_observation=True |
| C:e05 | 4.35 | CLOSING_END | C | track_001 | radar |  |
| C:e06 | 5.55 | CLOSING_START | C | track_001 | radar |  |
| C:e07 | 5.55 | CRITICAL_TTC_START | C | track_001 | radar |  |
| C:e08 | 6.45 | TRACK_LOST | C | track_001 | radar |  |
| C:e09 | 6.60 | COLLISION | C | - | collision_sensor | peak_impulse=839.68; merged_bursts=[[6.85, 241.71], [7.6, 236.89]] |
| C:e10 | 6.65 | THROTTLE_END | C | - | controls |  |
| C:e11 | 6.65 | BRAKE_START | C | - | controls |  |
| C:e12 | 7.45 | MOVING_END | C | - | ego |  |
| C:e13 | 7.45 | STOP_START | C | - | ego |  |

Events are state transitions; the quantities behind them (speed, pedals, ranges, TTC, relative motion, closest approach) are facts in `local_trace.jsonl`. Events with equal times are simultaneous at the recorder's resolution: PRECEDES links only different times. SAME_TRACK links a track's TRACK_APPEARED_* to every other event about the same local track (grouping only, no order).

## Edges

```
    C:e01 --PRECEDES--> C:e03
    C:e01 --PRECEDES--> C:e04
    C:e02 --PRECEDES--> C:e03
    C:e02 --PRECEDES--> C:e04
    C:e03 --PRECEDES--> C:e05
    C:e04 --PRECEDES--> C:e05
    C:e05 --PRECEDES--> C:e06
    C:e05 --PRECEDES--> C:e07
    C:e06 --PRECEDES--> C:e08
    C:e07 --PRECEDES--> C:e08
    C:e08 --PRECEDES--> C:e09
    C:e09 --PRECEDES--> C:e10
    C:e09 --PRECEDES--> C:e11
    C:e10 --PRECEDES--> C:e12
    C:e10 --PRECEDES--> C:e13
    C:e11 --PRECEDES--> C:e12
    C:e11 --PRECEDES--> C:e13
    C:e03 --SAME_TRACK--> C:e04
    C:e03 --SAME_TRACK--> C:e05
    C:e03 --SAME_TRACK--> C:e06
    C:e03 --SAME_TRACK--> C:e07
    C:e03 --SAME_TRACK--> C:e08
```

## Perceived state before each event

Each row is the state just BEFORE its events (none of them applied): events at one time are simultaneous and share it. True states are named, unknown ones end with `?`, false ones are omitted; a lost track's states are UNKNOWN, never ended. Facts: the trace frame at the time shown.

| Local time | Events | Perceived state just before | Facts at |
|-----------:|--------|-----------------------------|---------:|
| 0.00 | C:e01 MOVING_START<br>C:e02 THROTTLE_START | ego: not yet observed | - |
| 2.65 | C:e03 TRACK_APPEARED_RIGHT track_001<br>C:e04 CLOSING_START track_001 | ego: MOVING, THROTTLE | 2.60 |
| 4.35 | C:e05 CLOSING_END track_001 | ego: MOVING, THROTTLE<br>track_001: CLOSING | 4.30 |
| 5.55 | C:e06 CLOSING_START track_001<br>C:e07 CRITICAL_TTC_START track_001 | ego: MOVING, THROTTLE<br>track_001: no active state | 5.50 |
| 6.45 | C:e08 TRACK_LOST track_001 | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC | 6.40 |
| 6.60 | C:e09 COLLISION | ego: MOVING, THROTTLE<br>track lost, states UNKNOWN: track_001 | 6.50 |
| 6.65 | C:e10 THROTTLE_END<br>C:e11 BRAKE_START | ego: MOVING, THROTTLE<br>track lost, states UNKNOWN: track_001 | 6.60 |
| 7.45 | C:e12 MOVING_END<br>C:e13 STOP_START | ego: MOVING, BRAKE<br>track lost, states UNKNOWN: track_001 | 7.40 |

## States still active when observation ended

- CLOSING of track_001, since C:e06 (t = 5.55 s); the track was lost at 6.45 s
- CRITICAL_TTC of track_001, since C:e07 (t = 5.55 s); the track was lost at 6.45 s
- BRAKE, since C:e11 (t = 6.65 s)
- STOP, since C:e13 (t = 7.45 s)

## Tracks lost

- track_001 at 6.45 s (C:e08): CLOSING, CRITICAL_TTC were true; they are UNKNOWN afterwards (no END recorded)

## Temporal safety relations

Order of each track's cut-in, critical TTC and path entry and of the collision report, in local time. Temporal properties only, not causes.

- track_001: CRITICAL_TTC_START 5.55, COLLISION 6.60 (+1.05 s)

## Sign detection windows

- none

An END means this recorder stopped detecting the sign, not that its obligation ended.

## Anonymous radar tracks

| Track | First seen | Last seen | Measured sweeps | First range / bearing | Min range (at) | Last range / bearing | Max speed |
|-------|-----------:|----------:|----------------:|----------------------|----------------|---------------------|----------:|
| track_001 | 2.65 | 6.45 | 77 | 8.9 m / +154 deg | 3.07 m (6.45) | 3.1 m / +144 deg | 11.8 m/s |

Bearing: positive = to C's right. Ranges are measured from the radar to the visible surface of the object.

## Plain-language reading

- t = 0.00 s: C started moving (already the case when first observed).
- t = 0.00 s: C pressed the accelerator (already the case when first observed).
- t = 2.65 s: C's radar started tracking track_001, which appeared on its right.
- t = 2.65 s: C observed track_001 start closing in (already the case when first observed).
- t = 4.35 s: C observed track_001 stop closing in.
- t = 5.55 s: C observed track_001 start closing in.
- t = 5.55 s: C's time-to-contact with track_001 became critical.
- t = 6.45 s: C's radar lost track_001 (its states are UNKNOWN from then on, not ended).
- t = 6.60 s: C's collision sensor recorded a contact (peak impulse 840 N*s).
- t = 6.65 s: C released the accelerator.
- t = 6.65 s: C started braking.
- t = 7.45 s: C stopped moving.
- t = 7.45 s: C came to a stop.
