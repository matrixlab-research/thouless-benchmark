---
id: AD-TBQ-040
tbq_id: TBQ-040
suite: 08-open-transport
ad_role: essential
ad_status: ad_native_verified
forward_status: implemented
---

# AD-TBQ-040 — Generalization across contact families

## Scientific anchor

This companion is derived from [TBQ-040 — Generalization across contact families](../../problems/08-open-transport/tbq-040-generalization-across-contact-families.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `essential`.

The requested sensitivity is itself a scientific observable or changes the tractability of calibration, control, or inverse design.

## Controls and outputs

Continuous controls:

- contact couplings
- lead parameters
- device parameters

Scientific outputs:

- held-out contact-family transmission and local observables

## Differentiable formulation

Optimize a contact-robust loss and validate on excluded lead and interface families.

No-AD control: Derivative-free fitting followed by full held-out forward calculations.

## Validity and failure semantics

Contact topology and lead family remain external discrete variables.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/08-open-transport/tbq-040-generalization-across-contact-families.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of held-out contact-family transmission and local observables against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `lead-bias-thermodynamics` — Lead, bias, and thermodynamic controls
- `transport-thermoelectric` — Transport and thermoelectric composition
- `multiscale-inference` — Multiscale mapping and inference
- `heldout-generality` — Held-out generality

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `ad_native_verified`.
- Reason: A current Rust-native AD witness exercises the stated companion formulation; this does not claim completion of the full source TBQ.
- Existing Rust-native witnesses: `ad_inverse_transport`, `ad_lead_device_sensitivity`
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/08-open-transport/tbq-040-generalization-across-contact-families.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
