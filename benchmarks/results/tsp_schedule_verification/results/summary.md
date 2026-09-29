# TSP benchmark

Python: 3.14.4; CPU: Intel64 Family 6 Model 186 Stepping 3, GenuineIntel; system: Windows-11-10.0.26200-SP0.
Sizes: [6, 10, 15, 20]; instance seeds: [202600, 202601, 202602, 202603, 202604, 202605, 202606, 202607, 202608, 202609]; solver seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9].
Each solver receives 1 read(s) x 100 sweeps x n^2 attempted operations per run (40,000 at n=20 under the recorded settings). Attempts per city are num_reads x num_sweeps x n.
QUBO-SA counts bit-flip attempts; QUBO-SA-swap counts swap proposals; multi-start 2-opt counts candidate tour evaluations. Equal counts do not imply equal computational cost. Wall-clock time is recorded but is not the stopping budget.
All references are proven Held-Karp optima for each instance. Mean gap uses feasible runs only. A 5,000-replicate percentile bootstrap resamples independent instances for the 95% CI.
Swap schedule: beta_start=1, beta_end=30, normalized by max_distance. It was selected on separate instances; see [tuning](swap_tuning.md).

| Cities | Solver | Feasible | Mean gap [95% CI] | Mean attempts / target | Attempts per city | Mean runtime (s) |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 6 | qubo_sa | 100/100 | 4.14% [2.72, 5.63] | 3600 / 3600 | 600 | 0.0284 |
| 6 | qubo_sa_swap | 100/100 | 0.00% [0.00, 0.00] | 3600 / 3600 | 600 | 0.0426 |
| 6 | two_opt | 100/100 | 0.00% [0.00, 0.00] | 3600 / 3600 | 600 | 0.0259 |
| 10 | qubo_sa | 99/100 | 32.87% [29.06, 36.61] | 10000 / 10000 | 1000 | 0.1445 |
| 10 | qubo_sa_swap | 100/100 | 0.27% [0.00, 0.65] | 10000 / 10000 | 1000 | 0.2045 |
| 10 | two_opt | 100/100 | 0.41% [0.00, 1.23] | 10000 / 10000 | 1000 | 0.1205 |
| 15 | qubo_sa | 98/100 | 65.22% [60.56, 69.91] | 22500 / 22500 | 1500 | 0.3535 |
| 15 | qubo_sa_swap | 100/100 | 1.43% [0.52, 2.49] | 22500 / 22500 | 1500 | 0.4741 |
| 15 | two_opt | 100/100 | 0.00% [0.00, 0.00] | 22500 / 22500 | 1500 | 0.3384 |
| 20 | qubo_sa | 98/100 | 86.65% [77.37, 95.89] | 40000 / 40000 | 2000 | 0.6824 |
| 20 | qubo_sa_swap | 100/100 | 3.69% [2.59, 4.97] | 40000 / 40000 | 2000 | 0.8616 |
| 20 | two_opt | 100/100 | 0.37% [0.00, 1.08] | 40000 / 40000 | 2000 | 0.7671 |

## Paired solver comparisons

Differences are solver B minus solver A in percentage points, using paired instance and solver seeds where both runs are feasible. Exact sign flips are applied to the ten within-instance mean differences. The p-values are descriptive and are not used to select the swap schedule.

| Cities | Solver A | Solver B | Paired runs | Paired instances | Mean gap difference (B-A, pp) | Paired p |
| ---: | --- | --- | ---: | ---: | ---: | ---: |
| 6 | qubo_sa | qubo_sa_swap | 100 | 10 | -4.140 | 0.0020 |
| 6 | qubo_sa | two_opt | 100 | 10 | -4.140 | 0.0020 |
| 6 | qubo_sa_swap | two_opt | 100 | 10 | -0.000 | 1.0000 |
| 10 | qubo_sa | qubo_sa_swap | 99 | 10 | -32.591 | 0.0020 |
| 10 | qubo_sa | two_opt | 99 | 10 | -32.453 | 0.0020 |
| 10 | qubo_sa_swap | two_opt | 100 | 10 | 0.137 | 1.0000 |
| 15 | qubo_sa | qubo_sa_swap | 98 | 10 | -63.822 | 0.0020 |
| 15 | qubo_sa | two_opt | 98 | 10 | -65.224 | 0.0020 |
| 15 | qubo_sa_swap | two_opt | 100 | 10 | -1.431 | 0.0039 |
| 20 | qubo_sa | qubo_sa_swap | 98 | 10 | -82.923 | 0.0020 |
| 20 | qubo_sa | two_opt | 98 | 10 | -86.275 | 0.0020 |
| 20 | qubo_sa_swap | two_opt | 100 | 10 | -3.316 | 0.0059 |
