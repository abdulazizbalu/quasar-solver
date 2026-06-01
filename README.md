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
