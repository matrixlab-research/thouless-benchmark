---
id: AD-TBQ-098
tbq_id: TBQ-098
suite: 20-inference-inverse-design
ad_role: essential
ad_status: ad_native_verified
forward_status: not_applicable
---

# AD-TBQ-098 — Identifiability and predictive calibration

## Scientific anchor

This companion is derived from [TBQ-098 — Identifiability and predictive calibration](../../problems/20-inference-inverse-design/tbq-098-identifiability-and-predictive-calibration.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `essential`.

The requested sensitivity is itself a scientific observable or changes the tractability of calibration, control, or inverse design.

## Controls and outputs

Continuous controls:

- model parameters
- candidate measurement controls

Scientific outputs:

- Jacobian rank
- Fisher spectrum
- predictive uncertainty

## Differentiable formulation

Use Jacobian and Gauss-Newton products to expose nullspaces and design informative observables.

No-AD control: Finite-difference the full sensitivity matrix and refit perturbed data.

## Validity and failure semantics

Rank claims require scale-aware thresholds and held-out prediction.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/20-inference-inverse-design/tbq-098-identifiability-and-predictive-calibration.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of Jacobian rank, Fisher spectrum, predictive uncertainty against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `identifiability-higher-order` — Identifiability and higher-order products
- `multiscale-inference` — Multiscale mapping and inference
- `heldout-generality` — Held-out generality

## Current evidence and gap

- Source forward status for Thouless: `not_applicable`.
- AD companion status: `ad_native_verified`.
- Reason: A current Rust-native AD witness exercises the stated companion formulation; this does not claim completion of the full source TBQ.
- Existing Rust-native witnesses: `ad_identifiability`
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/20-inference-inverse-design/tbq-098-identifiability-and-predictive-calibration.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
