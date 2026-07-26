use std::env;
use std::error::Error;
use std::time::Instant;

use serde_json::{json, Value};
use thouless::model::{Lattice, ModelBuilder, TightBindingModel};
use thouless::spectrum::hermitian_eigensystem;
use thouless::topology::reduced_polarization_on_loop;
use thouless::transport::{solve_open_system, LeadContact, SurfaceGreenOptions};
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
