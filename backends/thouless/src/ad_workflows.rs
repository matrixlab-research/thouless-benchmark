//! Domain-facing automatic-differentiation benchmarks.
//!
//! These cases exercise complete scientific maps rather than isolated trait
//! calls.  Native Thouless derivatives provide the gradients; central finite
//! differences are used only as independent validation or cost baselines.

use std::error::Error;
use std::f64::consts::TAU;
use std::time::Instant;

use chainrules_core::{JvpRule, Pullback, VjpRule};
use serde_json::{json, Value};
use thouless::ad::{
    real_frobenius_pairing, AdError, AffineHermitianFamily, DifferentiableLead,
    DifferentiableOpenSystem, IsolatedEigenvalue, KpmMomentObjective, LeadDirection,
    ModelDirection, ModelGradient, ModelParameters, OpenSystemDirection, OpenSystemTransmission,
    OpenTransmissionObjective, QuantumMetricMeshObjective, SparseAffineOperator,
    SparseHermitianTerm, SparseLinearFunctionalObjective, SpectralProjectorObjective,
    SurfaceGreenArguments, SurfaceGreenRule, SurfaceGreenTangent,
};
use thouless::linear_operator::{CsrMatrix, GmresOptions};
use thouless::spectrum::hermitian_eigensystem;
use thouless::transport::solve_open_system_from_self_energies;

use super::*;

const FD_STEP: f64 = 1.0e-6;

fn relative_error(actual: f64, expected: f64) -> f64 {
    (actual - expected).abs() / actual.abs().max(expected.abs()).max(1.0e-12)
}

fn vector_norm(values: &[f64]) -> f64 {
    values.iter().map(|value| value * value).sum::<f64>().sqrt()
}

fn dot(left: &[f64], right: &[f64]) -> f64 {
    left.iter()
        .zip(right)
        .map(|(left, right)| left * right)
        .sum()
}

fn add_gradient(target: &mut [f64], source: &ModelGradient, scale: f64) {
    for (target, source) in target.iter_mut().zip(source.as_slice()) {
        *target += scale * source;
    }
}

fn occupied_projector(
    hamiltonian: &ComplexMatrix,
    occupied: usize,
) -> Result<ComplexMatrix, Box<dyn Error>> {
    let eigen = hermitian_eigensystem(hamiltonian, 1.0e-12)?;
    let dimension = hamiltonian.rows();
    let mut projector = ComplexMatrix::zeros(dimension, dimension);
    for state in 0..occupied {
        for row in 0..dimension {
            for column in 0..dimension {
                let left = eigen.eigenvectors().get(row, state)?;
                let right = eigen.eigenvectors().get(column, state)?;
                projector.add_entry(row, column, left * right.conj())?;
            }
        }
    }
    Ok(projector)
}

fn shifted_matrix(
    primal: &ComplexMatrix,
    tangent: &ComplexMatrix,
    scale: f64,
) -> Result<ComplexMatrix, Box<dyn Error>> {
    Ok(ComplexMatrix::new(
        primal.rows(),
        primal.columns(),
        primal
            .as_slice()
            .iter()
            .zip(tangent.as_slice())
            .map(|(primal, tangent)| primal + scale * tangent)
            .collect(),
    )?)
}

fn transform_matrix(
    unitary: &ComplexMatrix,
    matrix: &ComplexMatrix,
) -> Result<ComplexMatrix, Box<dyn Error>> {
    multiply_matrices(&multiply_matrices(unitary, matrix)?, &unitary.adjoint())
}

fn energy_and_gradient(
    family: &AffineHermitianFamily,
    parameters: &ModelParameters,
    index: usize,
    minimum_gap: f64,
) -> Result<(f64, ModelGradient), Box<dyn Error>> {
    let matrix = family.value(parameters)?;
    let rule = IsolatedEigenvalue::new(index, minimum_gap)?;
    let (value, pullback) = rule.vjp(&matrix)?;
    let matrix_gradient = pullback.apply(1.0)?;
    Ok((value, family.parameter_vjp(&matrix_gradient)?))
}

fn minimize_with_backtracking<F>(
    initial: Vec<f64>,
    maximum_iterations: usize,
    initial_step: f64,
    evaluate: F,
) -> Result<(Vec<f64>, Vec<f64>), Box<dyn Error>>
where
    F: Fn(&ModelParameters) -> Result<(f64, Vec<f64>), Box<dyn Error>>,
{
    let mut values = initial;
    let mut history = Vec::new();
    for _ in 0..maximum_iterations {
        let parameters = ModelParameters::new(values.clone())?;
        let (loss, gradient) = evaluate(&parameters)?;
        history.push(loss);
        if vector_norm(&gradient) < 1.0e-10 || loss < 1.0e-16 {
            break;
        }
        let mut step = initial_step;
        let gradient_norm_squared = dot(&gradient, &gradient);
        let mut accepted = None;
        for _ in 0..28 {
            let candidate = values
                .iter()
                .zip(&gradient)
                .map(|(value, gradient)| value - step * gradient)
                .collect::<Vec<_>>();
            let candidate_parameters = ModelParameters::new(candidate.clone())?;
            let (candidate_loss, _) = evaluate(&candidate_parameters)?;
            if candidate_loss <= loss - 1.0e-4 * step * gradient_norm_squared
                || candidate_loss < loss
            {
                accepted = Some(candidate);
                break;
            }
            step *= 0.5;
        }
        let Some(candidate) = accepted else {
            break;
        };
        values = candidate;
    }
    Ok((values, history))
}

fn two_band_family(momentum: f64) -> Result<AffineHermitianFamily, Box<dyn Error>> {
    let base = matrix2(
        scalar(0.18 * (2.0 * momentum).cos()),
        Complex64::new(0.55 * momentum.cos(), -0.45 * momentum.sin()),
        Complex64::new(0.55 * momentum.cos(), 0.45 * momentum.sin()),
        scalar(-0.18 * (2.0 * momentum).cos()),
    )?;
    let mass = pauli_z(scalar(1.0))?;
    let real_hopping = pauli_x(scalar(0.35 + 0.65 * momentum.cos()))?;
    let phase_hopping = pauli_y(scalar(0.4 + 0.6 * momentum.sin()))?;
    Ok(AffineHermitianFamily::new(
        base,
        vec![mass, real_hopping, phase_hopping],
    )?)
}

