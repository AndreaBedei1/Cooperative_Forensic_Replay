# Local graph - vehicle A

All times are A's own local clock: `t_local` = seconds since A's first ego sample (raw clock reading 2100.0170479118824 at `t_local` = 0). Only files under `vehicles/A/` were read; external objects are anonymous radar tracks.

- Local frame: origin = first ego position; x = first heading; y = to the right of the first heading (CARLA convention)
- Trace: 121 frames at 10 Hz in `local_trace.jsonl`, the last one at the recording end (11.95 s)
- Anonymous radar tracks: 10 (10 Hz samples in `local_tracks.jsonl`)
- Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.
- Nodes: 31; edges: 44 (PRECEDES 32, SAME_TRACK 12)

## Nodes

| Id | Local time | Type | Actor | Subject | Source | Details |
|----|-----------:|------|-------|---------|--------|---------|
| A:e01 | 0.00 | MOVING_START | A | - | ego | active_at_first_observation=True |
| A:e02 | 0.00 | THROTTLE_START | A | - | controls | active_at_first_observation=True |
| A:e03 | 0.00 | TRACK_APPEARED_FRONT | A | track_002 | radar | initial_in_ego_path=True |
| A:e04 | 0.00 | TRACK_APPEARED_LEFT | A | track_001 | radar | initial_in_ego_path=False |
| A:e05 | 0.00 | TRACK_APPEARED_LEFT | A | track_005 | radar | initial_in_ego_path=False |
| A:e06 | 0.00 | TRACK_APPEARED_LEFT | A | track_006 | radar | initial_in_ego_path=False |
| A:e07 | 0.00 | TRACK_APPEARED_RIGHT | A | track_003 | radar | initial_in_ego_path=False |
| A:e08 | 0.00 | TRACK_APPEARED_RIGHT | A | track_004 | radar | initial_in_ego_path=False |
| A:e09 | 0.00 | TRACK_APPEARED_RIGHT | A | track_007 | radar | initial_in_ego_path=False |
| A:e10 | 0.50 | CRITICAL_TTC_START | A | track_002 | radar |  |
| A:e11 | 5.95 | THROTTLE_END | A | - | controls |  |
| A:e12 | 5.95 | BRAKE_START | A | - | controls |  |
| A:e13 | 6.30 | CLOSING_START | A | track_006 | radar |  |
| A:e14 | 6.35 | CLOSING_START | A | track_007 | radar |  |
| A:e15 | 6.80 | CRITICAL_TTC_END | A | track_002 | radar |  |
| A:e16 | 6.90 | CLOSING_END | A | track_007 | radar |  |
| A:e17 | 7.05 | CLOSING_END | A | track_006 | radar |  |
| A:e18 | 7.15 | MOVING_END | A | - | ego |  |
| A:e19 | 7.15 | STOP_START | A | - | ego |  |
| A:e20 | 7.45 | COLLISION | A | - | collision_sensor | peak_impulse=34836.87 |
| A:e21 | 7.50 | BRAKE_END | A | - | controls |  |
| A:e22 | 7.90 | TRACK_APPEARED_FRONT | A | track_008 | radar | initial_in_ego_path=True |
| A:e23 | 8.00 | BRAKE_START | A | - | controls |  |
| A:e24 | 8.95 | TRACK_LOST | A | track_005 | radar |  |
| A:e25 | 9.55 | TRACK_LOST | A | track_001 | radar |  |
| A:e26 | 10.05 | TRACK_APPEARED_LEFT | A | track_009 | radar | initial_in_ego_path=False |
| A:e27 | 10.25 | TRACK_LOST | A | track_008 | radar |  |
| A:e28 | 10.40 | TRACK_APPEARED_LEFT | A | track_010 | radar | initial_in_ego_path=False |
| A:e29 | 11.35 | TRACK_LOST | A | track_009 | radar |  |
| A:e30 | 11.85 | TRACK_LOST | A | track_002 | radar |  |
| A:e31 | 11.90 | TRACK_LOST | A | track_003 | radar |  |

Events are state transitions; the quantities behind them (speed, pedals, ranges, TTC, relative motion, closest approach) are facts in `local_trace.jsonl`. Events with equal times are simultaneous at the recorder's resolution: PRECEDES links only different times. SAME_TRACK links a track's TRACK_APPEARED_* to every other event about the same local track (grouping only, no order).

