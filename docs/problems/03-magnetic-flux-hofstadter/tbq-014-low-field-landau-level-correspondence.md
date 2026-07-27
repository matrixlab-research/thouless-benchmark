---
id: TBQ-014
suite: 03-magnetic-flux-hofstadter
source_requirement: TB-REQ-014
status: executable
acceptance_class: reference
lkm_snapshot: 2026-07-27
---

# TBQ-014 — Low-field Landau-level correspondence

## Scientific question

Do lattice magnetic levels approach continuum Schrödinger or Dirac Landau levels at low
flux?

## Benchmark adaptation

This is a benchmark adaptation motivated by the cited research. It is not a claim to
reproduce the source paper. The benchmark family is:

Square, triangular, and honeycomb lattices with Peierls phases, including next-neighbour
hoppings and rational flux p/q per primitive plaquette.

## Parameters

`t` or another explicitly named scale is the reference energy when a row is
dimensionless. A concrete case must freeze exact values, conventions, and random seeds
inside the public or held-out evaluator.

| Name | Meaning | Public development range | Unit |
| --- | --- | --- | --- |
| `phi/phi0` | flux per plaquette | p/q with q=3 to 61 | flux quanta |
| `t2/t` | long-range hopping | 0 to 0.25 | dimensionless |
| `q` | magnetic denominator | 3 to 61 | integer |
| `L/a` | real-space linear size | 24 to 256 | lattice constants |
| `eta/t` | spectral broadening | 0.002 to 0.05 | dimensionless |

## Required computation

Track spectral peaks versus flux and fit the expected linear or square-root Landau fan
for square and honeycomb bands.

## Expected result

Level energies approach the correct analytic fan, including zero-mode structure for
Dirac bands, with lattice corrections growing outside the low-flux window.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `reference`

Relative error below 1 percent for the declared lowest-flux subset and monotone
convergence as q increases.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Hide the band type and include weak t2 particle-hole asymmetry.

Suite-wide isolation rule: Hold out flux denominators, a gauge family, and one lattice with non-nearest-neighbour
loops.

## Evidence

- LKM seeds: `gcn_7ad8b68bedaa49b5`, `gcn_75ecf3d114d74c69`, and `gcn_7cc10d3d9e354922`.
- Representative source: [Hofstadter Topology with Real Space Invariants and Reentrant Projective Symmetries](https://doi.org/10.48550/arXiv.2209.10559).
- Source requirement: [`TB-REQ-014`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`executable`: the package-backed evaluator, independent gates, recorded result, and CI are present for thouless: domain_magnetic_convergence. See the machine-readable [backend audit](../../../benchmark/problem_coverage.json). This public result is not held-out validation.
