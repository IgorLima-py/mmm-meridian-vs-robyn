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
