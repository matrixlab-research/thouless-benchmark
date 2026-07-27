---
id: TBQ-045
suite: 09-superconducting-bdg
source_requirement: TB-REQ-045
status: executable
acceptance_class: convergence
lkm_snapshot: 2026-07-27
---

# TBQ-045 — Continuum-to-lattice BdG convergence

## Scientific question

Does a lattice discretization reproduce the continuum superconducting model without
lattice artifacts?

## Benchmark adaptation

This is a benchmark adaptation motivated by the cited research. It is not a claim to
reproduce the source paper. The benchmark family is:

Kitaev chains, s-wave normal-superconductor junctions, and spin-orbit nanowires in a
declared Nambu basis with phase bias and disorder.

## Parameters

`t` or another explicitly named scale is the reference energy when a row is
dimensionless. A concrete case must freeze exact values, conventions, and random seeds
inside the public or held-out evaluator.

| Name | Meaning | Public development range | Unit |
| --- | --- | --- | --- |
| `mu/t` | chemical potential | -3 to 3 | dimensionless |
| `Delta/t` | pairing amplitude | 0.05 to 0.50 | dimensionless |
| `V_Z/t` | Zeeman energy | 0 to 2 | dimensionless |
| `phi` | superconducting phase difference | 0 to 4 pi | radian |
| `W/t` | onsite disorder | 0 to 4 | dimensionless |
| `L/a` | junction or wire length | 20 to 512 | sites |

## Required computation

Refine lattice spacing at fixed physical length, mass, spin-orbit, pairing, and Zeeman
scales.

## Expected result

Low-energy spectra, invariant boundaries, and localization lengths converge while
spurious high-momentum states move outside the target window.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `convergence`

Second-order or declared convergence and below 1 percent low-energy error at final
spacing.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Hide a sharper interface and smaller coherence length.

Suite-wide isolation rule: Hold out pairing symmetry, junction dimensions, contact transparency, and disorder
family.

## Evidence

- LKM seeds: `gcn_c034d6be7a204627`, `gcn_b9f13a7153b94880`, and `gcn_0623154216a444ed`.
- Representative source: [Quench dynamics of the Josephson current in a topological Josephson junction](https://doi.org/10.1103/PhysRevB.97.035311).
- Source requirement: [`TB-REQ-045`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`executable`: the package-backed evaluator, independent gates, recorded result, and CI are present for thouless: domain_bdg_discretization. See the machine-readable [backend audit](../../../benchmark/problem_coverage.json). This public result is not held-out validation.
