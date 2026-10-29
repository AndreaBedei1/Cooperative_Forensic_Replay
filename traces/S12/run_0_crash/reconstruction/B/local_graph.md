# Local graph - vehicle B

All times are B's own local clock: `t_local` = seconds since B's first ego sample (raw clock reading 2022.2515310794115 at `t_local` = 0). Only files under `vehicles/B/` were read; external objects are anonymous radar tracks.

- Local frame: origin = first ego position; x = first heading; y = to the right of the first heading (CARLA convention)
- Trace: 111 frames at 10 Hz in `local_trace.jsonl`, the last one at the recording end (10.95 s)
- Anonymous radar tracks: 3 (10 Hz samples in `local_tracks.jsonl`)
- Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.
- Nodes: 21; edges: 37 (PRECEDES 26, SAME_TRACK 11)

## Nodes

| Id | Local time | Type | Actor | Subject | Source | Details |
|----|-----------:|------|-------|---------|--------|---------|
| B:e01 | 0.00 | MOVING_START | B | - | ego | active_at_first_observation=True |
| B:e02 | 0.00 | THROTTLE_START | B | - | controls | active_at_first_observation=True |
| B:e03 | 0.00 | TRACK_APPEARED_RIGHT | B | track_001 | radar | initial_in_ego_path=False |
| B:e04 | 0.00 | TRACK_APPEARED_RIGHT | B | track_002 | radar | initial_in_ego_path=False |
| B:e05 | 0.00 | CLOSING_START | B | track_002 | radar | active_at_first_observation=True |
| B:e06 | 3.95 | CUT_IN_FROM_RIGHT_START | B | track_001 | radar | geometry=estimated_body |
| B:e07 | 4.05 | CRITICAL_TTC_START | B | track_001 | radar |  |
| B:e08 | 4.15 | CLOSING_START | B | track_001 | radar |  |
| B:e09 | 4.55 | EGO_PATH_ENTRY | B | track_001 | radar | occupancy_evidence=returns; occupancy_margin_m=0.46; occupancy_sigma_m=0.25; cause=TARGET_LATERAL; geometry=estimated_body |
| B:e10 | 4.95 | COLLISION | B | - | collision_sensor | peak_impulse=1576.92; merged_bursts=[[5.05, 263.76], [5.65, 13.44]] |
| B:e11 | 4.95 | CRITICAL_TTC_END | B | track_001 | radar |  |
| B:e12 | 4.95 | CLOSING_END | B | track_001 | radar |  |
| B:e13 | 5.00 | THROTTLE_END | B | - | controls |  |
| B:e14 | 5.00 | BRAKE_START | B | - | controls |  |
| B:e15 | 5.15 | CLOSING_END | B | track_002 | radar |  |
| B:e16 | 5.70 | TRACK_LOST | B | track_002 | radar |  |
| B:e17 | 5.95 | MOVING_END | B | - | ego |  |
| B:e18 | 5.95 | STOP_START | B | - | ego |  |
| B:e19 | 6.10 | CUT_IN_FROM_RIGHT_END | B | track_001 | radar | geometry=estimated_body |
| B:e20 | 6.40 | TRACK_APPEARED_RIGHT | B | track_003 | radar | initial_in_ego_path=False |
| B:e21 | 7.00 | TRACK_LOST | B | track_003 | radar |  |

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
    B:e08 --PRECEDES--> B:e09
    B:e09 --PRECEDES--> B:e10
    B:e09 --PRECEDES--> B:e11
    B:e09 --PRECEDES--> B:e12
    B:e10 --PRECEDES--> B:e13
    B:e10 --PRECEDES--> B:e14
    B:e11 --PRECEDES--> B:e13
    B:e11 --PRECEDES--> B:e14
    B:e12 --PRECEDES--> B:e13
    B:e12 --PRECEDES--> B:e14
    B:e13 --PRECEDES--> B:e15
    B:e14 --PRECEDES--> B:e15
    B:e15 --PRECEDES--> B:e16
    B:e16 --PRECEDES--> B:e17
    B:e16 --PRECEDES--> B:e18
    B:e17 --PRECEDES--> B:e19
    B:e18 --PRECEDES--> B:e19
    B:e19 --PRECEDES--> B:e20
    B:e20 --PRECEDES--> B:e21
    B:e04 --SAME_TRACK--> B:e05
    B:e03 --SAME_TRACK--> B:e06
    B:e03 --SAME_TRACK--> B:e07
    B:e03 --SAME_TRACK--> B:e08
    B:e03 --SAME_TRACK--> B:e09
    B:e03 --SAME_TRACK--> B:e11
    B:e03 --SAME_TRACK--> B:e12
    B:e04 --SAME_TRACK--> B:e15
    B:e04 --SAME_TRACK--> B:e16
    B:e03 --SAME_TRACK--> B:e19
    B:e20 --SAME_TRACK--> B:e21
