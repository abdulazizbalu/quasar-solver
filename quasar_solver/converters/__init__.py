"""Converters from common optimization problems to QUBO."""

from quasar_solver.converters.tsp import decode_tsp, tsp_to_qubo

__all__ = ["decode_tsp", "tsp_to_qubo"]
