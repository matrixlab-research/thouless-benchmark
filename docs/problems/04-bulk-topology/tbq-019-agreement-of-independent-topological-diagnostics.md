---
id: TBQ-019
suite: 04-bulk-topology
source_requirement: TB-REQ-019
status: executable
acceptance_class: exact
lkm_snapshot: 2026-07-27
---

# TBQ-019 — Agreement of independent topological diagnostics

## Scientific question

Do mathematically independent bulk diagnostics agree in their shared regime and fail
transparently outside it?

## Benchmark adaptation

This is a benchmark adaptation motivated by the cited research. It is not a claim to
reproduce the source paper. The benchmark family is:

Haldane, Qi-Wu-Zhang, Kane-Mele, BBH, and nodal semimetal families with tunable mass,
spin-orbit, and symmetry-breaking terms.

## Parameters

`t` or another explicitly named scale is the reference energy when a row is
dimensionless. A concrete case must freeze exact values, conventions, and random seeds
inside the public or held-out evaluator.

| Name | Meaning | Public development range | Unit |
| --- | --- | --- | --- |
| `m/t` | topological mass control | -3.5 to 3.5 | dimensionless |
| `lambda_SO/t` | intrinsic spin-orbit coupling | 0.02 to 0.20 | dimensionless |
| `lambda_R/t` | Rashba coupling | 0 to 0.15 | dimensionless |
| `delta/t` | symmetry-breaking perturbation | 0 to 0.20 | dimensionless |
| `N_k` | mesh or loop resolution | 16 to 256 | points per direction |

## Required computation

Compare momentum-space Chern or Wilson indices with real-space markers, pumping, or
boundary spectral flow on matched models.

## Expected result

Diagnostics agree in clean gapped limits; diagnostics whose symmetry or gap assumptions
are broken are marked inapplicable rather than coerced.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `exact`

Common-regime integer agreement and a documented inapplicability reason for every
adversarial case.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Hide which assumption is broken in one case.

Suite-wide isolation rule: Hold out a symmetry class, a nearly closed gap, and a basis-gauge family.

## Evidence

- LKM seeds: `gcn_e5dd806871ea4f6f`, `gcn_b761eeec869744ab`, and `gcn_177994dd04734e1e`.
- Representative source: [Topological Insulators from Group Cohomology](https://doi.org/10.1103/physrevx.6.021008).
- Source requirement: [`TB-REQ-019`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`executable`: the package-backed evaluator, independent gates, recorded result, and CI are present for kwant: bulk_haldane_chern_transition, boundary_haldane_ribbon_flow; pythtb: bulk_haldane_chern_transition, boundary_haldane_ribbon_flow; thouless: bulk_haldane_chern_transition, boundary_haldane_ribbon_flow. See the machine-readable [backend audit](../../../benchmark/problem_coverage.json). This public result is not held-out validation.
