# Local graph - vehicle B

All times are B's own local clock: `t_local` = seconds since B's first ego sample (raw clock reading 2116.1734774261713 at `t_local` = 0). Only files under `vehicles/B/` were read; external objects are anonymous radar tracks.

- Local frame: origin = first ego position; x = first heading; y = to the right of the first heading (CARLA convention)
- Trace: 121 frames at 10 Hz in `local_trace.jsonl`, the last one at the recording end (11.95 s)
- Anonymous radar tracks: 10 (10 Hz samples in `local_tracks.jsonl`)
- Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.
- Nodes: 40; edges: 84 (PRECEDES 61, SAME_TRACK 23)

## Nodes

| Id | Local time | Type | Actor | Subject | Source | Details |
|----|-----------:|------|-------|---------|--------|---------|
| B:e01 | 0.00 | MOVING_START | B | - | ego | active_at_first_observation=True |
| B:e02 | 0.00 | THROTTLE_START | B | - | controls | active_at_first_observation=True |
| B:e03 | 0.00 | TRACK_APPEARED_RIGHT | B | track_001 | radar | initial_in_ego_path=False |
| B:e04 | 0.00 | TRACK_APPEARED_RIGHT | B | track_002 | radar | initial_in_ego_path=False |
| B:e05 | 0.00 | TRACK_APPEARED_RIGHT | B | track_003 | radar | initial_in_ego_path=False |
| B:e06 | 0.00 | CLOSING_START | B | track_001 | radar | active_at_first_observation=True |
| B:e07 | 0.00 | CLOSING_START | B | track_002 | radar | active_at_first_observation=True |
| B:e08 | 0.20 | TRACK_APPEARED_FRONT | B | track_004 | radar | initial_in_ego_path=False |
| B:e09 | 0.20 | CLOSING_START | B | track_004 | radar | active_at_first_observation=True |
| B:e10 | 0.35 | TRACK_APPEARED_FRONT | B | track_005 | radar | initial_in_ego_path=True |
| B:e11 | 0.85 | CRITICAL_TTC_START | B | track_005 | radar |  |
| B:e12 | 3.10 | TRACK_LOST | B | track_004 | radar |  |
| B:e13 | 4.10 | CLOSING_END | B | track_001 | radar |  |
| B:e14 | 5.20 | TRACK_LOST | B | track_003 | radar |  |
| B:e15 | 5.65 | TRACK_APPEARED_RIGHT | B | track_006 | radar | initial_in_ego_path=False |
| B:e16 | 5.65 | CLOSING_START | B | track_006 | radar | active_at_first_observation=True |
| B:e17 | 5.65 | CRITICAL_TTC_START | B | track_001 | radar |  |
| B:e18 | 5.90 | TRACK_APPEARED_RIGHT | B | track_007 | radar | initial_in_ego_path=False |
| B:e19 | 5.90 | CLOSING_START | B | track_007 | radar | active_at_first_observation=True |
| B:e20 | 6.10 | CLOSING_START | B | track_001 | radar |  |
| B:e21 | 6.20 | TRACK_APPEARED_RIGHT | B | track_008 | radar | initial_in_ego_path=False |
| B:e22 | 6.20 | CLOSING_START | B | track_008 | radar | active_at_first_observation=True |
| B:e23 | 6.75 | COLLISION | B | - | collision_sensor | peak_impulse=191.84; merged_bursts=[[8.25, 12.44]] |
| B:e24 | 6.75 | CRITICAL_TTC_END | B | track_001 | radar |  |
| B:e25 | 6.80 | THROTTLE_END | B | - | controls |  |
| B:e26 | 6.80 | BRAKE_START | B | - | controls |  |
| B:e27 | 6.85 | CLOSING_END | B | track_001 | radar |  |
| B:e28 | 7.05 | CLOSING_END | B | track_007 | radar |  |
| B:e29 | 7.10 | CLOSING_END | B | track_002 | radar |  |
| B:e30 | 7.35 | CLOSING_END | B | track_006 | radar |  |
| B:e31 | 7.35 | CLOSING_END | B | track_008 | radar |  |
| B:e32 | 7.55 | CRITICAL_TTC_END | B | track_005 | radar |  |
| B:e33 | 7.55 | TRACK_LOST | B | track_008 | radar |  |
| B:e34 | 7.90 | MOVING_END | B | - | ego |  |
| B:e35 | 7.90 | STOP_START | B | - | ego |  |
| B:e36 | 8.25 | TRACK_APPEARED_LEFT | B | track_009 | radar | initial_in_ego_path=True |
| B:e37 | 9.70 | TRACK_LOST | B | track_009 | radar |  |
| B:e38 | 10.20 | TRACK_APPEARED_RIGHT | B | track_010 | radar | initial_in_ego_path=False |
| B:e39 | 11.10 | TRACK_LOST | B | track_005 | radar |  |
| B:e40 | 11.55 | TRACK_LOST | B | track_007 | radar |  |

