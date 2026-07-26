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
from thouless_benchmark.numerics import (  # noqa: E402
    berry_curvature_dipole,
    berry_phase,
    fhs_chern,
    minimum_direct_gap,
    nested_wilson_polarizations,
    wilson_centers,
)

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


def haldane_model(parameters: dict) -> TBModel:
    t1 = parameters["t1"]
    t2 = parameters["t2"] * np.sin(parameters["phase"])
    onsite = parameters["mass"] * SIGMA_Z + t1 * SIGMA_X
    hoppings = []
    for offset, chirality in [
        ((1, 0), -1.0),
        ((0, 1), 1.0),
        ((1, -1), 1.0),
    ]:
        matrix = np.diag([-1.0j * chirality * t2, 1.0j * chirality * t2])
        if offset in ((1, 0), (0, 1)):
            matrix[0, 1] += t1
        hoppings.append((offset, matrix))
    return fourier_model(2, onsite, hoppings)


def bulk_haldane_chern_transition(parameters: dict) -> tuple[dict, list[Check]]:
    model = haldane_model(parameters)
    hamiltonian = lambda momentum: hamiltonian_at(model, momentum)
    chern = fhs_chern(hamiltonian, (41, 41), occupied=1)
    dirac_points = [np.array([1.0 / 3.0, 2.0 / 3.0]), np.array([2.0 / 3.0, 1.0 / 3.0])]
    dirac_masses = [
        float((hamiltonian(point)[0, 0] - hamiltonian(point)[1, 1]).real / 2.0)
        for point in dirac_points
    ]
    minimum_gap = minimum_direct_gap(hamiltonian, 2, 60, 1)
    predicted_chern = int(np.sign(dirac_masses[0]) - np.sign(dirac_masses[1])) // 2
    rounded = int(np.rint(chern))
    metrics = {
        "dirac_masses": dirac_masses,
        "minimum_gap": minimum_gap,
        "chern_number": chern,
        "predicted_chern_from_masses": predicted_chern,
    }
    checks = [
        Check("opposite_dirac_masses", dirac_masses[0] * dirac_masses[1] < 0.0, dirac_masses, "opposite signs"),
        Check("chern_from_masses", rounded == predicted_chern, rounded, predicted_chern),
        Check("chern_integer", abs(chern - rounded) < 2.0e-6, chern, rounded, 2.0e-6),
        Check("positive_bulk_gap", minimum_gap > 1.0, minimum_gap, "> 1.0"),
    ]
    return metrics, checks


def kagome_soc_model(parameters: dict) -> TBModel:
    hopping = parameters["t"] + 1.0j * parameters["lambda"]
    onsite = np.zeros((3, 3), dtype=complex)
    for first, second in ((0, 1), (0, 2), (1, 2)):
        onsite[first, second] = hopping
        onsite[second, first] = hopping.conjugate()
    hoppings = []
    for offset, first, second in [
        ((1, 0), 0, 1),
        ((0, 1), 0, 2),
        ((1, -1), 1, 2),
    ]:
        matrix = np.zeros((3, 3), dtype=complex)
        matrix[first, second] = hopping
        hoppings.append((offset, matrix))
    return fourier_model(2, onsite, hoppings)


def bulk_kagome_soc_chern(parameters: dict) -> tuple[dict, list[Check]]:
    model = kagome_soc_model(parameters)
    hamiltonian = lambda momentum: hamiltonian_at(model, momentum)
    cumulative_one = fhs_chern(hamiltonian, (41, 41), occupied=1)
    cumulative_two = fhs_chern(hamiltonian, (41, 41), occupied=2)
    band_chern = [cumulative_one, cumulative_two - cumulative_one, -cumulative_two]
    rounded = [int(np.rint(value)) for value in band_chern]
    energies = []
    minimum_gaps = [np.inf, np.inf]
    for ix in range(50):
        for iy in range(50):
            values = np.linalg.eigvalsh(hamiltonian(np.array([ix / 50.0, iy / 50.0])))
            energies.append(values)
            minimum_gaps[0] = min(minimum_gaps[0], float(values[1] - values[0]))
            minimum_gaps[1] = min(minimum_gaps[1], float(values[2] - values[1]))
    energies = np.asarray(energies)
    bandwidths = np.ptp(energies, axis=0).tolist()
    metrics = {
        "band_chern_numbers": band_chern,
        "rounded_band_chern_numbers": rounded,
        "minimum_gaps": minimum_gaps,
        "bandwidths": bandwidths,
    }
    checks = [
        Check("nonzero_band_chern", any(abs(value) == 1 for value in rounded), rounded, "at least one nonzero band"),
        Check("chern_sum_rule", sum(rounded) == 0, sum(rounded), 0),
        Check("positive_gaps", min(minimum_gaps) > 0.05, minimum_gaps, "> 0.05"),
        Check("finite_bandwidths", all(value > 0.1 for value in bandwidths), bandwidths, "> 0.1"),
    ]
    return metrics, checks


