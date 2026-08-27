# References

Research compiled 2026-08-27 (planning session). Access dates = 2026-08-27 unless
noted. Items marked ⚠ are vendor-authored — useful, but they have a horse in the
race.

## Official docs, repos, releases

- Meridian repo — https://github.com/google/meridian — latest 1.8.0 (PyPI
  2026-08-15); tags only, no GitHub Releases; monthly cadence through 2026.
- Meridian PyPI — https://pypi.org/project/google-meridian/ — 1.8.0 pins
  `tensorflow>=2.21,<2.22` and an exact `tfp-nightly==0.26.0.dev20260130`.
- Meridian install docs — https://developers.google.com/meridian/docs/user-guide/installing
  — Python 3.11/3.12; only Linux (GPU) and macOS (CPU) listed; Windows absent.
- Meridian run-model docs — https://developers.google.com/meridian/docs/user-guide/run-model
  — `n_chains` as list, `n_burnin=0` note, ~15% thinning for iteration.
- Meridian getting-started colab — https://developers.google.com/meridian/notebook/meridian-getting-started
  — free-tier T4; sampling ≈ 10 min at 10 chains × 1000 keep on demo data.
- Meridian JAX backend — https://developers.google.com/meridian/docs/advanced-modeling/using-jax
  — introduced 1.6.0 (2026-04-30); ~40% faster on GPU (no CPU claims).
- Meridian saturation/lagging — https://developers.google.com/meridian/docs/advanced-modeling/media-saturation-lagging
- Meridian default priors — https://developers.google.com/meridian/docs/advanced-modeling/default-prior-distributions
  (verify exact values against `meridian/model/prior_distribution.py` before quoting).
- Meridian CHANGELOG — https://github.com/google/meridian/blob/main/CHANGELOG.md
  — TF-version-linked result drift (see also issue #976); Py3.10 dropped in 1.5.3.
- Meridian sample data — https://github.com/google/meridian/tree/main/meridian/data/simulated_data
  — geo/national CSVs; no generator or ground truth shipped.
- Meridian RF data-simulation notebook — https://github.com/google/meridian/blob/main/demo/RF_Data_Simulation_for_Meridian.ipynb
  — full recipe WITH ground truth, but uses Meridian's own transformers (biased
  as a comparison generator; useful as reference code).
- Meridian issues: Windows #449 (closed wontfix; WSL2 walkthrough),
  #439/#331/#1263 (Windows failures), #534 (national weekly + Colab RAM growth),
  #707 (absurd R-hat), #976 (TF-version result discrepancies), #659
  (vs-Robyn question, unanswered) — https://github.com/google/meridian/issues
- Robyn repo — https://github.com/facebookexperimental/Robyn — last main commit
  2025-06-27; last GitHub release v3.12.0 (2024-12-19).
- Robyn CRAN — https://cran.r-project.org/web/packages/Robyn/index.html — 3.12.1
  (2025-07-02); R ≥ 4.0; maintainer Bernardo Lares.
- Robyn features docs — https://facebookexperimental.github.io/Robyn/docs/features/
  — adstock (geometric/Weibull), Hill, DECOMP.RSSD, recommended hyperparameter
  bounds (θ: TV 0.3–0.8, OOH/print 0.1–0.4, digital 0.0–0.3; α ∈ [0.5,3],
  γ ∈ [0.3,1]).
- Robyn demo script — https://github.com/facebookexperimental/Robyn/blob/main/demo/demo.R
  — canonical roles for `dt_simulated_weekly`; 2000×5 recommendation.
- Robyn `robyn_run` reference — https://rdrr.io/cran/Robyn/man/robyn_run.html
- Robyn nevergrad install script — https://github.com/facebookexperimental/Robyn/blob/main/demo/install_nevergrad.R
- Robyn single-core-on-Windows (source) — https://github.com/facebookexperimental/Robyn/blob/main/R/R/checks.R
  (`check_parallel()` is unix-only) + issue #714 ("1 core (Windows fallback)").
