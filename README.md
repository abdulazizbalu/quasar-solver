[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests](https://github.com/abdulazizbalu/quasar-solver/actions/workflows/tests.yml/badge.svg)](https://github.com/abdulazizbalu/quasar-solver/actions/workflows/tests.yml)

<p align="center">
  <strong><a href="https://abdulazizbalu.github.io/quasar-solver/demos/web_demo.html">🚀 Live Demo</a></strong>
</p>

# Quasar Solver

Quasar Solver is a pure Python, quantum-inspired optimizer for quadratic unconstrained binary optimization (QUBO) problems. It provides a compact QUBO model, a NumPy-based simulated annealing solver, and converters for practical optimization examples.

## Installation

```bash
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

## Web Demo

🚀 Live Demo — open in browser, no install needed.

Click to place cities, hit Solve, watch the optimizer find the shortest route.

## Quick Usage

```python
from quasar_solver import QUBO, SimulatedAnnealingSolver
q = QUBO(); q.add(0, 0, -1.0); q.add(1, 1, 2.0)
result = SimulatedAnnealingSolver(seed=42).solve(q)
```

## TSP Demo

The routing demo builds a seeded six-city symmetric distance matrix, converts it to a QUBO with one-hot Travelling Salesman Problem constraints, and solves it with simulated annealing. It prints the best energy, decoded tour, and total route distance when the best sample is valid.

Run it with:

```bash
python demos/routing_demo.py
```

The demo saves a plot of the city coordinates and decoded route to `demos/tour.png`. If the annealer returns an invalid one-hot assignment, the demo prints a warning and still saves the city plot.

## Roadmap

- VRP support
- Schedule optimization
- Financial portfolio demo
- Web UI

## How It Works

QUBO formulation turns an optimization problem into a polynomial over binary variables. Each variable can be either 0 or 1, and the model assigns costs to individual variables and pairs of variables. Hard constraints are usually represented as large penalty terms, so invalid assignments become expensive. Once a problem is in QUBO form, many different search methods can try to minimize its energy.

Simulated annealing is a randomized search method inspired by cooling physical systems. It starts from a random binary sample, flips bits one at a time, and keeps changes that improve the energy. It can also accept worse moves early in the run, which helps it escape shallow local minima. As the temperature cools, the solver becomes more selective and settles into its best-found solution.

## Benchmarks

Reproduce all measurements from the repository root with `python -m benchmarks.run_benchmarks`. This runs ten seeds (0–9), both 1 s and 5 s budgets, QUBO-SA penalties `alpha × max_distance` for alpha in `{1, 2, 5, 10, 50}` plus fixed 100, and the `two_opt` baseline. It writes per-run data to `benchmarks/results/raw.csv`, full grouped tables to `benchmarks/results/summary.md`, and the chart below to `docs/tsp_benchmark.png`.

For n ≤ 12, the gap is measured against the proven Held–Karp optimum. For larger instances, the reference is the best feasible result found across this experiment and is explicitly not proven. The means below use feasible runs; invalid runs still count in feasibility and runtime statistics. Measurements were collected on Python 3.14.4, Intel64 Family 6 Model 186 Stepping 3, Windows 11.

| Cities | Budget | Solver | Penalty | Feasible | Mean gap | Mean runtime |
| ---: | ---: | --- | --- | ---: | ---: | ---: |
| 6 | 1 s | qubo_sa | alpha=10 | 100% | 0.000% | 1.000 s |
| 6 | 5 s | qubo_sa | alpha=10 | 100% | 0.000% | 5.000 s |
| 10 | 1 s | qubo_sa | alpha=10 | 100% | 32.007% | 1.001 s |
| 10 | 5 s | qubo_sa | alpha=10 | 100% | 24.819% | 5.001 s |
| 15 | 1 s | qubo_sa | alpha=10 | 100% | 91.381% | 1.002 s |
| 15 | 5 s | qubo_sa | alpha=10 | 100% | 75.874% | 5.003 s |
| 20 | 1 s | qubo_sa | alpha=10 | 0% | — | 1.019 s |
| 20 | 5 s | qubo_sa | alpha=10 | 0% | — | 5.017 s |
| 6 | 1 s | two_opt | — | 100% | 0.000% | 0.001 s |
| 6 | 5 s | two_opt | — | 100% | 0.000% | 0.001 s |
| 10 | 1 s | two_opt | — | 100% | 0.000% | 0.010 s |
| 10 | 5 s | two_opt | — | 100% | 0.000% | 0.009 s |
| 15 | 1 s | two_opt | — | 100% | 0.000% | 0.047 s |
| 15 | 5 s | two_opt | — | 100% | 0.000% | 0.052 s |
| 20 | 1 s | two_opt | — | 100% | 0.000% | 0.208 s |
| 20 | 5 s | two_opt | — | 100% | 0.000% | 0.219 s |

![Feasibility rate and mean gap by instance size, solver, and time budget](docs/tsp_benchmark.png)

### Penalty sweep and default

The complete alpha-by-size results at both budgets are in `benchmarks/results/summary.md`. Averaged over sizes 6, 10, and 15 and both budgets, alpha=10 had 100% feasibility and the lowest mean gap (37.35%) among penalties with 100% feasibility. Alpha=1 had a slightly lower feasible-only mean gap, but missed feasibility on one 15-city, 1 s run (90% there). Every alpha had 0% feasibility on 20 cities, so larger penalties did not fix that case. The default QUBO-SA penalty is therefore `10 × max_distance`; this is an empirical choice for these seeded Euclidean instances, not a universal optimum.

### Findings

- `two_opt` found feasible tours on every run and matched the proven optimum at 6 and 10 cities. It completed well before its time limit on these instances.
- QUBO-SA reached the proven 6-city optimum within either budget. At 10 and 15 cities it remained 19.5–91.4% above the reference, though the 5 s runs generally improved over 1 s. At 20 cities it returned no feasible tour for any tested penalty or budget.
- Increasing alpha helps preserve one-hot constraints at 15 cities: alpha=1 had a 90% feasibility rate at 1 s, while alpha ≥ 2 had 100%. At 20 cities none of the tested penalties was sufficient for the annealer to find a valid assignment within five seconds. Large penalties can dominate route-cost differences; small penalties make constraint violations attractive. A single-bit-flip annealer also faces a rugged landscape with dense one-hot penalties.
- The TSP QUBO has n² binary variables: 400 at 20 cities. The 5 s cap raises feasibility to 100% at 15 cities but does not rescue 20 cities. This points to the encoding and search neighborhood as well as available time.
- The old README's 0.45–9.5 s figures had no reproducible script or recorded settings, so their exact origin cannot be established. The earlier `qubo_sa` adapter was configured for 8 reads × 800 sweeps (6,400 attempted flips), versus the original QUBO solver defaults of 100 × 1,000 (100,000 flips). That 15.6× reduction in nominal work likely explains part of the apparent runtime drop to 0.03–0.2 s, but it does not validate the old figures. Current timed results instead use the full stated budget.
