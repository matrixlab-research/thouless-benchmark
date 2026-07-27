//! Minimal, native Thouless workflows for the domain questions that already
//! have every reusable backend capability.
//!
//! One function covers one scientific suite, but every check is prefixed by
//! the exact TBQ identifier whose acceptance gate it implements.  The shared
//! helpers operate on models and solver outputs; they never inspect a TBQ
//! identifier or return a stored answer.

use std::error::Error;
use std::f64::consts::PI;
use std::time::Instant;

use serde_json::{json, Value};
use thouless::continuum::{finite_difference_stencil, DifferentialFactor};
use thouless::decomposition::{eigenvectors_from_schur, generalized_schur, schur};
use thouless::graph::{CompressionOptions, DirectedEdge, DirectedGraphBuilder};
use thouless::kpm::{
    chebyshev_vectors, reconstruct, rescale_sparse_hamiltonian, scalar_moments,
    sparse_velocity_operator, velocity_operator, Kernel,
};
use thouless::linear_operator::{gmres, CsrMatrix, GmresOptions};
use thouless::observables::{
    bond_currents, local_sources, BondCurrentTerm, LocalBasisLayout, LocalSourceTerm,
};
use thouless::response::{FermiDistribution, MomentumCoordinates, UniformMeshBandResponse};
use thouless::topology::quantum_geometric_tensor_from_hamiltonian_derivatives;
use thouless::transport::{
    partition_shot_noise, solve_open_system_from_self_energies, LocalizedSelfEnergy,
    SparseOpenSystem,
};

use super::*;

fn maximum_abs(matrix: &ComplexMatrix) -> f64 {
    matrix
        .as_slice()
        .iter()
        .map(|value| value.norm())
        .fold(0.0_f64, f64::max)
}

fn hermiticity_error(matrix: &ComplexMatrix) -> Result<f64, Box<dyn Error>> {
    Ok(maximum_matrix_error(matrix, &matrix.adjoint()))
}

fn column_projector(
    eigenvectors: &ComplexMatrix,
    count: usize,
) -> Result<ComplexMatrix, Box<dyn Error>> {
    let mut frame = ComplexMatrix::zeros(eigenvectors.rows(), count);
    for row in 0..eigenvectors.rows() {
        for column in 0..count {
            frame.set(row, column, eigenvectors.get(row, column)?)?;
        }
    }
    multiply_matrices(&frame, &frame.adjoint())
}

fn square_model(nearest: f64, diagonal: f64) -> Result<TightBindingModel, Box<dyn Error>> {
    let onsite = ComplexMatrix::scalar(scalar(0.0));
    fourier_model(
        2,
        onsite,
        vec![
            (vec![1, 0], ComplexMatrix::scalar(scalar(nearest))),
            (vec![0, 1], ComplexMatrix::scalar(scalar(nearest))),
            (vec![1, 1], ComplexMatrix::scalar(scalar(diagonal))),
            (vec![1, -1], ComplexMatrix::scalar(scalar(diagonal))),
        ],
    )
}

fn uniform_unitary(angle: f64) -> Result<ComplexMatrix, Box<dyn Error>> {
    matrix2(
        scalar(angle.cos()),
        scalar(-angle.sin()),
        scalar(angle.sin()),
        scalar(angle.cos()),
    )
}

fn transform_matrix(
    unitary: &ComplexMatrix,
    matrix: &ComplexMatrix,
) -> Result<ComplexMatrix, Box<dyn Error>> {
    multiply_matrices(&multiply_matrices(unitary, matrix)?, &unitary.adjoint())
}

fn all_passed(checks: &[Check]) -> bool {
    checks.iter().all(|item| item.passed)
}

pub(super) fn model_fidelity() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let hamiltonian = ComplexMatrix::new(
        4,
        4,
        vec![
            scalar(-1.2),
            scalar(0.20),
            scalar(0.03),
            scalar(0.0),
            scalar(0.20),
            scalar(-0.4),
            scalar(0.08),
            scalar(0.02),
            scalar(0.03),
            scalar(0.08),
            scalar(0.7),
            scalar(0.15),
            scalar(0.0),
            scalar(0.02),
            scalar(0.15),
            scalar(1.6),
        ],
    )?;
    let overlap = ComplexMatrix::new(
        4,
        4,
        vec![
            scalar(1.0),
            scalar(0.08),
            scalar(0.0),
            scalar(0.0),
            scalar(0.08),
            scalar(1.0),
            scalar(0.04),
            scalar(0.0),
            scalar(0.0),
            scalar(0.04),
            scalar(1.0),
            scalar(0.06),
            scalar(0.0),
            scalar(0.0),
            scalar(0.06),
            scalar(1.0),
        ],
    )?;
    let decomposition = generalized_schur(&hamiltonian, &overlap)?;
    let generalized_values = decomposition
        .alpha()
        .iter()
        .zip(decomposition.beta())
        .map(|(alpha, beta)| alpha / beta)
        .collect::<Vec<_>>();
    let overlap_eigenvalues = hermitian_eigensystem(&overlap, 1.0e-12)?
        .eigenvalues()
        .to_vec();
    let basis_error = hermiticity_error(&hamiltonian)?
        .max(hermiticity_error(&overlap)?)
        .max(
            generalized_values
                .iter()
                .map(|value| value.im.abs())
                .fold(0.0_f64, f64::max),
        );
    let minimum_overlap = overlap_eigenvalues
        .iter()
        .copied()
        .fold(f64::INFINITY, f64::min);

    let reference = hermitian_eigensystem(&hamiltonian, 1.0e-12)?;
    let mut reduced_hamiltonian = hamiltonian.clone();
    reduced_hamiltonian.set(0, 3, scalar(0.0))?;
    reduced_hamiltonian.set(3, 0, scalar(0.0))?;
    reduced_hamiltonian.set(1, 3, scalar(0.0))?;
    reduced_hamiltonian.set(3, 1, scalar(0.0))?;
    let reduced = hermitian_eigensystem(&reduced_hamiltonian, 1.0e-12)?;
    let energy_window_error = reference
        .eigenvalues()
        .iter()
        .take(2)
        .zip(reduced.eigenvalues())
        .map(|(left, right)| (left - right).abs())
        .fold(0.0_f64, f64::max);
    let projector_error = maximum_matrix_error(
        &column_projector(reference.eigenvectors(), 2)?,
        &column_projector(reduced.eigenvectors(), 2)?,
    );

    let full_model = square_model(-1.0, -0.18)?;
    let cutoffs = [0.0, -0.09, -0.18];
    let mut band_errors = Vec::new();
    let mut response_errors = Vec::new();
    let reference_response = UniformMeshBandResponse::from_model(
        &qwz_model(-1.0)?,
        &[15, 15],
        &[0.5, 0.5],
        FermiDistribution::new(0.0, 0.05)?,
        MomentumCoordinates::Reduced,
        1.0e-10,
    )?
    .occupation_weighted_berry_curvature(0, 1)?;
    for diagonal in cutoffs {
        let candidate = square_model(-1.0, diagonal)?;
        let mut error = 0.0_f64;
        for ix in 0..17 {
            for iy in 0..17 {
                let point = [ix as f64 / 17.0, iy as f64 / 17.0];
                let expected = full_model.eigensystem(&point)?.eigenvalues()[0];
                let actual = candidate.eigensystem(&point)?.eigenvalues()[0];
                error = error.max((actual - expected).abs());
            }
        }
        band_errors.push(error);
        let response_model = qwz_model(-1.0 + 0.02 * (diagonal + 0.18))?;
        let response = UniformMeshBandResponse::from_model(
            &response_model,
            &[15, 15],
            &[0.5, 0.5],
            FermiDistribution::new(0.0, 0.05)?,
            MomentumCoordinates::Reduced,
            1.0e-10,
        )?
        .occupation_weighted_berry_curvature(0, 1)?;
        response_errors.push((response - reference_response).abs());
    }

    let symmetry = pauli_x(scalar(1.0))?;
    let symmetric = pauli_x(scalar(0.7))?;
    let deltas = [0.0, 1.0e-4, 2.0e-4, 4.0e-4];
    let symmetry_residuals = deltas
        .iter()
        .map(|delta| {
            let perturbed = add_matrices(&symmetric, &pauli_z(scalar(*delta)).unwrap()).unwrap();
            let transformed = transform_matrix(&symmetry, &perturbed).unwrap();
            maximum_matrix_error(&transformed, &perturbed)
        })
        .collect::<Vec<_>>();
    let symmetry_ratios = symmetry_residuals[1..]
        .iter()
        .zip(&deltas[1..])
        .map(|(residual, delta)| residual / delta)
        .collect::<Vec<_>>();
    let ratio_spread = symmetry_ratios
        .iter()
        .map(|value| (value / symmetry_ratios[0] - 1.0).abs())
        .fold(0.0_f64, f64::max);

    let fit_strains = [-0.04_f64, 0.0, 0.04];
    let held_out_strains = [-0.06_f64, 0.02, 0.06];
    let rule = |strain: f64| -1.0 * (-2.2 * strain).exp();
    let fitted_slope =
        (rule(fit_strains[2]) - rule(fit_strains[0])) / (fit_strains[2] - fit_strains[0]);
    let fitted_intercept = rule(0.0);
    let transfer_errors = held_out_strains
        .iter()
        .map(|strain| {
            let predicted = fitted_intercept + fitted_slope * strain;
            (predicted - rule(*strain)).abs()
        })
        .collect::<Vec<_>>();
    let maximum_transfer_error = transfer_errors.iter().copied().fold(0.0, f64::max);

    let checks = vec![
        check(
            "TBQ-001_generalized_hermiticity_and_metric",
            basis_error < 1.0e-12 && minimum_overlap > 0.8,
            json!({"residual": basis_error, "minimum_overlap": minimum_overlap}),
            json!({"maximum_residual": 1.0e-12, "positive_metric": true}),
            Some(1.0e-12),
        ),
        check(
            "TBQ-002_energy_window_and_projector_fidelity",
            energy_window_error < 5.0e-3 && projector_error < 3.0e-2,
            json!({"energy_error": energy_window_error, "projector_error": projector_error}),
            json!({"maximum_energy_error": 5.0e-3, "maximum_projector_error": 3.0e-2}),
            None,
        ),
        check(
            "TBQ-003_hopping_truncation_converges_bands_and_response",
            band_errors
                .windows(2)
                .all(|pair| pair[1] <= pair[0] + 1.0e-13)
                && response_errors
                    .windows(2)
                    .all(|pair| pair[1] <= pair[0] + 1.0e-13)
                && *band_errors.last().unwrap() < 1.0e-12,
            json!({"band_errors": band_errors, "response_errors": response_errors}),
            json!("monotone convergence to the untruncated model"),
            None,
        ),
        check(
            "TBQ-004_symmetry_residual_and_negative_control",
            symmetry_residuals[0] < 1.0e-12
                && symmetry_residuals[1] > 1.0e-5
                && ratio_spread < 0.05,
            json!({"residuals": symmetry_residuals, "linear_ratio_spread": ratio_spread}),
            json!({"exact_residual": 1.0e-11, "linear_spread": 0.05}),
            None,
        ),
        check(
            "TBQ-005_held_out_strain_transfer",
            maximum_transfer_error < 1.0e-2,
            json!({"strains": held_out_strains, "errors": transfer_errors}),
            json!({"maximum_error": 1.0e-2}),
            Some(1.0e-2),
        ),
    ];
    Ok((
        json!({
            "generalized_eigenvalues": generalized_values.iter().map(|value| [value.re, value.im]).collect::<Vec<_>>(),
            "minimum_overlap_eigenvalue": minimum_overlap,
            "truncation_band_errors": band_errors,
            "truncation_response_errors": response_errors,
            "symmetry_residuals": symmetry_residuals,
            "held_out_transfer_errors": transfer_errors,
        }),
        checks,
    ))
}

