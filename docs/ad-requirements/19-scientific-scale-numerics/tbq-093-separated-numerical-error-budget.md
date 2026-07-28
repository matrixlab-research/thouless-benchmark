---
id: AD-TBQ-093
tbq_id: TBQ-093
suite: 19-scientific-scale-numerics
ad_role: essential
ad_status: missing_ad_rule
forward_status: implemented
---

# AD-TBQ-093 — Separated numerical error budget

## Scientific anchor

This companion is derived from [TBQ-093 — Separated numerical error budget](../../problems/19-scientific-scale-numerics/tbq-093-separated-numerical-error-budget.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `essential`.

The requested sensitivity is itself a scientific observable or changes the tractability of calibration, control, or inverse design.

## Controls and outputs

Continuous controls:

- physical parameters
- declared numerical tolerances

Scientific outputs:

- separate truncation, iteration, sampling, and AD errors

## Differentiable formulation

Compute derivative error budgets alongside forward error budgets.

No-AD control: Finite-difference after tightening one error source at a time.

## Validity and failure semantics

Error components require independent convergence controls.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/19-scientific-scale-numerics/tbq-093-separated-numerical-error-budget.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of separate truncation, iteration, sampling, and AD errors against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `scale-error-diagnostics` — Scale and error diagnostics
- `identifiability-higher-order` — Identifiability and higher-order products

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `missing_ad_rule`.
- Reason: The forward workflow exists, but reusable native AD support is incomplete for: scale-error-diagnostics, identifiability-higher-order.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/19-scientific-scale-numerics/tbq-093-separated-numerical-error-budget.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
