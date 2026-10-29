# Local graph - vehicle B

All times are B's own local clock: `t_local` = seconds since B's first ego sample (raw clock reading 2100.0170479118824 at `t_local` = 0). Only files under `vehicles/B/` were read; external objects are anonymous radar tracks.

- Local frame: origin = first ego position; x = first heading; y = to the right of the first heading (CARLA convention)
- Trace: 121 frames at 10 Hz in `local_trace.jsonl`, the last one at the recording end (11.95 s)
- Anonymous radar tracks: 9 (10 Hz samples in `local_tracks.jsonl`)
- Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.
- Nodes: 25; edges: 45 (PRECEDES 33, SAME_TRACK 12)

## Nodes

| Id | Local time | Type | Actor | Subject | Source | Details |
|----|-----------:|------|-------|---------|--------|---------|
| B:e01 | 0.00 | MOVING_START | B | - | ego | active_at_first_observation=True |
| B:e02 | 0.00 | THROTTLE_START | B | - | controls | active_at_first_observation=True |
| B:e03 | 0.00 | TRACK_APPEARED_LEFT | B | track_001 | radar | initial_in_ego_path=False |
| B:e04 | 0.00 | TRACK_APPEARED_LEFT | B | track_002 | radar | initial_in_ego_path=False |
| B:e05 | 0.00 | TRACK_APPEARED_LEFT | B | track_005 | radar | initial_in_ego_path=False |
| B:e06 | 0.00 | TRACK_APPEARED_RIGHT | B | track_003 | radar | initial_in_ego_path=False |
| B:e07 | 0.00 | TRACK_APPEARED_RIGHT | B | track_004 | radar | initial_in_ego_path=False |
| B:e08 | 0.00 | TRACK_APPEARED_RIGHT | B | track_006 | radar | initial_in_ego_path=False |
| B:e09 | 0.05 | TRACK_APPEARED_FRONT | B | track_007 | radar | initial_in_ego_path=True |
| B:e10 | 0.55 | CRITICAL_TTC_START | B | track_007 | radar |  |
| B:e11 | 3.55 | TRACK_LOST | B | track_006 | radar |  |
| B:e12 | 3.70 | TRACK_LOST | B | track_002 | radar |  |
| B:e13 | 6.15 | TRACK_APPEARED_LEFT | B | track_008 | radar | initial_in_ego_path=False |
| B:e14 | 6.20 | CLOSING_START | B | track_007 | radar |  |
| B:e15 | 6.35 | TRACK_APPEARED_RIGHT | B | track_009 | radar | initial_in_ego_path=False |
| B:e16 | 6.60 | TRACK_LOST | B | track_009 | radar |  |
| B:e17 | 6.75 | TRACK_LOST | B | track_008 | radar |  |
| B:e18 | 7.40 | TRACK_LOST | B | track_004 | radar |  |
| B:e19 | 7.40 | TRACK_LOST | B | track_005 | radar |  |
| B:e20 | 7.45 | COLLISION | B | - | collision_sensor | peak_impulse=34836.87 |
| B:e21 | 7.45 | CRITICAL_TTC_END | B | track_007 | radar |  |
| B:e22 | 7.45 | CLOSING_END | B | track_007 | radar |  |
| B:e23 | 7.45 | TRACK_LOST | B | track_001 | radar |  |
| B:e24 | 7.45 | TRACK_LOST | B | track_003 | radar |  |
| B:e25 | 7.50 | THROTTLE_END | B | - | controls |  |

Events are state transitions; the quantities behind them (speed, pedals, ranges, TTC, relative motion, closest approach) are facts in `local_trace.jsonl`. Events with equal times are simultaneous at the recorder's resolution: PRECEDES links only different times. SAME_TRACK links a track's TRACK_APPEARED_* to every other event about the same local track (grouping only, no order).

## Edges

