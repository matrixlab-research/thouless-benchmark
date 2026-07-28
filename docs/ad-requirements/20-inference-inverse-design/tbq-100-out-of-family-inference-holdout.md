---
id: AD-TBQ-100
tbq_id: TBQ-100
suite: 20-inference-inverse-design
ad_role: essential
ad_status: ad_native_verified
forward_status: not_applicable
---

# AD-TBQ-100 — Out-of-family inference holdout

## Scientific anchor

This companion is derived from [TBQ-100 — Out-of-family inference holdout](../../problems/20-inference-inverse-design/tbq-100-out-of-family-inference-holdout.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `essential`.

The requested sensitivity is itself a scientific observable or changes the tractability of calibration, control, or inverse design.

## Controls and outputs

Continuous controls:

- shared parameters trained on declared families

Scientific outputs:

- unseen model-family predictions

## Differentiable formulation

Differentiate public training objectives and reserve a hidden family for evaluator-owned forward validation.

No-AD control: Refit public families and evaluate the same hidden family.

## Validity and failure semantics

Family identity and hidden expectations cannot enter gradients.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/20-inference-inverse-design/tbq-100-out-of-family-inference-holdout.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of unseen model-family predictions against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `multiscale-inference` — Multiscale mapping and inference
- `heldout-generality` — Held-out generality
- `identifiability-higher-order` — Identifiability and higher-order products

## Current evidence and gap

- Source forward status for Thouless: `not_applicable`.
- AD companion status: `ad_native_verified`.
- Reason: A current Rust-native AD witness exercises the stated companion formulation; this does not claim completion of the full source TBQ.
- Existing Rust-native witnesses: `ad_robust_kpm_design`
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/20-inference-inverse-design/tbq-100-out-of-family-inference-holdout.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
