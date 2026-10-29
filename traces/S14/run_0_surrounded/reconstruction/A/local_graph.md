# Local graph - vehicle A

All times are A's own local clock: `t_local` = seconds since A's first ego sample (raw clock reading 2084.0085746981204 at `t_local` = 0). Only files under `vehicles/A/` were read; external objects are anonymous radar tracks.

- Local frame: origin = first ego position; x = first heading; y = to the right of the first heading (CARLA convention)
- Trace: 121 frames at 10 Hz in `local_trace.jsonl`, the last one at the recording end (11.95 s)
- Anonymous radar tracks: 9 (10 Hz samples in `local_tracks.jsonl`)
- Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.
- Nodes: 29; edges: 49 (PRECEDES 33, SAME_TRACK 16)

## Nodes

| Id | Local time | Type | Actor | Subject | Source | Details |
|----|-----------:|------|-------|---------|--------|---------|
| A:e01 | 0.00 | MOVING_START | A | - | ego | active_at_first_observation=True |
| A:e02 | 0.00 | THROTTLE_START | A | - | controls | active_at_first_observation=True |
| A:e03 | 0.00 | TRACK_APPEARED_FRONT | A | track_001 | radar | initial_in_ego_path=True |
| A:e04 | 0.00 | TRACK_APPEARED_LEFT | A | track_002 | radar | initial_in_ego_path=False |
| A:e05 | 0.00 | TRACK_APPEARED_LEFT | A | track_003 | radar | initial_in_ego_path=False |
| A:e06 | 0.05 | TRACK_APPEARED_LEFT | A | track_004 | radar | initial_in_ego_path=False |
| A:e07 | 0.50 | CRITICAL_TTC_START | A | track_001 | radar |  |
| A:e08 | 6.35 | CRITICAL_TTC_START | A | track_003 | radar |  |
| A:e09 | 6.95 | CLOSING_START | A | track_003 | radar |  |
| A:e10 | 7.05 | TRACK_APPEARED_FRONT | A | track_005 | radar | initial_in_ego_path=False |
| A:e11 | 7.40 | TRACK_APPEARED_RIGHT | A | track_006 | radar | initial_in_ego_path=True |
| A:e12 | 7.40 | EGO_PATH_ENTRY | A | track_004 | radar | occupancy_evidence=box; occupancy_margin_m=0.56; occupancy_sigma_m=0.27; cause=MUTUAL_LATERAL; geometry=estimated_body |
| A:e13 | 7.40 | CRITICAL_TTC_START | A | track_004 | radar |  |
| A:e14 | 7.50 | EGO_PATH_ENTRY | A | track_005 | radar | occupancy_evidence=box; occupancy_margin_m=0.67; occupancy_sigma_m=0.34; cause=MUTUAL_LATERAL; geometry=estimated_body |
| A:e15 | 7.65 | TRACK_APPEARED_RIGHT | A | track_007 | radar | initial_in_ego_path=True |
| A:e16 | 7.70 | TRACK_LOST | A | track_005 | radar |  |
| A:e17 | 7.75 | COLLISION | A | - | collision_sensor | peak_impulse=255.03 |
| A:e18 | 7.75 | CRITICAL_TTC_END | A | track_003 | radar |  |
| A:e19 | 7.80 | THROTTLE_END | A | - | controls |  |
| A:e20 | 7.80 | EGO_PATH_ENTRY | A | track_003 | radar | occupancy_evidence=box; occupancy_margin_m=0.45; occupancy_sigma_m=0.26; cause=RECORDER_LATERAL; geometry=estimated_body |
| A:e21 | 7.85 | CLOSING_END | A | track_003 | radar |  |
| A:e22 | 8.45 | TRACK_APPEARED_LEFT | A | track_008 | radar | initial_in_ego_path=False |
| A:e23 | 9.00 | CRITICAL_TTC_END | A | track_001 | radar |  |
| A:e24 | 9.50 | TRACK_APPEARED_LEFT | A | track_009 | radar | initial_in_ego_path=True |
| A:e25 | 9.85 | EGO_PATH_EXIT | A | track_006 | radar | occupancy_evidence=box; occupancy_margin_m=-0.49; occupancy_sigma_m=0.28; cause=MUTUAL_LATERAL; geometry=estimated_body |
| A:e26 | 10.15 | CRITICAL_TTC_START | A | track_007 | radar |  |
| A:e27 | 10.45 | CRITICAL_TTC_START | A | track_001 | radar |  |
| A:e28 | 11.15 | TRACK_LOST | A | track_009 | radar |  |
| A:e29 | 11.35 | EGO_PATH_ENTRY | A | track_006 | radar | occupancy_evidence=returns; occupancy_margin_m=0.49; occupancy_sigma_m=0.25; cause=MUTUAL_LATERAL; geometry=estimated_body |

