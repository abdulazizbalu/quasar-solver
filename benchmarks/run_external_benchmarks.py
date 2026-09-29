"""Optional external annealer and schedule comparison.

Run after ``pip install -e '.[dev,vrp,external]'`` with
``python -m benchmarks.run_external_benchmarks``. Every annealer receives the
same QUBO coefficients, one read, and 100 full-variable sweeps. TSP also
includes fixed-effort swap and 2-opt baselines; tiny CVRP uses the same 0.2 s
wall cap for route-based VRP-SA and OR-Tools.
"""
from __future__ import annotations

import csv
import json
import platform
from pathlib import Path
from time import perf_counter
from importlib.metadata import version

import numpy as np

from benchmarks.run_benchmarks import (SIZES as TSP_SIZES, INSTANCE_SEEDS,
                                       SOLVER_SEEDS, held_karp, make_instance,
                                       two_opt)
from benchmarks.run_vrp_benchmarks import tiny_instance
from quasar_solver.converters.tsp import decode_tsp
from quasar_solver.external_samplers import DWaveSimulatedAnnealingSolver, OpenJijSASolver
from quasar_solver.problem import is_feasible_tsp, tour_length
from quasar_solver.tsp_solver import QuboSASolver
from quasar_solver.swap_solver import QuboSASwapSolver
from quasar_solver.vrp import is_feasible_vrp, routes_distance
from quasar_solver.vrp_qubo import (QuboSACVRPSolver, build_cvrp_qubo,
                                    decode_cvrp_sample)
from quasar_solver.vrp_solvers import ExactSmallCVRPSolver, ORToolsVRPSolver, VRPSASolver


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "benchmarks" / "results"
EXTERNALS = (DWaveSimulatedAnnealingSolver(), OpenJijSASolver())
OLD = "coefficient_scaled_linear"
NEW = "penalty_scaled_geometric"
SWEEPS = 100


def _row(group, size, instance, instance_seed, solver_seed, name, schedule,
         feasible, objective, reference, runtime, attempts, variables):
    gap = 100 * (objective / reference - 1) if feasible else ""
    if gap != "" and abs(objective-reference) < 1e-9:
        gap = 0.0
    return {"group": group, "size": size, "instance": instance,
            "instance_seed": instance_seed, "solver_seed": solver_seed,
            "solver": name, "schedule": schedule, "feasible": int(feasible),
            "objective": objective if feasible else "", "reference": reference,
            "gap_percent": gap, "optimal_hit": int(bool(feasible and abs(objective-reference) <= 1e-9)),
            "runtime_seconds": runtime, "attempts": attempts, "variable_count": variables}


def _mean_ci(rows, key, seed):
    grouped = {}
    for row in rows:
        if row[key] != "":
            grouped.setdefault(row["instance"], []).append(float(row[key]))
    values = np.asarray([np.mean(v) for v in grouped.values()], dtype=float)
    if not len(values):
        return None
    if len(values) == 1:
        return float(values.mean()), float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    boot = np.mean(rng.choice(values, (5000, len(values)), replace=True), axis=1)
    return float(values.mean()), float(np.quantile(boot, .025)), float(np.quantile(boot, .975))


