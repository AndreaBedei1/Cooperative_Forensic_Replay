# Privileged evaluation - S15/run_0_dense_platoon

This compares the finished reconstruction with `ground_truth/` (simulator state). The reconstruction never read it and was not changed by this evaluation.

**collision reconstructed: yes (1/1 vehicle contacts); associations correct: 1/1; anonymous: 18; max |t_global error| 0.0 s**

Privileged assumption: recorder raw clocks are CARLA simulator time.

## Collisions

| True contact | Sim time | Peak impulse | Reconstructed as | Participants correct | Report timing error |
|--------------|---------:|-------------:|------------------|----------------------|--------------------:|
| A + B | 2107.467 | 34836.9 | g39 | yes | 0.0 s |

Reconstructed COLLISION nodes that reproduce no true contact: none.

## Graph alignment accuracy

Local time at which each graph reads t_global = 0, against the true local time of the reference contact; the chain lists the matched collisions that aligned the graph.

| Graph | Status | Chain | Estimated (local) | True (local) | Error |
|-------|--------|-------|------------------:|-------------:|------:|
| A | ALIGNED | collision_001 | 7.45 | 7.45 | 0.0 s |
| B | ALIGNED | collision_001 | 7.45 | 7.45 | 0.0 s |

Relative clock offset B - A: estimated +0.000 s, true +0.000 s (error +0.000 s).

## Global event times

55 timed global nodes; max |t_global - true global time| = 0.0 s; event order agrees with the truth for 1334/1334 pairs.

## Anonymous tracks: identity and trajectory

| Track | Decision | True identity | Verdict | Samples | Position RMSE to surface: raw / smoothed | Smoothed RMSE to centre | Speed RMSE: raw differences / smoothed |
|-------|----------|---------------|---------|--------:|------------------------------------------|------------------------:|----------------------------------------|
| A:track_001 | U1 | F | correctly left anonymous | 95 | 0.241 / 0.298 m | 2.041 m | 3.259 / 0.024 m/s |
| A:track_002 | U2 | D | correctly left anonymous | 114 | 0.199 / 0.159 m | 2.103 m | 1.759 / 0.053 m/s |
| A:track_003 | U3 | I | correctly left anonymous | 120 | 0.206 / 0.204 m | 1.91 m | 1.583 / 0.062 m/s |
| A:track_004 | U4 | H | correctly left anonymous | 115 | 0.397 / 0.446 m | 1.988 m | 3.431 / 0.084 m/s |
| A:track_005 | U5 | E | correctly left anonymous | 86 | 0.371 / 0.39 m | 2.049 m | 3.669 / 0.048 m/s |
| A:track_006 | U6 | G | correctly left anonymous | 120 | 0.173 / 0.529 m | 1.449 m | 2.947 / 0.403 m/s |
| A:track_007 | U7 | J | correctly left anonymous | 120 | 0.206 / 0.459 m | 1.56 m | 3.568 / 0.418 m/s |
| A:track_008 | U9 | C | correctly left anonymous | 23 | 0.24 / 0.494 m | 1.693 m | 6.106 / 0.226 m/s |
| A:track_009 | U10 | E | correctly left anonymous | 9 | 0.196 / 0.555 m | 1.291 m | 8.446 / 0.301 m/s |
| A:track_010 | U11 | F | correctly left anonymous | 10 | 0.22 / 0.366 m | 1.363 m | 9.121 / 0.17 m/s |
| B:track_001 | U6 | G | correctly left anonymous | 75 | 0.193 / 0.194 m | 1.999 m | 0.278 / 0.021 m/s |
| B:track_002 | U5 | E | correctly left anonymous | 37 | 0.514 / 0.494 m | 1.907 m | 2.746 / 0.044 m/s |
| B:track_003 | U7 | J | correctly left anonymous | 75 | 0.17 / 0.169 m | 2.125 m | 0.737 / 0.024 m/s |
| B:track_004 | U3 | I | correctly left anonymous | 69 | 0.51 / 0.621 m | 1.501 m | 2.962 / 0.059 m/s |
| B:track_005 | U1 | F | correctly left anonymous | 73 | 0.277 / 0.321 m | 1.977 m | 2.834 / 0.053 m/s |
| B:track_006 | U4 | H | correctly left anonymous | 30 | 0.439 / 0.495 m | 1.902 m | 2.446 / 0.033 m/s |
| B:track_007 | A | A | correct | 119 | 0.198 / 0.18 m | 1.917 m | 2.054 / 0.067 m/s |
| B:track_008 | U5 | E | correctly left anonymous | 5 | 0.568 / 0.61 m | 1.799 m | 1.547 / 0.121 m/s |
| B:track_009 | U8 | H | correctly left anonymous | 3 | 0.646 / 0.511 m | 1.903 m | 5.084 / 0.039 m/s |

## Clearance at the true contacts

Per recorder, its track lying on the partner at the last 10 Hz sample at or before the contact: clearance (free distance from the recorder's footprint to the track's near surface), the true gap between the two vehicles' boxes at that instant, and the raw range from the radar.

| Contact | Recorder | Partner | Track | Seen before contact | Clearance | True gap | Error | Range |
|---------|----------|---------|-------|--------------------:|----------:|---------:|------:|------:|
| A + B | A | B | - | - s | - m | - m | - m | - m |
| A + B | B | A | B:track_007 | -0.05 s | 0.119 m | 0.0 m | 0.119 m | 0.236 m |

Surface distance = distance from a track point to the outline of the true vehicle's bounding box, i.e. where radar returns lie. Raw = median radar return of that sweep; smoothed = Kalman + RTS estimate; both on the same measured 10 Hz sweeps. Raw returns lie on the surface by construction, so smoothing cannot be expected to bring the position closer to it; its gain shows in the speed (raw differences of consecutive returns vs smoothed velocity). The distance to the centre includes the surface-to-centre offset. True identity = the vehicle whose box is closest (median <= 1.5 m).

## Clock-shift check (uses no ground truth)

Recorder B was rebuilt with its local clock reading +0.73 s later (its collision is then at local time 8.18 s), and alignment and fusion were rerun. Global graph identical: **yes**. B's offset_to_global changed by -0.73 s (expected -0.73 s).
