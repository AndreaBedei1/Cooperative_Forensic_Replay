# Local graph - vehicle A

All times are A's own local clock: `t_local` = seconds since A's first ego sample (raw clock reading 2148.3647394552827 at `t_local` = 0). Only files under `vehicles/A/` were read; external objects are anonymous radar tracks.

- Local frame: origin = first ego position; x = first heading; y = to the right of the first heading (CARLA convention)
- Trace: 121 frames at 10 Hz in `local_trace.jsonl`, the last one at the recording end (11.95 s)
- Anonymous radar tracks: 10 (10 Hz samples in `local_tracks.jsonl`)
- Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.
- Nodes: 39; edges: 89 (PRECEDES 67, SAME_TRACK 22)

## Nodes

| Id | Local time | Type | Actor | Subject | Source | Details |
|----|-----------:|------|-------|---------|--------|---------|
| A:e01 | 0.00 | MOVING_START | A | - | ego | active_at_first_observation=True |
| A:e02 | 0.00 | THROTTLE_START | A | - | controls | active_at_first_observation=True |
| A:e03 | 0.00 | TRACK_APPEARED_FRONT | A | track_002 | radar | initial_in_ego_path=True |
| A:e04 | 0.00 | TRACK_APPEARED_LEFT | A | track_001 | radar | initial_in_ego_path=False |
| A:e05 | 0.00 | TRACK_APPEARED_LEFT | A | track_003 | radar | initial_in_ego_path=False |
| A:e06 | 0.00 | TRACK_APPEARED_RIGHT | A | track_004 | radar | initial_in_ego_path=False |
| A:e07 | 0.00 | CLOSING_START | A | track_001 | radar | active_at_first_observation=True |
| A:e08 | 0.00 | CLOSING_START | A | track_002 | radar | active_at_first_observation=True |
| A:e09 | 0.05 | TRACK_APPEARED_RIGHT | A | track_005 | radar | initial_in_ego_path=False |
| A:e10 | 0.05 | CLOSING_START | A | track_005 | radar | active_at_first_observation=True |
| A:e11 | 0.40 | TRACK_APPEARED_FRONT | A | track_006 | radar | initial_in_ego_path=False |
| A:e12 | 0.40 | CLOSING_START | A | track_006 | radar | active_at_first_observation=True |
| A:e13 | 0.50 | CRITICAL_TTC_START | A | track_002 | radar |  |
| A:e14 | 4.60 | TRACK_LOST | A | track_006 | radar |  |
| A:e15 | 5.65 | TRACK_LOST | A | track_004 | radar |  |
| A:e16 | 6.35 | TRACK_LOST | A | track_003 | radar |  |
| A:e17 | 7.20 | CLOSING_END | A | track_005 | radar |  |
| A:e18 | 7.60 | TRACK_APPEARED_FRONT | A | track_008 | radar | initial_in_ego_path=True |
| A:e19 | 7.60 | TRACK_APPEARED_LEFT | A | track_007 | radar | initial_in_ego_path=False |
| A:e20 | 7.65 | COLLISION | A | - | collision_sensor | peak_impulse=1168.63 |
| A:e21 | 7.65 | CRITICAL_TTC_END | A | track_002 | radar |  |
| A:e22 | 7.65 | CLOSING_END | A | track_001 | radar |  |
| A:e23 | 7.65 | CLOSING_END | A | track_002 | radar |  |
| A:e24 | 7.70 | THROTTLE_END | A | - | controls |  |
| A:e25 | 7.70 | BRAKE_START | A | - | controls |  |
| A:e26 | 8.35 | TRACK_LOST | A | track_007 | radar |  |
| A:e27 | 8.35 | TRACK_LOST | A | track_008 | radar |  |
| A:e28 | 8.70 | TRACK_APPEARED_LEFT | A | track_009 | radar | initial_in_ego_path=False |
| A:e29 | 8.70 | CLOSING_START | A | track_009 | radar | active_at_first_observation=True |
| A:e30 | 8.75 | MOVING_END | A | - | ego |  |
| A:e31 | 8.75 | STOP_START | A | - | ego |  |
| A:e32 | 8.85 | TRACK_APPEARED_RIGHT | A | track_010 | radar | initial_in_ego_path=False |
| A:e33 | 8.85 | CLOSING_START | A | track_010 | radar | active_at_first_observation=True |
| A:e34 | 8.95 | TRACK_LOST | A | track_001 | radar |  |
| A:e35 | 9.10 | TRACK_LOST | A | track_005 | radar |  |
| A:e36 | 9.45 | CLOSING_END | A | track_009 | radar |  |
| A:e37 | 9.60 | CLOSING_END | A | track_010 | radar |  |
| A:e38 | 10.60 | TRACK_LOST | A | track_009 | radar |  |
| A:e39 | 10.75 | TRACK_LOST | A | track_010 | radar |  |

