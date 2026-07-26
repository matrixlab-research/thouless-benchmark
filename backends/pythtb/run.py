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
from thouless_benchmark.numerics import berry_phase, fhs_chern, minimum_direct_gap  # noqa: E402

SIGMA_X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
SIGMA_Y = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)
SIGMA_Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
IDENTITY_2 = np.eye(2, dtype=complex)
TAU = 2.0 * np.pi


def fourier_model(
    dimension: int,
    onsite: np.ndarray,
    hoppings: list[tuple[tuple[int, ...], np.ndarray]],
) -> TBModel:
    onsite = np.asarray(onsite, dtype=complex)
    states = onsite.shape[0]
    lattice = Lattice(np.eye(dimension), np.zeros((states, dimension)), "all")
    model = TBModel(lattice)
    for row in range(states):
        model.set_onsite(float(onsite[row, row].real), row)
        for column in range(row + 1, states):
            value = onsite[row, column]
            if abs(value) > 1.0e-15:
                model.set_hop(value, row, column, [0] * dimension)
    for offset, matrix in hoppings:
        matrix = np.asarray(matrix, dtype=complex)
        for row in range(states):
            for column in range(states):
                value = matrix[row, column]
                if abs(value) > 1.0e-15:
                    model.set_hop(value, row, column, list(offset))
    return model


def hamiltonian_at(model: TBModel, momentum: np.ndarray) -> np.ndarray:
    values = model.hamiltonian([np.asarray(momentum, dtype=float)], flatten_spin_axis=True)
    return np.asarray(values[0], dtype=complex)


def qwz_model(mass: float) -> TBModel:
    return fourier_model(
        2,
        mass * SIGMA_Z,
        [
            ((1, 0), 0.5 * SIGMA_Z - 0.5j * SIGMA_X),
            ((0, 1), 0.5 * SIGMA_Z - 0.5j * SIGMA_Y),
        ],
    )


def rice_mele_model(theta: float, parameters: dict) -> TBModel:
    mean = parameters["mean_hopping"]
    dimerization = parameters["dimerization"]
    staggering = parameters["staggering"]
    intracell = mean + dimerization * np.cos(theta)
    intercell = mean - dimerization * np.cos(theta)
    onsite = staggering * np.sin(theta) * SIGMA_Z
    return fourier_model(
        1,
        onsite,
        [
            ((1,), np.array([[0.0, 0.0], [intercell, 0.0]], dtype=complex)),
        ],
    ) if abs(intracell) < 1.0e-15 else _add_intracell(
        fourier_model(
            1,
            onsite,
            [((1,), np.array([[0.0, 0.0], [intercell, 0.0]], dtype=complex))],
        ),
        intracell,
    )


def _add_intracell(model: TBModel, amplitude: float) -> TBModel:
    model.set_hop(amplitude, 0, 1, [0])
    return model


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


def bulk_rice_mele_pump(parameters: dict) -> tuple[dict, list[Check]]:
    cache: dict[int, TBModel] = {}
    samples = 31

    def hamiltonian(point: np.ndarray) -> np.ndarray:
        theta_index = int(np.rint((point[1] % 1.0) * samples)) % samples
        model = cache.setdefault(
            theta_index, rice_mele_model(TAU * theta_index / samples, parameters)
        )
        return hamiltonian_at(model, np.array([point[0] % 1.0]))

    chern = fhs_chern(hamiltonian, (samples, samples), occupied=1)
    minimum_gap = np.inf
    for theta_index, model in cache.items():
        del theta_index
        minimum_gap = min(
            minimum_gap,
            minimum_direct_gap(
                lambda momentum, model=model: hamiltonian_at(model, momentum),
                dimension=1,
                samples=81,
                occupied=1,
            ),
        )
    pumped_charge = int(np.rint(chern))
    metrics = {
        "chern_number": chern,
        "pumped_charge": pumped_charge,
        "minimum_cycle_gap": float(minimum_gap),
    }
    checks = [
        Check("quantized_pump", abs(pumped_charge) == 1, pumped_charge, "magnitude 1"),
        Check("chern_integer", abs(chern - pumped_charge) < 1.0e-6, chern, pumped_charge, 1.0e-6),
        Check("cycle_stays_gapped", minimum_gap > 0.5, float(minimum_gap), "> 0.5"),
    ]
    return metrics, checks