def _summarize(rows):
    lines = ["# Optional external annealer comparison", "",
             "Ten instances per size and ten solver seeds per instance. Confidence intervals bootstrap independent instances. External adapters receive the exact same QUBO coefficients as the in-repository solver, one read and 100 full-variable sweeps. Equivalent sweep counts do not imply equivalent kernels or elapsed time.", "",
             "| Problem | Size | Solver | Feasible | Optimal hit | Mean gap [95% CI] | Mean runtime | Mean attempts | Variables |",
             "| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    keys = sorted({(r["group"], r["size"], r["solver"], r["schedule"]) for r in rows})
    for group, size, solver, schedule in keys:
        cell = [r for r in rows if (r["group"], r["size"], r["solver"], r["schedule"]) == (group, size, solver, schedule)]
        feas = sum(int(r["feasible"]) for r in cell)
        hits = sum(int(r["optimal_hit"]) for r in cell)
        ci = _mean_ci(cell, "gap_percent", size * 9000 + len(solver))
        if ci is None:
            gap = "n/a"
        elif np.isfinite(ci[1]):
            gap = f"{ci[0]:.2f}% [{ci[1]:.2f}, {ci[2]:.2f}]"
        else:
            gap = f"{ci[0]:.2f}% [CI unavailable]"
        label = solver if schedule == "" else f"{solver} ({schedule})"
        attempts = [float(r["attempts"]) for r in cell if r["attempts"] != ""]
        variables = sorted({int(r["variable_count"]) for r in cell if r["variable_count"] != ""})
        varlabel = "—" if not variables else str(variables[0]) if len(variables) == 1 else f"{variables[0]}–{variables[-1]}"
        effort = f"{np.mean(attempts):.0f}" if attempts else "—"
        lines.append(f"| {group} | {size} | {label} | {feas}/{len(cell)} | {hits}/{len(cell)} | {gap} | "
                     f"{np.mean([r['runtime_seconds'] for r in cell]):.3f} s | {effort} | {varlabel} |")
    return "\n".join(lines) + "\n"


def run_tsp(rows):
    for size in TSP_SIZES:
        for instance_seed in INSTANCE_SEEDS:
            problem = make_instance(size, instance_seed)
            _, optimum = held_karp(problem)
            qubo, penalty = QuboSASolver(num_reads=1, num_sweeps=SWEEPS).build_qubo(problem)
            for seed in SOLVER_SEEDS:
                for label, schedule in (("qubo_sa_old", OLD), ("qubo_sa_penalty", NEW)):
                    result = QuboSASolver(num_reads=1, num_sweeps=SWEEPS,
                                          schedule=schedule).solve(problem, seed=seed)
                    rows.append(_row("TSP", size, problem.name, instance_seed, seed,
                                     label, schedule, result.feasible, result.objective,
                                     optimum, result.runtime, result.metadata["flips_attempted"], size*size))
                for sampler in EXTERNALS:
                    started = perf_counter()
                    external = sampler.solve(qubo, num_sweeps=SWEEPS, num_reads=1,
                                             seed=seed, schedule=OLD)
                    route = decode_tsp(external.best_sample, size)
                    feasible = is_feasible_tsp(route, problem)
                    objective = tour_length(route, problem) if feasible else None
                    rows.append(_row("TSP", size, problem.name, instance_seed, seed,
                                     sampler.name, OLD, feasible, objective, optimum,
                                     perf_counter()-started, external.flips_attempted, size*size))
                for solution in (QuboSASwapSolver(num_reads=1, num_sweeps=SWEEPS).solve(problem, seed=seed),
                                 two_opt(problem, SWEEPS*size*size, seed)):
                    rows.append(_row("TSP", size, problem.name, instance_seed, seed,
                                     solution.solver_name, "baseline", solution.feasible,
                                     solution.objective, optimum, solution.runtime,
                                     solution.metadata.get("flips_attempted",
                                         solution.metadata.get("moves_attempted",
                                             solution.metadata.get("evaluations", 0))),
                                     size*size))


def run_cvrp(rows):
    for size in (4, 5, 6):
        for index in range(10):
            instance_seed = 203000 + index
            problem = tiny_instance(size, instance_seed)
            exact = ExactSmallCVRPSolver().solve(problem, time_limit=60, seed=0)
            if not exact.metadata["proven"]:
                raise RuntimeError(f"No proven CVRP optimum for {problem.name}")
            qubo, meta = build_cvrp_qubo(problem)
            for seed in SOLVER_SEEDS:
                for schedule in (OLD, NEW):
                    result = QuboSACVRPSolver(SWEEPS, 1, schedule).solve(problem, seed=seed)
                    rows.append(_row("CVRP", size, problem.name, instance_seed, seed,
                                     "qubo_sa", schedule, result.feasible, result.objective,
                                     exact.objective, result.runtime, result.metadata["attempts"],
                                     result.metadata["variable_count"]))
                    for sampler in EXTERNALS:
                        started = perf_counter()
                        external = sampler.solve(qubo, num_sweeps=SWEEPS, num_reads=1,
                                                 seed=seed, schedule=schedule,
                                                 schedule_scale=meta["penalty"] if schedule == NEW else None)
                        routes = decode_cvrp_sample(external.best_sample, problem)
                        feasible = is_feasible_vrp(routes, problem)
                        objective = routes_distance(routes, problem) if feasible else None
                        rows.append(_row("CVRP", size, problem.name, instance_seed, seed,
                                         sampler.name, schedule, feasible, objective,
                                         exact.objective, perf_counter()-started, external.flips_attempted,
                                         meta["variable_count"]))
                for solver in (VRPSASolver(100), ORToolsVRPSolver()):
                    solution = solver.solve(problem, time_limit=0.2, seed=seed, budget_mode="time")
                    rows.append(_row("CVRP", size, problem.name, instance_seed, seed,
                                     solver.name, "wall_clock", solution.feasible,
                                     solution.objective, exact.objective, solution.runtime,
                                     solution.metadata.get("attempts", ""), ""))
                rows.append(_row("CVRP", size, problem.name, instance_seed, seed,
                                 "exact_small", "proven", True, exact.objective,
                                 exact.objective, exact.runtime, "", ""))


def write_results(rows):
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "external_comparison_raw.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (OUT / "external_comparison_summary.md").write_text(_summarize(rows), encoding="utf-8")
    import dwave.samplers
    meta = {"python": platform.python_version(), "numpy": np.__version__,
            "platform": platform.platform(),
            "processor": platform.processor(), "dwave_samplers": version("dwave-samplers"),
            "openjij": version("openjij"), "sweeps": SWEEPS, "reads": 1,
            "solver_seeds": list(SOLVER_SEEDS), "tsp_instance_seeds": list(INSTANCE_SEEDS),
            "cvrp_instance_seeds": list(range(203000, 203010)),
            "route_solver_time_limit_seconds": 0.2}
    (OUT / "external_comparison_environment.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    summary = _summarize(rows)
    print(summary)
    return rows


def run():
    rows = []
    run_tsp(rows)
    run_cvrp(rows)
    return write_results(rows)


def refresh_cvrp_with_corrected_moves():
    """Reuse a completed TSP experiment and refresh CVRP route-search rows."""
    path = OUT / "external_comparison_raw.csv"
    if not path.exists():
        raise FileNotFoundError("run the full external comparison before refreshing CVRP")
    with path.open(newline="", encoding="utf-8") as stream:
        rows = [row for row in csv.DictReader(stream) if row["group"] == "TSP"]
    for row in rows:
        for key in ("size", "instance_seed", "solver_seed", "feasible", "optimal_hit", "attempts", "variable_count"):
            if row.get(key, "") != "":
                row[key] = int(float(row[key]))
        for key in ("objective", "reference", "runtime_seconds", "gap_percent"):
            if row.get(key, "") != "":
                row[key] = float(row[key])
    # The completed swap runs exhausted their fixed 100 x n^2 move budget;
    # older summary code omitted the solver's `moves_attempted` metadata key.
    for row in rows:
        if row["solver"] == "qubo_sa_swap":
            row["attempts"] = str(SWEEPS * int(row["size"]) ** 2)
    run_cvrp(rows)
    return write_results(rows)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh-cvrp", action="store_true",
                        help="reuse completed TSP rows and rerun CVRP rows after a route move fix")
    if parser.parse_args().refresh_cvrp:
        refresh_cvrp_with_corrected_moves()
    else:
        run()
