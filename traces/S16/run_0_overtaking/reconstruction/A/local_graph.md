# Local graph - vehicle A

All times are A's own local clock: `t_local` = seconds since A's first ego sample (raw clock reading 2116.1734774261713 at `t_local` = 0). Only files under `vehicles/A/` were read; external objects are anonymous radar tracks.

- Local frame: origin = first ego position; x = first heading; y = to the right of the first heading (CARLA convention)
- Trace: 121 frames at 10 Hz in `local_trace.jsonl`, the last one at the recording end (11.95 s)
- Anonymous radar tracks: 11 (10 Hz samples in `local_tracks.jsonl`)
- Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.
- Nodes: 42; edges: 90 (PRECEDES 66, SAME_TRACK 24)

## Nodes

| Id | Local time | Type | Actor | Subject | Source | Details |
|----|-----------:|------|-------|---------|--------|---------|
| A:e01 | 0.00 | MOVING_START | A | - | ego | active_at_first_observation=True |
| A:e02 | 0.00 | THROTTLE_START | A | - | controls | active_at_first_observation=True |
| A:e03 | 0.00 | TRACK_APPEARED_FRONT | A | track_003 | radar | initial_in_ego_path=True |
| A:e04 | 0.00 | TRACK_APPEARED_LEFT | A | track_001 | radar | initial_in_ego_path=False |
| A:e05 | 0.00 | TRACK_APPEARED_LEFT | A | track_002 | radar | initial_in_ego_path=False |
| A:e06 | 0.00 | TRACK_APPEARED_RIGHT | A | track_004 | radar | initial_in_ego_path=False |
| A:e07 | 0.00 | TRACK_APPEARED_RIGHT | A | track_005 | radar | initial_in_ego_path=False |
| A:e08 | 0.00 | CLOSING_START | A | track_004 | radar | active_at_first_observation=True |
| A:e09 | 0.40 | TRACK_APPEARED_LEFT | A | track_006 | radar | initial_in_ego_path=False |
| A:e10 | 0.40 | CLOSING_START | A | track_006 | radar | active_at_first_observation=True |
| A:e11 | 0.50 | CRITICAL_TTC_START | A | track_003 | radar |  |
| A:e12 | 0.50 | TRACK_LOST | A | track_005 | radar |  |
| A:e13 | 3.60 | TRACK_LOST | A | track_002 | radar |  |
| A:e14 | 3.60 | TRACK_LOST | A | track_004 | radar |  |
| A:e15 | 4.05 | CLOSING_END | A | track_006 | radar |  |
| A:e16 | 5.15 | CRITICAL_TTC_START | A | track_006 | radar |  |
| A:e17 | 5.30 | TRACK_APPEARED_RIGHT | A | track_007 | radar | initial_in_ego_path=False |
| A:e18 | 5.30 | CLOSING_START | A | track_007 | radar | active_at_first_observation=True |
| A:e19 | 5.90 | TRACK_APPEARED_FRONT | A | track_008 | radar | initial_in_ego_path=False |
| A:e20 | 5.90 | CLOSING_START | A | track_006 | radar |  |
| A:e21 | 6.30 | EGO_PATH_ENTRY | A | track_001 | radar | occupancy_evidence=box; occupancy_margin_m=0.47; occupancy_sigma_m=0.27; cause=MUTUAL_LATERAL; geometry=estimated_body |
| A:e22 | 6.30 | CRITICAL_TTC_START | A | track_001 | radar |  |
| A:e23 | 6.45 | EGO_PATH_ENTRY | A | track_006 | radar | occupancy_evidence=returns; occupancy_margin_m=0.42; occupancy_sigma_m=0.25; cause=RECORDER_LATERAL; geometry=estimated_body |
| A:e24 | 6.50 | EGO_PATH_ENTRY | A | track_008 | radar | occupancy_evidence=box; occupancy_margin_m=0.60; occupancy_sigma_m=0.28; cause=RECORDER_LATERAL; geometry=estimated_body |
| A:e25 | 6.75 | COLLISION | A | - | collision_sensor | peak_impulse=191.84; merged_bursts=[[8.25, 12.44]] |
| A:e26 | 6.75 | CRITICAL_TTC_END | A | track_006 | radar |  |
| A:e27 | 6.80 | CLOSING_END | A | track_006 | radar |  |
| A:e28 | 6.80 | THROTTLE_END | A | - | controls |  |
| A:e29 | 6.80 | BRAKE_START | A | - | controls |  |
| A:e30 | 7.20 | CLOSING_END | A | track_007 | radar |  |
| A:e31 | 7.45 | CRITICAL_TTC_END | A | track_003 | radar |  |
| A:e32 | 7.90 | TRACK_APPEARED_FRONT | A | track_009 | radar | initial_in_ego_path=False |
| A:e33 | 7.95 | MOVING_END | A | - | ego |  |
| A:e34 | 7.95 | STOP_START | A | - | ego |  |
| A:e35 | 8.30 | TRACK_APPEARED_RIGHT | A | track_010 | radar | initial_in_ego_path=False |
| A:e36 | 8.30 | CLOSING_START | A | track_010 | radar | active_at_first_observation=True |
| A:e37 | 8.55 | TRACK_APPEARED_LEFT | A | track_011 | radar | initial_in_ego_path=False |
| A:e38 | 9.20 | EGO_PATH_ENTRY | A | track_011 | radar | occupancy_evidence=box; occupancy_margin_m=0.57; occupancy_sigma_m=0.33; cause=TARGET_LATERAL; geometry=estimated_body |
| A:e39 | 9.95 | TRACK_LOST | A | track_011 | radar |  |
| A:e40 | 10.35 | CLOSING_END | A | track_010 | radar |  |
| A:e41 | 11.20 | TRACK_LOST | A | track_001 | radar |  |
| A:e42 | 11.85 | TRACK_LOST | A | track_008 | radar |  |

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
    A:e11 --PRECEDES--> A:e14
    A:e12 --PRECEDES--> A:e13
    A:e12 --PRECEDES--> A:e14
    A:e13 --PRECEDES--> A:e15
    A:e14 --PRECEDES--> A:e15
    A:e15 --PRECEDES--> A:e16
    A:e16 --PRECEDES--> A:e17
    A:e16 --PRECEDES--> A:e18
    A:e17 --PRECEDES--> A:e19
    A:e17 --PRECEDES--> A:e20
    A:e18 --PRECEDES--> A:e19
    A:e18 --PRECEDES--> A:e20
    A:e19 --PRECEDES--> A:e21
    A:e19 --PRECEDES--> A:e22
    A:e20 --PRECEDES--> A:e21
    A:e20 --PRECEDES--> A:e22
    A:e21 --PRECEDES--> A:e23
    A:e22 --PRECEDES--> A:e23
    A:e23 --PRECEDES--> A:e24
    A:e24 --PRECEDES--> A:e25
    A:e24 --PRECEDES--> A:e26
    A:e25 --PRECEDES--> A:e27
    A:e25 --PRECEDES--> A:e28
    A:e25 --PRECEDES--> A:e29
    A:e26 --PRECEDES--> A:e27
    A:e26 --PRECEDES--> A:e28
    A:e26 --PRECEDES--> A:e29
    A:e27 --PRECEDES--> A:e30
    A:e28 --PRECEDES--> A:e30
    A:e29 --PRECEDES--> A:e30
    A:e30 --PRECEDES--> A:e31
    A:e31 --PRECEDES--> A:e32
    A:e32 --PRECEDES--> A:e33
    A:e32 --PRECEDES--> A:e34
    A:e33 --PRECEDES--> A:e35
    A:e33 --PRECEDES--> A:e36
    A:e34 --PRECEDES--> A:e35
    A:e34 --PRECEDES--> A:e36
    A:e35 --PRECEDES--> A:e37
    A:e36 --PRECEDES--> A:e37
    A:e37 --PRECEDES--> A:e38
    A:e38 --PRECEDES--> A:e39
    A:e39 --PRECEDES--> A:e40
    A:e40 --PRECEDES--> A:e41
    A:e41 --PRECEDES--> A:e42
    A:e06 --SAME_TRACK--> A:e08
    A:e09 --SAME_TRACK--> A:e10
    A:e03 --SAME_TRACK--> A:e11
    A:e07 --SAME_TRACK--> A:e12
    A:e05 --SAME_TRACK--> A:e13
    A:e06 --SAME_TRACK--> A:e14
    A:e09 --SAME_TRACK--> A:e15
    A:e09 --SAME_TRACK--> A:e16
    A:e17 --SAME_TRACK--> A:e18
    A:e09 --SAME_TRACK--> A:e20
    A:e04 --SAME_TRACK--> A:e21
    A:e04 --SAME_TRACK--> A:e22
    A:e09 --SAME_TRACK--> A:e23
    A:e19 --SAME_TRACK--> A:e24
    A:e09 --SAME_TRACK--> A:e26
    A:e09 --SAME_TRACK--> A:e27
    A:e17 --SAME_TRACK--> A:e30
    A:e03 --SAME_TRACK--> A:e31
    A:e35 --SAME_TRACK--> A:e36
    A:e37 --SAME_TRACK--> A:e38
    A:e37 --SAME_TRACK--> A:e39
    A:e35 --SAME_TRACK--> A:e40
    A:e04 --SAME_TRACK--> A:e41
    A:e19 --SAME_TRACK--> A:e42
