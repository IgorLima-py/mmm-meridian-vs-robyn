# The oracle check — is the truth recoverable at all?

Every number on this page is regenerable from committed code, and lands in a
committed artifact rather than only in a terminal:

```
python analysis/oracle.py                              # fits the four rungs
python analysis/oracle.py --diagnostics                # -> analysis/out/diagnostics.md
python analysis/scoring.py --results runs --data data/sim --out analysis/out
```

Scored metrics — every ROI error, coverage and interval width below — come from
`analysis/out/summary.md`. The scenario numbers the harness does *not* produce
(the noiseless-recovery check, the per-channel signal-to-noise and regressor CV
columns, and the two cross-channel correlation views) come from
`analysis/out/diagnostics.md`. Both are committed, so every figure on this page
can be checked against a file rather than re-derived by the reader.

Results below are from 2026-09-09, all 5 seeds, generator 1.0.0, scored by the
same pre-registered harness as the tools. The Robyn columns are the final
extracts, after the 4000x5 escalation closed (`runs/robyn/DECISIONS.md`).

The three charts built on these numbers live in `analysis/figures/`, drawn by
`analysis/figures.py`; `analysis/FIGURES.md` records what each one shows and
which choices went into it.

## Why this exists

Meridian and Robyn both missed the true ROIs by roughly half, in the same
direction. That is *also* exactly what a bug in our ground truth, our export or
our scorer would look like. A comparison that cannot tell those two cases apart
is worthless, so before any of it gets published we fit models that know things
no real tool knows, and score them identically.

An oracle is **not a competing estimator**. It is handed the generator's own
functional form, the true adstock retention, the true Hill parameters, and (on
two rungs) the true baseline. Nobody can run one on real data. Its only job is
to draw the line between *the tools failed* and *the data could not have
answered*.

## The four rungs

| Rung | Tool id | What it is given | What it isolates |
|---|---|---|---|
| L1 | `oracle_geo_truebase` | geo regressors from the true parameters; true baseline and control subtracted from revenue; only the 5 betas free | validates ground truth + schema + scorer |
| L2 | `oracle_nat_truebase` | same, but regressors rebuilt from the **national aggregate** exposure | the aggregation (Jensen) gap any national-arm tool pays |
| L3 | `oracle_nat_estbase` | national regressors; baseline **estimated** (intercept + linear trend + 3 annual Fourier harmonics + observed control) | the ceiling for a national tool with perfect knowledge of adstock and saturation |
| L4 | `oracle_geo_estbase` | geo regressors; per-geo intercepts + shared trend/Fourier + control estimated | the same ceiling for the geo arm |

All four are unconstrained OLS. A negative fitted beta is reported, not clipped.

`oracle.py` refuses to run if the rebuilt `World` disagrees with the committed
`national.csv` by more than 1e-6 relative — the regressors and the shipped data
are provably the same world.

## First result: the harness is sound

Fitting L1's design to **noiseless** revenue (`y = M @ beta_true`, no noise
term) returns the true betas with a maximum relative error of **1.2e-14** across
all five seeds — machine precision. The generator, the ground-truth definition,
the results schema and `scoring.py` therefore agree with each other. Whatever
the tools' error is, it is not an artifact of our pipeline.

Add the simulated noise back (7% CV per geo) and the same design loses two of the
five betas — ooh and display, each off by about 100% on average. That is the whole
finding. *(Corrected during the pre-publication audit, 2026-09-10/11: this sentence
said "three", which contradicted the per-channel table below and the C7 floor.)*

## Second result: recoverability is per channel, not per dataset

Averaged over 5 seeds, **national arm only** for all three estimators — mixing
the geo arm into one column and not the others would not be a comparison.
`signal/noise` is the standard deviation of the channel's true national
contribution divided by the standard deviation of national revenue noise: how
much of the channel is *visible*, not how big it is. The column below is the
diagnostics version, built on the national-aggregate regressor the national
oracle actually sees; the cheap C7 gate in `simulation/checks.py` applies the
same definition to the geo-level contribution summed to national, and lands
within 0.02 of it on every channel (tv 1.89 there, 1.91 here). Neither is more
correct — they are the same ratio taken before and after the aggregation, and
the charts label theirs as the C7 value.

