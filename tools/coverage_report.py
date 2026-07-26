#!/usr/bin/env python3
"""Print implemented, applicable, and gap counts without conflating them."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    manifest = json.loads((ROOT / "benchmark" / "cases.json").read_text())
    status = json.loads((ROOT / "benchmark" / "implementation.json").read_text())
    cases = manifest["cases"]
    for backend in ("thouless", "pythtb", "kwant"):
        applicable = {case["id"] for case in cases if backend in case["backends"]}
        implemented = set(status["implemented"][backend])
        gaps = sorted(applicable - implemented)
        print(f"{backend}: {len(implemented)}/{len(applicable)} implemented; {len(gaps)} gaps")
        for case_id in gaps:
            print(f"  - {case_id}")


if __name__ == "__main__":
    main()
