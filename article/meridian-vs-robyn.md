# Two MMM tools, one dataset, and a known answer

**The dataset is simulated.** Five channels, eight geos, 156 weeks, from a committed
generator that writes every channel's true ROI, adstock and response curve to disk
*before* either tool sees it. No advertiser data is involved. Simulating buys a
question real data cannot ask: not "do the tools agree?" but "which one recovered
reality, and was reality recoverable at all?"

## The setup

Google **Meridian 1.8.0** (Python, Bayesian MCMC) and Meta **Robyn 3.12.1** (R, ridge
regression driven by Nevergrad) ran over the same five seeds on the national aggregate,
plus a second Meridian arm on two seeds of the geo panel, which Robyn cannot use. The
generator uses geometric adstock and Hill saturation, the intersection of both tools'
model families: neither gets a home advantage, and both work in the right family of media
transforms, though not with every parameter in it (below), a best case the limitations
return to. True ROIs span 0.8 to
3.5, with spend share deliberately misaligned from effect share. Harness, metrics and Robyn's selection
rule were pre-registered.

The setup was meant to be generous to both, and it is logged. Meridian got `max_lag=13`
instead of its default 8, matching the true adstock support. Robyn got its own recommended
bounds, which the pre-registration said would contain the true values, and on ooh and
display they do not: true adstock retention 0.6 against a 0.1–0.4 bound, and 0.4 against
0–0.3. Meridian ran on its default priors, which fix every Hill slope at 1 where the
pre-registration had called them merely "concave-leaning": against true slopes of 0.7 to
2, it cannot express the true curve on four channels, tv's S-shape furthest off. The
pre-registration misdescribed both, and only the pre-publication audit caught either.
Each tool's setup excluded part of the truth.

## The result that isn't the result

Mean absolute relative ROI error, national arm, five seeds: **Meridian 0.533, Robyn 0.555**
(three of Robyn's five seeds fail its own convergence check).
Both missed by about half, mostly low. That is a tie, and it is also what
a bug in our own ground truth would look like.

So we added a third estimator that cheats. The **oracle** gets the generator's
functional form and the true adstock and Hill parameters, and fits the five coefficients,
plus, on two of its four rungs, its own baseline, as the tools must (`analysis/ORACLE.md`
lists the rungs). Nobody can run one on real data. It exists to separate *the tools failed*
from *the data could not answer*. On noiseless revenue it recovers them to machine
precision; add the simulated noise back and two of the five channels stop being
recoverable by anyone.

## Recoverability is per channel

Ranked by signal-to-noise (a channel's true contribution against the revenue noise,
both as standard deviations), the channels fall into two regimes.

| channel | signal/noise | oracle err | Meridian err | Robyn err |
|---|---|---|---|---|
| tv | 1.91 | **0.04** | 0.34 | 0.61 |
| search | 0.39 | **0.15** | 0.70 | 0.79 |
| social | 0.34 | **0.24** | 0.70 | 0.72 |
| ooh | 0.11 | 0.97 | 0.55 | 0.23 |
| display | 0.10 | 0.76 | 0.38 | 0.43 |

*Mean absolute relative ROI error, national arm, five seeds; this oracle rung is handed
the true baseline, and three of Robyn's five seeds fail its own convergence check.*

For **tv, search and social the truth is in the data and neither tool, as configured,
found it**: the oracle lands at 0.04 / 0.15 / 0.24, the tools miss by 34% to 79%. The
oracle was handed the true parameters and neither tool's configuration was: Meridian's
slope is fixed at 1, and Robyn's setup has gaps of its own (below). So this ladder cannot
say how much of either tool's miss is the setup's.

For **ooh and display the truth is not in the data**: the oracle misses them by 97%
and 76%, the baseline-estimating rung by 98% and 122%. Read them as tied at "not
recoverable", never ranked: below the floor, what is left is noise.

## Reading a tool's own error table goes wrong

Rank the channels by each tool's error, as a validation against known answers would, and
Robyn's says
to trust **ooh most (0.23) and search least (0.79)**; the truth is the reverse.
Meridian's geo arm inverts further: its best channel is **ooh at 0.161** (two seeds, one
of them not converged), one of the two channels the data cannot identify, and the smallest
per-channel error either tool posts anywhere. The only five cells smaller are the oracle's: four on
tv, one on search, all measurable channels. Meridian's national arm flattens instead,
reporting display (0.38) as about as well measured as tv (0.34) when display was not
measured at all.

The mechanism is in the point estimates. True ROIs span a factor of 4.4; Meridian's
span 1.7x (0.74-1.24), Robyn's 1.1x (0.68-0.73). Robyn's band is one number: its
DECOMP.RSSD term at its optimum puts estimated effect share 0.54pp from spend share,
against Meridian's 4.62pp and the baseline-estimating rung's 8.69pp, and when effect
share equals spend share one ROI per channel follows arithmetically. Meridian's is wider,
with its default ROI prior's median (≈ 1.22) just below the *top* of its band (1.24) rather
than at the centre: compression, not collapse. And 0.8 and 1.2 are the only true ROIs anywhere near
those bands.

