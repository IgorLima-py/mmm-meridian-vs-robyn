# Robyn run decisions (Phase 4)

Written before comparing anything to ground truth (D8 spirit). Applies
uniformly to all seeds. The model-selection rule itself is pre-registered in
`analysis/SELECTION_RULE.md`; this file documents the input mapping and the
API-level interpretation it allows for.

| # | Decision | Rationale |
|---|---|---|
| RD1 | **Inputs:** `robyn.csv` (weekly national), spend as `paid_media_spends`, impressions as `paid_media_vars` (exposure), `competitor_index` as context var, revenue KPI | Mirrors the Meridian input mapping (both tools get exposure + spend, PLAN §3) |
| RD2 | **Hyperparameter names follow the exposure variables** (`tv_I_alphas`, …) | Robyn 3.12 convention when `paid_media_vars` ≠ spends (friction F7); bounds per D5: θ tv 0.3–0.8, ooh 0.1–0.4, digital 0–0.3; α 0.5–3; γ 0.3–1 |
| RD3 | **Prophet: trend + season + holiday, `prophet_country = "US"`** | The generator has Black Friday + Christmas bumps (US calendar covers both) and a mid-May event **not** on any holiday calendar — disclosed: Robyn's holiday regressor cannot see it, Meridian's knots must absorb it too; symmetric-ish stressor |
| RD4 | **`ts_validation = TRUE`**, `train_size` bounds 0.5–0.8 | Robyn's own demo-recommended flow; NRMSE on validation drives the Pareto front |
| RD5 | **2000 iterations × 5 trials, `cores = detectCores()-1` (11)** | PLAN Phase 4 spec; multi-core is the WSL2 payoff (F-log) |
| RD6 | **Tool seed = 123 + (dataset_seed − 101)** → 123…127 | D9 "seed=123+", one fixed seed per dataset |
| RD7 | **Error score = `Robyn:::errors_scores(..., ts_validation=TRUE)`** (internal but Robyn's own); fallback if the call fails: min-max-normalized NRMSE(validation) + DECOMP.RSSD, equal weights | SELECTION_RULE.md allows API-level mapping as long as it is Robyn's own composite intent, documented here. The JSON records which path ran |
| RD8 | **ROI = `xDecompAgg$roi_total`** (decomp contribution / channel window spend); **contribution_share = `xDecompAgg` / observed total revenue** | Matches the pre-registered definitions; denominator is *observed* revenue per RESULTS_SCHEMA.md |
| RD9 | **Response curves reconstructed from the selected model's own parameters:** adstock (θ) → windowed series → fitted Hill (α, γ with inflexion from the *observed* adstocked series, via `saturation_hill(x_marginal=)`) → × coef; evaluated on the schema multiplier grid. **Self-check:** the reconstruction at m=1 must match Robyn's `xDecompAgg` within 1% or the export aborts | Robyn has no native "scale the whole spend series" counterfactual; this reproduces its fitted response exactly and the m=1 identity proves it. Impressions are linear in spend per week (generator), so scaling spend scales exposure |
| RD10 | **mROI = [inc(1.01) − inc(1.00)] / (0.01 × spend)** on the same reconstruction | Matches the ground-truth +1% definition |
| RD11 | **`runtime_seconds` = `robyn_run` wall-clock only**; `robyn_outputs`+clustering time reported separately in `extras` | Comparable to Meridian's sampling wall-clock; M7 keeps both numbers |
| RD12 | **Heavy artifacts** (OutputModels/OutputCollect RDS) → `outputs/robyn/seed<NNN>/` (gitignored); committed extract = schema JSON only | Two-machine workflow rule |
| RD13 | Robyn's per-candidate ROI table is kept in `extras.candidate_roi_table` | Feeds M4 (does the candidate spread contain the truth) without schema changes |

Deviations discovered during execution are appended below with timestamps
rather than silently edited into the table.

## Amendments

- **2026-08-28 (convergence escalation, decided before any ground-truth
  comparison):** at the pre-registered 2000×5, Robyn's own convergence check
  passed fully only on seed105 (101/103/104 fail DECOMP.RSSD; 102 fails NRMSE
  and DECOMP.RSSD). Symmetric with the Meridian geo-arm escalations, seeds
  101–104 get ONE re-run at **4000 iterations × 5 trials** (same tool seeds);
  the exported JSON is the 4000×5 run whatever its convergence outcome, and
  the 2000×5 flags stay recorded here. seed105 keeps its converged 2000×5 run
  (the pre-registered spec). No further escalation after this.