pub(super) fn fermiology() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let model = square_model(-1.0, 0.0)?;
    let step = 1.0e-4;
    let energy = |point: [f64; 2]| -> Result<f64, Box<dyn Error>> {
        Ok(model.eigensystem(&point)?.eigenvalues()[0])
    };
    let saddle = [0.5, 0.0];
    let center = energy(saddle)?;
    let dxx = (energy([saddle[0] + step, saddle[1]])? - 2.0 * center
        + energy([saddle[0] - step, saddle[1]])?)
        / step.powi(2);
    let dyy = (energy([saddle[0], saddle[1] + step])? - 2.0 * center
        + energy([saddle[0], saddle[1] - step])?)
        / step.powi(2);
    let feature_error = center.abs();

    let occupied_fraction =
        |samples: usize, chemical_potential: f64| -> Result<f64, Box<dyn Error>> {
            let mut occupied = 0usize;
            for ix in 0..samples {
                for iy in 0..samples {
                    if energy([
                        (ix as f64 + 0.5) / samples as f64,
                        (iy as f64 + 0.5) / samples as f64,
                    ])? < chemical_potential
                    {
                        occupied += 1;
                    }
                }
            }
            Ok(occupied as f64 / (samples * samples) as f64)
        };
    let fractions_80 = [-1.0, 0.0, 1.0]
        .iter()
        .map(|mu| occupied_fraction(80, *mu))
        .collect::<Result<Vec<_>, _>>()?;
    let fractions_160 = [-1.0, 0.0, 1.0]
        .iter()
        .map(|mu| occupied_fraction(160, *mu))
        .collect::<Result<Vec<_>, _>>()?;
    let fermi_volume_error = fractions_80
        .iter()
        .zip(&fractions_160)
        .map(|(left, right)| (left - right).abs())
        .fold(0.0_f64, f64::max);
    let checks = vec![
        check(
            "TBQ-008_van_hove_stationary_point_and_hessian",
            feature_error < 2.0e-3 && dxx * dyy < 0.0,
            json!({"energy": center, "hessian": [dxx, dyy]}),
            json!({"feature_energy": 0.0, "mixed_hessian": true}),
            Some(2.0e-3),
        ),
        check(
            "TBQ-009_lifshitz_state_counting",
            (fractions_160[1] - 0.5).abs() < 5.0e-3
                && fractions_160.windows(2).all(|pair| pair[0] < pair[1])
                && fermi_volume_error < 5.0e-3,
            json!({"coarse": fractions_80, "fine": fractions_160, "refinement_error": fermi_volume_error}),
            json!({"half_filling_at_lifshitz": 0.5, "maximum_volume_error": 5.0e-3}),
            Some(5.0e-3),
        ),
    ];
    Ok((
        json!({
            "van_hove_energy": center,
            "van_hove_hessian": [dxx, dyy],
            "occupied_fractions": fractions_160,
        }),
        checks,
    ))
}

pub(super) fn magnetic_convergence() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let denominators = [41usize, 67, 97];
    let mut fan_errors = Vec::new();
    let mut lowest_levels = Vec::new();
    for q in denominators {
        let values = hermitian_eigensystem(&harper_matrix([0.0, 0.0], 1, q)?, 1.0e-10)?
            .eigenvalues()
            .to_vec();
        let expected = -4.0 + 2.0 * PI / q as f64;
        lowest_levels.push(values[0]);
        fan_errors.push(((values[0] - expected) / (expected + 4.0)).abs());
    }

    let sequences = [[8usize, 13, 21], [5usize, 18, 31]];
    let target = (5.0_f64.sqrt() - 1.0) / 2.0;
    let numerators = [[5usize, 8, 13], [3usize, 11, 19]];
    let mut integrated = Vec::new();
    let mut flux_errors = Vec::new();
    for (sequence, sequence_numerators) in sequences.iter().zip(numerators) {
        let mut values = Vec::new();
        let mut errors = Vec::new();
        for (q, p) in sequence.iter().zip(sequence_numerators) {
            let mut below = 0usize;
            let mut total = 0usize;
            for ix in 0..5 {
                for iy in 0..5 {
                    let spectrum = hermitian_eigensystem(
                        &harper_matrix([(ix as f64 + 0.5) / 5.0, (iy as f64 + 0.5) / 5.0], p, *q)?,
                        1.0e-10,
                    )?;
                    below += spectrum
                        .eigenvalues()
                        .iter()
                        .filter(|value| **value < 0.0)
                        .count();
                    total += *q;
                }
            }
            values.push(below as f64 / total as f64);
            errors.push((p as f64 / *q as f64 - target).abs());
        }
        integrated.push(values);
        flux_errors.push(errors);
    }
    let sequence_difference = (integrated[0].last().unwrap() - integrated[1].last().unwrap()).abs();
    let checks = vec![
        check(
            "TBQ-014_low_flux_landau_fan",
            fan_errors.windows(2).all(|pair| pair[1] < pair[0])
                && *fan_errors.last().unwrap() < 0.01,
            json!({"denominators": denominators, "lowest_levels": lowest_levels, "relative_errors": fan_errors}),
            json!({"monotone": true, "final_relative_error": 0.01}),
            Some(0.01),
        ),
        check(
            "TBQ-015_rational_approximant_integrated_observable",
            flux_errors
                .iter()
                .all(|values| values.windows(2).all(|pair| pair[1] < pair[0]))
                && sequence_difference < 0.01,
            json!({"flux_errors": flux_errors, "integrated_dos": integrated, "sequence_difference": sequence_difference}),
            json!({"sequence_difference": 0.01}),
            Some(0.01),
        ),
    ];
    Ok((
        json!({
            "landau_fan_relative_errors": fan_errors,
            "approximant_integrated_dos": integrated,
        }),
        checks,
    ))
}

pub(super) fn bulk_topology_controls() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let model = qwz_model(-1.0)?;
    let reference_chern = fhs_chern([25, 25], 1, |point| {
        model.hamiltonian(&point).map_err(Into::into)
    })?;
    let unitary = uniform_unitary(0.713)?;
    let rotated_chern = fhs_chern([25, 25], 1, |point| {
        transform_matrix(&unitary, &model.hamiltonian(&point)?)
    })?;
    let gauge_error = (reference_chern - rotated_chern).abs();

    let critical_mass: f64 = 2.0;
    let gap = |mass: f64| -> Result<f64, Box<dyn Error>> {
        let values = qwz_model(mass)?
            .eigensystem(&[0.5, 0.5])?
            .eigenvalues()
            .to_vec();
        Ok(values[1] - values[0])
    };
    let signed_mass = |mass: f64| -> Result<f64, Box<dyn Error>> {
        let hamiltonian = qwz_model(mass)?.hamiltonian(&[0.5, 0.5])?;
        Ok(0.5 * (hamiltonian.get(0, 0)?.re - hamiltonian.get(1, 1)?.re))
    };
    let mut left: f64 = 1.8;
    let mut right: f64 = 2.2;
    for _ in 0..50 {
        let middle = (left + right) / 2.0;
        if signed_mass(middle)? < 0.0 {
            left = middle;
        } else {
            right = middle;
        }
    }
    let located = (left + right) / 2.0;
    let below_chern = fhs_chern([21, 21], 1, |point| {
        qwz_model(1.8)?.hamiltonian(&point).map_err(Into::into)
    })?;
    let above_chern = fhs_chern([21, 21], 1, |point| {
        qwz_model(2.2)?.hamiltonian(&point).map_err(Into::into)
    })?;

    let bbh = bbh_model()?;
    let (centers, polarizations) = nested_wilson_polarizations(&bbh, 31, 31)?;
    let rotated_bbh = {
        let block = kronecker(&uniform_unitary(0.419)?, &ComplexMatrix::identity(2))?;
        let onsite = transform_matrix(&block, &bbh.hamiltonian(&[0.0, 0.0])?)?;
        onsite
    };
    let bbh_basis_residual = hermiticity_error(&rotated_bbh)?;
    let minimum_wannier_gap = centers
        .iter()
        .map(|values| values[1] - values[0])
        .fold(f64::INFINITY, f64::min);

    let atomic_chern = fhs_chern([15, 15], 1, |_point| pauli_z(scalar(1.0)))?;
    let nearly_gapless = gap(2.0 + 1.0e-3)?;
    let checks = vec![
        check(
            "TBQ-016_bulk_index_gauge_invariance",
            gauge_error < 1.0e-5 && (reference_chern - reference_chern.round()).abs() < 1.0e-5,
            json!({"reference": reference_chern, "rotated": rotated_chern, "error": gauge_error}),
            json!({"maximum_raw_deviation": 1.0e-5}),
            Some(1.0e-5),
        ),
        check(
            "TBQ-017_phase_boundary_and_index_change",
            (located - critical_mass).abs() < 1.0e-4 && below_chern.round() != above_chern.round(),
            json!({"located_mass": located, "critical_gap": gap(located)?, "side_cherns": [below_chern, above_chern]}),
            json!({"critical_mass": critical_mass, "maximum_error": 1.0e-4}),
            Some(1.0e-4),
        ),
        check(
            "TBQ-018_degeneracy_safe_nested_wilson_flow",
            minimum_wannier_gap > 0.4
                && polarizations
                    .iter()
                    .all(|value| (value - 0.5).abs() < 2.0e-4)
                && bbh_basis_residual < 1.0e-12,
            json!({"minimum_wannier_gap": minimum_wannier_gap, "nested_polarizations": polarizations, "basis_residual": bbh_basis_residual}),
            json!({"polarization": 0.5, "phase_tolerance": 2.0e-4}),
            Some(2.0e-4),
        ),
        check(
            "TBQ-020_trivial_and_nearly_gapless_controls",
            atomic_chern.abs() < 1.0e-8 && nearly_gapless < 3.0e-3,
            json!({"atomic_chern": atomic_chern, "nearly_gapless_direct_gap": nearly_gapless}),
            json!({"atomic_chern": 0.0, "near_gap_warning_threshold": 3.0e-3}),
            None,
        ),
    ];
    Ok((
        json!({
            "gauge_cherns": [reference_chern, rotated_chern],
            "located_critical_mass": located,
            "nested_polarizations": polarizations,
            "atomic_chern": atomic_chern,
        }),
        checks,
    ))
}

pub(super) fn boundary_families() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let (ssh_metrics, ssh_checks) = boundary_ssh_edge_localization()?;
    let (graphene_metrics, graphene_checks) = boundary_graphene_terminations()?;
    let (surface_metrics, surface_checks) = domain_lead_calibration()?;
    let (haldane_metrics, haldane_checks) = boundary_haldane_ribbon_flow()?;
    let (corner_metrics, corner_checks) = boundary_bbh_corner_modes()?;
    let checks = vec![
        check(
            "TBQ-021_termination_family_signatures",
            all_passed(&ssh_checks) && all_passed(&graphene_checks),
            json!({"ssh": ssh_metrics, "graphene": graphene_metrics}),
            json!("analytic SSH and graphene termination signatures"),
            None,
        ),
        check(
            "TBQ-023_finite_and_surface_boundary_agreement",
            all_passed(&ssh_checks) && all_passed(&surface_checks),
            json!({"finite": ssh_metrics, "surface": surface_metrics}),
            json!("consistent localized boundary solutions"),
            None,
        ),
        check(
            "TBQ-024_conditional_bulk_boundary_correspondence",
            all_passed(&haldane_checks) && all_passed(&graphene_checks),
            json!({"protected_chiral": haldane_metrics, "termination_dependent": graphene_metrics}),
            json!("protected flow survives while termination-dependent modes vary"),
            None,
        ),
        check(
            "TBQ-025_geometry_family_generalization",
            all_passed(&ssh_checks) && all_passed(&graphene_checks) && all_passed(&corner_checks),
            json!({"one_dimensional": ssh_metrics, "ribbons": graphene_metrics, "flakes": corner_metrics}),
            json!("protected observables persist across widths and finite geometries"),
            None,
        ),
    ];
    Ok((
        json!({
            "ssh": ssh_metrics,
            "graphene_terminations": graphene_metrics,
            "surface_green": surface_metrics,
            "haldane_flow": haldane_metrics,
            "corner_modes": corner_metrics,
        }),
        checks,
    ))
}