Events are state transitions; the quantities behind them (speed, pedals, ranges, TTC, relative motion, closest approach) are facts in `local_trace.jsonl`. Events with equal times are simultaneous at the recorder's resolution: PRECEDES links only different times. SAME_TRACK links a track's TRACK_APPEARED_* to every other event about the same local track (grouping only, no order).

## Edges

```
    A:e01 --PRECEDES--> A:e09
    A:e01 --PRECEDES--> A:e10
    A:e02 --PRECEDES--> A:e09
    A:e02 --PRECEDES--> A:e10
    A:e03 --PRECEDES--> A:e09
    A:e03 --PRECEDES--> A:e10
    A:e04 --PRECEDES--> A:e09
    A:e04 --PRECEDES--> A:e10
    A:e05 --PRECEDES--> A:e09
    A:e05 --PRECEDES--> A:e10
    A:e06 --PRECEDES--> A:e09
    A:e06 --PRECEDES--> A:e10
    A:e07 --PRECEDES--> A:e09
    A:e07 --PRECEDES--> A:e10
    A:e08 --PRECEDES--> A:e09
    A:e08 --PRECEDES--> A:e10
    A:e09 --PRECEDES--> A:e11
    A:e09 --PRECEDES--> A:e12
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
    A:e18 --PRECEDES--> A:e21
    A:e18 --PRECEDES--> A:e22
    A:e18 --PRECEDES--> A:e23
    A:e19 --PRECEDES--> A:e20
    A:e19 --PRECEDES--> A:e21
    A:e19 --PRECEDES--> A:e22
    A:e19 --PRECEDES--> A:e23
    A:e20 --PRECEDES--> A:e24
    A:e20 --PRECEDES--> A:e25
    A:e21 --PRECEDES--> A:e24
    A:e21 --PRECEDES--> A:e25
    A:e22 --PRECEDES--> A:e24
    A:e22 --PRECEDES--> A:e25
    A:e23 --PRECEDES--> A:e24
    A:e23 --PRECEDES--> A:e25
    A:e24 --PRECEDES--> A:e26
    A:e24 --PRECEDES--> A:e27
    A:e25 --PRECEDES--> A:e26
    A:e25 --PRECEDES--> A:e27
    A:e26 --PRECEDES--> A:e28
    A:e26 --PRECEDES--> A:e29
    A:e27 --PRECEDES--> A:e28
    A:e27 --PRECEDES--> A:e29
    A:e28 --PRECEDES--> A:e30
    A:e28 --PRECEDES--> A:e31
    A:e29 --PRECEDES--> A:e30
    A:e29 --PRECEDES--> A:e31
    A:e30 --PRECEDES--> A:e32
    A:e30 --PRECEDES--> A:e33
    A:e31 --PRECEDES--> A:e32
    A:e31 --PRECEDES--> A:e33
    A:e32 --PRECEDES--> A:e34
    A:e33 --PRECEDES--> A:e34
    A:e34 --PRECEDES--> A:e35
    A:e35 --PRECEDES--> A:e36
    A:e36 --PRECEDES--> A:e37
    A:e37 --PRECEDES--> A:e38
    A:e38 --PRECEDES--> A:e39
    A:e04 --SAME_TRACK--> A:e07
    A:e03 --SAME_TRACK--> A:e08
    A:e09 --SAME_TRACK--> A:e10
    A:e11 --SAME_TRACK--> A:e12
    A:e03 --SAME_TRACK--> A:e13
    A:e11 --SAME_TRACK--> A:e14
    A:e06 --SAME_TRACK--> A:e15
    A:e05 --SAME_TRACK--> A:e16
    A:e09 --SAME_TRACK--> A:e17
    A:e03 --SAME_TRACK--> A:e21
    A:e04 --SAME_TRACK--> A:e22
    A:e03 --SAME_TRACK--> A:e23
    A:e19 --SAME_TRACK--> A:e26
    A:e18 --SAME_TRACK--> A:e27
    A:e28 --SAME_TRACK--> A:e29
    A:e32 --SAME_TRACK--> A:e33
    A:e04 --SAME_TRACK--> A:e34
    A:e09 --SAME_TRACK--> A:e35
    A:e28 --SAME_TRACK--> A:e36
    A:e32 --SAME_TRACK--> A:e37
    A:e28 --SAME_TRACK--> A:e38
    A:e32 --SAME_TRACK--> A:e39
```

