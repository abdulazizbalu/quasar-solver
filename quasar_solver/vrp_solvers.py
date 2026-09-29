"""Optional OR-Tools references and a classical route-structure annealer."""
from __future__ import annotations

import math
from time import perf_counter
from typing import Literal

import numpy as np

from quasar_solver.tsp_solver import Solution
from quasar_solver.vrp import CVRPInstance, VRPTWInstance, is_feasible_vrp, routes_distance


def _solution(name: str, routes: list[list[int]], problem: CVRPInstance, start: float,
              metadata: dict) -> Solution:
    feasible = is_feasible_vrp(routes, problem)
    return Solution([], routes_distance(routes, problem) if feasible else None, feasible,
                    perf_counter() - start, name, metadata, routes)


class ORToolsVRPSolver:
    name = "ortools"

    def solve(self, problem: CVRPInstance, time_limit: float | None = 5.0, seed: int | None = None,
              budget_mode: Literal["iterations", "time"] = "time") -> Solution:
        from ortools.constraint_solver import pywrapcp, routing_enums_pb2

        start = perf_counter()
        if time_limit is None or time_limit <= 0:
            raise ValueError("ortools requires a positive time_limit")
        vehicles = problem.num_vehicles or problem.size
        manager = pywrapcp.RoutingIndexManager(problem.size + 1, vehicles, 0)
        model = pywrapcp.RoutingModel(manager)
        # OR-Tools uses integer arc costs. Quantization is recorded and the
        # returned route is independently evaluated at original precision.
        scale = 10 if isinstance(problem, VRPTWInstance) else 1
        def distance(a: int, b: int) -> int:
            return int(math.ceil(float(problem.distance_matrix[manager.IndexToNode(a), manager.IndexToNode(b)]) * scale - 1e-10))
        distance_idx = model.RegisterTransitCallback(distance)
        model.SetArcCostEvaluatorOfAllVehicles(distance_idx)
        if isinstance(problem, VRPTWInstance):
            # Solomon comparisons are lexicographic: vehicles, then distance.
            model.SetFixedCostOfAllVehicles(1_000_000 * scale)
        def demand(a: int) -> int:
            return int(problem.demands[manager.IndexToNode(a)])
        demand_idx = model.RegisterUnaryTransitCallback(demand)
        model.AddDimensionWithVehicleCapacity(demand_idx, 0, [problem.capacity] * vehicles, True, "Capacity")
        if isinstance(problem, VRPTWInstance):
            def transit(a: int, b: int) -> int:
                i, j = manager.IndexToNode(a), manager.IndexToNode(b)
                value = problem.service_times[i] + problem.travel_time_matrix[i, j]
                return int(math.ceil(float(value) * scale - 1e-10))
            transit_idx = model.RegisterTransitCallback(transit)
            horizon = int(math.ceil(float(problem.time_windows[0, 1]) * scale))
            model.AddDimension(transit_idx, horizon, horizon, False, "Time")
            dimension = model.GetDimensionOrDie("Time")
            for node in range(1, problem.size + 1):
                lo, hi = problem.time_windows[node]
                dimension.CumulVar(manager.NodeToIndex(node)).SetRange(int(math.ceil(lo * scale)), int(math.floor(hi * scale)))
            for vehicle in range(vehicles):
                lo, hi = problem.time_windows[0]
                dimension.CumulVar(model.Start(vehicle)).SetRange(int(math.ceil(lo * scale)), int(math.floor(hi * scale)))
                dimension.CumulVar(model.End(vehicle)).SetRange(int(math.ceil(lo * scale)), int(math.floor(hi * scale)))
        params = pywrapcp.DefaultRoutingSearchParameters()
        params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        params.time_limit.FromMilliseconds(max(1, int(1000 * time_limit)))
        params.log_search = False
        if seed is not None and hasattr(params, "random_seed"):
            params.random_seed = int(seed)
        assignment = model.SolveWithParameters(params)
        routes: list[list[int]] = []
        if assignment:
            for vehicle in range(vehicles):
                index = model.Start(vehicle)
                route = [0]
                while not model.IsEnd(index):
                    index = assignment.Value(model.NextVar(index))
                    if not model.IsEnd(index):
                        route.append(manager.IndexToNode(index))
                if len(route) > 1:
                    routes.append(route + [0])
        return _solution(self.name, routes, problem, start,
                         {"seed": seed, "time_limit_seconds": time_limit, "integer_scale": scale,
                          "search": "guided_local_search", "status": int(model.status())})


