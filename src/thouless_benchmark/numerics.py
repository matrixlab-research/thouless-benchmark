"""Backend-independent observables evaluated from backend-built Hamiltonians.

The package adapters remain responsible for constructing every Hamiltonian
with the original package. These routines implement common gauge-invariant
post-processing so that the scientific observable, rather than a package's
plotting convention, is compared.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable

import numpy as np

Hamiltonian = Callable[[np.ndarray], np.ndarray]


def occupied_frame(hamiltonian: np.ndarray, occupied: int) -> tuple[np.ndarray, np.ndarray]:
    values, vectors = np.linalg.eigh(np.asarray(hamiltonian, dtype=complex))
    return values, vectors[:, :occupied]


def unitary_link(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    overlap = left.conj().T @ right
    u, _, vh = np.linalg.svd(overlap)
    return u @ vh


def determinant_phase(matrix: np.ndarray) -> float:
    return float(np.angle(np.linalg.det(matrix)))


def berry_phase(hamiltonians: Iterable[np.ndarray], occupied: int = 1) -> float:
    frames = [occupied_frame(matrix, occupied)[1] for matrix in hamiltonians]
    if len(frames) < 2:
        raise ValueError("Berry loop needs at least two samples")
    product = np.eye(occupied, dtype=complex)
    for left, right in zip(frames, frames[1:] + frames[:1]):
        product = product @ unitary_link(left, right)
    return determinant_phase(product)


def fhs_chern(
    hamiltonian: Hamiltonian,
    samples: tuple[int, int] = (31, 31),
    occupied: int = 1,
) -> float:
    """Fukui-Hatsugai-Suzuki Chern number on a reduced-coordinate torus."""

    nx, ny = samples
    frames: list[list[np.ndarray]] = []
    for ix in range(nx):
        row = []
        for iy in range(ny):
            _, frame = occupied_frame(
                hamiltonian(np.array([ix / nx, iy / ny], dtype=float)), occupied
            )
            row.append(frame)
        frames.append(row)
    flux = 0.0
    for ix in range(nx):
        for iy in range(ny):
            u_x = np.linalg.det(unitary_link(frames[ix][iy], frames[(ix + 1) % nx][iy]))
            u_y_x = np.linalg.det(
                unitary_link(frames[(ix + 1) % nx][iy], frames[(ix + 1) % nx][(iy + 1) % ny])
            )
            u_x_y = np.linalg.det(
                unitary_link(frames[ix][(iy + 1) % ny], frames[(ix + 1) % nx][(iy + 1) % ny])
            )
            u_y = np.linalg.det(unitary_link(frames[ix][iy], frames[ix][(iy + 1) % ny]))
            flux += np.angle(u_x * u_y_x / (u_x_y * u_y))
    return float(flux / (2.0 * np.pi))


def minimum_direct_gap(
    hamiltonian: Hamiltonian,
    dimension: int,
    samples: int,
    occupied: int,
) -> float:
    minimum = np.inf
    for flat in np.ndindex(*(samples,) * dimension):
        momentum = np.asarray(flat, dtype=float) / samples
        values = np.linalg.eigvalsh(hamiltonian(momentum))
        minimum = min(minimum, float(values[occupied] - values[occupied - 1]))
    return float(minimum)


def wilson_centers(
    hamiltonian: Hamiltonian,
    *,
    loop_axis: int,
    fixed_momentum: np.ndarray,
    loop_samples: int,
    occupied: int,
) -> np.ndarray:
    frames = []
    for sample in range(loop_samples):
        momentum = np.asarray(fixed_momentum, dtype=float).copy()
        momentum[loop_axis] = sample / loop_samples
        frames.append(occupied_frame(hamiltonian(momentum), occupied)[1])
    product = np.eye(occupied, dtype=complex)
    for left, right in zip(frames, frames[1:] + frames[:1]):
        product = product @ unitary_link(left, right)
    centers = np.mod(np.angle(np.linalg.eigvals(product)) / (2.0 * np.pi), 1.0)
    return np.sort(centers)


def nested_wilson_polarizations(
    hamiltonian: Hamiltonian,
    *,
    loop_samples: int = 61,
    transverse_samples: int = 61,
    occupied: int = 2,
) -> tuple[np.ndarray, np.ndarray]:
    """Return x-directed Wannier bands and their nested y polarizations."""

    centers = np.empty((transverse_samples, occupied), dtype=float)
    sector_states: list[list[np.ndarray]] = [[] for _ in range(occupied)]
    for iy in range(transverse_samples):
        ky = iy / transverse_samples
        frames = [
            occupied_frame(
                hamiltonian(np.array([ix / loop_samples, ky], dtype=float)), occupied
            )[1]
            for ix in range(loop_samples)
        ]
        product = np.eye(occupied, dtype=complex)
        for left, right in zip(frames, frames[1:] + frames[:1]):
            product = product @ unitary_link(left, right)
        eigenvalues, eigenvectors = np.linalg.eig(product)
        current_centers = np.mod(np.angle(eigenvalues) / (2.0 * np.pi), 1.0)
        order = np.argsort(current_centers)
        centers[iy] = current_centers[order]
        for sector, index in enumerate(order):
            state = frames[0] @ eigenvectors[:, index]
            sector_states[sector].append(state / np.linalg.norm(state))
    polarizations = []
    for states in sector_states:
        product = 1.0 + 0.0j
        for left, right in zip(states, states[1:] + states[:1]):
            overlap = np.vdot(left, right)
            product *= overlap / abs(overlap)
        polarizations.append(float(np.mod(np.angle(product) / (2.0 * np.pi), 1.0)))
    return centers, np.asarray(polarizations)


def finite_difference(
    function: Callable[[np.ndarray], float],
    point: np.ndarray,
    axis: int,
    step: float,
) -> float:
    plus = np.asarray(point, dtype=float).copy()
    minus = np.asarray(point, dtype=float).copy()
    plus[axis] += step
    minus[axis] -= step
    return float((function(plus) - function(minus)) / (2.0 * step))


def berry_curvature_dipole(
    hamiltonian: Hamiltonian,
    chemical_potentials: Iterable[float],
    *,
    temperature: float,
    samples: int = 51,
    band: int = 1,
    derivative_step: float = 1.0e-4,
) -> np.ndarray:
    """Evaluate the x Berry-curvature dipole of one isolated two-band band."""

    records: list[tuple[float, float, float]] = []
    for ix in range(samples):
        for iy in range(samples):
            point = np.array(
                [(ix + 0.5) / samples - 0.5, (iy + 0.5) / samples - 0.5]
            )
            matrix = hamiltonian(point)
            energies, vectors = np.linalg.eigh(matrix)
            other = 1 - band
            plus_x = point + [derivative_step, 0.0]
            minus_x = point - [derivative_step, 0.0]
            plus_y = point + [0.0, derivative_step]
            minus_y = point - [0.0, derivative_step]
            velocity_x = (
                hamiltonian(plus_x) - hamiltonian(minus_x)
            ) / (2.0 * derivative_step)
            velocity_y = (
                hamiltonian(plus_y) - hamiltonian(minus_y)
            ) / (2.0 * derivative_step)
            numerator = np.vdot(
                vectors[:, band], velocity_x @ vectors[:, other]
            ) * np.vdot(vectors[:, other], velocity_y @ vectors[:, band])
            curvature = float(
                -2.0 * np.imag(numerator) / (energies[band] - energies[other]) ** 2
            )
            energy_velocity = float(
                (
                    np.linalg.eigvalsh(hamiltonian(plus_x))[band]
                    - np.linalg.eigvalsh(hamiltonian(minus_x))[band]
                )
                / (2.0 * derivative_step)
            )
            records.append((float(energies[band]), curvature, energy_velocity))
    dipoles = []
    for chemical_potential in chemical_potentials:
        total = 0.0
        for energy, curvature, energy_velocity in records:
            argument = np.clip(
                (energy - chemical_potential) / temperature, -40.0, 40.0
            )
            minus_derivative = 1.0 / (
                4.0 * temperature * np.cosh(argument / 2.0) ** 2
            )
            total += curvature * energy_velocity * minus_derivative
        dipoles.append(total / samples**2)
    return np.asarray(dipoles)
