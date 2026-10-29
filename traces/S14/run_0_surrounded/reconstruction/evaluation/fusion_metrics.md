# Road-user fusion against ground truth - S14/run_0_surrounded

Privileged evaluation (ground truth used here only). Assumptions: recorder raw clocks are CARLA simulator time; a vehicle box is centred on its origin in the horizontal plane.

## Track identity decisions (aligned recorders)

| Track | Decision | Status | By | True identity | Purity | Verdict |
|-------|----------|--------|----|---------------|-------:|---------|
| A:track_001 | U1 | ANONYMOUS | - | P | 1.000 | anonymous (non-recording road user P) |
| A:track_002 | U2 | ANONYMOUS | - | C | 1.000 | anonymous (non-recording road user C) |
| A:track_003 | B | ASSOCIATED | collision | B | 1.000 | correct link |
| A:track_004 | U3 | ANONYMOUS | - | D | 1.000 | anonymous (non-recording road user D) |
| A:track_005 | U9 | ANONYMOUS | - | J | 1.000 | anonymous (non-recording road user J) |
| A:track_006 | U7 | ANONYMOUS | - | G | 1.000 | anonymous (non-recording road user G) |
| A:track_007 | U5 | ANONYMOUS | - | E | 1.000 | anonymous (non-recording road user E) |
| A:track_008 | U4 | ANONYMOUS | - | F | 1.000 | anonymous (non-recording road user F) |
| A:track_009 | U11 | ANONYMOUS | - | J | 1.000 | anonymous (non-recording road user J) |
| B:track_001 | U3 | ANONYMOUS | - | D | 1.000 | anonymous (non-recording road user D) |
| B:track_002 | A | ASSOCIATED | common_frame | A | 1.000 | correct link |
| B:track_003 | U1 | ANONYMOUS | - | P | 1.000 | anonymous (non-recording road user P) |
| B:track_004 | U4 | ANONYMOUS | - | F | 1.000 | anonymous (non-recording road user F) |
| B:track_005 | U2 | ANONYMOUS | - | C | 1.000 | anonymous (non-recording road user C) |
| B:track_006 | U5 | ANONYMOUS | - | E | 1.000 | anonymous (non-recording road user E) |
| B:track_007 | U6 | ANONYMOUS | - | H | 1.000 | anonymous (non-recording road user H) |
| B:track_008 | U7 | ANONYMOUS | - | G | 1.000 | anonymous (non-recording road user G) |
| B:track_009 | U7 | ANONYMOUS | - | G | 1.000 | anonymous (non-recording road user G) |
| B:track_010 | U4 | ANONYMOUS | - | F | 1.000 | anonymous (non-recording road user F) |
| B:track_011 | U8 | ANONYMOUS | - | H | 1.000 | anonymous (non-recording road user H) |
| B:track_012 | U10 | ANONYMOUS | - | H | 1.000 | anonymous (non-recording road user H) |
| B:track_013 | U11 | ANONYMOUS | - | J | 1.000 | anonymous (non-recording road user J) |
| B:track_014 | U12 | ANONYMOUS | - | H | 1.000 | anonymous (non-recording road user H) |

Counts: anonymous: 21, correct link: 2

## Anonymous entities

| Entity | Source tracks | True identity | Recorder? | Purity |
|--------|---------------|---------------|-----------|-------:|
| U1 | A:track_001, B:track_003 | P | no | 1.000 |
| U2 | A:track_002, B:track_005 | C | no | 1.000 |
| U3 | B:track_001, A:track_004 | D | no | 1.000 |
| U4 | B:track_004, B:track_010, A:track_008 | F | no | 1.000 |
| U5 | B:track_006, A:track_007 | E | no | 1.000 |
| U6 | B:track_007 | H | no | 1.000 |
| U7 | B:track_008, B:track_009, A:track_006 | G | no | 1.000 |
| U8 | B:track_011 | H | no | 1.000 |
| U9 | A:track_005 | J | no | 1.000 |
| U10 | B:track_012 | H | no | 1.000 |
| U11 | B:track_013, A:track_009 | J | no | 1.000 |
| U12 | B:track_014 | H | no | 1.000 |

Merges over pairs of anonymous tracks: correct 11, false 0, missed 8.
Fragmentation (true road user -> entities): C -> U2, D -> U3, E -> U5, F -> U4, G -> U7, H -> U10/U12/U6/U8, J -> U11/U9, P -> U1

## Fused state errors (against the majority identity, 743 pure states; 0 impure states where a source track was on another body, excluded)

| Quantity | n | median | q25 | q75 | IQR | p90 | p95 | max |
|----------|--:|-------:|----:|----:|----:|----:|----:|----:|
| centre_error_m | 743 | 0.150 | 0.092 | 0.401 | 0.309 | 0.669 | 0.748 | 1.880 |
| coverage_s | 12 | 7.525 | 0.588 | 11.950 | 11.363 | 11.950 | 11.950 | 11.950 |
| heading_error_deg | 743 | 0.341 | 0.139 | 0.925 | 0.786 | 2.536 | 3.173 | 15.236 |
| length_error_m | 12 | 0.192 | 0.166 | 0.249 | 0.083 | 0.419 | 0.419 | 0.419 |
| normalised_centre_error | 743 | 1.770 | 1.159 | 3.371 | 2.212 | 5.156 | 5.819 | 8.590 |
| single_track_nominal_centre_error_m | 724 | 0.322 | 0.215 | 0.534 | 0.319 | 0.734 | 0.841 | 1.667 |
| speed_error_mps | 743 | 0.026 | 0.011 | 0.057 | 0.046 | 0.089 | 0.123 | 0.368 |
| velocity_error_mps | 743 | 0.076 | 0.039 | 0.197 | 0.158 | 0.452 | 0.647 | 3.256 |
| width_error_m | 12 | 0.185 | 0.104 | 0.263 | 0.159 | 0.263 | 0.263 | 0.263 |

### Method: box_fit

| Quantity | n | median | q25 | q75 | IQR | p90 | p95 | max |
|----------|--:|-------:|----:|----:|----:|----:|----:|----:|
| centre_error_m | 511 | 0.111 | 0.076 | 0.170 | 0.094 | 0.261 | 0.338 | 0.659 |
| heading_error_deg | 511 | 0.228 | 0.099 | 0.438 | 0.339 | 1.079 | 1.761 | 4.266 |
| speed_error_mps | 511 | 0.020 | 0.009 | 0.040 | 0.031 | 0.067 | 0.083 | 0.259 |
| velocity_error_mps | 511 | 0.056 | 0.027 | 0.100 | 0.074 | 0.229 | 0.349 | 0.882 |

### Method: covariance_intersection

| Quantity | n | median | q25 | q75 | IQR | p90 | p95 | max |
|----------|--:|-------:|----:|----:|----:|----:|----:|----:|
| centre_error_m | 232 | 0.496 | 0.382 | 0.699 | 0.317 | 0.808 | 0.917 | 1.880 |
| heading_error_deg | 232 | 1.108 | 0.522 | 2.552 | 2.030 | 3.565 | 5.399 | 15.236 |
| speed_error_mps | 232 | 0.052 | 0.022 | 0.087 | 0.065 | 0.165 | 0.204 | 0.368 |
| velocity_error_mps | 232 | 0.211 | 0.118 | 0.461 | 0.343 | 0.759 | 1.125 | 3.256 |

Calibration of pos_std_m over 743 states: within 1/2/3 sigma 0.195/0.540/0.688 (Gaussian: 0.393/0.865/0.989).
