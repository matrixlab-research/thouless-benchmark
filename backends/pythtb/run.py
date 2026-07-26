#!/usr/bin/env python3
"""Original PythTB 2.0 benchmark adapter."""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pythtb
from pythtb import Lattice, TBModel

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from thouless_benchmark.result import Check, result  # noqa: E402


def graphene_model(t: float) -> TBModel:
    lattice = Lattice(np.eye(2), np.array([[0.0, 0.0], [0.0, 0.0]]), "all")
    model = TBModel(lattice)
    for cell in ([0, 0], [-1, 0], [0, -1]):
        model.set_hop(t, 0, 1, cell)
    return model


def ssh_model(intracell: float, intercell: float) -> TBModel:
    # A periodic gauge with both orbitals at the cell origin makes the winding
    # of the off-diagonal block an integer. The finite-chain localization
    # calculation below is independent of this embedding choice.
    lattice = Lattice(np.array([[1.0]]), np.array([[0.0], [0.0]]), "all")
    model = TBModel(lattice)
    model.set_hop(intracell, 0, 1, [0])
    model.set_hop(intercell, 1, 0, [1])
    return model


def bulk_graphene_dirac_cone(parameters: dict) -> tuple[dict, list[Check]]:
    model = graphene_model(parameters["t"])
    gamma = np.asarray(model.solve_ham([[0.0, 0.0]])).reshape(-1)
    k_point = np.array([1.0 / 3.0, 2.0 / 3.0])
    dirac = np.asarray(model.solve_ham([k_point])).reshape(-1)
    delta = 1.0e-5
    shifted = np.asarray(model.solve_ham([k_point + [delta, 0.0]])).reshape(-1)
    velocity_reduced = float(shifted[-1] / delta)
    gamma_expected = 3.0 * abs(parameters["t"])
    gap = float(dirac[-1] - dirac[0])
    metrics = {
        "gamma_eigenvalues": gamma.tolist(),
        "dirac_gap": gap,
        "reduced_coordinate_velocity": velocity_reduced,
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
        Check("linear_dispersion", abs(velocity_reduced) > 1.0, velocity_reduced, "nonzero"),
    ]
    return metrics, checks


def bulk_ssh_polarization(parameters: dict) -> tuple[dict, list[Check]]:
    intra = parameters["intracell"]
    inter = parameters["intercell"]
    model = ssh_model(intra, inter)
    k_points = np.arange(401, dtype=float)[:, None] / 400.0
    hamiltonians = model.hamiltonian(k_points, flatten_spin_axis=True)
    off_diagonal = hamiltonians[:, 0, 1]
    phase = np.unwrap(np.angle(np.r_[off_diagonal, off_diagonal[:1]]))
    winding = int(np.rint((phase[-1] - phase[0]) / (2.0 * np.pi)))
    polarization = (winding / 2.0) % 1.0
    gaps = np.linalg.eigvalsh(hamiltonians)
    minimum_gap = float(np.min(gaps[:, 1] - gaps[:, 0]))
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
        finite = ssh_model(intra, inter).make_finite([0], [cells])
        values, vectors = finite.solve_ham(return_eigvecs=True)
        order = np.argsort(np.abs(values))
        pair = order[:2]
        splittings.append(float(np.max(np.abs(values[pair]))))
        weights = np.abs(vectors[pair]) ** 2
        edge_weights.append(float(np.mean(np.sum(weights[:, [0, 1, -2, -1]], axis=1))))
    cells = np.asarray(parameters["cells"], dtype=float)
    slope, _ = np.polyfit(cells, np.log(np.maximum(splittings, 1.0e-300)), 1)
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


IMPLEMENTED = {
    "bulk_graphene_dirac_cone": bulk_graphene_dirac_cone,
    "bulk_ssh_polarization": bulk_ssh_polarization,
    "boundary_ssh_edge_localization": boundary_ssh_edge_localization,
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
    if "pythtb" not in case["backends"]:
        print(
            json.dumps(
                {
                    "schema_version": 1,
                    "case_id": args.case_id,
                    "backend": "pythtb",
                    "backend_version": pythtb.__version__,
                    "status": "not_applicable",
                    "reason": case["not_applicable"]["pythtb"],
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
                    "backend": "pythtb",
                    "backend_version": pythtb.__version__,
                    "status": "not_implemented",
                }
            )
        )
        return 2
    started = time.perf_counter()
    metrics, checks = implementation(case["parameters"])
    payload = result(
        case_id=args.case_id,
        backend="pythtb",
        backend_version=pythtb.__version__,
        metrics=metrics,
        checks=checks,
        elapsed_seconds=time.perf_counter() - started,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
