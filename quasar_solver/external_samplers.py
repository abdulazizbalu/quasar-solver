"""Optional adapters to external classical QUBO annealers.

Both receive the same coefficient mapping as :class:`QUBO`; one sampler sweep
is matched to one attempted update per variable, and read/sweep counts match
``SimulatedAnnealingSolver``. Their internal update kernels and schedule
interpolation are library-specific, so equal sweep counts are comparable work
budgets, not equal wall-clock effort.
"""
from __future__ import annotations

from typing import Literal

import numpy as np

from quasar_solver.qubo import QUBO
from quasar_solver.solver import SolverResult

Schedule = Literal["coefficient_scaled_linear", "penalty_scaled_geometric"]


def _beta_range(qubo: QUBO, schedule: Schedule, scale: float | None) -> tuple[float, float, str]:
    matrix = qubo.to_matrix()
    magnitude = float(np.max(np.abs(matrix))) if matrix.size else 1.0
    magnitude = magnitude or 1.0
    if schedule == "coefficient_scaled_linear":
        return 0.1 / magnitude, 10.0 / magnitude, "linear"
    if scale is None or scale <= 0:
        raise ValueError("penalty_scaled_geometric requires a positive scale")
    return 1.0 / (8.0 * scale), 1.0 / (0.05 * scale), "geometric"


def _as_result(sampleset, qubo: QUBO, reads: int, sweeps: int, variables: int,
               beta: tuple[float, float]) -> SolverResult:
    first = sampleset.first
    sample = np.array([first.sample[i] for i in range(variables)], dtype=int)
    return SolverResult(sample, qubo.energy(sample), [float(first.energy)],
                        flips_attempted=reads * sweeps * variables,
                        sweeps_completed=reads * sweeps,
                        coefficient_scale=float(np.max(np.abs(qubo.to_matrix()))) or 1.0,
                        effective_beta_start=beta[0], effective_beta_end=beta[1])


def _bqm(qubo: QUBO):
    import dimod

    bqm = dimod.BinaryQuadraticModel.from_qubo(qubo.coefficients)
    for variable in range(qubo.num_vars()):
        bqm.add_variable(variable, 0.0)
    return bqm


class DWaveSimulatedAnnealingSolver:
    """Adapter for ``dwave.samplers.SimulatedAnnealingSampler``."""

    name = "dwave_sa"

    def solve(self, qubo: QUBO, num_sweeps: int, num_reads: int = 1,
              seed: int | None = None, schedule: Schedule = "coefficient_scaled_linear",
              schedule_scale: float | None = None) -> SolverResult:
        from dwave.samplers import SimulatedAnnealingSampler

        beta_start, beta_end, interpolation = _beta_range(qubo, schedule, schedule_scale)
        sampleset = SimulatedAnnealingSampler().sample(
            _bqm(qubo), num_sweeps=num_sweeps, num_reads=num_reads,
            beta_range=(beta_start, beta_end), beta_schedule_type=interpolation,
            seed=seed, answer_mode="raw")
        return _as_result(sampleset, qubo, num_reads, num_sweeps, qubo.num_vars(), (beta_start, beta_end))


class OpenJijSASolver:
    """Adapter for ``openjij.SASampler``."""

    name = "openjij_sa"

    def solve(self, qubo: QUBO, num_sweeps: int, num_reads: int = 1,
              seed: int | None = None, schedule: Schedule = "coefficient_scaled_linear",
              schedule_scale: float | None = None) -> SolverResult:
        import openjij

        beta_start, beta_end, interpolation = _beta_range(qubo, schedule, schedule_scale)
        betas = (np.linspace(beta_start, beta_end, num_sweeps) if interpolation == "linear"
                 else np.geomspace(beta_start, beta_end, num_sweeps))
        schedule_points = [[float(beta), 1] for beta in betas]
        sampler = openjij.SASampler()
        sampleset = sampler.sample(
            _bqm(qubo), num_reads=num_reads, schedule=schedule_points, seed=seed)
        return _as_result(sampleset, qubo, num_reads, num_sweeps, qubo.num_vars(), (beta_start, beta_end))
