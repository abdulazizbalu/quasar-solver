# TSP benchmark

Python: 3.14.4; CPU: Intel64 Family 6 Model 186 Stepping 3, GenuineIntel; system: Windows-11-10.0.26200-SP0.

Instances: NumPy default_rng(2026 + n), uniform [0,1)^2. Seeds: 0–9.
Each solver receives the same wall-clock limit per run. `two_opt` is multi-start nearest neighbor plus 2-opt. QUBO sweep uses alpha × max_distance for alpha in {1,2,5,10,50}, plus fixed penalty 100.
For n ≤ 12, gap is versus the proven Held–Karp optimum. For larger n, gap is versus the best feasible result across all tested solvers, budgets, and penalties; that reference is not proven. Objective/gap means include feasible runs only; runtimes include all runs.

## Time limit: 1 s

| Cities | Solver | Penalty | Feasible | Mean objective | Mean runtime (s) | Reference | Status | Mean gap |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- | ---: |
| 6 | qubo_sa | 1 | 100.0% | 2.2917 | 1.000 | 2.2917 | proven optimum | 0.000% |
| 6 | qubo_sa | 10 | 100.0% | 2.2917 | 1.000 | 2.2917 | proven optimum | 0.000% |
| 6 | qubo_sa | 2 | 100.0% | 2.2917 | 1.000 | 2.2917 | proven optimum | 0.000% |
| 6 | qubo_sa | 5 | 100.0% | 2.2917 | 1.000 | 2.2917 | proven optimum | 0.000% |
| 6 | qubo_sa | 50 | 100.0% | 2.2917 | 1.000 | 2.2917 | proven optimum | 0.000% |
| 6 | qubo_sa | fixed_100 | 100.0% | 2.2917 | 1.000 | 2.2917 | proven optimum | 0.000% |
| 6 | two_opt | n/a | 100.0% | 2.2917 | 0.001 | 2.2917 | proven optimum | 0.000% |
| 10 | qubo_sa | 1 | 100.0% | 3.5739 | 1.000 | 2.7555 | proven optimum | 29.704% |
| 10 | qubo_sa | 10 | 100.0% | 3.6374 | 1.001 | 2.7555 | proven optimum | 32.007% |
| 10 | qubo_sa | 2 | 100.0% | 3.7483 | 1.000 | 2.7555 | proven optimum | 36.032% |
| 10 | qubo_sa | 5 | 100.0% | 3.7690 | 1.002 | 2.7555 | proven optimum | 36.783% |
| 10 | qubo_sa | 50 | 100.0% | 3.6895 | 1.000 | 2.7555 | proven optimum | 33.898% |
| 10 | qubo_sa | fixed_100 | 100.0% | 3.6374 | 1.001 | 2.7555 | proven optimum | 32.007% |
| 10 | two_opt | n/a | 100.0% | 2.7555 | 0.010 | 2.7555 | proven optimum | 0.000% |
| 15 | qubo_sa | 1 | 90.0% | 5.8205 | 1.004 | 2.9346 | best found, not proven | 98.339% |
| 15 | qubo_sa | 10 | 100.0% | 5.6163 | 1.002 | 2.9346 | best found, not proven | 91.381% |
| 15 | qubo_sa | 2 | 100.0% | 5.7472 | 1.002 | 2.9346 | best found, not proven | 95.840% |
| 15 | qubo_sa | 5 | 100.0% | 5.6035 | 1.005 | 2.9346 | best found, not proven | 90.944% |
| 15 | qubo_sa | 50 | 100.0% | 5.6469 | 1.004 | 2.9346 | best found, not proven | 92.423% |
| 15 | qubo_sa | fixed_100 | 100.0% | 5.6642 | 1.002 | 2.9346 | best found, not proven | 93.013% |
| 15 | two_opt | n/a | 100.0% | 2.9346 | 0.047 | 2.9346 | best found, not proven | 0.000% |
| 20 | qubo_sa | 1 | 0.0% | — | 1.017 | 3.9030 | best found, not proven | — |
| 20 | qubo_sa | 10 | 0.0% | — | 1.019 | 3.9030 | best found, not proven | — |
| 20 | qubo_sa | 2 | 0.0% | — | 1.017 | 3.9030 | best found, not proven | — |
| 20 | qubo_sa | 5 | 0.0% | — | 1.014 | 3.9030 | best found, not proven | — |
| 20 | qubo_sa | 50 | 0.0% | — | 1.019 | 3.9030 | best found, not proven | — |
| 20 | qubo_sa | fixed_100 | 0.0% | — | 1.024 | 3.9030 | best found, not proven | — |
| 20 | two_opt | n/a | 100.0% | 3.9030 | 0.208 | 3.9030 | best found, not proven | 0.000% |

