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

Run from the repository root with `python -m benchmarks.run_benchmarks`. The script writes `benchmarks/results/raw.csv` and `benchmarks/results/summary.md`. Each size uses one seeded uniform 2D Euclidean instance and ten annealing seeds (0–9). "Best known" is the best of a deterministic multi-start nearest-neighbor tour improved with 2-opt and all feasible benchmark runs; it is **not a certified optimum**. Objective and gap averages use feasible runs only; runtime averages use every run. An invalid run has no tour objective.

The following measurements are from Python 3.14.4 on Intel64 Family 6 Model 186 Stepping 3, GenuineIntel, Windows 11. Runtime will vary by machine. The exact instance coordinates, run parameters, and per-seed outputs are defined by the script and recorded in the CSV.

| Cities | Runs | Feasible | Mean objective (feasible) | Mean runtime (s) | Best known | Mean gap vs best known (feasible) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 6 | 10 | 100.0% | 2.5517 | 0.0332 | 2.2917 | 11.3421% |
| 10 | 10 | 100.0% | 4.0248 | 0.0525 | 2.7555 | 46.0658% |
| 15 | 10 | 60.0% | 6.1029 | 0.0981 | 2.9346 | 107.9599% |
| 20 | 10 | 0.0% | — | 0.1969 | 3.9030 | — |