- Robyn Windows/nevergrad pain issues: #25, #181, #487, #670, #697, #817, #1004;
  runtime #118, #668; plotting RAM #858, #172; geo not supported: discussion
  #856, issue #1057 — https://github.com/facebookexperimental/Robyn/issues
- Robyn iteration guidance — https://github.com/facebookexperimental/Robyn/discussions/937
- RobynPy (beta LLM-translated Python port of 3.11.1; stalled 2025-04) —
  https://pypi.org/project/robynpy/
- TensorFlow Windows support policy — https://www.tensorflow.org/install/pip
  — no native-Windows GPU after 2.10; CPU wheels third-party (Intel).

## Papers & methodology

- Jin, Wang, Sun, Chan & Koehler (Google, 2017), *Bayesian Methods for Media Mix
  Modeling with Carryover and Shape Effects* —
  https://research.google/pubs/bayesian-methods-for-media-mix-modeling-with-carryover-and-shape-effects/
  — THE template: geometric/delayed adstock, Hill, simulation Table 1 parameters,
  curve-bias scoring, counterfactual ROAS, prior sensitivity at n≈104.
- Chan & Perry (Google, 2017), *Challenges and Opportunities in Media Mix
  Modeling* — https://research.google/pubs/challenges-and-opportunities-in-media-mix-modeling/
  — the standard pitfalls citation (sample size, collinearity, spend range,
  selection bias).
- Zhang & Vaver (Google, 2017), *Aggregate Marketing System Simulator* (AMSS) —
  https://github.com/google/amss (archived 2022) — model-agnostic generator;
  counterfactual-ROAS ground-truth methodology.
- Zhang et al. (Google, 2024), *Media Mix Model Calibration With Bayesian
  Priors* — https://research.google/pubs/media-mix-model-calibration-with-bayesian-priors/
  — basis of Meridian's ROI priors.
- Runge, Skokan, Zhou & Pauwels (2024), *Packaging Up Media Mix Modeling* (the
  Robyn paper) — https://arxiv.org/abs/2403.14674
- Runge, Pauwels, Skokan & Zhou (2026), *Open-Source Media and Marketing Mix
  Modeling* , Customer Needs and Solutions —
  https://link.springer.com/article/10.1007/s40547-026-00161-4
- Dew, Padilla & Shchetkina (2024), *Your MMM is Broken* —
  https://arxiv.org/pdf/2408.07678 — saturation vs time-variation identification.
- Heusch (2026), *A Synthetic Benchmark Dataset with Endogenous Marketing
  Spend…* — https://arxiv.org/abs/2608.21130 + https://github.com/oygo/mmm-synthetic
  — endogenous-spend generator; stretch-arm S2 reference.
- Heusch (2026), *Structural Estimation of MMM Parameters from Geo-Experiments* —
  https://arxiv.org/html/2608.21128 — observational-MMM bias framing.
- Orduz, *Media Effect Estimation with ROAS priors* (simulation study) —
  https://juanitorduz.github.io/mmm_roas/ — confounding inflates ROAS ~2×.

## Simulators & evaluation harnesses

- Meta siMMMulator (R) — https://github.com/facebookexperimental/siMMMulator —
  ground-truth ROI generator, Robyn-style Hill parameterization, dormant since
  2023-07. ⚠ Meta-authored.
- PySiMMMulator — https://github.com/RyanAugust/PySiMMMulator — small third-party port.
- pymc-marketing data generator —
  https://www.pymc-marketing.io/en/stable/notebooks/mmm/mmm_data_generator.html
  — maintained; logistic saturation ("nobody's form" option). ⚠ PyMC Labs.
- mmm-eval (Mutinex) — https://github.com/mutinex/mmm-eval — holdout/stability/
  placebo battery; supports Meridian + PyMC, NOT Robyn; no ground-truth test. ⚠

## Prior comparisons (the competitive landscape)

- PyMC Labs, *PyMC-Marketing vs Google Meridian* (2025-09-08) —
  https://www.pymc-labs.com/blog-posts/pymc-marketing-vs-google-meridian —
  closest methodology; excluded Robyn. ⚠
