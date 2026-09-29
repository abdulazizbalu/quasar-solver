import csv
from itertools import permutations

import numpy as np
import pytest

from benchmarks.run_benchmarks import held_karp, make_instance, run_benchmarks, two_opt
from quasar_solver import QuboSASolver, TSPInstance, is_feasible_tsp, tour_length


def test_problem_and_checker():
    problem = TSPInstance("square", coordinates=np.array([[0, 0], [1, 0], [1, 1], [0, 1]]), known_optimum=4)
    assert problem.size == 4
    assert is_feasible_tsp([0, 1, 2, 3], problem)
    assert tour_length([0, 1, 2, 3], problem) == 4
    assert not is_feasible_tsp([0, 1, 1, 3], problem)
    assert not is_feasible_tsp([0, 1, 2, 4], problem)
    with pytest.raises(ValueError):
        tour_length([0, 1, 1, 3], problem)


def test_solver_contract_and_repeatability():
    problem = make_instance(6)
    solver = QuboSASolver(num_reads=2, num_sweeps=50)
    a, b = solver.solve(problem, seed=7), solver.solve(problem, seed=7)
    assert a.solver_name == "qubo_sa" and a.runtime >= 0
    assert a.metadata["penalty"] == pytest.approx(10 * problem.distance_matrix.max())
    assert a.route == b.route and a.objective == b.objective and a.feasible == b.feasible
    assert a.feasible == is_feasible_tsp(a.route, problem)


def test_benchmark_output(tmp_path):
    output = tmp_path / "results"
    summary = run_benchmarks(sizes=(6,), seeds=range(2), time_limits=(0.01,), output_dir=output, alphas=(1,))
    with (output / "raw.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 6 and summary[0]["runs"] == 2
    assert "proven optimum" in (output / "summary.md").read_text(encoding="utf-8")


def test_held_karp_and_timed_two_opt():
    problem = make_instance(6)
    route, optimum = held_karp(problem)
    brute = min(tour_length((0,) + p, problem) for p in permutations(range(1, 6)))
    assert is_feasible_tsp(route, problem)
    assert optimum == pytest.approx(brute)
    baseline = two_opt(problem, 0.05, seed=3)
    assert baseline.solver_name == "two_opt" and baseline.feasible
    assert baseline.runtime < 0.15


def test_penalty_sweep_writes_summary_and_chart(tmp_path):
    output = tmp_path / "benchmarks" / "results"
    run_benchmarks(sizes=(6,), seeds=range(1), time_limits=(0.02,), output_dir=output, alphas=(1,))
    assert "proven optimum" in (output / "summary.md").read_text(encoding="utf-8")
    assert (tmp_path / "docs" / "tsp_benchmark.png").exists()
