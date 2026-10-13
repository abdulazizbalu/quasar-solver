# Final annealing temperature relative to the penalty

`max|Q|/P` is the largest absolute QUBO coefficient divided by the constraint penalty P. The default `coefficient_scaled_linear` schedule ends at temperature `max|Q|/10`, shown as `T_end/P`; `penalty_scaled_geometric` always ends at `0.05 P`.

| Problem | Instance set | Size | Instances | max\|Q\|/P (min–max) | Default T_end/P (min–max) |
| --- | --- | ---: | ---: | ---: | ---: |
| TSP | main benchmark | 6 | 10 | 2.00–2.00 | 0.20–0.20 |
| TSP | main benchmark | 10 | 10 | 2.00–2.00 | 0.20–0.20 |
| TSP | main benchmark | 15 | 10 | 2.00–2.00 | 0.20–0.20 |
| TSP | main benchmark | 20 | 10 | 2.00–2.00 | 0.20–0.20 |
| CVRP | tiny benchmark and external comparison | 4 | 10 | 20.0–64.0 | 2.0–6.4 |
| CVRP | tiny benchmark and external comparison | 5 | 10 | 24.0–144.0 | 2.4–14.4 |
| CVRP | tiny benchmark and external comparison | 6 | 10 | 24.0–144.0 | 2.4–14.4 |
| CVRP | QUBO budget sweep | 4 | 10 | 10.0–128.0 | 1.0–12.8 |
| CVRP | QUBO budget sweep | 5 | 10 | 16.0–112.0 | 1.6–11.2 |
| CVRP | QUBO budget sweep | 6 | 10 | 24.0–144.0 | 2.4–14.4 |
| CVRP | earlier unit-demand instances (commit 5283375) | 4 | 10 | 5.0–5.0 | 0.5–0.5 |
| CVRP | earlier unit-demand instances (commit 5283375) | 6 | 10 | 8.0–8.0 | 0.8–0.8 |

In the CVRP QUBO, squaring the capacity equation multiplies P by products of demand and binary slack-bit weights, so max|Q| is far above P and the coefficient-normalized default ends hotter than P.
