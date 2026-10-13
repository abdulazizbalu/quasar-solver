"""Reproducible Phase 3 VRP benchmark. Run: python -m benchmarks.run_vrp_benchmarks.

Tiny CVRP: 10 instances per size, 10 solver seeds per instance, integer
EUC_2D distances, CP-SAT OPTIMAL certificate required. Standard cases:
10 solver seeds per downloaded instance, with published reference values.
"""
from __future__ import annotations

import csv
import json
import platform
from pathlib import Path
from itertools import combinations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from benchmarks.download_vrp_data import download_all
from quasar_solver.vrp import CVRPInstance
from quasar_solver.vrp_parsers import parse_cvrplib, parse_solomon
from quasar_solver.vrp_qubo import QuboSACVRPSolver, build_cvrp_qubo
from quasar_solver.vrp_solvers import ExactSmallCVRPSolver, ORToolsVRPSolver, VRPSASolver


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "benchmarks" / "results"
CVRPLIB_REF = {"A-n32-k5": 784.0, "A-n33-k5": 661.0, "A-n37-k5": 669.0}
SOLOMON_REF = {"C101": (3, 191.3), "R101": (8, 617.1), "RC101": (4, 461.1)}


def tiny_instance(size: int, instance_seed: int) -> CVRPInstance:
    rng = np.random.default_rng(instance_seed)
    coords = rng.integers(0, 100, size=(size+1, 2))
    distances = np.floor(np.linalg.norm(coords[:, None, :] - coords[None, :, :], axis=2) + .5)
    tight = instance_seed % 2 == 0
    while True:
        demands = rng.integers(1, 4, size=size)
        capacity = max(int(demands.max()), (int(demands.sum()) + 1) // 2) if tight else int(demands.sum())
        possible = any(max(int(demands[list(a)].sum()) if a else 0,
                           int(demands[[i for i in range(size) if i not in a]].sum())) <= capacity
                       for count in range(size + 1) for a in combinations(range(size), count))
        if possible:
            break
    return CVRPInstance(f"tiny-{size}-{instance_seed}", distances,
                        np.concatenate(([0], demands)), capacity, 2)


def _record(group: str, size: int, instance_seed: str, solver_seed: int, solver, problem,
            reference: float, reference_vehicles: int | None, limit: float | None) -> dict:
    try:
        result = solver.solve(problem, time_limit=limit, seed=solver_seed,
                              budget_mode="iterations" if solver.name == "qubo_sa" else "time")
        route_count = len(result.routes or [])
        # Solomon values compare fleet size before distance.
        comparable = result.feasible and (reference_vehicles is None or route_count == reference_vehicles)
        gap = 100*(result.objective/reference-1) if result.feasible else ""
        if gap != "" and abs(result.objective-reference) < 1e-9:
            gap = 0.0
        return {"group": group, "size": size, "instance": problem.name, "instance_seed": instance_seed,
                "solver_seed": solver_seed, "solver": solver.name, "feasible": int(result.feasible),
                "objective": result.objective if result.objective is not None else "",
                "routes": route_count, "reference": reference, "reference_vehicles": reference_vehicles or "",
                "reference_type": "proven optimum" if group == "tiny" else "published reference",
                "gap_percent": gap if comparable else "", "gap_all_percent": gap,
                "fleet_match": int(result.feasible and (reference_vehicles is None or route_count == reference_vehicles)),
                "runtime_seconds": result.runtime, "attempts": result.metadata.get("attempts", ""),
                "variable_count": result.metadata.get("variable_count", ""),
                "first_solution_strategy": result.metadata.get("first_solution_strategy", ""),
                "status": result.metadata.get("status", ""), "time_limit_seconds": limit or ""}
    except Exception as exc:
        raise RuntimeError(f"{problem.name} {solver.name} seed={solver_seed}") from exc


def _ci_instance(rows: list[dict], key: str) -> tuple[float, float, float] | None:
    by_instance: dict[str, list[float]] = {}
    for row in rows:
        value = row[key]
        if value != "":
            by_instance.setdefault(row["instance"], []).append(float(value))
    if not by_instance:
        return None
    means = np.array([np.mean(v) for v in by_instance.values()])
    if len(means) < 2:
        return float(means.mean()), float("nan"), float("nan")
    rng = np.random.default_rng(20260929)
    samples = np.mean(rng.choice(means, size=(5000, len(means)), replace=True), axis=1)
    return float(means.mean()), float(np.quantile(samples, .025)), float(np.quantile(samples, .975))


def summarize(rows: list[dict]) -> str:
    lines = ["# VRP benchmark summary", "", "Tiny references are CP-SAT proven optima for each generated instance. Standard references are published values, not re-proven.", "",
             "| Group | Customers | Solver | Feasible | Fleet match | Mean gap (match) [95% CI] | Median gap (all runs) | Mean routes | Mean runtime | Runtime range | Mean attempts | QUBO vars |",
             "| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    keys = sorted({(r["group"], r["size"], r["instance"] if r["group"] != "tiny" else "all", r["solver"]) for r in rows})
    for group, size, label, solver in keys:
        subset = [r for r in rows if (r["group"], r["size"], r["instance"] if r["group"] != "tiny" else "all", r["solver"]) == (group, size, label, solver)]
        gap = _ci_instance(subset, "gap_percent")
        gap_text = (f"{gap[0]:.2f}% [{gap[1]:.2f}, {gap[2]:.2f}]" if np.isfinite(gap[1])
                    else f"{gap[0]:.2f}% [CI unavailable]") if gap else "n/a"
        comparable = sum(r["gap_percent"] != "" for r in subset)
        fleet_match = sum(int(r.get("fleet_match", 0)) for r in subset)
        all_gaps = [float(r["gap_all_percent"]) for r in subset if r.get("gap_all_percent", "") != ""]
        median_all = f"{np.median(all_gaps):.2f}%" if all_gaps else "n/a"
        feasible = sum(r["feasible"] for r in subset)
        routes = np.mean([r["routes"] for r in subset if r["feasible"]]) if feasible else float("nan")
        attempts = [float(r["attempts"]) for r in subset if r["attempts"] != ""]
        runtimes = [float(r["runtime_seconds"]) for r in subset]
        runtime_range = f"{min(runtimes):.3f}–{max(runtimes):.3f} s"
        variables = [int(r["variable_count"]) for r in subset if r["variable_count"] != ""]
        variable_range = f"{min(variables)}–{max(variables)}" if variables else "—"
        effort = f"{np.mean(attempts):.0f}" if attempts else "—"
        lines.append(f"| {label if label != 'all' else group} | {size} | {solver} | {feasible}/{len(subset)} | {fleet_match}/{len(subset)} | {gap_text} | {median_all} | {routes:.2f} | "
                     f"{np.mean(runtimes):.3f} s | {runtime_range} | {effort} | "
                     f"{variable_range} |")
    lines += ["", "For Solomon cases, the mean gap and its interval use feasible runs matching the published fleet. The median gap includes every feasible run, including runs with more vehicles than the reference; under the fleet-first Solomon objective those distances are not comparable with the reference distance. Tiny-instance gaps average per-instance means of feasible runs, and their intervals resample the ten tiny instances; standard cases each have one instance, so their intervals are unavailable despite ten solver seeds. The comparison table uses a shared wall-clock limit for vrp_sa and OR-Tools. OR-Tools seeds select one of six first-solution strategies (seed mod 6), so seeds 6–9 repeat the strategies of seeds 0–3. An infeasible tiny `vrp_sa` run means its greedy construction found no capacity-feasible start (status `construction_failed`); no annealing was run."]
    return "\n".join(lines) + "\n"


def chart(rows: list[dict]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for solver in ("qubo_sa", "vrp_sa", "ortools", "exact_small"):
        sizes = sorted({r["size"] for r in rows if r["group"] == "tiny" and r["solver"] == solver})
        if not sizes:
            continue
        subset = [[r for r in rows if r["group"] == "tiny" and r["size"] == n and r["solver"] == solver] for n in sizes]
        axes[0].plot(sizes, [100*np.mean([r["feasible"] for r in group]) for group in subset], marker="o", label=solver)
        axes[1].plot(sizes, [float(_ci_instance(group, "gap_percent")[0]) if _ci_instance(group, "gap_percent") else np.nan for group in subset], marker="o", label=solver)
    axes[0].set(ylabel="Feasible runs (%)", xlabel="Customers", ylim=(-5, 105))
    axes[1].set(ylabel="Mean gap to proven optimum (%)", xlabel="Customers")
    for axis in axes:
        axis.set_xticks(sorted({r["size"] for r in rows if r["group"] == "tiny"}))
    axes[0].legend(fontsize=8)
    qubo_feasible = sum(int(r["feasible"]) for r in rows if r["group"] == "tiny" and r["solver"] == "qubo_sa")
    qubo_total = sum(1 for r in rows if r["group"] == "tiny" and r["solver"] == "qubo_sa")
    fig.text(.5, .01, f"qubo_sa (default schedule, 100 sweeps): {qubo_feasible}/{qubo_total} feasible runs; "
             "gaps use feasible runs only.", ha="center", fontsize=8)
    fig.tight_layout(rect=(0, .04, 1, 1))
    target = ROOT / "docs" / "vrp_benchmark.png"
    target.parent.mkdir(exist_ok=True)
    fig.savefig(target, dpi=150)
    plt.close(fig)


def _bootstrap_mean(values: list[float], seed: int) -> tuple[float, float, float] | None:
    if not values:
        return None
    values = np.asarray(values, dtype=float)
    if len(values) == 1:
        return float(values.mean()), float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    samples = np.mean(rng.choice(values, (5000, len(values)), replace=True), axis=1)
    return float(values.mean()), float(np.quantile(samples, .025)), float(np.quantile(samples, .975))


def run_qubo_budget_sweep(sizes=(4, 5, 6), sweeps=(100, 500, 2000, 10000),
                          instance_seeds=range(203100, 203110)) -> list[dict]:
    """Budget x temperature sweep; one independent anneal per instance/cell."""
    sizes, sweeps, instance_seeds = tuple(sizes), tuple(sweeps), tuple(instance_seeds)
    schedules = ("coefficient_scaled_linear", "penalty_scaled_geometric")
    rows = []
    for size in sizes:
        for offset, instance_seed in enumerate(instance_seeds):
            problem = tiny_instance(size, instance_seed)
            exact = ExactSmallCVRPSolver().solve(problem, time_limit=60, seed=0)
            if not exact.metadata["proven"]:
                raise RuntimeError(f"No exact certificate for {problem.name}")
            for budget in sweeps:
                for schedule in schedules:
                    result = QuboSACVRPSolver(num_sweeps=budget, num_reads=1,
                                             schedule=schedule).solve(
                        problem, time_limit=30, seed=instance_seed + budget,
                        budget_mode="iterations")
                    variables = int(result.metadata["variable_count"])
                    optimal_hit = bool(result.feasible and abs(result.objective-exact.objective) <= 1e-9)
                    rows.append({"instance": problem.name, "instance_seed": instance_seed,
                                 "size": size, "demand_total": int(problem.demands.sum()),
                                 "capacity": problem.capacity,
                                 "capacity_regime": "tight" if instance_seed % 2 == 0 else "loose",
                                 "solver_seed": instance_seed + budget, "sweeps_per_variable": budget,
                                 "schedule": schedule, "feasible": int(result.feasible),
                                 "optimal_hit": int(optimal_hit),
                                 "objective": result.objective if result.feasible else "",
                                 "proven_optimum": exact.objective,
                                 "gap_percent": 100*(result.objective/exact.objective-1) if result.feasible else "",
                                 "runtime_seconds": result.runtime, "attempts": result.metadata["attempts"],
                                 "variable_count": variables, "slack_bits_per_vehicle": result.metadata["slack_bits_per_vehicle"]})
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "vrp_qubo_budget_sweep.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    write_sweep_report(rows)
    return rows


def wilson_interval(successes: int, trials: int, z: float = 1.959964) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion."""
    if trials <= 0:
        raise ValueError("trials must be positive")
    p = successes / trials
    denominator = 1 + z * z / trials
    centre = (p + z * z / (2 * trials)) / denominator
    half = z * np.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials)) / denominator
    return max(0.0, centre - half), min(1.0, centre + half)


def _count_cell(count: int, total: int) -> str:
    low, high = wilson_interval(count, total)
    return f"{count}/{total} [{100*low:.0f}, {100*high:.0f}]"


def _gap_cell(gaps: list[float], seed: int) -> str:
    """Bootstrap only with at least five feasible instances; otherwise list the values."""
    if not gaps:
        return "n/a (0 feasible)"
    if len(gaps) < 5:
        values = ", ".join(f"{g:.1f}" for g in sorted(gaps))
        return f"{np.mean(gaps):.1f}% (n={len(gaps)}: {values}; no CI)"
    stat = _bootstrap_mean(gaps, seed)
    return f"{stat[0]:.1f}% (n={len(gaps)}) [{stat[1]:.1f}, {stat[2]:.1f}]"


def write_sweep_report(rows: list[dict]) -> str:
    """Write the sweep markdown and chart from raw sweep rows."""
    sizes = sorted({int(r["size"]) for r in rows})
    sweeps = sorted({int(r["sweeps_per_variable"]) for r in rows})
    schedules = ("coefficient_scaled_linear", "penalty_scaled_geometric")
    report = ["# Tiny CVRP QUBO budget and schedule sweep", "",
              "Ten random instances per size (instance seeds 203100–203109; the same seed is reused across sizes, so instances are independent within a size, not across sizes); five use tight and five use loose capacity. One annealer seed is used per instance and cell, so each cell has ten independent binary outcomes. Feasible and optimal-hit columns show counts with 95% Wilson score intervals. Every reference was CP-SAT proven optimal.", "",
              "Gaps are conditional on feasibility: they average only the feasible runs, whose number `n` is shown, so a cell with few feasible runs is not comparable with one with many. With fewer than five feasible runs the individual gaps are listed and no interval is given; otherwise the interval is a 95% percentile bootstrap over the feasible instances.", "",
              "| Customers | Sweeps / variable | Schedule | Feasible [95% Wilson] | Optimal hits [95% Wilson] | Mean gap on feasible runs | Variables | Mean flips | Mean runtime |",
              "| ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    summary_rows = []
    for size in sizes:
        for budget in sweeps:
            for schedule in schedules:
                cell = [r for r in rows if int(r["size"]) == size and int(r["sweeps_per_variable"]) == budget
                        and r["schedule"] == schedule]
                if not cell:
                    continue
                feasible = sum(int(r["feasible"]) for r in cell)
                hits = sum(int(r["optimal_hit"]) for r in cell)
                gaps = [float(r["gap_percent"]) for r in cell if r["gap_percent"] != ""]
                variables = sorted({int(r["variable_count"]) for r in cell})
                var_text = str(variables[0]) if len(variables) == 1 else f"{variables[0]}–{variables[-1]}"
                attempts = np.mean([float(r["attempts"]) for r in cell])
                runtime = np.mean([float(r["runtime_seconds"]) for r in cell])
                summary_rows.append({"size": size, "sweeps": budget, "schedule": schedule,
                                     "feasible": feasible, "total": len(cell),
                                     "gap": float(np.mean(gaps)) if gaps else None})
                report.append(f"| {size} | {budget} | {schedule} | {_count_cell(feasible, len(cell))} | "
                              f"{_count_cell(hits, len(cell))} | {_gap_cell(gaps, 9900 + size + budget)} | "
                              f"{var_text} | {attempts:.0f} | {runtime:.3f} s |")
    text = "\n".join(report) + "\n"
    (OUT / "vrp_qubo_budget_sweep.md").write_text(text, encoding="utf-8")
    _sweep_chart(summary_rows)
    return text


def regenerate_sweep_report(path: Path = OUT / "vrp_qubo_budget_sweep.csv") -> str:
    """Rebuild the sweep markdown and chart from the saved CSV."""
    with path.open(newline="", encoding="utf-8") as stream:
        return write_sweep_report(list(csv.DictReader(stream)))


def _sweep_chart(summary_rows: list[dict]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    colors = {"coefficient_scaled_linear": "#2463a6", "penalty_scaled_geometric": "#c04b26"}
    for size in sorted({r["size"] for r in summary_rows}):
        for schedule in colors:
            subset = sorted((r for r in summary_rows if r["size"] == size and r["schedule"] == schedule),
                            key=lambda r: r["sweeps"])
            label = f"n={size}, {schedule}"
            style = "-" if size == 4 else "--" if size == 5 else ":"
            axes[0].plot([r["sweeps"] for r in subset], [r["feasible"] for r in subset],
                         marker="o", color=colors[schedule], linestyle=style, label=label)
            axes[1].plot([r["sweeps"] for r in subset], [r["gap"] if r["gap"] is not None else np.nan for r in subset],
                         marker="o", color=colors[schedule], linestyle=style, label=label)
            for r in subset:
                if r["gap"] is not None:
                    axes[1].annotate(str(r["feasible"]), (r["sweeps"], r["gap"]), fontsize=6,
                                     textcoords="offset points", xytext=(3, 3))
    for axis in axes:
        axis.set_xscale("log")
        axis.set_xlabel("Sweeps per variable")
        axis.grid(True, alpha=.3)
        axis.legend(fontsize=6)
    total = max(r["total"] for r in summary_rows)
    axes[0].set_ylabel(f"Feasible instances (of {total})")
    axes[0].set_ylim(-0.5, total + 0.5)
    axes[1].set_ylabel("Mean gap on feasible runs (%)")
    fig.text(.5, .01, "Right panel: labels give the number of feasible runs behind each mean; gaps condition on feasibility.",
             ha="center", fontsize=8)
    fig.tight_layout(rect=(0, .04, 1, 1))
    fig.savefig(ROOT / "docs" / "vrp_qubo_budget_sweep.png", dpi=150)
    plt.close(fig)


def run(tiny_sizes=(4, 5, 6), instance_seeds=range(10), solver_seeds=range(10),
        standard_seeds=range(10), standard_limit=1.0, data_dir: Path | None = None,
        run_qubo_sweep: bool = True) -> list[dict]:
    data_dir = data_dir or download_all()
    rows: list[dict] = []
    for size in tiny_sizes:
        for instance_seed in instance_seeds:
            problem = tiny_instance(size, 203000 + instance_seed)
            optimum = ExactSmallCVRPSolver().solve(problem, time_limit=60, seed=0)
            if not optimum.metadata["proven"]:
                raise RuntimeError(f"No exact certificate for {problem.name}")
            for seed in solver_seeds:
                for solver in (QuboSACVRPSolver(), VRPSASolver(100), ORToolsVRPSolver(), ExactSmallCVRPSolver()):
                    if solver.name == "exact_small":
                        # Reuse the certified result; exact optimization is not a stochastic run.
                        result = {"group": "tiny", "size": size, "instance": problem.name,
                                  "instance_seed": instance_seed, "solver_seed": seed, "solver": "exact_small",
                                  "feasible": 1, "objective": optimum.objective, "routes": len(optimum.routes or []),
                                  "reference": optimum.objective, "reference_vehicles": "", "reference_type": "proven optimum",
                                  "gap_percent": 0.0, "gap_all_percent": 0.0, "fleet_match": 1,
                                  "runtime_seconds": optimum.runtime, "attempts": "", "variable_count": "",
                                  "status": "OPTIMAL (reused)", "time_limit_seconds": 60}
                        rows.append(result)
                    else:
                        rows.append(_record("tiny", size, str(instance_seed), seed, solver, problem,
                                            optimum.objective, None, 0.2 if solver.name in ("ortools", "vrp_sa") else 5.0))
    for name, reference in CVRPLIB_REF.items():
        problem = parse_cvrplib(data_dir / f"{name}.vrp")
        for seed in standard_seeds:
            for solver in (VRPSASolver(100), ORToolsVRPSolver()):
                rows.append(_record("CVRPLIB", problem.size, "published", seed, solver, problem,
                                    reference, None, standard_limit))
    for name, (vehicles, reference) in SOLOMON_REF.items():
        problem = parse_solomon(data_dir / f"{name}.txt", 25)
        for seed in standard_seeds:
            for solver in (VRPSASolver(100), ORToolsVRPSolver()):
                rows.append(_record("Solomon25", 25, "published", seed, solver, problem,
                                    reference, vehicles, standard_limit))
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "vrp_raw.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    (OUT / "vrp_summary.md").write_text(summarize(rows), encoding="utf-8")
    metadata = {"command": "python -m benchmarks.run_vrp_benchmarks", "python": platform.python_version(),
                "platform": platform.platform(), "processor": platform.processor(),
                "numpy": np.__version__, "tiny_instance_seed_base": 203000,
                "tiny_instance_count_per_size": len(instance_seeds), "solver_seeds": list(solver_seeds),
                "standard_solver_seeds": list(standard_seeds), "standard_time_limit_seconds": standard_limit,
                "tiny_qubo_wall_cap_seconds": 5.0, "tiny_route_solver_wall_limit_seconds": 0.2,
                "tiny_vrp_sa_cooling_reference_attempts_per_customer": 100,
                "tiny_qubo_budget_mode": "iterations", "tiny_route_solver_budget_mode": "time",
                "ortools_first_solution_strategies": ["PATH_CHEAPEST_ARC", "SAVINGS",
                    "PARALLEL_CHEAPEST_INSERTION", "LOCAL_CHEAPEST_INSERTION",
                    "CHRISTOFIDES", "PATH_MOST_CONSTRAINED_ARC"],
                "tiny_qubo_sweeps_per_variable": 100,
                "qubo_budget_sweep": {"sweeps_per_variable": [100, 500, 2000, 10000],
                                      "schedules": ["coefficient_scaled_linear", "penalty_scaled_geometric"],
                                      "customers": [4, 5, 6], "instances_per_cell": 10,
                                      "solver_seeds_per_instance": 1}}
    import ortools
    metadata["ortools"] = ortools.__version__
    (OUT / "vrp_environment.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    chart(rows)
    if run_qubo_sweep:
        run_qubo_budget_sweep()
    print(summarize(rows))
    return rows


def regenerate_summary(path: Path = OUT / "vrp_raw.csv") -> str:
    """Rebuild the markdown summary from saved raw observations."""
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    for row in rows:
        for key in ("size", "feasible", "fleet_match"):
            row[key] = int(float(row[key]))
        row["routes"] = float(row["routes"])
        for key in ("gap_percent", "gap_all_percent", "runtime_seconds", "attempts", "variable_count"):
            if row.get(key, "") != "":
                row[key] = float(row[key])
    report = summarize(rows)
    (OUT / "vrp_summary.md").write_text(report, encoding="utf-8")
    chart(rows)
    return report


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-only", action="store_true",
                        help="rebuild vrp_summary.md, the QUBO sweep report and both charts from saved CSVs")
    if parser.parse_args().summary_only:
        print(regenerate_summary())
        print(regenerate_sweep_report())
    else:
        run()
