#!/usr/bin/env python3
"""Build the domain-first AD companion catalog and derived capability plan."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "benchmark" / "ad_requirements.json"
DOC_ROOT = ROOT / "docs" / "ad-requirements"
INDEX = DOC_ROOT / "README.md"
CAPABILITY_PLAN = ROOT / "docs" / "rust-native-ad-capability-plan.md"
SOURCE_ISSUE = "https://github.com/matrixlab-research/thouless-benchmark/issues/6"
NATIVE_AD_ISSUE = "https://github.com/matrixlab-research/thouless/issues/13"

ROLES = ("essential", "helpful", "conditional", "not_central")
STATUSES = (
    "ad_native_verified",
    "implementable_unverified",
    "missing_ad_rule",
    "missing_forward_physics",
    "conditionally_differentiable",
    "ad_not_central",
)

# These source workflows already have the required specialized Thouless
# primitives. Their missing work is the exact companion orchestration, frozen
# derivative oracle, result record, and CI witness—not a new package rule.
IMPLEMENTABLE_UNVERIFIED = {
    "TBQ-002",
    "TBQ-007",
    "TBQ-019",
    "TBQ-022",
    "TBQ-037",
    "TBQ-039",
    "TBQ-042",
    "TBQ-075",
    "TBQ-083",
    "TBQ-086",
    "TBQ-088",
}

CAPABILITIES = {
    "physical-parameter-spaces": {
        "label": "Physical parameter spaces",
        "description": (
            "Typed continuous controls with bounds, units, reparameterizations, "
            "and explicit separation from discrete model choices."
        ),
        "current_maturity": "partial",
    },
    "complex-generalized-basis": {
        "label": "Complex and generalized-basis differentiation",
        "description": (
            "Rules for complex Hamiltonians, overlap matrices, constrained "
            "Hermiticity, and basis-covariant pullbacks."
        ),
        "current_maturity": "partial",
    },
    "geometry-strain-defects": {
        "label": "Geometry, strain, and defect parameterization",
        "description": (
            "Differentiable coordinates, strain fields, hopping laws, and "
            "fixed-topology defect or interface parameterizations."
        ),
        "current_maturity": "missing",
    },
    "gauge-fields-drives": {
        "label": "Gauge fields and drive parameterization",
        "description": (
            "Gauge-covariant rules for Peierls phases, magnetic fields, time "
            "origin, amplitudes, frequencies, and waveform controls."
        ),
        "current_maturity": "missing",
    },
    "disorder-ensembles": {
        "label": "Disorder and ensemble differentiation",
        "description": (
            "Seeded reparameterization, common-random-number gradients, and "
            "distributional objectives with uncertainty estimates."
        ),
        "current_maturity": "missing",
    },
    "lead-bias-thermodynamics": {
        "label": "Lead, bias, and thermodynamic controls",
        "description": (
            "Physical controls for leads, contacts, chemical potentials, "
            "temperature, energy, and finite-bias boundary conditions."
        ),
        "current_maturity": "partial",
    },
    "hermitian-subspaces": {
        "label": "Hermitian spectral-subspace rules",
        "description": (
            "Gauge-safe eigensystem and projector derivatives, including "
            "degenerate occupied subspaces and generalized eigenproblems."
        ),
        "current_maturity": "available",
    },
    "nonhermitian-subspaces": {
        "label": "Non-Hermitian spectral rules",
        "description": (
            "Biorthogonal, Schur-subspace, exceptional-point, and "
            "pseudospectral differentiation with conditioning diagnostics."
        ),
        "current_maturity": "missing",
    },
    "linear-resolvent-adjoints": {
        "label": "Dense and sparse linear-resolvent adjoints",
        "description": (
            "Reusable JVP and VJP rules for dense or iterative linear solves, "
            "resolvents, self-energies, and preconditioned sparse operators."
        ),
        "current_maturity": "available",
    },
    "implicit-stationarity": {
        "label": "Implicit fixed-point and stationarity rules",
        "description": (
            "Adjoints for converged fixed points, self-consistency, "
            "stationarity conditions, and reusable factorization state."
        ),
        "current_maturity": "partial",
    },
    "time-floquet-adjoints": {
        "label": "Time evolution and Floquet adjoints",
        "description": (
            "Checkpointed propagation and rules for propagators, Floquet "
            "operators, Sambe systems, and time-dependent observables."
        ),
        "current_maturity": "missing",
    },
    "kpm-stochastic-adjoints": {
        "label": "KPM and stochastic adjoints",
        "description": (
            "Checkpointed reverse rules for Chebyshev recurrences, stochastic "
            "trace estimators, and common-random-number objectives."
        ),
        "current_maturity": "available",
    },
    "topology-geometry-response": {
        "label": "Topology, quantum geometry, and response composition",
        "description": (
            "Differentiable smooth proxies and tensor pipelines while keeping "
            "discrete invariants as independent forward validation."
        ),
        "current_maturity": "partial",
    },
    "boundary-localization": {
        "label": "Boundary and localization composition",
        "description": (
            "Differentiable surface, finite-geometry, local-marker, "
            "localization, and finite-size-scaling observables."
        ),
        "current_maturity": "partial",
    },
    "transport-thermoelectric": {
        "label": "Transport and thermoelectric composition",
        "description": (
            "Adjoints for scattering and NEGF observables, including energy "
            "and bias derivatives, finite-temperature moments, and noise."
        ),
        "current_maturity": "partial",
    },
    "interaction-self-consistency": {
        "label": "Interacting self-consistency",
        "description": (
            "Forward and reverse support for mean-field maps, competing "
            "stationary solutions, thermodynamic potentials, and metastability."
        ),
        "current_maturity": "missing",
    },
    "multiscale-inference": {
        "label": "Multiscale mapping and inference",
        "description": (
            "Differentiable representation maps, constrained multi-observable "
            "losses, calibration, and independent forward validation."
        ),
        "current_maturity": "partial",
    },
    "nonsmooth-failure-semantics": {
        "label": "Nonsmooth and discrete failure semantics",
        "description": (
            "Typed handling of gap closings, branch changes, connectivity "
            "changes, solver switches, rank changes, and invalid gradients."
        ),
        "current_maturity": "partial",
    },
    "scale-error-diagnostics": {
        "label": "Scale and error diagnostics",
        "description": (
            "Derivative error budgets, conditioning, convergence histories, "
            "memory accounting, checkpoint policies, and sparse-only guarantees."
        ),
        "current_maturity": "partial",
    },
    "identifiability-higher-order": {
        "label": "Identifiability and higher-order products",
        "description": (
            "Jacobian products, Fisher or Gauss-Newton operators, Hessian-vector "
            "products, nullspaces, and experiment-design diagnostics."
        ),
        "current_maturity": "partial",
    },
    "derivative-bindings": {
        "label": "Derivative bindings",
        "description": (
            "Stable Rust-native derivative entry points exposed consistently "
            "to Python and Julia without reimplementing scientific kernels."
        ),
        "current_maturity": "missing",
    },
    "heldout-generality": {
        "label": "Held-out generality",
        "description": (
            "Evaluator-owned unseen models, hidden expected results, and "
            "anti-overfitting checks separate from public CI."
        ),
        "current_maturity": "missing",
    },
}

# One row per immutable scientific anchor. Columns are:
# number, AD role, continuous controls, outputs, differentiable formulation,
# no-AD baseline, validity boundary, required capabilities.
ROWS = """
001	helpful	onsite and hopping coefficients; overlap-matrix elements	generalized eigenvalues; Hermiticity and residual losses	differentiate a basis-covariant loss built from H, S, and separated spectral subspaces	rebuild each perturbed H and S and use central finite differences	S must remain positive definite and the selected subspace must stay separated	physical-parameter-spaces,complex-generalized-basis,hermitian-subspaces
002	essential	energy-window weights; disentanglement and hopping parameters	out-of-window prediction error; subspace distance	differentiate the fitted subspace and held-out band error with respect to model parameters	repeat the fit for every parameter perturbation and compare excluded energies	window membership must be frozen or replaced by smooth weights	physical-parameter-spaces,hermitian-subspaces,multiscale-inference,heldout-generality
003	conditional	hopping decay parameters; smooth cutoff radius	band error; locality cost; symmetry residual	optimize a smooth locality-accuracy objective before applying a discrete truncation	scan every candidate cutoff and refit all retained hoppings	hard edge inclusion changes are nondifferentiable and require forward revalidation	physical-parameter-spaces,geometry-strain-defects,nonsmooth-failure-semantics
004	helpful	symmetry-tied onsite and hopping parameters	symmetry residuals; target spectral observables	pull gradients back through a symmetry-constrained parameterization and test forbidden directions	fit unconstrained and constrained models with repeated forward calculations	the declared symmetry group and representation must remain fixed	physical-parameter-spaces,complex-generalized-basis,hermitian-subspaces
005	essential	shared structural and coupling-law parameters	held-out structure spectra; transfer loss	differentiate a multi-structure training loss and predict structures excluded from optimization	refit by derivative-free search and run each held-out structure independently	connectivity-changing structural events remain external discrete choices	geometry-strain-defects,multiscale-inference,heldout-generality
006	essential	Hamiltonian and overlap parameters	occupied projector; subspace-resolved bands	differentiate separated projectors rather than gauge-dependent individual eigenvectors	central-difference the projector after independent diagonalizations	the occupied-cluster gap must exceed a declared floor	complex-generalized-basis,hermitian-subspaces,nonsmooth-failure-semantics
007	helpful	hopping and onsite parameters; chemical potential	DOS moments; state-counting residual	differentiate normalized DOS moments and integrated state count	execute a full DOS calculation for every perturbation	broadening and polynomial order must be frozen and converged	physical-parameter-spaces,kpm-stochastic-adjoints,scale-error-diagnostics
008	helpful	model parameters; energy and momentum coordinates	van Hove energy; flatness and peak-shape proxies	differentiate smooth spectral-feature estimators with respect to parameters and energy	grid-refine and finite-difference every feature location	exact argmax and band reordering are nonsmooth at feature mergers	hermitian-subspaces,nonsmooth-failure-semantics,scale-error-diagnostics
009	conditional	chemical potential; continuous band parameters	Fermi-surface area; topology proxy; critical energy	differentiate smooth occupation and contour functionals on each fixed Fermi-surface branch	scan chemical potential and reconstruct contours independently	a Lifshitz topology change is a branch event and must be located by forward scans	hermitian-subspaces,topology-geometry-response,nonsmooth-failure-semantics
010	helpful	shared hopping parameters; boundary potential	Bloch-versus-finite spectral discrepancy	differentiate the cross-representation discrepancy while holding geometry fixed	perturb parameters and rerun both Bloch and finite calculations	system-size and termination choices are discrete convergence variables	hermitian-subspaces,boundary-localization,scale-error-diagnostics
011	helpful	hopping amplitudes; magnetic field; gauge-origin parameters	spectra; loop phases; gauge-invariant loss	differentiate gauge-covariant Peierls phases and invariant observables	rebuild phases and finite-difference under several gauges	flux conventions and branch-unwrapped phases must be declared	gauge-fields-drives,complex-generalized-basis,hermitian-subspaces
012	not_central	hopping and onsite parameters at fixed rational flux	magnetic-cell residual; band observables	use AD only inside a preselected magnetic cell to tune continuous parameters	enumerate rational cells and solve each candidate forward	minimal-cell selection and flux rationalization are discrete	nonsmooth-failure-semantics
013	helpful	flux density; chemical potential; hopping parameters	gap proxy; density derivative; Chern and Streda discrepancy	differentiate density and smooth gap proxies while independently recomputing the integer invariant	finite-difference density versus flux and forward-compute Chern numbers	gap closings and rational-cell changes invalidate a local derivative	gauge-fields-drives,topology-geometry-response,nonsmooth-failure-semantics
014	helpful	magnetic field; effective-mass and hopping parameters	Landau-level energies; correspondence error	differentiate matched low-field levels on a fixed branch	scan fields and refit continuum correspondence from forward spectra	level crossings require subspace matching rather than label derivatives	gauge-fields-drives,hermitian-subspaces,nonsmooth-failure-semantics
015	conditional	continuous parameters within each rational approximant	approximant discrepancy; extrapolated observables	differentiate within each fixed approximant and combine with an external convergence sequence	recompute all rational approximants under every perturbation	denominator changes are discrete and never differentiated	gauge-fields-drives,scale-error-diagnostics,nonsmooth-failure-semantics
016	not_central	continuous Hamiltonian parameters	smooth projector geometry; independently recomputed bulk index	use AD for smooth projector observables but not for the integer index itself	parameter-scan and recompute the invariant on every model	the index derivative is zero away from transitions and undefined at gap closing	nonsmooth-failure-semantics
017	essential	mass, hopping, spin-orbit, or strain parameters	smooth phase proxy; gap; independently recomputed index	optimize a smooth occupied-subspace objective and locate the forward gap closing	grid-search parameters and recompute gaps and invariants	the topological transition is validated forward, never by differentiating the integer	topology-geometry-response,hermitian-subspaces,nonsmooth-failure-semantics
018	helpful	Hamiltonian parameters; loop base point	Wilson and nested-Wilson subspace spectra	differentiate gauge-covariant holonomy subspaces under a maintained spectral separation	finite-difference complete loop constructions with parallel-transport rematching	Wilson-sector gaps and occupied gaps must remain open	hermitian-subspaces,topology-geometry-response,nonsmooth-failure-semantics
019	helpful	model parameters	discrepancy among Chern, Wilson, parity, and real-space diagnostics	differentiate continuous discrepancy measures to diagnose which representation causes disagreement	recompute every diagnostic for each perturbed model	diagnostics with discrete outputs remain forward gates	topology-geometry-response,boundary-localization,multiscale-inference
020	conditional	gap-opening perturbations; basis-rotation coordinates	conditioning; false-positive loss; adversarial residual	differentiate only smooth, gapped negative controls and report gradient invalidity near singular cases	run explicit trivial, near-gapless, and rotated-basis controls	gap floor and conditioning thresholds define the valid domain	hermitian-subspaces,nonsmooth-failure-semantics,scale-error-diagnostics
021	conditional	boundary onsite and hopping parameters at fixed termination	edge spectrum; surface weight; termination sensitivity	differentiate within each declared termination family	enumerate terminations and finite-difference continuous boundary parameters	adding or removing sites and bonds is a discrete operation	geometry-strain-defects,boundary-localization,nonsmooth-failure-semantics
022	helpful	bulk and boundary couplings; system length	edge-state energy; localization length; splitting	differentiate localization and splitting at fixed finite size, then perform a forward size sequence	rerun diagonalization for each parameter and system size	state mixing and exact zero-mode crossings require projector treatment	hermitian-subspaces,boundary-localization,scale-error-diagnostics
023	essential	bulk and surface couplings; energy; broadening	surface Green function; spectral density; finite-slab discrepancy	apply an implicit adjoint to the retarded surface fixed point and compare with finite spectra	unroll or rerun the surface solver for every perturbation	the retarded branch and solver residual must remain stable	linear-resolvent-adjoints,implicit-stationarity,boundary-localization
024	conditional	bulk and boundary potentials	smooth bulk and boundary proxies; correspondence residual	differentiate within the validity conditions and separately test the correspondence hypothesis	scan parameters and recompute bulk and boundary diagnostics	correspondence is conditional on gap, symmetry, and boundary assumptions	topology-geometry-response,boundary-localization,nonsmooth-failure-semantics
025	essential	continuous geometry and termination-family parameters	held-out boundary spectra and localization	differentiate a family-level loss and validate on unseen geometries	brute-force calibrate each geometry and evaluate held-out families	connectivity and termination class remain evaluator-controlled	geometry-strain-defects,boundary-localization,heldout-generality
026	essential	Hamiltonian and overlap parameters; momentum	quantum metric; Berry curvature; covariance residual	differentiate gauge-invariant projector tensors with respect to physical controls	central-difference tensors after independent eigensystem reconstruction	subspace gaps and momentum-mesh convergence are mandatory	hermitian-subspaces,topology-geometry-response,scale-error-diagnostics
027	essential	chemical potential; relaxation time; band parameters	intrinsic, Berry-dipole, and extrinsic Hall contributions	differentiate mechanism-resolved response integrals instead of a single fitted total	finite-difference each mechanism after full Brillouin-zone integration	the chosen scattering model and Fermi-surface smoothing must be explicit	topology-geometry-response,physical-parameter-spaces,scale-error-diagnostics
028	helpful	symmetry-allowed perturbations; model parameters	allowed and forbidden tensor components	pull back response gradients through symmetry-constrained parameters and test zero directions	perturb each parameter and recompute the tensor	forbidden-component tests require exact declared symmetries	physical-parameter-spaces,topology-geometry-response,complex-generalized-basis
029	essential	chemical potential; temperature; momentum; model parameters	Fermi-surface response and parameter derivatives	differentiate smooth Fermi-surface quadrature and demonstrate joint value-gradient convergence	finite-difference after repeated mesh and smearing sweeps	zero-temperature discontinuities require a converged regularization	topology-geometry-response,scale-error-diagnostics,nonsmooth-failure-semantics
030	essential	bulk couplings; boundary potential; chemical potential	nonlinear bulk response; boundary accumulation; zero Chern number	differentiate the nonlinear response and boundary observable while forward-validating the zero-Chern condition	parameter-scan bulk and boundary calculations independently	the bulk gap, symmetry class, and boundary definition must remain declared	topology-geometry-response,boundary-localization,heldout-generality
031	helpful	disorder strength; differentiable noise amplitudes	ensemble DOS; localization and transport statistics	use fixed seeds or reparameterized noise to differentiate ensemble estimators	repeat large ensembles for every parameter perturbation	seed policy and confidence intervals are part of the result	disorder-ensembles,kpm-stochastic-adjoints,scale-error-diagnostics
032	essential	disorder and model parameters	IPR, transfer, conductance, and local-marker discrepancy	differentiate a cross-observable localization objective with common disorder samples	finite-difference every observable over matched ensembles	all observables must share samples and resolved finite-size errors	disorder-ensembles,boundary-localization,scale-error-diagnostics
033	essential	disorder strength; energy; continuous scaling parameters	mobility-edge location; critical exponent; collapse loss	differentiate a smooth finite-size-scaling collapse and validate the extracted crossing independently	grid-search scaling parameters and rerun all sizes	critical branches and finite-size corrections must be reported	disorder-ensembles,boundary-localization,identifiability-higher-order
034	helpful	disorder strength; chemical potential	mobility-gap proxy; real-space topology; transport	differentiate smooth localization and transport proxies while independently recomputing topology	scan disorder and energy with repeated sparse calculations	discrete invariants and mobility-edge crossings remain forward gates	disorder-ensembles,boundary-localization,topology-geometry-response
035	essential	distribution parameters; shared physical controls	held-out disorder-family performance	differentiate distributional training objectives and test unseen distributions	refit separately for every disorder family and perform external holdout	distribution-family identity is not a differentiable coordinate	disorder-ensembles,multiscale-inference,heldout-generality
036	essential	lead onsite, hopping, coupling; energy and broadening	lead modes; self-energy; device spectral response	differentiate calibrated lead self-energies and device observables with implicit or resolvent adjoints	finite-difference complete lead and device solves	retarded branch, propagating-mode count, and tolerance must stay stable	lead-bias-thermodynamics,linear-resolvent-adjoints,implicit-stationarity,transport-thermoelectric
037	helpful	device and contact parameters	scattering unitarity; bond-current continuity; source residual	differentiate physical observables and conservation residuals through the same scattering solution	recompute the scattering state for every perturbation	channel openings and solver-rank changes require typed failure	linear-resolvent-adjoints,transport-thermoelectric,nonsmooth-failure-semantics
038	essential	energy; temperature; chemical potential; device parameters	transmission; LDOS; shot and thermal noise	differentiate energy- and temperature-resolved observables and integrated moments	finite-difference energy, temperature, and every device parameter	integration windows and channel thresholds must be converged	lead-bias-thermodynamics,linear-resolvent-adjoints,transport-thermoelectric,scale-error-diagnostics
039	helpful	device length; barrier and hopping parameters	transmission; residual; condition and iteration counts	differentiate the sparse solve while treating solver diagnostics as acceptance evidence	finite-difference repeated long-device solves under a fixed solver	solver switching and preconditioner rebuilding are discrete events	linear-resolvent-adjoints,scale-error-diagnostics,nonsmooth-failure-semantics
040	essential	contact couplings; lead parameters; device parameters	held-out contact-family transmission and local observables	optimize a contact-robust loss and validate on excluded lead and interface families	derivative-free fitting followed by full held-out forward calculations	contact topology and lead family remain external discrete variables	lead-bias-thermodynamics,transport-thermoelectric,multiscale-inference,heldout-generality
041	helpful	normal hoppings; pairing amplitudes and phases	PHS residual; BdG spectrum and projector	differentiate a Nambu-convention-aware Hamiltonian with constrained particle-hole structure	finite-difference independently reconstructed BdG matrices	the Nambu basis and antiunitary convention must remain fixed	physical-parameter-spaces,complex-generalized-basis,hermitian-subspaces
042	essential	superconducting phase; junction and contact parameters	Andreev levels; free energy; Josephson current	differentiate the phase-dependent thermodynamic potential and compare with spectral current formulas	finite-difference free energy versus phase with branch tracking	level crossings require subspace or thermodynamic treatment	hermitian-subspaces,transport-thermoelectric,nonsmooth-failure-semantics
043	helpful	chemical potential; pairing; Zeeman and disorder parameters	near-zero projector; localization; topological and trivial diagnostics	differentiate projector-based robustness metrics and validate against independent diagnostics	scan all parameters and classify modes from repeated spectra	individual Majorana labels are invalid at degeneracy	hermitian-subspaces,boundary-localization,topology-geometry-response
044	conditional	phase; poisoning and symmetry-breaking parameters	parity-resolved current; periodicity and gap proxies	differentiate only a declared fixed-parity branch and forward-test branch relaxation	recompute even and odd branches over a phase grid	parity switches and branch selection are discrete physical events	nonsmooth-failure-semantics,hermitian-subspaces,transport-thermoelectric
045	helpful	continuum coefficients; lattice spacing; pairing parameters	continuum-lattice spectral and current discrepancy	differentiate matched continuous parameters at each fixed discretization and perform a forward convergence sequence	finite-difference both representations over several lattice spacings	the lattice spacing is a convergence variable, not an optimizable physical control	complex-generalized-basis,multiscale-inference,scale-error-diagnostics
046	essential	complex onsite and hopping parameters	left-right subspaces; eigenvalue and residual objectives	differentiate biorthogonal or Schur-subspace observables with normalization-invariant pullbacks	finite-difference complete left and right eigensystems	eigenvector conditioning and exceptional proximity must be reported	nonhermitian-subspaces,complex-generalized-basis,scale-error-diagnostics
047	conditional	gain, loss, and nonreciprocal couplings	eigenvalue splitting; pseudospectral and conditioning measures	differentiate smooth pseudospectral proxies away from the exceptional point and locate the singularity forward	scan the complex spectrum and fit splitting exponents	the derivative diverges or becomes undefined at the exceptional point	nonhermitian-subspaces,nonsmooth-failure-semantics,scale-error-diagnostics
048	conditional	complex model parameters	point-gap and line-gap proxies; non-Bloch spectral loops	differentiate smooth gap and loop-distance objectives while forward-recomputing discrete invariants	scan generalized Brillouin-zone contours and invariants	gap-type changes and winding transitions are nondifferentiable	nonhermitian-subspaces,topology-geometry-response,nonsmooth-failure-semantics
049	essential	nonreciprocal couplings; boundary potentials	periodic-open spectral mismatch; skin localization	differentiate mismatch and localization measures on fixed finite geometries	recompute periodic and open spectra for every perturbation	eigenvalue coalescence and boundary topology changes require failure semantics	nonhermitian-subspaces,boundary-localization,scale-error-diagnostics
050	essential	shared complex couplings across model families	held-out non-Hermitian spectra and localization	differentiate a family-level calibration loss and test unseen boundary and gain-loss families	refit every family independently and run external holdout	family and graph topology are evaluator-controlled	nonhermitian-subspaces,multiscale-inference,heldout-generality
051	helpful	drive amplitude, phase, frequency, and waveform coefficients	propagator and Floquet-observable discrepancy	differentiate a common drive representation and compare gauge-equivalent encodings	finite-difference full time evolution for each encoding	time-origin and gauge transformations must be handled covariantly	gauge-fields-drives,time-floquet-adjoints
052	conditional	drive controls; time origin	quasienergy subspaces; branch-consistency residual	differentiate Floquet projectors or unitary eigenphases on a fixed branch	finite-difference with explicit phase unwrapping	branch-cut crossings and quasienergy degeneracies invalidate label derivatives	time-floquet-adjoints,hermitian-subspaces,nonsmooth-failure-semantics
053	helpful	drive frequency and amplitude; time step; harmonic cutoff	Sambe-propagator-high-frequency discrepancy	differentiate physical controls within each representation and forward-test representation convergence	rerun all three methods for every perturbation	time step and harmonic cutoff remain discrete convergence variables	time-floquet-adjoints,multiscale-inference,scale-error-diagnostics
054	essential	drive waveform; phase; frequency	pumped charge; conversion efficiency; heating proxy	use checkpointed adjoints to optimize a dynamical observable and validate conservation and pumping forward	finite-difference full trajectories or use derivative-free control	time-origin, period count, and observable window must be fixed	time-floquet-adjoints,gauge-fields-drives,scale-error-diagnostics
055	conditional	physical drive controls at fixed numerical resolution	value and gradient convergence across time steps and cutoffs	differentiate only within a fixed discretization, then require an external value-gradient convergence ladder	rerun finite differences at every time step and cutoff	time-step and harmonic-count changes are not differentiated	time-floquet-adjoints,nonsmooth-failure-semantics,scale-error-diagnostics
056	helpful	interaction strengths; double-counting parameters	order parameters; energy decomposition and declaration residual	differentiate an explicitly declared energy functional and its bookkeeping terms	recompute the self-consistent solution for each perturbation	the functional and double-counting convention are immutable provenance	interaction-self-consistency,implicit-stationarity,physical-parameter-spaces
057	essential	interaction strengths; fields; initialization-independent controls	converged order parameters; susceptibility; metastability diagnostics	apply implicit differentiation to each stable fixed point and compare competing basins	rerun self-consistency from many seeds for every perturbation	Jacobian singularity and basin changes require typed failure	interaction-self-consistency,implicit-stationarity,nonsmooth-failure-semantics
058	conditional	interaction and field parameters	thermodynamic potential of competing orders	differentiate within each converged stationary branch and locate crossings by forward comparison	scan parameters and reconverge all competing solutions	the globally selected branch changes discontinuously	interaction-self-consistency,implicit-stationarity,nonsmooth-failure-semantics
059	helpful	physical interaction and model parameters	conservation, Ward-like, and unbroken-symmetry residuals	differentiate the physical observable while using conservation residual gradients as diagnostics	finite-difference converged observables and residuals	the declared approximation determines which conservation laws apply	interaction-self-consistency,implicit-stationarity,scale-error-diagnostics
060	helpful	shared Hamiltonian and interaction parameters	mean-field versus exact observable discrepancy	differentiate the approximate pipeline and compare predictions with a non-AD exact reference	finite-difference mean-field and exact small-system calculations	the exact solver is an independent validation path, not differentiated through	interaction-self-consistency,multiscale-inference,heldout-generality
061	conditional	twist, strain, and relaxation coordinates at fixed commensurability	geometry energy; band and localization observables	differentiate continuous reconstruction within a chosen commensurate supercell	enumerate commensurate cells and finite-difference relaxed geometries	commensurability and graph connectivity are discrete	geometry-strain-defects,nonsmooth-failure-semantics,scale-error-diagnostics
062	essential	atomic coordinates; strain tensor; coupling-law parameters	hoppings; bands; response and force-like sensitivities	differentiate geometry-dependent onsite and hopping laws from coordinates to observables	finite-difference every coordinate or coupling parameter	connectivity cutoffs require smoothing or explicit event handling	geometry-strain-defects,physical-parameter-spaces,scale-error-diagnostics
063	essential	shared continuum and atomistic parameters	band, subspace, and response discrepancy	differentiate an explicit representation map and cross-scale observable loss	refit and finite-difference both models separately	the mapping, gauge, and energy window must be declared	multiscale-inference,geometry-strain-defects,hermitian-subspaces
064	essential	geometry and coupling parameters	targeted eigenvalues; DOS; local and response observables	use sparse adjoints or checkpointed KPM without materializing dense matrices	finite-difference repeated sparse production calculations	the forward and reverse paths must both remain sparse	linear-resolvent-adjoints,kpm-stochastic-adjoints,scale-error-diagnostics
065	essential	shared relaxation and coupling-law parameters	held-out twist, strain, and reconstruction performance	differentiate across training structures and validate on unseen structural families	refit each structure and evaluate excluded families	commensurate-cell identity remains evaluator-controlled	geometry-strain-defects,multiscale-inference,heldout-generality
066	essential	texture angles and amplitudes; spin-orbit and exchange parameters	spinor observables; covariance residual	differentiate a normalized spinor-texture parameterization and covariant observables	finite-difference independently rotated textures	global spin rotations must preserve the declared covariance	physical-parameter-spaces,complex-generalized-basis,geometry-strain-defects
067	essential	texture and spin-orbital parameters	charge, spin, orbital currents; torque and continuity residual	differentiate all local observables through one Hamiltonian-consistent operator construction	finite-difference states and every current operator	the current and torque conventions must be explicit	complex-generalized-basis,linear-resolvent-adjoints,topology-geometry-response
068	essential	exchange, spin-orbit, disorder, and chemical-potential parameters	intrinsic and texture Hall contributions	differentiate mechanism-resolved Hall observables and their crossovers	finite-difference each mechanism after full integration	scattering and texture approximations define the validity domain	topology-geometry-response,geometry-strain-defects,scale-error-diagnostics
069	helpful	texture length scale; mesh spacing; exchange parameters	adiabatic error; current and torque convergence	differentiate at fixed resolution and require value-gradient convergence over texture meshes	rerun every perturbation for every resolution	mesh and topology changes remain external convergence choices	geometry-strain-defects,scale-error-diagnostics,nonsmooth-failure-semantics
070	essential	shared magnetic-texture and material parameters	held-out texture-family observables	differentiate a multi-texture loss and validate on unseen skyrmion, spiral, or domain-wall families	refit and forward-evaluate each texture family	texture topology and lattice graph are held-out categorical variables	geometry-strain-defects,multiscale-inference,heldout-generality
071	essential	Hamiltonian parameters; vector potential; chemical potential	velocity, charge-current, and heat-current matrix elements	differentiate operators generated from the same parameterized Hamiltonian and test identities	finite-difference Hamiltonian-derived operators independently	gauge, position, and heat-current conventions must be declared	complex-generalized-basis,topology-geometry-response,lead-bias-thermodynamics
072	essential	pulse or field controls; frequency; model parameters	optical conductivity; spectral sum; time-frequency discrepancy	differentiate both spectral and time-domain response pipelines and compare them	finite-difference eigenstate sums and full time propagation	broadening, time window, and sum-rule cutoff must converge	time-floquet-adjoints,topology-geometry-response,scale-error-diagnostics
073	essential	energy; chemical potential; temperature; device parameters	Landauer moments; Seebeck coefficient; Lorenz number; differential conductance	differentiate transmission with respect to energy for thermopower and current with respect to bias for differential conductance	finite-difference T(E) for Seebeck and I(V) for conductance, rerunning transport at every point	energy derivatives require converged quadrature; bias derivatives require a declared finite-bias forward model	lead-bias-thermodynamics,linear-resolvent-adjoints,transport-thermoelectric,scale-error-diagnostics
074	helpful	broadening; integration nodes; physical model parameters	response value and derivative convergence	differentiate physical parameters at fixed quadrature, then test convergence across broadenings and grids	repeat finite differences across the full convergence ladder	numerical regularizers are convergence variables unless scientifically declared	topology-geometry-response,scale-error-diagnostics,nonsmooth-failure-semantics
075	helpful	shared physical parameters	exact-versus-sparse response and gradient discrepancy	differentiate dense and sparse formulations and verify a reproducible crossover	finite-difference both solvers at every size	solver choice and size are external numerical controls	kpm-stochastic-adjoints,multiscale-inference,scale-error-diagnostics
076	conditional	coordinates and coupling-law parameters at fixed graph	geometric residuals; spectrum and local observables	differentiate coordinates and couplings while preserving graph topology	finite-difference every coordinate with graph reconstruction	connectivity changes and neighbor-list events are discrete	geometry-strain-defects,nonsmooth-failure-semantics
077	helpful	model and geometry parameters	spectral-measure moments; localization observables	differentiate smoothed measures and KPM moments with common random vectors	finite-difference repeated KPM and exact approximant calculations	singular measures require resolution and kernel convergence	kpm-stochastic-adjoints,boundary-localization,scale-error-diagnostics
078	helpful	model and coordinate parameters	local Chern or Bott proxies; mobility gap	differentiate smooth real-space projector objectives and independently recompute discrete markers	finite-difference sparse projectors and marker calculations	mobility gap and projector approximation must remain controlled	kpm-stochastic-adjoints,topology-geometry-response,boundary-localization
079	conditional	continuous model parameters within each approximant	multifractal spectrum; scaling exponents; collapse loss	differentiate smooth participation moments at fixed approximant and fit scaling forward	rerun all approximants for every perturbation	approximant order and box partition are discrete convergence choices	boundary-localization,scale-error-diagnostics,nonsmooth-failure-semantics
080	essential	shared geometry and coupling-law parameters	held-out amorphous, quasiperiodic, and fractal observables	differentiate training-family objectives and validate on unseen geometry families	refit each family and execute evaluator-owned holdouts	family identity and graph topology are categorical	geometry-strain-defects,multiscale-inference,heldout-generality
081	conditional	continuous defect relaxation and local couplings at fixed defect identity	structural provenance; local spectrum and formation proxy	differentiate a provenance-preserving defect parameterization within a fixed graph	finite-difference relaxed coordinates and couplings	defect insertion, removal, and topology are discrete	geometry-strain-defects,nonsmooth-failure-semantics
082	essential	defect onsite, charge-state, and local hopping parameters	local levels; charge and spin observables	differentiate a localized chemistry parameterization and its embedded observables	finite-difference each local chemistry parameter	charge-state or bonding changes require separate branches	geometry-strain-defects,linear-resolvent-adjoints,physical-parameter-spaces
083	helpful	defect and embedding parameters	embedding-versus-supercell Green function and spectrum discrepancy	differentiate both representations through a shared defect model	finite-difference independent embedding and supercell calculations	supercell size and embedding boundary are convergence variables	linear-resolvent-adjoints,multiscale-inference,scale-error-diagnostics
084	essential	defect, interface, lead, and chemical-potential parameters	local states; scattering and transport changes	differentiate the coupled defect-embedding-transport pipeline	finite-difference the full local and transport workflow	resonance crossings and channel changes need failure semantics	geometry-strain-defects,linear-resolvent-adjoints,transport-thermoelectric
085	essential	shared defect-family and interface parameters	held-out defect and interface predictions	differentiate across training defects and validate unseen chemistry or boundary families	refit each defect and run external family holdout	defect identity and connectivity remain evaluator-controlled	geometry-strain-defects,multiscale-inference,heldout-generality
086	helpful	shared physical parameters across representations	common gauge-invariant observables	differentiate one scientific objective through each scale-specific representation	finite-difference every representation independently	each representation retains its own declared approximation	multiscale-inference,complex-generalized-basis,scale-error-diagnostics
087	essential	representation-map and physical parameters	mapped Hamiltonian, subspace, and observable residuals	differentiate an explicit map rather than comparing unnamed matrices	finite-difference map construction and both endpoint solvers	map gauge, basis, window, and normalization must be explicit	multiscale-inference,complex-generalized-basis,hermitian-subspaces
088	helpful	shared physical and mapping parameters	gauge-invariant cross-scale observables	differentiate invariant observables and basis-covariant discrepancies	finite-difference independently gauge-transformed pipelines	gauge-dependent raw eigenvectors are never acceptance targets	multiscale-inference,hermitian-subspaces,topology-geometry-response
089	essential	physics, representation, and numerical parameters separately	decomposed model, mapping, solver, and sampling discrepancies	use block-structured Jacobian products to attribute error sources	finite-difference one parameter block at a time	parameter blocks and provenance must not be conflated	multiscale-inference,identifiability-higher-order,scale-error-diagnostics
090	essential	shared calibrated physical parameters	external material or geometry-family observables	differentiate only the training systems and reserve external families for forward evaluation	refit and forward-evaluate every external system independently	the holdout remains inaccessible to optimization	heldout-generality,multiscale-inference
091	helpful	physical parameters in a fixed sparse representation	target observables; memory and sparsity diagnostics	differentiate through matrix-free or sparse operators and assert no dense fallback	finite-difference repeated sparse forward calculations	matrix materialization is a hard failure	linear-resolvent-adjoints,kpm-stochastic-adjoints,scale-error-diagnostics
092	conditional	physical parameters under a fixed selected solver	residual, observable, and derivative accuracy	differentiate within each solver and compare a forward-selected portfolio	finite-difference each solver configuration	solver selection and preconditioner choice are discrete	nonsmooth-failure-semantics,linear-resolvent-adjoints,scale-error-diagnostics
093	essential	physical parameters; declared numerical tolerances	separate truncation, iteration, sampling, and AD errors	compute derivative error budgets alongside forward error budgets	finite-difference after tightening one error source at a time	error components require independent convergence controls	scale-error-diagnostics,identifiability-higher-order
094	essential	physical parameters at increasing size	time, memory, value, and gradient accuracy	use sparse adjoints or checkpointing and measure accuracy-preserving scaling	finite-difference two full forward solves per direction at every size	hardware, warmed execution, and accuracy must be matched	linear-resolvent-adjoints,kpm-stochastic-adjoints,scale-error-diagnostics
095	conditional	physical parameters at fixed exact or production method	exact-to-production value and gradient discrepancy	differentiate both methods on their overlap and forward-validate the transition policy	finite-difference both methods over the size ladder	method switching and size are discrete	nonsmooth-failure-semantics,multiscale-inference,scale-error-diagnostics
096	essential	constrained physical model parameters	multiple spectra, projectors, and response observables	differentiate a unit-aware constrained multi-observable loss	finite-difference or derivative-free optimize the full composite loss	constraints and observable weights must be declared	physical-parameter-spaces,multiscale-inference,identifiability-higher-order
097	essential	model parameters; arbitrary tangent and cotangent directions	JVP and VJP products through spectral calculations	compare native products with independent directional finite differences and adjoint identities	compute central differences for each tested direction	degenerate states require projector-based objectives	hermitian-subspaces,identifiability-higher-order,scale-error-diagnostics
098	essential	model parameters; candidate measurement controls	Jacobian rank; Fisher spectrum; predictive uncertainty	use Jacobian and Gauss-Newton products to expose nullspaces and design informative observables	finite-difference the full sensitivity matrix and refit perturbed data	rank claims require scale-aware thresholds and held-out prediction	identifiability-higher-order,multiscale-inference,heldout-generality
099	essential	optimized model or device parameters	training loss; excluded-observable forward predictions	optimize with native derivatives but accept only an independent non-AD forward calculation	derivative-free optimization followed by the same independent forward gate	validation code and points must be separate from the loss	multiscale-inference,heldout-generality,scale-error-diagnostics
100	essential	shared parameters trained on declared families	unseen model-family predictions	differentiate public training objectives and reserve a hidden family for evaluator-owned forward validation	refit public families and evaluate the same hidden family	family identity and hidden expectations cannot enter gradients	multiscale-inference,heldout-generality,identifiability-higher-order
""".strip()


def parse_rows() -> dict[str, dict[str, object]]:
    rows: dict[str, dict[str, object]] = {}
    for line_number, line in enumerate(ROWS.splitlines(), start=1):
        fields = line.split("\t")
        if len(fields) != 8:
            raise ValueError(
                f"AD requirement row {line_number} has {len(fields)} columns, expected 8"
            )
        number, role, controls, outputs, formulation, baseline, boundary, caps = fields
        qid = f"TBQ-{int(number):03d}"
        if qid in rows:
            raise ValueError(f"duplicate row for {qid}")
        rows[qid] = {
            "role": role,
            "continuous_controls": controls.split("; "),
            "scientific_outputs": outputs.split("; "),
            "differentiable_formulation": formulation,
            "no_ad_baseline": baseline,
            "validity_boundary": boundary,
            "required_capabilities": caps.split(","),
        }
    return rows


def source_questions() -> dict[str, dict[str, str]]:
    questions: dict[str, dict[str, str]] = {}
    pattern = re.compile(r"^# (TBQ-[0-9]{3}) — (.+)$", flags=re.MULTILINE)
    for path in sorted((ROOT / "docs" / "problems").glob("[0-9][0-9]-*/tbq-*.md")):
        text = path.read_text()
        match = pattern.search(text)
        if not match:
            raise ValueError(f"{path}: missing TBQ title")
        qid, title = match.groups()
        questions[qid] = {
            "title": title,
            "suite": path.parent.name,
            "source_problem": path.relative_to(ROOT).as_posix(),
        }
    return questions


def witness_map() -> dict[str, list[str]]:
    cases = json.loads((ROOT / "benchmark" / "ad_cases.json").read_text())["cases"]
    witnesses: defaultdict[str, list[str]] = defaultdict(list)
    for case in cases:
        for qid in case["question_ids"]:
            witnesses[qid].append(case["id"])
    return dict(witnesses)


def forward_statuses() -> dict[str, str]:
    coverage = json.loads((ROOT / "benchmark" / "problem_coverage.json").read_text())
    return {
        problem["id"]: problem["backends"]["thouless"]["status"]
        for problem in coverage["problems"]
    }


def companion_status(
    qid: str,
    row: dict[str, object],
    witnesses: dict[str, list[str]],
    forward_status: str,
) -> tuple[str, str]:
    role = row["role"]
    if role == "not_central":
        return (
            "ad_not_central",
            "AD is not the scientific acceptance target for this companion; "
            "continuous inner-loop sensitivities may still be useful.",
        )
    if role == "conditional":
        return (
            "conditionally_differentiable",
            "A local derivative is meaningful only inside the declared fixed "
            "branch or representation; the discrete event remains a forward gate.",
        )
    if qid in witnesses:
        return (
            "ad_native_verified",
            "A current Rust-native AD witness exercises the stated companion "
            "formulation; this does not claim completion of the full source TBQ.",
        )
    if forward_status != "implemented":
        return (
            "missing_forward_physics",
            "The complete Thouless forward workflow for the source TBQ is not "
            "yet implemented, so an end-to-end derivative claim would be premature.",
        )
    if qid in IMPLEMENTABLE_UNVERIFIED:
        return (
            "implementable_unverified",
            "All specialized primitives needed by this companion already exist; "
            "the remaining work is orchestration, a frozen oracle, a recorded "
            "result, and CI.",
        )
    missing = [
        capability
        for capability in row["required_capabilities"]
        if CAPABILITIES[capability]["current_maturity"] == "missing"
    ]
    partial = [
        capability
        for capability in row["required_capabilities"]
        if CAPABILITIES[capability]["current_maturity"] == "partial"
    ]
    if missing or partial:
        absent = ", ".join(missing + partial)
        return (
            "missing_ad_rule",
            "The forward workflow exists, but reusable native AD support is "
            f"incomplete for: {absent}.",
        )
    return (
        "implementable_unverified",
        "The required reusable primitives exist, but this exact companion "
        "workflow lacks a frozen oracle, recorded result, and CI witness.",
    )


def issue_for(status: str) -> str:
    if status == "missing_forward_physics":
        return SOURCE_ISSUE
    return NATIVE_AD_ISSUE


def build_payload() -> dict[str, object]:
    rows = parse_rows()
    sources = source_questions()
    witnesses = witness_map()
    forwards = forward_statuses()
    expected = {f"TBQ-{number:03d}" for number in range(1, 101)}
    if set(rows) != expected:
        raise ValueError(f"AD rows differ from TBQ-001..100: {set(rows) ^ expected}")
    if set(sources) != expected or set(forwards) != expected:
        raise ValueError("source catalog and forward audit must each contain TBQ-001..100")

    problems = []
    for qid in sorted(expected):
        row = rows[qid]
        source = sources[qid]
        forward = forwards[qid]
        status, reason = companion_status(qid, row, witnesses, forward)
        derivative_target = ", ".join(row["scientific_outputs"])
        problems.append(
            {
                "id": f"AD-{qid}",
                "tbq_id": qid,
                "title": source["title"],
                "suite": source["suite"],
                "source_problem": source["source_problem"],
                "ad_role": row["role"],
                "continuous_controls": row["continuous_controls"],
                "scientific_outputs": row["scientific_outputs"],
                "differentiable_formulation": row["differentiable_formulation"],
                "no_ad_baseline": row["no_ad_baseline"],
                "validity_boundary": row["validity_boundary"],
                "required_capabilities": row["required_capabilities"],
                "acceptance": {
                    "derivative_oracle": (
                        "Compare at least one predeclared directional derivative "
                        f"of {derivative_target} against an independent central "
                        "finite difference, analytic identity, or adjoint identity."
                    ),
                    "scientific_gate": (
                        f"The scientific acceptance and convergence conditions in "
                        f"{source['source_problem']} remain authoritative; the AD "
                        "path must reproduce the accepted forward observable before "
                        "any derivative or speed claim."
                    ),
                    "generalization_gate": (
                        "Repeat the value-and-derivative check on a held-out variant "
                        "declared by the source TBQ. Public examples are not held-out "
                        "evidence."
                    ),
                },
                "forward_status": forward,
                "ad_status": status,
                "status_reason": reason,
                "existing_witnesses": witnesses.get(qid, []),
                "issue": issue_for(status),
            }
        )

    status_counts = Counter(problem["ad_status"] for problem in problems)
    role_counts = Counter(problem["ad_role"] for problem in problems)
    forward_counts = Counter(problem["forward_status"] for problem in problems)
    capability_counts = Counter(
        capability
        for problem in problems
        for capability in problem["required_capabilities"]
    )
    return {
        "schema_version": 1,
        "meaning": (
            "One AD companion requirement for each immutable domain-first TBQ. "
            "The companions identify when differentiation changes the scientific "
            "workflow, the no-AD control, and the evidence needed. They do not "
            "redefine the source question or claim whole-TBQ completion."
        ),
        "source_catalog": "docs/problems/README.md",
        "source_issue": SOURCE_ISSUE,
        "native_ad_issue": NATIVE_AD_ISSUE,
        "status_vocabulary": {
            "ad_native_verified": (
                "A Rust-native witness validates this companion formulation; "
                "the source TBQ may still contain additional requirements."
            ),
            "implementable_unverified": (
                "Required reusable primitives exist, but the exact workflow lacks "
                "a frozen oracle, result record, or CI witness."
            ),
            "missing_ad_rule": (
                "The forward workflow is available, but at least one reusable "
                "parameterization, JVP, VJP, or composition rule is incomplete."
            ),
            "missing_forward_physics": (
                "The source scientific workflow itself is not fully implemented; "
                "native AD cannot yet be validated end to end."
            ),
            "conditionally_differentiable": (
                "A derivative is valid only within a fixed branch, graph, solver, "
                "or representation; the discrete event requires forward validation."
            ),
            "ad_not_central": (
                "AD may assist a continuous inner loop, but is not the scientific "
                "acceptance target for this question."
            ),
        },
        "role_vocabulary": {
            "essential": "AD changes tractability or directly yields the target sensitivity.",
            "helpful": "AD improves attribution or efficiency but is not required for the forward claim.",
            "conditional": "AD is meaningful only after a discrete branch or representation is fixed.",
            "not_central": "The scientific target is fundamentally a discrete or forward classification.",
        },
        "capabilities": CAPABILITIES,
        "summary": {
            "problems": len(problems),
            "status_counts": dict(sorted(status_counts.items())),
            "role_counts": dict(sorted(role_counts.items())),
            "forward_status_counts": dict(sorted(forward_counts.items())),
            "capability_demand_counts": dict(sorted(capability_counts.items())),
            "questions_with_existing_witnesses": sum(
                bool(problem["existing_witnesses"]) for problem in problems
            ),
        },
        "problems": problems,
    }


def render_problem(problem: dict[str, object]) -> str:
    def initial_upper(text: str) -> str:
        return text[:1].upper() + text[1:]

    role_explanation = {
        "essential": (
            "The requested sensitivity is itself a scientific observable or "
            "changes the tractability of calibration, control, or inverse design."
        ),
        "helpful": (
            "Differentiation improves attribution or efficiency, while the "
            "accepted forward scientific result remains independently obtainable."
        ),
        "conditional": (
            "A derivative is meaningful only after the relevant branch, graph, "
            "solver, or representation has been fixed."
        ),
        "not_central": (
            "The core acceptance target is a discrete or forward classification; "
            "AD is limited to a continuous inner loop."
        ),
    }[problem["ad_role"]]
    controls = "\n".join(f"- {item}" for item in problem["continuous_controls"])
    outputs = "\n".join(f"- {item}" for item in problem["scientific_outputs"])
    capabilities = "\n".join(
        f"- `{capability}` — {CAPABILITIES[capability]['label']}"
        for capability in problem["required_capabilities"]
    )
    witnesses = problem["existing_witnesses"]
    witness_text = (
        ", ".join(f"`{witness}`" for witness in witnesses)
        if witnesses
        else "None. Related public examples must not be treated as a held-out result."
    )
    acceptance = problem["acceptance"]
    return f"""---