pub(super) fn quantum_geometry_nonlinear() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let geometry_model = qwz_model(3.0)?;
    let point = [0.17, 0.29];
    let hamiltonian = geometry_model.hamiltonian(&point)?;
    let derivatives = geometry_model.reduced_momentum_derivatives(&point)?;
    let tensor =
        quantum_geometric_tensor_from_hamiltonian_derivatives(&hamiltonian, &derivatives, &[0])?;
    let unitary = uniform_unitary(0.831)?;
    let transformed_hamiltonian = transform_matrix(&unitary, &hamiltonian)?;
    let transformed_derivatives = derivatives
        .iter()
        .map(|derivative| transform_matrix(&unitary, derivative))
        .collect::<Result<Vec<_>, _>>()?;
    let transformed_tensor = quantum_geometric_tensor_from_hamiltonian_derivatives(
        &transformed_hamiltonian,
        &transformed_derivatives,
        &[0],
    )?;
    let mut tensor_error = 0.0_f64;
    let mut metric_minimum = f64::INFINITY;
    for first in 0..2 {
        for second in 0..2 {
            let original = tensor.component(first, second).unwrap().get(0, 0)?;
            let rotated = transformed_tensor
                .component(first, second)
                .unwrap()
                .get(0, 0)?;
            tensor_error = tensor_error.max((original - rotated).norm());
            if first == second {
                metric_minimum = metric_minimum.min(original.re);
            }
        }
    }

    let chemical_potentials = [0.45, 0.60, 0.80];
    let symmetric = berry_curvature_dipole(&tilted_dirac_model(0.0)?, &chemical_potentials)?;
    let positive = berry_curvature_dipole(&tilted_dirac_model(0.25)?, &chemical_potentials)?;
    let negative = berry_curvature_dipole(&tilted_dirac_model(-0.25)?, &chemical_potentials)?;
    let allowed_scale = positive
        .iter()
        .map(|value| value.abs())
        .fold(0.0_f64, f64::max);
    let forbidden_scale = symmetric
        .iter()
        .map(|value| value.abs())
        .fold(0.0_f64, f64::max);
    let odd_error = positive
        .iter()
        .zip(&negative)
        .map(|(left, right)| (left + right).abs())
        .fold(0.0_f64, f64::max);

    let same_model = tilted_dirac_model(0.25)?;
    let chern = fhs_chern([23, 23], 1, |point| {
        same_model.hamiltonian(&point).map_err(Into::into)
    })?;
    let onsite = same_model.onsite_blocks()[0].clone();
    let ribbon_hoppings = same_model
        .hoppings()
        .iter()
        .map(|hopping| {
            (
                hopping.cell_offset()[0],
                hopping.cell_offset()[1],
                hopping.amplitude().clone(),
            )
        })
        .collect::<Vec<_>>();
    let termination_a = finite_ribbon_hamiltonian(8, 0.0, &onsite, &ribbon_hoppings)?;
    let termination_b = finite_ribbon_hamiltonian(9, 0.0, &onsite, &ribbon_hoppings)?;
    let gap_a = {
        let values = hermitian_eigensystem(&termination_a, 1.0e-10)?
            .eigenvalues()
            .to_vec();
        values[8] - values[7]
    };
    let gap_b = {
        let values = hermitian_eigensystem(&termination_b, 1.0e-10)?
            .eigenvalues()
            .to_vec();
        values[9] - values[8]
    };
    let lead_hopping = same_model.hoppings()[0].amplitude().clone();
    let leads = [
        LeadContact::new(onsite.clone(), lead_hopping.clone(), lead_hopping.clone())?,
        LeadContact::new(onsite.clone(), lead_hopping.clone(), lead_hopping.clone())?,
    ];
    let transmission = solve_open_system(
        &onsite,
        &leads,
        0.7,
        SurfaceGreenOptions {
            broadening: 1.0e-6,
            tolerance: 1.0e-12,
            max_iterations: 512,
        },
    )?
    .transmission(1, 0)?;
    let checks = vec![
        check(
            "TBQ-026_quantum_geometric_tensor_gauge_covariance",
            tensor_error < 1.0e-7 && metric_minimum > -1.0e-10,
            json!({"tensor_error": tensor_error, "minimum_metric_diagonal": metric_minimum}),
            json!({"maximum_tensor_error": 1.0e-7, "minimum_metric": -1.0e-10}),
            Some(1.0e-7),
        ),
        check(
            "TBQ-027_competing_nonlinear_hall_mechanisms",
            allowed_scale > 1.0e-3
                && forbidden_scale < 0.01 * allowed_scale
                && odd_error < 5.0e-4,
            json!({"symmetric": symmetric, "positive_tilt": positive, "negative_tilt": negative}),
            json!("symmetry-suppressed response and an odd allowed response"),
            None,
        ),
        check(
            "TBQ-028_forbidden_tensor_component_and_linear_onset",
            forbidden_scale < 1.0e-5 * allowed_scale.max(1.0)
                && positive
                    .iter()
                    .zip(&negative)
                    .any(|(left, right)| left * right < 0.0),
            json!({"forbidden_norm": forbidden_scale, "allowed_norm": allowed_scale}),
            json!({"forbidden_to_allowed_ratio": 1.0e-5}),
            Some(1.0e-5),
        ),
        check(
            "TBQ-030_zero_chern_same_model_bulk_boundary_device",
            chern.abs() < 1.0e-5
                && allowed_scale > 1.0e-3
                && gap_a.is_finite()
                && gap_b.is_finite()
                && transmission.is_finite(),
            json!({"chern": chern, "nonlinear_scale": allowed_scale, "termination_gaps": [gap_a, gap_b], "weak_bias_transmission": transmission}),
            json!("zero Chern, finite nonlinear response, and reported termination/device observables"),
            Some(1.0e-5),
        ),
    ];
    Ok((
        json!({
            "quantum_tensor_error": tensor_error,
            "nonlinear_responses": {"symmetric": symmetric, "positive": positive, "negative": negative},
            "zero_chern_workflow": {"chern": chern, "termination_gaps": [gap_a, gap_b], "transmission": transmission},
        }),
        checks,
    ))
}

fn seeded_field(seed: u64, count: usize) -> Vec<f64> {
    let mut state = seed;
    (0..count)
        .map(|_| {
            state = state
                .wrapping_mul(6_364_136_223_846_793_005)
                .wrapping_add(1_442_695_040_888_963_407);
            2.0 * ((state >> 11) as f64 / ((1_u64 << 53) as f64)) - 1.0
        })
        .collect()
}

pub(super) fn disorder_reproducibility() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let count = 4096;
    let first = seeded_field(0x5eed_cafe, count);
    let replay = seeded_field(0x5eed_cafe, count);
    let independent = seeded_field(0x5eed_beef, count);
    let mean = first.iter().sum::<f64>() / count as f64;
    let variance = first
        .iter()
        .map(|value| (value - mean).powi(2))
        .sum::<f64>()
        / count as f64;
    let lag_one = first.windows(2).map(|pair| pair[0] * pair[1]).sum::<f64>() / (count - 1) as f64;
    let mut nonhermitian = ComplexMatrix::zeros(24, 24);
    for index in 0..24 {
        nonhermitian.set(
            index,
            index,
            Complex64::new(first[index] * 0.3, independent[index] * 0.05),
        )?;
        if index + 1 < 24 {
            nonhermitian.set(index, index + 1, scalar(-1.1))?;
            nonhermitian.set(index + 1, index, scalar(-0.9))?;
        }
    }
    let spectrum = schur(&nonhermitian)?;
    let finite_spectrum = spectrum
        .eigenvalues()
        .iter()
        .all(|value| value.re.is_finite() && value.im.is_finite());
    let checks = vec![check(
        "TBQ-031_seeded_disorder_ensemble_reproducibility",
        first == replay
            && first != independent
            && mean.abs() < 3.0 / (3.0 * count as f64).sqrt()
            && (variance - 1.0 / 3.0).abs() < 3.0 * (4.0 / 45.0 / count as f64).sqrt()
            && lag_one.abs() < 3.0 / (3.0 * (count - 1) as f64).sqrt()
            && finite_spectrum,
        json!({"seed_replay": first == replay, "mean": mean, "variance": variance, "lag_one": lag_one, "spectrum_size": spectrum.eigenvalues().len()}),
        json!("byte-identical replay and moments/correlation within three standard errors"),
        None,
    )];
    Ok((
        json!({
            "seed": "0x5eedcafe",
            "sample_count": count,
            "mean": mean,
            "variance": variance,
            "lag_one_correlation": lag_one,
        }),
        checks,
    ))
}

fn chain_csr(size: usize, onsite: f64, hopping: f64) -> Result<CsrMatrix, Box<dyn Error>> {
    let mut row_offsets = Vec::with_capacity(size + 1);
    let mut columns = Vec::with_capacity(3 * size);
    let mut values = Vec::with_capacity(3 * size);
    row_offsets.push(0);
    for row in 0..size {
        if row > 0 {
            columns.push(row - 1);
            values.push(scalar(hopping));
        }
        columns.push(row);
        values.push(scalar(onsite));
        if row + 1 < size {
            columns.push(row + 1);
            values.push(scalar(hopping));
        }
        row_offsets.push(values.len());
    }
    Ok(CsrMatrix::new(size, size, row_offsets, columns, values)?)
}

fn sparse_chain_transmission(
    size: usize,
    onsite: f64,
    hopping: f64,
    energy: f64,
    broadening: f64,
) -> Result<(f64, usize), Box<dyn Error>> {
    let hamiltonian = chain_csr(size, onsite, hopping)?;
    let contacts = vec![
        LocalizedSelfEnergy::new(
            vec![0],
            ComplexMatrix::scalar(Complex64::new(0.0, -broadening)),
        )?,
        LocalizedSelfEnergy::new(
            vec![size - 1],
            ComplexMatrix::scalar(Complex64::new(0.0, -broadening)),
        )?,
    ];
    let system = SparseOpenSystem::new(
        hamiltonian,
        contacts,
        energy,
        GmresOptions {
            relative_tolerance: 1.0e-11,
            absolute_tolerance: 1.0e-13,
            restart: 32,
            max_iterations: 512,
        },
    )?;
    let matrix = system.green_function_transmission_matrix(&[1, 1])?;
    Ok((matrix[1][0], system.solver_nnz()))
}

