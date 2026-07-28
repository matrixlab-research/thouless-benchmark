---
id: AD-TBQ-007
tbq_id: TBQ-007
suite: 02-bands-dos-fermiology
ad_role: helpful
ad_status: implementable_unverified
forward_status: implemented
---

# AD-TBQ-007 — Density-of-states state counting

## Scientific anchor

This companion is derived from [TBQ-007 — Density-of-states state counting](../../problems/02-bands-dos-fermiology/tbq-007-density-of-states-state-counting.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `helpful`.

Differentiation improves attribution or efficiency, while the accepted forward scientific result remains independently obtainable.

## Controls and outputs

Continuous controls:

- hopping and onsite parameters
- chemical potential

Scientific outputs:

- DOS moments
- state-counting residual

## Differentiable formulation

Differentiate normalized DOS moments and integrated state count.

No-AD control: Execute a full DOS calculation for every perturbation.

## Validity and failure semantics

Broadening and polynomial order must be frozen and converged.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/02-bands-dos-fermiology/tbq-007-density-of-states-state-counting.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of DOS moments, state-counting residual against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `physical-parameter-spaces` — Physical parameter spaces
- `kpm-stochastic-adjoints` — KPM and stochastic adjoints
- `scale-error-diagnostics` — Scale and error diagnostics

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `implementable_unverified`.
- Reason: All specialized primitives needed by this companion already exist; the remaining work is orchestration, a frozen oracle, a recorded result, and CI.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/02-bands-dos-fermiology/tbq-007-density-of-states-state-counting.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
