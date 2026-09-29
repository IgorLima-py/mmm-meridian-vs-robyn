# PLAN — Meridian vs Robyn on simulated ground truth

> Written 2026-08-27 after the planning-session research (see `REFERENCES.md` for
> every source). Current phase and next concrete step always live in `STATUS.md` —
> a fresh session reads STATUS first, then jumps to the phase section here.

## 0. What this project produces

Same simulated dataset — with a known, documented generating process — run through
**Google Meridian 1.8.0** (Python, Bayesian MCMC) and **Meta Robyn 3.12.1** (R,
ridge + Nevergrad), scored on how well each recovered the truth (ROI, channel
contributions, response curves), plus setup effort and runtime, ending in a
~1,000-word piece with a comparison table, a chart of both tools' estimates vs
truth, a decision guide, and the mandatory **"What neither tool can tell you"**
section.

**Framing rule (permanent):** this is a comparison and critical reading of two
tools. Nothing here claims "built an MMM" — see `CLAUDE.md`.

## 1. Why this exact design (research summary)

Key facts the plan rests on (full citations in `REFERENCES.md`):

1. **The gap is real.** As of 2026-08-27 there is **no published comparison that
   runs both Meridian and Robyn on the same simulated dataset with known ground
   truth and scores truth recovery.** The two near-misses: PyMC Labs' benchmark
   (Sep 2025) has the methodology but excluded Robyn and is vendor-authored; an
   ICATSD 2026 conference repo ran both tools but scored stability/agreement, not
   truth, and is effectively unindexed. Everything else is feature checklists,
   single-tool teardowns, or journalism.
2. **Timing angle.** Robyn's repo has been dormant since ~June 2025 (last CRAN
   release 3.12.1, 2025-07-02; trade press reports Meta "dismantled" the team),
   while Meridian ships monthly (1.8.0 on 2026-08-15, JAX backend, 2026 product
   pushes). No empirical piece has paired that story with data.