pub(super) fn spectral_recovery() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let public_momenta = [0.17, 0.63, 1.11, 1.72, 2.31];
    let hidden_momenta = [0.39, 0.91, 1.43, 2.03, 2.67];
    let target_values = vec![0.42, -0.27, 0.19];
    let target = ModelParameters::new(target_values.clone())?;
    let families = public_momenta
        .iter()
        .map(|momentum| two_band_family(*momentum))
        .collect::<Result<Vec<_>, _>>()?;
    let targets = families
        .iter()
        .map(|family| {
            let matrix = family.value(&target)?;
            Ok((
                hermitian_eigensystem(&matrix, 1.0e-12)?.eigenvalues()[0],
                occupied_projector(&matrix, 1)?,
            ))
        })
        .collect::<Result<Vec<_>, Box<dyn Error>>>()?;

    let evaluate = |parameters: &ModelParameters| -> Result<(f64, Vec<f64>), Box<dyn Error>> {
        let mut loss = 0.0;
        let mut gradient = vec![0.0; 3];
        for (family, (target_energy, target_projector)) in families.iter().zip(&targets) {
            let (energy, energy_gradient) = energy_and_gradient(family, parameters, 0, 1.0e-5)?;
            let energy_residual = energy - target_energy;
            loss += 0.5 * energy_residual * energy_residual;
            add_gradient(&mut gradient, &energy_gradient, energy_residual);

            let objective =
                SpectralProjectorObjective::new(family, 1, target_projector.clone(), 1.0e-5)?;
            let (projector_loss, projector_gradient) = objective.value_and_grad(parameters)?;
            loss += 0.4 * projector_loss;
            add_gradient(&mut gradient, &projector_gradient, 0.4);
        }
        let normalization = families.len() as f64;
        for entry in &mut gradient {
            *entry /= normalization;
        }
        Ok((loss / normalization, gradient))
    };

    let initial = vec![-0.18, 0.14, -0.11];
    let initial_parameters = ModelParameters::new(initial.clone())?;
    let direction = ModelDirection::new(vec![0.31, -0.22, 0.17])?;
    let (_, analytic_gradient) = evaluate(&initial_parameters)?;
    let analytic_directional = dot(&analytic_gradient, direction.as_slice());
    let positive = initial_parameters.displaced(&direction, FD_STEP)?;
    let negative = initial_parameters.displaced(&direction, -FD_STEP)?;
    let numerical_directional = (evaluate(&positive)?.0 - evaluate(&negative)?.0) / (2.0 * FD_STEP);
    let gradient_error = relative_error(analytic_directional, numerical_directional);

    let (recovered, loss_history) = minimize_with_backtracking(initial, 180, 1.0, evaluate)?;
    let recovered_parameters = ModelParameters::new(recovered.clone())?;
    let parameter_error = recovered
        .iter()
        .zip(&target_values)
        .map(|(actual, expected)| (actual - expected).abs())
        .fold(0.0_f64, f64::max);
    let mut hidden_energy_error = 0.0_f64;
    let mut hidden_projector_error = 0.0_f64;
    for momentum in hidden_momenta {
        let family = two_band_family(momentum)?;
        let expected = family.value(&target)?;
        let actual = family.value(&recovered_parameters)?;
        let expected_energy = hermitian_eigensystem(&expected, 1.0e-12)?.eigenvalues()[0];
        let actual_energy = hermitian_eigensystem(&actual, 1.0e-12)?.eigenvalues()[0];
        hidden_energy_error = hidden_energy_error.max((actual_energy - expected_energy).abs());
        hidden_projector_error = hidden_projector_error.max(maximum_matrix_error(
            &occupied_projector(&actual, 1)?,
            &occupied_projector(&expected, 1)?,
        ));
    }
    let final_loss = *loss_history.last().unwrap_or(&f64::INFINITY);
    let checks = vec![
        check(
            "AD-G01_spectral_loss_directional_derivative",
            gradient_error < 1.0e-5,
            json!(gradient_error),
            json!({"maximum_relative_error": 1.0e-5}),
            Some(1.0e-5),
        ),
        check(
            "AD-G11_joint_spectral_parameter_recovery",
            parameter_error < 2.0e-5 && final_loss < 1.0e-10,
            json!({"parameters": recovered, "maximum_parameter_error": parameter_error, "loss": final_loss}),
            json!({"target": target_values, "maximum_parameter_error": 2.0e-5}),
            None,
        ),
        check(
            "AD-G11_hidden_momentum_forward_validation",
            hidden_energy_error < 2.0e-5 && hidden_projector_error < 2.0e-5,
            json!({"energy_error": hidden_energy_error, "projector_error": hidden_projector_error}),
            json!({"maximum_error": 2.0e-5}),
            Some(2.0e-5),
        ),
    ];
    Ok((
        json!({
            "target_parameters": target_values,
            "recovered_parameters": recovered_parameters.as_slice(),
            "loss_history": loss_history,
            "directional_relative_error": gradient_error,
            "hidden_energy_error": hidden_energy_error,
            "hidden_projector_error": hidden_projector_error,
        }),
        checks,
    ))
}

fn degenerate_family() -> Result<AffineHermitianFamily, Box<dyn Error>> {
    let base = ComplexMatrix::new(
        4,
        4,
        vec![
            scalar(-1.0),
            scalar(0.0),
            scalar(0.0),
            scalar(0.0),
            scalar(0.0),
            scalar(-1.0),
            scalar(0.0),
            scalar(0.0),
            scalar(0.0),
            scalar(0.0),
            scalar(1.0),
            scalar(0.0),
            scalar(0.0),
            scalar(0.0),
            scalar(0.0),
            scalar(1.0),
        ],
    )?;
    let first = ComplexMatrix::new(
        4,
        4,
        vec![
            scalar(0.0),
            scalar(0.0),
            scalar(1.0),
            scalar(0.0),
            scalar(0.0),
            scalar(0.0),
            scalar(0.0),
            scalar(0.0),
            scalar(1.0),
            scalar(0.0),
            scalar(0.0),
            scalar(0.0),
            scalar(0.0),
            scalar(0.0),
            scalar(0.0),
            scalar(0.0),
        ],
    )?;
    let second = ComplexMatrix::new(
        4,
        4,
        vec![
            scalar(0.0),
            scalar(0.0),
            scalar(0.0),
            scalar(0.0),
            scalar(0.0),
            scalar(0.0),
            scalar(0.0),
            Complex64::new(0.0, -1.0),
            scalar(0.0),
            scalar(0.0),
            scalar(0.0),
            scalar(0.0),
            scalar(0.0),
            Complex64::new(0.0, 1.0),
            scalar(0.0),
            scalar(0.0),
        ],
    )?;
    Ok(AffineHermitianFamily::new(base, vec![first, second])?)
}

pub(super) fn degenerate_projector() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let family = degenerate_family()?;
    let target_parameters = ModelParameters::new(vec![0.21, -0.16])?;
    let target_projector = occupied_projector(&family.value(&target_parameters)?, 2)?;
    let objective = SpectralProjectorObjective::new(&family, 2, target_projector.clone(), 1.0e-4)?;
    let parameters = ModelParameters::new(vec![0.07, 0.04])?;
    let direction = ModelDirection::new(vec![0.37, -0.29])?;
    let (value, analytic) = objective.jvp(&parameters, &direction)?;
    let numerical = (objective.value(&parameters.displaced(&direction, FD_STEP)?)?
        - objective.value(&parameters.displaced(&direction, -FD_STEP)?)?)
        / (2.0 * FD_STEP);
    let directional_error = relative_error(analytic, numerical);

    let rotation = ComplexMatrix::new(
        4,
        4,
        vec![
            scalar(0.8),
            scalar(-0.6),
            scalar(0.0),
            scalar(0.0),
            scalar(0.6),
            scalar(0.8),
            scalar(0.0),
            scalar(0.0),
            scalar(0.0),
            scalar(0.0),
            scalar(1.0),
            scalar(0.0),
            scalar(0.0),
            scalar(0.0),
            scalar(0.0),
            scalar(1.0),
        ],
    )?;
    let rotated_family = AffineHermitianFamily::new(
        transform_matrix(&rotation, family.base())?,
        family
            .directions()
            .iter()
            .map(|matrix| transform_matrix(&rotation, matrix))
            .collect::<Result<Vec<_>, _>>()?,
    )?;
    let rotated_target = transform_matrix(&rotation, &target_projector)?;
    let rotated_objective =
        SpectralProjectorObjective::new(&rotated_family, 2, rotated_target, 1.0e-4)?;
    let (rotated_value, rotated_gradient) = rotated_objective.value_and_grad(&parameters)?;
    let (_, gradient) = objective.value_and_grad(&parameters)?;
    let gauge_value_error = (rotated_value - value).abs();
    let gauge_gradient_error = rotated_gradient
        .as_slice()
        .iter()
        .zip(gradient.as_slice())
        .map(|(left, right)| (left - right).abs())
        .fold(0.0_f64, f64::max);

    let exactly_degenerate = ComplexMatrix::new(
        2,
        2,
        vec![scalar(-1.0), scalar(0.0), scalar(0.0), scalar(-1.0)],
    )?;
    let isolated_direction = pauli_z(scalar(1.0))?;
    let isolated_rejected = matches!(
        IsolatedEigenvalue::new(0, 1.0e-4)?.jvp(&exactly_degenerate, &isolated_direction),
        Err(AdError::GapTooSmall { .. })
    );
    let checks = vec![
        check(
            "AD-G04_degenerate_projector_directional_derivative",
            directional_error < 1.0e-5,
            json!(directional_error),
            json!({"maximum_relative_error": 1.0e-5}),
            Some(1.0e-5),
        ),
        check(
            "AD-G04_occupied_basis_rotation_invariance",
            gauge_value_error < 1.0e-11 && gauge_gradient_error < 1.0e-10,
            json!({"value_error": gauge_value_error, "gradient_error": gauge_gradient_error}),
            json!({"maximum_value_error": 1.0e-11, "maximum_gradient_error": 1.0e-10}),
            None,
        ),
        check(
            "AD-G04_unstable_band_label_rejected",
            isolated_rejected,
            json!(isolated_rejected),
            json!(true),
            None,
        ),
    ];
    Ok((
        json!({
            "objective": value,
            "directional_relative_error": directional_error,
            "basis_rotation_value_error": gauge_value_error,
            "basis_rotation_gradient_error": gauge_gradient_error,
            "isolated_degeneracy_rejected": isolated_rejected,
        }),
        checks,
    ))
}

