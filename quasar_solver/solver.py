"""Simulated annealing solver for QUBO models."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Literal

import numpy as np

from quasar_solver.qubo import QUBO


@dataclass
class SolverResult:
    """Result returned by a QUBO solver."""

    best_sample: np.ndarray
    best_energy: float
    all_energies: list[float]
    flips_attempted: int = 0
    sweeps_completed: int = 0
    coefficient_scale: float = 1.0
    effective_beta_start: float = 0.0
    effective_beta_end: float = 0.0


class SimulatedAnnealingSolver:
    """Solve QUBO models with a simple simulated annealing schedule."""

    def __init__(
        self,
        num_reads: int = 100,
        num_sweeps: int = 1000,
        beta_start: float = 0.1,
        beta_end: float = 10.0,
        seed: int | None = None,
        schedule: Literal["coefficient_scaled_linear", "penalty_scaled_geometric"] = "coefficient_scaled_linear",
        schedule_scale: float | None = None,
    ) -> None:
        """Initialize the solver; one sweep attempts one flip for every variable."""
        if num_reads <= 0:
            raise ValueError("num_reads must be positive.")
        if num_sweeps <= 0:
            raise ValueError("num_sweeps must be positive.")
        if beta_start < 0 or beta_end < 0:
            raise ValueError("Beta values must be non-negative.")
        if schedule not in ("coefficient_scaled_linear", "penalty_scaled_geometric"):
            raise ValueError("unknown annealing schedule")
        if schedule == "penalty_scaled_geometric" and (schedule_scale is None or schedule_scale <= 0):
            raise ValueError("penalty_scaled_geometric requires a positive schedule_scale")

        self.num_reads = int(num_reads)
        self.num_sweeps = int(num_sweeps)
        self.beta_start = float(beta_start)
        self.beta_end = float(beta_end)
        self.seed = seed
        self.schedule = schedule
        self.schedule_scale = float(schedule_scale) if schedule_scale is not None else None

    def solve(
        self,
        qubo: QUBO,
        time_limit: float | None = None,
        budget_mode: Literal["iterations", "time"] = "iterations",
    ) -> SolverResult:
        """Run annealing with a fixed flip budget and an optional wall-clock cap.

        In iteration mode, each read gets ``num_sweeps * n`` attempted flips.
        Time mode repeats reads until the required wall-clock limit expires.
        """
        if time_limit is not None and time_limit <= 0:
            raise ValueError("time_limit must be positive")
        if budget_mode not in ("iterations", "time"):
            raise ValueError("budget_mode must be 'iterations' or 'time'")
        if budget_mode == "time" and time_limit is None:
            raise ValueError("time mode requires time_limit")
        deadline = perf_counter() + time_limit if time_limit is not None else None
        n = qubo.num_vars()
        matrix = qubo.to_matrix()
        coefficient_scale = float(np.max(np.abs(matrix))) if matrix.size else 1.0
        if coefficient_scale == 0.0:
            coefficient_scale = 1.0
        if self.schedule == "coefficient_scaled_linear":
            # Historical schedule retained verbatim for TSP reproducibility.
            effective_beta_start = self.beta_start / coefficient_scale
            effective_beta_end = self.beta_end / coefficient_scale
        else:
            # beta=1/T: cool geometrically from T=8P to T=0.05P.
            effective_beta_start = 1.0 / (8.0 * self.schedule_scale)
            effective_beta_end = 1.0 / (0.05 * self.schedule_scale)
        rng = np.random.default_rng(self.seed)
        best_sample = np.zeros(n, dtype=int)
        best_energy = float("inf")
        all_energies: list[float] = []

        if n == 0:
            return SolverResult(best_sample=best_sample, best_energy=0.0, all_energies=[0.0])

        reads = 0
        flips_attempted = 0
        sweeps_completed = 0
        while reads < self.num_reads or (budget_mode == "time" and deadline is not None and perf_counter() < deadline):
            if deadline is not None and perf_counter() >= deadline:
                break
            sample = rng.integers(0, 2, size=n, dtype=int)
            energy = qubo.energy(sample)
            read_best_sample = sample.copy()
            read_best_energy = energy

            for sweep in range(self.num_sweeps):
                complete_sweep = True
                beta = self._beta_for_sweep(sweep, effective_beta_start, effective_beta_end,
                                            geometric=self.schedule == "penalty_scaled_geometric")
                # A permutation guarantees exactly one attempted flip per variable.
                for bit_value in rng.permutation(n):
                    if deadline is not None and perf_counter() >= deadline:
                        complete_sweep = False
                        break
                    bit = int(bit_value)
                    delta = self._flip_delta(matrix, sample, bit)
                    flips_attempted += 1
                    if delta <= 0.0 or rng.random() < np.exp(-delta * beta):
                        sample[bit] = 1 - sample[bit]
                        energy += delta
                        if energy < read_best_energy:
                            read_best_energy = energy
                            read_best_sample = sample.copy()
                if complete_sweep:
                    sweeps_completed += 1
                else:
                    break

            all_energies.append(float(read_best_energy))
            reads += 1
            if read_best_energy < best_energy:
                best_energy = read_best_energy
                best_sample = read_best_sample.copy()

        return SolverResult(
            best_sample=best_sample,
            best_energy=float(best_energy),
            all_energies=all_energies,
            flips_attempted=flips_attempted,
            sweeps_completed=sweeps_completed,
            coefficient_scale=coefficient_scale,
            effective_beta_start=effective_beta_start,
            effective_beta_end=effective_beta_end,
        )

    def _beta_for_sweep(self, sweep: int, beta_start: float | None = None, beta_end: float | None = None,
                        geometric: bool = False) -> float:
        """Return the linearly interpolated inverse temperature for one sweep."""
        beta_start = self.beta_start if beta_start is None else beta_start
        beta_end = self.beta_end if beta_end is None else beta_end
        if self.num_sweeps == 1:
            return beta_end
        fraction = sweep / (self.num_sweeps - 1)
        if geometric:
            return beta_start * (beta_end / beta_start) ** fraction
        return beta_start + fraction * (beta_end - beta_start)

    def _flip_delta(self, matrix: np.ndarray, sample: np.ndarray, bit: int) -> float:
        """Return the energy change caused by flipping one bit."""
        change = 1 - 2 * sample[bit]
        contribution = matrix[bit, bit]
        contribution += float(np.dot(matrix[:bit, bit], sample[:bit]))
        contribution += float(np.dot(matrix[bit, bit + 1 :], sample[bit + 1 :]))
        return float(change * contribution)
