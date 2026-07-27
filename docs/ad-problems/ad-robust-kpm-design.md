# Robust checkpointed KPM design

**Case:** `ad_robust_kpm_design`  
**Motivating requirements:** TBQ-094, TBQ-100  
**AD gates:** AD-G08, AD-G17

## Scientific question

Can a stochastic sparse KPM objective be optimized across disorder
realizations with a checked gradient, bounded reverse memory, and improvement
on public unseen seeds?

## Benchmark adaptation

Eight deterministic disorder seeds define the training ensemble for a
four-parameter `96 x 96` sparse family. Five different public seeds are
excluded from optimization. A 36-moment recurrence uses checkpoint interval
six. The objective is deliberately expressed through general sparse operators,
probes, and coefficients rather than seed-specific branches.

## Parameters

- Sparse dimension: `96`.
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

LKM nodes `gcn_0e8306bb16b74c91` and `gcn_041957b9b14b4f04` motivated robust
design under fabrication disorder. Primary sources:
[Ryczko, Darancet, and Tamblyn (2020)](https://doi.org/10.1021/acs.jpcc.0c06903)
and [Molina (2020)](https://doi.org/10.1016/j.physleta.2020.126704).
Public unseen seeds are development evidence only; the isolated AD-G18
evaluator remains outside this repository.