id: {problem['id']}
tbq_id: {problem['tbq_id']}
suite: {problem['suite']}
ad_role: {problem['ad_role']}
ad_status: {problem['ad_status']}
forward_status: {problem['forward_status']}
---

# {problem['id']} — {problem['title']}

## Scientific anchor

This companion is derived from [{problem['tbq_id']} — {problem['title']}](../../{Path(problem['source_problem']).relative_to('docs').as_posix()}). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `{problem['ad_role']}`.

{role_explanation}

## Controls and outputs

Continuous controls:

{controls}

Scientific outputs:

{outputs}

## Differentiable formulation

{initial_upper(problem['differentiable_formulation'])}.

No-AD control: {initial_upper(problem['no_ad_baseline'])}.

## Validity and failure semantics

{initial_upper(problem['validity_boundary'])}.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** {acceptance['scientific_gate']}
2. **Derivative oracle:** {acceptance['derivative_oracle']}
3. **Generality:** {acceptance['generalization_gate']}

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

{capabilities}

## Current evidence and gap

- Source forward status for Thouless: `{problem['forward_status']}`.
- AD companion status: `{problem['ad_status']}`.
- Reason: {problem['status_reason']}
- Existing Rust-native witnesses: {witness_text}
- Tracking issue: [{problem['issue']}]({problem['issue']})

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../{Path(problem['source_problem']).relative_to('docs').as_posix()}). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
"""


def render_index(payload: dict[str, object]) -> str:
    summary = payload["summary"]
    status_lines = "\n".join(
        f"- `{status}`: {summary['status_counts'].get(status, 0)}"
        for status in STATUSES
    )
    role_lines = "\n".join(
        f"- `{role}`: {summary['role_counts'].get(role, 0)}" for role in ROLES
    )
    rows = []
    for problem in payload["problems"]:
        source_name = Path(problem["source_problem"]).name
        link = f"{problem['suite']}/{source_name}"
        witnesses = ", ".join(problem["existing_witnesses"]) or "—"
        rows.append(
            f"| [{problem['tbq_id']}]({link}) | {problem['title']} | "
            f"`{problem['ad_role']}` | `{problem['forward_status']}` | "
            f"`{problem['ad_status']}` | {witnesses} |"
        )
    return f"""# Domain-first AD companion requirements

