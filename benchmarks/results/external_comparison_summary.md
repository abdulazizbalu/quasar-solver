# Optional external annealer comparison

Ten instances per size and ten solver seeds per instance. Confidence intervals bootstrap independent instances. External adapters receive the exact same QUBO coefficients as the in-repository solver, one read and 100 full-variable sweeps. Equivalent sweep counts do not imply equivalent kernels or elapsed time.

| Problem | Size | Solver | Feasible | Optimal hit | Mean gap [95% CI] | Mean runtime | Mean attempts | Variables |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| CVRP | 4 | dwave_sa (coefficient_scaled_linear) | 0/100 | 0/100 | n/a | 0.009 s | 4600 | 44–48 |
| CVRP | 4 | dwave_sa (penalty_scaled_geometric) | 9/100 | 2/100 | 10.04% [3.05, 18.16] | 0.005 s | 4600 | 44–48 |
| CVRP | 4 | exact_small (proven) | 100/100 | 100/100 | 0.00% [0.00, 0.00] | 0.012 s | — | — |
| CVRP | 4 | openjij_sa (coefficient_scaled_linear) | 0/100 | 0/100 | n/a | 0.014 s | 4600 | 44–48 |
| CVRP | 4 | openjij_sa (penalty_scaled_geometric) | 5/100 | 3/100 | 22.39% [0.00, 58.43] | 0.012 s | 4600 | 44–48 |
| CVRP | 4 | ortools (wall_clock) | 100/100 | 100/100 | 0.00% [0.00, 0.00] | 0.199 s | — | — |
| CVRP | 4 | qubo_sa (coefficient_scaled_linear) | 0/100 | 0/100 | n/a | 0.064 s | 4600 | 44–48 |
| CVRP | 4 | qubo_sa (penalty_scaled_geometric) | 16/100 | 8/100 | 22.02% [5.87, 41.02] | 0.066 s | 4600 | 44–48 |
| CVRP | 4 | vrp_sa (wall_clock) | 91/100 | 91/100 | 0.00% [0.00, 0.00] | 0.182 s | 4708 | — |
| CVRP | 5 | dwave_sa (coefficient_scaled_linear) | 0/100 | 0/100 | n/a | 0.009 s | 6680 | 66–68 |
| CVRP | 5 | dwave_sa (penalty_scaled_geometric) | 0/100 | 0/100 | n/a | 0.009 s | 6680 | 66–68 |
| CVRP | 5 | exact_small (proven) | 100/100 | 100/100 | 0.00% [0.00, 0.00] | 0.023 s | — | — |
| CVRP | 5 | openjij_sa (coefficient_scaled_linear) | 0/100 | 0/100 | n/a | 0.022 s | 6680 | 66–68 |
| CVRP | 5 | openjij_sa (penalty_scaled_geometric) | 3/100 | 0/100 | 43.59% [34.79, 52.38] | 0.023 s | 6680 | 66–68 |
| CVRP | 5 | ortools (wall_clock) | 100/100 | 100/100 | 0.00% [0.00, 0.00] | 0.198 s | — | — |
| CVRP | 5 | qubo_sa (coefficient_scaled_linear) | 0/100 | 0/100 | n/a | 0.096 s | 6680 | 66–68 |
| CVRP | 5 | qubo_sa (penalty_scaled_geometric) | 2/100 | 0/100 | 30.39% [17.20, 43.58] | 0.099 s | 6680 | 66–68 |
| CVRP | 5 | vrp_sa (wall_clock) | 97/100 | 97/100 | 0.00% [0.00, 0.00] | 0.194 s | 3632 | — |
| CVRP | 6 | dwave_sa (coefficient_scaled_linear) | 0/100 | 0/100 | n/a | 0.015 s | 9120 | 90–92 |
| CVRP | 6 | dwave_sa (penalty_scaled_geometric) | 3/100 | 0/100 | 34.33% [14.48, 59.84] | 0.014 s | 9120 | 90–92 |
| CVRP | 6 | exact_small (proven) | 100/100 | 100/100 | 0.00% [0.00, 0.00] | 0.026 s | — | — |
| CVRP | 6 | openjij_sa (coefficient_scaled_linear) | 0/100 | 0/100 | n/a | 0.039 s | 9120 | 90–92 |
| CVRP | 6 | openjij_sa (penalty_scaled_geometric) | 3/100 | 0/100 | 60.50% [39.33, 81.67] | 0.039 s | 9120 | 90–92 |
| CVRP | 6 | ortools (wall_clock) | 100/100 | 100/100 | 0.00% [0.00, 0.00] | 0.201 s | — | — |
| CVRP | 6 | qubo_sa (coefficient_scaled_linear) | 0/100 | 0/100 | n/a | 0.135 s | 9120 | 90–92 |
| CVRP | 6 | qubo_sa (penalty_scaled_geometric) | 1/100 | 0/100 | 59.45% [CI unavailable] | 0.136 s | 9120 | 90–92 |
| CVRP | 6 | vrp_sa (wall_clock) | 90/100 | 87/100 | 0.63% [0.00, 1.89] | 0.180 s | 3192 | — |
| TSP | 6 | dwave_sa (coefficient_scaled_linear) | 88/100 | 13/100 | 13.34% [9.62, 17.33] | 0.007 s | 3600 | 36 |
| TSP | 6 | openjij_sa (coefficient_scaled_linear) | 87/100 | 7/100 | 16.34% [13.08, 19.64] | 0.011 s | 3600 | 36 |
| TSP | 6 | qubo_sa_old (coefficient_scaled_linear) | 100/100 | 45/100 | 4.14% [2.64, 5.62] | 0.041 s | 3600 | 36 |
| TSP | 6 | qubo_sa_penalty (penalty_scaled_geometric) | 99/100 | 20/100 | 8.61% [6.18, 10.63] | 0.041 s | 3600 | 36 |
| TSP | 6 | qubo_sa_swap (baseline) | 100/100 | 100/100 | 0.00% [0.00, 0.00] | 0.059 s | 3600 | 36 |
| TSP | 6 | two_opt (baseline) | 100/100 | 100/100 | 0.00% [0.00, 0.00] | 0.034 s | 3600 | 36 |
| TSP | 10 | dwave_sa (coefficient_scaled_linear) | 88/100 | 0/100 | 41.41% [38.41, 44.57] | 0.013 s | 10000 | 100 |
| TSP | 10 | openjij_sa (coefficient_scaled_linear) | 90/100 | 0/100 | 42.66% [38.94, 46.26] | 0.035 s | 10000 | 100 |
| TSP | 10 | qubo_sa_old (coefficient_scaled_linear) | 99/100 | 0/100 | 32.96% [29.18, 36.69] | 0.149 s | 10000 | 100 |
| TSP | 10 | qubo_sa_penalty (penalty_scaled_geometric) | 100/100 | 0/100 | 43.33% [40.28, 47.02] | 0.148 s | 10000 | 100 |
| TSP | 10 | qubo_sa_swap (baseline) | 100/100 | 93/100 | 0.27% [0.00, 0.65] | 0.206 s | 10000 | 100 |
| TSP | 10 | two_opt (baseline) | 100/100 | 90/100 | 0.41% [0.00, 1.23] | 0.124 s | 10000 | 100 |
| TSP | 15 | dwave_sa (coefficient_scaled_linear) | 90/100 | 0/100 | 73.42% [68.82, 78.88] | 0.040 s | 22500 | 225 |
| TSP | 15 | openjij_sa (coefficient_scaled_linear) | 89/100 | 0/100 | 75.62% [69.83, 82.06] | 0.114 s | 22500 | 225 |
| TSP | 15 | qubo_sa_old (coefficient_scaled_linear) | 98/100 | 0/100 | 65.24% [60.56, 69.79] | 0.359 s | 22500 | 225 |
| TSP | 15 | qubo_sa_penalty (penalty_scaled_geometric) | 95/100 | 0/100 | 81.45% [75.54, 87.20] | 0.353 s | 22500 | 225 |
| TSP | 15 | qubo_sa_swap (baseline) | 100/100 | 57/100 | 1.43% [0.48, 2.50] | 0.474 s | 22500 | 225 |
| TSP | 15 | two_opt (baseline) | 100/100 | 100/100 | 0.00% [0.00, 0.00] | 0.346 s | 22500 | 225 |
| TSP | 20 | dwave_sa (coefficient_scaled_linear) | 82/100 | 0/100 | 98.41% [90.70, 105.38] | 0.098 s | 40000 | 400 |
| TSP | 20 | openjij_sa (coefficient_scaled_linear) | 81/100 | 0/100 | 98.53% [89.30, 107.17] | 0.273 s | 40000 | 400 |
| TSP | 20 | qubo_sa_old (coefficient_scaled_linear) | 98/100 | 0/100 | 86.60% [77.17, 96.37] | 0.686 s | 40000 | 400 |
| TSP | 20 | qubo_sa_penalty (penalty_scaled_geometric) | 93/100 | 0/100 | 104.65% [95.76, 112.67] | 0.687 s | 40000 | 400 |
| TSP | 20 | qubo_sa_swap (baseline) | 100/100 | 29/100 | 3.69% [2.51, 5.02] | 0.864 s | 40000 | 400 |
| TSP | 20 | two_opt (baseline) | 100/100 | 80/100 | 0.37% [0.00, 1.08] | 0.777 s | 40000 | 400 |
