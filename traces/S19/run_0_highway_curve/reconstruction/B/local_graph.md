# Local graph - vehicle B

All times are B's own local clock: `t_local` = seconds since B's first ego sample (raw clock reading 23.57733292505145 at `t_local` = 0). Only files under `vehicles/B/` were read; external objects are anonymous radar tracks.

- Local frame: origin = first ego position; x = first heading; y = to the right of the first heading (CARLA convention)
- Trace: 121 frames at 10 Hz in `local_trace.jsonl`, the last one at the recording end (11.95 s)
- Anonymous radar tracks: 7 (10 Hz samples in `local_tracks.jsonl`)
- Speed limit 90 km/h, supplied as incident context: known a priori, not perceived and not ground truth.
- Nodes: 32; edges: 53 (PRECEDES 39, SAME_TRACK 14)

## Nodes

| Id | Local time | Type | Actor | Subject | Source | Details |
|----|-----------:|------|-------|---------|--------|---------|
| B:e01 | 0.00 | MOVING_START | B | - | ego | active_at_first_observation=True |
| B:e02 | 0.00 | THROTTLE_START | B | - | controls | active_at_first_observation=True |
| B:e03 | 0.00 | TRACK_APPEARED_LEFT | B | track_001 | radar | initial_in_ego_path=False |
| B:e04 | 0.00 | TRACK_APPEARED_LEFT | B | track_002 | radar | initial_in_ego_path=False |
| B:e05 | 0.00 | TRACK_APPEARED_LEFT | B | track_003 | radar | initial_in_ego_path=False |
| B:e06 | 0.00 | TRACK_APPEARED_RIGHT | B | track_004 | radar | initial_in_ego_path=False |
| B:e07 | 0.00 | CLOSING_START | B | track_003 | radar | active_at_first_observation=True |
| B:e08 | 5.35 | CLOSING_END | B | track_003 | radar |  |
| B:e09 | 5.45 | TRACK_APPEARED_LEFT | B | track_005 | radar | initial_in_ego_path=False |
| B:e10 | 5.45 | CLOSING_START | B | track_005 | radar | active_at_first_observation=True |
| B:e11 | 5.50 | TURN_LEFT_START | B | - | ego |  |
| B:e12 | 5.65 | CLOSING_START | B | track_003 | radar |  |
| B:e13 | 5.95 | CRITICAL_TTC_START | B | track_005 | radar |  |
| B:e14 | 6.05 | EGO_PATH_ENTRY | B | track_002 | radar | occupancy_evidence=box; occupancy_margin_m=0.52; occupancy_sigma_m=0.30; cause=RECORDER_LATERAL; geometry=estimated_body |
| B:e15 | 6.35 | CLOSING_END | B | track_003 | radar |  |
| B:e16 | 6.50 | TURN_LEFT_END | B | - | ego |  |
| B:e17 | 6.55 | THROTTLE_END | B | - | controls |  |
| B:e18 | 6.55 | BRAKE_START | B | - | controls |  |
| B:e19 | 6.60 | TRACK_LOST | B | track_005 | radar |  |
| B:e20 | 7.40 | THROTTLE_START | B | - | controls |  |
| B:e21 | 7.50 | COLLISION | B | - | collision_sensor | peak_impulse=7479.37 |
| B:e22 | 7.50 | THROTTLE_END | B | - | controls |  |
| B:e23 | 7.70 | TRACK_LOST | B | track_001 | radar |  |
| B:e24 | 7.70 | TRACK_LOST | B | track_002 | radar |  |
| B:e25 | 8.75 | TRACK_APPEARED_LEFT | B | track_006 | radar | initial_in_ego_path=False |
| B:e26 | 9.00 | TRACK_LOST | B | track_006 | radar |  |
| B:e27 | 9.05 | MOVING_END | B | - | ego |  |
| B:e28 | 9.05 | STOP_START | B | - | ego |  |
| B:e29 | 9.50 | TRACK_APPEARED_RIGHT | B | track_007 | radar | initial_in_ego_path=False |
| B:e30 | 9.50 | CLOSING_START | B | track_007 | radar | active_at_first_observation=True |
| B:e31 | 10.35 | CLOSING_END | B | track_007 | radar |  |
| B:e32 | 11.15 | TRACK_LOST | B | track_003 | radar |  |