## Perceived state before each event

Each row is the state just BEFORE its events (none of them applied): events at one time are simultaneous and share it. True states are named, unknown ones end with `?`, false ones are omitted; a lost track's states are UNKNOWN, never ended. Facts: the trace frame at the time shown.

| Local time | Events | Perceived state just before | Facts at |
|-----------:|--------|-----------------------------|---------:|
| 0.00 | A:e01 MOVING_START<br>A:e02 THROTTLE_START<br>A:e03 TRACK_APPEARED_FRONT track_002<br>A:e04 TRACK_APPEARED_LEFT track_001<br>A:e05 TRACK_APPEARED_LEFT track_003<br>A:e06 TRACK_APPEARED_RIGHT track_004<br>A:e07 CLOSING_START track_001<br>A:e08 CLOSING_START track_002 | ego: not yet observed | - |
| 0.05 | A:e09 TRACK_APPEARED_RIGHT track_005<br>A:e10 CLOSING_START track_005 | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC?<br>track_002: CLOSING, IN_EGO_PATH, CRITICAL_TTC?<br>track_003: CRITICAL_TTC?<br>track_004: CRITICAL_TTC? | 0.00 |
| 0.40 | A:e11 TRACK_APPEARED_FRONT track_006<br>A:e12 CLOSING_START track_006 | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC?<br>track_002: CLOSING, IN_EGO_PATH, CRITICAL_TTC?<br>track_003: CRITICAL_TTC?<br>track_004: CRITICAL_TTC?<br>track_005: CLOSING, CRITICAL_TTC? | 0.30 |
| 0.50 | A:e13 CRITICAL_TTC_START track_002 | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC?<br>track_002: CLOSING, IN_EGO_PATH, CRITICAL_TTC?<br>track_003: CRITICAL_TTC?<br>track_004: CRITICAL_TTC?<br>track_005: CLOSING, CRITICAL_TTC?<br>track_006: CLOSING, CRITICAL_TTC? | 0.40 |
| 4.60 | A:e14 TRACK_LOST track_006 | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>track_002: CLOSING, CRITICAL_TTC, IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_005: CLOSING<br>track_006: CLOSING | 4.50 |
| 5.65 | A:e15 TRACK_LOST track_004 | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>track_002: CLOSING, CRITICAL_TTC, IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_005: CLOSING<br>track lost, states UNKNOWN: track_006 | 5.60 |
| 6.35 | A:e16 TRACK_LOST track_003 | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>track_002: CLOSING, CRITICAL_TTC, IN_EGO_PATH<br>track_003: no active state<br>track_005: CLOSING<br>track lost, states UNKNOWN: track_004, track_006 | 6.30 |
| 7.20 | A:e17 CLOSING_END track_005 | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>track_002: CLOSING, CRITICAL_TTC, IN_EGO_PATH<br>track_005: CLOSING<br>track lost, states UNKNOWN: track_003, track_004, track_006 | 7.10 |
| 7.60 | A:e18 TRACK_APPEARED_FRONT track_008<br>A:e19 TRACK_APPEARED_LEFT track_007 | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>track_002: CLOSING, CRITICAL_TTC, IN_EGO_PATH<br>track_005: no active state<br>track lost, states UNKNOWN: track_003, track_004, track_006 | 7.50 |
| 7.65 | A:e20 COLLISION<br>A:e21 CRITICAL_TTC_END track_002<br>A:e22 CLOSING_END track_001<br>A:e23 CLOSING_END track_002 | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>track_002: CLOSING, CRITICAL_TTC, IN_EGO_PATH<br>track_005: no active state<br>track_007: CRITICAL_TTC?<br>track_008: IN_EGO_PATH, CRITICAL_TTC?<br>track lost, states UNKNOWN: track_003, track_004, track_006 | 7.60 |
| 7.70 | A:e24 THROTTLE_END<br>A:e25 BRAKE_START | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_005: no active state<br>track_007: CRITICAL_TTC?<br>track_008: IN_EGO_PATH, CRITICAL_TTC?<br>track lost, states UNKNOWN: track_003, track_004, track_006 | 7.60 |
| 8.35 | A:e26 TRACK_LOST track_007<br>A:e27 TRACK_LOST track_008 | ego: MOVING, BRAKE<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_005: no active state<br>track_007: no active state<br>track_008: IN_EGO_PATH<br>track lost, states UNKNOWN: track_003, track_004, track_006 | 8.30 |
| 8.70 | A:e28 TRACK_APPEARED_LEFT track_009<br>A:e29 CLOSING_START track_009 | ego: MOVING, BRAKE<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_005: no active state<br>track lost, states UNKNOWN: track_003, track_004, track_006, track_007, track_008 | 8.60 |
| 8.75 | A:e30 MOVING_END<br>A:e31 STOP_START | ego: MOVING, BRAKE<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_005: no active state<br>track_009: CLOSING, CRITICAL_TTC?<br>track lost, states UNKNOWN: track_003, track_004, track_006, track_007, track_008 | 8.70 |
| 8.85 | A:e32 TRACK_APPEARED_RIGHT track_010<br>A:e33 CLOSING_START track_010 | ego: STOP, BRAKE<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_005: no active state<br>track_009: CLOSING, CRITICAL_TTC?<br>track lost, states UNKNOWN: track_003, track_004, track_006, track_007, track_008 | 8.80 |
| 8.95 | A:e34 TRACK_LOST track_001 | ego: STOP, BRAKE<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_005: no active state<br>track_009: CLOSING, CRITICAL_TTC?<br>track_010: CLOSING, CRITICAL_TTC?<br>track lost, states UNKNOWN: track_003, track_004, track_006, track_007, track_008 | 8.90 |
| 9.10 | A:e35 TRACK_LOST track_005 | ego: STOP, BRAKE<br>track_002: IN_EGO_PATH<br>track_005: no active state<br>track_009: CLOSING, CRITICAL_TTC?<br>track_010: CLOSING, CRITICAL_TTC?<br>track lost, states UNKNOWN: track_001, track_003, track_004, track_006, track_007, track_008 | 9.00 |
| 9.45 | A:e36 CLOSING_END track_009 | ego: STOP, BRAKE<br>track_002: IN_EGO_PATH<br>track_009: CLOSING<br>track_010: CLOSING<br>track lost, states UNKNOWN: track_001, track_003, track_004, track_005, track_006, track_007, track_008 | 9.40 |
| 9.60 | A:e37 CLOSING_END track_010 | ego: STOP, BRAKE<br>track_002: IN_EGO_PATH<br>track_009: no active state<br>track_010: CLOSING<br>track lost, states UNKNOWN: track_001, track_003, track_004, track_005, track_006, track_007, track_008 | 9.50 |
| 10.60 | A:e38 TRACK_LOST track_009 | ego: STOP, BRAKE<br>track_002: IN_EGO_PATH<br>track_009: no active state<br>track_010: no active state<br>track lost, states UNKNOWN: track_001, track_003, track_004, track_005, track_006, track_007, track_008 | 10.50 |
| 10.75 | A:e39 TRACK_LOST track_010 | ego: STOP, BRAKE<br>track_002: IN_EGO_PATH<br>track_010: no active state<br>track lost, states UNKNOWN: track_001, track_003, track_004, track_005, track_006, track_007, track_008, track_009 | 10.70 |

