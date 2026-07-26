#!/usr/bin/env python3
"""Validate a collected result snapshot and selected cross-backend agreements."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


EXPECTED_VERSIONS = {
    "thouless": "0d87773278183ddc7c254438dccbda1face04fb2",
    "pythtb": "2.0.0",
    "kwant": "1.5.0",
}


def close(left: float, right: float, tolerance: float) -> None:
    if not math.isclose(left, right, rel_tol=0.0, abs_tol=tolerance):
        raise ValueError(f"{left} and {right} differ by more than {tolerance}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.snapshot.read_text())
    results = payload["results"]
    if payload["summary"] != {"failed": 0, "passed": 11, "result_count": 11}:
        raise ValueError(f"unexpected summary: {payload['summary']}")
    by_key = {(item["case_id"], item["backend"]): item for item in results}
    if len(by_key) != 11:
        raise ValueError("snapshot has duplicate or missing backend-case results")
    for item in results:
        if item["status"] != "passed" or not all(check["passed"] for check in item["checks"]):
            raise ValueError(f"failed scientific check: {item['backend']} {item['case_id']}")
        if item["backend_version"] != EXPECTED_VERSIONS[item["backend"]]:
            raise ValueError(f"unexpected backend version in {item['backend']} result")

    common_bulk = ["thouless", "pythtb", "kwant"]
    for backend in common_bulk[1:]:
        reference = by_key[("bulk_graphene_dirac_cone", "thouless")]["metrics"]
        compared = by_key[("bulk_graphene_dirac_cone", backend)]["metrics"]
        for left, right in zip(reference["gamma_eigenvalues"], compared["gamma_eigenvalues"]):
            close(left, right, 1.0e-12)
        close(reference["dirac_gap"], compared["dirac_gap"], 1.0e-12)

        reference = by_key[("bulk_ssh_polarization", "thouless")]["metrics"]
        compared = by_key[("bulk_ssh_polarization", backend)]["metrics"]
        close(reference["reduced_polarization"], compared["reduced_polarization"], 1.0e-12)
        close(reference["minimum_gap"], compared["minimum_gap"], 1.0e-12)

        reference = by_key[("boundary_ssh_edge_localization", "thouless")]["metrics"]
        compared = by_key[("boundary_ssh_edge_localization", backend)]["metrics"]
        # The longest chain has a 1e-11 splitting, so LAPACK backends differ
        # slightly in the fitted exponent despite agreeing on every physical
        # localization check.
        close(reference["localization_length"], compared["localization_length"], 1.0e-5)
        for left, right in zip(reference["splittings"], compared["splittings"]):
            close(left, right, 1.0e-12)

    thouless_transport = by_key[("transport_ballistic_chain", "thouless")]["metrics"]
    kwant_transport = by_key[("transport_ballistic_chain", "kwant")]["metrics"]
    for left, right in zip(thouless_transport["transmissions"], kwant_transport["transmissions"]):
        close(left, right, 1.0e-12)
    print("result snapshot passed: 11 analytic gates and selected cross-backend agreements")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
