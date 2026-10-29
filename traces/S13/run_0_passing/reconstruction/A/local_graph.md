# Local graph - vehicle A

All times are A's own local clock: `t_local` = seconds since A's first ego sample (raw clock reading 2068.4393607899547 at `t_local` = 0). Only files under `vehicles/A/` were read; external objects are anonymous radar tracks.

- Local frame: origin = first ego position; x = first heading; y = to the right of the first heading (CARLA convention)
- Trace: 116 frames at 10 Hz in `local_trace.jsonl`, the last one at the recording end (11.45 s)
- Anonymous radar tracks: 3 (10 Hz samples in `local_tracks.jsonl`)
- Speed limit 50 km/h, supplied as incident context: known a priori, not perceived and not ground truth.
- Nodes: 19; edges: 31 (PRECEDES 22, SAME_TRACK 9)

## Nodes

| Id | Local time | Type | Actor | Subject | Source | Details |
|----|-----------:|------|-------|---------|--------|---------|
| A:e01 | 0.00 | MOVING_START | A | - | ego | active_at_first_observation=True |
| A:e02 | 0.00 | THROTTLE_START | A | - | controls | active_at_first_observation=True |
| A:e03 | 0.00 | TRACK_APPEARED_LEFT | A | track_002 | radar | initial_in_ego_path=False |
| A:e04 | 0.00 | TRACK_APPEARED_RIGHT | A | track_001 | radar | initial_in_ego_path=False |
| A:e05 | 0.05 | TRACK_APPEARED_FRONT | A | track_003 | radar | initial_in_ego_path=True |
| A:e06 | 0.55 | CRITICAL_TTC_START | A | track_003 | radar |  |
| A:e07 | 5.20 | CRITICAL_TTC_START | A | track_002 | radar |  |
| A:e08 | 5.50 | CLOSING_START | A | track_002 | radar |  |
| A:e09 | 5.75 | CRITICAL_TTC_END | A | track_003 | radar |  |
| A:e10 | 6.20 | COLLISION | A | - | collision_sensor | peak_impulse=1093.08; merged_bursts=[[6.3, 41.87]] |
| A:e11 | 6.20 | CRITICAL_TTC_END | A | track_002 | radar |  |
| A:e12 | 6.25 | THROTTLE_END | A | - | controls |  |
| A:e13 | 6.25 | BRAKE_START | A | - | controls |  |
| A:e14 | 6.30 | EGO_PATH_ENTRY | A | track_002 | radar | occupancy_evidence=box; occupancy_margin_m=0.50; occupancy_sigma_m=0.26; cause=RECORDER_LATERAL; geometry=estimated_body |
| A:e15 | 6.35 | CLOSING_END | A | track_002 | radar |  |
| A:e16 | 7.35 | MOVING_END | A | - | ego |  |
| A:e17 | 7.35 | STOP_START | A | - | ego |  |
| A:e18 | 9.70 | TRACK_LOST | A | track_001 | radar |  |
| A:e19 | 10.20 | TRACK_LOST | A | track_003 | radar |  |

Events are state transitions; the quantities behind them (speed, pedals, ranges, TTC, relative motion, closest approach) are facts in `local_trace.jsonl`. Events with equal times are simultaneous at the recorder's resolution: PRECEDES links only different times. SAME_TRACK links a track's TRACK_APPEARED_* to every other event about the same local track (grouping only, no order).

## Edges

```
    A:e01 --PRECEDES--> A:e05
    A:e02 --PRECEDES--> A:e05
    A:e03 --PRECEDES--> A:e05
    A:e04 --PRECEDES--> A:e05
    A:e05 --PRECEDES--> A:e06
    A:e06 --PRECEDES--> A:e07
    A:e07 --PRECEDES--> A:e08
    A:e08 --PRECEDES--> A:e09
    A:e09 --PRECEDES--> A:e10
    A:e09 --PRECEDES--> A:e11
    A:e10 --PRECEDES--> A:e12
    A:e10 --PRECEDES--> A:e13
    A:e11 --PRECEDES--> A:e12
    A:e11 --PRECEDES--> A:e13
    A:e12 --PRECEDES--> A:e14
    A:e13 --PRECEDES--> A:e14
    A:e14 --PRECEDES--> A:e15
    A:e15 --PRECEDES--> A:e16
    A:e15 --PRECEDES--> A:e17
    A:e16 --PRECEDES--> A:e18
    A:e17 --PRECEDES--> A:e18
    A:e18 --PRECEDES--> A:e19
    A:e05 --SAME_TRACK--> A:e06
    A:e03 --SAME_TRACK--> A:e07
    A:e03 --SAME_TRACK--> A:e08
    A:e05 --SAME_TRACK--> A:e09
    A:e03 --SAME_TRACK--> A:e11
    A:e03 --SAME_TRACK--> A:e14
    A:e03 --SAME_TRACK--> A:e15
    A:e04 --SAME_TRACK--> A:e18
    A:e05 --SAME_TRACK--> A:e19
```

## Perceived state before each event

Each row is the state just BEFORE its events (none of them applied): events at one time are simultaneous and share it. True states are named, unknown ones end with `?`, false ones are omitted; a lost track's states are UNKNOWN, never ended. Facts: the trace frame at the time shown.

