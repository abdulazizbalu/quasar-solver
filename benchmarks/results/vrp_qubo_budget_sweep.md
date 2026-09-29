# Tiny CVRP QUBO budget and schedule sweep

Ten independent random instances per size; five use tight and five use loose capacity. One annealer seed is used per instance and cell; confidence intervals bootstrap independent instances, not repeated solver seeds. Every reference was CP-SAT proven optimal. Gaps are conditional on feasible runs.

| Customers | Sweeps / variable | Schedule | Feasible [95% CI] | Optimal hits [95% CI] | Mean gap on feasible [95% CI] | Variables | Mean flips | Mean runtime |
| ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 4 | 100 | coefficient_scaled_linear | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | n/a | 44–48 | 4660 | 0.067 s |
| 4 | 100 | penalty_scaled_geometric | 20.0% [0.0, 50.0] | 0.0% [0.0, 0.0] | 46.9% [38.5, 55.3] | 44–48 | 4660 | 0.068 s |
| 4 | 500 | coefficient_scaled_linear | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | n/a | 44–48 | 23300 | 0.317 s |
| 4 | 500 | penalty_scaled_geometric | 30.0% [0.0, 60.0] | 10.0% [0.0, 30.0] | 41.4% [0.0, 80.0] | 44–48 | 23300 | 0.327 s |
| 4 | 2000 | coefficient_scaled_linear | 10.0% [0.0, 30.0] | 10.0% [0.0, 30.0] | 0.0% [CI unavailable] | 44–48 | 93200 | 1.261 s |
| 4 | 2000 | penalty_scaled_geometric | 80.0% [50.0, 100.0] | 50.0% [20.0, 80.0] | 21.6% [2.5, 46.9] | 44–48 | 93200 | 1.300 s |
| 4 | 10000 | coefficient_scaled_linear | 10.0% [0.0, 30.0] | 10.0% [0.0, 30.0] | 0.0% [CI unavailable] | 44–48 | 466000 | 6.327 s |
| 4 | 10000 | penalty_scaled_geometric | 90.0% [70.0, 100.0] | 50.0% [20.0, 80.0] | 12.6% [2.2, 24.1] | 44–48 | 466000 | 6.522 s |
| 5 | 100 | coefficient_scaled_linear | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | n/a | 66–68 | 6700 | 0.094 s |
| 5 | 100 | penalty_scaled_geometric | 10.0% [0.0, 30.0] | 0.0% [0.0, 0.0] | 29.4% [CI unavailable] | 66–68 | 6700 | 0.092 s |
| 5 | 500 | coefficient_scaled_linear | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | n/a | 66–68 | 33500 | 0.450 s |
| 5 | 500 | penalty_scaled_geometric | 20.0% [0.0, 50.0] | 10.0% [0.0, 30.0] | 14.7% [0.0, 29.4] | 66–68 | 33500 | 0.481 s |
| 5 | 2000 | coefficient_scaled_linear | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | n/a | 66–68 | 134000 | 1.846 s |
| 5 | 2000 | penalty_scaled_geometric | 20.0% [0.0, 50.0] | 10.0% [0.0, 30.0] | 4.2% [0.0, 8.4] | 66–68 | 134000 | 1.895 s |
| 5 | 10000 | coefficient_scaled_linear | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | n/a | 66–68 | 670000 | 9.111 s |
| 5 | 10000 | penalty_scaled_geometric | 70.0% [40.0, 100.0] | 20.0% [0.0, 50.0] | 23.9% [10.0, 38.2] | 66–68 | 670000 | 9.333 s |
| 6 | 100 | coefficient_scaled_linear | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | n/a | 90–92 | 9100 | 0.128 s |
| 6 | 100 | penalty_scaled_geometric | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | n/a | 90–92 | 9100 | 0.139 s |
| 6 | 500 | coefficient_scaled_linear | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | n/a | 90–92 | 45500 | 0.646 s |
| 6 | 500 | penalty_scaled_geometric | 10.0% [0.0, 30.0] | 0.0% [0.0, 0.0] | 51.7% [CI unavailable] | 90–92 | 45500 | 0.652 s |
| 6 | 2000 | coefficient_scaled_linear | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | n/a | 90–92 | 182000 | 2.537 s |
| 6 | 2000 | penalty_scaled_geometric | 30.0% [0.0, 60.0] | 0.0% [0.0, 0.0] | 39.3% [24.6, 63.2] | 90–92 | 182000 | 2.593 s |
| 6 | 10000 | coefficient_scaled_linear | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | n/a | 90–92 | 910000 | 12.534 s |
| 6 | 10000 | penalty_scaled_geometric | 30.0% [0.0, 60.0] | 0.0% [0.0, 0.0] | 18.7% [7.9, 37.7] | 90–92 | 910000 | 12.887 s |
