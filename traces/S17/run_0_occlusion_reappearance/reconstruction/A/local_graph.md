# Local graph - vehicle A

All times are A's own local clock: `t_local` = seconds since A's first ego sample (raw clock reading 2132.2441545389593 at `t_local` = 0). Only files under `vehicles/A/` were read; external objects are anonymous radar tracks.

- Local frame: origin = first ego position; x = first heading; y = to the right of the first heading (CARLA convention)
- Trace: 121 frames at 10 Hz in `local_trace.jsonl`, the last one at the recording end (11.95 s)
- Anonymous radar tracks: 8 (10 Hz samples in `local_tracks.jsonl`)
- Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.
- Nodes: 35; edges: 68 (PRECEDES 51, SAME_TRACK 17)

## Nodes

| Id | Local time | Type | Actor | Subject | Source | Details |
|----|-----------:|------|-------|---------|--------|---------|
| A:e01 | 0.00 | MOVING_START | A | - | ego | active_at_first_observation=True |
| A:e02 | 0.00 | THROTTLE_START | A | - | controls | active_at_first_observation=True |
| A:e03 | 0.00 | TRACK_APPEARED_FRONT | A | track_002 | radar | initial_in_ego_path=True |
| A:e04 | 0.00 | TRACK_APPEARED_FRONT | A | track_003 | radar | initial_in_ego_path=False |
| A:e05 | 0.00 | TRACK_APPEARED_LEFT | A | track_001 | radar | initial_in_ego_path=False |
| A:e06 | 0.00 | TRACK_APPEARED_LEFT | A | track_004 | radar | initial_in_ego_path=False |
| A:e07 | 0.00 | CLOSING_START | A | track_004 | radar | active_at_first_observation=True |
| A:e08 | 0.90 | TRACK_APPEARED_LEFT | A | track_005 | radar | initial_in_ego_path=False |
| A:e09 | 0.90 | CLOSING_START | A | track_005 | radar | active_at_first_observation=True |
| A:e10 | 3.30 | TRACK_LOST | A | track_003 | radar |  |
| A:e11 | 3.80 | CLOSING_END | A | track_005 | radar |  |
| A:e12 | 4.00 | INDICATOR_LEFT_START | A | - | lights |  |
| A:e13 | 4.55 | TRACK_LOST | A | track_004 | radar |  |
| A:e14 | 4.80 | TRACK_LOST | A | track_002 | radar |  |
| A:e15 | 5.45 | CRITICAL_TTC_START | A | track_005 | radar |  |
| A:e16 | 5.50 | CLOSING_START | A | track_005 | radar |  |
| A:e17 | 6.15 | TRACK_APPEARED_RIGHT | A | track_006 | radar | initial_in_ego_path=True |
| A:e18 | 6.20 | EGO_PATH_ENTRY | A | track_001 | radar | occupancy_evidence=box; occupancy_margin_m=0.45; occupancy_sigma_m=0.26; cause=MUTUAL_LATERAL; geometry=estimated_body |
| A:e19 | 6.20 | CRITICAL_TTC_START | A | track_001 | radar |  |
| A:e20 | 6.35 | TRACK_APPEARED_LEFT | A | track_007 | radar | initial_in_ego_path=False |
| A:e21 | 6.35 | CLOSING_START | A | track_007 | radar | active_at_first_observation=True |
| A:e22 | 7.30 | COLLISION | A | - | collision_sensor | peak_impulse=389.26 |
| A:e23 | 7.30 | CRITICAL_TTC_END | A | track_005 | radar |  |
| A:e24 | 7.35 | CLOSING_END | A | track_005 | radar |  |
| A:e25 | 7.35 | THROTTLE_END | A | - | controls |  |
| A:e26 | 7.35 | BRAKE_START | A | - | controls |  |
| A:e27 | 7.40 | TURN_LEFT_START | A | - | ego |  |
| A:e28 | 7.45 | EGO_PATH_EXIT | A | track_006 | radar | occupancy_evidence=box; occupancy_margin_m=-0.54; occupancy_sigma_m=0.28; cause=MUTUAL_LATERAL; geometry=estimated_body |
| A:e29 | 7.50 | CLOSING_END | A | track_007 | radar |  |
| A:e30 | 7.65 | CRITICAL_TTC_END | A | track_001 | radar |  |
| A:e31 | 8.10 | TRACK_APPEARED_RIGHT | A | track_008 | radar | initial_in_ego_path=True |
| A:e32 | 8.25 | TURN_LEFT_END | A | - | ego |  |
| A:e33 | 8.30 | MOVING_END | A | - | ego |  |
| A:e34 | 8.30 | STOP_START | A | - | ego |  |
| A:e35 | 11.90 | TRACK_LOST | A | track_008 | radar |  |

