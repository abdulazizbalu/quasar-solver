"""Permutation-preserving simulated annealing for the TSP QUBO."""
from __future__ import annotations

from collections.abc import Callable
from time import perf_counter
from typing import Literal

import numpy as np

from quasar_solver.problem import TSPInstance, tour_length
from quasar_solver.tsp_solver import QuboSASolver, Solution


def permutation_sample(route: list[int]) -> np.ndarray:
    """Encode a tour with the same city-major indexing as tsp_to_qubo."""
    n = len(route)
    sample = np.zeros(n * n, dtype=np.int8)
    for position, city in enumerate(route):
        sample[city * n + position] = 1
    return sample


def swap_delta(route: list[int], distances: np.ndarray, first: int, second: int) -> float:
    """QUBO-energy change for swapping two positions in a valid tour.

    One-hot penalties have the same value for every permutation, so only the
    edges touching the two positions change. Adjacent positions are handled
    by deduplicating their affected edge indices.
    """
    n = len(route)
    if not (0 <= first < n and 0 <= second < n):
        raise ValueError("swap positions are outside the tour")
    if first == second:
        return 0.0
    changed = {first - 1, first, second - 1, second}
    before = sum(distances[route[k % n], route[(k + 1) % n]] for k in changed)

    def after(position: int) -> int:
        position %= n
        if position == first:
            return route[second]
        if position == second:
            return route[first]
        return route[position]

    after_cost = sum(distances[after(k), after(k + 1)] for k in changed)
    return float(after_cost - before)


class QuboSASwapSolver:
    """Anneal valid permutation matrices with a fixed number of swap attempts.

    City 0 stays at position 0. Each sweep proposes n^2 swaps, matching the
    bit-flip solver's n^2 attempted flips per sweep. This is n proposals per
    city per sweep; each proposal evaluates only changed route edges.
    """

    name = "qubo_sa_swap"

    def __init__(self, num_reads: int = 8, num_sweeps: int = 100,
                 penalty_alpha: float = 1.0, beta_start: float = 1.0,
                 beta_end: float = 30.0):
        if num_reads <= 0 or num_sweeps <= 0:
            raise ValueError("num_reads and num_sweeps must be positive")
        if penalty_alpha <= 0 or beta_start < 0 or beta_end < 0:
            raise ValueError("penalty_alpha must be positive and beta values nonnegative")
        self.num_reads = num_reads
        self.num_sweeps = num_sweeps
        self.penalty_alpha = penalty_alpha
        self.beta_start = beta_start
        self.beta_end = beta_end

    def solve(self, problem: TSPInstance, time_limit: float | None = None,
              seed: int | None = None, budget_mode: Literal["iterations", "time"] = "iterations",
              state_observer: Callable[[tuple[int, ...]], None] | None = None) -> Solution:
        if time_limit is not None and time_limit <= 0:
            raise ValueError("time_limit must be positive")
        if budget_mode not in ("iterations", "time"):
            raise ValueError("budget_mode must be 'iterations' or 'time'")
        if budget_mode == "time" and time_limit is None:
            raise ValueError("time mode requires time_limit")

        started = perf_counter()
        deadline = started + time_limit if time_limit is not None else None
        n = problem.size
        distances = problem.distance_matrix
        qubo, penalty = QuboSASolver(penalty_alpha=self.penalty_alpha).build_qubo(problem)
        scale = max(float(np.max(distances)), 1e-12)
        rng = np.random.default_rng(seed)
        target_moves = self.num_reads * self.num_sweeps * n * n
        moves_attempted = accepted_moves = reads = 0
        best_route: list[int] = []
        best_energy = float("inf")

        while reads < self.num_reads or (budget_mode == "time" and deadline is not None and perf_counter() < deadline):
            if deadline is not None and perf_counter() >= deadline:
                break
            route = [0] + [int(city) for city in rng.permutation(np.arange(1, n))]
            if state_observer is not None:
                state_observer(tuple(route))
            energy = qubo.energy(permutation_sample(route))
            if energy < best_energy:
                best_energy, best_route = energy, route.copy()
            if n < 3:
                reads += 1
                continue

            moves_per_read = self.num_sweeps * n * n
            for move in range(moves_per_read):
                if deadline is not None and perf_counter() >= deadline:
                    break
                first = int(rng.integers(1, n))
                second = int(rng.integers(1, n - 1))
                if second >= first:
                    second += 1
                delta = swap_delta(route, distances, first, second)
                moves_attempted += 1
                if state_observer is not None:
                    proposed = route.copy()
                    proposed[first], proposed[second] = proposed[second], proposed[first]
                    state_observer(tuple(proposed))
                fraction = move / max(1, moves_per_read - 1)
                beta = (self.beta_start + fraction * (self.beta_end - self.beta_start)) / scale
                if delta <= 0 or rng.random() < np.exp(-beta * delta):
                    route[first], route[second] = route[second], route[first]
                    energy += delta
                    accepted_moves += 1
                    if energy < best_energy:
                        best_energy, best_route = energy, route.copy()
            reads += 1

        feasible = bool(best_route)
        objective = tour_length(best_route, problem) if feasible else None
        return Solution(best_route, objective, feasible, perf_counter() - started, self.name,
                        {"budget_mode": budget_mode, "num_reads": self.num_reads,
                         "num_sweeps": self.num_sweeps, "moves_per_city_target": self.num_reads * self.num_sweeps * n,
                         "move_budget": target_moves, "moves_attempted": moves_attempted,
                         "accepted_moves": accepted_moves, "penalty": penalty,
                         "qubo_energy": best_energy, "seed": seed,
                         "beta_start": self.beta_start, "beta_end": self.beta_end,
                         "time_limit_seconds": time_limit})
