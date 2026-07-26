use std::env;
use std::error::Error;
use std::time::Instant;

use serde_json::{json, Value};
use thouless::decomposition::schur;
use thouless::model::{Lattice, ModelBuilder, TightBindingModel};
use thouless::spectrum::hermitian_eigensystem;
use thouless::topology::{
    chern_numbers_on_uniform_grid, plaquette_flux, reduced_polarization_on_loop, wilson_line_phase,
    wilson_loop_eigenphases, wilson_loop_unitary,
};
use thouless::transport::{solve_open_system, LeadContact, SurfaceGreenOptions};
use thouless::wannier::interpolate_periodic_matrices;
use thouless::{Complex64, ComplexMatrix};

const BACKEND_VERSION: &str = "0d87773278183ddc7c254438dccbda1face04fb2";

struct Check {
    name: &'static str,
    passed: bool,
    actual: Value,
    expected: Value,
    tolerance: Option<f64>,
}

fn check(
    name: &'static str,
    passed: bool,
    actual: Value,
    expected: Value,
    tolerance: Option<f64>,
) -> Check {
    Check {
        name,
        passed,
        actual,
        expected,
        tolerance,
    }
}

fn encoded_check(item: &Check) -> Value {
    json!({
        "name": item.name,
        "passed": item.passed,
        "actual": item.actual,
        "expected": item.expected,
        "tolerance": item.tolerance,
    })
}

fn scalar(value: f64) -> Complex64 {
    Complex64::new(value, 0.0)
}

fn matrix2(
    first: Complex64,
    second: Complex64,
    third: Complex64,
    fourth: Complex64,
) -> Result<ComplexMatrix, Box<dyn Error>> {
    Ok(ComplexMatrix::new(
        2,
        2,
        vec![first, second, third, fourth],
    )?)
}

fn pauli_x(scale: Complex64) -> Result<ComplexMatrix, Box<dyn Error>> {
    matrix2(
        Complex64::new(0.0, 0.0),
        scale,
        scale,
        Complex64::new(0.0, 0.0),
    )
}

fn pauli_y(scale: Complex64) -> Result<ComplexMatrix, Box<dyn Error>> {
    matrix2(
        Complex64::new(0.0, 0.0),
        -Complex64::i() * scale,
        Complex64::i() * scale,
        Complex64::new(0.0, 0.0),
    )
}

fn pauli_z(scale: Complex64) -> Result<ComplexMatrix, Box<dyn Error>> {
    matrix2(
        scale,
        Complex64::new(0.0, 0.0),
        Complex64::new(0.0, 0.0),
        -scale,
    )
}

fn add_matrices(
    left: &ComplexMatrix,
    right: &ComplexMatrix,
) -> Result<ComplexMatrix, Box<dyn Error>> {
    Ok(ComplexMatrix::new(
        left.rows(),
        left.columns(),
        left.as_slice()
            .iter()
            .zip(right.as_slice())
            .map(|(left, right)| left + right)
            .collect(),
    )?)
}

fn scale_matrix(matrix: &ComplexMatrix, scale: Complex64) -> Result<ComplexMatrix, Box<dyn Error>> {
    Ok(ComplexMatrix::new(
        matrix.rows(),
        matrix.columns(),
        matrix
            .as_slice()
            .iter()
            .map(|value| scale * value)
            .collect(),
    )?)
}

fn subtract_matrices(
    left: &ComplexMatrix,
    right: &ComplexMatrix,
) -> Result<ComplexMatrix, Box<dyn Error>> {
    add_matrices(left, &scale_matrix(right, scalar(-1.0))?)
}

fn kronecker(left: &ComplexMatrix, right: &ComplexMatrix) -> Result<ComplexMatrix, Box<dyn Error>> {
    let rows = left.rows() * right.rows();
    let columns = left.columns() * right.columns();
    let mut result = ComplexMatrix::zeros(rows, columns);
    for left_row in 0..left.rows() {
        for left_column in 0..left.columns() {
            for right_row in 0..right.rows() {
                for right_column in 0..right.columns() {
                    result.set(
                        left_row * right.rows() + right_row,
                        left_column * right.columns() + right_column,
                        left.get(left_row, left_column)? * right.get(right_row, right_column)?,
                    )?;
                }
            }
        }
    }
    Ok(result)
}

fn selected_submatrix(
    matrix: &ComplexMatrix,
    indices: &[usize],
) -> Result<ComplexMatrix, Box<dyn Error>> {
    let mut result = ComplexMatrix::zeros(indices.len(), indices.len());
    for (row, source_row) in indices.iter().enumerate() {
        for (column, source_column) in indices.iter().enumerate() {
            result.set(row, column, matrix.get(*source_row, *source_column)?)?;
        }
    }
    Ok(result)
}

fn minimum_direct_gap(
    model: &TightBindingModel,
    samples: usize,
    occupied: usize,
) -> Result<f64, Box<dyn Error>> {
    let mut minimum = f64::INFINITY;
    for ix in 0..samples {
        for iy in 0..samples {
            let values = model
                .eigensystem(&[ix as f64 / samples as f64, iy as f64 / samples as f64])?
                .eigenvalues()
                .to_vec();
            minimum = minimum.min(values[occupied] - values[occupied - 1]);
        }
    }
    Ok(minimum)
}

fn wilson_centers(
    model: &TightBindingModel,
    fixed_ky: f64,
    samples: usize,
    occupied: usize,
) -> Result<Vec<f64>, Box<dyn Error>> {
    let mut frames = (0..samples)
        .map(|ix| {
            occupied_frame(
                &model.hamiltonian(&[ix as f64 / samples as f64, fixed_ky])?,
                occupied,
            )
        })
        .collect::<Result<Vec<_>, _>>()?;
    frames.push(frames[0].clone());
    let mut centers = wilson_loop_eigenphases(&frames)?
        .iter()
        .map(|phase| (-phase / std::f64::consts::TAU).rem_euclid(1.0))
        .collect::<Vec<_>>();
    centers.sort_by(f64::total_cmp);
    Ok(centers)
}

fn fourier_model(
    dimension: usize,
    onsite: ComplexMatrix,
    hoppings: Vec<(Vec<i32>, ComplexMatrix)>,
) -> Result<TightBindingModel, Box<dyn Error>> {
    let mut primitive = vec![vec![0.0; dimension]; dimension];
    for (axis, vector) in primitive.iter_mut().enumerate() {
        vector[axis] = 1.0;
    }
    let lattice = Lattice::new(primitive, (0..dimension).collect())?;
    let mut builder = ModelBuilder::new(lattice);
    let orbital = builder.add_orbital_with_dof("spinor", vec![0.0; dimension], onsite.rows())?;
    builder.set_onsite_block(orbital, onsite)?;
    for (offset, matrix) in hoppings {
        builder.add_hopping_block(orbital, orbital, offset, matrix)?;
    }
    Ok(builder.build()?)
}

fn occupied_frame(
    hamiltonian: &ComplexMatrix,
    occupied: usize,
) -> Result<ComplexMatrix, Box<dyn Error>> {
    let eigensystem = hermitian_eigensystem(hamiltonian, 1.0e-10)?;
    let basis = hamiltonian.rows();
    let mut values = Vec::with_capacity(occupied * basis);
    for state in 0..occupied {
        for orbital in 0..basis {
            values.push(eigensystem.eigenvectors().get(orbital, state)?);
        }
    }
    Ok(ComplexMatrix::new(occupied, basis, values)?)
}

fn fhs_chern(
    samples: [usize; 2],
    occupied: usize,
    hamiltonian: impl Fn([f64; 2]) -> Result<ComplexMatrix, Box<dyn Error>>,
) -> Result<f64, Box<dyn Error>> {
    let [nx, ny] = samples;
    let mut frames = Vec::with_capacity(nx * ny);
    for ix in 0..nx {
        for iy in 0..ny {
            frames.push(occupied_frame(
                &hamiltonian([ix as f64 / nx as f64, iy as f64 / ny as f64])?,
                occupied,
            )?);
        }
    }
    let frame = |ix: usize, iy: usize| &frames[(ix % nx) * ny + iy % ny];
    let mut flux = 0.0;
    for ix in 0..nx {
        for iy in 0..ny {
            flux += plaquette_flux(&[
                frame(ix, iy).clone(),
                frame(ix + 1, iy).clone(),
                frame(ix + 1, iy + 1).clone(),
                frame(ix, iy + 1).clone(),
            ])?;
        }
    }
    Ok(flux / std::f64::consts::TAU)
}

fn graphene_model(t: f64) -> Result<TightBindingModel, Box<dyn Error>> {
    let lattice = Lattice::new(vec![vec![1.0, 0.0], vec![0.0, 1.0]], vec![0, 1])?;
    let mut builder = ModelBuilder::new(lattice);
    let a = builder.add_orbital("a", [0.0, 0.0])?;
    let b = builder.add_orbital("b", [0.0, 0.0])?;
    for offset in [[0, 0], [-1, 0], [0, -1]] {
        builder.add_hopping(a, b, offset, scalar(t))?;
    }
    Ok(builder.build()?)
}

fn ssh_model(intracell: f64, intercell: f64) -> Result<TightBindingModel, Box<dyn Error>> {
    let lattice = Lattice::new(vec![vec![1.0]], vec![0])?;
    let mut builder = ModelBuilder::new(lattice);
    let a = builder.add_orbital("a", [0.0])?;
    let b = builder.add_orbital("b", [0.0])?;
    builder.add_hopping(a, b, [0], scalar(intracell))?;
    builder.add_hopping(b, a, [1], scalar(intercell))?;
    Ok(builder.build()?)
}

fn bulk_graphene_dirac_cone() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let model = graphene_model(1.0)?;
    let gamma = model.eigensystem(&[0.0, 0.0])?.eigenvalues().to_vec();
    let k = [1.0 / 3.0, 2.0 / 3.0];
    let dirac = model.eigensystem(&k)?.eigenvalues().to_vec();
    let gap = dirac[1] - dirac[0];
    let delta = 1.0e-5;
    let shifted = model
        .eigensystem(&[k[0] + delta, k[1]])?
        .eigenvalues()
        .to_vec();
    let velocity = shifted[1] / delta;
    let checks = vec![
        check(
            "gamma_spectrum",
            (gamma[0] + 3.0).abs() < 1.0e-10 && (gamma[1] - 3.0).abs() < 1.0e-10,
            json!(gamma),
            json!([-3.0, 3.0]),
            Some(1.0e-10),
        ),
        check(
            "dirac_gap",
            gap.abs() < 1.0e-9,
            json!(gap),
            json!(0.0),
            Some(1.0e-9),
        ),
        check(
            "linear_dispersion",
            velocity.abs() > 1.0,
            json!(velocity),
            json!("nonzero"),
            None,
        ),
    ];
    Ok((
        json!({
            "gamma_eigenvalues": gamma,
            "dirac_gap": gap,
            "reduced_coordinate_velocity": velocity,
        }),
        checks,
    ))
}

