"""Fixed-effort TSP benchmark against proven Held-Karp optima."""
from __future__ import annotations

import argparse
import csv
import math
import platform
import random
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from statistics import mean
from time import perf_counter

import numpy as np

from quasar_solver import (QuboSASolver, QuboSASwapSolver, TSPInstance,
                           is_feasible_tsp, tour_length)
from quasar_solver.tsp_solver import Solution

SIZES = (6, 10, 15, 20)
INSTANCE_SEEDS = tuple(202600 + i for i in range(10))
SOLVER_SEEDS = tuple(range(10))
NUM_SWEEPS = 100
NUM_READS = 1
SWAP_BETA_START = 1.0
SWAP_BETA_END = 30.0
SOLVERS = ("qubo_sa", "qubo_sa_swap", "two_opt")


def make_instance(size: int, instance_seed: int) -> TSPInstance:
    rng = np.random.default_rng(instance_seed)
    return TSPInstance(f"uniform2d_n{size}_instance{instance_seed}",
                       coordinates=rng.random((size, 2)))


def held_karp(problem: TSPInstance) -> tuple[list[int], float]:
    """Exact subset DP anchored at city 0, using float64 costs and int8 parents.

    The full n=20 DP uses about 90 MiB for costs and parents. Subsets are
    processed by cardinality so predecessor states are always complete.
    """
    n, distances = problem.size, problem.distance_matrix
    width = n - 1
    state_count = 1 << width
    costs = np.full((state_count, width), np.inf, dtype=np.float64)
    parents = np.full((state_count, width), -1, dtype=np.int8)
    for city in range(width):
        costs[1 << city, city] = distances[0, city + 1]
    counts = np.zeros(state_count, dtype=np.uint8)
    for mask in range(1, state_count):
        counts[mask] = counts[mask >> 1] + (mask & 1)
    masks_by_size = [np.flatnonzero(counts == size) for size in range(width + 1)]
    for subset_size in range(2, width + 1):
        masks = masks_by_size[subset_size]
        for last in range(width):
            selected = masks[(masks & (1 << last)) != 0]
            if not len(selected):
                continue
            previous_masks = selected ^ (1 << last)
            best = np.full(len(selected), np.inf, dtype=np.float64)
            best_parent = np.full(len(selected), -1, dtype=np.int8)
            for previous in range(width):
                if previous == last:
                    continue
                candidate = costs[previous_masks, previous] + distances[previous + 1, last + 1]
                improved = candidate < best
                best[improved] = candidate[improved]
                best_parent[improved] = previous
            costs[selected, last] = best
            parents[selected, last] = best_parent
    full_mask = state_count - 1
    terminal = costs[full_mask] + distances[1:, 0]
    last = int(np.argmin(terminal))
    optimum = float(terminal[last])
    reversed_path = []
    mask = full_mask
    while mask:
        reversed_path.append(last + 1)
        previous = int(parents[mask, last])
        mask ^= 1 << last
        last = previous
    return [0] + reversed_path[::-1], optimum


def two_opt(problem: TSPInstance, evaluation_budget: int, seed: int = 0,
            time_limit: float | None = None) -> Solution:
    """Multi-start nearest-neighbor/2-opt using a fixed candidate-evaluation budget."""
    if evaluation_budget <= 0:
        raise ValueError("evaluation_budget must be positive")
    if time_limit is not None and time_limit <= 0:
        raise ValueError("time_limit must be positive")
    started = perf_counter()
    deadline = started + time_limit if time_limit is not None else None
    rng = np.random.default_rng(seed)
    n, distances = problem.size, problem.distance_matrix
    best_route: list[int] = []
    best_cost = float("inf")
    evaluations = 0
    while evaluations < evaluation_budget and (deadline is None or perf_counter() < deadline):
        first = int(rng.integers(n))
        route = [first]
        unvisited = set(range(n)) - {first}
        while unvisited:
            nxt = min(unvisited, key=lambda city: (distances[route[-1], city], city))
            route.append(nxt)
            unvisited.remove(nxt)
        while evaluations < evaluation_budget and (deadline is None or perf_counter() < deadline):
            current = tour_length(route, problem)
            improved = False
            for i in range(1, n - 1):
                for j in range(i + 1, n):
                    if evaluations >= evaluation_budget or (deadline is not None and perf_counter() >= deadline):
                        break
                    candidate = route[:i] + route[i:j + 1][::-1] + route[j + 1:]
                    candidate_cost = tour_length(candidate, problem)
                    evaluations += 1
                    if candidate_cost < current - 1e-12:
                        route = candidate
                        improved = True
                        break
                if improved or evaluations >= evaluation_budget or (deadline is not None and perf_counter() >= deadline):
                    break
            if not improved:
                break
        cost = tour_length(route, problem)
        if cost < best_cost:
            best_route, best_cost = route, cost
    feasible = is_feasible_tsp(best_route, problem)
    return Solution(best_route, best_cost if feasible else None, feasible,
                    perf_counter() - started, "two_opt",
                    {"evaluation_budget": evaluation_budget, "evaluations": evaluations, "seed": seed})


