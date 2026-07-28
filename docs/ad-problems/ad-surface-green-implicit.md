# SSH boundary Green-function differentiation

**Case:** `ad_surface_green_implicit`  
**Motivating requirements:** TBQ-023, TBQ-036  
**AD gates:** AD-G02, AD-G09, AD-G10

## Scientific question

Can the retarded boundary Green function of a semi-infinite SSH chain be
differentiated through its fixed-point equation while preserving causality
and avoiding memory growth with forward iterations?

## Benchmark adaptation

A Rice-Mele-regularized SSH lead has intracell hopping `0.65`, intercell
hopping `1.0`, and staggered onsite energy `0.05`. Native JVP and VJP rules
differentiate the converged surface Dyson equation with respect to all three
Hamiltonian controls, energy, and broadening. A looser forward tolerance is a
stability control. This is the minimal boundary-Green workflow used to study
SSH edge contributions, not a quantum-dot many-body calculation.

## Parameters

- Lead-cell dimension: `2`.
- Intracell/intercell hoppings: `0.65/1.0`.
- Staggered onsite energy: `0.05`.
- Evaluation energy: `0.18`.
- Broadening: `0.04`.
- Tight tolerance: `1e-14`.
- Loose tolerance: `1e-11`.
- Directional-difference step: `1e-6`.

## Required computation

Compare the implicit JVP with a central difference, evaluate the JVP/VJP
pairing identity, verify the retarded sign, and compare tight- and
loose-tolerance results and gradients.

## Expected result

The derivative is correct, the adjoint identity closes, all diagonal imaginary
parts have the retarded sign, and modest solver-tolerance changes do not move
the scientific result beyond tolerance.

## Acceptance

- Directional relative error below `1e-5`.
- Adjoint-pairing error below `1e-9`.
- Retarded branch and tolerance-stability checks both pass.

## Evidence and boundary

LKM node `gcn_e2f9ddf1a54846e4` reports the analytic boundary Green function
and edge-state singularity of a semi-infinite SSH lead; `gcn_93f7740861dc4400`
reports the semi-infinite-chain Green function used for the LDOS. Primary
sources:
[Maurer et al. (2022)](https://doi.org/10.48550/arXiv.2112.11814) and
[Dey and Maiti (2022)](https://doi.org/10.48550/arXiv.2205.02326). Raw
retrieval evidence is preserved under
`evidence/lkm/2026-07-28-ad-research-workflows`. The case covers the
surface-lead fixed point, not interacting self-consistency.