Events are state transitions; the quantities behind them (speed, pedals, ranges, TTC, relative motion, closest approach) are facts in `local_trace.jsonl`. Events with equal times are simultaneous at the recorder's resolution: PRECEDES links only different times. SAME_TRACK links a track's TRACK_APPEARED_* to every other event about the same local track (grouping only, no order).

## Edges

```
    A:e01 --PRECEDES--> A:e06
    A:e02 --PRECEDES--> A:e06
    A:e03 --PRECEDES--> A:e06
    A:e04 --PRECEDES--> A:e06
    A:e05 --PRECEDES--> A:e06
    A:e06 --PRECEDES--> A:e07
    A:e07 --PRECEDES--> A:e08
    A:e08 --PRECEDES--> A:e09
    A:e09 --PRECEDES--> A:e10
    A:e10 --PRECEDES--> A:e11
    A:e10 --PRECEDES--> A:e12
    A:e10 --PRECEDES--> A:e13
    A:e11 --PRECEDES--> A:e14
    A:e12 --PRECEDES--> A:e14
    A:e13 --PRECEDES--> A:e14
    A:e14 --PRECEDES--> A:e15
    A:e15 --PRECEDES--> A:e16
    A:e16 --PRECEDES--> A:e17
    A:e16 --PRECEDES--> A:e18
    A:e17 --PRECEDES--> A:e19
    A:e17 --PRECEDES--> A:e20
    A:e18 --PRECEDES--> A:e19
    A:e18 --PRECEDES--> A:e20
    A:e19 --PRECEDES--> A:e21
    A:e20 --PRECEDES--> A:e21
    A:e21 --PRECEDES--> A:e22
    A:e22 --PRECEDES--> A:e23
    A:e23 --PRECEDES--> A:e24
    A:e24 --PRECEDES--> A:e25
    A:e25 --PRECEDES--> A:e26
    A:e26 --PRECEDES--> A:e27
    A:e27 --PRECEDES--> A:e28
    A:e28 --PRECEDES--> A:e29
    A:e03 --SAME_TRACK--> A:e07
    A:e05 --SAME_TRACK--> A:e08
    A:e05 --SAME_TRACK--> A:e09
    A:e06 --SAME_TRACK--> A:e12
    A:e06 --SAME_TRACK--> A:e13
    A:e10 --SAME_TRACK--> A:e14
    A:e10 --SAME_TRACK--> A:e16
    A:e05 --SAME_TRACK--> A:e18
    A:e05 --SAME_TRACK--> A:e20
    A:e05 --SAME_TRACK--> A:e21
    A:e03 --SAME_TRACK--> A:e23
    A:e11 --SAME_TRACK--> A:e25
    A:e15 --SAME_TRACK--> A:e26
    A:e03 --SAME_TRACK--> A:e27
    A:e24 --SAME_TRACK--> A:e28
    A:e11 --SAME_TRACK--> A:e29
```

## Perceived state before each event

Each row is the state just BEFORE its events (none of them applied): events at one time are simultaneous and share it. True states are named, unknown ones end with `?`, false ones are omitted; a lost track's states are UNKNOWN, never ended. Facts: the trace frame at the time shown.

