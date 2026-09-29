"""Reproducible swap-annealer schedule selection on held-out TSP instances."""
from __future__ import annotations

import csv
from pathlib import Path
from statistics import mean

from benchmarks.run_benchmarks import held_karp, make_instance
from quasar_solver import QuboSASwapSolver

SIZES = (6, 10, 15, 20)
TUNING_INSTANCE_SEEDS = (303000, 303001)
TUNING_SOLVER_SEEDS = (100, 101, 102)
SCHEDULES = ((0.1, 10.0), (1.0, 30.0), (5.0, 100.0), (10.0, 100.0))


def tune(output_dir=Path("benchmarks/results")) -> tuple[float, float]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for size in SIZES:
        for instance_seed in TUNING_INSTANCE_SEEDS:
            problem = make_instance(size, instance_seed)
            _, optimum = held_karp(problem)
            for beta_start, beta_end in SCHEDULES:
                for solver_seed in TUNING_SOLVER_SEEDS:
                    result = QuboSASwapSolver(num_reads=1, num_sweeps=100,
                                              beta_start=beta_start,
                                              beta_end=beta_end).solve(problem, seed=solver_seed)
                    rows.append({"size": size, "instance_seed": instance_seed,
                                 "solver_seed": solver_seed, "beta_start": beta_start,
                                 "beta_end": beta_end, "optimum": optimum,
                                 "objective": result.objective,
                                 "gap_percent": 100 * (result.objective / optimum - 1),
                                 "moves_attempted": result.metadata["moves_attempted"],
                                 "runtime_seconds": result.runtime})
    with (output_dir / "swap_tuning.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    scores = {schedule: mean(row["gap_percent"] for row in rows
                             if (row["beta_start"], row["beta_end"]) == schedule)
              for schedule in SCHEDULES}
    selected = min(SCHEDULES, key=lambda schedule: (scores[schedule], schedule))
    lines = ["# Swap schedule tuning", "",
             "Command: `python -m benchmarks.tune_swap`.",
             f"Tuning instance seeds: {TUNING_INSTANCE_SEEDS}; solver seeds: {TUNING_SOLVER_SEEDS}.",
             "These seeds are disjoint from the benchmark instance and solver seeds.",
             "Each schedule uses one read, 100 sweeps, and 100 × n² attempted swaps per run.",
             "Inverse temperature is linearly interpolated from beta_start to beta_end, then divided by max_distance.",
             "Selection rule: lowest mean percentage gap to Held–Karp optimum across all 24 tuning runs per schedule; ties choose the lexicographically smaller schedule.",
             "", "| beta_start | beta_end | Runs | Mean gap |", "| ---: | ---: | ---: | ---: |"]
    for schedule in SCHEDULES:
        lines.append(f"| {schedule[0]:g} | {schedule[1]:g} | 24 | {scores[schedule]:.3f}% |")
    lines.extend(["", f"Selected schedule: beta_start={selected[0]:g}, beta_end={selected[1]:g}.", ""])
    (output_dir / "swap_tuning.md").write_text("\n".join(lines), encoding="utf-8")
    return selected


if __name__ == "__main__":
    print(tune())
