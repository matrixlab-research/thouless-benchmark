#!/usr/bin/env python3
"""Run the verified seed across isolated upstream and Rust environments."""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED = {
    "thouless": [
        "bulk_graphene_dirac_cone",
        "bulk_ssh_polarization",
        "boundary_ssh_edge_localization",
        "transport_ballistic_chain",
    ],
    "pythtb": [
        "bulk_graphene_dirac_cone",
        "bulk_ssh_polarization",
        "boundary_ssh_edge_localization",
    ],
    "kwant": [
        "bulk_graphene_dirac_cone",
        "bulk_ssh_polarization",
        "boundary_ssh_edge_localization",
        "transport_ballistic_chain",
    ],
}


def execute(command: list[str], env: dict[str, str] | None = None) -> dict:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pythtb-python", default=str(ROOT / ".venv" / "bin" / "python"))
    parser.add_argument("--kwant-python", default=str(ROOT / ".venv-kwant" / "bin" / "python"))
    parser.add_argument("--cargo", default="cargo")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "local" / "seed.json")
    args = parser.parse_args()
    results: list[dict] = []
    python_env = os.environ.copy()
    python_env["MPLCONFIGDIR"] = str(ROOT / "results" / "local" / "matplotlib")
    python_env["PYTHONWARNINGS"] = "ignore"
    rust_env = os.environ.copy()
    cargo_directory = str(Path(args.cargo).resolve().parent)
    rust_env["PATH"] = cargo_directory + os.pathsep + rust_env.get("PATH", "")
    for case_id in SEED["pythtb"]:
        results.append(
            execute([args.pythtb_python, "backends/pythtb/run.py", case_id], python_env)
        )
    for case_id in SEED["kwant"]:
        results.append(execute([args.kwant_python, "backends/kwant/run.py", case_id], python_env))
    for case_id in SEED["thouless"]:
        results.append(
            execute(
                [
                    args.cargo,
                    "run",
                    "--quiet",
                    "--release",
                    "--manifest-path",
                    "backends/thouless/Cargo.toml",
                    "--",
                    case_id,
                ],
                rust_env,
            )
        )
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(UTC).isoformat(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "policy": {
            "accuracy_is_gated": True,
            "timing_is_descriptive": True,
            "public_results_are_not_held_out": True,
        },
        "summary": {
            "result_count": len(results),
            "passed": sum(item["status"] == "passed" for item in results),
            "failed": sum(item["status"] == "failed" for item in results),
        },
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"wrote {len(results)} passing backend-case results to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