Events are state transitions; the quantities behind them (speed, pedals, ranges, TTC, relative motion, closest approach) are facts in `local_trace.jsonl`. Events with equal times are simultaneous at the recorder's resolution: PRECEDES links only different times. SAME_TRACK links a track's TRACK_APPEARED_* to every other event about the same local track (grouping only, no order).

## Edges

```
    A:e01 --PRECEDES--> A:e08
    A:e01 --PRECEDES--> A:e09
    A:e02 --PRECEDES--> A:e08
    A:e02 --PRECEDES--> A:e09
    A:e03 --PRECEDES--> A:e08
    A:e03 --PRECEDES--> A:e09
    A:e04 --PRECEDES--> A:e08
    A:e04 --PRECEDES--> A:e09
    A:e05 --PRECEDES--> A:e08
    A:e05 --PRECEDES--> A:e09
    A:e06 --PRECEDES--> A:e08
    A:e06 --PRECEDES--> A:e09
    A:e07 --PRECEDES--> A:e08
    A:e07 --PRECEDES--> A:e09
    A:e08 --PRECEDES--> A:e10
    A:e09 --PRECEDES--> A:e10
    A:e10 --PRECEDES--> A:e11
    A:e11 --PRECEDES--> A:e12
    A:e12 --PRECEDES--> A:e13
    A:e13 --PRECEDES--> A:e14
    A:e14 --PRECEDES--> A:e15
    A:e15 --PRECEDES--> A:e16
    A:e16 --PRECEDES--> A:e17
    A:e17 --PRECEDES--> A:e18
    A:e17 --PRECEDES--> A:e19
    A:e18 --PRECEDES--> A:e20
    A:e18 --PRECEDES--> A:e21
    A:e19 --PRECEDES--> A:e20
    A:e19 --PRECEDES--> A:e21
    A:e20 --PRECEDES--> A:e22
    A:e20 --PRECEDES--> A:e23
    A:e21 --PRECEDES--> A:e22
    A:e21 --PRECEDES--> A:e23
    A:e22 --PRECEDES--> A:e24
    A:e22 --PRECEDES--> A:e25
    A:e22 --PRECEDES--> A:e26
    A:e23 --PRECEDES--> A:e24
    A:e23 --PRECEDES--> A:e25
    A:e23 --PRECEDES--> A:e26
    A:e24 --PRECEDES--> A:e27
    A:e25 --PRECEDES--> A:e27
    A:e26 --PRECEDES--> A:e27
    A:e27 --PRECEDES--> A:e28
    A:e28 --PRECEDES--> A:e29
    A:e29 --PRECEDES--> A:e30
    A:e30 --PRECEDES--> A:e31
    A:e31 --PRECEDES--> A:e32
    A:e32 --PRECEDES--> A:e33
    A:e32 --PRECEDES--> A:e34
    A:e33 --PRECEDES--> A:e35
    A:e34 --PRECEDES--> A:e35
    A:e06 --SAME_TRACK--> A:e07
    A:e08 --SAME_TRACK--> A:e09
    A:e04 --SAME_TRACK--> A:e10
    A:e08 --SAME_TRACK--> A:e11
    A:e06 --SAME_TRACK--> A:e13
    A:e03 --SAME_TRACK--> A:e14
    A:e08 --SAME_TRACK--> A:e15
    A:e08 --SAME_TRACK--> A:e16
    A:e05 --SAME_TRACK--> A:e18
    A:e05 --SAME_TRACK--> A:e19
    A:e20 --SAME_TRACK--> A:e21
    A:e08 --SAME_TRACK--> A:e23
    A:e08 --SAME_TRACK--> A:e24
    A:e17 --SAME_TRACK--> A:e28
    A:e20 --SAME_TRACK--> A:e29
    A:e05 --SAME_TRACK--> A:e30
    A:e31 --SAME_TRACK--> A:e35
```