class ExactSmallCVRPSolver:
    name = "exact_small"

    def solve(self, problem: CVRPInstance, time_limit: float | None = 30.0, seed: int | None = None,
              budget_mode: Literal["iterations", "time"] = "time") -> Solution:
        from ortools.sat.python import cp_model

        if isinstance(problem, VRPTWInstance) or problem.size > 10:
            raise ValueError("exact_small supports CVRP with at most 10 customers")
        start = perf_counter()
        n, k = problem.size, problem.num_vehicles or problem.size
        # Integer arc costs are essential for an exact certificate.
        if not np.allclose(problem.distance_matrix, np.rint(problem.distance_matrix)):
            raise ValueError("exact_small requires integer distances")
        model = cp_model.CpModel()
        x = {}
        for v in range(k):
            arcs = []
            for i in range(n + 1):
                for j in range(n + 1):
                    bit = model.NewBoolVar(f"x_{v}_{i}_{j}")
                    x[v, i, j] = bit
                    arcs.append((i, j, bit))
            model.AddCircuit(arcs)
            # Depot can be skipped only when every customer is skipped.
            for i in range(1, n + 1):
                model.Add(x[v, 0, 0] <= x[v, i, i])
            model.Add(x[v, 0, 0] >= sum(x[v, i, i] for i in range(1, n + 1)) - (n - 1))
            model.Add(sum(int(problem.demands[i]) * (1 - x[v, i, i]) for i in range(1, n + 1)) <= problem.capacity)
        for i in range(1, n + 1):
            model.Add(sum(1 - x[v, i, i] for v in range(k)) == 1)
        model.Minimize(sum(int(round(problem.distance_matrix[i, j])) * bit
                           for (v, i, j), bit in x.items() if i != j))
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_limit or 30.0
        solver.parameters.num_search_workers = 1
        solver.parameters.random_seed = seed or 0
        status = solver.Solve(model)
        routes = []
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            for v in range(k):
                next_node = {i: j for i in range(n + 1) for j in range(n + 1)
                             if (v, i, j) in x and i != j and solver.BooleanValue(x[v, i, j])}
                if 0 not in next_node:
                    continue
                route, at = [0], next_node[0]
                while at != 0:
                    route.append(at)
                    at = next_node[at]
                routes.append(route + [0])
        result = _solution(self.name, routes, problem, start,
                           {"status": solver.StatusName(status), "proven": status == cp_model.OPTIMAL,
                            "best_bound": solver.BestObjectiveBound() if status in (cp_model.OPTIMAL, cp_model.FEASIBLE) else None})
        return result


