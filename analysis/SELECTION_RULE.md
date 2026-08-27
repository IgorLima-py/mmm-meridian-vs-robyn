# Robyn model-selection rule (pre-registered)

Committed BEFORE any Robyn run (PLAN D8). Purpose: Robyn returns a Pareto
front of many candidate models; without a pre-registered rule, picking one
after seeing the comparison invites cherry-picking (in either direction).

## The rule

1. Run Robyn with the settings in PLAN Phase 4 (2000 iterations x 5 trials,
   recommended hyperparameter bounds, fixed seed per dataset seed).
2. Run Robyn's own clustering step (`robyn_clusters` via `robyn_outputs`) with
   default settings.
3. **Selected model** = the candidate Robyn itself marks as best by its own
   combined error score (its normalized NRMSE + DECOMP.RSSD composite — plus
   MAPE only if calibration were used, which it is not here) **within the
   winning cluster** (the cluster containing that lowest-error candidate).
4. **Candidate set** (for `candidate_range` intervals in the results schema) =
   the "best model per cluster" set returned by Robyn's clustering.
5. If clustering fails or returns a single cluster, fall back to: candidate
   set = all Pareto-front models; selected = lowest combined error score.

## Notes

- Exact function/argument names follow Robyn 3.12.1's API at run time; if the
  API differs from the above naming, the *intent* (Robyn's own recommended
  flow, its own composite error, no manual re-picking) governs, and any
  mapping decision gets documented in `runs/robyn/DECISIONS.md` before results
  are compared to ground truth.
- The spread across the candidate set is reported alongside the selected
  model — Robyn's model-selection ambiguity is itself a measured outcome
  (metric M4/M5 in PLAN §4), not noise to hide.
- Symmetric guard for Meridian: default priors, sampling settings fixed in
  PLAN Phase 3, no prior tweaking after seeing ground-truth comparisons (the
  optional sensitivity mini-arm in Phase 5 is labeled as such).
