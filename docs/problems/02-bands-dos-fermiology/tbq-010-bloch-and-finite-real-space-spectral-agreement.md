---
id: TBQ-010
suite: 02-bands-dos-fermiology
source_requirement: TB-REQ-010
status: executable
acceptance_class: convergence
lkm_snapshot: 2026-07-27
---

# TBQ-010 — Bloch and finite-real-space spectral agreement

## Scientific question

Do periodic momentum-space and large finite real-space calculations describe the same
bulk spectral measure?

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

Compare Bloch DOS with the interior local DOS of increasing open samples using matched
broadening.

## Expected result

Interior local DOS approaches the Bloch DOS while boundary corrections decrease with
system size; state counting remains exact.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `convergence`

Extrapolated difference below 1 percent over the central 90 percent of the band.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Use a held-out lattice shape and boundary termination.

Suite-wide isolation rule: Hold out one lattice family and a topology-changing chemical-potential interval.

## Evidence

- LKM seeds: `gcn_4fb925994ab54a2e`, `gcn_b7cdd564aa464099`, and `gcn_7296c8f60c964c18`.
- Representative source: [Heavy-Fermion Behavior and a Tunable Density Wave in a Novel Vanadium-based Mosaic Lattice](https://doi.org/10.48550/arXiv.2603.08565).
- Source requirement: [`TB-REQ-010`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`executable`: the package-backed evaluator, independent gates, recorded result, and CI are present for kwant: domain_spectral_reliability; pythtb: domain_spectral_reliability; thouless: domain_spectral_reliability. See the machine-readable [backend audit](../../../benchmark/problem_coverage.json). This public result is not held-out validation.