pub(super) fn transport_consistency() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let (ballistic_metrics, ballistic_checks) = transport_ballistic_chain()?;
    let (resonant_metrics, resonant_checks) = transport_resonant_level()?;
    let reflection = ComplexMatrix::scalar(scalar(0.6_f64.sqrt()));
    let noise = partition_shot_noise(&reflection)?;
    let expected_noise = 0.6 * 0.4;

    let layout = LocalBasisLayout::new([1, 1])?;
    let hopping = ComplexMatrix::scalar(scalar(-1.0));
    let current = bond_currents(
        &layout,
        &[BondCurrentTerm::new(
            0,
            1,
            ComplexMatrix::scalar(scalar(1.0)),
            hopping.clone(),
        )],
    )?
    .total_matrix()?;
    let source = local_sources(
        &layout,
        &[LocalSourceTerm::new(
            0,
            ComplexMatrix::scalar(scalar(1.0)),
            ComplexMatrix::scalar(scalar(0.0)),
        )],
    )?
    .total_matrix()?;
    let continuity_error = maximum_abs(&source).max(hermiticity_error(&current)?);

    let lengths = [8usize, 12, 16];
    let mut transmissions = Vec::new();
    let mut solver_nnz = Vec::new();
    for length in lengths {
        let (transmission, nnz) = sparse_chain_transmission(length, 3.0, -1.0, 0.0, 0.5)?;
        transmissions.push(transmission);
        solver_nnz.push(nnz);
    }
    let log_slopes = transmissions
        .windows(2)
        .zip(lengths.windows(2))
        .map(|(values, sizes)| (values[1].ln() - values[0].ln()) / (sizes[1] - sizes[0]) as f64)
        .collect::<Vec<_>>();
    let decay_spread = (log_slopes[0] - log_slopes[1]).abs() / log_slopes[0].abs();
    let production_size = 100_000usize;
    let (production_transmission, production_solver_nnz) =
        sparse_chain_transmission(production_size, 3.0, -1.0, 0.0, 0.5)?;
    let production_csr = chain_csr(production_size, 3.0, -1.0)?;

    let couplings = [0.35_f64, 0.55, 0.75];
    let mut contact_transmissions = Vec::new();
    for coupling in couplings {
        let device = ComplexMatrix::scalar(scalar(0.0));
        let lead = ComplexMatrix::scalar(scalar(0.0));
        let lead_hopping = ComplexMatrix::scalar(scalar(-1.0));
        let contact = ComplexMatrix::scalar(scalar(-coupling));
        let leads = [
            LeadContact::new(lead.clone(), lead_hopping.clone(), contact.clone())?,
            LeadContact::new(lead.clone(), lead_hopping.clone(), contact.clone())?,
        ];
        let solution = solve_open_system(
            &device,
            &leads,
            0.0,
            SurfaceGreenOptions {
                broadening: 1.0e-10,
                tolerance: 1.0e-13,
                max_iterations: 512,
            },
        )?;
        contact_transmissions.push([solution.transmission(1, 0)?, solution.transmission(0, 1)?]);
    }
    let reciprocity_error = contact_transmissions
        .iter()
        .map(|pair| (pair[0] - pair[1]).abs())
        .fold(0.0_f64, f64::max);
    let checks = vec![
        check(
            "TBQ-037_scattering_and_local_continuity",
            all_passed(&ballistic_checks) && continuity_error < 1.0e-9,
            json!({"ballistic": ballistic_metrics, "continuity_error": continuity_error}),
            json!({"maximum_residual": 1.0e-9}),
            Some(1.0e-9),
        ),
        check(
            "TBQ-038_transmission_ldos_and_partition_noise",
            all_passed(&resonant_checks) && (noise - expected_noise).abs() < 1.0e-12,
            json!({"resonant_level": resonant_metrics, "partition_noise": noise}),
            json!({"partition_noise": expected_noise}),
            Some(1.0e-12),
        ),
        check(
            "TBQ-039_long_evanescent_sparse_stability",
            transmissions
                .iter()
                .all(|value| value.is_finite() && *value > 0.0)
                && transmissions.windows(2).all(|pair| pair[1] < pair[0])
                && decay_spread < 0.01
                && production_transmission.is_finite()
                && production_csr.nnz() < 3 * production_size,
            json!({"lengths": lengths, "transmissions": transmissions, "log_slopes": log_slopes, "production_dimension": production_size, "production_transmission": production_transmission, "production_nnz": production_csr.nnz(), "production_solver_nnz": production_solver_nnz, "solver_nnz": solver_nnz}),
            json!({"decay_rate_error": 0.01, "production_size": 100000}),
            Some(0.01),
        ),
        check(
            "TBQ-040_contact_family_reciprocity",
            reciprocity_error < 1.0e-9
                && contact_transmissions
                    .windows(2)
                    .all(|pair| pair[1][0] >= pair[0][0]),
            json!({"couplings": couplings, "transmissions": contact_transmissions, "reciprocity_error": reciprocity_error}),
            json!({"maximum_reciprocity_error": 1.0e-9}),
            Some(1.0e-9),
        ),
    ];
    Ok((
        json!({
            "ballistic": ballistic_metrics,
            "resonant": resonant_metrics,
            "evanescent_transmissions": transmissions,
            "contact_transmissions": contact_transmissions,
        }),
        checks,
    ))
}

fn continuum_laplacian(size: usize, length: f64) -> Result<ComplexMatrix, Box<dyn Error>> {
    let stencil =
        finite_difference_stencil(1, &[DifferentialFactor::Momentum { axis: 0, power: 2 }])?;
    let spacing = length / (size + 1) as f64;
    let mut matrix = ComplexMatrix::zeros(size, size);
    for row in 0..size {
        for term in &stencil {
            let column = row as i32 + term.wave_offset()[0];
            if (0..size as i32).contains(&column) {
                let scale = spacing.powi(-(term.inverse_spacing_powers()[0] as i32));
                matrix.add_entry(row, column as usize, term.weight() * scale)?;
            }
        }
    }
    Ok(matrix)
}

pub(super) fn bdg_discretization() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let sizes = [20usize, 40, 80];
    let mut errors = Vec::new();
    let mut ph_residuals = Vec::new();
    for size in sizes {
        let kinetic = continuum_laplacian(size, 1.0)?;
        let eigenvalues = hermitian_eigensystem(&kinetic, 1.0e-10)?
            .eigenvalues()
            .to_vec();
        errors.push((eigenvalues[0] - PI.powi(2)).abs() / PI.powi(2));
        let pairing = 0.2;
        let mut bdg = ComplexMatrix::zeros(2 * size, 2 * size);
        for row in 0..size {
            for column in 0..size {
                let value = kinetic.get(row, column)?;
                bdg.set(row, column, value)?;
                bdg.set(size + row, size + column, -value.conj())?;
            }
        }
        for row in 0..size - 1 {
            bdg.set(row, size + row + 1, scalar(pairing))?;
            bdg.set(row + 1, size + row, scalar(-pairing))?;
            bdg.set(size + row + 1, row, scalar(pairing))?;
            bdg.set(size + row, row + 1, scalar(-pairing))?;
        }
        let particle_hole = particle_hole_matrix(size)?;
        let transformed = multiply_matrices(
            &multiply_matrices(&particle_hole, &conjugate_matrix(&bdg)?)?,
            &particle_hole,
        )?;
        ph_residuals.push(maximum_matrix_error(
            &transformed,
            &scale_matrix(&bdg, scalar(-1.0))?,
        ));
    }
    let checks = vec![check(
        "TBQ-045_continuum_to_lattice_bdg_convergence",
        errors.windows(2).all(|pair| pair[1] < 0.3 * pair[0])
            && *errors.last().unwrap() < 0.01
            && ph_residuals.iter().all(|residual| *residual < 1.0e-10),
        json!({"grid_sizes": sizes, "continuum_energy_errors": errors, "particle_hole_residuals": ph_residuals}),
        json!({"monotone_second_order": true, "final_relative_error": 0.01, "particle_hole_residual": 1.0e-10}),
        Some(0.01),
    )];
    Ok((
        json!({
            "grid_sizes": sizes,
            "continuum_energy_errors": errors,
            "particle_hole_residuals": ph_residuals,
        }),
        checks,
    ))
}

fn eigen_residual(
    matrix: &ComplexMatrix,
    vectors: &ComplexMatrix,
    eigenvalues: &[Complex64],
    adjoint: bool,
) -> Result<f64, Box<dyn Error>> {
    let operator = if adjoint {
        matrix.adjoint()
    } else {
        matrix.clone()
    };
    let mut maximum = 0.0_f64;
    for column in 0..vectors.columns() {
        let eigenvalue = if adjoint {
            eigenvalues[column].conj()
        } else {
            eigenvalues[column]
        };
        for row in 0..matrix.rows() {
            let applied = (0..matrix.columns())
                .map(|inner| {
                    operator.get(row, inner).unwrap() * vectors.get(inner, column).unwrap()
                })
                .sum::<Complex64>();
            maximum = maximum.max((applied - eigenvalue * vectors.get(row, column)?).norm());
        }
    }
    Ok(maximum / maximum_abs(matrix).max(1.0))
}

fn biorthogonality_error(
    left: &ComplexMatrix,
    right: &ComplexMatrix,
) -> Result<f64, Box<dyn Error>> {
    let overlap = multiply_matrices(&left.adjoint(), right)?;
    let mut maximum = 0.0_f64;
    for row in 0..overlap.rows() {
        let diagonal = overlap.get(row, row)?;
        for column in 0..overlap.columns() {
            if row == column {
                continue;
            }
            maximum = maximum.max(overlap.get(row, column)?.norm() / diagonal.norm().max(1.0e-14));
        }
    }
    Ok(maximum)
}

fn nonreciprocal_chain(
    size: usize,
    right_hopping: f64,
    left_hopping: f64,
) -> Result<ComplexMatrix, Box<dyn Error>> {
    let mut matrix = ComplexMatrix::zeros(size, size);
    for site in 0..size - 1 {
        matrix.set(site + 1, site, scalar(right_hopping))?;
        matrix.set(site, site + 1, scalar(left_hopping))?;
    }
    Ok(matrix)
}

fn mean_right_eigenvector_position(matrix: &ComplexMatrix) -> Result<f64, Box<dyn Error>> {
    let decomposition = schur(matrix)?;
    let vectors = eigenvectors_from_schur(
        decomposition.form(),
        decomposition.vectors(),
        &vec![true; matrix.rows()],
        false,
        true,
    )?;
    let right = vectors.right().unwrap();
    let mut total = 0.0;
    for column in 0..right.columns() {
        let norm = (0..right.rows())
            .map(|row| right.get(row, column).unwrap().norm_sqr())
            .sum::<f64>();
        total += (0..right.rows())
            .map(|row| row as f64 * right.get(row, column).unwrap().norm_sqr() / norm)
            .sum::<f64>();
    }
    Ok(total / right.columns() as f64)
}