fn isolated_jacobian_row(
    family: &AffineHermitianFamily,
    parameters: &ModelParameters,
) -> Result<Vec<f64>, Box<dyn Error>> {
    Ok(energy_and_gradient(family, parameters, 0, 1.0e-5)?
        .1
        .as_slice()
        .to_vec())
}

fn fisher_2x2(rows: &[Vec<f64>]) -> [[f64; 2]; 2] {
    let mut fisher = [[0.0; 2]; 2];
    for row in rows {
        for first in 0..2 {
            for second in 0..2 {
                fisher[first][second] += row[first] * row[second];
            }
        }
    }
    fisher
}

fn symmetric_2x2_eigenvalues(matrix: [[f64; 2]; 2]) -> [f64; 2] {
    let trace = matrix[0][0] + matrix[1][1];
    let discriminant = ((matrix[0][0] - matrix[1][1]).powi(2) + 4.0 * matrix[0][1].powi(2)).sqrt();
    [(trace - discriminant) / 2.0, (trace + discriminant) / 2.0]
}

pub(super) fn identifiability() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let parameters = ModelParameters::new(vec![0.24, -0.08])?;
    let shared_families = [0.2_f64, 0.7, 1.3, 2.1]
        .iter()
        .map(|momentum| {
            let base = matrix2(
                scalar(0.3 * momentum.cos()),
                Complex64::new(momentum.cos(), -momentum.sin()),
                Complex64::new(momentum.cos(), momentum.sin()),
                scalar(-0.3 * momentum.cos()),
            )?;
            let common = pauli_z(scalar(1.0))?;
            Ok(AffineHermitianFamily::new(
                base,
                vec![common.clone(), common],
            )?)
        })
        .collect::<Result<Vec<_>, Box<dyn Error>>>()?;
    let shared_rows = shared_families
        .iter()
        .map(|family| isolated_jacobian_row(family, &parameters))
        .collect::<Result<Vec<_>, _>>()?;
    let shared_fisher = fisher_2x2(&shared_rows);
    let shared_eigenvalues = symmetric_2x2_eigenvalues(shared_fisher);
    let null_residual = shared_rows
        .iter()
        .map(|row| (row[0] - row[1]).abs())
        .fold(0.0_f64, f64::max);

    let local_family = AffineHermitianFamily::new(
        matrix2(
            scalar(0.2),
            Complex64::new(0.8, -0.35),
            Complex64::new(0.8, 0.35),
            scalar(-0.2),
        )?,
        vec![pauli_z(scalar(1.0))?, pauli_x(scalar(0.7))?],
    )?;
    let mut augmented_rows = shared_rows.clone();
    augmented_rows.push(isolated_jacobian_row(&local_family, &parameters)?);
    let augmented_fisher = fisher_2x2(&augmented_rows);
    let augmented_eigenvalues = symmetric_2x2_eigenvalues(augmented_fisher);

    let plus = ModelParameters::new(vec![0.34, -0.18])?;
    let minus = ModelParameters::new(vec![0.14, 0.02])?;
    let primary_difference = shared_families
        .iter()
        .map(|family| {
            let plus = energy_and_gradient(family, &plus, 0, 1.0e-5)?.0;
            let minus = energy_and_gradient(family, &minus, 0, 1.0e-5)?.0;
            Ok((plus - minus).abs())
        })
        .collect::<Result<Vec<_>, Box<dyn Error>>>()?
        .into_iter()
        .fold(0.0_f64, f64::max);
    let local_difference = (energy_and_gradient(&local_family, &plus, 0, 1.0e-5)?.0
        - energy_and_gradient(&local_family, &minus, 0, 1.0e-5)?.0)
        .abs();

    let checks = vec![
        check(
            "AD-G14_known_fisher_nullspace",
            null_residual < 1.0e-12
                && shared_eigenvalues[0].abs() < 1.0e-12
                && shared_eigenvalues[1] > 1.0e-3,
            json!({"eigenvalues": shared_eigenvalues, "null_residual": null_residual}),
            json!("one rank-one Fisher null direction"),
            None,
        ),
        check(
            "AD-G14_local_perturbation_lifts_ambiguity",
            augmented_eigenvalues[0] > 1.0e-3,
            json!({"eigenvalues": augmented_eigenvalues}),
            json!({"minimum_eigenvalue": 1.0e-3}),
            Some(1.0e-3),
        ),
        check(
            "AD-G14_predictive_ambiguity_is_not_hidden",
            primary_difference < 1.0e-12 && local_difference > 1.0e-2,
            json!({"primary_difference": primary_difference, "local_difference": local_difference}),
            json!({"primary_maximum": 1.0e-12, "local_minimum": 1.0e-2}),
            None,
        ),
    ];
    Ok((
        json!({
            "primary_jacobian": shared_rows,
            "primary_fisher": shared_fisher,
            "primary_fisher_eigenvalues": shared_eigenvalues,
            "augmented_fisher": augmented_fisher,
            "augmented_fisher_eigenvalues": augmented_eigenvalues,
            "ambiguous_primary_prediction_difference": primary_difference,
            "ambiguity_revealing_local_difference": local_difference,
        }),
        checks,
    ))
}

fn quantum_metric_families(
    point_count: usize,
) -> Result<Vec<AffineHermitianFamily>, Box<dyn Error>> {
    let momentum_step = TAU / point_count as f64;
    (0..point_count)
        .map(|point| {
            let momentum = point as f64 * momentum_step;
            let base = matrix2(
                scalar(0.0),
                Complex64::new(momentum.cos(), -momentum.sin()),
                Complex64::new(momentum.cos(), momentum.sin()),
                scalar(0.0),
            )?;
            Ok(AffineHermitianFamily::new(
                base,
                vec![pauli_z(scalar(1.0))?, pauli_x(scalar(1.0))?],
            )?)
        })
        .collect()
}

