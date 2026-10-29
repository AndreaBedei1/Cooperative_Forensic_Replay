# Privileged evaluation - S16/run_0_overtaking

This compares the finished reconstruction with `ground_truth/` (simulator state). The reconstruction never read it and was not changed by this evaluation.

**collision reconstructed: yes (1/1 vehicle contacts); associations correct: 2/2; anonymous: 19; max |t_global error| 0.0 s**

Privileged assumption: recorder raw clocks are CARLA simulator time.

## Collisions

| True contact | Sim time | Peak impulse | Reconstructed as | Participants correct | Report timing error |
|--------------|---------:|-------------:|------------------|----------------------|--------------------:|
| A + B | 2122.923 | 191.8 | g47 | yes | 0.0 s |

Reconstructed COLLISION nodes that reproduce no true contact: none.

## Graph alignment accuracy

Local time at which each graph reads t_global = 0, against the true local time of the reference contact; the chain lists the matched collisions that aligned the graph.

| Graph | Status | Chain | Estimated (local) | True (local) | Error |
|-------|--------|-------|------------------:|-------------:|------:|
| A | ALIGNED | collision_001 | 6.75 | 6.75 | 0.0 s |
| B | ALIGNED | collision_001 | 6.75 | 6.75 | 0.0 s |

Relative clock offset B - A: estimated +0.000 s, true +0.000 s (error +0.000 s).

## Global event times

81 timed global nodes; max |t_global - true global time| = 0.0 s; event order agrees with the truth for 3099/3099 pairs.

## Anonymous tracks: identity and trajectory

| Track | Decision | True identity | Verdict | Samples | Position RMSE to surface: raw / smoothed | Smoothed RMSE to centre | Speed RMSE: raw differences / smoothed |
|-------|----------|---------------|---------|--------:|------------------------------------------|------------------------:|----------------------------------------|
| A:track_001 | U1 | H | correctly left anonymous | 108 | 0.207 / 0.292 m | 2.014 m | 1.982 / 0.06 m/s |
| A:track_002 | U2 | I | correctly left anonymous | 36 | 0.446 / 0.448 m | 1.664 m | 3.17 / 0.065 m/s |
| A:track_003 | U3 | F | correctly left anonymous | 118 | 0.321 / 0.327 m | 1.776 m | 4.687 / 0.056 m/s |
| A:track_004 | U4 | D | correctly left anonymous | 36 | 0.42 / 0.503 m | 1.768 m | 2.408 / 0.087 m/s |
| A:track_005 | U5 | E | correctly left anonymous | 6 | 0.234 / 0.239 m | 2.27 m | 0.658 / 0.027 m/s |
| A:track_006 | B | B | correct | 116 | 0.22 / 0.385 m | 1.218 m | 4.643 / 0.339 m/s |
| A:track_007 | U4 | D | correctly left anonymous | 65 | 0.286 / 0.469 m | 1.821 m | 6.552 / 0.082 m/s |
| A:track_008 | U8 | G | correctly left anonymous | 55 | 1.15 / 1.206 m | 2.096 m | 6.108 / 1.039 m/s |
| A:track_009 | U10 | C | correctly left anonymous | 20 | 0.279 / 0.282 m | 2.189 m | 1.951 / 0.032 m/s |
| A:track_010 | U12 | E | correctly left anonymous | 37 | 0.207 / 0.515 m | 0.824 m | 3.51 / 0.48 m/s |
| A:track_011 | U11 | I | correctly left anonymous | 8 | 0.294 / 0.395 m | 1.67 m | 5.224 / 0.184 m/s |
| B:track_001 | A | A | correct | 120 | 0.182 / 0.334 m | 1.436 m | 1.26 / 0.333 m/s |
| B:track_002 | U3 | F | correctly left anonymous | 119 | 0.41 / 0.492 m | 1.636 m | 4.182 / 0.076 m/s |
| B:track_003 | U6 | E | correctly left anonymous | 53 | 0.284 / 0.45 m | 1.244 m | 2.97 / 0.242 m/s |
| B:track_004 | U7 | G | correctly left anonymous | 27 | 0.448 / 0.557 m | 1.715 m | 3.184 / 0.069 m/s |
| B:track_005 | U1 | H | correctly left anonymous | 106 | 0.21 / 0.231 m | 2.04 m | 3.08 / 0.083 m/s |
| B:track_006 | U4 | D | correctly left anonymous | 61 | 0.269 / 0.415 m | 1.854 m | 4.865 / 0.136 m/s |
| B:track_007 | U8 | G | correctly left anonymous | 53 | 0.352 / 0.423 m | 1.853 m | 5.555 / 0.13 m/s |
| B:track_008 | U9 | C | correctly left anonymous | 8 | 0.189 / 0.201 m | 1.119 m | 3.75 / 0.111 m/s |
| B:track_009 | U11 | I | correctly left anonymous | 13 | 0.569 / 0.595 m | 1.4 m | 6.795 / 0.208 m/s |
| B:track_010 | U12 | E | correctly left anonymous | 18 | 0.201 / 0.34 m | 1.095 m | 3.92 / 0.253 m/s |

## Clearance at the true contacts

Per recorder, its track lying on the partner at the last 10 Hz sample at or before the contact: clearance (free distance from the recorder's footprint to the track's near surface), the true gap between the two vehicles' boxes at that instant, and the raw range from the radar.

| Contact | Recorder | Partner | Track | Seen before contact | Clearance | True gap | Error | Range |
|---------|----------|---------|-------|--------------------:|----------:|---------:|------:|------:|
| A + B | A | B | A:track_006 | -0.05 s | 0.219 m | 0.0 m | 0.219 m | 1.55 m |
| A + B | B | A | B:track_001 | -0.05 s | 0.271 m | 0.0 m | 0.271 m | 1.033 m |

Surface distance = distance from a track point to the outline of the true vehicle's bounding box, i.e. where radar returns lie. Raw = median radar return of that sweep; smoothed = Kalman + RTS estimate; both on the same measured 10 Hz sweeps. Raw returns lie on the surface by construction, so smoothing cannot be expected to bring the position closer to it; its gain shows in the speed (raw differences of consecutive returns vs smoothed velocity). The distance to the centre includes the surface-to-centre offset. True identity = the vehicle whose box is closest (median <= 1.5 m).

## Clock-shift check (uses no ground truth)

Recorder B was rebuilt with its local clock reading +0.73 s later (its collision is then at local time 7.48 s), and alignment and fusion were rerun. Global graph identical: **yes**. B's offset_to_global changed by -0.73 s (expected -0.73 s).
