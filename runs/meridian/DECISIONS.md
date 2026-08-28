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
