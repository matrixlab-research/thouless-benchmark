#!/usr/bin/env python3
"""Collect paired native-AD and central-finite-difference timings."""

from __future__ import annotations

import argparse
import json
import platform
import statistics
import subprocess
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def execute(command: list[str]) -> dict:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"{' '.join(command)} failed with {completed.returncode}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    return json.loads(completed.stdout)


def timing(samples: list[float]) -> dict:
    return {
        "median": statistics.median(samples),
        "minimum": min(samples),
        "maximum": max(samples),
        "samples": samples,
    }


def machine_metadata() -> dict:
    return {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "processor": platform.processor(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--thouless-binary",
        default=str(
            ROOT
            / "backends"
            / "thouless"
            / "target"
            / "release"
            / "thouless-benchmark-runner"
        ),
    )
    parser.add_argument("--repetitions", type=int, default=7)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "results" / "local" / "ad-vs-finite-difference.json",
    )
    args = parser.parse_args()
    if args.repetitions < 3:
        raise ValueError("at least three repetitions are required")

    manifest = json.loads((ROOT / "benchmark" / "ad_comparison.json").read_text())
    records = []
    for case in manifest["cases"]:
        ad_samples = []
        finite_difference_samples = []
        representative = None
        command = [args.thouless_binary, case["id"]]
        for _ in range(args.repetitions):
            result = execute(command)
            if result["status"] != "passed":
                raise RuntimeError(f"thouless/{case['id']} did not pass")
            representative = result
            ad_samples.append(float(result["metrics"]["native_ad"]["seconds"]))
            finite_difference_samples.append(
                float(result["metrics"]["central_finite_difference"]["seconds"])
            )
        ad_timing = timing(ad_samples)
        finite_difference_timing = timing(finite_difference_samples)
        records.append(
            {
                "backend": "thouless",
                "case_id": case["id"],
                "source_case_id": case["source_case_id"],
                "command": command,
                "repetitions": args.repetitions,
                "native_ad_seconds": ad_timing,
                "central_finite_difference_seconds": finite_difference_timing,
                "speedup_finite_difference_over_ad": (
                    finite_difference_timing["median"] / ad_timing["median"]
                ),
                "representative_result": representative,
            }
        )

    speedups = [
        record["speedup_finite_difference_over_ad"] for record in records
    ]
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(UTC).isoformat(),
        "platform": machine_metadata(),
        "policy": {
            **manifest["fairness_contract"],
            "paired_methods_execute_in_one_process": True,
            "timing_is_descriptive": True,
            "public_validation_is_not_isolated_held_out_evaluation": True,
        },
        "summary": {
            "workflow_records": len(records),
            "passed": len(records),
            "failed": 0,
            "repetitions_per_record": args.repetitions,
            "native_ad_faster": sum(speedup > 1.0 for speedup in speedups),
            "central_finite_difference_faster": sum(
                speedup < 1.0 for speedup in speedups
            ),
            "median_speedup_finite_difference_over_ad": statistics.median(
                speedups
            ),
        },
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"wrote {len(records)} paired comparison records to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
