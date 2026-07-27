# Differentiable quantum metric

**Case:** `ad_quantum_metric`  
**Motivating requirements:** TBQ-026, TBQ-029  
**AD gates:** AD-G01, AD-G02, AD-G15

## Scientific question

Are parameter derivatives of an occupied-band quantum-metric objective
correct, covariant under a common basis rotation, and converged with momentum
resolution?

## Benchmark adaptation

A gapped two-band family is evaluated on periodic one-dimensional meshes. The
metric objective is expressed through occupied projectors. The complete model
is rotated by a fixed unitary and independently recomputed on a doubled mesh.

## Parameters

- Coarse mesh: `32` points.
- Refined mesh: `64` points.
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

LKM nodes `gcn_86bcebac99504f4c` and `gcn_43c4ae6e813149c4` motivated
derivative convergence and geometry-sensitive objectives. Primary sources:
[Yang and Wang (2020)](https://arxiv.org/abs/2010.05598) and
[Guo et al. (2017)](https://doi.org/10.1038/s41535-016-0007-2).
This case covers a quantum-metric path, not the full nonlinear-Hall workflow.