```
    B:e01 --PRECEDES--> B:e09
    B:e02 --PRECEDES--> B:e09
    B:e03 --PRECEDES--> B:e09
    B:e04 --PRECEDES--> B:e09
    B:e05 --PRECEDES--> B:e09
    B:e06 --PRECEDES--> B:e09
    B:e07 --PRECEDES--> B:e09
    B:e08 --PRECEDES--> B:e09
    B:e09 --PRECEDES--> B:e10
    B:e10 --PRECEDES--> B:e11
    B:e11 --PRECEDES--> B:e12
    B:e12 --PRECEDES--> B:e13
    B:e13 --PRECEDES--> B:e14
    B:e14 --PRECEDES--> B:e15
    B:e15 --PRECEDES--> B:e16
    B:e16 --PRECEDES--> B:e17
    B:e17 --PRECEDES--> B:e18
    B:e17 --PRECEDES--> B:e19
    B:e18 --PRECEDES--> B:e20
    B:e18 --PRECEDES--> B:e21
    B:e18 --PRECEDES--> B:e22
    B:e18 --PRECEDES--> B:e23
    B:e18 --PRECEDES--> B:e24
    B:e19 --PRECEDES--> B:e20
    B:e19 --PRECEDES--> B:e21
    B:e19 --PRECEDES--> B:e22
    B:e19 --PRECEDES--> B:e23
    B:e19 --PRECEDES--> B:e24
    B:e20 --PRECEDES--> B:e25
    B:e21 --PRECEDES--> B:e25
    B:e22 --PRECEDES--> B:e25
    B:e23 --PRECEDES--> B:e25
    B:e24 --PRECEDES--> B:e25
    B:e09 --SAME_TRACK--> B:e10
    B:e08 --SAME_TRACK--> B:e11
    B:e04 --SAME_TRACK--> B:e12
    B:e09 --SAME_TRACK--> B:e14
    B:e15 --SAME_TRACK--> B:e16
    B:e13 --SAME_TRACK--> B:e17
    B:e07 --SAME_TRACK--> B:e18
    B:e05 --SAME_TRACK--> B:e19
    B:e09 --SAME_TRACK--> B:e21
    B:e09 --SAME_TRACK--> B:e22
    B:e03 --SAME_TRACK--> B:e23
    B:e06 --SAME_TRACK--> B:e24
```

## Perceived state before each event

Each row is the state just BEFORE its events (none of them applied): events at one time are simultaneous and share it. True states are named, unknown ones end with `?`, false ones are omitted; a lost track's states are UNKNOWN, never ended. Facts: the trace frame at the time shown.

| Local time | Events | Perceived state just before | Facts at |
|-----------:|--------|-----------------------------|---------:|
| 0.00 | B:e01 MOVING_START<br>B:e02 THROTTLE_START<br>B:e03 TRACK_APPEARED_LEFT track_001<br>B:e04 TRACK_APPEARED_LEFT track_002<br>B:e05 TRACK_APPEARED_LEFT track_005<br>B:e06 TRACK_APPEARED_RIGHT track_003<br>B:e07 TRACK_APPEARED_RIGHT track_004<br>B:e08 TRACK_APPEARED_RIGHT track_006 | ego: not yet observed | - |
| 0.05 | B:e09 TRACK_APPEARED_FRONT track_007 | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC?<br>track_002: CRITICAL_TTC?<br>track_003: CRITICAL_TTC?<br>track_004: CRITICAL_TTC?<br>track_005: CRITICAL_TTC?<br>track_006: CRITICAL_TTC? | 0.00 |
| 0.55 | B:e10 CRITICAL_TTC_START track_007 | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: no active state<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_006: no active state<br>track_007: IN_EGO_PATH, CRITICAL_TTC? | 0.50 |
| 3.55 | B:e11 TRACK_LOST track_006 | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: no active state<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_006: no active state<br>track_007: CRITICAL_TTC, IN_EGO_PATH | 3.50 |
| 3.70 | B:e12 TRACK_LOST track_002 | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: no active state<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_007: CRITICAL_TTC, IN_EGO_PATH<br>track lost, states UNKNOWN: track_006 | 3.60 |
| 6.15 | B:e13 TRACK_APPEARED_LEFT track_008 | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_007: CRITICAL_TTC, IN_EGO_PATH<br>track lost, states UNKNOWN: track_002, track_006 | 6.10 |
| 6.20 | B:e14 CLOSING_START track_007 | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_007: CRITICAL_TTC, IN_EGO_PATH<br>track_008: CRITICAL_TTC?<br>track lost, states UNKNOWN: track_002, track_006 | 6.10 |
| 6.35 | B:e15 TRACK_APPEARED_RIGHT track_009 | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_007: CLOSING, CRITICAL_TTC, IN_EGO_PATH<br>track_008: CRITICAL_TTC?<br>track lost, states UNKNOWN: track_002, track_006 | 6.30 |
| 6.60 | B:e16 TRACK_LOST track_009 | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_007: CLOSING, CRITICAL_TTC, IN_EGO_PATH<br>track_008: CRITICAL_TTC?<br>track_009: CRITICAL_TTC?, CUT_IN_FROM_LEFT?, CUT_IN_FROM_RIGHT?<br>track lost, states UNKNOWN: track_002, track_006 | 6.50 |
| 6.75 | B:e17 TRACK_LOST track_008 | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_007: CLOSING, CRITICAL_TTC, IN_EGO_PATH<br>track_008: no active state<br>track lost, states UNKNOWN: track_002, track_006, track_009 | 6.70 |
| 7.40 | B:e18 TRACK_LOST track_004<br>B:e19 TRACK_LOST track_005 | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_007: CLOSING, CRITICAL_TTC, IN_EGO_PATH<br>track lost, states UNKNOWN: track_002, track_006, track_008, track_009 | 7.30 |
| 7.45 | B:e20 COLLISION<br>B:e21 CRITICAL_TTC_END track_007<br>B:e22 CLOSING_END track_007<br>B:e23 TRACK_LOST track_001<br>B:e24 TRACK_LOST track_003 | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_003: no active state<br>track_007: CLOSING, CRITICAL_TTC, IN_EGO_PATH<br>track lost, states UNKNOWN: track_002, track_004, track_005, track_006, track_008, track_009 | 7.40 |
| 7.50 | B:e25 THROTTLE_END | ego: MOVING, THROTTLE<br>track_007: IN_EGO_PATH<br>track lost, states UNKNOWN: track_001, track_002, track_003, track_004, track_005, track_006, track_008, track_009 | 7.40 |