Events are state transitions; the quantities behind them (speed, pedals, ranges, TTC, relative motion, closest approach) are facts in `local_trace.jsonl`. Events with equal times are simultaneous at the recorder's resolution: PRECEDES links only different times. SAME_TRACK links a track's TRACK_APPEARED_* to every other event about the same local track (grouping only, no order).

## Edges

```
    B:e01 --PRECEDES--> B:e08
    B:e02 --PRECEDES--> B:e08
    B:e03 --PRECEDES--> B:e08
    B:e04 --PRECEDES--> B:e08
    B:e05 --PRECEDES--> B:e08
    B:e06 --PRECEDES--> B:e08
    B:e07 --PRECEDES--> B:e08
    B:e08 --PRECEDES--> B:e09
    B:e08 --PRECEDES--> B:e10
    B:e09 --PRECEDES--> B:e11
    B:e10 --PRECEDES--> B:e11
    B:e11 --PRECEDES--> B:e12
    B:e12 --PRECEDES--> B:e13
    B:e13 --PRECEDES--> B:e14
    B:e14 --PRECEDES--> B:e15
    B:e15 --PRECEDES--> B:e16
    B:e16 --PRECEDES--> B:e17
    B:e16 --PRECEDES--> B:e18
    B:e17 --PRECEDES--> B:e19
    B:e18 --PRECEDES--> B:e19
    B:e19 --PRECEDES--> B:e20
    B:e20 --PRECEDES--> B:e21
    B:e20 --PRECEDES--> B:e22
    B:e21 --PRECEDES--> B:e23
    B:e21 --PRECEDES--> B:e24
    B:e22 --PRECEDES--> B:e23
    B:e22 --PRECEDES--> B:e24
    B:e23 --PRECEDES--> B:e25
    B:e24 --PRECEDES--> B:e25
    B:e25 --PRECEDES--> B:e26
    B:e26 --PRECEDES--> B:e27
    B:e26 --PRECEDES--> B:e28
    B:e27 --PRECEDES--> B:e29
    B:e27 --PRECEDES--> B:e30
    B:e28 --PRECEDES--> B:e29
    B:e28 --PRECEDES--> B:e30
    B:e29 --PRECEDES--> B:e31
    B:e30 --PRECEDES--> B:e31
    B:e31 --PRECEDES--> B:e32
    B:e05 --SAME_TRACK--> B:e07
    B:e05 --SAME_TRACK--> B:e08
    B:e09 --SAME_TRACK--> B:e10
    B:e05 --SAME_TRACK--> B:e12
    B:e09 --SAME_TRACK--> B:e13
    B:e04 --SAME_TRACK--> B:e14
    B:e05 --SAME_TRACK--> B:e15
    B:e09 --SAME_TRACK--> B:e19
    B:e03 --SAME_TRACK--> B:e23
    B:e04 --SAME_TRACK--> B:e24
    B:e25 --SAME_TRACK--> B:e26
    B:e29 --SAME_TRACK--> B:e30
    B:e29 --SAME_TRACK--> B:e31
    B:e05 --SAME_TRACK--> B:e32
```

## Perceived state before each event

Each row is the state just BEFORE its events (none of them applied): events at one time are simultaneous and share it. True states are named, unknown ones end with `?`, false ones are omitted; a lost track's states are UNKNOWN, never ended. Facts: the trace frame at the time shown.

