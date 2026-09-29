"""Fixed-iteration TSP benchmark with paired seeds and instance-cluster CIs."""
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

from quasar_solver import QuboSASolver, TSPInstance, is_feasible_tsp, tour_length
from quasar_solver.tsp_solver import Solution

PENALTY_ALPHAS = (1, 2, 5, 10, 50)
SIZES = (6, 10, 15, 20)
INSTANCE_SEEDS = tuple(202600 + i for i in range(10))
SOLVER_SEEDS = tuple(range(10))
NUM_SWEEPS = 100
NUM_READS = 1
DEFAULT_ALPHA = 1


def make_instance(size: int, instance_seed: int) -> TSPInstance:
    """Make an instance using a seed independent of the stochastic solver seed."""
    rng = np.random.default_rng(instance_seed)
    return TSPInstance(f"uniform2d_n{size}_instance{instance_seed}", coordinates=rng.random((size, 2)))


def held_karp(problem: TSPInstance) -> tuple[list[int], float]:
    """Return a proven optimal tour in O(n^2 2^n) time."""
    n, d = problem.size, problem.distance_matrix
    dp: dict[tuple[int, int], tuple[float, int]] = {}
    for j in range(1, n):
        dp[(1 << (j - 1), j)] = (float(d[0, j]), 0)
    for subset_size in range(2, n):
        for subset in combinations(range(1, n), subset_size):
            mask = sum(1 << (j - 1) for j in subset)
            for last in subset:
                prior = mask ^ (1 << (last - 1))
                dp[(mask, last)] = min((dp[(prior, prev)][0] + float(d[prev, last]), prev)
                                       for prev in subset if prev != last)
    full = (1 << (n - 1)) - 1
    optimum, last = min((dp[(full, j)][0] + float(d[j, 0]), j) for j in range(1, n))
    reverse_path = [last]
    mask = full
    while True:
        _, previous = dp[(mask, last)]
        mask ^= 1 << (last - 1)
        if previous == 0:
            break
        reverse_path.append(previous)
        last = previous
    route = [0] + list(reversed(reverse_path))
    return route, float(optimum)


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
    n, d = problem.size, problem.distance_matrix
    best_route: list[int] = []
    best_cost = float("inf")
    evaluations = 0
    while evaluations < evaluation_budget and (deadline is None or perf_counter() < deadline):
        first = int(rng.integers(n))
        route = [first]
        unvisited = set(range(n)) - {first}
        while unvisited:
            nxt = min(unvisited, key=lambda city: (d[route[-1], city], city))
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
    return Solution(best_route, best_cost if feasible else None, feasible, perf_counter() - started,
                    "two_opt", {"evaluation_budget": evaluation_budget, "evaluations": evaluations, "seed": seed})


def _bootstrap_cluster_ci(rows: list[dict], seed: int, replicates: int = 5000) -> tuple[float, float] | None:
    """Percentile CI resampling whole instances, preserving within-instance pairing."""
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
        resampled = [values[rng.randrange(len(values))] for _ in values]
        flattened = [x for cluster in resampled for x in cluster]
        samples.append(mean(flattened))
    samples.sort()
    return samples[int(0.025 * replicates)], samples[min(replicates - 1, int(0.975 * replicates))]


def _exact_binomial_two_sided(k: int, n: int) -> float:
    if n == 0:
        return 1.0
    lower = min(k, n - k)
    return min(1.0, 2.0 * sum(math.comb(n, i) for i in range(lower + 1)) / (2 ** n))


def _holm_adjust(values: list[float]) -> list[float]:
    """Apply Holm's step-down family-wise correction."""
    order = sorted(range(len(values)), key=values.__getitem__)
    adjusted = [0.0] * len(values)
    running = 0.0
    for rank, index in enumerate(order):
        running = max(running, (len(values) - rank) * values[index])
        adjusted[index] = min(1.0, running)
    return adjusted


def _paired_permutation_p(instance_mean_differences: list[float], seed: int, draws: int = 20000) -> float | None:
    """Sign-flip at the independent-instance level, after within-instance pairing."""
    if not instance_mean_differences:
        return None
    observed = abs(math.fsum(instance_mean_differences) / len(instance_mean_differences))
    if observed == 0:
        return 1.0
    if len(instance_mean_differences) <= 20:
        count = 0
        total = 1 << len(instance_mean_differences)
        for mask in range(total):
            value = abs(math.fsum(x if mask & (1 << index) else -x
                                  for index, x in enumerate(instance_mean_differences))
                        / len(instance_mean_differences))
            count += value >= observed - 1e-12 * max(1.0, observed)
        return count / total
    rng = random.Random(seed)
    at_least = 0
    for _ in range(draws):
        value = abs(math.fsum(x if rng.getrandbits(1) else -x for x in instance_mean_differences) / len(instance_mean_differences))
        at_least += value >= observed - 1e-12 * max(1.0, observed)
    return (at_least + 1) / (draws + 1)