def _bootstrap_cluster_ci(rows: list[dict], seed: int, replicates: int = 5000) -> tuple[float, float] | None:
    clusters: dict[int, list[float]] = defaultdict(list)
    for row in rows:
        if row["gap_percent"] != "":
            clusters[row["instance_seed"]].append(float(row["gap_percent"]))
    values = list(clusters.values())
    if not values:
        return None
    rng = random.Random(seed)
    samples = []
    for _ in range(replicates):
        selected = [values[rng.randrange(len(values))] for _ in values]
        samples.append(mean(x for cluster in selected for x in cluster))
    samples.sort()
    return samples[int(.025 * replicates)], samples[min(replicates - 1, int(.975 * replicates))]


def _paired_permutation_p(instance_mean_differences: list[float], seed: int,
                          draws: int = 20000) -> float | None:
    if not instance_mean_differences:
        return None
    observed = abs(math.fsum(instance_mean_differences) / len(instance_mean_differences))
    if observed == 0:
        return 1.0
    tolerance = 1e-12 * max(1.0, observed)
    if len(instance_mean_differences) <= 20:
        count = 0
        total = 1 << len(instance_mean_differences)
        for mask in range(total):
            value = abs(math.fsum(x if mask & (1 << index) else -x
                                  for index, x in enumerate(instance_mean_differences))
                        / len(instance_mean_differences))
            count += value >= observed - tolerance
        return count / total
    rng = random.Random(seed)
    count = 0
    for _ in range(draws):
        value = abs(math.fsum(x if rng.getrandbits(1) else -x
                              for x in instance_mean_differences) / len(instance_mean_differences))
        count += value >= observed - tolerance
    return (count + 1) / (draws + 1)


def _summaries(rows: list[dict]) -> list[dict]:
    groups = defaultdict(list)
    for row in rows:
        groups[(row["size"], row["solver"])].append(row)
    results = []
    for (size, solver), group in sorted(groups.items()):
        feasible = [row for row in group if row["feasible"]]
        gaps = [float(row["gap_percent"]) for row in feasible]
        ci = _bootstrap_cluster_ci(group, 12345 + size * 100 + SOLVERS.index(solver))
        results.append({"size": size, "solver": solver, "runs": len(group),
                        "instances": len({row["instance_seed"] for row in group}),
                        "feasible": len(feasible),
                        "feasibility_percent": 100 * len(feasible) / len(group),
                        "mean_gap_percent": mean(gaps) if gaps else None,
                        "gap_ci_low": ci[0] if ci else None,
                        "gap_ci_high": ci[1] if ci else None,
                        "mean_runtime_seconds": mean(row["runtime_seconds"] for row in group),
                        "mean_attempts": mean(row["attempts"] for row in group),
                        "attempt_budget": group[0]["attempt_budget"],
                        "attempts_per_city": group[0]["attempts_per_city"]})
    return results


def _paired_tests(rows: list[dict]) -> list[dict]:
    output = []
    for size in sorted({row["size"] for row in rows}):
        by_key = {(row["instance_seed"], row["solver_seed"], row["solver"]): row
                  for row in rows if row["size"] == size}
        instances = sorted({row["instance_seed"] for row in rows if row["size"] == size})
        seeds = sorted({row["solver_seed"] for row in rows if row["size"] == size})
        for solver_a, solver_b in combinations(SOLVERS, 2):
            by_instance = defaultdict(list)
            for instance in instances:
                for seed in seeds:
                    a, b = by_key[instance, seed, solver_a], by_key[instance, seed, solver_b]
                    if a["feasible"] and b["feasible"]:
                        by_instance[instance].append(float(b["gap_percent"]) - float(a["gap_percent"]))
            instance_means = [mean(values) for values in by_instance.values()]
            differences = [x for values in by_instance.values() for x in values]
            output.append({"size": size, "solver_a": solver_a, "solver_b": solver_b,
                           "paired_runs": sum(map(len, by_instance.values())),
                           "paired_instances": len(instance_means),
                           "mean_gap_difference_b_minus_a": mean(differences) if differences else "",
                           "paired_instance_sign_flip_p": _paired_permutation_p(instance_means, 12000 + size)})
    return output