## Perceived state before each event

Each row is the state just BEFORE its events (none of them applied): events at one time are simultaneous and share it. True states are named, unknown ones end with `?`, false ones are omitted; a lost track's states are UNKNOWN, never ended. Facts: the trace frame at the time shown.

| Local time | Events | Perceived state just before | Facts at |
|-----------:|--------|-----------------------------|---------:|
| 0.00 | A:e01 MOVING_START<br>A:e02 THROTTLE_START<br>A:e03 TRACK_APPEARED_FRONT track_002<br>A:e04 TRACK_APPEARED_FRONT track_003<br>A:e05 TRACK_APPEARED_LEFT track_001<br>A:e06 TRACK_APPEARED_LEFT track_004<br>A:e07 CLOSING_START track_004 | ego: not yet observed | - |
| 0.90 | A:e08 TRACK_APPEARED_LEFT track_005<br>A:e09 CLOSING_START track_005 | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: CLOSING | 0.80 |
| 3.30 | A:e10 TRACK_LOST track_003 | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: CLOSING<br>track_005: CLOSING | 3.20 |
| 3.80 | A:e11 CLOSING_END track_005 | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_004: CLOSING<br>track_005: CLOSING<br>track lost, states UNKNOWN: track_003 | 3.70 |
| 4.00 | A:e12 INDICATOR_LEFT_START | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_004: CLOSING<br>track_005: no active state<br>track lost, states UNKNOWN: track_003 | 3.90 |
| 4.55 | A:e13 TRACK_LOST track_004 | ego: MOVING, THROTTLE, INDICATOR_LEFT<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_004: CLOSING<br>track_005: no active state<br>track lost, states UNKNOWN: track_003 | 4.50 |
| 4.80 | A:e14 TRACK_LOST track_002 | ego: MOVING, THROTTLE, INDICATOR_LEFT<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_005: no active state<br>track lost, states UNKNOWN: track_003, track_004 | 4.70 |
| 5.45 | A:e15 CRITICAL_TTC_START track_005 | ego: MOVING, THROTTLE, INDICATOR_LEFT<br>track_001: no active state<br>track_005: no active state<br>track lost, states UNKNOWN: track_002, track_003, track_004 | 5.40 |
| 5.50 | A:e16 CLOSING_START track_005 | ego: MOVING, THROTTLE, INDICATOR_LEFT<br>track_001: no active state<br>track_005: CRITICAL_TTC<br>track lost, states UNKNOWN: track_002, track_003, track_004 | 5.40 |
| 6.15 | A:e17 TRACK_APPEARED_RIGHT track_006 | ego: MOVING, THROTTLE, INDICATOR_LEFT<br>track_001: no active state<br>track_005: CLOSING, CRITICAL_TTC<br>track lost, states UNKNOWN: track_002, track_003, track_004 | 6.10 |
| 6.20 | A:e18 EGO_PATH_ENTRY track_001<br>A:e19 CRITICAL_TTC_START track_001 | ego: MOVING, THROTTLE, INDICATOR_LEFT<br>track_001: no active state<br>track_005: CLOSING, CRITICAL_TTC<br>track_006: IN_EGO_PATH, CRITICAL_TTC?<br>track lost, states UNKNOWN: track_002, track_003, track_004 | 6.10 |
| 6.35 | A:e20 TRACK_APPEARED_LEFT track_007<br>A:e21 CLOSING_START track_007 | ego: MOVING, THROTTLE, INDICATOR_LEFT<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_005: CLOSING, CRITICAL_TTC<br>track_006: IN_EGO_PATH, CRITICAL_TTC?<br>track lost, states UNKNOWN: track_002, track_003, track_004 | 6.30 |
| 7.30 | A:e22 COLLISION<br>A:e23 CRITICAL_TTC_END track_005 | ego: MOVING, THROTTLE, INDICATOR_LEFT<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_005: CLOSING, CRITICAL_TTC<br>track_006: IN_EGO_PATH<br>track_007: CLOSING<br>track lost, states UNKNOWN: track_002, track_003, track_004 | 7.20 |
| 7.35 | A:e24 CLOSING_END track_005<br>A:e25 THROTTLE_END<br>A:e26 BRAKE_START | ego: MOVING, THROTTLE, INDICATOR_LEFT<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_005: CLOSING<br>track_006: IN_EGO_PATH<br>track_007: CLOSING<br>track lost, states UNKNOWN: track_002, track_003, track_004 | 7.30 |
| 7.40 | A:e27 TURN_LEFT_START | ego: MOVING, BRAKE, INDICATOR_LEFT<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_005: no active state<br>track_006: IN_EGO_PATH<br>track_007: CLOSING<br>track lost, states UNKNOWN: track_002, track_003, track_004 | 7.30 |
| 7.45 | A:e28 EGO_PATH_EXIT track_006 | ego: MOVING, BRAKE, TURN_LEFT, INDICATOR_LEFT<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_005: no active state<br>track_006: IN_EGO_PATH<br>track_007: CLOSING<br>track lost, states UNKNOWN: track_002, track_003, track_004 | 7.40 |
| 7.50 | A:e29 CLOSING_END track_007 | ego: MOVING, BRAKE, TURN_LEFT, INDICATOR_LEFT<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_005: no active state<br>track_006: no active state<br>track_007: CLOSING<br>track lost, states UNKNOWN: track_002, track_003, track_004 | 7.40 |
| 7.65 | A:e30 CRITICAL_TTC_END track_001 | ego: MOVING, BRAKE, TURN_LEFT, INDICATOR_LEFT<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_005: no active state<br>track_006: no active state<br>track_007: no active state<br>track lost, states UNKNOWN: track_002, track_003, track_004 | 7.60 |
| 8.10 | A:e31 TRACK_APPEARED_RIGHT track_008 | ego: MOVING, BRAKE, TURN_LEFT, INDICATOR_LEFT<br>track_001: IN_EGO_PATH<br>track_005: no active state<br>track_006: no active state<br>track_007: no active state<br>track lost, states UNKNOWN: track_002, track_003, track_004 | 8.00 |
| 8.25 | A:e32 TURN_LEFT_END | ego: MOVING, BRAKE, TURN_LEFT, INDICATOR_LEFT<br>track_001: IN_EGO_PATH<br>track_005: no active state<br>track_006: no active state<br>track_007: no active state<br>track_008: IN_EGO_PATH, CRITICAL_TTC?<br>track lost, states UNKNOWN: track_002, track_003, track_004 | 8.20 |
| 8.30 | A:e33 MOVING_END<br>A:e34 STOP_START | ego: MOVING, BRAKE, INDICATOR_LEFT<br>track_001: IN_EGO_PATH<br>track_005: no active state<br>track_006: no active state<br>track_007: no active state<br>track_008: IN_EGO_PATH, CRITICAL_TTC?<br>track lost, states UNKNOWN: track_002, track_003, track_004 | 8.20 |
| 11.90 | A:e35 TRACK_LOST track_008 | ego: STOP, BRAKE, INDICATOR_LEFT<br>track_001: IN_EGO_PATH<br>track_005: no active state<br>track_006: no active state<br>track_007: no active state<br>track_008: IN_EGO_PATH<br>track lost, states UNKNOWN: track_002, track_003, track_004 | 11.80 |

