# BACKLOG — post-v1 roadmap and discarded ideas

Scope decisions from a 2026-08-27 review, recorded with rationale so they don't
get re-litigated from scratch later. **v1 = the two-tool comparison exactly as
specified in `PLAN.md`.**

## Scope guards for v1

- **Two tools only (Meridian + Robyn), no expansion now.** The "Robyn dormant
  since mid-2025 while Meridian ships monthly" angle is *perishable* — in 18
  months it's history, not news. Publishing v1 while it's news is worth more
  than a bigger version later. Nothing below may delay v1 publication.
- **The scoring harness must be tool-agnostic** (PLAN Phase 2): every estimator
  exports the same results schema; the scorer consumes only that schema. Adding
  a third tool later = writing one exporter, not rewriting the harness.

## v2 backlog (only after v1 is published)

1. **PyMC-Marketing as a third estimator — PROMOTED 2026-09-09 to `C7` in
   `docs/ROADMAP.md`.** Full spec, including the logistic-vs-Hill fairness trap
   and the repo-rename decision, lives there; this entry is a pointer so the
   two files do not drift.

   What changed since this was written: PyMC-Marketing reached a stable **1.0.0
   on 2026-08-07**, and the oracle ladder (`analysis/ORACLE.md`) took over the
   *defensive* half of the rationale — it proves the failure is not a simulator
   bug far better than a third tool arguing by accumulation. What survives is
   the open question a third estimator alone can answer: Robyn's effect shares land
   0.54pp from spend share, by design (DECOMP.RSSD), and whether Meridian's estimates shrink toward its
   ROI prior is untested — so does a third tool have an anchor of its own? Still
   strictly post-publication.
2. **Attention-weighted MMM — a separate piece, not this repo's scope.**
   Simulate a world where the *truth* is attention-weighted exposure, fit the
   tools on raw spend, measure the bias. A live industry debate (attention
   metrics vendors vs. spend-based MMM), fully simulable, and it reuses this
   repo's simulator + harness. Sequenced after both this piece and the
   ad-attention-gap piece exist. Cross-note: correlating *this* repo's simulated
   results with *real* attention/retention metrics from that other project is
   not meaningful (different worlds, no common units) — the real bridge is
   reusing the harness here and, in that future piece, parameterizing the
   simulation with published attention-decay findings.
3. **Frequency:** one paragraph in "What neither tool can tell you" (neither
   tool models exposure frequency in its core regression, so the conclusion is
   known in advance) — optionally a stretch arm. Never a phase of its own. See
   item 5 below for the more precise version of this: Meridian *can* take
   reach & frequency as input, just not in v1's like-for-like design.
4. **Channel granularity — split `social`/`display` by vehicle** (Meta, Google,
   TikTok, etc.) instead of one aggregate channel each. Not a free improvement:
   more channels means more mutually correlated media columns to identify from
   the same 156 weeks of national data, which is the opposite of what a
   stress-test scenario wants. The 5 channels in v1 were chosen to probe
   specific known asymmetries (tv's S-curve, ooh's DECOMP.RSSD trap, search's
   near-exogeneity), not to mirror a realistic media mix — revisit only with a
   documented reason a finer split adds a new test, not just more realism.
5. **Give Meridian its native reach & frequency (RF) input, as a side
   experiment.** Meridian accepts a distinct RF channel type (reach + frequency
   instead of spend + impressions); Robyn has no equivalent. v1 gives both
   tools the same input shape (spend + impressions) on purpose, to keep the
   comparison like-for-like (PLAN D4, §5 fairness ledger) — so this capability
   was deliberately left unused, not overlooked. A v2 side experiment could run
   one Meridian-only arm with an RF channel to show what the extra input type
   buys on its own, but it must never be blended into the head-to-head
   Meridian-vs-Robyn numbers, since Robyn cannot receive the same input.

6. **The sensitivity mini-arm PLAN Phase 5 left optional.** One re-run of a
   single tool with a changed setting — Meridian's ROI prior, or Robyn's
   hyperparameter bounds — to show how much of the shrinkage is the setup
   rather than the tool. Dropped from v1 on 2026-09-09 for two reasons: the
   oracle answers the same question with five seeds behind it instead of one
   arm, and re-running a tool with different settings *after* seeing its
   results is precisely the move the pre-registration exists to prevent. In v2
   it must be pre-registered before the run, on both tools symmetrically or on
   neither.

7. **Pin the R side the way the Python side is pinned.** `envs/setup_robyn.sh`
   installs Robyn from CRAN with no version and *writes* `nevergrad.lock.txt`
   from the resolved environment instead of installing from it — so the R half
   of the stack records rather than reproduces. Fix is
   `remotes::install_version("Robyn", "3.12.1")` plus installing nevergrad from
   the committed lock, then re-running one seed to confirm the extract is
   unchanged. Not blocking v1: the resolved versions are recorded in the run
   JSONs and the limitation is stated in `envs/ENVIRONMENT.md`. Raised by the
   pre-publication audit on 2026-09-09.
8. **An oracle rung with the Hill slope fixed at 1.** Meridian's default priors
   fix every Hill slope at 1 (`Deterministic(1.0)`; `docs/PLAN.md` amendment of
   2026-09-11), while every oracle rung is handed the true slopes — so the ladder
   cannot say how much of Meridian's miss on tv, search and social comes from
   that constraint. A rung built like L3 but with slope 1 would measure it on the
   analysis layer, in seconds. Proposed by the pre-publication audit on
   2026-09-11 and not run: a new rung is new analysis, not a correction.
9. **Re-run with D5's contradiction removed.** The pre-registration set ooh's and
   display's true adstock outside Robyn's recommended bounds (`docs/PLAN.md`
   amendment of 2026-09-11). Removing it means moving those two truths inside
   the bounds, regenerating the data and re-running both tools on all five seeds
   — every published number changes. v1 discloses the contradiction instead;
   this is worth doing only if the disclosure comes to dominate how the result
   is read.

## Discarded (reopen only with new information)

- **Commercial SaaS (e.g., Recast) as a compared tool.** Closed-source, paid,
  can't be run locally on our simulated data, and a reproducible published
  comparison is impossible. Their public teardowns remain cited as sources in
  `REFERENCES.md` (flagged as vendor-authored). Dead end.
- **LightweightMMM.** Deprecated and superseded by Meridian itself; comparing
  against it answers nothing current. Historical footnote only.
- **Brand-health-tracking (BHT) data.** No public BHT dataset exists — it's
  proprietary panel data — so simulating one would mean inventing a brand
  response structure with no public basis to defend. Modeling brand equity as a
  generic simulated control variable is possible and public-domain, but it buys
  almost nothing for a *tool* comparison: both tools would treat it as just
  another control column. Out.