def bulk_qwz_phase_diagram(parameters: dict) -> tuple[dict, list[Check]]:
    chern_numbers: list[float] = []
    minimum_gaps: list[float] = []
    for mass in parameters["masses"]:
        model = qwz_model(mass)
        hamiltonian = lambda momentum, model=model: hamiltonian_at(model, momentum)
        chern_numbers.append(fhs_chern(hamiltonian, (31, 31), occupied=1))
        minimum_gaps.append(minimum_direct_gap(hamiltonian, 2, 40, 1))
    rounded = [int(np.rint(value)) for value in chern_numbers]
    expected_magnitudes = [0, 1, 1, 0]
    metrics = {
        "chern_numbers": chern_numbers,
        "rounded_chern_numbers": rounded,
        "minimum_gaps": minimum_gaps,
    }
    checks = [
        Check(
            "phase_sequence",
            [abs(value) for value in rounded] == expected_magnitudes,
            rounded,
            "trivial-Chern-Chern-trivial",
        ),
        Check("opposite_topological_signs", rounded[1] == -rounded[2], rounded[1:3], "opposite"),
        Check("sampled_points_gapped", min(minimum_gaps) > 1.9, minimum_gaps, "> 1.9"),
    ]
    return metrics, checks


def minimal_weyl_model(node: float) -> TBModel:
    onsite = (2.0 - np.cos(node)) * SIGMA_Z
    return fourier_model(
        3,
        onsite,
        [
            ((1, 0, 0), -0.5 * SIGMA_Z - 0.5j * SIGMA_X),
            ((0, 1, 0), -0.5 * SIGMA_Z - 0.5j * SIGMA_Y),
            ((0, 0, 1), 0.5 * SIGMA_Z),
        ],
    )


def bulk_weyl_chirality(parameters: dict) -> tuple[dict, list[Check]]:
    node = parameters["node"]
    model = minimal_weyl_model(node)

    def h3(momentum: np.ndarray) -> np.ndarray:
        return hamiltonian_at(model, momentum)

    node_reduced = node / TAU
    node_gaps = [
        float(np.ptp(np.linalg.eigvalsh(h3(np.array([0.0, 0.0, kz])))))
        for kz in (node_reduced, 1.0 - node_reduced)
    ]
    slice_coordinates = [0.0, 0.25, 0.75]
    slice_chern = []
    for kz in slice_coordinates:
        slice_chern.append(
            fhs_chern(
                lambda momentum, kz=kz: h3(np.array([momentum[0], momentum[1], kz])),
                (31, 31),
                occupied=1,
            )
        )
    rounded = [int(np.rint(value)) for value in slice_chern]
    metrics = {
        "node_positions_reduced": [node_reduced, 1.0 - node_reduced],
        "node_gaps": node_gaps,
        "slice_coordinates": slice_coordinates,
        "slice_chern_numbers": slice_chern,
    }
    checks = [
        Check("node_locations", max(node_gaps) < 1.0e-10, node_gaps, 0.0, 1.0e-10),
        Check(
            "slice_chern_jump",
            rounded[0] == 0 and abs(rounded[1]) == 1 and rounded[1] == rounded[2],
            rounded,
            "trivial between nodes and nonzero outside",
        ),
        Check(
            "opposite_chiralities",
            rounded[1] - rounded[0] == -(rounded[0] - rounded[2]),
            [rounded[1] - rounded[0], rounded[0] - rounded[2]],
            "opposite monopole charges",
        ),
    ]
    return metrics, checks


def nodal_ring_model(mass: float) -> TBModel:
    return fourier_model(
        3,
        mass * SIGMA_X,
        [
            ((1, 0, 0), -0.5 * SIGMA_X),
            ((0, 1, 0), -0.5 * SIGMA_X),
            ((0, 0, 1), -0.5j * SIGMA_Z),
        ],
    )


