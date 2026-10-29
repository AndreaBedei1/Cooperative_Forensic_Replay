# Privileged evaluation - S17/run_0_occlusion_reappearance

This compares the finished reconstruction with `ground_truth/` (simulator state). The reconstruction never read it and was not changed by this evaluation.

**collision reconstructed: yes (1/1 vehicle contacts); associations correct: 2/2; anonymous: 12; max |t_global error| 0.0 s**

Privileged assumption: recorder raw clocks are CARLA simulator time.

## Collisions

| True contact | Sim time | Peak impulse | Reconstructed as | Participants correct | Report timing error |
|--------------|---------:|-------------:|------------------|----------------------|--------------------:|
| A + B | 2139.544 | 389.3 | g43 | yes | 0.0 s |

Reconstructed COLLISION nodes that reproduce no true contact: none.

## Graph alignment accuracy

Local time at which each graph reads t_global = 0, against the true local time of the reference contact; the chain lists the matched collisions that aligned the graph.

| Graph | Status | Chain | Estimated (local) | True (local) | Error |
|-------|--------|-------|------------------:|-------------:|------:|
| A | ALIGNED | collision_001 | 7.3 | 7.3 | 0.0 s |
| B | ALIGNED | collision_001 | 7.3 | 7.3 | 0.0 s |

Relative clock offset B - A: estimated +0.000 s, true +0.000 s (error +0.000 s).

## Global event times

67 timed global nodes; max |t_global - true global time| = 0.0 s; event order agrees with the truth for 2093/2093 pairs.

## Anonymous tracks: identity and trajectory

| Track | Decision | True identity | Verdict | Samples | Position RMSE to surface: raw / smoothed | Smoothed RMSE to centre | Speed RMSE: raw differences / smoothed |
|-------|----------|---------------|---------|--------:|------------------------------------------|------------------------:|----------------------------------------|
| A:track_001 | U1 | V | correctly left anonymous | 120 | 0.132 / 0.211 m | 2.804 m | 3.193 / 0.039 m/s |
| A:track_002 | U2 | D | correctly left anonymous | 49 | 0.407 / 0.393 m | 2.004 m | 1.391 / 0.041 m/s |
| A:track_003 | U3 | E | correctly left anonymous | 32 | 0.466 / 0.588 m | 1.68 m | 4.972 / 0.079 m/s |
| A:track_004 | U4 | C | correctly left anonymous | 45 | 0.371 / 0.536 m | 1.511 m | 6.606 / 0.124 m/s |
| A:track_005 | B | B | correct | 111 | 0.144 / 0.424 m | 1.631 m | 1.603 / 0.499 m/s |
| A:track_006 | U2 | D | correctly left anonymous | 55 | 0.43 / 0.542 m | 1.861 m | 6.078 / 0.061 m/s |
| A:track_007 | U4 | C | correctly left anonymous | 56 | 0.274 / 0.269 m | 2.149 m | 2.728 / 0.071 m/s |
| A:track_008 | U5 | E | correctly left anonymous | 29 | 0.322 / 0.542 m | 1.64 m | 7.904 / 0.221 m/s |
| B:track_001 | U4 | C | correctly left anonymous | 81 | 0.312 / 0.295 m | 2.106 m | 1.354 / 0.026 m/s |
| B:track_002 | U2 | D | correctly left anonymous | 50 | 0.423 / 0.503 m | 1.94 m | 3.759 / 0.071 m/s |
| B:track_003 | U1 | V | correctly left anonymous | 79 | 0.096 / 0.376 m | 1.527 m | 1.683 / 0.459 m/s |
| B:track_004 | U3 | E | correctly left anonymous | 30 | 0.446 / 0.586 m | 1.682 m | 3.962 / 0.052 m/s |
| B:track_005 | A | A | correct | 90 | 0.05 / 0.133 m | 0.906 m | 2.515 / 0.213 m/s |
| B:track_006 | U2 | D | correctly left anonymous | 9 | 0.531 / 0.574 m | 1.814 m | 5.484 / 0.233 m/s |

## Clearance at the true contacts

Per recorder, its track lying on the partner at the last 10 Hz sample at or before the contact: clearance (free distance from the recorder's footprint to the track's near surface), the true gap between the two vehicles' boxes at that instant, and the raw range from the radar.

| Contact | Recorder | Partner | Track | Seen before contact | Clearance | True gap | Error | Range |
|---------|----------|---------|-------|--------------------:|----------:|---------:|------:|------:|
| A + B | A | B | A:track_005 | 0.0 s | 0.481 m | 0.0 m | 0.481 m | 1.484 m |
| A + B | B | A | B:track_005 | 0.0 s | 0.0 m | 0.0 m | 0.0 m | 1.008 m |

Surface distance = distance from a track point to the outline of the true vehicle's bounding box, i.e. where radar returns lie. Raw = median radar return of that sweep; smoothed = Kalman + RTS estimate; both on the same measured 10 Hz sweeps. Raw returns lie on the surface by construction, so smoothing cannot be expected to bring the position closer to it; its gain shows in the speed (raw differences of consecutive returns vs smoothed velocity). The distance to the centre includes the surface-to-centre offset. True identity = the vehicle whose box is closest (median <= 1.5 m).

## Clock-shift check (uses no ground truth)

Recorder B was rebuilt with its local clock reading +0.73 s later (its collision is then at local time 8.03 s), and alignment and fusion were rerun. Global graph identical: **yes**. B's offset_to_global changed by -0.73 s (expected -0.73 s).
