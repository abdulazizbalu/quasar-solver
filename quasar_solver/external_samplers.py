"""Optional adapters to external classical QUBO annealers.

Both receive the same coefficient mapping as :class:`QUBO`; one sampler sweep
is matched to one attempted update per variable, and read/sweep counts match
``SimulatedAnnealingSolver``. They return final states; the in-repository
solver's ``best_sample`` is the best state seen along the trajectory, and its
``final_sample`` is the like-for-like comparison. Their internal update kernels and schedule
interpolation are library-specific, so equal sweep counts are comparable work
budgets, not equal wall-clock effort.
"""
from __future__ import annotations

from typing import Literal

import numpy as np

from quasar_solver.qubo import QUBO
from quasar_solver.solver import SolverResult

Schedule = Literal["coefficient_scaled_linear", "penalty_scaled_geometric", "library_default"]


def _beta_range(qubo: QUBO, schedule: Schedule, scale: float | None) -> tuple[float, float, str]:
    """Return (beta_start, beta_end, interpolation); NaNs mean the library chooses."""
    if schedule == "library_default":
        return float("nan"), float("nan"), "default"
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
    energy = qubo.energy(sample)
    # These samplers return final states only, so best and final coincide.
    return SolverResult(sample, energy, [float(e) for e in sampleset.record.energy],
                        flips_attempted=reads * sweeps * variables,
                        sweeps_completed=reads * sweeps,
                        coefficient_scale=float(np.max(np.abs(qubo.to_matrix()))) or 1.0,
                        effective_beta_start=beta[0], effective_beta_end=beta[1],
                        final_sample=sample.copy(), final_energy=energy)


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
        options = {} if interpolation == "default" else {
            "beta_range": (beta_start, beta_end), "beta_schedule_type": interpolation}
        sampleset = SimulatedAnnealingSampler().sample(
            _bqm(qubo), num_sweeps=num_sweeps, num_reads=num_reads,
            seed=seed, answer_mode="raw", **options)
        if interpolation == "default":
            beta_start, beta_end = (float(b) for b in sampleset.info["beta_range"])
        return _as_result(sampleset, qubo, num_reads, num_sweeps, qubo.num_vars(), (beta_start, beta_end))


class OpenJijSASolver:
    """Adapter for ``openjij.SASampler``."""

    name = "openjij_sa"

    def solve(self, qubo: QUBO, num_sweeps: int, num_reads: int = 1,
              seed: int | None = None, schedule: Schedule = "coefficient_scaled_linear",
              schedule_scale: float | None = None) -> SolverResult:
        import dimod
        import openjij

        beta_start, beta_end, interpolation = _beta_range(qubo, schedule, schedule_scale)
        if interpolation == "default":
            options = {"num_sweeps": num_sweeps}
        else:
            betas = (np.linspace(beta_start, beta_end, num_sweeps) if interpolation == "linear"
                     else np.geomspace(beta_start, beta_end, num_sweeps))
            options = {"schedule": [[float(beta), 1] for beta in betas]}
        sampler = openjij.SASampler()
        bqm = _bqm(qubo)
        # With a fixed seed, OpenJij repeats one identical read num_reads times,
        # so each read is a separate call: read 0 uses ``seed`` itself and later
        # reads use seeds derived from it.
        if seed is None:
            read_seeds = [None] * num_reads
        else:
            derived = np.random.SeedSequence(seed).generate_state(max(num_reads - 1, 1))
            read_seeds = [int(seed)] + [int(x) for x in derived[:num_reads - 1]]
        samplesets = [sampler.sample(bqm, num_reads=1, seed=s, **options) for s in read_seeds]
        if interpolation == "default":
            info = samplesets[0].info["schedule"]
            beta_start, beta_end = float(info["beta_min"]), float(info["beta_max"])
        sampleset = dimod.concatenate(samplesets)
        return _as_result(sampleset, qubo, num_reads, num_sweeps, qubo.num_vars(), (beta_start, beta_end))