def kane_mele_model(parameters: dict, rashba: float | None = None) -> TBModel:
    tau_x, tau_y, tau_z = SIGMA_X, SIGMA_Y, SIGMA_Z
    spin_x, spin_y, spin_z = SIGMA_X, SIGMA_Y, SIGMA_Z
    identity = IDENTITY_2
    t = parameters["t"]
    intrinsic = parameters["lambda_so"]
    rashba = parameters["lambda_r"] if rashba is None else rashba
    mass = parameters["mass"]
    onsite = (
        mass * np.kron(tau_z, identity)
        + t * np.kron(tau_x, identity)
        + rashba * np.kron(tau_y, spin_x)
    )
    hoppings = []
    for offset, chirality in [
        ((1, 0), -1.0),
        ((0, 1), 1.0),
        ((1, -1), 1.0),
    ]:
        matrix = -1.0j * chirality * intrinsic * np.kron(tau_z, spin_z)
        if offset in ((1, 0), (0, 1)):
            nearest = np.zeros((4, 4), dtype=complex)
            nearest[0:2, 2:4] = t * identity
            matrix += nearest
        hoppings.append((offset, matrix))
    return fourier_model(2, onsite, hoppings)


def bulk_kane_mele_z2(parameters: dict) -> tuple[dict, list[Check]]:
    spin_conserved = kane_mele_model(parameters, rashba=0.0)
    h0 = lambda momentum: hamiltonian_at(spin_conserved, momentum)
    spin_up = fhs_chern(lambda k: h0(k)[np.ix_([0, 2], [0, 2])], (31, 31), 1)
    spin_down = fhs_chern(lambda k: h0(k)[np.ix_([1, 3], [1, 3])], (31, 31), 1)
    spin_chern = int(np.rint((spin_up - spin_down) / 2.0))
    model = kane_mele_model(parameters)
    hamiltonian = lambda momentum: hamiltonian_at(model, momentum)
    minimum_gap = minimum_direct_gap(hamiltonian, 2, 40, 2)
    transverse = np.linspace(0.0, 0.5, 21)
    centers = np.asarray(
        [
            wilson_centers(
                hamiltonian,
                loop_axis=0,
                fixed_momentum=np.array([0.0, ky]),
                loop_samples=81,
                occupied=2,
            )
            for ky in transverse
        ]
    )
    endpoint_separation = float(abs(centers[-1, 1] - centers[-1, 0]))
    midpoint_spread = float(np.max(centers[:, 1] - centers[:, 0]))
    z2 = abs(spin_chern) % 2
    metrics = {
        "spin_chern_numbers_at_zero_rashba": [spin_up, spin_down],
        "z2": z2,
        "minimum_rashba_gap": minimum_gap,
        "wilson_centers": centers.tolist(),
        "endpoint_separation": endpoint_separation,
        "maximum_wannier_separation": midpoint_spread,
    }
    checks = [
        Check("time_reversal_spin_chern_pair", int(np.rint(spin_up)) == -int(np.rint(spin_down)), [spin_up, spin_down], "opposite"),
        Check("nontrivial_z2", z2 == 1, z2, 1),
        Check("rashba_gap_stays_open", minimum_gap > 0.5, minimum_gap, "> 0.5"),
        Check("wilson_partner_switching", endpoint_separation < 1.0e-6 and midpoint_spread > 0.4, [endpoint_separation, midpoint_spread], "degenerate endpoint with separated flow"),
    ]
    return metrics, checks


def bbh_model(parameters: dict) -> TBModel:
    tau_1, tau_2, tau_3 = SIGMA_X, SIGMA_Y, SIGMA_Z
    sigma_0, sigma_1, sigma_2, sigma_3 = IDENTITY_2, SIGMA_X, SIGMA_Y, SIGMA_Z
    gamma_1 = -np.kron(tau_2, sigma_1)
    gamma_2 = -np.kron(tau_2, sigma_2)
    gamma_3 = -np.kron(tau_2, sigma_3)
    gamma_4 = np.kron(tau_1, sigma_0)
    onsite = parameters["gamma_x"] * gamma_4 + parameters["gamma_y"] * gamma_2
    hopping_x = 0.5 * parameters["lambda_x"] * gamma_4 - 0.5j * parameters["lambda_x"] * gamma_3
    hopping_y = 0.5 * parameters["lambda_y"] * gamma_2 - 0.5j * parameters["lambda_y"] * gamma_1
    return fourier_model(2, onsite, [((1, 0), hopping_x), ((0, 1), hopping_y)])


