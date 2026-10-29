# Road-user fusion against ground truth - S15/run_0_dense_platoon

Privileged evaluation (ground truth used here only). Assumptions: recorder raw clocks are CARLA simulator time; a vehicle box is centred on its origin in the horizontal plane.

## Track identity decisions (aligned recorders)

| Track | Decision | Status | By | True identity | Purity | Verdict |
|-------|----------|--------|----|---------------|-------:|---------|
| A:track_001 | U1 | ANONYMOUS | - | F | 1.000 | anonymous (non-recording road user F) |
| A:track_002 | U2 | ANONYMOUS | - | D | 1.000 | anonymous (non-recording road user D) |
| A:track_003 | U3 | ANONYMOUS | - | I | 1.000 | anonymous (non-recording road user I) |
| A:track_004 | U4 | ANONYMOUS | - | H | 1.000 | anonymous (non-recording road user H) |
| A:track_005 | U5 | ANONYMOUS | - | E | 1.000 | anonymous (non-recording road user E) |
| A:track_006 | U6 | ANONYMOUS | - | G | 1.000 | anonymous (non-recording road user G) |
| A:track_007 | U7 | ANONYMOUS | - | J | 1.000 | anonymous (non-recording road user J) |
| A:track_008 | U9 | ANONYMOUS | - | C | 1.000 | anonymous (non-recording road user C) |
| A:track_009 | U10 | ANONYMOUS | - | E | 1.000 | anonymous (non-recording road user E) |
| A:track_010 | U11 | ANONYMOUS | - | F | 1.000 | anonymous (non-recording road user F) |
| B:track_001 | U6 | ANONYMOUS | - | G | 1.000 | anonymous (non-recording road user G) |
| B:track_002 | U5 | ANONYMOUS | - | E | 1.000 | anonymous (non-recording road user E) |
| B:track_003 | U7 | ANONYMOUS | - | J | 1.000 | anonymous (non-recording road user J) |
| B:track_004 | U3 | ANONYMOUS | - | I | 1.000 | anonymous (non-recording road user I) |
| B:track_005 | U1 | ANONYMOUS | - | F | 1.000 | anonymous (non-recording road user F) |
| B:track_006 | U4 | ANONYMOUS | - | H | 1.000 | anonymous (non-recording road user H) |
| B:track_007 | A | ASSOCIATED | collision | A | 1.000 | correct link |
| B:track_008 | U5 | ANONYMOUS | - | E | 1.000 | anonymous (non-recording road user E) |
| B:track_009 | U8 | ANONYMOUS | - | H | 1.000 | anonymous (non-recording road user H) |

Counts: anonymous: 18, correct link: 1

## Anonymous entities

| Entity | Source tracks | True identity | Recorder? | Purity |
|--------|---------------|---------------|-----------|-------:|
| U1 | A:track_001, B:track_005 | F | no | 1.000 |
| U2 | A:track_002 | D | no | 1.000 |
| U3 | A:track_003, B:track_004 | I | no | 1.000 |
| U4 | A:track_004, B:track_006 | H | no | 1.000 |
| U5 | A:track_005, B:track_002, B:track_008 | E | no | 1.000 |
| U6 | A:track_006, B:track_001 | G | no | 1.000 |
| U7 | A:track_007, B:track_003 | J | no | 1.000 |
| U8 | B:track_009 | H | no | 1.000 |
| U9 | A:track_008 | C | no | 1.000 |
| U10 | A:track_009 | E | no | 1.000 |
| U11 | A:track_010 | F | no | 1.000 |

Merges over pairs of anonymous tracks: correct 8, false 0, missed 7.
Fragmentation (true road user -> entities): C -> U9, D -> U2, E -> U10/U5, F -> U1/U11, G -> U6, H -> U4/U8, I -> U3, J -> U7

## Fused state errors (against the majority identity, 841 pure states; 0 impure states where a source track was on another body, excluded)

| Quantity | n | median | q25 | q75 | IQR | p90 | p95 | max |
|----------|--:|-------:|----:|----:|----:|----:|----:|----:|
| centre_error_m | 841 | 0.202 | 0.079 | 0.276 | 0.197 | 0.515 | 0.885 | 1.660 |
| coverage_s | 11 | 9.550 | 1.950 | 11.925 | 9.975 | 11.950 | 11.950 | 11.950 |
| heading_error_deg | 841 | 0.238 | 0.096 | 0.988 | 0.892 | 2.636 | 3.499 | 10.906 |
| length_error_m | 11 | 0.192 | 0.105 | 0.192 | 0.086 | 0.194 | 0.306 | 0.419 |
| normalised_centre_error | 841 | 2.127 | 1.074 | 3.130 | 2.056 | 4.296 | 5.888 | 8.279 |
| single_track_nominal_centre_error_m | 830 | 0.390 | 0.228 | 0.658 | 0.430 | 0.989 | 1.180 | 1.898 |
| speed_error_mps | 841 | 0.033 | 0.015 | 0.071 | 0.056 | 0.222 | 0.354 | 0.854 |
| velocity_error_mps | 841 | 0.071 | 0.029 | 0.252 | 0.223 | 0.624 | 0.824 | 2.328 |
| width_error_m | 11 | 0.107 | 0.107 | 0.263 | 0.156 | 0.263 | 0.263 | 0.263 |

### Method: box_fit

| Quantity | n | median | q25 | q75 | IQR | p90 | p95 | max |
|----------|--:|-------:|----:|----:|----:|----:|----:|----:|
| centre_error_m | 496 | 0.126 | 0.056 | 0.239 | 0.183 | 0.281 | 0.405 | 0.787 |
| heading_error_deg | 496 | 0.170 | 0.084 | 0.431 | 0.347 | 1.085 | 1.698 | 3.744 |
| speed_error_mps | 496 | 0.027 | 0.014 | 0.055 | 0.041 | 0.245 | 0.477 | 0.854 |
| velocity_error_mps | 496 | 0.047 | 0.024 | 0.132 | 0.109 | 0.360 | 0.596 | 0.854 |

### Method: covariance_intersection

| Quantity | n | median | q25 | q75 | IQR | p90 | p95 | max |
|----------|--:|-------:|----:|----:|----:|----:|----:|----:|
| centre_error_m | 345 | 0.263 | 0.183 | 0.466 | 0.283 | 0.983 | 1.211 | 1.660 |
| heading_error_deg | 345 | 0.682 | 0.151 | 2.258 | 2.107 | 3.814 | 5.648 | 10.906 |
| speed_error_mps | 345 | 0.048 | 0.017 | 0.112 | 0.095 | 0.217 | 0.249 | 0.375 |
| velocity_error_mps | 345 | 0.154 | 0.055 | 0.535 | 0.480 | 0.864 | 1.232 | 2.328 |

Calibration of pos_std_m over 841 states: within 1/2/3 sigma 0.233/0.466/0.725 (Gaussian: 0.393/0.865/0.989).