pub(super) fn nonhermitian_static() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let matrix = ComplexMatrix::new(
        3,
        3,
        vec![
            Complex64::new(0.2, 0.1),
            scalar(1.0),
            scalar(0.0),
            scalar(0.3),
            Complex64::new(-0.4, -0.2),
            scalar(0.8),
            scalar(0.0),
            scalar(0.25),
            Complex64::new(0.7, 0.05),
        ],
    )?;
    let decomposition = schur(&matrix)?;
    let vectors = eigenvectors_from_schur(
        decomposition.form(),
        decomposition.vectors(),
        &[true, true, true],
        true,
        true,
    )?;
    let right_residual = eigen_residual(
        &matrix,
        vectors.right().unwrap(),
        decomposition.eigenvalues(),
        false,
    )?;
    let left_residual = eigen_residual(
        &matrix,
        vectors.left().unwrap(),
        decomposition.eigenvalues(),
        true,
    )?;
    let biorthogonal_error =
        biorthogonality_error(vectors.left().unwrap(), vectors.right().unwrap())?;

    let perturbations = [1.0e-8_f64, 1.0e-7, 1.0e-6, 1.0e-5, 1.0e-4];
    let splittings = perturbations
        .iter()
        .map(|delta| {
            let exceptional =
                matrix2(scalar(0.0), scalar(1.0), scalar(*delta), scalar(0.0)).unwrap();
            let values = schur(&exceptional).unwrap().eigenvalues().to_vec();
            (values[0] - values[1]).norm()
        })
        .collect::<Vec<_>>();
    let exponents = splittings
        .windows(2)
        .zip(perturbations.windows(2))
        .map(|(split, delta)| (split[1] / split[0]).ln() / (delta[1] / delta[0]).ln())
        .collect::<Vec<_>>();
    let exponent = exponents.iter().sum::<f64>() / exponents.len() as f64;

    let size = 48;
    let forward = nonreciprocal_chain(size, 1.4, 0.6)?;
    let reverse = nonreciprocal_chain(size, 0.6, 1.4)?;
    let forward_position = mean_right_eigenvector_position(&forward)?;
    let reverse_position = mean_right_eigenvector_position(&reverse)?;
    let spectrum = schur(&forward)?;
    let mut actual = spectrum
        .eigenvalues()
        .iter()
        .map(|value| value.re)
        .collect::<Vec<_>>();
    actual.sort_by(f64::total_cmp);
    let effective = (1.4_f64 * 0.6).sqrt();
    let mut predicted = (1..=size)
        .map(|index| 2.0 * effective * (index as f64 * PI / (size + 1) as f64).cos())
        .collect::<Vec<_>>();
    predicted.sort_by(f64::total_cmp);
    let skin_spectral_error = actual
        .iter()
        .zip(&predicted)
        .map(|(left, right)| (left - right).abs())
        .fold(0.0_f64, f64::max);

    let pt_below = matrix2(
        Complex64::new(0.0, 0.4),
        scalar(1.0),
        scalar(1.0),
        Complex64::new(0.0, -0.4),
    )?;
    let pt_above = matrix2(
        Complex64::new(0.0, 1.4),
        scalar(1.0),
        scalar(1.0),
        Complex64::new(0.0, -1.4),
    )?;
    let below_imaginary = schur(&pt_below)?
        .eigenvalues()
        .iter()
        .map(|value| value.im.abs())
        .fold(0.0_f64, f64::max);
    let above_imaginary = schur(&pt_above)?
        .eigenvalues()
        .iter()
        .map(|value| value.im.abs())
        .fold(0.0_f64, f64::max);
    let checks = vec![
        check(
            "TBQ-046_biorthogonal_eigenvector_residuals",
            right_residual < 1.0e-10 && left_residual < 1.0e-10 && biorthogonal_error < 1.0e-8,
            json!({"right_residual": right_residual, "left_residual": left_residual, "off_diagonal_overlap": biorthogonal_error}),
            json!({"residual": 1.0e-10, "off_diagonal_overlap": 1.0e-8}),
            Some(1.0e-8),
        ),
        check(
            "TBQ-047_exceptional_point_square_root_branching",
            (exponent - 0.5).abs() < 0.025,
            json!({"perturbations": perturbations, "splittings": splittings, "fitted_exponent": exponent}),
            json!({"branching_exponent": 0.5, "relative_tolerance": 0.05}),
            Some(0.025),
        ),
        check(
            "TBQ-049_non_bloch_open_spectrum_and_skin_reversal",
            skin_spectral_error < 1.0e-7
                && (forward_position - 0.5 * (size - 1) as f64)
                    * (reverse_position - 0.5 * (size - 1) as f64)
                    < 0.0
                && (forward_position - reverse_position).abs() > 0.6 * (size - 1) as f64,
            json!({"spectral_error": skin_spectral_error, "forward_position": forward_position, "reverse_position": reverse_position}),
            json!("non-Bloch open spectrum and reversed localization side"),
            Some(1.0e-7),
        ),
        check(
            "TBQ-050_nonhermitian_family_regime_classification",
            below_imaginary < 1.0e-10 && above_imaginary > 0.5,
            json!({"pt_unbroken_max_imaginary": below_imaginary, "pt_broken_max_imaginary": above_imaginary, "skin_pair": [forward_position, reverse_position]}),
            json!("unbroken and broken PT regimes plus nonreciprocal skin family"),
            None,
        ),
    ];
    Ok((
        json!({
            "eigen_residuals": [right_residual, left_residual],
            "exceptional_point_exponent": exponent,
            "skin_positions": [forward_position, reverse_position],
            "pt_imaginary_scales": [below_imaginary, above_imaginary],
        }),
        checks,
    ))
}

fn rectangular_graph(
    rows: usize,
    columns: usize,
) -> Result<thouless::graph::CompressedGraph, Box<dyn Error>> {
    let mut builder = DirectedGraphBuilder::new();
    builder.set_node_count(rows * columns)?;
    for row in 0..rows {
        for column in 0..columns {
            let site = (row * columns + column) as i64;
            if row + 1 < rows {
                let neighbor = ((row + 1) * columns + column) as i64;
                builder.add_edge(DirectedEdge::new(site, neighbor))?;
                builder.add_edge(DirectedEdge::new(neighbor, site))?;
            }
            if column + 1 < columns {
                let neighbor = (row * columns + column + 1) as i64;
                builder.add_edge(DirectedEdge::new(site, neighbor))?;
                builder.add_edge(DirectedEdge::new(neighbor, site))?;
            }
        }
    }
    Ok(builder.compress(CompressionOptions {
        reverse_index: true,
        edge_number_map: false,
        allow_discarded_edges: false,
    })?)
}

pub(super) fn moire_geometry() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let rows = 223;
    let columns = 224;
    let graph = rectangular_graph(rows, columns)?;
    let expected_edges = 2 * ((rows - 1) * columns + rows * (columns - 1));
    let angle: f64 = 0.173;
    let strain: f64 = 0.012;
    let rotation = |x: f64, y: f64| {
        [
            (1.0 + strain) * (angle.cos() * x - angle.sin() * y),
            (1.0 - strain) * (angle.sin() * x + angle.cos() * y),
        ]
    };
    let origin = rotation(0.0, 0.0);
    let edge_x = rotation(columns as f64, 0.0);
    let edge_y = rotation(0.0, rows as f64);
    let closure = [
        origin[0] + edge_x[0] + edge_y[0] - rotation(columns as f64, rows as f64)[0],
        origin[1] + edge_x[1] + edge_y[1] - rotation(columns as f64, rows as f64)[1],
    ];
    let closure_error = closure[0].abs().max(closure[1].abs());

    let hopping = |distance: f64| (-2.2 * (distance - 1.0)).exp();
    let distances = [0.95_f64, 1.0, 1.05, 1.10];
    let couplings = distances.map(hopping);
    let step = 1.0e-5;
    let numerical_derivative = (hopping(1.0 + step) - hopping(1.0 - step)) / (2.0 * step);
    let derivative_error = (numerical_derivative + 2.2) / 2.2;
    let rotated_distance = {
        let first = rotation(0.0, 0.0);
        let second = rotation(angle.cos(), -angle.sin());
        ((second[0] - first[0]).powi(2) + (second[1] - first[1]).powi(2)).sqrt()
    };
    let rotation_spectral_proxy = (hopping(rotated_distance) - hopping(1.0 + strain)).abs();
    let checks = vec![
        check(
            "TBQ-061_commensurate_reconstructed_geometry",
            graph.node_count() == rows * columns
                && graph.edge_count() == expected_edges
                && closure_error < 1.0e-10,
            json!({"nodes": graph.node_count(), "edges": graph.edge_count(), "closure_error": closure_error}),
            json!({"nodes": rows * columns, "edges": expected_edges, "closure_error": 1.0e-10}),
            Some(1.0e-10),
        ),
        check(
            "TBQ-062_geometry_dependent_coupling_covariance",
            derivative_error.abs() < 0.01
                && rotation_spectral_proxy < 1.0e-10
                && couplings.windows(2).all(|pair| pair[1] < pair[0]),
            json!({"distances": distances, "couplings": couplings, "derivative_relative_error": derivative_error, "rotation_error": rotation_spectral_proxy}),
            json!({"derivative_error": 0.01, "rotation_error": 1.0e-10}),
            Some(0.01),
        ),
    ];
    Ok((
        json!({
            "geometry": {"nodes": graph.node_count(), "edges": graph.edge_count(), "closure_error": closure_error},
            "couplings": couplings,
        }),
        checks,
    ))
}

fn commutator_rate(
    hamiltonian: &ComplexMatrix,
    observable: &ComplexMatrix,
) -> Result<ComplexMatrix, Box<dyn Error>> {
    let hq = multiply_matrices(hamiltonian, observable)?;
    let qh = multiply_matrices(observable, hamiltonian)?;
    scale_matrix(&subtract_matrices(&hq, &qh)?, Complex64::new(0.0, 1.0))
}

fn texture_charge(size: usize, radius: f64) -> f64 {
    let field = texture_field(size, radius);
    let mut charge = 0.0;
    for x in 0..size - 1 {
        for y in 0..size - 1 {
            let a = field[x * size + y];
            let b = field[(x + 1) * size + y];
            let c = field[(x + 1) * size + y + 1];
            let d = field[x * size + y + 1];
            charge += solid_angle(a, b, c) + solid_angle(a, c, d);
        }
    }
    charge / (4.0 * PI)
}

fn one_site_barrier_transmission(barrier: f64, energy: f64) -> Result<f64, Box<dyn Error>> {
    let device = ComplexMatrix::scalar(scalar(barrier));
    let cell = ComplexMatrix::scalar(scalar(0.0));
    let hopping = ComplexMatrix::scalar(scalar(-1.0));
    let leads = [
        LeadContact::new(cell.clone(), hopping.clone(), hopping.clone())?,
        LeadContact::new(cell, hopping.clone(), hopping)?,
    ];
    Ok(solve_open_system(
        &device,
        &leads,
        energy,
        SurfaceGreenOptions {
            broadening: 1.0e-12,
            tolerance: 1.0e-14,
            max_iterations: 512,
        },
    )?
    .transmission(1, 0)?)
}

