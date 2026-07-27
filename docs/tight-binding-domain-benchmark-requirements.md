# Tight-Binding Domain Benchmark Requirements

Status: research-derived benchmark specification

Evidence snapshot: 2026-07-27

Scope: scientific tight-binding workflows, independent of any language or API

## 1. Purpose

This document defines one hundred requirements for evaluating general-purpose
tight-binding scientific software. The requirements were selected from domain
research questions first. They were not selected from the current Thouless
implementation, the PythTB or Kwant interfaces, or any Rust interface.

The benchmark asks whether a system can answer scientifically meaningful
questions with controlled error, appropriate counterexamples, and
research-scale inputs. Only after the benchmark is fixed may its workflows be
used to derive software capabilities and API requirements.

The benchmark covers a wider scientific domain than the current Thouless
project. Inclusion here is therefore not an implementation-completeness claim
or an automatic commitment to a particular release.

## 2. Evidence and derivation method

The LKM snapshot contains:

- 846 deduplicated public research-question or claim nodes;
- 835 deduplicated papers in the discovery results;
- 250 retrieved reasoning chains from 243 papers, for 1,048 unique papers
  across discovery and reasoning results; and
- 21 discovery searches spanning model construction, topology, transport,
  response, disorder, dynamics, interactions, complex geometry, numerical
  scale, and inverse problems.

LKM nodes are used as research leads and as sources of proposed observables,
failure modes, and validation strategies. They are not treated as proof that a
claim is true or novel. Raw responses and their provenance are retained in
[`evidence/lkm/2026-07-27-tight-binding-domain`](../evidence/lkm/2026-07-27-tight-binding-domain/README.md).

Each benchmark suite was derived in this order:

1. identify a domain research question;
2. identify the physical object, perturbations, and target observables;
3. define a case family rather than one frozen fixture;
4. define an independent oracle, invariant, or convergence relation;
5. define held-out axes that prevent answer or fixture fitting; and
6. only then record the capabilities implied for future software design.

## 3. Benchmark-wide rules

### 3.1 Unit of evaluation

Every benchmark case must publish:

- the scientific question and regime of validity;
- the Hamiltonian or model-construction recipe, units, basis, and provenance;
- the requested observables and conventions;
- an independent reference or exact relation;
- accuracy, convergence, and resource criteria; and
- the axes used to form public development cases and isolated held-out cases.

### 3.2 Acceptance classes

The suite author must assign every observable one of these acceptance classes:

- **Exact:** analytic result, integer invariant, algebraic identity, or
  conservation law;
- **Reference:** independently generated high-accuracy numerical, continuum,
  first-principles, or experimental reference with a declared uncertainty;
- **Convergence:** no unique scalar truth is available, so the result must
  converge under a declared refinement sequence and agree across two
  independent formulations where possible;
- **Scaling:** accuracy must be retained while a declared time, memory, and
  problem-size envelope is measured.

Numerical tolerances must follow the physical scale, reference uncertainty, and
conditioning of each case. A benchmark may not silently relax tolerances to
make an implementation pass.

### 3.3 Anti-overfitting boundary

Public and held-out sets must be split by model family or scientific regime,
not merely by random parameter rows from the same fixture. Held-out data should
vary lattice family, orbital content, symmetry class, boundary termination,
contact geometry, disorder distribution, system size, or perturbation family
as appropriate. A solution that recognizes case identifiers or returns stored
answers is invalid.

## 4. One hundred domain requirements

### Suite 01 — Low-energy model construction and provenance

**Scientific question.** Can a localized-orbital Hamiltonian preserve the
low-energy information needed for subsequent many-body, transport, and response
studies?

**Benchmark family and oracle.** Build orthogonal and non-orthogonal models
from analytic, Slater-Koster, and Wannier-like inputs. Compare bands,
subspace projectors, orbital characters, and symmetries with an independently
prepared reference over declared energy and momentum windows.

**LKM seeds.** `gcn_c63bb5a9ee604e87` (paper `966947791895003140`),
`gcn_7236e40f8a0f46dd` (paper `1251845489087741964`), and reasoning chain
`867765819981955534_1`.

- **TB-REQ-001 — Physical basis fidelity.** The benchmark shall include
  multi-orbital models with spin, spin-orbit coupling, and optional overlap
  matrices, and shall require the submitted calculation to preserve the stated
  basis ordering, units, lattice translations, and Hermiticity or generalized
  Hermiticity.
- **TB-REQ-002 — Energy-window fidelity.** The benchmark shall compare band
  energies and gauge-invariant subspace projectors throughout a declared
  momentum and energy window, rather than at a few high-symmetry points only.
