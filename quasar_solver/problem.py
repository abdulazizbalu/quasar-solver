"""TSP problem data and solver-independent evaluation."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np


class Problem(Protocol):
    name: str
    known_optimum: float | None


@dataclass
class TSPInstance:
    name: str
    distance_matrix: np.ndarray | None = None
    coordinates: np.ndarray | None = None
    known_optimum: float | None = None

    def __post_init__(self) -> None:
        if (self.distance_matrix is None) == (self.coordinates is None):
            raise ValueError("Provide exactly one of distance_matrix or coordinates")
        if self.coordinates is not None:
            points = np.asarray(self.coordinates, dtype=float)
            if points.ndim != 2 or points.shape[0] < 2 or points.shape[1] < 1 or not np.isfinite(points).all():
                raise ValueError("coordinates must be a finite 2D array with at least two cities")
            self.coordinates = points
            self.distance_matrix = np.linalg.norm(points[:, None, :] - points[None, :, :], axis=2)
        else:
            matrix = np.asarray(self.distance_matrix, dtype=float)
            if matrix.ndim != 2 or matrix.shape[0] < 2 or matrix.shape[0] != matrix.shape[1] or not np.isfinite(matrix).all() or (matrix < 0).any():
                raise ValueError("distance_matrix must be finite, nonnegative, square, and at least 2x2")
            self.distance_matrix = matrix
        if self.known_optimum is not None and (not np.isfinite(self.known_optimum) or self.known_optimum < 0):
            raise ValueError("known_optimum must be finite and nonnegative")

    @property
    def size(self) -> int:
        return len(self.distance_matrix)


def is_feasible_tsp(route: object, problem: TSPInstance) -> bool:
    """Check that a route visits each city exactly once."""
    if not isinstance(route, (list, tuple, np.ndarray)) or len(route) != problem.size:
        return False
    return all(isinstance(x, (int, np.integer)) and not isinstance(x, (bool, np.bool_)) for x in route) and set(route) == set(range(problem.size))


def tour_length(route: object, problem: TSPInstance) -> float:
    if not is_feasible_tsp(route, problem):
        raise ValueError("Invalid TSP route")
    return float(sum(problem.distance_matrix[route[i], route[(i + 1) % problem.size]] for i in range(problem.size)))
