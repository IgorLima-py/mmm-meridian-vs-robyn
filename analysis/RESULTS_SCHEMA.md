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
        "interval_kind": "credible90"  // credible90 | candidate_range
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
  never averaged together.
- **contribution_share** uses total revenue (not media-only) as denominator.
- **response_curve** multipliers MUST be the generator grid
  `[0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0]` (scaling the
  channel's observed spend series); `incremental_revenue` is window-total.
- Optional fields may be omitted; the scorer then skips those metrics for that
  run and says so in the summary.
- `extras` is a dump for anything else worth keeping (e.g., Robyn Pareto
  candidates, Meridian prior spec); the scorer never reads it.
