import csv
from itertools import permutations

import numpy as np
import pytest

from benchmarks.run_benchmarks import (
    _paired_permutation_p, held_karp, make_instance, regenerate_reports,
    run_benchmarks, two_opt,
)
from quasar_solver import QuboSASolver, TSPInstance, is_feasible_tsp, tour_length
from quasar_solver.qubo import QUBO
from quasar_solver.solver import SimulatedAnnealingSolver


def test_problem_and_checker():
    problem = TSPInstance("square", coordinates=np.array([[0, 0], [1, 0], [1, 1], [0, 1]]), known_optimum=4)
    assert problem.size == 4
    assert is_feasible_tsp([0, 1, 2, 3], problem)
    assert tour_length([0, 1, 2, 3], problem) == 4
    assert not is_feasible_tsp([0, 1, 1, 3], problem)
    assert not is_feasible_tsp([0, 1, 2, 4], problem)
    with pytest.raises(ValueError):
        tour_length([0, 1, 1, 3], problem)


def test_sweep_is_one_flip_per_variable_and_budget_is_explicit():
    qubo = QUBO()
    for index in range(4):
        qubo.add(index, index, 1.0)
    result = SimulatedAnnealingSolver(num_reads=2, num_sweeps=3, seed=1).solve(qubo)
    assert result.flips_attempted == 2 * 3 * 4
    assert result.sweeps_completed == 2 * 3
    assert QuboSASolver().num_sweeps >= 100


def test_scaled_penalties_change_matrix_and_temperature_tracks_scale():
    problem = make_instance(6, 8041)
    low = QuboSASolver(penalty_alpha=1)
    high = QuboSASolver(penalty_alpha=10)
    low_qubo, low_penalty = low.build_qubo(problem)
    high_qubo, high_penalty = high.build_qubo(problem)
    assert low_penalty != high_penalty
    assert not np.array_equal(low_qubo.to_matrix(), high_qubo.to_matrix())

    result = SimulatedAnnealingSolver(num_reads=1, num_sweeps=100, seed=2).solve(high_qubo)
    assert result.effective_beta_start * result.coefficient_scale == pytest.approx(0.1)
    assert result.effective_beta_end * result.coefficient_scale == pytest.approx(10.0)


def test_solver_adapter_repeatability_and_default_penalty():
    problem = make_instance(6, 71)
    solver = QuboSASolver(num_reads=1, num_sweeps=100)
    a, b = solver.solve(problem, seed=7), solver.solve(problem, seed=7)
    assert a.solver_name == "qubo_sa" and a.runtime >= 0
    assert a.metadata["penalty"] == pytest.approx(problem.distance_matrix.max())
    assert a.metadata["budget_mode"] == "iterations"
    assert a.metadata["flips_attempted"] == 100 * problem.size**2
    assert a.route == b.route and a.objective == b.objective and a.feasible == b.feasible
    assert a.feasible == is_feasible_tsp(a.route, problem)


def test_held_karp_matches_brute_force():
    problem = make_instance(6, 123)
    route, optimum = held_karp(problem)
    brute = min(tour_length((0,) + p, problem) for p in permutations(range(1, 6)))
    assert is_feasible_tsp(route, problem)
    assert optimum == pytest.approx(brute)


def test_two_opt_uses_same_move_evaluation_budget():
    problem = make_instance(6, 992)
    budget = 100 * problem.size**2
    result = two_opt(problem, budget, seed=3)
    assert result.solver_name == "two_opt" and result.feasible
    assert result.metadata["evaluations"] == budget


def test_paired_gap_test_uses_independent_instances():
    # Three consistently positive instance differences have 2/8 two-sided tails.
    assert _paired_permutation_p([1.0, 2.0, 3.0], seed=0) == pytest.approx(0.25)


def test_benchmark_uses_separate_paired_seeds_and_writes_artifacts(tmp_path):
    output = tmp_path / "benchmarks" / "results"
    summaries = run_benchmarks(sizes=(6,), instance_seeds=(301, 302),
                               solver_seeds=(4, 9), output_dir=output,
                               alphas=(1, 10), num_sweeps=100, num_reads=1)
    with (output / "raw.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 16  # two instances × two solver seeds × four methods/configurations
    assert {row["instance_seed"] for row in rows} == {"301", "302"}
    assert {row["solver_seed"] for row in rows} == {"4", "9"}
    assert all(row["reference_status"] == "proven optimum" for row in rows)
    assert all(row["flips_attempted"] in ("", str(100 * 6**2)) for row in rows)
    assert summaries and (output / "paired_tests.csv").exists()
    assert "95%" in (output / "summary.md").read_text(encoding="utf-8")
    assert (tmp_path / "docs" / "tsp_benchmark.png").exists()
    assert regenerate_reports(output) == summaries
