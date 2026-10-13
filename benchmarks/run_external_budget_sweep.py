"""Larger-budget check of external annealers on 20-city TSP.

Run after ``pip install -e '.[dev,vrp,external]'`` with
``python -m benchmarks.run_external_budget_sweep``. It asks whether the
bit-flip QUBO gap seen at the matched 100-sweep budget shrinks with more
sweeps, more reads, or a different inverse-temperature range. Each
configuration runs on the ten 20-city benchmark instances with solver seeds
0-2 (30 runs). With several reads, the lowest-energy read is decoded, as a
QUBO user would. References are the proven optima in ``results/raw.csv``.

Runs execute in four worker processes, so runtimes are indicative only.
"""
from __future__ import annotations

import csv
import json
import platform
from importlib.metadata import version
from multiprocessing import Pool
from pathlib import Path
from time import perf_counter

import numpy as np

from benchmarks.run_benchmarks import INSTANCE_SEEDS, make_instance
from quasar_solver.converters.tsp import decode_tsp
from quasar_solver.external_samplers import DWaveSimulatedAnnealingSolver, OpenJijSASolver
from quasar_solver.problem import is_feasible_tsp, tour_length
from quasar_solver.solver import SimulatedAnnealingSolver
from quasar_solver.tsp_solver import QuboSASolver


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "benchmarks" / "results"
SIZE = 20
SOLVER_SEEDS = (0, 1, 2)
RANGES = ("coefficient_scaled_linear", "penalty_scaled_geometric", "library_default")
EXTERNAL_SWEEPS = {"dwave_sa": (100, 1000, 10000, 100000), "openjij_sa": (100, 1000, 10000)}
NATIVE_SWEEPS = (100, 1000)
READS = (1, 10)


def _references() -> dict[int, float]:
    with (OUT / "raw.csv").open(newline="", encoding="utf-8") as stream:
        return {int(r["instance_seed"]): float(r["proven_optimum"])
                for r in csv.DictReader(stream) if int(r["size"]) == SIZE}


def _row(problem, sample, reference, **fields) -> dict:
    route = decode_tsp(np.asarray(sample, dtype=int), SIZE)
    feasible = is_feasible_tsp(route, problem)
    objective = tour_length(route, problem) if feasible else None
    return {**fields, "feasible": int(feasible), "objective": objective if feasible else "",
            "reference": reference,
            "gap_percent": 100 * (objective / reference - 1) if feasible else ""}


def _task(args) -> list[dict]:
    instance_seed, seed, reference = args
    problem = make_instance(SIZE, instance_seed)
    qubo, penalty = QuboSASolver(num_reads=1, num_sweeps=100).build_qubo(problem)
    rows = []
    for sweeps in NATIVE_SWEEPS:
        started = perf_counter()
        result = SimulatedAnnealingSolver(num_reads=1, num_sweeps=sweeps, seed=seed).solve(qubo)
        runtime = perf_counter() - started
        for state, sample in (("best_seen", result.best_sample), ("final", result.final_sample)):
            rows.append(_row(problem, sample, reference, solver=f"qubo_sa ({state})",
                             beta_range="coefficient_scaled_linear", sweeps=sweeps, reads=1,
                             instance_seed=instance_seed, solver_seed=seed,
                             beta_start=result.effective_beta_start, beta_end=result.effective_beta_end,
                             runtime_seconds=runtime))
    for sampler in (DWaveSimulatedAnnealingSolver(), OpenJijSASolver()):
        for beta_range in RANGES:
            for sweeps in EXTERNAL_SWEEPS[sampler.name]:
                for reads in READS:
                    started = perf_counter()
                    result = sampler.solve(qubo, num_sweeps=sweeps, num_reads=reads, seed=seed,
                                           schedule=beta_range,
                                           schedule_scale=penalty if beta_range == "penalty_scaled_geometric" else None)
                    rows.append(_row(problem, result.best_sample, reference, solver=sampler.name,
                                     beta_range=beta_range, sweeps=sweeps, reads=reads,
                                     instance_seed=instance_seed, solver_seed=seed,
                                     beta_start=result.effective_beta_start,
                                     beta_end=result.effective_beta_end,
                                     runtime_seconds=perf_counter() - started))
    return rows


def summarize(rows: list[dict]) -> str:
    lines = ["# External annealers at larger budgets (20-city TSP)", "",
             f"Ten 20-city benchmark instances × solver seeds {SOLVER_SEEDS[0]}–{SOLVER_SEEDS[-1]} = 30 runs per configuration. "
             "With several reads the lowest-energy read is decoded. Mean gap is the plain mean over feasible runs, so it is "
             "conditional on feasibility; the number of feasible runs is shown next to it. "
             "Beta ranges: `coefficient_scaled_linear` is 0.1/max|Q| to 10/max|Q| (linear), "
             "`penalty_scaled_geometric` is 1/(8P) to 1/(0.05P) (geometric), and `library_default` lets each "
             "library choose its own range. `qubo_sa (best_seen)` returns the lowest-energy state visited; "
             "`qubo_sa (final)` returns the end state of the same run, like the external samplers. "
             "Runs used four worker processes, so runtimes are indicative only.", "",
             "| Solver | Beta range | Sweeps | Reads | Feasible | Mean gap on feasible runs | Median beta range | Mean runtime |",
             "| --- | --- | ---: | ---: | ---: | ---: | --- | ---: |"]
    keys = sorted({(r["solver"], r["beta_range"], int(r["sweeps"]), int(r["reads"])) for r in rows})
    for solver, beta_range, sweeps, reads in keys:
        cell = [r for r in rows if (r["solver"], r["beta_range"], int(r["sweeps"]), int(r["reads"]))
                == (solver, beta_range, sweeps, reads)]
        gaps = [float(r["gap_percent"]) for r in cell if r["gap_percent"] != ""]
        gap = f"{np.mean(gaps):.1f}% (n={len(gaps)})" if gaps else "n/a (0 feasible)"
        betas = (f"{np.median([float(r['beta_start']) for r in cell]):.3g}–"
                 f"{np.median([float(r['beta_end']) for r in cell]):.3g}")
        runtime = np.mean([float(r["runtime_seconds"]) for r in cell])
        lines.append(f"| {solver} | {beta_range} | {sweeps:,} | {reads} | {len(gaps)}/{len(cell)} | {gap} | "
                     f"{betas} | {runtime:.3f} s |")
    return "\n".join(lines) + "\n"


def run() -> list[dict]:
    references = _references()
    tasks = [(instance_seed, seed, references[instance_seed])
             for instance_seed in INSTANCE_SEEDS for seed in SOLVER_SEEDS]
    with Pool(4) as pool:
        rows = [row for chunk in pool.map(_task, tasks, chunksize=1) for row in chunk]
    with (OUT / "external_budget_sweep.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    report = summarize(rows)
    (OUT / "external_budget_sweep.md").write_text(report, encoding="utf-8")
    meta = {"command": "python -m benchmarks.run_external_budget_sweep",
            "python": platform.python_version(), "numpy": np.__version__,
            "platform": platform.platform(), "processor": platform.processor(),
            "dwave_samplers": version("dwave-samplers"), "openjij": version("openjij"),
            "size": SIZE, "instance_seeds": list(INSTANCE_SEEDS), "solver_seeds": list(SOLVER_SEEDS),
            "worker_processes": 4}
    (OUT / "external_budget_sweep_environment.json").write_text(json.dumps(meta, indent=2) + "\n",
                                                                encoding="utf-8")
    print(report)
    return rows


if __name__ == "__main__":
    run()
