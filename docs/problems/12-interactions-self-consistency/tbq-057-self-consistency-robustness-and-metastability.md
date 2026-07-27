---
id: TBQ-057
suite: 12-interactions-self-consistency
source_requirement: TB-REQ-057
status: proposed
acceptance_class: convergence
lkm_snapshot: 2026-07-27
---

# TBQ-057 — Self-consistency robustness and metastability

## Scientific question

Does the converged state depend on numerical mixing or on a genuine metastable basin?

## Benchmark adaptation

This is a benchmark adaptation motivated by the cited research. It is not a claim to
reproduce the source paper. The benchmark family is:

Hubbard, extended-Hubbard, electron-hole, and long-range Hartree models treated by
explicitly declared Hartree-Fock or mean-field decouplings.

## Parameters

`t` or another explicitly named scale is the reference energy when a row is
dimensionless. A concrete case must freeze exact values, conventions, and random seeds
inside the public or held-out evaluator.

| Name | Meaning | Public development range | Unit |
| --- | --- | --- | --- |
| `U/t` | onsite interaction | 0 to 12 | dimensionless |
| `V/t` | intersite interaction | 0 to 5 | dimensionless |
| `n` | filling per cell | 0.25 to 3.75 | electrons |
| `T/t` | temperature | 0 to 0.20 | dimensionless |
| `tol_rho` | density convergence tolerance | 1e-6 to 1e-12 | dimensionless |
| `alpha` | mixing parameter | 0.05 to 0.8 | dimensionless |

## Required computation

Solve from symmetric, random, and ordered seeds using multiple mixing schedules and
compare residuals and free energies.

## Expected result

Equivalent basins converge to the same state; distinct metastable states are retained
and ranked rather than silently discarded.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `convergence`

Density residual below tol_rho and free-energy ordering stable under tighter tolerances.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Hide an initial order with a small basin of attraction.

Suite-wide isolation rule: Hold out filling, interaction ratio, flux, and initial order-parameter family.

## Evidence

- LKM seeds: `gcn_938aef02737f4298`, `gcn_ba2c8f81bdf64292`, and reasoning chain `1229352235507384343_8`.
- Representative source: [The correlated insulators of magic angle twisted bilayer graphene at zero and one quantum of magnetic flux: a tight-binding study](https://doi.org/10.48550/arXiv.2308.01997).
- Source requirement: [`TB-REQ-057`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`proposed`: this document specifies a scientific problem but does not claim that any
backend currently passes it. No current executable case is asserted to cover this full problem.