## Time limit: 5 s

| Cities | Solver | Penalty | Feasible | Mean objective | Mean runtime (s) | Reference | Status | Mean gap |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- | ---: |
| 6 | qubo_sa | 1 | 100.0% | 2.2917 | 5.000 | 2.2917 | proven optimum | 0.000% |
| 6 | qubo_sa | 10 | 100.0% | 2.2917 | 5.000 | 2.2917 | proven optimum | 0.000% |
| 6 | qubo_sa | 2 | 100.0% | 2.2917 | 5.000 | 2.2917 | proven optimum | 0.000% |
| 6 | qubo_sa | 5 | 100.0% | 2.2917 | 5.000 | 2.2917 | proven optimum | 0.000% |
| 6 | qubo_sa | 50 | 100.0% | 2.2917 | 5.000 | 2.2917 | proven optimum | 0.000% |
| 6 | qubo_sa | fixed_100 | 100.0% | 2.2917 | 5.000 | 2.2917 | proven optimum | 0.000% |
| 6 | two_opt | n/a | 100.0% | 2.2917 | 0.001 | 2.2917 | proven optimum | 0.000% |
| 10 | qubo_sa | 1 | 100.0% | 3.2938 | 5.001 | 2.7555 | proven optimum | 19.537% |
| 10 | qubo_sa | 10 | 100.0% | 3.4393 | 5.001 | 2.7555 | proven optimum | 24.819% |
| 10 | qubo_sa | 2 | 100.0% | 3.3695 | 5.001 | 2.7555 | proven optimum | 22.284% |
| 10 | qubo_sa | 5 | 100.0% | 3.3619 | 5.001 | 2.7555 | proven optimum | 22.009% |
| 10 | qubo_sa | 50 | 100.0% | 3.4011 | 5.000 | 2.7555 | proven optimum | 23.430% |
| 10 | qubo_sa | fixed_100 | 100.0% | 3.4242 | 5.002 | 2.7555 | proven optimum | 24.270% |
| 10 | two_opt | n/a | 100.0% | 2.7555 | 0.009 | 2.7555 | proven optimum | 0.000% |
| 15 | qubo_sa | 1 | 100.0% | 5.0618 | 5.006 | 2.9346 | best found, not proven | 72.485% |
| 15 | qubo_sa | 10 | 100.0% | 5.1612 | 5.003 | 2.9346 | best found, not proven | 75.874% |
| 15 | qubo_sa | 2 | 100.0% | 5.1363 | 5.003 | 2.9346 | best found, not proven | 75.024% |
| 15 | qubo_sa | 5 | 100.0% | 5.2674 | 5.003 | 2.9346 | best found, not proven | 79.492% |
| 15 | qubo_sa | 50 | 100.0% | 5.1612 | 5.006 | 2.9346 | best found, not proven | 75.874% |
| 15 | qubo_sa | fixed_100 | 100.0% | 5.2514 | 5.003 | 2.9346 | best found, not proven | 78.947% |
| 15 | two_opt | n/a | 100.0% | 2.9346 | 0.052 | 2.9346 | best found, not proven | 0.000% |
| 20 | qubo_sa | 1 | 0.0% | — | 5.016 | 3.9030 | best found, not proven | — |
| 20 | qubo_sa | 10 | 0.0% | — | 5.017 | 3.9030 | best found, not proven | — |
| 20 | qubo_sa | 2 | 0.0% | — | 5.025 | 3.9030 | best found, not proven | — |
| 20 | qubo_sa | 5 | 0.0% | — | 5.016 | 3.9030 | best found, not proven | — |
| 20 | qubo_sa | 50 | 0.0% | — | 5.020 | 3.9030 | best found, not proven | — |
| 20 | qubo_sa | fixed_100 | 0.0% | — | 5.022 | 3.9030 | best found, not proven | — |
| 20 | two_opt | n/a | 100.0% | 3.9030 | 0.219 | 3.9030 | best found, not proven | 0.000% |

