# Whole-problem backend capability assessment

This is the human-readable view of
[`benchmark/problem_coverage.json`](../benchmark/problem_coverage.json).
The assessment unit is one complete scientific problem, not an API name.

## Status definitions

- **Implemented:** a package-backed evaluator, independent gate, recorded
  result, and CI witness every required claim.
- **Implementable, unverified:** source evidence shows that every specialized
  primitive already exists; only end-to-end orchestration and verification
  remain. This is not counted as coverage.
- **Missing capability:** at least one reusable solver or representation is
  absent, so writing test glue alone cannot complete the workflow.
- **Not applicable:** the core workflow lies outside the package's declared
  scope. A missing API by itself is not enough for this label.

Shared model definitions, parameter loops, statistics, and gauge-invariant
postprocessing are allowed only after the named backend constructs the
Hamiltonian. A specialized solver cannot be hidden in NumPy or SciPy and
then attributed to the backend. A documented dependency counts only when
the package exposes the required representation as its normal workflow,
and the dependency is named in the evidence.

The documented parameter range is part of each assessment. A dense
toy-size route does not establish a sparse or production-scale capability.

## Summary

| Backend | Implemented | Implementable, unverified | Missing capability | Not applicable | Verified coverage |
| --- | ---: | ---: | ---: | ---: | ---: |
| thouless | 67 | 0 | 18 | 15 | 67% |
| pythtb | 12 | 16 | 42 | 30 | 12% |
| kwant | 13 | 46 | 21 | 20 | 13% |

## Package evidence boundary