3. **Neither demo dataset has published ground truth** (Robyn's
   `dt_simulated_weekly`, Meridian's `simulated_data/` CSVs) → custom simulation
   is necessary.
4. **Fair generator = geometric adstock + Hill saturation** — the intersection of
   both tools' model families ("equally native"). Weibull adstock would be
   fittable only by Robyn; Meridian's own transformers would favor Meridian.
   Canonical parameter ranges come from Jin et al. (Google, 2017).
5. **Score curves and ROI, not raw parameters.** Jin et al. show Hill parameters
   (K, S, β) are near-unidentifiable even when the response curve is well
   estimated. Ground-truth ROI must be computed counterfactually (zero-out a
   channel including carryover), not read off coefficients.
6. **Known asymmetries to design around and disclose** (§5): Robyn's DECOMP.RSSD
   pulls effect share toward spend share; Robyn only searches inside user-set
   hyperparameter bounds; Meridian's default slope prior favors concave
   saturation; Meridian is geo-native while Robyn is national-only.
7. **Windows reality.** Meridian does not support Windows natively (the one
   Windows-guidance issue was closed wontfix); community path is WSL2 or Colab.
   Robyn runs natively on Windows **but its main loop is single-core on Windows**
   (parallelization is unix-only, verified in `R/checks.R`). WSL2 fixes both at
   once. Local machine: Python 3.14 only (too new — Meridian needs 3.11/3.12),
   no R, no WSL yet, 32 GB RAM, 10-core CPU, no discrete GPU.
8. **Runtime envelopes (planning figures, not guarantees):** Meridian national on
   CPU ≈ tens of minutes to ~1–2 h per run (fewer chains + `n_burnin=0` are
   sanctioned knobs; Colab T4 fallback ≈ 10 min). Robyn 2000×5 on a small weekly
   dataset ≈ 20–60 min multi-core under WSL2 (1–3 h single-core native).
   `robyn_outputs()` plotting is a known RAM/time hog — export few one-pagers.

## 2. Decisions (D1–D10)

| # | Decision | Rationale / what to document |
|---|----------|------------------------------|
| D1 | **All tool environments live on the GPU desktop (admin available): WSL2 Ubuntu; Meridian in a Python 3.12 venv via `google-meridian[and-cuda]==1.8.0` (RTX 4070 Super, 12 GB VRAM); Robyn in R ≥ 4.2 + CRAN 3.12.1, nevergrad in a dedicated Python 3.10 venv, `RETICULATE_PYTHON` pinned. The laptop (no admin rights → WSL2 impossible) does only tool-free work: simulator, scoring harness, analysis of committed extracts, writing.** | Linux + CUDA is Meridian's *officially documented* configuration — the GPU turns MCMC from ~1–2 h CPU into minutes and makes the seeds × arms matrix comfortable; WSL2 also unlocks Robyn's multi-core loop (unix-only). The no-admin laptop settles the split by elimination. See §6 header for the phase-to-machine mapping. |
| D2 | **Pin everything**: `google-meridian==1.8.0` (which itself hard-pins TF 2.21.x and a tfp-nightly build — document this oddity), Robyn 3.12.1, R version, nevergrad version; lockfiles committed in `envs/` | Reproducibility is the credibility signal. Meridian results are known to drift across TF versions (issue #976). |
| D3 | **Generator: geometric adstock + Hill**, parameters in Jin-plausible ranges; simulator is our own small Python package | Intersection of both tools' families; neither tool's code generates the data. |
| D4 | **Geo-level simulation (8 geos, 156 weeks), aggregated to national for Robyn.** Primary comparison arm = **both tools on the national aggregate** (like-for-like); secondary arm = **Meridian on geo data** (quantifies what geo variation buys) | Robyn cannot use geos; a geo-only design would be unfair, a national-only design would hide Meridian's main advantage. The conditional answer is the point. |
| D5 | **True adstock/saturation values chosen inside Robyn's recommended hyperparameter bounds** (θ: TV 0.3–0.8, OOH/print 0.1–0.4, digital 0.0–0.3; Hill α ∈ [0.5,3], γ ∈ [0.3,1]) with **one S-shaped channel (S=2)** kept in the base scenario | Truth outside Robyn's bounds would rig the test; S=2 is realistic (TV), sits inside Robyn's bounds, and stresses Meridian's concave-leaning default prior — a disclosed, symmetric-ish stressor. |
| D6 | **Heterogeneous true ROIs (~0.8 to ~3.5) with spend share deliberately misaligned from effect share** | This is the direct probe of Robyn's DECOMP.RSSD bias — measured, not averaged away. |
| D7 | **Ground truth = counterfactual**: true ROI per channel via zero-out re-simulation including the carryover tail; true response curves saved on a spend grid; all truths in `ground_truth.json` | AMSS/Jin methodology; avoids "truth = coefficient" errors. |
| D8 | **Pre-registered scoring**: the scoring harness AND the Robyn model-selection rule are committed before any tool run | Kills the cherry-picking critique. Robyn rule: Robyn's own recommended flow (Pareto front → clustering → its suggested best), and we additionally report the spread across top candidates. |
| D9 | **Seeds**: 5 data-generation seeds for the primary national arm; ≥1 seed for the geo arm; fixed tool seeds (Meridian `seed`, Robyn `seed=123`+) | Enables the coverage/stability analysis nobody has published (Meridian CrI coverage across seeds; Robyn candidate spread). Scale down to 3 seeds if runtime bites. |
| D10 | **Runs on the GPU desktop by default; Colab T4 as documented fallback for Meridian** if the desktop is unavailable (pin versions in the notebook; note bit-reproducibility caveat across hardware). Published results state the exact environment; CPU-only re-runs by readers remain possible (seeds fixed, versions pinned), with the usual same-hardware-only bit-reproducibility caveat. | Keeps "anyone can re-run this" honest either way. |

## 3. Simulation design (target spec — finalized in Phase 2)

- **Panel:** 8 geos × 156 weeks (3 years), heterogeneous geo sizes (population),
  weekly. Revenue KPI (simplest common ground for both tools).
- **Baseline:** geo-scaled base level + mild trend + yearly seasonality (2–3
  Fourier harmonics) + a few holiday bumps. Both tools get something real to
  absorb (Robyn via Prophet, Meridian via knots).
- **Channels (5):** each with weekly spend AND impressions (impressions = spend /
  noisy CPM; both tools receive exposure + spend, as both prefer).

| Channel | Adstock α (geom. retention) | Hill shape S | Half-sat K (vs median spend) | True ROI target | Notes |
|---|---|---|---|---|---|
| tv | 0.7 | 2.0 (S-shaped) | ~1.2× | ~1.8 | the stress channel (D5) |
| ooh | 0.6 | 1.0 | ~1.0× | ~0.8 | low-ROI probe for DECOMP.RSSD (D6) |
| social | 0.3 | 0.9 | ~0.8× | ~2.5 | |
| display | 0.4 | 0.8 | ~0.9× | ~1.2 | |
| search | 0.1 | 0.7 | ~0.7× | ~3.5 | exogenous in base scenario (disclosed) |

- **Spend patterns:** always-on base + campaign pulses reaching ~2–3× K (spend
  must span the saturation curve or recovery is impossible — Jin/Chan & Perry);
  tv and ooh planned together → pairwise correlation ~0.4–0.5 (the honest
  multicollinearity dial); others ~0.1–0.3.
- **Noise:** sized so media explains ~15–25% of revenue variance (Jin's
  simulation is the anchor; noisier than that is realistic but hostile for a
  first scenario).
- **Explicitly out of the base scenario (disclosed as limitations):** endogenous
  spend / demand-chasing budgets, time-varying effectiveness, reach & frequency
  channels (Meridian-only input), synergies. A stretch arm can add one of these
  (§7).
- **Simulator checks before freezing data:** spend-spans-K check per channel,
  target correlation matrix realized, variance decomposition report, seed
  determinism test.
- **Per-channel recoverability gate (C7 in `simulation/checks.py`, added
  2026-09-09):** the *total* media-variance check above only bounds the sum
  across channels — v1 passed it with ~85% of the media signal in one channel
  and four channels under 1% each, and two of those four turned out to be
  unrecoverable by any estimator, tools included (`analysis/ORACLE.md`). C7
  prints signal-to-noise per channel (std of the channel's true national
  contribution / std of national revenue noise) and **warns**, never fails,
  below a floor of 0.15 — v1 itself has two channels (ooh, display) under it,
  disclosed as a finding rather than fixed. C7 is a cheap proxy; `python
  analysis/oracle.py` is the pre-registered ground-truth check any future
  scenario should run *before* committing a GPU run to it — see
  `analysis/ORACLE.md` for what it actually measures and why C7 cannot
  replace it.

## 4. Metrics (pre-registered in Phase 2)

The scoring harness is **estimator-agnostic**: each tool run exports the same
results schema (defined in Phase 2), and the scorer consumes only that schema —
so adding a third estimator later (see `BACKLOG.md`) means writing one
exporter, not touching the harness.

- **M1 — ROI recovery:** per-channel (est − true)/true. Meridian: posterior
  median + 90% CrI. Robyn: selected model + min–max across top Pareto candidates.
- **M2 — Contribution shares:** absolute error in percentage points.
- **M3 — Response-curve bias** at spend p50 and p90 (Jin's Table-4 style).
- **M4 — Uncertainty honesty:** Meridian CrI coverage of truth across the 5
  seeds; Robyn analog = does the candidate spread contain the truth.
- **M5 — DECOMP.RSSD probe:** estimated effect share vs spend share vs true
  effect share (does Robyn drag estimates toward spend share?).
- **M6 — Convergence/health:** Meridian R-hat & divergences; Robyn convergence
  flags & iterations-to-plateau.
- **M7 — Operational cost:** wall-clock runtime, setup hours, and a friction log
  (kept from day one, per tool).

## 5. Fairness & disclosure ledger (feeds "What neither tool can tell you")

Disclose rather than hide: (a) generator uses geometric+Hill — inside both
families but still a modeling choice; (b) Robyn constrained to its recommended
bounds, truths chosen inside them; (c) Meridian's concave-leaning slope prior vs
our S=2 channel; (d) DECOMP.RSSD is a business heuristic, probed by design;
(e) geo asymmetry (Robyn national-only) — handled by the two-arm design;
(f) base scenario has exogenous spend — the *easy* regime; real MMMs face
endogeneity, so measured accuracy is an upper bound; (g) constant true
parameters over time — an assumption both tools share and reality doesn't;
(h) priors/bounds do a lot of work in both tools at n≈156 — shown, not
asserted; (i) exposure frequency — neither tool models it in the core
regression, so it gets a paragraph in the article, not a phase (see `BACKLOG.md`).

**Amendment, 2026-09-11 (pre-publication audit): D5 contradicted this plan's own
parameter table.** D5 requires every true adstock retention inside Robyn's
recommended bounds (OOH/print 0.1–0.4, digital 0.0–0.3); the §3 table, committed
alongside it, sets ooh to 0.6 and display to 0.4. The generator implemented the
table and Robyn ran with D5's bounds, so on those two channels the true carryover
lies outside what Robyn could fit — the arrangement D5 says would rig the test.
Ledger item (b) holds for tv, social (at the edge of its bound) and search only.
It is disclosed rather than fixed, because fixing it means regenerating the data
and re-running both tools. Those two channels sit below the C7 signal-to-noise
floor, where no estimator recovers anything here, so the recoverability result
does not rest on them. Robyn's five-channel means do include them, and because
ooh's spend was designed to track tv's, the cap may also have moved carryover
onto Robyn's tv estimate — not tested.

**Amendment, 2026-09-11 (pre-publication audit): Meridian's default slope prior
is not "concave-leaning".** §1 (item 6), D5's rationale and ledger item (c)
describe it so. In
Meridian 1.8.0 `slope_m` is `Deterministic(1.0)`: every Hill slope is fixed at
1, which is why the committed geo extracts, listing R-hat for every sampled
parameter, have no slope entry. Under the pre-registered default priors (MD2)
Meridian therefore cannot fit tv's S-shape (true slope 2) at all, matches ooh's
slope of 1 exactly, and cannot express the other three (0.7 to 0.9) either, though it comes close.
D5 meant the S-shaped channel as a disclosed stressor; the article and README
disclose it only as of this amendment. With the D5 amendment above, each tool's
pre-registered setup excluded part of the truth: Robyn's adstock on two
channels, Meridian's response shape on four.

**Amendment, 2026-09-11 (pre-publication audit): ledger item (h) was never
shown.** Figure 1 draws each tool's reference level (Meridian's ROI-prior
median, Robyn's portfolio ROI), but no ablation measured how much work the
priors and bounds did at n≈156, so the article says only that they may do much
of it, untested — and after the two amendments above, part of that work was
excluding the truth. An oracle rung with the slope fixed at 1 would measure Meridian's share;
it is proposed in `docs/BACKLOG.md`, not run.

## 6. Execution phases

> Each phase ends with: update `STATUS.md` (phase done, next step), commit.
> A fresh `/oi` session = read STATUS → open the phase section below → go.
>
> **Machine split** (two-PC workflow, see `CLAUDE.md`): Phases **1, 3, 4** run
> on the GPU desktop (WSL2 + CUDA). Phases **2, 5, 6** need only plain Python +
> committed files and run on either machine. Phases 1 and 2 have no dependency
> on each other — they can proceed in parallel on the two machines.

### Phase 1 — Environments (est. 2–4 h, some unattended)
- [ ] **Igor (GPU desktop, admin):** install WSL2 + Ubuntu (`wsl --install`),
      reboot; current NVIDIA Windows driver (CUDA libraries inside WSL come via
      pip's `[and-cuda]` extras — no separate CUDA toolkit install).
- [ ] Meridian env: Ubuntu Python 3.12 venv,
      `pip install "google-meridian[and-cuda]==1.8.0"`, lockfile via
      `pip freeze`; smoke test = TF sees the RTX 4070 Super
      (`tf.config.list_physical_devices('GPU')`) + tiny model on Meridian's own
      sample data (few draws) on GPU, record wall-clock.
- [ ] Robyn env: R ≥ 4.2 (apt/CRAN), `install.packages("Robyn")` (3.12.1),
      Python 3.10 venv + `nevergrad`, pin `RETICULATE_PYTHON` in `.Renviron`;
      smoke test = `dt_simulated_weekly`, ~200 iterations × 1 trial; confirm
      multi-core engages ("Using X cores"); record wall-clock.
- [ ] Write `envs/ENVIRONMENT.md` (exact versions, install scripts, every
      friction item → M7 log). **Gate:** both smoke tests sample/optimize.
- Fallback: Meridian native-Windows pip attempt is NOT plan-A; if WSL2 is
  blocked, go Colab (D10). Robyn native-Windows single-core is the fallback if
  R-in-WSL misbehaves.

### Phase 2 — Simulator + pre-registered scoring — **DONE 2026-08-27**
- [x] `simulation/` Python package (runs on Windows Python 3.14 or the WSL venv —
      no tool dependencies): config-driven generator per §3, seeded.
- [x] Counterfactual ground-truth module (true ROI, true curves) → `ground_truth.json`.
- [x] Sanity checks per §3 (`python -m simulation.checks`, exit 0 on all 5
      seeds); `data/README.md` documents every assumption.
- [x] Tool-agnostic results schema in `analysis/RESULTS_SCHEMA.md`.
- [x] Scoring harness `analysis/scoring.py` (M1–M5); selftest
      (`--selftest`) distinguishes an honest stub from a spend-share-biased
      stub and flags the latter's rssd_pull.
- [x] Robyn model-selection rule pre-registered in `analysis/SELECTION_RULE.md`.
- [x] 5 seeds × (geo + national + Robyn CSVs + ground truth) in `data/sim/`.
      **Gate met:** checks pass; scoring runs end-to-end on stubs.
- Calibration notes: tv–ooh spend correlation realized 0.34–0.61; media var
      share 0.23–0.35 (seeds 103/105 slightly above the 0.30 ideal — accepted
      and disclosed); tv true mROI > ROI (S-shaped curve below inflection —
      intentional).

### Phase 3 — Meridian runs (est. 1–2 h active + background runtime)
- [ ] National arm × 5 seeds: default priors, documented `n_chains/n_adapt/
      n_burnin/n_keep` (start ~4–7 chains × 1000 keep; `seed` fixed), R-hat check.
- [ ] Geo arm × 1–2 seeds.
- [ ] Export per-run: ROI posteriors, contribution shares, response curves,
      runtime, convergence report → `outputs/meridian/` (gitignored if large;
      committed extracts in `runs/meridian/results/`).
- [ ] Document every decision in `runs/meridian/DECISIONS.md`. **Gate:** all
      primary-arm runs converged (R-hat < 1.1) or divergences documented.

### Phase 4 — Robyn runs (est. 1–2 h active + background runtime)
- [ ] Input mapping (spend + exposure vars, context, Prophet country/holidays),
      recommended bounds (D5), 2000 iterations × 5 trials, seeds aligned to the
      5 datasets; select via pre-registered rule; also export top-candidate spread.
- [ ] Minimal `robyn_outputs` exports (plotting is the known resource hog).
- [ ] Same exports + `runs/robyn/DECISIONS.md`. **Gate:** converged runs (or
      documented non-convergence) for all 5 seeds.

### Phase 5 — Scoring & comparison (est. 2 h) — DONE 2026-09-09
- [x] Run the pre-registered harness over both tools' extracts → metrics tables.
      `analysis/scoring.py` over all seven tool-arms (both tools plus the four
      oracle rungs) → `analysis/out/metrics_long.csv` and the committed
      `analysis/out/summary.md`.
- [x] Charts: (1) estimated vs true ROI per channel per tool (the money chart);
      (2) response curves est vs truth; (3) coverage/spread visualization.
      `analysis/figures.py` → the three PNGs in `analysis/figures/`. The oracle
      is a third series in charts 1 and 2 — without it chart 1 is a tie
      (0.533 vs 0.555 mean absolute ROI error) rather than a result. Every
      design choice is recorded in `analysis/FIGURES.md`.
- [ ] Optional if time: one sensitivity mini-arm (Meridian ROI-prior tweak OR
      Robyn bounds widened) — pick ONE. **Not done, and not planned for v1.**
      The oracle answers the question the mini-arm was there to answer — is the
      miss the tool's or the data's — with five seeds behind it instead of one
      arm. Re-running either tool with different settings after seeing the
      results is also the move this project's pre-registration exists to avoid.
      It stays in `docs/BACKLOG.md` for v2, where it would be pre-registered.

### Phase 6 — Writing (est. 2–3 h)
- [ ] `article/` ~1,000 words: setup, results (conditional verdict — who was
      closer under which conditions), decision guide, **"What neither tool can
      tell you"** (§5 ledger + multicollinearity + endogeneity + priors-do-the-
      work + MMM ≠ incrementality testing).
- [ ] README rewrite for the public repo; final reproducibility pass (fresh-clone
      re-run instructions); public-audience test on full history.

### Stretch arms (only after Phase 6, each optional)
- S1: noise ladder (2× / 4× noise). S2: endogenous-spend scenario (Heusch-style
  demand chasing). S3: Meridian JAX backend timing. S4: "nobody's functional
  form" robustness (logistic saturation generator).

Post-v1 backlog and discarded ideas, with rationale: **`BACKLOG.md`**. Scope
guard: the Robyn-dormancy timing angle is perishable — nothing in the backlog
or stretch list may delay v1 publication.

**Honest total estimate: ~12–16 h** (BRIEF said ~8 h; environment setup and dual
runs are the overrun — flagged here deliberately).

## 7. Risks & fallbacks

| Risk | Mitigation |
|---|---|
| GPU desktop unavailable / WSL2 blocked | Robyn native single-core on the laptop (per-user R install, no admin needed) + Meridian Colab (D10) |
| 12 GB VRAM vs Meridian's tested 16 GB | dataset is small; if memory bites: `n_chains` as a list, 1.8.0's `reconstruction_batch_size`, CPU fallback stays viable |
| Meridian CPU runtime unworkable | fewer chains, `n_burnin=0`, thinning for iteration; Colab for finals |
| Robyn ggplot2 4.x breakage on fresh 2026 install | pin ggplot2 < 4 in env; known risk from research |
| Nevergrad/reticulate misbinding | official `install_nevergrad.R` flow, `RETICULATE_PYTHON` pinned, restart R |
| Neither tool recovers anything (too-hard scenario) | that IS a publishable result with ground truth to prove it; check simulator sanity first, then report honestly |
| Scope creep | stretch arms live strictly after Phase 6 |

## 8. Part 2 pre-registration (amendment, 2026-09-29)

Written and committed **before any number in it is computed**. It fixes the
three new oracle rungs, the answers they are meant to give, the two scoring
additions, and the budget-regret metric with the per-channel limits that C11
and C12 use. Everything here runs on the v1 data and the v1 extracts; no tool
is re-run. A change to anything below needs a dated amendment of its own.

### 8.1 Setup-constrained rungs (C10)

`analysis/AUDIT.md` left three questions open, all of the same kind: every
v1 rung is handed the true shape, so the ladder cannot tell how much of a
tool's miss came from the parameter space its setup allowed. Three new
national rungs answer that. They share everything with L3 — national
aggregate exposure (pre-window exposure known, as in L1–L4), the same
estimated baseline (intercept + linear trend + 3 annual Fourier harmonics +
the observed control), unconstrained OLS for the betas — and replace L3's
known shape with a shape **estimated from the data**. They differ from each
other only in the parameter space the shape is searched over:

| Rung | Tool id | Shape searched over |
|---|---|---|
| L5 | `oracle_nat_fitshape` | the generator's own family, free: retention θ ∈ {0, 0.05, …, 0.95}; Hill slope s ∈ {0.3, 0.4, …, 4.0}; half-saturation k ∈ {0.05, 0.10, …, 4.00} (k in the generator's units: multiples of the channel's mean window exposure per capita) |
| L6 | `oracle_nat_meridian_setup` | Meridian 1.8.0 as run in v1: s ≡ 1 (`slope_m` is `Deterministic(1.0)`); θ on L5's grid (`alpha_m` is `Uniform(0, 1)`); k on L5's grid, inside the support of `ec_m`, `TruncatedNormal(0.8, 0.8, 0.1, 10)`, whose units are Meridian's median-scaled media, mapped to the generator's units by × median(national exposure per capita)/mean |
| L7 | `oracle_nat_robyn_setup` | Robyn 3.12.1 as run in v1 (RD2): θ inside each channel's bounds (tv 0.3–0.8, ooh 0.1–0.4, social/display/search 0–0.3) on L5's grid; s = Robyn's α ∈ [0.5, 3] on L5's grid; k on L5's grid, inside Robyn's γ ∈ [0.3, 1], where Robyn's inflexion is γ · max(z) and z is Robyn's own adstocked series — the unnormalised geometric recursion over the 156 window weeks it sees, cold start. Mapped to the generator's units by the steady-state ratio z/u = population × mean exposure per capita / (1 − θ) |

The three definitions were read from the installed packages on the run
machine on 2026-09-29, not from documentation: Meridian's
`model/prior_distribution.py` for `alpha_m`, `ec_m` and `slope_m`, its
`model/transformers.py` for the population-scaled non-zero median, and
Robyn's `saturation_hill` (`inflexion <- max(x) * gamma`). Only **hard
constraints** are modelled — the support of a prior, the bounds of a
hyperparameter. Where a prior puts its mass inside that support is left to
the tool's side of the ledger in 8.3, not to the setup's.

Two family differences are deliberately **not** modelled, because they are
not what the audit asked about and modelling them would blur the contrast:
Meridian's adstock window is `max_lag + 1` = 14 weights against the
generator's 13 (the 14th weight is 0.7¹³ ≈ 0.01 of the first, on tv);
Robyn's adstock is unnormalised and cold-started. All three rungs use the
generator's normalised 13-week adstock with the warm-up known; the setup
constraint is the only thing that changes between them.

**Estimation.** Variable projection: for a fixed shape, the betas and the
baseline are OLS; the shape is found by coordinate descent over channels —
for one channel, an exhaustive search over its admissible grid with the other
four held fixed; cycle through the five until no parameter changes (at most
50 cycles). Eight starts per run: the true shape projected to the nearest
admissible grid point, and seven admissible grid points drawn uniformly by a
generator seeded with (dataset seed, rung number). The run keeps the start
with the lowest residual sum of squares. Each JSON records, under `extras`,
the fitted shape, how many starts reached the best SSR (relative tolerance
1e-9), whether the truth-projected start was the winner, the cycles used, and
which fitted parameters sit on an admissible boundary.

A grid rather than a gradient optimiser, because the analysis lock has no
scipy and a new dependency is not worth one rung; and because every true
parameter lies on L5's grid, which makes the optimiser testable (next
paragraph). Grid resolution is part of each rung's error and is disclosed as
such.

**The optimiser check, and its stop rule.** Before any rung is exported, the
procedure is run on revenue built exactly from L2's national regressors with
the true shape and true betas, with no noise and no baseline, and fitted with
L2's design. L5's parameter space contains the truth, so the search must
return the true ROI on every channel of every seed to 1e-9 — and it must do
so from the **seven random starts alone**: the truth-projected start begins
at the answer and would pass the check without testing anything. If it does
not, the optimiser is not trusted and **no L5–L7 number is published**; the
failure is reported instead.

**No intervals.** An OLS interval conditional on a fitted shape ignores the
uncertainty of the shape and would read as a calibration result it is not.
The three rungs export ROI, mROI, contribution share and response curve
without `interval_low`/`interval_high`; their coverage is not reported.

### 8.2 Pseudo-true projections (C10)

Noise and setup are confounded in any single noisy fit. To separate them, the
same procedure is run once per seed on **noiseless** national data with the
true baseline and control removed (y = the sum of the five true national
media contributions; L2's design with the shape fitted). What remains is the
setup's bias plus the aggregation gap L2 already measures. Five parameter
spaces are projected:

1. free (L5's space) — the aggregation-only reference;
2. Meridian's space (L6);
3. Robyn's space (L7);
4. free, except ooh's and display's θ capped at Robyn's bounds;
5. free, except tv's slope fixed at 1.

These go to `analysis/out/diagnostics.md` through `oracle.py --diagnostics`,
not to scored JSONs.

### 8.3 The three open questions, and the decomposition

- **Q1 — how much of Meridian's miss on tv, search and social is its fixed
  slope.** Per channel: the setup's price on noisy data,
  mean|err L6| − mean|err L5| over the five seeds, set against Meridian
  national's mean|err|; and the pseudo-true bias, projection 2's ROI error
  minus projection 1's.
- **Q2 — did one channel's constraint reach the other.** Robyn: tv's ROI error
  in projection 4 minus projection 1. Meridian: ooh's ROI error in projection
  5 minus projection 1. Each is reported as a fraction of the tool's mean|err|
  on that channel. No pass/fail threshold: the size is the answer.
- **Q3 — do Robyn's γ bounds contain the true half-saturation.** Per seed and
  channel, γ_true = k_true × population × mean exposure per capita /
  ((1 − θ_true) × max z), with z as in L7 at θ_true; contained iff
  0.3 ≤ γ_true ≤ 1. Because the steady-state ratio is an approximation, the
  observed range of z/u over window weeks 13 onward is reported beside it,
  and a verdict within that range of a bound is reported as "at the bound",
  not as inside or outside.

**The decomposition.** For each tool T (Meridian national, Robyn national)
and each channel, the mean absolute ROI error over the five seeds splits
exactly into three terms:

    |err T| = |err L5|                        estimating the shape (the data's price)
            + (|err setup(T)| − |err L5|)     the setup's parameter space
            + (|err T| − |err setup(T)|)      the tool: priors, regularisation,
                                              DECOMP.RSSD, baseline machinery,
                                              sampler and model selection

with setup(Meridian) = L6 and setup(Robyn) = L7. It is an identity on the
means, not per seed. A negative term is reported as it is, never clipped.
Only tv, search and social are interpreted; ooh and display are reported and
flagged as below the recoverability floor (`analysis/ORACLE.md`), where no
term means anything.

### 8.4 Scoring additions (C10)

1. **Rank agreement.** Per run, the Spearman correlation between estimated
   and true ROI across the five channels; per tool-arm, its mean and range
   over seeds. With five channels it moves in steps of 0.1.
2. **Seed-level spread of the tool difference.** National arm, per seed:
   D = mean over channels of |err Meridian| − the same for Robyn. Reported:
   each seed's D, their mean and standard deviation (ddof = 1), and how many
   seeds each tool is lower on.

### 8.5 Budget regret and per-channel limits (C11, C12)

- **Allocation.** A vector of per-channel multipliers m applied to the whole
  observed spend series — the response curve's own definition. The total
  budget is fixed at observed window spend: Σ m_c × spend_c = Σ spend_c.
- **Curves.** Piecewise-linear interpolation of the 10-point response curves
  on the generator's multiplier grid: true curves from `ground_truth.json`,
  estimated curves from each result JSON's `response_curve`. The same
  interpolation is used to optimise and to evaluate, so the true curves give
  a regret of exactly 0.
- **Optimiser.** Exact, by vertex enumeration: a separable piecewise-linear
  objective under one linear budget constraint and box limits has an optimum
  where at most one channel sits strictly between breakpoints. No numerical
  optimiser.
- **Metric.** With a* the allocation that maximises true incremental revenue
  and â the one that maximises the estimator's: regret =
  (R_true(a*) − R_true(â)) / R_true(a*), the share of the achievable
  incremental revenue lost. Secondary: uplift captured =
  (R_true(â) − R_true(1)) / (R_true(a*) − R_true(1)), where 1 is the observed
  allocation.
- **Limits, primary: m_c ∈ [0.5, 2.0] for every channel.** Robyn 3.12.1's
  `robyn_allocator` default for `max_response` (read from the installed
  source, 2026-09-29). Both ends are points of the multiplier grid. C12 runs
  both tools' own allocators with these limits.
- **Limits, sensitivity: m_c ∈ [0.7, 1.3].** Meridian 1.8.0's default for a
  fixed-budget optimisation (`SPEND_CONSTRAINT_DEFAULT_FIXED_BUDGET = 0.3` in
  `constants.py`, read 2026-09-29). Neutral optimiser only; the allocators are
  not re-run with it.
- **Estimators.** Meridian national, Meridian geo (two seeds, flagged),
  Robyn national, and oracles L2, L3, L5, L6 and L7. One line per estimator
  in `## Budget regret` in `analysis/out/summary.md`.

### 8.6 Amendment, 2026-09-29 (same day): the stop rule fired

**What happened.** §8.1 was implemented as written (commit `a9e062b`), and
its optimiser check failed on all five seeds. From the seven random starts
the search did not return the true shape on noiseless data built from L2's
regressors: max |ROI rel err| 0.75, 5.8, 0.72, 4.8 and 0.67 on seeds 101 to
105, with one of the seven starts on the winner each time
(`python analysis/oracle.py --rungs L5` at `a9e062b` reproduces it). It is
not a code error: the truth-projected start sits at an SSR of about 1e-16
and stays there, while the random starts stop at shapes whose SSR is about
1e-7 of y'y. An exploratory run with 40 random starts on seeds 101–103
reached the truth from none of them (the script was not kept). Coordinate
descent cannot cross the ridges along which one channel's shape compensates
for another's, and on the national aggregate the five shapes are close to
jointly unidentified even without noise. As the stop rule requires, no
L5–L7 number from that search exists. **No fit on noisy data was run before
this amendment**, so no result motivated what follows.

**What replaces §8.1 and §8.2.**

- **L5 is retired**, and its name is not reused. Part 2 does not measure what
  estimating the shape costs.
- **L6 and L7 become projection rungs**: L3, with each channel's regressor
  replaced by the best approximation of that channel's true response inside
  the tool's space. Per channel, the target is L3's own regressor (the true
  shape), and the projection is the admissible (θ, s, k) that minimises
  min over β of ‖target − β · candidate‖², with no intercept, so the level is
  matched as well as the variation — the level is what an ROI measures. The
  search is exhaustive on §8.1's grid, then exhaustive on a grid ten times
  finer (steps 0.005 in θ, 0.01 in s, 0.005 in k) spanning one coarse step
  either side of the coarse winner, restricted to the space; Robyn's γ bound
  is applied at each fine θ. One channel at a time: each of these problems is
  identified, which is what the joint search lacked. The betas and the
  baseline are then fitted by OLS on noisy national revenue with L3's
  design, exactly as L3.
- **Intervals.** The shape is now fixed before revenue is seen, as in L3, so
  L6 and L7 export L3's OLS 90% interval (`ols_ci90`). §8.1's "no intervals"
  no longer applies.
- **The check** that replaces §8.1's: projecting onto the free space must
  return the true shape exactly, on every channel of every seed (the truth
  is on the coarse grid, where its residual is 0). It is now a check of the
  code, not of a search. The stop rule keeps its force: if it fails, no L6
  or L7 result is exported.
- **Pseudo-true projections** (replaces §8.2). The projected columns, fitted
  by OLS without a baseline to noiseless national data (the true national
  media contributions, summed from the geo level). Reference: the same fit
  with the true columns, which is L2 without noise — the aggregation gap
  alone. Spaces: Meridian's, Robyn's, and for Q2 two partial variants —
  (4) only ooh's and display's regressors projected onto Robyn's space, the
  rest true; (5) only tv's regressor projected onto Meridian's space, the rest
  true. The two variants are also fitted on noisy revenue with L3's design,
  five seeds. All of this goes to `analysis/out/diagnostics.md`, not to
  scored JSONs.

**What changes in §8.3 and §8.5.**

- **L3 replaces L5 as the reference.** Q1: mean|err L6| − mean|err L3|, and
  the pseudo-true bias of Meridian's space minus the reference's. Q2: tv's
  error under variant 4 minus under L3 (noisy, mean over seeds) and minus the
  reference (noiseless), for Robyn; ooh's under variant 5, the same way, for
  Meridian; each as a fraction of the tool's mean|err| on that channel. Q3 is
  unchanged.
- **The decomposition** keeps its form with L3 in L5's place:

      |err T| = |err L3|                        knowing the shape, estimating the baseline
              + (|err setup(T)| − |err L3|)     the setup's parameter space
              + (|err T| − |err setup(T)|)      everything else

  The cost of estimating the shape now sits in the third term, which
  therefore mixes a difficulty of the data with the tool's machinery. Any
  sentence that quotes the third term says so.
- **Regret estimators:** L5 is removed from §8.5's list.

### 8.7 Amendment, 2026-09-29 (same day): the k grid was tighter than Meridian

**What happened.** On the first run of §8.6, Meridian's-space projection of
tv landed on k = 4.00 on every seed: the ceiling of §8.1's k grid, not of
Meridian's space. The best slope-1 approximation of tv's S-curve is close
to linear, and it keeps asking for a larger half-saturation. `ec_m`'s
ceiling of 10, mapped to the generator's units, sits near 5.3 for tv, so
L6 as run was more constrained than Meridian was — against §8.1's own
wording ("inside the support of `ec_m`"). **Seen before this amendment:**
that run's mean |ROI rel err| over all channels and seeds, 0.661 for L6 and
0.635 for L7, printed by `oracle.py`; no per-channel number and no
comparison with the tools. The amendment is decided on the boundary hit,
which is a statement about the grid, not about any result.

**What changes.** The k grid runs from 0.05 to **10.00** in steps of 0.05, for
every space. `oracle.py` refuses to run if `ec_m`'s mapped ceiling exceeds
the grid on any channel of any seed, so the grid can never again be the
binding constraint for Meridian's space. The free space and Robyn's are
unaffected in substance (the free projection must still return the truth,
and Robyn's γ ≤ 1 keeps k far below the new ceiling). A projection that
lands on a bound of its space is reported with the bound's name.
