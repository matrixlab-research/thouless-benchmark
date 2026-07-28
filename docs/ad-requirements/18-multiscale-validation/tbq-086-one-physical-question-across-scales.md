---
id: AD-TBQ-086
tbq_id: TBQ-086
suite: 18-multiscale-validation
ad_role: helpful
ad_status: implementable_unverified
forward_status: implemented
---

# AD-TBQ-086 — One physical question across scales

## Scientific anchor

This companion is derived from [TBQ-086 — One physical question across scales](../../problems/18-multiscale-validation/tbq-086-one-physical-question-across-scales.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `helpful`.

Differentiation improves attribution or efficiency, while the accepted forward scientific result remains independently obtainable.

## Controls and outputs

Continuous controls:

- shared physical parameters across representations

Scientific outputs:

- common gauge-invariant observables

## Differentiable formulation

Differentiate one scientific objective through each scale-specific representation.

No-AD control: Finite-difference every representation independently.

## Validity and failure semantics

Each representation retains its own declared approximation.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/18-multiscale-validation/tbq-086-one-physical-question-across-scales.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of common gauge-invariant observables against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `multiscale-inference` — Multiscale mapping and inference
- `complex-generalized-basis` — Complex and generalized-basis differentiation
- `scale-error-diagnostics` — Scale and error diagnostics

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `implementable_unverified`.
- Reason: All specialized primitives needed by this companion already exist; the remaining work is orchestration, a frozen oracle, a recorded result, and CI.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/18-multiscale-validation/tbq-086-one-physical-question-across-scales.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