Events are state transitions; the quantities behind them (speed, pedals, ranges, TTC, relative motion, closest approach) are facts in `local_trace.jsonl`. Events with equal times are simultaneous at the recorder's resolution: PRECEDES links only different times. SAME_TRACK links a track's TRACK_APPEARED_* to every other event about the same local track (grouping only, no order).

## Edges

```
    B:e01 --PRECEDES--> B:e08
    B:e01 --PRECEDES--> B:e09
    B:e02 --PRECEDES--> B:e08
    B:e02 --PRECEDES--> B:e09
    B:e03 --PRECEDES--> B:e08
    B:e03 --PRECEDES--> B:e09
    B:e04 --PRECEDES--> B:e08
    B:e04 --PRECEDES--> B:e09
    B:e05 --PRECEDES--> B:e08
    B:e05 --PRECEDES--> B:e09
    B:e06 --PRECEDES--> B:e08
    B:e06 --PRECEDES--> B:e09
    B:e07 --PRECEDES--> B:e08
    B:e07 --PRECEDES--> B:e09
    B:e08 --PRECEDES--> B:e10
    B:e09 --PRECEDES--> B:e10
    B:e10 --PRECEDES--> B:e11
    B:e11 --PRECEDES--> B:e12
    B:e12 --PRECEDES--> B:e13
    B:e13 --PRECEDES--> B:e14
    B:e14 --PRECEDES--> B:e15
    B:e14 --PRECEDES--> B:e16
    B:e14 --PRECEDES--> B:e17
    B:e15 --PRECEDES--> B:e18
    B:e15 --PRECEDES--> B:e19
    B:e16 --PRECEDES--> B:e18
    B:e16 --PRECEDES--> B:e19
    B:e17 --PRECEDES--> B:e18
    B:e17 --PRECEDES--> B:e19
    B:e18 --PRECEDES--> B:e20
    B:e19 --PRECEDES--> B:e20
    B:e20 --PRECEDES--> B:e21
    B:e20 --PRECEDES--> B:e22
    B:e21 --PRECEDES--> B:e23
    B:e21 --PRECEDES--> B:e24
    B:e22 --PRECEDES--> B:e23
    B:e22 --PRECEDES--> B:e24
    B:e23 --PRECEDES--> B:e25
    B:e23 --PRECEDES--> B:e26
    B:e24 --PRECEDES--> B:e25
    B:e24 --PRECEDES--> B:e26
    B:e25 --PRECEDES--> B:e27
    B:e26 --PRECEDES--> B:e27
    B:e27 --PRECEDES--> B:e28
    B:e28 --PRECEDES--> B:e29
    B:e29 --PRECEDES--> B:e30
    B:e29 --PRECEDES--> B:e31
    B:e30 --PRECEDES--> B:e32
    B:e30 --PRECEDES--> B:e33
    B:e31 --PRECEDES--> B:e32
    B:e31 --PRECEDES--> B:e33
    B:e32 --PRECEDES--> B:e34
    B:e32 --PRECEDES--> B:e35
    B:e33 --PRECEDES--> B:e34
    B:e33 --PRECEDES--> B:e35
    B:e34 --PRECEDES--> B:e36
    B:e35 --PRECEDES--> B:e36
    B:e36 --PRECEDES--> B:e37
    B:e37 --PRECEDES--> B:e38
    B:e38 --PRECEDES--> B:e39
    B:e39 --PRECEDES--> B:e40
    B:e03 --SAME_TRACK--> B:e06
    B:e04 --SAME_TRACK--> B:e07
    B:e08 --SAME_TRACK--> B:e09
    B:e10 --SAME_TRACK--> B:e11
    B:e08 --SAME_TRACK--> B:e12
    B:e03 --SAME_TRACK--> B:e13
    B:e05 --SAME_TRACK--> B:e14
    B:e15 --SAME_TRACK--> B:e16
    B:e03 --SAME_TRACK--> B:e17
    B:e18 --SAME_TRACK--> B:e19
    B:e03 --SAME_TRACK--> B:e20
    B:e21 --SAME_TRACK--> B:e22
    B:e03 --SAME_TRACK--> B:e24
    B:e03 --SAME_TRACK--> B:e27
    B:e18 --SAME_TRACK--> B:e28
    B:e04 --SAME_TRACK--> B:e29
    B:e15 --SAME_TRACK--> B:e30
    B:e21 --SAME_TRACK--> B:e31
    B:e10 --SAME_TRACK--> B:e32
    B:e21 --SAME_TRACK--> B:e33
    B:e36 --SAME_TRACK--> B:e37
    B:e10 --SAME_TRACK--> B:e39
    B:e18 --SAME_TRACK--> B:e40
```

