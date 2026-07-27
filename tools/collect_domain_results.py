#!/usr/bin/env python3
"""Collect repeated same-machine correctness and timing records for domain cases."""

from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def execute(command: list[str], environment: dict[str, str]) -> tuple[dict, float]:
    started = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
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
    metadata = {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "processor": platform.processor(),
    }
    if platform.system() == "Darwin":
        completed = subprocess.run(
            ["sysctl", "-n", "machdep.cpu.brand_string"],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode == 0:
            metadata["cpu"] = completed.stdout.strip()
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pythtb-python", default=str(ROOT / ".venv" / "bin" / "python"))
    parser.add_argument("--kwant-python", default=str(ROOT / ".venv-kwant" / "bin" / "python"))
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
        default=ROOT / "results" / "local" / "domain.json",
    )
    args = parser.parse_args()
    if args.repetitions < 3:
        raise ValueError("at least three repetitions are required")

    implementations = json.loads(
        (ROOT / "benchmark" / "domain_implementation.json").read_text()
    )["implemented"]
    commands = {
        "pythtb": lambda case_id: [
            args.pythtb_python,
            "backends/pythtb/run.py",
            case_id,
        ],
        "kwant": lambda case_id: [
            args.kwant_python,
            "backends/kwant/run.py",
            case_id,
        ],
        "thouless": lambda case_id: [args.thouless_binary, case_id],
    }
    environment = os.environ.copy()
    environment["MPLCONFIGDIR"] = str(ROOT / "results" / "local" / "matplotlib")
    environment["PYTHONWARNINGS"] = "ignore"
    records = []
    for backend in ("pythtb", "kwant", "thouless"):
        for case_id in implementations[backend]:
            elapsed_samples = []
            wall_samples = []
            representative = None
            command = commands[backend](case_id)
            for _ in range(args.repetitions):
                result, wall = execute(command, environment)
                if result["status"] != "passed":
                    raise RuntimeError(f"{backend}/{case_id} did not pass")
                representative = result
                elapsed_samples.append(float(result["elapsed_seconds"]))
                wall_samples.append(wall)
            records.append(
                {
                    "backend": backend,
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
            "kernel_time_excludes_import_and_process_startup": True,
            "process_wall_time_includes_import_and_process_startup": True,
            "public_results_are_not_held_out": True,
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
    print(f"wrote {len(records)} passing repeated records to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
