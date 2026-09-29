"""Vehicle routing data and independent route validation.

Node zero is the depot. Routes include both depot endpoints. Service starts
after waiting for a window to open, and depot return must meet its deadline.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class CVRPInstance:
    name: str
    distance_matrix: np.ndarray
    demands: np.ndarray
    capacity: int
    num_vehicles: int | None = None
    depot: int = 0
    known_optimum: float | None = None

    def __post_init__(self) -> None:
        d = np.asarray(self.distance_matrix, dtype=float)
        q = np.asarray(self.demands, dtype=int)
        if d.ndim != 2 or d.shape[0] < 2 or d.shape[0] != d.shape[1] or not np.isfinite(d).all() or (d < 0).any():
            raise ValueError("distance_matrix must be finite, nonnegative and square")
        if q.shape != (len(d),) or (q < 0).any() or q[0] != 0:
            raise ValueError("demands must have one nonnegative entry per node and zero at depot")
        if self.depot != 0 or self.capacity <= 0 or (q[1:] > self.capacity).any():
            raise ValueError("depot must be node zero and each demand must fit capacity")
        if self.num_vehicles is not None and self.num_vehicles <= 0:
            raise ValueError("num_vehicles must be positive")
        self.distance_matrix, self.demands = d, q

    @property
    def size(self) -> int:
        return len(self.demands) - 1


@dataclass
class VRPTWInstance(CVRPInstance):
    time_windows: np.ndarray | None = None
    service_times: np.ndarray | None = None
    travel_time_matrix: np.ndarray | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        w = np.asarray(self.time_windows, dtype=float)
        s = np.asarray(self.service_times, dtype=float)
        t = self.distance_matrix if self.travel_time_matrix is None else np.asarray(self.travel_time_matrix, dtype=float)
        if w.shape != (self.size + 1, 2) or not np.isfinite(w).all() or (w[:, 0] > w[:, 1]).any():
            raise ValueError("invalid time_windows")
        if s.shape != (self.size + 1,) or not np.isfinite(s).all() or (s < 0).any():
            raise ValueError("invalid service_times")
        if t.shape != self.distance_matrix.shape or not np.isfinite(t).all() or (t < 0).any():
            raise ValueError("invalid travel_time_matrix")
        self.time_windows, self.service_times, self.travel_time_matrix = w, s, t


def check_vrp_routes(routes: object, problem: CVRPInstance) -> tuple[bool, str]:
    if not isinstance(routes, (tuple, list)):
        return False, "routes must be a sequence"
    if problem.num_vehicles is not None and len(routes) > problem.num_vehicles:
        return False, "too many vehicles"
    seen: list[int] = []
    for route in routes:
        if not isinstance(route, (tuple, list)) or len(route) < 3 or route[0] != 0 or route[-1] != 0:
            return False, "route must start/end at depot and visit a customer"
        if any(not isinstance(x, (int, np.integer)) or isinstance(x, (bool, np.bool_)) or x < 0 or x > problem.size for x in route):
            return False, "invalid node"
        if 0 in route[1:-1]:
            return False, "depot inside route"
        seen.extend(route[1:-1])
        if sum(int(problem.demands[x]) for x in route[1:-1]) > problem.capacity:
            return False, "capacity exceeded"
        if isinstance(problem, VRPTWInstance):
            clock = float(problem.time_windows[0, 0])
            for a, b in zip(route, route[1:]):
                clock = max(clock + problem.service_times[a] + problem.travel_time_matrix[a, b], problem.time_windows[b, 0])
                if clock > problem.time_windows[b, 1] + 1e-9:
                    return False, "time window missed"
    if sorted(seen) != list(range(1, problem.size + 1)):
        return False, "customers missing or duplicated"
    return True, "ok"


def is_feasible_vrp(routes: object, problem: CVRPInstance) -> bool:
    return check_vrp_routes(routes, problem)[0]


def routes_distance(routes: list[list[int]], problem: CVRPInstance) -> float:
    if not is_feasible_vrp(routes, problem):
        raise ValueError("infeasible routes")
    return float(sum(problem.distance_matrix[a, b] for route in routes for a, b in zip(route, route[1:])))
