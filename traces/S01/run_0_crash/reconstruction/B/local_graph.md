# Local graph - vehicle B

All times are B's own local clock: `t_local` = seconds since B's first ego sample (raw clock reading 1819.336835194379 at `t_local` = 0). Only files under `vehicles/B/` were read; external objects are anonymous radar tracks.

- Local frame: origin = first ego position; x = first heading; y = to the right of the first heading (CARLA convention)
- Trace: 121 frames at 10 Hz in `local_trace.jsonl`, the last one at the recording end (11.95 s)
- Anonymous radar tracks: 0 (10 Hz samples in `local_tracks.jsonl`)
- Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.
- Nodes: 7; edges: 10 (PRECEDES 10)

## Nodes

| Id | Local time | Type | Actor | Subject | Source | Details |
|----|-----------:|------|-------|---------|--------|---------|
| B:e01 | 0.00 | MOVING_START | B | - | ego | active_at_first_observation=True |
| B:e02 | 0.00 | THROTTLE_START | B | - | controls | active_at_first_observation=True |
| B:e03 | 3.95 | THROTTLE_END | B | - | controls |  |
| B:e04 | 3.95 | BRAKE_START | B | - | controls |  |
| B:e05 | 5.15 | MOVING_END | B | - | ego |  |
| B:e06 | 5.15 | STOP_START | B | - | ego |  |
| B:e07 | 6.75 | COLLISION | B | - | collision_sensor | peak_impulse=14394.11 |

Events are state transitions; the quantities behind them (speed, pedals, ranges, TTC, relative motion, closest approach) are facts in `local_trace.jsonl`. Events with equal times are simultaneous at the recorder's resolution: PRECEDES links only different times. SAME_TRACK links a track's TRACK_APPEARED_* to every other event about the same local track (grouping only, no order).

## Edges

```
    B:e01 --PRECEDES--> B:e03
    B:e01 --PRECEDES--> B:e04
    B:e02 --PRECEDES--> B:e03
    B:e02 --PRECEDES--> B:e04
    B:e03 --PRECEDES--> B:e05
    B:e03 --PRECEDES--> B:e06
    B:e04 --PRECEDES--> B:e05
    B:e04 --PRECEDES--> B:e06
    B:e05 --PRECEDES--> B:e07
    B:e06 --PRECEDES--> B:e07
```

## Perceived state before each event

Each row is the state just BEFORE its events (none of them applied): events at one time are simultaneous and share it. True states are named, unknown ones end with `?`, false ones are omitted; a lost track's states are UNKNOWN, never ended. Facts: the trace frame at the time shown.

| Local time | Events | Perceived state just before | Facts at |
|-----------:|--------|-----------------------------|---------:|
| 0.00 | B:e01 MOVING_START<br>B:e02 THROTTLE_START | ego: not yet observed | - |
| 3.95 | B:e03 THROTTLE_END<br>B:e04 BRAKE_START | ego: MOVING, THROTTLE | 3.90 |
| 5.15 | B:e05 MOVING_END<br>B:e06 STOP_START | ego: MOVING, BRAKE | 5.10 |
| 6.75 | B:e07 COLLISION | ego: STOP, BRAKE | 6.70 |

## States still active when observation ended

- BRAKE, since B:e04 (t = 3.95 s)
- STOP, since B:e06 (t = 5.15 s)

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
- t = 3.95 s: B released the accelerator.
- t = 3.95 s: B started braking.
- t = 5.15 s: B stopped moving.
- t = 5.15 s: B came to a stop.
- t = 6.75 s: B's collision sensor recorded a contact (peak impulse 14394 N*s).
