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
    domain = json.loads(
        (ROOT / "benchmark" / "problem_coverage.json").read_text()
    )["summary"]
    print("whole-problem domain coverage:")
    for backend in ("thouless", "pythtb", "kwant"):
        item = domain[backend]
        print(
            f"{backend}: {item['implemented']}/100 implemented; "
            f"{item['implementable_unverified']} implementable but unverified; "
            f"{item['missing_capability']} missing capability; "
            f"{item['not_applicable']} not applicable"
        )


if __name__ == "__main__":
    main()