| Backend | Pinned version | Source | Declared scope |
| --- | --- | --- | --- |
| thouless | git 0d87773278183ddc7c254438dccbda1face04fb2 | [pinned source](https://github.com/matrixlab-research/thouless/tree/0d87773278183ddc7c254438dccbda1face04fb2) | Rust-native tight binding, topology, intrinsic response, sparse spectral methods, steady-state quantum transport, and dense non-Hermitian eigensystems. |
| pythtb | 2.0.0; source commit 0f3bb0b8588101cafbdf428c70fb43c9302fe7cf | [pinned source](https://github.com/pythtb/pythtb/tree/0f3bb0b8588101cafbdf428c70fb43c9302fe7cf) | Construction and analysis of static Hermitian tight-binding models for topological band theory. |
| kwant | 1.5.0; source commit de315f171270d62ee2412c4084260c912cc4d58f | [pinned source](https://gitlab.kwant-project.org/kwant/kwant/-/tree/de315f171270d62ee2412c4084260c912cc4d58f) | Static Hermitian tight-binding systems with a strong focus on sparse steady-state quantum transport. |

The machine-readable audit records the exact package API evidence used
for every required capability. The principal inspected sources were the
pinned Thouless Rust source and coverage manifests, the installed
PythTB 2.0 package source and metadata, and the installed Kwant 1.5
package source and metadata.

## All questions

| ID | Scientific problem | Thouless | PythTB | Kwant | Witnesses |
| --- | --- | --- | --- | --- | --- |
| TBQ-001 | [Basis and generalized-Hermiticity fidelity](problems/01-model-construction/tbq-001-basis-and-generalized-hermiticity-fidelity.md) | implemented | missing capability | missing capability | `domain_model_fidelity` |
| TBQ-002 | [Energy-window and subspace fidelity](problems/01-model-construction/tbq-002-energy-window-and-subspace-fidelity.md) | implemented | missing capability | missing capability | `domain_model_fidelity` |
| TBQ-003 | [Controlled hopping truncation](problems/01-model-construction/tbq-003-controlled-hopping-truncation.md) | implemented | missing capability | missing capability | `domain_model_fidelity` |
| TBQ-004 | [Symmetry preservation and negative controls](problems/01-model-construction/tbq-004-symmetry-preservation-and-negative-controls.md) | implemented | missing capability | missing capability | `domain_model_fidelity` |
| TBQ-005 | [Transfer beyond fitted structures](problems/01-model-construction/tbq-005-transfer-beyond-fitted-structures.md) | implemented | missing capability | missing capability | `domain_model_fidelity` |
| TBQ-006 | [Degeneracy-safe band projectors](problems/02-bands-dos-fermiology/tbq-006-degeneracy-safe-band-projectors.md) | implemented | implemented | implemented | `domain_spectral_reliability` |
| TBQ-007 | [Density-of-states state counting](problems/02-bands-dos-fermiology/tbq-007-density-of-states-state-counting.md) | implemented | implemented | implemented | `domain_spectral_reliability` |
| TBQ-008 | [Van Hove and flat-band feature resolution](problems/02-bands-dos-fermiology/tbq-008-van-hove-and-flat-band-feature-resolution.md) | implemented | implementable, unverified | implementable, unverified | `domain_fermiology` |
| TBQ-009 | [Fermi-surface topology and Lifshitz transitions](problems/02-bands-dos-fermiology/tbq-009-fermi-surface-topology-and-lifshitz-transitions.md) | implemented | implementable, unverified | implementable, unverified | `domain_fermiology` |
| TBQ-010 | [Bloch and finite-real-space spectral agreement](problems/02-bands-dos-fermiology/tbq-010-bloch-and-finite-real-space-spectral-agreement.md) | implemented | implemented | implemented | `domain_spectral_reliability` |
| TBQ-011 | [Gauge-covariant Peierls substitution](problems/03-magnetic-flux-hofstadter/tbq-011-gauge-covariant-peierls-substitution.md) | implemented | implemented | implemented | `domain_magnetic_hofstadter` |
| TBQ-012 | [Magnetic translation and minimal unit cell](problems/03-magnetic-flux-hofstadter/tbq-012-magnetic-translation-and-minimal-unit-cell.md) | implemented | implemented | implemented | `domain_magnetic_hofstadter` |
| TBQ-013 | [Hofstadter gap topology and Streda consistency](problems/03-magnetic-flux-hofstadter/tbq-013-hofstadter-gap-topology-and-streda-consistency.md) | implemented | implemented | implemented | `domain_magnetic_hofstadter` |
| TBQ-014 | [Low-field Landau-level correspondence](problems/03-magnetic-flux-hofstadter/tbq-014-low-field-landau-level-correspondence.md) | implemented | implementable, unverified | implementable, unverified | `domain_magnetic_convergence` |
| TBQ-015 | [Rational-approximant convergence](problems/03-magnetic-flux-hofstadter/tbq-015-rational-approximant-convergence.md) | implemented | implementable, unverified | implementable, unverified | `domain_magnetic_convergence` |
| TBQ-016 | [Gauge-invariant bulk indices](problems/04-bulk-topology/tbq-016-gauge-invariant-bulk-indices.md) | implemented | implementable, unverified | implementable, unverified | `domain_bulk_topology_controls` |
| TBQ-017 | [Topological phase-boundary localization](problems/04-bulk-topology/tbq-017-topological-phase-boundary-localization.md) | implemented | implementable, unverified | implementable, unverified | `domain_bulk_topology_controls` |
| TBQ-018 | [Degeneracy-safe Wilson and nested Wilson flow](problems/04-bulk-topology/tbq-018-degeneracy-safe-wilson-and-nested-wilson-flow.md) | implemented | implementable, unverified | implementable, unverified | `domain_bulk_topology_controls` |
| TBQ-019 | [Agreement of independent topological diagnostics](problems/04-bulk-topology/tbq-019-agreement-of-independent-topological-diagnostics.md) | implemented | implemented | implemented | `boundary_haldane_ribbon_flow`, `bulk_haldane_chern_transition` |
| TBQ-020 | [Trivial, nearly gapless, and basis-adversarial controls](problems/04-bulk-topology/tbq-020-trivial-nearly-gapless-and-basis-adversarial-controls.md) | implemented | implementable, unverified | implementable, unverified | `domain_bulk_topology_controls` |
| TBQ-021 | [Termination families from one bulk model](problems/05-boundaries-bulk-boundary/tbq-021-termination-families-from-one-bulk-model.md) | implemented | implementable, unverified | implementable, unverified | `domain_boundary_families` |
| TBQ-022 | [Boundary-state localization and finite-size splitting](problems/05-boundaries-bulk-boundary/tbq-022-boundary-state-localization-and-finite-size-splitting.md) | implemented | implemented | implemented | `boundary_ssh_edge_localization` |
| TBQ-023 | [Finite-spectrum and surface-Green-function agreement](problems/05-boundaries-bulk-boundary/tbq-023-finite-spectrum-and-surface-green-function-agreement.md) | implemented | missing capability | implementable, unverified | `domain_boundary_families` |
| TBQ-024 | [Conditional bulk-boundary correspondence](problems/05-boundaries-bulk-boundary/tbq-024-conditional-bulk-boundary-correspondence.md) | implemented | implementable, unverified | implementable, unverified | `domain_boundary_families` |
| TBQ-025 | [Geometry-family generalization](problems/05-boundaries-bulk-boundary/tbq-025-geometry-family-generalization.md) | implemented | implementable, unverified | implementable, unverified | `domain_boundary_families` |
| TBQ-026 | [Gauge covariance of geometric tensors](problems/06-quantum-geometry-response/tbq-026-gauge-covariance-of-geometric-tensors.md) | implemented | implementable, unverified | missing capability | `domain_quantum_geometry_nonlinear` |
| TBQ-027 | [Competing nonlinear Hall mechanisms](problems/06-quantum-geometry-response/tbq-027-competing-nonlinear-hall-mechanisms.md) | implemented | implementable, unverified | implementable, unverified | `domain_quantum_geometry_nonlinear` |
| TBQ-028 | [Symmetry-forbidden nonlinear tensor components](problems/06-quantum-geometry-response/tbq-028-symmetry-forbidden-nonlinear-tensor-components.md) | implemented | implementable, unverified | implementable, unverified | `domain_quantum_geometry_nonlinear` |
| TBQ-029 | [Fermi-surface and derivative convergence](problems/06-quantum-geometry-response/tbq-029-fermi-surface-and-derivative-convergence.md) | missing capability | missing capability | missing capability | none |
| TBQ-030 | [Zero-Chern nonlinear bulk-boundary workflow](problems/06-quantum-geometry-response/tbq-030-zero-chern-nonlinear-bulk-boundary-workflow.md) | implemented | missing capability | implementable, unverified | `domain_quantum_geometry_nonlinear` |
| TBQ-031 | [Reproducible disorder ensembles](problems/07-disorder-localization/tbq-031-reproducible-disorder-ensembles.md) | implemented | missing capability | missing capability | `domain_disorder_reproducibility` |
| TBQ-032 | [Cross-observable localization diagnosis](problems/07-disorder-localization/tbq-032-cross-observable-localization-diagnosis.md) | missing capability | missing capability | missing capability | none |
| TBQ-033 | [Finite-size scaling of mobility edges](problems/07-disorder-localization/tbq-033-finite-size-scaling-of-mobility-edges.md) | missing capability | missing capability | missing capability | none |
| TBQ-034 | [Topological mobility gap](problems/07-disorder-localization/tbq-034-topological-mobility-gap.md) | missing capability | missing capability | missing capability | none |
| TBQ-035 | [Statistical generalization across disorder families](problems/07-disorder-localization/tbq-035-statistical-generalization-across-disorder-families.md) | missing capability | missing capability | missing capability | none |
| TBQ-036 | [Lead modes and self-energy calibration](problems/08-open-transport/tbq-036-lead-modes-and-self-energy-calibration.md) | implemented | not applicable | implemented | `domain_lead_calibration` |
| TBQ-037 | [Scattering conservation and local continuity](problems/08-open-transport/tbq-037-scattering-conservation-and-local-continuity.md) | implemented | not applicable | implementable, unverified | `domain_transport_consistency` |
| TBQ-038 | [Transmission, local density, and finite-temperature noise](problems/08-open-transport/tbq-038-transmission-local-density-and-finite-temperature-noise.md) | implemented | not applicable | implementable, unverified | `domain_transport_consistency` |
| TBQ-039 | [Numerical stability for long evanescent devices](problems/08-open-transport/tbq-039-numerical-stability-for-long-evanescent-devices.md) | implemented | not applicable | implementable, unverified | `domain_transport_consistency` |
| TBQ-040 | [Generalization across contact families](problems/08-open-transport/tbq-040-generalization-across-contact-families.md) | implemented | not applicable | implementable, unverified | `domain_transport_consistency` |
| TBQ-041 | [Nambu convention and particle-hole symmetry](problems/09-superconducting-bdg/tbq-041-nambu-convention-and-particle-hole-symmetry.md) | implemented | implemented | implemented | `domain_bdg_majorana` |
| TBQ-042 | [Phase-resolved Andreev spectrum and Josephson current](problems/09-superconducting-bdg/tbq-042-phase-resolved-andreev-spectrum-and-josephson-current.md) | implemented | implemented | implemented | `domain_bdg_majorana` |
| TBQ-043 | [Majorana versus trivial near-zero modes](problems/09-superconducting-bdg/tbq-043-majorana-versus-trivial-near-zero-modes.md) | implemented | implemented | implemented | `domain_bdg_majorana` |
| TBQ-044 | [Fragility of four-pi Josephson response](problems/09-superconducting-bdg/tbq-044-fragility-of-four-pi-josephson-response.md) | missing capability | missing capability | missing capability | none |
| TBQ-045 | [Continuum-to-lattice BdG convergence](problems/09-superconducting-bdg/tbq-045-continuum-to-lattice-bdg-convergence.md) | implemented | missing capability | implementable, unverified | `domain_bdg_discretization` |
| TBQ-046 | [Biorthogonal eigenvectors and residuals](problems/10-non-hermitian/tbq-046-biorthogonal-eigenvectors-and-residuals.md) | implemented | not applicable | not applicable | `domain_nonhermitian_static` |
| TBQ-047 | [Exceptional-point order and sensitivity](problems/10-non-hermitian/tbq-047-exceptional-point-order-and-sensitivity.md) | implemented | not applicable | not applicable | `domain_nonhermitian_static` |
| TBQ-048 | [Point-gap, line-gap, and non-Bloch invariants](problems/10-non-hermitian/tbq-048-point-gap-line-gap-and-non-bloch-invariants.md) | missing capability | not applicable | not applicable | none |
| TBQ-049 | [Periodic-open mismatch and skin localization](problems/10-non-hermitian/tbq-049-periodic-open-mismatch-and-skin-localization.md) | implemented | not applicable | not applicable | `domain_nonhermitian_static` |
| TBQ-050 | [Non-Hermitian family generalization](problems/10-non-hermitian/tbq-050-non-hermitian-family-generalization.md) | implemented | not applicable | not applicable | `domain_nonhermitian_static` |
| TBQ-051 | [Equivalent representations of a drive](problems/11-floquet-dynamics/tbq-051-equivalent-representations-of-a-drive.md) | not applicable | not applicable | not applicable | none |
| TBQ-052 | [Quasienergy branch and time-origin consistency](problems/11-floquet-dynamics/tbq-052-quasienergy-branch-and-time-origin-consistency.md) | not applicable | not applicable | not applicable | none |
| TBQ-053 | [Sambe, direct-propagation, and high-frequency agreement](problems/11-floquet-dynamics/tbq-053-sambe-direct-propagation-and-high-frequency-agreement.md) | not applicable | not applicable | not applicable | none |
| TBQ-054 | [Dynamical pumping and frequency conversion](problems/11-floquet-dynamics/tbq-054-dynamical-pumping-and-frequency-conversion.md) | not applicable | not applicable | not applicable | none |
| TBQ-055 | [Time-step and harmonic-cutoff holdout](problems/11-floquet-dynamics/tbq-055-time-step-and-harmonic-cutoff-holdout.md) | not applicable | not applicable | not applicable | none |
| TBQ-056 | [Interaction and double-counting declaration](problems/12-interactions-self-consistency/tbq-056-interaction-and-double-counting-declaration.md) | not applicable | not applicable | not applicable | none |
| TBQ-057 | [Self-consistency robustness and metastability](problems/12-interactions-self-consistency/tbq-057-self-consistency-robustness-and-metastability.md) | not applicable | not applicable | not applicable | none |
| TBQ-058 | [Thermodynamic comparison of competing orders](problems/12-interactions-self-consistency/tbq-058-thermodynamic-comparison-of-competing-orders.md) | not applicable | not applicable | not applicable | none |
| TBQ-059 | [Conservation and unbroken-symmetry checks](problems/12-interactions-self-consistency/tbq-059-conservation-and-unbroken-symmetry-checks.md) | not applicable | not applicable | not applicable | none |
| TBQ-060 | [Validation against small exact systems](problems/12-interactions-self-consistency/tbq-060-validation-against-small-exact-systems.md) | not applicable | not applicable | not applicable | none |
| TBQ-061 | [Commensurate and reconstructed geometry](problems/13-moire-strain-supercells/tbq-061-commensurate-and-reconstructed-geometry.md) | implemented | missing capability | implementable, unverified | `domain_moire_geometry` |
| TBQ-062 | [Geometry-dependent coupling laws](problems/13-moire-strain-supercells/tbq-062-geometry-dependent-coupling-laws.md) | implemented | missing capability | implementable, unverified | `domain_moire_geometry` |
| TBQ-063 | [Continuum-atomistic correspondence](problems/13-moire-strain-supercells/tbq-063-continuum-atomistic-correspondence.md) | missing capability | missing capability | implementable, unverified | none |
| TBQ-064 | [Sparse observables in giant supercells](problems/13-moire-strain-supercells/tbq-064-sparse-observables-in-giant-supercells.md) | missing capability | missing capability | implementable, unverified | none |
| TBQ-065 | [Structural-family transfer](problems/13-moire-strain-supercells/tbq-065-structural-family-transfer.md) | missing capability | missing capability | implementable, unverified | none |
| TBQ-066 | [Spinor texture construction and covariance](problems/14-magnetism-spin-orbital/tbq-066-spinor-texture-construction-and-covariance.md) | implemented | implemented | implemented | `domain_spin_texture_covariance` |
| TBQ-067 | [Charge, spin, orbital-current, and torque continuity](problems/14-magnetism-spin-orbital/tbq-067-charge-spin-orbital-current-and-torque-continuity.md) | implemented | missing capability | implementable, unverified | `domain_spin_transport` |
| TBQ-068 | [Mechanism-resolved Hall response](problems/14-magnetism-spin-orbital/tbq-068-mechanism-resolved-hall-response.md) | implemented | implementable, unverified | implementable, unverified | `domain_spin_transport` |
| TBQ-069 | [Texture-resolution and adiabatic convergence](problems/14-magnetism-spin-orbital/tbq-069-texture-resolution-and-adiabatic-convergence.md) | implemented | missing capability | implementable, unverified | `domain_spin_transport` |
| TBQ-070 | [Magnetic-family generalization](problems/14-magnetism-spin-orbital/tbq-070-magnetic-family-generalization.md) | implemented | missing capability | implementable, unverified | `domain_spin_transport` |
| TBQ-071 | [Hamiltonian-consistent response operators](problems/15-optical-thermoelectric/tbq-071-hamiltonian-consistent-response-operators.md) | implemented | missing capability | missing capability | `domain_response_thermoelectric` |
| TBQ-072 | [Optical spectral-sum and time-domain agreement](problems/15-optical-thermoelectric/tbq-072-optical-spectral-sum-and-time-domain-agreement.md) | missing capability | missing capability | missing capability | none |
| TBQ-073 | [Thermoelectric and Onsager relations](problems/15-optical-thermoelectric/tbq-073-thermoelectric-and-onsager-relations.md) | implemented | missing capability | implementable, unverified | `domain_response_thermoelectric` |
| TBQ-074 | [Broadening and integration convergence](problems/15-optical-thermoelectric/tbq-074-broadening-and-integration-convergence.md) | missing capability | missing capability | missing capability | none |
| TBQ-075 | [Method transfer from exact to large sparse systems](problems/15-optical-thermoelectric/tbq-075-method-transfer-from-exact-to-large-sparse-systems.md) | implemented | missing capability | implementable, unverified | `domain_response_thermoelectric` |
| TBQ-076 | [Translation-free geometric construction](problems/16-aperiodic-amorphous-fractal/tbq-076-translation-free-geometric-construction.md) | implemented | missing capability | implementable, unverified | `domain_arbitrary_graphs` |
| TBQ-077 | [Singular spectral measures and localization](problems/16-aperiodic-amorphous-fractal/tbq-077-singular-spectral-measures-and-localization.md) | missing capability | missing capability | implementable, unverified | none |
| TBQ-078 | [Real-space topology without translation symmetry](problems/16-aperiodic-amorphous-fractal/tbq-078-real-space-topology-without-translation-symmetry.md) | missing capability | missing capability | missing capability | none |
| TBQ-079 | [Approximant and multifractal scaling](problems/16-aperiodic-amorphous-fractal/tbq-079-approximant-and-multifractal-scaling.md) | missing capability | missing capability | implementable, unverified | none |
| TBQ-080 | [Geometry-family generalization](problems/16-aperiodic-amorphous-fractal/tbq-080-geometry-family-generalization.md) | missing capability | missing capability | missing capability | none |
| TBQ-081 | [Provenance-preserving structural defects](problems/17-defects-interfaces/tbq-081-provenance-preserving-structural-defects.md) | implemented | implementable, unverified | implementable, unverified | `domain_defect_workflows` |
| TBQ-082 | [Defect-specific local chemistry](problems/17-defects-interfaces/tbq-082-defect-specific-local-chemistry.md) | implemented | missing capability | implementable, unverified | `domain_defect_workflows` |
| TBQ-083 | [Embedding and supercell agreement](problems/17-defects-interfaces/tbq-083-embedding-and-supercell-agreement.md) | implemented | missing capability | implementable, unverified | `domain_defect_workflows` |
| TBQ-084 | [Local-state and transport consequences](problems/17-defects-interfaces/tbq-084-local-state-and-transport-consequences.md) | implemented | missing capability | implementable, unverified | `domain_defect_workflows` |
| TBQ-085 | [Defect-family generalization](problems/17-defects-interfaces/tbq-085-defect-family-generalization.md) | implemented | missing capability | implementable, unverified | `domain_defect_workflows` |
| TBQ-086 | [One physical question across scales](problems/18-multiscale-validation/tbq-086-one-physical-question-across-scales.md) | implemented | missing capability | implementable, unverified | `domain_multiscale_validation` |
| TBQ-087 | [Explicit representation mapping](problems/18-multiscale-validation/tbq-087-explicit-representation-mapping.md) | implemented | missing capability | missing capability | `domain_multiscale_validation` |
| TBQ-088 | [Gauge-invariant observable comparison](problems/18-multiscale-validation/tbq-088-gauge-invariant-observable-comparison.md) | implemented | missing capability | implementable, unverified | `domain_multiscale_validation` |
| TBQ-089 | [Discrepancy decomposition](problems/18-multiscale-validation/tbq-089-discrepancy-decomposition.md) | implemented | missing capability | implementable, unverified | `domain_multiscale_validation` |
| TBQ-090 | [External-family validation](problems/18-multiscale-validation/tbq-090-external-family-validation.md) | implemented | missing capability | implementable, unverified | `domain_multiscale_validation` |
| TBQ-091 | [Sparse-only production path](problems/19-scientific-scale-numerics/tbq-091-sparse-only-production-path.md) | missing capability | not applicable | missing capability | none |
| TBQ-092 | [Scalable solver portfolio](problems/19-scientific-scale-numerics/tbq-092-scalable-solver-portfolio.md) | missing capability | not applicable | missing capability | none |
| TBQ-093 | [Separated numerical error budget](problems/19-scientific-scale-numerics/tbq-093-separated-numerical-error-budget.md) | implemented | not applicable | implementable, unverified | `domain_sparse_numerics` |
| TBQ-094 | [Accuracy-preserving time and memory scaling](problems/19-scientific-scale-numerics/tbq-094-accuracy-preserving-time-and-memory-scaling.md) | implemented | not applicable | implementable, unverified | `domain_sparse_numerics` |
| TBQ-095 | [Reproducible transition from exact to production scale](problems/19-scientific-scale-numerics/tbq-095-reproducible-transition-from-exact-to-production-scale.md) | implemented | not applicable | implementable, unverified | `domain_sparse_numerics` |
| TBQ-096 | [Constrained multi-observable parameter inference](problems/20-inference-inverse-design/tbq-096-constrained-multi-observable-parameter-inference.md) | not applicable | not applicable | not applicable | none |
| TBQ-097 | [Gradient verification through spectral calculations](problems/20-inference-inverse-design/tbq-097-gradient-verification-through-spectral-calculations.md) | not applicable | not applicable | not applicable | none |
| TBQ-098 | [Identifiability and predictive calibration](problems/20-inference-inverse-design/tbq-098-identifiability-and-predictive-calibration.md) | not applicable | not applicable | not applicable | none |
| TBQ-099 | [Independent forward validation of inverse designs](problems/20-inference-inverse-design/tbq-099-independent-forward-validation-of-inverse-designs.md) | not applicable | not applicable | not applicable | none |
| TBQ-100 | [Out-of-family inference holdout](problems/20-inference-inverse-design/tbq-100-out-of-family-inference-holdout.md) | not applicable | not applicable | not applicable | none |

## Detailed 300-way assessment

| ID | Backend | Status | Required capabilities | Missing capabilities |
| --- | --- | --- | --- | --- |
| TBQ-001 | thouless | implemented | `periodic_model`, `generalized_eigensystem` | none |
| TBQ-001 | pythtb | missing capability | `periodic_model`, `generalized_eigensystem` | `generalized_eigensystem` |
| TBQ-001 | kwant | missing capability | `periodic_model`, `generalized_eigensystem` | `generalized_eigensystem` |
| TBQ-002 | thouless | implemented | `periodic_model`, `generalized_eigensystem`, `dense_spectrum`, `topological_inputs` | none |
| TBQ-002 | pythtb | missing capability | `periodic_model`, `generalized_eigensystem`, `dense_spectrum`, `topological_inputs` | `generalized_eigensystem` |
| TBQ-002 | kwant | missing capability | `periodic_model`, `generalized_eigensystem`, `dense_spectrum`, `topological_inputs` | `generalized_eigensystem` |
| TBQ-003 | thouless | implemented | `periodic_model`, `generalized_eigensystem`, `dense_spectrum`, `frequency_response` | none |
| TBQ-003 | pythtb | missing capability | `periodic_model`, `generalized_eigensystem`, `dense_spectrum`, `frequency_response` | `generalized_eigensystem` |
| TBQ-003 | kwant | missing capability | `periodic_model`, `generalized_eigensystem`, `dense_spectrum`, `frequency_response` | `generalized_eigensystem` |
| TBQ-004 | thouless | implemented | `periodic_model`, `generalized_eigensystem`, `dense_spectrum`, `parameterized_models` | none |
| TBQ-004 | pythtb | missing capability | `periodic_model`, `generalized_eigensystem`, `dense_spectrum`, `parameterized_models` | `generalized_eigensystem` |
| TBQ-004 | kwant | missing capability | `periodic_model`, `generalized_eigensystem`, `dense_spectrum`, `parameterized_models` | `generalized_eigensystem` |
| TBQ-005 | thouless | implemented | `periodic_model`, `generalized_eigensystem`, `dense_spectrum`, `parameterized_models` | none |
| TBQ-005 | pythtb | missing capability | `periodic_model`, `generalized_eigensystem`, `dense_spectrum`, `parameterized_models` | `generalized_eigensystem` |
| TBQ-005 | kwant | missing capability | `periodic_model`, `generalized_eigensystem`, `dense_spectrum`, `parameterized_models` | `generalized_eigensystem` |
| TBQ-006 | thouless | implemented | `periodic_model`, `dense_spectrum`, `topological_inputs` | none |
| TBQ-006 | pythtb | implemented | `periodic_model`, `dense_spectrum`, `topological_inputs` | none |
| TBQ-006 | kwant | implemented | `periodic_model`, `dense_spectrum`, `topological_inputs` | none |
| TBQ-007 | thouless | implemented | `periodic_model`, `finite_model`, `dense_spectrum` | none |
| TBQ-007 | pythtb | implemented | `periodic_model`, `finite_model`, `dense_spectrum` | none |
| TBQ-007 | kwant | implemented | `periodic_model`, `finite_model`, `dense_spectrum` | none |
| TBQ-008 | thouless | implemented | `periodic_model`, `dense_spectrum` | none |
| TBQ-008 | pythtb | implementable, unverified | `periodic_model`, `dense_spectrum` | none |
| TBQ-008 | kwant | implementable, unverified | `periodic_model`, `dense_spectrum` | none |
| TBQ-009 | thouless | implemented | `periodic_model`, `dense_spectrum` | none |
| TBQ-009 | pythtb | implementable, unverified | `periodic_model`, `dense_spectrum` | none |
| TBQ-009 | kwant | implementable, unverified | `periodic_model`, `dense_spectrum` | none |
| TBQ-010 | thouless | implemented | `periodic_model`, `finite_model`, `dense_spectrum` | none |
| TBQ-010 | pythtb | implemented | `periodic_model`, `finite_model`, `dense_spectrum` | none |
| TBQ-010 | kwant | implemented | `periodic_model`, `finite_model`, `dense_spectrum` | none |
| TBQ-011 | thouless | implemented | `finite_model`, `magnetic_models`, `dense_spectrum` | none |
| TBQ-011 | pythtb | implemented | `finite_model`, `magnetic_models`, `dense_spectrum` | none |
| TBQ-011 | kwant | implemented | `finite_model`, `magnetic_models`, `dense_spectrum` | none |
| TBQ-012 | thouless | implemented | `periodic_model`, `magnetic_models`, `dense_spectrum` | none |
| TBQ-012 | pythtb | implemented | `periodic_model`, `magnetic_models`, `dense_spectrum` | none |
| TBQ-012 | kwant | implemented | `periodic_model`, `magnetic_models`, `dense_spectrum` | none |
| TBQ-013 | thouless | implemented | `periodic_model`, `magnetic_models`, `topological_inputs` | none |
| TBQ-013 | pythtb | implemented | `periodic_model`, `magnetic_models`, `topological_inputs` | none |
| TBQ-013 | kwant | implemented | `periodic_model`, `magnetic_models`, `topological_inputs` | none |
| TBQ-014 | thouless | implemented | `periodic_model`, `magnetic_models`, `dense_spectrum` | none |
| TBQ-014 | pythtb | implementable, unverified | `periodic_model`, `magnetic_models`, `dense_spectrum` | none |
| TBQ-014 | kwant | implementable, unverified | `periodic_model`, `magnetic_models`, `dense_spectrum` | none |
| TBQ-015 | thouless | implemented | `periodic_model`, `finite_model`, `magnetic_models`, `topological_inputs` | none |
| TBQ-015 | pythtb | implementable, unverified | `periodic_model`, `finite_model`, `magnetic_models`, `topological_inputs` | none |
| TBQ-015 | kwant | implementable, unverified | `periodic_model`, `finite_model`, `magnetic_models`, `topological_inputs` | none |
| TBQ-016 | thouless | implemented | `periodic_model`, `dense_spectrum`, `topological_inputs` | none |
| TBQ-016 | pythtb | implementable, unverified | `periodic_model`, `dense_spectrum`, `topological_inputs` | none |
| TBQ-016 | kwant | implementable, unverified | `periodic_model`, `dense_spectrum`, `topological_inputs` | none |
| TBQ-017 | thouless | implemented | `periodic_model`, `dense_spectrum`, `topological_inputs`, `parameterized_models` | none |
| TBQ-017 | pythtb | implementable, unverified | `periodic_model`, `dense_spectrum`, `topological_inputs`, `parameterized_models` | none |
| TBQ-017 | kwant | implementable, unverified | `periodic_model`, `dense_spectrum`, `topological_inputs`, `parameterized_models` | none |
| TBQ-018 | thouless | implemented | `periodic_model`, `dense_spectrum`, `topological_inputs` | none |
| TBQ-018 | pythtb | implementable, unverified | `periodic_model`, `dense_spectrum`, `topological_inputs` | none |
| TBQ-018 | kwant | implementable, unverified | `periodic_model`, `dense_spectrum`, `topological_inputs` | none |
| TBQ-019 | thouless | implemented | `periodic_model`, `finite_model`, `dense_spectrum`, `topological_inputs` | none |
| TBQ-019 | pythtb | implemented | `periodic_model`, `finite_model`, `dense_spectrum`, `topological_inputs` | none |
| TBQ-019 | kwant | implemented | `periodic_model`, `finite_model`, `dense_spectrum`, `topological_inputs` | none |
| TBQ-020 | thouless | implemented | `periodic_model`, `dense_spectrum`, `topological_inputs`, `parameterized_models` | none |
| TBQ-020 | pythtb | implementable, unverified | `periodic_model`, `dense_spectrum`, `topological_inputs`, `parameterized_models` | none |
| TBQ-020 | kwant | implementable, unverified | `periodic_model`, `dense_spectrum`, `topological_inputs`, `parameterized_models` | none |
| TBQ-021 | thouless | implemented | `periodic_model`, `finite_model` | none |
| TBQ-021 | pythtb | implementable, unverified | `periodic_model`, `finite_model` | none |
| TBQ-021 | kwant | implementable, unverified | `periodic_model`, `finite_model` | none |
| TBQ-022 | thouless | implemented | `finite_model`, `dense_spectrum` | none |
| TBQ-022 | pythtb | implemented | `finite_model`, `dense_spectrum` | none |
| TBQ-022 | kwant | implemented | `finite_model`, `dense_spectrum` | none |
| TBQ-023 | thouless | implemented | `finite_model`, `dense_spectrum`, `surface_green_function` | none |
| TBQ-023 | pythtb | missing capability | `finite_model`, `dense_spectrum`, `surface_green_function` | `surface_green_function` |
| TBQ-023 | kwant | implementable, unverified | `finite_model`, `dense_spectrum`, `surface_green_function` | none |
| TBQ-024 | thouless | implemented | `periodic_model`, `finite_model`, `dense_spectrum`, `topological_inputs` | none |
| TBQ-024 | pythtb | implementable, unverified | `periodic_model`, `finite_model`, `dense_spectrum`, `topological_inputs` | none |
| TBQ-024 | kwant | implementable, unverified | `periodic_model`, `finite_model`, `dense_spectrum`, `topological_inputs` | none |
| TBQ-025 | thouless | implemented | `periodic_model`, `finite_model`, `dense_spectrum` | none |
| TBQ-025 | pythtb | implementable, unverified | `periodic_model`, `finite_model`, `dense_spectrum` | none |
| TBQ-025 | kwant | implementable, unverified | `periodic_model`, `finite_model`, `dense_spectrum` | none |
| TBQ-026 | thouless | implemented | `periodic_model`, `dense_spectrum`, `quantum_geometry`, `analytic_hamiltonian_derivatives` | none |
| TBQ-026 | pythtb | implementable, unverified | `periodic_model`, `dense_spectrum`, `quantum_geometry`, `analytic_hamiltonian_derivatives` | none |
| TBQ-026 | kwant | missing capability | `periodic_model`, `dense_spectrum`, `quantum_geometry`, `analytic_hamiltonian_derivatives` | `analytic_hamiltonian_derivatives` |
| TBQ-027 | thouless | implemented | `periodic_model`, `quantum_geometry`, `frequency_response` | none |
| TBQ-027 | pythtb | implementable, unverified | `periodic_model`, `quantum_geometry`, `frequency_response` | none |
| TBQ-027 | kwant | implementable, unverified | `periodic_model`, `quantum_geometry`, `frequency_response` | none |
| TBQ-028 | thouless | implemented | `periodic_model`, `quantum_geometry`, `frequency_response` | none |
| TBQ-028 | pythtb | implementable, unverified | `periodic_model`, `quantum_geometry`, `frequency_response` | none |
| TBQ-028 | kwant | implementable, unverified | `periodic_model`, `quantum_geometry`, `frequency_response` | none |
| TBQ-029 | thouless | missing capability | `periodic_model`, `quantum_geometry`, `frequency_response`, `parameterized_models`, `automatic_differentiation` | `automatic_differentiation` |
| TBQ-029 | pythtb | missing capability | `periodic_model`, `quantum_geometry`, `frequency_response`, `parameterized_models`, `automatic_differentiation` | `automatic_differentiation` |
| TBQ-029 | kwant | missing capability | `periodic_model`, `quantum_geometry`, `frequency_response`, `parameterized_models`, `automatic_differentiation` | `automatic_differentiation` |
| TBQ-030 | thouless | implemented | `periodic_model`, `finite_model`, `quantum_geometry`, `steady_state_transport` | none |
| TBQ-030 | pythtb | missing capability | `periodic_model`, `finite_model`, `quantum_geometry`, `steady_state_transport` | `steady_state_transport` |
| TBQ-030 | kwant | implementable, unverified | `periodic_model`, `finite_model`, `quantum_geometry`, `steady_state_transport` | none |
| TBQ-031 | thouless | implemented | `finite_model`, `parameterized_models`, `nonhermitian_spectrum` | none |
| TBQ-031 | pythtb | missing capability | `finite_model`, `parameterized_models`, `nonhermitian_spectrum` | `nonhermitian_spectrum` |
| TBQ-031 | kwant | missing capability | `finite_model`, `parameterized_models`, `nonhermitian_spectrum` | `nonhermitian_spectrum` |
| TBQ-032 | thouless | missing capability | `finite_model`, `sparse_operators`, `kernel_polynomial`, `steady_state_transport`, `sparse_nonhermitian_solver` | `sparse_nonhermitian_solver` |
| TBQ-032 | pythtb | missing capability | `finite_model`, `sparse_operators`, `kernel_polynomial`, `steady_state_transport`, `sparse_nonhermitian_solver` | `sparse_operators`, `kernel_polynomial`, `steady_state_transport`, `sparse_nonhermitian_solver` |
| TBQ-032 | kwant | missing capability | `finite_model`, `sparse_operators`, `kernel_polynomial`, `steady_state_transport`, `sparse_nonhermitian_solver` | `sparse_nonhermitian_solver` |
| TBQ-033 | thouless | missing capability | `finite_model`, `sparse_operators`, `steady_state_transport`, `sparse_nonhermitian_solver` | `sparse_nonhermitian_solver` |
| TBQ-033 | pythtb | missing capability | `finite_model`, `sparse_operators`, `steady_state_transport`, `sparse_nonhermitian_solver` | `sparse_operators`, `steady_state_transport`, `sparse_nonhermitian_solver` |
| TBQ-033 | kwant | missing capability | `finite_model`, `sparse_operators`, `steady_state_transport`, `sparse_nonhermitian_solver` | `sparse_nonhermitian_solver` |
| TBQ-034 | thouless | missing capability | `finite_model`, `sparse_operators`, `topological_inputs`, `steady_state_transport`, `sparse_nonhermitian_solver` | `sparse_nonhermitian_solver` |
| TBQ-034 | pythtb | missing capability | `finite_model`, `sparse_operators`, `topological_inputs`, `steady_state_transport`, `sparse_nonhermitian_solver` | `sparse_operators`, `steady_state_transport`, `sparse_nonhermitian_solver` |
| TBQ-034 | kwant | missing capability | `finite_model`, `sparse_operators`, `topological_inputs`, `steady_state_transport`, `sparse_nonhermitian_solver` | `sparse_nonhermitian_solver` |
| TBQ-035 | thouless | missing capability | `finite_model`, `sparse_operators`, `parameterized_models`, `sparse_nonhermitian_solver` | `sparse_nonhermitian_solver` |
| TBQ-035 | pythtb | missing capability | `finite_model`, `sparse_operators`, `parameterized_models`, `sparse_nonhermitian_solver` | `sparse_operators`, `sparse_nonhermitian_solver` |
| TBQ-035 | kwant | missing capability | `finite_model`, `sparse_operators`, `parameterized_models`, `sparse_nonhermitian_solver` | `sparse_nonhermitian_solver` |
| TBQ-036 | thouless | implemented | `surface_green_function`, `steady_state_transport` | none |
| TBQ-036 | pythtb | not applicable | `surface_green_function`, `steady_state_transport` | `surface_green_function`, `steady_state_transport` |
| TBQ-036 | kwant | implemented | `surface_green_function`, `steady_state_transport` | none |
| TBQ-037 | thouless | implemented | `steady_state_transport`, `local_continuity`, `transport_noise` | none |
| TBQ-037 | pythtb | not applicable | `steady_state_transport`, `local_continuity`, `transport_noise` | `steady_state_transport`, `local_continuity`, `transport_noise` |
| TBQ-037 | kwant | implementable, unverified | `steady_state_transport`, `local_continuity`, `transport_noise` | none |
| TBQ-038 | thouless | implemented | `steady_state_transport`, `local_continuity`, `transport_noise` | none |
| TBQ-038 | pythtb | not applicable | `steady_state_transport`, `local_continuity`, `transport_noise` | `steady_state_transport`, `local_continuity`, `transport_noise` |
| TBQ-038 | kwant | implementable, unverified | `steady_state_transport`, `local_continuity`, `transport_noise` | none |
| TBQ-039 | thouless | implemented | `steady_state_transport`, `long_device_solver` | none |
| TBQ-039 | pythtb | not applicable | `steady_state_transport`, `long_device_solver` | `steady_state_transport`, `long_device_solver` |
| TBQ-039 | kwant | implementable, unverified | `steady_state_transport`, `long_device_solver` | none |
| TBQ-040 | thouless | implemented | `steady_state_transport`, `surface_green_function`, `parameterized_models` | none |
| TBQ-040 | pythtb | not applicable | `steady_state_transport`, `surface_green_function`, `parameterized_models` | `steady_state_transport`, `surface_green_function` |
| TBQ-040 | kwant | implementable, unverified | `steady_state_transport`, `surface_green_function`, `parameterized_models` | none |
| TBQ-041 | thouless | implemented | `finite_model`, `dense_spectrum`, `static_bdg` | none |
| TBQ-041 | pythtb | implemented | `finite_model`, `dense_spectrum`, `static_bdg` | none |
| TBQ-041 | kwant | implemented | `finite_model`, `dense_spectrum`, `static_bdg` | none |
| TBQ-042 | thouless | implemented | `finite_model`, `dense_spectrum`, `static_bdg` | none |
| TBQ-042 | pythtb | implemented | `finite_model`, `dense_spectrum`, `static_bdg` | none |
| TBQ-042 | kwant | implemented | `finite_model`, `dense_spectrum`, `static_bdg` | none |
| TBQ-043 | thouless | implemented | `periodic_model`, `finite_model`, `dense_spectrum`, `static_bdg`, `topological_inputs` | none |
| TBQ-043 | pythtb | implemented | `periodic_model`, `finite_model`, `dense_spectrum`, `static_bdg`, `topological_inputs` | none |
| TBQ-043 | kwant | implemented | `periodic_model`, `finite_model`, `dense_spectrum`, `static_bdg`, `topological_inputs` | none |
| TBQ-044 | thouless | missing capability | `finite_model`, `static_bdg`, `real_time_propagation` | `real_time_propagation` |
| TBQ-044 | pythtb | missing capability | `finite_model`, `static_bdg`, `real_time_propagation` | `real_time_propagation` |
| TBQ-044 | kwant | missing capability | `finite_model`, `static_bdg`, `real_time_propagation` | `real_time_propagation` |
| TBQ-045 | thouless | implemented | `finite_model`, `dense_spectrum`, `static_bdg`, `parameterized_models`, `continuum_discretization` | none |
| TBQ-045 | pythtb | missing capability | `finite_model`, `dense_spectrum`, `static_bdg`, `parameterized_models`, `continuum_discretization` | `continuum_discretization` |
| TBQ-045 | kwant | implementable, unverified | `finite_model`, `dense_spectrum`, `static_bdg`, `parameterized_models`, `continuum_discretization` | none |
| TBQ-046 | thouless | implemented | `nonhermitian_spectrum` | none |
| TBQ-046 | pythtb | not applicable | `nonhermitian_spectrum` | `nonhermitian_spectrum` |
| TBQ-046 | kwant | not applicable | `nonhermitian_spectrum` | `nonhermitian_spectrum` |
| TBQ-047 | thouless | implemented | `nonhermitian_spectrum`, `parameterized_models` | none |
| TBQ-047 | pythtb | not applicable | `nonhermitian_spectrum`, `parameterized_models` | `nonhermitian_spectrum` |
| TBQ-047 | kwant | not applicable | `nonhermitian_spectrum`, `parameterized_models` | `nonhermitian_spectrum` |
| TBQ-048 | thouless | missing capability | `nonhermitian_spectrum`, `topological_inputs`, `non_bloch_topology` | `non_bloch_topology` |
| TBQ-048 | pythtb | not applicable | `nonhermitian_spectrum`, `topological_inputs`, `non_bloch_topology` | `nonhermitian_spectrum`, `non_bloch_topology` |
| TBQ-048 | kwant | not applicable | `nonhermitian_spectrum`, `topological_inputs`, `non_bloch_topology` | `nonhermitian_spectrum`, `non_bloch_topology` |
| TBQ-049 | thouless | implemented | `nonhermitian_spectrum`, `finite_model`, `periodic_model` | none |
| TBQ-049 | pythtb | not applicable | `nonhermitian_spectrum`, `finite_model`, `periodic_model` | `nonhermitian_spectrum` |
| TBQ-049 | kwant | not applicable | `nonhermitian_spectrum`, `finite_model`, `periodic_model` | `nonhermitian_spectrum` |
| TBQ-050 | thouless | implemented | `nonhermitian_spectrum`, `finite_model`, `parameterized_models` | none |
| TBQ-050 | pythtb | not applicable | `nonhermitian_spectrum`, `finite_model`, `parameterized_models` | `nonhermitian_spectrum` |
| TBQ-050 | kwant | not applicable | `nonhermitian_spectrum`, `finite_model`, `parameterized_models` | `nonhermitian_spectrum` |
| TBQ-051 | thouless | not applicable | `real_time_propagation`, `parameterized_models` | `real_time_propagation` |
| TBQ-051 | pythtb | not applicable | `real_time_propagation`, `parameterized_models` | `real_time_propagation` |
| TBQ-051 | kwant | not applicable | `real_time_propagation`, `parameterized_models` | `real_time_propagation` |
| TBQ-052 | thouless | not applicable | `real_time_propagation`, `dense_spectrum` | `real_time_propagation` |
| TBQ-052 | pythtb | not applicable | `real_time_propagation`, `dense_spectrum` | `real_time_propagation` |
| TBQ-052 | kwant | not applicable | `real_time_propagation`, `dense_spectrum` | `real_time_propagation` |
| TBQ-053 | thouless | not applicable | `real_time_propagation`, `dense_spectrum` | `real_time_propagation` |
| TBQ-053 | pythtb | not applicable | `real_time_propagation`, `dense_spectrum` | `real_time_propagation` |
| TBQ-053 | kwant | not applicable | `real_time_propagation`, `dense_spectrum` | `real_time_propagation` |
| TBQ-054 | thouless | not applicable | `real_time_propagation`, `local_continuity`, `topological_inputs` | `real_time_propagation` |
| TBQ-054 | pythtb | not applicable | `real_time_propagation`, `local_continuity`, `topological_inputs` | `real_time_propagation`, `local_continuity` |
| TBQ-054 | kwant | not applicable | `real_time_propagation`, `local_continuity`, `topological_inputs` | `real_time_propagation` |
| TBQ-055 | thouless | not applicable | `real_time_propagation`, `parameterized_models` | `real_time_propagation` |
| TBQ-055 | pythtb | not applicable | `real_time_propagation`, `parameterized_models` | `real_time_propagation` |
| TBQ-055 | kwant | not applicable | `real_time_propagation`, `parameterized_models` | `real_time_propagation` |
| TBQ-056 | thouless | not applicable | `self_consistent_interactions` | `self_consistent_interactions` |
| TBQ-056 | pythtb | not applicable | `self_consistent_interactions` | `self_consistent_interactions` |
| TBQ-056 | kwant | not applicable | `self_consistent_interactions` | `self_consistent_interactions` |
| TBQ-057 | thouless | not applicable | `self_consistent_interactions`, `parameterized_models` | `self_consistent_interactions` |
| TBQ-057 | pythtb | not applicable | `self_consistent_interactions`, `parameterized_models` | `self_consistent_interactions` |
| TBQ-057 | kwant | not applicable | `self_consistent_interactions`, `parameterized_models` | `self_consistent_interactions` |
| TBQ-058 | thouless | not applicable | `self_consistent_interactions`, `dense_spectrum` | `self_consistent_interactions` |
| TBQ-058 | pythtb | not applicable | `self_consistent_interactions`, `dense_spectrum` | `self_consistent_interactions` |
| TBQ-058 | kwant | not applicable | `self_consistent_interactions`, `dense_spectrum` | `self_consistent_interactions` |
| TBQ-059 | thouless | not applicable | `self_consistent_interactions`, `local_continuity` | `self_consistent_interactions` |
| TBQ-059 | pythtb | not applicable | `self_consistent_interactions`, `local_continuity` | `self_consistent_interactions`, `local_continuity` |
| TBQ-059 | kwant | not applicable | `self_consistent_interactions`, `local_continuity` | `self_consistent_interactions` |
| TBQ-060 | thouless | not applicable | `self_consistent_interactions`, `dense_spectrum` | `self_consistent_interactions` |
| TBQ-060 | pythtb | not applicable | `self_consistent_interactions`, `dense_spectrum` | `self_consistent_interactions` |
| TBQ-060 | kwant | not applicable | `self_consistent_interactions`, `dense_spectrum` | `self_consistent_interactions` |
| TBQ-061 | thouless | implemented | `large_sparse_geometry` | none |
| TBQ-061 | pythtb | missing capability | `large_sparse_geometry` | `large_sparse_geometry` |
| TBQ-061 | kwant | implementable, unverified | `large_sparse_geometry` | none |
| TBQ-062 | thouless | implemented | `large_sparse_geometry`, `parameterized_models` | none |
| TBQ-062 | pythtb | missing capability | `large_sparse_geometry`, `parameterized_models` | `large_sparse_geometry` |
| TBQ-062 | kwant | implementable, unverified | `large_sparse_geometry`, `parameterized_models` | none |
| TBQ-063 | thouless | missing capability | `large_sparse_geometry`, `continuum_discretization`, `sparse_operators`, `targeted_sparse_eigenpairs`, `topological_inputs` | `targeted_sparse_eigenpairs` |
| TBQ-063 | pythtb | missing capability | `large_sparse_geometry`, `continuum_discretization`, `sparse_operators`, `targeted_sparse_eigenpairs`, `topological_inputs` | `large_sparse_geometry`, `continuum_discretization`, `sparse_operators`, `targeted_sparse_eigenpairs` |
| TBQ-063 | kwant | implementable, unverified | `large_sparse_geometry`, `continuum_discretization`, `sparse_operators`, `targeted_sparse_eigenpairs`, `topological_inputs` | none |
| TBQ-064 | thouless | missing capability | `large_sparse_geometry`, `sparse_operators`, `kernel_polynomial`, `targeted_sparse_eigenpairs` | `targeted_sparse_eigenpairs` |
| TBQ-064 | pythtb | missing capability | `large_sparse_geometry`, `sparse_operators`, `kernel_polynomial`, `targeted_sparse_eigenpairs` | `large_sparse_geometry`, `sparse_operators`, `kernel_polynomial`, `targeted_sparse_eigenpairs` |
| TBQ-064 | kwant | implementable, unverified | `large_sparse_geometry`, `sparse_operators`, `kernel_polynomial`, `targeted_sparse_eigenpairs` | none |
| TBQ-065 | thouless | missing capability | `large_sparse_geometry`, `sparse_operators`, `kernel_polynomial`, `targeted_sparse_eigenpairs`, `parameterized_models` | `targeted_sparse_eigenpairs` |
| TBQ-065 | pythtb | missing capability | `large_sparse_geometry`, `sparse_operators`, `kernel_polynomial`, `targeted_sparse_eigenpairs`, `parameterized_models` | `large_sparse_geometry`, `sparse_operators`, `kernel_polynomial`, `targeted_sparse_eigenpairs` |
| TBQ-065 | kwant | implementable, unverified | `large_sparse_geometry`, `sparse_operators`, `kernel_polynomial`, `targeted_sparse_eigenpairs`, `parameterized_models` | none |
| TBQ-066 | thouless | implemented | `finite_model`, `dense_spectrum`, `spin_observables` | none |
| TBQ-066 | pythtb | implemented | `finite_model`, `dense_spectrum`, `spin_observables` | none |
| TBQ-066 | kwant | implemented | `finite_model`, `dense_spectrum`, `spin_observables` | none |
| TBQ-067 | thouless | implemented | `finite_model`, `spin_observables`, `local_continuity` | none |
| TBQ-067 | pythtb | missing capability | `finite_model`, `spin_observables`, `local_continuity` | `local_continuity` |
| TBQ-067 | kwant | implementable, unverified | `finite_model`, `spin_observables`, `local_continuity` | none |
| TBQ-068 | thouless | implemented | `periodic_model`, `spin_observables`, `frequency_response` | none |
| TBQ-068 | pythtb | implementable, unverified | `periodic_model`, `spin_observables`, `frequency_response` | none |
| TBQ-068 | kwant | implementable, unverified | `periodic_model`, `spin_observables`, `frequency_response` | none |
| TBQ-069 | thouless | implemented | `finite_model`, `spin_observables`, `steady_state_transport` | none |
| TBQ-069 | pythtb | missing capability | `finite_model`, `spin_observables`, `steady_state_transport` | `steady_state_transport` |
| TBQ-069 | kwant | implementable, unverified | `finite_model`, `spin_observables`, `steady_state_transport` | none |
| TBQ-070 | thouless | implemented | `finite_model`, `spin_observables`, `steady_state_transport`, `parameterized_models` | none |
| TBQ-070 | pythtb | missing capability | `finite_model`, `spin_observables`, `steady_state_transport`, `parameterized_models` | `steady_state_transport` |
| TBQ-070 | kwant | implementable, unverified | `finite_model`, `spin_observables`, `steady_state_transport`, `parameterized_models` | none |
| TBQ-071 | thouless | implemented | `generalized_eigensystem`, `sparse_operators`, `response_operators` | none |
| TBQ-071 | pythtb | missing capability | `generalized_eigensystem`, `sparse_operators`, `response_operators` | `generalized_eigensystem`, `sparse_operators` |
| TBQ-071 | kwant | missing capability | `generalized_eigensystem`, `sparse_operators`, `response_operators` | `generalized_eigensystem` |
| TBQ-072 | thouless | missing capability | `frequency_response`, `real_time_propagation` | `real_time_propagation` |
| TBQ-072 | pythtb | missing capability | `frequency_response`, `real_time_propagation` | `real_time_propagation` |
| TBQ-072 | kwant | missing capability | `frequency_response`, `real_time_propagation` | `real_time_propagation` |
| TBQ-073 | thouless | implemented | `thermoelectric_response`, `sparse_operators`, `parameterized_models` | none |
| TBQ-073 | pythtb | missing capability | `thermoelectric_response`, `sparse_operators`, `parameterized_models` | `sparse_operators` |
| TBQ-073 | kwant | implementable, unverified | `thermoelectric_response`, `sparse_operators`, `parameterized_models` | none |
| TBQ-074 | thouless | missing capability | `frequency_response`, `kernel_polynomial`, `real_time_propagation` | `real_time_propagation` |
| TBQ-074 | pythtb | missing capability | `frequency_response`, `kernel_polynomial`, `real_time_propagation` | `kernel_polynomial`, `real_time_propagation` |
| TBQ-074 | kwant | missing capability | `frequency_response`, `kernel_polynomial`, `real_time_propagation` | `real_time_propagation` |
| TBQ-075 | thouless | implemented | `frequency_response`, `kernel_polynomial`, `sparse_operators` | none |
| TBQ-075 | pythtb | missing capability | `frequency_response`, `kernel_polynomial`, `sparse_operators` | `kernel_polynomial`, `sparse_operators` |
| TBQ-075 | kwant | implementable, unverified | `frequency_response`, `kernel_polynomial`, `sparse_operators` | none |
| TBQ-076 | thouless | implemented | `arbitrary_graphs`, `finite_model`, `large_sparse_geometry` | none |
| TBQ-076 | pythtb | missing capability | `arbitrary_graphs`, `finite_model`, `large_sparse_geometry` | `large_sparse_geometry` |
| TBQ-076 | kwant | implementable, unverified | `arbitrary_graphs`, `finite_model`, `large_sparse_geometry` | none |
| TBQ-077 | thouless | missing capability | `arbitrary_graphs`, `finite_model`, `large_sparse_geometry`, `sparse_operators`, `kernel_polynomial`, `targeted_sparse_eigenpairs` | `targeted_sparse_eigenpairs` |
| TBQ-077 | pythtb | missing capability | `arbitrary_graphs`, `finite_model`, `large_sparse_geometry`, `sparse_operators`, `kernel_polynomial`, `targeted_sparse_eigenpairs` | `large_sparse_geometry`, `sparse_operators`, `kernel_polynomial`, `targeted_sparse_eigenpairs` |
| TBQ-077 | kwant | implementable, unverified | `arbitrary_graphs`, `finite_model`, `large_sparse_geometry`, `sparse_operators`, `kernel_polynomial`, `targeted_sparse_eigenpairs` | none |
| TBQ-078 | thouless | missing capability | `arbitrary_graphs`, `finite_model`, `large_sparse_geometry`, `sparse_operators`, `kernel_polynomial`, `topological_inputs`, `sparse_real_space_topology` | `sparse_real_space_topology` |
| TBQ-078 | pythtb | missing capability | `arbitrary_graphs`, `finite_model`, `large_sparse_geometry`, `sparse_operators`, `kernel_polynomial`, `topological_inputs`, `sparse_real_space_topology` | `large_sparse_geometry`, `sparse_operators`, `kernel_polynomial`, `sparse_real_space_topology` |
| TBQ-078 | kwant | missing capability | `arbitrary_graphs`, `finite_model`, `large_sparse_geometry`, `sparse_operators`, `kernel_polynomial`, `topological_inputs`, `sparse_real_space_topology` | `sparse_real_space_topology` |
| TBQ-079 | thouless | missing capability | `arbitrary_graphs`, `finite_model`, `large_sparse_geometry`, `sparse_operators`, `targeted_sparse_eigenpairs` | `targeted_sparse_eigenpairs` |
| TBQ-079 | pythtb | missing capability | `arbitrary_graphs`, `finite_model`, `large_sparse_geometry`, `sparse_operators`, `targeted_sparse_eigenpairs` | `large_sparse_geometry`, `sparse_operators`, `targeted_sparse_eigenpairs` |
| TBQ-079 | kwant | implementable, unverified | `arbitrary_graphs`, `finite_model`, `large_sparse_geometry`, `sparse_operators`, `targeted_sparse_eigenpairs` | none |
| TBQ-080 | thouless | missing capability | `arbitrary_graphs`, `finite_model`, `large_sparse_geometry`, `sparse_operators`, `kernel_polynomial`, `targeted_sparse_eigenpairs`, `sparse_real_space_topology`, `parameterized_models` | `targeted_sparse_eigenpairs`, `sparse_real_space_topology` |
| TBQ-080 | pythtb | missing capability | `arbitrary_graphs`, `finite_model`, `large_sparse_geometry`, `sparse_operators`, `kernel_polynomial`, `targeted_sparse_eigenpairs`, `sparse_real_space_topology`, `parameterized_models` | `large_sparse_geometry`, `sparse_operators`, `kernel_polynomial`, `targeted_sparse_eigenpairs`, `sparse_real_space_topology` |
| TBQ-080 | kwant | missing capability | `arbitrary_graphs`, `finite_model`, `large_sparse_geometry`, `sparse_operators`, `kernel_polynomial`, `targeted_sparse_eigenpairs`, `sparse_real_space_topology`, `parameterized_models` | `sparse_real_space_topology` |
| TBQ-081 | thouless | implemented | `arbitrary_graphs`, `finite_model` | none |
| TBQ-081 | pythtb | implementable, unverified | `arbitrary_graphs`, `finite_model` | none |
| TBQ-081 | kwant | implementable, unverified | `arbitrary_graphs`, `finite_model` | none |
| TBQ-082 | thouless | implemented | `arbitrary_graphs`, `finite_model`, `dense_spectrum`, `embedding_green_function` | none |
| TBQ-082 | pythtb | missing capability | `arbitrary_graphs`, `finite_model`, `dense_spectrum`, `embedding_green_function` | `embedding_green_function` |
| TBQ-082 | kwant | implementable, unverified | `arbitrary_graphs`, `finite_model`, `dense_spectrum`, `embedding_green_function` | none |
| TBQ-083 | thouless | implemented | `finite_model`, `dense_spectrum`, `embedding_green_function` | none |
| TBQ-083 | pythtb | missing capability | `finite_model`, `dense_spectrum`, `embedding_green_function` | `embedding_green_function` |
| TBQ-083 | kwant | implementable, unverified | `finite_model`, `dense_spectrum`, `embedding_green_function` | none |
| TBQ-084 | thouless | implemented | `finite_model`, `dense_spectrum`, `steady_state_transport` | none |
| TBQ-084 | pythtb | missing capability | `finite_model`, `dense_spectrum`, `steady_state_transport` | `steady_state_transport` |
| TBQ-084 | kwant | implementable, unverified | `finite_model`, `dense_spectrum`, `steady_state_transport` | none |
| TBQ-085 | thouless | implemented | `arbitrary_graphs`, `finite_model`, `sparse_operators`, `kernel_polynomial`, `parameterized_models` | none |
| TBQ-085 | pythtb | missing capability | `arbitrary_graphs`, `finite_model`, `sparse_operators`, `kernel_polynomial`, `parameterized_models` | `sparse_operators`, `kernel_polynomial` |
| TBQ-085 | kwant | implementable, unverified | `arbitrary_graphs`, `finite_model`, `sparse_operators`, `kernel_polynomial`, `parameterized_models` | none |
| TBQ-086 | thouless | implemented | `periodic_model`, `finite_model`, `dense_spectrum`, `sparse_operators`, `continuum_discretization`, `parameterized_models` | none |
| TBQ-086 | pythtb | missing capability | `periodic_model`, `finite_model`, `dense_spectrum`, `sparse_operators`, `continuum_discretization`, `parameterized_models` | `sparse_operators`, `continuum_discretization` |
| TBQ-086 | kwant | implementable, unverified | `periodic_model`, `finite_model`, `dense_spectrum`, `sparse_operators`, `continuum_discretization`, `parameterized_models` | none |
| TBQ-087 | thouless | implemented | `periodic_model`, `finite_model`, `generalized_eigensystem`, `dense_spectrum`, `topological_inputs` | none |
| TBQ-087 | pythtb | missing capability | `periodic_model`, `finite_model`, `generalized_eigensystem`, `dense_spectrum`, `topological_inputs` | `generalized_eigensystem` |
| TBQ-087 | kwant | missing capability | `periodic_model`, `finite_model`, `generalized_eigensystem`, `dense_spectrum`, `topological_inputs` | `generalized_eigensystem` |
| TBQ-088 | thouless | implemented | `periodic_model`, `finite_model`, `sparse_operators`, `topological_inputs`, `steady_state_transport`, `frequency_response` | none |
| TBQ-088 | pythtb | missing capability | `periodic_model`, `finite_model`, `sparse_operators`, `topological_inputs`, `steady_state_transport`, `frequency_response` | `sparse_operators`, `steady_state_transport` |
| TBQ-088 | kwant | implementable, unverified | `periodic_model`, `finite_model`, `sparse_operators`, `topological_inputs`, `steady_state_transport`, `frequency_response` | none |
| TBQ-089 | thouless | implemented | `periodic_model`, `finite_model`, `dense_spectrum`, `sparse_operators`, `parameterized_models` | none |
| TBQ-089 | pythtb | missing capability | `periodic_model`, `finite_model`, `dense_spectrum`, `sparse_operators`, `parameterized_models` | `sparse_operators` |
| TBQ-089 | kwant | implementable, unverified | `periodic_model`, `finite_model`, `dense_spectrum`, `sparse_operators`, `parameterized_models` | none |
| TBQ-090 | thouless | implemented | `periodic_model`, `finite_model`, `dense_spectrum`, `sparse_operators`, `parameterized_models` | none |
| TBQ-090 | pythtb | missing capability | `periodic_model`, `finite_model`, `dense_spectrum`, `sparse_operators`, `parameterized_models` | `sparse_operators` |
| TBQ-090 | kwant | implementable, unverified | `periodic_model`, `finite_model`, `dense_spectrum`, `sparse_operators`, `parameterized_models` | none |
| TBQ-091 | thouless | missing capability | `large_sparse_geometry`, `sparse_operators`, `kernel_polynomial`, `targeted_sparse_eigenpairs`, `iterative_linear_solver`, `real_time_propagation` | `targeted_sparse_eigenpairs`, `real_time_propagation` |
| TBQ-091 | pythtb | not applicable | `large_sparse_geometry`, `sparse_operators`, `kernel_polynomial`, `targeted_sparse_eigenpairs`, `iterative_linear_solver`, `real_time_propagation` | `large_sparse_geometry`, `sparse_operators`, `kernel_polynomial`, `targeted_sparse_eigenpairs`, `iterative_linear_solver`, `real_time_propagation` |
| TBQ-091 | kwant | missing capability | `large_sparse_geometry`, `sparse_operators`, `kernel_polynomial`, `targeted_sparse_eigenpairs`, `iterative_linear_solver`, `real_time_propagation` | `real_time_propagation` |
| TBQ-092 | thouless | missing capability | `sparse_operators`, `kernel_polynomial`, `targeted_sparse_eigenpairs`, `iterative_linear_solver`, `real_time_propagation` | `targeted_sparse_eigenpairs`, `real_time_propagation` |
| TBQ-092 | pythtb | not applicable | `sparse_operators`, `kernel_polynomial`, `targeted_sparse_eigenpairs`, `iterative_linear_solver`, `real_time_propagation` | `sparse_operators`, `kernel_polynomial`, `targeted_sparse_eigenpairs`, `iterative_linear_solver`, `real_time_propagation` |
| TBQ-092 | kwant | missing capability | `sparse_operators`, `kernel_polynomial`, `targeted_sparse_eigenpairs`, `iterative_linear_solver`, `real_time_propagation` | `real_time_propagation` |
| TBQ-093 | thouless | implemented | `sparse_operators`, `kernel_polynomial`, `iterative_linear_solver` | none |
| TBQ-093 | pythtb | not applicable | `sparse_operators`, `kernel_polynomial`, `iterative_linear_solver` | `sparse_operators`, `kernel_polynomial`, `iterative_linear_solver` |
| TBQ-093 | kwant | implementable, unverified | `sparse_operators`, `kernel_polynomial`, `iterative_linear_solver` | none |
| TBQ-094 | thouless | implemented | `sparse_operators`, `kernel_polynomial` | none |
| TBQ-094 | pythtb | not applicable | `sparse_operators`, `kernel_polynomial` | `sparse_operators`, `kernel_polynomial` |
| TBQ-094 | kwant | implementable, unverified | `sparse_operators`, `kernel_polynomial` | none |
| TBQ-095 | thouless | implemented | `large_sparse_geometry`, `sparse_operators`, `kernel_polynomial`, `parameterized_models` | none |
| TBQ-095 | pythtb | not applicable | `large_sparse_geometry`, `sparse_operators`, `kernel_polynomial`, `parameterized_models` | `large_sparse_geometry`, `sparse_operators`, `kernel_polynomial` |
| TBQ-095 | kwant | implementable, unverified | `large_sparse_geometry`, `sparse_operators`, `kernel_polynomial`, `parameterized_models` | none |
| TBQ-096 | thouless | not applicable | `model_inference`, `parameterized_models` | `model_inference` |
| TBQ-096 | pythtb | not applicable | `model_inference`, `parameterized_models` | `model_inference` |
| TBQ-096 | kwant | not applicable | `model_inference`, `parameterized_models` | `model_inference` |
| TBQ-097 | thouless | not applicable | `model_inference`, `automatic_differentiation`, `parameterized_models` | `model_inference`, `automatic_differentiation` |
| TBQ-097 | pythtb | not applicable | `model_inference`, `automatic_differentiation`, `parameterized_models` | `model_inference`, `automatic_differentiation` |
| TBQ-097 | kwant | not applicable | `model_inference`, `automatic_differentiation`, `parameterized_models` | `model_inference`, `automatic_differentiation` |
| TBQ-098 | thouless | not applicable | `model_inference`, `parameterized_models` | `model_inference` |
| TBQ-098 | pythtb | not applicable | `model_inference`, `parameterized_models` | `model_inference` |
| TBQ-098 | kwant | not applicable | `model_inference`, `parameterized_models` | `model_inference` |
| TBQ-099 | thouless | not applicable | `model_inference`, `parameterized_models`, `finite_model`, `steady_state_transport` | `model_inference` |
| TBQ-099 | pythtb | not applicable | `model_inference`, `parameterized_models`, `finite_model`, `steady_state_transport` | `model_inference`, `steady_state_transport` |
| TBQ-099 | kwant | not applicable | `model_inference`, `parameterized_models`, `finite_model`, `steady_state_transport` | `model_inference` |
| TBQ-100 | thouless | not applicable | `model_inference`, `parameterized_models` | `model_inference` |
| TBQ-100 | pythtb | not applicable | `model_inference`, `parameterized_models` | `model_inference` |
| TBQ-100 | kwant | not applicable | `model_inference`, `parameterized_models` | `model_inference` |

`Implementable, unverified` is an engineering queue, not verified
scientific coverage. Public witnesses are not held-out validation.
