---
id: TBQ-027
suite: 06-quantum-geometry-response
source_requirement: TB-REQ-027
status: executable
acceptance_class: reference
lkm_snapshot: 2026-07-27
---

# TBQ-027 — Competing nonlinear Hall mechanisms

## Scientific question

Is a finite second-order Hall response caused by the Berry-curvature dipole, the
quantum-metric dipole, or both?

## Benchmark adaptation

This is a benchmark adaptation motivated by the cited research. It is not a claim to
reproduce the source paper. The benchmark family is:

A lattice-regularized PT-symmetric deformed Dirac family with independently tunable
mass, inversion breaking, tilt, and rotational-symmetry breaking.

## Parameters

`t` or another explicitly named scale is the reference energy when a row is
dimensionless. A concrete case must freeze exact values, conventions, and random seeds
inside the public or held-out evaluator.

| Name | Meaning | Public development range | Unit |
| --- | --- | --- | --- |
| `v` | Dirac velocity | 1.0 | eV nm |
| `m` | Dirac mass | 0.05 to 0.30 | eV |
| `b` | quadratic regularization | 0.5 to 2.0 | eV nm^2 |
| `d/v` | deformation or tilt ratio | -0.9 to 0.9 | dimensionless |
| `epsilon_F` | Fermi energy | 0.12 to 0.60 | eV |
| `T` | temperature | 1 to 100 | K |

## Required computation

Compute both contributions across d, epsilon_F, and T instead of assuming symmetry
suppression.

## Expected result

At PT-symmetric settings the Berry-curvature-dipole contribution vanishes within
numerical error while the allowed metric term follows deformation-induced Fermi-surface
asymmetry.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `reference`

Suppressed term below 1 percent of the allowed term away from zeros, with both
independently converged.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Break PT weakly in hidden cases so both mechanisms coexist.

Suite-wide isolation rule: Hold out deformation direction, lattice regularization, termination, and one symmetry-
breaking family.

## Evidence

- LKM seeds: `gcn_625da35d83a54c6a`, `gcn_3e90ac9901294fc5`, and reasoning chain `1159462780185608201_8`.
- Representative source: [A Clarification on Quantum-Metric-Induced Nonlinear Transport](https://doi.org/10.48550/arXiv.2508.02088).
- Source requirement: [`TB-REQ-027`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`executable`: the package-backed evaluator, independent gates, recorded result, and CI are present for thouless: domain_quantum_geometry_nonlinear. See the machine-readable [backend audit](../../../benchmark/problem_coverage.json). This public result is not held-out validation.
