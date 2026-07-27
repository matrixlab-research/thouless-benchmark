# LKM Evidence Snapshot for the Domain Problem Catalog

Retrieved: 2026-07-27

Interface: public LKM search and reasoning endpoints

Purpose: domain-first derivation of tight-binding benchmark problems

## Preservation boundary

The files under `raw/` are verbatim LKM JSON responses. No returned field was
removed, normalized, or rewritten. The snapshot supports:

- [`docs/tight-binding-domain-benchmark-requirements.md`](../../../docs/tight-binding-domain-benchmark-requirements.md);
- the [100-question problem catalog](../../../docs/problems/README.md); and
- later construction of executable public and isolated held-out cases.

The discovery results contain 846 deduplicated research-question or claim nodes
and 835 deduplicated papers. The successful reasoning searches add 250 chains
from 243 papers; discovery and reasoning together contain 1,048 unique papers.
These are coverage counts, not truth or novelty claims.

## Discovery coverage

The 21 discovery files cover general model construction, Wannier and fitted
models, bands and singularities, magnetic flux, bulk topology, boundaries,
quantum geometry, disorder, transport, superconductivity, non-Hermiticity,
Floquet dynamics, interactions, moiré and strain, magnetism, optical and
thermoelectric response, aperiodic systems, defects, multiscale validation,
scientific-scale numerics, and inverse problems.

`raw/01-general.json` contains 50 nodes. Each numbered discovery file from
`02` through `21` contains 40 nodes. Nodes and papers can occur in more than one
file, so file-level totals are larger than the deduplicated corpus.

## Reasoning coverage

The first ten files under `raw/reasoning/` contain 25 returned reasoning chains
each:

1. model construction;
2. topology and boundaries;
3. quantum geometry and response;
4. disorder and defects;
5. open transport;
6. extended Hamiltonians;
7. complex geometry;
8. interacting and self-consistent models;
9. numerical scaling; and
10. inference and validation.

The direct lookup retained in
`raw/reasoning/11-zero-chern-nonlinear-boundary.json` returned `claim not
found` for an older identifier. It is preserved as a failed lookup rather than
silently replaced. The current nonlinear-response problem specifications use
successful chain `1159462780185608201_8`.

## Interpretation

LKM nodes seed research questions, observables, counterexamples, and validation
strategies. Retrieval scores are ranking signals, not scientific confidence
probabilities. Every compact lattice case is a benchmark adaptation and must
not be described as a reproduction of the cited paper.
