# Local graph - vehicle B

All times are B's own local clock: `t_local` = seconds since B's first ego sample (raw clock reading 1835.5202581100166 at `t_local` = 0). Only files under `vehicles/B/` were read; external objects are anonymous radar tracks.

- Local frame: origin = first ego position; x = first heading; y = to the right of the first heading (CARLA convention)
- Trace: 153 frames at 10 Hz in `local_trace.jsonl`, the last one at the recording end (15.15 s)
- Anonymous radar tracks: 0 (10 Hz samples in `local_tracks.jsonl`)
- Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.
- Nodes: 11; edges: 16 (PRECEDES 16)

## Nodes

| Id | Local time | Type | Actor | Subject | Source | Details |
|----|-----------:|------|-------|---------|--------|---------|
| B:e01 | 0.00 | MOVING_START | B | - | ego | active_at_first_observation=True |
| B:e02 | 0.00 | THROTTLE_START | B | - | controls | active_at_first_observation=True |
| B:e03 | 3.15 | THROTTLE_END | B | - | controls |  |
| B:e04 | 3.15 | BRAKE_START | B | - | controls |  |
| B:e05 | 3.65 | BRAKE_END | B | - | controls |  |
| B:e06 | 3.75 | THROTTLE_START | B | - | controls |  |
| B:e07 | 5.25 | COLLISION | B | - | collision_sensor | peak_impulse=2604.14 |
| B:e08 | 5.25 | THROTTLE_END | B | - | controls |  |
| B:e09 | 5.25 | BRAKE_START | B | - | controls |  |
| B:e10 | 5.80 | MOVING_END | B | - | ego |  |
| B:e11 | 5.80 | STOP_START | B | - | ego |  |

Events are state transitions; the quantities behind them (speed, pedals, ranges, TTC, relative motion, closest approach) are facts in `local_trace.jsonl`. Events with equal times are simultaneous at the recorder's resolution: PRECEDES links only different times. SAME_TRACK links a track's TRACK_APPEARED_* to every other event about the same local track (grouping only, no order).

## Edges

```
    B:e01 --PRECEDES--> B:e03
    B:e01 --PRECEDES--> B:e04
    B:e02 --PRECEDES--> B:e03
    B:e02 --PRECEDES--> B:e04
    B:e03 --PRECEDES--> B:e05
    B:e04 --PRECEDES--> B:e05
    B:e05 --PRECEDES--> B:e06
    B:e06 --PRECEDES--> B:e07
    B:e06 --PRECEDES--> B:e08
    B:e06 --PRECEDES--> B:e09
    B:e07 --PRECEDES--> B:e10
    B:e07 --PRECEDES--> B:e11
    B:e08 --PRECEDES--> B:e10
    B:e08 --PRECEDES--> B:e11
    B:e09 --PRECEDES--> B:e10
    B:e09 --PRECEDES--> B:e11
```

## Perceived state before each event

Each row is the state just BEFORE its events (none of them applied): events at one time are simultaneous and share it. True states are named, unknown ones end with `?`, false ones are omitted; a lost track's states are UNKNOWN, never ended. Facts: the trace frame at the time shown.

| Local time | Events | Perceived state just before | Facts at |
|-----------:|--------|-----------------------------|---------:|
| 0.00 | B:e01 MOVING_START<br>B:e02 THROTTLE_START | ego: not yet observed | - |
| 3.15 | B:e03 THROTTLE_END<br>B:e04 BRAKE_START | ego: MOVING, THROTTLE | 3.10 |
| 3.65 | B:e05 BRAKE_END | ego: MOVING, BRAKE | 3.60 |
| 3.75 | B:e06 THROTTLE_START | ego: MOVING | 3.70 |
| 5.25 | B:e07 COLLISION<br>B:e08 THROTTLE_END<br>B:e09 BRAKE_START | ego: MOVING, THROTTLE | 5.20 |
| 5.80 | B:e10 MOVING_END<br>B:e11 STOP_START | ego: MOVING, BRAKE | 5.70 |

## States still active when observation ended

- BRAKE, since B:e09 (t = 5.25 s)
- STOP, since B:e11 (t = 5.80 s)

## Tracks lost

- no track was lost

## Temporal safety relations

Order of each track's cut-in, critical TTC and path entry and of the collision report, in local time. Temporal properties only, not causes.

- none

## Sign detection windows

- none

An END means this recorder stopped detecting the sign, not that its obligation ended.

## Anonymous radar tracks

No radar track: nothing moving stayed in B's radar view long enough.

## Plain-language reading

- t = 0.00 s: B started moving (already the case when first observed).
- t = 0.00 s: B pressed the accelerator (already the case when first observed).
- t = 3.15 s: B released the accelerator.
- t = 3.15 s: B started braking.
- t = 3.65 s: B released the brake.
- t = 3.75 s: B pressed the accelerator.
- t = 5.25 s: B's collision sensor recorded a contact (peak impulse 2604 N*s).
- t = 5.25 s: B released the accelerator.
- t = 5.25 s: B started braking.
- t = 5.80 s: B stopped moving.
- t = 5.80 s: B came to a stop.