pub(super) fn quantum_metric() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let point_count = 32;
    let step = TAU / point_count as f64;
    let families = quantum_metric_families(point_count)?;
    let rotated_families = {
        let unitary = matrix2(
            scalar((0.37_f64).cos()),
            scalar(-(0.37_f64).sin()),
            scalar((0.37_f64).sin()),
            scalar((0.37_f64).cos()),
        )?;
        families
            .iter()
            .map(|family| {
                Ok(AffineHermitianFamily::new(
                    transform_matrix(&unitary, family.base())?,
                    family
                        .directions()
                        .iter()
                        .map(|direction| transform_matrix(&unitary, direction))
                        .collect::<Result<Vec<_>, _>>()?,
                )?)
            })
            .collect::<Result<Vec<_>, Box<dyn Error>>>()?
    };
    let objective = QuantumMetricMeshObjective::new(families, 1, step, 1.0e-5)?;
    let rotated = QuantumMetricMeshObjective::new(rotated_families, 1, step, 1.0e-5)?;
    let parameters = ModelParameters::new(vec![0.31, -0.18])?;
    let direction = ModelDirection::new(vec![0.27, -0.41])?;
    let (value, derivative) = objective.jvp(&parameters, &direction)?;
    let numerical = (objective.value(&parameters.displaced(&direction, FD_STEP)?)?
        - objective.value(&parameters.displaced(&direction, -FD_STEP)?)?)
        / (2.0 * FD_STEP);
    let directional_error = relative_error(derivative, numerical);
    let (rotated_value, rotated_gradient) = rotated.value_and_grad(&parameters)?;
    let (_, gradient) = objective.value_and_grad(&parameters)?;
    let covariance_error = (rotated_value - value).abs().max(
        rotated_gradient
            .as_slice()
            .iter()
            .zip(gradient.as_slice())
            .map(|(left, right)| (left - right).abs())
            .fold(0.0_f64, f64::max),
    );

    let refined_count = 64;
    let refined = QuantumMetricMeshObjective::new(
        quantum_metric_families(refined_count)?,
        1,
        TAU / refined_count as f64,
        1.0e-5,
    )?;
    let (refined_value, refined_derivative) = refined.jvp(&parameters, &direction)?;
    let mesh_value_change = relative_error(value, refined_value);
    let mesh_derivative_change = relative_error(derivative, refined_derivative);
    let checks = vec![
        check(
            "AD-G01_quantum_metric_directional_derivative",
            directional_error < 1.0e-5,
            json!(directional_error),
            json!({"maximum_relative_error": 1.0e-5}),
            Some(1.0e-5),
        ),
        check(
            "AD-G02_quantum_metric_basis_covariance",
            covariance_error < 1.0e-10,
            json!(covariance_error),
            json!({"maximum_error": 1.0e-10}),
            Some(1.0e-10),
        ),
        check(
            "AD-G15_quantum_geometry_mesh_convergence",
            mesh_value_change < 2.0e-2 && mesh_derivative_change < 3.0e-2,
            json!({"value_change": mesh_value_change, "derivative_change": mesh_derivative_change}),
            json!({"maximum_value_change": 2.0e-2, "maximum_derivative_change": 3.0e-2}),
            None,
        ),
    ];
    Ok((
        json!({
            "value": value,
            "directional_derivative": derivative,
            "directional_relative_error": directional_error,
            "basis_covariance_error": covariance_error,
            "refined_value": refined_value,
            "refined_directional_derivative": refined_derivative,
            "mesh_value_change": mesh_value_change,
            "mesh_derivative_change": mesh_derivative_change,
        }),
        checks,
    ))
}

fn qwz_matrix_at(mass: f64, reduced: [f64; 2]) -> Result<ComplexMatrix, Box<dyn Error>> {
    let kx = TAU * reduced[0];
    let ky = TAU * reduced[1];
    let dx = kx.sin();
    let dy = ky.sin();
    let dz = mass + kx.cos() + ky.cos();
    matrix2(
        scalar(dz),
        Complex64::new(dx, -dy),
        Complex64::new(dx, dy),
        scalar(-dz),
    )
}

fn qwz_family(reduced: [f64; 2]) -> Result<AffineHermitianFamily, Box<dyn Error>> {
    Ok(AffineHermitianFamily::new(
        qwz_matrix_at(0.0, reduced)?,
        vec![pauli_z(scalar(1.0))?],
    )?)
}

fn qwz_minimum_gap(mass: f64, samples: usize) -> Result<f64, Box<dyn Error>> {
    let mut minimum = f64::INFINITY;
    for ix in 0..samples {
        for iy in 0..samples {
            let values = hermitian_eigensystem(
                &qwz_matrix_at(
                    mass,
                    [ix as f64 / samples as f64, iy as f64 / samples as f64],
                )?,
                1.0e-12,
            )?
            .eigenvalues()
            .to_vec();
            minimum = minimum.min(values[1] - values[0]);
        }
    }
    Ok(minimum)
}

pub(super) fn topological_design() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let target_mass = 1.0;
    let target_parameters = ModelParameters::new(vec![target_mass])?;
    let mesh = (0..7)
        .flat_map(|ix| (0..7).map(move |iy| [(ix as f64 + 0.31) / 7.0, (iy as f64 + 0.43) / 7.0]))
        .collect::<Vec<_>>();
    let families = mesh
        .iter()
        .map(|point| qwz_family(*point))
        .collect::<Result<Vec<_>, _>>()?;
    let target_projectors = families
        .iter()
        .map(|family| occupied_projector(&family.value(&target_parameters)?, 1))
        .collect::<Result<Vec<_>, _>>()?;
    let evaluate = |parameters: &ModelParameters| -> Result<(f64, Vec<f64>), Box<dyn Error>> {
        let mut value = 0.0;
        let mut gradient = vec![0.0];
        for (family, target_projector) in families.iter().zip(&target_projectors) {
            let objective =
                SpectralProjectorObjective::new(family, 1, target_projector.clone(), 1.0e-4)?;
            let (local_value, local_gradient) = objective.value_and_grad(parameters)?;
            value += local_value;
            gradient[0] += local_gradient.as_slice()[0];
        }
        Ok((value / families.len() as f64, gradient))
    };
    let initial_mass = 2.65;
    let (optimized, history) = minimize_with_backtracking(vec![initial_mass], 120, 0.8, evaluate)?;
    let final_mass = optimized[0];
    let initial_chern = fhs_chern([25, 25], 1, |point| qwz_matrix_at(initial_mass, point))?;
    let final_chern = fhs_chern([25, 25], 1, |point| qwz_matrix_at(final_mass, point))?;
    let scan_masses = (0..81)
        .map(|index| 1.6 + 0.01 * index as f64)
        .collect::<Vec<_>>();
    let scan_gaps = scan_masses
        .iter()
        .map(|mass| qwz_minimum_gap(*mass, 20))
        .collect::<Result<Vec<_>, _>>()?;
    let (minimum_index, minimum_gap) = scan_gaps
        .iter()
        .copied()
        .enumerate()
        .min_by(|left, right| left.1.total_cmp(&right.1))
        .ok_or("empty gap scan")?;
    let closing_mass = scan_masses[minimum_index];
    let checks = vec![
        check(
            "AD-G16_smooth_topological_proxy_optimized",
            (final_mass - target_mass).abs() < 2.0e-3
                && history.last().copied().unwrap_or(f64::INFINITY) < 1.0e-8,
            json!({"final_mass": final_mass, "final_loss": history.last()}),
            json!({"target_mass": target_mass, "maximum_mass_error": 2.0e-3}),
            None,
        ),
        check(
            "AD-G16_discrete_invariant_forward_recomputed",
            initial_chern.abs() < 0.1 && (final_chern.abs() - 1.0).abs() < 0.1,
            json!({"initial_chern": initial_chern, "final_chern": final_chern}),
            json!({"initial": 0, "final_magnitude": 1}),
            Some(0.1),
        ),
        check(
            "AD-G16_invariant_change_has_resolved_gap_closing",
            (closing_mass - 2.0).abs() <= 0.02 && minimum_gap < 1.0e-8,
            json!({"closing_mass": closing_mass, "minimum_gap": minimum_gap}),
            json!({"critical_mass": 2.0, "mass_tolerance": 0.02, "maximum_gap": 1.0e-8}),
            None,
        ),
    ];
    Ok((
        json!({
            "initial_mass": initial_mass,
            "target_mass": target_mass,
            "optimized_mass": final_mass,
            "loss_history": history,
            "initial_chern": initial_chern,
            "final_chern": final_chern,
            "gap_scan_masses": scan_masses,
            "gap_scan": scan_gaps,
            "resolved_closing_mass": closing_mass,
        }),
        checks,
    ))
}