def _paired_tests(rows: list[dict], alphas) -> list[dict]:
    output = []
    penalties = tuple(str(a) for a in alphas) + ("fixed_100",)
    sizes = sorted({r["size"] for r in rows})
    for size in sizes:
        by_key = {(r["instance_seed"], r["solver_seed"], r["penalty_setting"]): r
                  for r in rows if r["size"] == size}
        for alpha_a, alpha_b in combinations(penalties, 2):
            b_only_feasible = a_only_feasible = 0
            gap_differences: dict[int, list[float]] = defaultdict(list)
            feasibility_direction_by_instance: dict[int, int] = defaultdict(int)
            instance_seeds = sorted({r["instance_seed"] for r in rows if r["size"] == size})
            solver_seeds = sorted({r["solver_seed"] for r in rows if r["size"] == size})
            for instance_seed in instance_seeds:
                for solver_seed in solver_seeds:
                    a = by_key[(instance_seed, solver_seed, alpha_a)]
                    b = by_key[(instance_seed, solver_seed, alpha_b)]
                    af, bf = a["feasible"], b["feasible"]
                    if bf and not af:
                        b_only_feasible += 1
                        feasibility_direction_by_instance[instance_seed] += 1
                    elif af and not bf:
                        a_only_feasible += 1
                        feasibility_direction_by_instance[instance_seed] -= 1
                    if af and bf:
                        gap_differences[instance_seed].append(float(b["gap_percent"]) - float(a["gap_percent"]))
            discordant = b_only_feasible + a_only_feasible
            flat_gap_differences = [x for values in gap_differences.values() for x in values]
            instance_gap_differences = [mean(values) for values in gap_differences.values() if values]
            instance_feasibility_directions = [x for x in feasibility_direction_by_instance.values() if x]
            instance_better = sum(x > 0 for x in instance_feasibility_directions)
            output.append({"size": size, "alpha_a": alpha_a, "alpha_b": alpha_b,
                           "paired_gap_n": len(flat_gap_differences),
                           "paired_instance_n": len(instance_gap_differences),
                           "mean_gap_difference_b_minus_a": mean(flat_gap_differences) if flat_gap_differences else "",
                           "paired_gap_permutation_p": _paired_permutation_p(instance_gap_differences, 9000 + size * 100 + len(output)) or "",
                           "paired_gap_holm_p": "",
                           "feasibility_discordant_n": discordant,
                           "alpha_b_feasible_only": b_only_feasible,
                           "alpha_a_feasible_only": a_only_feasible,
                           "feasibility_discordant_instance_n": len(instance_feasibility_directions),
                           "feasibility_paired_sign_p": _exact_binomial_two_sided(instance_better, len(instance_feasibility_directions)),
                           "feasibility_sign_holm_p": ""})
    for size in sizes:
        family = [r for r in output if r["size"] == size]
        for raw_key, adjusted_key in (("paired_gap_permutation_p", "paired_gap_holm_p"),
                                      ("feasibility_paired_sign_p", "feasibility_sign_holm_p")):
            present = [(r, r[raw_key]) for r in family if r[raw_key] != ""]
            adjusted = _holm_adjust([p for _, p in present])
            for (row, _), value in zip(present, adjusted):
                row[adjusted_key] = value
    return output


