#!/usr/bin/env python3
"""Original Kwant 1.5 benchmark adapter."""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
import warnings
from pathlib import Path

import kwant
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from thouless_benchmark.result import Check, result  # noqa: E402

warnings.filterwarnings("ignore", message="MUMPS is not available")


def wrapped_graphene(t: float):
    lattice = kwant.lattice.general(
        [(1.0, 0.0), (0.0, 1.0)], [(0.0, 0.0), (0.0, 0.0)], norbs=1
    )
    a, b = lattice.sublattices
    builder = kwant.Builder(kwant.TranslationalSymmetry((1.0, 0.0), (0.0, 1.0)))
    builder[a(0, 0)] = 0.0
    builder[b(0, 0)] = 0.0
    for cell in ((0, 0), (-1, 0), (0, -1)):
        builder[a(0, 0), b(*cell)] = t
    return kwant.wraparound.wraparound(builder).finalized()


def wrapped_ssh(intracell: float, intercell: float):
    lattice = kwant.lattice.general([(1.0,)], [(0.0,), (0.0,)], norbs=1)
    a, b = lattice.sublattices
    builder = kwant.Builder(kwant.TranslationalSymmetry((1.0,)))
    builder[a(0)] = 0.0
    builder[b(0)] = 0.0
    builder[a(0), b(0)] = intracell
    builder[b(0), a(1)] = intercell
    return kwant.wraparound.wraparound(builder).finalized()


def finite_ssh(cells: int, intracell: float, intercell: float):
    lattice = kwant.lattice.general([(1.0,)], [(0.0,), (0.0,)], norbs=1)
    a, b = lattice.sublattices
    builder = kwant.Builder()
    for cell in range(cells):
        builder[a(cell)] = 0.0
        builder[b(cell)] = 0.0
    for cell in range(cells):
        builder[a(cell), b(cell)] = intracell
        if cell + 1 < cells:
            builder[b(cell), a(cell + 1)] = intercell
    return builder.finalized()


def bulk_graphene_dirac_cone(parameters: dict) -> tuple[dict, list[Check]]:
    system = wrapped_graphene(parameters["t"])

    def values(kx: float, ky: float) -> np.ndarray:
        hamiltonian = system.hamiltonian_submatrix(params={"k_x": kx, "k_y": ky})
        return np.linalg.eigvalsh(hamiltonian)

    gamma = values(0.0, 0.0)
    kx, ky = 2.0 * np.pi / 3.0, 4.0 * np.pi / 3.0
    dirac = values(kx, ky)
    delta = 1.0e-5
    velocity = float(values(kx + delta, ky)[-1] / delta)
    gamma_expected = 3.0 * abs(parameters["t"])
    gap = float(dirac[-1] - dirac[0])
    metrics = {
        "gamma_eigenvalues": gamma.tolist(),
        "dirac_gap": gap,
        "radian_coordinate_velocity": velocity,
    }
    checks = [
        Check(
            "gamma_spectrum",
            bool(np.allclose(gamma, [-gamma_expected, gamma_expected], atol=1.0e-10)),
            gamma.tolist(),
            [-gamma_expected, gamma_expected],
            1.0e-10,
        ),
        Check("dirac_gap", abs(gap) < 1.0e-9, gap, 0.0, 1.0e-9),
        Check("linear_dispersion", abs(velocity) > 0.1, velocity, "nonzero"),
    ]
    return metrics, checks


def bulk_ssh_polarization(parameters: dict) -> tuple[dict, list[Check]]:
    intra = parameters["intracell"]
    inter = parameters["intercell"]
    system = wrapped_ssh(intra, inter)
    k_points = np.linspace(0.0, 2.0 * np.pi, 401, endpoint=True)
    hamiltonians = np.asarray(
        [system.hamiltonian_submatrix(params={"k_x": k}) for k in k_points]
    )
    off_diagonal = hamiltonians[:, 0, 1]
    phase = np.unwrap(np.angle(np.r_[off_diagonal, off_diagonal[:1]]))
    winding = int(np.rint((phase[-1] - phase[0]) / (2.0 * np.pi)))
    polarization = (winding / 2.0) % 1.0
    values = np.linalg.eigvalsh(hamiltonians)
    minimum_gap = float(np.min(values[:, 1] - values[:, 0]))
    expected_gap = 2.0 * abs(inter - intra)
    metrics = {
        "winding": winding,
        "reduced_polarization": polarization,
        "minimum_gap": minimum_gap,
    }
    checks = [
        Check("winding_magnitude", abs(winding) == 1, abs(winding), 1),
        Check("polarization_modulo_one", abs(polarization - 0.5) < 1.0e-8, polarization, 0.5, 1.0e-8),
        Check("bulk_gap", abs(minimum_gap - expected_gap) < 2.0e-4, minimum_gap, expected_gap, 2.0e-4),
    ]
    return metrics, checks


