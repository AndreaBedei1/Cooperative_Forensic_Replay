# Local graph - vehicle A

All times are A's own local clock: `t_local` = seconds since A's first ego sample (raw clock reading 2005.8708217665553 at `t_local` = 0). Only files under `vehicles/A/` were read; external objects are anonymous radar tracks.

- Local frame: origin = first ego position; x = first heading; y = to the right of the first heading (CARLA convention)
- Trace: 121 frames at 10 Hz in `local_trace.jsonl`, the last one at the recording end (11.95 s)
- Anonymous radar tracks: 1 (10 Hz samples in `local_tracks.jsonl`)
- Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.
- Nodes: 22; edges: 42 (PRECEDES 35, SAME_TRACK 7)

## Nodes

| Id | Local time | Type | Actor | Subject | Source | Details |
|----|-----------:|------|-------|---------|--------|---------|
| A:e01 | 0.00 | MOVING_START | A | - | ego | active_at_first_observation=True |
| A:e02 | 0.00 | THROTTLE_START | A | - | controls | active_at_first_observation=True |
| A:e03 | 0.00 | TRACK_APPEARED_LEFT | A | track_001 | radar | initial_in_ego_path=False |
| A:e04 | 0.00 | CLOSING_START | A | track_001 | radar | active_at_first_observation=True |
| A:e05 | 3.95 | THROTTLE_END | A | - | controls |  |
| A:e06 | 3.95 | BRAKE_START | A | - | controls |  |
| A:e07 | 4.40 | CLOSING_END | A | track_001 | radar |  |
| A:e08 | 4.55 | BRAKE_END | A | - | controls |  |
| A:e09 | 4.65 | THROTTLE_START | A | - | controls |  |
| A:e10 | 5.55 | COLLISION | A | - | collision_sensor | peak_impulse=4243.51 |
| A:e11 | 5.55 | THROTTLE_END | A | - | controls |  |
| A:e12 | 5.55 | BRAKE_START | A | - | controls |  |
| A:e13 | 5.55 | CLOSING_START | A | track_001 | radar |  |
| A:e14 | 5.55 | CRITICAL_TTC_START | A | track_001 | radar |  |
| A:e15 | 5.60 | BRAKE_END | A | - | controls |  |
| A:e16 | 5.90 | EGO_PATH_ENTRY | A | track_001 | radar | occupancy_evidence=box; occupancy_margin_m=0.58; occupancy_sigma_m=0.26; cause=RECORDER_LATERAL; geometry=estimated_body |
| A:e17 | 6.60 | COLLISION | A | - | collision_sensor | peak_impulse=839.68; merged_bursts=[[6.85, 241.71], [7.6, 236.89]] |
| A:e18 | 6.60 | CRITICAL_TTC_END | A | track_001 | radar |  |
| A:e19 | 6.60 | CLOSING_END | A | track_001 | radar |  |
| A:e20 | 7.45 | MOVING_END | A | - | ego |  |
| A:e21 | 7.45 | STOP_START | A | - | ego |  |
| A:e22 | 7.45 | BRAKE_START | A | - | controls |  |

Events are state transitions; the quantities behind them (speed, pedals, ranges, TTC, relative motion, closest approach) are facts in `local_trace.jsonl`. Events with equal times are simultaneous at the recorder's resolution: PRECEDES links only different times. SAME_TRACK links a track's TRACK_APPEARED_* to every other event about the same local track (grouping only, no order).

## Edges

```
    A:e01 --PRECEDES--> A:e05
    A:e01 --PRECEDES--> A:e06
    A:e02 --PRECEDES--> A:e05
    A:e02 --PRECEDES--> A:e06
    A:e03 --PRECEDES--> A:e05
    A:e03 --PRECEDES--> A:e06
    A:e04 --PRECEDES--> A:e05
    A:e04 --PRECEDES--> A:e06
    A:e05 --PRECEDES--> A:e07
    A:e06 --PRECEDES--> A:e07
    A:e07 --PRECEDES--> A:e08
    A:e08 --PRECEDES--> A:e09
    A:e09 --PRECEDES--> A:e10
    A:e09 --PRECEDES--> A:e11
    A:e09 --PRECEDES--> A:e12
    A:e09 --PRECEDES--> A:e13
    A:e09 --PRECEDES--> A:e14
    A:e10 --PRECEDES--> A:e15
    A:e11 --PRECEDES--> A:e15
    A:e12 --PRECEDES--> A:e15
    A:e13 --PRECEDES--> A:e15
    A:e14 --PRECEDES--> A:e15
    A:e15 --PRECEDES--> A:e16
    A:e16 --PRECEDES--> A:e17
    A:e16 --PRECEDES--> A:e18
    A:e16 --PRECEDES--> A:e19
    A:e17 --PRECEDES--> A:e20
    A:e17 --PRECEDES--> A:e21
    A:e17 --PRECEDES--> A:e22
    A:e18 --PRECEDES--> A:e20
    A:e18 --PRECEDES--> A:e21
    A:e18 --PRECEDES--> A:e22
    A:e19 --PRECEDES--> A:e20
    A:e19 --PRECEDES--> A:e21
    A:e19 --PRECEDES--> A:e22
    A:e03 --SAME_TRACK--> A:e04
    A:e03 --SAME_TRACK--> A:e07
    A:e03 --SAME_TRACK--> A:e13
    A:e03 --SAME_TRACK--> A:e14
    A:e03 --SAME_TRACK--> A:e16
    A:e03 --SAME_TRACK--> A:e18
    A:e03 --SAME_TRACK--> A:e19
```

