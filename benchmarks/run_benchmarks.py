"""Reproducible TSP benchmark. Run from the repository root."""
from __future__ import annotations

import argparse
import csv
import platform
import sys
from pathlib import Path
from statistics import mean

import numpy as np

from quasar_solver import QuboSASolver, TSPInstance, tour_length


def make_instance(size: int, instance_seed: int = 2026) -> TSPInstance:
    rng = np.random.default_rng(instance_seed + size)
    return TSPInstance(f"uniform2d_n{size}_seed{instance_seed + size}", coordinates=rng.random((size, 2)))


def reference_tour(problem: TSPInstance) -> tuple[list[int], float]:
    """Deterministic nearest-neighbor starts followed by 2-opt; an upper bound, not an optimum."""
    best_route: list[int] = []
    best = float("inf")
    d = problem.distance_matrix
    for start in range(problem.size):
        route = [start]
        remaining = set(range(problem.size)) - {start}
        while remaining:
            city = min(remaining, key=lambda j: (d[route[-1], j], j))
            route.append(city)
            remaining.remove(city)
        improved = True
        while improved:
            improved = False
            current = tour_length(route, problem)
            for i in range(1, problem.size - 1):
                for j in range(i + 1, problem.size):
                    candidate = route[:i] + route[i:j + 1][::-1] + route[j + 1:]
                    if tour_length(candidate, problem) < current - 1e-12:
                        route, improved = candidate, True
                        break
                if improved:
                    break
        length = tour_length(route, problem)
        if length < best:
            best_route, best = route, length
    return best_route, best


def run_benchmarks(sizes=(6, 10, 15, 20), seeds=range(10), output_dir=Path("benchmarks/results"),
                   solver=None) -> list[dict]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    solver = solver or QuboSASolver()
    cpu = platform.processor() or platform.uname().processor or "unknown"
    system = platform.platform()
    python = platform.python_version()
    rows = []
    summary = []
    for size in sizes:
        problem = make_instance(size)
        _, reference = reference_tour(problem)
        group = []
        for seed in seeds:
            solution = solver.solve(problem, seed=seed)
            row = {"instance": problem.name, "size": size, "solver": solution.solver_name,
                   "seed": seed, "objective": solution.objective if solution.feasible else "",
                   "feasible": solution.feasible, "runtime_seconds": solution.runtime,
                   "reference_objective": reference,
                   "gap_percent": 100 * (solution.objective / reference - 1) if solution.feasible and reference > 0 else "",
                   "python": python, "cpu": cpu, "system": system}
            rows.append(row)
            group.append(row)
        feasible = [row for row in group if row["feasible"]]
        best_known = min([reference] + [row["objective"] for row in feasible])
        for row in group:
            row["reference_objective"] = best_known
            row["gap_percent"] = 100 * (row["objective"] / best_known - 1) if row["feasible"] and best_known > 0 else ""
        summary.append({"size": size, "runs": len(group), "feasibility_percent": 100 * len(feasible) / len(group),
                        "mean_objective": mean(row["objective"] for row in feasible) if feasible else None,
                        "mean_runtime_seconds": mean(row["runtime_seconds"] for row in group),
                        "reference_objective": best_known,
                        "mean_gap_percent": mean(row["gap_percent"] for row in feasible) if feasible else None})
    if rows:
        with (output_dir / "raw.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
    lines = ["# TSP benchmark", "", f"Python: {python}; CPU: {cpu}; system: {system}.",
             "", "Instances: NumPy default_rng(instance_seed + size), uniform [0,1)^2; instance_seed=2026.",
             "Best known is the best of deterministic multi-start nearest-neighbor + 2-opt and feasible benchmark runs. It is a feasible upper bound, not a certified optimum.",
             "Averages for objective and gap use feasible runs only; runtime uses all runs. Invalid objectives and gaps are blank in raw.csv.",
             "", "| Cities | Runs | Feasible | Mean objective (feasible) | Mean runtime (s) | Best known | Mean gap vs best known (feasible) |",
             "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for x in summary:
        fmt = lambda v: "—" if v is None else f"{v:.4f}"
        gap = "—" if x['mean_gap_percent'] is None else f"{x['mean_gap_percent']:.4f}%"
        lines.append(f"| {x['size']} | {x['runs']} | {x['feasibility_percent']:.1f}% | {fmt(x['mean_objective'])} | {x['mean_runtime_seconds']:.4f} | {x['reference_objective']:.4f} | {gap} |")
    (output_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("benchmarks/results"))
    args = parser.parse_args()
    run_benchmarks(output_dir=args.output_dir)