fn bulk_ssh_polarization() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let intracell = 0.6;
    let intercell = 1.0;
    let model = ssh_model(intracell, intercell)?;
    let polarization = reduced_polarization_on_loop(&model, 400, 0, &[0.0], &[0])?;
    let mut minimum_gap = f64::INFINITY;
    for index in 0..400 {
        let values = model
            .eigensystem(&[index as f64 / 400.0])?
            .eigenvalues()
            .to_vec();
        minimum_gap = minimum_gap.min(values[1] - values[0]);
    }
    let expected_gap = 2.0 * (intercell - intracell);
    let checks = vec![
        check(
            "polarization_modulo_one",
            (polarization - 0.5).abs() < 1.0e-8,
            json!(polarization),
            json!(0.5),
            Some(1.0e-8),
        ),
        check(
            "bulk_gap",
            (minimum_gap - expected_gap).abs() < 2.0e-4,
            json!(minimum_gap),
            json!(expected_gap),
            Some(2.0e-4),
        ),
    ];
    Ok((
        json!({"reduced_polarization": polarization, "minimum_gap": minimum_gap}),
        checks,
    ))
}

fn rice_mele_hamiltonian(
    reduced_momentum: f64,
    reduced_parameter: f64,
) -> Result<ComplexMatrix, Box<dyn Error>> {
    let mean = 1.0;
    let dimerization = 0.5;
    let staggering = 0.8;
    let theta = std::f64::consts::TAU * reduced_parameter;
    let intracell = mean + dimerization * theta.cos();
    let intercell = mean - dimerization * theta.cos();
    let phase = Complex64::from_polar(1.0, std::f64::consts::TAU * reduced_momentum);
    let off_diagonal = scalar(intracell) + scalar(intercell) * phase;
    let mass = staggering * theta.sin();
    matrix2(
        scalar(mass),
        off_diagonal,
        off_diagonal.conj(),
        scalar(-mass),
    )
}

fn bulk_rice_mele_pump() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let chern = fhs_chern([31, 31], 1, |point| {
        rice_mele_hamiltonian(point[0], point[1])
    })?;
    let pumped_charge = chern.round() as i64;
    let mut minimum_gap = f64::INFINITY;
    for momentum in 0..81 {
        for parameter in 0..81 {
            let values = hermitian_eigensystem(
                &rice_mele_hamiltonian(momentum as f64 / 81.0, parameter as f64 / 81.0)?,
                1.0e-10,
            )?
            .eigenvalues()
            .to_vec();
            minimum_gap = minimum_gap.min(values[1] - values[0]);
        }
    }
    let checks = vec![
        check(
            "quantized_pump",
            pumped_charge.abs() == 1,
            json!(pumped_charge),
            json!("magnitude 1"),
            None,
        ),
        check(
            "chern_integer",
            (chern - pumped_charge as f64).abs() < 1.0e-6,
            json!(chern),
            json!(pumped_charge),
            Some(1.0e-6),
        ),
        check(
            "cycle_stays_gapped",
            minimum_gap > 0.5,
            json!(minimum_gap),
            json!("> 0.5"),
            None,
        ),
    ];
    Ok((
        json!({
            "chern_number": chern,
            "pumped_charge": pumped_charge,
            "minimum_cycle_gap": minimum_gap,
        }),
        checks,
    ))
}

fn qwz_model(mass: f64) -> Result<TightBindingModel, Box<dyn Error>> {
    let onsite = pauli_z(scalar(mass))?;
    let hopping_x = add_matrices(&pauli_z(scalar(0.5))?, &pauli_x(Complex64::new(0.0, -0.5))?)?;
    let hopping_y = add_matrices(&pauli_z(scalar(0.5))?, &pauli_y(Complex64::new(0.0, -0.5))?)?;
    fourier_model(
        2,
        onsite,
        vec![(vec![1, 0], hopping_x), (vec![0, 1], hopping_y)],
    )
}

fn bulk_qwz_phase_diagram() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let masses = [-3.0, -1.0, 1.0, 3.0];
    let mut chern_numbers = Vec::new();
    let mut minimum_gaps = Vec::new();
    for mass in masses {
        let model = qwz_model(mass)?;
        chern_numbers
            .push(chern_numbers_on_uniform_grid(&model, &[31, 31], [0, 1], &[0])?.values()[0]);
        let mut minimum_gap = f64::INFINITY;
        for ix in 0..40 {
            for iy in 0..40 {
                let values = model
                    .eigensystem(&[ix as f64 / 40.0, iy as f64 / 40.0])?
                    .eigenvalues()
                    .to_vec();
                minimum_gap = minimum_gap.min(values[1] - values[0]);
            }
        }
        minimum_gaps.push(minimum_gap);
    }
    let rounded = chern_numbers
        .iter()
        .map(|value| value.round() as i64)
        .collect::<Vec<_>>();
    let checks = vec![
        check(
            "phase_sequence",
            rounded.iter().map(|value| value.abs()).collect::<Vec<_>>() == vec![0, 1, 1, 0],
            json!(rounded),
            json!("trivial-Chern-Chern-trivial"),
            None,
        ),
        check(
            "opposite_topological_signs",
            rounded[1] == -rounded[2],
            json!([rounded[1], rounded[2]]),
            json!("opposite"),
            None,
        ),
        check(
            "sampled_points_gapped",
            minimum_gaps.iter().all(|value| *value > 1.9),
            json!(minimum_gaps),
            json!("> 1.9"),
            None,
        ),
    ];
    Ok((
        json!({
            "chern_numbers": chern_numbers,
            "rounded_chern_numbers": rounded,
            "minimum_gaps": minimum_gaps,
        }),
        checks,
    ))
}

fn haldane_model() -> Result<TightBindingModel, Box<dyn Error>> {
    let t1 = 1.0;
    let t2 = 0.15;
    let mass = 0.2;
    let onsite = add_matrices(&pauli_z(scalar(mass))?, &pauli_x(scalar(t1))?)?;
    let mut hoppings = Vec::new();
    for (offset, chirality) in [(vec![1, 0], -1.0), (vec![0, 1], 1.0), (vec![1, -1], 1.0)] {
        let mut matrix = ComplexMatrix::zeros(2, 2);
        matrix.set(0, 0, Complex64::new(0.0, -chirality * t2))?;
        matrix.set(1, 1, Complex64::new(0.0, chirality * t2))?;
        if offset == [1, 0] || offset == [0, 1] {
            matrix.set(0, 1, scalar(t1))?;
        }
        hoppings.push((offset, matrix));
    }
    fourier_model(2, onsite, hoppings)
}

fn bulk_haldane_chern_transition() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let model = haldane_model()?;
    let chern = fhs_chern([41, 41], 1, |point| {
        model.hamiltonian(&point).map_err(Into::into)
    })?;
    let mut dirac_masses = Vec::new();
    for point in [[1.0 / 3.0, 2.0 / 3.0], [2.0 / 3.0, 1.0 / 3.0]] {
        let hamiltonian = model.hamiltonian(&point)?;
        dirac_masses.push((hamiltonian.get(0, 0)?.re - hamiltonian.get(1, 1)?.re) / 2.0);
    }
    let minimum_gap = minimum_direct_gap(&model, 60, 1)?;
    let predicted_chern = ((dirac_masses[0].signum() - dirac_masses[1].signum()) / 2.0) as i64;
    let rounded = chern.round() as i64;
    let checks = vec![
        check(
            "opposite_dirac_masses",
            dirac_masses[0] * dirac_masses[1] < 0.0,
            json!(dirac_masses),
            json!("opposite signs"),
            None,
        ),
        check(
            "chern_from_masses",
            rounded == -predicted_chern,
            json!(rounded),
            json!(-predicted_chern),
            None,
        ),
        check(
            "chern_integer",
            (chern - rounded as f64).abs() < 2.0e-6,
            json!(chern),
            json!(rounded),
            Some(2.0e-6),
        ),
        check(
            "positive_bulk_gap",
            minimum_gap > 1.0,
            json!(minimum_gap),
            json!("> 1.0"),
            None,
        ),
    ];
    Ok((
        json!({
            "dirac_masses": dirac_masses,
            "minimum_gap": minimum_gap,
            "chern_number": chern,
            "predicted_chern_from_masses": predicted_chern,
        }),
        checks,
    ))
}

fn kagome_soc_model() -> Result<TightBindingModel, Box<dyn Error>> {
    let hopping = Complex64::new(1.0, 0.1);
    let mut onsite = ComplexMatrix::zeros(3, 3);
    for (first, second) in [(0, 1), (0, 2), (1, 2)] {
        onsite.set(first, second, hopping)?;
        onsite.set(second, first, hopping.conj())?;
    }
    let mut hoppings = Vec::new();
    for (offset, first, second) in [(vec![1, 0], 0, 1), (vec![0, 1], 0, 2), (vec![1, -1], 1, 2)] {
        let mut matrix = ComplexMatrix::zeros(3, 3);
        matrix.set(first, second, hopping)?;
        hoppings.push((offset, matrix));
    }
    fourier_model(2, onsite, hoppings)
}