def run_benchmarks(sizes=SIZES, instance_seeds=INSTANCE_SEEDS, solver_seeds=SOLVER_SEEDS,
                   output_dir=Path("benchmarks/results"), alphas=PENALTY_ALPHAS,
                   num_sweeps=NUM_SWEEPS, num_reads=NUM_READS, time_limit: float | None = None) -> list[dict]:
    if num_sweeps < 100:
        raise ValueError("num_sweeps must be at least 100")
    if num_reads <= 0:
        raise ValueError("num_reads must be positive")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    sizes = tuple(sizes)
    instance_seeds = tuple(instance_seeds)
    solver_seeds = tuple(solver_seeds)
    alphas = tuple(alphas)
    rows: list[dict] = []
    python = platform.python_version()
    cpu = platform.processor() or platform.uname().processor or "unknown"
    system = platform.platform()
    for size in sizes:
        for instance_seed in instance_seeds:
            problem = make_instance(size, instance_seed)
            if size <= 12:
                _, optimum = held_karp(problem)
                status = "proven optimum"
            else:
                optimum, status = None, "best found, not proven"
            evaluation_budget = num_sweeps * num_reads * size * size
            for solver_seed in solver_seeds:
                baseline = two_opt(problem, evaluation_budget, solver_seed, time_limit)
                rows.append(_row(problem, baseline, "n/a", "", size, instance_seed, solver_seed,
                                 num_sweeps, num_reads, evaluation_budget, time_limit,
                                 optimum, status, python, cpu, system))
                for alpha in alphas:
                    adapter = QuboSASolver(num_reads=num_reads, num_sweeps=num_sweeps,
                                           penalty_alpha=float(alpha))
                    result = adapter.solve(problem, time_limit=time_limit, seed=solver_seed,
                                           budget_mode="iterations")
                    rows.append(_row(problem, result, str(alpha), result.metadata["penalty"],
                                     size, instance_seed, solver_seed, num_sweeps, num_reads,
                                     evaluation_budget, time_limit, optimum, status, python, cpu, system))
                fixed = QuboSASolver(num_reads=num_reads, num_sweeps=num_sweeps, penalty=100.0)
                result = fixed.solve(problem, time_limit=time_limit, seed=solver_seed,
                                     budget_mode="iterations")
                rows.append(_row(problem, result, "fixed_100", result.metadata["penalty"], size,
                                 instance_seed, solver_seed, num_sweeps, num_reads,
                                 evaluation_budget, time_limit, optimum, status, python, cpu, system))
            if optimum is None:
                candidates = [float(r["objective"]) for r in rows
                              if r["size"] == size and r["instance_seed"] == instance_seed and r["objective"] != ""]
                optimum = min(candidates) if candidates else None
            # Same instance reference for every solver, penalty, and solver seed.
            for row in rows:
                if row["size"] == size and row["instance_seed"] == instance_seed:
                    row["best_known"] = optimum if optimum is not None else ""
                    row["reference_status"] = status
                    row["gap_percent"] = (100 * (float(row["objective"]) / optimum - 1)
                                          if row["objective"] != "" and optimum else "")

    raw_path = output_dir / "raw.csv"
    with raw_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summaries = _summaries(rows, alphas)
    paired = _paired_tests(rows, alphas)
    _write_summary(output_dir / "summary.md", summaries, paired, python, cpu, system,
                   sizes, instance_seeds, solver_seeds, num_sweeps, num_reads, time_limit)
    with (output_dir / "paired_tests.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(paired[0]) if paired else [])
        writer.writeheader()
        writer.writerows(paired)
    _write_chart(output_dir.parent.parent / "docs" / "tsp_benchmark.png", summaries, sizes, num_sweeps, num_reads)
    return summaries


def regenerate_reports(output_dir=Path("benchmarks/results")):
    """Rebuild confidence intervals, paired tests, summary, and chart from raw.csv."""
    output_dir = Path(output_dir)
    with (output_dir / "raw.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError("raw.csv has no benchmark rows")
    int_fields = ("size", "instance_seed", "solver_seed", "num_sweeps", "num_reads",
                  "flip_or_evaluation_budget", "qubo_variables", "flips_attempted",
                  "sweeps_completed", "baseline_evaluations")
    float_fields = ("wall_time_limit_seconds", "runtime_seconds", "objective", "best_known", "gap_percent", "penalty")
    for row in rows:
        for key in int_fields:
            if row[key] != "":
                row[key] = int(row[key])
        for key in float_fields:
            if row[key] != "":
                row[key] = float(row[key])
        row["feasible"] = row["feasible"].lower() == "true"
    sizes = tuple(sorted({r["size"] for r in rows}))
    instance_seeds = tuple(sorted({r["instance_seed"] for r in rows}))
    solver_seeds = tuple(sorted({r["solver_seed"] for r in rows}))
    alphas = tuple(sorted({int(r["penalty_setting"]) for r in rows
                           if r["penalty_setting"] not in ("fixed_100", "n/a")}))
    first = rows[0]
    summaries = _summaries(rows, alphas)
    paired = _paired_tests(rows, alphas)
    time_limit = first["wall_time_limit_seconds"] or None
    _write_summary(output_dir / "summary.md", summaries, paired, first["python"], first["cpu"],
                   first["system"], sizes, instance_seeds, solver_seeds,
                   first["num_sweeps"], first["num_reads"], time_limit)
    with (output_dir / "paired_tests.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(paired[0]) if paired else [])
        writer.writeheader()
        writer.writerows(paired)
    _write_chart(output_dir.parent.parent / "docs" / "tsp_benchmark.png", summaries, sizes,
                 first["num_sweeps"], first["num_reads"])
    return summaries


def _row(problem, solution, penalty_setting, penalty, size, instance_seed, solver_seed,
         sweeps, reads, evaluation_budget, time_limit, reference, reference_status,
         python, cpu, system):
    return {"instance": problem.name, "size": size, "instance_seed": instance_seed,
            "solver_seed": solver_seed, "solver": solution.solver_name,
            "penalty_setting": penalty_setting, "penalty": penalty,
            "budget_mode": "iterations", "num_sweeps": sweeps, "num_reads": reads,
            "flip_or_evaluation_budget": evaluation_budget,
            "flips_attempted": solution.metadata.get("flips_attempted", ""),
            "qubo_variables": solution.metadata.get("qubo_variables", problem.size ** 2),
            "sweeps_completed": solution.metadata.get("sweeps_completed", ""),
            "baseline_evaluations": solution.metadata.get("evaluations", ""),
            "wall_time_limit_seconds": time_limit if time_limit is not None else "",
            "runtime_seconds": solution.runtime,
            "objective": solution.objective if solution.feasible else "",
            "feasible": solution.feasible, "best_known": reference if reference is not None else "",
            "reference_status": reference_status, "gap_percent": "",
            "python": python, "cpu": cpu, "system": system}


def _summaries(rows, alphas):
    groups = defaultdict(list)
    for row in rows:
        groups[(row["size"], row["solver"], row["penalty_setting"])].append(row)
    results = []
    for (size, solver, penalty), group in sorted(groups.items(), key=lambda x: (x[0][0], x[0][1], x[0][2])):
        feasible = [r for r in group if r["feasible"]]
        gaps = [float(r["gap_percent"]) for r in feasible if r["gap_percent"] != ""]
        ci = _bootstrap_cluster_ci(group, seed=12345 + size * 100 + len(results))
        results.append({"size": size, "solver": solver, "penalty_setting": penalty,
                        "runs": len(group), "instance_count": len({r["instance_seed"] for r in group}),
                        "feasibility_percent": 100 * len(feasible) / len(group),
                        "mean_objective": mean(float(r["objective"]) for r in feasible) if feasible else None,
                        "mean_runtime_seconds": mean(r["runtime_seconds"] for r in group),
                        "mean_gap_percent": mean(gaps) if gaps else None,
                        "gap_ci_low": ci[0] if ci else None, "gap_ci_high": ci[1] if ci else None,
                        "gap_n": len(gaps), "reference_status": group[0]["reference_status"]})
    return results


def _write_summary(path, summaries, paired, python, cpu, system, sizes, instance_seeds,
                   solver_seeds, num_sweeps, num_reads, time_limit):
    lines = ["# TSP benchmark", "", f"Python: {python}; CPU: {cpu}; system: {system}.",
             "", f"Instance seeds: {list(instance_seeds)} (separate from solver seeds {list(solver_seeds)}).",
             f"Each instance/solver-seed pair gets {num_reads} read(s) × {num_sweeps} sweeps; each sweep attempts one flip for each of the V={sizes[0] ** 2 if len(sizes) == 1 else 'n²'} QUBO binary variables. Total target is num_reads × num_sweeps × V; at 20 cities that is {num_reads * num_sweeps * 20 * 20:,} flips. Time limit is a secondary cap: {time_limit if time_limit is not None else 'none'}.",
             "The `two_opt` baseline receives the same number of candidate move evaluations as QUBO-SA attempted flips. Instances with n ≤ 12 use a proven Held–Karp optimum. For n=15 and 20, each instance uses one shared best feasible tour found across all solvers/seeds, labeled best found, not proven.",
             "Gap means use feasible runs only. The 95% confidence interval is a 5,000-replicate percentile bootstrap that resamples whole instances; raw paired runs are preserved in raw.csv.",
             "", "| Cities | Solver | Penalty | Runs | Feasible | Mean gap [95% instance-bootstrap CI] | Mean runtime (s) | Reference |",
             "| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |"]
    for x in summaries:
        gap = "—" if x["mean_gap_percent"] is None else f"{x['mean_gap_percent']:.2f}% [{x['gap_ci_low']:.2f}, {x['gap_ci_high']:.2f}] (n={x['gap_n']})"
        lines.append(f"| {x['size']} | {x['solver']} | {x['penalty_setting']} | {x['runs']} | {x['feasibility_percent']:.1f}% | {gap} | {x['mean_runtime_seconds']:.4f} | {x['reference_status']} |")
    lines += ["", "## Paired alpha comparisons (all pairs)", "",
             "For each alpha pair, the gap difference is alpha B minus alpha A over paired instance-seed/solver-seed observations where both are feasible. Gap tests use exact sign flips of within-instance mean differences for up to 20 instances (otherwise 20,000 draws); feasibility uses an exact paired sign test over instances with discordant outcomes. These tests treat instances as independent units. Holm correction is applied to all 15 pair comparisons within each size.",
              "", "| Cities | Alpha A | Alpha B | Paired runs | Paired instances | Mean gap difference (B−A, pp) | Gap p (Holm) | Feasibility discordant runs | B only feasible | A only feasible | Discordant instances | Feasibility p (Holm) |",
              "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for r in paired:
        fd = lambda value: "—" if value == "" or value is None else f"{value:.3f}"
        lines.append(f"| {r['size']} | {r['alpha_a']} | {r['alpha_b']} | {r['paired_gap_n']} | {r['paired_instance_n']} | {fd(r['mean_gap_difference_b_minus_a'])} | {fd(r['paired_gap_holm_p'])} | {r['feasibility_discordant_n']} | {r['alpha_b_feasible_only']} | {r['alpha_a_feasible_only']} | {r['feasibility_discordant_instance_n']} | {fd(r['feasibility_sign_holm_p'])} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_chart(path, summaries, sizes, num_sweeps, num_reads):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    for solver, penalty, label, color in (("qubo_sa", str(DEFAULT_ALPHA), f"qubo_sa alpha={DEFAULT_ALPHA}", "#2463a6"),
                                         ("two_opt", "n/a", "two_opt", "#e87520")):
        series = [next((x for x in summaries if x["size"] == size and x["solver"] == solver and x["penalty_setting"] == penalty), None)
                  for size in sizes]
        x = [size for size, item in zip(sizes, series) if item is not None]
        y_feas = [item["feasibility_percent"] for item in series if item is not None]
        axes[0].plot(x, y_feas, marker="o", label=label, color=color)
        valid = [(size, item) for size, item in zip(sizes, series) if item is not None and item["mean_gap_percent"] is not None]
        axes[1].errorbar([s for s, _ in valid], [item["mean_gap_percent"] for _, item in valid],
                         yerr=[[item["mean_gap_percent"] - item["gap_ci_low"] for _, item in valid],
                               [item["gap_ci_high"] - item["mean_gap_percent"] for _, item in valid]],
                         marker="o", capsize=3, label=label, color=color)
    axes[0].set_ylabel("Feasible runs (%)")
    axes[0].set_ylim(-5, 105)
    axes[1].set_ylabel("Mean gap (%) with 95% CI")
    for ax in axes:
        ax.set_xlabel("Number of cities")
        ax.set_xticks(sizes)
        ax.grid(True, alpha=.3)
        ax.legend()
    fig.suptitle(f"TSP results under {flips_per_variable_label(num_sweeps, num_reads)} fixed iteration budget")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def flips_per_variable_label(sweeps, reads):
    return f"{reads} read(s) × {sweeps} sweeps (one flip per QUBO variable per sweep)"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("benchmarks/results"))
    parser.add_argument("--instances", type=int, default=10)
    parser.add_argument("--solver-seeds", type=int, default=10)
    parser.add_argument("--sweeps", type=int, default=NUM_SWEEPS)
    parser.add_argument("--reads", type=int, default=NUM_READS)
    parser.add_argument("--reports-only", action="store_true", help="Rebuild derived reports from existing raw.csv")
    args = parser.parse_args()
    if args.reports_only:
        regenerate_reports(args.output_dir)
    else:
        run_benchmarks(instance_seeds=INSTANCE_SEEDS[:args.instances], solver_seeds=range(args.solver_seeds),
                       output_dir=args.output_dir, num_sweeps=args.sweeps, num_reads=args.reads)
