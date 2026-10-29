# Road-user fusion against ground truth - S17/run_0_occlusion_reappearance

Privileged evaluation (ground truth used here only). Assumptions: recorder raw clocks are CARLA simulator time; a vehicle box is centred on its origin in the horizontal plane.

## Track identity decisions (aligned recorders)

| Track | Decision | Status | By | True identity | Purity | Verdict |
|-------|----------|--------|----|---------------|-------:|---------|
| A:track_001 | U1 | ANONYMOUS | - | V | 1.000 | anonymous (non-recording road user V) |
| A:track_002 | U2 | ANONYMOUS | - | D | 1.000 | anonymous (non-recording road user D) |
| A:track_003 | U3 | ANONYMOUS | - | E | 1.000 | anonymous (non-recording road user E) |
| A:track_004 | U4 | ANONYMOUS | - | C | 1.000 | anonymous (non-recording road user C) |
| A:track_005 | B | ASSOCIATED | collision | B | 1.000 | correct link |
| A:track_006 | U2 | ANONYMOUS | - | D | 1.000 | anonymous (non-recording road user D) |
| A:track_007 | U4 | ANONYMOUS | - | C | 1.000 | anonymous (non-recording road user C) |
| A:track_008 | U5 | ANONYMOUS | - | E | 1.000 | anonymous (non-recording road user E) |
| B:track_001 | U4 | ANONYMOUS | - | C | 1.000 | anonymous (non-recording road user C) |
| B:track_002 | U2 | ANONYMOUS | - | D | 1.000 | anonymous (non-recording road user D) |
| B:track_003 | U1 | ANONYMOUS | - | V | 1.000 | anonymous (non-recording road user V) |
| B:track_004 | U3 | ANONYMOUS | - | E | 1.000 | anonymous (non-recording road user E) |
| B:track_005 | A | ASSOCIATED | collision | A | 1.000 | correct link |
| B:track_006 | U2 | ANONYMOUS | - | D | 1.000 | anonymous (non-recording road user D) |

Counts: anonymous: 12, correct link: 2

## Anonymous entities

| Entity | Source tracks | True identity | Recorder? | Purity |
|--------|---------------|---------------|-----------|-------:|
| U1 | A:track_001, B:track_003 | V | no | 1.000 |
| U2 | A:track_002, B:track_002, A:track_006, B:track_006 | D | no | 1.000 |
| U3 | A:track_003, B:track_004 | E | no | 1.000 |
| U4 | A:track_004, B:track_001, A:track_007 | C | no | 1.000 |
| U5 | A:track_008 | E | no | 1.000 |

Merges over pairs of anonymous tracks: correct 11, false 0, missed 2.
Fragmentation (true road user -> entities): C -> U4, D -> U2, E -> U3/U5, V -> U1

## Fused state errors (against the majority identity, 425 pure states; 0 impure states where a source track was on another body, excluded)

| Quantity | n | median | q25 | q75 | IQR | p90 | p95 | max |
|----------|--:|-------:|----:|----:|----:|----:|----:|----:|
| centre_error_m | 425 | 0.294 | 0.148 | 0.596 | 0.448 | 0.651 | 0.679 | 0.901 |
| coverage_s | 5 | 11.950 | 3.800 | 11.950 | 8.150 | 11.950 | 11.950 | 11.950 |
| heading_error_deg | 425 | 0.490 | 0.218 | 0.956 | 0.738 | 1.484 | 1.778 | 7.617 |
| length_error_m | 5 | 0.192 | 0.086 | 0.192 | 0.106 | 0.778 | 0.974 | 1.169 |
| normalised_centre_error | 425 | 2.748 | 1.584 | 5.742 | 4.158 | 8.661 | 8.990 | 10.383 |
| single_track_nominal_centre_error_m | 423 | 0.439 | 0.336 | 0.578 | 0.242 | 0.769 | 0.858 | 1.231 |
| speed_error_mps | 425 | 0.034 | 0.014 | 0.060 | 0.046 | 0.127 | 0.195 | 0.479 |
| velocity_error_mps | 425 | 0.110 | 0.050 | 0.186 | 0.136 | 0.301 | 0.438 | 1.715 |
| width_error_m | 5 | 0.107 | 0.107 | 0.263 | 0.156 | 0.263 | 0.263 | 0.263 |

### Method: box_fit

| Quantity | n | median | q25 | q75 | IQR | p90 | p95 | max |
|----------|--:|-------:|----:|----:|----:|----:|----:|----:|
| centre_error_m | 249 | 0.233 | 0.152 | 0.584 | 0.432 | 0.655 | 0.669 | 0.727 |
| heading_error_deg | 249 | 0.329 | 0.179 | 0.709 | 0.530 | 1.006 | 1.217 | 2.188 |
| speed_error_mps | 249 | 0.031 | 0.010 | 0.046 | 0.036 | 0.079 | 0.129 | 0.308 |
| velocity_error_mps | 249 | 0.076 | 0.043 | 0.146 | 0.103 | 0.208 | 0.265 | 0.368 |

### Method: covariance_intersection

| Quantity | n | median | q25 | q75 | IQR | p90 | p95 | max |
|----------|--:|-------:|----:|----:|----:|----:|----:|----:|
| centre_error_m | 176 | 0.337 | 0.146 | 0.603 | 0.457 | 0.633 | 0.758 | 0.901 |
| heading_error_deg | 176 | 0.741 | 0.390 | 1.380 | 0.990 | 1.994 | 3.415 | 7.617 |
| speed_error_mps | 176 | 0.040 | 0.022 | 0.098 | 0.077 | 0.182 | 0.296 | 0.479 |
| velocity_error_mps | 176 | 0.147 | 0.091 | 0.277 | 0.187 | 0.491 | 0.806 | 1.715 |

Calibration of pos_std_m over 425 states: within 1/2/3 sigma 0.122/0.351/0.525 (Gaussian: 0.393/0.865/0.989).
