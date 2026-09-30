# VRP benchmark summary

Tiny references are CP-SAT proven optima for each generated instance. Standard references are published values, not re-proven.

| Group | Customers | Solver | Feasible | Fleet match | Mean gap (match) [95% CI] | Median gap (all runs) | Mean routes | Mean runtime | Runtime range | Mean attempts | QUBO vars |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A-n32-k5 | 31 | ortools | 10/10 | 10/10 | 1.03% [CI unavailable] | 0.00% | 5.00 | 1.002 s | 1.001–1.003 s | — | — |
| A-n32-k5 | 31 | vrp_sa | 10/10 | 10/10 | 22.72% [CI unavailable] | 22.58% | 5.00 | 1.000 s | 1.000–1.000 s | 8626 | — |
| A-n33-k5 | 32 | ortools | 10/10 | 10/10 | 3.69% [CI unavailable] | 2.57% | 5.00 | 1.002 s | 1.002–1.003 s | — | — |
| A-n33-k5 | 32 | vrp_sa | 10/10 | 10/10 | 17.66% [CI unavailable] | 15.73% | 5.00 | 1.000 s | 1.000–1.000 s | 8780 | — |
| A-n37-k5 | 36 | ortools | 10/10 | 10/10 | 2.18% [CI unavailable] | 2.24% | 5.00 | 1.002 s | 1.001–1.002 s | — | — |
| A-n37-k5 | 36 | vrp_sa | 10/10 | 10/10 | 27.62% [CI unavailable] | 27.88% | 5.00 | 1.000 s | 1.000–1.000 s | 8026 | — |
| C101-25 | 25 | ortools | 10/10 | 10/10 | 0.00% [CI unavailable] | 0.00% | 3.00 | 1.002 s | 1.001–1.003 s | — | — |
| C101-25 | 25 | vrp_sa | 10/10 | 3/10 | 14.04% [CI unavailable] | 32.23% | 3.70 | 1.000 s | 1.000–1.000 s | 12282 | — |
| R101-25 | 25 | ortools | 10/10 | 10/10 | 1.52% [CI unavailable] | 2.03% | 8.00 | 1.002 s | 1.001–1.003 s | — | — |
| R101-25 | 25 | vrp_sa | 10/10 | 8/10 | 3.22% [CI unavailable] | 2.96% | 8.20 | 1.000 s | 1.000–1.001 s | 12023 | — |
| RC101-25 | 25 | ortools | 10/10 | 10/10 | 0.00% [CI unavailable] | 0.00% | 4.00 | 1.002 s | 1.001–1.004 s | — | — |
| RC101-25 | 25 | vrp_sa | 10/10 | 0/10 | n/a | 7.28% | 5.30 | 1.000 s | 1.000–1.000 s | 11218 | — |
| tiny | 4 | exact_small | 100/100 | 100/100 | 0.00% [0.00, 0.00] | 0.00% | 1.50 | 0.012 s | 0.008–0.016 s | — | — |
| tiny | 4 | ortools | 100/100 | 100/100 | 0.00% [0.00, 0.00] | 0.00% | 1.50 | 0.199 s | 0.006–0.207 s | — | — |
| tiny | 4 | qubo_sa | 0/100 | 0/100 | n/a | n/a | nan | 0.063 s | 0.015–0.072 s | 4600 | 44–48 |
| tiny | 4 | vrp_sa | 91/100 | 91/100 | 0.00% [0.00, 0.00] | 0.00% | 1.45 | 0.182 s | 0.000–0.200 s | 4941 | — |
| tiny | 5 | exact_small | 100/100 | 100/100 | 0.00% [0.00, 0.00] | 0.00% | 1.50 | 0.022 s | 0.013–0.038 s | — | — |
| tiny | 5 | ortools | 100/100 | 100/100 | 0.00% [0.00, 0.00] | 0.00% | 1.50 | 0.197 s | 0.017–0.203 s | — | — |
| tiny | 5 | qubo_sa | 0/100 | 0/100 | n/a | n/a | nan | 0.099 s | 0.094–0.115 s | 6680 | 66–68 |
| tiny | 5 | vrp_sa | 97/100 | 97/100 | 0.00% [0.00, 0.00] | 0.00% | 1.48 | 0.194 s | 0.000–0.200 s | 3580 | — |
| tiny | 6 | exact_small | 100/100 | 100/100 | 0.00% [0.00, 0.00] | 0.00% | 1.50 | 0.028 s | 0.018–0.052 s | — | — |
| tiny | 6 | ortools | 100/100 | 100/100 | 0.00% [0.00, 0.00] | 0.00% | 1.50 | 0.201 s | 0.201–0.202 s | — | — |
| tiny | 6 | qubo_sa | 0/100 | 0/100 | n/a | n/a | nan | 0.137 s | 0.133–0.152 s | 9120 | 90–92 |
| tiny | 6 | vrp_sa | 90/100 | 90/100 | 0.63% [0.00, 1.89] | 0.00% | 1.44 | 0.180 s | 0.000–0.200 s | 3137 | — |

For Solomon cases, the mean gap and its interval use feasible runs matching the published fleet; median gap includes every feasible run. Confidence intervals resample independent tiny instances; standard cases each have one instance, so their intervals are unavailable despite ten solver seeds. The comparison table uses a shared wall-clock limit for vrp_sa and OR-Tools.