## States still active when observation ended

- CLOSING of track_004, since A:e07 (t = 0.00 s); the track was lost at 4.55 s
- INDICATOR_LEFT, since A:e12 (t = 4.00 s)
- EGO_PATH of track_001, since A:e18 (t = 6.20 s)
- BRAKE, since A:e26 (t = 7.35 s)
- STOP, since A:e34 (t = 8.30 s)

## Tracks lost

- track_004 at 4.55 s (A:e13): CLOSING were true; they are UNKNOWN afterwards (no END recorded)
- track_002 at 4.80 s (A:e14): IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)
- track_008 at 11.90 s (A:e35): IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)
- lost with no state active: track_003

## Temporal safety relations

Order of each track's cut-in, critical TTC and path entry and of the collision report, in local time. Temporal properties only, not causes.

- track_001: CRITICAL_TTC_START 6.20, COLLISION 7.30 (+1.10 s); EGO_PATH_ENTRY 6.20 together with critical TTC (+0.00 s)
- track_005: CRITICAL_TTC_START 5.45, COLLISION 7.30 (+1.85 s)

## Sign detection windows

- none

An END means this recorder stopped detecting the sign, not that its obligation ended.

## Anonymous radar tracks

| Track | First seen | Last seen | Measured sweeps | First range / bearing | Min range (at) | Last range / bearing | Max speed |
|-------|-----------:|----------:|----------------:|----------------------|----------------|---------------------|----------:|
| track_001 | 0.00 | 11.95 | 240 | 3.3 m / -34 deg | 3.21 m (3.25) | 74.0 m / +29 deg | 15.2 m/s |
| track_002 | 0.00 | 4.80 | 96 | 20.4 m / +0 deg | 20.35 m (1.70) | 20.5 m / +0 deg | 11.9 m/s |
| track_003 | 0.00 | 3.30 | 62 | 38.0 m / -5 deg | 37.57 m (2.90) | 37.6 m / -5 deg | 11.8 m/s |
| track_004 | 0.00 | 4.55 | 89 | 26.8 m / -13 deg | 18.51 m (4.55) | 18.5 m / -16 deg | 10.2 m/s |
| track_005 | 0.90 | 11.95 | 222 | 9.9 m / -46 deg | 0.65 m (11.95) | 0.7 m / -107 deg | 10.9 m/s |
| track_006 | 6.15 | 11.95 | 112 | 21.0 m / +9 deg | 20.96 m (6.15) | 68.9 m / +33 deg | 12.2 m/s |
| track_007 | 6.35 | 11.95 | 113 | 14.3 m / -12 deg | 11.75 m (7.65) | 52.3 m / +30 deg | 10.3 m/s |
| track_008 | 8.10 | 11.90 | 53 | 41.1 m / +33 deg | 41.12 m (8.10) | 86.5 m / +27 deg | 12.5 m/s |