## Perceived state before each event

Each row is the state just BEFORE its events (none of them applied): events at one time are simultaneous and share it. True states are named, unknown ones end with `?`, false ones are omitted; a lost track's states are UNKNOWN, never ended. Facts: the trace frame at the time shown.

| Local time | Events | Perceived state just before | Facts at |
|-----------:|--------|-----------------------------|---------:|
| 0.00 | B:e01 MOVING_START<br>B:e02 THROTTLE_START<br>B:e03 TRACK_APPEARED_RIGHT track_001<br>B:e04 TRACK_APPEARED_RIGHT track_002<br>B:e05 TRACK_APPEARED_RIGHT track_003<br>B:e06 CLOSING_START track_001<br>B:e07 CLOSING_START track_002 | ego: not yet observed | - |
| 0.20 | B:e08 TRACK_APPEARED_FRONT track_004<br>B:e09 CLOSING_START track_004 | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC?<br>track_002: CLOSING, CRITICAL_TTC?<br>track_003: CRITICAL_TTC? | 0.10 |
| 0.35 | B:e10 TRACK_APPEARED_FRONT track_005 | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC?<br>track_002: CLOSING, CRITICAL_TTC?<br>track_003: CRITICAL_TTC?<br>track_004: CLOSING, CRITICAL_TTC? | 0.30 |
| 0.85 | B:e11 CRITICAL_TTC_START track_005 | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>track_002: CLOSING<br>track_003: no active state<br>track_004: CLOSING<br>track_005: IN_EGO_PATH, CRITICAL_TTC? | 0.80 |
| 3.10 | B:e12 TRACK_LOST track_004 | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>track_002: CLOSING<br>track_003: no active state<br>track_004: CLOSING<br>track_005: CRITICAL_TTC, IN_EGO_PATH | 3.00 |
| 4.10 | B:e13 CLOSING_END track_001 | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>track_002: CLOSING<br>track_003: no active state<br>track_005: CRITICAL_TTC, IN_EGO_PATH<br>track lost, states UNKNOWN: track_004 | 4.00 |
| 5.20 | B:e14 TRACK_LOST track_003 | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: CLOSING<br>track_003: no active state<br>track_005: CRITICAL_TTC, IN_EGO_PATH<br>track lost, states UNKNOWN: track_004 | 5.10 |
| 5.65 | B:e15 TRACK_APPEARED_RIGHT track_006<br>B:e16 CLOSING_START track_006<br>B:e17 CRITICAL_TTC_START track_001 | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: CLOSING<br>track_005: CRITICAL_TTC, IN_EGO_PATH<br>track lost, states UNKNOWN: track_003, track_004 | 5.60 |
| 5.90 | B:e18 TRACK_APPEARED_RIGHT track_007<br>B:e19 CLOSING_START track_007 | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC<br>track_002: CLOSING<br>track_005: CRITICAL_TTC, IN_EGO_PATH<br>track_006: CLOSING, CRITICAL_TTC?<br>track lost, states UNKNOWN: track_003, track_004 | 5.80 |
| 6.10 | B:e20 CLOSING_START track_001 | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC<br>track_002: CLOSING<br>track_005: CRITICAL_TTC, IN_EGO_PATH<br>track_006: CLOSING, CRITICAL_TTC?<br>track_007: CLOSING, CRITICAL_TTC?<br>track lost, states UNKNOWN: track_003, track_004 | 6.00 |
| 6.20 | B:e21 TRACK_APPEARED_RIGHT track_008<br>B:e22 CLOSING_START track_008 | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC<br>track_002: CLOSING<br>track_005: CRITICAL_TTC, IN_EGO_PATH<br>track_006: CLOSING<br>track_007: CLOSING, CRITICAL_TTC?<br>track lost, states UNKNOWN: track_003, track_004 | 6.10 |
| 6.75 | B:e23 COLLISION<br>B:e24 CRITICAL_TTC_END track_001 | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC<br>track_002: CLOSING<br>track_005: CRITICAL_TTC, IN_EGO_PATH<br>track_006: CLOSING<br>track_007: CLOSING<br>track_008: CLOSING<br>track lost, states UNKNOWN: track_003, track_004 | 6.70 |
| 6.80 | B:e25 THROTTLE_END<br>B:e26 BRAKE_START | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>track_002: CLOSING<br>track_005: CRITICAL_TTC, IN_EGO_PATH<br>track_006: CLOSING<br>track_007: CLOSING<br>track_008: CLOSING<br>track lost, states UNKNOWN: track_003, track_004 | 6.70 |
| 6.85 | B:e27 CLOSING_END track_001 | ego: MOVING, BRAKE<br>track_001: CLOSING<br>track_002: CLOSING<br>track_005: CRITICAL_TTC, IN_EGO_PATH<br>track_006: CLOSING<br>track_007: CLOSING<br>track_008: CLOSING<br>track lost, states UNKNOWN: track_003, track_004 | 6.80 |
| 7.05 | B:e28 CLOSING_END track_007 | ego: MOVING, BRAKE<br>track_001: no active state<br>track_002: CLOSING<br>track_005: CRITICAL_TTC, IN_EGO_PATH<br>track_006: CLOSING<br>track_007: CLOSING<br>track_008: CLOSING<br>track lost, states UNKNOWN: track_003, track_004 | 7.00 |
| 7.10 | B:e29 CLOSING_END track_002 | ego: MOVING, BRAKE<br>track_001: no active state<br>track_002: CLOSING<br>track_005: CRITICAL_TTC, IN_EGO_PATH<br>track_006: CLOSING<br>track_007: no active state<br>track_008: CLOSING<br>track lost, states UNKNOWN: track_003, track_004 | 7.00 |
| 7.35 | B:e30 CLOSING_END track_006<br>B:e31 CLOSING_END track_008 | ego: MOVING, BRAKE<br>track_001: no active state<br>track_002: no active state<br>track_005: CRITICAL_TTC, IN_EGO_PATH<br>track_006: CLOSING<br>track_007: no active state<br>track_008: CLOSING<br>track lost, states UNKNOWN: track_003, track_004 | 7.30 |
| 7.55 | B:e32 CRITICAL_TTC_END track_005<br>B:e33 TRACK_LOST track_008 | ego: MOVING, BRAKE<br>track_001: no active state<br>track_002: no active state<br>track_005: CRITICAL_TTC, IN_EGO_PATH<br>track_006: no active state<br>track_007: no active state<br>track_008: no active state<br>track lost, states UNKNOWN: track_003, track_004 | 7.50 |
| 7.90 | B:e34 MOVING_END<br>B:e35 STOP_START | ego: MOVING, BRAKE<br>track_001: no active state<br>track_002: no active state<br>track_005: IN_EGO_PATH<br>track_006: no active state<br>track_007: no active state<br>track lost, states UNKNOWN: track_003, track_004, track_008 | 7.80 |
| 8.25 | B:e36 TRACK_APPEARED_LEFT track_009 | ego: STOP, BRAKE<br>track_001: no active state<br>track_002: no active state<br>track_005: IN_EGO_PATH<br>track_006: no active state<br>track_007: no active state<br>track lost, states UNKNOWN: track_003, track_004, track_008 | 8.20 |
| 9.70 | B:e37 TRACK_LOST track_009 | ego: STOP, BRAKE<br>track_001: no active state<br>track_002: no active state<br>track_005: IN_EGO_PATH<br>track_006: no active state<br>track_007: no active state<br>track_009: IN_EGO_PATH<br>track lost, states UNKNOWN: track_003, track_004, track_008 | 9.60 |
| 10.20 | B:e38 TRACK_APPEARED_RIGHT track_010 | ego: STOP, BRAKE<br>track_001: no active state<br>track_002: no active state<br>track_005: IN_EGO_PATH<br>track_006: no active state<br>track_007: no active state<br>track lost, states UNKNOWN: track_003, track_004, track_008, track_009 | 10.10 |
| 11.10 | B:e39 TRACK_LOST track_005 | ego: STOP, BRAKE<br>track_001: no active state<br>track_002: no active state<br>track_005: IN_EGO_PATH<br>track_006: no active state<br>track_007: no active state<br>track_010: no active state<br>track lost, states UNKNOWN: track_003, track_004, track_008, track_009 | 11.00 |
| 11.55 | B:e40 TRACK_LOST track_007 | ego: STOP, BRAKE<br>track_001: no active state<br>track_002: no active state<br>track_006: no active state<br>track_007: no active state<br>track_010: no active state<br>track lost, states UNKNOWN: track_003, track_004, track_005, track_008, track_009 | 11.50 |