| Local time | Events | Perceived state just before | Facts at |
|-----------:|--------|-----------------------------|---------:|
| 0.00 | B:e01 MOVING_START<br>B:e02 THROTTLE_START<br>B:e03 TRACK_APPEARED_LEFT track_001<br>B:e04 TRACK_APPEARED_LEFT track_002<br>B:e05 TRACK_APPEARED_LEFT track_003<br>B:e06 TRACK_APPEARED_RIGHT track_004<br>B:e07 CLOSING_START track_003 | ego: not yet observed | - |
| 5.35 | B:e08 CLOSING_END track_003 | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: no active state<br>track_003: CLOSING<br>track_004: no active state | 5.30 |
| 5.45 | B:e09 TRACK_APPEARED_LEFT track_005<br>B:e10 CLOSING_START track_005 | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: no active state<br>track_003: no active state<br>track_004: no active state | 5.40 |
| 5.50 | B:e11 TURN_LEFT_START | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: no active state<br>track_003: no active state<br>track_004: no active state<br>track_005: CLOSING, CRITICAL_TTC? | 5.40 |
| 5.65 | B:e12 CLOSING_START track_003 | ego: MOVING, THROTTLE, TURN_LEFT<br>track_001: no active state<br>track_002: no active state<br>track_003: no active state<br>track_004: no active state<br>track_005: CLOSING, CRITICAL_TTC? | 5.60 |
| 5.95 | B:e13 CRITICAL_TTC_START track_005 | ego: MOVING, THROTTLE, TURN_LEFT<br>track_001: no active state<br>track_002: no active state<br>track_003: CLOSING<br>track_004: no active state<br>track_005: CLOSING, CRITICAL_TTC? | 5.90 |
| 6.05 | B:e14 EGO_PATH_ENTRY track_002 | ego: MOVING, THROTTLE, TURN_LEFT<br>track_001: no active state<br>track_002: no active state<br>track_003: CLOSING<br>track_004: no active state<br>track_005: CLOSING, CRITICAL_TTC | 6.00 |
| 6.35 | B:e15 CLOSING_END track_003 | ego: MOVING, THROTTLE, TURN_LEFT<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_003: CLOSING<br>track_004: no active state<br>track_005: CLOSING, CRITICAL_TTC | 6.30 |
| 6.50 | B:e16 TURN_LEFT_END | ego: MOVING, THROTTLE, TURN_LEFT<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_005: CLOSING, CRITICAL_TTC | 6.40 |
| 6.55 | B:e17 THROTTLE_END<br>B:e18 BRAKE_START | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_005: CLOSING, CRITICAL_TTC | 6.50 |
| 6.60 | B:e19 TRACK_LOST track_005 | ego: MOVING, BRAKE<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track_005: CLOSING, CRITICAL_TTC | 6.50 |
| 7.40 | B:e20 THROTTLE_START | ego: MOVING, BRAKE<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track lost, states UNKNOWN: track_005 | 7.30 |
| 7.50 | B:e21 COLLISION<br>B:e22 THROTTLE_END | ego: MOVING, BRAKE, THROTTLE<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track lost, states UNKNOWN: track_005 | 7.40 |
| 7.70 | B:e23 TRACK_LOST track_001<br>B:e24 TRACK_LOST track_002 | ego: MOVING, BRAKE<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_003: no active state<br>track_004: no active state<br>track lost, states UNKNOWN: track_005 | 7.60 |
| 8.75 | B:e25 TRACK_APPEARED_LEFT track_006 | ego: MOVING, BRAKE<br>track_003: no active state<br>track_004: no active state<br>track lost, states UNKNOWN: track_001, track_002, track_005 | 8.70 |
| 9.00 | B:e26 TRACK_LOST track_006 | ego: MOVING, BRAKE<br>track_003: no active state<br>track_004: no active state<br>track_006: CRITICAL_TTC?, CUT_IN_FROM_LEFT?, CUT_IN_FROM_RIGHT?<br>track lost, states UNKNOWN: track_001, track_002, track_005 | 8.90 |
| 9.05 | B:e27 MOVING_END<br>B:e28 STOP_START | ego: MOVING, BRAKE<br>track_003: no active state<br>track_004: no active state<br>track lost, states UNKNOWN: track_001, track_002, track_005, track_006 | 9.00 |
| 9.50 | B:e29 TRACK_APPEARED_RIGHT track_007<br>B:e30 CLOSING_START track_007 | ego: STOP, BRAKE<br>track_003: no active state<br>track_004: no active state<br>track lost, states UNKNOWN: track_001, track_002, track_005, track_006 | 9.40 |
| 10.35 | B:e31 CLOSING_END track_007 | ego: STOP, BRAKE<br>track_003: no active state<br>track_004: no active state<br>track_007: CLOSING<br>track lost, states UNKNOWN: track_001, track_002, track_005, track_006 | 10.30 |
| 11.15 | B:e32 TRACK_LOST track_003 | ego: STOP, BRAKE<br>track_003: no active state<br>track_004: no active state<br>track_007: no active state<br>track lost, states UNKNOWN: track_001, track_002, track_005, track_006 | 11.10 |

## States still active when observation ended

- CLOSING of track_005, since B:e10 (t = 5.45 s); the track was lost at 6.60 s
- CRITICAL_TTC of track_005, since B:e13 (t = 5.95 s); the track was lost at 6.60 s
- EGO_PATH of track_002, since B:e14 (t = 6.05 s); the track was lost at 7.70 s
- BRAKE, since B:e18 (t = 6.55 s)
- STOP, since B:e28 (t = 9.05 s)

## Tracks lost

