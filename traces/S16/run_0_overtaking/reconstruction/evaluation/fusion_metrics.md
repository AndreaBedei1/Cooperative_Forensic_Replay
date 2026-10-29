# Road-user fusion against ground truth - S16/run_0_overtaking

Privileged evaluation (ground truth used here only). Assumptions: recorder raw clocks are CARLA simulator time; a vehicle box is centred on its origin in the horizontal plane.

## Track identity decisions (aligned recorders)

| Track | Decision | Status | By | True identity | Purity | Verdict |
|-------|----------|--------|----|---------------|-------:|---------|
| A:track_001 | U1 | ANONYMOUS | - | H | 1.000 | anonymous (non-recording road user H) |
| A:track_002 | U2 | ANONYMOUS | - | I | 1.000 | anonymous (non-recording road user I) |
| A:track_003 | U3 | ANONYMOUS | - | F | 1.000 | anonymous (non-recording road user F) |
| A:track_004 | U4 | ANONYMOUS | - | D | 1.000 | anonymous (non-recording road user D) |
| A:track_005 | U5 | ANONYMOUS | - | E | 1.000 | anonymous (non-recording road user E) |
| A:track_006 | B | ASSOCIATED | collision | B | 1.000 | correct link |
| A:track_007 | U4 | ANONYMOUS | - | D | 1.000 | anonymous (non-recording road user D) |
| A:track_008 | U8 | ANONYMOUS | - | G | 0.727 | anonymous (non-recording road user G) |
| A:track_009 | U10 | ANONYMOUS | - | C | 1.000 | anonymous (non-recording road user C) |
| A:track_010 | U12 | ANONYMOUS | - | E | 1.000 | anonymous (non-recording road user E) |
| A:track_011 | U11 | ANONYMOUS | - | I | 1.000 | anonymous (non-recording road user I) |
| B:track_001 | A | ASSOCIATED | collision | A | 1.000 | correct link |
| B:track_002 | U3 | ANONYMOUS | - | F | 1.000 | anonymous (non-recording road user F) |
| B:track_003 | U6 | ANONYMOUS | - | E | 1.000 | anonymous (non-recording road user E) |
| B:track_004 | U7 | ANONYMOUS | - | G | 1.000 | anonymous (non-recording road user G) |
| B:track_005 | U1 | ANONYMOUS | - | H | 1.000 | anonymous (non-recording road user H) |
| B:track_006 | U4 | ANONYMOUS | - | D | 1.000 | anonymous (non-recording road user D) |
| B:track_007 | U8 | ANONYMOUS | - | G | 1.000 | anonymous (non-recording road user G) |
| B:track_008 | U9 | ANONYMOUS | - | C | 1.000 | anonymous (non-recording road user C) |
| B:track_009 | U11 | ANONYMOUS | - | I | 1.000 | anonymous (non-recording road user I) |
| B:track_010 | U12 | ANONYMOUS | - | E | 1.000 | anonymous (non-recording road user E) |

Counts: anonymous: 19, correct link: 2

## Anonymous entities

| Entity | Source tracks | True identity | Recorder? | Purity |
|--------|---------------|---------------|-----------|-------:|
| U1 | A:track_001, B:track_005 | H | no | 1.000 |
| U2 | A:track_002 | I | no | 1.000 |
| U3 | A:track_003, B:track_002 | F | no | 1.000 |
| U4 | A:track_004, A:track_007, B:track_006 | D | no | 1.000 |
| U5 | A:track_005 | E | no | 1.000 |
| U6 | B:track_003 | E | no | 1.000 |
| U7 | B:track_004 | G | no | 1.000 |
| U8 | A:track_008, B:track_007 | G | no | 0.861 |
| U9 | B:track_008 | C | no | 1.000 |
| U10 | A:track_009 | C | no | 1.000 |
| U11 | B:track_009, A:track_011 | I | no | 1.000 |
| U12 | A:track_010, B:track_010 | E | no | 1.000 |

Merges over pairs of anonymous tracks: correct 8, false 0, missed 10.
Fragmentation (true road user -> entities): C -> U10/U9, D -> U4, E -> U12/U5/U6, F -> U3, G -> U7/U8, H -> U1, I -> U11/U2

## Fused state errors (against the majority identity, 614 pure states; 15 impure states where a source track was on another body, excluded)

| Quantity | n | median | q25 | q75 | IQR | p90 | p95 | max |
|----------|--:|-------:|----:|----:|----:|----:|----:|----:|
| centre_error_m | 614 | 0.389 | 0.167 | 0.544 | 0.376 | 0.654 | 0.977 | 3.072 |
| coverage_s | 12 | 3.850 | 2.600 | 7.263 | 4.662 | 11.875 | 11.950 | 11.950 |
| heading_error_deg | 614 | 0.572 | 0.190 | 1.409 | 1.219 | 3.144 | 4.593 | 15.343 |
| length_error_m | 12 | 0.192 | 0.086 | 0.249 | 0.163 | 0.419 | 0.419 | 0.419 |
| normalised_centre_error | 614 | 3.087 | 2.017 | 4.589 | 2.572 | 6.522 | 8.064 | 15.271 |
| single_track_nominal_centre_error_m | 604 | 0.582 | 0.432 | 0.807 | 0.375 | 1.375 | 1.474 | 3.084 |
| speed_error_mps | 614 | 0.058 | 0.024 | 0.108 | 0.085 | 0.233 | 0.342 | 0.625 |
| velocity_error_mps | 614 | 0.136 | 0.066 | 0.284 | 0.219 | 0.584 | 0.930 | 2.654 |
| width_error_m | 12 | 0.107 | 0.104 | 0.263 | 0.159 | 0.263 | 0.263 | 0.263 |

### Method: box_fit

| Quantity | n | median | q25 | q75 | IQR | p90 | p95 | max |
|----------|--:|-------:|----:|----:|----:|----:|----:|----:|
| centre_error_m | 387 | 0.224 | 0.143 | 0.426 | 0.284 | 0.568 | 0.650 | 1.444 |
| heading_error_deg | 387 | 0.390 | 0.159 | 1.201 | 1.043 | 2.598 | 4.372 | 14.982 |
| speed_error_mps | 387 | 0.058 | 0.026 | 0.108 | 0.082 | 0.236 | 0.352 | 0.625 |
| velocity_error_mps | 387 | 0.118 | 0.059 | 0.237 | 0.178 | 0.512 | 0.798 | 2.598 |

### Method: covariance_intersection

| Quantity | n | median | q25 | q75 | IQR | p90 | p95 | max |
|----------|--:|-------:|----:|----:|----:|----:|----:|----:|
| centre_error_m | 227 | 0.533 | 0.406 | 0.614 | 0.209 | 1.092 | 2.701 | 3.072 |
| heading_error_deg | 227 | 0.810 | 0.352 | 1.764 | 1.412 | 3.853 | 5.186 | 15.343 |
| speed_error_mps | 227 | 0.054 | 0.020 | 0.108 | 0.088 | 0.222 | 0.328 | 0.523 |
| velocity_error_mps | 227 | 0.169 | 0.089 | 0.316 | 0.226 | 0.810 | 1.151 | 2.654 |

Calibration of pos_std_m over 614 states: within 1/2/3 sigma 0.050/0.248/0.489 (Gaussian: 0.393/0.865/0.989).
