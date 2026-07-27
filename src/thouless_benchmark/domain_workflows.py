"""Backend-independent observables for package-built domain Hamiltonians.

The callbacks in this module must return matrices reconstructed from the named
backend.  This module performs only gauge-invariant postprocessing and analytic
gates; it is not a replacement Hamiltonian implementation.
"""

from __future__ import annotations

import math
from collections.abc import Callable

import numpy as np

from .numerics import fhs_chern
from .result import Check


MatrixBuilder = Callable[[np.ndarray], np.ndarray]

SIGMA_X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
SIGMA_Y = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)
SIGMA_Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)


def _trapezoid(values: np.ndarray, grid: np.ndarray) -> float:
    """Support NumPy 1.26 (`trapz`) and NumPy 2.5 (`trapezoid`)."""

    if hasattr(np, "trapezoid"):
        return float(np.trapezoid(values, grid))
    return float(np.trapz(values, grid))


def spectral_reliability(
    build_matrix: MatrixBuilder,
    periodic_energy: Callable[[float], float],
    open_chain: Callable[[int], np.ndarray],
    parameters: dict,
) -> tuple[dict, list[Check]]:
    """Projector, DOS sum-rule, and Bloch-to-open spectral checks."""

    reference = np.diag([-1.0, -1.0, 1.0, 1.0]).astype(complex)
    matrix = build_matrix(reference)
    values, vectors = np.linalg.eigh(matrix)
    occupied = vectors[:, np.argsort(values)[:2]]
    projector = occupied @ occupied.conj().T
    angle = 0.713
    rotation = np.array(
        [
            [np.cos(angle), np.sin(angle)],
            [-np.sin(angle), np.cos(angle)],
        ],
        dtype=complex,
    )
    rotated = occupied @ rotation
    projector_error = float(np.max(np.abs(projector - rotated @ rotated.conj().T)))

    momentum_mesh = int(parameters["momentum_mesh"])
    momenta = 2.0 * np.pi * np.arange(momentum_mesh) / momentum_mesh
    square_energies = np.asarray(
        [
            periodic_energy(float(kx)) + periodic_energy(float(ky))
            for kx in momenta
            for ky in momenta
        ]
    )
    eta = float(parameters["broadening"])
    energy_grid = np.linspace(-4.8, 4.8, int(parameters["energy_samples"]))
    gaussian = np.exp(
        -0.5 * ((energy_grid[:, None] - square_energies[None, :]) / eta) ** 2
    ) / (math.sqrt(2.0 * math.pi) * eta)
    dos = np.mean(gaussian, axis=1)
    integrated_dos = _trapezoid(dos, energy_grid)

    chain_momenta = 2.0 * np.pi * np.arange(4096) / 4096.0
    chain_energies = np.asarray([periodic_energy(float(k)) for k in chain_momenta])
    ldos_grid = np.linspace(-1.7, 1.7, 121)
    bloch_ldos = np.mean(
        np.exp(-0.5 * ((ldos_grid[:, None] - chain_energies[None, :]) / eta) ** 2)
        / (math.sqrt(2.0 * math.pi) * eta),
        axis=1,
    )
    ldos_errors: list[float] = []
    for size in parameters["open_chain_sizes"]:
        finite = open_chain(int(size))
        values, vectors = np.linalg.eigh(finite)
        center = int(size) // 2
        weights = np.abs(vectors[center, :]) ** 2
        finite_ldos = np.sum(
            weights[None, :]
            * np.exp(-0.5 * ((ldos_grid[:, None] - values[None, :]) / eta) ** 2)
            / (math.sqrt(2.0 * math.pi) * eta),
            axis=1,
        )
        ldos_errors.append(float(np.sqrt(np.mean((finite_ldos - bloch_ldos) ** 2))))

    metrics = {
        "projector_gauge_error": projector_error,
        "integrated_dos_states_per_cell": integrated_dos,
        "open_to_bloch_ldos_rms_errors": ldos_errors,
    }
    checks = [
        Check("degenerate_projector_gauge_invariance", projector_error < 1.0e-12, projector_error, 0.0, 1.0e-12),
        Check("dos_state_count", abs(integrated_dos - 1.0) < 2.0e-4, integrated_dos, 1.0, 2.0e-4),
        Check(
            "interior_ldos_converges_to_bloch",
            ldos_errors[-1] < 0.55 * ldos_errors[0],
            ldos_errors,
            "last error < 0.55 * first error",
        ),
    ]
    return metrics, checks


def landau_gauge_square(size: int, flux: float) -> np.ndarray:
    matrix = np.zeros((size * size, size * size), dtype=complex)
    index = lambda x, y: x * size + y
    for x in range(size):
        for y in range(size):
            if x + 1 < size:
                phase = np.exp(-2.0j * np.pi * flux * y)
                matrix[index(x, y), index(x + 1, y)] = -phase
            if y + 1 < size:
                matrix[index(x, y), index(x, y + 1)] = -1.0
    return matrix + matrix.conj().T


