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
   the open question a third estimator alone can answer: Meridian shrinks toward
   its ROI prior and Robyn toward spend share, so does a third tool have an
   anchor of its own? Still strictly post-publication.
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
   known in advance) — optionally a stretch arm. Never a phase of its own.

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