- **TB-REQ-003 — Controlled truncation.** The benchmark shall provide a
  hopping-range or sparsification ladder and require an error-versus-cost curve
  for bands, orbital weights, and at least one downstream observable.
- **TB-REQ-004 — Symmetry preservation.** The benchmark shall require explicit
  residuals for all declared unitary and antiunitary symmetries and shall
  include a deliberately symmetry-breaking perturbation as a negative control.
- **TB-REQ-005 — Transfer outside the fitted case.** Model parameters or
  construction rules shall be tested on held-out structures, strain states, or
  momentum regions that were not used during fitting.

### Suite 02 — Bands, density of states, and Fermiology

**Scientific question.** Can the electronic structure locate the band
features that control instabilities, carriers, and low-energy experiments?

**Benchmark family and oracle.** Use analytic lattices and material-derived
multi-orbital models containing degeneracies, flat bands, ordinary and
higher-order van Hove singularities, and Lifshitz transitions. Compare against
analytic limits and independently converged integration.

**LKM seeds.** `gcn_4fb925994ab54a2e` (paper `1238105795019669508`),
`gcn_b7cdd564aa464099` (paper `995573268746338319`), and
`gcn_7296c8f60c964c18` (paper `812469412236886018`).

- **TB-REQ-006 — Degenerate band structure.** The benchmark shall require
  eigenvalues and composite-subspace projectors along paths and meshes,
  including exact and near degeneracies where individual eigenvector gauges
  are not valid comparison objects.
- **TB-REQ-007 — State-counting density of states.** Computed total and
  projected densities of states shall satisfy the integrated state-count sum
  rule and converge with broadening, mesh, or polynomial order.
- **TB-REQ-008 — Singular-feature resolution.** The benchmark shall require
  the energy, type, and uncertainty of flat-band features and ordinary or
  higher-order van Hove singularities, not only a plotted density-of-states
  curve.
- **TB-REQ-009 — Fermi-surface topology.** The benchmark shall track pockets,
  carrier character, and Lifshitz transitions across chemical potential,
  pressure, strain, or hopping parameters.
- **TB-REQ-010 — Cross-representation agreement.** Periodic momentum-space
  and sufficiently large real-space formulations shall agree for bulk spectral
  observables within their declared finite-size and broadening errors.

### Suite 03 — Magnetic fields, Landau fans, and Hofstadter physics

**Scientific question.** Can lattice models describe magnetic flux without
introducing gauge- or unit-cell-dependent physics?

**Benchmark family and oracle.** Exercise square, triangular, honeycomb, and
topological bands under rational and real-space flux, including long-range
hoppings. Compare gauge-equivalent spectra, Diophantine labels, Chern numbers,
and low-field Landau-level limits.

**LKM seeds.** `gcn_7ad8b68bedaa49b5` (paper `867757609485074549`),
`gcn_75ecf3d114d74c69` (paper `867746837434466703`), and
`gcn_7cc10d3d9e354922` (paper `943750642852168355`).

- **TB-REQ-011 — Gauge-covariant flux insertion.** The benchmark shall
  include multiple vector-potential gauges and require gauge-equivalent
  spectra and gauge-invariant local observables for arbitrary-range hoppings.
- **TB-REQ-012 — Magnetic translation structure.** Rational-flux cases shall
  verify the expected magnetic unit-cell size, projective translation
  relations, and band multiplicity without assuming a particular gauge.
- **TB-REQ-013 — Topological gap labelling.** Hofstadter gaps shall be checked
  using independently computed Chern numbers and the appropriate gap-labelling
  or Streda relation.
- **TB-REQ-014 — Low-field correspondence.** Lattice Landau fans shall
  approach independently derived continuum or semiclassical levels in a
  declared flux regime while retaining lattice corrections outside it.
- **TB-REQ-015 — Flux and approximant convergence.** The benchmark shall test
  sequences of rational approximants, system sizes, and boundary conditions,
  including held-out flux denominators and hopping ranges.

### Suite 04 — Bulk topology and phase diagrams

**Scientific question.** Can a calculation distinguish topological phases and
locate their transitions without relying on a favored gauge or diagnostic?

**Benchmark family and oracle.** Include trivial and topological insulators,
semimetal nodes, time-reversal systems, crystalline phases, and gap-closing
transitions. Use analytic invariants where available and cross-check Wilson,
real-space, and response-based diagnostics.

**LKM seeds.** `gcn_e5dd806871ea4f6f` (paper `814532884890124290`),
`gcn_b761eeec869744ab` (paper `812536452305911808`), and
`gcn_177994dd04734e1e` (paper `966036046494040252`).

