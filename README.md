[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests](https://github.com/abdulazizbalu/quasar-solver/actions/workflows/tests.yml/badge.svg)](https://github.com/abdulazizbalu/quasar-solver/actions/workflows/tests.yml)

<p align="center">
  <strong><a href="https://abdulazizbalu.github.io/quasar-solver/demos/web_demo.html">Route visualization demo</a></strong>
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

## Route visualization demo

The linked demo is a standalone JavaScript 2-opt annealer; it does not run the Python QUBO solver. Open it in a browser, place cities, and watch its route visualization.

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

Run `python -m benchmarks.run_benchmarks` from the repository root to reproduce the data, summary, paired comparisons, and chart. The script generates ten independent Euclidean instances per size (instance seeds 202600–202609) and runs ten solver seeds (0–9) on each instance. Raw observations are in [`benchmarks/results/raw.csv`](benchmarks/results/raw.csv); the complete penalty sweep, confidence intervals, and paired tests are in [`benchmarks/results/summary.md`](benchmarks/results/summary.md) and [`benchmarks/results/paired_tests.csv`](benchmarks/results/paired_tests.csv).

The benchmark uses a fixed iteration budget with no wall-clock cap. QUBO-SA gets one read of 100 sweeps. A sweep attempts one flip per binary variable, so each run attempts `100 × n²` flips (40,000 at 20 cities). Multi-start `two_opt` receives the same count of candidate tour evaluations. Those operations have different computational costs; the recorded runtime is a measurement, not a matched time budget. The QUBO-SA adapter defaults to eight reads of 100 sweeps for ordinary use. A wall-clock limit remains available as a secondary cap.

For 6 and 10 cities, the reference is the proven Held–Karp optimum. For 15 and 20 cities, each instance has one shared best feasible tour found in this experiment; it is **best found, not proven**. Mean gaps include feasible runs only. The 95% confidence intervals resample the ten independent instances. Measurements below were collected with Python 3.14.4 on an Intel64 Family 6 Model 186 Stepping 3 CPU, Windows 11.

| Cities | Solver | Feasible | Mean gap [95% CI] | Mean runtime |
| ---: | --- | ---: | ---: | ---: |
| 6 | qubo_sa, alpha=1 | 100/100 | 4.14% [2.72, 5.63] | 0.0566 s |
| 6 | two_opt | 100/100 | 0.00% [0.00, 0.00] | 0.0512 s |
| 10 | qubo_sa, alpha=1 | 99/100 | 32.87% [29.02, 36.52] | 0.1661 s |
| 10 | two_opt | 100/100 | 0.41% [0.00, 1.23] | 0.1335 s |
| 15 | qubo_sa, alpha=1 | 98/100 | 65.22% [60.66, 69.76] | 0.2372 s |
| 15 | two_opt | 100/100 | 0.00% [0.00, 0.00] | 0.2743 s |
| 20 | qubo_sa, alpha=1 | 98/100 | 86.03% [76.10, 95.77] | 0.3658 s |
| 20 | two_opt | 100/100 | 0.01% [0.00, 0.02] | 0.5961 s |

![Feasibility rate and feasible-run mean gap by number of cities, for QUBO-SA and multi-start 2-opt](docs/tsp_benchmark.png)

### Findings

- Correcting the sweep definition changes the 20-city result: alpha=1 produced 98 feasible tours in 100 runs, and the other tested penalties produced 99 or 100. The earlier zero-feasibility result came from a much smaller effective flip budget.
- Across all four sizes, alpha=1 has a lower feasible-run mean gap than alpha=2, with Holm-adjusted paired instance-level gap-test p-values of 0.029 for each size. Feasibility was 100%, 99%, 98%, and 98% for alpha=1 versus 100%, 100%, 100%, and 99% for alpha=2. Paired instance-level feasibility tests did not distinguish those rates. The default is therefore `penalty = 1 × max_distance` for this benchmark setting. Users who require a feasible tour on every run should check the feasibility flag or use the always-feasible `two_opt` baseline; this experiment does not establish a universal penalty.
- Alpha=10 and fixed penalty 100 no longer give identical results on most seeds. The configured penalty reaches the QUBO matrix, and the annealer scales inverse temperature by the largest absolute QUBO coefficient. Larger penalties preserve one-hot feasibility in this sample but increase the feasible-run gap. They make constraint energy larger relative to route-cost differences; the table and paired tests quantify the observed effect.
- The QUBO has `n²` binary variables (400 at 20 cities). At the tested budget, QUBO-SA's feasible tours have substantially larger gaps than multi-start 2-opt. The 15- and 20-city reference is only the best tour found here, so those gaps are lower bounds on gaps to an unknown optimum.
- The old README's 0.45–9.5 s figures had no reproducible script or recorded settings, so their origin cannot be established. The prior adapter used eight reads of 800 so-called sweeps, but each sweep attempted only one bit flip: 6,400 flips in total. Its shorter 0.03–0.2 s measurements reflected that smaller work count. The corrected benchmark fixes flips per variable and records both effort and runtime; its numbers use different instances and cannot be directly compared with the old timed table.