## States still active when observation ended

- CLOSING of track_004, since B:e09 (t = 0.20 s); the track was lost at 3.10 s
- BRAKE, since B:e26 (t = 6.80 s)
- STOP, since B:e35 (t = 7.90 s)

## Tracks lost

- track_004 at 3.10 s (B:e12): CLOSING were true; they are UNKNOWN afterwards (no END recorded)
- track_009 at 9.70 s (B:e37): IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)
- track_005 at 11.10 s (B:e39): IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)
- lost with no state active: track_003, track_008, track_007

## Temporal safety relations

Order of each track's cut-in, critical TTC and path entry and of the collision report, in local time. Temporal properties only, not causes.

- track_001: CRITICAL_TTC_START 5.65, COLLISION 6.75 (+1.10 s)
- track_005: CRITICAL_TTC_START 0.85, COLLISION 6.75 (+5.90 s)

## Sign detection windows

- none

An END means this recorder stopped detecting the sign, not that its obligation ended.

## Anonymous radar tracks

| Track | First seen | Last seen | Measured sweeps | First range / bearing | Min range (at) | Last range / bearing | Max speed |
|-------|-----------:|----------:|----------------:|----------------------|----------------|---------------------|----------:|
| track_001 | 0.00 | 11.95 | 240 | 8.5 m / +16 deg | 0.17 m (11.95) | 0.2 m / +100 deg | 13.2 m/s |
| track_002 | 0.00 | 11.95 | 238 | 23.9 m / +8 deg | 10.54 m (7.15) | 61.7 m / -10 deg | 12.1 m/s |
| track_003 | 0.00 | 5.20 | 105 | 5.6 m / +69 deg | 5.09 m (0.60) | 18.3 m / +156 deg | 10.3 m/s |
| track_004 | 0.20 | 3.10 | 52 | 39.2 m / +5 deg | 33.13 m (3.10) | 33.1 m / +5 deg | 11.8 m/s |
| track_005 | 0.35 | 11.10 | 209 | 11.2 m / +0 deg | 10.31 m (6.75) | 60.4 m / -12 deg | 14.2 m/s |
| track_006 | 5.65 | 11.95 | 124 | 22.4 m / +17 deg | 16.92 m (7.40) | 58.0 m / -6 deg | 10.3 m/s |
| track_007 | 5.90 | 11.55 | 109 | 28.1 m / +6 deg | 25.93 m (7.15) | 71.9 m / -12 deg | 12.1 m/s |
| track_008 | 6.20 | 7.55 | 18 | 36.5 m / +9 deg | 32.87 m (7.40) | 33.0 m / +3 deg | 10.2 m/s |
| track_009 | 8.25 | 9.70 | 24 | 38.7 m / -9 deg | 38.71 m (8.25) | 58.7 m / -12 deg | 14.1 m/s |
| track_010 | 10.20 | 11.95 | 36 | 5.1 m / +103 deg | 4.86 m (10.40) | 14.3 m / +16 deg | 10.0 m/s |