| Local time | Events | Perceived state just before | Facts at |
|-----------:|--------|-----------------------------|---------:|
| 0.00 | A:e01 MOVING_START<br>A:e02 THROTTLE_START<br>A:e03 TRACK_APPEARED_FRONT track_001<br>A:e04 TRACK_APPEARED_LEFT track_002<br>A:e05 TRACK_APPEARED_LEFT track_003 | ego: not yet observed | - |
| 0.05 | A:e06 TRACK_APPEARED_LEFT track_004 | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH, CRITICAL_TTC?<br>track_002: CRITICAL_TTC?<br>track_003: CRITICAL_TTC? | 0.00 |
| 0.50 | A:e07 CRITICAL_TTC_START track_001 | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH, CRITICAL_TTC?<br>track_002: CRITICAL_TTC?<br>track_003: CRITICAL_TTC?<br>track_004: CRITICAL_TTC? | 0.40 |
| 6.35 | A:e08 CRITICAL_TTC_START track_003 | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: no active state<br>track_004: no active state | 6.30 |
| 6.95 | A:e09 CLOSING_START track_003 | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: CRITICAL_TTC<br>track_004: no active state | 6.90 |
| 7.05 | A:e10 TRACK_APPEARED_FRONT track_005 | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: CLOSING, CRITICAL_TTC<br>track_004: no active state | 7.00 |
| 7.40 | A:e11 TRACK_APPEARED_RIGHT track_006<br>A:e12 EGO_PATH_ENTRY track_004<br>A:e13 CRITICAL_TTC_START track_004 | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: CLOSING, CRITICAL_TTC<br>track_004: no active state<br>track_005: CRITICAL_TTC? | 7.30 |
| 7.50 | A:e14 EGO_PATH_ENTRY track_005 | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: CLOSING, CRITICAL_TTC<br>track_004: CRITICAL_TTC, IN_EGO_PATH<br>track_005: CRITICAL_TTC?<br>track_006: IN_EGO_PATH, CRITICAL_TTC? | 7.40 |
| 7.65 | A:e15 TRACK_APPEARED_RIGHT track_007 | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: CLOSING, CRITICAL_TTC<br>track_004: CRITICAL_TTC, IN_EGO_PATH<br>track_005: IN_EGO_PATH<br>track_006: IN_EGO_PATH, CRITICAL_TTC? | 7.60 |
| 7.70 | A:e16 TRACK_LOST track_005 | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: CLOSING, CRITICAL_TTC<br>track_004: CRITICAL_TTC, IN_EGO_PATH<br>track_005: IN_EGO_PATH<br>track_006: IN_EGO_PATH, CRITICAL_TTC?<br>track_007: IN_EGO_PATH, CRITICAL_TTC? | 7.60 |
| 7.75 | A:e17 COLLISION<br>A:e18 CRITICAL_TTC_END track_003 | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: CLOSING, CRITICAL_TTC<br>track_004: CRITICAL_TTC, IN_EGO_PATH<br>track_006: IN_EGO_PATH, CRITICAL_TTC?<br>track_007: IN_EGO_PATH, CRITICAL_TTC?<br>track lost, states UNKNOWN: track_005 | 7.70 |
| 7.80 | A:e19 THROTTLE_END<br>A:e20 EGO_PATH_ENTRY track_003 | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: CLOSING<br>track_004: CRITICAL_TTC, IN_EGO_PATH<br>track_006: IN_EGO_PATH, CRITICAL_TTC?<br>track_007: IN_EGO_PATH, CRITICAL_TTC?<br>track lost, states UNKNOWN: track_005 | 7.70 |
| 7.85 | A:e21 CLOSING_END track_003 | ego: MOVING<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: CLOSING, IN_EGO_PATH<br>track_004: CRITICAL_TTC, IN_EGO_PATH<br>track_006: IN_EGO_PATH, CRITICAL_TTC?<br>track_007: IN_EGO_PATH, CRITICAL_TTC?<br>track lost, states UNKNOWN: track_005 | 7.80 |
| 8.45 | A:e22 TRACK_APPEARED_LEFT track_008 | ego: MOVING<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: IN_EGO_PATH<br>track_004: CRITICAL_TTC, IN_EGO_PATH<br>track_006: IN_EGO_PATH<br>track_007: IN_EGO_PATH<br>track lost, states UNKNOWN: track_005 | 8.40 |
| 9.00 | A:e23 CRITICAL_TTC_END track_001 | ego: MOVING<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: IN_EGO_PATH<br>track_004: CRITICAL_TTC, IN_EGO_PATH<br>track_006: IN_EGO_PATH<br>track_007: IN_EGO_PATH<br>track_008: no active state<br>track lost, states UNKNOWN: track_005 | 8.90 |
| 9.50 | A:e24 TRACK_APPEARED_LEFT track_009 | ego: MOVING<br>track_001: IN_EGO_PATH<br>track_002: no active state<br>track_003: IN_EGO_PATH<br>track_004: CRITICAL_TTC, IN_EGO_PATH<br>track_006: IN_EGO_PATH<br>track_007: IN_EGO_PATH<br>track_008: no active state<br>track lost, states UNKNOWN: track_005 | 9.40 |
| 9.85 | A:e25 EGO_PATH_EXIT track_006 | ego: MOVING<br>track_001: IN_EGO_PATH<br>track_002: no active state<br>track_003: IN_EGO_PATH<br>track_004: CRITICAL_TTC, IN_EGO_PATH<br>track_006: IN_EGO_PATH<br>track_007: IN_EGO_PATH<br>track_008: no active state<br>track_009: IN_EGO_PATH, CRITICAL_TTC?<br>track lost, states UNKNOWN: track_005 | 9.80 |
| 10.15 | A:e26 CRITICAL_TTC_START track_007 | ego: MOVING<br>track_001: IN_EGO_PATH<br>track_002: no active state<br>track_003: IN_EGO_PATH<br>track_004: CRITICAL_TTC, IN_EGO_PATH<br>track_006: no active state<br>track_007: IN_EGO_PATH<br>track_008: no active state<br>track_009: IN_EGO_PATH<br>track lost, states UNKNOWN: track_005 | 10.10 |
| 10.45 | A:e27 CRITICAL_TTC_START track_001 | ego: MOVING<br>track_001: IN_EGO_PATH<br>track_002: no active state<br>track_003: IN_EGO_PATH<br>track_004: CRITICAL_TTC, IN_EGO_PATH<br>track_006: no active state<br>track_007: CRITICAL_TTC, IN_EGO_PATH<br>track_008: no active state<br>track_009: IN_EGO_PATH<br>track lost, states UNKNOWN: track_005 | 10.40 |
| 11.15 | A:e28 TRACK_LOST track_009 | ego: MOVING<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: IN_EGO_PATH<br>track_004: CRITICAL_TTC, IN_EGO_PATH<br>track_006: no active state<br>track_007: CRITICAL_TTC, IN_EGO_PATH<br>track_008: no active state<br>track_009: IN_EGO_PATH<br>track lost, states UNKNOWN: track_005 | 11.10 |
| 11.35 | A:e29 EGO_PATH_ENTRY track_006 | ego: MOVING<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state<br>track_003: IN_EGO_PATH<br>track_004: CRITICAL_TTC, IN_EGO_PATH<br>track_006: no active state<br>track_007: CRITICAL_TTC, IN_EGO_PATH<br>track_008: no active state<br>track lost, states UNKNOWN: track_005, track_009 | 11.30 |

