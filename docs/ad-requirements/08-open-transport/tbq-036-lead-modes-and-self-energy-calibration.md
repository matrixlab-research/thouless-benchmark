---
id: AD-TBQ-036
tbq_id: TBQ-036
suite: 08-open-transport
ad_role: essential
ad_status: ad_native_verified
forward_status: implemented
---

# AD-TBQ-036 — Lead modes and self-energy calibration

## Scientific anchor

This companion is derived from [TBQ-036 — Lead modes and self-energy calibration](../../problems/08-open-transport/tbq-036-lead-modes-and-self-energy-calibration.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `essential`.

The requested sensitivity is itself a scientific observable or changes the tractability of calibration, control, or inverse design.

## Controls and outputs

Continuous controls:

- lead onsite, hopping, coupling
- energy and broadening

Scientific outputs:

- lead modes
- self-energy
- device spectral response

## Differentiable formulation

Differentiate calibrated lead self-energies and device observables with implicit or resolvent adjoints.

No-AD control: Finite-difference complete lead and device solves.

## Validity and failure semantics

Retarded branch, propagating-mode count, and tolerance must stay stable.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/08-open-transport/tbq-036-lead-modes-and-self-energy-calibration.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of lead modes, self-energy, device spectral response against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `lead-bias-thermodynamics` — Lead, bias, and thermodynamic controls
- `linear-resolvent-adjoints` — Dense and sparse linear-resolvent adjoints
- `implicit-stationarity` — Implicit fixed-point and stationarity rules
- `transport-thermoelectric` — Transport and thermoelectric composition

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `ad_native_verified`.
- Reason: A current Rust-native AD witness exercises the stated companion formulation; this does not claim completion of the full source TBQ.
- Existing Rust-native witnesses: `ad_surface_green_implicit`, `ad_lead_device_sensitivity`
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/08-open-transport/tbq-036-lead-modes-and-self-energy-calibration.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
