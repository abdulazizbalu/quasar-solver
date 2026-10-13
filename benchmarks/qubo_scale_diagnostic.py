"""Diagnose the final annealing temperature of each schedule relative to the penalty.

Run: python -m benchmarks.qubo_scale_diagnostic

The default ``coefficient_scaled_linear`` schedule ends at beta = 10 / max|Q|,
i.e. temperature max|Q| / 10. A one-hot or assignment violation costs on the
order of the penalty P, so a final temperature at or above P leaves such
violations thermally accessible. ``penalty_scaled_geometric`` ends at 0.05 P.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from benchmarks.run_benchmarks import INSTANCE_SEEDS, SIZES as TSP_SIZES, make_instance
from benchmarks.run_vrp_benchmarks import tiny_instance
from quasar_solver.tsp_solver import QuboSASolver
from quasar_solver.vrp_qubo import build_cvrp_qubo

OUT = Path(__file__).resolve().parent / "results" / "qubo_scale_diagnostic.md"
CVRP_SETS = {"tiny benchmark and external comparison": range(203000, 203010),
             "QUBO budget sweep": range(203100, 203110)}


def _ratio(qubo, penalty: float) -> float:
    return float(np.max(np.abs(qubo.to_matrix()))) / penalty


def main() -> str:
    lines = ["# Final annealing temperature relative to the penalty", "",
             "`max|Q|/P` is the largest absolute QUBO coefficient divided by the constraint penalty P. "
             "The default `coefficient_scaled_linear` schedule ends at temperature `max|Q|/10`, "
             "shown as `T_end/P`; `penalty_scaled_geometric` always ends at `0.05 P`.", "",
             "| Problem | Instance set | Size | Instances | max\\|Q\\|/P (min–max) | Default T_end/P (min–max) |",
             "| --- | --- | ---: | ---: | ---: | ---: |"]
    for size in TSP_SIZES:
        ratios = []
        for seed in INSTANCE_SEEDS:
            qubo, penalty = QuboSASolver().build_qubo(make_instance(size, seed))
            ratios.append(_ratio(qubo, penalty))
        lines.append(f"| TSP | main benchmark | {size} | {len(ratios)} | {min(ratios):.2f}–{max(ratios):.2f} | "
                     f"{min(ratios)/10:.2f}–{max(ratios)/10:.2f} |")
    for label, seeds in CVRP_SETS.items():
        for size in (4, 5, 6):
            ratios = []
            for seed in seeds:
                qubo, meta = build_cvrp_qubo(tiny_instance(size, seed))
                ratios.append(_ratio(qubo, meta["penalty"]))
            lines.append(f"| CVRP | {label} | {size} | {len(ratios)} | {min(ratios):.1f}–{max(ratios):.1f} | "
                         f"{min(ratios)/10:.1f}–{max(ratios)/10:.1f} |")
    lines += ["", "In the CVRP QUBO, squaring the capacity equation multiplies P by products of demand and binary "
              "slack-bit weights, so max|Q| is far above P and the coefficient-normalized default ends hotter than P."]
    report = "\n".join(lines) + "\n"
    OUT.write_text(report, encoding="utf-8")
    return report


if __name__ == "__main__":
    print(main())
