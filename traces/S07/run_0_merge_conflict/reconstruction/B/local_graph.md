# Local graph - vehicle B

All times are B's own local clock: `t_local` = seconds since B's first ego sample (raw clock reading 28.253541942685843 at `t_local` = 0). Only files under `vehicles/B/` were read; external objects are anonymous radar tracks.

- Local frame: origin = first ego position; x = first heading; y = to the right of the first heading (CARLA convention)
- Trace: 325 frames at 10 Hz in `local_trace.jsonl`, the last one at the recording end (32.35 s)
- Anonymous radar tracks: 1 (10 Hz samples in `local_tracks.jsonl`)
- Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.
- Nodes: 17; edges: 32 (PRECEDES 27, SAME_TRACK 5)

## Nodes

| Id | Local time | Type | Actor | Subject | Source | Details |
|----|-----------:|------|-------|---------|--------|---------|
| B:e01 | 0.00 | MOVING_START | B | - | ego | active_at_first_observation=True |
| B:e02 | 0.00 | THROTTLE_START | B | - | controls | active_at_first_observation=True |
| B:e03 | 12.30 | TRACK_APPEARED_LEFT | B | track_001 | radar | initial_in_ego_path=False |
| B:e04 | 12.30 | CLOSING_START | B | track_001 | radar | active_at_first_observation=True |
| B:e05 | 13.00 | INDICATOR_RIGHT_START | B | - | lights |  |
| B:e06 | 15.50 | CRITICAL_TTC_START | B | track_001 | radar |  |
| B:e07 | 16.90 | TURN_RIGHT_START | B | - | ego |  |
| B:e08 | 18.95 | TURN_RIGHT_END | B | - | ego |  |
| B:e09 | 19.10 | INDICATOR_RIGHT_END | B | - | lights |  |
| B:e10 | 19.10 | EGO_PATH_ENTRY | B | track_001 | radar | occupancy_evidence=returns; occupancy_margin_m=0.44; occupancy_sigma_m=0.25; cause=MUTUAL_LATERAL; geometry=estimated_body |
| B:e11 | 19.25 | COLLISION | B | - | collision_sensor | peak_impulse=1928.22; merged_bursts=[[19.85, 6.8]] |
| B:e12 | 19.25 | CRITICAL_TTC_END | B | track_001 | radar |  |
| B:e13 | 19.25 | CLOSING_END | B | track_001 | radar |  |
| B:e14 | 19.30 | THROTTLE_END | B | - | controls |  |
| B:e15 | 19.30 | BRAKE_START | B | - | controls |  |
| B:e16 | 20.00 | MOVING_END | B | - | ego |  |
| B:e17 | 20.00 | STOP_START | B | - | ego |  |

Events are state transitions; the quantities behind them (speed, pedals, ranges, TTC, relative motion, closest approach) are facts in `local_trace.jsonl`. Events with equal times are simultaneous at the recorder's resolution: PRECEDES links only different times. SAME_TRACK links a track's TRACK_APPEARED_* to every other event about the same local track (grouping only, no order).

## Edges

```
    B:e01 --PRECEDES--> B:e03
    B:e01 --PRECEDES--> B:e04
    B:e02 --PRECEDES--> B:e03
    B:e02 --PRECEDES--> B:e04
    B:e03 --PRECEDES--> B:e05
    B:e04 --PRECEDES--> B:e05
    B:e05 --PRECEDES--> B:e06
    B:e06 --PRECEDES--> B:e07
    B:e07 --PRECEDES--> B:e08
    B:e08 --PRECEDES--> B:e09
    B:e08 --PRECEDES--> B:e10
    B:e09 --PRECEDES--> B:e11
    B:e09 --PRECEDES--> B:e12
    B:e09 --PRECEDES--> B:e13
    B:e10 --PRECEDES--> B:e11
    B:e10 --PRECEDES--> B:e12
    B:e10 --PRECEDES--> B:e13
    B:e11 --PRECEDES--> B:e14
    B:e11 --PRECEDES--> B:e15
    B:e12 --PRECEDES--> B:e14
    B:e12 --PRECEDES--> B:e15
    B:e13 --PRECEDES--> B:e14
    B:e13 --PRECEDES--> B:e15
    B:e14 --PRECEDES--> B:e16
    B:e14 --PRECEDES--> B:e17
    B:e15 --PRECEDES--> B:e16
    B:e15 --PRECEDES--> B:e17
    B:e03 --SAME_TRACK--> B:e04
    B:e03 --SAME_TRACK--> B:e06
    B:e03 --SAME_TRACK--> B:e10
    B:e03 --SAME_TRACK--> B:e12
    B:e03 --SAME_TRACK--> B:e13
```

