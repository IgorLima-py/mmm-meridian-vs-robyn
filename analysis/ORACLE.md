# The oracle check — is the truth recoverable at all?

Every number on this page is regenerable from committed code:

```
python analysis/oracle.py                              # fits the four rungs
python analysis/oracle.py --diagnostics                # the scenario numbers
python analysis/scoring.py --results runs --data data/sim --out analysis/out
```

Results below are from 2026-09-08, all 5 seeds, generator 1.0.0, scored by the
same pre-registered harness as the tools.

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

Add the simulated noise back (7% CV per geo) and the same design loses three of
the five betas. That is the whole finding.

## Second result: recoverability is per channel, not per dataset

Averaged over 5 seeds, **national arm only** for all three estimators — mixing
the geo arm into one column and not the others would not be a comparison.
`signal/noise` is the standard deviation of the channel's true national
contribution divided by the standard deviation of national revenue noise: how
much of the channel is *visible*, not how big it is.

| channel | true ROI | contribution share | regressor CV | signal/noise | **oracle L2 err** | Meridian err | Robyn err |
|---|---|---|---|---|---|---|---|
| tv | 1.8 | 7.8% | 0.500 | **1.91** | **0.04** | 0.34 | 0.57 |
| search | 3.5 | 9.1% | 0.088 | **0.39** | **0.15** | 0.70 | 0.76 |
| social | 2.5 | 4.3% | 0.160 | **0.34** | **0.24** | 0.70 | 0.68 |
| ooh | 0.8 | 0.9% | 0.233 | 0.11 | 0.97 | 0.55 | 0.19 |
| display | 1.2 | 1.6% | 0.126 | 0.10 | 0.76 | 0.38 | 0.48 |

> **Robyn's numbers carry a caveat that must travel with them.** Three of the
> five Robyn runs behind this column — seeds 102, 103 and 104 — fail Robyn's own
> convergence check at the pre-registered 2000x5, and the escalation that
> `runs/robyn/DECISIONS.md` pre-registered for them has not run yet. Only seeds
> 101 and 105 converged. Read every Robyn figure on this page as provisional
> until that closes.