class VRPSASolver:
    name = "vrp_sa"

    def __init__(self, attempts_per_customer: int = 100):
        if attempts_per_customer <= 0:
            raise ValueError("attempts_per_customer must be positive")
        self.attempts_per_customer = attempts_per_customer

    def solve(self, problem: CVRPInstance, time_limit: float | None = None, seed: int | None = None,
              budget_mode: Literal["iterations", "time"] = "iterations") -> Solution:
        if budget_mode not in ("iterations", "time") or (budget_mode == "time" and not time_limit):
            raise ValueError("invalid budget_mode/time_limit")
        start = perf_counter()
        rng = np.random.default_rng(seed)
        # A randomized, valid insertion builds the starting state.
        routes: list[list[int]] = []
        for customer in rng.permutation(np.arange(1, problem.size + 1)):
            options = []
            for r in range(len(routes) + (problem.num_vehicles is None or len(routes) < problem.num_vehicles)):
                old = routes[r] if r < len(routes) else [0, 0]
                for pos in range(1, len(old)):
                    candidate = old[:pos] + [int(customer)] + old[pos:]
                    trial = routes[:r] + [candidate] + routes[r + 1:] if r < len(routes) else routes + [candidate]
                    # Check only capacity/windows until all customers are placed.
                    if _partial_feasible(trial, problem):
                        options.append((routes_distance_partial(trial, problem), trial))
            if not options:
                return _solution(self.name, [], problem, start, {"status": "construction_failed", "seed": seed})
            minimum = min(value for value, _ in options)
            elite = [trial for value, trial in options if value <= minimum * 1.15 + 1e-9]
            routes = elite[int(rng.integers(len(elite)))]
        best = [r[:] for r in routes]
        energy = _score(routes, problem)
        best_energy = energy
        attempts = 0
        budget = self.attempts_per_customer * problem.size
        while (attempts < budget if budget_mode == "iterations" else True):
            if time_limit is not None and perf_counter() - start >= time_limit:
                break
            trial = [r[:] for r in routes]
            move = int(rng.integers(3))
            if move == 0:  # relocate
                a = int(rng.integers(len(trial)))
                pos = int(rng.integers(1, len(trial[a]) - 1))
                node = trial[a].pop(pos)
                if len(trial[a]) == 2:
                    trial.pop(a)
                b = int(rng.integers(len(trial) + (problem.num_vehicles is None or len(trial) < problem.num_vehicles)))
                if b == len(trial):
                    trial.append([0, node, 0])
                else:
                    trial[b].insert(int(rng.integers(1, len(trial[b]))), node)
            elif move == 1:  # swap
                a, b = rng.integers(len(trial), size=2)
                i, j = int(rng.integers(1, len(trial[a]) - 1)), int(rng.integers(1, len(trial[b]) - 1))
                trial[a][i], trial[b][j] = trial[b][j], trial[a][i]
            else:  # intra-route 2-opt
                a = int(rng.integers(len(trial)))
                if len(trial[a]) <= 4:
                    attempts += 1
                    continue
                i, j = sorted(int(x) for x in rng.choice(np.arange(1, len(trial[a]) - 1), 2, replace=False))
                trial[a][i:j + 1] = reversed(trial[a][i:j + 1])
            attempts += 1
            if not is_feasible_vrp(trial, problem):
                continue
            trial_energy = _score(trial, problem)
            beta = 0.1 + 9.9 * min(1.0, attempts / budget)
            scale = max(1.0, float(problem.distance_matrix.max()))
            if trial_energy <= energy or rng.random() < math.exp(-(trial_energy - energy) * beta / scale):
                routes, energy = trial, trial_energy
                if energy < best_energy:
                    best, best_energy = [r[:] for r in routes], energy
        return _solution(self.name, best, problem, start,
                         {"seed": seed, "attempts": attempts, "attempts_per_customer": self.attempts_per_customer,
                          "budget_mode": budget_mode, "time_limit_seconds": time_limit})


def routes_distance_partial(routes: list[list[int]], problem: CVRPInstance) -> float:
    return float(sum(problem.distance_matrix[a, b] for route in routes for a, b in zip(route, route[1:])))


def _score(routes: list[list[int]], problem: CVRPInstance) -> float:
    return routes_distance(routes, problem) + (1_000_000 * len(routes) if isinstance(problem, VRPTWInstance) else 0)


def _partial_feasible(routes: list[list[int]], problem: CVRPInstance) -> bool:
    if problem.num_vehicles is not None and len(routes) > problem.num_vehicles:
        return False
    for route in routes:
        if sum(problem.demands[x] for x in route[1:-1]) > problem.capacity:
            return False
        if isinstance(problem, VRPTWInstance):
            t = problem.time_windows[0, 0]
            for a, b in zip(route, route[1:]):
                t = max(t + problem.service_times[a] + problem.travel_time_matrix[a, b], problem.time_windows[b, 0])
                if t > problem.time_windows[b, 1] + 1e-9:
                    return False
    return True