def harper_matrix(point: np.ndarray, p: int, q: int) -> np.ndarray:
    kx, ky = 2.0 * np.pi * np.asarray(point, dtype=float)
    matrix = np.zeros((q, q), dtype=complex)
    for row in range(q):
        matrix[row, row] = -2.0 * np.cos(ky + 2.0 * np.pi * p * row / q)
        if row + 1 < q:
            matrix[row, row + 1] = -1.0
            matrix[row + 1, row] = -1.0
    # point[0] spans the reduced magnetic Brillouin zone.  The boundary
    # hopping therefore accumulates one full reduced-zone phase, not q copies.
    boundary = -np.exp(1.0j * kx)
    matrix[q - 1, 0] = boundary
    matrix[0, q - 1] = boundary.conjugate()
    return matrix


def magnetic_hofstadter(
    build_matrix: MatrixBuilder,
    parameters: dict,
) -> tuple[dict, list[Check]]:
    """Gauge equivalence, magnetic translation, and Hofstadter Chern checks."""

    size = int(parameters["finite_square_size"])
    flux = float(parameters["flux_per_plaquette"])
    landau = landau_gauge_square(size, flux)
    coordinates = np.asarray(
        [(x, y) for x in range(size) for y in range(size)], dtype=float
    )
    phases = 0.37 * coordinates[:, 0] + 0.19 * coordinates[:, 1] ** 2
    gauge = np.diag(np.exp(1.0j * phases))
    transformed = gauge @ landau @ gauge.conj().T
    package_landau = build_matrix(landau)
    package_transformed = build_matrix(transformed)
    gauge_residual = float(
        np.max(np.abs(package_transformed - gauge @ package_landau @ gauge.conj().T))
    )
    spectral_error = float(
        np.max(
            np.abs(
                np.linalg.eigvalsh(package_landau)
                - np.linalg.eigvalsh(package_transformed)
            )
        )
    )

    translation_errors: list[float] = []
    band_counts: list[int] = []
    for q in parameters["magnetic_denominators"]:
        q = int(q)
        shift = np.zeros((q, q), dtype=complex)
        clock = np.zeros((q, q), dtype=complex)
        for row in range(q):
            shift[(row + 1) % q, row] = 1.0
            clock[row, row] = np.exp(2.0j * np.pi * row / q)
        phase = np.exp(-2.0j * np.pi / q)
        translation_errors.append(
            float(np.max(np.abs(shift @ clock - phase * clock @ shift)))
        )
        band_counts.append(len(np.linalg.eigvalsh(build_matrix(harper_matrix(np.zeros(2), 1, q)))))

    def package_harper(point: np.ndarray) -> np.ndarray:
        return build_matrix(harper_matrix(point, 1, 3))

    chern = fhs_chern(package_harper, (int(parameters["chern_mesh"]),) * 2, occupied=1)
    rounded_chern = int(np.rint(chern))
    metrics = {
        "gauge_covariance_residual": gauge_residual,
        "gauge_spectral_error": spectral_error,
        "magnetic_translation_errors": translation_errors,
        "magnetic_band_counts": band_counts,
        "lowest_band_chern": chern,
        "diophantine_chern_magnitude": 1,
    }
    checks = [
        Check("peierls_gauge_covariance", gauge_residual < 1.0e-12, gauge_residual, 0.0, 1.0e-12),
        Check("gauge_invariant_spectrum", spectral_error < 1.0e-11, spectral_error, 0.0, 1.0e-11),
        Check("magnetic_translation_algebra", max(translation_errors) < 1.0e-12, translation_errors, 0.0, 1.0e-12),
        Check("magnetic_band_multiplicity", band_counts == parameters["magnetic_denominators"], band_counts, parameters["magnetic_denominators"]),
        Check("diophantine_chern_label", abs(rounded_chern) == 1 and abs(chern - rounded_chern) < 2.0e-6, chern, "integer with magnitude 1", 2.0e-6),
    ]
    return metrics, checks


def effective_andreev(phi: float, transparency: float) -> np.ndarray:
    return np.cos(phi / 2.0) * SIGMA_Z + math.sqrt(1.0 - transparency) * np.sin(
        phi / 2.0
    ) * SIGMA_X


def kitaev_bdg(size: int, hopping: float, pairing: float, chemical_potential: float) -> np.ndarray:
    normal = np.zeros((size, size), dtype=complex)
    pair = np.zeros((size, size), dtype=complex)
    np.fill_diagonal(normal, -chemical_potential)
    for site in range(size - 1):
        normal[site, site + 1] = -hopping
        normal[site + 1, site] = -hopping
        pair[site, site + 1] = pairing
        pair[site + 1, site] = -pairing
    return np.block([[normal, pair], [-pair.conj(), -normal.conj()]])