Every `err` column below is the **mean absolute** relative ROI error over
the five seeds. `analysis/out/summary.md` carries the same per-channel
cells — signed and absolute, side by side — for every tool-arm, so each
number here can be checked against a committed artifact rather than
against a local CSV.

| channel | true ROI | contribution share | regressor CV | signal/noise | **oracle L2 err** | Meridian err | Robyn err |
|---|---|---|---|---|---|---|---|
| tv | 1.8 | 7.8% | 0.500 | **1.91** | **0.04** | 0.34 | 0.61 |
| search | 3.5 | 9.1% | 0.088 | **0.39** | **0.15** | 0.70 | 0.79 |
| social | 2.5 | 4.3% | 0.160 | **0.34** | **0.24** | 0.70 | 0.72 |
| ooh | 0.8 | 0.9% | 0.233 | 0.11 | 0.97 | 0.55 | 0.23 |
| display | 1.2 | 1.6% | 0.126 | 0.10 | 0.76 | 0.38 | 0.43 |

> **Robyn's numbers carry three caveats that must travel with them, and this is
> the full version** (`runs/robyn/DECISIONS.md`; this said "two" until the
> pre-publication audit added the third, 2026-09-11).
>
> *Convergence.* At the pre-registered 2000x5, **four** of five seeds failed
> Robyn's own check — 101, 103 and 104 on DECOMP.RSSD, 102 on both DECOMP.RSSD
> and NRMSE; only seed105 passed. The pre-registered escalation re-ran 101-104
> at 4000x5: seed101 converged there, 102, 103 and 104 did not. The final state
> is **three of five non-converged**, and the only Robyn seed that converged at
> the original spec is seed105.
>
> *Mixed spec.* The committed extracts are therefore **not one spec**: seeds
> 101-104 are 4000x5 runs, seed105 is its original converged 2000x5 run, left
> untouched exactly as the amendment pre-registered before any ground-truth
> comparison. Every aggregate Robyn number on this page and in
> `analysis/figures/` averages those five runs. It is disclosed rather than
> smoothed over, but a reader has to know that is what "mean over 5 seeds"
> means for Robyn.
>
> *Adstock bounds.* On ooh and display Robyn's pre-registered θ bounds exclude
> the true retention (0.6 against 0.1–0.4; 0.4 against 0–0.3), so it cannot
> express the true carryover there — the ooh 0.23 and display 0.43 in the table
> above included (dated amendment to `docs/PLAN.md` D5).

> **Meridian's numbers carry one of the same kind.** Its default priors fix
> every Hill slope at 1 (`slope_m` is `Deterministic(1.0)`), so it cannot
> express the true slope on tv, search, social or display — tv's S-shape (2)
> furthest off. The oracle rungs are handed the true slopes, so they cannot say
> how much of Meridian's error that explains (dated amendment to MD2 in
> `runs/meridian/DECISIONS.md`, 2026-09-11).

**The oracle's error is ordered by signal-to-noise; the tools' error is not.**
Above the floor the ordering is strict — tv 0.04, search 0.15, social 0.24, in
exactly the order of their S/N. Below it the ordering dissolves rather than
continuing: ooh (S/N 0.11) errs 0.97 and display (S/N 0.10, lower) errs 0.76.
That is not a counterexample to the mechanism, it is what the mechanism
predicts — once a channel is invisible what is left is noise, and noise does
not rank. Read ooh and display as tied at "not recoverable", never as ordered.
**Both tools compress five different ROIs into one narrow band, and the band
is not the truth's.** The five true ROIs span a factor of 4.4 (0.8 to 3.5).
Mean point estimates, national arm:

| | tv | search | social | ooh | display | span |
|---|---|---|---|---|---|---|
| true | 1.80 | 3.50 | 2.50 | 0.80 | 1.20 | **4.4x** |
| Meridian | 1.20 | 1.06 | 0.76 | 1.24 | 0.74 | **1.7x** |
| Robyn | 0.70 | 0.73 | 0.71 | 0.68 | 0.69 | **1.1x** |

