# Many-parameter sparse adjoint scaling

**Case:** `ad_sparse_adjoint_scaling`  
**Motivating requirements:** TBQ-094, TBQ-097  
**AD gates:** AD-G07, AD-G08

## Scientific question

Can a sparse reverse-mode calculation return correct many-parameter gradients
with a solve count that does not grow linearly with the number of parameters?

## Benchmark adaptation

A `128 x 128` sparse Hermitian operator is solved for parameter counts
`8, 32, 64`. A scalar linear functional supplies the cotangent. Native reverse
mode requires one primal and one adjoint system; central parameter-wise
differences require two systems per parameter.

## Parameters

- Sparse dimension: `128`.
- Parameter counts: `8, 32, 64`.
- GMRES relative tolerance: `1e-11`.
- GMRES absolute tolerance: `1e-13`.

## Required computation

Report true primal and adjoint residuals, compare VJP, JVP, and central
directional differences, and record solve counts as the parameter count grows.

## Expected result

Residuals converge, all three derivative routes agree, and the reverse solve
count remains two while the finite-difference baseline grows from 16 to 128
systems.

## Acceptance

- Maximum true residual below `1e-9`.
- Maximum directional relative error below `1e-5`.
- Two native systems for every parameter count and 128 finite-difference
  systems at 64 parameters.

## Evidence and boundary

LKM nodes `gcn_e8d4a72c26304f59` and `gcn_b1a69b35d07f45ad` motivated the
many-parameter adjoint comparison. Primary sources:
[Zhou et al. (2023)](https://doi.org/10.1103/PhysRevB.108.195143) and
[Sen and Mitchell (2023)](https://arxiv.org/abs/2310.14775).
Solve count is the architectural scaling claim; wall time remains descriptive.