- Vo, Phan & Nguyen, ICATSD 2026 repo —
  https://github.com/VoTatThien/mmm-meridian-robyn-comparison — both tools, same
  synthetic data, 10 seeds; stability/agreement scored, NOT truth recovery.
- Walsh / Linea Analytics (2025-12-02) —
  https://linea-analytics.com/articles/comparing-open-source/article.html — feature
  comparison; recommends Meridian for uncertainty + calibration. ⚠
- eliya.io (2025-05-22) — https://eliya.io/blog/media-mix-modeling/Meridian-vs-Robyn ⚠
- Incubeta (2025-12-01) — https://incubeta.com/knowledge-base/mmm-powerhouses-comparing-meridian-and-robyn/ ⚠ (Google partner)
- Search Engine Land, Wenner (2026-01-12) —
  https://searchengineland.com/mmm-tools-explained-467284 — "a well-executed
  Robyn beats an abandoned Meridian project".
- PyMC-Marketing "How We Compare" —
  https://www.pymc-marketing.io/en/stable/guide/mmm/comparison.html ⚠
- Nuso (2026-03-10) — https://nuso.co.uk/blog/robyn-vs-pymc-vs-meridian-shopify-mmm
  — runtime anecdotes (Robyn 5–15 min; Meridian 30+ min CPU). ⚠
- Cassandra YouTube comparison — https://www.youtube.com/watch?v=uUCKR2tsG5M ⚠

## Critiques, community & journalism

- Recast teardowns ⚠ — https://getrecast.com/facebook-robyn/ ,
  https://getrecast.com/google-meridian/ — ridge shrinkage / static-coefficients
  critiques; Kaminsky's validation triad (parameter recovery on simulated data,
  holdout, lift tests) on Mobile Dev Memo (2026-07-28) —
  https://mobiledevmemo.com/podcast-demystifying-open-source-mmm-with-michael-kaminsky/
- Aryma Labs ⚠, *Hits and Misses of Meridian* (2025-02-03) —
  https://arymalabs.substack.com/p/hits-and-misses-of-meridian-a-thorough —
  prior-sensitivity and log-normal-ROI critiques.
- AdExchanger, Hercher (2026-07-14) —
  https://www.adexchanger.com/marketers/googles-meridian-and-metas-robyn-a-gift-to-measurement-or-trojan-horses/
  — Robyn team reportedly "dismantled"; platform-incentive concerns (anonymous
  sourcing; treat as reported, not established).
- AdBeacon (2026-08-11) —
  https://www.adbeacon.com/google-is-doubling-down-on-meridian-while-meta-quietly-shelves-robyn/
- Robyn ground-truth failures by community: issue #625 (siMMMulator recovery
  failed) — https://github.com/facebookexperimental/Robyn/issues/625 ;
  discussion #918 (simulated-data recovery "wildly incorrect") —
  https://github.com/facebookexperimental/Robyn/discussions/918 ; maintainers
  acknowledge recovery testing gap — discussion #513.
- r/PPC Meridian launch thread (2025-01-29) —
  https://reddit.com/r/PPC/comments/1icuddv/ — practitioner sentiment; MMM Hub
  (https://mmmhub.org) named as the community venue.
- r/dataanalyst Robyn critique list (2025-01-14) —
  https://reddit.com/r/dataanalyst/comments/1i1hwi6/ (authorship uncertain;
  claims match wider discourse).
- Mutinex Open MMM Validation Framework (Mi3, 2025-07-22) —
  https://www.mi-3.com.au/22-07-2025/mmm-unmuddled-mutinex-lands-industry-wide-backing-open-sourced-model-comparison ⚠

## Research caveats

Compiled via web research agents; every load-bearing claim above carries its
source, but a few items were snippet-only (403/paywalled) and are flagged in the
session research notes. Before quoting anything verbatim in the article, re-open
the primary source. Known unverified items: Meridian native-Windows CPU install
success (nobody documents one); exact Meridian default prior values (read the
source file); origin/truth of Robyn's `dt_simulated_weekly`; the anonymous
AdExchanger claims.