fn bulk_kagome_soc_chern() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let model = kagome_soc_model()?;
    let cumulative_one = fhs_chern([41, 41], 1, |point| {
        model.hamiltonian(&point).map_err(Into::into)
    })?;
    let cumulative_two = fhs_chern([41, 41], 2, |point| {
        model.hamiltonian(&point).map_err(Into::into)
    })?;
    let band_chern = [
        cumulative_one,
        cumulative_two - cumulative_one,
        -cumulative_two,
    ];
    let rounded = band_chern
        .iter()
        .map(|value| value.round() as i64)
        .collect::<Vec<_>>();
    let mut minimum_gaps = [f64::INFINITY; 2];
    let mut minima = [f64::INFINITY; 3];
    let mut maxima = [f64::NEG_INFINITY; 3];
    for ix in 0..50 {
        for iy in 0..50 {
            let values = model
                .eigensystem(&[ix as f64 / 50.0, iy as f64 / 50.0])?
                .eigenvalues()
                .to_vec();
            for band in 0..3 {
                minima[band] = minima[band].min(values[band]);
                maxima[band] = maxima[band].max(values[band]);
            }
            minimum_gaps[0] = minimum_gaps[0].min(values[1] - values[0]);
            minimum_gaps[1] = minimum_gaps[1].min(values[2] - values[1]);
        }
    }
    let bandwidths = (0..3)
        .map(|band| maxima[band] - minima[band])
        .collect::<Vec<_>>();
    let checks = vec![
        check(
            "nonzero_band_chern",
            rounded.iter().any(|value| value.abs() == 1),
            json!(rounded),
            json!("at least one nonzero band"),
            None,
        ),
        check(
            "chern_sum_rule",
            rounded.iter().sum::<i64>() == 0,
            json!(rounded.iter().sum::<i64>()),
            json!(0),
            None,
        ),
        check(
            "positive_gaps",
            minimum_gaps.iter().all(|value| *value > 0.05),
            json!(minimum_gaps),
            json!("> 0.05"),
            None,
        ),
        check(
            "finite_bandwidths",
            bandwidths.iter().all(|value| *value > 0.1),
            json!(bandwidths),
            json!("> 0.1"),
            None,
        ),
    ];
    Ok((
        json!({
            "band_chern_numbers": band_chern,
            "rounded_band_chern_numbers": rounded,
            "minimum_gaps": minimum_gaps,
            "bandwidths": bandwidths,
        }),
        checks,
    ))
}

fn kane_mele_model(rashba: f64) -> Result<TightBindingModel, Box<dyn Error>> {
    let identity = ComplexMatrix::identity(2);
    let tau_x = pauli_x(scalar(1.0))?;
    let tau_y = pauli_y(scalar(1.0))?;
    let tau_z = pauli_z(scalar(1.0))?;
    let spin_x = pauli_x(scalar(1.0))?;
    let spin_z = pauli_z(scalar(1.0))?;
    let onsite = add_matrices(
        &kronecker(&tau_x, &identity)?,
        &scale_matrix(&kronecker(&tau_y, &spin_x)?, scalar(rashba))?,
    )?;
    let mut hoppings = Vec::new();
    for (offset, chirality) in [(vec![1, 0], -1.0), (vec![0, 1], 1.0), (vec![1, -1], 1.0)] {
        let mut matrix = scale_matrix(
            &kronecker(&tau_z, &spin_z)?,
            Complex64::new(0.0, -chirality * 0.06),
        )?;
        if offset == [1, 0] || offset == [0, 1] {
            matrix.set(0, 2, scalar(1.0))?;
            matrix.set(1, 3, scalar(1.0))?;
        }
        hoppings.push((offset, matrix));
    }
    fourier_model(2, onsite, hoppings)
}

fn bulk_kane_mele_z2() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let spin_conserved = kane_mele_model(0.0)?;
    let spin_up = fhs_chern([31, 31], 1, |point| {
        selected_submatrix(&spin_conserved.hamiltonian(&point)?, &[0, 2])
    })?;
    let spin_down = fhs_chern([31, 31], 1, |point| {
        selected_submatrix(&spin_conserved.hamiltonian(&point)?, &[1, 3])
    })?;
    let spin_chern = ((spin_up - spin_down) / 2.0).round() as i64;
    let z2 = spin_chern.unsigned_abs() % 2;
    let model = kane_mele_model(0.02)?;
    let minimum_gap = minimum_direct_gap(&model, 40, 2)?;
    let centers = (0..=20)
        .map(|index| wilson_centers(&model, index as f64 / 40.0, 81, 2))
        .collect::<Result<Vec<_>, _>>()?;
    let endpoint_separation = (centers[20][1] - centers[20][0]).abs();
    let maximum_wannier_separation = centers
        .iter()
        .map(|values| values[1] - values[0])
        .fold(0.0_f64, f64::max);
    let checks = vec![
        check(
            "time_reversal_spin_chern_pair",
            spin_up.round() as i64 == -(spin_down.round() as i64),
            json!([spin_up, spin_down]),
            json!("opposite"),
            None,
        ),
        check("nontrivial_z2", z2 == 1, json!(z2), json!(1), None),
        check(
            "rashba_gap_stays_open",
            minimum_gap > 0.5,
            json!(minimum_gap),
            json!("> 0.5"),
            None,
        ),
        check(
            "wilson_partner_switching",
            endpoint_separation < 1.0e-6 && maximum_wannier_separation > 0.4,
            json!([endpoint_separation, maximum_wannier_separation]),
            json!("degenerate endpoint with separated flow"),
            None,
        ),
    ];
    Ok((
        json!({
            "spin_chern_numbers_at_zero_rashba": [spin_up, spin_down],
            "z2": z2,
            "minimum_rashba_gap": minimum_gap,
            "wilson_centers": centers,
            "endpoint_separation": endpoint_separation,
            "maximum_wannier_separation": maximum_wannier_separation,
        }),
        checks,
    ))
}

fn bbh_model() -> Result<TightBindingModel, Box<dyn Error>> {
    let identity = ComplexMatrix::identity(2);
    let tau_x = pauli_x(scalar(1.0))?;
    let tau_y = pauli_y(scalar(1.0))?;
    let sigma_x = pauli_x(scalar(1.0))?;
    let sigma_y = pauli_y(scalar(1.0))?;
    let sigma_z = pauli_z(scalar(1.0))?;
    let gamma_1 = scale_matrix(&kronecker(&tau_y, &sigma_x)?, scalar(-1.0))?;
    let gamma_2 = scale_matrix(&kronecker(&tau_y, &sigma_y)?, scalar(-1.0))?;
    let gamma_3 = scale_matrix(&kronecker(&tau_y, &sigma_z)?, scalar(-1.0))?;
    let gamma_4 = kronecker(&tau_x, &identity)?;
    let onsite = add_matrices(
        &scale_matrix(&gamma_4, scalar(0.5))?,
        &scale_matrix(&gamma_2, scalar(0.5))?,
    )?;
    let hopping_x = add_matrices(
        &scale_matrix(&gamma_4, scalar(0.5))?,
        &scale_matrix(&gamma_3, Complex64::new(0.0, -0.5))?,
    )?;
    let hopping_y = add_matrices(
        &scale_matrix(&gamma_2, scalar(0.5))?,
        &scale_matrix(&gamma_1, Complex64::new(0.0, -0.5))?,
    )?;
    fourier_model(
        2,
        onsite,
        vec![(vec![1, 0], hopping_x), (vec![0, 1], hopping_y)],
    )
}

fn nested_wilson_polarizations(
    model: &TightBindingModel,
    loop_samples: usize,
    transverse_samples: usize,
) -> Result<(Vec<Vec<f64>>, Vec<f64>), Box<dyn Error>> {
    let occupied = 2;
    let mut centers = Vec::new();
    let mut sector_frames = vec![Vec::new(), Vec::new()];
    for iy in 0..transverse_samples {
        let ky = iy as f64 / transverse_samples as f64;
        let mut frames = (0..loop_samples)
            .map(|ix| {
                occupied_frame(
                    &model.hamiltonian(&[ix as f64 / loop_samples as f64, ky])?,
                    occupied,
                )
            })
            .collect::<Result<Vec<_>, _>>()?;
        frames.push(frames[0].clone());
        let unitary = wilson_loop_unitary(&frames)?;
        let decomposition = schur(&unitary)?;
        let mut order = (0..occupied).collect::<Vec<_>>();
        let local_centers = decomposition
            .eigenvalues()
            .iter()
            .map(|value| (value.arg() / std::f64::consts::TAU).rem_euclid(1.0))
            .collect::<Vec<_>>();
        order.sort_by(|left, right| local_centers[*left].total_cmp(&local_centers[*right]));
        centers.push(order.iter().map(|index| local_centers[*index]).collect());
        for (sector, index) in order.iter().enumerate() {
            let mut state = ComplexMatrix::zeros(1, frames[0].columns());
            for basis in 0..frames[0].columns() {
                let amplitude = (0..occupied)
                    .map(|row| {
                        frames[0].get(row, basis).unwrap()
                            * decomposition.vectors().get(row, *index).unwrap()
                    })
                    .sum::<Complex64>();
                state.set(0, basis, amplitude)?;
            }
            let norm = state
                .as_slice()
                .iter()
                .map(|value| value.norm_sqr())
                .sum::<f64>()
                .sqrt();
            sector_frames[sector].push(scale_matrix(&state, scalar(1.0 / norm))?);
        }
    }
    let polarizations = sector_frames
        .iter()
        .map(|states| {
            let mut closed = states.clone();
            closed.push(closed[0].clone());
            Ok((-wilson_line_phase(&closed)? / std::f64::consts::TAU).rem_euclid(1.0))
        })
        .collect::<Result<Vec<_>, Box<dyn Error>>>()?;
    Ok((centers, polarizations))
}

fn bulk_bbh_nested_wilson() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let model = bbh_model()?;
    let minimum_gap = minimum_direct_gap(&model, 24, 2)?;
    let (centers, sector_polarizations) = nested_wilson_polarizations(&model, 51, 51)?;
    let minimum_wannier_gap = centers
        .iter()
        .map(|values| values[1] - values[0])
        .fold(f64::INFINITY, f64::min);
    let quadrupole = ((sector_polarizations[0] + sector_polarizations[1]) / 2.0).rem_euclid(1.0);
    let checks = vec![
        check(
            "bulk_gap",
            minimum_gap > 1.3,
            json!(minimum_gap),
            json!("> 1.3"),
            None,
        ),
        check(
            "wannier_gap",
            minimum_wannier_gap > 0.45,
            json!(minimum_wannier_gap),
            json!("> 0.45"),
            None,
        ),
        check(
            "nested_sector_polarizations",
            sector_polarizations
                .iter()
                .all(|value| (value - 0.5).abs() < 3.0e-5),
            json!(sector_polarizations),
            json!([0.5, 0.5]),
            Some(3.0e-5),
        ),
        check(
            "quadrupole",
            (quadrupole - 0.5).abs() < 3.0e-5,
            json!(quadrupole),
            json!(0.5),
            Some(3.0e-5),
        ),
    ];
    Ok((
        json!({
            "minimum_bulk_gap": minimum_gap,
            "minimum_wannier_gap": minimum_wannier_gap,
            "sector_polarizations": sector_polarizations,
            "quadrupole": quadrupole,
        }),
        checks,
    ))
}

