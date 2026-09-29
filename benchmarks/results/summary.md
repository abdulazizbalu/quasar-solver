# TSP benchmark

Python: 3.14.4; CPU: Intel64 Family 6 Model 186 Stepping 3, GenuineIntel; system: Windows-11-10.0.26200-SP0.

Instances: NumPy default_rng(instance_seed + size), uniform [0,1)^2; instance_seed=2026.
Best known is the best of deterministic multi-start nearest-neighbor + 2-opt and feasible benchmark runs. It is a feasible upper bound, not a certified optimum.
Averages for objective and gap use feasible runs only; runtime uses all runs. Invalid objectives and gaps are blank in raw.csv.

| Cities | Runs | Feasible | Mean objective (feasible) | Mean runtime (s) | Best known | Mean gap vs best known (feasible) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 6 | 10 | 100.0% | 2.5517 | 0.0332 | 2.2917 | 11.3421% |
| 10 | 10 | 100.0% | 4.0248 | 0.0525 | 2.7555 | 46.0658% |
| 15 | 10 | 60.0% | 6.1029 | 0.0981 | 2.9346 | 107.9599% |
| 20 | 10 | 0.0% | — | 0.1969 | 3.9030 | — |
