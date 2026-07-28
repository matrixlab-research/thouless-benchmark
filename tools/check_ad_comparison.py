#!/usr/bin/env python3
"""Validate a paired native-AD and finite-difference result record."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.result.read_text())
    manifest = json.loads((ROOT / "benchmark" / "ad_comparison.json").read_text())
    records = payload["records"]
    expected = {case["id"]: case for case in manifest["cases"]}
    by_id = {record["case_id"]: record for record in records}
    if len(records) != len(by_id):
        raise ValueError("AD comparison result contains duplicate cases")
    if set(by_id) != set(expected):
        raise ValueError(
            "AD comparison result does not exactly match the comparison manifest"
        )
    if payload["summary"]["workflow_records"] != len(records):
        raise ValueError("AD comparison summary count does not match its records")
    if payload["summary"]["passed"] != len(records):
        raise ValueError("AD comparison summary is not completely passing")
    required_checks = set(manifest["required_checks"])
    for case_id, record in by_id.items():
        result = record["representative_result"]
        if result["status"] != "passed":
            raise ValueError(f"{case_id} representative result failed")
        if result["backend_version"] != "237f544c497e89cd99dedd68f16e399bc9980987":
            raise ValueError(f"{case_id} is not pinned to the native AD revision")
        if result["metrics"]["physical_model"] != expected[case_id]["physical_system"]:
            raise ValueError(f"{case_id} reports the wrong physical system")
        if result["metrics"]["parameter_count"] != expected[case_id]["parameter_count"]:
            raise ValueError(f"{case_id} reports the wrong parameter count")
        available = {
            check["name"] for check in result["checks"] if check["passed"]
        }
        if not required_checks <= available:
            raise ValueError(
                f"{case_id} lacks comparison checks "
                f"{sorted(required_checks - available)}"
            )
        if record["repetitions"] < 3:
            raise ValueError(f"{case_id} has fewer than three repetitions")
        for method in (
            "native_ad_seconds",
            "central_finite_difference_seconds",
        ):
            samples = record[method]["samples"]
            if len(samples) != record["repetitions"]:
                raise ValueError(f"{case_id}/{method} sample count is inconsistent")
            if min(samples) <= 0.0:
                raise ValueError(f"{case_id}/{method} timing is not positive")
        if record["speedup_finite_difference_over_ad"] <= 0.0:
            raise ValueError(f"{case_id} speed ratio is not positive")

    if not payload["policy"]["same_rust_forward_model"]:
        raise ValueError("comparison does not freeze the Rust forward model")
    if not payload["policy"]["finite_difference_uses_forward_only_calls"]:
        raise ValueError("finite-difference baseline may be using AD internally")
    if not payload["policy"]["both_derivative_paths_are_warmed_before_timing"]:
        raise ValueError("both derivative paths must be warmed before timing")
    if not payload["policy"]["relative_speed_is_not_a_ci_gate"]:
        raise ValueError("relative speed must remain descriptive")
    print(f"AD method comparison passed: {len(records)} paired workflows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
