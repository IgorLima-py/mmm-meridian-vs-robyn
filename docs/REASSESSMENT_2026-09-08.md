# Reassessment — 2026-09-08

> **Snapshot, not a live document (added 2026-09-09).** Everything below is the
> state of the project on 2026-09-08, and it is left unedited on purpose — it
> is the record of what was known when the decisions were made. Three things
> moved afterwards, so do not quote its Robyn figures or its reading of
> Meridian:
>
> - The Robyn escalation this document recommended has since run. Seeds 102,
>   103 and 104 went to 4000x5 and still fail Robyn's own convergence check
>   (`runs/robyn/DECISIONS.md`). The mixed-spec risk R6 is closed: every seed's
>   spec is now documented rather than mixed-and-unexplained.
> - With those final extracts the Robyn row of the scoring table is
>   −0.540 / 0.555 / 0.16 / 0.277, not the −0.506 / 0.538 / 0.20 / 0.263 quoted
>   below, and the Meridian-vs-Robyn gap is 0.533 vs 0.555, not 0.533 vs 0.538.
> - Its reading that Meridian collapses to its prior median (~1.22) did not
>   survive either. `analysis/ORACLE.md` rejected it on 2026-09-09: Meridian's
>   five national channel means span 0.74 to 1.24, with the prior median near the
>   top of that range, not its centre — compression, not collapse. (This
>   bullet was added in the pre-publication audit, 2026-09-11.)
>
> The current numbers of record are `analysis/out/summary.md` and
> `analysis/ORACLE.md`; the charts built on them are in `analysis/figures/`.

A 360° review of this project after Google shipped Meridian GeoX (2026-09-01)
and Meridian 2.0.0 (2026-09-03). Written before any implementation decision;
every external claim was re-verified against a primary source on 2026-09-08 and
carries its URL. Numbers about this repo were produced by running the committed
code, not read off earlier notes.

**Bottom line up front.** The project's *design* survives the landscape change.
The project's *headline* does not: the interesting result in the data we already
have is not "which tool is closer to truth" — both are equally far — but **how
each tool fails when a channel is unidentifiable, and that they fail toward
different anchors while reporting very different confidence**.

§6.1 flagged one blocking check: we had not shown the truth was recoverable at
all. **It has since been run** — see `analysis/ORACLE.md` and §6.1 below. The
answer is per channel, not per dataset: for tv, search and social the truth *is*
in the data and neither tool found it; for ooh and display it is not, and both
tools only *appear* accurate there by coincidence. That result is what makes the
comparison publishable, and it is now the spine of the piece.

---

## 1. What exists in this repo today

66 tracked files, clean tree, 5 commits of substantive work between 2026-08-27
and 2026-08-28. Phases 1–4 of `docs/PLAN.md` are done; Phases 5–6 are not
started.

| Area | State | Evidence |
|---|---|---|
| Planning | Complete and unusually thorough | `docs/PLAN.md` (246 lines, D1–D10 decisions), `docs/REFERENCES.md` (~90 sources, vendor-authored ones flagged) |
| Simulator | Complete, seeded, deterministic | `simulation/` (584 lines), 5 seeds × 4 files in `data/sim/`, `python -m simulation.checks` gates on C1–C6 |
| Ground truth | Counterfactual, per seed | `ground_truth.json`: true ROI, mROI, contribution share, response curves on a 10-point multiplier grid |
| Scoring harness | Complete, pre-registered, tool-agnostic | `analysis/scoring.py` (252 lines), schema in `analysis/RESULTS_SCHEMA.md`, Robyn selection rule pre-registered in `analysis/SELECTION_RULE.md` |
| Environments | Reproducible from scratch | `envs/*.sh` idempotent; `envs/ENVIRONMENT.md` with exact versions and an 8-item friction log (F1–F8) |
| Meridian runs | 7 runs exported (5 national + 2 geo), Meridian 1.8.0 | `runs/meridian/results/*.json`; all 5 national converged; geo seed101 did not (max R-hat 1.118, time effects) |
| Robyn runs | 5 runs exported, Robyn 3.12.1 | `runs/robyn/results/*.json`; seed101 (4000×5) and seed105 (2000×5) pass Robyn's own convergence check; 102–104 do not |
| Decision logs | Written before results were seen, amendments timestamped | `runs/meridian/DECISIONS.md` (MD1–MD11 + 3 amendments), `runs/robyn/DECISIONS.md` (RD1–RD13 + 1 amendment) |
| Analysis | **Not started** | `analysis/out/` does not exist |
| Article / public README | **Not started** | `README.md` is 8 lines, still "work in progress" |

