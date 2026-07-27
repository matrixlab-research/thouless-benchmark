---
id: TBQ-024
suite: 05-boundaries-bulk-boundary
source_requirement: TB-REQ-024
status: proposed
acceptance_class: exact
lkm_snapshot: 2026-07-27
---

# TBQ-024 — Conditional bulk-boundary correspondence

## Scientific question

When do boundary states follow universally from the bulk, and when may termination
remove, split, or mask them?

## Benchmark adaptation

This is a benchmark adaptation motivated by the cited research. It is not a claim to
reproduce the source paper. The benchmark family is:

SSH, graphene, Haldane, and BBH bulk Hamiltonians cut into ribbons, flakes, corners, and
semi-infinite surfaces with multiple terminations.

## Parameters

`t` or another explicitly named scale is the reference energy when a row is
dimensionless. A concrete case must freeze exact values, conventions, and random seeds
inside the public or held-out evaluator.

| Name | Meaning | Public development range | Unit |
| --- | --- | --- | --- |
| `L/a` | finite length or width | 8 to 128 | cells |
| `r` | weak-to-strong hopping ratio | 0.2 to 1.4 | dimensionless |
| `m/t` | bulk or boundary mass | -0.5 to 0.5 | dimensionless |
| `W_edge/t` | boundary disorder amplitude | 0 to 0.50 | dimensionless |
| `eta/t` | surface spectral broadening | 0.002 to 0.05 | dimensionless |

## Required computation

Test topological and trivial bulks under symmetry-preserving and symmetry-breaking
boundaries and report the hypotheses of each correspondence.

## Expected result

Protected chiral flow survives valid perturbations; termination-dependent or obstructed
modes may move or disappear without being falsely labelled a bulk failure.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `exact`

Correct branch count in protected cases and explicit hypothesis failure in every
nonuniversal case.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Hide whether the boundary preserves the protecting symmetry.

Suite-wide isolation rule: Hold out termination, corner angle, aspect ratio, and a weak boundary-disorder family.

## Evidence

- LKM seeds: `gcn_79c7aedbe338479f`, `gcn_845407cac1554d64`, and reasoning chain `1244230567847788545_3`.
- Representative source: [Topology of honeycomb nanoribbons revisited](https://doi.org/10.48550/arXiv.2603.25497).
- Source requirement: [`TB-REQ-024`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`proposed`: this document specifies a scientific problem but does not claim that any
backend currently passes it. [`boundary_bbh_corner_modes`](../../../benchmark/cases.json) is related, but does not by itself establish full coverage of this specification.