- **TB-REQ-016 — Gauge-invariant bulk indices.** The benchmark shall require
  Chern, time-reversal, winding, or crystalline indices using composite
  occupied subspaces and shall test invariance under random basis gauges.
- **TB-REQ-017 — Phase-boundary localization.** Parameter sweeps shall locate
  gap closings and changes of invariant with an uncertainty tied to mesh or
  root-finding resolution.
- **TB-REQ-018 — Degeneracy-safe Wilson analysis.** Wilson spectra and nested
  constructions shall remain well defined under band crossings inside the
  selected subspace and under unitary rotations within degenerate manifolds.
- **TB-REQ-019 — Independent diagnostic agreement.** At least two
  mathematically independent diagnostics shall agree in their common regime,
  and the benchmark shall include cases where one diagnostic's assumptions
  fail.
- **TB-REQ-020 — Trivial and adversarial controls.** Held-out cases shall
  include atomic limits, nearly closed gaps, symmetry-broken perturbations, and
  topologically equivalent Hamiltonians in different bases.

### Suite 05 — Boundaries, higher-order topology, and bulk-boundary relations

**Scientific question.** Which boundary phenomena genuinely follow from the
bulk, and which depend on termination, filling, or finite geometry?

**Benchmark family and oracle.** Construct ribbons, flakes, tubes, corners, and
hinges from the same bulk Hamiltonian while varying termination and size.
Compare finite diagonalization, boundary Green functions, local charge, and
bulk predictions.

**LKM seeds.** `gcn_79c7aedbe338479f` (paper `817336503179935746`),
`gcn_845407cac1554d64` (paper `947196961813954948`), and reasoning chain
`1244230567847788545_3`.

- **TB-REQ-021 — Explicit termination families.** The benchmark shall derive
  multiple crystallographically valid terminations from one bulk model and
  preserve the source-site and source-orbital provenance of every boundary
  degree of freedom.
- **TB-REQ-022 — Boundary-state characterization.** Candidate edge, corner,
  and hinge states shall be reported with energy, localization profile,
  finite-size splitting, and participation measure rather than by eigenvalue
  alone.
- **TB-REQ-023 — Boundary observable cross-check.** Spectral functions,
  finite-sample eigenstates, and local charge or current shall be compared in
  geometries where the formulations should agree.
- **TB-REQ-024 — Conditional bulk-boundary claims.** The benchmark shall score
  agreement only when the hypotheses of the relevant correspondence hold and
  shall accept physically correct termination-dependent absence, splitting, or
  masking of boundary states.
- **TB-REQ-025 — Held-out geometry generalization.** Hidden cases shall change
  termination, corner angle, aspect ratio, and weak boundary disorder, not just
  the number of repeated cells.

### Suite 06 — Quantum geometry and nonlinear response

**Scientific question.** Can observable nonlinear response be attributed to
the correct quantum-geometric mechanism, including cases with zero Chern
number?

**Benchmark family and oracle.** Use symmetry-controlled Dirac and lattice
families with tunable inversion, time-reversal, and rotational symmetry.
Evaluate geometric tensors and all competing second-order contributions across
Fermi energy and deformation.

**LKM seeds.** `gcn_625da35d83a54c6a` (paper `1225780552007680004`),
`gcn_3e90ac9901294fc5` (paper `1225780552007680003`), and reasoning chain
`1159462780185608201_8`.

- **TB-REQ-026 — Geometric-tensor covariance.** Berry curvature, quantum
  metric, and their subspace forms shall be invariant under allowed band-gauge
  rotations and shall satisfy positivity and symmetry identities.
- **TB-REQ-027 — Competing mechanisms.** A nonlinear Hall case shall compute
  Berry-curvature-dipole and quantum-metric contributions separately, even when
  symmetry is expected to suppress one of them.
- **TB-REQ-028 — Response identities.** Tensor components forbidden by the
  model's symmetries, including the relevant longitudinal quantum-metric
  identity, shall vanish at the rate expected from numerical convergence.
- **TB-REQ-029 — Fermi-surface convergence.** Response curves versus chemical
  potential, temperature, and deformation shall include convergence in
  momentum resolution, derivative evaluation, and Fermi-surface broadening.
- **TB-REQ-030 — Zero-Chern nonlinear bulk-boundary workflow.** At least one
  model family with zero Chern number and finite nonlinear Hall response shall
  reuse the identical Hamiltonian across bulk geometry, finite boundaries, and
  open transport; held-out cases shall vary symmetry-breaking direction and
  termination so that no protected edge state is assumed.

### Suite 07 — Disorder, localization, and mobility edges

**Scientific question.** Which states remain extended, localized, or
topologically conducting as disorder changes?