## States still active when observation ended

- CLOSING of track_006, since A:e12 (t = 0.40 s); the track was lost at 4.60 s
- BRAKE, since A:e25 (t = 7.70 s)
- STOP, since A:e31 (t = 8.75 s)

## Tracks lost

- track_006 at 4.60 s (A:e14): CLOSING were true; they are UNKNOWN afterwards (no END recorded)
- track_008 at 8.35 s (A:e27): IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)
- lost with no state active: track_004, track_003, track_007, track_001, track_005, track_009, track_010

## Temporal safety relations

Order of each track's cut-in, critical TTC and path entry and of the collision report, in local time. Temporal properties only, not causes.

- track_002: CRITICAL_TTC_START 0.50, COLLISION 7.65 (+7.15 s)

## Sign detection windows

- none

An END means this recorder stopped detecting the sign, not that its obligation ended.

## Anonymous radar tracks

| Track | First seen | Last seen | Measured sweeps | First range / bearing | Min range (at) | Last range / bearing | Max speed |
|-------|-----------:|----------:|----------------:|----------------------|----------------|---------------------|----------:|
| track_001 | 0.00 | 8.95 | 180 | 16.9 m / -9 deg | 3.42 m (7.35) | 8.7 m / -21 deg | 11.1 m/s |
| track_002 | 0.00 | 11.95 | 240 | 15.4 m / +1 deg | 0.14 m (7.80) | 1.0 m / -0 deg | 11.7 m/s |
| track_003 | 0.00 | 6.35 | 127 | 3.0 m / -48 deg | 1.69 m (1.35) | 9.1 m / -153 deg | 11.5 m/s |
| track_004 | 0.00 | 5.65 | 111 | 2.4 m / +59 deg | 1.69 m (0.80) | 9.4 m / +154 deg | 11.4 m/s |
| track_005 | 0.05 | 9.10 | 182 | 14.8 m / +12 deg | 2.35 m (7.90) | 8.9 m / +19 deg | 11.2 m/s |
| track_006 | 0.40 | 4.60 | 84 | 35.1 m / -5 deg | 26.49 m (4.60) | 26.5 m / -8 deg | 11.0 m/s |
| track_007 | 7.60 | 8.35 | 16 | 20.7 m / -7 deg | 20.46 m (7.90) | 21.2 m / -6 deg | 11.0 m/s |
| track_008 | 7.60 | 8.35 | 16 | 18.5 m / +0 deg | 18.31 m (7.90) | 19.1 m / +0 deg | 11.0 m/s |
| track_009 | 8.70 | 10.60 | 39 | 10.3 m / -160 deg | 2.14 m (9.65) | 10.5 m / -18 deg | 10.9 m/s |
| track_010 | 8.85 | 10.75 | 39 | 10.3 m / +160 deg | 2.14 m (9.80) | 10.6 m / +18 deg | 10.9 m/s |