## Perceived state before each event

Each row is the state just BEFORE its events (none of them applied): events at one time are simultaneous and share it. True states are named, unknown ones end with `?`, false ones are omitted; a lost track's states are UNKNOWN, never ended. Facts: the trace frame at the time shown.

| Local time | Events | Perceived state just before | Facts at |
|-----------:|--------|-----------------------------|---------:|
| 0.00 | B:e01 MOVING_START<br>B:e02 THROTTLE_START | ego: not yet observed | - |
| 12.30 | B:e03 TRACK_APPEARED_LEFT track_001<br>B:e04 CLOSING_START track_001 | ego: MOVING, THROTTLE | 12.20 |
| 13.00 | B:e05 INDICATOR_RIGHT_START | ego: MOVING, THROTTLE<br>track_001: CLOSING | 12.90 |
| 15.50 | B:e06 CRITICAL_TTC_START track_001 | ego: MOVING, THROTTLE, INDICATOR_RIGHT<br>track_001: CLOSING | 15.40 |
| 16.90 | B:e07 TURN_RIGHT_START | ego: MOVING, THROTTLE, INDICATOR_RIGHT<br>track_001: CLOSING, CRITICAL_TTC | 16.80 |
| 18.95 | B:e08 TURN_RIGHT_END | ego: MOVING, THROTTLE, TURN_RIGHT, INDICATOR_RIGHT<br>track_001: CLOSING, CRITICAL_TTC | 18.90 |
| 19.10 | B:e09 INDICATOR_RIGHT_END<br>B:e10 EGO_PATH_ENTRY track_001 | ego: MOVING, THROTTLE, INDICATOR_RIGHT<br>track_001: CLOSING, CRITICAL_TTC | 19.00 |
| 19.25 | B:e11 COLLISION<br>B:e12 CRITICAL_TTC_END track_001<br>B:e13 CLOSING_END track_001 | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH | 19.20 |
| 19.30 | B:e14 THROTTLE_END<br>B:e15 BRAKE_START | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH | 19.20 |
| 20.00 | B:e16 MOVING_END<br>B:e17 STOP_START | ego: MOVING, BRAKE<br>track_001: IN_EGO_PATH | 19.90 |

## States still active when observation ended

- EGO_PATH of track_001, since B:e10 (t = 19.10 s)
- BRAKE, since B:e15 (t = 19.30 s)
- STOP, since B:e17 (t = 20.00 s)

## Tracks lost

- no track was lost

## Temporal safety relations

Order of each track's cut-in, critical TTC and path entry and of the collision report, in local time. Temporal properties only, not causes.

- track_001: CRITICAL_TTC_START 15.50, COLLISION 19.25 (+3.75 s); EGO_PATH_ENTRY 19.10 after critical TTC (+3.60 s)

## Sign detection windows

- none

An END means this recorder stopped detecting the sign, not that its obligation ended.

## Anonymous radar tracks

| Track | First seen | Last seen | Measured sweeps | First range / bearing | Min range (at) | Last range / bearing | Max speed |
|-------|-----------:|----------:|----------------:|----------------------|----------------|---------------------|----------:|
| track_001 | 12.30 | 32.35 | 401 | 80.4 m / -21 deg | 0.01 m (32.35) | 0.0 m / -90 deg | 8.2 m/s |

Bearing: positive = to B's right. Ranges are measured from the radar to the visible surface of the object.

## Plain-language reading

- t = 0.00 s: B started moving (already the case when first observed).
- t = 0.00 s: B pressed the accelerator (already the case when first observed).
- t = 12.30 s: B's radar started tracking track_001, which appeared on its left.
- t = 12.30 s: B observed track_001 start closing in (already the case when first observed).
- t = 13.00 s: B switched on its right turn indicator.
- t = 15.50 s: B's time-to-contact with track_001 became critical.
- t = 16.90 s: B started turning right.
- t = 18.95 s: B stopped turning right.
- t = 19.10 s: B switched off its right turn indicator.
- t = 19.10 s: B observed track_001 enter its forward path corridor.
- t = 19.25 s: B's collision sensor recorded a contact (peak impulse 1928 N*s).
- t = 19.25 s: B's time-to-contact with track_001 stopped being critical.
- t = 19.25 s: B observed track_001 stop closing in.
- t = 19.30 s: B released the accelerator.
- t = 19.30 s: B started braking.
- t = 20.00 s: B stopped moving.
- t = 20.00 s: B came to a stop.
