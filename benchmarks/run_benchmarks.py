"""Timed, reproducible TSP comparison and QUBO penalty sweep."""
from __future__ import annotations

import argparse
import csv
import platform
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from statistics import mean
from time import perf_counter

import numpy as np

from quasar_solver import QuboSASolver, TSPInstance, is_feasible_tsp, tour_length
from quasar_solver.tsp_solver import Solution

PENALTY_ALPHAS = (1, 2, 5, 10, 50)
TIME_LIMITS = (1.0, 5.0)
SIZES = (6, 10, 15, 20)


def make_instance(size: int, instance_seed: int = 2026) -> TSPInstance:
    rng = np.random.default_rng(instance_seed + size)
    return TSPInstance(f"uniform2d_n{size}_seed{instance_seed + size}", coordinates=rng.random((size, 2)))


def held_karp(problem: TSPInstance) -> tuple[list[int], float]:
    """Return a proven optimal cycle using O(n^2 2^n) dynamic programming."""
    n, d = problem.size, problem.distance_matrix
    # State (visited subset excluding city 0, final city) -> (length, predecessor).
    dp: dict[tuple[int, int], tuple[float, int | None]] = {}
    for j in range(1, n):
        dp[(1 << (j - 1), j)] = (float(d[0, j]), 0)
    for subset_size in range(2, n):
        for subset in combinations(range(1, n), subset_size):
            mask = sum(1 << (j - 1) for j in subset)
            for last in subset:
                prior_mask = mask ^ (1 << (last - 1))
                candidates = [(dp[(prior_mask, prev)][0] + float(d[prev, last]), prev)
                              for prev in subset if prev != last]
                dp[(mask, last)] = min(candidates)
    full = (1 << (n - 1)) - 1
    cost, last = min((dp[(full, j)][0] + float(d[j, 0]), j) for j in range(1, n))
    route = [last]
    mask = full
    while last != 0:
        _, previous = dp[(mask, last)]
        mask ^= 1 << (last - 1)
        if previous == 0:
            break
        route.append(previous)
        last = previous
    route = [0] + list(reversed(route))
    return route, float(cost)


def two_opt(problem: TSPInstance, time_limit: float, seed: int = 0) -> Solution:
    """Multi-start nearest neighbor plus first-improvement 2-opt until deadline."""
    if time_limit <= 0:
        raise ValueError("time_limit must be positive")
    start_time = perf_counter()
    deadline = start_time + time_limit
    d, n = problem.distance_matrix, problem.size
    rng = np.random.default_rng(seed)
    best_route: list[int] = []
    best_length = float("inf")
    starts = list(range(n))
    rng.shuffle(starts)
    for first in starts:
        if perf_counter() >= deadline and best_route:
            break
        route = [first]
        remaining = set(range(n)) - {first}
        while remaining:
            nxt = min(remaining, key=lambda city: (d[route[-1], city], city))
            route.append(nxt)
            remaining.remove(nxt)
        improved = True
        while improved and perf_counter() < deadline:
            improved = False
            current = tour_length(route, problem)
            for i in range(1, n - 1):
                for j in range(i + 1, n):
                    if perf_counter() >= deadline:
                        break
                    candidate = route[:i] + route[i:j + 1][::-1] + route[j + 1:]
                    value = tour_length(candidate, problem)
                    if value < current - 1e-12:
                        route, improved = candidate, True
                        break
                if improved or perf_counter() >= deadline:
                    break
        value = tour_length(route, problem)
        if value < best_length:
            best_route, best_length = route, value
    feasible = is_feasible_tsp(best_route, problem)
    return Solution(best_route, best_length if feasible else None, feasible,
                    perf_counter() - start_time, "two_opt", {"seed": seed})


def _summary(rows: list[dict]) -> list[dict]:
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        groups[(row["size"], row["time_limit_seconds"], row["solver"], row["penalty_setting"])].append(row)
    result = []
    for (size, limit, solver, penalty), group in sorted(groups.items(), key=lambda x: (x[0][0], x[0][1], x[0][2], str(x[0][3]))):
        feasible = [r for r in group if r["feasible"]]
        result.append({"size": size, "time_limit_seconds": limit, "solver": solver, "penalty_setting": penalty,
                       "runs": len(group), "feasibility_percent": 100 * len(feasible) / len(group),
                       "mean_objective": mean(r["objective"] for r in feasible) if feasible else None,
                       "mean_runtime_seconds": mean(r["runtime_seconds"] for r in group),
                       "best_known": group[0]["best_known"], "reference_status": group[0]["reference_status"],
                       "mean_gap_percent": mean(r["gap_percent"] for r in feasible) if feasible else None})
    return result


