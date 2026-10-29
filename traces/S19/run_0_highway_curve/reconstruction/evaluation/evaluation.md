# Privileged evaluation - S19/run_0_highway_curve

This compares the finished reconstruction with `ground_truth/` (simulator state). The reconstruction never read it and was not changed by this evaluation.

**collision reconstructed: yes (1/1 vehicle contacts); associations correct: 2/2; anonymous: 16; max |t_global error| 0.0 s**

Privileged assumption: recorder raw clocks are CARLA simulator time.

## Collisions

| True contact | Sim time | Peak impulse | Reconstructed as | Participants correct | Report timing error |
|--------------|---------:|-------------:|------------------|----------------------|--------------------:|
| A + B | 31.077 | 7479.4 | g44 | yes | 0.0 s |

Reconstructed COLLISION nodes that reproduce no true contact: none.

## Graph alignment accuracy

Local time at which each graph reads t_global = 0, against the true local time of the reference contact; the chain lists the matched collisions that aligned the graph.

| Graph | Status | Chain | Estimated (local) | True (local) | Error |
|-------|--------|-------|------------------:|-------------:|------:|
| A | ALIGNED | collision_001 | 7.5 | 7.5 | 0.0 s |
| B | ALIGNED | collision_001 | 7.5 | 7.5 | 0.0 s |

Relative clock offset B - A: estimated +0.000 s, true +0.000 s (error +0.000 s).

## Global event times

70 timed global nodes; max |t_global - true global time| = 0.0 s; event order agrees with the truth for 2300/2300 pairs.

## Anonymous tracks: identity and trajectory

| Track | Decision | True identity | Verdict | Samples | Position RMSE to surface: raw / smoothed | Smoothed RMSE to centre | Speed RMSE: raw differences / smoothed |
|-------|----------|---------------|---------|--------:|------------------------------------------|------------------------:|----------------------------------------|
| A:track_001 | U1 | C | correctly left anonymous | 81 | 0.277 / 0.417 m | 1.563 m | 2.177 / 0.11 m/s |
| A:track_002 | U2 | D | correctly left anonymous | 119 | 0.322 / 0.443 m | 1.593 m | 5.062 / 0.155 m/s |
| A:track_003 | U3 | G | correctly left anonymous | 49 | 0.269 / 0.332 m | 1.954 m | 5.066 / 0.075 m/s |
| A:track_004 | U4 | F | correctly left anonymous | 24 | 0.245 / 0.311 m | 2.172 m | 1.304 / 0.262 m/s |
| A:track_005 | U6 | E | correctly left anonymous | 4 | 0.276 / 0.419 m | 1.575 m | 6.74 / 0.189 m/s |
| A:track_006 | B | B | correct | 117 | 0.354 / 0.425 m | 2.02 m | 2.521 / 0.099 m/s |
| A:track_007 | U5 | E | correctly left anonymous | 4 | 0.43 / 0.491 m | 0.977 m | 3.592 / 0.231 m/s |
| A:track_008 | U5 | E | correctly left anonymous | 4 | 0.344 / 0.321 m | 0.821 m | 19.845 / 0.121 m/s |
| A:track_009 | U5 | E | correctly left anonymous | 1 | 0.073 / 0.047 m | 1.055 m | - / 0.566 m/s |
| A:track_010 | U7 | G | correctly left anonymous | 5 | 0.426 / 0.616 m | 1.642 m | 9.914 / 0.074 m/s |
| A:track_011 | U8 | F | correctly left anonymous | 33 | 0.409 / 0.678 m | 0.691 m | 5.127 / 0.518 m/s |
| B:track_001 | U3 | G | correctly left anonymous | 72 | 0.318 / 0.332 m | 1.931 m | 7.103 / 0.062 m/s |
| B:track_002 | U5 | E | correctly left anonymous | 50 | 0.348 / 0.458 m | 1.648 m | 6.358 / 0.077 m/s |
| B:track_003 | U1 | C | correctly left anonymous | 105 | 0.345 / 0.502 m | 1.583 m | 4.14 / 0.368 m/s |
| B:track_004 | U2 | D | correctly left anonymous | 120 | 0.194 / 0.437 m | 1.106 m | 5.034 / 0.31 m/s |
| B:track_005 | A | A | correct | 12 | 0.152 / 0.174 m | 2.013 m | 1.207 / 0.064 m/s |
| B:track_006 | U9 | G | correctly left anonymous | 3 | 0.302 / 0.248 m | 2.011 m | 7.604 / 0.158 m/s |
| B:track_007 | U8 | F | correctly left anonymous | 25 | 0.376 / 0.667 m | 0.587 m | 4.717 / 0.496 m/s |

## Clearance at the true contacts

Per recorder, its track lying on the partner at the last 10 Hz sample at or before the contact: clearance (free distance from the recorder's footprint to the track's near surface), the true gap between the two vehicles' boxes at that instant, and the raw range from the radar.

| Contact | Recorder | Partner | Track | Seen before contact | Clearance | True gap | Error | Range |
|---------|----------|---------|-------|--------------------:|----------:|---------:|------:|------:|
| A + B | A | B | A:track_006 | 0.0 s | 0.161 m | 0.0 m | 0.161 m | 0.915 m |
| A + B | B | A | B:track_005 | 0.9 s | 4.847 m | 4.498 m | 0.349 m | 7.094 m |

Surface distance = distance from a track point to the outline of the true vehicle's bounding box, i.e. where radar returns lie. Raw = median radar return of that sweep; smoothed = Kalman + RTS estimate; both on the same measured 10 Hz sweeps. Raw returns lie on the surface by construction, so smoothing cannot be expected to bring the position closer to it; its gain shows in the speed (raw differences of consecutive returns vs smoothed velocity). The distance to the centre includes the surface-to-centre offset. True identity = the vehicle whose box is closest (median <= 1.5 m).

## Clock-shift check (uses no ground truth)

Recorder B was rebuilt with its local clock reading +0.73 s later (its collision is then at local time 8.23 s), and alignment and fusion were rerun. Global graph identical: **yes**. B's offset_to_global changed by -0.73 s (expected -0.73 s).