def particle_hole_transform(size: int) -> np.ndarray:
    zero = np.zeros((size, size), dtype=complex)
    identity = np.eye(size, dtype=complex)
    return np.block([[zero, identity], [identity, zero]])


def bdg_majorana(
    build_matrix: MatrixBuilder,
    parameters: dict,
) -> tuple[dict, list[Check]]:
    """Nambu, short-junction, and Majorana gates."""

    hopping = float(parameters["hopping"])
    pairing = float(parameters["pairing"])
    topological_mu = float(parameters["topological_mu"])
    trivial_mu = float(parameters["trivial_mu"])
    sizes = [int(item) for item in parameters["chain_sizes"]]
    reference = kitaev_bdg(sizes[0], hopping, pairing, topological_mu)
    matrix = build_matrix(reference)
    particle_hole = particle_hole_transform(sizes[0])
    ph_residual = float(
        np.max(np.abs(particle_hole @ matrix.conj() @ particle_hole - (-matrix)))
    )
    values = np.linalg.eigvalsh(matrix)
    pairing_error = float(np.max(np.abs(values + values[::-1])))

    transparency = float(parameters["junction_transparency"])
    phases = np.linspace(0.0, 1.8 * np.pi, 37)
    positive_levels = []
    expected_levels = []
    for phase in phases:
        levels = np.linalg.eigvalsh(build_matrix(effective_andreev(float(phase), transparency)))
        positive_levels.append(float(levels[-1]))
        expected_levels.append(
            float(np.sqrt(1.0 - transparency * np.sin(phase / 2.0) ** 2))
        )
    andreev_error = float(
        np.max(np.abs(np.asarray(positive_levels) - np.asarray(expected_levels)))
    )
    numerical_current = -np.gradient(positive_levels, phases)
    analytic_current = (
        transparency
        * np.sin(phases)
        / (4.0 * np.maximum(np.asarray(expected_levels), 1.0e-12))
    )
    current_error = float(
        np.max(np.abs(numerical_current[2:-2] - analytic_current[2:-2]))
    )

    splittings: list[float] = []
    end_weights: list[float] = []
    trivial_end_weight = 0.0
    self_conjugacy_errors: list[float] = []
    for size in sizes:
        topological = build_matrix(kitaev_bdg(size, hopping, pairing, topological_mu))
        eigenvalues, eigenvectors = np.linalg.eigh(topological)
        order = np.argsort(np.abs(eigenvalues))
        splittings.append(float(np.max(np.abs(eigenvalues[order[:2]]))))
        vector = eigenvectors[:, order[0]]
        weights = np.abs(vector[:size]) ** 2 + np.abs(vector[size:]) ** 2
        end_weights.append(float(np.sum(weights[[0, 1, size - 2, size - 1]])))
        conjugate = particle_hole_transform(size) @ vector.conj()
        majorana = vector + conjugate
        majorana /= np.linalg.norm(majorana)
        self_conjugacy_errors.append(
            float(np.linalg.norm(particle_hole_transform(size) @ majorana.conj() - majorana))
        )
    trivial = build_matrix(kitaev_bdg(sizes[-1], hopping, pairing, trivial_mu))
    trivial_values, trivial_vectors = np.linalg.eigh(trivial)
    trivial_vector = trivial_vectors[:, np.argmin(np.abs(trivial_values))]
    size = sizes[-1]
    trivial_weights = np.abs(trivial_vector[:size]) ** 2 + np.abs(trivial_vector[size:]) ** 2
    trivial_end_weight = float(np.sum(trivial_weights[[0, 1, size - 2, size - 1]]))

    topological_invariant = int(abs(topological_mu) < 2.0 * abs(hopping))
    trivial_invariant = int(abs(trivial_mu) < 2.0 * abs(hopping))
    metrics = {
        "particle_hole_residual": ph_residual,
        "paired_energy_error": pairing_error,
        "andreev_level_error": andreev_error,
        "josephson_current_error": current_error,
        "topological_invariant": topological_invariant,
        "trivial_invariant": trivial_invariant,
        "majorana_splittings": splittings,
        "majorana_end_weights": end_weights,
        "majorana_self_conjugacy_errors": self_conjugacy_errors,
        "trivial_lowest_state_end_weight": trivial_end_weight,
    }
    checks = [
        Check("particle_hole_symmetry", ph_residual < 1.0e-11, ph_residual, 0.0, 1.0e-11),
        Check("paired_bdg_spectrum", pairing_error < 1.0e-10, pairing_error, 0.0, 1.0e-10),
        Check("short_junction_andreev_spectrum", andreev_error < 1.0e-12, andreev_error, 0.0, 1.0e-12),
        Check("josephson_current_derivative", current_error < 3.0e-3, current_error, 0.0, 3.0e-3),
        Check("kitaev_bulk_invariants", topological_invariant == 1 and trivial_invariant == 0, [topological_invariant, trivial_invariant], [1, 0]),
        Check("majorana_splitting_decreases", all(left > right for left, right in zip(splittings, splittings[1:])), splittings, "strictly decreasing"),
        Check("majorana_end_localization", min(end_weights) > 0.85, end_weights, "> 0.85"),
        Check("majorana_self_conjugacy", max(self_conjugacy_errors) < 1.0e-10, self_conjugacy_errors, 0.0, 1.0e-10),
        Check("trivial_control_not_end_localized", trivial_end_weight < 0.35, trivial_end_weight, "< 0.35"),
    ]
    return metrics, checks