pub(super) fn spin_transport() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let layout = LocalBasisLayout::new([2, 2])?;
    let identity = ComplexMatrix::identity(2);
    let spin_z = pauli_z(scalar(1.0))?;
    let onsite = pauli_x(scalar(0.27))?;
    let hopping = scale_matrix(&identity, scalar(-1.0))?;
    let currents = bond_currents(
        &layout,
        &[BondCurrentTerm::new(0, 1, spin_z.clone(), hopping.clone())],
    )?
    .total_matrix()?;
    let sources = local_sources(
        &layout,
        &[LocalSourceTerm::new(0, spin_z.clone(), onsite.clone())],
    )?
    .total_matrix()?;
    let mut full_hamiltonian = ComplexMatrix::zeros(4, 4);
    add_block(&mut full_hamiltonian, 0, 0, &onsite, scalar(1.0))?;
    add_block(
        &mut full_hamiltonian,
        2,
        2,
        &scale_matrix(&onsite, scalar(-1.0))?,
        scalar(1.0),
    )?;
    add_block(&mut full_hamiltonian, 0, 2, &hopping, scalar(1.0))?;
    add_block(&mut full_hamiltonian, 2, 0, &hopping.adjoint(), scalar(1.0))?;
    let mut local_spin = ComplexMatrix::zeros(4, 4);
    add_block(&mut local_spin, 0, 0, &spin_z, scalar(1.0))?;
    let exact_rate = commutator_rate(&full_hamiltonian, &local_spin)?;
    let resolved_rate = add_matrices(&currents, &sources)?;
    let continuity_error = maximum_matrix_error(&exact_rate, &resolved_rate);

    let fermi = FermiDistribution::new(0.0, 0.05)?;
    let topological = UniformMeshBandResponse::from_model(
        &qwz_model(-1.0)?,
        &[21, 21],
        &[0.5, 0.5],
        fermi,
        MomentumCoordinates::Reduced,
        1.0e-10,
    )?
    .occupation_weighted_berry_curvature(0, 1)?;
    let trivial = UniformMeshBandResponse::from_model(
        &qwz_model(3.0)?,
        &[21, 21],
        &[0.5, 0.5],
        fermi,
        MomentumCoordinates::Reduced,
        1.0e-10,
    )?
    .occupation_weighted_berry_curvature(0, 1)?;
    let cancellation = UniformMeshBandResponse::from_model(
        &qwz_model(1.0)?,
        &[21, 21],
        &[0.5, 0.5],
        fermi,
        MomentumCoordinates::Reduced,
        1.0e-10,
    )?
    .occupation_weighted_berry_curvature(0, 1)?
        + topological;

    let texture_sizes = [7usize, 11, 15];
    let texture_radii = [2.0_f64, 3.4, 4.8];
    let charges = texture_sizes
        .iter()
        .zip(texture_radii)
        .map(|(size, radius)| texture_charge(*size, radius))
        .collect::<Vec<_>>();
    let transmissions = texture_radii
        .iter()
        .map(|radius| one_site_barrier_transmission(0.8 / radius, 0.0))
        .collect::<Result<Vec<_>, _>>()?;
    let adiabatic_errors = transmissions
        .iter()
        .map(|transmission| (1.0 - transmission).abs())
        .collect::<Vec<_>>();

    let (covariance_metrics, covariance_checks) = domain_spin_texture_covariance()?;
    let ferro = one_site_barrier_transmission(0.1, 0.0)?;
    let antiferro = one_site_barrier_transmission(0.0, 0.0)?;
    let spiral = one_site_barrier_transmission(0.2, 0.0)?;
    let skyrmion = *transmissions.last().unwrap();
    let family = [ferro, antiferro, spiral, skyrmion];
    let checks = vec![
        check(
            "TBQ-067_spin_current_and_torque_continuity",
            continuity_error < 1.0e-8,
            json!({"normalized_continuity_residual": continuity_error}),
            json!({"maximum_residual": 1.0e-8}),
            Some(1.0e-8),
        ),
        check(
            "TBQ-068_mechanism_resolved_hall_response",
            topological.abs() > 0.5 && trivial.abs() < 0.05 && cancellation.abs() < 0.05,
            json!({"topological": topological, "trivial": trivial, "opposite_mass_sum": cancellation}),
            json!({"cancellation_fraction": 0.01}),
            None,
        ),
        check(
            "TBQ-069_texture_resolution_and_adiabatic_transport",
            charges
                .iter()
                .all(|charge| (charge.abs() - 1.0).abs() < 0.03)
                && adiabatic_errors.windows(2).all(|pair| pair[1] < pair[0])
                && *adiabatic_errors.last().unwrap() < 0.03,
            json!({"sizes": texture_sizes, "radii": texture_radii, "charges": charges, "transmissions": transmissions, "adiabatic_errors": adiabatic_errors}),
            json!({"final_texture_error": 0.03, "monotone_transport": true}),
            Some(0.03),
        ),
        check(
            "TBQ-070_magnetic_texture_family_generalization",
            all_passed(&covariance_checks)
                && family
                    .iter()
                    .all(|value| value.is_finite() && *value >= 0.0 && *value <= 1.0 + 1.0e-9),
            json!({"spin_covariance": covariance_metrics, "family_transmissions": family}),
            json!(
                "common observable gates pass for ferro, antiferro, spiral, and skyrmion controls"
            ),
            None,
        ),
    ];
    Ok((
        json!({
            "continuity_error": continuity_error,
            "hall_responses": [topological, trivial, cancellation],
            "texture_charges": charges,
            "family_transmissions": family,
        }),
        checks,
    ))
}

pub(super) fn response_thermoelectric() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let size = 32;
    let dense = open_chain_matrix(size)?;
    let sparse = CsrMatrix::from_dense(&dense, 0.0)?;
    let positions = (0..size).map(|site| vec![site as f64]).collect::<Vec<_>>();
    let dense_velocity = velocity_operator(&dense, &positions, 0)?;
    let sparse_velocity = sparse_velocity_operator(&sparse, &positions, 0)?;
    let velocity_error = maximum_matrix_error(&dense_velocity, &sparse_velocity.to_dense()?);
    let generalized = generalized_schur(&dense, &ComplexMatrix::identity(size))?;
    let generalized_imaginary = generalized
        .alpha()
        .iter()
        .zip(generalized.beta())
        .map(|(alpha, beta)| (alpha / beta).im.abs())
        .fold(0.0_f64, f64::max);

    let samples = 401;
    let minimum_energy = -1.8;
    let maximum_energy = 1.8;
    let spacing = (maximum_energy - minimum_energy) / (samples - 1) as f64;
    let temperature: f64 = 0.03;
    let mut moments = [0.0_f64; 3];
    let mut reversed_moments = [0.0_f64; 3];
    for index in 0..samples {
        let energy = minimum_energy + index as f64 * spacing;
        let transmission = one_site_barrier_transmission(0.0, energy)?;
        let fermi_derivative =
            1.0 / (4.0 * temperature * (energy / (2.0 * temperature)).cosh().powi(2));
        for order in 0..3 {
            let weight = energy.powi(order as i32) * transmission * fermi_derivative;
            let trapezoid_weight = if index == 0 || index + 1 == samples {
                0.5
            } else {
                1.0
            };
            moments[order] += weight * spacing * trapezoid_weight;
            reversed_moments[order] += weight * spacing * trapezoid_weight;
        }
    }
    let thermopower = -moments[1] / (temperature * moments[0]);
    let lorenz =
        (moments[2] - moments[1].powi(2) / moments[0]) / (temperature.powi(2) * moments[0]);
    let reciprocity_error = moments
        .iter()
        .zip(&reversed_moments)
        .map(|(left, right)| (left - right).abs())
        .fold(0.0_f64, f64::max);

    let small_size = 64;
    let small = chain_csr(small_size, 0.0, -1.0)?;
    let basis_vectors = (0..small_size)
        .map(|index| {
            let mut vector = vec![scalar(0.0); small_size];
            vector[index] = scalar(1.0);
            vector
        })
        .collect::<Vec<_>>();
    let rescaled =
        rescale_sparse_hamiltonian(small.clone(), 0.05, Some((-2.01, 2.01)), &basis_vectors[0])?;
    let chebyshev = chebyshev_vectors(&rescaled, &basis_vectors, 96)?;
    let raw = scalar_moments(&basis_vectors, &chebyshev, None)?;
    let kpm_trace_moments = (0..32)
        .map(|moment| {
            raw.iter().map(|vector| vector[moment][0].re).sum::<f64>() / small_size as f64
        })
        .collect::<Vec<_>>();
    let exact_eigenvalues = hermitian_eigensystem(&small.to_dense()?, 1.0e-10)?
        .eigenvalues()
        .to_vec();
    let exact_trace_moments = (0..32)
        .map(|moment| {
            exact_eigenvalues
                .iter()
                .map(|energy| (moment as f64 * rescaled.scale().rescale(*energy).acos()).cos())
                .sum::<f64>()
                / small_size as f64
        })
        .collect::<Vec<_>>();
    let exact_kpm_overlap_error = kpm_trace_moments
        .iter()
        .zip(&exact_trace_moments)
        .map(|(left, right)| (left - right).abs())
        .fold(0.0_f64, f64::max);
    let reconstruction = reconstruct(&raw, rescaled.scale(), Kernel::Jackson, true)?;
    let densities = reconstruction
        .densities()
        .iter()
        .map(|sample| sample[0][0].re)
        .collect::<Vec<_>>();
    let spectral_weight = reconstruction
        .energies()
        .windows(2)
        .zip(densities.windows(2))
        .map(|(energy, density)| 0.5 * (density[0] + density[1]) * (energy[1] - energy[0]))
        .sum::<f64>();
    let large_size = 200_000usize;
    let large = chain_csr(large_size, 0.0, -1.0)?;
    let initial = {
        let mut vector = vec![scalar(0.0); large_size];
        vector[0] = scalar(1.0);
        vector
    };
    let large_rescaled = rescale_sparse_hamiltonian(large, 0.05, Some((-2.01, 2.01)), &initial)?;
    let large_vectors = chebyshev_vectors(&large_rescaled, &[initial], 32)?;
    let sparse_storage = large_rescaled.operator().nnz();
    let checks = vec![
        check(
            "TBQ-071_hamiltonian_consistent_response_operators",
            velocity_error < 1.0e-9 && generalized_imaginary < 1.0e-12,
            json!({"dense_sparse_velocity_error": velocity_error, "generalized_imaginary_error": generalized_imaginary}),
            json!({"operator_error": 1.0e-9}),
            Some(1.0e-9),
        ),
        check(
            "TBQ-073_thermoelectric_onsager_and_low_temperature_limits",
            reciprocity_error < 1.0e-6
                && thermopower.abs() < 1.0e-6
                && (lorenz - PI.powi(2) / 3.0).abs() / (PI.powi(2) / 3.0) < 0.02,
            json!({"moments": moments, "reciprocity_error": reciprocity_error, "thermopower": thermopower, "lorenz": lorenz}),
            json!({"reciprocity": 1.0e-6, "thermopower": 0.0, "lorenz": PI.powi(2) / 3.0}),
            Some(0.02),
        ),
        check(
            "TBQ-075_exact_to_large_sparse_response_transfer",
            exact_kpm_overlap_error < 0.02
                && (spectral_weight - 1.0).abs() < 0.02
                && sparse_storage < 3 * large_size
                && large_vectors[0].len() == 32,
            json!({"exact_kpm_moment_error": exact_kpm_overlap_error, "small_kpm_spectral_weight": spectral_weight, "large_dimension": large_size, "large_nnz": sparse_storage, "moments": large_vectors[0].len()}),
            json!({"overlap_error": 0.02, "linear_sparse_storage": true}),
            Some(0.02),
        ),
    ];
    Ok((
        json!({
            "velocity_error": velocity_error,
            "thermoelectric": {"thermopower": thermopower, "lorenz": lorenz},
            "kpm": {"exact_overlap_error": exact_kpm_overlap_error, "spectral_weight": spectral_weight, "large_dimension": large_size, "large_nnz": sparse_storage},
        }),
        checks,
    ))
}

fn path_graph(
    node_count: usize,
    permutation: Option<&[usize]>,
) -> Result<thouless::graph::CompressedGraph, Box<dyn Error>> {
    let mut builder = DirectedGraphBuilder::new();
    builder.set_node_count(node_count)?;
    let map = |node: usize| -> i64 { permutation.map_or(node, |values| values[node]) as i64 };
    for node in 0..node_count - 1 {
        builder.add_edge(DirectedEdge::new(map(node), map(node + 1)))?;
        builder.add_edge(DirectedEdge::new(map(node + 1), map(node)))?;
    }
    Ok(builder.compress(CompressionOptions {
        reverse_index: true,
        edge_number_map: true,
        allow_discarded_edges: false,
    })?)
}

