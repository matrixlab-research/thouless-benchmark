---
id: TBQ-006
suite: 02-bands-dos-fermiology
source_requirement: TB-REQ-006
status: executable
acceptance_class: exact
lkm_snapshot: 2026-07-27
---

# TBQ-006 — Degeneracy-safe band projectors

## Scientific question

Can band structure be compared reliably when individual eigenvectors are undefined
inside degenerate manifolds?

## Benchmark adaptation

This is a benchmark adaptation motivated by the cited research. It is not a claim to
reproduce the source paper. The benchmark family is:

Square, honeycomb, and kagome lattice families with tunable next-neighbour hopping, weak
symmetry breaking, and flat or saddle-point bands.

## Parameters

`t` or another explicitly named scale is the reference energy when a row is
dimensionless. A concrete case must freeze exact values, conventions, and random seeds
inside the public or held-out evaluator.

| Name | Meaning | Public development range | Unit |
| --- | --- | --- | --- |
| `t` | nearest-neighbour energy scale | 1.0 | reference energy |
| `t2/t` | next-neighbour hopping ratio | -0.30 to 0.30 | dimensionless |
| `Delta/t` | gap or sublattice perturbation | 0 to 0.20 | dimensionless |
| `mu/t` | chemical potential | -4.0 to 4.0 | dimensionless |
| `N_k` | linear momentum resolution | 32 to 1024 | points per direction |

## Required computation

Compute eigenvalues and composite projectors around Dirac points, kagome degeneracies,
and weakly split crossings.

## Expected result

Eigenvalue sets agree with analytic values and subspace projectors remain gauge
invariant under random rotations inside each degenerate block.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `exact`

Energy residual below 1e-10 in analytic cases and projector distance below 1e-9.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Hide the degeneracy multiplicity and add a small Delta.

Suite-wide isolation rule: Hold out one lattice family and a topology-changing chemical-potential interval.

## Evidence

- LKM seeds: `gcn_4fb925994ab54a2e`, `gcn_b7cdd564aa464099`, and `gcn_7296c8f60c964c18`.
- Representative source: [Heavy-Fermion Behavior and a Tunable Density Wave in a Novel Vanadium-based Mosaic Lattice](https://doi.org/10.48550/arXiv.2603.08565).
- Source requirement: [`TB-REQ-006`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`executable`: [`domain_spectral_reliability`](../../../benchmark/domain_cases.json)
passes with native Thouless, original PythTB, and original Kwant. The backend-level
witnesses and remaining gaps are recorded in
[`benchmark/problem_coverage.json`](../../../benchmark/problem_coverage.json).
