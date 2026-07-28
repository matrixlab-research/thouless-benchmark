# LKM evidence for native-AD research workflows

This bundle records the domain-first discovery pass used to replace synthetic
AD capability demonstrations with ten named tight-binding research workflows.
The raw files are unedited responses from the public Bohrium LKM API.

## Method

For each workflow, the search started from a physical system, observable, and
research task without mentioning Thouless or its Rust API. Searches used
`reasoning_only=true` with `top_k=15`. One representative conclusion was then
traced with the LKM reasoning endpoint. Retrieval scores were used only for
ranking; they were not interpreted as confidence or scientific correctness.

The source paper motivates the workflow. Each executable case is explicitly a
compact benchmark adaptation unless it reproduces the paper's full system,
data, and conclusion. The independent benchmark oracle comes from analytic
symmetry, finite differences, a separately recomputed invariant, residuals, or
public excluded inputs rather than the LKM answer.

## Frozen selection

| Case | Physical workflow | Selected LKM conclusion | Source paper |
|---|---|---|---|
| `ad_spectral_recovery` | Rice-Mele spectral and Wannier-sector inference | `gcn_c52f0ae9e48644a6` | Klimkin et al., arXiv:2106.08638 |
| `ad_degenerate_projector` | BHZ Kramers-subspace differentiation | `gcn_00da49cbfa6c47d6` | Zhang et al., Nature Physics 10, 387 (2014) |
| `ad_identifiability` | SSH hopping identifiability with a local marker | `gcn_8dff8e3ffbb54f6e` | Burgarth and Ajoy, arXiv:1705.07725 |
| `ad_quantum_metric` | Rice-Mele quantum-geometry sensitivity | `gcn_e264632a5a0e4780` | Villani et al., arXiv:2308.16070 |
| `ad_topological_design` | QWZ Chern-phase inverse design | `gcn_9da619e467814f8e` | Christiansen, Wang, and Sigmund, PRL 122, 234502 (2019) |
| `ad_surface_green_implicit` | SSH boundary Green-function sensitivity | `gcn_e2f9ddf1a54846e4` | Maurer et al., arXiv:2112.11814 |
| `ad_inverse_transport` | Double-quantum-dot transmission inference | `gcn_a5eb3fecc5264ac5` | Zhou et al., arXiv:2202.05098 |
| `ad_lead_device_sensitivity` | Resonant-level device/contact sensitivity | `gcn_cb7923a88d2246b7` | Yang et al., Chaos 23 (2013) |
| `ad_sparse_adjoint_scaling` | Many-parameter Anderson sparse response | `gcn_a72c49f810f54d63` | Zhou et al., arXiv:2202.05098 |
| `ad_robust_kpm_design` | Bond-disordered SSH KPM design | `gcn_dd35cab4703b4260` | Whittaker, McCarthy, and Duan, arXiv:2311.11040 |

The manifest records additional LKM nodes when the physical system and the
computational method came from different papers.

## Files

- `raw/01-*.json` through `raw/10-*.json`: discovery searches, including
  variables, paper metadata, ranking signals, and trace identifiers.
- `raw/reasoning/01-*.json` through `raw/reasoning/10-*.json`: reasoning-chain
  responses for the selected representative conclusions.

Public excluded momenta, energies, and disorder seeds remain visible
development checks. This evidence bundle does not provide isolated held-out
validation.
