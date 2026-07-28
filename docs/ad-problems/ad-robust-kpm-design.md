# Robust KPM design of a disordered SSH chain

**Case:** `ad_robust_kpm_design`  
**Motivating requirements:** TBQ-094, TBQ-100  
**AD gates:** AD-G08, AD-G17

## Scientific question

Can a sparse KPM objective for a bond-disordered SSH chain be optimized across
disorder realizations with a checked gradient, bounded reverse memory, and
improvement on public unseen disorder seeds?

## Benchmark adaptation

The `96`-site chain has clean alternating hoppings `0.16/0.24` and chiral
bond disorder of amplitude `0.018`. Four regional bond controls are optimized
over eight deterministic disorder seeds; five public seeds are excluded from
optimization. A 36-moment recurrence uses checkpoint interval six. This is a
compact disordered-SSH KPM adaptation, not a reproduction of the source
coaxial-cable sample or its finite-size scaling.

## Parameters

- Sparse dimension: `96`.
- Clean intracell/intercell hoppings: `0.16/0.24`.
- Bond-disorder amplitude: `0.018`.
- Parameters: `4`.
- KPM moments: `36`.
- Checkpoint interval: `6`.
- Training seeds: `11, 23, 37, 53, 71, 89, 107, 131`.
- Public validation seeds: `17, 41, 67, 97, 127`.

## Required computation

Validate an ensemble directional derivative, optimize the mean training
objective, evaluate the frozen result on public unseen seeds, and report
operator applications and peak stored recurrence vectors.

## Expected result

Training and public-validation losses both decrease substantially. The native
checkpointed reverse path uses fewer operator applications than a central
parameter-wise finite-difference baseline and stores fewer than all 36
recurrence vectors.

## Acceptance

- Directional relative error below `2e-5`.
- Training and public-validation losses each decrease by at least 80%.
- Native operator applications below the 2,240-operation finite-difference
  baseline and peak stored vectors below 36.

## Evidence and boundary

LKM node `gcn_dd35cab4703b4260` reports finite-size and binary-disorder effects
at a random chiral SSH transition, while `gcn_58636b14cc7d4109` provides a KPM
disorder-averaged density-of-states workflow. Primary sources:
[Whittaker, McCarthy, and Duan (2023)](https://doi.org/10.48550/arXiv.2311.11040)
and [Terletska et al. (2025)](https://doi.org/10.48550/arxiv.2505.00806). Raw
retrieval evidence is preserved under
`evidence/lkm/2026-07-28-ad-research-workflows`. Public unseen seeds are
development evidence only; the isolated AD-G18 evaluator remains outside this
repository.
