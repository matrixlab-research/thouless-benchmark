#!/usr/bin/env python3
"""Validate a repeated native AD correctness and performance record."""

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
        help="require an exact snapshot of the current AD implementation manifest",
    )
    args = parser.parse_args()
    payload = json.loads(args.result.read_text())
    records = payload["records"]
    if payload["summary"]["backend_case_records"] != len(records):
        raise ValueError("AD result summary count does not match its records")
    keys = [(record["backend"], record["case_id"]) for record in records]
    if len(keys) != len(set(keys)):
        raise ValueError("AD result contains a duplicate backend-case record")

    implemented = json.loads(
        (ROOT / "benchmark" / "ad_implementation.json").read_text()
    )["implemented"]
    current = {
        (backend, case_id)
        for backend, case_ids in implemented.items()
        for case_id in case_ids
    }
    if not set(keys) <= current:
        raise ValueError("AD result names a case outside the implementation manifest")
    if args.current and set(keys) != current:
        missing = sorted(current - set(keys))
        extra = sorted(set(keys) - current)
        raise ValueError(
            f"AD result is not the current complete snapshot; "
            f"missing={missing}, extra={extra}"
        )

    if any(record["representative_result"]["status"] != "passed" for record in records):
        raise ValueError("a representative AD result failed")
    if any(record["repetitions"] < 3 for record in records):
        raise ValueError("AD performance records require at least three repetitions")
    if any(record["kernel_seconds"]["median"] <= 0.0 for record in records):
        raise ValueError("kernel timing must be positive")
    if any(record["process_wall_seconds"]["median"] <= 0.0 for record in records):
        raise ValueError("wall timing must be positive")

    cases = {
        case["id"]: case
        for case in json.loads(
            (ROOT / "benchmark" / "ad_cases.json").read_text()
        )["cases"]
    }
    for record in records:
        case = cases[record["case_id"]]
        result = record["representative_result"]
        available_checks = {
            check["name"] for check in result["checks"] if check["passed"]
        }
        required_checks = set(case["required_checks"])
        if not required_checks <= available_checks:
            missing = sorted(required_checks - available_checks)
            raise ValueError(
                f"{record['backend']}/{record['case_id']} lacks passing AD gates: "
                f"{missing}"
            )
        if result["backend_version"] != "237f544c497e89cd99dedd68f16e399bc9980987":
            raise ValueError("AD result is not pinned to the merged native AD revision")

    robust = next(
        record["representative_result"]
        for record in records
        if record["case_id"] == "ad_robust_kpm_design"
    )
    if robust["metrics"]["isolated_held_out_validation_claimed"]:
        raise ValueError("public AD benchmark must not claim isolated held-out validation")

    qualifier = " current" if args.current else ""
    print(
        f"AD result validation passed:{qualifier} "
        f"{len(records)} backend-case records"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