This catalog adds exactly one differentiation analysis to each of the 100 immutable scientific questions in [`docs/problems`](../problems/README.md). It was produced before proposing Rust API changes. The existing ten executable AD workflows are evidence witnesses, not the source or boundary of the catalog.

Each companion states the continuous controls, scientific outputs, differentiable formulation, no-AD control, validity boundary, acceptance evidence, and reusable Rust-native capabilities. A companion status never implies that the entire source TBQ is complete.

## Summary

- Scientific anchors: {summary['problems']}
- Questions touched by an existing native AD witness: {summary['questions_with_existing_witnesses']}
- Canonical machine-readable matrix: [`benchmark/ad_requirements.json`](../../benchmark/ad_requirements.json)
- Derived capability plan: [`docs/rust-native-ad-capability-plan.md`](../rust-native-ad-capability-plan.md)

AD roles:

{role_lines}

AD companion statuses:

{status_lines}

The forward status is copied from the independent three-backend domain audit. `missing_forward_physics` and `missing_ad_rule` are intentionally separate: adding a pullback does not substitute for implementing the scientific solver.

## Catalog

| TBQ | Scientific anchor | AD role | Thouless forward | AD companion | Existing witness |
|---|---|---|---|---|---|
{chr(10).join(rows)}
"""


def render_capability_plan(payload: dict[str, object]) -> str:
    counts = payload["summary"]["capability_demand_counts"]
    rows = []
    for capability, spec in CAPABILITIES.items():
        rows.append(
            f"| `{capability}` | {counts.get(capability, 0)} | "
            f"`{spec['current_maturity']}` | {spec['description']} |"
        )
    return f"""# Rust-native AD capability plan derived from 100 scientific questions

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
{chr(10).join(rows)}

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