## States still active when observation ended

- MOVING, since A:e01 (t = 0.00 s)
- EGO_PATH of track_004, since A:e12 (t = 7.40 s)
- CRITICAL_TTC of track_004, since A:e13 (t = 7.40 s)
- EGO_PATH of track_005, since A:e14 (t = 7.50 s); the track was lost at 7.70 s
- EGO_PATH of track_003, since A:e20 (t = 7.80 s)
- CRITICAL_TTC of track_007, since A:e26 (t = 10.15 s)
- CRITICAL_TTC of track_001, since A:e27 (t = 10.45 s)
- EGO_PATH of track_006, since A:e29 (t = 11.35 s)

## Tracks lost

- track_005 at 7.70 s (A:e16): IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)
- track_009 at 11.15 s (A:e28): IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)

## Temporal safety relations

Order of each track's cut-in, critical TTC and path entry and of the collision report, in local time. Temporal properties only, not causes.

- track_001: CRITICAL_TTC_START 0.50, COLLISION 7.75 (+7.25 s)
- track_003: CRITICAL_TTC_START 6.35, COLLISION 7.75 (+1.40 s); EGO_PATH_ENTRY 7.80 after critical TTC (+1.45 s)
- track_004: CRITICAL_TTC_START 7.40, COLLISION 7.75 (+0.35 s); EGO_PATH_ENTRY 7.40 together with critical TTC (+0.00 s)
- track_005: EGO_PATH_ENTRY 7.50, no critical TTC
- track_006: EGO_PATH_ENTRY 11.35, no critical TTC
- track_007: CRITICAL_TTC_START 10.15

