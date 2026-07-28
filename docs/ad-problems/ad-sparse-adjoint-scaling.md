# Many-parameter Anderson sparse adjoint

**Case:** `ad_sparse_adjoint_scaling`  
**Motivating requirements:** TBQ-094, TBQ-097  
**AD gates:** AD-G07, AD-G08

## Scientific question

Can a sparse reverse-mode calculation return correct gradients of an Anderson
chain resolvent with respect to many grouped onsite gates, while keeping the
number of linear systems independent of parameter count?

## Benchmark adaptation

A `128`-site nearest-neighbor Anderson resolvent contains deterministic onsite
disorder of amplitude `0.11` and hopping `-0.22`. Sites are grouped into
`8, 32, 64` independently controlled onsite gates. A scalar response
functional supplies the cotangent. Native reverse mode requires one primal
and one adjoint system; central parameter-wise differences require two
systems per parameter. The benchmark tests the differentiable sparse
workflow, not localization critical exponents.

## Parameters

- Sparse dimension: `128`.
- Onsite disorder amplitude: `0.11`.
- Nearest-neighbor hopping: `-0.22`.
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

LKM node `gcn_e70f4e09b2734747` provides an Anderson-localization
finite-size-scaling workflow, while `gcn_a72c49f810f54d63` supplies the
implicit Green-function gradient used in differentiable transport. Primary
sources:
[Fleury and Waintal (2008)](https://doi.org/10.1103/PhysRevLett.100.076602)
and [Zhou et al. (2022)](https://doi.org/10.48550/arXiv.2202.05098). Raw
retrieval evidence is preserved under
`evidence/lkm/2026-07-28-ad-research-workflows`. Solve count is the
architectural scaling claim; wall time remains descriptive.
