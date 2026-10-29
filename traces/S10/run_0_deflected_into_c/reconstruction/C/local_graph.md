# Local graph - vehicle C

All times are C's own local clock: `t_local` = seconds since C's first ego sample (raw clock reading 1987.095780223608 at `t_local` = 0). Only files under `vehicles/C/` were read; external objects are anonymous radar tracks.

- Local frame: origin = first ego position; x = first heading; y = to the right of the first heading (CARLA convention)
- Trace: 141 frames at 10 Hz in `local_trace.jsonl`, the last one at the recording end (13.95 s)
- Anonymous radar tracks: 2 (10 Hz samples in `local_tracks.jsonl`)
- Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.
- Nodes: 16; edges: 31 (PRECEDES 24, SAME_TRACK 7)

## Nodes

| Id | Local time | Type | Actor | Subject | Source | Details |
|----|-----------:|------|-------|---------|--------|---------|
| C:e01 | 0.00 | MOVING_START | C | - | ego | active_at_first_observation=True |
| C:e02 | 0.00 | THROTTLE_START | C | - | controls | active_at_first_observation=True |
| C:e03 | 0.00 | TRACK_APPEARED_FRONT | C | track_001 | radar | initial_in_ego_path=False |
| C:e04 | 0.00 | CLOSING_START | C | track_001 | radar | active_at_first_observation=True |
| C:e05 | 0.15 | TRACK_APPEARED_LEFT | C | track_002 | radar | initial_in_ego_path=False |
| C:e06 | 0.15 | CLOSING_START | C | track_002 | radar | active_at_first_observation=True |
| C:e07 | 3.65 | CRITICAL_TTC_START | C | track_001 | radar |  |
| C:e08 | 4.20 | EGO_PATH_ENTRY | C | track_001 | radar | occupancy_evidence=box; occupancy_margin_m=0.48; occupancy_sigma_m=0.27; cause=TARGET_LATERAL; geometry=estimated_body |
| C:e09 | 4.70 | COLLISION | C | - | collision_sensor | peak_impulse=2250.28; merged_bursts=[[4.8, 765.39], [6.1, 3.03], [6.75, 0.2]] |
| C:e10 | 4.70 | CRITICAL_TTC_END | C | track_001 | radar |  |
| C:e11 | 4.70 | CLOSING_END | C | track_001 | radar |  |
| C:e12 | 4.75 | THROTTLE_END | C | - | controls |  |
| C:e13 | 4.75 | BRAKE_START | C | - | controls |  |
| C:e14 | 5.05 | CLOSING_END | C | track_002 | radar |  |
| C:e15 | 5.10 | MOVING_END | C | - | ego |  |
| C:e16 | 5.10 | STOP_START | C | - | ego |  |

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
    C:e06 --PRECEDES--> C:e07
    C:e07 --PRECEDES--> C:e08
    C:e08 --PRECEDES--> C:e09
    C:e08 --PRECEDES--> C:e10
    C:e08 --PRECEDES--> C:e11
    C:e09 --PRECEDES--> C:e12
    C:e09 --PRECEDES--> C:e13
    C:e10 --PRECEDES--> C:e12
    C:e10 --PRECEDES--> C:e13
    C:e11 --PRECEDES--> C:e12
    C:e11 --PRECEDES--> C:e13
    C:e12 --PRECEDES--> C:e14
    C:e13 --PRECEDES--> C:e14
    C:e14 --PRECEDES--> C:e15
    C:e14 --PRECEDES--> C:e16
    C:e03 --SAME_TRACK--> C:e04
    C:e05 --SAME_TRACK--> C:e06
    C:e03 --SAME_TRACK--> C:e07
    C:e03 --SAME_TRACK--> C:e08
    C:e03 --SAME_TRACK--> C:e10
    C:e03 --SAME_TRACK--> C:e11
    C:e05 --SAME_TRACK--> C:e14
