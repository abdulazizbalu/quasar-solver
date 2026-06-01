"""Quasar Solver: a small quantum-inspired QUBO optimization toolkit."""

from quasar_solver.qubo import QUBO
from quasar_solver.solver import SimulatedAnnealingSolver, SolverResult

__all__ = ["QUBO", "SimulatedAnnealingSolver", "SolverResult"]