pub(super) fn surface_green_implicit() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let arguments = SurfaceGreenArguments {
        cell_hamiltonian: matrix2(
            scalar(0.15),
            Complex64::new(-0.08, 0.03),
            Complex64::new(-0.08, -0.03),
            scalar(-0.12),
        )?,
        inter_cell_hopping: matrix2(
            Complex64::new(0.31, 0.02),
            Complex64::new(0.04, -0.03),
            Complex64::new(-0.02, 0.01),
            Complex64::new(0.27, -0.01),
        )?,
        energy: 0.07,
        broadening: 0.12,
    };
    let tangent = SurfaceGreenTangent {
        cell_hamiltonian: matrix2(
            scalar(0.2),
            Complex64::new(-0.03, 0.05),
            Complex64::new(-0.03, -0.05),
            scalar(-0.1),
        )?,
        inter_cell_hopping: matrix2(
            Complex64::new(0.06, -0.02),
            Complex64::new(0.03, 0.04),
            Complex64::new(-0.05, 0.01),
            Complex64::new(-0.02, 0.03),
        )?,
        energy: -0.08,
        broadening: 0.04,
    };
    let output_cotangent = matrix2(
        Complex64::new(0.2, -0.1),
        Complex64::new(-0.03, 0.08),
        Complex64::new(0.05, -0.04),
        Complex64::new(-0.15, 0.06),
    )?;
    let rule = SurfaceGreenRule::new(1.0e-14, 512)?;
    let (green, green_tangent) = rule.jvp(&arguments, &tangent)?;
    let (_, pullback) = rule.vjp(&arguments)?;
    let input_cotangent = pullback.apply(output_cotangent.clone())?;
    let output_pairing = real_frobenius_pairing(&green_tangent, &output_cotangent)?;
    let input_pairing =
        real_frobenius_pairing(&tangent.cell_hamiltonian, &input_cotangent.cell_hamiltonian)?
            + real_frobenius_pairing(
                &tangent.inter_cell_hopping,
                &input_cotangent.inter_cell_hopping,
            )?
            + tangent.energy * input_cotangent.energy
            + tangent.broadening * input_cotangent.broadening;
    let duality_error = relative_error(output_pairing, input_pairing);

    let displaced = |scale: f64| -> Result<SurfaceGreenArguments, Box<dyn Error>> {
        Ok(SurfaceGreenArguments {
            cell_hamiltonian: shifted_matrix(
                &arguments.cell_hamiltonian,
                &tangent.cell_hamiltonian,
                scale,
            )?,
            inter_cell_hopping: shifted_matrix(
                &arguments.inter_cell_hopping,
                &tangent.inter_cell_hopping,
                scale,
            )?,
            energy: arguments.energy + scale * tangent.energy,
            broadening: arguments.broadening + scale * tangent.broadening,
        })
    };
    let positive = rule.value(&displaced(FD_STEP)?)?;
    let negative = rule.value(&displaced(-FD_STEP)?)?;
    let numerical = ComplexMatrix::new(
        positive.rows(),
        positive.columns(),
        positive
            .as_slice()
            .iter()
            .zip(negative.as_slice())
            .map(|(positive, negative)| (positive - negative) / (2.0 * FD_STEP))
            .collect(),
    )?;
    let finite_difference_error = numerical
        .as_slice()
        .iter()
        .zip(green_tangent.as_slice())
        .map(|(numerical, analytic)| {
            (numerical - analytic).norm() / numerical.norm().max(analytic.norm()).max(1.0e-12)
        })
        .fold(0.0_f64, f64::max);
    let loose_rule = SurfaceGreenRule::new(1.0e-11, 512)?;
    let (_, loose_tangent) = loose_rule.jvp(&arguments, &tangent)?;
    let tolerance_stability = maximum_matrix_error(&loose_tangent, &green_tangent);
    let maximum_imaginary_diagonal = (0..green.rows())
        .map(|index| green.get(index, index).map(|value| value.im))
        .collect::<Result<Vec<_>, _>>()?
        .into_iter()
        .fold(f64::NEG_INFINITY, f64::max);
    let checks = vec![
        check(
            "AD-G09_surface_green_directional_derivative",
            finite_difference_error < 1.0e-5,
            json!(finite_difference_error),
            json!({"maximum_relative_error": 1.0e-5}),
            Some(1.0e-5),
        ),
        check(
            "AD-G02_surface_green_adjoint_identity",
            duality_error < 1.0e-10,
            json!(duality_error),
            json!({"maximum_relative_error": 1.0e-10}),
            Some(1.0e-10),
        ),
        check(
            "AD-G10_retarded_branch_and_tolerance_stability",
            maximum_imaginary_diagonal < 0.0 && tolerance_stability < 1.0e-8,
            json!({"maximum_imaginary_diagonal": maximum_imaginary_diagonal, "tolerance_stability": tolerance_stability}),
            json!({"retarded_diagonal_imaginary": "negative", "maximum_tolerance_change": 1.0e-8}),
            None,
        ),
    ];
    Ok((
        json!({
            "green_function": green.as_slice().iter().map(|value| [value.re, value.im]).collect::<Vec<_>>(),
            "finite_difference_relative_error": finite_difference_error,
            "adjoint_identity_relative_error": duality_error,
            "tolerance_stability": tolerance_stability,
            "maximum_imaginary_diagonal": maximum_imaginary_diagonal,
            "implicit_rule_retains_iteration_tape": false,
        }),
        checks,
    ))
}

fn transport_family() -> Result<AffineHermitianFamily, Box<dyn Error>> {
    let base = ComplexMatrix::new(
        2,
        2,
        vec![scalar(0.0), scalar(-0.62), scalar(-0.62), scalar(0.0)],
    )?;
    let first = ComplexMatrix::new(
        2,
        2,
        vec![scalar(1.0), scalar(0.0), scalar(0.0), scalar(0.0)],
    )?;
    let hopping = ComplexMatrix::new(
        2,
        2,
        vec![scalar(0.0), scalar(1.0), scalar(1.0), scalar(0.0)],
    )?;
    Ok(AffineHermitianFamily::new(base, vec![first, hopping])?)
}

fn endpoint_self_energies(
    dimension: usize,
    left_gamma: f64,
    right_gamma: f64,
) -> Result<Vec<ComplexMatrix>, Box<dyn Error>> {
    let mut left = ComplexMatrix::zeros(dimension, dimension);
    let mut right = ComplexMatrix::zeros(dimension, dimension);
    left.set(0, 0, Complex64::new(0.0, -0.5 * left_gamma))?;
    right.set(
        dimension - 1,
        dimension - 1,
        Complex64::new(0.0, -0.5 * right_gamma),
    )?;
    Ok(vec![left, right])
}