## Perceived state before each event

Each row is the state just BEFORE its events (none of them applied): events at one time are simultaneous and share it. True states are named, unknown ones end with `?`, false ones are omitted; a lost track's states are UNKNOWN, never ended. Facts: the trace frame at the time shown.

| Local time | Events | Perceived state just before | Facts at |
|-----------:|--------|-----------------------------|---------:|
| 0.00 | A:e01 MOVING_START<br>A:e02 THROTTLE_START<br>A:e03 TRACK_APPEARED_LEFT track_001<br>A:e04 CLOSING_START track_001 | ego: not yet observed | - |
| 3.95 | A:e05 THROTTLE_END<br>A:e06 BRAKE_START | ego: MOVING, THROTTLE<br>track_001: CLOSING | 3.90 |
| 4.40 | A:e07 CLOSING_END track_001 | ego: MOVING, BRAKE<br>track_001: CLOSING | 4.30 |
| 4.55 | A:e08 BRAKE_END | ego: MOVING, BRAKE<br>track_001: no active state | 4.50 |
| 4.65 | A:e09 THROTTLE_START | ego: MOVING<br>track_001: no active state | 4.60 |
| 5.55 | A:e10 COLLISION<br>A:e11 THROTTLE_END<br>A:e12 BRAKE_START<br>A:e13 CLOSING_START track_001<br>A:e14 CRITICAL_TTC_START track_001 | ego: MOVING, THROTTLE<br>track_001: no active state | 5.50 |
| 5.60 | A:e15 BRAKE_END | ego: MOVING, BRAKE<br>track_001: CLOSING, CRITICAL_TTC | 5.50 |
| 5.90 | A:e16 EGO_PATH_ENTRY track_001 | ego: MOVING<br>track_001: CLOSING, CRITICAL_TTC | 5.80 |
| 6.60 | A:e17 COLLISION<br>A:e18 CRITICAL_TTC_END track_001<br>A:e19 CLOSING_END track_001 | ego: MOVING<br>track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH | 6.50 |
| 7.45 | A:e20 MOVING_END<br>A:e21 STOP_START<br>A:e22 BRAKE_START | ego: MOVING<br>track_001: IN_EGO_PATH | 7.40 |

## States still active when observation ended

- EGO_PATH of track_001, since A:e16 (t = 5.90 s)
- STOP, since A:e21 (t = 7.45 s)
- BRAKE, since A:e22 (t = 7.45 s)

## Tracks lost

- no track was lost

## Temporal safety relations

Order of each track's cut-in, critical TTC and path entry and of the collision report, in local time. Temporal properties only, not causes.

- track_001: CRITICAL_TTC_START 5.55, COLLISION 5.55 (+0.00 s); EGO_PATH_ENTRY 5.90 after critical TTC (+0.35 s)

## Sign detection windows

- none

An END means this recorder stopped detecting the sign, not that its obligation ended.

## Anonymous radar tracks

| Track | First seen | Last seen | Measured sweeps | First range / bearing | Min range (at) | Last range / bearing | Max speed |
|-------|-----------:|----------:|----------------:|----------------------|----------------|---------------------|----------:|
| track_001 | 0.00 | 11.95 | 240 | 14.1 m / -10 deg | 0.06 m (7.25) | 0.1 m / -1 deg | 9.3 m/s |

Bearing: positive = to A's right. Ranges are measured from the radar to the visible surface of the object.

## Plain-language reading

- t = 0.00 s: A started moving (already the case when first observed).
- t = 0.00 s: A pressed the accelerator (already the case when first observed).
- t = 0.00 s: A's radar started tracking track_001, which appeared on its left.
- t = 0.00 s: A observed track_001 start closing in (already the case when first observed).
- t = 3.95 s: A released the accelerator.
- t = 3.95 s: A started braking.
- t = 4.40 s: A observed track_001 stop closing in.
- t = 4.55 s: A released the brake.
- t = 4.65 s: A pressed the accelerator.
- t = 5.55 s: A's collision sensor recorded a contact (peak impulse 4244 N*s).
- t = 5.55 s: A released the accelerator.
- t = 5.55 s: A started braking.
- t = 5.55 s: A observed track_001 start closing in.
- t = 5.55 s: A's time-to-contact with track_001 became critical.
- t = 5.60 s: A released the brake.
- t = 5.90 s: A observed track_001 enter its forward path corridor.
- t = 6.60 s: A's collision sensor recorded a contact (peak impulse 840 N*s).
- t = 6.60 s: A's time-to-contact with track_001 stopped being critical.
- t = 6.60 s: A observed track_001 stop closing in.
- t = 7.45 s: A stopped moving.
- t = 7.45 s: A came to a stop.
- t = 7.45 s: A started braking.
