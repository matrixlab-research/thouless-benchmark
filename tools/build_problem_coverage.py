#!/usr/bin/env python3
"""Build or verify the explicit 100-question, three-backend audit."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "benchmark" / "problem_coverage.json"
MARKDOWN_OUTPUT = ROOT / "docs" / "problem-coverage.md"
BACKENDS = ("thouless", "pythtb", "kwant")

# Only whole-problem witnesses belong here.  A related model or one matching
# observable is not enough.
COMMON_IMPLEMENTED = {
    "TBQ-006": ["domain_spectral_reliability"],
    "TBQ-007": ["domain_spectral_reliability"],
    "TBQ-010": ["domain_spectral_reliability"],
    "TBQ-011": ["domain_magnetic_hofstadter"],
    "TBQ-012": ["domain_magnetic_hofstadter"],
    "TBQ-013": ["domain_magnetic_hofstadter"],
    "TBQ-019": [
        "bulk_haldane_chern_transition",
        "boundary_haldane_ribbon_flow",
    ],
    "TBQ-022": ["boundary_ssh_edge_localization"],
    "TBQ-041": ["domain_bdg_majorana"],
    "TBQ-042": ["domain_bdg_majorana"],
    "TBQ-043": ["domain_bdg_majorana"],
    "TBQ-066": ["domain_spin_texture_covariance"],
}
BACKEND_IMPLEMENTED = {
    "thouless": {"TBQ-036": ["domain_lead_calibration"]},
    "pythtb": {},
    "kwant": {"TBQ-036": ["domain_lead_calibration"]},
}

PYTHTB_NOT_APPLICABLE = (
    {1, 23, 30}
    | set(range(36, 41))
    | set(range(44, 61))
    | {64, 67, 69}
    | set(range(71, 76))
    | {84}
    | set(range(91, 101))
)
KWANT_NOT_APPLICABLE = (
    {1, 2}
    | set(range(44, 61))
    | {72, 73}
    | set(range(96, 101))
)
THOULESS_NOT_APPLICABLE = (
    {1}
    | set(range(51, 61))
    | set(range(96, 101))
)
NOT_APPLICABLE = {
    "pythtb": PYTHTB_NOT_APPLICABLE,
    "kwant": KWANT_NOT_APPLICABLE,
    "thouless": THOULESS_NOT_APPLICABLE,
}

NOT_APPLICABLE_REASON = {
    "pythtb": (
        "The complete required workflow lies outside original PythTB 2.0: "
        "it has no corresponding overlap, open-lead, real-time, self-consistent, "
        "response, sparse-production, or inference solver."
    ),
    "kwant": (
        "The complete required workflow lies outside original Kwant 1.5: "
        "its static scattering and sparse-system APIs do not supply the required "
        "Wannier, non-Hermitian-topology, real-time, self-consistent, optical, "
        "thermoelectric, or inference workflow."
    ),
    "thouless": (
        "The pinned native Thouless revision does not supply the required "
        "generalized-overlap, real-time Floquet, interacting self-consistency, "
        "or parameter-inference workflow."
    ),
}


def problem_rows() -> list[tuple[str, str, str, str]]:
    rows = []
    paths = sorted(
        (ROOT / "docs" / "problems").glob("[0-9][0-9]-*/tbq-[0-9][0-9][0-9]-*.md")
    )
    for path in paths:
        text = path.read_text()
        qid = re.search(r"^id: (TBQ-[0-9]{3})$", text, re.MULTILINE)
        title = re.search(r"^# TBQ-[0-9]{3} — (.+)$", text, re.MULTILINE)
        if qid is None or title is None:
            raise ValueError(f"cannot parse {path}")
        rows.append(
            (
                qid.group(1),
                title.group(1),
                path.parent.name,
                path.relative_to(ROOT / "docs").as_posix(),
            )
        )
    if len(rows) != 100:
        raise ValueError(f"expected 100 problems, found {len(rows)}")
    return rows


def audit_entry(qid: str, backend: str) -> dict:
    witnesses = COMMON_IMPLEMENTED.get(qid) or BACKEND_IMPLEMENTED[backend].get(qid)
    if witnesses is not None:
        return {
            "status": "implemented",
            "witness_cases": witnesses,
            "reason": (
                "Every required claim is exercised by package-backed code and "
                "an analytic or invariant-based gate."
            ),
        }
    number = int(qid.split("-")[1])
    if number in NOT_APPLICABLE[backend]:
        return {
            "status": "not_applicable",
            "witness_cases": [],
            "reason": NOT_APPLICABLE_REASON[backend],
        }
    return {
        "status": "partial",
        "witness_cases": [],
        "reason": (
            "The backend can supply at least one relevant one-body model, matrix, "
            "or solver component, but no current evaluator witnesses every "
            f"required computation and control in {qid}."
        ),
    }


def build() -> dict:
    problems = []
    for qid, title, suite, document in problem_rows():
        problems.append(
            {
                "id": qid,
                "title": title,
                "suite": suite,
                "document": document,
                "backends": {
                    backend: audit_entry(qid, backend) for backend in BACKENDS
                },
            }
        )
    summary = {}
    for backend in BACKENDS:
        counts = {
            status: sum(
                problem["backends"][backend]["status"] == status
                for problem in problems
            )
            for status in ("implemented", "partial", "not_applicable")
        }
        applicable = counts["implemented"] + counts["partial"]
        summary[backend] = {
            **counts,
            "total_questions": 100,
            "raw_coverage_percent": counts["implemented"],
            "applicable_coverage_percent": round(
                100.0 * counts["implemented"] / applicable, 2
            ),
        }
    return {
        "schema_version": 1,
        "policy": {
            "unit": "whole scientific problem",
            "implemented": "all required claims have executable package-backed witnesses and passing gates",
            "partial": "relevant package capability exists but the complete problem is not yet witnessed",
            "not_applicable": "the required end-to-end scientific workflow is outside the package scope",
            "shared_postprocessing": "allowed only after the named backend constructs the Hamiltonian",
            "public_is_not_held_out": True,
        },
        "summary": summary,
        "problems": problems,
    }


def render_markdown(payload: dict) -> str:
    labels = {
        "implemented": "implemented",
        "partial": "capability gap",
        "not_applicable": "not applicable",
    }
    lines = [
        "# Whole-problem backend coverage",
        "",
        "This is the human-readable view of",
        "[`benchmark/problem_coverage.json`](../benchmark/problem_coverage.json).",
        "Coverage is counted only when every required claim in one domain problem has",
        "package-backed executable evidence and an analytic or invariant-based gate.",
        "",
        "## Summary",
        "",
        "| Backend | Implemented | Capability gap | Not applicable | Raw coverage |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for backend in BACKENDS:
        item = payload["summary"][backend]
        lines.append(
            f"| {backend} | {item['implemented']} | {item['partial']} | "
            f"{item['not_applicable']} | {item['raw_coverage_percent']}% |"
        )
    lines.extend(
        [
            "",
            "## All questions",
            "",
            "| ID | Scientific problem | Thouless | PythTB | Kwant | Witnesses |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for problem in payload["problems"]:
        witnesses = sorted(
            {
                witness
                for record in problem["backends"].values()
                for witness in record["witness_cases"]
            }
        )
        link = f"[{problem['title']}]({problem['document']})"
        lines.append(
            f"| {problem['id']} | {link} | "
            f"{labels[problem['backends']['thouless']['status']]} | "
            f"{labels[problem['backends']['pythtb']['status']]} | "
            f"{labels[problem['backends']['kwant']['status']]} | "
            f"{', '.join(f'`{item}`' for item in witnesses) or 'none'} |"
        )
    lines.extend(
        [
            "",
            "`Capability gap` means that the backend supplies at least one relevant",
            "component but does not currently solve the complete problem. It is not",
            "included in coverage. Public witnesses are not held-out validation.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    markdown = render_markdown(payload)
    if args.check:
        if (
            not OUTPUT.exists()
            or OUTPUT.read_text() != encoded
            or not MARKDOWN_OUTPUT.exists()
            or MARKDOWN_OUTPUT.read_text() != markdown
        ):
            print(
                "problem coverage audit is missing or stale; run "
                "python tools/build_problem_coverage.py",
                file=sys.stderr,
            )
            return 1
        print("problem coverage audit passed: 100 questions x 3 backends")
        return 0
    OUTPUT.write_text(encoded)
    MARKDOWN_OUTPUT.write_text(markdown)
    print(f"wrote {OUTPUT} and {MARKDOWN_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
