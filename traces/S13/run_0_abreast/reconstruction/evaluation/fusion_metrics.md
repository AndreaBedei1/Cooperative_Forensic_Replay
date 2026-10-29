# Road-user fusion against ground truth - S13/run_0_abreast

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

Counts: anonymous: 4, correct link: 2

## Anonymous entities

| Entity | Source tracks | True identity | Recorder? | Purity |
|--------|---------------|---------------|-----------|-------:|
| U1 | A:track_001, B:track_002 | D | no | 1.000 |
| U2 | B:track_003, A:track_003 | C | no | 1.000 |

Merges over pairs of anonymous tracks: correct 2, false 0, missed 0.
Fragmentation (true road user -> entities): C -> U2, D -> U1

## Fused state errors (against the majority identity, 208 pure states; 0 impure states where a source track was on another body, excluded)

| Quantity | n | median | q25 | q75 | IQR | p90 | p95 | max |
|----------|--:|-------:|----:|----:|----:|----:|----:|----:|
| centre_error_m | 208 | 0.277 | 0.241 | 0.392 | 0.150 | 0.606 | 0.677 | 0.758 |
| coverage_s | 2 | 10.325 | 10.262 | 10.387 | 0.125 | 10.425 | 10.438 | 10.450 |
| heading_error_deg | 208 | 0.400 | 0.129 | 0.706 | 0.577 | 1.097 | 1.422 | 3.163 |
| length_error_m | 2 | 0.139 | 0.113 | 0.166 | 0.053 | 0.181 | 0.187 | 0.192 |
| normalised_centre_error | 208 | 3.289 | 2.754 | 4.029 | 1.275 | 4.497 | 5.056 | 5.539 |
| single_track_nominal_centre_error_m | 208 | 0.448 | 0.323 | 0.612 | 0.289 | 0.697 | 0.743 | 0.836 |
| speed_error_mps | 208 | 0.040 | 0.019 | 0.097 | 0.077 | 0.175 | 0.213 | 0.303 |
| velocity_error_mps | 208 | 0.113 | 0.059 | 0.189 | 0.129 | 0.292 | 0.388 | 0.887 |
| width_error_m | 2 | 0.185 | 0.146 | 0.224 | 0.078 | 0.247 | 0.255 | 0.263 |

### Method: box_fit

| Quantity | n | median | q25 | q75 | IQR | p90 | p95 | max |
|----------|--:|-------:|----:|----:|----:|----:|----:|----:|
| centre_error_m | 156 | 0.264 | 0.220 | 0.308 | 0.088 | 0.391 | 0.398 | 0.587 |
| heading_error_deg | 156 | 0.350 | 0.110 | 0.640 | 0.530 | 0.985 | 1.096 | 2.518 |
| speed_error_mps | 156 | 0.031 | 0.017 | 0.070 | 0.053 | 0.154 | 0.190 | 0.303 |
| velocity_error_mps | 156 | 0.086 | 0.041 | 0.158 | 0.117 | 0.221 | 0.263 | 0.494 |

### Method: covariance_intersection

| Quantity | n | median | q25 | q75 | IQR | p90 | p95 | max |
|----------|--:|-------:|----:|----:|----:|----:|----:|----:|
| centre_error_m | 52 | 0.564 | 0.392 | 0.671 | 0.279 | 0.733 | 0.749 | 0.758 |
| heading_error_deg | 52 | 0.537 | 0.271 | 1.094 | 0.823 | 2.028 | 2.421 | 3.163 |
| speed_error_mps | 52 | 0.096 | 0.039 | 0.156 | 0.117 | 0.212 | 0.220 | 0.282 |
| velocity_error_mps | 52 | 0.198 | 0.146 | 0.299 | 0.152 | 0.455 | 0.551 | 0.887 |

Calibration of pos_std_m over 208 states: within 1/2/3 sigma 0.000/0.077/0.337 (Gaussian: 0.393/0.865/0.989).
