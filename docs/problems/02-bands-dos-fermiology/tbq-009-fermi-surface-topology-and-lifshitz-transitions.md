---
id: TBQ-009
suite: 02-bands-dos-fermiology
source_requirement: TB-REQ-009
status: executable
acceptance_class: reference
lkm_snapshot: 2026-07-27
---

# TBQ-009 — Fermi-surface topology and Lifshitz transitions

## Scientific question

At which chemical potentials do Fermi pockets appear, merge, or change carrier
character?

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

Extract closed Fermi contours or surfaces across mu and track pocket count, enclosed
volume, and electron or hole orientation.

## Expected result

Pocket topology changes only at critical band energies and the enclosed volume satisfies
the appropriate state-counting relation.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `reference`

Critical mu within 2e-3 t and Fermi-volume error below 0.5 percent after refinement.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Hide an anisotropic hopping ratio and one transition with touching pockets.

Suite-wide isolation rule: Hold out one lattice family and a topology-changing chemical-potential interval.

## Evidence

- LKM seeds: `gcn_4fb925994ab54a2e`, `gcn_b7cdd564aa464099`, and `gcn_7296c8f60c964c18`.
- Representative source: [Heavy-Fermion Behavior and a Tunable Density Wave in a Novel Vanadium-based Mosaic Lattice](https://doi.org/10.48550/arXiv.2603.08565).
- Source requirement: [`TB-REQ-009`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`executable`: the package-backed evaluator, independent gates, recorded result, and CI are present for thouless: domain_fermiology. See the machine-readable [backend audit](../../../benchmark/problem_coverage.json). This public result is not held-out validation.
