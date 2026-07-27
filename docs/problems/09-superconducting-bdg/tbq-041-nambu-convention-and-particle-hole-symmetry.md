---
id: TBQ-041
suite: 09-superconducting-bdg
source_requirement: TB-REQ-041
status: executable
acceptance_class: exact
lkm_snapshot: 2026-07-27
---

# TBQ-041 — Nambu convention and particle-hole symmetry

## Scientific question

Does the BdG construction implement the declared Nambu ordering without double counting
observables?

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

Assemble normal and pairing blocks, apply the particle-hole operator, and compare
positive and negative spectra and densities.

## Expected result

C H(k) C^-1 equals -H(-k), eigenvalues pair as plus or minus E, and physical density
uses the declared Nambu factor.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `exact`

Symmetry residual below 1e-11 and paired-energy error below 1e-10.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Hide Nambu ordering and include spinful pairing.

Suite-wide isolation rule: Hold out pairing symmetry, junction dimensions, contact transparency, and disorder
family.

## Evidence

- LKM seeds: `gcn_c034d6be7a204627`, `gcn_b9f13a7153b94880`, and `gcn_0623154216a444ed`.
- Representative source: [Quench dynamics of the Josephson current in a topological Josephson junction](https://doi.org/10.1103/PhysRevB.97.035311).
- Source requirement: [`TB-REQ-041`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`executable`: [`domain_bdg_majorana`](../../../benchmark/domain_cases.json) passes
with native Thouless, original PythTB, and original Kwant. The backend-level
witnesses and remaining gaps are recorded in
[`benchmark/problem_coverage.json`](../../../benchmark/problem_coverage.json).