fn tilted_dirac_model(tilt: f64) -> Result<TightBindingModel, Box<dyn Error>> {
    let onsite = pauli_z(scalar(2.4))?;
    let hopping_x = add_matrices(
        &add_matrices(
            &pauli_z(scalar(-0.5))?,
            &pauli_x(Complex64::new(0.0, -0.5))?,
        )?,
        &scale_matrix(
            &ComplexMatrix::identity(2),
            Complex64::new(0.0, -0.5 * tilt),
        )?,
    )?;
    let hopping_y = add_matrices(
        &pauli_z(scalar(-0.5))?,
        &pauli_y(Complex64::new(0.0, -0.5))?,
    )?;
    fourier_model(
        2,
        onsite,
        vec![(vec![1, 0], hopping_x), (vec![0, 1], hopping_y)],
    )
}

fn matrix_element(
    left_state: usize,
    operator: &ComplexMatrix,
    right_state: usize,
    eigenvectors: &ComplexMatrix,
) -> Result<Complex64, Box<dyn Error>> {
    let mut value = Complex64::new(0.0, 0.0);
    for row in 0..operator.rows() {
        for column in 0..operator.columns() {
            value += eigenvectors.get(row, left_state)?.conj()
                * operator.get(row, column)?
                * eigenvectors.get(column, right_state)?;
        }
    }
    Ok(value)
}

fn berry_curvature_dipole(
    model: &TightBindingModel,
    chemical_potentials: &[f64],
) -> Result<Vec<f64>, Box<dyn Error>> {
    let samples = 51;
    let step = 1.0e-4;
    let temperature = 0.03;
    let mut records = Vec::new();
    for ix in 0..samples {
        for iy in 0..samples {
            let point = [
                (ix as f64 + 0.5) / samples as f64 - 0.5,
                (iy as f64 + 0.5) / samples as f64 - 0.5,
            ];
            let plus_x = [point[0] + step, point[1]];
            let minus_x = [point[0] - step, point[1]];
            let plus_y = [point[0], point[1] + step];
            let minus_y = [point[0], point[1] - step];
            let eigensystem = model.eigensystem(&point)?;
            let plus_x_h = model.hamiltonian(&plus_x)?;
            let minus_x_h = model.hamiltonian(&minus_x)?;
            let plus_y_h = model.hamiltonian(&plus_y)?;
            let minus_y_h = model.hamiltonian(&minus_y)?;
            let velocity_x = scale_matrix(
                &subtract_matrices(&plus_x_h, &minus_x_h)?,
                scalar(0.5 / step),
            )?;
            let velocity_y = scale_matrix(
                &subtract_matrices(&plus_y_h, &minus_y_h)?,
                scalar(0.5 / step),
            )?;
            let first = matrix_element(1, &velocity_x, 0, eigensystem.eigenvectors())?;
            let second = matrix_element(0, &velocity_y, 1, eigensystem.eigenvectors())?;
            let gap = eigensystem.eigenvalues()[1] - eigensystem.eigenvalues()[0];
            let curvature = -2.0 * (first * second).im / gap.powi(2);
            let plus_energy = model.eigensystem(&plus_x)?.eigenvalues()[1];
            let minus_energy = model.eigensystem(&minus_x)?.eigenvalues()[1];
            let energy_velocity = (plus_energy - minus_energy) / (2.0 * step);
            records.push((eigensystem.eigenvalues()[1], curvature, energy_velocity));
        }
    }
    Ok(chemical_potentials
        .iter()
        .map(|chemical_potential| {
            records
                .iter()
                .map(|(energy, curvature, velocity)| {
                    let argument = ((energy - chemical_potential) / temperature).clamp(-40.0, 40.0);
                    let minus_derivative =
                        1.0 / (4.0 * temperature * (argument / 2.0).cosh().powi(2));
                    curvature * velocity * minus_derivative
                })
                .sum::<f64>()
                / (samples * samples) as f64
        })
        .collect())
}

fn bulk_tilted_dirac_berry_dipole() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let chemical_potentials = [0.4, 0.5, 0.6, 0.8, 1.0];
    let positive = berry_curvature_dipole(&tilted_dirac_model(0.25)?, &chemical_potentials)?;
    let negative = berry_curvature_dipole(&tilted_dirac_model(-0.25)?, &chemical_potentials)?;
    let odd_error = positive
        .iter()
        .zip(&negative)
        .map(|(left, right)| (left + right).abs())
        .fold(0.0_f64, f64::max);
    let peak_index = positive
        .iter()
        .enumerate()
        .max_by(|left, right| left.1.abs().total_cmp(&right.1.abs()))
        .map(|(index, _)| index)
        .unwrap();
    let maximum_response = positive
        .iter()
        .map(|value| value.abs())
        .fold(0.0_f64, f64::max);
    let checks = vec![
        check(
            "odd_under_tilt_reversal",
            odd_error < 5.0e-4,
            json!(odd_error),
            json!(0.0),
            Some(5.0e-4),
        ),
        check(
            "finite_nonlinear_response",
            maximum_response > 0.5,
            json!(maximum_response),
            json!("> 0.5"),
            None,
        ),
        check(
            "band_edge_variation",
            [1, 2, 3].contains(&peak_index),
            json!(chemical_potentials[peak_index]),
            json!("near the band edge"),
            None,
        ),
    ];
    Ok((
        json!({
            "chemical_potentials": chemical_potentials,
            "positive_tilt_dipole": positive,
            "negative_tilt_dipole": negative,
            "odd_reversal_error": odd_error,
            "peak_chemical_potential": chemical_potentials[peak_index],
        }),
        checks,
    ))
}

fn minimal_weyl_model(node: f64) -> Result<TightBindingModel, Box<dyn Error>> {
    let onsite = pauli_z(scalar(2.0 - node.cos()))?;
    let hopping_x = add_matrices(
        &pauli_z(scalar(-0.5))?,
        &pauli_x(Complex64::new(0.0, -0.5))?,
    )?;
    let hopping_y = add_matrices(
        &pauli_z(scalar(-0.5))?,
        &pauli_y(Complex64::new(0.0, -0.5))?,
    )?;
    fourier_model(
        3,
        onsite,
        vec![
            (vec![1, 0, 0], hopping_x),
            (vec![0, 1, 0], hopping_y),
            (vec![0, 0, 1], pauli_z(scalar(0.5))?),
        ],
    )
}

fn bulk_weyl_chirality() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let node = std::f64::consts::PI / 3.0;
    let node_reduced = node / std::f64::consts::TAU;
    let model = minimal_weyl_model(node)?;
    let node_gaps = [node_reduced, 1.0 - node_reduced]
        .iter()
        .map(|kz| {
            model
                .eigensystem(&[0.0, 0.0, *kz])
                .map(|system| system.eigenvalues()[1] - system.eigenvalues()[0])
        })
        .collect::<Result<Vec<_>, _>>()?;
    let all_slices = chern_numbers_on_uniform_grid(&model, &[31, 31, 4], [0, 1], &[0])?
        .values()
        .to_vec();
    let slice_coordinates = [0.0, 0.25, 0.75];
    let slice_chern = vec![all_slices[0], all_slices[1], all_slices[3]];
    let rounded = slice_chern
        .iter()
        .map(|value| value.round() as i64)
        .collect::<Vec<_>>();
    let jumps = [rounded[1] - rounded[0], rounded[0] - rounded[2]];
    let checks = vec![
        check(
            "node_locations",
            node_gaps.iter().all(|gap| gap.abs() < 1.0e-10),
            json!(node_gaps),
            json!(0.0),
            Some(1.0e-10),
        ),
        check(
            "slice_chern_jump",
            rounded[0] == 0 && rounded[1].abs() == 1 && rounded[1] == rounded[2],
            json!(rounded),
            json!("trivial between nodes and nonzero outside"),
            None,
        ),
        check(
            "opposite_chiralities",
            jumps[0] == -jumps[1],
            json!(jumps),
            json!("opposite monopole charges"),
            None,
        ),
    ];
    Ok((
        json!({
            "node_positions_reduced": [node_reduced, 1.0 - node_reduced],
            "node_gaps": node_gaps,
            "slice_coordinates": slice_coordinates,
            "slice_chern_numbers": slice_chern,
        }),
        checks,
    ))
}

fn nodal_ring_model(mass: f64) -> Result<TightBindingModel, Box<dyn Error>> {
    fourier_model(
        3,
        pauli_x(scalar(mass))?,
        vec![
            (vec![1, 0, 0], pauli_x(scalar(-0.5))?),
            (vec![0, 1, 0], pauli_x(scalar(-0.5))?),
            (vec![0, 0, 1], pauli_z(Complex64::new(0.0, -0.5))?),
        ],
    )
}

fn loop_berry_phase(
    model: &TightBindingModel,
    center_kx: f64,
    radius: f64,
) -> Result<f64, Box<dyn Error>> {
    let mut frames = Vec::new();
    for sample in 0..401 {
        let angle = std::f64::consts::TAU * sample as f64 / 401.0;
        let momentum = [
            (center_kx + radius * angle.cos()) / std::f64::consts::TAU,
            0.0,
            (radius * angle.sin()) / std::f64::consts::TAU,
        ];
        frames.push(occupied_frame(&model.hamiltonian(&momentum)?, 1)?);
    }
    frames.push(frames[0].clone());
    Ok(wilson_line_phase(&frames)?)
}

fn bulk_nodal_line_berry_phase() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let mass = 1.5_f64;
    let model = nodal_ring_model(mass)?;
    let ring_kx = (mass - 1.0).acos();
    let linked = loop_berry_phase(&model, ring_kx, 0.08)?;
    let unlinked = loop_berry_phase(&model, 0.0, 0.08)?;
    let checks = vec![
        check(
            "linked_pi_phase",
            (linked.abs() - std::f64::consts::PI).abs() < 2.0e-5,
            json!(linked),
            json!("pi modulo 2pi"),
            Some(2.0e-5),
        ),
        check(
            "unlinked_trivial_phase",
            unlinked.abs() < 2.0e-5,
            json!(unlinked),
            json!(0.0),
            Some(2.0e-5),
        ),
    ];
    Ok((
        json!({
            "ring_point": [ring_kx / std::f64::consts::TAU, 0.0, 0.0],
            "linked_loop_phase": linked,
            "unlinked_loop_phase": unlinked,
        }),
        checks,
    ))
}