**Benchmark family and oracle.** Apply multiple disorder ensembles to ordinary,
spin-orbit, topological, non-Hermitian, and non-Euclidean lattices. Use
finite-size scaling of localization and transport observables.

**LKM seeds.** `gcn_1b045590a2ba409d` (paper `812638298013958144`),
`gcn_e09795d6cb3646fe` (paper `1116523427977494535`), and reasoning chain
`1066570812665888771_2`.

- **TB-REQ-031 — Declared disorder ensembles.** The benchmark shall specify
  distributions, correlations, affected matrix elements, seeds, and ensemble
  sizes for onsite, hopping, vacancy, and spatially correlated disorder.
- **TB-REQ-032 — Multiple localization observables.** Density of states,
  participation ratios, localization length or level statistics, and
  conductance shall be jointly evaluated where applicable.
- **TB-REQ-033 — Mobility-edge scaling.** Mobility edges shall be inferred
  from a size-dependent crossing or scaling analysis with uncertainty, not
  from a fixed participation-ratio threshold.
- **TB-REQ-034 — Mobility-gap topology.** Cases claiming a topological
  mobility gap shall demonstrate localized bulk states and robust boundary
  transport or an appropriate real-space invariant in the same disorder
  window.
- **TB-REQ-035 — Statistical generalization.** Acceptance shall include
  confidence intervals and held-out disorder distributions, correlation
  lengths, geometries, and random seeds.

### Suite 08 — Open-system transport and scattering

**Scientific question.** Can steady-state calculations predict transmission,
noise, and local observables for realistic devices without violating
conservation laws or becoming unstable?

**Benchmark family and oracle.** Connect multi-orbital finite devices to
periodic leads with propagating and evanescent modes. Include long devices,
magnetic fields, superconducting interfaces, disorder, and multiterminal
geometries.

**LKM seeds.** `gcn_da2e995d149b4da4` (paper `867769035654168759`),
`gcn_8d5107693c024b90` (paper `867758509083591444`), and reasoning chain
`811903549792321536_1`.

- **TB-REQ-036 — Lead and self-energy correctness.** Surface Green functions,
  modes, velocities, broadenings, and self-energies shall agree with analytic
  leads or an independent solver, including band edges and evanescent sectors.
- **TB-REQ-037 — Scattering conservation.** Scattering matrices shall satisfy
  unitarity or the appropriate flux balance, while local density, bond current,
  and source terms satisfy the discrete continuity equation.
- **TB-REQ-038 — Complete transport observables.** The benchmark shall include
  conductance, transmission eigenvalues, local density of states, scattering
  states, and finite-temperature auto- and cross-correlated noise where
  physically defined.
- **TB-REQ-039 — Long-device stability.** Results for long or strongly
  evanescent systems shall remain stable under device partitioning and shall
  avoid the exponential numerical instability of naive transfer-matrix
  multiplication.
- **TB-REQ-040 — Contact-family holdout.** Hidden cases shall change lead
  orientation, cross-section, orbital matching, contact transparency, terminal
  count, and disorder rather than only device length.

### Suite 09 — Superconducting BdG and Majorana systems

**Scientific question.** Can lattice BdG calculations distinguish ordinary
Andreev physics from robust topological superconducting signatures?

**Benchmark family and oracle.** Include normal-superconductor and Josephson
junctions, trivial and topological wires, phase bias, disorder, and
continuum-to-lattice discretizations. Compare analytic short-junction limits
and independent BdG solvers.

**LKM seeds.** `gcn_c034d6be7a204627` (paper `867769623435543500`),
`gcn_b9f13a7153b94880` (paper `817335361834319875`), and
`gcn_0623154216a444ed` (paper `817404425080406019`).

- **TB-REQ-041 — Nambu convention and particle-hole symmetry.** The benchmark
  shall declare Nambu ordering and counting conventions and require the BdG
  Hamiltonian and observables to satisfy particle-hole constraints.
- **TB-REQ-042 — Phase-resolved Andreev spectrum.** Andreev levels and
  Josephson current shall be computed across phase, temperature, and
  transparency and compared with analytic limits where available.
- **TB-REQ-043 — Majorana discrimination.** A zero-mode claim shall combine a
  bulk invariant, particle-hole properties, spatial separation or
  localization, and finite-size splitting, with trivial near-zero states as
  negative controls.
- **TB-REQ-044 — Fragility and parity regimes.** The benchmark shall vary
  disorder, poisoning or parity assumptions, temperature, and quench protocol
  to distinguish equilibrium, transient, \(2\pi\), and \(4\pi\) responses.
