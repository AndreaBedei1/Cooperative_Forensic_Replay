# Privileged evaluation - S14/run_0_surrounded

This compares the finished reconstruction with `ground_truth/` (simulator state). The reconstruction never read it and was not changed by this evaluation.

**collision reconstructed: yes (1/1 vehicle contacts); associations correct: 2/2; anonymous: 21; max |t_global error| 0.0 s**

Privileged assumption: recorder raw clocks are CARLA simulator time.

## Collisions

| True contact | Sim time | Peak impulse | Reconstructed as | Participants correct | Report timing error |
|--------------|---------:|-------------:|------------------|----------------------|--------------------:|
| A + B | 2091.759 | 255.0 | g39 | yes | 0.0 s |

Reconstructed COLLISION nodes that reproduce no true contact: none.

## Graph alignment accuracy

Local time at which each graph reads t_global = 0, against the true local time of the reference contact; the chain lists the matched collisions that aligned the graph.

| Graph | Status | Chain | Estimated (local) | True (local) | Error |
|-------|--------|-------|------------------:|-------------:|------:|
| A | ALIGNED | collision_001 | 7.75 | 7.75 | 0.0 s |
| B | ALIGNED | collision_001 | 7.75 | 7.75 | 0.0 s |

Relative clock offset B - A: estimated +0.000 s, true +0.000 s (error +0.000 s).

## Global event times

60 timed global nodes; max |t_global - true global time| = 0.0 s; event order agrees with the truth for 1692/1692 pairs.

## Anonymous tracks: identity and trajectory

| Track | Decision | True identity | Verdict | Samples | Position RMSE to surface: raw / smoothed | Smoothed RMSE to centre | Speed RMSE: raw differences / smoothed |
|-------|----------|---------------|---------|--------:|------------------------------------------|------------------------:|----------------------------------------|
| A:track_001 | U1 | P | correctly left anonymous | 120 | 0.137 / 0.135 m | 2.145 m | 0.217 / 0.015 m/s |
| A:track_002 | U2 | C | correctly left anonymous | 120 | 0.322 / 0.359 m | 2.104 m | 1.88 / 0.048 m/s |
| A:track_003 | B | B | correct | 120 | 0.092 / 0.094 m | 1.184 m | 1.025 / 0.141 m/s |
| A:track_004 | U3 | D | correctly left anonymous | 119 | 0.158 / 0.16 m | 2.113 m | 0.856 / 0.059 m/s |
| A:track_005 | U9 | J | correctly left anonymous | 7 | 0.175 / 0.237 m | 1.925 m | 0.807 / 0.257 m/s |
| A:track_006 | U7 | G | correctly left anonymous | 46 | 0.213 / 0.29 m | 2.002 m | 3.955 / 0.105 m/s |
| A:track_007 | U5 | E | correctly left anonymous | 42 | 0.253 / 0.314 m | 2.165 m | 3.29 / 0.041 m/s |
| A:track_008 | U4 | F | correctly left anonymous | 33 | 0.306 / 0.353 m | 1.767 m | 3.874 / 0.047 m/s |
| A:track_009 | U11 | J | correctly left anonymous | 13 | 0.383 / 0.428 m | 1.362 m | 5.96 / 0.123 m/s |
| B:track_001 | U3 | D | correctly left anonymous | 120 | 0.176 / 0.173 m | 2.102 m | 0.511 / 0.04 m/s |
| B:track_002 | A | A | correct | 120 | 0.161 / 0.436 m | 1.186 m | 2.825 / 0.145 m/s |
| B:track_003 | U1 | P | correctly left anonymous | 120 | 0.208 / 0.272 m | 2.014 m | 1.061 / 0.038 m/s |
| B:track_004 | U4 | F | correctly left anonymous | 35 | 0.49 / 0.618 m | 1.465 m | 6.005 / 0.031 m/s |
| B:track_005 | U2 | C | correctly left anonymous | 119 | 0.315 / 0.328 m | 2.121 m | 1.724 / 0.037 m/s |
| B:track_006 | U5 | E | correctly left anonymous | 119 | 0.346 / 0.44 m | 1.976 m | 3.609 / 0.051 m/s |
| B:track_007 | U6 | H | correctly left anonymous | 21 | 0.598 / 0.723 m | 1.67 m | 3.704 / 0.05 m/s |
| B:track_008 | U7 | G | correctly left anonymous | 31 | 0.44 / 0.551 m | 1.724 m | 2.777 / 0.064 m/s |
| B:track_009 | U7 | G | correctly left anonymous | 24 | 0.196 / 0.172 m | 2.104 m | 2.284 / 0.118 m/s |
| B:track_010 | U4 | F | correctly left anonymous | 29 | 0.377 / 0.39 m | 1.726 m | 2.833 / 0.051 m/s |
| B:track_011 | U8 | H | correctly left anonymous | 5 | 0.56 / 0.698 m | 1.714 m | 4.029 / 0.053 m/s |
| B:track_012 | U10 | H | correctly left anonymous | 2 | 0.327 / 0.27 m | 2.202 m | 1.582 / 0.001 m/s |
| B:track_013 | U11 | J | correctly left anonymous | 31 | 0.297 / 0.401 m | 1.714 m | 3.588 / 0.144 m/s |
| B:track_014 | U12 | H | correctly left anonymous | 2 | 0.272 / 0.19 m | 1.066 m | 20.511 / 0.14 m/s |

## Clearance at the true contacts

Per recorder, its track lying on the partner at the last 10 Hz sample at or before the contact: clearance (free distance from the recorder's footprint to the track's near surface), the true gap between the two vehicles' boxes at that instant, and the raw range from the radar.

| Contact | Recorder | Partner | Track | Seen before contact | Clearance | True gap | Error | Range |
|---------|----------|---------|-------|--------------------:|----------:|---------:|------:|------:|
| A + B | A | B | A:track_003 | -0.05 s | 0.089 m | 0.0 m | 0.089 m | 0.295 m |
| A + B | B | A | B:track_002 | -0.05 s | 0.795 m | 0.0 m | 0.795 m | 1.185 m |

Surface distance = distance from a track point to the outline of the true vehicle's bounding box, i.e. where radar returns lie. Raw = median radar return of that sweep; smoothed = Kalman + RTS estimate; both on the same measured 10 Hz sweeps. Raw returns lie on the surface by construction, so smoothing cannot be expected to bring the position closer to it; its gain shows in the speed (raw differences of consecutive returns vs smoothed velocity). The distance to the centre includes the surface-to-centre offset. True identity = the vehicle whose box is closest (median <= 1.5 m).

## Clock-shift check (uses no ground truth)

Recorder B was rebuilt with its local clock reading +0.73 s later (its collision is then at local time 8.48 s), and alignment and fusion were rerun. Global graph identical: **yes**. B's offset_to_global changed by -0.73 s (expected -0.73 s).
