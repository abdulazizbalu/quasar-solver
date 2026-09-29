"""Download benchmark data without redistributing third-party instance files.

URLs and SHA-256 digests were pinned on 2026-09-29. The Solomon mirror is
used because the original SINTEF archive rejected automated downloads.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from urllib.request import urlopen


CVRPLIB = "https://galgos.inf.puc-rio.br/cvrplib/en/download/instance/"
SOLOMON = "https://raw.githubusercontent.com/BUAAxyf/Solomon100/23f7cf053cc7c0a7740de246791df3ece179c8df/data/solomon_100/"
FILES = {
    "A-n32-k5.vrp": (CVRPLIB + "4", "2ebedd0631c4c56c08ba3b1476ac874a7d54cc448bd3795de534f43b2c099ce2"),
    "A-n33-k5.vrp": (CVRPLIB + "5", "35712de0054a0fbfd609d5cdb4ec638c39f7c181b6e39e3c8bf6f8e359b78aef"),
    "A-n37-k5.vrp": (CVRPLIB + "10", "8b3c9c86c6ec147d6699ef1a7e9b33d7d2637c6b8f254922ff3494d56efed3d0"),
    "C101.txt": (SOLOMON + "C101.txt", "bb9cc415285b1f18ed5ba1428c1caa9e31e880c72c7561587b061266229cf077"),
    "R101.txt": (SOLOMON + "R101.txt", "6c93fc10138a643d7827da23b74b70cc09f3c5debafd58c81514b4d735d858a0"),
    "RC101.txt": (SOLOMON + "RC101.txt", "bbf8c5a3e429265d69ed711184054c83788de2f92d376b69da27c898a9a2c472"),
}


def download_all(directory: Path | None = None) -> Path:
    directory = directory or Path(__file__).parent / "data" / "vrp"
    directory.mkdir(parents=True, exist_ok=True)
    for name, (url, expected) in FILES.items():
        target = directory / name
        data = target.read_bytes() if target.exists() else urlopen(url, timeout=30).read()
        digest = hashlib.sha256(data).hexdigest()
        if digest != expected:
            raise ValueError(f"SHA-256 mismatch for {name}: {digest}")
        if not target.exists():
            target.write_bytes(data)
        print(f"{name}: {digest}")
    return directory


if __name__ == "__main__":
    download_all()