Bearing: positive = to A's right. Ranges are measured from the radar to the visible surface of the object.

## Plain-language reading

- t = 0.00 s: A started moving (already the case when first observed).
- t = 0.00 s: A pressed the accelerator (already the case when first observed).
- t = 0.00 s: A's radar started tracking track_002, which appeared in front of it.
- t = 0.00 s: A's radar started tracking track_003, which appeared in front of it.
- t = 0.00 s: A's radar started tracking track_001, which appeared on its left.
- t = 0.00 s: A's radar started tracking track_004, which appeared on its left.
- t = 0.00 s: A observed track_004 start closing in (already the case when first observed).
- t = 0.90 s: A's radar started tracking track_005, which appeared on its left.
- t = 0.90 s: A observed track_005 start closing in (already the case when first observed).
- t = 3.30 s: A's radar lost track_003 (its states are UNKNOWN from then on, not ended).
- t = 3.80 s: A observed track_005 stop closing in.
- t = 4.00 s: A switched on its left turn indicator.
- t = 4.55 s: A's radar lost track_004 (its states are UNKNOWN from then on, not ended).
- t = 4.80 s: A's radar lost track_002 (its states are UNKNOWN from then on, not ended).
- t = 5.45 s: A's time-to-contact with track_005 became critical.
- t = 5.50 s: A observed track_005 start closing in.
- t = 6.15 s: A's radar started tracking track_006, which appeared on its right.
- t = 6.20 s: A observed track_001 enter its forward path corridor.
- t = 6.20 s: A's time-to-contact with track_001 became critical.
- t = 6.35 s: A's radar started tracking track_007, which appeared on its left.
- t = 6.35 s: A observed track_007 start closing in (already the case when first observed).
- t = 7.30 s: A's collision sensor recorded a contact (peak impulse 389 N*s).
- t = 7.30 s: A's time-to-contact with track_005 stopped being critical.
- t = 7.35 s: A observed track_005 stop closing in.
- t = 7.35 s: A released the accelerator.
- t = 7.35 s: A started braking.
- t = 7.40 s: A started turning left.
- t = 7.45 s: A observed track_006 leave its forward path corridor.
- t = 7.50 s: A observed track_007 stop closing in.
- t = 7.65 s: A's time-to-contact with track_001 stopped being critical.
- t = 8.10 s: A's radar started tracking track_008, which appeared on its right.
- t = 8.25 s: A stopped turning left.
- t = 8.30 s: A stopped moving.
- t = 8.30 s: A came to a stop.
- t = 11.90 s: A's radar lost track_008 (its states are UNKNOWN from then on, not ended).