pub(super) fn inverse_transport() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let family = transport_family()?;
    let self_energies = endpoint_self_energies(2, 0.72, 0.61)?;
    let training_energies = [-0.72, -0.48, -0.21, 0.0, 0.24, 0.51, 0.77];
    let hidden_energies = [-0.61, -0.34, 0.13, 0.39, 0.68];
    let target_values = vec![0.23, -0.19];
    let target = ModelParameters::new(target_values.clone())?;
    let objectives = training_energies
        .iter()
        .map(|energy| OpenTransmissionObjective::new(&family, self_energies.clone(), *energy, 1, 0))
        .collect::<Result<Vec<_>, _>>()?;
    let targets = objectives
        .iter()
        .map(|objective| objective.value(&target))
        .collect::<Result<Vec<_>, _>>()?;
    let evaluate = |parameters: &ModelParameters| -> Result<(f64, Vec<f64>), Box<dyn Error>> {
        let mut loss = 0.0;
        let mut gradient = vec![0.0; 2];
        for (objective, target) in objectives.iter().zip(&targets) {
            let (value, local_gradient) = objective.value_and_grad(parameters)?;
            let residual = value - target;
            loss += 0.5 * residual * residual;
            add_gradient(&mut gradient, &local_gradient, residual);
        }
        let normalization = objectives.len() as f64;
        for entry in &mut gradient {
            *entry /= normalization;
        }
        Ok((loss / normalization, gradient))
    };
    let initial = vec![-0.31, 0.17];
    let initial_parameters = ModelParameters::new(initial.clone())?;
    let direction = ModelDirection::new(vec![0.37, -0.22])?;
    let (_, initial_gradient) = evaluate(&initial_parameters)?;
    let analytic = dot(&initial_gradient, direction.as_slice());
    let numerical = (evaluate(&initial_parameters.displaced(&direction, FD_STEP)?)?.0
        - evaluate(&initial_parameters.displaced(&direction, -FD_STEP)?)?.0)
        / (2.0 * FD_STEP);
    let gradient_error = relative_error(analytic, numerical);

    let (optimized, history) = minimize_with_backtracking(initial, 220, 0.5, evaluate)?;
    let optimized_parameters = ModelParameters::new(optimized.clone())?;
    let optimized_hamiltonian = family.value(&optimized_parameters)?;
    let target_hamiltonian = family.value(&target)?;
    let mut hidden_rms = 0.0;
    let mut hidden_count = 0usize;
    for energy in hidden_energies {
        let actual =
            solve_open_system_from_self_energies(&optimized_hamiltonian, &self_energies, energy)?
                .transmission(1, 0)?;
        let expected =
            solve_open_system_from_self_energies(&target_hamiltonian, &self_energies, energy)?
                .transmission(1, 0)?;
        hidden_rms += (actual - expected).powi(2);
        hidden_count += 1;
    }
    hidden_rms = (hidden_rms / hidden_count as f64).sqrt();
    let final_loss = *history.last().unwrap_or(&f64::INFINITY);
    let checks = vec![
        check(
            "AD-G12_transport_loss_directional_derivative",
            gradient_error < 1.0e-5,
            json!(gradient_error),
            json!({"maximum_relative_error": 1.0e-5}),
            Some(1.0e-5),
        ),
        check(
            "AD-G13_inverse_transmission_trace",
            final_loss < 1.0e-10,
            json!({"final_loss": final_loss, "optimized_parameters": optimized}),
            json!({"maximum_loss": 1.0e-10}),
            Some(1.0e-10),
        ),
        check(
            "AD-G13_independent_forward_transport_validation",
            hidden_rms < 2.0e-5,
            json!(hidden_rms),
            json!({"maximum_hidden_rms": 2.0e-5}),
            Some(2.0e-5),
        ),
    ];
    Ok((
        json!({
            "target_parameters": target_values,
            "optimized_parameters": optimized_parameters.as_slice(),
            "loss_history": history,
            "gradient_relative_error": gradient_error,
            "hidden_forward_rms": hidden_rms,
        }),
        checks,
    ))
}

fn displaced_open_system(
    system: &DifferentiableOpenSystem,
    direction: &OpenSystemDirection,
    scale: f64,
) -> Result<DifferentiableOpenSystem, Box<dyn Error>> {
    Ok(DifferentiableOpenSystem {
        device_hamiltonian: shifted_matrix(
            &system.device_hamiltonian,
            &direction.device_hamiltonian,
            scale,
        )?,
        leads: system
            .leads
            .iter()
            .zip(&direction.leads)
            .map(|(lead, tangent)| {
                Ok(DifferentiableLead {
                    cell_hamiltonian: shifted_matrix(
                        &lead.cell_hamiltonian,
                        &tangent.cell_hamiltonian,
                        scale,
                    )?,
                    inter_cell_hopping: shifted_matrix(
                        &lead.inter_cell_hopping,
                        &tangent.inter_cell_hopping,
                        scale,
                    )?,
                    coupling: shifted_matrix(&lead.coupling, &tangent.coupling, scale)?,
                    broadening: lead.broadening + scale * tangent.broadening,
                })
            })
            .collect::<Result<Vec<_>, Box<dyn Error>>>()?,
        energy: system.energy + scale * direction.energy,
    })
}

pub(super) fn lead_device_sensitivity() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let system = DifferentiableOpenSystem {
        device_hamiltonian: ComplexMatrix::scalar(scalar(0.1)),
        leads: vec![
            DifferentiableLead {
                cell_hamiltonian: ComplexMatrix::scalar(scalar(-0.04)),
                inter_cell_hopping: ComplexMatrix::scalar(Complex64::new(-0.82, 0.03)),
                coupling: ComplexMatrix::scalar(Complex64::new(-0.51, 0.02)),
                broadening: 0.08,
            },
            DifferentiableLead {
                cell_hamiltonian: ComplexMatrix::scalar(scalar(0.06)),
                inter_cell_hopping: ComplexMatrix::scalar(Complex64::new(-0.73, -0.02)),
                coupling: ComplexMatrix::scalar(Complex64::new(-0.43, -0.04)),
                broadening: 0.09,
            },
        ],
        energy: 0.12,
    };
    let direction = OpenSystemDirection {
        device_hamiltonian: ComplexMatrix::scalar(scalar(0.07)),
        leads: vec![
            LeadDirection {
                cell_hamiltonian: ComplexMatrix::scalar(scalar(0.03)),
                inter_cell_hopping: ComplexMatrix::scalar(Complex64::new(0.02, -0.01)),
                coupling: ComplexMatrix::scalar(Complex64::new(-0.015, 0.012)),
                broadening: 0.01,
            },
            LeadDirection {
                cell_hamiltonian: ComplexMatrix::scalar(scalar(-0.025)),
                inter_cell_hopping: ComplexMatrix::scalar(Complex64::new(-0.018, 0.009)),
                coupling: ComplexMatrix::scalar(Complex64::new(0.011, -0.007)),
                broadening: -0.008,
            },
        ],
        energy: -0.04,
    };
    let objective = OpenSystemTransmission::new(1, 0, 1.0e-14, 512)?;
    let (value, analytic) = objective.jvp(&system, &direction)?;
    let numerical = (objective.value(&displaced_open_system(&system, &direction, FD_STEP)?)?
        - objective.value(&displaced_open_system(&system, &direction, -FD_STEP)?)?)
        / (2.0 * FD_STEP);
    let directional_error = relative_error(analytic, numerical);
    let (_, gradient) = objective.value_and_grad(&system)?;
    let device_contribution =
        real_frobenius_pairing(&gradient.device_hamiltonian, &direction.device_hamiltonian)?;
    let lead_cell_contribution = gradient
        .leads
        .iter()
        .zip(&direction.leads)
        .map(|(gradient, direction)| {
            real_frobenius_pairing(&gradient.cell_hamiltonian, &direction.cell_hamiltonian)
        })
        .collect::<Result<Vec<_>, _>>()?
        .into_iter()
        .sum::<f64>();
    let lead_hopping_contribution = gradient
        .leads
        .iter()
        .zip(&direction.leads)
        .map(|(gradient, direction)| {
            real_frobenius_pairing(&gradient.inter_cell_hopping, &direction.inter_cell_hopping)
        })
        .collect::<Result<Vec<_>, _>>()?
        .into_iter()
        .sum::<f64>();
    let interface_contribution = gradient
        .leads
        .iter()
        .zip(&direction.leads)
        .map(|(gradient, direction)| {
            real_frobenius_pairing(&gradient.coupling, &direction.coupling)
        })
        .collect::<Result<Vec<_>, _>>()?
        .into_iter()
        .sum::<f64>();
    let spectral_contribution = gradient.energy * direction.energy
        + gradient
            .leads
            .iter()
            .zip(&direction.leads)
            .map(|(gradient, direction)| gradient.broadening * direction.broadening)
            .sum::<f64>();
    let decomposed = device_contribution
        + lead_cell_contribution
        + lead_hopping_contribution
        + interface_contribution
        + spectral_contribution;
    let decomposition_error = relative_error(decomposed, analytic);
    let checks = vec![
        check(
            "AD-G12_complete_device_lead_directional_derivative",
            directional_error < 1.0e-5,
            json!(directional_error),
            json!({"maximum_relative_error": 1.0e-5}),
            Some(1.0e-5),
        ),
        check(
            "AD-G12_device_lead_interface_energy_contributions",
            decomposition_error < 1.0e-10
                && lead_hopping_contribution.abs() > 1.0e-8
                && interface_contribution.abs() > 1.0e-8,
            json!({
                "decomposition_error": decomposition_error,
                "device": device_contribution,
                "lead_cell": lead_cell_contribution,
                "lead_hopping": lead_hopping_contribution,
                "interface": interface_contribution,
                "energy_and_broadening": spectral_contribution,
            }),
            json!("all physical layers contribute and sum to the JVP"),
            None,
        ),
        check(
            "AD-G09_periodic_lead_implicit_path",
            gradient
                .leads
                .iter()
                .all(|lead| lead.broadening.is_finite())
                && value > 0.0,
            json!({"transmission": value, "broadening_gradients": gradient.leads.iter().map(|lead| lead.broadening).collect::<Vec<_>>()}),
            json!("finite causal lead gradients and positive transmission"),
            None,
        ),
    ];
    Ok((
        json!({
            "transmission": value,
            "native_directional_derivative": analytic,
            "finite_difference_directional_derivative": numerical,
            "directional_relative_error": directional_error,
            "contributions": {
                "device": device_contribution,
                "lead_cells": lead_cell_contribution,
                "periodic_hoppings": lead_hopping_contribution,
                "interfaces": interface_contribution,
                "energy_and_broadening": spectral_contribution,
            },
        }),
        checks,
    ))
}

