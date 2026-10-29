# Local graph - vehicle A

All times are A's own local clock: `t_local` = seconds since A's first ego sample (raw clock reading 2022.2515310794115 at `t_local` = 0). Only files under `vehicles/A/` were read; external objects are anonymous radar tracks.

- Local frame: origin = first ego position; x = first heading; y = to the right of the first heading (CARLA convention)
- Trace: 111 frames at 10 Hz in `local_trace.jsonl`, the last one at the recording end (10.95 s)
- Anonymous radar tracks: 2 (10 Hz samples in `local_tracks.jsonl`)
- Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.
- Nodes: 21; edges: 38 (PRECEDES 26, SAME_TRACK 12)

## Nodes

| Id | Local time | Type | Actor | Subject | Source | Details |
|----|-----------:|------|-------|---------|--------|---------|
| A:e01 | 0.00 | MOVING_START | A | - | ego | active_at_first_observation=True |
| A:e02 | 0.00 | THROTTLE_START | A | - | controls | active_at_first_observation=True |
| A:e03 | 0.00 | TRACK_APPEARED_LEFT | A | track_002 | radar | initial_in_ego_path=False |
| A:e04 | 0.00 | TRACK_APPEARED_RIGHT | A | track_001 | radar | initial_in_ego_path=False |
| A:e05 | 0.00 | CLOSING_START | A | track_001 | radar | active_at_first_observation=True |
| A:e06 | 2.30 | CUT_IN_FROM_RIGHT_START | A | track_001 | radar | geometry=estimated_body |
| A:e07 | 2.50 | CRITICAL_TTC_START | A | track_001 | radar |  |
| A:e08 | 2.85 | EGO_PATH_ENTRY | A | track_001 | radar | occupancy_evidence=box; occupancy_margin_m=0.51; occupancy_sigma_m=0.26; cause=TARGET_LATERAL; geometry=estimated_body |
| A:e09 | 3.85 | CRITICAL_TTC_START | A | track_002 | radar |  |
| A:e10 | 4.25 | CLOSING_START | A | track_002 | radar |  |
| A:e11 | 4.55 | CLOSING_END | A | track_001 | radar |  |
| A:e12 | 4.95 | COLLISION | A | - | collision_sensor | peak_impulse=1576.92; merged_bursts=[[5.05, 263.76], [5.65, 13.44]] |
| A:e13 | 4.95 | CRITICAL_TTC_END | A | track_002 | radar |  |
| A:e14 | 4.95 | CLOSING_END | A | track_002 | radar |  |
| A:e15 | 5.00 | THROTTLE_END | A | - | controls |  |
| A:e16 | 5.00 | BRAKE_START | A | - | controls |  |
| A:e17 | 5.35 | CUT_IN_FROM_RIGHT_END | A | track_001 | radar | geometry=estimated_body |
| A:e18 | 5.45 | CRITICAL_TTC_END | A | track_001 | radar |  |
| A:e19 | 6.05 | MOVING_END | A | - | ego |  |
| A:e20 | 6.05 | STOP_START | A | - | ego |  |
| A:e21 | 7.45 | TRACK_LOST | A | track_001 | radar |  |

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
    A:e11 --PRECEDES--> A:e12
    A:e11 --PRECEDES--> A:e13
    A:e11 --PRECEDES--> A:e14
    A:e12 --PRECEDES--> A:e15
    A:e12 --PRECEDES--> A:e16
    A:e13 --PRECEDES--> A:e15
    A:e13 --PRECEDES--> A:e16
    A:e14 --PRECEDES--> A:e15
    A:e14 --PRECEDES--> A:e16
    A:e15 --PRECEDES--> A:e17
    A:e16 --PRECEDES--> A:e17
    A:e17 --PRECEDES--> A:e18
    A:e18 --PRECEDES--> A:e19
    A:e18 --PRECEDES--> A:e20
    A:e19 --PRECEDES--> A:e21
    A:e20 --PRECEDES--> A:e21
    A:e04 --SAME_TRACK--> A:e05
    A:e04 --SAME_TRACK--> A:e06
    A:e04 --SAME_TRACK--> A:e07
    A:e04 --SAME_TRACK--> A:e08
    A:e03 --SAME_TRACK--> A:e09
    A:e03 --SAME_TRACK--> A:e10
    A:e04 --SAME_TRACK--> A:e11
    A:e03 --SAME_TRACK--> A:e13
    A:e03 --SAME_TRACK--> A:e14
    A:e04 --SAME_TRACK--> A:e17
    A:e04 --SAME_TRACK--> A:e18
    A:e04 --SAME_TRACK--> A:e21
