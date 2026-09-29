"""Parsers for CVRPLIB EUC_2D and Solomon text files."""
from __future__ import annotations

from pathlib import Path
import re

import numpy as np

from quasar_solver.vrp import CVRPInstance, VRPTWInstance


def parse_cvrplib(path: str | Path) -> CVRPInstance:
    lines = Path(path).read_text().splitlines()
    fields: dict[str, str] = {}
    sections: dict[str, list[str]] = {}
    section = ""
    for raw in lines:
        line = raw.strip()
        if not line or line == "EOF":
            continue
        if line.endswith("_SECTION"):
            section = line
            sections[section] = []
        elif section:
            sections[section].append(line)
        else:
            match = re.match(r"([A-Z_]+)\s*:?\s*(.*)", line)
            if match:
                fields[match[1]] = match[2]
    if fields.get("EDGE_WEIGHT_TYPE") != "EUC_2D":
        raise ValueError("only CVRPLIB EUC_2D is supported")
    n = int(fields["DIMENSION"])
    depot = [int(x) for row in sections["DEPOT_SECTION"] for x in row.split() if int(x) > 0]
    if depot != [1]:
        raise ValueError("only depot node 1 is supported")
    coords = np.zeros((n, 2), dtype=float)
    demands = np.zeros(n, dtype=int)
    coord_ids, demand_ids = set(), set()
    for line in sections["NODE_COORD_SECTION"]:
        i, x, y = line.split()
        j = int(i) - 1
        coords[j] = float(x), float(y)
        coord_ids.add(j)
    for line in sections["DEMAND_SECTION"]:
        i, q = line.split()
        j = int(i) - 1
        demands[j] = int(q)
        demand_ids.add(j)
    if coord_ids != set(range(n)) or demand_ids != set(range(n)):
        raise ValueError("missing or duplicate node data")
    euclidean = np.linalg.norm(coords[:, None, :] - coords[None, :, :], axis=2)
    distance = np.floor(euclidean + 0.5)  # TSPLIB EUC_2D, not Python's ties-to-even round
    name = fields.get("NAME", Path(path).stem)
    vehicles = re.search(r"-k(\d+)$", name)
    return CVRPInstance(name, distance, demands, int(fields["CAPACITY"]),
                        int(vehicles[1]) if vehicles else None)


def parse_cvrplib_solution(path: str | Path) -> tuple[list[list[int]], float | None]:
    routes: list[list[int]] = []
    objective = None
    for line in Path(path).read_text().splitlines():
        if line.startswith("Route #"):
            routes.append([0] + [int(x) for x in line.split(":", 1)[1].split()] + [0])
        elif line.startswith("Cost"):
            objective = float(line.split()[-1])
    if not routes:
        raise ValueError("no routes in solution")
    return routes, objective


def parse_solomon(path: str | Path, customers: int = 25) -> VRPTWInstance:
    """Read Solomon's 100-customer format, optionally taking the first 25."""
    text = Path(path).read_text()
    name = text.splitlines()[0].strip()
    vehicle_match = re.search(r"VEHICLE\s+NUMBER\s+CAPACITY\s+(\d+)\s+(\d+)", text, re.I)
    if vehicle_match is None:
        raise ValueError("missing vehicle section")
    count, capacity = map(int, vehicle_match.groups())
    rows: list[list[float]] = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) == 7 and all(re.fullmatch(r"-?\d+(?:\.\d+)?", x) for x in parts):
            rows.append([float(x) for x in parts])
    if len(rows) < customers + 1 or [int(x[0]) for x in rows[:customers + 1]] != list(range(customers + 1)):
        raise ValueError("missing Solomon customer rows")
    data = np.asarray(rows[:customers + 1])
    coords = data[:, 1:3]
    # Published 25-customer Solomon references truncate travel to one decimal.
    distance = np.floor(np.linalg.norm(coords[:, None, :] - coords[None, :, :], axis=2) * 10 + 1e-10) / 10
    return VRPTWInstance(f"{name}-{customers}", distance, data[:, 3].astype(int), capacity,
                         count, time_windows=data[:, 4:6], service_times=data[:, 6])