def run_benchmarks(sizes=SIZES, seeds=range(10), time_limits=TIME_LIMITS,
                   output_dir=Path("benchmarks/results"), alphas=PENALTY_ALPHAS) -> list[dict]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    raw: list[dict] = []
    python, cpu, system = platform.python_version(), platform.processor() or platform.uname().processor or "unknown", platform.platform()
    for size in sizes:
        problem = make_instance(size)
        if size <= 12:
            _, reference, status = *held_karp(problem), "proven optimum"
        else:
            reference, status = None, "best found, not proven"
        # Run one baseline and each requested penalty under every identical time budget.
        for limit in time_limits:
            cases = [("two_opt", "n/a", None)] + [("qubo_sa", str(alpha), alpha) for alpha in alphas] + [("qubo_sa", "fixed_100", None)]
            for seed in seeds:
                for solver_name, penalty_setting, alpha in cases:
                    if solver_name == "two_opt":
                        solution = two_opt(problem, limit, seed)
                    else:
                        adapter = QuboSASolver(penalty=100.0 if penalty_setting == "fixed_100" else None,
                                               penalty_alpha=alpha)
                        solution = adapter.solve(problem, time_limit=limit, seed=seed)
                    raw.append({"instance": problem.name, "size": size, "solver": solver_name,
                                "penalty_setting": penalty_setting, "penalty": solution.metadata.get("penalty", ""),
                                "time_limit_seconds": limit, "seed": seed,
                                "objective": solution.objective if solution.feasible else "",
                                "feasible": solution.feasible, "runtime_seconds": solution.runtime,
                                "best_known": reference if reference is not None else "",
                                "reference_status": status if reference is not None else "pending",
                                "gap_percent": "", "python": python, "cpu": cpu, "system": system})
        # For n>12 define best found globally across both solvers/budgets/settings on this instance.
        if reference is None:
            candidates = [r["objective"] for r in raw if r["size"] == size and r["objective"] != ""]
            reference = min(candidates) if candidates else None
        for row in raw:
            if row["size"] != size:
                continue
            row["best_known"] = reference if reference is not None else ""
            row["reference_status"] = status
            row["gap_percent"] = (100 * (row["objective"] / reference - 1)
                                  if row["objective"] != "" and reference and reference > 0 else "")
    # Save the raw data before rendering derived reports.
    fields = list(raw[0]) if raw else []
    with (output_dir / "raw.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(raw)
    summaries = _summary(raw)
    _write_summary(output_dir / "summary.md", summaries, python, cpu, system, time_limits)
    _write_chart(output_dir.parent.parent / "docs" / "tsp_benchmark.png", summaries, time_limits, sizes)
    return summaries


def _write_summary(path: Path, summaries: list[dict], python: str, cpu: str, system: str, time_limits) -> None:
    lines = ["# TSP benchmark", "", f"Python: {python}; CPU: {cpu}; system: {system}.",
             "", "Instances: NumPy default_rng(2026 + n), uniform [0,1)^2. Seeds: 0–9.",
             "Each solver receives the same wall-clock limit per run. `two_opt` is multi-start nearest neighbor plus 2-opt. QUBO sweep uses alpha × max_distance for alpha in {1,2,5,10,50}, plus fixed penalty 100.",
             "For n ≤ 12, gap is versus the proven Held–Karp optimum. For larger n, gap is versus the best feasible result across all tested solvers, budgets, and penalties; that reference is not proven. Objective/gap means include feasible runs only; runtimes include all runs."]
    for limit in time_limits:
        lines += ["", f"## Time limit: {limit:g} s", "",
                  "| Cities | Solver | Penalty | Feasible | Mean objective | Mean runtime (s) | Reference | Status | Mean gap |",
                  "| ---: | --- | --- | ---: | ---: | ---: | ---: | --- | ---: |"]
        for x in summaries:
            if x["time_limit_seconds"] != limit:
                continue
            fmt = lambda v: "—" if v is None else f"{v:.4f}"
            gap_value = x["mean_gap_percent"]
            if gap_value is not None and abs(gap_value) < 0.0005:
                gap_value = 0.0
            gap = "—" if gap_value is None else f"{gap_value:.3f}%"
            lines.append(f"| {x['size']} | {x['solver']} | {x['penalty_setting']} | {x['feasibility_percent']:.1f}% | {fmt(x['mean_objective'])} | {x['mean_runtime_seconds']:.3f} | {x['best_known']:.4f} | {x['reference_status']} | {gap} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_chart(path: Path, summaries: list[dict], time_limits, sizes) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, len(time_limits), figsize=(6 * len(time_limits), 8), sharex="col", squeeze=False)
    for col, limit in enumerate(time_limits):
        for solver in ("qubo_sa", "two_opt"):
            series = []
            for size in sizes:
                group = [x for x in summaries if x["size"] == size and x["time_limit_seconds"] == limit and x["solver"] == solver]
                if solver == "qubo_sa":
                    feasible_runs = [x for x in group if x["mean_gap_percent"] is not None]
                    feasibility = mean(x["feasibility_percent"] for x in group) if group else 0
                    gap = mean(x["mean_gap_percent"] for x in feasible_runs) if feasible_runs else None
                else:
                    item = group[0] if group else None
                    feasibility = item["feasibility_percent"] if item else 0
                    gap = item["mean_gap_percent"] if item else None
                series.append((size, feasibility, gap))
            axes[0, col].plot([p[0] for p in series], [p[1] for p in series], marker="o", label=solver)
            axes[1, col].plot([p[0] for p in series], [p[2] if p[2] is not None else np.nan for p in series], marker="o", label=solver)
        axes[0, col].set_title(f"Time limit {limit:g} s")
        axes[0, col].set_ylabel("Feasible runs (%)")
        axes[0, col].set_ylim(-5, 105)
        axes[1, col].set_ylabel("Mean gap (%)")
        axes[1, col].set_xlabel("Number of cities")
        axes[0, col].grid(True, alpha=.3)
        axes[1, col].grid(True, alpha=.3)
        axes[0, col].legend()
    fig.suptitle("TSP benchmark: QUBO-SA aggregated across penalties vs 2-opt")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("benchmarks/results"))
    parser.add_argument("--runs", type=int, default=10)
    args = parser.parse_args()
    run_benchmarks(seeds=range(args.runs), output_dir=args.output_dir)