def _row(problem, solution, size, instance_seed, solver_seed, sweeps, reads,
         attempt_budget, time_limit, optimum, python, cpu, system):
    attempted = (solution.metadata.get("flips_attempted") or
                 solution.metadata.get("moves_attempted") or
                 solution.metadata.get("evaluations", 0))
    gap = 100 * (solution.objective / optimum - 1) if solution.feasible else ""
    if gap != "":
        if gap < -1e-8:
            raise AssertionError("a solver objective is below the proven optimum")
        gap = max(0.0, gap)  # Suppress negative roundoff at an exact tie.
    return {"instance": problem.name, "size": size, "instance_seed": instance_seed,
            "solver_seed": solver_seed, "solver": solution.solver_name,
            "budget_mode": "iterations", "num_sweeps": sweeps, "num_reads": reads,
            "qubo_variables": size * size, "attempt_budget": attempt_budget,
            "attempts_per_city": reads * sweeps * size, "attempts": attempted,
            "runtime_seconds": solution.runtime,
            "objective": solution.objective if solution.feasible else "",
            "feasible": solution.feasible, "proven_optimum": optimum,
            "gap_percent": gap,
            "wall_time_limit_seconds": time_limit if time_limit is not None else "",
            "python": python, "cpu": cpu, "system": system}


