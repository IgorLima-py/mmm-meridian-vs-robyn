# The pre-publication audit

Before this piece was published, it was reviewed by an adversarial auditor whose
brief was to **fail** it: a `publication-auditor` agent (`.claude/agents/`) given
read-only access to the whole repository, run in nine rounds on 2026-09-10 and
2026-09-11. It indicts; it never edits. Every finding below was fixed by hand in
the working tree and re-audited.

This page is a record written from those rounds, not a verbatim transcript. It
exists so a reader can see what the piece was reviewed *for*, and what the review
actually caught.

## What it was reviewed for

1. **Number provenance.** Every number in the article, the README, the figures
   and the results text must trace to committed code or committed data.
2. **The forbidden framing.** Nothing may say or imply that a marketing-mix
   model was built here as a credential. The frame is tool comparison.
3. **Limitations.** "What neither tool can tell you" must be specific to this
   setup, not generic hedging.
4. **No absolute winner.** Every comparative claim carries its conditions —
   including in chart titles, where an unconditional verdict hides most easily.
5. **Simulated is never presented as real**, including in axis labels and in any
   figure that might be screenshotted away from its prose.
6. **Reproducibility.** The published commands, seeds, versions and configs must
   match what is committed.
7. **Coherence.** The article, README, `ORACLE.md`, `FIGURES.md`, `PLAN.md`, the
   decision logs and the three figures must tell one story with one set of
   numbers.

## What the nine rounds changed

Seven rounds returned BLOCK. Two returned SHIP — round 6, and round 9 after a
regression check. The findings that changed the substance of the piece, rather
than its wording:

- **The geo-versus-national comparison was a composition artefact.** The article
  reported Meridian's geo arm as the better aggregate, 0.499 against the national
  arm's 0.533. But 0.499 is a two-seed mean and 0.533 a five-seed mean; on the
  same two seeds the national arm scores **0.470**, so the geo arm is worse, not
  better. `analysis/scoring.py` now emits that same-seed comparison into
  `analysis/out/summary.md`, and every surface states it.
- **The pre-registration contradicted itself.** `docs/PLAN.md` D5 required every
  true adstock retention to sit inside Robyn's recommended bounds, with the
  stated reason that truth outside them "would rig the test". The parameter table
  committed alongside it set ooh to 0.6 (bound 0.1–0.4) and display to 0.4 (bound
  0–0.3). Robyn therefore could not express the true carryover on those two
  channels. Disclosed in dated amendments to D5 and to both decision logs rather
  than fixed, because fixing it means regenerating the data and re-running both
  tools.
- **Meridian's default Hill slope is fixed, not merely concave-leaning.** In
  Meridian 1.8.0 `slope_m` is `Deterministic(1.0)`, so under the pre-registered
  default priors every Hill slope is 1. Against true slopes of 0.7 to 2, Meridian
  cannot express the true curve on four of five channels, tv's S-shape furthest
  off. The pre-registration described this as a "concave-leaning" prior and
  promised it as a disclosed stressor; it was never disclosed until this audit.
- **The framing changed as a result.** The piece used to say both tools were
  treated generously. It now says each tool's setup excluded part of the truth,
  and names both exclusions wherever the numbers appear.
- **A missing limitation.** The simulator's adstock-plus-Hill form sits inside
  both tools' model families — sold as fairness, absent from the limitations. It
  is now in "What neither tool can tell you", together with what is still not
  exact: the per-geo Hill summed to a national total, and a mid-May event on no
  holiday calendar.
- **Three false statements in the supporting documents.** `ORACLE.md` said noise
  costs the oracle three of five betas (it is two); that no estimator could have
  done better on ooh and display (both tools land closer there, by luck); and
  that Meridian's prior median is the ceiling of its band (its ooh mean sits
  above it). All corrected, with dated notes.
- **Two captions made claims their own figures contradicted.** Figure 1 said "no
  estimator could have done better" where the tools' own dots do better; figure 2
  said the curves are "wrong at every budget" while its caption documented a
  crossing.

## What the audit hardened

- **The figure captions now check themselves.** `curve_facts()` and `roi_facts()`
  in `analysis/figures.py` compute the numbers figure 2's caption quotes and
  assert the qualitative claims both captions make. A re-export that breaks one
  stops the figure instead of shipping a stale caption. Both were negative-tested.
- **Caveats travel with the numbers.** Robyn's three caveats and Meridian's one
  are on the figures that show them, not only in the prose.
- **Reproducibility was re-verified against the final state**, not the state the
  claim was written for: a fresh clone into an empty directory, a virtualenv
  built only from `envs/analysis.lock.txt`, the six Layer 1 commands, and a
  byte-for-byte comparison of every regenerated artifact.

## What the audit did not resolve

- How much of Meridian's miss on tv, search and social comes from its fixed
  slope. Every oracle rung is handed the true slopes, so the ladder cannot
  apportion it. An oracle rung with the slope fixed at 1 would measure it;
  it is proposed in `docs/BACKLOG.md` and was not run.
- Whether Robyn's capped ooh carryover reached its tv estimate, or Meridian's
  slope misfit on tv reached its ooh estimate. The two channels' spend was
  designed to move together, so either leak is possible. Neither was tested.
- Whether Robyn's γ bounds contain the true half-saturation points. Its
  parametrisation is relative to each series' own range; this was not checked.

VERDICT: SHIP
