# Rice-Mele quantum-metric sensitivity

**Case:** `ad_quantum_metric`  
**Motivating requirements:** TBQ-026, TBQ-029  
**AD gates:** AD-G01, AD-G02, AD-G15

## Scientific question

Are parameter derivatives of an occupied-band quantum-metric objective
correct, covariant under a common basis rotation, and converged with momentum
resolution?

## Benchmark adaptation

The Rice-Mele Hamiltonian uses fixed average hopping and two controls:
staggered onsite energy and dimerization. Its occupied-band quantum metric is
evaluated on periodic one-dimensional meshes through projectors. The complete
model is rotated by a fixed unitary and independently recomputed on a doubled
mesh. This is a geometry-sensitivity adaptation, not a reproduction of a
material piezoelectric coefficient.

## Parameters

- Coarse mesh: `64` points.
- Refined mesh: `128` points.
- Fixed average hopping: `1`.
- Parameters: `(0.31, -0.18)`.
- Direction: `(0.27, -0.41)`.

## Required computation

Evaluate the metric value and native JVP on both meshes, compare the coarse JVP
with a central difference, and compare value and gradient before and after the
basis rotation.

## Expected result

The derivative agrees with finite differences, the rotated and unrotated
objectives agree, and both the value and derivative stabilize under mesh
refinement.

## Acceptance

- Directional relative error below `1e-5`.
- Basis-covariance error below `1e-10`.
- Coarse-to-refined value and derivative changes below the declared
  convergence tolerance.

## Evidence and boundary

LKM node `gcn_e264632a5a0e4780` reports closed-form Rice-Mele polarization and
piezoelectric response, while `gcn_61fac1b8d03e407d` reports experimental
Wannier centers consistent with the model. Primary sources:
[Villani et al. (2023)](https://doi.org/10.48550/arXiv.2308.16070) and
[Ligthart et al. (2024)](https://doi.org/10.48550/arxiv.2407.14465). Raw
retrieval evidence is preserved under
`evidence/lkm/2026-07-28-ad-research-workflows`. This case covers a
quantum-metric path, not the full polarization or piezoelectric workflow.