The two bands are reached by different mechanisms, and they are not equally
tight:

- **Robyn's band is a single number.** 0.68 to 0.73 is a 1.08x spread across
  five channels whose truths differ by 4.4x. That is the DECOMP.RSSD term
  solved to its optimum: across the 25 channel-seed cells its estimated
  media-effect share sits **0.54pp** from spend share on average, against
  Meridian's 4.62pp and the L3 oracle's 8.69pp. All three are the "distance
  from spend share" line in `analysis/out/summary.md`, taken per channel-seed
  and then averaged — averaging the shares across seeds first would cancel
  sign and flatter Robyn. When effect share equals spend share, one ROI for
  every channel follows arithmetically, and the value of that single number is
  Robyn's own portfolio ROI: total estimated media contribution over total
  spend.

  The one number that reads the other way is the pre-registered M5 metric.
  `analysis/out/summary.md` scores Meridian at 0.085 on "pull toward spend
  share" against Robyn's 0.067, which looks like the opposite of everything
  above. It is a limit of M5, not a contradiction: it measures displacement in
  the spend-share direction and does not cap at spend share, so a tool that
  overshoots outscores one that lands on it: Meridian's tv effect share sits
  **+5.10pp past** spend share, where the truth is 6.1pp *below* it. The
  per-channel "effect share − spend share" column in `analysis/out/summary.md`
  carries that figure, and the same column shows Robyn's five channels all
  inside 1pp of spend share. M5 is left exactly
  as pre-registered; the "distance from spend share" line was added beside it
  to say where each tool actually ended up.
