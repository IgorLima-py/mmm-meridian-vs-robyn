# Results schema (v1.0) — the tool-agnostic contract

Every estimator run exports **one JSON file** in this schema; `scoring.py`
consumes *only* this schema. Adding another tool later means writing one
exporter — the scorer does not change (PLAN D8, BACKLOG scope guard).

File name convention: `<tool>_<arm>_seed<NNN>.json`, stored under
`runs/<tool>/results/`.

```json
{
  "schema_version": "1.0",
  "tool": "meridian",                  // lowercase id: meridian | robyn | ...
  "tool_version": "1.8.0",
  "arm": "national",                   // national | geo
  "seed_dataset": 101,                 // which data/sim/seed<NNN> was fit
  "run": {
    "tool_seed": 1,                    // the tool's own RNG seed(s)
    "runtime_seconds": 1234.5,
    "hardware": "WSL2 Ubuntu, RTX 4070 Super",
    "converged": true,
    "convergence_detail": {}           // tool-specific (R-hat, iterations...)
  },
  "channels": {
    "tv": {
      "roi": {
        "point": 1.72,
        "interval_low": 1.31,          // see interval semantics below
        "interval_high": 2.20,
        "interval_kind": "credible90"  // credible90 | candidate_range | ols_ci90
      },
      "mroi": { "point": 1.5 },        // optional; interval optional
      "contribution_share": {          // channel contribution / total revenue,
        "point": 0.071,                //   full modeling window
        "interval_low": 0.05,
        "interval_high": 0.09
      },
      "response_curve": {              // optional but expected for both tools
        "multipliers": [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0],
        "incremental_revenue": [0.0, ...],   // window-total, vs channel at 0
        "kind": "posterior_median"     // posterior_median | selected_model
      }
    }
  },
  "extras": {}                         // anything tool-specific; scorer ignores
}
```

## Semantics (pre-registered — do not reinterpret after seeing results)

- **ROI** = incremental revenue of the channel over the full modeling window /
  total spend of the channel in the window — matching the ground-truth
  definition (full-window zero-out; the generator's model is additive, so no
  cross-channel terms).
- **Intervals.** Meridian: central 90% credible interval (`credible90`).
  Robyn: min–max across the pre-registered candidate set defined in
  `SELECTION_RULE.md` (`candidate_range`); `point` is the selected model.
  These are *different uncertainty objects* — scored side by side but labeled,
  never averaged together. The oracle rungs (`analysis/oracle.py`) export an
  OLS 90% confidence interval conditional on their fixed shape (`ols_ci90`);
  they have used it since v1, and this line, added 2026-09-29 (C11), only
  writes down what the files already said.
- **contribution_share** uses total revenue (not media-only) as denominator.
- **response_curve** multipliers MUST be the generator grid
  `[0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0]` (scaling the
  channel's observed spend series); `incremental_revenue` is window-total.
- Optional fields may be omitted; the scorer then skips those metrics for that
  run and says so in the summary.
- `extras` is a dump for anything else worth keeping (e.g., Robyn Pareto
  candidates, Meridian prior spec); the scorer never reads it.

## Allocation files (added 2026-09-29, C11; first written by C12)

An allocation is not a fit: it is the budget split a tool's own optimiser
recommends, on a model already fitted. It is scored by `analysis/regret.py`
on the true curves, never by the per-channel metrics above.

File name: `<tool>_<arm>_allocation_seed<NNN>.json`, under
`runs/<tool>/results/`.

```json
{
  "schema_version": "1.0",
  "kind": "allocation",                // what makes it an allocation file
  "tool": "robyn",
  "tool_version": "3.12.1",
  "arm": "national",
  "seed_dataset": 101,
  "bounds": "primary",                 // a name in analysis/regret.py BOUNDS
  "run": { ... },                      // as above
  "channels": {
    "tv": { "multiplier": 1.37 }       // one per channel, nothing else
  },
  "extras": {}                         // the tool's own output, unread
}
```

- **multiplier** scales the channel's whole observed spend series over the
  window, the same object as a `response_curve` multiplier. Spend in money
  goes in `extras`, if at all.
- The budget is the observed window total: Σ multiplier × window spend must
  equal Σ window spend (`ground_truth.json`, `spend_total`).
- Every multiplier sits inside the named `BOUNDS` entry.

## Validation

`python analysis/validate_schema.py --strict <files>` checks result files
against this document; `--allocations` checks allocation files, their limits
and their budget. An **error** is anything the scorer would crash on or would
silently misread or skip — a channel name not in the ground truth, a missing
channel or ROI point, a curve off the grid, a non-finite number. A
**warning** is outside the letter of this document but harmless to the
scorer today — an unknown key, a file name off the convention. `--strict`
fails on both. A pattern that matches no file exits 2, not 0.
