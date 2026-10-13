# Tiny CVRP QUBO budget and schedule sweep

Ten random instances per size (instance seeds 203100–203109; the same seed is reused across sizes, so instances are independent within a size, not across sizes); five use tight and five use loose capacity. One annealer seed is used per instance and cell, so each cell has ten independent binary outcomes. Feasible and optimal-hit columns show counts with 95% Wilson score intervals. Every reference was CP-SAT proven optimal.

Gaps are conditional on feasibility: they average only the feasible runs, whose number `n` is shown, so a cell with few feasible runs is not comparable with one with many. With fewer than five feasible runs the individual gaps are listed and no interval is given; otherwise the interval is a 95% percentile bootstrap over the feasible instances.

| Customers | Sweeps / variable | Schedule | Feasible [95% Wilson] | Optimal hits [95% Wilson] | Mean gap on feasible runs | Variables | Mean flips | Mean runtime |
| ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 4 | 100 | coefficient_scaled_linear | 0/10 [0, 28] | 0/10 [0, 28] | n/a (0 feasible) | 44–48 | 4660 | 0.067 s |
| 4 | 100 | penalty_scaled_geometric | 2/10 [6, 51] | 0/10 [0, 28] | 46.9% (n=2: 38.5, 55.3; no CI) | 44–48 | 4660 | 0.068 s |
| 4 | 500 | coefficient_scaled_linear | 0/10 [0, 28] | 0/10 [0, 28] | n/a (0 feasible) | 44–48 | 23300 | 0.317 s |
| 4 | 500 | penalty_scaled_geometric | 3/10 [11, 60] | 1/10 [2, 40] | 41.4% (n=3: 0.0, 44.3, 80.0; no CI) | 44–48 | 23300 | 0.327 s |
| 4 | 2000 | coefficient_scaled_linear | 1/10 [2, 40] | 1/10 [2, 40] | 0.0% (n=1: 0.0; no CI) | 44–48 | 93200 | 1.261 s |
| 4 | 2000 | penalty_scaled_geometric | 8/10 [49, 94] | 5/10 [24, 76] | 21.6% (n=8) [2.5, 46.9] | 44–48 | 93200 | 1.300 s |
| 4 | 10000 | coefficient_scaled_linear | 1/10 [2, 40] | 1/10 [2, 40] | 0.0% (n=1: 0.0; no CI) | 44–48 | 466000 | 6.327 s |
| 4 | 10000 | penalty_scaled_geometric | 9/10 [60, 98] | 5/10 [24, 76] | 12.6% (n=9) [2.2, 24.1] | 44–48 | 466000 | 6.522 s |
| 5 | 100 | coefficient_scaled_linear | 0/10 [0, 28] | 0/10 [0, 28] | n/a (0 feasible) | 66–68 | 6700 | 0.094 s |
| 5 | 100 | penalty_scaled_geometric | 1/10 [2, 40] | 0/10 [0, 28] | 29.4% (n=1: 29.4; no CI) | 66–68 | 6700 | 0.092 s |
| 5 | 500 | coefficient_scaled_linear | 0/10 [0, 28] | 0/10 [0, 28] | n/a (0 feasible) | 66–68 | 33500 | 0.450 s |
| 5 | 500 | penalty_scaled_geometric | 2/10 [6, 51] | 1/10 [2, 40] | 14.7% (n=2: 0.0, 29.4; no CI) | 66–68 | 33500 | 0.481 s |
| 5 | 2000 | coefficient_scaled_linear | 0/10 [0, 28] | 0/10 [0, 28] | n/a (0 feasible) | 66–68 | 134000 | 1.846 s |
| 5 | 2000 | penalty_scaled_geometric | 2/10 [6, 51] | 1/10 [2, 40] | 4.2% (n=2: 0.0, 8.4; no CI) | 66–68 | 134000 | 1.895 s |
| 5 | 10000 | coefficient_scaled_linear | 0/10 [0, 28] | 0/10 [0, 28] | n/a (0 feasible) | 66–68 | 670000 | 9.111 s |
| 5 | 10000 | penalty_scaled_geometric | 7/10 [40, 89] | 2/10 [6, 51] | 23.9% (n=7) [10.0, 38.2] | 66–68 | 670000 | 9.333 s |
| 6 | 100 | coefficient_scaled_linear | 0/10 [0, 28] | 0/10 [0, 28] | n/a (0 feasible) | 90–92 | 9100 | 0.128 s |
| 6 | 100 | penalty_scaled_geometric | 0/10 [0, 28] | 0/10 [0, 28] | n/a (0 feasible) | 90–92 | 9100 | 0.139 s |
| 6 | 500 | coefficient_scaled_linear | 0/10 [0, 28] | 0/10 [0, 28] | n/a (0 feasible) | 90–92 | 45500 | 0.646 s |
| 6 | 500 | penalty_scaled_geometric | 1/10 [2, 40] | 0/10 [0, 28] | 51.7% (n=1: 51.7; no CI) | 90–92 | 45500 | 0.652 s |
| 6 | 2000 | coefficient_scaled_linear | 0/10 [0, 28] | 0/10 [0, 28] | n/a (0 feasible) | 90–92 | 182000 | 2.537 s |
| 6 | 2000 | penalty_scaled_geometric | 3/10 [11, 60] | 0/10 [0, 28] | 39.3% (n=3: 24.6, 30.1, 63.2; no CI) | 90–92 | 182000 | 2.593 s |
| 6 | 10000 | coefficient_scaled_linear | 0/10 [0, 28] | 0/10 [0, 28] | n/a (0 feasible) | 90–92 | 910000 | 12.534 s |
| 6 | 10000 | penalty_scaled_geometric | 3/10 [11, 60] | 0/10 [0, 28] | 18.7% (n=3: 7.9, 10.6, 37.7; no CI) | 90–92 | 910000 | 12.887 s |
