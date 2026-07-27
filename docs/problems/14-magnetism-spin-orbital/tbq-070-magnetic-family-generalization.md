---
id: TBQ-070
suite: 14-magnetism-spin-orbital
source_requirement: TB-REQ-070
status: proposed
acceptance_class: reference
lkm_snapshot: 2026-07-27
---

# TBQ-070 — Magnetic-family generalization

## Scientific question

Do response diagnostics transfer across ferro-, antiferro-, spiral, and skyrmion
textures?

## Benchmark adaptation

This is a benchmark adaptation motivated by the cited research. It is not a claim to
reproduce the source paper. The benchmark family is:

Spinful square or triangular lattices coupled to ferromagnetic, antiferromagnetic,
spiral, domain-wall, and skyrmion exchange textures.

## Parameters

`t` or another explicitly named scale is the reference energy when a row is
dimensionless. A concrete case must freeze exact values, conventions, and random seeds
inside the public or held-out evaluator.

| Name | Meaning | Public development range | Unit |
| --- | --- | --- | --- |
| `J/t` | exchange coupling | 0.1 to 10 | dimensionless |
| `lambda_SO/t` | spin-orbit coupling | 0 to 1 | dimensionless |
| `R_sk/a` | skyrmion or texture radius | 2 to 64 | lattice constants |
| `q` | spiral wavevector | 0 to pi | inverse lattice constant |
| `E_F/t` | Fermi energy | -4 to 4 | dimensionless |

## Required computation

Apply the same observable definitions and convergence protocol across texture families
and contacts.

## Expected result

Symmetry-allowed responses transfer; symmetry-forbidden components remain zero and
texture-specific features are identified.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `reference`

Correct tensor selection rules and hidden reference agreement within 5 percent.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Use unseen chirality, boundary, and weak disorder.

Suite-wide isolation rule: Hold out texture topology, chirality, sublattice structure, spin-orbit strength, and
contacts.

## Evidence

- LKM seeds: `gcn_24b0aa946f4346b7`, `gcn_a572d7be0648498e`, and `gcn_9897d0405aaa497b`.
- Representative source: [Topological orbital Hall effect caused by skyrmions and antiferromagnetic skyrmions](https://doi.org/10.48550/arXiv.2410.00820).
- Source requirement: [`TB-REQ-070`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`proposed`: this document specifies a scientific problem but does not claim that any
backend currently passes it. No current executable case is asserted to cover this full problem.