fn tridiagonal_csr(
    dimension: usize,
    diagonal: impl Fn(usize) -> f64,
    hopping: f64,
) -> Result<CsrMatrix, Box<dyn Error>> {
    let mut row_offsets = Vec::with_capacity(dimension + 1);
    let mut column_indices = Vec::with_capacity(3 * dimension);
    let mut values = Vec::with_capacity(3 * dimension);
    row_offsets.push(0);
    for row in 0..dimension {
        if row > 0 {
            column_indices.push(row - 1);
            values.push(scalar(hopping));
        }
        column_indices.push(row);
        values.push(scalar(diagonal(row)));
        if row + 1 < dimension {
            column_indices.push(row + 1);
            values.push(scalar(hopping));
        }
        row_offsets.push(column_indices.len());
    }
    Ok(CsrMatrix::new(
        dimension,
        dimension,
        row_offsets,
        column_indices,
        values,
    )?)
}

fn sparse_family(
    dimension: usize,
    parameter_count: usize,
    diagonal: impl Fn(usize) -> f64,
    hopping: f64,
    coefficient: f64,
) -> Result<SparseAffineOperator, Box<dyn Error>> {
    let base = tridiagonal_csr(dimension, diagonal, hopping)?;
    let terms = (0..dimension)
        .map(|site| SparseHermitianTerm {
            parameter: site % parameter_count,
            row: site,
            column: site,
            coefficient: scalar(coefficient),
        })
        .collect();
    Ok(SparseAffineOperator::new(base, parameter_count, terms)?)
}

fn deterministic_vector(dimension: usize, phase: f64) -> Vec<Complex64> {
    let mut values = (0..dimension)
        .map(|index| {
            let angle = phase + index as f64 * 0.371;
            Complex64::new(angle.sin(), (1.7 * angle).cos())
        })
        .collect::<Vec<_>>();
    let norm = values
        .iter()
        .map(|value| value.norm_sqr())
        .sum::<f64>()
        .sqrt();
    for value in &mut values {
        *value /= norm;
    }
    values
}

pub(super) fn sparse_adjoint_scaling() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let dimension = 128;
    let parameter_counts = [8_usize, 32, 64];
    let mut records = Vec::new();
    let mut maximum_gradient_error = 0.0_f64;
    let mut maximum_residual = 0.0_f64;
    for parameter_count in parameter_counts {
        let family = sparse_family(dimension, parameter_count, |_| 2.4, -0.22, 0.04)?;
        let right_hand_side = deterministic_vector(dimension, 0.2);
        let output_cotangent = deterministic_vector(dimension, 0.9);
        let objective = SparseLinearFunctionalObjective::new(
            &family,
            right_hand_side,
            output_cotangent,
            GmresOptions {
                relative_tolerance: 1.0e-11,
                absolute_tolerance: 1.0e-13,
                restart: 64,
                max_iterations: 512,
            },
        )?;
        let parameters = ModelParameters::new(
            (0..parameter_count)
                .map(|index| 0.08 * (0.31 * index as f64).sin())
                .collect(),
        )?;
        let direction_values = (0..parameter_count)
            .map(|index| (0.17 + 0.29 * index as f64).cos())
            .collect::<Vec<_>>();
        let direction_norm = vector_norm(&direction_values);
        let direction = ModelDirection::new(
            direction_values
                .into_iter()
                .map(|value| value / direction_norm)
                .collect(),
        )?;
        let started = Instant::now();
        let report = objective.value_and_grad_with_report(&parameters)?;
        let native_microseconds = started.elapsed().as_micros();
        let reverse_directional = dot(report.gradient().as_slice(), direction.as_slice());
        let (_, forward_directional) = objective.jvp(&parameters, &direction)?;
        let numerical = (objective.value(&parameters.displaced(&direction, FD_STEP)?)?
            - objective.value(&parameters.displaced(&direction, -FD_STEP)?)?)
            / (2.0 * FD_STEP);
        let error = relative_error(reverse_directional, numerical)
            .max(relative_error(reverse_directional, forward_directional));
        maximum_gradient_error = maximum_gradient_error.max(error);
        maximum_residual = maximum_residual
            .max(report.primal_residual_norm())
            .max(report.adjoint_residual_norm());
        records.push(json!({
            "parameter_count": parameter_count,
            "native_microseconds": native_microseconds,
            "primal_iterations": report.primal_iterations(),
            "adjoint_iterations": report.adjoint_iterations(),
            "primal_residual": report.primal_residual_norm(),
            "adjoint_residual": report.adjoint_residual_norm(),
            "directional_relative_error": error,
            "native_linear_systems": 2,
            "central_difference_linear_systems": 2 * parameter_count,
        }));
    }
    let solve_counts_constant = records
        .iter()
        .all(|record| record["native_linear_systems"] == json!(2));
    let maximum_iterations = records
        .iter()
        .flat_map(|record| {
            [
                record["primal_iterations"].as_u64().unwrap_or(u64::MAX),
                record["adjoint_iterations"].as_u64().unwrap_or(u64::MAX),
            ]
        })
        .max()
        .unwrap_or(u64::MAX);
    let checks = vec![
        check(
            "AD-G07_sparse_primal_and_adjoint_residuals",
            maximum_residual < 1.0e-9 && maximum_iterations < 128,
            json!({"maximum_residual": maximum_residual, "maximum_iterations": maximum_iterations}),
            json!({"maximum_residual": 1.0e-9, "maximum_iterations": 128}),
            None,
        ),
        check(
            "AD-G07_sparse_adjoint_gradient",
            maximum_gradient_error < 1.0e-5,
            json!(maximum_gradient_error),
            json!({"maximum_relative_error": 1.0e-5}),
            Some(1.0e-5),
        ),
        check(
            "AD-G08_reverse_solve_count_independent_of_parameters",
            solve_counts_constant
                && records.last().unwrap()["central_difference_linear_systems"]
                    .as_u64()
                    .unwrap_or(0)
                    == 128,
            json!(records),
            json!("two native systems versus two systems per finite-difference parameter"),
            None,
        ),
    ];
    Ok((
        json!({
            "dimension": dimension,
            "records": records,
            "maximum_gradient_relative_error": maximum_gradient_error,
            "maximum_true_residual": maximum_residual,
        }),
        checks,
    ))
}

fn kpm_coefficients(moment_count: usize) -> Vec<f64> {
    (0..moment_count)
        .map(|moment| {
            let order = moment as f64;
            120.0 * (-order / 11.0).exp() * (0.43 * order).cos()
        })
        .collect()
}

type KpmEnsembleComponents = (
    Vec<SparseAffineOperator>,
    Vec<Vec<Complex64>>,
    Vec<Vec<f64>>,
);
type KpmEvaluation = (f64, Vec<f64>, usize, usize);

fn robust_kpm_objectives(
    seeds: &[usize],
    dimension: usize,
    parameter_count: usize,
    moment_count: usize,
) -> Result<KpmEnsembleComponents, Box<dyn Error>> {
    let mut operators = Vec::new();
    let mut probes = Vec::new();
    let mut coefficients = Vec::new();
    for seed in seeds {
        let phase = *seed as f64 * 0.173;
        operators.push(sparse_family(
            dimension,
            parameter_count,
            |site| 0.11 * (phase + 0.37 * site as f64).sin(),
            0.18,
            0.035,
        )?);
        probes.push(deterministic_vector(dimension, phase + 0.31));
        coefficients.push(kpm_coefficients(moment_count));
    }
    Ok((operators, probes, coefficients))
}