**The oracle's error is monotone in signal-to-noise. The tools' error is not.**
The tools' error tracks `|true ROI − the value that tool shrinks toward|`:
Meridian toward the median of its default ROI prior — `LogNormal(0.2, 0.9)`,
median e^0.2 ≈ 1.22, in
[`prior_distribution.py`](https://github.com/google/meridian/blob/main/meridian/model/prior_distribution.py)
— and Robyn toward a single spend-proportional ROI.

This splits the five channels into two regimes, and they must never be read
together:

- **tv, search, social — the truth is in the data.** The oracle recovers them to
  within 4%, 15% and 24%. Meridian and Robyn miss them by **34% to 76%**. Here
  the failure belongs to the tools.
- **ooh, display — the truth is not in the data.** The oracle misses ooh by 97%
  and display by 76%; no estimator could have done better.

The second regime is where reading a tool's own error table goes wrong, but the
honest version of that claim is narrower than it first looks:

- **For Robyn the inversion is complete.** ooh is its *best* channel (0.19) and
  display its third (0.48), while search and tv are its worst. Ranked by Robyn's
  own error you would trust ooh most — the one channel no estimator can measure
  at all.
- **For Meridian it is partial.** Its ooh error is 0.55, its second-worst. The
  inversion shows up only for display (0.38, its best) against search (0.70).

In both cases the apparent accuracy on ooh and display is a coincidence of this
scenario: those channels' true ROIs (0.8 and 1.2) sit near the value each tool
collapses toward. It is not a measurement, and no tool output tells you which
of its channels are in which regime.

## Third result: the shrinkage is the tools', not the data's

| | ROI bias (signed) | \|ROI err\| | interval covers truth | interval width / true ROI |
|---|---|---|---|---|
| oracle L2 (national, true baseline) | +0.065 | 0.432 | 0.88 | 1.338 |
| oracle L3 (national, estimated baseline) | −0.008 | 0.598 | **0.92** | 2.753 |
| oracle L1 (geo, true baseline) | +0.118 | 0.520 | 0.60 | 1.099 |
| oracle L4 (geo, estimated baseline) | +0.091 | 0.932 | 0.56 | 1.555 |
| Meridian national | −0.312 | 0.533 | 0.60 | 1.615 |
| Meridian geo (2 seeds; seed101 max R-hat 1.118, not converged) | −0.499 | 0.499 | 0.50 | 1.196 |
| Robyn national (3 of 5 seeds non-converged) | −0.506 | 0.538 | 0.20 | 0.263 |

Two things the aggregate error column hides:

1. **The oracles are unbiased; the tools are not.** Oracle bias spans −0.01 to
   +0.12; Meridian national is −0.31 and Robyn −0.51. The oracles are wrong by
   *variance* — noise pushes individual estimates around a correct centre. The
   tools are wrong by *systematic shrinkage*. Similar average error, opposite
   pathology.
2. **Well-calibrated intervals were available in this dataset.** L3 — the rung
   that estimates its own baseline, the fairest comparison to a real tool —
   covers the truth 92% of the time against a nominal 90%. Meridian covers 60%,
   Robyn 20%. "The data were hard" does not explain the tools' interval
   miscalibration, because an OLS on the same data got it right.

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
the deliberate tv–ooh spend correlation from `docs/PLAN.md` §3, which
pre-registered a target of ~0.4–0.5 and realized 0.46 here, and every other pair
sits between −0.05 (ooh–search, negative) and 0.09.

So cross-channel collinearity in this dataset is mild. The severe collinearity
is between each channel and the baseline — which is what "no time variation"
means. This is also consistent with Meridian's geo arm being the run that spent
its information on 156 weekly knots and did not converge on seed101.

**Non-convergence across the whole comparison, in one place:** four runs did not
converge — Meridian geo seed101 (max R-hat 1.118, driven by time-effect
parameters) and Robyn national seeds 102, 103 and 104 (Robyn's own check, at the
pre-registered 2000x5). Both are published as-is per the pre-registered gates.

## What this does and does not license us to say

**Licensed.** That for tv, search and social this dataset contains the truth and
neither tool found it. That each tool has a characteristic value it collapses
toward, and they are different values reached by different mechanisms. That the
tools' uncertainty intervals are miscalibrated in a way the data do not excuse.
That per-channel error rankings from a tool alone are untrustworthy without a
recoverability check.

**Not licensed.**

- That the tools would fail this way on other scenarios, other noise levels, or
  real data.
- **That any of this describes the hard regime.** Spend here is exogenous — no
  budget chasing demand, no targeting feedback. That is the *easy* case for MMM;
  the measured accuracy is an upper bound on what these tools do in production.
- **That the tools were given a hard setup.** Both were handed generosities,
  documented in the decision logs: Meridian got `max_lag=13`, matching the
  generator's true adstock support instead of its default 8
  (`runs/meridian/DECISIONS.md` MD5), and Robyn's hyperparameter bounds were
  chosen to *contain* the true adstock and Hill values (`docs/PLAN.md` D5). A
  setup that hid the truth outside those bounds would have failed worse.
- That OLS is a better MMM — it is not an MMM, it was given the answers.
- That ooh and display were estimated well by anyone.
- That Robyn's figures here are final: three of its five seeds have not
  converged and its pre-registered escalation is still pending.

## The reusable part

The scenario's per-channel signal-to-noise was never checked before the runs.
`simulation/checks.py` C3 gates only the *total* media variance share into
[0.10, 0.35]; all five seeds passed it with roughly 85% of the media signal in
one channel. A per-channel recoverability gate — run the oracle, require a
minimum oracle accuracy before any tool run is worth doing — is the fix, and it
is the part of this project most worth handing to someone else.
