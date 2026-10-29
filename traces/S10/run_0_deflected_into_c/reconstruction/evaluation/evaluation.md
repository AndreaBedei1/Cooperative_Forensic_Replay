# Privileged evaluation - S10/run_0_deflected_into_c

This compares the finished reconstruction with `ground_truth/` (simulator state). The reconstruction never read it and was not changed by this evaluation.

**collision reconstructed: yes (2/2 vehicle contacts); associations correct: 6/6; anonymous: 0; max |t_global error| 0.0 s**

Privileged assumption: recorder raw clocks are CARLA simulator time.

## Collisions

| True contact | Sim time | Peak impulse | Reconstructed as | Participants correct | Report timing error |
|--------------|---------:|-------------:|------------------|----------------------|--------------------:|
| A + B | 1990.896 | 10358.2 | g30 | yes | 0.0 s |
| A + C | 1991.796 | 2250.3 | g44 | yes | 0.0 s |

Reconstructed COLLISION nodes that reproduce no true contact: none.

## Graph alignment accuracy

Local time at which each graph reads t_global = 0, against the true local time of the reference contact; the chain lists the matched collisions that aligned the graph.

| Graph | Status | Chain | Estimated (local) | True (local) | Error |
|-------|--------|-------|------------------:|-------------:|------:|
| A | ALIGNED | collision_001 | 3.8 | 3.8 | 0.0 s |
| B | ALIGNED | collision_001 | 3.8 | 3.8 | 0.0 s |
| C | ALIGNED | collision_001 -> collision_002 | 3.8 | 3.8 | 0.0 s |

Relative clock offset B - A: estimated +0.000 s, true +0.000 s (error +0.000 s).

Relative clock offset C - A: estimated +0.000 s, true +0.000 s (error +0.000 s).

Relative clock offset C - B: estimated +0.000 s, true +0.000 s (error +0.000 s).

## Global event times

57 timed global nodes; max |t_global - true global time| = 0.0 s; event order agrees with the truth for 1518/1518 pairs.

## Anonymous tracks: identity and trajectory

| Track | Decision | True identity | Verdict | Samples | Position RMSE to surface: raw / smoothed | Smoothed RMSE to centre | Speed RMSE: raw differences / smoothed |
|-------|----------|---------------|---------|--------:|------------------------------------------|------------------------:|----------------------------------------|
| A:track_001 | C | C | correct | 140 | 0.191 / 0.26 m | 1.478 m | 3.672 / 0.075 m/s |
| A:track_002 | B | B | correct | 119 | 0.399 / 0.223 m | 1.018 m | 8.428 / 0.295 m/s |
| B:track_001 | C | C | correct | 121 | 0.145 / 0.173 m | 1.812 m | 2.864 / 0.271 m/s |
| B:track_002 | A | A | correct | 120 | 0.2 / 0.381 m | 1.88 m | 2.809 / 0.282 m/s |
| C:track_001 | A | A | correct | 136 | 0.242 / 0.376 m | 1.503 m | 3.267 / 0.131 m/s |
| C:track_002 | B | B | correct | 135 | 0.25 / 0.318 m | 1.634 m | 4.14 / 0.301 m/s |

## Clearance at the true contacts

Per recorder, its track lying on the partner at the last 10 Hz sample at or before the contact: clearance (free distance from the recorder's footprint to the track's near surface), the true gap between the two vehicles' boxes at that instant, and the raw range from the radar.

| Contact | Recorder | Partner | Track | Seen before contact | Clearance | True gap | Error | Range |
|---------|----------|---------|-------|--------------------:|----------:|---------:|------:|------:|
| A + B | A | B | A:track_002 | 0.0 s | 1.126 m | 0.0 m | 1.126 m | 3.314 m |
| A + B | B | A | B:track_002 | 0.0 s | 1.457 m | 0.0 m | 1.457 m | 2.231 m |
| A + C | A | C | A:track_001 | 0.0 s | 0.017 m | 0.0 m | 0.017 m | 1.41 m |
| A + C | C | A | C:track_001 | 0.0 s | 0.0 m | 0.0 m | 0.0 m | 1.349 m |

Surface distance = distance from a track point to the outline of the true vehicle's bounding box, i.e. where radar returns lie. Raw = median radar return of that sweep; smoothed = Kalman + RTS estimate; both on the same measured 10 Hz sweeps. Raw returns lie on the surface by construction, so smoothing cannot be expected to bring the position closer to it; its gain shows in the speed (raw differences of consecutive returns vs smoothed velocity). The distance to the centre includes the surface-to-centre offset. True identity = the vehicle whose box is closest (median <= 1.5 m).

## Clock-shift check (uses no ground truth)

Recorder C was rebuilt with its local clock reading +0.73 s later (its collision is then at local time 5.43 s), and alignment and fusion were rerun. Global graph identical: **yes**. C's offset_to_global changed by -0.73 s (expected -0.73 s).
