"""Simulated annealing solver for QUBO models."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from quasar_solver.qubo import QUBO


@dataclass
class SolverResult:
    """Result returned by a QUBO solver."""

    best_sample: np.ndarray
    best_energy: float
    all_energies: list[float]


class SimulatedAnnealingSolver:
    """Solve QUBO models with a simple simulated annealing schedule."""

    def __init__(
        self,
        num_reads: int = 100,
        num_sweeps: int = 1000,
        beta_start: float = 0.1,
        beta_end: float = 10.0,
        seed: int | None = None,
    ) -> None:
        """Initialize the solver with restart count, sweep count, schedule, and seed."""
        if num_reads <= 0:
            raise ValueError("num_reads must be positive.")
        if num_sweeps <= 0:
            raise ValueError("num_sweeps must be positive.")
        if beta_start < 0 or beta_end < 0:
            raise ValueError("Beta values must be non-negative.")

        self.num_reads = int(num_reads)
        self.num_sweeps = int(num_sweeps)
        self.beta_start = float(beta_start)
        self.beta_end = float(beta_end)
        self.seed = seed

    def solve(self, qubo: QUBO) -> SolverResult:
        """Run independent annealing restarts and return the best sample found."""
        n = qubo.num_vars()
        matrix = qubo.to_matrix()
        rng = np.random.default_rng(self.seed)
        best_sample = np.zeros(n, dtype=int)
        best_energy = float("inf")
        all_energies: list[float] = []

        if n == 0:
            return SolverResult(best_sample=best_sample, best_energy=0.0, all_energies=[0.0])

        for _ in range(self.num_reads):
            sample = rng.integers(0, 2, size=n, dtype=int)
            energy = qubo.energy(sample)
            read_best_sample = sample.copy()
            read_best_energy = energy

            for sweep in range(self.num_sweeps):
                beta = self._beta_for_sweep(sweep)
                bit = int(rng.integers(0, n))
                delta = self._flip_delta(matrix, sample, bit)

                if delta <= 0.0 or rng.random() < np.exp(-delta * beta):
                    sample[bit] = 1 - sample[bit]
                    energy += delta
                    if energy < read_best_energy:
                        read_best_energy = energy
                        read_best_sample = sample.copy()

            all_energies.append(float(read_best_energy))
            if read_best_energy < best_energy:
                best_energy = read_best_energy
                best_sample = read_best_sample.copy()

        return SolverResult(
            best_sample=best_sample,
            best_energy=float(best_energy),
            all_energies=all_energies,
        )

    def _beta_for_sweep(self, sweep: int) -> float:
        """Return the linearly interpolated inverse temperature for one sweep."""
        if self.num_sweeps == 1:
            return self.beta_end
        fraction = sweep / (self.num_sweeps - 1)
        return self.beta_start + fraction * (self.beta_end - self.beta_start)

    def _flip_delta(self, matrix: np.ndarray, sample: np.ndarray, bit: int) -> float:
        """Return the energy change caused by flipping one bit."""
        change = 1 - 2 * sample[bit]
        contribution = matrix[bit, bit]
        contribution += float(np.dot(matrix[:bit, bit], sample[:bit]))
        contribution += float(np.dot(matrix[bit, bit + 1 :], sample[bit + 1 :]))
        return float(change * contribution)