Bearing: positive = to B's right. Ranges are measured from the radar to the visible surface of the object.

## Plain-language reading

- t = 0.00 s: B started moving (already the case when first observed).
- t = 0.00 s: B pressed the accelerator (already the case when first observed).
- t = 0.00 s: B's radar started tracking track_001, which appeared on its right.
- t = 0.00 s: B's radar started tracking track_002, which appeared on its right.
- t = 0.00 s: B's radar started tracking track_003, which appeared on its right.
- t = 0.00 s: B observed track_001 start closing in (already the case when first observed).
- t = 0.00 s: B observed track_002 start closing in (already the case when first observed).
- t = 0.20 s: B's radar started tracking track_004, which appeared in front of it.
- t = 0.20 s: B observed track_004 start closing in (already the case when first observed).
- t = 0.35 s: B's radar started tracking track_005, which appeared in front of it.
- t = 0.85 s: B's time-to-contact with track_005 became critical.
- t = 3.10 s: B's radar lost track_004 (its states are UNKNOWN from then on, not ended).
- t = 4.10 s: B observed track_001 stop closing in.
- t = 5.20 s: B's radar lost track_003 (its states are UNKNOWN from then on, not ended).
- t = 5.65 s: B's radar started tracking track_006, which appeared on its right.
- t = 5.65 s: B observed track_006 start closing in (already the case when first observed).
- t = 5.65 s: B's time-to-contact with track_001 became critical.
- t = 5.90 s: B's radar started tracking track_007, which appeared on its right.
- t = 5.90 s: B observed track_007 start closing in (already the case when first observed).
- t = 6.10 s: B observed track_001 start closing in.
- t = 6.20 s: B's radar started tracking track_008, which appeared on its right.
- t = 6.20 s: B observed track_008 start closing in (already the case when first observed).
- t = 6.75 s: B's collision sensor recorded a contact (peak impulse 192 N*s).
- t = 6.75 s: B's time-to-contact with track_001 stopped being critical.
- t = 6.80 s: B released the accelerator.
- t = 6.80 s: B started braking.
- t = 6.85 s: B observed track_001 stop closing in.
- t = 7.05 s: B observed track_007 stop closing in.
- t = 7.10 s: B observed track_002 stop closing in.
- t = 7.35 s: B observed track_006 stop closing in.
- t = 7.35 s: B observed track_008 stop closing in.
- t = 7.55 s: B's time-to-contact with track_005 stopped being critical.
- t = 7.55 s: B's radar lost track_008 (its states are UNKNOWN from then on, not ended).
- t = 7.90 s: B stopped moving.
- t = 7.90 s: B came to a stop.
- t = 8.25 s: B's radar started tracking track_009, which appeared on its left.
- t = 9.70 s: B's radar lost track_009 (its states are UNKNOWN from then on, not ended).
- t = 10.20 s: B's radar started tracking track_010, which appeared on its right.
- t = 11.10 s: B's radar lost track_005 (its states are UNKNOWN from then on, not ended).
- t = 11.55 s: B's radar lost track_007 (its states are UNKNOWN from then on, not ended).
