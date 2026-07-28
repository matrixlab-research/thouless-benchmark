# BHZ Kramers-subspace differentiation

**Case:** `ad_degenerate_projector`  
**Motivating requirements:** TBQ-006, TBQ-097  
**AD gate:** AD-G04

## Scientific question

Does differentiation of a spin-degenerate BHZ occupied sector remain gauge
safe when the Kramers partners are individually non-unique but the occupied
subspace is separated from the unoccupied sector?

## Benchmark adaptation

A four-state BHZ orbital block contains identical spin copies and hence a
two-dimensional occupied Kramers sector. Two orbital-mixing controls preserve
the internal degeneracy. The objective is the distance between occupied
projectors, not labeled eigenvectors. A common unitary mixes the occupied
partners, while a separate exact degeneracy is a negative control for an
isolated-band derivative. This is a minimal BHZ subspace adaptation, not a
full quantum-spin-Hall edge calculation.

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

LKM node `gcn_995145fb96d14e92` identifies the BHZ quantum-spin-Hall
gauge/topology constraint, while `gcn_00da49cbfa6c47d6` motivates
wavefunction-sector projection in degenerate bands. Primary sources:
[Li, Sheng, and Xing (2012)](https://doi.org/10.48550/arXiv.1201.1690) and
[Zhang et al. (2014)](https://doi.org/10.1038/nphys2933). Raw retrieval
evidence is preserved under
`evidence/lkm/2026-07-28-ad-research-workflows`. This case validates a
separated subspace; it does not make a gap-closing projector differentiable.