def boundary_ssh_edge_localization(parameters: dict) -> tuple[dict, list[Check]]:
    intra = parameters["intracell"]
    inter = parameters["intercell"]
    splittings: list[float] = []
    edge_weights: list[float] = []
    for cells in parameters["cells"]:
        hamiltonian = finite_ssh(cells, intra, inter).hamiltonian_submatrix()
        values, vectors = np.linalg.eigh(hamiltonian)
        pair = np.argsort(np.abs(values))[:2]
        splittings.append(float(np.max(np.abs(values[pair]))))
        edge_weights.append(
            float(np.mean(np.sum(np.abs(vectors[[0, 1, -2, -1]][:, pair]) ** 2, axis=0)))
        )
    cell_counts = np.asarray(parameters["cells"], dtype=float)
    slope, _ = np.polyfit(cell_counts, np.log(np.maximum(splittings, 1.0e-300)), 1)
    localization_length = float(-1.0 / slope)
    expected_length = float(-1.0 / math.log(abs(intra / inter)))
    metrics = {
        "splittings": splittings,
        "edge_weights": edge_weights,
        "localization_length": localization_length,
    }
    checks = [
        Check("splitting_decreases", all(a > b for a, b in zip(splittings, splittings[1:])), splittings, "strictly decreasing"),
        Check("edge_localization", min(edge_weights) > 0.60, edge_weights, "> 0.60"),
        Check(
            "localization_length",
            abs(localization_length - expected_length) / expected_length < 0.08,
            localization_length,
            expected_length,
            0.08 * expected_length,
        ),
    ]
    return metrics, checks


def transport_ballistic_chain(parameters: dict) -> tuple[dict, list[Check]]:
    lattice = kwant.lattice.chain(norbs=1)
    builder = kwant.Builder()
    for site in range(parameters["device_sites"]):
        builder[lattice(site)] = parameters["onsite"]
        if site:
            builder[lattice(site - 1), lattice(site)] = parameters["hopping"]
    lead = kwant.Builder(kwant.TranslationalSymmetry((-1,)))
    lead[lattice(0)] = parameters["onsite"]
    lead[lattice(0), lattice(-1)] = parameters["hopping"]
    builder.attach_lead(lead)
    builder.attach_lead(lead.reversed())
    system = builder.finalized()
    energies = [-1.5, -0.5, 0.0, 0.5, 1.5]
    transmissions: list[float] = []
    unitarity_errors: list[float] = []
    for energy in energies:
        scattering = kwant.smatrix(system, energy)
        transmissions.append(float(scattering.transmission(1, 0)))
        matrix = scattering.data
        identity = np.eye(matrix.shape[0])
        unitarity_errors.append(float(np.max(np.abs(matrix.conj().T @ matrix - identity))))
    max_transmission_error = float(np.max(np.abs(np.asarray(transmissions) - 1.0)))
    max_unitarity_error = max(unitarity_errors)
    metrics = {
        "energies": energies,
        "transmissions": transmissions,
        "maximum_transmission_error": max_transmission_error,
        "maximum_unitarity_error": max_unitarity_error,
    }
    checks = [
        Check("unit_transmission", max_transmission_error < 1.0e-9, max_transmission_error, 0.0, 1.0e-9),
        Check("scattering_unitarity", max_unitarity_error < 1.0e-9, max_unitarity_error, 0.0, 1.0e-9),
    ]
    return metrics, checks


IMPLEMENTED = {
    "bulk_graphene_dirac_cone": bulk_graphene_dirac_cone,
    "bulk_ssh_polarization": bulk_ssh_polarization,
    "boundary_ssh_edge_localization": boundary_ssh_edge_localization,
    "transport_ballistic_chain": transport_ballistic_chain,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_id")
    args = parser.parse_args()
    manifest = json.loads((ROOT / "benchmark" / "cases.json").read_text())
    case = next((item for item in manifest["cases"] if item["id"] == args.case_id), None)
    if case is None:
        print(json.dumps({"status": "unknown_case", "case_id": args.case_id}))
        return 2
    if "kwant" not in case["backends"]:
        print(
            json.dumps(
                {
                    "schema_version": 1,
                    "case_id": args.case_id,
                    "backend": "kwant",
                    "backend_version": kwant.__version__,
                    "status": "not_applicable",
                    "reason": case["not_applicable"]["kwant"],
                }
            )
        )
        return 0
    implementation = IMPLEMENTED.get(args.case_id)
    if implementation is None:
        print(
            json.dumps(
                {
                    "schema_version": 1,
                    "case_id": args.case_id,
                    "backend": "kwant",
                    "backend_version": kwant.__version__,
                    "status": "not_implemented",
                }
            )
        )
        return 2
    started = time.perf_counter()
    metrics, checks = implementation(case["parameters"])
    payload = result(
        case_id=args.case_id,
        backend="kwant",
        backend_version=kwant.__version__,
        metrics=metrics,
        checks=checks,
        elapsed_seconds=time.perf_counter() - started,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