## Edges

```
    A:e01 --PRECEDES--> A:e10
    A:e02 --PRECEDES--> A:e10
    A:e03 --PRECEDES--> A:e10
    A:e04 --PRECEDES--> A:e10
    A:e05 --PRECEDES--> A:e10
    A:e06 --PRECEDES--> A:e10
    A:e07 --PRECEDES--> A:e10
    A:e08 --PRECEDES--> A:e10
    A:e09 --PRECEDES--> A:e10
    A:e10 --PRECEDES--> A:e11
    A:e10 --PRECEDES--> A:e12
    A:e11 --PRECEDES--> A:e13
    A:e12 --PRECEDES--> A:e13
    A:e13 --PRECEDES--> A:e14
    A:e14 --PRECEDES--> A:e15
    A:e15 --PRECEDES--> A:e16
    A:e16 --PRECEDES--> A:e17
    A:e17 --PRECEDES--> A:e18
    A:e17 --PRECEDES--> A:e19
    A:e18 --PRECEDES--> A:e20
    A:e19 --PRECEDES--> A:e20
    A:e20 --PRECEDES--> A:e21
    A:e21 --PRECEDES--> A:e22
    A:e22 --PRECEDES--> A:e23
    A:e23 --PRECEDES--> A:e24
    A:e24 --PRECEDES--> A:e25
    A:e25 --PRECEDES--> A:e26
    A:e26 --PRECEDES--> A:e27
    A:e27 --PRECEDES--> A:e28
    A:e28 --PRECEDES--> A:e29
    A:e29 --PRECEDES--> A:e30
    A:e30 --PRECEDES--> A:e31
    A:e03 --SAME_TRACK--> A:e10
    A:e06 --SAME_TRACK--> A:e13
    A:e09 --SAME_TRACK--> A:e14
    A:e03 --SAME_TRACK--> A:e15
    A:e09 --SAME_TRACK--> A:e16
    A:e06 --SAME_TRACK--> A:e17
    A:e05 --SAME_TRACK--> A:e24
    A:e04 --SAME_TRACK--> A:e25
    A:e22 --SAME_TRACK--> A:e27
    A:e26 --SAME_TRACK--> A:e29
    A:e03 --SAME_TRACK--> A:e30
    A:e07 --SAME_TRACK--> A:e31
```

## Perceived state before each event

Each row is the state just BEFORE its events (none of them applied): events at one time are simultaneous and share it. True states are named, unknown ones end with `?`, false ones are omitted; a lost track's states are UNKNOWN, never ended. Facts: the trace frame at the time shown.