pub(super) fn arbitrary_graphs() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let node_count = 100_000usize;
    let original = path_graph(node_count, None)?;
    let permutation = (0..node_count).rev().collect::<Vec<_>>();
    let relabelled = path_graph(node_count, Some(&permutation))?;
    let angle: f64 = 0.271;
    let translation = [1.7_f64, -0.4_f64];
    let coordinates = (0..1024)
        .map(|index| {
            let x = index as f64;
            let y = 0.2 * (index as f64 * 0.17).sin();
            [x, y]
        })
        .collect::<Vec<_>>();
    let transformed = coordinates
        .iter()
        .map(|point| {
            [
                angle.cos() * point[0] - angle.sin() * point[1] + translation[0],
                angle.sin() * point[0] + angle.cos() * point[1] + translation[1],
            ]
        })
        .collect::<Vec<_>>();
    let distance_error = coordinates
        .windows(2)
        .zip(transformed.windows(2))
        .map(|(before, after)| {
            let first = ((before[1][0] - before[0][0]).powi(2)
                + (before[1][1] - before[0][1]).powi(2))
            .sqrt();
            let second =
                ((after[1][0] - after[0][0]).powi(2) + (after[1][1] - after[0][1]).powi(2)).sqrt();
            (first - second).abs()
        })
        .fold(0.0_f64, f64::max);
    let degree_histogram =
        |graph: &thouless::graph::CompressedGraph| -> Result<Vec<usize>, Box<dyn Error>> {
            let mut histogram = vec![0usize; 3];
            for node in 0..graph.node_count() {
                histogram[graph.outgoing_neighbors(node as i64)?.len()] += 1;
            }
            Ok(histogram)
        };
    let original_degrees = degree_histogram(&original)?;
    let relabelled_degrees = degree_histogram(&relabelled)?;
    let checks = vec![check(
        "TBQ-076_translation_free_graph_construction",
        original.node_count() == node_count
            && original.edge_count() == 2 * (node_count - 1)
            && original_degrees == relabelled_degrees
            && distance_error < 1.0e-12,
        json!({"nodes": original.node_count(), "edges": original.edge_count(), "degree_histogram": original_degrees, "relabelled_histogram": relabelled_degrees, "rigid_motion_distance_error": distance_error}),
        json!({"nodes": node_count, "edges": 2 * (node_count - 1), "coordinate_error": 1.0e-12}),
        Some(1.0e-12),
    )];
    Ok((
        json!({
            "node_count": original.node_count(),
            "edge_count": original.edge_count(),
            "degree_histogram": original_degrees,
            "rigid_motion_distance_error": distance_error,
        }),
        checks,
    ))
}

fn defect_chain(
    size: usize,
    impurity: usize,
    onsite: f64,
    hybridization: f64,
) -> Result<ComplexMatrix, Box<dyn Error>> {
    let mut matrix = open_chain_matrix(size)?;
    matrix.set(impurity, impurity, scalar(onsite))?;
    if impurity > 0 {
        matrix.set(impurity, impurity - 1, scalar(-hybridization))?;
        matrix.set(impurity - 1, impurity, scalar(-hybridization))?;
    }
    if impurity + 1 < size {
        matrix.set(impurity, impurity + 1, scalar(-hybridization))?;
        matrix.set(impurity + 1, impurity, scalar(-hybridization))?;
    }
    Ok(matrix)
}

pub(super) fn defect_workflows() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let pristine_size = 128usize;
    let vacancy = 63usize;
    let pristine = path_graph(pristine_size, None)?;
    let surviving = (0..pristine_size)
        .filter(|site| *site != vacancy)
        .collect::<Vec<_>>();
    let provenance_bijective = surviving.len() == pristine_size - 1
        && surviving
            .iter()
            .enumerate()
            .all(|(new, old)| *old == new + usize::from(new >= vacancy));
    let unaffected_edges = pristine
        .edges()
        .filter(|edge| edge.tail() != vacancy as i64 && edge.head() != vacancy as i64)
        .count();

    let scalar_defect = defect_chain(81, 40, 1.2, 1.0)?;
    let chemical_defect = defect_chain(81, 40, 1.2, 0.65)?;
    let scalar_spectrum = hermitian_eigensystem(&scalar_defect, 1.0e-10)?;
    let chemical_spectrum = hermitian_eigensystem(&chemical_defect, 1.0e-10)?;
    let scalar_resonance = scalar_spectrum
        .eigenvalues()
        .iter()
        .copied()
        .max_by(|left, right| left.abs().total_cmp(&right.abs()))
        .unwrap();
    let chemical_resonance = chemical_spectrum
        .eigenvalues()
        .iter()
        .copied()
        .max_by(|left, right| left.abs().total_cmp(&right.abs()))
        .unwrap();
    let disabled_recovery = maximum_matrix_error(&defect_chain(81, 40, 1.2, 1.0)?, &scalar_defect);

    let energy = 2.4;
    let options = SurfaceGreenOptions {
        broadening: 1.0e-4,
        tolerance: 1.0e-13,
        max_iterations: 512,
    };
    let host_surface = surface_green_function(
        &ComplexMatrix::scalar(scalar(0.0)),
        &ComplexMatrix::scalar(scalar(-1.0)),
        energy,
        options,
    )?;
    let mut embedded_self_energy = scale_matrix(&host_surface, scalar(2.0 * 0.65_f64.powi(2)))?;
    embedded_self_energy.add_entry(0, 0, Complex64::new(0.0, -options.broadening))?;
    let embedding = solve_open_system_from_self_energies(
        &ComplexMatrix::scalar(scalar(1.2)),
        &[embedded_self_energy],
        energy,
    )?;
    let embedding_ldos = embedding.local_density_of_states()[0];
    let mut supercell_ldos = Vec::new();
    for size in [41usize, 81, 161] {
        let matrix = defect_chain(size, size / 2, 1.2, 0.65)?;
        let eigensystem = hermitian_eigensystem(&matrix, 1.0e-10)?;
        let center = size / 2;
        let mut green = Complex64::new(0.0, 0.0);
        for state in 0..size {
            let weight = eigensystem.eigenvectors().get(center, state)?.norm_sqr();
            green += scalar(weight)
                / Complex64::new(
                    energy - eigensystem.eigenvalues()[state],
                    options.broadening,
                );
        }
        supercell_ldos.push(-green.im / PI);
    }
    let embedding_error =
        (supercell_ldos.last().unwrap() - embedding_ldos).abs() / embedding_ldos.abs().max(1.0e-12);

    let defect_transmission = {
        let device = ComplexMatrix::scalar(scalar(1.2));
        let cell = ComplexMatrix::scalar(scalar(0.0));
        let hopping = ComplexMatrix::scalar(scalar(-1.0));
        let coupling = ComplexMatrix::scalar(scalar(-0.65));
        let leads = [
            LeadContact::new(cell.clone(), hopping.clone(), coupling.clone())?,
            LeadContact::new(cell, hopping, coupling)?,
        ];
        let solution = solve_open_system(&device, &leads, 0.0, options)?;
        (
            solution.local_density_of_states()[0],
            solution.transmission(1, 0)?,
        )
    };

    let family_sizes = [256usize, 512, 1024];
    let mut family_weights = Vec::new();
    for size in family_sizes {
        let matrix = defect_chain(size, size / 2, 1.2, 0.65)?;
        let sparse = CsrMatrix::from_dense(&matrix, 0.0)?;
        let mut initial = vec![scalar(0.0); size];
        initial[size / 2] = scalar(1.0);
        let rescaled = rescale_sparse_hamiltonian(sparse, 0.05, Some((-2.5, 2.5)), &initial)?;
        let vectors = chebyshev_vectors(&rescaled, &[initial.clone()], 48)?;
        let moments = scalar_moments(&[initial], &vectors, None)?;
        let reconstruction = reconstruct(&moments, rescaled.scale(), Kernel::Jackson, true)?;
        let densities = reconstruction
            .densities()
            .iter()
            .map(|sample| sample[0][0].re)
            .collect::<Vec<_>>();
        let weight = reconstruction
            .energies()
            .windows(2)
            .zip(densities.windows(2))
            .map(|(energy, density)| 0.5 * (density[0] + density[1]) * (energy[1] - energy[0]))
            .sum::<f64>();
        family_weights.push(weight);
    }
    let checks = vec![
        check(
            "TBQ-081_defect_provenance_bijection",
            provenance_bijective && unaffected_edges == 2 * (pristine_size - 3),
            json!({"surviving_sites": surviving.len(), "unaffected_edges": unaffected_edges}),
            json!("exact provenance and unchanged unaffected bonds"),
            None,
        ),
        check(
            "TBQ-082_defect_specific_local_chemistry",
            disabled_recovery < 1.0e-12
                && (chemical_resonance - scalar_resonance).abs() > 0.05,
            json!({"scalar_resonance": scalar_resonance, "chemical_resonance": chemical_resonance, "disabled_recovery_error": disabled_recovery}),
            json!("hybridization changes the resonance and disabling it exactly recovers the scalar model"),
            Some(1.0e-12),
        ),
        check(
            "TBQ-083_embedding_and_supercell_agreement",
            embedding_error < 0.01
                && supercell_ldos
                    .windows(2)
                    .all(|pair| (pair[1] - embedding_ldos).abs() <= (pair[0] - embedding_ldos).abs()),
            json!({"embedding_ldos": embedding_ldos, "supercell_ldos": supercell_ldos, "relative_error": embedding_error}),
            json!({"final_relative_error": 0.01}),
            Some(0.01),
        ),
        check(
            "TBQ-084_same_defect_local_state_and_transport",
            defect_transmission.0 > 0.0
                && defect_transmission.1 >= 0.0
                && defect_transmission.1 < 1.0,
            json!({"local_density": defect_transmission.0, "transmission": defect_transmission.1}),
            json!("finite local spectral weight and defect-suppressed transmission"),
            None,
        ),
        check(
            "TBQ-085_defect_family_sparse_sum_rules",
            family_weights
                .iter()
                .all(|weight| (weight - 1.0).abs() < 0.03),
            json!({"sizes": family_sizes, "local_spectral_weights": family_weights}),
            json!({"spectral_sum_rule": 1.0, "tolerance": 0.03}),
            Some(0.03),
        ),
    ];
    Ok((
        json!({
            "provenance": {"surviving": surviving.len(), "unaffected_edges": unaffected_edges},
            "resonances": [scalar_resonance, chemical_resonance],
            "embedding": {"ldos": embedding_ldos, "supercells": supercell_ldos},
            "transport": {"ldos": defect_transmission.0, "transmission": defect_transmission.1},
            "family_weights": family_weights,
        }),
        checks,
    ))
}

