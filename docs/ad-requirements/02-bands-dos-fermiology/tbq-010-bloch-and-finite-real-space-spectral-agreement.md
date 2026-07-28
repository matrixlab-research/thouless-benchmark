---
id: AD-TBQ-010
tbq_id: TBQ-010
suite: 02-bands-dos-fermiology
ad_role: helpful
ad_status: missing_ad_rule
forward_status: implemented
---

# AD-TBQ-010 — Bloch and finite-real-space spectral agreement

## Scientific anchor

This companion is derived from [TBQ-010 — Bloch and finite-real-space spectral agreement](../../problems/02-bands-dos-fermiology/tbq-010-bloch-and-finite-real-space-spectral-agreement.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `helpful`.

Differentiation improves attribution or efficiency, while the accepted forward scientific result remains independently obtainable.

## Controls and outputs

Continuous controls:

- shared hopping parameters
- boundary potential

Scientific outputs:

- Bloch-versus-finite spectral discrepancy

## Differentiable formulation

Differentiate the cross-representation discrepancy while holding geometry fixed.

No-AD control: Perturb parameters and rerun both Bloch and finite calculations.

## Validity and failure semantics

System-size and termination choices are discrete convergence variables.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/02-bands-dos-fermiology/tbq-010-bloch-and-finite-real-space-spectral-agreement.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of Bloch-versus-finite spectral discrepancy against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `hermitian-subspaces` — Hermitian spectral-subspace rules
- `boundary-localization` — Boundary and localization composition
- `scale-error-diagnostics` — Scale and error diagnostics

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `missing_ad_rule`.
- Reason: The forward workflow exists, but reusable native AD support is incomplete for: boundary-localization, scale-error-diagnostics.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/02-bands-dos-fermiology/tbq-010-bloch-and-finite-real-space-spectral-agreement.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