def bulk_bbh_nested_wilson(parameters: dict) -> tuple[dict, list[Check]]:
    model = bbh_model(parameters)
    hamiltonian = lambda momentum: hamiltonian_at(model, momentum)
    minimum_gap = minimum_direct_gap(hamiltonian, 2, 24, 2)
    centers, sector_polarizations = nested_wilson_polarizations(
        hamiltonian, loop_samples=51, transverse_samples=51, occupied=2
    )
    wannier_gap = float(np.min(centers[:, 1] - centers[:, 0]))
    quadrupole = float(np.mod(np.mean(sector_polarizations), 1.0))
    metrics = {
        "minimum_bulk_gap": minimum_gap,
        "minimum_wannier_gap": wannier_gap,
        "sector_polarizations": sector_polarizations.tolist(),
        "quadrupole": quadrupole,
    }
    checks = [
        Check("bulk_gap", minimum_gap > 1.3, minimum_gap, "> 1.3"),
        Check("wannier_gap", wannier_gap > 0.45, wannier_gap, "> 0.45"),
        Check("nested_sector_polarizations", bool(np.allclose(sector_polarizations, [0.5, 0.5], atol=3.0e-5)), sector_polarizations.tolist(), [0.5, 0.5], 3.0e-5),
        Check("quadrupole", abs(quadrupole - 0.5) < 3.0e-5, quadrupole, 0.5, 3.0e-5),
    ]
    return metrics, checks


def tilted_dirac_model(parameters: dict, tilt: float) -> TBModel:
    mass = parameters["mass"]
    onsite = (mass + 2.0) * SIGMA_Z
    hopping_x = -0.5 * SIGMA_Z - 0.5j * SIGMA_X - 0.5j * tilt * IDENTITY_2
    hopping_y = -0.5 * SIGMA_Z - 0.5j * SIGMA_Y
    return fourier_model(2, onsite, [((1, 0), hopping_x), ((0, 1), hopping_y)])


