# Inverse transmission design

**Case:** `ad_inverse_transport`  
**Motivating requirements:** TBQ-040, TBQ-099  
**AD gates:** AD-G12, AD-G13

## Scientific question

Can microscopic device parameters be inferred from a transmission spectrum and
then validated through an independent non-AD forward solve at excluded
energies?

## Benchmark adaptation

A two-site device with fixed endpoint self-energies has two unknown
Hamiltonian parameters. Seven energies define the training trace. Five
interleaved energies are excluded from the loss and evaluated through the
ordinary open-system solver after optimization.

## Parameters

- Target parameters: `(0.23, -0.19)`.
- Training energies: `-0.72, -0.48, -0.21, 0, 0.24, 0.51, 0.77`.
- Public validation energies: `-0.61, -0.34, 0.13, 0.39, 0.68`.
- Lead broadenings: `0.72` and `0.61`.

## Required computation

Compose transmission VJPs into a normalized trace loss, validate one
directional derivative, optimize both parameters, rebuild the device, and
evaluate excluded energies through the independent forward path.

## Expected result

The gradient agrees with finite differences, the training trace is recovered,
and the excluded-energy transmission RMS remains small.

## Acceptance

- Directional relative error below `1e-5`.
- Final trace loss below `1e-10`.
- Excluded-energy forward RMS below `2e-5`.

## Evidence and boundary

LKM nodes `gcn_7508395e785e4a5e`, `gcn_e8d4a72c26304f59`, and
`gcn_b1a69b35d07f45ad` motivated differentiable transport and
many-parameter inverse design. Primary sources:
[Hirasaki, Inui, and Saitoh (2024)](https://arxiv.org/abs/2409.02009),
[Zhou et al. (2023)](https://doi.org/10.1103/PhysRevB.108.195143), and
[Sen and Mitchell (2023)](https://arxiv.org/abs/2310.14775).
This compact case tests the end-to-end map, not large-device scaling.
