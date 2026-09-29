# VRP benchmark summary

Tiny references are CP-SAT proven optima for each generated instance. Standard references are published values, not re-proven.

| Group | Customers | Solver | Feasible | Gap comparable | Mean gap [95% CI] | Mean routes | Mean runtime | Mean attempts | QUBO vars |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A-n32-k5 | 31 | ortools | 10/10 | 10/10 | 1.53% [CI unavailable] | 5.00 | 1.001 s | — | — |
| A-n32-k5 | 31 | vrp_sa | 10/10 | 10/10 | 35.64% [CI unavailable] | 5.00 | 0.271 s | 3100 | — |
| A-n33-k5 | 32 | ortools | 10/10 | 10/10 | 0.30% [CI unavailable] | 5.00 | 1.002 s | — | — |
| A-n33-k5 | 32 | vrp_sa | 10/10 | 10/10 | 40.24% [CI unavailable] | 5.00 | 0.256 s | 3200 | — |
| A-n37-k5 | 36 | ortools | 10/10 | 10/10 | 0.12% [CI unavailable] | 5.00 | 1.001 s | — | — |
| A-n37-k5 | 36 | vrp_sa | 10/10 | 10/10 | 49.88% [CI unavailable] | 5.00 | 0.314 s | 3600 | — |
| C101-25 | 25 | ortools | 10/10 | 10/10 | 0.00% [CI unavailable] | 3.00 | 1.003 s | — | — |
| C101-25 | 25 | vrp_sa | 10/10 | 1/10 | 39.52% [CI unavailable] | 4.60 | 0.131 s | 2500 | — |
| R101-25 | 25 | ortools | 10/10 | 10/10 | 0.94% [CI unavailable] | 8.00 | 1.003 s | — | — |
| R101-25 | 25 | vrp_sa | 10/10 | 3/10 | 11.45% [CI unavailable] | 8.80 | 0.139 s | 2500 | — |
| RC101-25 | 25 | ortools | 10/10 | 10/10 | 0.00% [CI unavailable] | 4.00 | 1.002 s | — | — |
| RC101-25 | 25 | vrp_sa | 10/10 | 0/10 | n/a | 6.00 | 0.181 s | 2500 | — |
| tiny | 4 | exact_small | 100/100 | 100/100 | 0.00% [0.00, 0.00] | 2.00 | 0.012 s | — | — |
| tiny | 4 | ortools | 100/100 | 100/100 | 0.00% [0.00, 0.00] | 2.00 | 0.202 s | — | — |
| tiny | 4 | qubo_sa | 40/100 | 40/100 | 8.67% [5.12, 12.83] | 2.00 | 0.033 s | 4400 | 44 |
| tiny | 4 | vrp_sa | 100/100 | 100/100 | 0.00% [0.00, 0.00] | 2.00 | 0.010 s | 400 | — |
| tiny | 6 | exact_small | 100/100 | 100/100 | 0.00% [0.00, 0.00] | 2.00 | 0.019 s | — | — |
| tiny | 6 | ortools | 100/100 | 100/100 | 0.00% [0.00, 0.00] | 2.00 | 0.201 s | — | — |
| tiny | 6 | qubo_sa | 1/100 | 1/100 | 57.87% [CI unavailable] | 2.00 | 0.052 s | 8800 | 88 |
| tiny | 6 | vrp_sa | 100/100 | 100/100 | 0.00% [0.00, 0.00] | 2.00 | 0.020 s | 600 | — |

For Solomon cases, gap is reported only for feasible runs using the published number of vehicles; n/a means no comparable run. Confidence intervals resample independent instances for tiny cases. A gap observed on only one independent instance has no estimable 95% interval. Standard cases each have one instance; their intervals are therefore unavailable despite ten solver seeds.
