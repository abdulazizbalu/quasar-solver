"""Core QUBO representation."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np


class QUBO:
    """A quadratic unconstrained binary optimization model."""

    def __init__(self) -> None:
        """Create an empty QUBO model."""
        self.coefficients: dict[tuple[int, int], float] = {}

    def add(self, i: int, j: int, value: float) -> None:
        """Add a coefficient to the QUBO, storing only the upper triangle."""
        if i < 0 or j < 0:
            raise ValueError("Variable indices must be non-negative.")

        row, col = sorted((int(i), int(j)))
        key = (row, col)
        self.coefficients[key] = self.coefficients.get(key, 0.0) + float(value)

    def energy(self, x: np.ndarray) -> float:
        """Compute the QUBO energy for a binary vector."""
        sample = np.asarray(x)
        if sample.ndim != 1:
            raise ValueError("Sample must be a one-dimensional binary vector.")
        if len(sample) < self.num_vars():
            raise ValueError("Sample is shorter than the number of QUBO variables.")

        energy = 0.0
        for (i, j), coefficient in self.coefficients.items():
            energy += coefficient * sample[i] * sample[j]
        return float(energy)

    def num_vars(self) -> int:
        """Return the inferred number of variables in the dense index space."""
        if not self.coefficients:
            return 0
        return max(max(i, j) for i, j in self.coefficients) + 1

    def to_matrix(self) -> np.ndarray:
        """Return a dense upper-triangular matrix of QUBO coefficients."""
        n = self.num_vars()
        matrix = np.zeros((n, n), dtype=float)
        for (i, j), coefficient in self.coefficients.items():
            matrix[i, j] = coefficient
        return matrix

    def variables(self) -> Iterable[int]:
        """Return the variable indices that appear in the QUBO coefficients."""
        return sorted({index for pair in self.coefficients for index in pair})
