"""Run a small TSP routing demo with simulated annealing."""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np

from quasar_solver.converters.tsp import decode_tsp, tsp_to_qubo
from quasar_solver.solver import SimulatedAnnealingSolver

_DEMO_DIR = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(_DEMO_DIR / ".matplotlib-cache"))
os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib.pyplot as plt


def main() -> None:
    """Build, solve, and plot a seeded six-city routing example."""
    rng = np.random.default_rng(42)
    n = 6

    raw_distances = rng.integers(10, 101, size=(n, n))
    distances = np.triu(raw_distances, 1)
    distances = distances + distances.T
    np.fill_diagonal(distances, 0)

    print("Distance matrix:")
    print(distances)

    qubo = tsp_to_qubo(distances)
    solver = SimulatedAnnealingSolver(num_reads=200, num_sweeps=2000, seed=42)
    result = solver.solve(qubo)
    tour = decode_tsp(result.best_sample, n)

    print(f"Best energy: {result.best_energy}")
    print(f"Decoded tour: {tour}")

    if tour:
        total_distance = tour_distance(distances, tour)
        print(f"Total tour distance: {total_distance}")
    else:
        print("Warning: best sample did not decode to a valid TSP tour.")

    coords = rng.random((n, 2))
    plot_tour(coords, tour, _DEMO_DIR / "tour.png")


def tour_distance(distances: np.ndarray, tour: list[int]) -> float:
    """Return the wrapped distance of a decoded tour."""
    total = 0.0
    for index, city in enumerate(tour):
        next_city = tour[(index + 1) % len(tour)]
        total += distances[city, next_city]
    return float(total)


def plot_tour(coords: np.ndarray, tour: list[int], output_path: Path) -> None:
    """Save a plot of city points and the decoded tour, if one is available."""
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(coords[:, 0], coords[:, 1], s=80, color="#1f77b4")

    for city, (x_coord, y_coord) in enumerate(coords):
        ax.annotate(str(city), (x_coord, y_coord), xytext=(6, 6), textcoords="offset points")

    if tour:
        ordered = coords[tour + [tour[0]]]
        ax.plot(ordered[:, 0], ordered[:, 1], color="#d62728", linewidth=2)

    ax.set_title("Quasar Solver TSP Demo")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
