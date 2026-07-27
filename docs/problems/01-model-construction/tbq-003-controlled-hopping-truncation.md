---
id: TBQ-003
suite: 01-model-construction
source_requirement: TB-REQ-003
status: executable
acceptance_class: convergence
lkm_snapshot: 2026-07-27
---

# TBQ-003 — Controlled hopping truncation

## Scientific question

How much scientific accuracy is lost when long-range hopping terms are truncated?

## Benchmark adaptation

This is a benchmark adaptation motivated by the cited research. It is not a claim to
reproduce the source paper. The benchmark family is:

A localized-orbital Hamiltonian family obtained from an analytic reference or a Wannier-
like real-space representation. Both orthogonal and generalized eigenproblems are
included.

## Parameters

`t` or another explicitly named scale is the reference energy when a row is
dimensionless. A concrete case must freeze exact values, conventions, and random seeds
inside the public or held-out evaluator.

| Name | Meaning | Public development range | Unit |
| --- | --- | --- | --- |
| `N_orb` | orbitals per cell | 2, 4, 6, 10 | count |
| `R_cut` | retained hopping shells | 1 to 8 | lattice shells |
| `s_max` | largest off-diagonal overlap | 0 to 0.20 | dimensionless |
| `lambda_SO` | spin-orbit scale | 0 to 0.30 | eV |
| `epsilon_win` | validated energy window about the Fermi level | 0.5 to 4.0 | eV |

## Required computation

Sweep R_cut or a matrix-element threshold and recompute bands, projectors, density of
states, and one response observable.

## Expected result

Errors decrease toward the untruncated reference; the benchmark exposes any observable
whose convergence is slower than band-energy convergence.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `convergence`

Publish an error-versus-nonzero-count curve and identify the smallest model meeting the
case-specific observable tolerance.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Hold out a material family with more slowly decaying hoppings.

Suite-wide isolation rule: Hold out an orbital basis size, a structural or strain family, and an energy window; do
not form the hidden set by resampling fitted k-points.

## Evidence

- LKM seeds: `gcn_c63bb5a9ee604e87`, `gcn_7236e40f8a0f46dd`, and reasoning chain `867765819981955534_1`.
- Representative source: [Construction of optimized tight-binding models using ab initio Hamiltonian: Application to monolayer 2H-transition metal dichalcogenides](https://doi.org/10.48550/arXiv.2402.11969).
- Source requirement: [`TB-REQ-003`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`executable`: the package-backed evaluator, independent gates, recorded result, and CI are present for thouless: domain_model_fidelity. See the machine-readable [backend audit](../../../benchmark/problem_coverage.json). This public result is not held-out validation.