## The intervals

The national baseline-estimating rung covers the truth **92%** against a nominal 90%.
Meridian covers **60%**, so "the data were hard" does not explain the miscalibration,
because an OLS on the same data got it right.

Robyn's 16% is **not comparable**: its interval is the spread across Pareto-front
candidate models, not a posterior. Nor is its narrowness (0.277 of true ROI, the
smallest here) evidence of precision.

Three caveats travel with every Robyn number here: three of five seeds fail its own
convergence check even at double the pre-registered iterations; its five-seed means blend
two specs: seeds 101-104 at 4000x5, seed 105 at its original converged 2000x5; and it
cannot express the true adstock on ooh and display. One travels with every Meridian number:
it cannot express the true Hill slope on four channels, tv's S-shape furthest off. The two
exclusions fall on different channels (Robyn's on the two this data cannot identify for
anyone, Meridian's on all three it can, and on display), and because ooh's spend was
designed to track tv's, a misfit on either channel can leak into the other, for either
tool; that was not tested. Meridian's geo arm carries more: it shipped at
four times its pre-registered adaptation and burn-in, carrying 64 and 122 divergent
transitions against 1 to 6 nationally, and without the pre-registered competitor control,
which the geo arm's baseline, with its own free level every week, makes redundant: Meridian
rejects it, and dropping it is statistically a no-op.

## Which one should you use?

There is no winner. The honest answer is conditional.

- **Uncertainty you can act on:** Meridian: 60% coverage is bad, but Robyn's interval
  answers a different question.
- **Geographic variation:** only Meridian can use it, and here it showed no accuracy gain.
  On the two seeds the geo arm ran it scored 0.499, the national arm 0.470 on those same
  seeds (the 0.533 above averages all five), with one geo seed not converged and worse
  coverage. Nor is that a clean test of geography: the geo arm's baseline also has its own
  free level every week, the national arm's only at points Meridian picks itself, and the
  geo arm had four times the warm-up.
- **An allocation finance will sign off on:** Robyn's DECOMP.RSSD lands near spend
  share, a business heuristic, not a measurement.
- **Runtime and stack:** 432s mean per Meridian national run on a consumer GPU under WSL2.
  Robyn's 1017s multi-core mean blends specs: its one seed at the pre-registered 2000x5
  ran 566s. Meridian is unsupported on native Windows; Robyn runs there single-core.
- **Maintenance:** Robyn's last CRAN release is 3.12.1 (2025-07-02), no repository commit
  since June 2025; Meridian 2.0.0 shipped 2026-09-03, after these runs, moving its default
  backend from TensorFlow to JAX. One may stop, the other moves under you.

But the tool mattered less than the question underneath. **Run a recoverability check
first:** fit an estimator that knows the true parameters on data simulated like yours.
If it cannot recover a channel, no tool will from this data alone.

## What neither tool can tell you

- **Which of its own channels it actually measured.** Both report numbers of identical
  apparent quality whether the data identify a channel or not; Robyn and Meridian's geo
  arm go further and look *best* on the unmeasurable ones.
- **That spend and demand move together.** Spend here is exogenous: no budget chasing
  demand, no targeting feedback. That is the *easy* regime, so every accuracy figure above
  likely flatters both tools.
- **Whether its functional form is right.** Here the media transforms were in both tools'
  families by construction, though Robyn cannot express the true adstock on ooh and
  display, nor Meridian, its slope fixed at 1, the true slope on four channels. The rest was not exact
  either: on the national arm, Hill applied per geo and
  then summed is not Hill of the national total, and the simulated baseline carries a
  mid-May event on no holiday calendar, which Robyn's holiday regressor cannot see and
  Meridian's baseline must absorb. Gross misspecification, the normal case on real data,
  is untested, and one simulator is one data-generating process.
- **That effectiveness changes.** Both assume constant parameters over 156 weeks.
- **How much of the answer came from the priors**, or from the setup: Meridian's generous
  `max_lag=13` beside its default slope fixed at 1, and Robyn's bounds, which contain the
  true adstock on three channels and exclude it on two. None of it was ablated. At n = 156
  the priors may do much of the work, untested here.
- **Whether channels that always move together can be separated.** They cannot. Here the
  severe collinearity is between each channel and the baseline, which is what "not enough
  variation" means.
- **Anything about incrementality.** MMM does not replace a geo experiment or a holdout
  test; it is what you calibrate with them.

## Reproducing this

Every figure traces to a committed artifact: scored metrics to
`analysis/out/summary.md`, per-channel point estimates to `runs/*/results/*.json`, scenario
numbers to `analysis/out/diagnostics.md`, the rung
definitions to `analysis/ORACLE.md`, and every setup decision (those that flatter each
tool included) to `runs/*/DECISIONS.md` and `analysis/SELECTION_RULE.md`.

Scope: one simulated scenario with media transforms both tools share, exogenous spend, five
fixed seeds, one version of each tool (Robyn's recorded, not reproducibly pinned),
pre-registered setups with the escalations logged above, not evidence about misspecified
models, other scenarios, endogenous spend, or real data.