**Assessment of quality.** The methodological discipline here is well above the
market artifact this project is measured against. Pre-registration of both the
scoring harness and the Robyn selection rule, before any run, is the single
strongest thing in the repo — it is what makes the eventual result
non-cherry-pickable. The friction log (F1–F8) is real, specific, and directly
publishable. Nothing in the history fails the "readable by anyone, forever"
test.

**One process gap.** `runs/robyn/DECISIONS.md` amendment RD says seeds 101–104
get one escalation to 4000×5. Only seed101 ran; 102–104 were interrupted. The
committed extracts are therefore a **mix of specs** (seed101 at 4000×5,
seeds 102–105 at 2000×5). That is defensible only if disclosed exactly that way
in the article, and it is cleaner to either finish the escalation or drop it and
publish all five at the pre-registered 2000×5. Leaving it mixed and unexplained
would be the kind of thing this project exists to criticize.

### 1.1 First look at the results (scorer run today, 2026-09-08)

`python analysis/scoring.py --results runs --data data/sim` on the current
extracts. These are preliminary — 3 of 5 Robyn JSONs may still be replaced by
the escalation — but the pattern is stable across all five seeds and both arms.

| Arm | mean ROI rel. err | mean abs. rel. err | interval covers truth | mean interval width / true ROI |
|---|---|---|---|---|
| Meridian national (5 seeds, all converged) | −0.312 | 0.533 | 0.60 | 1.615 |
| Meridian geo (2 seeds; seed101 not converged) | −0.499 | 0.499 | 0.50 | 1.196 |
| Robyn national (5 seeds; 3 not converged) | −0.506 | 0.538 | 0.20 | 0.263 |

Per channel, national arm, averaged over 5 seeds:

| Channel | true ROI | share of revenue **variance** | Meridian est. ROI | Robyn est. ROI |
|---|---|---|---|---|
| tv | 1.8 | 0.240 | 1.20 | 0.77 |
| search | 3.5 | 0.010 | 1.06 | 0.83 |
| social | 2.5 | 0.008 | 0.76 | 0.79 |
| ooh | 0.8 | 0.0007 | 1.24 | 0.78 |
| display | 1.2 | 0.0006 | 0.74 | 0.62 |

Three things fall out of this, and they are the piece:

1. **Neither tool is more accurate.** Mean absolute ROI error is 0.533
   (Meridian) vs 0.538 (Robyn) — a difference of half a percentage point on
   five seeds. Any headline of the form "X recovered truth better" is not
   supported by this data. The pre-registered no-winner rule turns out to be
   the empirically correct call, not just an editorial preference.
