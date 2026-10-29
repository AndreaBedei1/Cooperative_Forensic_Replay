# Privileged evaluation - S18/run_0_collision_ambiguity

This compares the finished reconstruction with `ground_truth/` (simulator state). The reconstruction never read it and was not changed by this evaluation.

**collision reconstructed: yes (1/1 vehicle contacts); associations correct: 1/1; anonymous: 15; max |t_global error| 0.0 s**

Privileged assumption: recorder raw clocks are CARLA simulator time.

## Collisions

| True contact | Sim time | Peak impulse | Reconstructed as | Participants correct | Report timing error |
|--------------|---------:|-------------:|------------------|----------------------|--------------------:|
| A + B | 2156.015 | 1168.6 | g27 | yes | 0.0 s |

Reconstructed COLLISION nodes that reproduce no true contact: none.

## Graph alignment accuracy

Local time at which each graph reads t_global = 0, against the true local time of the reference contact; the chain lists the matched collisions that aligned the graph.

| Graph | Status | Chain | Estimated (local) | True (local) | Error |
|-------|--------|-------|------------------:|-------------:|------:|
| A | ALIGNED | collision_001 | 7.65 | 7.65 | 0.0 s |
| B | ALIGNED | collision_001 | 7.65 | 7.65 | 0.0 s |

Relative clock offset B - A: estimated +0.000 s, true +0.000 s (error +0.000 s).

## Global event times

57 timed global nodes; max |t_global - true global time| = 0.0 s; event order agrees with the truth for 1493/1493 pairs.

## Anonymous tracks: identity and trajectory

| Track | Decision | True identity | Verdict | Samples | Position RMSE to surface: raw / smoothed | Smoothed RMSE to centre | Speed RMSE: raw differences / smoothed |
|-------|----------|---------------|---------|--------:|------------------------------------------|------------------------:|----------------------------------------|
| A:track_001 | U1 | C | correctly left anonymous | 90 | 0.233 / 0.24 m | 2.21 m | 1.487 / 0.05 m/s |
| A:track_002 | B | B | correct | 120 | 0.144 / 0.184 m | 2.225 m | 1.35 / 0.069 m/s |
| A:track_003 | U2 | E | correctly left anonymous | 63 | 0.12 / 0.337 m | 1.577 m | 1.105 / 0.284 m/s |
| A:track_004 | U3 | F | correctly left anonymous | 55 | 0.106 / 0.328 m | 1.583 m | 1.153 / 0.234 m/s |
| A:track_005 | U5 | D | correctly left anonymous | 91 | 0.224 / 0.387 m | 2.066 m | 2.347 / 0.072 m/s |
| A:track_006 | U6 | H | correctly left anonymous | 43 | 0.245 / 0.199 m | 1.911 m | 2.318 / 0.038 m/s |
| A:track_007 | U6 | H | correctly left anonymous | 8 | 0.244 / 0.237 m | 1.631 m | 5.85 / 0.008 m/s |
| A:track_008 | U4 | G | correctly left anonymous | 8 | 0.072 / 0.068 m | 2.189 m | 0.385 / 0.01 m/s |
| A:track_009 | U7 | E | correctly left anonymous | 20 | 0.114 / 0.759 m | 0.354 m | 4.235 / 0.359 m/s |
| A:track_010 | U8 | F | correctly left anonymous | 19 | 0.11 / 0.742 m | 0.339 m | 4.023 / 0.35 m/s |
| B:track_001 | U4 | G | correctly left anonymous | 120 | 0.073 / 0.071 m | 2.186 m | 0.35 / 0.009 m/s |
| B:track_002 | U1 | C | correctly left anonymous | 120 | 0.173 / 0.284 m | 1.388 m | 1.702 / 0.154 m/s |
| B:track_003 | U5 | D | correctly left anonymous | 120 | 0.171 / 0.344 m | 1.18 m | 1.927 / 0.28 m/s |
| B:track_004 | U6 | H | correctly left anonymous | 115 | 0.214 / 0.256 m | 1.879 m | 2.592 / 0.028 m/s |
| B:track_005 | U7 | E | correctly left anonymous | 28 | 0.152 / 0.579 m | 0.696 m | 3.544 / 0.395 m/s |
| B:track_006 | U9 | F | correctly left anonymous | 26 | 0.123 / 0.632 m | 0.619 m | 3.208 / 0.377 m/s |

## Clearance at the true contacts

Per recorder, its track lying on the partner at the last 10 Hz sample at or before the contact: clearance (free distance from the recorder's footprint to the track's near surface), the true gap between the two vehicles' boxes at that instant, and the raw range from the radar.

| Contact | Recorder | Partner | Track | Seen before contact | Clearance | True gap | Error | Range |
|---------|----------|---------|-------|--------------------:|----------:|---------:|------:|------:|
| A + B | A | B | A:track_002 | -0.05 s | 0.0 m | 0.0 m | 0.0 m | 0.144 m |
| A + B | B | A | - | - s | - m | - m | - m | - m |

Surface distance = distance from a track point to the outline of the true vehicle's bounding box, i.e. where radar returns lie. Raw = median radar return of that sweep; smoothed = Kalman + RTS estimate; both on the same measured 10 Hz sweeps. Raw returns lie on the surface by construction, so smoothing cannot be expected to bring the position closer to it; its gain shows in the speed (raw differences of consecutive returns vs smoothed velocity). The distance to the centre includes the surface-to-centre offset. True identity = the vehicle whose box is closest (median <= 1.5 m).

## Clock-shift check (uses no ground truth)

Recorder B was rebuilt with its local clock reading +0.73 s later (its collision is then at local time 8.38 s), and alignment and fusion were rerun. Global graph identical: **yes**. B's offset_to_global changed by -0.73 s (expected -0.73 s).