fn interpolation_source_model() -> Result<TightBindingModel, Box<dyn Error>> {
    let onsite = add_matrices(&pauli_z(scalar(0.23))?, &pauli_x(scalar(0.17))?)?;
    let first = add_matrices(
        &pauli_z(scalar(0.31))?,
        &pauli_x(Complex64::new(0.0, -0.22))?,
    )?;
    let second = add_matrices(
        &pauli_z(scalar(-0.19))?,
        &pauli_y(Complex64::new(0.0, -0.27))?,
    )?;
    let third = add_matrices(
        &pauli_x(scalar(0.07))?,
        &pauli_z(Complex64::new(0.0, 0.05))?,
    )?;
    fourier_model(
        2,
        onsite,
        vec![
            (vec![1, 0], first),
            (vec![0, 1], second),
            (vec![2, 1], third),
        ],
    )
}

fn bulk_wannier_interpolation() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let model = interpolation_source_model()?;
    let mesh = [8_usize, 8_usize];
    let mut samples = Vec::new();
    for ix in 0..mesh[0] {
        for iy in 0..mesh[1] {
            samples.push(
                model.hamiltonian(&[ix as f64 / mesh[0] as f64, iy as f64 / mesh[1] as f64])?,
            );
        }
    }
    let points = (0..17)
        .map(|index| {
            vec![
                ((index * 7 + 3) % 37) as f64 / 37.0,
                ((index * 11 + 5) % 41) as f64 / 41.0,
            ]
        })
        .collect::<Vec<_>>();
    let interpolated = interpolate_periodic_matrices(&mesh, &samples, &points)?;
    let mut maximum_error = 0.0_f64;
    let mut maximum_hermiticity_error = 0.0_f64;
    for (point, estimate) in points.iter().zip(&interpolated) {
        let direct = model.eigensystem(point)?.eigenvalues().to_vec();
        let estimate_values = hermitian_eigensystem(estimate, 1.0e-10)?
            .eigenvalues()
            .to_vec();
        for (left, right) in direct.iter().zip(&estimate_values) {
            maximum_error = maximum_error.max((left - right).abs());
        }
        for row in 0..estimate.rows() {
            for column in 0..estimate.columns() {
                maximum_hermiticity_error = maximum_hermiticity_error
                    .max((estimate.get(row, column)? - estimate.get(column, row)?.conj()).norm());
            }
        }
    }
    let checks = vec![
        check(
            "off_mesh_energies",
            maximum_error < 1.0e-9,
            json!(maximum_error),
            json!(0.0),
            Some(1.0e-9),
        ),
        check(
            "hermiticity",
            maximum_hermiticity_error < 1.0e-12,
            json!(maximum_hermiticity_error),
            json!(0.0),
            Some(1.0e-12),
        ),
    ];
    Ok((
        json!({
            "maximum_off_mesh_energy_error": maximum_error,
            "maximum_hermiticity_error": maximum_hermiticity_error,
            "validation_points": points.len(),
        }),
        checks,
    ))
}

fn add_block(
    target: &mut ComplexMatrix,
    row_offset: usize,
    column_offset: usize,
    block: &ComplexMatrix,
    scale: Complex64,
) -> Result<(), Box<dyn Error>> {
    for row in 0..block.rows() {
        for column in 0..block.columns() {
            target.add_entry(
                row_offset + row,
                column_offset + column,
                scale * block.get(row, column)?,
            )?;
        }
    }
    Ok(())
}

fn finite_ribbon_hamiltonian(
    width: usize,
    reduced_momentum: f64,
    onsite: &ComplexMatrix,
    hoppings: &[(i32, i32, ComplexMatrix)],
) -> Result<ComplexMatrix, Box<dyn Error>> {
    let block_size = onsite.rows();
    let mut hamiltonian = ComplexMatrix::zeros(width * block_size, width * block_size);
    for cell in 0..width {
        add_block(
            &mut hamiltonian,
            cell * block_size,
            cell * block_size,
            onsite,
            scalar(1.0),
        )?;
    }
    for cell in 0..width {
        for (offset_x, offset_y, hopping) in hoppings {
            let target_cell = cell as i32 + offset_y;
            if !(0..width as i32).contains(&target_cell) {
                continue;
            }
            let phase = Complex64::from_polar(
                1.0,
                std::f64::consts::TAU * reduced_momentum * *offset_x as f64,
            );
            add_block(
                &mut hamiltonian,
                cell * block_size,
                target_cell as usize * block_size,
                hopping,
                phase,
            )?;
            add_block(
                &mut hamiltonian,
                target_cell as usize * block_size,
                cell * block_size,
                &hopping.adjoint(),
                phase.conj(),
            )?;
        }
    }
    Ok(hamiltonian)
}

fn haldane_ribbon_hamiltonian(
    width: usize,
    momentum: f64,
) -> Result<ComplexMatrix, Box<dyn Error>> {
    let onsite = add_matrices(&pauli_z(scalar(0.2))?, &pauli_x(scalar(1.0))?)?;
    let mut hoppings = Vec::new();
    for (offset_x, offset_y, chirality) in [(1, 0, -1.0), (0, 1, 1.0), (1, -1, 1.0)] {
        let mut matrix = ComplexMatrix::zeros(2, 2);
        matrix.set(0, 0, Complex64::new(0.0, -chirality * 0.15))?;
        matrix.set(1, 1, Complex64::new(0.0, chirality * 0.15))?;
        if (offset_x, offset_y) == (1, 0) || (offset_x, offset_y) == (0, 1) {
            matrix.set(0, 1, scalar(1.0))?;
        }
        hoppings.push((offset_x, offset_y, matrix));
    }
    finite_ribbon_hamiltonian(width, momentum, &onsite, &hoppings)
}

fn state_weight(
    vectors: &ComplexMatrix,
    state: usize,
    orbitals: &[usize],
) -> Result<f64, Box<dyn Error>> {
    Ok(orbitals
        .iter()
        .map(|orbital| vectors.get(*orbital, state).map(|value| value.norm_sqr()))
        .collect::<Result<Vec<_>, _>>()?
        .iter()
        .sum())
}

fn state_overlap(
    left_vectors: &ComplexMatrix,
    left_state: usize,
    right_vectors: &ComplexMatrix,
    right_state: usize,
) -> Result<f64, Box<dyn Error>> {
    let overlap = (0..left_vectors.rows())
        .map(|orbital| {
            Ok(left_vectors.get(orbital, left_state)?.conj()
                * right_vectors.get(orbital, right_state)?)
        })
        .collect::<Result<Vec<Complex64>, Box<dyn Error>>>()?
        .iter()
        .sum::<Complex64>();
    Ok(overlap.norm_sqr())
}

fn boundary_haldane_ribbon_flow() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let width = 24;
    let mut best: Option<(f64, f64, Vec<f64>, ComplexMatrix, Vec<usize>)> = None;
    for sample in 0..=300 {
        let momentum = 0.4 + 0.15 * sample as f64 / 300.0;
        let eigensystem =
            hermitian_eigensystem(&haldane_ribbon_hamiltonian(width, momentum)?, 1.0e-10)?;
        let values = eigensystem.eigenvalues().to_vec();
        let mut order = (0..values.len()).collect::<Vec<_>>();
        order.sort_by(|left, right| values[*left].abs().total_cmp(&values[*right].abs()));
        let pair = order[..2].to_vec();
        let score = values[pair[0]].abs().max(values[pair[1]].abs());
        if best.as_ref().map_or(true, |current| score < current.0) {
            best = Some((
                score,
                momentum,
                values,
                eigensystem.eigenvectors().clone(),
                pair,
            ));
        }
    }
    let (_, crossing_momentum, values, vectors, pair) = best.unwrap();
    let lower_orbitals = (0..4).collect::<Vec<_>>();
    let upper_orbitals = (2 * width - 4..2 * width).collect::<Vec<_>>();
    let lower_state = *pair
        .iter()
        .max_by(|left, right| {
            state_weight(&vectors, **left, &lower_orbitals)
                .unwrap()
                .total_cmp(&state_weight(&vectors, **right, &lower_orbitals).unwrap())
        })
        .unwrap();
    let upper_state = *pair
        .iter()
        .max_by(|left, right| {
            state_weight(&vectors, **left, &upper_orbitals)
                .unwrap()
                .total_cmp(&state_weight(&vectors, **right, &upper_orbitals).unwrap())
        })
        .unwrap();
    let ordered_states = [lower_state, upper_state];
    let edge_weights = [
        state_weight(&vectors, lower_state, &lower_orbitals)?,
        state_weight(&vectors, upper_state, &upper_orbitals)?,
    ];
    let crossing_energies = [values[lower_state], values[upper_state]];
    let delta = 1.0e-4;
    let mut velocities = Vec::new();
    for state in ordered_states {
        let mut branch_energies = Vec::new();
        for momentum in [crossing_momentum - delta, crossing_momentum + delta] {
            let shifted =
                hermitian_eigensystem(&haldane_ribbon_hamiltonian(width, momentum)?, 1.0e-10)?;
            let shifted_state = (0..shifted.eigenvalues().len())
                .max_by(|left, right| {
                    state_overlap(&vectors, state, shifted.eigenvectors(), *left)
                        .unwrap()
                        .total_cmp(
                            &state_overlap(&vectors, state, shifted.eigenvectors(), *right)
                                .unwrap(),
                        )
                })
                .unwrap();
            branch_energies.push(shifted.eigenvalues()[shifted_state]);
        }
        velocities.push((branch_energies[1] - branch_energies[0]) / (2.0 * delta));
    }
    let bulk = haldane_model()?;
    let bulk_chern = fhs_chern([31, 31], 1, |point| {
        bulk.hamiltonian(&point).map_err(Into::into)
    })?;
    let checks = vec![
        check(
            "nontrivial_bulk",
            (bulk_chern.round() as i64).abs() == 1,
            json!(bulk_chern),
            json!("magnitude 1"),
            None,
        ),
        check(
            "two_in_gap_branches",
            crossing_energies.iter().all(|energy| energy.abs() < 1.0e-2),
            json!(crossing_energies),
            json!("two near-zero branches"),
            None,
        ),
        check(
            "opposite_edge_localization",
            edge_weights.iter().all(|weight| *weight > 0.9),
            json!(edge_weights),
            json!("> 0.9"),
            None,
        ),
        check(
            "chiral_spectral_flow",
            velocities[0] * velocities[1] < 0.0
                && velocities.iter().all(|velocity| velocity.abs() > 1.0),
            json!(velocities),
            json!("opposite nonzero velocities"),
            None,
        ),
    ];
    Ok((
        json!({
            "bulk_chern_number": bulk_chern,
            "crossing_momentum": crossing_momentum,
            "crossing_energies": crossing_energies,
            "edge_weights": edge_weights,
            "edge_velocities": velocities,
            "in_gap_edge_branch_count": 2,
        }),
        checks,
    ))
}

