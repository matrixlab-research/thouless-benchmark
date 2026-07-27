---
id: TBQ-043
suite: 09-superconducting-bdg
source_requirement: TB-REQ-043
status: executable
acceptance_class: reference
lkm_snapshot: 2026-07-27
---

# TBQ-043 — Majorana versus trivial near-zero modes

## Scientific question

Can the workflow distinguish separated Majorana modes from accidental Andreev states
near zero energy?

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

Combine a bulk invariant, particle-hole self-conjugacy, spatial profiles, end
separation, and finite-size splitting.

## Expected result

Topological wires show paired end-localized Majoranas with exponentially small
splitting; trivial smooth-potential controls may approach zero but fail at least one
criterion.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `reference`

Correct classification across the public phase diagram and localization-length fit
within 5 percent.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Hide a trivial near-zero control and an inhomogeneous topological wire.

Suite-wide isolation rule: Hold out pairing symmetry, junction dimensions, contact transparency, and disorder
family.

## Evidence

- LKM seeds: `gcn_c034d6be7a204627`, `gcn_b9f13a7153b94880`, and `gcn_0623154216a444ed`.
- Representative source: [Quench dynamics of the Josephson current in a topological Josephson junction](https://doi.org/10.1103/PhysRevB.97.035311).
- Source requirement: [`TB-REQ-043`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`executable`: the package-backed evaluator, independent gates, recorded result, and CI are present for kwant: domain_bdg_majorana; pythtb: domain_bdg_majorana; thouless: domain_bdg_majorana. See the machine-readable [backend audit](../../../benchmark/problem_coverage.json). This public result is not held-out validation.
