---
id: TBQ-083
suite: 17-defects-interfaces
source_requirement: TB-REQ-083
status: proposed
acceptance_class: convergence
lkm_snapshot: 2026-07-27
---

# TBQ-083 — Embedding and supercell agreement

## Scientific question

Do dilute impurity Green-function or T-matrix calculations agree with finite supercells?

## Benchmark adaptation

This is a benchmark adaptation motivated by the cited research. It is not a claim to
reproduce the source paper. The benchmark family is:

Pristine lattice models modified by vacancies, substitutions, adsorbates, missing bonds,
grain boundaries, and heterointerfaces.

## Parameters

`t` or another explicitly named scale is the reference energy when a row is
dimensionless. A concrete case must freeze exact values, conventions, and random seeds
inside the public or held-out evaluator.

| Name | Meaning | Public development range | Unit |
| --- | --- | --- | --- |
| `V_imp/t` | impurity onsite shift | -10 to 10 | dimensionless |
| `delta_t/t` | local hopping change | -1 to 2 | dimensionless |
| `c` | defect concentration | 1e-4 to 0.20 | fraction |
| `d/a` | defect separation | 1 to 128 | lattice constants |
| `L/a` | supercell or device size | 16 to 512 | cells |

## Required computation

Compute bound states, resonances, and local DOS using embedding and increasing
supercells at matched broadening.

## Expected result

Supercell image interactions vanish with size and the extrapolated result matches the
embedding solution.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `convergence`

Final energy or linewidth mismatch below 1 percent after size extrapolation.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Hide a slower-decaying impurity state and two-defect interference.

Suite-wide isolation rule: Hold out defect species, cluster topology, concentration, grain-boundary motif, and
interface registry.

## Evidence

- LKM seeds: `gcn_4e2c18caeab14287`, `gcn_fb0dd68b25b94c98`, and `gcn_1378eeb2ef914577`.
- Representative source: [Hydrogen adatoms on graphene: The role of hybridization and lattice distortion](https://doi.org/10.1103/physrevb.102.195416).
- Source requirement: [`TB-REQ-083`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`proposed`: this document specifies a scientific problem but does not claim that any
backend currently passes it. No current executable case is asserted to cover this full problem.
