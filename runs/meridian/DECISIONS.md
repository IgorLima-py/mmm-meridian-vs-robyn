# Meridian run decisions (Phase 3)

Every non-default choice, and every default we relied on, with rationale.
Written **before** looking at any scored result (D8 spirit). Applies uniformly
to all seeds — nothing is tuned per seed.

| # | Decision | Rationale |
|---|---|---|
| MD1 | **Inputs:** impressions as `media` (exposure), spend as `media_spend`, `kpi_type="revenue"`, `competitor_index` as the single control | Both tools receive exposure + spend (PLAN §3); revenue KPI is the common ground |
| MD2 | **Priors: Meridian defaults** untouched | PLAN Phase 3 pre-registers "default priors"; the default concave-leaning saturation prior vs our S-shaped tv channel is a *disclosed* stressor (PLAN §5c) |
| MD3 | **Knots — national arm: `enable_aks=True`** (Meridian's Automatic Knot Selection). Meridian's national default (`knots=None` → 1 knot) forces a constant baseline, which cannot express the simulated trend + seasonality + holidays | Fairness symmetry: Robyn gets its own automated baseline machinery (Prophet trend/season/holiday); AKS is Meridian's sanctioned automated equivalent, not a hand-tuned knob. Chosen knot count is exported per run (`extras.n_knots_used`) |
| MD4 | **Knots — geo arm: Meridian default** (`knots=None` → `n_times` knots) | The documented default for geo models; time effects are estimable via cross-geo pooling |
| MD5 | **`max_lag=13`** (default is 8) | The generator's adstock support is 13 weeks (public in `simulation/config.py`). D5 gave Robyn hyperparameter bounds that contain the truth; a `max_lag` that can express the true carryover is the symmetric courtesy to Meridian. Disclosed rather than silently using 8 |
| MD6 | **Sampling: 7 chains × (500 adapt / 500 burn-in / 1000 keep), `seed=1`** for every run | PLAN suggests 4–7 chains × 1000 keep; 7 chains gives 7000 draws and a strong R-hat basis; identical seed across runs per D9 |
| MD7 | **Convergence gate: max R-hat < 1.1** across all parameters + divergence count reported | PLAN Phase 3 gate |
| MD8 | **ROI/mROI/contribution from Meridian's own counterfactuals:** `Analyzer.roi()` (zero-out, full window), `Analyzer.marginal_roi()` (+1%), `incremental_outcome()` / observed total revenue | These match the pre-registered ground-truth definitions (full-window zero-out incl. carryover; +1% mROI; total-revenue denominator) — no re-derivation on our side |
| MD9 | **Response curves via `incremental_outcome(scaling_factor1=m)`** on the schema's multiplier grid; posterior **median**; `m=0` fixed at 0 | Exactly the generator's curve definition (scale the observed spend series, window-total incremental vs zero). Meridian's `response_curves()` helper reports means, and the schema pre-registered medians |
| MD10 | **`runtime_seconds` = posterior sampling wall-clock, XLA compile included** (flagged in `extras`) | Honest M7 accounting: a fresh user pays compile time too; noted so it is not read as steady-state sampling speed |
| MD11 | **Heavy artifacts** (`save_mmm` pickle) go to `outputs/meridian/` (gitignored, live on the run machine); the committed extract is only the schema JSON | Two-machine workflow rule (CLAUDE.md) |

Deviations discovered during execution, if any, are appended below with
timestamps rather than silently edited into the table.

## Amendments

- **2026-08-28 (before any geo run completed):** MD1 said `competitor_index`
  is a control in both arms. Meridian *rejects* it in the geo arm: it does not
  vary across geos, and with the default one-knot-per-time-period it is
  "collinear with time and redundant in a model with a parameter for each time
  period" (Meridian's own `ValueError`). Resolution: the geo arm drops
  `competitor_index` and keeps the default knots (MD4) — statistically a no-op
  since the per-time knots span the same national-temporal space; the national
  arm keeps the control. Disclosed here rather than silently changed.
- **2026-08-28 (geo non-convergence at MD6 settings):** at 7 × (500 adapt /
  500 burn-in / 1000 keep), the geo arm did NOT converge: seed101 max R-hat
  1.222 (23 divergences), seed102 max R-hat 1.301 (75 divergences). Standard
  MCMC remedy applied — adaptation/burn-in doubled to 1000/1000 for the geo
  arm only (sampler mechanics; priors, estimands, and data untouched). The
  first-attempt numbers stay recorded here; the exported geo JSONs are from
  the extended run, whose own convergence status is reported inside them
  honestly (if still not converged, that is the published result).
- **2026-08-28 (second and final escalation):** 1000/1000 still failed the
  gate — seed101 max R-hat 1.228 (28 div), seed102 1.157 (23 div). Per-param
  diagnosis: the offenders are the time-effect parameters (`mu_t`,
  `knot_values`, i.e. the 156 weekly knots); on seed101 the media parameters
  (`roi_m` 1.14, `beta_m` 1.12) also exceed the gate, on seed102 they do not.
  Final attempt: 2000 adapt / 2000 burn-in, geo arm only. Exported JSONs now
  carry `rhat_by_param` so the article can separate baseline-parameter from
  media-parameter non-convergence. No further escalation after this — three
  documented attempts is the honest budget; whatever status results is
  published as-is.

- **2026-09-09 (divergence counts for the runs that actually shipped).** The
  amendments above report divergence counts for the *superseded* geo attempts
  (500/500 and 1000/1000) and never for the 2000/2000 runs that were exported
  and scored. Recording them now, read straight from the committed extracts'
  `run.convergence_detail.n_divergences` — no re-run, no change to any number:
  **geo seed101 = 64 divergences** (max R-hat 1.118, not converged) and **geo
  seed102 = 122 divergences** (max R-hat 1.024, counted as converged by the
  pre-registered 1.1 gate). The national arm, at the pre-registered 500/500,
  runs 1 to 6 divergences per seed. seed102 therefore passes the gate this
  project pre-registered while carrying a divergence count an order of
  magnitude above the national runs; it is published as-is per those gates,
  with the count disclosed rather than the gate revised after the fact.
  Raised by the pre-publication audit, not by a re-run.