def bulk_nodal_line_berry_phase(parameters: dict) -> tuple[dict, list[Check]]:
    mass = parameters["mass"]
    model = nodal_ring_model(mass)
    ring_kx = float(np.arccos(mass - 1.0))
    radius = 0.08

    def loop(center_kx: float) -> list[np.ndarray]:
        matrices = []
        for angle in np.linspace(0.0, TAU, 401, endpoint=False):
            momentum = np.array(
                [
                    (center_kx + radius * np.cos(angle)) / TAU,
                    0.0,
                    (radius * np.sin(angle)) / TAU,
                ]
            )
            matrices.append(hamiltonian_at(model, momentum))
        return matrices

    linked = berry_phase(loop(ring_kx), occupied=1)
    unlinked = berry_phase(loop(0.0), occupied=1)
    linked_distance = abs(abs(linked) - np.pi)
    unlinked_distance = abs(unlinked)
    metrics = {
        "ring_point": [ring_kx / TAU, 0.0, 0.0],
        "linked_loop_phase": linked,
        "unlinked_loop_phase": unlinked,
    }
    checks = [
        Check("linked_pi_phase", linked_distance < 2.0e-5, linked, "pi modulo 2pi", 2.0e-5),
        Check("unlinked_trivial_phase", unlinked_distance < 2.0e-5, unlinked, 0.0, 2.0e-5),
    ]
    return metrics, checks


def interpolation_source_model() -> TBModel:
    onsite = 0.23 * SIGMA_Z + 0.17 * SIGMA_X
    return fourier_model(
        2,
        onsite,
        [
            ((1, 0), 0.31 * SIGMA_Z - 0.22j * SIGMA_X),
            ((0, 1), -0.19 * SIGMA_Z - 0.27j * SIGMA_Y),
            ((2, 1), 0.07 * SIGMA_X + 0.05j * SIGMA_Z),
        ],
    )


def bulk_wannier_interpolation(parameters: dict) -> tuple[dict, list[Check]]:
    model = interpolation_source_model()
    nx, ny = parameters["mesh"]
    samples = np.empty((nx, ny, 2, 2), dtype=complex)
    for ix in range(nx):
        for iy in range(ny):
            samples[ix, iy] = hamiltonian_at(model, np.array([ix / nx, iy / ny]))
    coefficients = np.fft.fftn(samples, axes=(0, 1)) / (nx * ny)

    def interpolated(momentum: np.ndarray) -> np.ndarray:
        value = np.zeros((2, 2), dtype=complex)
        for ix in range(nx):
            rx = ix if ix <= nx // 2 else ix - nx
            for iy in range(ny):
                ry = iy if iy <= ny // 2 else iy - ny
                value += coefficients[ix, iy] * np.exp(
                    2.0j * np.pi * (rx * momentum[0] + ry * momentum[1])
                )
        return value

    errors = []
    hermiticity = []
    count = parameters["validation_points"]
    for index in range(count):
        momentum = np.array(
            [((index * 7 + 3) % 37) / 37.0, ((index * 11 + 5) % 41) / 41.0]
        )
        direct = hamiltonian_at(model, momentum)
        estimate = interpolated(momentum)
        errors.append(float(np.max(np.abs(np.linalg.eigvalsh(direct) - np.linalg.eigvalsh(estimate)))))
        hermiticity.append(float(np.max(np.abs(estimate - estimate.conj().T))))
    maximum_error = max(errors)
    maximum_hermiticity_error = max(hermiticity)
    metrics = {
        "maximum_off_mesh_energy_error": maximum_error,
        "maximum_hermiticity_error": maximum_hermiticity_error,
        "validation_points": count,
    }
    checks = [
        Check("off_mesh_energies", maximum_error < 1.0e-9, maximum_error, 0.0, 1.0e-9),
        Check("hermiticity", maximum_hermiticity_error < 1.0e-12, maximum_hermiticity_error, 0.0, 1.0e-12),
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
    "bulk_rice_mele_pump": bulk_rice_mele_pump,
    "bulk_qwz_phase_diagram": bulk_qwz_phase_diagram,
    "bulk_weyl_chirality": bulk_weyl_chirality,
    "bulk_nodal_line_berry_phase": bulk_nodal_line_berry_phase,
    "bulk_wannier_interpolation": bulk_wannier_interpolation,
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
