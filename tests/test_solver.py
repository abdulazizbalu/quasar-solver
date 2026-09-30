import numpy as np

from quasar_solver.qubo import QUBO
from quasar_solver.solver import SimulatedAnnealingSolver


def test_solver_finds_zero_vector_for_positive_diagonal_qubo():
    qubo = QUBO()
    for i in range(4):
        qubo.add(i, i, 2.0)

    solver = SimulatedAnnealingSolver(num_reads=50, num_sweeps=200, seed=7)
    result = solver.solve(qubo)

    np.testing.assert_array_equal(result.best_sample, np.zeros(4, dtype=int))
    assert result.best_energy == 0.0
    assert len(result.all_energies) == 50


def test_solver_finds_known_minimum_for_negative_diagonal_qubo():
    qubo = QUBO()
    qubo.add(0, 0, -1.0)
    qubo.add(1, 1, 2.0)
    qubo.add(2, 2, -3.0)

    solver = SimulatedAnnealingSolver(num_reads=50, num_sweeps=200, seed=11)
    result = solver.solve(qubo)

    np.testing.assert_array_equal(result.best_sample, np.array([1, 0, 1]))
    assert result.best_energy == -4.0


def test_penalty_scaled_geometric_schedule_has_documented_endpoints():
    solver = SimulatedAnnealingSolver(num_reads=1, num_sweeps=5, seed=1,
                                      schedule="penalty_scaled_geometric", schedule_scale=10.0)
    assert solver._beta_for_sweep(0, 1 / 80, 2, geometric=True) == 1 / 80
    assert solver._beta_for_sweep(4, 1 / 80, 2, geometric=True) == 2


def test_old_schedule_is_the_default():
    qubo = QUBO()
    qubo.add(0, 0, -2)
    qubo.add(0, 1, 3)
    default = SimulatedAnnealingSolver(num_reads=4, num_sweeps=10, seed=42).solve(qubo)
    explicit = SimulatedAnnealingSolver(num_reads=4, num_sweeps=10, seed=42,
                                        schedule="coefficient_scaled_linear").solve(qubo)
    np.testing.assert_array_equal(default.best_sample, explicit.best_sample)
    assert default.best_energy == explicit.best_energy
