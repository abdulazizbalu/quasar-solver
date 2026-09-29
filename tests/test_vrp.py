from pathlib import Path

import numpy as np
import pytest

from quasar_solver.vrp import CVRPInstance, VRPTWInstance, check_vrp_routes, is_feasible_vrp, routes_distance
from quasar_solver.vrp_parsers import parse_cvrplib, parse_cvrplib_solution, parse_solomon
from quasar_solver.vrp_qubo import build_cvrp_qubo, decode_cvrp_sample, encode_cvrp_routes, QuboSACVRPSolver
from quasar_solver.vrp_solvers import ExactSmallCVRPSolver, ORToolsVRPSolver, VRPSASolver


@pytest.fixture
def tiny():
    return CVRPInstance("tiny", np.array([[0, 1, 2], [1, 0, 1], [2, 1, 0]]),
                        np.array([0, 1, 1]), 2, 2)


def test_checker_catches_broken_routes(tiny):
    assert is_feasible_vrp([[0, 1, 2, 0]], tiny)
    for routes in ([[0, 1, 0]], [[0, 1, 1, 2, 0]], [[1, 2, 0]], [[0, 1, 0], [0, 2, 0], [0, 0, 0]]):
        assert not is_feasible_vrp(routes, tiny)
    p = CVRPInstance("cap", tiny.distance_matrix, [0, 2, 2], 2, 2)
    assert check_vrp_routes([[0, 1, 2, 0]], p)[1] == "capacity exceeded"
    tw = VRPTWInstance("tw", tiny.distance_matrix, tiny.demands, 2, 2,
                       time_windows=[[0, 10], [0, 1], [0, 2]], service_times=[0, 1, 0])
    assert not is_feasible_vrp([[0, 1, 2, 0]], tw)
    assert is_feasible_vrp([[0, 1, 0], [0, 2, 0]], tw)


def test_qubo_hand_checked_energy(tiny):
    routes = [[0, 1, 2, 0]]
    q, info = build_cvrp_qubo(tiny)
    x = encode_cvrp_routes(routes, tiny)
    assert info["variable_count"] == 16
    assert decode_cvrp_sample(x, tiny) == routes
    assert q.energy(x) + info["constant_offset"] == routes_distance(routes, tiny) == 4
    assert q.energy(x) < q.energy(np.zeros_like(x))
    with pytest.raises(ValueError, match="at most six"):
        build_cvrp_qubo(CVRPInstance("large", np.zeros((8, 8)), [0] + [1]*7, 4, 2))


def test_all_solvers_tiny(tiny):
    for solver in [ExactSmallCVRPSolver(), ORToolsVRPSolver(), VRPSASolver(), QuboSACVRPSolver(100, 2)]:
        result = solver.solve(tiny, time_limit=2, seed=3)
        assert result.routes is not None
        assert result.feasible == is_feasible_vrp(result.routes, tiny)
        if solver.name != "qubo_sa":
            assert result.feasible
        if solver.name == "exact_small":
            assert result.metadata["proven"] and result.objective == 4


def test_parsers(tmp_path: Path):
    vrp = tmp_path / "A-n3-k2.vrp"
    vrp.write_text("NAME : A-n3-k2\nTYPE : CVRP\nDIMENSION : 3\nEDGE_WEIGHT_TYPE : EUC_2D\nCAPACITY : 2\nNODE_COORD_SECTION\n1 0 0\n2 1 0\n3 2 0\nDEMAND_SECTION\n1 0\n2 1\n3 1\nDEPOT_SECTION\n1\n-1\nEOF\n")
    p = parse_cvrplib(vrp)
    assert p.size == 2 and p.num_vehicles == 2 and p.distance_matrix[0, 2] == 2
    sol = tmp_path / "x.sol"
    sol.write_text("Route #1: 1 2\nCost 4\n")
    assert parse_cvrplib_solution(sol) == ([[0, 1, 2, 0]], 4)
    txt = tmp_path / "C101.txt"
    txt.write_text("C101\nVEHICLE\nNUMBER CAPACITY\n2 2\nCUSTOMER\n0 0 0 0 0 10 0\n1 1 0 1 0 10 0\n2 2 0 1 0 10 0\n")
    assert parse_solomon(txt, 2).size == 2
    # Reference convention truncates Euclidean arc costs to one decimal.
    txt.write_text(txt.read_text().replace("2 2 0 1", "2 2 1 1"))
    assert parse_solomon(txt, 2).distance_matrix[0, 2] == 2.2


def test_benchmark_seed_separation_and_summary():
    from benchmarks.run_vrp_benchmarks import tiny_instance, summarize
    a = tiny_instance(4, 10)
    b = tiny_instance(4, 11)
    assert not np.array_equal(a.distance_matrix, b.distance_matrix)
    rows = [dict(group="tiny", size=4, instance="a", solver="vrp_sa", feasible=1,
                 gap_percent=0.0, routes=2, runtime_seconds=.1, attempts=400, variable_count=""),
            dict(group="tiny", size=4, instance="b", solver="vrp_sa", feasible=1,
                 gap_percent=10.0, routes=2, runtime_seconds=.2, attempts=400, variable_count="")]
    summary = summarize(rows)
    assert "5.00%" in summary and "2/2" in summary
