# Privileged evaluation - S13/run_0_platoon

This compares the finished reconstruction with `ground_truth/` (simulator state). The reconstruction never read it and was not changed by this evaluation.

**collision reconstructed: yes (1/1 vehicle contacts); associations correct: 2/2; anonymous: 5; max |t_global error| 0.0 s**

Privileged assumption: recorder raw clocks are CARLA simulator time.

## Collisions

| True contact | Sim time | Peak impulse | Reconstructed as | Participants correct | Report timing error |
|--------------|---------:|-------------:|------------------|----------------------|--------------------:|
| A + B | 2058.987 | 1093.1 | g21 | yes | 0.0 s |

Reconstructed COLLISION nodes that reproduce no true contact: none.

## Graph alignment accuracy

Local time at which each graph reads t_global = 0, against the true local time of the reference contact; the chain lists the matched collisions that aligned the graph.

| Graph | Status | Chain | Estimated (local) | True (local) | Error |
|-------|--------|-------|------------------:|-------------:|------:|
| A | ALIGNED | collision_001 | 6.2 | 6.2 | 0.0 s |
| B | ALIGNED | collision_001 | 6.2 | 6.2 | 0.0 s |

Relative clock offset B - A: estimated +0.000 s, true +0.000 s (error +0.000 s).

## Global event times

42 timed global nodes; max |t_global - true global time| = 0.0 s; event order agrees with the truth for 798/798 pairs.

## Anonymous tracks: identity and trajectory

| Track | Decision | True identity | Verdict | Samples | Position RMSE to surface: raw / smoothed | Smoothed RMSE to centre | Speed RMSE: raw differences / smoothed |
|-------|----------|---------------|---------|--------:|------------------------------------------|------------------------:|----------------------------------------|
| A:track_001 | B | B | correct | 115 | 0.244 / 0.311 m | 1.607 m | 0.827 / 0.118 m/s |
| A:track_002 | U1 | D | correctly left anonymous | 88 | 0.276 / 0.286 m | 1.983 m | 1.961 / 0.055 m/s |
| A:track_003 | U2 | C | correctly left anonymous | 18 | 0.487 / 0.469 m | 1.374 m | 6.339 / 0.052 m/s |
| B:track_001 | A | A | correct | 115 | 0.121 / 0.224 m | 1.434 m | 1.466 / 0.131 m/s |
| B:track_002 | U1 | D | correctly left anonymous | 91 | 0.402 / 0.436 m | 1.847 m | 3.412 / 0.056 m/s |
| B:track_003 | U2 | C | correctly left anonymous | 37 | 0.858 / 0.412 m | 1.593 m | 8.82 / 0.09 m/s |
| B:track_004 | U2 | C | correctly left anonymous | 13 | 0.561 / 0.629 m | 1.704 m | 2.024 / 0.052 m/s |

## Clearance at the true contacts

Per recorder, its track lying on the partner at the last 10 Hz sample at or before the contact: clearance (free distance from the recorder's footprint to the track's near surface), the true gap between the two vehicles' boxes at that instant, and the raw range from the radar.

| Contact | Recorder | Partner | Track | Seen before contact | Clearance | True gap | Error | Range |
|---------|----------|---------|-------|--------------------:|----------:|---------:|------:|------:|
| A + B | A | B | A:track_001 | 0.0 s | 0.228 m | 0.0 m | 0.228 m | 0.539 m |
| A + B | B | A | B:track_001 | 0.0 s | 0.342 m | 0.0 m | 0.342 m | 0.379 m |

Surface distance = distance from a track point to the outline of the true vehicle's bounding box, i.e. where radar returns lie. Raw = median radar return of that sweep; smoothed = Kalman + RTS estimate; both on the same measured 10 Hz sweeps. Raw returns lie on the surface by construction, so smoothing cannot be expected to bring the position closer to it; its gain shows in the speed (raw differences of consecutive returns vs smoothed velocity). The distance to the centre includes the surface-to-centre offset. True identity = the vehicle whose box is closest (median <= 1.5 m).

## Clock-shift check (uses no ground truth)

Recorder B was rebuilt with its local clock reading +0.73 s later (its collision is then at local time 6.93 s), and alignment and fusion were rerun. Global graph identical: **yes**. B's offset_to_global changed by -0.73 s (expected -0.73 s).