- **TB-REQ-045 — Discretization and family holdout.** Continuum and lattice
  models shall agree in a controlled discretization limit, while held-out
  junction dimensions, pairing symmetries, and contact structures test
  transfer.

### Suite 10 — Non-Hermitian spectra and topology

**Scientific question.** Can open or dissipative lattice physics be computed
when complex spectra invalidate Hermitian bulk-band intuition?

**Benchmark family and oracle.** Include asymmetric hopping, gain/loss,
exceptional points, point and line gaps, skin effects, and disorder under both
periodic and open boundaries.

**LKM seeds.** `gcn_130f99edf2fc49a5` (paper `1147866257039556623`),
`gcn_61de6af0dab44776` (paper `867771125713601288`), and reasoning chain
`867752662542582493_2`.

- **TB-REQ-046 — Biorthogonal spectral data.** The benchmark shall require
  complex eigenvalues and consistently paired left and right eigenvectors,
  including residuals and biorthogonality diagnostics.
- **TB-REQ-047 — Defectiveness and sensitivity.** Exceptional points shall be
  identified using eigenvector coalescence or rank information and accompanied
  by condition-number or pseudospectral sensitivity.
- **TB-REQ-048 — Gap-appropriate invariants.** Point-gap, line-gap, and
  non-Bloch invariants shall be used only in their valid regimes and checked
  against analytic winding examples.
- **TB-REQ-049 — Periodic-open spectral mismatch.** The benchmark shall
  compare periodic and open spectra, generalized Brillouin-zone predictions,
  and spatial skin localization in the same model.
- **TB-REQ-050 — Non-Hermitian holdout.** Hidden cases shall vary boundary
  orientation, gain/loss pattern, hopping nonreciprocity, exceptional-point
  order, and disorder.

### Suite 11 — Floquet and time-dependent dynamics

**Scientific question.** Can driven lattice calculations separate genuine
nonequilibrium phases and observables from harmonic or time-step artifacts?

**Benchmark family and oracle.** Drive analytic and material-inspired models
with one or multiple frequencies, weak and strong amplitudes, resonant and
high-frequency regimes, and adiabatic pumping cycles.

**LKM seeds.** `gcn_7d5c22f3ec22410d` (paper `813093316601053184`),
`gcn_da29fc093cae4f5e` (paper `1162365540585439237`), and
`gcn_69c35496847846eb` (paper `867763562716595086`).

- **TB-REQ-051 — General drive representation.** The benchmark shall include
  piecewise, harmonic, pulsed, and incommensurate multi-frequency drives with
  explicit phases, gauges, and time origins.
- **TB-REQ-052 — Quasienergy and branch consistency.** Floquet operators,
  quasienergies, micromotion, and state matching shall be invariant under
  equivalent time origins and consistent across quasienergy branch cuts.
- **TB-REQ-053 — Independent evolution formulations.** Sambe-space
  diagonalization, direct time propagation, and high-frequency expansion shall
  agree in their common regimes and expose their breakdown outside them.
- **TB-REQ-054 — Dynamical observables.** The benchmark shall test pumping,
  occupations, currents, return probabilities, or topological frequency
  conversion rather than quasienergy spectra alone.
- **TB-REQ-055 — Drive-convergence holdout.** Acceptance shall vary time step,
  harmonic cutoff, total cycles, switching protocol, and held-out frequency
  ratios and waveform families.

### Suite 12 — Interactions and self-consistent lattice approximations

**Scientific question.** Can an effective interacting model produce
well-defined, reproducible phases without hiding double counting or
metastability?

**Benchmark family and oracle.** Use Hubbard, extended Coulomb, exchange,
electron-hole, and long-range Hartree terms in dispersive and flat-band
systems. Compare small exact solutions, symmetry constraints, and independent
self-consistency routes.

**LKM seeds.** `gcn_938aef02737f4298` (paper `812707666555043841`),
`gcn_ba2c8f81bdf64292` (paper `977191075573661697`), and reasoning chain
`1229352235507384343_8`.

- **TB-REQ-056 — Interaction and double-counting declaration.** Every case
  shall specify interaction matrix elements, decoupling channels, background
  charge, and any double-counting correction relative to the one-body model.
- **TB-REQ-057 — Self-consistency robustness.** Converged states shall satisfy
  density and energy residuals and shall be tested from multiple seeds to
  reveal metastable solutions.
- **TB-REQ-058 — Thermodynamic phase comparison.** Competing solutions shall
  be compared using a declared thermodynamic potential while reporting order
  parameters, spectra, charge, and symmetry breaking.
- **TB-REQ-059 — Conservation and symmetry checks.** Self-consistent
  observables shall satisfy particle-number, Hermiticity, and unbroken-symmetry
  constraints, with deliberately unrestricted calculations as controls.
