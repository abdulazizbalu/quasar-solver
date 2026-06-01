import numpy as np

from quasar_solver.qubo import QUBO


def test_energy_matches_hand_calculated_example():
    qubo = QUBO()
    qubo.add(0, 0, 1.5)
    qubo.add(1, 1, -2.0)
    qubo.add(2, 2, 0.25)
    qubo.add(0, 1, 3.0)
    qubo.add(1, 2, -4.0)

    sample = np.array([1, 1, 0])

    assert qubo.energy(sample) == 2.5


def test_num_vars_counts_unique_variable_indices():
    qubo = QUBO()
    qubo.add(0, 0, 1.0)
    qubo.add(2, 2, 1.0)
    qubo.add(1, 2, 1.0)

    assert qubo.num_vars() == 3


def test_to_matrix_returns_dense_upper_triangular_matrix_with_expected_shape():
    qubo = QUBO()
    qubo.add(0, 0, 1.0)
    qubo.add(0, 2, 2.0)
    qubo.add(1, 1, 3.0)

    matrix = qubo.to_matrix()

    assert matrix.shape == (3, 3)
    np.testing.assert_array_equal(
        matrix,
        np.array(
            [
                [1.0, 0.0, 2.0],
                [0.0, 3.0, 0.0],
                [0.0, 0.0, 0.0],
            ]
        ),
    )