fn graphene_ribbon_hamiltonian(
    width: usize,
    momentum: f64,
    armchair: bool,
) -> Result<ComplexMatrix, Box<dyn Error>> {
    let mut hamiltonian = ComplexMatrix::zeros(2 * width, 2 * width);
    for cell in 0..width {
        for (offset_x, offset_y) in [(0_i32, 0_i32), (-1, 0), (0, -1)] {
            let shift = if armchair {
                offset_y - offset_x
            } else {
                offset_y
            };
            let target_cell = cell as i32 + shift;
            if !(0..width as i32).contains(&target_cell) {
                continue;
            }
            let phase =
                Complex64::from_polar(1.0, std::f64::consts::TAU * momentum * offset_x as f64);
            let left = 2 * cell;
            let right = 2 * target_cell as usize + 1;
            hamiltonian.add_entry(left, right, -phase)?;
            hamiltonian.add_entry(right, left, -phase.conj())?;
        }
    }
    Ok(hamiltonian)
}

fn boundary_graphene_terminations() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let widths = [12_usize, 18, 24];
    let mut zigzag_minimum_gaps = Vec::new();
    let mut zigzag_edge_weights = Vec::new();
    let mut armchair_gaps = Vec::new();
    for width in widths {
        let mut minimum_gap = f64::INFINITY;
        let mut maximum_edge_weight = 0.0_f64;
        let edge_orbitals = [0, 1, 2 * width - 2, 2 * width - 1];
        for sample in 0..301 {
            let momentum = sample as f64 / 301.0;
            let eigensystem = hermitian_eigensystem(
                &graphene_ribbon_hamiltonian(width, momentum, false)?,
                1.0e-10,
            )?;
            let gap = eigensystem.eigenvalues()[width] - eigensystem.eigenvalues()[width - 1];
            minimum_gap = minimum_gap.min(gap);
            let mut order = (0..2 * width).collect::<Vec<_>>();
            order.sort_by(|left, right| {
                eigensystem.eigenvalues()[*left]
                    .abs()
                    .total_cmp(&eigensystem.eigenvalues()[*right].abs())
            });
            let edge_weight = order[..2]
                .iter()
                .map(|state| state_weight(eigensystem.eigenvectors(), *state, &edge_orbitals))
                .collect::<Result<Vec<_>, _>>()?
                .iter()
                .sum::<f64>()
                / 2.0;
            maximum_edge_weight = maximum_edge_weight.max(edge_weight);
        }
        zigzag_minimum_gaps.push(minimum_gap);
        zigzag_edge_weights.push(maximum_edge_weight);
        let values =
            hermitian_eigensystem(&graphene_ribbon_hamiltonian(width, 0.0, true)?, 1.0e-10)?
                .eigenvalues()
                .to_vec();
        armchair_gaps.push(values[width] - values[width - 1]);
    }
    let scaled = widths
        .iter()
        .zip(&armchair_gaps)
        .map(|(width, gap)| *width as f64 * gap)
        .collect::<Vec<_>>();
    let mean = scaled.iter().sum::<f64>() / scaled.len() as f64;
    let spread = (scaled.iter().copied().fold(f64::NEG_INFINITY, f64::max)
        - scaled.iter().copied().fold(f64::INFINITY, f64::min))
        / mean;
    let checks = vec![
        check(
            "zigzag_edge_band",
            zigzag_minimum_gaps.iter().all(|gap| *gap < 1.0e-6),
            json!(zigzag_minimum_gaps),
            json!("gapless"),
            None,
        ),
        check(
            "zigzag_edge_localization",
            zigzag_edge_weights.iter().all(|weight| *weight > 0.95),
            json!(zigzag_edge_weights),
            json!("> 0.95"),
            None,
        ),
        check(
            "armchair_finite_gaps",
            armchair_gaps.iter().all(|gap| *gap > 0.1),
            json!(armchair_gaps),
            json!("> 0.1"),
            None,
        ),
        check(
            "armchair_inverse_width_scaling",
            armchair_gaps.windows(2).all(|pair| pair[0] > pair[1]) && spread < 0.08,
            json!(spread),
            json!("< 0.08"),
            None,
        ),
    ];
    Ok((
        json!({
            "widths": widths,
            "zigzag_minimum_gaps": zigzag_minimum_gaps,
            "zigzag_edge_weights": zigzag_edge_weights,
            "armchair_gaps": armchair_gaps,
            "width_scaled_armchair_gaps": scaled,
            "armchair_scaling_spread": spread,
        }),
        checks,
    ))
}

fn finite_bbh_hamiltonian(cells_x: usize, cells_y: usize) -> Result<ComplexMatrix, Box<dyn Error>> {
    let gamma_1 = scale_matrix(
        &kronecker(&pauli_y(scalar(1.0))?, &pauli_x(scalar(1.0))?)?,
        scalar(-1.0),
    )?;
    let gamma_2 = scale_matrix(
        &kronecker(&pauli_y(scalar(1.0))?, &pauli_y(scalar(1.0))?)?,
        scalar(-1.0),
    )?;
    let gamma_3 = scale_matrix(
        &kronecker(&pauli_y(scalar(1.0))?, &pauli_z(scalar(1.0))?)?,
        scalar(-1.0),
    )?;
    let gamma_4 = kronecker(&pauli_x(scalar(1.0))?, &ComplexMatrix::identity(2))?;
    let onsite = add_matrices(
        &scale_matrix(&gamma_4, scalar(0.5))?,
        &scale_matrix(&gamma_2, scalar(0.5))?,
    )?;
    let hopping_x = add_matrices(
        &scale_matrix(&gamma_4, scalar(0.5))?,
        &scale_matrix(&gamma_3, Complex64::new(0.0, -0.5))?,
    )?;
    let hopping_y = add_matrices(
        &scale_matrix(&gamma_2, scalar(0.5))?,
        &scale_matrix(&gamma_1, Complex64::new(0.0, -0.5))?,
    )?;
    let dimension = 4 * cells_x * cells_y;
    let mut hamiltonian = ComplexMatrix::zeros(dimension, dimension);
    let cell_offset = |x: usize, y: usize| 4 * (y * cells_x + x);
    for y in 0..cells_y {
        for x in 0..cells_x {
            let current = cell_offset(x, y);
            add_block(&mut hamiltonian, current, current, &onsite, scalar(1.0))?;
            if x + 1 < cells_x {
                let target = cell_offset(x + 1, y);
                add_block(&mut hamiltonian, current, target, &hopping_x, scalar(1.0))?;
                add_block(
                    &mut hamiltonian,
                    target,
                    current,
                    &hopping_x.adjoint(),
                    scalar(1.0),
                )?;
            }
            if y + 1 < cells_y {
                let target = cell_offset(x, y + 1);
                add_block(&mut hamiltonian, current, target, &hopping_y, scalar(1.0))?;
                add_block(
                    &mut hamiltonian,
                    target,
                    current,
                    &hopping_y.adjoint(),
                    scalar(1.0),
                )?;
            }
        }
    }
    Ok(hamiltonian)
}

fn boundary_bbh_corner_modes() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let cells_x = 8;
    let cells_y = 8;
    let eigensystem = hermitian_eigensystem(&finite_bbh_hamiltonian(cells_x, cells_y)?, 1.0e-10)?;
    let values = eigensystem.eigenvalues();
    let vectors = eigensystem.eigenvectors();
    let mut order = (0..values.len()).collect::<Vec<_>>();
    order.sort_by(|left, right| values[*left].abs().total_cmp(&values[*right].abs()));
    let midgap = &order[..4];
    let midgap_energies = midgap
        .iter()
        .map(|state| values[*state])
        .collect::<Vec<_>>();
    let next_gap = values[order[4]].abs();
    let cell_offset = |x: usize, y: usize| 4 * (y * cells_x + x);
    let mut corner_orbitals = Vec::new();
    for (x, y) in [
        (0, 0),
        (0, cells_y - 1),
        (cells_x - 1, 0),
        (cells_x - 1, cells_y - 1),
    ] {
        corner_orbitals.extend(cell_offset(x, y)..cell_offset(x, y) + 4);
    }
    let corner_weights = midgap
        .iter()
        .map(|state| state_weight(vectors, *state, &corner_orbitals))
        .collect::<Result<Vec<_>, _>>()?;
    let mut sublattice_support = Vec::new();
    for orbital in 0..4 {
        let mut support = 0.0;
        for state in midgap {
            for cell in 0..cells_x * cells_y {
                support += vectors.get(4 * cell + orbital, *state)?.norm_sqr();
            }
        }
        sublattice_support.push(support);
    }
    let checks = vec![
        check(
            "four_midgap_modes",
            midgap_energies.iter().all(|energy| energy.abs() < 1.0e-2) && next_gap > 0.5,
            json!(midgap_energies),
            json!("four isolated midgap states"),
            None,
        ),
        check(
            "corner_localization",
            corner_weights.iter().all(|weight| *weight > 0.55),
            json!(corner_weights),
            json!("> 0.55"),
            None,
        ),
        check(
            "sublattice_support",
            sublattice_support
                .iter()
                .all(|support| (support - 1.0).abs() < 2.0e-5),
            json!(sublattice_support),
            json!([1.0, 1.0, 1.0, 1.0]),
            Some(2.0e-5),
        ),
    ];
    Ok((
        json!({
            "midgap_energies": midgap_energies,
            "midgap_count": 4,
            "next_state_absolute_energy": next_gap,
            "corner_weights": corner_weights,
            "sublattice_projector_support": sublattice_support,
        }),
        checks,
    ))
}

