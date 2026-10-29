# Road-user fusion against ground truth - S13/run_0_platoon

Privileged evaluation (ground truth used here only). Assumptions: recorder raw clocks are CARLA simulator time; a vehicle box is centred on its origin in the horizontal plane.

## Track identity decisions (aligned recorders)

| Track | Decision | Status | By | True identity | Purity | Verdict |
|-------|----------|--------|----|---------------|-------:|---------|
| A:track_001 | B | ASSOCIATED | collision | B | 1.000 | correct link |
| A:track_002 | U1 | ANONYMOUS | - | D | 1.000 | anonymous (non-recording road user D) |
| A:track_003 | U2 | ANONYMOUS | - | C | 1.000 | anonymous (non-recording road user C) |
| B:track_001 | A | ASSOCIATED | collision | A | 1.000 | correct link |
| B:track_002 | U1 | ANONYMOUS | - | D | 1.000 | anonymous (non-recording road user D) |
| B:track_003 | U2 | ANONYMOUS | - | C | 1.000 | anonymous (non-recording road user C) |
| B:track_004 | U2 | ANONYMOUS | - | C | 1.000 | anonymous (non-recording road user C) |

Counts: anonymous: 5, correct link: 2

## Anonymous entities

| Entity | Source tracks | True identity | Recorder? | Purity |
|--------|---------------|---------------|-----------|-------:|
| U1 | B:track_002, A:track_002 | D | no | 1.000 |
| U2 | B:track_003, A:track_003, B:track_004 | C | no | 1.000 |

Merges over pairs of anonymous tracks: correct 4, false 0, missed 0.
Fragmentation (true road user -> entities): C -> U2, D -> U1

## Fused state errors (against the majority identity, 187 pure states; 0 impure states where a source track was on another body, excluded)

| Quantity | n | median | q25 | q75 | IQR | p90 | p95 | max |
|----------|--:|-------:|----:|----:|----:|----:|----:|----:|
| centre_error_m | 187 | 0.415 | 0.253 | 0.841 | 0.588 | 0.974 | 1.098 | 1.265 |
| coverage_s | 2 | 10.025 | 9.787 | 10.262 | 0.475 | 10.405 | 10.453 | 10.500 |
| heading_error_deg | 187 | 0.486 | 0.227 | 1.053 | 0.826 | 1.674 | 3.676 | 6.481 |
| length_error_m | 2 | 0.139 | 0.113 | 0.166 | 0.053 | 0.181 | 0.187 | 0.192 |
| normalised_centre_error | 187 | 3.409 | 2.952 | 7.019 | 4.066 | 7.927 | 8.162 | 8.594 |
| single_track_nominal_centre_error_m | 185 | 0.488 | 0.313 | 0.899 | 0.586 | 1.055 | 1.140 | 1.313 |
| speed_error_mps | 187 | 0.048 | 0.022 | 0.108 | 0.087 | 0.141 | 0.195 | 0.945 |
| velocity_error_mps | 187 | 0.136 | 0.078 | 0.242 | 0.164 | 0.513 | 0.945 | 1.594 |
| width_error_m | 2 | 0.185 | 0.146 | 0.224 | 0.078 | 0.247 | 0.255 | 0.263 |

### Method: box_fit

| Quantity | n | median | q25 | q75 | IQR | p90 | p95 | max |
|----------|--:|-------:|----:|----:|----:|----:|----:|----:|
| centre_error_m | 86 | 0.253 | 0.244 | 0.267 | 0.023 | 0.796 | 0.899 | 0.978 |
| heading_error_deg | 86 | 0.305 | 0.122 | 0.582 | 0.460 | 1.106 | 1.487 | 1.766 |
| speed_error_mps | 86 | 0.025 | 0.014 | 0.076 | 0.061 | 0.120 | 0.130 | 0.230 |
| velocity_error_mps | 86 | 0.086 | 0.051 | 0.139 | 0.088 | 0.243 | 0.302 | 0.328 |

### Method: covariance_intersection

| Quantity | n | median | q25 | q75 | IQR | p90 | p95 | max |
|----------|--:|-------:|----:|----:|----:|----:|----:|----:|
| centre_error_m | 101 | 0.824 | 0.494 | 0.939 | 0.445 | 1.091 | 1.175 | 1.265 |
| heading_error_deg | 101 | 0.810 | 0.363 | 1.314 | 0.951 | 3.320 | 5.039 | 6.481 |
| speed_error_mps | 101 | 0.079 | 0.040 | 0.119 | 0.078 | 0.180 | 0.239 | 0.945 |
| velocity_error_mps | 101 | 0.181 | 0.111 | 0.351 | 0.241 | 0.922 | 1.168 | 1.594 |

Calibration of pos_std_m over 187 states: within 1/2/3 sigma 0.011/0.102/0.262 (Gaussian: 0.393/0.865/0.989).