```

## Perceived state before each event

Each row is the state just BEFORE its events (none of them applied): events at one time are simultaneous and share it. True states are named, unknown ones end with `?`, false ones are omitted; a lost track's states are UNKNOWN, never ended. Facts: the trace frame at the time shown.

| Local time | Events | Perceived state just before | Facts at |
|-----------:|--------|-----------------------------|---------:|
| 0.00 | A:e01 MOVING_START<br>A:e02 THROTTLE_START<br>A:e03 TRACK_APPEARED_LEFT track_002<br>A:e04 TRACK_APPEARED_RIGHT track_001<br>A:e05 CLOSING_START track_001 | ego: not yet observed | - |
| 2.30 | A:e06 CUT_IN_FROM_RIGHT_START track_001 | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>track_002: no active state | 2.20 |
| 2.50 | A:e07 CRITICAL_TTC_START track_001 | ego: MOVING, THROTTLE<br>track_001: CLOSING, CUT_IN_FROM_RIGHT<br>track_002: no active state | 2.40 |
| 2.85 | A:e08 EGO_PATH_ENTRY track_001 | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC, CUT_IN_FROM_RIGHT<br>track_002: no active state | 2.80 |
| 3.85 | A:e09 CRITICAL_TTC_START track_002 | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH, CUT_IN_FROM_RIGHT<br>track_002: no active state | 3.80 |
| 4.25 | A:e10 CLOSING_START track_002 | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH, CUT_IN_FROM_RIGHT<br>track_002: CRITICAL_TTC | 4.20 |
| 4.55 | A:e11 CLOSING_END track_001 | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH, CUT_IN_FROM_RIGHT<br>track_002: CLOSING, CRITICAL_TTC | 4.50 |
| 4.95 | A:e12 COLLISION<br>A:e13 CRITICAL_TTC_END track_002<br>A:e14 CLOSING_END track_002 | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH, CUT_IN_FROM_RIGHT<br>track_002: CLOSING, CRITICAL_TTC | 4.90 |
| 5.00 | A:e15 THROTTLE_END<br>A:e16 BRAKE_START | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC, IN_EGO_PATH, CUT_IN_FROM_RIGHT<br>track_002: no active state | 4.90 |
| 5.35 | A:e17 CUT_IN_FROM_RIGHT_END track_001 | ego: MOVING, BRAKE<br>track_001: CRITICAL_TTC, IN_EGO_PATH, CUT_IN_FROM_RIGHT<br>track_002: no active state | 5.30 |
| 5.45 | A:e18 CRITICAL_TTC_END track_001 | ego: MOVING, BRAKE<br>track_001: CRITICAL_TTC, IN_EGO_PATH<br>track_002: no active state | 5.40 |
| 6.05 | A:e19 MOVING_END<br>A:e20 STOP_START | ego: MOVING, BRAKE<br>track_001: IN_EGO_PATH<br>track_002: no active state | 6.00 |
| 7.45 | A:e21 TRACK_LOST track_001 | ego: STOP, BRAKE<br>track_001: IN_EGO_PATH<br>track_002: no active state | 7.40 |

## States still active when observation ended

- EGO_PATH of track_001, since A:e08 (t = 2.85 s); the track was lost at 7.45 s
- BRAKE, since A:e16 (t = 5.00 s)
- STOP, since A:e20 (t = 6.05 s)

## Tracks lost

- track_001 at 7.45 s (A:e21): IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)

## Temporal safety relations

Order of each track's cut-in, critical TTC and path entry and of the collision report, in local time. Temporal properties only, not causes.

- track_001: cut-in started before critical TTC: CUT_IN_FROM_RIGHT_START 2.30 < CRITICAL_TTC_START 2.50 (+0.20 s) < COLLISION 4.95 (+2.45 s); EGO_PATH_ENTRY 2.85 after critical TTC (+0.35 s)
- track_002: CRITICAL_TTC_START 3.85, COLLISION 4.95 (+1.10 s)

## Sign detection windows

- none

An END means this recorder stopped detecting the sign, not that its obligation ended.

## Anonymous radar tracks

| Track | First seen | Last seen | Measured sweeps | First range / bearing | Min range (at) | Last range / bearing | Max speed |
|-------|-----------:|----------:|----------------:|----------------------|----------------|---------------------|----------:|
| track_001 | 0.00 | 7.45 | 146 | 6.9 m / +20 deg | 1.89 m (4.35) | 20.0 m / +16 deg | 13.0 m/s |
| track_002 | 0.00 | 10.95 | 220 | 5.5 m / -148 deg | 0.32 m (5.40) | 0.9 m / -114 deg | 13.0 m/s |

Bearing: positive = to A's right. Ranges are measured from the radar to the visible surface of the object.

## Plain-language reading

- t = 0.00 s: A started moving (already the case when first observed).
- t = 0.00 s: A pressed the accelerator (already the case when first observed).
- t = 0.00 s: A's radar started tracking track_002, which appeared on its left.
- t = 0.00 s: A's radar started tracking track_001, which appeared on its right.
- t = 0.00 s: A observed track_001 start closing in (already the case when first observed).
- t = 2.30 s: A observed track_001 cutting in from the right.
- t = 2.50 s: A's time-to-contact with track_001 became critical.
- t = 2.85 s: A observed track_001 enter its forward path corridor.
- t = 3.85 s: A's time-to-contact with track_002 became critical.
- t = 4.25 s: A observed track_002 start closing in.
- t = 4.55 s: A observed track_001 stop closing in.
- t = 4.95 s: A's collision sensor recorded a contact (peak impulse 1577 N*s).
- t = 4.95 s: A's time-to-contact with track_002 stopped being critical.
- t = 4.95 s: A observed track_002 stop closing in.
- t = 5.00 s: A released the accelerator.
- t = 5.00 s: A started braking.
- t = 5.35 s: A observed track_001's cut-in from the right settle.
- t = 5.45 s: A's time-to-contact with track_001 stopped being critical.
- t = 6.05 s: A stopped moving.
- t = 6.05 s: A came to a stop.
- t = 7.45 s: A's radar lost track_001 (its states are UNKNOWN from then on, not ended).
