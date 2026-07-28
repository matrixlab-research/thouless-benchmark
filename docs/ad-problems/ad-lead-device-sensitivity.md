# Resonant-level device-and-contact sensitivity

**Case:** `ad_lead_device_sensitivity`  
**Motivating requirements:** TBQ-036, TBQ-040  
**AD gates:** AD-G09, AD-G12

## Scientific question

For a resonant level between semi-infinite one-dimensional leads, does the
transmission gradient include every declared device, lead, interface, energy,
and broadening parameter rather than silently treating contacts as constants?

## Benchmark adaptation

A single resonant device level is connected to two differentiable periodic
one-dimensional leads. One direction simultaneously perturbs the device
onsite energy, lead unit cells, lead periodic hoppings, device-lead
couplings, energy, and broadening. This is a complete resonant-tunneling
sensitivity graph, not a claim to model the geometry of the source device.

## Parameters

- Device dimension: `1`.
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

LKM node `gcn_cb7923a88d2246b7` identifies device-lead boundary amplitude as a
control of transport coupling, while `gcn_4f5c36bfc4254a27` provides the
one-dimensional lead self-energy construction. Primary sources:
[Yang et al. (2013)](https://doi.org/10.1063/1.4790863) and
[Polizzi and Datta (2003)](https://doi.org/10.1109/nano.2003.1231709). Raw
retrieval evidence is preserved under
`evidence/lkm/2026-07-28-ad-research-workflows`. Flux and geometry
parameterizations remain separate upstream model rules.