| Local time | Events | Perceived state just before | Facts at |
|-----------:|--------|-----------------------------|---------:|
| 0.00 | A:e01 MOVING_START<br>A:e02 THROTTLE_START<br>A:e03 TRACK_APPEARED_FRONT track_002<br>A:e04 TRACK_APPEARED_LEFT track_001<br>A:e05 TRACK_APPEARED_LEFT track_005<br>A:e06 TRACK_APPEARED_LEFT track_006<br>A:e07 TRACK_APPEARED_RIGHT track_003<br>A:e08 TRACK_APPEARED_RIGHT track_004<br>A:e09 TRACK_APPEARED_RIGHT track_007 | ego: not yet observed | - |
| 0.50 | A:e10 CRITICAL_TTC_START track_002 | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC?<br>track_002: IN_EGO_PATH, CRITICAL_TTC?<br>track_003: CRITICAL_TTC?<br>track_004: CRITICAL_TTC?<br>track_005: CRITICAL_TTC?<br>track_006: CRITICAL_TTC?<br>track_007: CRITICAL_TTC? | 0.40 |
| 5.95 | A:e11 THROTTLE_END<br>A:e12 BRAKE_START | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: CRITICAL_TTC, IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_006: no active state<br>track_007: no active state | 5.90 |
| 6.30 | A:e13 CLOSING_START track_006 | ego: MOVING, BRAKE<br>track_001: no active state<br>track_002: CRITICAL_TTC, IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_006: no active state<br>track_007: no active state | 6.20 |
| 6.35 | A:e14 CLOSING_START track_007 | ego: MOVING, BRAKE<br>track_001: no active state<br>track_002: CRITICAL_TTC, IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_006: CLOSING<br>track_007: no active state | 6.30 |
| 6.80 | A:e15 CRITICAL_TTC_END track_002 | ego: MOVING, BRAKE<br>track_001: no active state<br>track_002: CRITICAL_TTC, IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_006: CLOSING<br>track_007: CLOSING | 6.70 |
| 6.90 | A:e16 CLOSING_END track_007 | ego: MOVING, BRAKE<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_006: CLOSING<br>track_007: CLOSING | 6.80 |
| 7.05 | A:e17 CLOSING_END track_006 | ego: MOVING, BRAKE<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_006: CLOSING<br>track_007: no active state | 7.00 |
| 7.15 | A:e18 MOVING_END<br>A:e19 STOP_START | ego: MOVING, BRAKE<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_006: no active state<br>track_007: no active state | 7.10 |
| 7.45 | A:e20 COLLISION | ego: STOP, BRAKE<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_006: no active state<br>track_007: no active state | 7.40 |
| 7.50 | A:e21 BRAKE_END | ego: STOP, BRAKE<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_006: no active state<br>track_007: no active state | 7.40 |
| 7.90 | A:e22 TRACK_APPEARED_FRONT track_008 | ego: STOP<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_006: no active state<br>track_007: no active state | 7.80 |
| 8.00 | A:e23 BRAKE_START | ego: STOP<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_006: no active state<br>track_007: no active state<br>track_008: IN_EGO_PATH, CRITICAL_TTC? | 7.90 |
| 8.95 | A:e24 TRACK_LOST track_005 | ego: STOP, BRAKE<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_005: no active state<br>track_006: no active state<br>track_007: no active state<br>track_008: IN_EGO_PATH | 8.90 |
| 9.55 | A:e25 TRACK_LOST track_001 | ego: STOP, BRAKE<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_006: no active state<br>track_007: no active state<br>track_008: IN_EGO_PATH<br>track lost, states UNKNOWN: track_005 | 9.50 |
| 10.05 | A:e26 TRACK_APPEARED_LEFT track_009 | ego: STOP, BRAKE<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_006: no active state<br>track_007: no active state<br>track_008: IN_EGO_PATH<br>track lost, states UNKNOWN: track_001, track_005 | 10.00 |
| 10.25 | A:e27 TRACK_LOST track_008 | ego: STOP, BRAKE<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_006: no active state<br>track_007: no active state<br>track_008: IN_EGO_PATH<br>track_009: CRITICAL_TTC?<br>track lost, states UNKNOWN: track_001, track_005 | 10.20 |
| 10.40 | A:e28 TRACK_APPEARED_LEFT track_010 | ego: STOP, BRAKE<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_006: no active state<br>track_007: no active state<br>track_009: CRITICAL_TTC?<br>track lost, states UNKNOWN: track_001, track_005, track_008 | 10.30 |
| 11.35 | A:e29 TRACK_LOST track_009 | ego: STOP, BRAKE<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_006: no active state<br>track_007: no active state<br>track_009: no active state<br>track_010: no active state<br>track lost, states UNKNOWN: track_001, track_005, track_008 | 11.30 |
| 11.85 | A:e30 TRACK_LOST track_002 | ego: STOP, BRAKE<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_006: no active state<br>track_007: no active state<br>track_010: no active state<br>track lost, states UNKNOWN: track_001, track_005, track_008, track_009 | 11.80 |
| 11.90 | A:e31 TRACK_LOST track_003 | ego: STOP, BRAKE<br>track_003: no active state<br>track_004: no active state<br>track_006: no active state<br>track_007: no active state<br>track_010: no active state<br>track lost, states UNKNOWN: track_001, track_002, track_005, track_008, track_009 | 11.80 |

## States still active when observation ended

- STOP, since A:e19 (t = 7.15 s)
- BRAKE, since A:e23 (t = 8.00 s)

## Tracks lost

- track_008 at 10.25 s (A:e27): IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)
- track_002 at 11.85 s (A:e30): IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)
- lost with no state active: track_005, track_001, track_009, track_003

## Temporal safety relations

Order of each track's cut-in, critical TTC and path entry and of the collision report, in local time. Temporal properties only, not causes.

- track_002: CRITICAL_TTC_START 0.50, COLLISION 7.45 (+6.95 s)

## Sign detection windows

- none

An END means this recorder stopped detecting the sign, not that its obligation ended.

## Anonymous radar tracks

