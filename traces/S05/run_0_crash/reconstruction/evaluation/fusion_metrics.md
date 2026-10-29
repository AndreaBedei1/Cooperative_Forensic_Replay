# Road-user fusion against ground truth - S05/run_0_crash

Privileged evaluation (ground truth used here only). Assumptions: recorder raw clocks are CARLA simulator time; a vehicle box is centred on its origin in the horizontal plane.

## Track identity decisions (aligned recorders)

| Track | Decision | Status | By | True identity | Purity | Verdict |
|-------|----------|--------|----|---------------|-------:|---------|
| A:track_001 | B | ASSOCIATED | collision | B | 1.000 | correct link |
| B:track_001 | C | ASSOCIATED | common_frame | C | 1.000 | correct link |

Counts: correct link: 2

## Anonymous entities

| Entity | Source tracks | True identity | Recorder? | Purity |
|--------|---------------|---------------|-----------|-------:|

Merges over pairs of anonymous tracks: correct 0, false 0, missed 0.
Fragmentation (true road user -> entities): none

## Fused state errors (against the majority identity, 0 pure states; 0 impure states where a source track was on another body, excluded)

| Quantity | n | median | q25 | q75 | IQR | p90 | p95 | max |
|----------|--:|-------:|----:|----:|----:|----:|----:|----:|

Calibration of pos_std_m over 0 states: within 1/2/3 sigma 0.000/0.000/0.000 (Gaussian: 0.393/0.865/0.989).

## Observed-trajectory alignment

| Recorder | Accepted | Estimated offset | True offset | Error | Interval |
|----------|----------|-----------------:|------------:|------:|----------|
| C | True | -5.950 | -5.900 | -0.050 | [-5.95, -5.9] |
