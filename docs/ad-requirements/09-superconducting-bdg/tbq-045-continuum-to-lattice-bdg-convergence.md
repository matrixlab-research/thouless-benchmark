---
id: AD-TBQ-045
tbq_id: TBQ-045
suite: 09-superconducting-bdg
ad_role: helpful
ad_status: missing_ad_rule
forward_status: implemented
---

# AD-TBQ-045 — Continuum-to-lattice BdG convergence

## Scientific anchor

This companion is derived from [TBQ-045 — Continuum-to-lattice BdG convergence](../../problems/09-superconducting-bdg/tbq-045-continuum-to-lattice-bdg-convergence.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `helpful`.

Differentiation improves attribution or efficiency, while the accepted forward scientific result remains independently obtainable.

## Controls and outputs

Continuous controls:

- continuum coefficients
- lattice spacing
- pairing parameters

Scientific outputs:

- continuum-lattice spectral and current discrepancy

## Differentiable formulation

Differentiate matched continuous parameters at each fixed discretization and perform a forward convergence sequence.

No-AD control: Finite-difference both representations over several lattice spacings.

## Validity and failure semantics

The lattice spacing is a convergence variable, not an optimizable physical control.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/09-superconducting-bdg/tbq-045-continuum-to-lattice-bdg-convergence.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of continuum-lattice spectral and current discrepancy against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `complex-generalized-basis` — Complex and generalized-basis differentiation
- `multiscale-inference` — Multiscale mapping and inference
- `scale-error-diagnostics` — Scale and error diagnostics

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `missing_ad_rule`.
- Reason: The forward workflow exists, but reusable native AD support is incomplete for: complex-generalized-basis, multiscale-inference, scale-error-diagnostics.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/09-superconducting-bdg/tbq-045-continuum-to-lattice-bdg-convergence.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
