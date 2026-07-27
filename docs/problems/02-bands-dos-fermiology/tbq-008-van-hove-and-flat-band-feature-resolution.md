---
id: TBQ-008
suite: 02-bands-dos-fermiology
source_requirement: TB-REQ-008
status: proposed
acceptance_class: reference
lkm_snapshot: 2026-07-27
---

# TBQ-008 — Van Hove and flat-band feature resolution

## Scientific question

Can the calculation locate and classify the spectral singularities that enhance
correlation effects?

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

Find stationary points, Hessian signatures, flat-band bandwidths, and corresponding DOS
peaks as t2 is varied.

## Expected result

Ordinary saddle points have mixed Hessian signature, higher-order points show a
vanishing quadratic direction, and flat-band bandwidth follows the analytic perturbative
scale.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `reference`

Feature energy within 2e-3 t and classification stable under a factor-of-two mesh
refinement.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Hide a higher-order saddle and a weakly dispersive flat band.

Suite-wide isolation rule: Hold out one lattice family and a topology-changing chemical-potential interval.

## Evidence

- LKM seeds: `gcn_4fb925994ab54a2e`, `gcn_b7cdd564aa464099`, and `gcn_7296c8f60c964c18`.
- Representative source: [Heavy-Fermion Behavior and a Tunable Density Wave in a Novel Vanadium-based Mosaic Lattice](https://doi.org/10.48550/arXiv.2603.08565).
- Source requirement: [`TB-REQ-008`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`proposed`: this document specifies a scientific problem but does not claim that any
backend currently passes it. [`bulk_kagome_soc_chern`](../../../benchmark/cases.json) is related, but does not by itself establish full coverage of this specification.
