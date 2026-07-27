#!/usr/bin/env python3
"""Synchronize per-problem executable status from the backend audit."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROBLEM_ROOT = ROOT / "docs" / "problems"
INDEX = PROBLEM_ROOT / "README.md"


def expected_documents() -> dict[Path, tuple[str, str]]:
    audit = json.loads((ROOT / "benchmark" / "problem_coverage.json").read_text())
    expected: dict[Path, tuple[str, str]] = {}
    for problem in audit["problems"]:
        implemented = {
            backend: record["witness_cases"]
            for backend, record in problem["backends"].items()
            if record["status"] == "implemented"
        }
        status = "executable" if implemented else "proposed"
        if implemented:
            evidence = "; ".join(
                f"{backend}: {', '.join(cases)}"
                for backend, cases in implemented.items()
            )
            paragraph = (
                "`executable`: the package-backed evaluator, independent gates, "
                "recorded result, and CI are present for "
                f"{evidence}. See the machine-readable "
                "[backend audit](../../../benchmark/problem_coverage.json). "
                "This public result is not held-out validation."
            )
        else:
            paragraph = (
                "`proposed`: this document specifies a scientific problem but "
                "does not claim that any backend currently passes it. No current "
                "executable case is asserted to cover this full problem."
            )
        expected[ROOT / "docs" / problem["document"]] = (status, paragraph)
    return expected


def render_problem(text: str, status: str, paragraph: str) -> str:
    text = re.sub(
        r"(?m)^status: (?:proposed|executable)$",
        f"status: {status}",
        text,
        count=1,
    )
    prefix, separator, _old = text.partition("## Implementation status\n\n")
    if not separator:
        raise ValueError("missing implementation-status section")
    return f"{prefix}{separator}{paragraph}\n"


def render_index(text: str, statuses: dict[str, str]) -> str:
    def replacement(match: re.Match[str]) -> str:
        qid = match.group(2)
        return f"{match.group(1)}{statuses[qid]}{match.group(4)}"

    return re.sub(
        r"(?m)^(\| (TBQ-[0-9]{3}) \|.+\| TB-REQ-[0-9]{3} \| )"
        r"(proposed|executable)( \|)$",
        replacement,
        text,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = expected_documents()
    mismatches: list[str] = []
    statuses: dict[str, str] = {}
    for path, (status, paragraph) in expected.items():
        match = re.search(r"tbq-([0-9]{3})-", path.name)
        if match is None:
            raise ValueError(f"cannot parse question id from {path}")
        statuses[f"TBQ-{match.group(1)}"] = status
        rendered = render_problem(path.read_text(), status, paragraph)
        if rendered != path.read_text():
            if args.check:
                mismatches.append(str(path.relative_to(ROOT)))
            else:
                path.write_text(rendered)
    rendered_index = render_index(INDEX.read_text(), statuses)
    if rendered_index != INDEX.read_text():
        if args.check:
            mismatches.append(str(INDEX.relative_to(ROOT)))
        else:
            INDEX.write_text(rendered_index)
    if mismatches:
        print(
            "problem status synchronization failed: " + ", ".join(mismatches),
            file=sys.stderr,
        )
        return 1
    print(
        f"problem statuses {'verified' if args.check else 'synchronized'}: "
        f"{sum(value == 'executable' for value in statuses.values())} executable"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