fn finite_ssh(
    cells: usize,
    intracell: f64,
    intercell: f64,
) -> Result<ComplexMatrix, Box<dyn Error>> {
    let dimension = 2 * cells;
    let mut hamiltonian = ComplexMatrix::zeros(dimension, dimension);
    for cell in 0..cells {
        let a = 2 * cell;
        let b = a + 1;
        hamiltonian.set(a, b, scalar(intracell))?;
        hamiltonian.set(b, a, scalar(intracell))?;
        if cell + 1 < cells {
            hamiltonian.set(b, a + 2, scalar(intercell))?;
            hamiltonian.set(a + 2, b, scalar(intercell))?;
        }
    }
    Ok(hamiltonian)
}

fn boundary_ssh_edge_localization() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let cell_counts = [12_usize, 20, 32, 48];
    let intracell = 0.6_f64;
    let intercell = 1.0_f64;
    let mut splittings = Vec::new();
    let mut edge_weights = Vec::new();
    for cells in cell_counts {
        let eigensystem =
            hermitian_eigensystem(&finite_ssh(cells, intracell, intercell)?, 1.0e-12)?;
        let mut indices = (0..2 * cells).collect::<Vec<_>>();
        indices.sort_by(|left, right| {
            eigensystem.eigenvalues()[*left]
                .abs()
                .partial_cmp(&eigensystem.eigenvalues()[*right].abs())
                .unwrap()
        });
        let pair = &indices[..2];
        splittings.push(
            pair.iter()
                .map(|state| eigensystem.eigenvalues()[*state].abs())
                .fold(0.0_f64, f64::max),
        );
        let mut mean_weight = 0.0;
        for state in pair {
            let basis = [0, 1, 2 * cells - 2, 2 * cells - 1];
            mean_weight += basis
                .iter()
                .map(|site| {
                    eigensystem
                        .eigenvectors()
                        .get(*site, *state)
                        .unwrap()
                        .norm_sqr()
                })
                .sum::<f64>()
                / 2.0;
        }
        edge_weights.push(mean_weight);
    }
    let n = cell_counts.len() as f64;
    let x_mean = cell_counts.iter().map(|value| *value as f64).sum::<f64>() / n;
    let y = splittings
        .iter()
        .map(|value| value.max(1.0e-300).ln())
        .collect::<Vec<_>>();
    let y_mean = y.iter().sum::<f64>() / n;
    let slope = cell_counts
        .iter()
        .zip(&y)
        .map(|(x, y)| (*x as f64 - x_mean) * (*y - y_mean))
        .sum::<f64>()
        / cell_counts
            .iter()
            .map(|x| (*x as f64 - x_mean).powi(2))
            .sum::<f64>();
    let localization_length = -1.0 / slope;
    let expected_length = -1.0 / (intracell / intercell).ln();
    let decreasing = splittings.windows(2).all(|pair| pair[0] > pair[1]);
    let localized = edge_weights.iter().all(|weight| *weight > 0.60);
    let length_pass = (localization_length - expected_length).abs() / expected_length < 0.08;
    let checks = vec![
        check(
            "splitting_decreases",
            decreasing,
            json!(splittings),
            json!("strictly decreasing"),
            None,
        ),
        check(
            "edge_localization",
            localized,
            json!(edge_weights),
            json!("> 0.60"),
            None,
        ),
        check(
            "localization_length",
            length_pass,
            json!(localization_length),
            json!(expected_length),
            Some(0.08 * expected_length),
        ),
    ];
    Ok((
        json!({
            "splittings": splittings,
            "edge_weights": edge_weights,
            "localization_length": localization_length,
        }),
        checks,
    ))
}

fn transport_ballistic_chain() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let sites = 41;
    let hopping = -1.0;
    let mut device = ComplexMatrix::zeros(sites, sites);
    for site in 0..sites - 1 {
        device.set(site, site + 1, scalar(hopping))?;
        device.set(site + 1, site, scalar(hopping))?;
    }
    let onsite = ComplexMatrix::scalar(scalar(0.0));
    let lead_hopping = ComplexMatrix::scalar(scalar(hopping));
    let mut left_coupling = ComplexMatrix::zeros(sites, 1);
    left_coupling.set(0, 0, scalar(hopping))?;
    let mut right_coupling = ComplexMatrix::zeros(sites, 1);
    right_coupling.set(sites - 1, 0, scalar(hopping))?;
    let leads = [
        LeadContact::new(onsite.clone(), lead_hopping.clone(), left_coupling)?,
        LeadContact::new(onsite, lead_hopping, right_coupling)?,
    ];
    let energies = [-1.5, -0.5, 0.0, 0.5, 1.5];
    let mut transmissions = Vec::new();
    let options = SurfaceGreenOptions {
        broadening: 1.0e-12,
        tolerance: 1.0e-14,
        max_iterations: 512,
    };
    for energy in energies {
        transmissions
            .push(solve_open_system(&device, &leads, energy, options)?.transmission(1, 0)?);
    }
    let maximum_error = transmissions
        .iter()
        .map(|value| (value - 1.0).abs())
        .fold(0.0_f64, f64::max);
    let checks = vec![check(
        "unit_transmission",
        maximum_error < 1.0e-9,
        json!(maximum_error),
        json!(0.0),
        Some(1.0e-9),
    )];
    Ok((
        json!({
            "energies": energies,
            "transmissions": transmissions,
            "maximum_transmission_error": maximum_error,
        }),
        checks,
    ))
}

fn transport_resonant_level() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let level = 0.2;
    let coupling = -0.4;
    let lead_hopping = -1.0;
    let device = ComplexMatrix::scalar(scalar(level));
    let lead_onsite = ComplexMatrix::scalar(scalar(0.0));
    let lead_cell_hopping = ComplexMatrix::scalar(scalar(lead_hopping));
    let device_coupling = ComplexMatrix::scalar(scalar(coupling));
    let leads = [
        LeadContact::new(
            lead_onsite.clone(),
            lead_cell_hopping.clone(),
            device_coupling.clone(),
        )?,
        LeadContact::new(lead_onsite, lead_cell_hopping, device_coupling)?,
    ];
    let resonance = level / (1.0 - coupling.powi(2));
    let energies = [-0.2, -0.1, 0.0, 0.1, 0.2]
        .iter()
        .map(|offset| resonance + offset)
        .collect::<Vec<_>>();
    let options = SurfaceGreenOptions {
        broadening: 1.0e-12,
        tolerance: 1.0e-14,
        max_iterations: 512,
    };
    let mut transmissions = Vec::new();
    let mut analytic = Vec::new();
    for energy in &energies {
        transmissions
            .push(solve_open_system(&device, &leads, *energy, options)?.transmission(1, 0)?);
        let root = (4.0 - energy.powi(2)).sqrt();
        let surface_green = Complex64::new(*energy, -root) / 2.0;
        let self_energy = coupling.powi(2) * surface_green;
        let gamma = -2.0 * self_energy.im;
        let dot_green =
            Complex64::new(1.0, 0.0) / (Complex64::new(*energy - level, 0.0) - 2.0 * self_energy);
        analytic.push(gamma.powi(2) * dot_green.norm_sqr());
    }
    let maximum_analytic_error = transmissions
        .iter()
        .zip(&analytic)
        .map(|(left, right)| (left - right).abs())
        .fold(0.0_f64, f64::max);
    let peak_index = transmissions
        .iter()
        .enumerate()
        .max_by(|left, right| left.1.total_cmp(right.1))
        .map(|(index, _)| index)
        .unwrap();
    let checks = vec![
        check(
            "analytic_line_shape",
            maximum_analytic_error < 2.0e-7,
            json!(maximum_analytic_error),
            json!(0.0),
            Some(2.0e-7),
        ),
        check(
            "resonance_tracks_level",
            (energies[peak_index] - level).abs() < 0.05,
            json!(energies[peak_index]),
            json!(level),
            Some(0.05),
        ),
        check(
            "perfect_symmetric_resonance",
            (transmissions[peak_index] - 1.0).abs() < 2.0e-7,
            json!(transmissions[peak_index]),
            json!(1.0),
            Some(2.0e-7),
        ),
    ];
    Ok((
        json!({
            "energies": energies,
            "transmissions": transmissions,
            "analytic_transmissions": analytic,
            "resonance_energy": energies[peak_index],
            "predicted_resonance_energy": resonance,
            "peak_transmission": transmissions[peak_index],
            "maximum_analytic_error": maximum_analytic_error,
        }),
        checks,
    ))
}

fn aharonov_bohm_device(arm_sites: usize, flux: f64) -> Result<ComplexMatrix, Box<dyn Error>> {
    let dimension = 2 + 2 * arm_sites;
    let left = 0;
    let right = 1;
    let upper = (0..arm_sites).map(|site| 2 + site).collect::<Vec<_>>();
    let lower = (0..arm_sites)
        .map(|site| 2 + arm_sites + site)
        .collect::<Vec<_>>();
    let mut hamiltonian = ComplexMatrix::zeros(dimension, dimension);
    let phase = std::f64::consts::PI * flux / (arm_sites + 1) as f64;
    for (path, sign) in [(&upper, 1.0), (&lower, -1.0)] {
        let mut sites = Vec::with_capacity(arm_sites + 2);
        sites.push(left);
        sites.extend(path);
        sites.push(right);
        let hopping = -Complex64::from_polar(1.0, sign * phase);
        for pair in sites.windows(2) {
            hamiltonian.set(pair[0], pair[1], hopping)?;
            hamiltonian.set(pair[1], pair[0], hopping.conj())?;
        }
    }
    Ok(hamiltonian)
}

