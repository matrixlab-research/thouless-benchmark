#!/usr/bin/env python3
"""Run the current native Thouless implementation manifest."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--binary",
        type=Path,
        default=(
            ROOT
            / "backends"
            / "thouless"
            / "target"
            / "release"
            / "thouless-benchmark-runner"
        ),
    )
    parser.add_argument(
        "--track",
        choices=("seed", "domain", "ad", "all"),
        default="all",
    )
    args = parser.parse_args()
    seed = json.loads((ROOT / "benchmark" / "implementation.json").read_text())[
        "implemented"
    ]["thouless"]
    domain = json.loads(
        (ROOT / "benchmark" / "domain_implementation.json").read_text()
    )["implemented"]["thouless"]
    domain_cases = {
        case["id"]: case
        for case in json.loads(
            (ROOT / "benchmark" / "domain_cases.json").read_text()
        )["cases"]
    }
    ad = json.loads(
        (ROOT / "benchmark" / "ad_implementation.json").read_text()
    )["implemented"]["thouless"]
    ad_cases = {
        case["id"]: case
        for case in json.loads(
            (ROOT / "benchmark" / "ad_cases.json").read_text()
        )["cases"]
    }
    case_ids = {
        "seed": seed,
        "domain": domain,
        "ad": ad,
        "all": seed + domain + ad,
    }[args.track]
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("selected Thouless manifest contains duplicate case ids")
    for case_id in case_ids:
        completed = subprocess.run(
            [str(args.binary), case_id],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            print(completed.stdout, file=sys.stderr)
            print(completed.stderr, file=sys.stderr)
            raise RuntimeError(
                f"native Thouless case {case_id} failed with "
                f"{completed.returncode}"
            )
        result = json.loads(completed.stdout)
        if result["status"] != "passed":
            raise ValueError(f"native Thouless case {case_id} did not pass")
        if case_id in domain_cases:
            available = {
                check["name"]
                for check in result["checks"]
                if check["passed"]
            }
            required = {
                gate
                for gates in domain_cases[case_id]["question_gates"].values()
                for gate in gates
            }
            if not required <= available:
                raise ValueError(
                    f"native Thouless case {case_id} lacks gates "
                    f"{sorted(required - available)}"
                )
        if case_id in ad_cases:
            available = {
                check["name"]
                for check in result["checks"]
                if check["passed"]
            }
            required = set(ad_cases[case_id]["required_checks"])
            if not required <= available:
                raise ValueError(
                    f"native Thouless AD case {case_id} lacks gates "
                    f"{sorted(required - available)}"
                )
        print(
            f"passed {case_id}: {len(result['checks'])} checks, "
            f"{result['elapsed_seconds']:.6f} s"
        )
    print(f"native Thouless manifest passed: {len(case_ids)} {args.track} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
