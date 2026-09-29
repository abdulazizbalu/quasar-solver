"""Tiny fixed-fleet CVRP QUBO with empty slots and binary capacity slack.

For m customers and two vehicles, there are 2*m*(m+1) one-hot slot
variables plus 2*ceil(log2(capacity+1)) slack bits. Empty slots must trail
occupied slots. All distances and demands are integer. The constant offset
of squared penalties is omitted, so feasible energy differs from tour cost
by a fixed constant.
"""
from __future__ import annotations

from time import perf_counter
import math

import numpy as np

from quasar_solver.qubo import QUBO
from quasar_solver.solver import SimulatedAnnealingSolver
from quasar_solver.tsp_solver import Solution
from quasar_solver.vrp import CVRPInstance, VRPTWInstance, is_feasible_vrp, routes_distance


def build_cvrp_qubo(problem: CVRPInstance, penalty: float | None = None) -> tuple[QUBO, dict]:
    if isinstance(problem, VRPTWInstance) or problem.size > 6 or problem.num_vehicles != 2:
        raise ValueError("CVRP QUBO supports at most six customers and exactly two vehicles")
    if not np.allclose(problem.distance_matrix, np.rint(problem.distance_matrix)):
        raise ValueError("CVRP QUBO requires integer distances")
    m, k = problem.size, 2
    if penalty is None:
        penalty = 4.0 * m * max(1.0, float(problem.distance_matrix.max()))
    if penalty <= 0:
        raise ValueError("penalty must be positive")
    slack_bits = math.ceil(math.log2(problem.capacity + 1))
    slot_count = k * m * (m + 1)
    variable_count = slot_count + k * slack_bits
    if variable_count > 100:
        raise ValueError("QUBO variable limit is 100")
    def slot(v: int, t: int, i: int) -> int:
        return (v * m + t) * (m + 1) + i
    def slack(v: int, b: int) -> int:
        return slot_count + v * slack_bits + b
    qubo = QUBO()
    qubo.add(variable_count - 1, variable_count - 1, 0.0)
    def square(terms: dict[int, float], target: float) -> None:
        # penalty * (sum(c_i*x_i)-target)^2, omitting constant target^2
        for i, c in terms.items():
            qubo.add(i, i, penalty * (c*c - 2*target*c))
        items = list(terms.items())
        for a, (i, ci) in enumerate(items):
            for j, cj in items[a+1:]:
                qubo.add(i, j, 2*penalty*ci*cj)
    for v in range(k):
        for t in range(m):
            square({slot(v, t, i): 1 for i in range(m+1)}, 1)
            if t < m - 1:
                for i in range(1, m+1):
                    qubo.add(slot(v, t, 0), slot(v, t+1, i), penalty)
            for i in range(m+1):
                if t == 0:
                    qubo.add(slot(v, t, i), slot(v, t, i), problem.distance_matrix[0, i])
                if t == m - 1:
                    qubo.add(slot(v, t, i), slot(v, t, i), problem.distance_matrix[i, 0])
                if t < m - 1:
                    for j in range(m+1):
                        qubo.add(slot(v, t, i), slot(v, t+1, j), problem.distance_matrix[i, j])
        load = {slot(v, t, i): float(problem.demands[i]) for t in range(m) for i in range(1, m+1)}
        load.update({slack(v, b): float(1 << b) for b in range(slack_bits)})
        square(load, problem.capacity)
    for i in range(1, m+1):
        square({slot(v, t, i): 1 for v in range(k) for t in range(m)}, 1)
    return qubo, {"slot_count": slot_count, "slack_bits_per_vehicle": slack_bits,
                  "variable_count": variable_count, "penalty": penalty, "constant_offset": penalty*(k*m + m + k*problem.capacity**2)}


def encode_cvrp_routes(routes: list[list[int]], problem: CVRPInstance) -> np.ndarray:
    if not is_feasible_vrp(routes, problem):
        raise ValueError("infeasible routes")
    _, meta = build_cvrp_qubo(problem)
    m, bits = problem.size, meta["slack_bits_per_vehicle"]
    x = np.zeros(meta["variable_count"], dtype=int)
    for v in range(2):
        customers = routes[v][1:-1] if v < len(routes) else []
        for t in range(m):
            i = customers[t] if t < len(customers) else 0
            x[(v*m+t)*(m+1)+i] = 1
        slack = problem.capacity - sum(int(problem.demands[i]) for i in customers)
        for b in range(bits):
            x[meta["slot_count"] + v*bits + b] = (slack >> b) & 1
    return x


def decode_cvrp_sample(sample: np.ndarray, problem: CVRPInstance) -> list[list[int]]:
    m = problem.size
    routes = []
    for v in range(2):
        slots = [np.flatnonzero(sample[(v*m+t)*(m+1):(v*m+t+1)*(m+1)]) for t in range(m)]
        if any(len(s) != 1 for s in slots):
            return []
        nodes = [int(s[0]) for s in slots]
        if any(nodes[t] == 0 and any(x != 0 for x in nodes[t+1:]) for t in range(m)):
            return []
        if any(nodes):
            routes.append([0] + [i for i in nodes if i != 0] + [0])
    return routes


class QuboSACVRPSolver:
    name = "qubo_sa"

    def __init__(self, num_sweeps: int = 100, num_reads: int = 1,
                 schedule: str = "coefficient_scaled_linear"):
        self.num_sweeps, self.num_reads = num_sweeps, num_reads
        self.schedule = schedule

    def solve(self, problem: CVRPInstance, time_limit: float | None = None, seed: int | None = None,
              budget_mode: str = "iterations") -> Solution:
        start = perf_counter()
        qubo, meta = build_cvrp_qubo(problem)
        remaining = None if time_limit is None else max(1e-9, time_limit - (perf_counter() - start))
        result = SimulatedAnnealingSolver(self.num_reads, self.num_sweeps, seed=seed,
                                          schedule=self.schedule, schedule_scale=meta["penalty"]
                                          if self.schedule == "penalty_scaled_geometric" else None).solve(
            qubo, time_limit=remaining, budget_mode=budget_mode)
        routes = decode_cvrp_sample(result.best_sample, problem)
        feasible = is_feasible_vrp(routes, problem)
        return Solution([], routes_distance(routes, problem) if feasible else None, feasible,
                        perf_counter()-start, self.name,
                        {**meta, "attempts": result.flips_attempted, "seed": seed,
                         "num_sweeps": self.num_sweeps, "num_reads": self.num_reads,
                         "budget_mode": budget_mode, "schedule": self.schedule,
                         "qubo_energy": result.best_energy}, routes)
