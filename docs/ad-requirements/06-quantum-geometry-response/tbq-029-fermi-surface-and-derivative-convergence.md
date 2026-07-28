---
id: AD-TBQ-029
tbq_id: TBQ-029
suite: 06-quantum-geometry-response
ad_role: essential
ad_status: ad_native_verified
forward_status: missing_capability
---

# AD-TBQ-029 — Fermi-surface and derivative convergence

## Scientific anchor

This companion is derived from [TBQ-029 — Fermi-surface and derivative convergence](../../problems/06-quantum-geometry-response/tbq-029-fermi-surface-and-derivative-convergence.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `essential`.

The requested sensitivity is itself a scientific observable or changes the tractability of calibration, control, or inverse design.

## Controls and outputs

Continuous controls:

- chemical potential
- temperature
- momentum
- model parameters

Scientific outputs:

- Fermi-surface response and parameter derivatives

## Differentiable formulation

Differentiate smooth Fermi-surface quadrature and demonstrate joint value-gradient convergence.

No-AD control: Finite-difference after repeated mesh and smearing sweeps.

## Validity and failure semantics

Zero-temperature discontinuities require a converged regularization.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/06-quantum-geometry-response/tbq-029-fermi-surface-and-derivative-convergence.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of Fermi-surface response and parameter derivatives against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `topology-geometry-response` — Topology, quantum geometry, and response composition
- `scale-error-diagnostics` — Scale and error diagnostics
- `nonsmooth-failure-semantics` — Nonsmooth and discrete failure semantics

## Current evidence and gap

- Source forward status for Thouless: `missing_capability`.
- AD companion status: `ad_native_verified`.
- Reason: A current Rust-native AD witness exercises the stated companion formulation; this does not claim completion of the full source TBQ.
- Existing Rust-native witnesses: `ad_quantum_metric`
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/06-quantum-geometry-response/tbq-029-fermi-surface-and-derivative-convergence.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