fn transport_aharonov_bohm_ring() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let arm_sites = 12;
    let fluxes = [0.0, 0.25, 0.5, 0.75, 1.0];
    let energy = 0.3;
    let mut left_coupling = ComplexMatrix::zeros(2 + 2 * arm_sites, 1);
    left_coupling.set(0, 0, scalar(-1.0))?;
    let mut right_coupling = ComplexMatrix::zeros(2 + 2 * arm_sites, 1);
    right_coupling.set(1, 0, scalar(-1.0))?;
    let leads = [
        LeadContact::new(
            ComplexMatrix::scalar(scalar(0.0)),
            ComplexMatrix::scalar(scalar(-1.0)),
            left_coupling,
        )?,
        LeadContact::new(
            ComplexMatrix::scalar(scalar(0.0)),
            ComplexMatrix::scalar(scalar(-1.0)),
            right_coupling,
        )?,
    ];
    let options = SurfaceGreenOptions {
        broadening: 1.0e-12,
        tolerance: 1.0e-14,
        max_iterations: 512,
    };
    let transmissions = fluxes
        .iter()
        .map(|flux| {
            Ok(solve_open_system(
                &aharonov_bohm_device(arm_sites, *flux)?,
                &leads,
                energy,
                options,
            )?
            .transmission(1, 0)?)
        })
        .collect::<Result<Vec<_>, Box<dyn Error>>>()?;
    let periodicity_error = (transmissions[0] - transmissions[4]).abs();
    let reflection_error = (transmissions[1] - transmissions[3]).abs();
    let half_flux_transmission = transmissions[2];
    let checks = vec![
        check(
            "one_flux_quantum_periodicity",
            periodicity_error < 2.0e-7,
            json!(periodicity_error),
            json!(0.0),
            Some(2.0e-7),
        ),
        check(
            "flux_reflection_symmetry",
            reflection_error < 2.0e-7,
            json!(reflection_error),
            json!(0.0),
            Some(2.0e-7),
        ),
        check(
            "half_flux_destructive_interference",
            half_flux_transmission < 2.0e-7,
            json!(half_flux_transmission),
            json!(0.0),
            Some(2.0e-7),
        ),
        check(
            "finite_zero_flux_transport",
            transmissions[0] > 0.5,
            json!(transmissions[0]),
            json!("> 0.5"),
            None,
        ),
    ];
    Ok((
        json!({
            "energy": energy,
            "fluxes": fluxes,
            "transmissions": transmissions,
            "periodicity_error": periodicity_error,
            "flux_reflection_error": reflection_error,
            "half_flux_transmission": half_flux_transmission,
        }),
        checks,
    ))
}

fn hofstadter_device(
    length: usize,
    width: usize,
    flux: f64,
    disorder: f64,
) -> Result<ComplexMatrix, Box<dyn Error>> {
    let dimension = length * width;
    let mut hamiltonian = ComplexMatrix::zeros(dimension, dimension);
    let index = |x: usize, y: usize| x * width + y;
    for x in 0..length {
        for y in 0..width {
            let current = index(x, y);
            hamiltonian.set(
                current,
                current,
                scalar(disorder * (1.37 * x as f64 + 2.11 * y as f64).sin()),
            )?;
            if x + 1 < length {
                let target = index(x + 1, y);
                let hopping = -Complex64::from_polar(1.0, -std::f64::consts::TAU * flux * y as f64);
                hamiltonian.set(current, target, hopping)?;
                hamiltonian.set(target, current, hopping.conj())?;
            }
            if y + 1 < width {
                let target = index(x, y + 1);
                hamiltonian.set(current, target, scalar(-1.0))?;
                hamiltonian.set(target, current, scalar(-1.0))?;
            }
        }
    }
    Ok(hamiltonian)
}

fn hofstadter_leads(
    length: usize,
    width: usize,
    flux: f64,
) -> Result<[LeadContact; 2], Box<dyn Error>> {
    let mut cell = ComplexMatrix::zeros(width, width);
    for y in 0..width - 1 {
        cell.set(y, y + 1, scalar(-1.0))?;
        cell.set(y + 1, y, scalar(-1.0))?;
    }
    let mut left_hopping = ComplexMatrix::zeros(width, width);
    let mut right_hopping = ComplexMatrix::zeros(width, width);
    let mut left_coupling = ComplexMatrix::zeros(length * width, width);
    let mut right_coupling = ComplexMatrix::zeros(length * width, width);
    for y in 0..width {
        let phase = Complex64::from_polar(1.0, std::f64::consts::TAU * flux * y as f64);
        left_hopping.set(y, y, -phase)?;
        right_hopping.set(y, y, -phase.conj())?;
        left_coupling.set(y, y, -phase)?;
        right_coupling.set((length - 1) * width + y, y, -phase.conj())?;
    }
    Ok([
        LeadContact::new(cell.clone(), left_hopping, left_coupling)?,
        LeadContact::new(cell, right_hopping, right_coupling)?,
    ])
}

fn transport_quantum_hall_strip() -> Result<(Value, Vec<Check>), Box<dyn Error>> {
    let width = 18;
    let length = 32;
    let flux = 0.125;
    let disorder = 0.05;
    let device = hofstadter_device(length, width, flux, disorder)?;
    let leads = hofstadter_leads(length, width, flux)?;
    let energies = [-3.1, -2.8, -2.4, -2.2];
    let options = SurfaceGreenOptions {
        broadening: 1.0e-12,
        tolerance: 1.0e-13,
        max_iterations: 512,
    };
    let mut transmissions = Vec::new();
    let mut reference_solution = None;
    for energy in energies {
        let solution = solve_open_system(&device, &leads, energy, options)?;
        transmissions.push(solution.transmission(1, 0)?);
        if (energy + 2.8_f64).abs() < 1.0e-12 {
            reference_solution = Some(solution);
        }
    }
    let solution = reference_solution.unwrap();
    let probabilities = solution.green_function_transmission_matrix(&[1, 1])?;
    let unitarity_error = (probabilities[0][0] + probabilities[1][0] - 1.0).abs();
    let injection = solution.broadening_factor(0, 1)?;
    let states = solution.scattering_states(&[injection])?;
    let state = &states[0];
    let index = |x: usize, y: usize| x * width + y;
    let mut total_current_weight = 0.0;
    let mut edge_current_weight = 0.0;
    for x in 0..length - 1 {
        for y in 0..width {
            let left = index(x, y);
            let right = index(x + 1, y);
            let current = 2.0
                * (state.get(0, left)?.conj() * device.get(left, right)? * state.get(0, right)?).im;
            total_current_weight += current.abs();
            if y < 2 || y >= width - 2 {
                edge_current_weight += current.abs();
            }
        }
    }
    let edge_current_fraction = edge_current_weight / total_current_weight;
    let maximum_plateau_error = transmissions
        .iter()
        .map(|transmission| (transmission - 1.0).abs())
        .fold(0.0_f64, f64::max);
    let checks = vec![
        check(
            "first_hall_plateau",
            maximum_plateau_error < 3.0e-5,
            json!(maximum_plateau_error),
            json!(0.0),
            Some(3.0e-5),
        ),
        check(
            "scattering_unitarity",
            unitarity_error < 3.0e-5,
            json!(unitarity_error),
            json!(0.0),
            Some(3.0e-5),
        ),
        check(
            "edge_localized_bond_current",
            edge_current_fraction > 0.8,
            json!(edge_current_fraction),
            json!("> 0.8"),
            None,
        ),
    ];
    Ok((
        json!({
            "energies": energies,
            "transmissions": transmissions,
            "maximum_plateau_error": maximum_plateau_error,
            "maximum_unitarity_error": unitarity_error,
            "edge_current_fraction": edge_current_fraction,
        }),
        checks,
    ))
}

fn not_implemented(case_id: &str) -> Value {
    json!({
        "schema_version": 1,
        "case_id": case_id,
        "backend": "thouless",
        "backend_version": BACKEND_VERSION,
        "status": "not_implemented",
    })
}

fn main() -> Result<(), Box<dyn Error>> {
    let case_id = env::args()
        .nth(1)
        .ok_or("usage: thouless-benchmark-runner CASE_ID")?;
    let started = Instant::now();
    let computed = match case_id.as_str() {
        "bulk_graphene_dirac_cone" => Some(bulk_graphene_dirac_cone()?),
        "bulk_ssh_polarization" => Some(bulk_ssh_polarization()?),
        "bulk_rice_mele_pump" => Some(bulk_rice_mele_pump()?),
        "bulk_haldane_chern_transition" => Some(bulk_haldane_chern_transition()?),
        "bulk_qwz_phase_diagram" => Some(bulk_qwz_phase_diagram()?),
        "bulk_kane_mele_z2" => Some(bulk_kane_mele_z2()?),
        "bulk_kagome_soc_chern" => Some(bulk_kagome_soc_chern()?),
        "bulk_bbh_nested_wilson" => Some(bulk_bbh_nested_wilson()?),
        "bulk_weyl_chirality" => Some(bulk_weyl_chirality()?),
        "bulk_nodal_line_berry_phase" => Some(bulk_nodal_line_berry_phase()?),
        "bulk_tilted_dirac_berry_dipole" => Some(bulk_tilted_dirac_berry_dipole()?),
        "bulk_wannier_interpolation" => Some(bulk_wannier_interpolation()?),
        "boundary_ssh_edge_localization" => Some(boundary_ssh_edge_localization()?),
        "boundary_haldane_ribbon_flow" => Some(boundary_haldane_ribbon_flow()?),
        "boundary_graphene_terminations" => Some(boundary_graphene_terminations()?),
        "boundary_bbh_corner_modes" => Some(boundary_bbh_corner_modes()?),
        "transport_ballistic_chain" => Some(transport_ballistic_chain()?),
        "transport_resonant_level" => Some(transport_resonant_level()?),
        "transport_aharonov_bohm_ring" => Some(transport_aharonov_bohm_ring()?),
        "transport_quantum_hall_strip" => Some(transport_quantum_hall_strip()?),
        _ => None,
    };
    let Some((metrics, checks)) = computed else {
        println!(
            "{}",
            serde_json::to_string_pretty(&not_implemented(&case_id))?
        );
        std::process::exit(2);
    };
    let passed = checks.iter().all(|item| item.passed);
    let payload = json!({
        "schema_version": 1,
        "case_id": case_id,
        "backend": "thouless",
        "backend_version": BACKEND_VERSION,
        "status": if passed { "passed" } else { "failed" },
        "metrics": metrics,
        "checks": checks.iter().map(encoded_check).collect::<Vec<_>>(),
        "elapsed_seconds": started.elapsed().as_secs_f64(),
    });
    println!("{}", serde_json::to_string_pretty(&payload)?);
    if !passed {
        std::process::exit(1);
    }
    Ok(())
}
