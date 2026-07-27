---
id: TBQ-017
suite: 04-bulk-topology
source_requirement: TB-REQ-017
status: proposed
acceptance_class: exact
lkm_snapshot: 2026-07-27
---

# TBQ-017 — Topological phase-boundary localization

## Scientific question

Can parameter sweeps locate the gap closings where bulk indices change?

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

Scan and root-find the direct gap of QWZ and Haldane families around analytic critical
masses and compute indices on both sides.

## Expected result

Critical parameters match analytic values, and index changes occur only across a
resolved gap closing.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `exact`

Critical mass error below 1e-4 t and no false index transition in a gapped interval.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Hide one critical point and add weak anisotropy.

Suite-wide isolation rule: Hold out a symmetry class, a nearly closed gap, and a basis-gauge family.

## Evidence

- LKM seeds: `gcn_e5dd806871ea4f6f`, `gcn_b761eeec869744ab`, and `gcn_177994dd04734e1e`.
- Representative source: [Topological Insulators from Group Cohomology](https://doi.org/10.1103/physrevx.6.021008).
- Source requirement: [`TB-REQ-017`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`proposed`: this document specifies a scientific problem but does not claim that any
backend currently passes it. [`bulk_qwz_phase_diagram`](../../../benchmark/cases.json) is related, but does not by itself establish full coverage of this specification.
