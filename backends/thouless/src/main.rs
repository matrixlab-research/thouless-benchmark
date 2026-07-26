use std::env;
use std::error::Error;
use std::time::Instant;

use serde_json::{json, Value};
use thouless::model::{Lattice, ModelBuilder, TightBindingModel};
use thouless::spectrum::hermitian_eigensystem;
use thouless::topology::{
    chern_numbers_on_uniform_grid, plaquette_flux, reduced_polarization_on_loop, wilson_line_phase,
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
        "bulk_qwz_phase_diagram" => Some(bulk_qwz_phase_diagram()?),
        "bulk_weyl_chirality" => Some(bulk_weyl_chirality()?),
        "bulk_nodal_line_berry_phase" => Some(bulk_nodal_line_berry_phase()?),
        "bulk_wannier_interpolation" => Some(bulk_wannier_interpolation()?),
        "boundary_ssh_edge_localization" => Some(boundary_ssh_edge_localization()?),
        "transport_ballistic_chain" => Some(transport_ballistic_chain()?),
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
