---
id: TBQ-042
suite: 09-superconducting-bdg
source_requirement: TB-REQ-042
status: executable
acceptance_class: reference
lkm_snapshot: 2026-07-27
---

# TBQ-042 — Phase-resolved Andreev spectrum and Josephson current

## Scientific question

Do short-junction Andreev levels and current follow transparency and phase?

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

Sweep phi and transparency, compute subgap levels, and differentiate free energy or use
the current operator.

## Expected result

Levels follow E=Delta sqrt(1-T sin^2(phi/2)) in the short single-channel limit and
current is its thermodynamic derivative.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `reference`

Level and current error below 0.5 percent away from level crossings.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Hide T, finite temperature, and a second channel.

Suite-wide isolation rule: Hold out pairing symmetry, junction dimensions, contact transparency, and disorder
family.

## Evidence

- LKM seeds: `gcn_c034d6be7a204627`, `gcn_b9f13a7153b94880`, and `gcn_0623154216a444ed`.
- Representative source: [Quench dynamics of the Josephson current in a topological Josephson junction](https://doi.org/10.1103/PhysRevB.97.035311).
- Source requirement: [`TB-REQ-042`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`executable`: [`domain_bdg_majorana`](../../../benchmark/domain_cases.json) passes
with native Thouless, original PythTB, and original Kwant. The backend-level
witnesses and remaining gaps are recorded in
[`benchmark/problem_coverage.json`](../../../benchmark/problem_coverage.json).