| Track | First seen | Last seen | Measured sweeps | First range / bearing | Min range (at) | Last range / bearing | Max speed |
|-------|-----------:|----------:|----------------:|----------------------|----------------|---------------------|----------:|
| track_001 | 0.00 | 9.55 | 190 | 3.3 m / -34 deg | 3.07 m (4.55) | 35.2 m / -5 deg | 12.1 m/s |
| track_002 | 0.00 | 11.85 | 229 | 7.7 m / +0 deg | 7.20 m (4.05) | 68.2 m / -6 deg | 12.1 m/s |
| track_003 | 0.00 | 11.90 | 239 | 5.1 m / +28 deg | 5.14 m (0.00) | 65.4 m / -3 deg | 12.1 m/s |
| track_004 | 0.00 | 11.95 | 229 | 16.1 m / +10 deg | 16.13 m (0.30) | 76.8 m / -6 deg | 12.2 m/s |
| track_005 | 0.00 | 8.95 | 173 | 14.1 m / -11 deg | 14.11 m (0.35) | 40.5 m / -5 deg | 12.2 m/s |
| track_006 | 0.00 | 11.95 | 240 | 4.6 m / -141 deg | 1.82 m (7.25) | 53.2 m / -8 deg | 12.0 m/s |
| track_007 | 0.00 | 11.95 | 240 | 2.7 m / +128 deg | 1.74 m (7.15) | 53.6 m / -0 deg | 12.0 m/s |
| track_008 | 7.90 | 10.25 | 46 | 34.3 m / -2 deg | 34.34 m (7.90) | 61.9 m / -5 deg | 11.9 m/s |
| track_009 | 10.05 | 11.35 | 20 | 54.6 m / -8 deg | 54.60 m (10.05) | 69.8 m / -10 deg | 11.9 m/s |
| track_010 | 10.40 | 11.95 | 23 | 46.3 m / -8 deg | 46.28 m (10.40) | 64.6 m / -9 deg | 12.0 m/s |

Bearing: positive = to A's right. Ranges are measured from the radar to the visible surface of the object.

## Plain-language reading

- t = 0.00 s: A started moving (already the case when first observed).
- t = 0.00 s: A pressed the accelerator (already the case when first observed).
- t = 0.00 s: A's radar started tracking track_002, which appeared in front of it.
- t = 0.00 s: A's radar started tracking track_001, which appeared on its left.
- t = 0.00 s: A's radar started tracking track_005, which appeared on its left.
- t = 0.00 s: A's radar started tracking track_006, which appeared on its left.
- t = 0.00 s: A's radar started tracking track_003, which appeared on its right.
- t = 0.00 s: A's radar started tracking track_004, which appeared on its right.
- t = 0.00 s: A's radar started tracking track_007, which appeared on its right.
- t = 0.50 s: A's time-to-contact with track_002 became critical.
- t = 5.95 s: A released the accelerator.
- t = 5.95 s: A started braking.
- t = 6.30 s: A observed track_006 start closing in.
- t = 6.35 s: A observed track_007 start closing in.
- t = 6.80 s: A's time-to-contact with track_002 stopped being critical.
- t = 6.90 s: A observed track_007 stop closing in.
- t = 7.05 s: A observed track_006 stop closing in.
- t = 7.15 s: A stopped moving.
- t = 7.15 s: A came to a stop.
- t = 7.45 s: A's collision sensor recorded a contact (peak impulse 34837 N*s).
- t = 7.50 s: A released the brake.
- t = 7.90 s: A's radar started tracking track_008, which appeared in front of it.
- t = 8.00 s: A started braking.
- t = 8.95 s: A's radar lost track_005 (its states are UNKNOWN from then on, not ended).
- t = 9.55 s: A's radar lost track_001 (its states are UNKNOWN from then on, not ended).
- t = 10.05 s: A's radar started tracking track_009, which appeared on its left.
- t = 10.25 s: A's radar lost track_008 (its states are UNKNOWN from then on, not ended).
- t = 10.40 s: A's radar started tracking track_010, which appeared on its left.
- t = 11.35 s: A's radar lost track_009 (its states are UNKNOWN from then on, not ended).
- t = 11.85 s: A's radar lost track_002 (its states are UNKNOWN from then on, not ended).
- t = 11.90 s: A's radar lost track_003 (its states are UNKNOWN from then on, not ended).
