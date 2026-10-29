# Road-user fusion against ground truth - S19/run_0_highway_curve

Privileged evaluation (ground truth used here only). Assumptions: recorder raw clocks are CARLA simulator time; a vehicle box is centred on its origin in the horizontal plane.

## Track identity decisions (aligned recorders)

| Track | Decision | Status | By | True identity | Purity | Verdict |
|-------|----------|--------|----|---------------|-------:|---------|
| A:track_001 | U1 | ANONYMOUS | - | C | 1.000 | anonymous (non-recording road user C) |
| A:track_002 | U2 | ANONYMOUS | - | D | 1.000 | anonymous (non-recording road user D) |
| A:track_003 | U3 | ANONYMOUS | - | G | 1.000 | anonymous (non-recording road user G) |
| A:track_004 | U4 | ANONYMOUS | - | F | 1.000 | anonymous (non-recording road user F) |
| A:track_005 | U6 | ANONYMOUS | - | E | 1.000 | anonymous (non-recording road user E) |
| A:track_006 | B | ASSOCIATED | collision | B | 1.000 | correct link |
| A:track_007 | U5 | ANONYMOUS | - | E | 1.000 | anonymous (non-recording road user E) |
| A:track_008 | U5 | ANONYMOUS | - | E | 1.000 | anonymous (non-recording road user E) |
| A:track_009 | U5 | ANONYMOUS | - | E | 1.000 | anonymous (non-recording road user E) |
| A:track_010 | U7 | ANONYMOUS | - | G | 1.000 | anonymous (non-recording road user G) |
| A:track_011 | U8 | ANONYMOUS | - | F | 1.000 | anonymous (non-recording road user F) |
| B:track_001 | U3 | ANONYMOUS | - | G | 1.000 | anonymous (non-recording road user G) |
| B:track_002 | U5 | ANONYMOUS | - | E | 1.000 | anonymous (non-recording road user E) |
| B:track_003 | U1 | ANONYMOUS | - | C | 1.000 | anonymous (non-recording road user C) |
| B:track_004 | U2 | ANONYMOUS | - | D | 1.000 | anonymous (non-recording road user D) |
| B:track_005 | A | ASSOCIATED | collision | A | 1.000 | correct link |
| B:track_006 | U9 | ANONYMOUS | - | G | 1.000 | anonymous (non-recording road user G) |
| B:track_007 | U8 | ANONYMOUS | - | F | 1.000 | anonymous (non-recording road user F) |

Counts: anonymous: 16, correct link: 2

## Anonymous entities

| Entity | Source tracks | True identity | Recorder? | Purity |
|--------|---------------|---------------|-----------|-------:|
| U1 | A:track_001, B:track_003 | C | no | 1.000 |
| U2 | A:track_002, B:track_004 | D | no | 1.000 |
| U3 | A:track_003, B:track_001 | G | no | 1.000 |
| U4 | A:track_004 | F | no | 1.000 |
| U5 | B:track_002, A:track_007, A:track_008, A:track_009 | E | no | 1.000 |
| U6 | A:track_005 | E | no | 1.000 |
| U7 | A:track_010 | G | no | 1.000 |
| U8 | A:track_011, B:track_007 | F | no | 1.000 |
| U9 | B:track_006 | G | no | 1.000 |

Merges over pairs of anonymous tracks: correct 10, false 0, missed 11.
Fragmentation (true road user -> entities): C -> U1, D -> U2, E -> U5/U6, F -> U4/U8, G -> U3/U7/U9

## Fused state errors (against the majority identity, 461 pure states; 0 impure states where a source track was on another body, excluded)

| Quantity | n | median | q25 | q75 | IQR | p90 | p95 | max |
|----------|--:|-------:|----:|----:|----:|----:|----:|----:|
| centre_error_m | 461 | 0.270 | 0.147 | 0.509 | 0.362 | 0.600 | 0.756 | 1.620 |
| coverage_s | 9 | 3.250 | 0.700 | 7.700 | 7.000 | 11.310 | 11.630 | 11.950 |
| heading_error_deg | 461 | 0.829 | 0.393 | 1.397 | 1.004 | 2.407 | 3.220 | 10.252 |
| length_error_m | 9 | 0.192 | 0.086 | 0.303 | 0.217 | 0.419 | 0.419 | 0.419 |
| normalised_centre_error | 461 | 2.488 | 1.643 | 3.723 | 2.080 | 4.572 | 4.982 | 12.366 |
| single_track_nominal_centre_error_m | 461 | 0.763 | 0.556 | 0.935 | 0.379 | 1.188 | 1.517 | 2.180 |
| speed_error_mps | 461 | 0.044 | 0.018 | 0.125 | 0.106 | 0.309 | 0.430 | 0.641 |
| velocity_error_mps | 461 | 0.127 | 0.058 | 0.360 | 0.302 | 0.780 | 1.007 | 3.164 |
| width_error_m | 9 | 0.107 | 0.107 | 0.263 | 0.156 | 0.263 | 0.263 | 0.263 |

### Method: box_fit

| Quantity | n | median | q25 | q75 | IQR | p90 | p95 | max |
|----------|--:|-------:|----:|----:|----:|----:|----:|----:|
| centre_error_m | 292 | 0.188 | 0.093 | 0.295 | 0.202 | 0.386 | 0.572 | 0.908 |
| heading_error_deg | 292 | 0.505 | 0.270 | 1.113 | 0.843 | 2.015 | 2.690 | 6.762 |
| speed_error_mps | 292 | 0.037 | 0.016 | 0.119 | 0.103 | 0.306 | 0.436 | 0.641 |
| velocity_error_mps | 292 | 0.107 | 0.049 | 0.232 | 0.183 | 0.611 | 0.812 | 2.147 |

### Method: covariance_intersection

| Quantity | n | median | q25 | q75 | IQR | p90 | p95 | max |
|----------|--:|-------:|----:|----:|----:|----:|----:|----:|
| centre_error_m | 169 | 0.558 | 0.305 | 0.599 | 0.293 | 0.812 | 1.035 | 1.620 |
| heading_error_deg | 169 | 1.153 | 0.827 | 1.961 | 1.134 | 3.174 | 4.541 | 10.252 |
| speed_error_mps | 169 | 0.052 | 0.019 | 0.142 | 0.123 | 0.311 | 0.414 | 0.565 |
| velocity_error_mps | 169 | 0.222 | 0.099 | 0.623 | 0.524 | 1.026 | 1.631 | 3.164 |

Calibration of pos_std_m over 461 states: within 1/2/3 sigma 0.104/0.367/0.586 (Gaussian: 0.393/0.865/0.989).
