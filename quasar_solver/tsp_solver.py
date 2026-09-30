"""Common solver contract and QUBO simulated annealing adapter."""
from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter
from typing import Any, Literal, Protocol

from quasar_solver.converters.tsp import decode_tsp, tsp_to_qubo
from quasar_solver.problem import Problem, TSPInstance, is_feasible_tsp, tour_length
from quasar_solver.solver import SimulatedAnnealingSolver


@dataclass
class Solution:
    route: list[int]
    objective: float | None
    feasible: bool
    runtime: float
    solver_name: str
    metadata: dict[str, Any] = field(default_factory=dict)
    routes: list[list[int]] | None = None


class Solver(Protocol):
    def solve(self, problem: Problem, time_limit: float | None = None, seed: int | None = None) -> Solution: ...


class QuboSASolver:
    name = "qubo_sa"

    def __init__(self, num_reads: int = 8, num_sweeps: int = 100, penalty: float | None = None,
                 penalty_alpha: float | None = 1.0,
                 schedule: Literal["coefficient_scaled_linear", "penalty_scaled_geometric"] = "coefficient_scaled_linear"):
        self.num_reads = num_reads
        self.num_sweeps = num_sweeps
        self.penalty = penalty
        self.penalty_alpha = penalty_alpha
        self.schedule = schedule

    def build_qubo(self, problem: TSPInstance):
        """Build this adapter's TSP QUBO, applying its configured penalty scale."""
        max_distance = float(problem.distance_matrix.max())
        penalty = self.penalty if self.penalty is not None else (
            self.penalty_alpha * max_distance if self.penalty_alpha is not None
            else problem.size * max_distance + 1.0)
        return tsp_to_qubo(problem.distance_matrix, penalty=penalty), penalty

    def solve(self, problem: TSPInstance, time_limit: float | None = None, seed: int | None = None,
              budget_mode: Literal["iterations", "time"] = "iterations") -> Solution:
        if time_limit is not None and time_limit <= 0:
            raise ValueError("time_limit must be positive")
        start = perf_counter()
        qubo, penalty = self.build_qubo(problem)
        remaining = max(1e-9, time_limit - (perf_counter() - start)) if time_limit is not None else None
        result = SimulatedAnnealingSolver(num_reads=self.num_reads, num_sweeps=self.num_sweeps, seed=seed,
                                          schedule=self.schedule,
                                          schedule_scale=penalty if self.schedule == "penalty_scaled_geometric" else None).solve(
            qubo, time_limit=remaining, budget_mode=budget_mode)
        route = decode_tsp(result.best_sample, problem.size)
        feasible = is_feasible_tsp(route, problem)
        return Solution(route, tour_length(route, problem) if feasible else None, feasible,
                        perf_counter() - start, self.name,
                        {"qubo_energy": result.best_energy, "penalty": penalty, "penalty_alpha": self.penalty_alpha,
                         "seed": seed, "budget_mode": budget_mode, "num_sweeps": self.num_sweeps,
                         "schedule": self.schedule,
                         "num_reads": self.num_reads, "flips_attempted": result.flips_attempted,
                         "qubo_variables": qubo.num_vars(),
                         "sweeps_completed": result.sweeps_completed,
                         "coefficient_scale": result.coefficient_scale,
                         "effective_beta_start": result.effective_beta_start,
                         "effective_beta_end": result.effective_beta_end,
                         "time_limit_seconds": time_limit})
