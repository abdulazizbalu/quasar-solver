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
