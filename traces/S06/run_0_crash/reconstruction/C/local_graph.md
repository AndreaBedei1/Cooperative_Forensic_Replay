# Local graph - vehicle C

All times are C's own local clock: `t_local` = seconds since C's first ego sample (raw clock reading 1929.7311951592565 at `t_local` = 0). Only files under `vehicles/C/` were read; external objects are anonymous radar tracks.

- Local frame: origin = first ego position; x = first heading; y = to the right of the first heading (CARLA convention)
- Trace: 153 frames at 10 Hz in `local_trace.jsonl`, the last one at the recording end (15.15 s)
- Anonymous radar tracks: 2 (10 Hz samples in `local_tracks.jsonl`)
- Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.
- Nodes: 14; edges: 27 (PRECEDES 21, SAME_TRACK 6)

## Nodes

| Id | Local time | Type | Actor | Subject | Source | Details |
|----|-----------:|------|-------|---------|--------|---------|
| C:e01 | 0.00 | MOVING_START | C | - | ego | active_at_first_observation=True |
| C:e02 | 0.00 | THROTTLE_START | C | - | controls | active_at_first_observation=True |
| C:e03 | 0.00 | TRACK_APPEARED_FRONT | C | track_001 | radar | initial_in_ego_path=False |
| C:e04 | 0.00 | CLOSING_START | C | track_001 | radar | active_at_first_observation=True |
| C:e05 | 2.10 | TRACK_APPEARED_LEFT | C | track_002 | radar | initial_in_ego_path=False |
| C:e06 | 2.10 | CLOSING_START | C | track_002 | radar | active_at_first_observation=True |
| C:e07 | 2.35 | THROTTLE_END | C | - | controls |  |
| C:e08 | 2.35 | BRAKE_START | C | - | controls |  |
| C:e09 | 2.90 | MOVING_END | C | - | ego |  |
| C:e10 | 2.90 | STOP_START | C | - | ego |  |
| C:e11 | 3.90 | EGO_PATH_ENTRY | C | track_002 | radar | occupancy_evidence=returns; occupancy_margin_m=0.51; occupancy_sigma_m=0.25; cause=TARGET_LATERAL; geometry=estimated_body |
| C:e12 | 3.95 | EGO_PATH_ENTRY | C | track_001 | radar | occupancy_evidence=box; occupancy_margin_m=0.47; occupancy_sigma_m=0.28; cause=TARGET_LATERAL; geometry=estimated_body |
| C:e13 | 4.55 | CLOSING_END | C | track_002 | radar |  |
| C:e14 | 4.55 | TRACK_LOST | C | track_001 | radar |  |

Events are state transitions; the quantities behind them (speed, pedals, ranges, TTC, relative motion, closest approach) are facts in `local_trace.jsonl`. Events with equal times are simultaneous at the recorder's resolution: PRECEDES links only different times. SAME_TRACK links a track's TRACK_APPEARED_* to every other event about the same local track (grouping only, no order).

## Edges

```
    C:e01 --PRECEDES--> C:e05
    C:e01 --PRECEDES--> C:e06
    C:e02 --PRECEDES--> C:e05
    C:e02 --PRECEDES--> C:e06
    C:e03 --PRECEDES--> C:e05
    C:e03 --PRECEDES--> C:e06
    C:e04 --PRECEDES--> C:e05
    C:e04 --PRECEDES--> C:e06
    C:e05 --PRECEDES--> C:e07
    C:e05 --PRECEDES--> C:e08
    C:e06 --PRECEDES--> C:e07
    C:e06 --PRECEDES--> C:e08
    C:e07 --PRECEDES--> C:e09
    C:e07 --PRECEDES--> C:e10
    C:e08 --PRECEDES--> C:e09
    C:e08 --PRECEDES--> C:e10
    C:e09 --PRECEDES--> C:e11
    C:e10 --PRECEDES--> C:e11
    C:e11 --PRECEDES--> C:e12
    C:e12 --PRECEDES--> C:e13
    C:e12 --PRECEDES--> C:e14
    C:e03 --SAME_TRACK--> C:e04
    C:e05 --SAME_TRACK--> C:e06
    C:e05 --SAME_TRACK--> C:e11
    C:e03 --SAME_TRACK--> C:e12
    C:e05 --SAME_TRACK--> C:e13
    C:e03 --SAME_TRACK--> C:e14
```