- **TB-REQ-060 — Beyond-fit validation.** Small systems shall be compared with
  exact or higher-level references, and hidden cases shall vary filling,
  interaction ratios, flux, and initial order outside the tuned set.

### Suite 13 — Moiré, strain, and large reconstructed supercells

**Scientific question.** How do relaxation, strain, and local registry reshape
large-supercell bands, localization, and topology?

**Benchmark family and oracle.** Construct commensurate and approximant
supercells, relaxed and rigid geometries, and continuum and atomistic
descriptions across twist angle and strain.

**LKM seeds.** `gcn_01a4701e71284ca0` (paper `1074575319303716878`),
`gcn_20c39b6a194e48e5` (paper `966036063640354870`), and reasoning chain
`928713876365640298_1`.

- **TB-REQ-061 — Geometry construction.** The benchmark shall validate atom
  counts, commensurability, local registry, periodicity, and strain fields for
  rigid, reconstructed, and approximant structures.
- **TB-REQ-062 — Geometry-dependent coupling.** Hopping and onsite changes
  caused by distance, orientation, strain, and interlayer registry shall be
  evaluated with declared parameter provenance and smooth limiting behavior.
- **TB-REQ-063 — Continuum-atomistic correspondence.** Bandwidths, gaps,
  orbital or layer weights, and selected topology shall be compared between
  continuum and atomistic descriptions over their shared validity window.
- **TB-REQ-064 — Supercell-scale observables.** The benchmark shall require
  sparse evaluation of spectra, local density, and selected response on
  supercells too large for full dense diagonalization.
- **TB-REQ-065 — Structural-family holdout.** Hidden cases shall vary twist
  angle, strain texture, relaxation model, material pair, and commensurate
  index rather than merely rescaling one cell.

### Suite 14 — Magnetism, textures, and spin-orbital transport

**Scientific question.** How do non-collinear textures and spin-orbit or
orbital degrees of freedom generate charge, spin, orbital, and torque
responses?

**Benchmark family and oracle.** Include ferromagnetic, antiferromagnetic,
spiral, domain-wall, and skyrmion textures with tunable exchange and spin-orbit
coupling. Compare adiabatic limits, symmetry selection rules, and transport
conservation relations.

**LKM seeds.** `gcn_24b0aa946f4346b7` (paper `1048481575555039239`),
`gcn_a572d7be0648498e` (paper `1134915489739309136`), and
`gcn_9897d0405aaa497b` (paper `817346350029996034`).

- **TB-REQ-066 — Texture and spinor construction.** The benchmark shall
  represent site-resolved non-collinear exchange, spin-orbit terms, and
  texture winding with invariance under global spin rotation where applicable.
- **TB-REQ-067 — Operator definitions and continuity.** Charge, spin,
  orbital-current, spin-density, and torque conventions shall be explicit, and
  their source or continuity relations shall be checked.
- **TB-REQ-068 — Mechanism-resolved Hall response.** Topological, anomalous,
  spin, and orbital Hall contributions shall be separated when the model
  permits, including parameter values where cancellation is predicted.
- **TB-REQ-069 — Texture-resolution convergence.** Results shall be converged
  in texture discretization, system width, lead matching, and momentum or
  disorder sampling.
- **TB-REQ-070 — Magnetic-family holdout.** Hidden cases shall vary texture
  topology, chirality, size, sublattice structure, spin-orbit strength,
  contacts, and weak disorder.

### Suite 15 — Optical and thermoelectric response

**Scientific question.** Can frequency-, temperature-, and chemical-potential
dependent responses be computed with the correct operators, sum rules, and
limits?

**Benchmark family and oracle.** Use clean and disordered models from small
exactly diagonalizable cells to large sparse systems. Compare spectral-sum and
time-domain Kubo formulations and analytic transport limits.

**LKM seeds.** `gcn_372abc282cf6400a` (paper `867765002071704074`),
`gcn_b74a9f94ce394173` (paper `839814087947845633`), and
`gcn_da7d99ec9d9c470d` (paper `867766869136769368`).

- **TB-REQ-071 — Consistent response operators.** Velocity, charge-current,
  heat-current, and position conventions shall be derived consistently from
  the Hamiltonian, including non-orthogonal or periodic-basis corrections when
  present.
- **TB-REQ-072 — Optical cross-formulation agreement.** Frequency-dependent
  optical conductivity from spectral sums and time-domain Kubo propagation
  shall agree on shared small and intermediate cases and satisfy the relevant
  sum rule.
