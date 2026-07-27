# Degeneracy-safe occupied-projector differentiation

**Case:** `ad_degenerate_projector`  
**Motivating requirements:** TBQ-006, TBQ-097  
**AD gate:** AD-G04

## Scientific question

Does spectral differentiation remain gauge safe when individual occupied
states are degenerate but the occupied subspace is separated from the
unoccupied subspace?

## Benchmark adaptation

A four-state model has a two-dimensional occupied sector. The objective is the
distance between occupied projectors, not labeled eigenvectors. The complete
family and target are rotated by the same nontrivial unitary. A separate
two-state exact degeneracy is used as a negative control for an isolated-band
derivative.

## Parameters

- Matrix dimension: `4`.
- Occupied dimension: `2`.
- Subspace gap floor: `1e-4`.
- Directional-difference step: `1e-6`.

## Required computation

Compute a projector-objective JVP, repeat value and gradient evaluation after
a basis transformation, and request an isolated-eigenvalue derivative at
exact degeneracy.

## Expected result

The projector derivative is correct and basis invariant. The isolated-band
request fails explicitly with a gap-too-small condition instead of returning
an unstable gradient.

## Acceptance

- Directional relative error below `1e-5`.
- Basis-rotated value error below `1e-11` and gradient error below `1e-10`.
- Exact-degeneracy isolated-band derivative is rejected.

## Evidence and boundary

LKM node `gcn_fb3f3fe0ae0d411b` motivated explicit eigenderivative semantics.
Primary source:
[Peano, Sapper, and Marquardt (2021)](https://doi.org/10.1103/PhysRevX.11.021052).
This case validates a separated subspace; it does not make a gap-closing
projector differentiable.
