[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests passing](https://img.shields.io/badge/tests-passing-brightgreen)](https://github.com/abdulazizbalu/quasar-solver/actions)

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

Open `demos/web_demo.html` in your browser — no server required. Click to place cities, hit Solve, watch the optimizer find the shortest route.

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

| Problem size (cities) | Variables (n²) | Avg solve time (ms) | Typical tour quality |
| --- | ---: | ---: | --- |
| 6 | 36 | 450 | Usually valid, near-optimal |
| 10 | 100 | 1,800 | Often valid, good heuristic tours |
| 20 | 400 | 9,500 | Mixed validity, useful exploratory tours |
