# Swap schedule tuning

Command: `python -m benchmarks.tune_swap`.
Tuning instance seeds: (303000, 303001); solver seeds: (100, 101, 102).
These seeds are disjoint from the benchmark instance and solver seeds.
Each schedule uses one read, 100 sweeps, and 100 × n² attempted swaps per run.
Inverse temperature is linearly interpolated from beta_start to beta_end, then divided by max_distance.
Selection rule: lowest mean percentage gap to Held–Karp optimum across all 24 tuning runs per schedule; ties choose the lexicographically smaller schedule.

| beta_start | beta_end | Runs | Mean gap |
| ---: | ---: | ---: | ---: |
| 0.1 | 10 | 24 | 3.225% |
| 1 | 30 | 24 | 1.698% |
| 5 | 100 | 24 | 1.879% |
| 10 | 100 | 24 | 3.538% |

Selected schedule: beta_start=1, beta_end=30.
