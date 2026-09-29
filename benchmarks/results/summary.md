# TSP benchmark

Python: 3.14.4; CPU: Intel64 Family 6 Model 186 Stepping 3, GenuineIntel; system: Windows-11-10.0.26200-SP0.

Instance seeds: [202600, 202601, 202602, 202603, 202604, 202605, 202606, 202607, 202608, 202609] (separate from solver seeds [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]).
Each instance/solver-seed pair gets 1 read(s) × 100 sweeps; each sweep attempts one flip for each of the V=n² QUBO binary variables. Total target is num_reads × num_sweeps × V; at 20 cities that is 40,000 flips. Time limit is a secondary cap: none.
The `two_opt` baseline receives the same number of candidate move evaluations as QUBO-SA attempted flips. Instances with n ≤ 12 use a proven Held–Karp optimum. For n=15 and 20, each instance uses one shared best feasible tour found across all solvers/seeds, labeled best found, not proven.
Gap means use feasible runs only. The 95% confidence interval is a 5,000-replicate percentile bootstrap that resamples whole instances; raw paired runs are preserved in raw.csv.

| Cities | Solver | Penalty | Runs | Feasible | Mean gap [95% instance-bootstrap CI] | Mean runtime (s) | Reference |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 6 | qubo_sa | 1 | 100 | 100.0% | 4.14% [2.72, 5.63] (n=100) | 0.0566 | proven optimum |
| 6 | qubo_sa | 10 | 100 | 100.0% | 13.24% [10.62, 15.77] (n=100) | 0.0587 | proven optimum |
| 6 | qubo_sa | 2 | 100 | 100.0% | 9.33% [7.10, 11.51] (n=100) | 0.0571 | proven optimum |
| 6 | qubo_sa | 5 | 100 | 100.0% | 14.26% [11.91, 16.57] (n=100) | 0.0585 | proven optimum |
| 6 | qubo_sa | 50 | 100 | 100.0% | 11.91% [9.02, 14.59] (n=100) | 0.0583 | proven optimum |
| 6 | qubo_sa | fixed_100 | 100 | 100.0% | 14.00% [10.53, 17.42] (n=100) | 0.0579 | proven optimum |
| 6 | two_opt | n/a | 100 | 100.0% | 0.00% [-0.00, 0.00] (n=100) | 0.0512 | proven optimum |
| 10 | qubo_sa | 1 | 100 | 99.0% | 32.87% [29.02, 36.52] (n=99) | 0.1661 | proven optimum |
| 10 | qubo_sa | 10 | 100 | 100.0% | 61.49% [55.24, 67.14] (n=100) | 0.1640 | proven optimum |
| 10 | qubo_sa | 2 | 100 | 100.0% | 49.07% [44.58, 54.44] (n=100) | 0.1636 | proven optimum |
| 10 | qubo_sa | 5 | 100 | 100.0% | 59.59% [53.79, 65.39] (n=100) | 0.1651 | proven optimum |
| 10 | qubo_sa | 50 | 100 | 100.0% | 64.06% [56.61, 71.36] (n=100) | 0.1634 | proven optimum |
| 10 | qubo_sa | fixed_100 | 100 | 100.0% | 62.60% [55.90, 68.83] (n=100) | 0.1639 | proven optimum |
| 10 | two_opt | n/a | 100 | 100.0% | 0.41% [-0.00, 1.23] (n=100) | 0.1335 | proven optimum |
| 15 | qubo_sa | 1 | 100 | 98.0% | 65.22% [60.66, 69.76] (n=98) | 0.2372 | best found, not proven |
| 15 | qubo_sa | 10 | 100 | 100.0% | 118.41% [106.86, 127.69] (n=100) | 0.2402 | best found, not proven |
| 15 | qubo_sa | 2 | 100 | 100.0% | 96.25% [89.11, 102.81] (n=100) | 0.2431 | best found, not proven |
| 15 | qubo_sa | 5 | 100 | 100.0% | 111.53% [101.61, 121.19] (n=100) | 0.2407 | best found, not proven |
| 15 | qubo_sa | 50 | 100 | 100.0% | 124.30% [113.15, 134.59] (n=100) | 0.2396 | best found, not proven |
| 15 | qubo_sa | fixed_100 | 100 | 100.0% | 120.95% [112.00, 129.13] (n=100) | 0.2389 | best found, not proven |
| 15 | two_opt | n/a | 100 | 100.0% | 0.00% [0.00, 0.00] (n=100) | 0.2743 | best found, not proven |
| 20 | qubo_sa | 1 | 100 | 98.0% | 86.03% [76.10, 95.77] (n=98) | 0.3658 | best found, not proven |
| 20 | qubo_sa | 10 | 100 | 99.0% | 144.23% [131.11, 155.69] (n=99) | 0.3901 | best found, not proven |
| 20 | qubo_sa | 2 | 100 | 99.0% | 120.75% [111.91, 128.90] (n=99) | 0.3937 | best found, not proven |
| 20 | qubo_sa | 5 | 100 | 99.0% | 140.51% [125.02, 154.15] (n=99) | 0.3906 | best found, not proven |
| 20 | qubo_sa | 50 | 100 | 100.0% | 155.13% [139.94, 169.28] (n=100) | 0.3811 | best found, not proven |
| 20 | qubo_sa | fixed_100 | 100 | 100.0% | 156.39% [141.41, 170.24] (n=100) | 0.3669 | best found, not proven |
| 20 | two_opt | n/a | 100 | 100.0% | 0.01% [0.00, 0.02] (n=100) | 0.5961 | best found, not proven |

