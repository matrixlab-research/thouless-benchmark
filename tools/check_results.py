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
    root = Path(__file__).resolve().parents[1]
    implementation = json.loads(
        (root / "benchmark" / "implementation.json").read_text()
    )["implemented"]
    expected_keys = {
        (case_id, backend)
        for backend, case_ids in implementation.items()
        for case_id in case_ids
    }
    expected_count = len(expected_keys)
    if payload["summary"] != {
        "failed": 0,
        "passed": expected_count,
        "result_count": expected_count,
    }:
        raise ValueError(f"unexpected summary: {payload['summary']}")
    by_key = {(item["case_id"], item["backend"]): item for item in results}
    if set(by_key) != expected_keys:
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

        reference = by_key[("boundary_haldane_ribbon_flow", "thouless")]["metrics"]
        compared = by_key[("boundary_haldane_ribbon_flow", backend)]["metrics"]
        if abs(round(reference["bulk_chern_number"])) != abs(
            round(compared["bulk_chern_number"])
        ):
            raise ValueError("Haldane bulk-boundary topology differs across backends")
        close(reference["crossing_momentum"], compared["crossing_momentum"], 1.0e-12)
        for name in ("crossing_energies", "edge_weights", "edge_velocities"):
            for left, right in zip(reference[name], compared[name]):
                close(left, right, 1.0e-10)

        reference = by_key[("boundary_graphene_terminations", "thouless")]["metrics"]
        compared = by_key[("boundary_graphene_terminations", backend)]["metrics"]
        for name in ("armchair_gaps", "zigzag_edge_weights"):
            for left, right in zip(reference[name], compared[name]):
                close(left, right, 1.0e-12)
        close(
            reference["armchair_scaling_spread"],
            compared["armchair_scaling_spread"],
            1.0e-12,
        )

        reference = by_key[("boundary_bbh_corner_modes", "thouless")]["metrics"]
        compared = by_key[("boundary_bbh_corner_modes", backend)]["metrics"]
        for left, right in zip(
            sorted(abs(value) for value in reference["midgap_energies"]),
            sorted(abs(value) for value in compared["midgap_energies"]),
        ):
            close(left, right, 1.0e-12)
        close(
            reference["next_state_absolute_energy"],
            compared["next_state_absolute_energy"],
            1.0e-12,
        )
        for left, right in zip(
            sorted(reference["corner_weights"]), sorted(compared["corner_weights"])
        ):
            close(left, right, 1.0e-12)

        reference = by_key[("bulk_rice_mele_pump", "thouless")]["metrics"]
        compared = by_key[("bulk_rice_mele_pump", backend)]["metrics"]
        close(reference["chern_number"], compared["chern_number"], 1.0e-12)
        close(reference["minimum_cycle_gap"], compared["minimum_cycle_gap"], 2.0e-3)

        reference = by_key[("bulk_qwz_phase_diagram", "thouless")]["metrics"]
        compared = by_key[("bulk_qwz_phase_diagram", backend)]["metrics"]
        if [abs(round(value)) for value in reference["chern_numbers"]] != [
            abs(round(value)) for value in compared["chern_numbers"]
        ]:
            raise ValueError("QWZ phase sequence differs across backends")

        reference = by_key[("bulk_haldane_chern_transition", "thouless")]["metrics"]
        compared = by_key[("bulk_haldane_chern_transition", backend)]["metrics"]
        if abs(round(reference["chern_number"])) != abs(round(compared["chern_number"])):
            raise ValueError("Haldane topological class differs across backends")
        for left, right in zip(reference["dirac_masses"], compared["dirac_masses"]):
            close(left, right, 1.0e-12)
        close(reference["minimum_gap"], compared["minimum_gap"], 1.0e-12)

        reference = by_key[("bulk_kagome_soc_chern", "thouless")]["metrics"]
        compared = by_key[("bulk_kagome_soc_chern", backend)]["metrics"]
        if [abs(value) for value in reference["rounded_band_chern_numbers"]] != [
            abs(value) for value in compared["rounded_band_chern_numbers"]
        ]:
            raise ValueError("Kagome band topology differs across backends")
        for name in ("minimum_gaps", "bandwidths"):
            for left, right in zip(reference[name], compared[name]):
                close(left, right, 1.0e-12)

        reference = by_key[("bulk_kane_mele_z2", "thouless")]["metrics"]
        compared = by_key[("bulk_kane_mele_z2", backend)]["metrics"]
        if reference["z2"] != compared["z2"]:
            raise ValueError("Kane-Mele Z2 class differs across backends")
        close(reference["minimum_rashba_gap"], compared["minimum_rashba_gap"], 1.0e-12)
        close(reference["endpoint_separation"], compared["endpoint_separation"], 1.0e-12)
        close(
            reference["maximum_wannier_separation"],
            compared["maximum_wannier_separation"],
            1.0e-12,
        )

        reference = by_key[("bulk_bbh_nested_wilson", "thouless")]["metrics"]
        compared = by_key[("bulk_bbh_nested_wilson", backend)]["metrics"]
        for name in ("minimum_bulk_gap", "minimum_wannier_gap", "quadrupole"):
            close(reference[name], compared[name], 1.0e-12)
        for left, right in zip(
            reference["sector_polarizations"], compared["sector_polarizations"]
        ):
            close(left, right, 1.0e-12)

        reference = by_key[("bulk_tilted_dirac_berry_dipole", "thouless")]["metrics"]
        compared = by_key[("bulk_tilted_dirac_berry_dipole", backend)]["metrics"]
        if reference["peak_chemical_potential"] != compared["peak_chemical_potential"]:
            raise ValueError("Berry-curvature-dipole peak differs across backends")
        for name in ("positive_tilt_dipole", "negative_tilt_dipole"):
            for left, right in zip(reference[name], compared[name]):
                close(left, right, 1.0e-9)

        reference = by_key[("bulk_weyl_chirality", "thouless")]["metrics"]
        compared = by_key[("bulk_weyl_chirality", backend)]["metrics"]
        if [abs(round(value)) for value in reference["slice_chern_numbers"]] != [
            abs(round(value)) for value in compared["slice_chern_numbers"]
        ]:
            raise ValueError("Weyl slice topology differs across backends")

        reference = by_key[("bulk_nodal_line_berry_phase", "thouless")]["metrics"]
        compared = by_key[("bulk_nodal_line_berry_phase", backend)]["metrics"]
        close(abs(reference["linked_loop_phase"]), abs(compared["linked_loop_phase"]), 1.0e-12)
        close(reference["unlinked_loop_phase"], compared["unlinked_loop_phase"], 1.0e-12)

    thouless_interpolation = by_key[("bulk_wannier_interpolation", "thouless")]
    pythtb_interpolation = by_key[("bulk_wannier_interpolation", "pythtb")]
    if thouless_interpolation["status"] != "passed" or pythtb_interpolation["status"] != "passed":
        raise ValueError("Wannier interpolation did not pass in both applicable backends")

    thouless_transport = by_key[("transport_ballistic_chain", "thouless")]["metrics"]
    kwant_transport = by_key[("transport_ballistic_chain", "kwant")]["metrics"]
    for left, right in zip(thouless_transport["transmissions"], kwant_transport["transmissions"]):
        close(left, right, 1.0e-12)

    for case_id, tolerance in (
        ("transport_resonant_level", 2.0e-9),
        ("transport_aharonov_bohm_ring", 2.0e-12),
        ("transport_quantum_hall_strip", 2.0e-10),
    ):
        reference = by_key[(case_id, "thouless")]["metrics"]
        compared = by_key[(case_id, "kwant")]["metrics"]
        for left, right in zip(reference["transmissions"], compared["transmissions"]):
            close(left, right, tolerance)
    reference = by_key[("transport_quantum_hall_strip", "thouless")]["metrics"]
    compared = by_key[("transport_quantum_hall_strip", "kwant")]["metrics"]
    close(reference["edge_current_fraction"], compared["edge_current_fraction"], 1.0e-12)
    print(
        f"result snapshot passed: {expected_count} analytic gates and selected "
        "cross-backend agreements"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
