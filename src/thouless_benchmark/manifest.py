"""Typed access to the canonical benchmark manifest."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Case:
    id: str
    track: str
    domain: str
    question: str
    model: str
    parameters: dict[str, Any]
    observable: str
    gate: dict[str, Any]
    backends: tuple[str, ...]
    not_applicable: dict[str, str]
    lkm: dict[str, str]


def load_manifest(path: Path) -> list[Case]:
    payload = json.loads(path.read_text())
    return [
        Case(
            id=item["id"],
            track=item["track"],
            domain=item["domain"],
            question=item["question"],
            model=item["model"],
            parameters=item["parameters"],
            observable=item["observable"],
            gate=item["gate"],
            backends=tuple(item["backends"]),
            not_applicable=item.get("not_applicable", {}),
            lkm=item["lkm"],
        )
        for item in payload["cases"]
    ]