## Paired alpha comparisons (all pairs)

For each alpha pair, the gap difference is alpha B minus alpha A over paired instance-seed/solver-seed observations where both are feasible. Gap tests use exact sign flips of within-instance mean differences for up to 20 instances (otherwise 20,000 draws); feasibility uses an exact paired sign test over instances with discordant outcomes. These tests treat instances as independent units. Holm correction is applied to all 15 pair comparisons within each size.

| Cities | Alpha A | Alpha B | Paired runs | Paired instances | Mean gap difference (B−A, pp) | Gap p (Holm) | Feasibility discordant runs | B only feasible | A only feasible | Discordant instances | Feasibility p (Holm) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 6 | 1 | 2 | 100 | 10 | 5.192 | 0.029 | 0 | 0 | 0 | 0 | 1.000 |
| 6 | 1 | 5 | 100 | 10 | 10.123 | 0.029 | 0 | 0 | 0 | 0 | 1.000 |
| 6 | 1 | 10 | 100 | 10 | 9.100 | 0.029 | 0 | 0 | 0 | 0 | 1.000 |
| 6 | 1 | 50 | 100 | 10 | 7.768 | 0.029 | 0 | 0 | 0 | 0 | 1.000 |
| 6 | 1 | fixed_100 | 100 | 10 | 9.855 | 0.029 | 0 | 0 | 0 | 0 | 1.000 |
| 6 | 2 | 5 | 100 | 10 | 4.931 | 0.029 | 0 | 0 | 0 | 0 | 1.000 |
| 6 | 2 | 10 | 100 | 10 | 3.908 | 0.141 | 0 | 0 | 0 | 0 | 1.000 |
| 6 | 2 | 50 | 100 | 10 | 2.576 | 0.750 | 0 | 0 | 0 | 0 | 1.000 |
| 6 | 2 | fixed_100 | 100 | 10 | 4.663 | 0.203 | 0 | 0 | 0 | 0 | 1.000 |
| 6 | 5 | 10 | 100 | 10 | -1.023 | 0.811 | 0 | 0 | 0 | 0 | 1.000 |
| 6 | 5 | 50 | 100 | 10 | -2.354 | 0.465 | 0 | 0 | 0 | 0 | 1.000 |
| 6 | 5 | fixed_100 | 100 | 10 | -0.267 | 0.852 | 0 | 0 | 0 | 0 | 1.000 |
| 6 | 10 | 50 | 100 | 10 | -1.332 | 0.811 | 0 | 0 | 0 | 0 | 1.000 |
| 6 | 10 | fixed_100 | 100 | 10 | 0.755 | 0.852 | 0 | 0 | 0 | 0 | 1.000 |
| 6 | 50 | fixed_100 | 100 | 10 | 2.087 | 0.811 | 0 | 0 | 0 | 0 | 1.000 |
| 10 | 1 | 2 | 99 | 10 | 15.923 | 0.029 | 1 | 1 | 0 | 1 | 1.000 |
| 10 | 1 | 5 | 99 | 10 | 26.842 | 0.029 | 1 | 1 | 0 | 1 | 1.000 |
| 10 | 1 | 10 | 99 | 10 | 28.586 | 0.029 | 1 | 1 | 0 | 1 | 1.000 |
| 10 | 1 | 50 | 99 | 10 | 31.088 | 0.029 | 1 | 1 | 0 | 1 | 1.000 |
| 10 | 1 | fixed_100 | 99 | 10 | 29.760 | 0.029 | 1 | 1 | 0 | 1 | 1.000 |
| 10 | 2 | 5 | 100 | 10 | 10.521 | 0.047 | 0 | 0 | 0 | 0 | 1.000 |
| 10 | 2 | 10 | 100 | 10 | 12.427 | 0.047 | 0 | 0 | 0 | 0 | 1.000 |
| 10 | 2 | 50 | 100 | 10 | 14.990 | 0.035 | 0 | 0 | 0 | 0 | 1.000 |
| 10 | 2 | fixed_100 | 100 | 10 | 13.532 | 0.029 | 0 | 0 | 0 | 0 | 1.000 |
| 10 | 5 | 10 | 100 | 10 | 1.905 | 1.000 | 0 | 0 | 0 | 0 | 1.000 |
| 10 | 5 | 50 | 100 | 10 | 4.469 | 0.164 | 0 | 0 | 0 | 0 | 1.000 |
| 10 | 5 | fixed_100 | 100 | 10 | 3.011 | 0.898 | 0 | 0 | 0 | 0 | 1.000 |
| 10 | 10 | 50 | 100 | 10 | 2.563 | 0.791 | 0 | 0 | 0 | 0 | 1.000 |
| 10 | 10 | fixed_100 | 100 | 10 | 1.106 | 1.000 | 0 | 0 | 0 | 0 | 1.000 |
| 10 | 50 | fixed_100 | 100 | 10 | -1.458 | 1.000 | 0 | 0 | 0 | 0 | 1.000 |
| 15 | 1 | 2 | 98 | 10 | 31.005 | 0.029 | 2 | 2 | 0 | 2 | 1.000 |
| 15 | 1 | 5 | 98 | 10 | 46.089 | 0.029 | 2 | 2 | 0 | 2 | 1.000 |
| 15 | 1 | 10 | 98 | 10 | 52.603 | 0.029 | 2 | 2 | 0 | 2 | 1.000 |
| 15 | 1 | 50 | 98 | 10 | 58.955 | 0.029 | 2 | 2 | 0 | 2 | 1.000 |
| 15 | 1 | fixed_100 | 98 | 10 | 55.684 | 0.029 | 2 | 2 | 0 | 2 | 1.000 |
| 15 | 2 | 5 | 100 | 10 | 15.280 | 0.029 | 0 | 0 | 0 | 0 | 1.000 |
| 15 | 2 | 10 | 100 | 10 | 22.166 | 0.029 | 0 | 0 | 0 | 0 | 1.000 |
| 15 | 2 | 50 | 100 | 10 | 28.054 | 0.029 | 0 | 0 | 0 | 0 | 1.000 |
| 15 | 2 | fixed_100 | 100 | 10 | 24.698 | 0.029 | 0 | 0 | 0 | 0 | 1.000 |
| 15 | 5 | 10 | 100 | 10 | 6.885 | 0.240 | 0 | 0 | 0 | 0 | 1.000 |
| 15 | 5 | 50 | 100 | 10 | 12.773 | 0.029 | 0 | 0 | 0 | 0 | 1.000 |
| 15 | 5 | fixed_100 | 100 | 10 | 9.418 | 0.068 | 0 | 0 | 0 | 0 | 1.000 |
| 15 | 10 | 50 | 100 | 10 | 5.888 | 0.195 | 0 | 0 | 0 | 0 | 1.000 |
| 15 | 10 | fixed_100 | 100 | 10 | 2.533 | 0.477 | 0 | 0 | 0 | 0 | 1.000 |
| 15 | 50 | fixed_100 | 100 | 10 | -3.356 | 0.477 | 0 | 0 | 0 | 0 | 1.000 |
| 20 | 1 | 2 | 97 | 10 | 34.541 | 0.029 | 3 | 2 | 1 | 3 | 1.000 |
| 20 | 1 | 5 | 97 | 10 | 55.372 | 0.029 | 3 | 2 | 1 | 3 | 1.000 |
| 20 | 1 | 10 | 97 | 10 | 58.225 | 0.029 | 3 | 2 | 1 | 1 | 1.000 |
| 20 | 1 | 50 | 98 | 10 | 69.562 | 0.029 | 2 | 2 | 0 | 2 | 1.000 |
| 20 | 1 | fixed_100 | 98 | 10 | 70.824 | 0.029 | 2 | 2 | 0 | 2 | 1.000 |
| 20 | 2 | 5 | 98 | 10 | 19.929 | 0.029 | 2 | 1 | 1 | 2 | 1.000 |
| 20 | 2 | 10 | 98 | 10 | 22.631 | 0.029 | 2 | 1 | 1 | 2 | 1.000 |
| 20 | 2 | 50 | 99 | 10 | 34.116 | 0.029 | 1 | 1 | 0 | 1 | 1.000 |
| 20 | 2 | fixed_100 | 99 | 10 | 35.272 | 0.029 | 1 | 1 | 0 | 1 | 1.000 |
| 20 | 5 | 10 | 98 | 10 | 2.863 | 0.379 | 2 | 1 | 1 | 2 | 1.000 |
| 20 | 5 | 50 | 99 | 10 | 14.282 | 0.029 | 1 | 1 | 0 | 1 | 1.000 |
| 20 | 5 | fixed_100 | 99 | 10 | 15.302 | 0.029 | 1 | 1 | 0 | 1 | 1.000 |
| 20 | 10 | 50 | 99 | 10 | 11.387 | 0.029 | 1 | 1 | 0 | 1 | 1.000 |
| 20 | 10 | fixed_100 | 99 | 10 | 12.783 | 0.029 | 1 | 1 | 0 | 1 | 1.000 |
| 20 | 50 | fixed_100 | 100 | 10 | 1.252 | 0.633 | 0 | 0 | 0 | 0 | 1.000 |
