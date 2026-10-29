# Local graph - vehicle B

All times are B's own local clock: `t_local` = seconds since B's first ego sample (raw clock reading 1949.6870362199843 at `t_local` = 0). Only files under `vehicles/B/` were read; external objects are anonymous radar tracks.

- Local frame: origin = first ego position; x = first heading; y = to the right of the first heading (CARLA convention)
- Trace: 161 frames at 10 Hz in `local_trace.jsonl`, the last one at the recording end (15.95 s)
- Anonymous radar tracks: 1 (10 Hz samples in `local_tracks.jsonl`)
- Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.
- Nodes: 13; edges: 25 (PRECEDES 20, SAME_TRACK 5)

## Nodes

| Id | Local time | Type | Actor | Subject | Source | Details |
|----|-----------:|------|-------|---------|--------|---------|
| B:e01 | 0.00 | MOVING_START | B | - | ego | active_at_first_observation=True |
| B:e02 | 0.00 | THROTTLE_START | B | - | controls | active_at_first_observation=True |
| B:e03 | 2.70 | TRACK_APPEARED_RIGHT | B | track_001 | radar | initial_in_ego_path=False |
| B:e04 | 2.70 | CLOSING_START | B | track_001 | radar | active_at_first_observation=True |
| B:e05 | 3.55 | CRITICAL_TTC_START | B | track_001 | radar |  |
| B:e06 | 5.00 | EGO_PATH_ENTRY | B | track_001 | radar | occupancy_evidence=returns; occupancy_margin_m=0.44; occupancy_sigma_m=0.25; cause=TARGET_LATERAL; geometry=estimated_body |
| B:e07 | 5.40 | COLLISION | B | - | collision_sensor | peak_impulse=12940.27 |
| B:e08 | 5.40 | CRITICAL_TTC_END | B | track_001 | radar |  |
| B:e09 | 5.40 | CLOSING_END | B | track_001 | radar |  |
| B:e10 | 5.45 | THROTTLE_END | B | - | controls |  |
| B:e11 | 5.45 | BRAKE_START | B | - | controls |  |
| B:e12 | 5.60 | MOVING_END | B | - | ego |  |
| B:e13 | 5.60 | STOP_START | B | - | ego |  |

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
    B:e06 --PRECEDES--> B:e08
    B:e06 --PRECEDES--> B:e09
    B:e07 --PRECEDES--> B:e10
    B:e07 --PRECEDES--> B:e11
    B:e08 --PRECEDES--> B:e10
    B:e08 --PRECEDES--> B:e11
    B:e09 --PRECEDES--> B:e10
    B:e09 --PRECEDES--> B:e11
    B:e10 --PRECEDES--> B:e12
    B:e10 --PRECEDES--> B:e13
    B:e11 --PRECEDES--> B:e12
    B:e11 --PRECEDES--> B:e13
    B:e03 --SAME_TRACK--> B:e04
    B:e03 --SAME_TRACK--> B:e05
    B:e03 --SAME_TRACK--> B:e06
    B:e03 --SAME_TRACK--> B:e08
    B:e03 --SAME_TRACK--> B:e09
```

## Perceived state before each event

Each row is the state just BEFORE its events (none of them applied): events at one time are simultaneous and share it. True states are named, unknown ones end with `?`, false ones are omitted; a lost track's states are UNKNOWN, never ended. Facts: the trace frame at the time shown.

| Local time | Events | Perceived state just before | Facts at |
|-----------:|--------|-----------------------------|---------:|
| 0.00 | B:e01 MOVING_START<br>B:e02 THROTTLE_START | ego: not yet observed | - |
| 2.70 | B:e03 TRACK_APPEARED_RIGHT track_001<br>B:e04 CLOSING_START track_001 | ego: MOVING, THROTTLE | 2.60 |
| 3.55 | B:e05 CRITICAL_TTC_START track_001 | ego: MOVING, THROTTLE<br>track_001: CLOSING | 3.50 |
| 5.00 | B:e06 EGO_PATH_ENTRY track_001 | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC | 4.90 |
| 5.40 | B:e07 COLLISION<br>B:e08 CRITICAL_TTC_END track_001<br>B:e09 CLOSING_END track_001 | ego: MOVING, THROTTLE<br>track_001: CLOSING, CRITICAL_TTC, IN_EGO_PATH | 5.30 |
| 5.45 | B:e10 THROTTLE_END<br>B:e11 BRAKE_START | ego: MOVING, THROTTLE<br>track_001: IN_EGO_PATH | 5.40 |
| 5.60 | B:e12 MOVING_END<br>B:e13 STOP_START | ego: MOVING, BRAKE<br>track_001: IN_EGO_PATH | 5.50 |

## States still active when observation ended

- EGO_PATH of track_001, since B:e06 (t = 5.00 s)
- BRAKE, since B:e11 (t = 5.45 s)
- STOP, since B:e13 (t = 5.60 s)

## Tracks lost

- no track was lost

## Temporal safety relations

Order of each track's cut-in, critical TTC and path entry and of the collision report, in local time. Temporal properties only, not causes.

- track_001: CRITICAL_TTC_START 3.55, COLLISION 5.40 (+1.85 s); EGO_PATH_ENTRY 5.00 after critical TTC (+1.45 s)

## Sign detection windows

- none

An END means this recorder stopped detecting the sign, not that its obligation ended.

## Anonymous radar tracks

| Track | First seen | Last seen | Measured sweeps | First range / bearing | Min range (at) | Last range / bearing | Max speed |
|-------|-----------:|----------:|----------------:|----------------------|----------------|---------------------|----------:|
| track_001 | 2.70 | 15.95 | 266 | 34.3 m / +21 deg | 0.54 m (15.95) | 0.5 m / +10 deg | 5.3 m/s |

Bearing: positive = to B's right. Ranges are measured from the radar to the visible surface of the object.

## Plain-language reading

- t = 0.00 s: B started moving (already the case when first observed).
- t = 0.00 s: B pressed the accelerator (already the case when first observed).
- t = 2.70 s: B's radar started tracking track_001, which appeared on its right.
- t = 2.70 s: B observed track_001 start closing in (already the case when first observed).
- t = 3.55 s: B's time-to-contact with track_001 became critical.
- t = 5.00 s: B observed track_001 enter its forward path corridor.
- t = 5.40 s: B's collision sensor recorded a contact (peak impulse 12940 N*s).
- t = 5.40 s: B's time-to-contact with track_001 stopped being critical.
- t = 5.40 s: B observed track_001 stop closing in.
- t = 5.45 s: B released the accelerator.
- t = 5.45 s: B started braking.
- t = 5.60 s: B stopped moving.
- t = 5.60 s: B came to a stop.
