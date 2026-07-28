# SSH hopping identifiability with a local marker

**Case:** `ad_identifiability`  
**Motivating requirement:** TBQ-098  
**AD gate:** AD-G14

## Scientific question

Can automatic sensitivities expose the ambiguity of determining SSH
intracell and intercell hoppings from bulk spectra, and can a local
Hamiltonian marker lift that ambiguity?

## Benchmark adaptation

For the SSH Bloch Hamiltonian, the bulk energies are invariant under swapping
`t1` and `t2`. At the symmetric point `t1 = t2`, the Fisher matrix therefore
has the exact local null direction `(1, -1)`. A marked intracell bond breaks
the swap symmetry and is appended as a local spectral observation. This
implements a physical identifiability workflow rather than planting an
abstract rank-deficient matrix.

## Parameters

- Model parameters: `2`.
- Symmetric point: `(t1, t2) = (0.8, 0.8)`.
- Spectral observations: `4` momenta.
- Local perturbation observations: `1`.
- Fisher analysis: exact symmetric `2 x 2` eigenproblem.

## Required computation

Build bulk SSH energy gradients with native eigenderivatives, form the Fisher
matrix, compare its smallest-eigenvector direction with the analytic
hopping-swap nullspace, and repeat after adding the local bond marker.

## Expected result

The bulk spectral Fisher matrix is rank deficient in the SSH hopping-swap
direction. The local marker gives nonzero sensitivity along that direction
and removes the degeneracy. Swapped hopping pairs retain the same bulk
spectrum but differ under the marker.

## Acceptance

- Spectral null eigenvalue and eigenvector match the analytic construction.
- Augmented minimum Fisher eigenvalue is strictly positive.
- Two spectrally equivalent parameter sets give distinct local predictions.

## Evidence and boundary

LKM node `gcn_8dff8e3ffbb54f6e` reports reconstruction of tight-binding
couplings from spectra and local eigenstate weights through Hamiltonian
markers; `gcn_ab12a53ddc864f6e` provides an SSH tight-binding
parameterization in graphene nanoribbons. Primary sources:
[Burgarth and Ajoy (2017)](https://doi.org/10.48550/arXiv.1705.07725) and
[Rizzo et al. (2018)](https://doi.org/10.1038/s41586-018-0375-9). Raw
retrieval evidence is preserved under
`evidence/lkm/2026-07-28-ad-research-workflows`. This deterministic case
establishes structural identifiability, not a noise-calibrated posterior.
