---
id: TBQ-033
suite: 07-disorder-localization
source_requirement: TB-REQ-033
status: proposed
acceptance_class: convergence
lkm_snapshot: 2026-07-27
---

# TBQ-033 — Finite-size scaling of mobility edges

## Scientific question

Where are energy-dependent mobility edges, and how uncertain are they?

## Benchmark adaptation

This is a benchmark adaptation motivated by the cited research. It is not a claim to
reproduce the source paper. The benchmark family is:

Ordinary, spin-orbit, topological, and non-Hermitian two-dimensional lattices with
onsite, hopping, vacancy, and spatially correlated disorder.

## Parameters

`t` or another explicitly named scale is the reference energy when a row is
dimensionless. A concrete case must freeze exact values, conventions, and random seeds
inside the public or held-out evaluator.

| Name | Meaning | Public development range | Unit |
| --- | --- | --- | --- |
| `W/t` | disorder width | 0 to 10 | dimensionless |
| `xi_d/a` | disorder correlation length | 0 to 8 | lattice constants |
| `p_vac` | vacancy probability | 0 to 0.20 | fraction |
| `L/a` | linear size | 24 to 512 | lattice constants |
| `N_seed` | ensemble realizations | 20 to 500 | count |

## Required computation

Perform multi-size crossings or scaling collapse for dimensionless localization or
conductance observables.

## Expected result

A stable critical energy and uncertainty emerge across increasing minimum size; fixed-
threshold estimates alone do not pass.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `convergence`

Critical-energy drift smaller than its reported 95 percent interval on the final size
ladder.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Hide the strongest size and one disorder value.

Suite-wide isolation rule: Hold out disorder distribution, correlation length, lattice geometry, and random seeds.

## Evidence

- LKM seeds: `gcn_1b045590a2ba409d`, `gcn_e09795d6cb3646fe`, and reasoning chain `1066570812665888771_2`.
- Representative source: [Emergent Z2 topological invariant and robust helical edge states in two-dimensional topological metals](https://doi.org/10.1007/s11433-019-1523-6).
- Source requirement: [`TB-REQ-033`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`proposed`: this document specifies a scientific problem but does not claim that any backend currently passes it. No current executable case is asserted to cover this full problem.
