# Road-user fusion against ground truth - S13/run_0_passing

Privileged evaluation (ground truth used here only). Assumptions: recorder raw clocks are CARLA simulator time; a vehicle box is centred on its origin in the horizontal plane.

## Track identity decisions (aligned recorders)

| Track | Decision | Status | By | True identity | Purity | Verdict |
|-------|----------|--------|----|---------------|-------:|---------|
| A:track_001 | U1 | ANONYMOUS | - | D | 1.000 | anonymous (non-recording road user D) |
| A:track_002 | B | ASSOCIATED | collision | B | 1.000 | correct link |
| A:track_003 | U2 | ANONYMOUS | - | C | 1.000 | anonymous (non-recording road user C) |
| B:track_001 | A | ASSOCIATED | collision | A | 1.000 | correct link |
| B:track_002 | U1 | ANONYMOUS | - | D | 1.000 | anonymous (non-recording road user D) |
| B:track_003 | U2 | ANONYMOUS | - | C | 1.000 | anonymous (non-recording road user C) |
| B:track_004 | U1 | ANONYMOUS | - | D | 1.000 | anonymous (non-recording road user D) |

Counts: anonymous: 5, correct link: 2

## Anonymous entities

| Entity | Source tracks | True identity | Recorder? | Purity |
|--------|---------------|---------------|-----------|-------:|
| U1 | A:track_001, B:track_002, B:track_004 | D | no | 1.000 |
| U2 | B:track_003, A:track_003 | C | no | 1.000 |

Merges over pairs of anonymous tracks: correct 4, false 0, missed 0.
Fragmentation (true road user -> entities): C -> U2, D -> U1

## Fused state errors (against the majority identity, 201 pure states; 0 impure states where a source track was on another body, excluded)

| Quantity | n | median | q25 | q75 | IQR | p90 | p95 | max |
|----------|--:|-------:|----:|----:|----:|----:|----:|----:|
| centre_error_m | 201 | 0.313 | 0.243 | 0.402 | 0.159 | 0.550 | 0.576 | 0.784 |
| coverage_s | 2 | 9.950 | 9.825 | 10.075 | 0.250 | 10.150 | 10.175 | 10.200 |
| heading_error_deg | 201 | 0.328 | 0.109 | 0.761 | 0.652 | 1.193 | 1.901 | 14.233 |
| length_error_m | 2 | 0.139 | 0.113 | 0.166 | 0.053 | 0.181 | 0.187 | 0.192 |
| normalised_centre_error | 201 | 3.394 | 2.626 | 4.086 | 1.461 | 4.377 | 4.495 | 7.398 |
| single_track_nominal_centre_error_m | 201 | 0.431 | 0.300 | 0.593 | 0.293 | 0.712 | 0.733 | 0.922 |
| speed_error_mps | 201 | 0.043 | 0.018 | 0.079 | 0.062 | 0.156 | 0.190 | 0.468 |
| velocity_error_mps | 201 | 0.101 | 0.062 | 0.190 | 0.128 | 0.315 | 0.396 | 3.009 |
| width_error_m | 2 | 0.185 | 0.146 | 0.224 | 0.078 | 0.247 | 0.255 | 0.263 |

### Method: box_fit

| Quantity | n | median | q25 | q75 | IQR | p90 | p95 | max |
|----------|--:|-------:|----:|----:|----:|----:|----:|----:|
| centre_error_m | 143 | 0.277 | 0.209 | 0.339 | 0.131 | 0.388 | 0.404 | 0.784 |
| heading_error_deg | 143 | 0.269 | 0.109 | 0.668 | 0.559 | 1.185 | 1.372 | 14.233 |
| speed_error_mps | 143 | 0.037 | 0.015 | 0.073 | 0.058 | 0.156 | 0.190 | 0.468 |
| velocity_error_mps | 143 | 0.083 | 0.053 | 0.166 | 0.113 | 0.245 | 0.385 | 3.009 |

### Method: covariance_intersection

| Quantity | n | median | q25 | q75 | IQR | p90 | p95 | max |
|----------|--:|-------:|----:|----:|----:|----:|----:|----:|
| centre_error_m | 58 | 0.509 | 0.400 | 0.565 | 0.166 | 0.620 | 0.654 | 0.669 |
| heading_error_deg | 58 | 0.466 | 0.109 | 0.888 | 0.779 | 1.656 | 2.008 | 2.541 |
| speed_error_mps | 58 | 0.064 | 0.025 | 0.129 | 0.104 | 0.158 | 0.220 | 0.279 |
| velocity_error_mps | 58 | 0.163 | 0.115 | 0.232 | 0.117 | 0.385 | 0.425 | 0.641 |

Calibration of pos_std_m over 201 states: within 1/2/3 sigma 0.000/0.124/0.318 (Gaussian: 0.393/0.865/0.989).
