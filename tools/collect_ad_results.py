#!/usr/bin/env python3
"""Collect repeated correctness and timing records for native AD benchmarks."""

from __future__ import annotations

import argparse
import json
import platform
import statistics
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def execute(command: list[str]) -> tuple[dict, float]:
    started = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    wall = time.perf_counter() - started
    if completed.returncode != 0:
        raise RuntimeError(
            f"{' '.join(command)} failed with {completed.returncode}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    return json.loads(completed.stdout), wall


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
        default=ROOT / "results" / "local" / "ad.json",
    )
    args = parser.parse_args()
    if args.repetitions < 3:
        raise ValueError("at least three repetitions are required")

    case_ids = json.loads(
        (ROOT / "benchmark" / "ad_implementation.json").read_text()
    )["implemented"]["thouless"]
    records = []
    for case_id in case_ids:
        elapsed_samples = []
        wall_samples = []
        representative = None
        command = [args.thouless_binary, case_id]
        for _ in range(args.repetitions):
            result, wall = execute(command)
            if result["status"] != "passed":
                raise RuntimeError(f"thouless/{case_id} did not pass")
            representative = result
            elapsed_samples.append(float(result["elapsed_seconds"]))
            wall_samples.append(wall)
        records.append(
            {
                "backend": "thouless",
                "case_id": case_id,
                "command": command,
                "repetitions": args.repetitions,
                "kernel_seconds": {
                    "median": statistics.median(elapsed_samples),
                    "minimum": min(elapsed_samples),
                    "maximum": max(elapsed_samples),
                    "samples": elapsed_samples,
                },
                "process_wall_seconds": {
                    "median": statistics.median(wall_samples),
                    "minimum": min(wall_samples),
                    "maximum": max(wall_samples),
                    "samples": wall_samples,
                },
                "representative_result": representative,
            }
        )
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(UTC).isoformat(),
        "platform": machine_metadata(),
        "policy": {
            "same_machine": True,
            "accuracy_is_gated": True,
            "timing_is_descriptive": True,
            "finite_differences_are_validation_only": True,
            "public_validation_is_not_isolated_held_out_evaluation": True,
            "whole_tbq_coverage_is_not_inferred_from_ad_witnesses": True,
        },
        "summary": {
            "backend_case_records": len(records),
            "passed": len(records),
            "failed": 0,
            "repetitions_per_record": args.repetitions,
        },
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"wrote {len(records)} passing AD records to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
