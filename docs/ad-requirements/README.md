# Domain-first AD companion requirements

This catalog adds exactly one differentiation analysis to each of the 100 immutable scientific questions in [`docs/problems`](../problems/README.md). It was produced before proposing Rust API changes. The existing ten executable AD workflows are evidence witnesses, not the source or boundary of the catalog.

Each companion states the continuous controls, scientific outputs, differentiable formulation, no-AD control, validity boundary, acceptance evidence, and reusable Rust-native capabilities. A companion status never implies that the entire source TBQ is complete.

## Summary

- Scientific anchors: 100
- Questions touched by an existing native AD witness: 14
- Canonical machine-readable matrix: [`benchmark/ad_requirements.json`](../../benchmark/ad_requirements.json)
- Derived capability plan: [`docs/rust-native-ad-capability-plan.md`](../rust-native-ad-capability-plan.md)

AD roles:

- `essential`: 47
- `helpful`: 33
- `conditional`: 18
- `not_central`: 2

AD companion statuses:

- `ad_native_verified`: 14
- `implementable_unverified`: 11
- `missing_ad_rule`: 35
- `missing_forward_physics`: 20
- `conditionally_differentiable`: 18
- `ad_not_central`: 2

The forward status is copied from the independent three-backend domain audit. `missing_forward_physics` and `missing_ad_rule` are intentionally separate: adding a pullback does not substitute for implementing the scientific solver.

## Catalog

