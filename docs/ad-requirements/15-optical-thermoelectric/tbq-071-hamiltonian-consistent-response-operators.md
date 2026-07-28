---
id: AD-TBQ-071
tbq_id: TBQ-071
suite: 15-optical-thermoelectric
ad_role: essential
ad_status: missing_ad_rule
forward_status: implemented
---

# AD-TBQ-071 — Hamiltonian-consistent response operators

## Scientific anchor

This companion is derived from [TBQ-071 — Hamiltonian-consistent response operators](../../problems/15-optical-thermoelectric/tbq-071-hamiltonian-consistent-response-operators.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `essential`.

The requested sensitivity is itself a scientific observable or changes the tractability of calibration, control, or inverse design.

## Controls and outputs

Continuous controls:

- Hamiltonian parameters
- vector potential
- chemical potential

Scientific outputs:

- velocity, charge-current, and heat-current matrix elements

## Differentiable formulation

Differentiate operators generated from the same parameterized Hamiltonian and test identities.

No-AD control: Finite-difference Hamiltonian-derived operators independently.

## Validity and failure semantics

Gauge, position, and heat-current conventions must be declared.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/15-optical-thermoelectric/tbq-071-hamiltonian-consistent-response-operators.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of velocity, charge-current, and heat-current matrix elements against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `complex-generalized-basis` — Complex and generalized-basis differentiation
- `topology-geometry-response` — Topology, quantum geometry, and response composition
- `lead-bias-thermodynamics` — Lead, bias, and thermodynamic controls

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `missing_ad_rule`.
- Reason: The forward workflow exists, but reusable native AD support is incomplete for: complex-generalized-basis, topology-geometry-response, lead-bias-thermodynamics.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/15-optical-thermoelectric/tbq-071-hamiltonian-consistent-response-operators.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
