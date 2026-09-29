"""Quasar Solver: a small quantum-inspired QUBO optimization toolkit."""

from quasar_solver.qubo import QUBO
from quasar_solver.solver import SimulatedAnnealingSolver, SolverResult
from quasar_solver.problem import Problem, TSPInstance, is_feasible_tsp, tour_length
from quasar_solver.tsp_solver import Solver, Solution, QuboSASolver
from quasar_solver.swap_solver import QuboSASwapSolver
from quasar_solver.vrp import CVRPInstance, VRPTWInstance, is_feasible_vrp, check_vrp_routes, routes_distance
from quasar_solver.vrp_solvers import ORToolsVRPSolver, ExactSmallCVRPSolver, VRPSASolver
from quasar_solver.vrp_qubo import QuboSACVRPSolver

__all__ = ["QUBO", "SimulatedAnnealingSolver", "SolverResult", "Problem", "TSPInstance", "is_feasible_tsp", "tour_length", "Solver", "Solution", "QuboSASolver", "QuboSASwapSolver"]
__all__ += ["CVRPInstance", "VRPTWInstance", "is_feasible_vrp", "check_vrp_routes", "routes_distance",
            "ORToolsVRPSolver", "ExactSmallCVRPSolver", "VRPSASolver", "QuboSACVRPSolver"]