Bearing: positive = to A's right. Ranges are measured from the radar to the visible surface of the object.

## Plain-language reading

- t = 0.00 s: A started moving (already the case when first observed).
- t = 0.00 s: A pressed the accelerator (already the case when first observed).
- t = 0.00 s: A's radar started tracking track_002, which appeared in front of it.
- t = 0.00 s: A's radar started tracking track_001, which appeared on its left.
- t = 0.00 s: A's radar started tracking track_003, which appeared on its left.
- t = 0.00 s: A's radar started tracking track_004, which appeared on its right.
- t = 0.00 s: A observed track_001 start closing in (already the case when first observed).
- t = 0.00 s: A observed track_002 start closing in (already the case when first observed).
- t = 0.05 s: A's radar started tracking track_005, which appeared on its right.
- t = 0.05 s: A observed track_005 start closing in (already the case when first observed).
- t = 0.40 s: A's radar started tracking track_006, which appeared in front of it.
- t = 0.40 s: A observed track_006 start closing in (already the case when first observed).
- t = 0.50 s: A's time-to-contact with track_002 became critical.
- t = 4.60 s: A's radar lost track_006 (its states are UNKNOWN from then on, not ended).
- t = 5.65 s: A's radar lost track_004 (its states are UNKNOWN from then on, not ended).
- t = 6.35 s: A's radar lost track_003 (its states are UNKNOWN from then on, not ended).
- t = 7.20 s: A observed track_005 stop closing in.
- t = 7.60 s: A's radar started tracking track_008, which appeared in front of it.
- t = 7.60 s: A's radar started tracking track_007, which appeared on its left.
- t = 7.65 s: A's collision sensor recorded a contact (peak impulse 1169 N*s).
- t = 7.65 s: A's time-to-contact with track_002 stopped being critical.
- t = 7.65 s: A observed track_001 stop closing in.
- t = 7.65 s: A observed track_002 stop closing in.
- t = 7.70 s: A released the accelerator.
- t = 7.70 s: A started braking.
- t = 8.35 s: A's radar lost track_007 (its states are UNKNOWN from then on, not ended).
- t = 8.35 s: A's radar lost track_008 (its states are UNKNOWN from then on, not ended).
- t = 8.70 s: A's radar started tracking track_009, which appeared on its left.
- t = 8.70 s: A observed track_009 start closing in (already the case when first observed).
- t = 8.75 s: A stopped moving.
- t = 8.75 s: A came to a stop.
- t = 8.85 s: A's radar started tracking track_010, which appeared on its right.
- t = 8.85 s: A observed track_010 start closing in (already the case when first observed).
- t = 8.95 s: A's radar lost track_001 (its states are UNKNOWN from then on, not ended).
- t = 9.10 s: A's radar lost track_005 (its states are UNKNOWN from then on, not ended).
- t = 9.45 s: A observed track_009 stop closing in.
- t = 9.60 s: A observed track_010 stop closing in.
- t = 10.60 s: A's radar lost track_009 (its states are UNKNOWN from then on, not ended).
- t = 10.75 s: A's radar lost track_010 (its states are UNKNOWN from then on, not ended).
