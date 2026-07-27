# Complete device-and-lead sensitivity

**Case:** `ad_lead_device_sensitivity`  
**Motivating requirements:** TBQ-036, TBQ-040  
**AD gates:** AD-G09, AD-G12

## Scientific question

Does an open-system transmission gradient include every declared physical
parameter family rather than silently treating the leads or interfaces as
constants?

## Benchmark adaptation

A two-site device is connected to two differentiable periodic leads. One
direction simultaneously perturbs the device Hamiltonian, lead unit cells,
lead periodic hoppings, device-lead couplings, energy, and broadening.

## Parameters

- Device dimension: `2`.
- Leads: `2`.
- Parameter families: device, lead cell, periodic hopping, interface coupling,
  energy, and broadening.
- Directional-difference step: `1e-6`.

## Required computation

Evaluate the full open-system VJP, contract every gradient block with the
corresponding direction, compare their sum with a central difference of the
complete forward system, and retain the periodic-lead implicit contribution.

## Expected result

The full directional derivative agrees with finite differences and every
declared physical block contributes to the sensitivity.

## Acceptance

- Full-graph directional relative error below `1e-5`.
- Device, lead-cell, periodic-hopping, interface, and spectral contributions
  are finite and nonzero in the constructed case.
- The periodic-lead implicit path satisfies its dedicated check.

## Evidence and boundary

LKM nodes `gcn_7508395e785e4a5e`, `gcn_599a15903a2a40bc`, and
`gcn_e8d4a72c26304f59` motivated microscopic transport sensitivities and native
reverse-mode support. Primary sources:
[Hirasaki, Inui, and Saitoh (2024)](https://doi.org/10.1103/PhysRevB.110.214201)
and [Zhou et al. (2023)](https://doi.org/10.1103/PhysRevB.108.195143).
Flux and geometry parameterizations remain separate upstream model rules.
