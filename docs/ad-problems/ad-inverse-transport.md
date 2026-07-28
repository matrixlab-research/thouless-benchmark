# Double-quantum-dot transmission inference

**Case:** `ad_inverse_transport`  
**Motivating requirements:** TBQ-040, TBQ-099  
**AD gates:** AD-G12, AD-G13

## Scientific question

Can the onsite detuning and interdot hopping of a serial double quantum dot be
inferred from its transmission spectrum and then validated through an
independent non-AD forward solve at excluded energies?

## Benchmark adaptation

A noninteracting serial double quantum dot is coupled to wide-band endpoint
self-energies. The left-dot onsite energy and interdot hopping correction are
unknown. Seven energies define the training trace; five interleaved energies
are excluded from the loss and evaluated through the ordinary open-system
solver after optimization. This is a compact NEGF inverse workflow, not a
fit to a specific experimental trace.

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

LKM node `gcn_a5eb3fecc5264ac5` reports gradient-based Hamiltonian inverse
design against a target transmission, while `gcn_8670a519b2ed4d85` reports a
double-quantum-dot transmission model fitted to first-principles transport.
Primary sources:
[Zhou et al. (2022)](https://doi.org/10.48550/arXiv.2202.05098) and
[Li et al. (2010)](https://doi.org/10.1021/nn101840a). Raw retrieval evidence
is preserved under `evidence/lkm/2026-07-28-ad-research-workflows`. This
compact case tests the end-to-end map, not interacting or large-device
transport.
