import numpy as np

from quasar_solver.converters.tsp import decode_tsp, tsp_to_qubo
from quasar_solver.qubo import QUBO


def test_tsp_to_qubo_uses_n_squared_variables():
    distances = np.array(
        [
            [0.0, 3.0, 4.0],
            [3.0, 0.0, 5.0],
            [4.0, 5.0, 0.0],
        ]
    )

    qubo = tsp_to_qubo(distances)

    assert isinstance(qubo, QUBO)
    assert qubo.num_vars() == 9


def test_decode_tsp_returns_empty_list_for_all_zero_sample():
    sample = np.zeros(9, dtype=int)

    assert decode_tsp(sample, 3) == []


def test_decode_tsp_returns_tour_for_valid_one_hot_sample():
    sample = np.zeros(9, dtype=int)
    sample[0 * 3 + 0] = 1
    sample[2 * 3 + 1] = 1
    sample[1 * 3 + 2] = 1

    assert decode_tsp(sample, 3) == [0, 2, 1]