```

## Perceived state before each event

Each row is the state just BEFORE its events (none of them applied): events at one time are simultaneous and share it. True states are named, unknown ones end with `?`, false ones are omitted; a lost track's states are UNKNOWN, never ended. Facts: the trace frame at the time shown.

| Local time | Events | Perceived state just before | Facts at |
|-----------:|--------|-----------------------------|---------:|
| 0.00 | B:e01 MOVING_START<br>B:e02 THROTTLE_START<br>B:e03 TRACK_APPEARED_RIGHT track_001<br>B:e04 TRACK_APPEARED_RIGHT track_002<br>B:e05 CLOSING_START track_002 | ego: not yet observed | - |
| 3.95 | B:e06 CUT_IN_FROM_RIGHT_START track_001 | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: CLOSING | 3.90 |
| 4.05 | B:e07 CRITICAL_TTC_START track_001 | ego: MOVING, THROTTLE<br>track_001: CUT_IN_FROM_RIGHT<br>track_002: CLOSING | 4.00 |
| 4.15 | B:e08 CLOSING_START track_001 | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, CUT_IN_FROM_RIGHT<br>track_002: CLOSING | 4.10 |
| 4.55 | B:e09 EGO_PATH_ENTRY track_001 | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC, CUT_IN_FROM_RIGHT<br>track_002: CLOSING | 4.50 |
| 4.95 | B:e10 COLLISION<br>B:e11 CRITICAL_TTC_END track_001<br>B:e12 CLOSING_END track_001 | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH, CUT_IN_FROM_RIGHT<br>track_002: CLOSING | 4.90 |
| 5.00 | B:e13 THROTTLE_END<br>B:e14 BRAKE_START | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH, CUT_IN_FROM_RIGHT<br>track_002: CLOSING | 4.90 |
| 5.15 | B:e15 CLOSING_END track_002 | ego: MOVING, BRAKE<br>track_001: IN_EGO_PATH, CUT_IN_FROM_RIGHT<br>track_002: CLOSING | 5.10 |
| 5.70 | B:e16 TRACK_LOST track_002 | ego: MOVING, BRAKE<br>track_001: IN_EGO_PATH, CUT_IN_FROM_RIGHT<br>track_002: no active state | 5.60 |
| 5.95 | B:e17 MOVING_END<br>B:e18 STOP_START | ego: MOVING, BRAKE<br>track_001: IN_EGO_PATH, CUT_IN_FROM_RIGHT<br>track lost, states UNKNOWN: track_002 | 5.90 |
| 6.10 | B:e19 CUT_IN_FROM_RIGHT_END track_001 | ego: STOP, BRAKE<br>track_001: IN_EGO_PATH, CUT_IN_FROM_RIGHT<br>track lost, states UNKNOWN: track_002 | 6.00 |
| 6.40 | B:e20 TRACK_APPEARED_RIGHT track_003 | ego: STOP, BRAKE<br>track_001: IN_EGO_PATH<br>track lost, states UNKNOWN: track_002 | 6.30 |
| 7.00 | B:e21 TRACK_LOST track_003 | ego: STOP, BRAKE<br>track_001: IN_EGO_PATH<br>track_003: no active state<br>track lost, states UNKNOWN: track_002 | 6.90 |

## States still active when observation ended

- EGO_PATH of track_001, since B:e09 (t = 4.55 s)
- BRAKE, since B:e14 (t = 5.00 s)
- STOP, since B:e18 (t = 5.95 s)

## Tracks lost

- lost with no state active: track_002, track_003

## Temporal safety relations

Order of each track's cut-in, critical TTC and path entry and of the collision report, in local time. Temporal properties only, not causes.

- track_001: cut-in started before critical TTC: CUT_IN_FROM_RIGHT_START 3.95 < CRITICAL_TTC_START 4.05 (+0.10 s) < COLLISION 4.95 (+0.90 s); EGO_PATH_ENTRY 4.55 after critical TTC (+0.50 s)

## Sign detection windows

- none

An END means this recorder stopped detecting the sign, not that its obligation ended.

## Anonymous radar tracks

| Track | First seen | Last seen | Measured sweeps | First range / bearing | Min range (at) | Last range / bearing | Max speed |
|-------|-----------:|----------:|----------------:|----------------------|----------------|---------------------|----------:|
| track_001 | 0.00 | 10.95 | 220 | 4.4 m / +26 deg | 0.94 m (6.60) | 1.0 m / +20 deg | 12.4 m/s |
| track_002 | 0.00 | 5.70 | 114 | 16.7 m / +18 deg | 5.81 m (5.15) | 6.9 m / +25 deg | 11.9 m/s |
| track_003 | 6.40 | 7.00 | 11 | 12.8 m / +20 deg | 12.82 m (6.40) | 19.2 m / +19 deg | 10.7 m/s |

Bearing: positive = to B's right. Ranges are measured from the radar to the visible surface of the object.

## Plain-language reading

- t = 0.00 s: B started moving (already the case when first observed).
- t = 0.00 s: B pressed the accelerator (already the case when first observed).
- t = 0.00 s: B's radar started tracking track_001, which appeared on its right.
- t = 0.00 s: B's radar started tracking track_002, which appeared on its right.
- t = 0.00 s: B observed track_002 start closing in (already the case when first observed).
- t = 3.95 s: B observed track_001 cutting in from the right.
- t = 4.05 s: B's time-to-contact with track_001 became critical.
- t = 4.15 s: B observed track_001 start closing in.
- t = 4.55 s: B observed track_001 enter its forward path corridor.
- t = 4.95 s: B's collision sensor recorded a contact (peak impulse 1577 N*s).
- t = 4.95 s: B's time-to-contact with track_001 stopped being critical.
- t = 4.95 s: B observed track_001 stop closing in.
- t = 5.00 s: B released the accelerator.
- t = 5.00 s: B started braking.
- t = 5.15 s: B observed track_002 stop closing in.
- t = 5.70 s: B's radar lost track_002 (its states are UNKNOWN from then on, not ended).
- t = 5.95 s: B stopped moving.
- t = 5.95 s: B came to a stop.
- t = 6.10 s: B observed track_001's cut-in from the right settle.
- t = 6.40 s: B's radar started tracking track_003, which appeared on its right.
- t = 7.00 s: B's radar lost track_003 (its states are UNKNOWN from then on, not ended).
