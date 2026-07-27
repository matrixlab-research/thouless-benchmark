# Implicit differentiation of a surface Green function

**Case:** `ad_surface_green_implicit`  
**Motivating requirements:** TBQ-023, TBQ-036  
**AD gates:** AD-G02, AD-G09, AD-G10

## Scientific question

Can a converged retarded surface Green function be differentiated through its
fixed-point equation while preserving causality and avoiding memory growth
with forward iterations?

## Benchmark adaptation

A two-orbital periodic lead is evaluated at a complex retarded energy. Native
JVP and VJP rules operate on the converged implicit equation. A looser forward
tolerance is evaluated as a stability control.

## Parameters

- Lead-cell dimension: `2`.
- Broadening: `1e-3`.
- Tight tolerance: `1e-12`.
- Loose tolerance: `1e-9`.
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

LKM nodes `gcn_ce17a6832cec4c76` and `gcn_e8d4a72c26304f59` motivated
implicit fixed-point differentiation and differentiable NEGF. Primary sources:
[Zhang and Chan (2022)](https://doi.org/10.1063/5.0118200) and
[Zhou et al. (2023)](https://doi.org/10.1103/PhysRevB.108.195143).
The case covers the surface-lead fixed point, not future interacting
self-consistency.
