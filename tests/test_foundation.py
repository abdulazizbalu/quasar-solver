import csv

import numpy as np
import pytest

from benchmarks.run_benchmarks import make_instance, run_benchmarks
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
    assert a.route == b.route and a.objective == b.objective and a.feasible == b.feasible
    assert a.feasible == is_feasible_tsp(a.route, problem)


def test_benchmark_output(tmp_path):
    output = tmp_path / "results"
    summary = run_benchmarks(sizes=(6,), seeds=range(2), output_dir=output,
                             solver=QuboSASolver(num_reads=1, num_sweeps=20))
    with (output / "raw.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2 and summary[0]["runs"] == 2
    assert "Best known is" in (output / "summary.md").read_text(encoding="utf-8")
