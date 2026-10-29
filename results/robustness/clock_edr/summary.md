# Clock residuals and crash-recorder reports

## Residual clock offsets (uniform within +-50 ms per recorder)

| condition | jobs | failed | pairs | error median / P95 / max [ms] | within 50 ms | unaligned (unshifted / shifted) | recorder events: jobs unchanged, order changes / pairs | all events: jobs unchanged, order changes / pairs | reproduces committed |
|---|--:|--:|--:|---|--:|---|---|---|--:|
| G0 | 66 | 0 | 84 | 0.0 / 50.0 / 50.1 | 80 | 0 / 0 | 65, 80 / 31821 | 65, 91 / 70072 | 66 |
| G2+severe | 66 | 0 | 82 | 0.0 / 0.1 / 50.1 | 80 | 1 / 2 | 52, 134 / 33635 | 7, 57729 / 2359686 | - |

## Crash-recorder-like collision reports (delta-V and mass errors, +-10 ms timing)

| condition | delta-V 1-sigma | jobs | failed | identified / reportable | invented | matched events | impulse ratio min / P5 / median | unaligned | max relative offset [ms] |
|---|---|--:|--:|---|--:|--:|---|--:|--:|
| G0 | 10 % | 66 | 0 | 78 / 78 (1.000) | 0 | 81 | 0.690 / 0.716 / 0.877 | 0 | 64.8 |
| G0 | 5 % | 66 | 0 | 78 / 78 (1.000) | 0 | 81 | 0.784 / 0.811 / 0.931 | 0 | 64.8 |
| G2+severe | 10 % | 66 | 0 | 78 / 78 (1.000) | 0 | 81 | 0.690 / 0.716 / 0.877 | 1 | 58.9 |
| G2+severe | 5 % | 66 | 0 | 78 / 78 (1.000) | 0 | 81 | 0.784 / 0.811 / 0.931 | 1 | 58.9 |

## Trigger census (26 true contacts; trigger 8.0 km/h within 150 ms)

| delta-V from | every recorder triggers | at least one recorder triggers | none triggers |
|---|--:|--:|--:|
| impulse / 1500 kg | 14 | 14 | 12 |
| recorded velocity | 9 | 16 | 10 |

Recorders without a road map although the incident names one: 0.