- **TB-REQ-073 — Thermoelectric relations.** Electrical, thermoelectric, and
  thermal coefficients shall obey Onsager reciprocity and approach
  independently known low-temperature or particle-hole-symmetric limits.
- **TB-REQ-074 — Broadening and integration convergence.** Response spectra
  shall report convergence with frequency grid, broadening, temperature,
  momentum mesh, propagation time, or polynomial order as applicable.
- **TB-REQ-075 — Scale and method holdout.** Hidden cases shall mix clean and
  disordered models, interband and intraband regimes, and system sizes that
  force a method different from full diagonalization.

### Suite 16 — Aperiodic, amorphous, and fractal lattices

**Scientific question.** Which spectral, localization, and topological
phenomena survive without translational symmetry?

**Benchmark family and oracle.** Use Penrose and Ammann-Beenker approximants,
amorphous point sets, hierarchical or fractal graphs, and periodic controls.
Evaluate real-space quantities and scaling across approximant order.

**LKM seeds.** `gcn_dfde823db8fb4c7d` (paper `867766048789627277`),
`gcn_9e58c6a7cc274d8e` (paper `867763861497839913`), and
`gcn_6ccd073ef5034202` (paper `939222012528689276`).

- **TB-REQ-076 — Translation-free model construction.** The benchmark shall
  accept coordinates and connectivity without a primitive cell while
  preserving geometry, edge types, and local environments.
- **TB-REQ-077 — Singular spectral characterization.** Density of states,
  local density, participation measures, and spectral gaps shall be evaluated
  without assuming smooth Bloch bands.
- **TB-REQ-078 — Real-space topology.** Topological claims shall use
  appropriate local markers, spectral flow, pumping, or boundary observables
  and shall recover periodic invariants on periodic controls.
- **TB-REQ-079 — Approximant and fractal scaling.** Results shall track
  approximant order or graph generation and quantify convergence,
  multifractality, or persistent nonconvergence rather than report one finite
  sample.
- **TB-REQ-080 — Geometry-family holdout.** Hidden cases shall change tiling,
  phason configuration, amorphous seed or correlation, fractal generation, and
  boundary shape.

### Suite 17 — Defects, impurities, and interfaces

**Scientific question.** How do atomically specific defects and interfaces
alter local states, coupling, scattering, and magnetism?

**Benchmark family and oracle.** Include vacancies, substitutions, adsorbates,
missing bonds, grain boundaries, and heterointerfaces in analytic and
material-derived models. Compare dilute analytic limits, supercells, and
embedding or scattering formulations.

**LKM seeds.** `gcn_4e2c18caeab14287` (paper `812543518613438464`),
`gcn_fb0dd68b25b94c98` (paper `812713204089094144`), and
`gcn_1378eeb2ef914577` (paper `813360770292121603`).

- **TB-REQ-081 — Structural defect operations.** The benchmark shall create
  vacancies, substitutions, adsorbates, bond changes, and interfaces while
  maintaining a traceable mapping to the pristine model.
- **TB-REQ-082 — Local chemistry perturbations.** Cases shall support
  defect-specific onsite, hopping, overlap, spin-orbit, exchange, and local
  structural changes rather than treating every defect as a scalar onsite
  shift.
- **TB-REQ-083 — Embedding-supercell agreement.** Dilute-defect Green-function
  or T-matrix results shall agree with converged finite-supercell calculations
  in their common regime.
- **TB-REQ-084 — Local and transport consequences.** The benchmark shall
  jointly evaluate bound or resonance energies, localization, local density,
  scattering or transmission, and magnetic response where defined.
- **TB-REQ-085 — Defect-family holdout.** Hidden cases shall vary defect type,
  cluster topology, concentration, position, grain-boundary motif, and
  interface registry.

### Suite 18 — Multiscale and external validation

**Scientific question.** When does a tight-binding explanation remain valid
against continuum theory, first-principles calculation, or experiment?

**Benchmark family and oracle.** Select workflows with two or more independent
description levels and compare the same physical observables after explicit
unit, basis, geometry, and uncertainty alignment.

**LKM seeds.** `gcn_c9883ef775314033` (paper `1102523558807994392`),
`gcn_d2c6245554f04bd1` (paper `1177308086130442242`), and
`gcn_3226df8d95374015` (paper `867757942403760871`).

- **TB-REQ-086 — Same-question cross-scale cases.** Each case shall pose one
  physical question to at least two of analytic, continuum, lattice,
  first-principles, and experimental descriptions.
- **TB-REQ-087 — Explicit representation mapping.** Unit conversions, basis
  projections, Brillouin-zone folding, geometry matching, and parameter
  provenance shall be stored as part of the benchmark case.
