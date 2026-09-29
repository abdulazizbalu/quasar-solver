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
    return CVRPInstance(f"tiny-{size}-{instance_seed}", distances,
                        np.array([0] + [1]*size), size//2, 2)


def _record(group: str, size: int, instance_seed: str, solver_seed: int, solver, problem,
            reference: float, reference_vehicles: int | None, limit: float | None) -> dict:
    try:
        result = solver.solve(problem, time_limit=limit, seed=solver_seed, budget_mode="iterations"
                              if solver.name in ("qubo_sa", "vrp_sa") else "time")
        route_count = len(result.routes or [])
        # Solomon values compare fleet size before distance.
        comparable = result.feasible and (reference_vehicles is None or route_count == reference_vehicles)
        return {"group": group, "size": size, "instance": problem.name, "instance_seed": instance_seed,
                "solver_seed": solver_seed, "solver": solver.name, "feasible": int(result.feasible),
                "objective": result.objective if result.objective is not None else "",
                "routes": route_count, "reference": reference, "reference_vehicles": reference_vehicles or "",
                "reference_type": "proven optimum" if group == "tiny" else "published reference",
                "gap_percent": (0.0 if abs(result.objective-reference) < 1e-9 else
                                100*(result.objective/reference-1)) if comparable else "",
                "runtime_seconds": result.runtime, "attempts": result.metadata.get("attempts", ""),
                "variable_count": result.metadata.get("variable_count", ""),
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
             "| Group | Customers | Solver | Feasible | Gap comparable | Mean gap [95% CI] | Mean routes | Mean runtime | Mean attempts | QUBO vars |",
             "| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    keys = sorted({(r["group"], r["size"], r["instance"] if r["group"] != "tiny" else "all", r["solver"]) for r in rows})
    for group, size, label, solver in keys:
        subset = [r for r in rows if (r["group"], r["size"], r["instance"] if r["group"] != "tiny" else "all", r["solver"]) == (group, size, label, solver)]
        gap = _ci_instance(subset, "gap_percent")
        gap_text = (f"{gap[0]:.2f}% [{gap[1]:.2f}, {gap[2]:.2f}]" if np.isfinite(gap[1])
                    else f"{gap[0]:.2f}% [CI unavailable]") if gap else "n/a"
        comparable = sum(r["gap_percent"] != "" for r in subset)
        feasible = sum(r["feasible"] for r in subset)
        routes = np.mean([r["routes"] for r in subset if r["feasible"]]) if feasible else float("nan")
        attempts = [float(r["attempts"]) for r in subset if r["attempts"] != ""]
        variables = [int(r["variable_count"]) for r in subset if r["variable_count"] != ""]
        effort = f"{np.mean(attempts):.0f}" if attempts else "—"
        lines.append(f"| {label if label != 'all' else group} | {size} | {solver} | {feasible}/{len(subset)} | {comparable}/{len(subset)} | {gap_text} | {routes:.2f} | "
                     f"{np.mean([r['runtime_seconds'] for r in subset]):.3f} s | {effort} | "
                     f"{variables[0] if variables else '—'} |")
    lines += ["", "For Solomon cases, gap is reported only for feasible runs using the published number of vehicles; n/a means no comparable run. Confidence intervals resample independent instances for tiny cases. A gap observed on only one independent instance has no estimable 95% interval. Standard cases each have one instance; their intervals are therefore unavailable despite ten solver seeds."]
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
        axis.set_xticks([4, 6])
    axes[0].legend(fontsize=8)
    fig.text(.5, .01, "Six-customer QUBO gap uses one feasible run; CI unavailable.", ha="center", fontsize=8)
    fig.tight_layout(rect=(0, .04, 1, 1))
    target = ROOT / "docs" / "vrp_benchmark.png"
    target.parent.mkdir(exist_ok=True)
    fig.savefig(target, dpi=150)
    plt.close(fig)


def run(tiny_sizes=(4, 6), instance_seeds=range(10), solver_seeds=range(10),
        standard_seeds=range(10), standard_limit=1.0, data_dir: Path | None = None) -> list[dict]:
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
                                  "gap_percent": 0.0, "runtime_seconds": optimum.runtime, "attempts": "", "variable_count": "",
                                  "status": "OPTIMAL (reused)", "time_limit_seconds": 60}
                        rows.append(result)
                    else:
                        rows.append(_record("tiny", size, str(instance_seed), seed, solver, problem,
                                            optimum.objective, None, 0.2 if solver.name == "ortools" else 5.0))
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
    with (OUT / "vrp_raw.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    (OUT / "vrp_summary.md").write_text(summarize(rows))
    metadata = {"command": "python -m benchmarks.run_vrp_benchmarks", "python": platform.python_version(),
                "platform": platform.platform(), "processor": platform.processor(),
                "numpy": np.__version__, "tiny_instance_seed_base": 203000,
                "tiny_instance_count_per_size": len(instance_seeds), "solver_seeds": list(solver_seeds),
                "standard_solver_seeds": list(standard_seeds), "standard_time_limit_seconds": standard_limit,
                "tiny_sa_wall_cap_seconds": 5.0, "tiny_ortools_time_limit_seconds": 0.2,
                "tiny_vrp_sa_attempts_per_customer": 100,
                "tiny_qubo_sweeps_per_variable": 100}
    import ortools
    metadata["ortools"] = ortools.__version__
    (OUT / "vrp_environment.json").write_text(json.dumps(metadata, indent=2) + "\n")
    chart(rows)
    print(summarize(rows))
    return rows


if __name__ == "__main__":
    run()