def bulk_tilted_dirac_berry_dipole(parameters: dict) -> tuple[dict, list[Check]]:
    chemical_potentials = [0.4, 0.5, 0.6, 0.8, 1.0]
    positive = tilted_dirac_model(parameters, parameters["tilt"])
    negative = tilted_dirac_model(parameters, -parameters["tilt"])
    positive_values = berry_curvature_dipole(
        lambda momentum: hamiltonian_at(positive, momentum),
        chemical_potentials,
        temperature=parameters["temperature"],
        samples=51,
    )
    negative_values = berry_curvature_dipole(
        lambda momentum: hamiltonian_at(negative, momentum),
        chemical_potentials,
        temperature=parameters["temperature"],
        samples=51,
    )
    odd_error = float(np.max(np.abs(positive_values + negative_values)))
    peak_index = int(np.argmax(np.abs(positive_values)))
    metrics = {
        "chemical_potentials": chemical_potentials,
        "positive_tilt_dipole": positive_values.tolist(),
        "negative_tilt_dipole": negative_values.tolist(),
        "odd_reversal_error": odd_error,
        "peak_chemical_potential": chemical_potentials[peak_index],
    }
    checks = [
        Check("odd_under_tilt_reversal", odd_error < 5.0e-4, odd_error, 0.0, 5.0e-4),
        Check("finite_nonlinear_response", float(np.max(np.abs(positive_values))) > 0.5, float(np.max(np.abs(positive_values))), "> 0.5"),
        Check("band_edge_variation", peak_index in (1, 2, 3), chemical_potentials[peak_index], "near the band edge"),
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


def boundary_haldane_ribbon_flow(parameters: dict) -> tuple[dict, list[Check]]:
    width = parameters["width"]
    ribbon = haldane_model(parameters).cut_piece(width, 1, glue_edges=False)
    momenta = np.linspace(0.4, 0.55, 301)
    best = None
    for momentum in momenta:
        hamiltonian = hamiltonian_at(ribbon, np.array([momentum]))
        values, vectors = np.linalg.eigh(hamiltonian)
        pair = np.argsort(np.abs(values))[:2]
        score = float(np.max(np.abs(values[pair])))
        if best is None or score < best[0]:
            best = (score, momentum, values, vectors, pair)
    _, crossing_momentum, values, vectors, pair = best
    lower_indices = np.arange(4)
    upper_indices = np.arange(2 * width - 4, 2 * width)
    lower_state = max(
        pair, key=lambda state: np.sum(np.abs(vectors[lower_indices, state]) ** 2)
    )
    upper_state = max(
        pair, key=lambda state: np.sum(np.abs(vectors[upper_indices, state]) ** 2)
    )
    ordered_states = [lower_state, upper_state]
    edge_weights = [
        float(np.sum(np.abs(vectors[indices, state]) ** 2))
        for state, indices in zip(ordered_states, (lower_indices, upper_indices))
    ]
    crossing_energies = [float(values[state]) for state in ordered_states]
    delta = 1.0e-4
    velocities = []
    for state in ordered_states:
        reference = vectors[:, state]
        branch_energies = []
        for momentum in (crossing_momentum - delta, crossing_momentum + delta):
            shifted_values, shifted_vectors = np.linalg.eigh(
                hamiltonian_at(ribbon, np.array([momentum]))
            )
            overlap = np.abs(shifted_vectors.conj().T @ reference) ** 2
            branch_energies.append(float(shifted_values[int(np.argmax(overlap))]))
        velocities.append((branch_energies[1] - branch_energies[0]) / (2.0 * delta))
    bulk_chern = fhs_chern(
        lambda momentum: hamiltonian_at(haldane_model(parameters), momentum),
        (31, 31),
        occupied=1,
    )
    metrics = {
        "bulk_chern_number": bulk_chern,
        "crossing_momentum": crossing_momentum,
        "crossing_energies": crossing_energies,
        "edge_weights": edge_weights,
        "edge_velocities": velocities,
        "in_gap_edge_branch_count": 2,
    }
    checks = [
        Check("nontrivial_bulk", abs(int(np.rint(bulk_chern))) == 1, bulk_chern, "magnitude 1"),
        Check("two_in_gap_branches", max(abs(value) for value in crossing_energies) < 1.0e-2, crossing_energies, "two near-zero branches"),
        Check("opposite_edge_localization", min(edge_weights) > 0.9, edge_weights, "> 0.9"),
        Check("chiral_spectral_flow", velocities[0] * velocities[1] < 0.0 and min(abs(value) for value in velocities) > 1.0, velocities, "opposite nonzero velocities"),
    ]
    return metrics, checks


def graphene_nanoribbon_model() -> TBModel:
    lattice = Lattice(
        [[np.sqrt(3.0) / 2.0, 1.5], [-np.sqrt(3.0) / 2.0, 1.5]],
        [[0.0, 0.0], [0.0, 1.0 / 3.0]],
        "all",
    )
    model = TBModel(lattice)
    for offset in ([0, 0], [-1, 0], [0, -1]):
        model.set_hop(-1.0, 0, 1, offset)
    return model


def boundary_graphene_terminations(parameters: dict) -> tuple[dict, list[Check]]:
    widths = parameters["widths"]
    model = graphene_nanoribbon_model()
    zigzag_minimum_gaps = []
    zigzag_edge_weights = []
    armchair_gaps = []
    for width in widths:
        zigzag = model.cut_piece(width, 1, glue_edges=False)
        minimum_gap = np.inf
        maximum_edge_weight = 0.0
        for momentum in np.linspace(0.0, 1.0, 301, endpoint=False):
            values, vectors = np.linalg.eigh(
                hamiltonian_at(zigzag, np.array([momentum]))
            )
            gap = float(values[width] - values[width - 1])
            pair = np.argsort(np.abs(values))[:2]
            edge_weight = float(
                np.mean(
                    np.sum(
                        np.abs(vectors[[0, 1, -2, -1]][:, pair]) ** 2,
                        axis=0,
                    )
                )
            )
            minimum_gap = min(minimum_gap, gap)
            maximum_edge_weight = max(maximum_edge_weight, edge_weight)
        zigzag_minimum_gaps.append(minimum_gap)
        zigzag_edge_weights.append(maximum_edge_weight)

        armchair_supercell = model.make_supercell([[1, 1], [-1, 1]])
        armchair = armchair_supercell.cut_piece(width // 2, 1, glue_edges=False)
        armchair_values = np.linalg.eigvalsh(
            hamiltonian_at(armchair, np.array([0.0]))
        )
        armchair_gaps.append(
            float(armchair_values[width] - armchair_values[width - 1])
        )
    scaled_armchair_gaps = [
        width * gap for width, gap in zip(widths, armchair_gaps)
    ]
    relative_spread = (
        max(scaled_armchair_gaps) - min(scaled_armchair_gaps)
    ) / np.mean(scaled_armchair_gaps)
    metrics = {
        "widths": widths,
        "zigzag_minimum_gaps": zigzag_minimum_gaps,
        "zigzag_edge_weights": zigzag_edge_weights,
        "armchair_gaps": armchair_gaps,
        "width_scaled_armchair_gaps": scaled_armchair_gaps,
        "armchair_scaling_spread": relative_spread,
    }
    checks = [
        Check("zigzag_edge_band", bool(max(zigzag_minimum_gaps) < 1.0e-6), zigzag_minimum_gaps, "gapless"),
        Check("zigzag_edge_localization", bool(min(zigzag_edge_weights) > 0.95), zigzag_edge_weights, "> 0.95"),
        Check("armchair_finite_gaps", bool(min(armchair_gaps) > 0.1), armchair_gaps, "> 0.1"),
        Check("armchair_inverse_width_scaling", bool(all(left > right for left, right in zip(armchair_gaps, armchair_gaps[1:])) and relative_spread < 0.08), relative_spread, "< 0.08"),
    ]
    return metrics, checks


def boundary_bbh_corner_modes(parameters: dict) -> tuple[dict, list[Check]]:
    cells_x, cells_y = parameters["cells"]
    finite = (
        bbh_model(parameters)
        .cut_piece(cells_x, 0, glue_edges=False)
        .cut_piece(cells_y, 1, glue_edges=False)
    )
    hamiltonian = finite.hamiltonian(None, flatten_spin_axis=True)
    values, vectors = np.linalg.eigh(hamiltonian)
    order = np.argsort(np.abs(values))
    midgap = order[:4]
    next_gap = float(abs(values[order[4]]))
    positions = np.asarray(finite.lattice.orb_vecs)
    corner_orbitals = np.where(
        ((positions[:, 0] < 0.5) | (positions[:, 0] > cells_x - 1.5))
        & ((positions[:, 1] < 0.5) | (positions[:, 1] > cells_y - 1.5))
    )[0]
    corner_weights = [
        float(np.sum(np.abs(vectors[corner_orbitals, state]) ** 2))
        for state in midgap
    ]
    sublattice_support = [
        float(
            sum(
                np.sum(np.abs(vectors[orbital::4, state]) ** 2)
                for state in midgap
            )
        )
        for orbital in range(4)
    ]
    midgap_energies = values[midgap].tolist()
    metrics = {
        "midgap_energies": midgap_energies,
        "midgap_count": 4,
        "next_state_absolute_energy": next_gap,
        "corner_weights": corner_weights,
        "sublattice_projector_support": sublattice_support,
    }
    checks = [
        Check("four_midgap_modes", max(abs(value) for value in midgap_energies) < 1.0e-2 and next_gap > 0.5, midgap_energies, "four isolated midgap states"),
        Check("corner_localization", min(corner_weights) > 0.55, corner_weights, "> 0.55"),
        Check("sublattice_support", bool(np.allclose(sublattice_support, np.ones(4), atol=2.0e-5)), sublattice_support, [1.0] * 4, 2.0e-5),
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
    "bulk_haldane_chern_transition": bulk_haldane_chern_transition,
    "bulk_qwz_phase_diagram": bulk_qwz_phase_diagram,
    "bulk_kane_mele_z2": bulk_kane_mele_z2,
    "bulk_kagome_soc_chern": bulk_kagome_soc_chern,
    "bulk_bbh_nested_wilson": bulk_bbh_nested_wilson,
    "bulk_weyl_chirality": bulk_weyl_chirality,
    "bulk_nodal_line_berry_phase": bulk_nodal_line_berry_phase,
    "bulk_tilted_dirac_berry_dipole": bulk_tilted_dirac_berry_dipole,
    "bulk_wannier_interpolation": bulk_wannier_interpolation,
    "boundary_ssh_edge_localization": boundary_ssh_edge_localization,
    "boundary_haldane_ribbon_flow": boundary_haldane_ribbon_flow,
    "boundary_graphene_terminations": boundary_graphene_terminations,
    "boundary_bbh_corner_modes": boundary_bbh_corner_modes,
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
