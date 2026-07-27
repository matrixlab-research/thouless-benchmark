#!/usr/bin/env python3
"""Validate a repeated domain correctness and performance record."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    parser.add_argument(
        "--current",
        action="store_true",
        help="require an exact snapshot of the current implementation manifest",
    )
    args = parser.parse_args()
    payload = json.loads(args.result.read_text())
    records = payload["records"]
    if payload["summary"]["backend_case_records"] != len(records):
        raise ValueError("domain result summary count does not match its records")
    keys = [(record["backend"], record["case_id"]) for record in records]
    if len(keys) != len(set(keys)):
        raise ValueError("domain result contains a duplicate backend-case record")
    implementations = json.loads(
        (ROOT / "benchmark" / "domain_implementation.json").read_text()
    )["implemented"]
    current = {
        (backend, case_id)
        for backend, case_ids in implementations.items()
        for case_id in case_ids
    }
    if not set(keys) <= current:
        raise ValueError("domain result names a case outside the implementation manifest")
    if args.current and set(keys) != current:
        missing = sorted(current - set(keys))
        extra = sorted(set(keys) - current)
        raise ValueError(
            f"domain result is not the current complete snapshot; missing={missing}, extra={extra}"
        )
    if any(record["representative_result"]["status"] != "passed" for record in records):
        raise ValueError("a representative domain result failed")
    if any(record["repetitions"] < 3 for record in records):
        raise ValueError("domain performance records require at least three repetitions")
    if any(record["kernel_seconds"]["median"] <= 0.0 for record in records):
        raise ValueError("kernel timing must be positive")
    if any(record["process_wall_seconds"]["median"] <= 0.0 for record in records):
        raise ValueError("wall timing must be positive")
    cases = {
        case["id"]: case
        for case in json.loads(
            (ROOT / "benchmark" / "domain_cases.json").read_text()
        )["cases"]
    }
    for record in records:
        case = cases[record["case_id"]]
        available_checks = {
            check["name"]
            for check in record["representative_result"]["checks"]
            if check["passed"]
        }
        required_checks = {
            check
            for checks in case["question_gates"].values()
            for check in checks
        }
        if not required_checks <= available_checks:
            missing = sorted(required_checks - available_checks)
            raise ValueError(
                f"{record['backend']}/{record['case_id']} lacks passing question gates: {missing}"
            )
    qualifier = " current" if args.current else ""
    print(
        f"domain result validation passed:{qualifier} "
        f"{len(records)} backend-case records"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