```

## Perceived state before each event

Each row is the state just BEFORE its events (none of them applied): events at one time are simultaneous and share it. True states are named, unknown ones end with `?`, false ones are omitted; a lost track's states are UNKNOWN, never ended. Facts: the trace frame at the time shown.

| Local time | Events | Perceived state just before | Facts at |
|-----------:|--------|-----------------------------|---------:|
| 0.00 | C:e01 MOVING_START<br>C:e02 THROTTLE_START<br>C:e03 TRACK_APPEARED_FRONT track_001<br>C:e04 CLOSING_START track_001 | ego: not yet observed | - |
| 0.15 | C:e05 TRACK_APPEARED_LEFT track_002<br>C:e06 CLOSING_START track_002 | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC? | 0.10 |
| 3.65 | C:e07 CRITICAL_TTC_START track_001 | ego: MOVING, THROTTLE<br>track_001: CLOSING<br>track_002: CLOSING | 3.60 |
| 4.20 | C:e08 EGO_PATH_ENTRY track_001 | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC<br>track_002: CLOSING | 4.10 |
| 4.70 | C:e09 COLLISION<br>C:e10 CRITICAL_TTC_END track_001<br>C:e11 CLOSING_END track_001 | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH<br>track_002: CLOSING | 4.60 |
| 4.75 | C:e12 THROTTLE_END<br>C:e13 BRAKE_START | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH<br>track_002: CLOSING | 4.70 |
| 5.05 | C:e14 CLOSING_END track_002 | ego: MOVING, BRAKE<br>track_001: IN_EGO_PATH<br>track_002: CLOSING | 5.00 |
| 5.10 | C:e15 MOVING_END<br>C:e16 STOP_START | ego: MOVING, BRAKE<br>track_001: IN_EGO_PATH<br>track_002: no active state | 5.00 |

## States still active when observation ended

- EGO_PATH of track_001, since C:e08 (t = 4.20 s)
- BRAKE, since C:e13 (t = 4.75 s)
- STOP, since C:e16 (t = 5.10 s)

## Tracks lost

- no track was lost

## Temporal safety relations

Order of each track's cut-in, critical TTC and path entry and of the collision report, in local time. Temporal properties only, not causes.

- track_001: CRITICAL_TTC_START 3.65, COLLISION 4.70 (+1.05 s); EGO_PATH_ENTRY 4.20 after critical TTC (+0.55 s)

## Sign detection windows

- none

An END means this recorder stopped detecting the sign, not that its obligation ended.

## Anonymous radar tracks

| Track | First seen | Last seen | Measured sweeps | First range / bearing | Min range (at) | Last range / bearing | Max speed |
|-------|-----------:|----------:|----------------:|----------------------|----------------|---------------------|----------:|
| track_001 | 0.00 | 13.95 | 270 | 73.9 m / -3 deg | 0.09 m (13.30) | 0.1 m / -90 deg | 11.1 m/s |
| track_002 | 0.15 | 13.95 | 272 | 46.2 m / -54 deg | 4.92 m (13.95) | 4.9 m / -40 deg | 10.2 m/s |

Bearing: positive = to C's right. Ranges are measured from the radar to the visible surface of the object.

## Plain-language reading

- t = 0.00 s: C started moving (already the case when first observed).
- t = 0.00 s: C pressed the accelerator (already the case when first observed).
- t = 0.00 s: C's radar started tracking track_001, which appeared in front of it.
- t = 0.00 s: C observed track_001 start closing in (already the case when first observed).
- t = 0.15 s: C's radar started tracking track_002, which appeared on its left.
- t = 0.15 s: C observed track_002 start closing in (already the case when first observed).
- t = 3.65 s: C's time-to-contact with track_001 became critical.
- t = 4.20 s: C observed track_001 enter its forward path corridor.
- t = 4.70 s: C's collision sensor recorded a contact (peak impulse 2250 N*s).
- t = 4.70 s: C's time-to-contact with track_001 stopped being critical.
- t = 4.70 s: C observed track_001 stop closing in.
- t = 4.75 s: C released the accelerator.
- t = 4.75 s: C started braking.
- t = 5.05 s: C observed track_002 stop closing in.
- t = 5.10 s: C stopped moving.
- t = 5.10 s: C came to a stop.
