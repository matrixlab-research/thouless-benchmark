# Topological inverse design with independent invariants

**Case:** `ad_topological_design`  
**Motivating requirements:** TBQ-017, TBQ-030  
**AD gate:** AD-G16

## Scientific question

Can a smooth differentiable objective move a trivial model into a target
topological phase while keeping the discrete topological conclusion outside
the differentiated loss?

## Benchmark adaptation

The QWZ mass starts at `2.65` and is optimized against target occupied
projectors generated at mass `1.0`. The loss uses an offset `7 x 7` momentum
mesh. Initial and final Chern numbers are recomputed with an independent FHS
implementation on a `25 x 25` mesh. A separate mass scan resolves the analytic
gap closing near mass `2`. The differentiable topology-optimization workflow
is adapted to the canonical QWZ model; it is not a reproduction of the source
photonic structure.

## Parameters

- Initial mass: `2.65`.
- Target mass: `1.0`.
- Optimization mesh: `7 x 7`.
- Chern mesh: `25 x 25`.
- Gap scan: masses `1.6` through `2.4` with step `0.01`.

## Required computation

Optimize the smooth projector loss, rebuild the initial and final Hamiltonian
families, compute their discrete Chern numbers, and scan the direct gap between
them.

## Expected result

The optimized mass approaches the target, the independently computed Chern
number changes from trivial to unit magnitude, and the interpolation crosses a
resolved gap closing.

## Acceptance

- Final projector loss below `1e-10`.
- Initial Chern magnitude near zero and final magnitude near one.
- Minimum scanned gap below `1e-6` at a mass within `0.02` of `2`.

## Evidence and boundary

LKM node `gcn_9da619e467814f8e` reports inverse design of topological
insulators through topology optimization; `gcn_d08eb08225d74091` provides a
QWZ phase-transition application. Primary sources:
[Christiansen, Wang, and Sigmund (2019)](https://doi.org/10.1103/PhysRevLett.122.234502)
and [Adak et al. (2026)](https://doi.org/10.48550/arxiv.2606.31604). Raw
retrieval evidence is preserved under
`evidence/lkm/2026-07-28-ad-research-workflows`. No derivative of the integer
Chern number is defined or used.
