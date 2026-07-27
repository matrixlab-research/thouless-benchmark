---
id: TBQ-029
suite: 06-quantum-geometry-response
source_requirement: TB-REQ-029
status: proposed
acceptance_class: convergence
lkm_snapshot: 2026-07-27
---

# TBQ-029 — Fermi-surface and derivative convergence

## Scientific question

Are sharp nonlinear-response features robust to k-mesh, derivative scheme, temperature,
and broadening?

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

Compare analytic, automatic, and finite-difference derivatives over nested meshes and
temperature or smearing ladders.

## Expected result

Response curves converge to the same limit away from genuine singularities; uncertainty
expands near band edges rather than being hidden.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `convergence`

Two independent derivative routes agree within 2 percent on the converged interval.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Hide a Fermi energy close to a band edge and a lower temperature.

Suite-wide isolation rule: Hold out deformation direction, lattice regularization, termination, and one symmetry-
breaking family.

## Evidence

- LKM seeds: `gcn_625da35d83a54c6a`, `gcn_3e90ac9901294fc5`, and reasoning chain `1159462780185608201_8`.
- Representative source: [A Clarification on Quantum-Metric-Induced Nonlinear Transport](https://doi.org/10.48550/arXiv.2508.02088).
- Source requirement: [`TB-REQ-029`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`proposed`: this document specifies a scientific problem but does not claim that any backend currently passes it. No current executable case is asserted to cover this full problem.