fn kpm_ensemble_value_and_gradient(
    operators: &[SparseAffineOperator],
    probes: &[Vec<Complex64>],
    coefficients: &[Vec<f64>],
    targets: &[f64],
    parameters: &ModelParameters,
    checkpoint_interval: usize,
) -> Result<KpmEvaluation, Box<dyn Error>> {
    let mut loss = 0.0;
    let mut gradient = vec![0.0; parameters.len()];
    let mut operator_applications = 0usize;
    let mut peak_vectors = 0usize;
    for (((operator, probe), coefficients), target) in
        operators.iter().zip(probes).zip(coefficients).zip(targets)
    {
        let objective = KpmMomentObjective::new(
            operator,
            probe.clone(),
            coefficients.clone(),
            checkpoint_interval,
        )?;
        let report = objective.value_and_grad_with_report(parameters)?;
        let residual = report.value() - target;
        loss += 0.5 * residual * residual;
        add_gradient(&mut gradient, report.gradient(), residual);
        operator_applications += report.forward_operator_applications()
            + report.recomputed_operator_applications()
            + report.adjoint_operator_applications();
        peak_vectors = peak_vectors.max(report.peak_stored_vectors());
    }
    let normalization = operators.len() as f64;
    for entry in &mut gradient {
        *entry /= normalization;
    }
    Ok((
        loss / normalization,
        gradient,
        operator_applications,
        peak_vectors,
    ))
}

fn kpm_targets(
    operators: &[SparseAffineOperator],
    probes: &[Vec<Complex64>],
    coefficients: &[Vec<f64>],
    parameters: &ModelParameters,
    checkpoint_interval: usize,
) -> Result<Vec<f64>, Box<dyn Error>> {
    operators
        .iter()
        .zip(probes)
        .zip(coefficients)
        .map(|((operator, probe), coefficients)| {
            Ok(KpmMomentObjective::new(
                operator,
                probe.clone(),
                coefficients.clone(),
                checkpoint_interval,
            )?
            .value(parameters)?)
        })
        .collect()
}

pub(super) fn robust_kpm_design() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let dimension = 96;
    let parameter_count = 4;
    let moment_count = 36;
    let checkpoint_interval = 6;
    let training_seeds = [11_usize, 23, 37, 53, 71, 89, 107, 131];
    let public_holdout_seeds = [17_usize, 41, 67, 97, 127];
    let target_values = vec![0.18, -0.13, 0.09, -0.16];
    let target = ModelParameters::new(target_values.clone())?;
    let (training_operators, training_probes, training_coefficients) =
        robust_kpm_objectives(&training_seeds, dimension, parameter_count, moment_count)?;
    let training_targets = kpm_targets(
        &training_operators,
        &training_probes,
        &training_coefficients,
        &target,
        checkpoint_interval,
    )?;
    let (holdout_operators, holdout_probes, holdout_coefficients) = robust_kpm_objectives(
        &public_holdout_seeds,
        dimension,
        parameter_count,
        moment_count,
    )?;
    let holdout_targets = kpm_targets(
        &holdout_operators,
        &holdout_probes,
        &holdout_coefficients,
        &target,
        checkpoint_interval,
    )?;
    let evaluate = |parameters: &ModelParameters| -> Result<(f64, Vec<f64>), Box<dyn Error>> {
        let (loss, gradient, _, _) = kpm_ensemble_value_and_gradient(
            &training_operators,
            &training_probes,
            &training_coefficients,
            &training_targets,
            parameters,
            checkpoint_interval,
        )?;
        Ok((loss, gradient))
    };
    let initial = vec![0.0; parameter_count];
    let initial_parameters = ModelParameters::new(initial.clone())?;
    let direction_values = vec![0.41, -0.27, 0.19, 0.33];
    let norm = vector_norm(&direction_values);
    let direction = ModelDirection::new(
        direction_values
            .into_iter()
            .map(|value| value / norm)
            .collect(),
    )?;
    let (initial_loss, initial_gradient, native_applications, peak_vectors) =
        kpm_ensemble_value_and_gradient(
            &training_operators,
            &training_probes,
            &training_coefficients,
            &training_targets,
            &initial_parameters,
            checkpoint_interval,
        )?;
    let analytic = dot(&initial_gradient, direction.as_slice());
    let numerical = (evaluate(&initial_parameters.displaced(&direction, FD_STEP)?)?.0
        - evaluate(&initial_parameters.displaced(&direction, -FD_STEP)?)?.0)
        / (2.0 * FD_STEP);
    let gradient_error = relative_error(analytic, numerical);

    let (optimized, history) = minimize_with_backtracking(initial, 180, 40.0, evaluate)?;
    let optimized_parameters = ModelParameters::new(optimized.clone())?;
    let (training_loss, _, _, _) = kpm_ensemble_value_and_gradient(
        &training_operators,
        &training_probes,
        &training_coefficients,
        &training_targets,
        &optimized_parameters,
        checkpoint_interval,
    )?;
    let (holdout_loss, _, _, _) = kpm_ensemble_value_and_gradient(
        &holdout_operators,
        &holdout_probes,
        &holdout_coefficients,
        &holdout_targets,
        &optimized_parameters,
        checkpoint_interval,
    )?;
    let (initial_holdout_loss, _, _, _) = kpm_ensemble_value_and_gradient(
        &holdout_operators,
        &holdout_probes,
        &holdout_coefficients,
        &holdout_targets,
        &initial_parameters,
        checkpoint_interval,
    )?;
    let finite_difference_applications =
        training_seeds.len() * 2 * parameter_count * (moment_count - 1);
    let parameter_error = optimized
        .iter()
        .zip(&target_values)
        .map(|(actual, expected)| (actual - expected).abs())
        .fold(0.0_f64, f64::max);
    let checks = vec![
        check(
            "AD-G17_stochastic_kpm_directional_derivative",
            gradient_error < 2.0e-5,
            json!(gradient_error),
            json!({"maximum_relative_error": 2.0e-5}),
            Some(2.0e-5),
        ),
        check(
            "AD-G17_training_and_public_holdout_improve",
            training_loss < initial_loss * 0.2
                && holdout_loss < initial_holdout_loss * 0.2,
            json!({
                "initial_training_loss": initial_loss,
                "final_training_loss": training_loss,
                "initial_public_holdout_loss": initial_holdout_loss,
                "final_public_holdout_loss": holdout_loss,
                "parameter_error": parameter_error,
            }),
            json!("training and unseen public-seed losses both decrease by at least 80%"),
            None,
        ),
        check(
            "AD-G08_checkpointed_kpm_cost_reduction",
            native_applications < finite_difference_applications
                && peak_vectors < moment_count,
            json!({
                "native_operator_applications": native_applications,
                "finite_difference_operator_applications": finite_difference_applications,
                "peak_stored_vectors": peak_vectors,
                "full_tape_vectors": moment_count,
            }),
            json!("native reverse uses fewer operator actions and vectors than parameter-wise finite differences"),
            None,
        ),
    ];
    Ok((
        json!({
            "dimension": dimension,
            "parameter_count": parameter_count,
            "moment_count": moment_count,
            "training_seeds": training_seeds,
            "public_holdout_seeds": public_holdout_seeds,
            "target_parameters": target_values,
            "optimized_parameters": optimized_parameters.as_slice(),
            "loss_history": history,
            "initial_training_loss": initial_loss,
            "final_training_loss": training_loss,
            "initial_public_holdout_loss": initial_holdout_loss,
            "final_public_holdout_loss": holdout_loss,
            "gradient_relative_error": gradient_error,
            "native_operator_applications": native_applications,
            "finite_difference_operator_applications": finite_difference_applications,
            "peak_stored_vectors": peak_vectors,
            "isolated_held_out_validation_claimed": false,
        }),
        checks,
    ))
}
