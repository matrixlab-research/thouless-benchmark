#!/usr/bin/env python3
"""Validate a repeated domain correctness and performance record."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_domain_results.py RESULT.json", file=sys.stderr)
        return 2
    payload = json.loads(Path(sys.argv[1]).read_text())
    records = payload["records"]
    if payload["summary"]["backend_case_records"] != 14 or len(records) != 14:
        raise ValueError("domain result must contain 14 backend-case records")
    expected = {"thouless": 5, "pythtb": 4, "kwant": 5}
    actual = {
        backend: sum(record["backend"] == backend for record in records)
        for backend in expected
    }
    if actual != expected:
        raise ValueError(f"unexpected backend record counts: {actual}")
    if any(record["representative_result"]["status"] != "passed" for record in records):
        raise ValueError("a representative domain result failed")
    if any(record["repetitions"] < 3 for record in records):
        raise ValueError("domain performance records require at least three repetitions")
    if any(record["kernel_seconds"]["median"] <= 0.0 for record in records):
        raise ValueError("kernel timing must be positive")
    if any(record["process_wall_seconds"]["median"] <= 0.0 for record in records):
        raise ValueError("wall timing must be positive")
    print("domain result validation passed: 14 backend-case records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
