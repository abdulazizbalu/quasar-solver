"""Travelling Salesman Problem conversion utilities."""

from __future__ import annotations

import numpy as np

from quasar_solver.qubo import QUBO


def tsp_to_qubo(distance_matrix: np.ndarray, penalty: float = 100.0) -> QUBO:
    """Encode a Travelling Salesman Problem instance as a QUBO."""
    distances = np.asarray(distance_matrix, dtype=float)
    if distances.ndim != 2 or distances.shape[0] != distances.shape[1]:
        raise ValueError("distance_matrix must be a square matrix.")
    if penalty <= 0:
        raise ValueError("penalty must be positive.")

    n = distances.shape[0]
    qubo = QUBO()

    for city in range(n):
        _add_exactly_one_penalty(qubo, [var(city, t, n) for t in range(n)], penalty)

    for t in range(n):
        _add_exactly_one_penalty(qubo, [var(city, t, n) for city in range(n)], penalty)

    for t in range(n):
        next_t = (t + 1) % n
        for i in range(n):
            for j in range(n):
                qubo.add(var(i, t, n), var(j, next_t, n), distances[i, j])

    return qubo


def decode_tsp(sample: np.ndarray, n: int) -> list[int]:
    """Decode a one-hot TSP sample into a tour order, or return an empty list."""
    if n <= 0:
        return []

    values = np.asarray(sample)
    if values.ndim != 1 or len(values) < n * n:
        return []

    tour: list[int] = []
    used_cities: set[int] = set()
    for t in range(n):
        active_cities = [city for city in range(n) if values[var(city, t, n)] == 1]
        if len(active_cities) != 1:
            return []

        city = active_cities[0]
        if city in used_cities:
            return []
        tour.append(city)
        used_cities.add(city)

    if len(used_cities) != n:
        return []
    return tour


def var(i: int, t: int, n: int) -> int:
    """Return the flattened variable index for city i at timestep t."""
    return i * n + t


def _add_exactly_one_penalty(qubo: QUBO, variables: list[int], penalty: float) -> None:
    """Add penalty * (sum variables - 1)^2 for binary variables."""
    for index, variable in enumerate(variables):
        qubo.add(variable, variable, -penalty)
        for other in variables[index + 1 :]:
            qubo.add(variable, other, 2.0 * penalty)