## States still active when observation ended

- MOVING, since B:e01 (t = 0.00 s)

## Tracks lost

- lost with no state active: track_006, track_002, track_009, track_008, track_004, track_005, track_001, track_003

## Temporal safety relations

Order of each track's cut-in, critical TTC and path entry and of the collision report, in local time. Temporal properties only, not causes.

- track_007: CRITICAL_TTC_START 0.55, COLLISION 7.45 (+6.90 s)

## Sign detection windows

- none

An END means this recorder stopped detecting the sign, not that its obligation ended.

## Anonymous radar tracks

| Track | First seen | Last seen | Measured sweeps | First range / bearing | Min range (at) | Last range / bearing | Max speed |
|-------|-----------:|----------:|----------------:|----------------------|----------------|---------------------|----------:|
| track_001 | 0.00 | 7.45 | 150 | 3.4 m / -35 deg | 3.31 m (0.80) | 5.2 m / -31 deg | 12.1 m/s |
| track_002 | 0.00 | 3.70 | 69 | 25.8 m / -7 deg | 25.69 m (0.75) | 26.0 m / -7 deg | 12.0 m/s |
| track_003 | 0.00 | 7.45 | 150 | 4.7 m / +28 deg | 4.14 m (5.75) | 6.0 m / +30 deg | 12.1 m/s |
| track_004 | 0.00 | 7.40 | 136 | 16.3 m / +10 deg | 16.22 m (0.75) | 17.0 m / +10 deg | 12.2 m/s |
| track_005 | 0.00 | 7.40 | 145 | 14.0 m / -11 deg | 13.41 m (4.15) | 13.6 m / -11 deg | 12.3 m/s |
| track_006 | 0.00 | 3.55 | 59 | 27.8 m / +7 deg | 27.70 m (0.80) | 27.9 m / +6 deg | 11.9 m/s |
| track_007 | 0.05 | 11.95 | 239 | 7.7 m / -0 deg | 0.18 m (7.45) | 9.3 m / +1 deg | 12.1 m/s |
| track_008 | 6.15 | 6.75 | 11 | 26.4 m / -7 deg | 26.42 m (6.75) | 26.4 m / -8 deg | 11.9 m/s |
| track_009 | 6.35 | 6.60 | 5 | 28.4 m / +7 deg | 28.38 m (6.60) | 28.4 m / +7 deg | 12.0 m/s |

Bearing: positive = to B's right. Ranges are measured from the radar to the visible surface of the object.

## Plain-language reading

- t = 0.00 s: B started moving (already the case when first observed).
- t = 0.00 s: B pressed the accelerator (already the case when first observed).
- t = 0.00 s: B's radar started tracking track_001, which appeared on its left.
- t = 0.00 s: B's radar started tracking track_002, which appeared on its left.
- t = 0.00 s: B's radar started tracking track_005, which appeared on its left.
- t = 0.00 s: B's radar started tracking track_003, which appeared on its right.
- t = 0.00 s: B's radar started tracking track_004, which appeared on its right.
- t = 0.00 s: B's radar started tracking track_006, which appeared on its right.
- t = 0.05 s: B's radar started tracking track_007, which appeared in front of it.
- t = 0.55 s: B's time-to-contact with track_007 became critical.
- t = 3.55 s: B's radar lost track_006 (its states are UNKNOWN from then on, not ended).
- t = 3.70 s: B's radar lost track_002 (its states are UNKNOWN from then on, not ended).
- t = 6.15 s: B's radar started tracking track_008, which appeared on its left.
- t = 6.20 s: B observed track_007 start closing in.
- t = 6.35 s: B's radar started tracking track_009, which appeared on its right.
- t = 6.60 s: B's radar lost track_009 (its states are UNKNOWN from then on, not ended).
- t = 6.75 s: B's radar lost track_008 (its states are UNKNOWN from then on, not ended).
- t = 7.40 s: B's radar lost track_004 (its states are UNKNOWN from then on, not ended).
- t = 7.40 s: B's radar lost track_005 (its states are UNKNOWN from then on, not ended).
- t = 7.45 s: B's collision sensor recorded a contact (peak impulse 34837 N*s).
- t = 7.45 s: B's time-to-contact with track_007 stopped being critical.
- t = 7.45 s: B observed track_007 stop closing in.
- t = 7.45 s: B's radar lost track_001 (its states are UNKNOWN from then on, not ended).
- t = 7.45 s: B's radar lost track_003 (its states are UNKNOWN from then on, not ended).
- t = 7.50 s: B released the accelerator.
