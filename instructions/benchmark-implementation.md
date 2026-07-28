# Thouless benchmark implementation instructions

## Objective

Maintain an executable, source-traceable benchmark for the full 100-question
tight-binding domain catalog. Compare native Thouless Rust with the original
PythTB 2.0 and Kwant 1.5 packages where each package is scientifically
applicable. Count only whole scientific problems, not isolated API calls or
related observables.

## Non-negotiable rules

1. Each case must state a scientific question, observable, model parameters,
   expected invariant or reference value, tolerance, and LKM provenance.
2. LKM retrieval scores are ranking signals, not confidence or correctness
   probabilities.
3. LKM questions motivate the benchmark. A simplified lattice problem must be
   labeled as an adaptation and must not be presented as a reproduction of the
   source paper.
4. Original PythTB and Kwant installations must be used for their baselines.
   Never benchmark Thouless compatibility modules while labeling them as the
   original packages.
5. Thouless cases must execute a native Rust binary linked to the pinned
   Thouless commit. Python may orchestrate processes but may not replace the
   Rust scientific calculation.
6. A core scientific workflow outside a package's declared scope must be marked
   `not_applicable`. An in-scope workflow lacking a specialized primitive must
   be marked `missing_capability`. Do not hide a separate NumPy or SciPy
   implementation behind that package's name.
7. Prefer analytic invariants and metamorphic relations over stored numerical
   arrays. Cross-backend agreement is supporting evidence, not ground truth.
8. Do not recognize case identifiers inside a numerical routine to return
   expected answers. Case identifiers may select a general model and workflow.
9. Accuracy is a required gate. Timing is descriptive: report cold build
   separately from warmed execution, use the same machine, and never fail CI
   on wall-clock ordering.
10. Preserve exact versions, hardware metadata, commands, raw result JSON, and
    failures. Do not silently remove a failing backend or widen a tolerance.
11. Public cases are not held-out validation. Generality claims require a
    separate evaluator with unseen models and hidden expected results.
12. Backend-level problem assessments use exactly four states:
    `implemented`, `implementable_unverified`, `missing_capability`, and
    `not_applicable`. `Implementable_unverified` requires source evidence for
    every specialized primitive. `Missing_capability` means a general solver
    or representation must be added. `Not_applicable` is reserved for a core
    workflow outside the package's declared scope.
13. Model definitions, parameter loops, statistics, and gauge-invariant
    postprocessing may be shared after the named backend constructs the
    Hamiltonian. Do not attribute an unrelated external scientific solver to a
    backend merely because its matrix can be exported. A documented package
    dependency may provide a numerical kernel only when the package exposes the
    required representation as its normal workflow; record that dependency
    explicitly.
14. The documented parameter range is part of the scientific problem. A dense
    toy-size path is not evidence that a backend has the required sparse or
    production-scale capability.

## Required checks

- The original manifest contains exactly twenty unique seed cases.
- The domain manifest contains twenty-two executable witnesses and the generated
  audit contains exactly 100 questions by three backends.
- Every domain question maps to one or more named checks in `question_gates`;
  every named check must be present and passing in the recorded backend result.
- Every one of the 300 backend-question assessments names its required,
  available, and missing capabilities and links available capabilities to
  pinned source-level API evidence.
- The domain problem catalog contains exactly one hundred unique questions in
  twenty suites. Sixty-seven currently have complete executable witnesses; the
  remaining thirty-three documents stay proposed.
- The AD companion catalog contains exactly one requirement per domain
  question. Every companion states its derivative variable, scientific output,
  no-AD control, validity boundary, acceptance evidence, capability demand, and
  issue-backed status. Existing AD witnesses do not imply whole-question
  coverage.
- Every case has a public LKM GCN identifier and source paper.
- Every case has at least one native Thouless implementation.
- Every scored result records backend version and commit where applicable.
- Schema, manifest, reference, and provenance checks pass.
- All applicable backend outputs satisfy their declared scientific gates.
- CI runs the deterministic accuracy profile; performance reports are generated
  manually or on dedicated hardware.

## Domain problem documentation

The canonical proposed-problem catalog is
[`docs/problems/README.md`](../docs/problems/README.md). Keep one scientific
question per Markdown file. Every problem file must define:

1. the scientific question and benchmark adaptation;
2. the model family and parameters, including ranges and units;
3. the required computation and expected scientific result;
4. an acceptance class, numerical convergence conditions, and held-out
   model-family variations;
5. LKM and paper provenance; and
6. an honest implementation status.

Do not mark a problem `executable` merely because a related case exists.
Executable status requires a frozen case definition, an independent oracle,
backend execution, result records, and CI. Held-out validation remains a
separate evaluator-owned claim.
