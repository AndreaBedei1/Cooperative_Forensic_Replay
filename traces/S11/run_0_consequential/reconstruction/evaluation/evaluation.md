# Privileged evaluation - S11/run_0_consequential

This compares the finished reconstruction with `ground_truth/` (simulator state). The reconstruction never read it and was not changed by this evaluation.

**collision reconstructed: yes (2/2 vehicle contacts); associations correct: 4/4; anonymous: 0; max |t_global error| 0.0 s**

Privileged assumption: recorder raw clocks are CARLA simulator time.

## Collisions

| True contact | Sim time | Peak impulse | Reconstructed as | Participants correct | Report timing error |
|--------------|---------:|-------------:|------------------|----------------------|--------------------:|
| A + B | 2011.421 | 4243.5 | g24 | yes | 0.0 s |
| A + C | 2012.471 | 839.7 | g39 | yes | 0.0 s |

Reconstructed COLLISION nodes that reproduce no true contact: none.

## Graph alignment accuracy

Local time at which each graph reads t_global = 0, against the true local time of the reference contact; the chain lists the matched collisions that aligned the graph.

| Graph | Status | Chain | Estimated (local) | True (local) | Error |
|-------|--------|-------|------------------:|-------------:|------:|
| A | ALIGNED | collision_001 | 5.55 | 5.55 | 0.0 s |
| B | ALIGNED | collision_001 | 5.55 | 5.55 | 0.0 s |
| C | ALIGNED | collision_001 -> collision_002 | 5.55 | 5.55 | 0.0 s |

Relative clock offset B - A: estimated +0.000 s, true +0.000 s (error +0.000 s).

Relative clock offset C - A: estimated +0.000 s, true +0.000 s (error +0.000 s).

Relative clock offset C - B: estimated +0.000 s, true +0.000 s (error +0.000 s).

## Global event times

49 timed global nodes; max |t_global - true global time| = 0.0 s; event order agrees with the truth for 1071/1071 pairs.

## Anonymous tracks: identity and trajectory

| Track | Decision | True identity | Verdict | Samples | Position RMSE to surface: raw / smoothed | Smoothed RMSE to centre | Speed RMSE: raw differences / smoothed |
|-------|----------|---------------|---------|--------:|------------------------------------------|------------------------:|----------------------------------------|
| A:track_001 | C | C | correct | 120 | 0.134 / 0.21 m | 2.781 m | 0.983 / 0.04 m/s |
| B:track_001 | A | A | correct | 120 | 0.42 / 0.412 m | 1.751 m | 2.515 / 0.145 m/s |
| B:track_002 | C | C | correct | 116 | 0.285 / 0.376 m | 2.61 m | 6.248 / 0.175 m/s |
| C:track_001 | A | A | correct | 38 | 0.162 / 0.182 m | 1.947 m | 0.292 / 0.128 m/s |

## Clearance at the true contacts

Per recorder, its track lying on the partner at the last 10 Hz sample at or before the contact: clearance (free distance from the recorder's footprint to the track's near surface), the true gap between the two vehicles' boxes at that instant, and the raw range from the radar.

| Contact | Recorder | Partner | Track | Seen before contact | Clearance | True gap | Error | Range |
|---------|----------|---------|-------|--------------------:|----------:|---------:|------:|------:|
| A + B | A | B | - | - s | - m | - m | - m | - m |
| A + B | B | A | B:track_001 | -0.05 s | 0.042 m | 0.0 m | 0.042 m | 0.36 m |
| A + C | A | C | A:track_001 | 0.0 s | 0.0 m | 0.0 m | 0.0 m | 0.338 m |
| A + C | C | A | C:track_001 | 0.2 s | 1.064 m | 0.028 m | 1.036 m | 3.148 m |

Surface distance = distance from a track point to the outline of the true vehicle's bounding box, i.e. where radar returns lie. Raw = median radar return of that sweep; smoothed = Kalman + RTS estimate; both on the same measured 10 Hz sweeps. Raw returns lie on the surface by construction, so smoothing cannot be expected to bring the position closer to it; its gain shows in the speed (raw differences of consecutive returns vs smoothed velocity). The distance to the centre includes the surface-to-centre offset. True identity = the vehicle whose box is closest (median <= 1.5 m).

## Clock-shift check (uses no ground truth)

Recorder C was rebuilt with its local clock reading +0.73 s later (its collision is then at local time 7.33 s), and alignment and fusion were rerun. Global graph identical: **yes**. C's offset_to_global changed by -0.73 s (expected -0.73 s).
