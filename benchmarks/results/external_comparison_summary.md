# Optional external annealer comparison

Ten instances per size and ten solver seeds per instance. External adapters receive the exact same QUBO coefficients as the in-repository solver, one read and 100 full-variable sweeps. Equivalent sweep counts do not imply equivalent kernels or elapsed time.

Mean gap is computed over feasible runs only (it is conditional on feasibility, so compare it together with the feasible count): runs are first averaged within each instance, then across instances that have at least one feasible run. The main TSP table instead pools all feasible runs, so the same runs can show slightly different means there. The 95% interval bootstraps those instances and is shown only when at least five instances contribute.

`qubo_sa* (best_seen)` is the lowest-energy state visited during the run, as in the main TSP table; `qubo_sa* (final)` is the state at the end of the same run. D-Wave and OpenJij return final states, so the final rows are the like-for-like comparison.

| Problem | Size | Solver | Feasible | Optimal hit | Mean gap [95% CI] | Mean runtime | Mean attempts | Variables |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| CVRP | 4 | dwave_sa (coefficient_scaled_linear) | 0/100 | 0/100 | n/a | 0.004 s | 4600 | 44–48 |
| CVRP | 4 | dwave_sa (penalty_scaled_geometric) | 9/100 | 2/100 | 10.04% [3.05, 18.16] (6 inst.) | 0.004 s | 4600 | 44–48 |
| CVRP | 4 | exact_small (proven) | 100/100 | 100/100 | 0.00% [0.00, 0.00] (10 inst.) | 0.008 s | — | — |
| CVRP | 4 | openjij_sa (coefficient_scaled_linear) | 0/100 | 0/100 | n/a | 0.008 s | 4600 | 44–48 |
| CVRP | 4 | openjij_sa (penalty_scaled_geometric) | 5/100 | 3/100 | 22.39% (no CI; 4 inst.) | 0.008 s | 4600 | 44–48 |
| CVRP | 4 | ortools (wall_clock) | 100/100 | 100/100 | 0.00% [0.00, 0.00] (10 inst.) | 0.199 s | — | — |
| CVRP | 4 | qubo_sa (best_seen) (coefficient_scaled_linear) | 0/100 | 0/100 | n/a | 0.030 s | 4600 | 44–48 |
| CVRP | 4 | qubo_sa (best_seen) (penalty_scaled_geometric) | 16/100 | 8/100 | 22.02% [5.88, 40.69] (9 inst.) | 0.029 s | 4600 | 44–48 |
| CVRP | 4 | qubo_sa (final) (coefficient_scaled_linear) | 0/100 | 0/100 | n/a | 0.030 s | 4600 | 44–48 |
| CVRP | 4 | qubo_sa (final) (penalty_scaled_geometric) | 10/100 | 4/100 | 16.35% [1.66, 33.51] (7 inst.) | 0.029 s | 4600 | 44–48 |
| CVRP | 4 | vrp_sa (wall_clock) | 91/100 | 91/100 | 0.00% [0.00, 0.00] (10 inst.) | 0.182 s | 7957 | — |
| CVRP | 5 | dwave_sa (coefficient_scaled_linear) | 0/100 | 0/100 | n/a | 0.007 s | 6680 | 66–68 |
| CVRP | 5 | dwave_sa (penalty_scaled_geometric) | 0/100 | 0/100 | n/a | 0.007 s | 6680 | 66–68 |
| CVRP | 5 | exact_small (proven) | 100/100 | 100/100 | 0.00% [0.00, 0.00] (10 inst.) | 0.014 s | — | — |
| CVRP | 5 | openjij_sa (coefficient_scaled_linear) | 0/100 | 0/100 | n/a | 0.016 s | 6680 | 66–68 |
| CVRP | 5 | openjij_sa (penalty_scaled_geometric) | 3/100 | 0/100 | 43.59% (no CI; 2 inst.) | 0.015 s | 6680 | 66–68 |
| CVRP | 5 | ortools (wall_clock) | 100/100 | 100/100 | 0.00% [0.00, 0.00] (10 inst.) | 0.197 s | — | — |
| CVRP | 5 | qubo_sa (best_seen) (coefficient_scaled_linear) | 0/100 | 0/100 | n/a | 0.047 s | 6680 | 66–68 |
| CVRP | 5 | qubo_sa (best_seen) (penalty_scaled_geometric) | 2/100 | 0/100 | 30.39% (no CI; 2 inst.) | 0.048 s | 6680 | 66–68 |
| CVRP | 5 | qubo_sa (final) (coefficient_scaled_linear) | 0/100 | 0/100 | n/a | 0.047 s | 6680 | 66–68 |
| CVRP | 5 | qubo_sa (final) (penalty_scaled_geometric) | 2/100 | 0/100 | 30.39% (no CI; 2 inst.) | 0.048 s | 6680 | 66–68 |
| CVRP | 5 | vrp_sa (wall_clock) | 97/100 | 97/100 | 0.00% [0.00, 0.00] (10 inst.) | 0.194 s | 6145 | — |
| CVRP | 6 | dwave_sa (coefficient_scaled_linear) | 0/100 | 0/100 | n/a | 0.012 s | 9120 | 90–92 |
| CVRP | 6 | dwave_sa (penalty_scaled_geometric) | 3/100 | 0/100 | 34.33% (no CI; 3 inst.) | 0.012 s | 9120 | 90–92 |
| CVRP | 6 | exact_small (proven) | 100/100 | 100/100 | 0.00% [0.00, 0.00] (10 inst.) | 0.016 s | — | — |
| CVRP | 6 | openjij_sa (coefficient_scaled_linear) | 0/100 | 0/100 | n/a | 0.027 s | 9120 | 90–92 |
| CVRP | 6 | openjij_sa (penalty_scaled_geometric) | 3/100 | 0/100 | 60.50% (no CI; 2 inst.) | 0.027 s | 9120 | 90–92 |
| CVRP | 6 | ortools (wall_clock) | 100/100 | 100/100 | 0.00% [0.00, 0.00] (10 inst.) | 0.201 s | — | — |
| CVRP | 6 | qubo_sa (best_seen) (coefficient_scaled_linear) | 0/100 | 0/100 | n/a | 0.068 s | 9120 | 90–92 |
| CVRP | 6 | qubo_sa (best_seen) (penalty_scaled_geometric) | 1/100 | 0/100 | 59.45% (no CI; 1 inst.) | 0.064 s | 9120 | 90–92 |
| CVRP | 6 | qubo_sa (final) (coefficient_scaled_linear) | 0/100 | 0/100 | n/a | 0.068 s | 9120 | 90–92 |
| CVRP | 6 | qubo_sa (final) (penalty_scaled_geometric) | 1/100 | 0/100 | 59.45% (no CI; 1 inst.) | 0.064 s | 9120 | 90–92 |
| CVRP | 6 | vrp_sa (wall_clock) | 90/100 | 87/100 | 0.63% [0.00, 1.89] (10 inst.) | 0.180 s | 5345 | — |
| TSP | 6 | dwave_sa (coefficient_scaled_linear) | 88/100 | 13/100 | 13.34% [9.62, 17.33] (10 inst.) | 0.005 s | 3600 | 36 |
| TSP | 6 | openjij_sa (coefficient_scaled_linear) | 86/100 | 13/100 | 15.15% [11.04, 19.08] (10 inst.) | 0.007 s | 3600 | 36 |
| TSP | 6 | qubo_sa_old (best_seen) (coefficient_scaled_linear) | 100/100 | 45/100 | 4.14% [2.67, 5.60] (10 inst.) | 0.022 s | 3600 | 36 |
| TSP | 6 | qubo_sa_old (final) (coefficient_scaled_linear) | 86/100 | 11/100 | 15.19% [12.49, 18.11] (10 inst.) | 0.022 s | 3600 | 36 |
| TSP | 6 | qubo_sa_penalty (best_seen) (penalty_scaled_geometric) | 99/100 | 20/100 | 8.61% [6.26, 10.64] (10 inst.) | 0.022 s | 3600 | 36 |
| TSP | 6 | qubo_sa_penalty (final) (penalty_scaled_geometric) | 99/100 | 10/100 | 17.19% [13.82, 20.06] (10 inst.) | 0.022 s | 3600 | 36 |
| TSP | 6 | qubo_sa_swap (baseline) | 100/100 | 100/100 | 0.00% [0.00, 0.00] (10 inst.) | 0.034 s | 3600 | 36 |
| TSP | 6 | two_opt (baseline) | 100/100 | 100/100 | 0.00% [0.00, 0.00] (10 inst.) | 0.025 s | 3600 | 36 |
| TSP | 10 | dwave_sa (coefficient_scaled_linear) | 88/100 | 0/100 | 41.41% [38.41, 44.57] (10 inst.) | 0.009 s | 10000 | 100 |
| TSP | 10 | openjij_sa (coefficient_scaled_linear) | 86/100 | 1/100 | 40.93% [36.03, 45.40] (10 inst.) | 0.023 s | 10000 | 100 |
| TSP | 10 | qubo_sa_old (best_seen) (coefficient_scaled_linear) | 99/100 | 0/100 | 32.96% [29.25, 36.59] (10 inst.) | 0.064 s | 10000 | 100 |
| TSP | 10 | qubo_sa_old (final) (coefficient_scaled_linear) | 88/100 | 0/100 | 42.35% [38.55, 46.17] (10 inst.) | 0.064 s | 10000 | 100 |
| TSP | 10 | qubo_sa_penalty (best_seen) (penalty_scaled_geometric) | 100/100 | 0/100 | 43.33% [40.20, 46.90] (10 inst.) | 0.064 s | 10000 | 100 |
| TSP | 10 | qubo_sa_penalty (final) (penalty_scaled_geometric) | 100/100 | 0/100 | 51.94% [47.28, 56.87] (10 inst.) | 0.064 s | 10000 | 100 |
| TSP | 10 | qubo_sa_swap (baseline) | 100/100 | 93/100 | 0.27% [0.00, 0.65] (10 inst.) | 0.102 s | 10000 | 100 |
| TSP | 10 | two_opt (baseline) | 100/100 | 90/100 | 0.41% [0.00, 1.23] (10 inst.) | 0.080 s | 10000 | 100 |
| TSP | 15 | dwave_sa (coefficient_scaled_linear) | 90/100 | 0/100 | 73.42% [68.82, 78.88] (10 inst.) | 0.027 s | 22500 | 225 |
| TSP | 15 | openjij_sa (coefficient_scaled_linear) | 86/100 | 0/100 | 73.77% [68.12, 79.32] (10 inst.) | 0.068 s | 22500 | 225 |
| TSP | 15 | qubo_sa_old (best_seen) (coefficient_scaled_linear) | 98/100 | 0/100 | 65.24% [60.54, 69.80] (10 inst.) | 0.154 s | 22500 | 225 |
| TSP | 15 | qubo_sa_old (final) (coefficient_scaled_linear) | 85/100 | 0/100 | 76.76% [70.04, 83.96] (10 inst.) | 0.154 s | 22500 | 225 |
| TSP | 15 | qubo_sa_penalty (best_seen) (penalty_scaled_geometric) | 95/100 | 0/100 | 81.45% [75.61, 87.12] (10 inst.) | 0.160 s | 22500 | 225 |
| TSP | 15 | qubo_sa_penalty (final) (penalty_scaled_geometric) | 100/100 | 0/100 | 87.31% [81.21, 93.18] (10 inst.) | 0.160 s | 22500 | 225 |
| TSP | 15 | qubo_sa_swap (baseline) | 100/100 | 57/100 | 1.43% [0.48, 2.50] (10 inst.) | 0.233 s | 22500 | 225 |
| TSP | 15 | two_opt (baseline) | 100/100 | 100/100 | 0.00% [0.00, 0.00] (10 inst.) | 0.229 s | 22500 | 225 |
| TSP | 20 | dwave_sa (coefficient_scaled_linear) | 82/100 | 0/100 | 98.41% [90.70, 105.38] (10 inst.) | 0.068 s | 40000 | 400 |
| TSP | 20 | openjij_sa (coefficient_scaled_linear) | 83/100 | 0/100 | 98.33% [86.84, 109.41] (10 inst.) | 0.169 s | 40000 | 400 |
| TSP | 20 | qubo_sa_old (best_seen) (coefficient_scaled_linear) | 98/100 | 0/100 | 86.60% [77.13, 96.47] (10 inst.) | 0.313 s | 40000 | 400 |
| TSP | 20 | qubo_sa_old (final) (coefficient_scaled_linear) | 86/100 | 0/100 | 97.14% [88.82, 105.85] (10 inst.) | 0.313 s | 40000 | 400 |
| TSP | 20 | qubo_sa_penalty (best_seen) (penalty_scaled_geometric) | 93/100 | 0/100 | 104.65% [95.76, 112.65] (10 inst.) | 0.316 s | 40000 | 400 |
| TSP | 20 | qubo_sa_penalty (final) (penalty_scaled_geometric) | 100/100 | 0/100 | 108.84% [99.24, 117.05] (10 inst.) | 0.316 s | 40000 | 400 |
| TSP | 20 | qubo_sa_swap (baseline) | 100/100 | 29/100 | 3.69% [2.51, 5.02] (10 inst.) | 0.446 s | 40000 | 400 |
| TSP | 20 | two_opt (baseline) | 100/100 | 80/100 | 0.37% [0.00, 1.08] (10 inst.) | 0.541 s | 40000 | 400 |
