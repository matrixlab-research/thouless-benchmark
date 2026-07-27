---
id: TBQ-076
suite: 16-aperiodic-amorphous-fractal
source_requirement: TB-REQ-076
status: proposed
acceptance_class: exact
lkm_snapshot: 2026-07-27
---

# TBQ-076 — Translation-free geometric construction

## Scientific question

Can a model preserve arbitrary coordinates, connectivity, tile types, and local
environments without inventing a primitive cell?

## Benchmark adaptation

This is a benchmark adaptation motivated by the cited research. It is not a claim to
reproduce the source paper. The benchmark family is:

Penrose and Ammann-Beenker approximants, amorphous point sets, and hierarchical or
fractal graphs with periodic lattices as controls.

## Parameters

`t` or another explicitly named scale is the reference energy when a row is
dimensionless. A concrete case must freeze exact values, conventions, and random seeds
inside the public or held-out evaluator.

| Name | Meaning | Public development range | Unit |
| --- | --- | --- | --- |
| `g` | approximant or graph generation | 2 to 10 | integer |
| `N` | number of sites | 1e2 to 1e7 | count |
| `r_c/a` | geometric connection cutoff | 1.0 to 2.5 | dimensionless |
| `sigma_r/a` | amorphous positional disorder | 0 to 0.5 | dimensionless |
| `phi/phi0` | tile or loop flux | 0 to 1 | flux quanta |

## Required computation

Build known approximants and graphs, count vertices and edges, and verify geometric
adjacency and boundary extraction.

## Expected result

Counts and local coordination match construction rules and remain invariant under rigid
motions and vertex relabelling.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `exact`

Exact graph isomorphism invariants and coordinate residual below 1e-12 a.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Hide a phason-flipped approximant and relabel all vertices.

Suite-wide isolation rule: Hold out tiling, phason configuration, amorphous seed, fractal rule, and boundary shape.

## Evidence

- LKM seeds: `gcn_dfde823db8fb4c7d`, `gcn_9e58c6a7cc274d8e`, and `gcn_6ccd073ef5034202`.
- Representative source: [Higher-dimensional Hofstadter butterfly on Penrose lattice](https://doi.org/10.48550/arXiv.2207.03028).
- Source requirement: [`TB-REQ-076`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`proposed`: this document specifies a scientific problem but does not claim that any
backend currently passes it. No current executable case is asserted to cover this full problem.
