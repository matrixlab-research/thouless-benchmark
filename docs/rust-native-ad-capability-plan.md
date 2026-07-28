# Rust-native AD capability plan derived from 100 scientific questions

## Decision

Thouless should expose a small set of composable Rust-native differentiation capabilities, not one API per benchmark. The dependency direction is fixed:

`scientific question → differentiable workflow → reusable capability → Rust API`

The 100 source TBQs remain the scientific anchors. The companion catalog records where AD is essential, helpful, conditional, or not central, and it preserves a no-AD control for every question. The current overall status is **Incomplete**.

## What the complete catalog changes

The former ten-workflow set proves selected spectral, projector, implicit surface-Green-function, transport, sparse-adjoint, and KPM paths. It does not cover the full parameter boundary exposed by the 100 questions. The catalog adds explicit demand for:

- energy derivatives for thermopower and finite-bias current derivatives for differential conductance;
- geometry, strain, magnetic-field, disorder, drive, lead, temperature, and bias controls;
- non-Hermitian, time-dependent, interacting, multiscale, and scientific-scale reverse rules;
- typed invalid-gradient semantics at gap closings, branch changes, graph changes, channel openings, and solver switches;
- evaluator-owned held-out validation, plus derivative bindings as a
  cross-language delivery boundary rather than a scientific observable.

## Minimal capability waist

| Capability | TBQ demand | Current maturity | Required reusable behavior |
|---|---:|---|---|
| `physical-parameter-spaces` | 13 | `partial` | Typed continuous controls with bounds, units, reparameterizations, and explicit separation from discrete model choices. |
| `complex-generalized-basis` | 13 | `partial` | Rules for complex Hamiltonians, overlap matrices, constrained Hermiticity, and basis-covariant pullbacks. |
| `geometry-strain-defects` | 18 | `missing` | Differentiable coordinates, strain fields, hopping laws, and fixed-topology defect or interface parameterizations. |
| `gauge-fields-drives` | 6 | `missing` | Gauge-covariant rules for Peierls phases, magnetic fields, time origin, amplitudes, frequencies, and waveform controls. |
| `disorder-ensembles` | 5 | `missing` | Seeded reparameterization, common-random-number gradients, and distributional objectives with uncertainty estimates. |
| `lead-bias-thermodynamics` | 5 | `partial` | Physical controls for leads, contacts, chemical potentials, temperature, energy, and finite-bias boundary conditions. |
| `hermitian-subspaces` | 23 | `available` | Gauge-safe eigensystem and projector derivatives, including degenerate occupied subspaces and generalized eigenproblems. |
| `nonhermitian-subspaces` | 5 | `missing` | Biorthogonal, Schur-subspace, exceptional-point, and pseudospectral differentiation with conditioning diagnostics. |
| `linear-resolvent-adjoints` | 14 | `available` | Reusable JVP and VJP rules for dense or iterative linear solves, resolvents, self-energies, and preconditioned sparse operators. |
| `implicit-stationarity` | 6 | `partial` | Adjoints for converged fixed points, self-consistency, stationarity conditions, and reusable factorization state. |
| `time-floquet-adjoints` | 6 | `missing` | Checkpointed propagation and rules for propagators, Floquet operators, Sambe systems, and time-dependent observables. |
| `kpm-stochastic-adjoints` | 8 | `available` | Checkpointed reverse rules for Chebyshev recurrences, stochastic trace estimators, and common-random-number objectives. |
| `topology-geometry-response` | 21 | `partial` | Differentiable smooth proxies and tensor pipelines while keeping discrete invariants as independent forward validation. |
| `boundary-localization` | 16 | `partial` | Differentiable surface, finite-geometry, local-marker, localization, and finite-size-scaling observables. |
| `transport-thermoelectric` | 8 | `partial` | Adjoints for scattering and NEGF observables, including energy and bias derivatives, finite-temperature moments, and noise. |
| `interaction-self-consistency` | 5 | `missing` | Forward and reverse support for mean-field maps, competing stationary solutions, thermodynamic potentials, and metastability. |
| `multiscale-inference` | 26 | `partial` | Differentiable representation maps, constrained multi-observable losses, calibration, and independent forward validation. |
| `nonsmooth-failure-semantics` | 33 | `partial` | Typed handling of gap closings, branch changes, connectivity changes, solver switches, rank changes, and invalid gradients. |
| `scale-error-diagnostics` | 42 | `partial` | Derivative error budgets, conditioning, convergence histories, memory accounting, checkpoint policies, and sparse-only guarantees. |
| `identifiability-higher-order` | 7 | `partial` | Jacobian products, Fisher or Gauss-Newton operators, Hessian-vector products, nullspaces, and experiment-design diagnostics. |
| `derivative-bindings` | 0 | `missing` | Stable Rust-native derivative entry points exposed consistently to Python and Julia without reimplementing scientific kernels. |
| `heldout-generality` | 16 | `missing` | Evaluator-owned unseen models, hidden expected results, and anti-overfitting checks separate from public CI. |

Demand counts are requirement incidence, not priorities or claims of independent kernels. A single robust primitive may satisfy many companions. `derivative-bindings` has zero direct TBQ incidence because it is a delivery requirement shared by all bindings, not a domain scientific requirement.

## Native Rust interface boundary

The minimum stable interface should be organized around four concepts:

1. `ParameterSpace`: typed physical controls, constraints, units, and tangent projection.
2. `DifferentiableProblem`: a forward value plus explicit JVP and VJP products over scientific outputs; dense Jacobians remain optional.
3. `SolveContext`: reusable primal state, factorization or preconditioner state, convergence history, and checkpoint policy.
4. `DerivativeReport`: value and derivative error budgets, conditioning, branch validity, sparsity and memory evidence, and failure reason.

Existing ChainRules-style rule traits can implement primitive JVP and VJP behavior behind this boundary. Domain modules compose those primitives; Python and Julia bindings expose the same native operations rather than maintaining separate differentiation engines.

## Ordering by logical dependency

This is one complete design, not a reduced staged deliverable:

1. close the physical parameter boundary and typed failure semantics;
2. complete primitive spectral, linear, implicit, non-Hermitian, time, and stochastic rules;
3. compose them into geometry, topology, localization, transport, interactions, and multiscale workflows;
4. add scale diagnostics, derivative bindings, and held-out evaluation.

## Evidence required to close a gap

A capability is not complete because an API name exists. Closure requires:

- an accepted forward observable under the source TBQ's convergence conditions;
- an independent derivative oracle or adjoint identity;
- invariance, covariance, conservation, or failure-semantics checks where applicable;
- an accuracy-matched no-AD baseline;
- a recorded public result and CI witness;
- evaluator-owned unseen models for any generality claim.

Unresolved scientific-forward gaps remain in [https://github.com/matrixlab-research/thouless-benchmark/issues/6](https://github.com/matrixlab-research/thouless-benchmark/issues/6); native AD and rule gaps remain in [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13).