| Local time | Events | Perceived state just before | Facts at |
|-----------:|--------|-----------------------------|---------:|
| 0.00 | A:e01 MOVING_START<br>A:e02 THROTTLE_START<br>A:e03 TRACK_APPEARED_LEFT track_002<br>A:e04 TRACK_APPEARED_RIGHT track_001 | ego: not yet observed | - |
| 0.05 | A:e05 TRACK_APPEARED_FRONT track_003 | ego: MOVING, THROTTLE<br>track_001: CRITICAL_TTC?<br>track_002: CRITICAL_TTC? | 0.00 |
| 0.55 | A:e06 CRITICAL_TTC_START track_003 | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: no active state<br>track_003: IN_EGO_PATH, CRITICAL_TTC? | 0.50 |
| 5.20 | A:e07 CRITICAL_TTC_START track_002 | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: no active state<br>track_003: CRITICAL_TTC, IN_EGO_PATH | 5.10 |
| 5.50 | A:e08 CLOSING_START track_002 | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: CRITICAL_TTC<br>track_003: CRITICAL_TTC, IN_EGO_PATH | 5.40 |
| 5.75 | A:e09 CRITICAL_TTC_END track_003 | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: CLOSING, CRITICAL_TTC<br>track_003: CRITICAL_TTC, IN_EGO_PATH | 5.70 |
| 6.20 | A:e10 COLLISION<br>A:e11 CRITICAL_TTC_END track_002 | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: CLOSING, CRITICAL_TTC<br>track_003: IN_EGO_PATH | 6.10 |
| 6.25 | A:e12 THROTTLE_END<br>A:e13 BRAKE_START | ego: MOVING, THROTTLE<br>track_001: no active state<br>track_002: CLOSING<br>track_003: IN_EGO_PATH | 6.20 |
| 6.30 | A:e14 EGO_PATH_ENTRY track_002 | ego: MOVING, BRAKE<br>track_001: no active state<br>track_002: CLOSING<br>track_003: IN_EGO_PATH | 6.20 |
| 6.35 | A:e15 CLOSING_END track_002 | ego: MOVING, BRAKE<br>track_001: no active state<br>track_002: CLOSING, IN_EGO_PATH<br>track_003: IN_EGO_PATH | 6.30 |
| 7.35 | A:e16 MOVING_END<br>A:e17 STOP_START | ego: MOVING, BRAKE<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_003: IN_EGO_PATH | 7.30 |
| 9.70 | A:e18 TRACK_LOST track_001 | ego: STOP, BRAKE<br>track_001: no active state<br>track_002: IN_EGO_PATH<br>track_003: IN_EGO_PATH | 9.60 |
| 10.20 | A:e19 TRACK_LOST track_003 | ego: STOP, BRAKE<br>track_002: IN_EGO_PATH<br>track_003: IN_EGO_PATH<br>track lost, states UNKNOWN: track_001 | 10.10 |

## States still active when observation ended

- BRAKE, since A:e13 (t = 6.25 s)
- EGO_PATH of track_002, since A:e14 (t = 6.30 s)
- STOP, since A:e17 (t = 7.35 s)

## Tracks lost

- track_003 at 10.20 s (A:e19): IN_EGO_PATH were true; they are UNKNOWN afterwards (no END recorded)
- lost with no state active: track_001

## Temporal safety relations

Order of each track's cut-in, critical TTC and path entry and of the collision report, in local time. Temporal properties only, not causes.

- track_002: CRITICAL_TTC_START 5.20, COLLISION 6.20 (+1.00 s); EGO_PATH_ENTRY 6.30 after critical TTC (+1.10 s)
- track_003: CRITICAL_TTC_START 0.55, COLLISION 6.20 (+5.65 s)

## Sign detection windows

- none

An END means this recorder stopped detecting the sign, not that its obligation ended.

## Anonymous radar tracks

| Track | First seen | Last seen | Measured sweeps | First range / bearing | Min range (at) | Last range / bearing | Max speed |
|-------|-----------:|----------:|----------------:|----------------------|----------------|---------------------|----------:|
| track_001 | 0.00 | 9.70 | 178 | 13.1 m / +9 deg | 13.13 m (0.00) | 56.3 m / +7 deg | 14.2 m/s |
| track_002 | 0.00 | 11.45 | 230 | 5.6 m / -149 deg | 0.20 m (7.20) | 0.3 m / -91 deg | 12.9 m/s |
| track_003 | 0.05 | 10.20 | 191 | 15.4 m / -1 deg | 15.31 m (1.30) | 58.4 m / +3 deg | 14.3 m/s |

Bearing: positive = to A's right. Ranges are measured from the radar to the visible surface of the object.

## Plain-language reading

- t = 0.00 s: A started moving (already the case when first observed).
- t = 0.00 s: A pressed the accelerator (already the case when first observed).
- t = 0.00 s: A's radar started tracking track_002, which appeared on its left.
- t = 0.00 s: A's radar started tracking track_001, which appeared on its right.
- t = 0.05 s: A's radar started tracking track_003, which appeared in front of it.
- t = 0.55 s: A's time-to-contact with track_003 became critical.
- t = 5.20 s: A's time-to-contact with track_002 became critical.
- t = 5.50 s: A observed track_002 start closing in.
- t = 5.75 s: A's time-to-contact with track_003 stopped being critical.
- t = 6.20 s: A's collision sensor recorded a contact (peak impulse 1093 N*s).
- t = 6.20 s: A's time-to-contact with track_002 stopped being critical.
- t = 6.25 s: A released the accelerator.
- t = 6.25 s: A started braking.
- t = 6.30 s: A observed track_002 enter its forward path corridor.
- t = 6.35 s: A observed track_002 stop closing in.
- t = 7.35 s: A stopped moving.
- t = 7.35 s: A came to a stop.
- t = 9.70 s: A's radar lost track_001 (its states are UNKNOWN from then on, not ended).
- t = 10.20 s: A's radar lost track_003 (its states are UNKNOWN from then on, not ended).
