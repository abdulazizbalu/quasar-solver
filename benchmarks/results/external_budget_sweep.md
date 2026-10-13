# External annealers at larger budgets (20-city TSP)

Ten 20-city benchmark instances × solver seeds 0–2 = 30 runs per configuration. With several reads the lowest-energy read is decoded. Mean gap is the plain mean over feasible runs, so it is conditional on feasibility; the number of feasible runs is shown next to it. Beta ranges: `coefficient_scaled_linear` is 0.1/max|Q| to 10/max|Q| (linear), `penalty_scaled_geometric` is 1/(8P) to 1/(0.05P) (geometric), and `library_default` lets each library choose its own range. `qubo_sa (best_seen)` returns the lowest-energy state visited; `qubo_sa (final)` returns the end state of the same run, like the external samplers. Runs used four worker processes, so runtimes are indicative only.

| Solver | Beta range | Sweeps | Reads | Feasible | Mean gap on feasible runs | Median beta range | Mean runtime |
| --- | --- | ---: | ---: | ---: | ---: | --- | ---: |
| dwave_sa | coefficient_scaled_linear | 100 | 1 | 25/30 | 95.2% (n=25) | 0.0468–4.68 | 0.094 s |
| dwave_sa | coefficient_scaled_linear | 100 | 10 | 29/30 | 67.3% (n=29) | 0.0468–4.68 | 0.076 s |
| dwave_sa | coefficient_scaled_linear | 1,000 | 1 | 27/30 | 89.0% (n=27) | 0.0468–4.68 | 0.076 s |
| dwave_sa | coefficient_scaled_linear | 1,000 | 10 | 30/30 | 50.0% (n=30) | 0.0468–4.68 | 0.154 s |
| dwave_sa | coefficient_scaled_linear | 10,000 | 1 | 27/30 | 80.2% (n=27) | 0.0468–4.68 | 0.161 s |
| dwave_sa | coefficient_scaled_linear | 10,000 | 10 | 30/30 | 49.1% (n=30) | 0.0468–4.68 | 0.921 s |
| dwave_sa | coefficient_scaled_linear | 100,000 | 1 | 29/30 | 74.7% (n=29) | 0.0468–4.68 | 0.915 s |
| dwave_sa | coefficient_scaled_linear | 100,000 | 10 | 30/30 | 46.8% (n=30) | 0.0468–4.68 | 8.713 s |
| dwave_sa | library_default | 100 | 1 | 30/30 | 112.7% (n=30) | 0.00653–528 | 0.085 s |
| dwave_sa | library_default | 100 | 10 | 30/30 | 81.2% (n=30) | 0.00653–528 | 0.104 s |
| dwave_sa | library_default | 1,000 | 1 | 30/30 | 91.3% (n=30) | 0.00653–528 | 0.099 s |
| dwave_sa | library_default | 1,000 | 10 | 30/30 | 62.3% (n=30) | 0.00653–528 | 0.200 s |
| dwave_sa | library_default | 10,000 | 1 | 30/30 | 74.8% (n=30) | 0.00653–528 | 0.209 s |
| dwave_sa | library_default | 10,000 | 10 | 30/30 | 46.9% (n=30) | 0.00653–528 | 1.200 s |
| dwave_sa | library_default | 100,000 | 1 | 30/30 | 62.9% (n=30) | 0.00653–528 | 1.174 s |
| dwave_sa | library_default | 100,000 | 10 | 30/30 | 36.1% (n=30) | 0.00653–528 | 11.484 s |
| dwave_sa | penalty_scaled_geometric | 100 | 1 | 30/30 | 107.4% (n=30) | 0.117–18.7 | 0.073 s |
| dwave_sa | penalty_scaled_geometric | 100 | 10 | 30/30 | 70.3% (n=30) | 0.117–18.7 | 0.085 s |
| dwave_sa | penalty_scaled_geometric | 1,000 | 1 | 30/30 | 83.9% (n=30) | 0.117–18.7 | 0.086 s |
| dwave_sa | penalty_scaled_geometric | 1,000 | 10 | 30/30 | 57.0% (n=30) | 0.117–18.7 | 0.173 s |
| dwave_sa | penalty_scaled_geometric | 10,000 | 1 | 30/30 | 68.2% (n=30) | 0.117–18.7 | 0.172 s |
| dwave_sa | penalty_scaled_geometric | 10,000 | 10 | 30/30 | 43.1% (n=30) | 0.117–18.7 | 1.058 s |
| dwave_sa | penalty_scaled_geometric | 100,000 | 1 | 30/30 | 54.8% (n=30) | 0.117–18.7 | 1.075 s |
| dwave_sa | penalty_scaled_geometric | 100,000 | 10 | 30/30 | 32.5% (n=30) | 0.117–18.7 | 9.542 s |
| openjij_sa | coefficient_scaled_linear | 100 | 1 | 23/30 | 98.1% (n=23) | 0.0468–4.68 | 0.198 s |
| openjij_sa | coefficient_scaled_linear | 100 | 10 | 30/30 | 66.8% (n=30) | 0.0468–4.68 | 1.198 s |
| openjij_sa | coefficient_scaled_linear | 1,000 | 1 | 29/30 | 75.6% (n=29) | 0.0468–4.68 | 0.188 s |
| openjij_sa | coefficient_scaled_linear | 1,000 | 10 | 30/30 | 51.1% (n=30) | 0.0468–4.68 | 1.244 s |
| openjij_sa | coefficient_scaled_linear | 10,000 | 1 | 28/30 | 74.8% (n=28) | 0.0468–4.68 | 0.263 s |
| openjij_sa | coefficient_scaled_linear | 10,000 | 10 | 30/30 | 49.5% (n=30) | 0.0468–4.68 | 2.142 s |
| openjij_sa | library_default | 100 | 1 | 30/30 | 103.8% (n=30) | 1.9–152 | 0.182 s |
| openjij_sa | library_default | 100 | 10 | 30/30 | 73.9% (n=30) | 1.9–152 | 1.234 s |
| openjij_sa | library_default | 1,000 | 1 | 29/30 | 84.7% (n=29) | 2.91–18.6 | 0.191 s |
| openjij_sa | library_default | 1,000 | 10 | 30/30 | 51.4% (n=30) | 2.91–18.6 | 1.258 s |
| openjij_sa | library_default | 10,000 | 1 | 29/30 | 64.1% (n=29) | 2.93–18.6 | 0.232 s |
| openjij_sa | library_default | 10,000 | 10 | 30/30 | 37.7% (n=30) | 2.93–18.6 | 1.878 s |
| openjij_sa | penalty_scaled_geometric | 100 | 1 | 30/30 | 105.4% (n=30) | 0.117–18.7 | 0.173 s |
| openjij_sa | penalty_scaled_geometric | 100 | 10 | 30/30 | 72.6% (n=30) | 0.117–18.7 | 1.188 s |
| openjij_sa | penalty_scaled_geometric | 1,000 | 1 | 30/30 | 87.4% (n=30) | 0.117–18.7 | 0.186 s |
| openjij_sa | penalty_scaled_geometric | 1,000 | 10 | 30/30 | 58.2% (n=30) | 0.117–18.7 | 1.303 s |
| openjij_sa | penalty_scaled_geometric | 10,000 | 1 | 30/30 | 66.4% (n=30) | 0.117–18.7 | 0.294 s |
| openjij_sa | penalty_scaled_geometric | 10,000 | 10 | 30/30 | 45.3% (n=30) | 0.117–18.7 | 2.315 s |
| qubo_sa (best_seen) | coefficient_scaled_linear | 100 | 1 | 29/30 | 87.0% (n=29) | 0.0468–4.68 | 0.339 s |
| qubo_sa (best_seen) | coefficient_scaled_linear | 1,000 | 1 | 30/30 | 60.1% (n=30) | 0.0468–4.68 | 3.013 s |
| qubo_sa (final) | coefficient_scaled_linear | 100 | 1 | 27/30 | 96.0% (n=27) | 0.0468–4.68 | 0.339 s |
| qubo_sa (final) | coefficient_scaled_linear | 1,000 | 1 | 26/30 | 83.8% (n=26) | 0.0468–4.68 | 3.013 s |