## Perceived state before each event

Each row is the state just BEFORE its events (none of them applied): events at one time are simultaneous and share it. True states are named, unknown ones end with `?`, false ones are omitted; a lost track's states are UNKNOWN, never ended. Facts: the trace frame at the time shown.

| Local time | Events | Perceived state just before | Facts at |
|-----------:|--------|-----------------------------|---------:|
| 0.00 | C:e01 MOVING_START<br>C:e02 THROTTLE_START<br>C:e03 TRACK_APPEARED_FRONT track_001<br>C:e04 CLOSING_START track_001 | ego: not yet observed | - |
| 2.10 | C:e05 TRACK_APPEARED_LEFT track_002<br>C:e06 CLOSING_START track_002 | ego: MOVING, THROTTLE<br>track_001: CLOSING | 2.00 |
| 2.35 | C:e07 THROTTLE_END<br>C:e08 BRAKE_START | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>track_002: CLOSING, CRITICAL_TTC? | 2.30 |
| 2.90 | C:e09 MOVING_END<br>C:e10 STOP_START | ego: MOVING, BRAKE<br>track_001: CLOSING<br>track_002: CLOSING | 2.80 |
| 3.90 | C:e11 EGO_PATH_ENTRY track_002 | ego: STOP, BRAKE<br>track_001: CLOSING<br>track_002: CLOSING | 3.80 |
| 3.95 | C:e12 EGO_PATH_ENTRY track_001 | ego: STOP, BRAKE<br>track_001: CLOSING<br>track_002: CLOSING, IN_EGO_PATH | 3.90 |
| 4.55 | C:e13 CLOSING_END track_002<br>C:e14 TRACK_LOST track_001 | ego: STOP, BRAKE<br>track_001: CLOSING, IN_EGO_PATH<br>track_002: CLOSING, IN_EGO_PATH | 4.50 |

## States still active when observation ended

- CLOSING of track_001, since C:e04 (t = 0.00 s); the track was lost at 4.55 s
- BRAKE, since C:e08 (t = 2.35 s)
- STOP, since C:e10 (t = 2.90 s)
- EGO_PATH of track_002, since C:e11 (t = 3.90 s)
- EGO_PATH of track_001, since C:e12 (t = 3.95 s); the track was lost at 4.55 s

## Tracks lost

- track_001 at 4.55 s (C:e14): CLOSING, IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)

## Temporal safety relations

Order of each track's cut-in, critical TTC and path entry and of the collision report, in local time. Temporal properties only, not causes.

- track_001: EGO_PATH_ENTRY 3.95, no critical TTC
- track_002: EGO_PATH_ENTRY 3.90, no critical TTC

## Sign detection windows

- none

An END means this recorder stopped detecting the sign, not that its obligation ended.

## Anonymous radar tracks

| Track | First seen | Last seen | Measured sweeps | First range / bearing | Min range (at) | Last range / bearing | Max speed |
|-------|-----------:|----------:|----------------:|----------------------|----------------|---------------------|----------:|
| track_001 | 0.00 | 4.55 | 89 | 77.6 m / -3 deg | 9.31 m (4.55) | 9.3 m / -9 deg | 10.2 m/s |
| track_002 | 2.10 | 15.15 | 261 | 34.4 m / -59 deg | 9.18 m (7.60) | 9.2 m / -0 deg | 12.4 m/s |

Bearing: positive = to C's right. Ranges are measured from the radar to the visible surface of the object.

## Plain-language reading

- t = 0.00 s: C started moving (already the case when first observed).
- t = 0.00 s: C pressed the accelerator (already the case when first observed).
- t = 0.00 s: C's radar started tracking track_001, which appeared in front of it.
- t = 0.00 s: C observed track_001 start closing in (already the case when first observed).
- t = 2.10 s: C's radar started tracking track_002, which appeared on its left.
- t = 2.10 s: C observed track_002 start closing in (already the case when first observed).
- t = 2.35 s: C released the accelerator.
- t = 2.35 s: C started braking.
- t = 2.90 s: C stopped moving.
- t = 2.90 s: C came to a stop.
- t = 3.90 s: C observed track_002 enter its forward path corridor.
- t = 3.95 s: C observed track_001 enter its forward path corridor.
- t = 4.55 s: C observed track_002 stop closing in.
- t = 4.55 s: C's radar lost track_001 (its states are UNKNOWN from then on, not ended).
