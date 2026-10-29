# Local graph - vehicle B

All times are B's own local clock: `t_local` = seconds since B's first ego sample (raw clock reading 1874.510636933148 at `t_local` = 0). Only files under `vehicles/B/` were read; external objects are anonymous radar tracks.

- Local frame: origin = first ego position; x = first heading; y = to the right of the first heading (CARLA convention)
- Trace: 138 frames at 10 Hz in `local_trace.jsonl`
- Anonymous radar tracks: 1 (10 Hz samples in `local_tracks.jsonl`)
- Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.
- Nodes: 15; edges: 25 (PRECEDES 21, SAME_TRACK 4)

## Nodes

| Id | Local time | Type | Actor | Subject | Source | Details |
|----|-----------:|------|-------|---------|--------|---------|
| B:e01 | 0.00 | MOVING_START | B | - | ego | active_at_first_observation=True |
| B:e02 | 0.00 | THROTTLE_START | B | - | controls | active_at_first_observation=True |
| B:e03 | 0.00 | TRACK_APPEARED_FRONT | B | track_001 | radar | initial_in_ego_path=True |
| B:e04 | 0.50 | CRITICAL_TTC_START | B | track_001 | radar |  |
| B:e05 | 3.20 | CLOSING_START | B | track_001 | radar |  |
| B:e06 | 3.70 | THROTTLE_END | B | - | controls |  |
| B:e07 | 3.70 | BRAKE_START | B | - | controls |  |
| B:e08 | 4.80 | COLLISION | B | - | collision_sensor | peak_impulse=10281.41 |
| B:e09 | 4.85 | BRAKE_END | B | - | controls |  |
| B:e10 | 5.30 | COLLISION | B | - | collision_sensor | peak_impulse=8788.05; new_contact=break_s 0.50, evidence peak, peak_ratio 0.85; merged_bursts=[[5.45, 1509.76]] |
| B:e11 | 5.30 | CRITICAL_TTC_END | B | track_001 | radar |  |
| B:e12 | 5.30 | CLOSING_END | B | track_001 | radar |  |
| B:e13 | 5.45 | MOVING_END | B | - | ego |  |
| B:e14 | 5.45 | STOP_START | B | - | ego |  |
| B:e15 | 5.45 | BRAKE_START | B | - | controls |  |

Events are state transitions; the quantities behind them (speed, pedals, ranges, TTC, relative motion, closest approach) are facts in `local_trace.jsonl`. Events with equal times are simultaneous at the recorder's resolution: PRECEDES links only different times. SAME_TRACK links a track's TRACK_APPEARED_* to every other event about the same local track (grouping only, no order).

## Edges

```
    B:e01 --PRECEDES--> B:e04
    B:e02 --PRECEDES--> B:e04
    B:e03 --PRECEDES--> B:e04
    B:e04 --PRECEDES--> B:e05
    B:e05 --PRECEDES--> B:e06
    B:e05 --PRECEDES--> B:e07
    B:e06 --PRECEDES--> B:e08
    B:e07 --PRECEDES--> B:e08
    B:e08 --PRECEDES--> B:e09
    B:e09 --PRECEDES--> B:e10
    B:e09 --PRECEDES--> B:e11
    B:e09 --PRECEDES--> B:e12
    B:e10 --PRECEDES--> B:e13
    B:e10 --PRECEDES--> B:e14
    B:e10 --PRECEDES--> B:e15
    B:e11 --PRECEDES--> B:e13
    B:e11 --PRECEDES--> B:e14
    B:e11 --PRECEDES--> B:e15
    B:e12 --PRECEDES--> B:e13
    B:e12 --PRECEDES--> B:e14
    B:e12 --PRECEDES--> B:e15
    B:e03 --SAME_TRACK--> B:e04
    B:e03 --SAME_TRACK--> B:e05
    B:e03 --SAME_TRACK--> B:e11
    B:e03 --SAME_TRACK--> B:e12
```

## Perceived state before each event

Each row is the state just BEFORE its events (none of them applied): events at one time are simultaneous and share it. True states are named, unknown ones end with `?`, false ones are omitted; a lost track's states are UNKNOWN, never ended. Facts: the trace frame at the time shown.

| Local time | Events | Perceived state just before | Facts at |
|-----------:|--------|-----------------------------|---------:|
| 0.00 | B:e01 MOVING_START<br>B:e02 THROTTLE_START<br>B:e03 TRACK_APPEARED_FRONT track_001 | ego: not yet observed | - |
| 0.50 | B:e04 CRITICAL_TTC_START track_001 | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH, CRITICAL_TTC? | 0.40 |
| 3.20 | B:e05 CLOSING_START track_001 | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH | 3.10 |
| 3.70 | B:e06 THROTTLE_END<br>B:e07 BRAKE_START | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH | 3.60 |
| 4.80 | B:e08 COLLISION | ego: MOVING, BRAKE<br>track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH | 4.70 |
| 4.85 | B:e09 BRAKE_END | ego: MOVING, BRAKE<br>track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH | 4.80 |
| 5.30 | B:e10 COLLISION<br>B:e11 CRITICAL_TTC_END track_001<br>B:e12 CLOSING_END track_001 | ego: MOVING<br>track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH | 5.20 |
| 5.45 | B:e13 MOVING_END<br>B:e14 STOP_START<br>B:e15 BRAKE_START | ego: MOVING<br>track_001: IN_EGO_PATH | 5.40 |

## States still active when observation ended

- STOP, since B:e14 (t = 5.45 s)
- BRAKE, since B:e15 (t = 5.45 s)

## Tracks lost

- no track was lost

## Temporal safety relations

Order of each track's cut-in, critical TTC and path entry and of the collision report, in local time. Temporal properties only, not causes.

- track_001: CRITICAL_TTC_START 0.50, COLLISION 4.80 (+4.30 s)

## Sign detection windows

- none

An END means this recorder stopped detecting the sign, not that its obligation ended.

## Anonymous radar tracks

| Track | First seen | Last seen | Measured sweeps | First range / bearing | Min range (at) | Last range / bearing | Max speed |
|-------|-----------:|----------:|----------------:|----------------------|----------------|---------------------|----------:|
| track_001 | 0.00 | 13.70 | 275 | 13.5 m / +0 deg | 0.02 m (5.30) | 0.1 m / -0 deg | 13.8 m/s |

Bearing: positive = to B's right. Ranges are measured from the radar to the visible surface of the object.

## Plain-language reading

- t = 0.00 s: B started moving (already the case when first observed).
- t = 0.00 s: B pressed the accelerator (already the case when first observed).
- t = 0.00 s: B's radar started tracking track_001, which appeared in front of it.
- t = 0.50 s: B's time-to-contact with track_001 became critical.
- t = 3.20 s: B observed track_001 start closing in.
- t = 3.70 s: B released the accelerator.
- t = 3.70 s: B started braking.
- t = 4.80 s: B's collision sensor recorded a contact (peak impulse 10281 N*s).
- t = 4.85 s: B released the brake.
- t = 5.30 s: B's collision sensor recorded a contact (peak impulse 8788 N*s).
- t = 5.30 s: B's time-to-contact with track_001 stopped being critical.
- t = 5.30 s: B observed track_001 stop closing in.
- t = 5.45 s: B stopped moving.
- t = 5.45 s: B came to a stop.
- t = 5.45 s: B started braking.
