# Rice-Mele spectral and Wannier-sector inference

**Case:** `ad_spectral_recovery`  
**Motivating requirements:** TBQ-096, TBQ-099  
**AD gates:** AD-G01, AD-G11

## Scientific question

Can the staggered onsite energy and two hopping amplitudes of a Rice-Mele
chain be inferred jointly from band energies and occupied-subspace
information, and does the inferred Hamiltonian predict momenta excluded from
the fit?

## Benchmark adaptation

The Bloch Hamiltonian is
`H(k) = delta sigma_z + (t1 + t2 cos(k)) sigma_x + t2 sin(k) sigma_y`.
Five momenta play the role of measured band and Wannier-sector information.
The loss combines the lower eigenvalue and occupied projector, avoiding
arbitrary eigenvector phases. This is a compact adaptation of Rice-Mele
Hamiltonian inference, not a reproduction of a particular experiment or HHG
dataset.

## Parameters

- Energy unit: target intercell hopping `t2 = 1`.
- Target `(delta, t1, t2)`: `(0.35, 0.72, 1.0)`.
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

LKM node `gcn_c52f0ae9e48644a6` reports simultaneous recovery of modified
Rice-Mele band parameters from spectra; `gcn_61fac1b8d03e407d` reports
experimental Wannier-center extraction consistent with a Rice-Mele
tight-binding description. Primary sources:
[Klimkin et al. (2021)](https://doi.org/10.48550/arXiv.2106.08638) and
[Ligthart et al. (2024)](https://doi.org/10.48550/arxiv.2407.14465).
The raw LKM search and reasoning response are preserved under
`evidence/lkm/2026-07-28-ad-research-workflows`. Visible validation momenta
test interpolation but are not isolated held-out evidence.