def texture_field(size: int, radius: float) -> np.ndarray:
    center = (size - 1) / 2.0
    field = np.zeros((size, size, 3), dtype=float)
    for x in range(size):
        for y in range(size):
            dx, dy = x - center, y - center
            radial = math.hypot(dx, dy)
            theta = math.pi * min(radial / radius, 1.0)
            phi = math.atan2(dy, dx)
            field[x, y] = [
                math.sin(theta) * math.cos(phi),
                math.sin(theta) * math.sin(phi),
                math.cos(theta),
            ]
    return field


def texture_hamiltonian(field: np.ndarray, exchange: float, hopping: float) -> np.ndarray:
    size = field.shape[0]
    matrix = np.zeros((2 * size * size, 2 * size * size), dtype=complex)
    site = lambda x, y: 2 * (x * size + y)
    for x in range(size):
        for y in range(size):
            start = site(x, y)
            nx, ny, nz = field[x, y]
            matrix[start : start + 2, start : start + 2] = exchange * (
                nx * SIGMA_X + ny * SIGMA_Y + nz * SIGMA_Z
            )
            for next_x, next_y in ((x + 1, y), (x, y + 1)):
                if next_x < size and next_y < size:
                    other = site(next_x, next_y)
                    matrix[start : start + 2, other : other + 2] = hopping * np.eye(2)
                    matrix[other : other + 2, start : start + 2] = hopping * np.eye(2)
    return matrix


def spin_texture_covariance(
    build_matrix: MatrixBuilder,
    parameters: dict,
) -> tuple[dict, list[Check]]:
    size = int(parameters["linear_size"])
    field = texture_field(size, float(parameters["radius"]))
    angle = 0.619
    rotation3 = np.array(
        [
            [np.cos(angle), 0.0, np.sin(angle)],
            [0.0, 1.0, 0.0],
            [-np.sin(angle), 0.0, np.cos(angle)],
        ]
    )
    rotated_field = field @ rotation3.T
    spin_rotation = np.cos(angle / 2.0) * np.eye(2) - 1.0j * np.sin(
        angle / 2.0
    ) * SIGMA_Y
    unitary = np.kron(np.eye(size * size), spin_rotation)
    original = build_matrix(
        texture_hamiltonian(field, float(parameters["exchange"]), float(parameters["hopping"]))
    )
    rotated = build_matrix(
        texture_hamiltonian(
            rotated_field, float(parameters["exchange"]), float(parameters["hopping"])
        )
    )
    covariance_error = float(np.max(np.abs(rotated - unitary @ original @ unitary.conj().T)))
    spectral_error = float(
        np.max(np.abs(np.linalg.eigvalsh(original) - np.linalg.eigvalsh(rotated)))
    )

    charge = 0.0
    for x in range(size - 1):
        for y in range(size - 1):
            a, b, c, d = field[x, y], field[x + 1, y], field[x + 1, y + 1], field[x, y + 1]
            for first, second, third in ((a, b, c), (a, c, d)):
                numerator = float(np.dot(first, np.cross(second, third)))
                denominator = float(
                    1.0
                    + np.dot(first, second)
                    + np.dot(second, third)
                    + np.dot(third, first)
                )
                charge += 2.0 * math.atan2(numerator, denominator)
    charge /= 4.0 * math.pi
    metrics = {
        "discrete_skyrmion_charge": charge,
        "spin_rotation_covariance_error": covariance_error,
        "rotated_spectrum_error": spectral_error,
    }
    checks = [
        Check("nontrivial_texture_charge", abs(abs(charge) - 1.0) < 0.20, charge, "magnitude 1", 0.20),
        Check("global_spin_rotation_covariance", covariance_error < 2.0e-12, covariance_error, 0.0, 2.0e-12),
        Check("global_spin_rotation_spectrum", spectral_error < 2.0e-11, spectral_error, 0.0, 2.0e-11),
    ]
    return metrics, checks
