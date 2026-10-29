# Road-user fusion against ground truth - S06/run_0_crash

Privileged evaluation (ground truth used here only). Assumptions: recorder raw clocks are CARLA simulator time; a vehicle box is centred on its origin in the horizontal plane.

## Track identity decisions (aligned recorders)

| Track | Decision | Status | By | True identity | Purity | Verdict |
|-------|----------|--------|----|---------------|-------:|---------|
| A:track_001 | C | ASSOCIATED | common_frame | C | 1.000 | correct link |
| A:track_002 | B | ASSOCIATED | collision | B | 1.000 | correct link |
| B:track_001 | C | ASSOCIATED | common_frame | C | 1.000 | correct link |
| B:track_002 | A | ASSOCIATED | collision | A | 1.000 | correct link |
| C:track_001 | A | ASSOCIATED | common_frame | A | 1.000 | correct link |
| C:track_002 | U1 | ANONYMOUS | - | A | 0.800 | missed link (true identity A) |

Counts: correct link: 5, missed link: 1

## Anonymous entities

| Entity | Source tracks | True identity | Recorder? | Purity |
|--------|---------------|---------------|-----------|-------:|
| U1 | C:track_002 | A | yes | 0.800 |

Merges over pairs of anonymous tracks: correct 0, false 0, missed 0.
Fragmentation (true road user -> entities): A -> U1

## Fused state errors (against the majority identity, 106 pure states; 25 impure states where a source track was on another body, excluded)

| Quantity | n | median | q25 | q75 | IQR | p90 | p95 | max |
|----------|--:|-------:|----:|----:|----:|----:|----:|----:|
| centre_error_m | 106 | 1.813 | 1.768 | 1.844 | 0.076 | 1.849 | 1.851 | 1.853 |
| coverage_s | 1 | 13.050 | 13.050 | 13.050 | 0.000 | 13.050 | 13.050 | 13.050 |
| heading_error_deg | 1 | 69.637 | 69.637 | 69.637 | 0.000 | 69.637 | 69.637 | 69.637 |
| length_error_m | 1 | 0.192 | 0.192 | 0.192 | 0.000 | 0.192 | 0.192 | 0.192 |
| normalised_centre_error | 106 | 10.979 | 9.684 | 11.827 | 2.143 | 12.005 | 12.029 | 12.111 |
| single_track_nominal_centre_error_m | 105 | 1.937 | 1.894 | 1.964 | 0.070 | 1.970 | 1.978 | 1.986 |
| speed_error_mps | 106 | 0.062 | 0.020 | 0.103 | 0.083 | 0.919 | 1.225 | 1.893 |
| velocity_error_mps | 106 | 0.062 | 0.020 | 0.103 | 0.083 | 0.919 | 1.257 | 3.522 |
| width_error_m | 1 | 0.263 | 0.263 | 0.263 | 0.000 | 0.263 | 0.263 | 0.263 |

### Method: covariance_intersection

| Quantity | n | median | q25 | q75 | IQR | p90 | p95 | max |
|----------|--:|-------:|----:|----:|----:|----:|----:|----:|
| centre_error_m | 106 | 1.813 | 1.768 | 1.844 | 0.076 | 1.849 | 1.851 | 1.853 |
| heading_error_deg | 1 | 69.637 | 69.637 | 69.637 | 0.000 | 69.637 | 69.637 | 69.637 |
| speed_error_mps | 106 | 0.062 | 0.020 | 0.103 | 0.083 | 0.919 | 1.225 | 1.893 |
| velocity_error_mps | 106 | 0.062 | 0.020 | 0.103 | 0.083 | 0.919 | 1.257 | 3.522 |

Calibration of pos_std_m over 106 states: within 1/2/3 sigma 0.000/0.000/0.000 (Gaussian: 0.393/0.865/0.989).

## Observed-trajectory alignment

| Recorder | Accepted | Estimated offset | True offset | Error | Interval |
|----------|----------|-----------------:|------------:|------:|----------|
| C | True | -4.150 | -4.100 | -0.050 | [-4.2, -4.0] |
