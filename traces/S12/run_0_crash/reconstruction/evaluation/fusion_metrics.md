# Road-user fusion against ground truth - S12/run_0_crash

Privileged evaluation (ground truth used here only). Assumptions: recorder raw clocks are CARLA simulator time; a vehicle box is centred on its origin in the horizontal plane.

## Track identity decisions (aligned recorders)

| Track | Decision | Status | By | True identity | Purity | Verdict |
|-------|----------|--------|----|---------------|-------:|---------|
| A:track_001 | U1 | ANONYMOUS | - | C | 1.000 | anonymous (non-recording road user C) |
| A:track_002 | B | ASSOCIATED | collision | B | 1.000 | correct link |
| B:track_001 | A | ASSOCIATED | collision | A | 1.000 | correct link |
| B:track_002 | U1 | ANONYMOUS | - | C | 1.000 | anonymous (non-recording road user C) |
| B:track_003 | U1 | ANONYMOUS | - | C | 1.000 | anonymous (non-recording road user C) |

Counts: anonymous: 3, correct link: 2

## Anonymous entities

| Entity | Source tracks | True identity | Recorder? | Purity |
|--------|---------------|---------------|-----------|-------:|
| U1 | A:track_001, B:track_002, B:track_003 | C | no | 1.000 |

Merges over pairs of anonymous tracks: correct 3, false 0, missed 0.
Fragmentation (true road user -> entities): C -> U1

## Fused state errors (against the majority identity, 75 pure states; 0 impure states where a source track was on another body, excluded)

| Quantity | n | median | q25 | q75 | IQR | p90 | p95 | max |
|----------|--:|-------:|----:|----:|----:|----:|----:|----:|
| centre_error_m | 75 | 0.045 | 0.036 | 0.057 | 0.021 | 0.097 | 0.197 | 0.319 |
| coverage_s | 1 | 7.450 | 7.450 | 7.450 | 0.000 | 7.450 | 7.450 | 7.450 |
| heading_error_deg | 75 | 0.315 | 0.154 | 0.641 | 0.487 | 1.412 | 1.677 | 2.715 |
| length_error_m | 1 | 0.192 | 0.192 | 0.192 | 0.000 | 0.192 | 0.192 | 0.192 |
| normalised_centre_error | 75 | 0.475 | 0.389 | 0.715 | 0.326 | 0.963 | 1.696 | 1.969 |
| single_track_nominal_centre_error_m | 74 | 1.002 | 0.832 | 1.211 | 0.379 | 1.302 | 1.343 | 1.653 |
| speed_error_mps | 75 | 0.018 | 0.011 | 0.035 | 0.024 | 0.051 | 0.091 | 0.630 |
| velocity_error_mps | 75 | 0.045 | 0.028 | 0.099 | 0.071 | 0.221 | 0.351 | 0.816 |
| width_error_m | 1 | 0.263 | 0.263 | 0.263 | 0.000 | 0.263 | 0.263 | 0.263 |

### Method: box_fit

| Quantity | n | median | q25 | q75 | IQR | p90 | p95 | max |
|----------|--:|-------:|----:|----:|----:|----:|----:|----:|
| centre_error_m | 69 | 0.043 | 0.036 | 0.054 | 0.019 | 0.071 | 0.084 | 0.154 |
| heading_error_deg | 69 | 0.298 | 0.146 | 0.558 | 0.412 | 0.996 | 1.236 | 1.500 |
| speed_error_mps | 69 | 0.018 | 0.010 | 0.031 | 0.021 | 0.041 | 0.045 | 0.091 |
| velocity_error_mps | 69 | 0.041 | 0.028 | 0.072 | 0.045 | 0.120 | 0.146 | 0.297 |

### Method: covariance_intersection

| Quantity | n | median | q25 | q75 | IQR | p90 | p95 | max |
|----------|--:|-------:|----:|----:|----:|----:|----:|----:|
| centre_error_m | 6 | 0.238 | 0.196 | 0.275 | 0.080 | 0.300 | 0.310 | 0.319 |
| heading_error_deg | 6 | 2.048 | 1.665 | 2.451 | 0.786 | 2.618 | 2.666 | 2.715 |
| speed_error_mps | 6 | 0.125 | 0.088 | 0.291 | 0.203 | 0.483 | 0.556 | 0.630 |
| velocity_error_mps | 6 | 0.374 | 0.350 | 0.506 | 0.156 | 0.681 | 0.749 | 0.816 |

Calibration of pos_std_m over 75 states: within 1/2/3 sigma 0.893/1.000/1.000 (Gaussian: 0.393/0.865/0.989).