- **Meridian's band is wider and its prior median sits near the top, not the
  centre.** 0.74 to 1.24, with the default ROI prior's median — `LogNormal(0.2,
  0.9)`, median e^0.2 ≈ 1.22, in
  [`prior_distribution.py`](https://github.com/google/meridian/blob/main/meridian/model/prior_distribution.py)
  — sitting just below the top of it. Its five channel means: ooh 1.24 (true
  0.8; the one channel it over-estimates, lifted by one seed's 2.21), tv 1.20,
  search 1.06, social 0.76, display 0.74 (true 2.5 and 1.2 for the last two). So "Meridian collapses to 1.22" is
  too strong a claim for these five estimates, and this page does not make it.
  What it does say is that Meridian compresses, and that the compressed band tops
  out just above its prior median, 1.24 against 1.22. *(Corrected during the
  pre-publication audit, 2026-09-11: this bullet called the prior median the
  band's ceiling, which the ooh mean exceeds.)*

This splits the five channels into two regimes, and they must never be read
together:

- **tv, search, social — the truth is in the data.** L2 recovers them with errors of
  0.04, 0.15 and 0.24; L3, which also has to estimate its own baseline, 0.10,
  0.32 and 0.38. Meridian and Robyn miss them by **34% to 79%** — worse than
  either rung, on every one of the three. Here the failure belongs to the tools as
  configured. The rungs are handed the true parameters and neither tool's
  configuration is — Meridian's slope is fixed at 1; Robyn's ooh cap can reach tv
  through the designed tv–ooh correlation, and its γ coverage was not checked — so
  this ladder cannot say how much of either tool's miss is the setup's.
- **ooh, display — the truth is not in the data.** L2 misses ooh by 97% and
  display by 76%; L3 by 98% and 122%. A tool that lands closer there — Robyn's
  0.23 on ooh — is lucky, not measuring.

**Which rung belongs in which argument.** The table above uses **L2**, the rung
handed the true baseline, because the question it answers is a ceiling
question: *was this channel recoverable by anybody?* Handing it the baseline is
the point — it removes one more excuse. Figures 1 and 2 in `analysis/figures/` use **L3** instead, because they run a
different argument (figure 3 shows both rungs side by side, since there the
subject is interval calibration rather than a race): a like-for-like race
against two tools that must estimate their own baselines, where L2 would carry
an advantage neither tool gets (`analysis/FIGURES.md` D-F2). The two rungs
agree on the finding and disagree on the size of the gap, and neither is the
"real" oracle — L2 is the ceiling, L3 is the fair opponent. Any sentence built
on an oracle number has to say which one it used.

The second regime is where reading a tool's own error table goes wrong, but the
honest version of that claim is narrower than it first looks:

- **For Robyn the inversion is complete.** Its two best channels are exactly
  the two nobody can measure: ooh (0.23) and display (0.43). Its three worst are
  the three the oracle recovers — tv (0.61), social (0.72), search (0.79).
  Ranked by Robyn's own error you would trust ooh most, and search least; the
  truth is the other way round.
- **For Meridian's national arm there is no inversion, only a flattening.**
  Its ranking is tv 0.34, display 0.38, ooh 0.55, search 0.70, social 0.70 —
  its best channel *is* the most recoverable one, so a reader ranking that
  arm's channels by its own error would not be led to trust ooh most. What they
  would be led to believe is that display (0.38) was measured about as well as
  tv (0.34), when the oracle says display was not measured at all. The failure
  mode there is a false sense of precision on an unmeasurable channel, not a
  reversed order.
- **Meridian's geo arm inverts completely, and further than Robyn does.** Its
  ranking is ooh **0.161**, display 0.331, tv 0.501, social 0.712, search 0.793
  (`analysis/out/summary.md`, geo block). ooh — the least recoverable channel in
  the scenario, S/N 0.11 — is that arm's most accurate channel, and 0.161 is the
  **smallest per-channel error either tool achieves anywhere in the scoring
  table**. Five cells in that table are smaller and all five belong to the
  oracle: L2 tv 0.039, L1 tv 0.044, L3 tv 0.098, L4 tv 0.120, L2 search 0.152.
  That contrast is the finding in one line — every one of the oracle's best
  cells sits on a channel the data can measure, and the tools' single best cell
  sits on one it cannot. Anyone ranking that arm's channels by its own
  error would trust ooh above everything, including tv, the one channel the data
  genuinely contain. The inversion is therefore not a Robyn quirk: it shows up
  in both tools, and in Meridian it takes the arm with *more* data. Two seeds
  sit behind that column and one of them did not converge, so read it as an
  instance of the pattern, not as a measurement of its size.

In both cases the apparent accuracy on ooh and display is a coincidence of this
scenario, and the band table above says exactly why: 0.8 and 1.2 are the only
two true ROIs that fall inside or next to the tools' compressed bands, while
tv (1.8), social (2.5) and search (3.5) all sit far outside them. A tool whose
five answers span 1.1x will look accurate on whichever channel happens to be
near its one answer. It is not a measurement, and no tool output tells you
which of its channels are in which regime.

## Third result: the shrinkage is the tools', not the data's

| | ROI bias (signed) | \|ROI err\| | interval covers truth | interval width / true ROI |
|---|---|---|---|---|
| oracle L2 (national, true baseline) | +0.065 | 0.432 | 0.88 | 1.338 |
| oracle L3 (national, estimated baseline) | −0.008 | 0.598 | **0.92** | 2.753 |
| oracle L1 (geo, true baseline) | +0.118 | 0.520 | 0.60 | 1.099 |
| oracle L4 (geo, estimated baseline) | +0.091 | 0.932 | 0.56 | 1.555 |
| Meridian national | −0.312 | 0.533 | 0.60 | 1.615 |
| Meridian geo (2 seeds; seed101 max R-hat 1.118, not converged) | −0.499 | 0.499 | 0.50 | 1.196 |
| Robyn national (3 of 5 seeds non-converged) | −0.540 | 0.555 | 0.16 | 0.277 |

*Added during the pre-publication audit, 2026-09-10/11.* Meridian geo's 0.499 is a
two-seed mean and is not an upgrade on the national arm: on those same two seeds
Meridian national scores 0.470 (`analysis/out/summary.md`). The arms also differ
in more than geography — a baseline knot per week against automatic knot
selection, and 2000/2000 adaptation/burn-in against 500/500. The geo arm's
dropped competitor control is not one of the differences that matter: under a
knot per week it is redundant, and `runs/meridian/DECISIONS.md` (amendment of
2026-08-28) records dropping it as a statistical no-op.

Two things the aggregate error column hides:

1. **The oracles are unbiased; the tools are not.** Oracle bias spans −0.01 to
   +0.12; Meridian national is −0.31 and Robyn −0.54. The oracles are wrong by
   *variance* — noise pushes individual estimates around a correct centre. The
   tools are wrong by *systematic shrinkage*. Similar average error, opposite
   pathology.
2. **Well-calibrated intervals were available on the national aggregate.** L3 — the rung
   that estimates its own baseline, the fairest comparison to a real tool —
   covers the truth 92% of the time against a nominal 90%. Meridian covers 60%,
   Robyn 16%. "The data were hard" does not explain the tools' interval
   miscalibration, because an OLS on the same data got it right.

   **Both Robyn cells in the table above — its 0.16 coverage and its 0.277
   width — are outside the like-for-like comparison, and neither should be
   read against the other rows.** Robyn's interval is the spread across
   Pareto-front candidate models, not a posterior interval: it was never meant
   to be a 90% interval, so 0.16 is not a calibration failure of the same kind
   as Meridian's 0.60, and 0.277 is not evidence that Robyn is the more precise
   tool. A narrow spread across a shortlist of models is a statement about how
   similar those models are to each other, not about how sure Robyn is of the
   answer — and on this dataset its shortlist agrees closely on a number that
   is wrong. `analysis/figures/fig3_intervals.png` hatches that bar and says
   the same thing in its caption.

## Fourth result: aggregating geos to national helped here

L2 (national) beats L1 (geo) — 0.432 vs 0.520 — with the *same* true parameters
and the same true baseline. Two reasons, both specific to this scenario.

Geo revenue noise is iid across the 8 geos, so summing averages it down; because
the geos are unequal (`pop_shares` runs 0.28 to 0.05) the effective reduction is
about √6, not √8.

And at geo level every channel's regressor carries the same dominant population
factor, which inflates their raw pairwise correlation to **0.66–0.94** (mean per
pair over seeds; the maximum is display–search). Removing that factor by
time-demeaning within geo drops the range to **−0.05 to 0.46**: the top of it is
the tv–ooh pair, which carries the deliberate spend correlation `docs/PLAN.md`
§3 dialled in, and every other pair sits between −0.05 (ooh–search, negative)
and 0.09.

Two different correlations get called "tv–ooh" in this project and they must
not be swapped. **0.46 is the time-demeaned geo regressor correlation**, which
is what this paragraph is about. The **realized spend** correlation the PLAN's
dial actually targeted is **0.34–0.61** across the five seeds (`docs/PLAN.md`
§3, `data/README.md`) against a pre-registered target of ~0.4–0.5. **No seed
landed inside that target**: the realized values are 0.34, 0.37, 0.38, 0.38 and
0.61. What the data were actually frozen against is the C2 gate in
`simulation/checks.py`, which admits the wider [0.30, 0.65], and all five pass
it. The dial therefore did what a gate lets it do rather than what the target
asked for — worth knowing before anyone reads the tv–ooh correlation as
tuned.

So cross-channel collinearity in this dataset is mild. The severe collinearity
is between each channel and the baseline — which is what "no time variation"
means. This is also consistent with Meridian's geo arm being the run that spent
its information on 156 weekly knots and did not converge on seed101.

**Sampler escalations, in one place.** Robyn is not the only tool that got a
second chance, and the record has to say so symmetrically. Meridian's **geo**
arm did not converge at the pre-registered 500/500 adapt/burnin, nor at
1000/1000; the exported geo runs are the third attempt, at **2000/2000** — four
times the pre-registered adaptation and burn-in, with the 1000 kept draws
unchanged (`runs/meridian/DECISIONS.md` MD6 and its
amendments). Its national arm needed no escalation and shipped at 500/500.

The exported geo runs also carry divergent transitions the national runs do
not: **64 on seed101 and 122 on seed102**, against 1 to 6 per national run.
seed102 is counted as converged — max R-hat 1.024, inside the 1.1 gate — with
122 divergences behind it, and a divergence count that high is a warning about
the geometry that R-hat alone does not carry. Both numbers are in the committed
run JSONs (`run.convergence_detail.n_divergences`).

**Non-convergence across the whole comparison, in one place:** four runs did not
converge — Meridian geo seed101 (max R-hat 1.118, driven by time-effect
parameters) and Robyn national seeds 102, 103 and 104 (Robyn's own check, at
the pre-registered 2000x5 and again at 4000x5). Both are published as-is per the
pre-registered gates.

## What this does and does not license us to say

**Licensed.** That for tv, search and social this dataset contains the truth and
neither tool, as configured, found it. That **Robyn** collapses to a single characteristic
value — its own portfolio ROI — while **Meridian** compresses into a band (0.74
to 1.24) whose upper edge sits just above its prior median, 1.22: different behaviours, different
mechanisms. The stronger claim that Meridian too collapses to one value is not
licensed by these five seeds. That the tools' uncertainty intervals are
miscalibrated in a way the data do not excuse.
That per-channel error rankings from a tool alone are untrustworthy without a
recoverability check.

**Not licensed.**

- That the tools would fail this way on other scenarios, other noise levels, or
  real data.
- **That any of this describes the hard regime.** Spend here is exogenous — no
  budget chasing demand, no targeting feedback. That is the *easy* case for MMM;
  the measured accuracy likely flatters what these tools would do in production.
- **That the setup was uniformly generous.** Both were meant to be handed
  generosities, documented in the decision logs: Meridian got `max_lag=13`,
  matching the generator's true adstock support instead of its default 8
  (`runs/meridian/DECISIONS.md` MD5), and Robyn's hyperparameter bounds were
  meant to *contain* the true adstock and Hill values (`docs/PLAN.md` D5). For
  adstock they do on tv, social and search; on ooh and display they exclude the
  true retention (0.6 against 0.1–0.4; 0.4 against 0–0.3) — the arrangement D5
  was written to prevent, caught only in the pre-publication audit and recorded
  in dated amendments to D5 and both decision logs. The true Hill shapes all
  fall inside Robyn's α range; its γ is set relative to each series' range, so
  whether the true half-saturation points fall inside was not checked.
  Meridian's default priors fix every Hill slope at 1 (`slope_m` is
  `Deterministic(1.0)`), so only ooh's true slope is expressible there, and
  tv's S-shape (slope 2) is not.
- That OLS is a better MMM — it is not an MMM, it was given the answers.
- That ooh and display were estimated well by anyone.
- That Robyn's figures here describe a converged Robyn: three of its five seeds
  fail its own convergence check at 2000x5 and again at double that. What they
  describe is Robyn as this pre-registered protocol ran it, non-convergence and
  all.

## The reusable part

The scenario's per-channel signal-to-noise was never checked before the runs.
`simulation/checks.py` C3 gates only the *total* media variance share into
[0.10, 0.35]; all five seeds passed it with the media signal overwhelmingly
concentrated in one channel. The measure of that concentration is
`simulation.checks.channel_snr`, the C7 gate's own function: averaged over the
five seeds it gives tv 1.89 against 0.39 for the next highest, search — nearly
five times less. `python -m simulation.checks` prints it per seed and
`python analysis/figures.py` prints the five-seed means. Note that the
`signal/noise` column earlier on this page is the *diagnostics* variant
(tv 1.91), computed on the national-aggregate regressor; the two agree within
0.02 on every channel.

It is deliberately not quoted as a "share of media variance". That figure
depends on the definition, and the defensible ones disagree badly: tv's share
of the summed per-channel variances of the national contribution series is
0.93, its share of the geo-level series' variances is 0.52, and a
variance-decomposition route gives about 0.84. A number that moves between
0.52 and 0.93 with the definition does not belong in a published claim. The
S/N figure above is one definition, computed by one committed function. A per-channel recoverability gate — run the oracle, require a
minimum oracle accuracy before any tool run is worth doing — is the fix, and it
is the part of this project most worth handing to someone else.
