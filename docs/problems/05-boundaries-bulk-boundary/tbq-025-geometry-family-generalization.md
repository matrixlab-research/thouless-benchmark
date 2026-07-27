---
id: TBQ-025
suite: 05-boundaries-bulk-boundary
source_requirement: TB-REQ-025
status: executable
acceptance_class: convergence
lkm_snapshot: 2026-07-27
---

# TBQ-025 — Geometry-family generalization

## Scientific question

Does a boundary workflow transfer across widths, corner angles, aspect ratios, and weak
roughness?

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

Evaluate the same bulk on ribbons, rectangular and polygonal flakes, and rough
boundaries while tracking invariant boundary observables.

## Expected result

Protected observables remain stable within the bulk gap; nonprotected energies vary
continuously with geometry and are reported as such.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `convergence`

No loss of protected branch count before gap closure and converged localization
statistics.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Use unseen polygon topology and correlated edge roughness.

Suite-wide isolation rule: Hold out termination, corner angle, aspect ratio, and a weak boundary-disorder family.

## Evidence

- LKM seeds: `gcn_79c7aedbe338479f`, `gcn_845407cac1554d64`, and reasoning chain `1244230567847788545_3`.
- Representative source: [Topology of honeycomb nanoribbons revisited](https://doi.org/10.48550/arXiv.2603.25497).
- Source requirement: [`TB-REQ-025`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`executable`: the package-backed evaluator, independent gates, recorded result, and CI are present for thouless: domain_boundary_families. See the machine-readable [backend audit](../../../benchmark/problem_coverage.json). This public result is not held-out validation.
