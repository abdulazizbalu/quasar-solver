"""Compare published TSP benchmark outcomes with a fresh default-schedule run."""
from __future__ import annotations

import csv
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BASELINE = ROOT / "benchmarks" / "results" / "raw.csv"
RERUN = ROOT / "benchmarks" / "results" / "tsp_schedule_verification" / "results" / "raw.csv"
OUTPUT = ROOT / "benchmarks" / "results" / "tsp_schedule_verification.md"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def main() -> str:
    old, new = read(BASELINE), read(RERUN)
    rows = ["# Historical TSP schedule verification", "",
            "The default remains `coefficient_scaled_linear`, preserving the schedule used for the published TSP table. This fresh run used the same benchmark design and seeds. Feasibility, objective, and gap were compared run-by-run; measured runtime is included as a diagnostic because it varies with machine load.", "",
            "| Cities | Solver | Outcomes identical (100 runs) | Published mean runtime | Rerun mean runtime |", "| ---: | --- | --- | ---: | ---: |"]
    for size in (6, 10, 15, 20):
        for solver in ("qubo_sa", "qubo_sa_swap", "two_opt"):
            a = [r for r in old if int(r["size"]) == size and r["solver"] == solver]
            b = [r for r in new if int(r["size"]) == size and r["solver"] == solver]
            same = len(a) == len(b) == 100 and all(
                x["feasible"] == y["feasible"] and x["objective"] == y["objective"]
                and x["gap_percent"] == y["gap_percent"] for x, y in zip(a, b))
            if not same:
                raise AssertionError(f"TSP outcomes changed for n={size}, {solver}")
            mean_a = statistics.mean(float(r["runtime_seconds"]) for r in a)
            mean_b = statistics.mean(float(r["runtime_seconds"]) for r in b)
            rows.append(f"| {size} | {solver} | yes | {mean_a:.4f} s | {mean_b:.4f} s |")
    report = "\n".join(rows) + "\n"
    OUTPUT.write_text(report, encoding="utf-8")
    return report


if __name__ == "__main__":
    print(main())
