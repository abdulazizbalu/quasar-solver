[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests](https://github.com/abdulazizbalu/quasar-solver/actions/workflows/tests.yml/badge.svg)](https://github.com/abdulazizbalu/quasar-solver/actions/workflows/tests.yml)

<p align="center">
  <strong><a href="https://abdulazizbalu.github.io/quasar-solver/demos/web_demo.html">Route visualization demo</a></strong>
</p>

# Quasar Solver

Quasar Solver is a Python research package for QUBO simulated annealing and small routing experiments. It includes TSP, capacitated vehicle routing (CVRP), and vehicle routing with time windows (VRPTW), with independent feasibility checks and classical reference solvers. The VRP QUBO is restricted to tiny CVRP instances.

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

- Schedule optimization
- Financial portfolio demo
- Web UI

## How It Works

QUBO formulation turns an optimization problem into a polynomial over binary variables. Each variable can be either 0 or 1, and the model assigns costs to individual variables and pairs of variables. Hard constraints are usually represented as large penalty terms, so invalid assignments become expensive. Once a problem is in QUBO form, many different search methods can try to minimize its energy.

Simulated annealing is a randomized search method inspired by cooling physical systems. It starts from a random binary sample, flips bits one at a time, and keeps changes that improve the energy. It can also accept worse moves early in the run, which helps it escape shallow local minima. As the temperature cools, the solver becomes more selective and settles into its best-found solution.

For TSP, `QuboSASwapSolver` anneals the same QUBO energy while representing each state as a tour. It holds city 0 at position 0 and proposes swaps of two other cities, so each state remains a valid permutation. Its move cost is computed from the affected tour edges.

## Benchmarks

Run `python -m benchmarks.run_benchmarks` from the repository root to reproduce the raw results, summary, paired comparisons, and chart. Each size has ten seeded Euclidean instances (instance seeds 202600–202609), and each instance has ten solver seeds (0–9). The reference for **every** instance, including 15 and 20 cities, is the proven Held–Karp optimum computed by float64 subset dynamic programming. Raw observations are in [`benchmarks/results/raw.csv`](benchmarks/results/raw.csv); the full tables and confidence intervals are in [`benchmarks/results/summary.md`](benchmarks/results/summary.md).

All three methods receive one read of 100 sweeps, with `100 × n²` attempted operations per run: 3,600, 10,000, 22,500, and 40,000 at 6, 10, 15, and 20 cities. This is `100n` attempts per city. Bit-flip QUBO-SA counts attempted bit flips, permutation-preserving `qubo_sa_swap` counts proposed city swaps, and multi-start `two_opt` counts evaluated tour moves. These operations have different computational costs, so equal counts do not imply equal wall time. A wall-clock limit is available as a secondary cap; it was not used for these results. Mean gaps use feasible runs; the 95% confidence intervals resample the ten independent instances. Measurements were collected with Python 3.14.4 on an Intel64 Family 6 Model 186 Stepping 3 CPU, Windows 11.

| Cities | Solver | Feasible | Mean gap to proven optimum [95% CI] | Attempts | Mean runtime |
| ---: | --- | ---: | ---: | ---: | ---: |
| 6 | qubo_sa | 100/100 | 4.14% [2.72, 5.63] | 3,600 | 0.0424 s |
| 6 | qubo_sa_swap | 100/100 | 0.00% [0.00, 0.00] | 3,600 | 0.0612 s |
| 6 | two_opt | 100/100 | 0.00% [0.00, 0.00] | 3,600 | 0.0365 s |
| 10 | qubo_sa | 99/100 | 32.87% [29.06, 36.61] | 10,000 | 0.1584 s |
| 10 | qubo_sa_swap | 100/100 | 0.27% [0.00, 0.65] | 10,000 | 0.2173 s |
| 10 | two_opt | 100/100 | 0.41% [0.00, 1.23] | 10,000 | 0.1282 s |
| 15 | qubo_sa | 98/100 | 65.22% [60.56, 69.91] | 22,500 | 0.3930 s |
| 15 | qubo_sa_swap | 100/100 | 1.43% [0.52, 2.49] | 22,500 | 0.5060 s |
| 15 | two_opt | 100/100 | 0.00% [0.00, 0.00] | 22,500 | 0.3630 s |
| 20 | qubo_sa | 98/100 | 86.65% [77.37, 95.89] | 40,000 | 0.7410 s |
| 20 | qubo_sa_swap | 100/100 | 3.69% [2.59, 4.97] | 40,000 | 0.9126 s |
| 20 | two_opt | 100/100 | 0.37% [0.00, 1.08] | 40,000 | 0.8145 s |

![Feasibility and mean gap to proven optimum by TSP size for bit-flip QUBO-SA, swap QUBO-SA, and multi-start 2-opt](docs/tsp_benchmark.png)

### Swap schedule tuning

Run `python -m benchmarks.tune_swap` to reproduce the cooling-schedule experiment. It uses instance seeds 303000–303001 and solver seeds 100–102, disjoint from the benchmark. Four schedules were compared over 24 runs each at the same `100 × n²` proposal budget. The lowest aggregate mean gap, 1.698%, came from inverse-temperature endpoints 1 and 30 divided by `max_distance`; the other tested schedules scored 3.225%, 1.879%, and 3.538%. The selected schedule is fixed in `qubo_sa_swap` and in the benchmark. See the [tuning table](benchmarks/results/swap_tuning.md) and [raw tuning results](benchmarks/results/swap_tuning.csv).

### Findings

- Swap moves keep the one-hot assignment valid: all 400 swap runs returned feasible tours, compared with 395/400 bit-flip runs. A swap changes four one-hot bits but leaves the constraint penalty constant, so its energy change comes from the affected tour edges.
- At 20 cities, the swap mean gap is 3.69%, down 82.96 percentage points from bit-flip SA's 86.65%. It remains 3.32 percentage points above 2-opt's 0.37%. At 15 cities, swap is 1.43 percentage points above 2-opt. At 6 cities the two methods tie at the optimum; at 10 cities swap's 0.27% mean gap is 0.14 percentage points below 2-opt's 0.41%, a small difference in these runs.
- The 20-city bit-flip result changed from Phase 1b's 86.03% gap to 86.65% because the reference is now the proven optimum rather than the experiment's best found tour. The exact reference also exposes 2-opt's 0.37% gap at 20 cities. These are changes in the denominator, not improvements in those solvers.
- Under equal attempt counts, swap SA took more wall time than 2-opt at every tested size. The QUBO contains `n²` binary variables (400 at 20 cities); the swap solver avoids invalid states but still builds that QUBO once per run. The measured gap and runtime therefore do not establish an advantage over 2-opt.

### Scope and limits

`qubo_sa_swap` uses the QUBO to define energy, but its moves swap two cities in a tour. Each move flips four one-hot bits at once and leaves the constraint penalty constant. A generic QUBO annealer or quantum hardware running the plain QUBO does not make this move. It is a classical permutation heuristic, so its results do not establish that one-hot QUBO annealing works for TSP.

The `qubo_sa` bit-flip results show what a plain QUBO solver encounters. Handling constraints through penalties is the main obstacle in these runs, and its gap grows quickly with size.

Multi-start 2-opt remains the stronger routing baseline in these experiments. The swap solver also took more wall time under equal attempt counts.

These instances are random Euclidean TSP with at most 20 cities. The results do not establish performance on larger instances or other problem classes.

The main TSP table continues to use the historical coefficient_scaled_linear default; the separately labeled penalty-scaled schedule experiment is reported in the [external sampler comparison](benchmarks/results/external_comparison_summary.md), not mixed into the main TSP table. A fresh default-schedule rerun confirmed identical feasibility, objective, and gap for all seeded runs; the measured runtime comparison is in [the verification report](benchmarks/results/tsp_schedule_verification.md).

## Vehicle routing (CVRP and VRPTW)

`CVRPInstance` stores demands, capacity, fleet size (or unlimited), and a distance matrix with depot node 0. `VRPTWInstance` adds time windows and service times. VRP results store multiple routes in `Solution.routes`; `Solution.route` remains empty for this interface. `is_feasible_vrp` independently checks visits, capacity, fleet size, depot endpoints, and time windows. `exact_small` uses CP-SAT and reports a proven optimum only when its status is `OPTIMAL`. `vrp_sa` is a classical route-structure annealer. Tiny-CVRP `qubo_sa` uses one-hot assignment/order variables with capacity slack bits and is deliberately capped at six customers (at most 92 variables in these instances).

Run the complete route benchmark and the separate QUBO budget sweep from the repository root:

```bash
pip install -e ".[dev,vrp]"
python -m benchmarks.run_vrp_benchmarks
```

The command downloads checksum-verified files to ignored `benchmarks/data/vrp/` and writes raw rows, environment metadata, summaries, and charts. No third-party instance files are redistributed. Tiny cases use 10 independent random Euclidean instances per size (4, 5, 6), integer demands in 1–3, alternating five tight and five loose capacities, and 10 solver seeds per instance. The CP-SAT reference is proven for each generated instance. Tiny route solvers share a 0.2-second deadline; standard `vrp_sa` and OR-Tools share a 1-second deadline. For OR-Tools, `random_seed` does not affect RoutingSearch. The recorded seed instead selects among six first-solution strategies; the search is time limited, so runtime varies slightly across reruns. Each standard instance has one test instance and ten strategy selections/seeds.

The primary tiny-CVRP QUBO settings use 100 sweeps, or 100 attempted flips per binary variable, with a 5-second secondary cap. `vrp_sa` continues until the same 0.2-second deadline as OR-Tools. This primary comparison shows the 100-sweep setting; the full schedule-by-budget study is in [the QUBO sweep report](benchmarks/results/vrp_qubo_budget_sweep.md), [raw CSV](benchmarks/results/vrp_qubo_budget_sweep.csv), and [chart](docs/vrp_qubo_budget_sweep.png). The historical `coefficient_scaled_linear` schedule remains the default. The explicit `penalty_scaled_geometric` schedule starts at temperature `8P` and cools geometrically to `0.05P`, where `P` is the constraint penalty.

### Tiny CVRP: 100-sweep primary setting

| Customers | Solver | Feasible | Mean gap on feasible runs [95% CI] | QUBO variables |
| ---: | --- | ---: | ---: | ---: |
| 4 | `qubo_sa` | 0/100 | n/a | 44–48 |
| 4 | `vrp_sa` | 91/100 | 0.00% [0.00, 0.00] | — |
| 4 | OR-Tools | 100/100 | 0.00% [0.00, 0.00] | — |
| 4 | `exact_small` | 100/100 | 0.00% [0.00, 0.00] | — |
| 5 | `qubo_sa` | 0/100 | n/a | 66–68 |
| 5 | `vrp_sa` | 97/100 | 0.00% [0.00, 0.00] | — |
| 5 | OR-Tools | 100/100 | 0.00% [0.00, 0.00] | — |
| 5 | `exact_small` | 100/100 | 0.00% [0.00, 0.00] | — |
| 6 | `qubo_sa` | 0/100 | n/a | 90–92 |
| 6 | `vrp_sa` | 90/100 | 0.63% [0.00, 1.89] | — |
| 6 | OR-Tools | 100/100 | 0.00% [0.00, 0.00] | — |
| 6 | `exact_small` | 100/100 | 0.00% [0.00, 0.00] | — |

### Standard CVRP and VRPTW references

| Instance | Published reference | Solver | Feasible | Fleet matches | Mean distance gap on matching fleet | Median gap across all feasible runs |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| A-n32-k5 | 784 | OR-Tools | 10/10 | 10/10 | 1.03% | 0.00% |
| A-n32-k5 | 784 | `vrp_sa` | 10/10 | 10/10 | 22.72% | 22.58% |
| A-n33-k5 | 661 | OR-Tools | 10/10 | 10/10 | 3.69% | 2.57% |
| A-n33-k5 | 661 | `vrp_sa` | 10/10 | 10/10 | 17.66% | 15.73% |
| A-n37-k5 | 669 | OR-Tools | 10/10 | 10/10 | 2.18% | 2.24% |
| A-n37-k5 | 669 | `vrp_sa` | 10/10 | 10/10 | 27.62% | 27.88% |
| C101-25 | 3 vehicles, 191.3 | OR-Tools | 10/10 | 10/10 | 0.00% | 0.00% |
| C101-25 | 3 vehicles, 191.3 | `vrp_sa` | 10/10 | 3/10 | 14.04% | 32.23% |
| R101-25 | 8 vehicles, 617.1 | OR-Tools | 10/10 | 10/10 | 1.52% | 2.03% |
| R101-25 | 8 vehicles, 617.1 | `vrp_sa` | 10/10 | 8/10 | 3.22% | 2.96% |
| RC101-25 | 4 vehicles, 461.1 | OR-Tools | 10/10 | 10/10 | 0.00% | 0.00% |
| RC101-25 | 4 vehicles, 461.1 | `vrp_sa` | 10/10 | 0/10 | n/a | 7.28% |

The published Augerat CVRP values come from the [CVRPLIB reference table](https://galgos.inf.puc-rio.br/cvrplib/en/instances/1). Solomon’s original VRPTW benchmark is described in [Solomon (1987)](https://doi.org/10.1287/opre.35.2.254). The 25-customer distances here are from [Pisinger and Ropke, Table 19](https://backend.orbit.dtu.dk/ws/portalfiles/portal/3154462/A%20general%20heuristic%20for%20vehicle%20routing%20problems_TechRep_Pisinger_Ropke.pdf), with fleet counts cross-checked against [Table 6 in this comparison](https://pmc.ncbi.nlm.nih.gov/articles/PMC11784799/); the benchmark is also described by [SINTEF](https://www.sintef.no/projectweb/top/vrptw/solomon-benchmark/). These 25-customer references are distance-minimizing values and here coincide with the fleet-first references. They are cited, not re-proven. The Solomon files come from the Solomon100 mirror maintained at [BUAAxyf/Solomon100](https://github.com/BUAAxyf/Solomon100/tree/23f7cf053cc7c0a7740de246791df3ece179c8df/data/solomon_100); the benchmark data originate with Solomon (1987). No files are redistributed, and the downloader pins the mirror revision and verifies each file’s SHA-256.

![Tiny CVRP feasibility and gap by customer count and solver](docs/vrp_benchmark.png)

### VRP findings

The primary 100-sweep QUBO configuration produced no feasible route in 300 runs. In the independent budget sweep, at 10,000 sweeps per variable, the penalty-scaled schedule had feasibility of 90%, 70%, and 30% at 4, 5, and 6 customers; the old schedule had 10%, 0%, and 0%. On feasible runs the corresponding penalty-scaled mean gaps were 12.6%, 23.9%, and 18.7%, and optimal-hit rates were 50%, 20%, and 0%. This improves feasibility with more effort and the penalty-scaled temperature, but leaves weak tour quality and high cost: the 10,000-sweep cells took a mean 6.5, 9.3, and 12.9 seconds. The sweep uses one annealer seed per independent instance and reports instance-bootstrap intervals; its full cell-level values and intervals are linked above.

On the three Augerat instances, under equal one-second deadlines, OR-Tools’ mean distance gaps were 1.03–3.69%, while `vrp_sa`’s were 17.66–27.62%. On the Solomon instances, OR-Tools matched the reference fleet in every run. `vrp_sa` matched in 3/10 C101, 8/10 R101, and 0/10 RC101 runs. For those single standard instances, ten seeds do not provide an instance-level confidence interval. The swap proposal now excludes selecting the same customer slot twice; as expected, this changed the route annealer’s seeded outcomes. These measurements show where this implementation performed in this run; they do not establish general solver rankings.

### VRP scope and limits

The QUBO experiment covers tiny two-vehicle CVRP only; the largest tested encoding has 92 variables, and feasible output remained limited even at the highest tested budget. `vrp_sa` is a classical routing heuristic, not a QUBO solver. Published standard reference values are cited, not re-proven. Solomon cases use the first 25 customers, with Euclidean distance and travel time truncated to one decimal to follow the cited reference convention. No results here establish performance on larger instances or other problem classes.

### Optional external QUBO samplers

Install the optional dependencies and reproduce the comparisons with:

```bash
pip install -e ".[dev,vrp,external]"
python -m benchmarks.run_external_benchmarks
```

The D-Wave `SimulatedAnnealingSampler` and OpenJij `SASampler` receive the exact same QUBO matrices as `qubo_sa`, with one read and 100 full-variable sweeps. Equal sweep counts match attempted-flip counts, not implementation speed. TSP additionally compares bit-flip `qubo_sa`, its penalty-scaled schedule, `qubo_sa_swap`, and multi-start 2-opt. Tiny CVRP compares both annealers and schedules against `vrp_sa`, OR-Tools, and the CP-SAT optimum; the two routing heuristics receive the same 0.2-second deadline. See [raw results](benchmarks/results/external_comparison_raw.csv), [summary](benchmarks/results/external_comparison_summary.md), and [environment](benchmarks/results/external_comparison_environment.json) after running the command. These optional solvers are not core dependencies.

Both external annealers also struggled with the plain bit-flip QUBOs: at 20-city TSP, D-Wave was feasible in 82/100 runs with an average gap of 98.41%, and OpenJij was feasible in 81/100 runs with a 98.53% gap; the in-repository bit-flip solver was feasible in 98/100 runs with an 86.60% gap under the same flip count. For tiny CVRP’s 100-sweep penalty-scaled schedule, feasibility at 4/5/6 customers was 16/2/1 runs for native `qubo_sa`, 9/0/3 for D-Wave, and 5/3/3 for OpenJij, out of 100 each. This evidence shows the weakness is not unique to our annealer, while the performance differences show that annealing kernels matter. It is consistent with the penalty encoding and one-bit moves being limiting, but it does not isolate either as the cause.
