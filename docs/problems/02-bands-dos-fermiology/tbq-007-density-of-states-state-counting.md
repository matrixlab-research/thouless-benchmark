---
id: TBQ-007
suite: 02-bands-dos-fermiology
source_requirement: TB-REQ-007
status: executable
acceptance_class: convergence
lkm_snapshot: 2026-07-27
---

# TBQ-007 — Density-of-states state counting

## Scientific question

Does the computed total and projected density of states conserve the number of one-
particle states?

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

Evaluate DOS using mesh integration and a real-space polynomial or spectral formulation
over a broadening ladder.

## Expected result

The integrated total DOS equals N_orb per cell; projected DOS sums to the total and
analytic band-edge features occur at correct energies.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `convergence`

State-count error below 1e-4 after convergence and agreement between formulations within
their estimated broadening error.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Use a held-out flat-band lattice and a nonuniform orbital projection.

Suite-wide isolation rule: Hold out one lattice family and a topology-changing chemical-potential interval.

## Evidence

- LKM seeds: `gcn_4fb925994ab54a2e`, `gcn_b7cdd564aa464099`, and `gcn_7296c8f60c964c18`.
- Representative source: [Heavy-Fermion Behavior and a Tunable Density Wave in a Novel Vanadium-based Mosaic Lattice](https://doi.org/10.48550/arXiv.2603.08565).
- Source requirement: [`TB-REQ-007`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`executable`: the package-backed evaluator, independent gates, recorded result, and CI are present for kwant: domain_spectral_reliability; pythtb: domain_spectral_reliability; thouless: domain_spectral_reliability. See the machine-readable [backend audit](../../../benchmark/problem_coverage.json). This public result is not held-out validation.