Unresolved scientific-forward gaps remain in [{SOURCE_ISSUE}]({SOURCE_ISSUE}); native AD and rule gaps remain in [{NATIVE_AD_ISSUE}]({NATIVE_AD_ISSUE}).
"""


def outputs(payload: dict[str, object]) -> dict[Path, str]:
    rendered: dict[Path, str] = {
        OUTPUT: json.dumps(payload, indent=2, sort_keys=False) + "\n",
        INDEX: render_index(payload),
        CAPABILITY_PLAN: render_capability_plan(payload),
    }
    for problem in payload["problems"]:
        source_name = Path(problem["source_problem"]).name
        rendered[DOC_ROOT / problem["suite"] / source_name] = render_problem(problem)
    return rendered


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    expected_outputs = outputs(payload)
    if args.check:
        failures = [
            path.relative_to(ROOT).as_posix()
            for path, expected in expected_outputs.items()
            if not path.is_file() or path.read_text() != expected
        ]
        expected_docs = {
            path
            for path in expected_outputs
            if DOC_ROOT in path.parents and path != INDEX
        }
        extra_docs = set(DOC_ROOT.glob("[0-9][0-9]-*/tbq-*.md")) - expected_docs
        failures.extend(path.relative_to(ROOT).as_posix() for path in extra_docs)
        if failures:
            print("generated AD requirement artifacts are stale:")
            for path in sorted(failures):
                print(f"  {path}")
            return 1
        print("AD requirement artifacts match the 100-question source")
        return 0
    for path, content in expected_outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    print(f"wrote {len(expected_outputs)} AD requirement artifacts")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyError, ValueError) as error:
        print(error, file=sys.stderr)
        raise SystemExit(1) from error
