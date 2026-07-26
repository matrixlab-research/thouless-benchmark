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
from thouless_benchmark.numerics import berry_phase, fhs_chern, minimum_direct_gap  # noqa: E402

warnings.filterwarnings("ignore", message="MUMPS is not available")

SIGMA_X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
SIGMA_Y = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)
SIGMA_Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
TAU = 2.0 * np.pi


def fourier_system(
    dimension: int,
    onsite: np.ndarray,
    hoppings: list[tuple[tuple[int, ...], np.ndarray]],
):
    onsite = np.asarray(onsite, dtype=complex)
    states = onsite.shape[0]
    primitive = np.eye(dimension)
    lattice = kwant.lattice.general(primitive, [np.zeros(dimension)], norbs=states)
    family = lattice.sublattices[0]
    symmetry = kwant.TranslationalSymmetry(*[tuple(vector) for vector in primitive])
    builder = kwant.Builder(symmetry)
    origin = family(*([0] * dimension))
    builder[origin] = onsite
    for offset, matrix in hoppings:
        builder[origin, family(*offset)] = np.asarray(matrix, dtype=complex)
    return kwant.wraparound.wraparound(builder).finalized()


def hamiltonian_at(system, momentum: np.ndarray) -> np.ndarray:
    names = ("k_x", "k_y", "k_z")
    params = {
        names[axis]: float(TAU * value)
        for axis, value in enumerate(np.asarray(momentum, dtype=float))
    }
    return np.asarray(system.hamiltonian_submatrix(params=params), dtype=complex)


def qwz_system(mass: float):
    return fourier_system(
        2,
        mass * SIGMA_Z,
        [
            ((1, 0), 0.5 * SIGMA_Z - 0.5j * SIGMA_X),
            ((0, 1), 0.5 * SIGMA_Z - 0.5j * SIGMA_Y),
        ],
    )


def rice_mele_system(theta: float, parameters: dict):
    mean = parameters["mean_hopping"]
    dimerization = parameters["dimerization"]
    staggering = parameters["staggering"]
    intracell = mean + dimerization * np.cos(theta)
    intercell = mean - dimerization * np.cos(theta)
    onsite = staggering * np.sin(theta) * SIGMA_Z + intracell * SIGMA_X
    return fourier_system(
        1,
        onsite,
        [((1,), np.array([[0.0, 0.0], [intercell, 0.0]], dtype=complex))],
    )


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


def bulk_rice_mele_pump(parameters: dict) -> tuple[dict, list[Check]]:
    cache: dict[int, object] = {}
    samples = 31

    def hamiltonian(point: np.ndarray) -> np.ndarray:
        theta_index = int(np.rint((point[1] % 1.0) * samples)) % samples
        system = cache.setdefault(
            theta_index, rice_mele_system(TAU * theta_index / samples, parameters)
        )
        return hamiltonian_at(system, np.array([point[0] % 1.0]))

    chern = fhs_chern(hamiltonian, (samples, samples), occupied=1)
    minimum_gap = np.inf
    for system in cache.values():
        minimum_gap = min(
            minimum_gap,
            minimum_direct_gap(
                lambda momentum, system=system: hamiltonian_at(system, momentum),
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
        system = qwz_system(mass)
        hamiltonian = lambda momentum, system=system: hamiltonian_at(system, momentum)
        chern_numbers.append(fhs_chern(hamiltonian, (31, 31), occupied=1))
        minimum_gaps.append(minimum_direct_gap(hamiltonian, 2, 40, 1))
    rounded = [int(np.rint(value)) for value in chern_numbers]
    metrics = {
        "chern_numbers": chern_numbers,
        "rounded_chern_numbers": rounded,
        "minimum_gaps": minimum_gaps,
    }
    checks = [
        Check(
            "phase_sequence",
            [abs(value) for value in rounded] == [0, 1, 1, 0],
            rounded,
            "trivial-Chern-Chern-trivial",
        ),
        Check("opposite_topological_signs", rounded[1] == -rounded[2], rounded[1:3], "opposite"),
        Check("sampled_points_gapped", min(minimum_gaps) > 1.9, minimum_gaps, "> 1.9"),
    ]
    return metrics, checks


def minimal_weyl_system(node: float):
    return fourier_system(
        3,
        (2.0 - np.cos(node)) * SIGMA_Z,
        [
            ((1, 0, 0), -0.5 * SIGMA_Z - 0.5j * SIGMA_X),
            ((0, 1, 0), -0.5 * SIGMA_Z - 0.5j * SIGMA_Y),
            ((0, 0, 1), 0.5 * SIGMA_Z),
        ],
    )


def bulk_weyl_chirality(parameters: dict) -> tuple[dict, list[Check]]:
    node = parameters["node"]
    system = minimal_weyl_system(node)
    h3 = lambda momentum: hamiltonian_at(system, momentum)
    node_reduced = node / TAU
    node_gaps = [
        float(np.ptp(np.linalg.eigvalsh(h3(np.array([0.0, 0.0, kz])))))
        for kz in (node_reduced, 1.0 - node_reduced)
    ]
    slice_coordinates = [0.0, 0.25, 0.75]
    slice_chern = [
        fhs_chern(
            lambda momentum, kz=kz: h3(np.array([momentum[0], momentum[1], kz])),
            (31, 31),
            occupied=1,
        )
        for kz in slice_coordinates
    ]
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


def nodal_ring_system(mass: float):
    return fourier_system(
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
    system = nodal_ring_system(mass)
    ring_kx = float(np.arccos(mass - 1.0))
    radius = 0.08

    def loop(center_kx: float) -> list[np.ndarray]:
        return [
            hamiltonian_at(
                system,
                np.array(
                    [
                        (center_kx + radius * np.cos(angle)) / TAU,
                        0.0,
                        (radius * np.sin(angle)) / TAU,
                    ]
                ),
            )
            for angle in np.linspace(0.0, TAU, 401, endpoint=False)
        ]

    linked = berry_phase(loop(ring_kx), occupied=1)
    unlinked = berry_phase(loop(0.0), occupied=1)
    metrics = {
        "ring_point": [ring_kx / TAU, 0.0, 0.0],
        "linked_loop_phase": linked,
        "unlinked_loop_phase": unlinked,
    }
    checks = [
        Check("linked_pi_phase", abs(abs(linked) - np.pi) < 2.0e-5, linked, "pi modulo 2pi", 2.0e-5),
        Check("unlinked_trivial_phase", abs(unlinked) < 2.0e-5, unlinked, 0.0, 2.0e-5),
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
    "bulk_rice_mele_pump": bulk_rice_mele_pump,
    "bulk_qwz_phase_diagram": bulk_qwz_phase_diagram,
    "bulk_weyl_chirality": bulk_weyl_chirality,
    "bulk_nodal_line_berry_phase": bulk_nodal_line_berry_phase,
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