## Sign detection windows

- none

An END means this recorder stopped detecting the sign, not that its obligation ended.

## Anonymous radar tracks

| Track | First seen | Last seen | Measured sweeps | First range / bearing | Min range (at) | Last range / bearing | Max speed |
|-------|-----------:|----------:|----------------:|----------------------|----------------|---------------------|----------:|
| track_001 | 0.00 | 11.95 | 240 | 3.0 m / -0 deg | 1.53 m (11.95) | 1.5 m / +4 deg | 12.1 m/s |
| track_002 | 0.00 | 11.95 | 240 | 12.3 m / -27 deg | 10.92 m (9.85) | 12.4 m / -32 deg | 12.2 m/s |
| track_003 | 0.00 | 11.95 | 240 | 3.0 m / -134 deg | 0.04 m (11.95) | 0.0 m / -88 deg | 12.4 m/s |
| track_004 | 0.05 | 11.95 | 239 | 11.1 m / -15 deg | 9.56 m (10.55) | 10.1 m / -19 deg | 12.3 m/s |
| track_005 | 7.05 | 7.70 | 14 | 42.0 m / -1 deg | 41.99 m (7.70) | 42.0 m / +5 deg | 12.5 m/s |
| track_006 | 7.40 | 11.95 | 89 | 26.4 m / +8 deg | 24.90 m (11.75) | 24.9 m / -11 deg | 12.1 m/s |
| track_007 | 7.65 | 11.95 | 86 | 11.2 m / +12 deg | 9.88 m (11.90) | 9.9 m / -6 deg | 12.0 m/s |
| track_008 | 8.45 | 11.95 | 66 | 27.0 m / -9 deg | 26.95 m (9.20) | 28.4 m / -26 deg | 12.1 m/s |
| track_009 | 9.50 | 11.15 | 26 | 41.9 m / -7 deg | 41.71 m (10.50) | 41.8 m / -16 deg | 12.0 m/s |

Bearing: positive = to A's right. Ranges are measured from the radar to the visible surface of the object.

## Plain-language reading

- t = 0.00 s: A started moving (already the case when first observed).
- t = 0.00 s: A pressed the accelerator (already the case when first observed).
- t = 0.00 s: A's radar started tracking track_001, which appeared in front of it.
- t = 0.00 s: A's radar started tracking track_002, which appeared on its left.
- t = 0.00 s: A's radar started tracking track_003, which appeared on its left.
- t = 0.05 s: A's radar started tracking track_004, which appeared on its left.
- t = 0.50 s: A's time-to-contact with track_001 became critical.
- t = 6.35 s: A's time-to-contact with track_003 became critical.
- t = 6.95 s: A observed track_003 start closing in.
- t = 7.05 s: A's radar started tracking track_005, which appeared in front of it.
- t = 7.40 s: A's radar started tracking track_006, which appeared on its right.
- t = 7.40 s: A observed track_004 enter its forward path corridor.
- t = 7.40 s: A's time-to-contact with track_004 became critical.
- t = 7.50 s: A observed track_005 enter its forward path corridor.
- t = 7.65 s: A's radar started tracking track_007, which appeared on its right.
- t = 7.70 s: A's radar lost track_005 (its states are UNKNOWN from then on, not ended).
- t = 7.75 s: A's collision sensor recorded a contact (peak impulse 255 N*s).
- t = 7.75 s: A's time-to-contact with track_003 stopped being critical.
- t = 7.80 s: A released the accelerator.
- t = 7.80 s: A observed track_003 enter its forward path corridor.
- t = 7.85 s: A observed track_003 stop closing in.
- t = 8.45 s: A's radar started tracking track_008, which appeared on its left.
- t = 9.00 s: A's time-to-contact with track_001 stopped being critical.
- t = 9.50 s: A's radar started tracking track_009, which appeared on its left.
- t = 9.85 s: A observed track_006 leave its forward path corridor.
- t = 10.15 s: A's time-to-contact with track_007 became critical.
- t = 10.45 s: A's time-to-contact with track_001 became critical.
- t = 11.15 s: A's radar lost track_009 (its states are UNKNOWN from then on, not ended).
- t = 11.35 s: A observed track_006 enter its forward path corridor.