2. **Each tool collapses toward its own anchor.** Meridian's estimates cluster
   around ~1.2 — the median of its default ROI prior, `LogNormal(0.2, 0.9)`,
   median e^0.2 ≈ 1.22 ([prior_distribution.py](https://github.com/google/meridian/blob/main/meridian/model/prior_distribution.py)).
   Robyn's estimates cluster far harder: within a single seed, all five channel
   ROIs land inside a band of ~0.02–0.25 (seed101: 0.919–0.939; seed103:
   0.809–0.857; seed105: 0.566–0.605) while the truth ranges 0.8–3.5. A single
   ROI for every channel is exactly what "effect share pulled to spend share"
   looks like — the DECOMP.RSSD signature the design was built to probe (PLAN
   D6/M5). **Two completely different mechanisms, the same symptom: the
   estimate is the tool's prior belief, not a measurement.**
3. **The uncertainty story is the real asymmetry.** Robyn's candidate spread is
   ~6× narrower than Meridian's credible interval and contains the truth 20% of
   the time vs Meridian's 60% (against a nominal 90%). Both are miscalibrated;
   Robyn is confidently miscalibrated. That is a genuinely useful, decision-
   relevant finding for a practitioner, and it is a finding about *uncertainty
   honesty*, which is this project's declared differentiator anyway.

**And the reason the estimates are anchors: 4 of the 5 channels are nearly
invisible in the data.** The generator's own variance decomposition, averaged
over the five seeds, gives tv 24% of revenue variance and the other four
channels **0.06% to 1.0% each** — less than the 6–9% iid noise. Their
contributions are large in *level* (search: 9% of revenue) but nearly constant
in *time*, so they are absorbed by the baseline. `simulation/checks.py` C3 only
gates the media **total** variance share into [0.10, 0.35]; it never checks the
per-channel split, so the simulator passed its own gate with ~85% of the media
signal concentrated in one channel. This is a real design gap in Phase 2, found
today.

---

## 2. Landscape re-verification (all checked 2026-09-08)

The briefing was accurate as of when it was written and is **wrong in two
places now**. Both matter.

### 2.1 Google Meridian

| Fact | Value | Source |
|---|---|---|
| Latest release | **2.0.0**, 2026-09-03 (changelog dated 2026-09-02) | [PyPI JSON](https://pypi.org/pypi/google-meridian/json), [CHANGELOG](https://github.com/google/meridian/blob/main/CHANGELOG.md) |
| Version this repo ran | 1.8.0, 2026-08-15 | `envs/ENVIRONMENT.md` |
| 2026 cadence | 1.5.0 (Jan) → 2.0.0 (Sep): 11 releases in 8 months | PyPI |
| Repo activity | last push 2026-09-07; 1,522 stars; 102 open issues | [GitHub API](https://api.github.com/repos/google/meridian) |
| Python | 3.11–3.13 per docs; `requires_python >= 3.10` in metadata | [install docs](https://developers.google.com/meridian/docs/user-guide/installing) |
| Still pins tfp-nightly | yes — `tfp-nightly[substrates-jax]==0.26.0.dev20260130`, `tensorflow>=2.21,<2.22` | [PyPI 2.0.0 JSON](https://pypi.org/pypi/google-meridian/2.0.0/json) |

**2.0.0 breaking changes** (from the changelog): default backend toggled **from
TensorFlow to JAX**; `NotFittedModelError` moved to `common.errors`;
time-selection arguments across `Analyzer` and `BudgetOptimizer` now "strictly
require date string coordinates (`Sequence[str]`), removing support for
positional boolean masks"; `max_rhat` renamed `max_r_hat` in
`ConvergenceCheckResult`; `Meridian.populate_cached_properties()` removed;
`EDASeverity` statuses changed from `INFO/ATTENTION/ERROR` to
`INFO/REVIEW/FAIL`.

**2.0.0 additions that matter to this project:** prior calibration from
incrementality experiments, and *channel calibration recommendations* (the model
tells you which channel would benefit most from a test).

### 2.2 Meridian GeoX

| Fact | Value | Source |
|---|---|---|
| Latest version | **1.0.1**, 2026-09-03 — not 0.1.1 | [PyPI JSON](https://pypi.org/pypi/meridian-geox/json) |
| Full release history | 0.1.0rc1 (08-19), rc2 (08-25), 0.1.1 (09-01), **1.0.0 (09-01)**, 1.0.1 (09-03) | PyPI |
| Repo | created 2026-04-02, last push 2026-09-03, 27 stars, 3 open issues, Apache-2.0 | [GitHub API](https://api.github.com/repos/google/meridian-geox) |
| Landing page | live with real content, no longer "coming soon" | [developers.google.com/meridian/geox](https://developers.google.com/meridian/geox) |
| The extra | **works now.** `google-meridian` 2.0.0 declares extra `geox` → `meridian-geox>=0.1.1` | PyPI 2.0.0 metadata (`provides_extra`, `requires_dist`) |

Two corrections to the briefing: GeoX went **0.1.1 → 1.0.0 → 1.0.1 within 48
hours**, so "a v0.1.1 library" understates both the churn and the maturity
signal; and the failing install command was failing because the extra is named
`geox`, not `meridian-geox` — `pip install "google-meridian[geox]"` is the
correct form and is now declared in the published metadata.

The MMM↔experiment integration is real and named: `CalibrationBuilder` with
`with_meridian_geox_experiment_result()`, which takes a GeoX `AnalysisResult`
and extracts point estimate, standard error, spend and dates to build an ROI
prior ([set custom priors](https://developers.google.com/meridian/docs/advanced-modeling/set-custom-priors-past-experiments),
[calibrate treatment priors](https://developers.google.com/meridian/docs/advanced-modeling/roi-priors-and-calibration)).

### 2.3 Meta Robyn

| Fact | Value | Source |
|---|---|---|
| Last commit on `main` | **2025-06-27** ("fix: refresh window end issue #1270") | [GitHub API](https://api.github.com/repos/facebookexperimental/Robyn/commits?sha=main) |
| Repo `pushed_at` | 2026-01-26 (a non-`main` branch — do not read this as activity on main) | GitHub API |
| CRAN | 3.12.1, published **2025-07-02**, maintainer Bernardo Lares, R ≥ 4.0.0 | [CRAN](https://cran.r-project.org/web/packages/Robyn/index.html) |
| Not archived | 1,513 stars, 115 open issues — active-but-unmaintained | GitHub API |
| Calibration input | point estimate only — `calibration_input` takes `channel, liftStartDate, liftEndDate, liftAbs, spend, confidence, metric`; MAPE.LIFT becomes a third objective | [robyn_inputs docs](https://rdrr.io/cran/Robyn/man/robyn_inputs.html), [discussion #768](https://github.com/facebookexperimental/Robyn/discussions/768) |

**Star counts are 1,522 vs 1,513.** Meridian did pass Robyn, but by nine stars,
this month. Writing "Meridian overtook Robyn in popularity" as a headline would
be technically true and rhetorically dishonest; the defensible statement is
about *maintenance cadence*, where the gap is not close: 11 releases in 2026 vs
zero commits on main in 14 months.

### 2.4 Everything else

| Tool | State on 2026-09-08 | Source |
|---|---|---|
| **GeoLift** (Meta, `facebookincubator`) | last push 2026-06-30, 263 stars, not archived. Still a separate org from Robyn, no native MMM integration | [GitHub API](https://api.github.com/repos/facebookincubator/GeoLift) |
| **PyMC-Marketing** | **1.0.0 on 2026-08-07** ("after two years of 0.x releases, this is our stable API"), 1.1.0 on 2026-08-27 | [GitHub releases](https://github.com/pymc-labs/pymc-marketing/releases) |
| **Heusch (2026), arXiv 2608.21128** | "Structural Estimation of MMM Parameters from Geo-Experiments", submitted 2026-08-21. Reports a synthetic paid-search channel with true ROAS 4.20 estimated at **10.61** by an observational MMM (8.41 even with oracle controls), recovered to 4.31/4.14 by their structural geo method | [arXiv](https://arxiv.org/html/2608.21128v1) |
| **Heusch (2026), arXiv 2608.21130** | Companion: synthetic benchmark with *endogenous* spend; generator and notebooks public | [arXiv](https://arxiv.org/html/2608.21130) |

**Critical detail about Heusch, verified in the full text:** he did **not run
Meridian, Robyn or pymc-marketing**. He implemented his own observational MMM
using the seasonal controls those tools ship as standard ("MMM (realistic)" vs
"MMM (oracle ctrl.)"). His paper is about a *specification* class, not about
the software.

**Therefore the gap this project claims still exists.** As of today there is
still no published work that runs the actual Meridian and Robyn packages on the
same simulated dataset with known ground truth and scores truth recovery. The
closest three remain: PyMC Labs' benchmark (vendor-authored, excluded Robyn),
the ICATSD 2026 repo (both tools, scored stability/agreement, not truth), and
Heusch (right question, own implementation). That premise of `PLAN.md` §1.1 was
re-checked today and holds.

---

## 3. Does the thesis still hold?

### 3.1 The hypothesis, attacked

> "The thesis stops being 'I compared two tools' and becomes 'I simulated data
> with known truth, measured which tool recovers it under which conditions, and
> showed how a geo experiment calibrates the model.' Comparison is the means;
> ground truth is the product."

**The first half is right and should go further. The second half — the geo
experiment arm — should not be in v1.**

**Where the hypothesis is right.** Ground truth *is* the product, and after
today's scorer run that is not an aspiration, it is the only thing that
survived: without truth, the two tools' outputs are just two different-looking
tables and the piece is another feature comparison. With truth, the piece can
say *both were wrong by roughly half, in different directions, for mechanically
explicable reasons*. Nobody else can say that, because nobody else has the
truth.

**Where it needs sharpening.** "Which tool recovers the truth under which
conditions" is still framed as a contest, and the data says there is no contest
to report: 0.533 vs 0.538 mean absolute error. If the piece leads on relative
accuracy, the honest answer is "a tie", which is an anticlimax and invites the
reader to conclude the exercise was uninformative. The finding that *is* there
is stronger, and it is not comparative at all:

> **When a channel's contribution has no time variation, neither tool measures
> it — each returns its own prior. Meridian returns the median of its ROI prior
> (≈1.2) with a wide interval that still misses truth 40% of the time. Robyn
> returns spend share with an interval 6× narrower that misses 80% of the time.
> The difference between the tools is not accuracy; it is whether the output
> tells you it doesn't know.**

That is a claim about how to *read* MMM output, which is exactly the framing
`BRIEF.md` committed to ("here's how to read them"), it is decision-relevant,
and it cannot be produced without ground truth. Comparison remains the vehicle.

**Where to push back hardest: the geo-experiment arm.** Adding a GeoX arm means
(a) upgrading to Meridian 2.0.0 and re-running all 7 Meridian runs, because
`CalibrationBuilder` does not exist in 1.8.0; (b) extending the simulator to
generate a geo experiment with a known true lift — new simulation design work,
not a config change; (c) accepting that Robyn's side is a point estimate fed to
`calibration_input` while Meridian's is a full prior, so the arm stops being a
fair comparison and becomes a Meridian feature demo; and (d) publishing against
a six-day-old 1.0.1 library on a repo with 27 stars. Estimated cost: 12–20 h on
top of the ~6 h left in the current plan, with a real chance of a Meridian 2.1
landing mid-work.

The perishable asset here is the timing angle, and `BACKLOG.md` already ruled
that nothing may delay v1 publication. A GeoX arm is a *better second piece*
than a worse first one: it has its own news hook (GeoX is new, GeoLift is not
integrated, Heusch just published the academic version of the same argument),
it reuses this repo's simulator and harness, and it is the natural sequel. In
v1 it earns a paragraph in "What neither tool can tell you" — *the honest fix
for the failure we measured is an experiment, and here is what each ecosystem
now offers* — with versions and dates cited. That paragraph costs an hour and
captures most of the value.

### 3.2 The thesis to publish

*(Revised 2026-09-08, after the oracle ran — see §6.1.)*

> **Same simulated data, known truth, two open-source MMM tools. Both got the
> ROIs wrong by roughly half — but so did a model that was handed the true
> adstock and saturation parameters. So the first question is not "which tool
> won", it is "was the answer in the data at all?" For three of the five
> channels it was, and neither tool found it. For the other two it was not, and
> both tools happen to look their best exactly there. Here is the check that
> tells those cases apart, and what it means for reading any MMM output.**

The oracle turns a tie into a result. Without it, the honest summary is "0.533
vs 0.538, no winner, possibly our simulation was broken." With it, the summary
is that both tools miss the recoverable channels by 34–76% while shrinking
toward their own priors, and that an ordinary least-squares fit on the same data
produced correctly calibrated intervals that neither tool managed. The
comparison survives as the vehicle; the recoverability check is the
contribution.

Framing checks: it never claims a built MMM; the dataset is simulated and said
so up front; no absolute winner; every number traces to committed code; the
limitations section is the spine, not an appendix.

### 3.3 One structural weakness to name

The repo is named and framed `meridian-vs-robyn`. If the result is "neither
recovered the truth", a *two*-tool sample invites the obvious rebuttal: "your
simulation was broken." A third estimator is the cheapest defense against that,
and `BACKLOG.md` already scoped PyMC-Marketing as a v2 exporter (~3–5 h, same
Python env, plugs into the schema). It just got cheaper and more credible:
PyMC-Marketing hit a stable **1.0.0 on 2026-08-07**. This is *not* a v1
recommendation — but §6.1 describes a much cheaper version of the same defense
that is mandatory.

---

## 4. What this project will not be able to conclude

The limitations section of the published piece. Written as things that cannot be
claimed, not as apologies.

**About generalization**

1. **Nothing about which tool is better in general.** Five seeds, one generating
   process, one panel size, one noise level, one collinearity setting. The
   result is conditional on all of them, and the article must say so in the same
   breath as the result.
2. **Nothing about real data.** Simulated spend is exogenous — no budget chasing
   demand. That is the *easy* regime; Heusch's work shows the endogenous regime
   is where the large biases live. Measured accuracy here is an **upper bound**
   on what these tools do in production.
3. **Nothing about time-varying effectiveness.** True adstock, saturation and
   betas are constant across 156 weeks. Real media effectiveness is not. Both
   tools assume near-constancy, so the simulation is *kind* to both.
4. **Nothing about the functional-form question.** The generator uses geometric
   adstock + Hill, which sits inside both tools' model families by design. A
   generator using neither form would be a different and harder test; it is
   stretch arm S4 and will not be in v1.

**About the tools' scope**

5. **Nothing about reach & frequency**, Meridian's flagship differentiator — the
   simulator has no R&F channels and Robyn cannot take them, so the one place
   Meridian is architecturally unique goes untested.
6. **Nothing about Robyn's budget allocator or Meridian's optimizer.** Both
   produce reallocation recommendations; testing whether those recommendations
   pay off requires an experiment, not a model. (This is exactly the unearned
   claim in the market artifact this project is measured against.)
7. **Nothing about geo modeling as such.** The geo arm is 2 seeds, Meridian
   only, and seed101 did not converge. It can say "geo did not rescue the
   national failure here"; it cannot say what geo modeling is worth.
8. **Nothing about calibration.** Neither run used calibration. The piece can
   describe what each ecosystem offers (Meridian 2.0.0 `CalibrationBuilder` +
   GeoX 1.0.1; Robyn `calibration_input`, point estimate only) with dates and
   citations, but it has measured none of it.

**About the runs themselves**

9. **Version-frozen, and already stale.** Results are Meridian **1.8.0** and
   Robyn **3.12.1**. Meridian 2.0.0 shipped 2026-09-03 with a different default
   backend; these numbers do not describe it.
10. **Not fully converged everywhere.** Meridian geo seed101 sits at max R-hat
    1.118, driven by time-effect parameters; Robyn's own convergence check fails
    on some seeds. Both are published as-is per the pre-registered gates, and
    every affected conclusion must be labeled.
11. **Two different uncertainty objects.** Meridian's 90% credible interval and
    Robyn's min–max across Pareto candidates are not the same kind of thing.
    They are reported side by side and never averaged, and the coverage
    comparison is descriptive, not a formal test.
12. **Robyn's result depends on a selection rule.** It was pre-registered, which
    removes cherry-picking, but a different defensible rule could yield a
    different selected model. The candidate spread is reported for that reason.
13. **No statistical inference across seeds.** Five seeds support description,
    not significance testing. No p-values, no confidence intervals on the
    comparison itself.
14. **Bit-reproducibility is hardware-bound.** Seeds and versions are pinned, so
    a re-run reproduces the analysis; identical floating-point output requires
    the same hardware and CUDA stack.

**About authorship**

15. **This is not a production MMM and does not claim to be.** It is a
    comparative analysis of two open-source tools on simulated data, written by
    a user of those tools.

---

## 5. Risks

Ordered by expected damage.

| # | Risk | Likelihood | Damage | Mitigation |
|---|---|---|---|---|
| R1 | ~~The headline finding is an artifact of the simulator~~ | — | — | **CLOSED 2026-09-08.** The oracle recovers the true betas exactly on noiseless revenue; generator, ground truth, schema and scorer agree. §6.1 |
| R2 | **Design flaw: 4 of 5 channels carry <1% of revenue variance each**, and C3 never caught it because it only gates the media total | **Confirmed** | Medium (was High) | **Downgraded.** The oracle showed 3 of 5 channels are still recoverable, so the scenario is usable as-is; the two that are not become the counter-example. Fix the checker, disclose the gap, keep the data (§6.3) |
| R3 | **Meridian 2.0.0 makes the published numbers historical on day one.** Default backend TF→JAX, plus six breaking API changes | **Confirmed** | Medium | State the version in the article's opening and in every table header; do not re-run for v1 (§6.2) |
| R4 | **API churn if we chase GeoX.** 0.1.1 → 1.0.0 → 1.0.1 in 48 hours; 27 stars; some docs pages still thin | High | Medium | Do not build a GeoX arm in v1 (§3.1). Cite versions and dates instead |
| R5 | **The timing angle decays.** "Robyn dormant while Meridian ships monthly" is news now, history in a year. It is already 14 months since Robyn's last main commit | Certain, slow | Medium | Ship v1. Nothing in the backlog may delay it |
| R6 | **Mixed Robyn specs in the committed extracts** (seed101 at 4000×5, rest at 2000×5) reads as post-hoc tuning to a hostile reader, even though the amendment was written before scoring | Medium | Medium | Finish the escalation (≈60 min, this machine) **or** revert seed101 to its 2000×5 run. Do not publish mixed-and-unexplained |
| R7 | **Compute cost of any re-run.** A full Meridian re-run is 7 runs × 5–23 min on this GPU; Robyn is 5 × ~10–17 min on CPU. Cheap individually, but a simulator change re-runs *everything* | Medium | Medium | Settle §6.1 and §6.3 before touching anything |
| R8 | **Machine lock-in.** All heavy runs live on the GPU desktop; the laptop cannot rebuild the environments (no admin). A hardware failure means a fresh WSL2 build elsewhere | Low | High | `envs/*.sh` are idempotent and committed; the committed extracts — not the pickles — are what the article needs, and they are in git |
| R9 | **`tfp-nightly` pin rot.** Meridian 2.0.0 still hard-pins `tfp-nightly==0.26.0.dev20260130`. Nightly builds are not guaranteed to remain downloadable | Low-Medium | High | `envs/meridian.lock.txt` is committed; state the risk in the reproducibility section — it is itself a finding about the tool |
| R10 | **A competing publication lands first.** Heusch is publishing in this exact space and moving fast | Medium | Medium | Our angle (the real packages, two ecosystems, uncertainty calibration) is distinct from his (own implementation, endogeneity, structural fix). Cite him; do not duplicate him |

---

## 6. Decisions required before implementation

### 6.1 RESOLVED 2026-09-08 — the oracle check

Built as a four-rung ladder in `analysis/oracle.py`, exported through the
standard schema, scored by the same harness. Full write-up: `analysis/ORACLE.md`.

**The harness is sound.** Fitting the oracle design to noiseless revenue returns
the true betas with relative error `0.0` on every channel. Generator, ground
truth, schema and scorer agree exactly. The tools' error is not our bug.

**Recoverability is per channel.** Oracle error is monotone in each channel's
signal-to-noise ratio; the tools' error is not.

National arm only, all three estimators, 5 seeds:

| channel | signal/noise | oracle err | Meridian err | Robyn err |
|---|---|---|---|---|
| tv | 1.91 | **0.04** | 0.34 | 0.57 |
| search | 0.39 | **0.15** | 0.70 | 0.76 |
| social | 0.34 | **0.24** | 0.70 | 0.68 |
| ooh | 0.11 | 0.97 | 0.55 | 0.19 |
| display | 0.10 | 0.76 | 0.38 | 0.48 |

For **tv, search and social the truth is in the data and neither tool found
it** — they miss by 34% to 76%. For **ooh and display it is not**, and the tools
look accurate there only because those channels' true ROIs (0.8, 1.2) sit near
the value each shrinks toward. Reading a tool's own per-channel error table
without the oracle inverts the ordering completely for Robyn (ooh is its *best*
channel and no estimator can measure ooh at all) and partially for Meridian.

Caveat that travels with every Robyn figure: three of its five seeds (102, 103,
104) fail Robyn's own convergence check at the pre-registered 2000x5, and the
escalation is still pending — that is C1 in `docs/ROADMAP.md`.

**The shrinkage belongs to the tools.** Oracle ROI bias spans −0.01 to +0.12
(error by variance, correct centre); Meridian is −0.31 and Robyn −0.51 (error by
systematic shrinkage). And the oracle rung that estimates its own baseline
covers the truth **92%** of the time against a nominal 90%, versus Meridian's
60% and Robyn's 20% — so "the data were hard" does not excuse the tools'
interval miscalibration.

Consequence for §6.3: **keep the data.** No regeneration, no re-runs.

### 6.2 Meridian 1.8.0 or re-run on 2.0.0?

**Recommendation: stay on 1.8.0 for v1**, and say so loudly. The runs are done
and converged; 2.0.0's breaking changes hit exactly the surfaces
`run_meridian.py` uses (`Analyzer` time selection, `max_rhat`); "results are as
of Meridian 1.8.0, 2026-08-15; 2.0.0 shipped 2026-09-03 and changed the default
backend" is *itself* one of the article's findings about tool churn; and a
re-run costs a day for numbers that will be stale again by November. The
counter-argument — a reader asking "why not the current version" — is answered
in one sentence.

### 6.3 SETTLED 2026-09-08 — keep the data

The oracle answered this. Regenerating was only worth it if *no* channel were
recoverable; three of five are, and those three carry the finding. The two that
are not (ooh, display) are not waste — they are the counter-example that shows
why a tool's own per-channel error table cannot be trusted alone.

Two follow-ups this creates, both cheap and both improvements to the repo rather
than to the result:

- **C3 gets a per-channel companion.** The current check gates only the media
  *total* variance share; a per-channel signal-to-noise floor (or simply "run
  the oracle and require a minimum accuracy") is the gate that would have caught
  this before any GPU time was spent. Worth adding to `simulation/checks.py` and
  documenting as a limitation of how the v1 scenario was validated.
- **The oracle becomes a pre-registered step**, not a rescue. Any future
  scenario runs it before the tools do.

### 6.4 GeoX arm in v1?

**Recommendation: no.** One cited paragraph in "What neither tool can tell you",
and a v2 piece. See §3.1.

### 6.5 Robyn escalation

Finish 102–104 at 4000×5 (≈60 min on the GPU desktop, unattended) or revert
seed101 to 2000×5. **Recommendation: finish it** — it is cheap, it closes the
amendment as written, and it removes R6 entirely.

---

## 7. Sources

All accessed 2026-09-08.

- https://pypi.org/pypi/google-meridian/json · https://pypi.org/pypi/google-meridian/2.0.0/json
- https://github.com/google/meridian/blob/main/CHANGELOG.md
- https://api.github.com/repos/google/meridian
- https://github.com/google/meridian/blob/main/meridian/model/prior_distribution.py
- https://developers.google.com/meridian/docs/user-guide/installing
- https://developers.google.com/meridian/docs/advanced-modeling/set-custom-priors-past-experiments
- https://developers.google.com/meridian/docs/advanced-modeling/roi-priors-and-calibration
- https://developers.google.com/meridian/geox
- https://pypi.org/pypi/meridian-geox/json · https://api.github.com/repos/google/meridian-geox
- https://api.github.com/repos/facebookexperimental/Robyn · https://api.github.com/repos/facebookexperimental/Robyn/commits?sha=main
- https://cran.r-project.org/web/packages/Robyn/index.html
- https://rdrr.io/cran/Robyn/man/robyn_inputs.html · https://github.com/facebookexperimental/Robyn/discussions/768
- https://api.github.com/repos/facebookincubator/GeoLift
- https://github.com/pymc-labs/pymc-marketing/releases
- https://arxiv.org/html/2608.21128v1 · https://arxiv.org/html/2608.21130

Everything already catalogued in `docs/REFERENCES.md` from the 2026-08-27
planning session remains valid; this document records only what changed and what
was re-verified.