| TBQ | Scientific anchor | AD role | Thouless forward | AD companion | Existing witness |
|---|---|---|---|---|---|
| [TBQ-001](01-model-construction/tbq-001-basis-and-generalized-hermiticity-fidelity.md) | Basis and generalized-Hermiticity fidelity | `helpful` | `implemented` | `missing_ad_rule` | — |
| [TBQ-002](01-model-construction/tbq-002-energy-window-and-subspace-fidelity.md) | Energy-window and subspace fidelity | `essential` | `implemented` | `implementable_unverified` | — |
| [TBQ-003](01-model-construction/tbq-003-controlled-hopping-truncation.md) | Controlled hopping truncation | `conditional` | `implemented` | `conditionally_differentiable` | — |
| [TBQ-004](01-model-construction/tbq-004-symmetry-preservation-and-negative-controls.md) | Symmetry preservation and negative controls | `helpful` | `implemented` | `missing_ad_rule` | — |
| [TBQ-005](01-model-construction/tbq-005-transfer-beyond-fitted-structures.md) | Transfer beyond fitted structures | `essential` | `implemented` | `missing_ad_rule` | — |
| [TBQ-006](02-bands-dos-fermiology/tbq-006-degeneracy-safe-band-projectors.md) | Degeneracy-safe band projectors | `essential` | `implemented` | `ad_native_verified` | ad_degenerate_projector |
| [TBQ-007](02-bands-dos-fermiology/tbq-007-density-of-states-state-counting.md) | Density-of-states state counting | `helpful` | `implemented` | `implementable_unverified` | — |
| [TBQ-008](02-bands-dos-fermiology/tbq-008-van-hove-and-flat-band-feature-resolution.md) | Van Hove and flat-band feature resolution | `helpful` | `implemented` | `missing_ad_rule` | — |
| [TBQ-009](02-bands-dos-fermiology/tbq-009-fermi-surface-topology-and-lifshitz-transitions.md) | Fermi-surface topology and Lifshitz transitions | `conditional` | `implemented` | `conditionally_differentiable` | — |
| [TBQ-010](02-bands-dos-fermiology/tbq-010-bloch-and-finite-real-space-spectral-agreement.md) | Bloch and finite-real-space spectral agreement | `helpful` | `implemented` | `missing_ad_rule` | — |
| [TBQ-011](03-magnetic-flux-hofstadter/tbq-011-gauge-covariant-peierls-substitution.md) | Gauge-covariant Peierls substitution | `helpful` | `implemented` | `missing_ad_rule` | — |
| [TBQ-012](03-magnetic-flux-hofstadter/tbq-012-magnetic-translation-and-minimal-unit-cell.md) | Magnetic translation and minimal unit cell | `not_central` | `implemented` | `ad_not_central` | — |
| [TBQ-013](03-magnetic-flux-hofstadter/tbq-013-hofstadter-gap-topology-and-streda-consistency.md) | Hofstadter gap topology and Streda consistency | `helpful` | `implemented` | `missing_ad_rule` | — |
| [TBQ-014](03-magnetic-flux-hofstadter/tbq-014-low-field-landau-level-correspondence.md) | Low-field Landau-level correspondence | `helpful` | `implemented` | `missing_ad_rule` | — |
| [TBQ-015](03-magnetic-flux-hofstadter/tbq-015-rational-approximant-convergence.md) | Rational-approximant convergence | `conditional` | `implemented` | `conditionally_differentiable` | — |
| [TBQ-016](04-bulk-topology/tbq-016-gauge-invariant-bulk-indices.md) | Gauge-invariant bulk indices | `not_central` | `implemented` | `ad_not_central` | — |
| [TBQ-017](04-bulk-topology/tbq-017-topological-phase-boundary-localization.md) | Topological phase-boundary localization | `essential` | `implemented` | `ad_native_verified` | ad_topological_design |
| [TBQ-018](04-bulk-topology/tbq-018-degeneracy-safe-wilson-and-nested-wilson-flow.md) | Degeneracy-safe Wilson and nested Wilson flow | `helpful` | `implemented` | `missing_ad_rule` | — |
| [TBQ-019](04-bulk-topology/tbq-019-agreement-of-independent-topological-diagnostics.md) | Agreement of independent topological diagnostics | `helpful` | `implemented` | `implementable_unverified` | — |
| [TBQ-020](04-bulk-topology/tbq-020-trivial-nearly-gapless-and-basis-adversarial-controls.md) | Trivial, nearly gapless, and basis-adversarial controls | `conditional` | `implemented` | `conditionally_differentiable` | — |
| [TBQ-021](05-boundaries-bulk-boundary/tbq-021-termination-families-from-one-bulk-model.md) | Termination families from one bulk model | `conditional` | `implemented` | `conditionally_differentiable` | — |
| [TBQ-022](05-boundaries-bulk-boundary/tbq-022-boundary-state-localization-and-finite-size-splitting.md) | Boundary-state localization and finite-size splitting | `helpful` | `implemented` | `implementable_unverified` | — |
| [TBQ-023](05-boundaries-bulk-boundary/tbq-023-finite-spectrum-and-surface-green-function-agreement.md) | Finite-spectrum and surface-Green-function agreement | `essential` | `implemented` | `ad_native_verified` | ad_surface_green_implicit |
| [TBQ-024](05-boundaries-bulk-boundary/tbq-024-conditional-bulk-boundary-correspondence.md) | Conditional bulk-boundary correspondence | `conditional` | `implemented` | `conditionally_differentiable` | — |
| [TBQ-025](05-boundaries-bulk-boundary/tbq-025-geometry-family-generalization.md) | Geometry-family generalization | `essential` | `implemented` | `missing_ad_rule` | — |
| [TBQ-026](06-quantum-geometry-response/tbq-026-gauge-covariance-of-geometric-tensors.md) | Gauge covariance of geometric tensors | `essential` | `implemented` | `ad_native_verified` | ad_quantum_metric |
| [TBQ-027](06-quantum-geometry-response/tbq-027-competing-nonlinear-hall-mechanisms.md) | Competing nonlinear Hall mechanisms | `essential` | `implemented` | `missing_ad_rule` | — |
| [TBQ-028](06-quantum-geometry-response/tbq-028-symmetry-forbidden-nonlinear-tensor-components.md) | Symmetry-forbidden nonlinear tensor components | `helpful` | `implemented` | `missing_ad_rule` | — |
| [TBQ-029](06-quantum-geometry-response/tbq-029-fermi-surface-and-derivative-convergence.md) | Fermi-surface and derivative convergence | `essential` | `missing_capability` | `ad_native_verified` | ad_quantum_metric |
| [TBQ-030](06-quantum-geometry-response/tbq-030-zero-chern-nonlinear-bulk-boundary-workflow.md) | Zero-Chern nonlinear bulk-boundary workflow | `essential` | `implemented` | `ad_native_verified` | ad_topological_design |
| [TBQ-031](07-disorder-localization/tbq-031-reproducible-disorder-ensembles.md) | Reproducible disorder ensembles | `helpful` | `implemented` | `missing_ad_rule` | — |
| [TBQ-032](07-disorder-localization/tbq-032-cross-observable-localization-diagnosis.md) | Cross-observable localization diagnosis | `essential` | `missing_capability` | `missing_forward_physics` | — |
| [TBQ-033](07-disorder-localization/tbq-033-finite-size-scaling-of-mobility-edges.md) | Finite-size scaling of mobility edges | `essential` | `missing_capability` | `missing_forward_physics` | — |
| [TBQ-034](07-disorder-localization/tbq-034-topological-mobility-gap.md) | Topological mobility gap | `helpful` | `missing_capability` | `missing_forward_physics` | — |
| [TBQ-035](07-disorder-localization/tbq-035-statistical-generalization-across-disorder-families.md) | Statistical generalization across disorder families | `essential` | `missing_capability` | `missing_forward_physics` | — |
| [TBQ-036](08-open-transport/tbq-036-lead-modes-and-self-energy-calibration.md) | Lead modes and self-energy calibration | `essential` | `implemented` | `ad_native_verified` | ad_surface_green_implicit, ad_lead_device_sensitivity |
| [TBQ-037](08-open-transport/tbq-037-scattering-conservation-and-local-continuity.md) | Scattering conservation and local continuity | `helpful` | `implemented` | `implementable_unverified` | — |
| [TBQ-038](08-open-transport/tbq-038-transmission-local-density-and-finite-temperature-noise.md) | Transmission, local density, and finite-temperature noise | `essential` | `implemented` | `missing_ad_rule` | — |
| [TBQ-039](08-open-transport/tbq-039-numerical-stability-for-long-evanescent-devices.md) | Numerical stability for long evanescent devices | `helpful` | `implemented` | `implementable_unverified` | — |
| [TBQ-040](08-open-transport/tbq-040-generalization-across-contact-families.md) | Generalization across contact families | `essential` | `implemented` | `ad_native_verified` | ad_inverse_transport, ad_lead_device_sensitivity |
| [TBQ-041](09-superconducting-bdg/tbq-041-nambu-convention-and-particle-hole-symmetry.md) | Nambu convention and particle-hole symmetry | `helpful` | `implemented` | `missing_ad_rule` | — |
| [TBQ-042](09-superconducting-bdg/tbq-042-phase-resolved-andreev-spectrum-and-josephson-current.md) | Phase-resolved Andreev spectrum and Josephson current | `essential` | `implemented` | `implementable_unverified` | — |
| [TBQ-043](09-superconducting-bdg/tbq-043-majorana-versus-trivial-near-zero-modes.md) | Majorana versus trivial near-zero modes | `helpful` | `implemented` | `missing_ad_rule` | — |
| [TBQ-044](09-superconducting-bdg/tbq-044-fragility-of-four-pi-josephson-response.md) | Fragility of four-pi Josephson response | `conditional` | `missing_capability` | `conditionally_differentiable` | — |
| [TBQ-045](09-superconducting-bdg/tbq-045-continuum-to-lattice-bdg-convergence.md) | Continuum-to-lattice BdG convergence | `helpful` | `implemented` | `missing_ad_rule` | — |
| [TBQ-046](10-non-hermitian/tbq-046-biorthogonal-eigenvectors-and-residuals.md) | Biorthogonal eigenvectors and residuals | `essential` | `implemented` | `missing_ad_rule` | — |
| [TBQ-047](10-non-hermitian/tbq-047-exceptional-point-order-and-sensitivity.md) | Exceptional-point order and sensitivity | `conditional` | `implemented` | `conditionally_differentiable` | — |
| [TBQ-048](10-non-hermitian/tbq-048-point-gap-line-gap-and-non-bloch-invariants.md) | Point-gap, line-gap, and non-Bloch invariants | `conditional` | `missing_capability` | `conditionally_differentiable` | — |
| [TBQ-049](10-non-hermitian/tbq-049-periodic-open-mismatch-and-skin-localization.md) | Periodic-open mismatch and skin localization | `essential` | `implemented` | `missing_ad_rule` | — |
| [TBQ-050](10-non-hermitian/tbq-050-non-hermitian-family-generalization.md) | Non-Hermitian family generalization | `essential` | `implemented` | `missing_ad_rule` | — |
| [TBQ-051](11-floquet-dynamics/tbq-051-equivalent-representations-of-a-drive.md) | Equivalent representations of a drive | `helpful` | `not_applicable` | `missing_forward_physics` | — |
| [TBQ-052](11-floquet-dynamics/tbq-052-quasienergy-branch-and-time-origin-consistency.md) | Quasienergy branch and time-origin consistency | `conditional` | `not_applicable` | `conditionally_differentiable` | — |
| [TBQ-053](11-floquet-dynamics/tbq-053-sambe-direct-propagation-and-high-frequency-agreement.md) | Sambe, direct-propagation, and high-frequency agreement | `helpful` | `not_applicable` | `missing_forward_physics` | — |
| [TBQ-054](11-floquet-dynamics/tbq-054-dynamical-pumping-and-frequency-conversion.md) | Dynamical pumping and frequency conversion | `essential` | `not_applicable` | `missing_forward_physics` | — |
| [TBQ-055](11-floquet-dynamics/tbq-055-time-step-and-harmonic-cutoff-holdout.md) | Time-step and harmonic-cutoff holdout | `conditional` | `not_applicable` | `conditionally_differentiable` | — |
| [TBQ-056](12-interactions-self-consistency/tbq-056-interaction-and-double-counting-declaration.md) | Interaction and double-counting declaration | `helpful` | `not_applicable` | `missing_forward_physics` | — |
| [TBQ-057](12-interactions-self-consistency/tbq-057-self-consistency-robustness-and-metastability.md) | Self-consistency robustness and metastability | `essential` | `not_applicable` | `missing_forward_physics` | — |
| [TBQ-058](12-interactions-self-consistency/tbq-058-thermodynamic-comparison-of-competing-orders.md) | Thermodynamic comparison of competing orders | `conditional` | `not_applicable` | `conditionally_differentiable` | — |
| [TBQ-059](12-interactions-self-consistency/tbq-059-conservation-and-unbroken-symmetry-checks.md) | Conservation and unbroken-symmetry checks | `helpful` | `not_applicable` | `missing_forward_physics` | — |
| [TBQ-060](12-interactions-self-consistency/tbq-060-validation-against-small-exact-systems.md) | Validation against small exact systems | `helpful` | `not_applicable` | `missing_forward_physics` | — |
| [TBQ-061](13-moire-strain-supercells/tbq-061-commensurate-and-reconstructed-geometry.md) | Commensurate and reconstructed geometry | `conditional` | `implemented` | `conditionally_differentiable` | — |
| [TBQ-062](13-moire-strain-supercells/tbq-062-geometry-dependent-coupling-laws.md) | Geometry-dependent coupling laws | `essential` | `implemented` | `missing_ad_rule` | — |
| [TBQ-063](13-moire-strain-supercells/tbq-063-continuum-atomistic-correspondence.md) | Continuum-atomistic correspondence | `essential` | `missing_capability` | `missing_forward_physics` | — |
| [TBQ-064](13-moire-strain-supercells/tbq-064-sparse-observables-in-giant-supercells.md) | Sparse observables in giant supercells | `essential` | `missing_capability` | `missing_forward_physics` | — |
| [TBQ-065](13-moire-strain-supercells/tbq-065-structural-family-transfer.md) | Structural-family transfer | `essential` | `missing_capability` | `missing_forward_physics` | — |
| [TBQ-066](14-magnetism-spin-orbital/tbq-066-spinor-texture-construction-and-covariance.md) | Spinor texture construction and covariance | `essential` | `implemented` | `missing_ad_rule` | — |
| [TBQ-067](14-magnetism-spin-orbital/tbq-067-charge-spin-orbital-current-and-torque-continuity.md) | Charge, spin, orbital-current, and torque continuity | `essential` | `implemented` | `missing_ad_rule` | — |
| [TBQ-068](14-magnetism-spin-orbital/tbq-068-mechanism-resolved-hall-response.md) | Mechanism-resolved Hall response | `essential` | `implemented` | `missing_ad_rule` | — |
| [TBQ-069](14-magnetism-spin-orbital/tbq-069-texture-resolution-and-adiabatic-convergence.md) | Texture-resolution and adiabatic convergence | `helpful` | `implemented` | `missing_ad_rule` | — |
| [TBQ-070](14-magnetism-spin-orbital/tbq-070-magnetic-family-generalization.md) | Magnetic-family generalization | `essential` | `implemented` | `missing_ad_rule` | — |
| [TBQ-071](15-optical-thermoelectric/tbq-071-hamiltonian-consistent-response-operators.md) | Hamiltonian-consistent response operators | `essential` | `implemented` | `missing_ad_rule` | — |
| [TBQ-072](15-optical-thermoelectric/tbq-072-optical-spectral-sum-and-time-domain-agreement.md) | Optical spectral-sum and time-domain agreement | `essential` | `missing_capability` | `missing_forward_physics` | — |
| [TBQ-073](15-optical-thermoelectric/tbq-073-thermoelectric-and-onsager-relations.md) | Thermoelectric and Onsager relations | `essential` | `implemented` | `missing_ad_rule` | — |
| [TBQ-074](15-optical-thermoelectric/tbq-074-broadening-and-integration-convergence.md) | Broadening and integration convergence | `helpful` | `missing_capability` | `missing_forward_physics` | — |
| [TBQ-075](15-optical-thermoelectric/tbq-075-method-transfer-from-exact-to-large-sparse-systems.md) | Method transfer from exact to large sparse systems | `helpful` | `implemented` | `implementable_unverified` | — |
| [TBQ-076](16-aperiodic-amorphous-fractal/tbq-076-translation-free-geometric-construction.md) | Translation-free geometric construction | `conditional` | `implemented` | `conditionally_differentiable` | — |
| [TBQ-077](16-aperiodic-amorphous-fractal/tbq-077-singular-spectral-measures-and-localization.md) | Singular spectral measures and localization | `helpful` | `missing_capability` | `missing_forward_physics` | — |
| [TBQ-078](16-aperiodic-amorphous-fractal/tbq-078-real-space-topology-without-translation-symmetry.md) | Real-space topology without translation symmetry | `helpful` | `missing_capability` | `missing_forward_physics` | — |
| [TBQ-079](16-aperiodic-amorphous-fractal/tbq-079-approximant-and-multifractal-scaling.md) | Approximant and multifractal scaling | `conditional` | `missing_capability` | `conditionally_differentiable` | — |
| [TBQ-080](16-aperiodic-amorphous-fractal/tbq-080-geometry-family-generalization.md) | Geometry-family generalization | `essential` | `missing_capability` | `missing_forward_physics` | — |
| [TBQ-081](17-defects-interfaces/tbq-081-provenance-preserving-structural-defects.md) | Provenance-preserving structural defects | `conditional` | `implemented` | `conditionally_differentiable` | — |
| [TBQ-082](17-defects-interfaces/tbq-082-defect-specific-local-chemistry.md) | Defect-specific local chemistry | `essential` | `implemented` | `missing_ad_rule` | — |
| [TBQ-083](17-defects-interfaces/tbq-083-embedding-and-supercell-agreement.md) | Embedding and supercell agreement | `helpful` | `implemented` | `implementable_unverified` | — |
| [TBQ-084](17-defects-interfaces/tbq-084-local-state-and-transport-consequences.md) | Local-state and transport consequences | `essential` | `implemented` | `missing_ad_rule` | — |
| [TBQ-085](17-defects-interfaces/tbq-085-defect-family-generalization.md) | Defect-family generalization | `essential` | `implemented` | `missing_ad_rule` | — |
| [TBQ-086](18-multiscale-validation/tbq-086-one-physical-question-across-scales.md) | One physical question across scales | `helpful` | `implemented` | `implementable_unverified` | — |
| [TBQ-087](18-multiscale-validation/tbq-087-explicit-representation-mapping.md) | Explicit representation mapping | `essential` | `implemented` | `missing_ad_rule` | — |
| [TBQ-088](18-multiscale-validation/tbq-088-gauge-invariant-observable-comparison.md) | Gauge-invariant observable comparison | `helpful` | `implemented` | `implementable_unverified` | — |
| [TBQ-089](18-multiscale-validation/tbq-089-discrepancy-decomposition.md) | Discrepancy decomposition | `essential` | `implemented` | `missing_ad_rule` | — |
| [TBQ-090](18-multiscale-validation/tbq-090-external-family-validation.md) | External-family validation | `essential` | `implemented` | `missing_ad_rule` | — |
| [TBQ-091](19-scientific-scale-numerics/tbq-091-sparse-only-production-path.md) | Sparse-only production path | `helpful` | `missing_capability` | `missing_forward_physics` | — |
| [TBQ-092](19-scientific-scale-numerics/tbq-092-scalable-solver-portfolio.md) | Scalable solver portfolio | `conditional` | `missing_capability` | `conditionally_differentiable` | — |
| [TBQ-093](19-scientific-scale-numerics/tbq-093-separated-numerical-error-budget.md) | Separated numerical error budget | `essential` | `implemented` | `missing_ad_rule` | — |
| [TBQ-094](19-scientific-scale-numerics/tbq-094-accuracy-preserving-time-and-memory-scaling.md) | Accuracy-preserving time and memory scaling | `essential` | `implemented` | `ad_native_verified` | ad_sparse_adjoint_scaling, ad_robust_kpm_design |
| [TBQ-095](19-scientific-scale-numerics/tbq-095-reproducible-transition-from-exact-to-production-scale.md) | Reproducible transition from exact to production scale | `conditional` | `implemented` | `conditionally_differentiable` | — |
| [TBQ-096](20-inference-inverse-design/tbq-096-constrained-multi-observable-parameter-inference.md) | Constrained multi-observable parameter inference | `essential` | `not_applicable` | `ad_native_verified` | ad_spectral_recovery |
| [TBQ-097](20-inference-inverse-design/tbq-097-gradient-verification-through-spectral-calculations.md) | Gradient verification through spectral calculations | `essential` | `not_applicable` | `ad_native_verified` | ad_degenerate_projector, ad_sparse_adjoint_scaling |
| [TBQ-098](20-inference-inverse-design/tbq-098-identifiability-and-predictive-calibration.md) | Identifiability and predictive calibration | `essential` | `not_applicable` | `ad_native_verified` | ad_identifiability |
| [TBQ-099](20-inference-inverse-design/tbq-099-independent-forward-validation-of-inverse-designs.md) | Independent forward validation of inverse designs | `essential` | `not_applicable` | `ad_native_verified` | ad_spectral_recovery, ad_inverse_transport |
| [TBQ-100](20-inference-inverse-design/tbq-100-out-of-family-inference-holdout.md) | Out-of-family inference holdout | `essential` | `not_applicable` | `ad_native_verified` | ad_robust_kpm_design |