- track_005 at 6.60 s (B:e19): CLOSING, CRITICAL_TTC were true; they are UNKNOWN afterwards (no END recorded)
- track_002 at 7.70 s (B:e24): IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)
- lost with no state active: track_001, track_006, track_003

## Temporal safety relations

Order of each track's cut-in, critical TTC and path entry and of the collision report, in local time. Temporal properties only, not causes.

- track_002: EGO_PATH_ENTRY 6.05, no critical TTC
- track_005: CRITICAL_TTC_START 5.95, COLLISION 7.50 (+1.55 s)

## Sign detection windows

- none

An END means this recorder stopped detecting the sign, not that its obligation ended.

## Anonymous radar tracks

| Track | First seen | Last seen | Measured sweeps | First range / bearing | Min range (at) | Last range / bearing | Max speed |
|-------|-----------:|----------:|----------------:|----------------------|----------------|---------------------|----------:|
| track_001 | 0.00 | 7.70 | 144 | 18.5 m / -21 deg | 18.51 m (0.00) | 71.1 m / -10 deg | 23.9 m/s |
| track_002 | 0.00 | 7.70 | 105 | 59.5 m / -11 deg | 59.48 m (0.00) | 80.9 m / -9 deg | 20.1 m/s |
| track_003 | 0.00 | 11.15 | 212 | 23.5 m / -156 deg | 4.52 m (5.95) | 82.2 m / -14 deg | 23.7 m/s |
| track_004 | 0.00 | 11.95 | 240 | 1.6 m / +100 deg | 1.53 m (0.45) | 59.6 m / -2 deg | 17.9 m/s |
| track_005 | 5.45 | 6.60 | 24 | 10.6 m / -155 deg | 7.09 m (6.60) | 7.1 m / -154 deg | 20.2 m/s |
| track_006 | 8.75 | 9.00 | 5 | 85.4 m / -15 deg | 85.38 m (8.75) | 90.2 m / -16 deg | 23.9 m/s |
| track_007 | 9.50 | 11.95 | 50 | 17.7 m / +160 deg | 5.16 m (10.50) | 23.8 m / +12 deg | 17.6 m/s |

Bearing: positive = to B's right. Ranges are measured from the radar to the visible surface of the object.

## Plain-language reading

- t = 0.00 s: B started moving (already the case when first observed).
- t = 0.00 s: B pressed the accelerator (already the case when first observed).
- t = 0.00 s: B's radar started tracking track_001, which appeared on its left.
- t = 0.00 s: B's radar started tracking track_002, which appeared on its left.
- t = 0.00 s: B's radar started tracking track_003, which appeared on its left.
- t = 0.00 s: B's radar started tracking track_004, which appeared on its right.
- t = 0.00 s: B observed track_003 start closing in (already the case when first observed).
- t = 5.35 s: B observed track_003 stop closing in.
- t = 5.45 s: B's radar started tracking track_005, which appeared on its left.
- t = 5.45 s: B observed track_005 start closing in (already the case when first observed).
- t = 5.50 s: B started turning left.
- t = 5.65 s: B observed track_003 start closing in.
- t = 5.95 s: B's time-to-contact with track_005 became critical.
- t = 6.05 s: B observed track_002 enter its forward path corridor.
- t = 6.35 s: B observed track_003 stop closing in.
- t = 6.50 s: B stopped turning left.
- t = 6.55 s: B released the accelerator.
- t = 6.55 s: B started braking.
- t = 6.60 s: B's radar lost track_005 (its states are UNKNOWN from then on, not ended).
- t = 7.40 s: B pressed the accelerator.
- t = 7.50 s: B's collision sensor recorded a contact (peak impulse 7479 N*s).
- t = 7.50 s: B released the accelerator.
- t = 7.70 s: B's radar lost track_001 (its states are UNKNOWN from then on, not ended).
- t = 7.70 s: B's radar lost track_002 (its states are UNKNOWN from then on, not ended).
- t = 8.75 s: B's radar started tracking track_006, which appeared on its left.
- t = 9.00 s: B's radar lost track_006 (its states are UNKNOWN from then on, not ended).
- t = 9.05 s: B stopped moving.
- t = 9.05 s: B came to a stop.
- t = 9.50 s: B's radar started tracking track_007, which appeared on its right.
- t = 9.50 s: B observed track_007 start closing in (already the case when first observed).
- t = 10.35 s: B observed track_007 stop closing in.
- t = 11.15 s: B's radar lost track_003 (its states are UNKNOWN from then on, not ended).