def _write_summary(path, summaries, paired, rows):
    first = rows[0]
    sizes = sorted({row["size"] for row in rows})
    instances = sorted({row["instance_seed"] for row in rows})
    seeds = sorted({row["solver_seed"] for row in rows})
    lines = ["# TSP benchmark", "",
             f"Python: {first['python']}; CPU: {first['cpu']}; system: {first['system']}.",
             f"Sizes: {sizes}; instance seeds: {instances}; solver seeds: {seeds}.",
             f"Each solver receives {first['num_reads']} read(s) x {first['num_sweeps']} sweeps x n^2 attempted operations per run (40,000 at n=20 under the recorded settings). Attempts per city are num_reads x num_sweeps x n.",
             "QUBO-SA counts bit-flip attempts; QUBO-SA-swap counts swap proposals; multi-start 2-opt counts candidate tour evaluations. Equal counts do not imply equal computational cost. Wall-clock time is recorded but is not the stopping budget.",
             "All references are proven Held-Karp optima for each instance. Mean gap uses feasible runs only. A 5,000-replicate percentile bootstrap resamples independent instances for the 95% CI.",
             f"Swap schedule: beta_start={SWAP_BETA_START:g}, beta_end={SWAP_BETA_END:g}, normalized by max_distance. It was selected on separate instances; see [tuning](swap_tuning.md).",
             "", "| Cities | Solver | Feasible | Mean gap [95% CI] | Mean attempts / target | Attempts per city | Mean runtime (s) |",
             "| ---: | --- | ---: | ---: | ---: | ---: | ---: |"]
    for row in summaries:
        gap = "--" if row["mean_gap_percent"] is None else f"{row['mean_gap_percent']:.2f}% [{row['gap_ci_low']:.2f}, {row['gap_ci_high']:.2f}]"
        lines.append(f"| {row['size']} | {row['solver']} | {row['feasible']}/{row['runs']} | {gap} | {row['mean_attempts']:.0f} / {row['attempt_budget']} | {row['attempts_per_city']} | {row['mean_runtime_seconds']:.4f} |")
    lines += ["", "## Paired solver comparisons", "",
              "Differences are solver B minus solver A in percentage points, using paired instance and solver seeds where both runs are feasible. Exact sign flips are applied to the ten within-instance mean differences. The p-values are descriptive and are not used to select the swap schedule.",
              "", "| Cities | Solver A | Solver B | Paired runs | Paired instances | Mean gap difference (B-A, pp) | Paired p |",
              "| ---: | --- | --- | ---: | ---: | ---: | ---: |"]
    for row in paired:
        difference = "--" if row["mean_gap_difference_b_minus_a"] == "" else f"{row['mean_gap_difference_b_minus_a']:.3f}"
        p_value = "--" if row["paired_instance_sign_flip_p"] is None else f"{row['paired_instance_sign_flip_p']:.4f}"
        lines.append(f"| {row['size']} | {row['solver_a']} | {row['solver_b']} | {row['paired_runs']} | {row['paired_instances']} | {difference} | {p_value} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_chart(path, summaries, sizes):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    colors = {"qubo_sa": "#2463a6", "qubo_sa_swap": "#00896b", "two_opt": "#e87520"}
    for solver in SOLVERS:
        series = [next(row for row in summaries if row["size"] == size and row["solver"] == solver)
                  for size in sizes]
        axes[0].plot(sizes, [row["feasibility_percent"] for row in series], marker="o",
                     label=solver, color=colors[solver])
        axes[1].errorbar(sizes, [row["mean_gap_percent"] for row in series],
                         yerr=[[row["mean_gap_percent"] - row["gap_ci_low"] for row in series],
                               [row["gap_ci_high"] - row["mean_gap_percent"] for row in series]],
                         marker="o", capsize=3, label=solver, color=colors[solver])
    axes[0].set_ylabel("Feasible runs (%)")
    axes[0].set_ylim(-5, 105)
    axes[1].set_ylabel("Mean gap to proven optimum (%) with 95% CI")
    for ax in axes:
        ax.set_xlabel("Number of cities")
        ax.set_xticks(sizes)
        ax.grid(True, alpha=.3)
        ax.legend()
    fig.suptitle("TSP solvers under 100 x n^2 attempted operations per run")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _write_reports(output_dir, rows):
    summaries = _summaries(rows)
    paired = _paired_tests(rows)
    _write_summary(output_dir / "summary.md", summaries, paired, rows)
    with (output_dir / "paired_tests.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(paired[0]))
        writer.writeheader()
        writer.writerows(paired)
    _write_chart(output_dir.parent.parent / "docs" / "tsp_benchmark.png",
                 summaries, sorted({row["size"] for row in rows}))
    return summaries


def run_benchmarks(sizes=SIZES, instance_seeds=INSTANCE_SEEDS,
                   solver_seeds=SOLVER_SEEDS, output_dir=Path("benchmarks/results"),
                   num_sweeps=NUM_SWEEPS, num_reads=NUM_READS,
                   time_limit: float | None = None) -> list[dict]:
    if num_sweeps < 100 or num_reads <= 0:
        raise ValueError("benchmark requires at least 100 sweeps and a positive read count")
    sizes, instance_seeds, solver_seeds = tuple(sizes), tuple(instance_seeds), tuple(solver_seeds)
    if not sizes or not instance_seeds or not solver_seeds:
        raise ValueError("sizes and seeds must not be empty")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    python = platform.python_version()
    cpu = platform.processor() or platform.uname().processor or "unknown"
    system = platform.platform()
    rows = []
    for size in sizes:
        for instance_seed in instance_seeds:
            problem = make_instance(size, instance_seed)
            _, optimum = held_karp(problem)
            attempt_budget = num_reads * num_sweeps * size * size
            for solver_seed in solver_seeds:
                solvers = (two_opt(problem, attempt_budget, solver_seed, time_limit),
                           QuboSASolver(num_reads=num_reads, num_sweeps=num_sweeps).solve(
                               problem, time_limit=time_limit, seed=solver_seed,
                               budget_mode="iterations"),
                           QuboSASwapSolver(num_reads=num_reads, num_sweeps=num_sweeps,
                                            beta_start=SWAP_BETA_START, beta_end=SWAP_BETA_END).solve(
                               problem, time_limit=time_limit, seed=solver_seed,
                               budget_mode="iterations"))
                for solution in solvers:
                    rows.append(_row(problem, solution, size, instance_seed, solver_seed,
                                     num_sweeps, num_reads, attempt_budget, time_limit,
                                     optimum, python, cpu, system))
    with (output_dir / "raw.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return _write_reports(output_dir, rows)


def regenerate_reports(output_dir=Path("benchmarks/results")):
    output_dir = Path(output_dir)
    with (output_dir / "raw.csv").open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    if not rows:
        raise ValueError("raw.csv has no benchmark rows")
    int_fields = ("size", "instance_seed", "solver_seed", "num_sweeps", "num_reads",
                  "qubo_variables", "attempt_budget", "attempts_per_city", "attempts")
    float_fields = ("runtime_seconds", "objective", "proven_optimum", "gap_percent",
                    "wall_time_limit_seconds")
    for row in rows:
        for key in int_fields:
            row[key] = int(row[key])
        for key in float_fields:
            if row[key] != "":
                row[key] = float(row[key])
        row["feasible"] = row["feasible"].lower() == "true"
        if row["gap_percent"] != "":
            if row["gap_percent"] < -1e-8:
                raise AssertionError("a solver objective is below the proven optimum")
            row["gap_percent"] = max(0.0, row["gap_percent"])
    with (output_dir / "raw.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return _write_reports(output_dir, rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("benchmarks/results"))
    parser.add_argument("--instances", type=int, default=10)
    parser.add_argument("--solver-seeds", type=int, default=10)
    parser.add_argument("--sweeps", type=int, default=NUM_SWEEPS)
    parser.add_argument("--reads", type=int, default=NUM_READS)
    parser.add_argument("--reports-only", action="store_true")
    args = parser.parse_args()
    if args.reports_only:
        regenerate_reports(args.output_dir)
    else:
        run_benchmarks(instance_seeds=INSTANCE_SEEDS[:args.instances],
                       solver_seeds=range(args.solver_seeds), output_dir=args.output_dir,
                       num_sweeps=args.sweeps, num_reads=args.reads)