```

## Perceived state before each event

Each row is the state just BEFORE its events (none of them applied): events at one time are simultaneous and share it. True states are named, unknown ones end with `?`, false ones are omitted; a lost track's states are UNKNOWN, never ended. Facts: the trace frame at the time shown.

| Local time | Events | Perceived state just before | Facts at |
|-----------:|--------|-----------------------------|---------:|
| 0.00 | A:e01 MOVING_START<br>A:e02 THROTTLE_START<br>A:e03 TRACK_APPEARED_FRONT track_003<br>A:e04 TRACK_APPEARED_LEFT track_001<br>A:e05 TRACK_APPEARED_LEFT track_002<br>A:e06 TRACK_APPEARED_RIGHT track_004<br>A:e07 TRACK_APPEARED_RIGHT track_005<br>A:e08 CLOSING_START track_004 | ego: not yet observed | - |
| 0.40 | A:e09 TRACK_APPEARED_LEFT track_006<br>A:e10 CLOSING_START track_006 | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC?<br>track_002: CRITICAL_TTC?<br>track_003: IN_EGO_PATH, CRITICAL_TTC?<br>track_004: CLOSING, CRITICAL_TTC?<br>track_005: CRITICAL_TTC? | 0.30 |
| 0.50 | A:e11 CRITICAL_TTC_START track_003<br>A:e12 TRACK_LOST track_005 | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC?<br>track_002: CRITICAL_TTC?<br>track_003: IN_EGO_PATH, CRITICAL_TTC?<br>track_004: CLOSING, CRITICAL_TTC?<br>track_005: CRITICAL_TTC?<br>track_006: CLOSING, CRITICAL_TTC? | 0.40 |
| 3.60 | A:e13 TRACK_LOST track_002<br>A:e14 TRACK_LOST track_004 | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: no active state<br>track_003: CRITICAL_TTC, IN_EGO_PATH<br>track_004: CLOSING<br>track_006: CLOSING<br>track lost, states UNKNOWN: track_005 | 3.50 |
| 4.05 | A:e15 CLOSING_END track_006 | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_003: CRITICAL_TTC, IN_EGO_PATH<br>track_006: CLOSING<br>track lost, states UNKNOWN: track_002, track_004, track_005 | 4.00 |
| 5.15 | A:e16 CRITICAL_TTC_START track_006 | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_003: CRITICAL_TTC, IN_EGO_PATH<br>track_006: no active state<br>track lost, states UNKNOWN: track_002, track_004, track_005 | 5.10 |
| 5.30 | A:e17 TRACK_APPEARED_RIGHT track_007<br>A:e18 CLOSING_START track_007 | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_003: CRITICAL_TTC, IN_EGO_PATH<br>track_006: CRITICAL_TTC<br>track lost, states UNKNOWN: track_002, track_004, track_005 | 5.20 |
| 5.90 | A:e19 TRACK_APPEARED_FRONT track_008<br>A:e20 CLOSING_START track_006 | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_003: CRITICAL_TTC, IN_EGO_PATH<br>track_006: CRITICAL_TTC<br>track_007: CLOSING<br>track lost, states UNKNOWN: track_002, track_004, track_005 | 5.80 |
| 6.30 | A:e21 EGO_PATH_ENTRY track_001<br>A:e22 CRITICAL_TTC_START track_001 | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_003: CRITICAL_TTC, IN_EGO_PATH<br>track_006: CLOSING, CRITICAL_TTC<br>track_007: CLOSING<br>track_008: CRITICAL_TTC?<br>track lost, states UNKNOWN: track_002, track_004, track_005 | 6.20 |
| 6.45 | A:e23 EGO_PATH_ENTRY track_006 | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_003: CRITICAL_TTC, IN_EGO_PATH<br>track_006: CLOSING, CRITICAL_TTC<br>track_007: CLOSING<br>track_008: no active state<br>track lost, states UNKNOWN: track_002, track_004, track_005 | 6.40 |
| 6.50 | A:e24 EGO_PATH_ENTRY track_008 | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_003: CRITICAL_TTC, IN_EGO_PATH<br>track_006: CLOSING, CRITICAL_TTC, IN_EGO_PATH<br>track_007: CLOSING<br>track_008: no active state<br>track lost, states UNKNOWN: track_002, track_004, track_005 | 6.40 |
| 6.75 | A:e25 COLLISION<br>A:e26 CRITICAL_TTC_END track_006 | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_003: CRITICAL_TTC, IN_EGO_PATH<br>track_006: CLOSING, CRITICAL_TTC, IN_EGO_PATH<br>track_007: CLOSING<br>track_008: IN_EGO_PATH<br>track lost, states UNKNOWN: track_002, track_004, track_005 | 6.70 |
| 6.80 | A:e27 CLOSING_END track_006<br>A:e28 THROTTLE_END<br>A:e29 BRAKE_START | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_003: CRITICAL_TTC, IN_EGO_PATH<br>track_006: CLOSING, IN_EGO_PATH<br>track_007: CLOSING<br>track_008: IN_EGO_PATH<br>track lost, states UNKNOWN: track_002, track_004, track_005 | 6.70 |
| 7.20 | A:e30 CLOSING_END track_007 | ego: MOVING, BRAKE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_003: CRITICAL_TTC, IN_EGO_PATH<br>track_006: IN_EGO_PATH<br>track_007: CLOSING<br>track_008: IN_EGO_PATH<br>track lost, states UNKNOWN: track_002, track_004, track_005 | 7.10 |
| 7.45 | A:e31 CRITICAL_TTC_END track_003 | ego: MOVING, BRAKE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_003: CRITICAL_TTC, IN_EGO_PATH<br>track_006: IN_EGO_PATH<br>track_007: no active state<br>track_008: IN_EGO_PATH<br>track lost, states UNKNOWN: track_002, track_004, track_005 | 7.40 |
| 7.90 | A:e32 TRACK_APPEARED_FRONT track_009 | ego: MOVING, BRAKE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_003: IN_EGO_PATH<br>track_006: IN_EGO_PATH<br>track_007: no active state<br>track_008: IN_EGO_PATH<br>track lost, states UNKNOWN: track_002, track_004, track_005 | 7.80 |
| 7.95 | A:e33 MOVING_END<br>A:e34 STOP_START | ego: MOVING, BRAKE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_003: IN_EGO_PATH<br>track_006: IN_EGO_PATH<br>track_007: no active state<br>track_008: IN_EGO_PATH<br>track_009: CRITICAL_TTC?<br>track lost, states UNKNOWN: track_002, track_004, track_005 | 7.90 |
| 8.30 | A:e35 TRACK_APPEARED_RIGHT track_010<br>A:e36 CLOSING_START track_010 | ego: STOP, BRAKE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_003: IN_EGO_PATH<br>track_006: IN_EGO_PATH<br>track_007: no active state<br>track_008: IN_EGO_PATH<br>track_009: CRITICAL_TTC?<br>track lost, states UNKNOWN: track_002, track_004, track_005 | 8.20 |
| 8.55 | A:e37 TRACK_APPEARED_LEFT track_011 | ego: STOP, BRAKE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_003: IN_EGO_PATH<br>track_006: IN_EGO_PATH<br>track_007: no active state<br>track_008: IN_EGO_PATH<br>track_009: no active state<br>track_010: CLOSING, CRITICAL_TTC?<br>track lost, states UNKNOWN: track_002, track_004, track_005 | 8.50 |
| 9.20 | A:e38 EGO_PATH_ENTRY track_011 | ego: STOP, BRAKE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_003: IN_EGO_PATH<br>track_006: IN_EGO_PATH<br>track_007: no active state<br>track_008: IN_EGO_PATH<br>track_009: no active state<br>track_010: CLOSING<br>track_011: no active state<br>track lost, states UNKNOWN: track_002, track_004, track_005 | 9.10 |
| 9.95 | A:e39 TRACK_LOST track_011 | ego: STOP, BRAKE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_003: IN_EGO_PATH<br>track_006: IN_EGO_PATH<br>track_007: no active state<br>track_008: IN_EGO_PATH<br>track_009: no active state<br>track_010: CLOSING<br>track_011: IN_EGO_PATH<br>track lost, states UNKNOWN: track_002, track_004, track_005 | 9.90 |
| 10.35 | A:e40 CLOSING_END track_010 | ego: STOP, BRAKE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_003: IN_EGO_PATH<br>track_006: IN_EGO_PATH<br>track_007: no active state<br>track_008: IN_EGO_PATH<br>track_009: no active state<br>track_010: CLOSING<br>track lost, states UNKNOWN: track_002, track_004, track_005, track_011 | 10.30 |
| 11.20 | A:e41 TRACK_LOST track_001 | ego: STOP, BRAKE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_003: IN_EGO_PATH<br>track_006: IN_EGO_PATH<br>track_007: no active state<br>track_008: IN_EGO_PATH<br>track_009: no active state<br>track_010: no active state<br>track lost, states UNKNOWN: track_002, track_004, track_005, track_011 | 11.10 |
| 11.85 | A:e42 TRACK_LOST track_008 | ego: STOP, BRAKE<br>track_003: IN_EGO_PATH<br>track_006: IN_EGO_PATH<br>track_007: no active state<br>track_008: IN_EGO_PATH<br>track_009: no active state<br>track_010: no active state<br>track lost, states UNKNOWN: track_001, track_002, track_004, track_005, track_011 | 11.80 |

## States still active when observation ended

- CLOSING of track_004, since A:e08 (t = 0.00 s); the track was lost at 3.60 s
- EGO_PATH of track_001, since A:e21 (t = 6.30 s); the track was lost at 11.20 s
- CRITICAL_TTC of track_001, since A:e22 (t = 6.30 s); the track was lost at 11.20 s
- EGO_PATH of track_006, since A:e23 (t = 6.45 s)
- EGO_PATH of track_008, since A:e24 (t = 6.50 s); the track was lost at 11.85 s
- BRAKE, since A:e29 (t = 6.80 s)
- STOP, since A:e34 (t = 7.95 s)
- EGO_PATH of track_011, since A:e38 (t = 9.20 s); the track was lost at 9.95 s

## Tracks lost

- track_004 at 3.60 s (A:e14): CLOSING were true; they are UNKNOWN afterwards (no END recorded)
- track_011 at 9.95 s (A:e39): IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)
- track_001 at 11.20 s (A:e41): CRITICAL_TTC, IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)
- track_008 at 11.85 s (A:e42): IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)
- lost with no state active: track_005, track_002

## Temporal safety relations

Order of each track's cut-in, critical TTC and path entry and of the collision report, in local time. Temporal properties only, not causes.

- track_001: CRITICAL_TTC_START 6.30, COLLISION 6.75 (+0.45 s); EGO_PATH_ENTRY 6.30 together with critical TTC (+0.00 s)
- track_003: CRITICAL_TTC_START 0.50, COLLISION 6.75 (+6.25 s)
- track_006: CRITICAL_TTC_START 5.15, COLLISION 6.75 (+1.60 s); EGO_PATH_ENTRY 6.45 after critical TTC (+1.30 s)
- track_008: EGO_PATH_ENTRY 6.50, no critical TTC
- track_011: EGO_PATH_ENTRY 9.20, no critical TTC

## Sign detection windows

- none

An END means this recorder stopped detecting the sign, not that its obligation ended.

## Anonymous radar tracks

| Track | First seen | Last seen | Measured sweeps | First range / bearing | Min range (at) | Last range / bearing | Max speed |
|-------|-----------:|----------:|----------------:|----------------------|----------------|---------------------|----------:|
| track_001 | 0.00 | 11.20 | 215 | 2.8 m / -53 deg | 2.84 m (0.00) | 64.3 m / -13 deg | 14.1 m/s |
| track_002 | 0.00 | 3.60 | 70 | 16.5 m / -10 deg | 16.46 m (0.00) | 23.6 m / -8 deg | 13.9 m/s |
| track_003 | 0.00 | 11.95 | 237 | 11.9 m / +0 deg | 11.93 m (0.05) | 64.2 m / -10 deg | 12.2 m/s |
| track_004 | 0.00 | 3.60 | 72 | 32.1 m / +5 deg | 24.86 m (3.60) | 24.9 m / +8 deg | 9.9 m/s |
| track_005 | 0.00 | 0.50 | 11 | 8.4 m / +152 deg | 8.40 m (0.00) | 9.3 m / +154 deg | 9.9 m/s |
| track_006 | 0.40 | 11.95 | 232 | 9.4 m / -153 deg | 1.16 m (6.25) | 1.2 m / -46 deg | 13.8 m/s |
| track_007 | 5.30 | 11.95 | 129 | 22.1 m / +9 deg | 18.78 m (7.30) | 60.2 m / -6 deg | 10.2 m/s |
| track_008 | 5.90 | 11.85 | 111 | 28.4 m / -1 deg | 28.41 m (5.90) | 77.8 m / -13 deg | 14.2 m/s |
| track_009 | 7.90 | 11.95 | 41 | 34.7 m / +4 deg | 34.71 m (7.90) | 73.6 m / -9 deg | 10.2 m/s |
| track_010 | 8.30 | 11.95 | 74 | 17.8 m / +157 deg | 3.19 m (10.10) | 16.2 m / +10 deg | 9.9 m/s |
| track_011 | 8.55 | 9.95 | 19 | 45.1 m / -11 deg | 45.07 m (8.55) | 64.3 m / -12 deg | 13.9 m/s |

Bearing: positive = to A's right. Ranges are measured from the radar to the visible surface of the object.

## Plain-language reading

- t = 0.00 s: A started moving (already the case when first observed).
- t = 0.00 s: A pressed the accelerator (already the case when first observed).
- t = 0.00 s: A's radar started tracking track_003, which appeared in front of it.
- t = 0.00 s: A's radar started tracking track_001, which appeared on its left.
- t = 0.00 s: A's radar started tracking track_002, which appeared on its left.
- t = 0.00 s: A's radar started tracking track_004, which appeared on its right.
- t = 0.00 s: A's radar started tracking track_005, which appeared on its right.
- t = 0.00 s: A observed track_004 start closing in (already the case when first observed).
- t = 0.40 s: A's radar started tracking track_006, which appeared on its left.
- t = 0.40 s: A observed track_006 start closing in (already the case when first observed).
- t = 0.50 s: A's time-to-contact with track_003 became critical.
- t = 0.50 s: A's radar lost track_005 (its states are UNKNOWN from then on, not ended).
- t = 3.60 s: A's radar lost track_002 (its states are UNKNOWN from then on, not ended).
- t = 3.60 s: A's radar lost track_004 (its states are UNKNOWN from then on, not ended).
- t = 4.05 s: A observed track_006 stop closing in.
- t = 5.15 s: A's time-to-contact with track_006 became critical.
- t = 5.30 s: A's radar started tracking track_007, which appeared on its right.
- t = 5.30 s: A observed track_007 start closing in (already the case when first observed).
- t = 5.90 s: A's radar started tracking track_008, which appeared in front of it.
- t = 5.90 s: A observed track_006 start closing in.
- t = 6.30 s: A observed track_001 enter its forward path corridor.
- t = 6.30 s: A's time-to-contact with track_001 became critical.
- t = 6.45 s: A observed track_006 enter its forward path corridor.
- t = 6.50 s: A observed track_008 enter its forward path corridor.
- t = 6.75 s: A's collision sensor recorded a contact (peak impulse 192 N*s).
- t = 6.75 s: A's time-to-contact with track_006 stopped being critical.
- t = 6.80 s: A observed track_006 stop closing in.
- t = 6.80 s: A released the accelerator.
- t = 6.80 s: A started braking.
- t = 7.20 s: A observed track_007 stop closing in.
- t = 7.45 s: A's time-to-contact with track_003 stopped being critical.
- t = 7.90 s: A's radar started tracking track_009, which appeared in front of it.
- t = 7.95 s: A stopped moving.
- t = 7.95 s: A came to a stop.
- t = 8.30 s: A's radar started tracking track_010, which appeared on its right.
- t = 8.30 s: A observed track_010 start closing in (already the case when first observed).
- t = 8.55 s: A's radar started tracking track_011, which appeared on its left.
- t = 9.20 s: A observed track_011 enter its forward path corridor.
- t = 9.95 s: A's radar lost track_011 (its states are UNKNOWN from then on, not ended).
- t = 10.35 s: A observed track_010 stop closing in.
- t = 11.20 s: A's radar lost track_001 (its states are UNKNOWN from then on, not ended).
- t = 11.85 s: A's radar lost track_008 (its states are UNKNOWN from then on, not ended).