- **TB-REQ-088 — Observable-level comparison.** Agreement shall be evaluated
  on gauge-invariant observables with uncertainty, not on raw basis-dependent
  matrix entries unless a common gauge is explicitly constructed.
- **TB-REQ-089 — Discrepancy diagnosis.** A failed comparison shall be
  decomposed across discretization, finite size, parameter uncertainty, missing
  interaction, and model-form error rather than collapsed into one score.
- **TB-REQ-090 — External-family holdout.** At least one material, device
  geometry, or experiment family shall remain isolated from model selection
  and tolerance tuning.

### Suite 19 — Scientific-scale numerical reliability

**Scientific question.** Can the same scientific observable remain accurate
and reproducible when the lattice is too large for dense linear algebra?

**Benchmark family and oracle.** Scale spectral, propagation, Green-function,
and Kubo tasks from exactly solvable small systems to sparse systems with
millions of orbitals, measuring error and resources together.

**LKM seeds.** `gcn_61cc01e25fae41d8` (paper `867751696124608936`),
`gcn_e6394f2f69bb47a8` (paper `1052629302647980034`), and reasoning chain
`811267572279279617_2`.

- **TB-REQ-091 — Sparse production path.** Scientific-scale cases shall
  prohibit full dense Hamiltonian materialization and shall verify storage
  proportional to the declared sparsity structure.
- **TB-REQ-092 — Multiple scalable solvers.** The benchmark shall exercise
  selected interior or edge eigenpairs, Green functions, polynomial spectra,
  time propagation, and response without requiring all eigenvectors.
- **TB-REQ-093 — Error-budget reporting.** Truncation, iterative residual,
  stochastic, broadening, finite-size, and discretization errors shall be
  reported separately and tied to observable convergence.
- **TB-REQ-094 — Accuracy-preserving scaling.** Runtime and peak memory shall
  be measured across a size ladder while holding a declared scientific error
  target fixed; hardware, threading, precision, and stopping rules shall be
  recorded.
- **TB-REQ-095 — Reproducible scale transition.** A small exact case and its
  large sparse continuation shall share one construction recipe, with seeded
  randomness and enough provenance to rerun both paths independently.

### Suite 20 — Parameter inference, inverse design, and uncertainty

**Scientific question.** Can model parameters or structures be inferred and
designed without confusing fit quality with physical identifiability or
out-of-distribution validity?

**Benchmark family and oracle.** Infer tight-binding parameters from synthetic
and real-like spectra or transport, then optimize structures for target
observables. Retain known synthetic truth and held-out forward evaluations.

**LKM seeds.** `gcn_f5b9878833c94b63` (paper `812558777017434113`),
`gcn_5a24091ab6c34b61` (paper `812530864717037569`), and
`gcn_17339133dbf44624` (paper `1074881578984800301`).

- **TB-REQ-096 — Constrained multi-observable inference.** Parameter fitting
  shall combine multiple observables and physical constraints, with a
  documented loss whose terms retain interpretable units or normalization.
- **TB-REQ-097 — Derivative verification.** Analytic, automatic, or adjoint
  derivatives used for inference shall be checked against converged finite
  differences on nondegenerate cases and handled explicitly at degeneracies.
- **TB-REQ-098 — Identifiability and calibration.** The benchmark shall report
  parameter correlations or posterior uncertainty and test predictive
  calibration, not only a best-fit parameter vector.
- **TB-REQ-099 — Forward validation of designs.** Every optimized design shall
  be reevaluated by an independent forward calculation and checked for
  robustness to fabrication-like or parameter perturbations.
- **TB-REQ-100 — Inference-family holdout.** Hidden cases shall change lattice
  or device family, target observable, noise model, and parameter regime, and
  all hidden forward outputs shall remain unavailable during fitting.

## 5. Downstream capability envelopes

The one hundred requirements imply capability envelopes, not a predetermined
API. A future software-design pass should derive the smallest complete set of
physical abstractions needed to express:

1. basis-aware periodic and finite Hamiltonians, including overlap, spin,
   Nambu, time dependence, interactions, non-Hermiticity, and provenance;
2. geometry transformations for boundaries, fields, strain, textures,
   disorder, defects, supercells, leads, and aperiodic graphs;
3. gauge- and degeneracy-safe spectral, geometric, topological, local,
   transport, dynamical, response, and inference observables;
4. dense reference and sparse production algorithms with explicit convergence
   and error controls; and
5. benchmark artifacts, family-level held-out splits, independent oracles, and
   reproducible resource measurements.

No language binding or source-package compatibility surface should be designed
from this list until representative benchmark workflows have been made
executable. Compatibility may later expose these capabilities, but it must not
be allowed to define the underlying scientific architecture.