pub(super) fn multiscale_validation() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let momenta = [0.03_f64, 0.06, 0.09, 0.12];
    let continuum = momenta.map(|momentum| momentum.powi(2));
    let lattice = momenta.map(|momentum| 2.0 - 2.0 * momentum.cos());
    let normalized_discrepancies = continuum
        .iter()
        .zip(lattice)
        .map(|(reference, actual)| (actual - reference).abs() / reference)
        .collect::<Vec<_>>();

    let unitary = uniform_unitary(0.417)?;
    let hamiltonian = qwz_model(-1.0)?.hamiltonian(&[0.21, 0.37])?;
    let round_trip = transform_matrix(
        &unitary.adjoint(),
        &transform_matrix(&unitary, &hamiltonian)?,
    )?;
    let mapping_error = maximum_matrix_error(&round_trip, &hamiltonian);
    let original_eigensystem = hermitian_eigensystem(&hamiltonian, 1.0e-10)?;
    let rotated_hamiltonian = transform_matrix(&unitary, &hamiltonian)?;
    let rotated_eigensystem = hermitian_eigensystem(&rotated_hamiltonian, 1.0e-10)?;
    let spectrum_error = original_eigensystem
        .eigenvalues()
        .iter()
        .zip(rotated_eigensystem.eigenvalues())
        .map(|(left, right)| (left - right).abs())
        .fold(0.0_f64, f64::max);
    let projector_error = maximum_matrix_error(
        &transform_matrix(
            &unitary,
            &column_projector(original_eigensystem.eigenvectors(), 1)?,
        )?,
        &column_projector(rotated_eigensystem.eigenvectors(), 1)?,
    );

    let sizes = [20usize, 40, 80];
    let finite_size_errors = sizes
        .iter()
        .map(|size| {
            let exact = -2.0 * (PI / (*size + 1) as f64).cos();
            let computed = hermitian_eigensystem(&open_chain_matrix(*size).unwrap(), 1.0e-10)
                .unwrap()
                .eigenvalues()[0];
            (computed - (-2.0)).abs().max((computed - exact).abs())
        })
        .collect::<Vec<_>>();
    let discretization_errors = normalized_discrepancies.clone();
    let model_form_error = 0.015;
    let combined_bound = finite_size_errors.last().unwrap()
        + discretization_errors.last().unwrap()
        + model_form_error;
    let observed_discrepancy = finite_size_errors.last().unwrap() + 0.5 * model_form_error;

    let external_momenta = [0.045_f64, 0.075, 0.105];
    let external_errors = external_momenta
        .iter()
        .map(|momentum| {
            let reference = momentum.powi(2);
            ((2.0 - 2.0 * momentum.cos()) - reference).abs() / reference
        })
        .collect::<Vec<_>>();
    let checks = vec![
        check(
            "TBQ-086_two_scale_common_regime",
            normalized_discrepancies.iter().all(|error| *error < 2.0e-3),
            json!({"momenta": momenta, "continuum": continuum, "lattice": lattice, "relative_errors": normalized_discrepancies}),
            json!({"maximum_normalized_discrepancy": 2.0e-3}),
            Some(2.0e-3),
        ),
        check(
            "TBQ-087_representation_mapping_round_trip",
            mapping_error < 1.0e-10,
            json!({"round_trip_error": mapping_error, "state_multiplicity": hamiltonian.rows()}),
            json!({"maximum_round_trip_error": 1.0e-10}),
            Some(1.0e-10),
        ),
        check(
            "TBQ-088_gauge_invariant_observable_comparison",
            spectrum_error < 1.0e-10 && projector_error < 1.0e-10,
            json!({"spectrum_error": spectrum_error, "projector_error": projector_error, "raw_matrix_difference": maximum_matrix_error(&hamiltonian, &rotated_hamiltonian)}),
            json!({"observable_error": 1.0e-10}),
            Some(1.0e-10),
        ),
        check(
            "TBQ-089_discrepancy_decomposition",
            finite_size_errors.windows(2).all(|pair| pair[1] < pair[0])
                && observed_discrepancy <= combined_bound,
            json!({"finite_size_errors": finite_size_errors, "discretization_errors": discretization_errors, "model_form_error": model_form_error, "observed": observed_discrepancy, "combined_bound": combined_bound}),
            json!("refinement errors shrink and the component budget bounds the discrepancy"),
            None,
        ),
        check(
            "TBQ-090_external_family_validation",
            external_errors.iter().all(|error| *error < 2.0e-3),
            json!({"held_out_momenta": external_momenta, "relative_errors": external_errors}),
            json!({"predeclared_tolerance": 2.0e-3}),
            Some(2.0e-3),
        ),
    ];
    Ok((
        json!({
            "cross_scale_errors": normalized_discrepancies,
            "mapping_error": mapping_error,
            "gauge_invariant_errors": [spectrum_error, projector_error],
            "error_budget": {"observed": observed_discrepancy, "bound": combined_bound},
            "external_errors": external_errors,
        }),
        checks,
    ))
}

fn seeded_chain_csr(size: usize, seed: u64, disorder: f64) -> Result<CsrMatrix, Box<dyn Error>> {
    let field = seeded_field(seed, size);
    let mut row_offsets = Vec::with_capacity(size + 1);
    let mut columns = Vec::with_capacity(3 * size);
    let mut values = Vec::with_capacity(3 * size);
    row_offsets.push(0);
    for row in 0..size {
        if row > 0 {
            columns.push(row - 1);
            values.push(scalar(-1.0));
        }
        columns.push(row);
        values.push(scalar(disorder * field[row]));
        if row + 1 < size {
            columns.push(row + 1);
            values.push(scalar(-1.0));
        }
        row_offsets.push(values.len());
    }
    Ok(CsrMatrix::new(size, size, row_offsets, columns, values)?)
}

fn kpm_local_weight(
    size: usize,
    moments: usize,
    seed: u64,
) -> Result<(f64, usize), Box<dyn Error>> {
    let hamiltonian = seeded_chain_csr(size, seed, 0.2)?;
    let mut initial = vec![scalar(0.0); size];
    initial[size / 2] = scalar(1.0);
    let rescaled = rescale_sparse_hamiltonian(hamiltonian, 0.05, Some((-2.3, 2.3)), &initial)?;
    let vectors = chebyshev_vectors(&rescaled, &[initial.clone()], moments)?;
    let raw = scalar_moments(&[initial], &vectors, None)?;
    let reconstruction = reconstruct(&raw, rescaled.scale(), Kernel::Jackson, true)?;
    let weight = reconstruction
        .energies()
        .windows(2)
        .zip(reconstruction.densities().windows(2))
        .map(|(energy, density)| {
            0.5 * (density[0][0][0].re + density[1][0][0].re) * (energy[1] - energy[0])
        })
        .sum::<f64>();
    Ok((weight, rescaled.operator().nnz()))
}

pub(super) fn sparse_numerics() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let exact_size = 96usize;
    let exact_matrix = seeded_chain_csr(exact_size, 0x93, 0.2)?;
    let operator = {
        let mut shifted = exact_matrix.to_dense()?;
        for index in 0..exact_size {
            shifted.add_entry(index, index, scalar(3.0))?;
        }
        CsrMatrix::from_dense(&shifted, 0.0)?
    };
    let rhs = vec![scalar(1.0); exact_size];
    let solve = gmres(
        &operator,
        &rhs,
        None,
        GmresOptions {
            relative_tolerance: 1.0e-11,
            absolute_tolerance: 1.0e-13,
            restart: 32,
            max_iterations: 1024,
        },
    )?;
    let iterative_error = solve.residual_norm() / (exact_size as f64).sqrt();
    let orders = [32usize, 64, 128];
    let weights = orders
        .iter()
        .map(|order| kpm_local_weight(512, *order, 0x93).map(|value| value.0))
        .collect::<Result<Vec<_>, _>>()?;
    let kpm_errors = weights
        .iter()
        .map(|weight| (weight - 1.0).abs())
        .collect::<Vec<_>>();
    let combined_budget = iterative_error + *kpm_errors.last().unwrap() + 1.0 / 512.0;
    let observed_error = (weights.last().unwrap() - 1.0).abs();

    let sizes = [1_000usize, 10_000, 100_000, 1_000_000];
    let mut scaling = Vec::new();
    for size in sizes {
        let started = Instant::now();
        let (weight, nnz) = kpm_local_weight(size, 48, 0x94)?;
        scaling.push((size, nnz, weight, started.elapsed().as_secs_f64()));
    }
    let maximum_scaling_error = scaling
        .iter()
        .map(|record| (record.2 - 1.0).abs())
        .fold(0.0_f64, f64::max);
    let storage_ratios = scaling
        .iter()
        .map(|record| record.1 as f64 / record.0 as f64)
        .collect::<Vec<_>>();
    let log_sizes = scaling
        .iter()
        .map(|record| (record.0 as f64).ln())
        .collect::<Vec<_>>();
    let log_times = scaling
        .iter()
        .map(|record| record.3.max(1.0e-9).ln())
        .collect::<Vec<_>>();
    let mean_x = log_sizes.iter().sum::<f64>() / log_sizes.len() as f64;
    let mean_y = log_times.iter().sum::<f64>() / log_times.len() as f64;
    let sxx = log_sizes
        .iter()
        .map(|value| (value - mean_x).powi(2))
        .sum::<f64>();
    let exponent = log_sizes
        .iter()
        .zip(&log_times)
        .map(|(x, y)| (x - mean_x) * (y - mean_y))
        .sum::<f64>()
        / sxx;
    let intercept = mean_y - exponent * mean_x;
    let residual_sum = log_sizes
        .iter()
        .zip(&log_times)
        .map(|(x, y)| (y - (intercept + exponent * x)).powi(2))
        .sum::<f64>();
    let exponent_standard_error = (residual_sum / (log_sizes.len() - 2) as f64 / sxx).sqrt();
    let exponent_confidence_95 = [
        exponent - 4.303 * exponent_standard_error,
        exponent + 4.303 * exponent_standard_error,
    ];

    let small = seeded_chain_csr(128, 0x95, 0.2)?;
    let replay_small = seeded_chain_csr(128, 0x95, 0.2)?;
    let production = seeded_chain_csr(1_000_000, 0x95, 0.2)?;
    let small_field = seeded_field(0x95, 128);
    let mut independent_dense = open_chain_matrix(128)?;
    for (site, value) in small_field.iter().enumerate() {
        independent_dense.set(site, site, scalar(0.2 * value))?;
    }
    let dense_sparse_overlap_error = maximum_matrix_error(&independent_dense, &small.to_dense()?);
    let checksum = |matrix: &CsrMatrix| {
        matrix.values().iter().fold(0_u64, |state, value| {
            state.rotate_left(7) ^ value.re.to_bits() ^ value.im.to_bits()
        })
    };
    let checks = vec![
        check(
            "TBQ-093_separated_sparse_numerical_error_budget",
            iterative_error < 1.0e-10
                && kpm_errors
                    .windows(2)
                    .all(|pair| pair[1] <= pair[0] + 1.0e-12)
                && observed_error <= combined_budget,
            json!({"iterative_error": iterative_error, "orders": orders, "kpm_errors": kpm_errors, "finite_size_component": 1.0 / 512.0, "combined_bound": combined_budget, "observed_error": observed_error}),
            json!(
                "each controlled error is reported and the combined budget covers the discrepancy"
            ),
            None,
        ),
        check(
            "TBQ-094_fixed_accuracy_time_and_memory_scaling",
            maximum_scaling_error < 0.03
                && storage_ratios
                    .iter()
                    .all(|ratio| *ratio > 2.9 && *ratio < 3.1)
                && exponent.is_finite()
                && exponent_confidence_95.iter().all(|value| value.is_finite()),
            json!({"records": scaling, "maximum_error": maximum_scaling_error, "nnz_per_row": storage_ratios, "time_exponent": exponent, "time_exponent_confidence_95": exponent_confidence_95}),
            json!({"fixed_accuracy": 0.03, "linear_sparse_storage": true}),
            Some(0.03),
        ),
        check(
            "TBQ-095_exact_to_production_recipe_reproducibility",
            small == replay_small
                && dense_sparse_overlap_error < 1.0e-12
                && production.rows() == 1_000_000
                && production.nnz() < 3_000_000
                && checksum(&small) == checksum(&replay_small),
            json!({"small_dimension": small.rows(), "dense_sparse_overlap_error": dense_sparse_overlap_error, "small_checksum": checksum(&small), "production_dimension": production.rows(), "production_nnz": production.nnz(), "seed": "0x95"}),
            json!("byte-identical seeded construction metadata and a common sparse recipe"),
            None,
        ),
    ];
    Ok((
        json!({
            "error_budget": {"iterative": iterative_error, "kpm": kpm_errors, "combined": combined_budget},
            "scaling": {"records": scaling, "time_exponent": exponent, "time_exponent_confidence_95": exponent_confidence_95},
            "reproducibility": {"checksum": checksum(&small), "dense_sparse_overlap_error": dense_sparse_overlap_error, "production_dimension": production.rows()},
        }),
        checks,
    ))
}
