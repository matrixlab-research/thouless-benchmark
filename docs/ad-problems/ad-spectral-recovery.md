# Multi-observable spectral recovery

**Case:** `ad_spectral_recovery`  
**Motivating requirements:** TBQ-096, TBQ-099  
**AD gates:** AD-G01, AD-G11

## Scientific question

Can one tight-binding Hamiltonian be inferred jointly from band energies and
occupied-subspace information, and does that Hamiltonian predict momenta that
were excluded from the loss?

## Benchmark adaptation

A three-parameter, two-band Hermitian family is sampled at five training
momenta. The loss combines the lower eigenvalue and the occupied projector,
avoiding any dependence on arbitrary eigenvector phases. A thin
backtracking optimizer consumes the native gradient.

## Parameters

- Target parameters: `(0.42, -0.27, 0.19)`.
- Training momenta: `0.17, 0.63, 1.11, 1.72, 2.31`.
- Public validation momenta: `0.39, 0.91, 1.43, 2.03, 2.67`.
- Directional-difference step: `1e-6`.

## Required computation

Evaluate eigenvalue and occupied-projector VJPs, compose their normalized
loss, recover the three parameters, and rebuild eigensystems at excluded
momenta through the ordinary forward solver.

## Expected result

The directional gradient agrees with a central difference, the recovered
parameters agree with the planted values, and excluded-momentum energy and
projector errors remain below the declared tolerance.

## Acceptance

- Directional relative error below `1e-5`.
- Maximum parameter error below `2e-5` with final loss below `1e-10`.
- Maximum excluded-momentum energy and projector error below `2e-5`.

## Evidence and boundary

LKM nodes `gcn_d8da92281f564142` and `gcn_d369960c13104475` motivated joint
spectral fitting and differentiable tight-binding observables. Primary sources:
[Elbaz and Toroker (2024)](https://doi.org/10.1038/s41598-024-62788-4) and
[Vargas-Hernández et al. (2023)](https://doi.org/10.1063/5.0137103).
The visible validation momenta test interpolation but are not isolated
held-out evidence.
