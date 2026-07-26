#!/usr/bin/env python3
"""Validate benchmark structure and cross-field invariants."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import jsonschema

BACKENDS = {"thouless", "pythtb", "kwant"}
EXPECTED_TRACKS = {"bulk": 12, "boundary": 4, "transport": 4}


def validate(root: Path) -> None:
    manifest_path = root / "benchmark" / "cases.json"
    schema_path = root / "benchmark" / "case.schema.json"
    manifest = json.loads(manifest_path.read_text())
    schema = json.loads(schema_path.read_text())
    jsonschema.Draft202012Validator(schema).validate(manifest)

    cases = manifest["cases"]
    ids = [case["id"] for case in cases]
    gcns = [case["lkm"]["gcn_id"] for case in cases]
    if len(set(ids)) != len(ids):
        raise ValueError(f"duplicate case ids: {duplicates(ids)}")
    if len(set(gcns)) != len(gcns):
        raise ValueError(f"duplicate LKM GCN ids: {duplicates(gcns)}")

    tracks = Counter(case["track"] for case in cases)
    if dict(tracks) != EXPECTED_TRACKS:
        raise ValueError(f"track distribution is {dict(tracks)}, expected {EXPECTED_TRACKS}")

    for case in cases:
        prefix = case["id"].split("_", 1)[0]
        if prefix != case["track"]:
            raise ValueError(f"{case['id']}: id prefix disagrees with track")
        applicable = set(case["backends"])
        missing = BACKENDS - applicable
        declared_na = set(case.get("not_applicable", {}))
        if "thouless" not in applicable:
            raise ValueError(f"{case['id']}: native Thouless must be applicable")
        if missing != declared_na:
            raise ValueError(
                f"{case['id']}: missing backends {sorted(missing)} "
                f"but not_applicable declares {sorted(declared_na)}"
            )
        if case["track"] == "transport" and "pythtb" in applicable:
            raise ValueError(f"{case['id']}: open transport cannot be attributed to PythTB")


def duplicates(values: list[str]) -> list[str]:
    return sorted(value for value, count in Counter(values).items() if count > 1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        validate(args.root)
    except (OSError, ValueError, json.JSONDecodeError, jsonschema.ValidationError) as error:
        print(f"manifest validation failed: {error}", file=sys.stderr)
        return 1
    print("manifest validation passed: 20 unique cases (12 bulk, 4 boundary, 4 transport)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
