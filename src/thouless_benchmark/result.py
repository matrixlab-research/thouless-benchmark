"""Stable result records shared by backend executables."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    actual: float | int | list[float] | list[int]
    expected: float | int | list[float] | list[int] | str
    tolerance: float | None = None


def result(
    *,
    case_id: str,
    backend: str,
    backend_version: str,
    metrics: dict[str, Any],
    checks: list[Check],
    elapsed_seconds: float,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "case_id": case_id,
        "backend": backend,
        "backend_version": backend_version,
        "status": "passed" if all(check.passed for check in checks) else "failed",
        "metrics": metrics,
        "checks": [asdict(check) for check in checks],
        "elapsed_seconds": elapsed_seconds,
    }
