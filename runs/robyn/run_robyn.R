# Robyn runs over the simulated datasets (PLAN Phase 4).
#
# Fits Meta Robyn 3.12.1 on data/sim/seed<NNN>/robyn.csv, applies the
# pre-registered selection rule (analysis/SELECTION_RULE.md), and exports one
# JSON per seed in the schema of analysis/RESULTS_SCHEMA.md. Every modeling
# decision is documented in runs/robyn/DECISIONS.md.
#
# Run inside the WSL2 env, from the repo root (see envs/ENVIRONMENT.md):
#   Rscript runs/robyn/run_robyn.R 101 102 103 104 105
suppressPackageStartupMessages({
  library(Robyn)
  library(dplyr)
  library(jsonlite)
})

args <- commandArgs(trailingOnly = TRUE)
seeds <- if (length(args)) as.integer(args) else c(101L, 102L, 103L, 104L, 105L)

REPO <- getwd()
CH <- c("tv", "ooh", "social", "display", "search")
SPEND_VARS <- paste0(CH, "_S")
EXPO_VARS <- paste0(CH, "_I")
MULTIPLIERS <- c(0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0)
ITERATIONS <- 2000L
TRIALS <- 5L
CORES <- max(1L, parallel::detectCores() - 1L)
HARDWARE <- sprintf("WSL2 Ubuntu 26.04, %d cores (Ryzen 5 5600G), R 4.5.2", CORES)

# D5 recommended bounds by channel type; names follow the EXPOSURE variables
# (Robyn 3.12 convention — friction F7 in envs/ENVIRONMENT.md).
theta_bounds <- list(
  tv_I = c(0.3, 0.8), ooh_I = c(0.1, 0.4),
  social_I = c(0, 0.3), display_I = c(0, 0.3), search_I = c(0, 0.3)
)
hyperparameters <- list()
for (v in EXPO_VARS) {
  hyperparameters[[paste0(v, "_alphas")]] <- c(0.5, 3)
  hyperparameters[[paste0(v, "_gammas")]] <- c(0.3, 1)
  hyperparameters[[paste0(v, "_thetas")]] <- theta_bounds[[v]]
}
hyperparameters$train_size <- c(0.5, 0.8)

# Window-total incremental revenue of one channel at spend multiplier m,
# reconstructed from the selected model's own parameters. Impressions are
# linear in spend per week (generator), so scaling spend by m scales the
# exposure series by m. The fitted saturation curve keeps its observed
# inflexion (saturation_hill: inflexion = max(x) * gamma; x_marginal evaluates
# the scaled series on that fitted curve).
channel_curve <- function(expo_series, win_idx, theta, alpha, gamma, coef, m) {
  z <- adstock_geometric(expo_series, theta)$x_decayed[win_idx]
  sat <- saturation_hill(x = z, alpha = alpha, gamma = gamma, x_marginal = m * z)
  sum(coef * sat$x_saturated)
}

error_scores_safe <- function(df, ts_validation) {
  out <- tryCatch(
    Robyn:::errors_scores(df, ts_validation = ts_validation),
    error = function(e) NULL
  )
  if (!is.null(out)) return(out)
  # Documented fallback (DECISIONS.md RD7): min-max normalize each error on the
  # Pareto set, equal weights — the same intent as Robyn's composite.
  nrmse_col <- if (ts_validation && "nrmse_val" %in% names(df)) "nrmse_val" else "nrmse"
  norm01 <- function(x) if (diff(range(x)) == 0) rep(0, length(x)) else (x - min(x)) / diff(range(x))
  norm01(df[[nrmse_col]]) + norm01(df$decomp.rssd)
}

run_one <- function(seed) {
  cat(sprintf("=== robyn seed%d: inputs ===\n", seed))
  dt <- read.csv(file.path(REPO, "data", "sim", sprintf("seed%d", seed), "robyn.csv"))
  dt$DATE <- as.Date(dt$DATE)
  total_revenue <- sum(dt$revenue)
  robyn_seed <- 123L + (seed - 101L)

  heavy_dir <- file.path(REPO, "outputs", "robyn", sprintf("seed%d", seed))
  dir.create(heavy_dir, recursive = TRUE, showWarnings = FALSE)

  data("dt_prophet_holidays", envir = environment())
  InputCollect <- robyn_inputs(
    dt_input = dt,
    dt_holidays = dt_prophet_holidays,
    date_var = "DATE",
    dep_var = "revenue",
    dep_var_type = "revenue",
    prophet_vars = c("trend", "season", "holiday"),
    prophet_country = "US",
    context_vars = "competitor_index",
    paid_media_spends = SPEND_VARS,
    paid_media_vars = EXPO_VARS,
    window_start = min(dt$DATE),
    window_end = max(dt$DATE),
    adstock = "geometric",
    hyperparameters = hyperparameters
  )

  cat(sprintf("=== robyn seed%d: robyn_run (%d iter x %d trials, seed %d) ===\n",
              seed, ITERATIONS, TRIALS, robyn_seed))
  t0 <- Sys.time()
  # NOTE: no `quiet = TRUE` — Robyn 3.12.1 crashes with "object 'pb' not
  # found" when quiet suppresses the progress bar (friction F8).
  OutputModels <- robyn_run(
    InputCollect = InputCollect,
    iterations = ITERATIONS,
    trials = TRIALS,
    ts_validation = TRUE,
    seed = robyn_seed,
    cores = CORES
  )
  runtime <- as.numeric(difftime(Sys.time(), t0, units = "secs"))
  conv_msgs <- unlist(OutputModels$convergence$conv_msg)
  converged <- !any(grepl("NOT converged", conv_msgs, fixed = TRUE))
  cat(sprintf("    robyn_run: %.0fs; converged=%s\n", runtime, converged))

  cat(sprintf("=== robyn seed%d: outputs + clusters ===\n", seed))
  t1 <- Sys.time()
  OutputCollect <- robyn_outputs(
    InputCollect, OutputModels,
    pareto_fronts = "auto",
    clusters = TRUE,
    plot_folder = heavy_dir,
    plot_pareto = FALSE,
    csv_out = NULL,
    export = FALSE
  )
  outputs_seconds <- as.numeric(difftime(Sys.time(), t1, units = "secs"))

  # Persist the heavy objects BEFORE metric extraction so an exporter bug
  # never costs the modeling run itself.
  saveRDS(OutputModels, file.path(heavy_dir, "OutputModels.rds"))
  saveRDS(OutputCollect, file.path(heavy_dir, "OutputCollect.rds"))

  rhp <- as.data.frame(OutputCollect$resultHypParam)
  rhp$error_score_used <- error_scores_safe(rhp, ts_validation = TRUE)

  cl <- OutputCollect$clusters
  if (!is.null(cl) && !is.null(cl$models) && nrow(as.data.frame(cl$models)) > 1) {
    candidates <- unique(as.data.frame(cl$models)$solID)
    cl_assign <- as.data.frame(cl$data)[, c("solID", "cluster")]
    best_overall <- rhp$solID[which.min(rhp$error_score_used)]
    win_cluster <- cl_assign$cluster[match(best_overall, cl_assign$solID)]
    in_win <- candidates[candidates %in% cl_assign$solID[cl_assign$cluster == win_cluster]]
    selected <- if (length(in_win)) {
      in_win[which.min(rhp$error_score_used[match(in_win, rhp$solID)])]
    } else best_overall
    selection_path <- "clusters"
  } else {
    candidates <- rhp$solID
    selected <- rhp$solID[which.min(rhp$error_score_used)]
    selection_path <- "pareto_fallback (SELECTION_RULE.md step 5)"
  }
  cat(sprintf("    selected=%s from %d candidates (%s)\n",
              selected, length(candidates), selection_path))

  xda <- as.data.frame(OutputCollect$xDecompAgg)
  win_idx <- InputCollect$rollingWindowStartWhich:InputCollect$rollingWindowEndWhich
  sel_hyp <- rhp[rhp$solID == selected, ]

  get_metrics <- function(sol) {
    rows <- xda[xda$solID == sol & xda$rn %in% EXPO_VARS, ]
    rows$channel <- sub("_I$", "", rows$rn)
    rows
  }
  sel_m <- get_metrics(selected)
  cand_m <- do.call(rbind, lapply(candidates, get_metrics))

  channels_out <- list()
  for (i in seq_along(CH)) {
    ch <- CH[i]; ev <- EXPO_VARS[i]
    sel_row <- sel_m[sel_m$channel == ch, ]
    cand_rows <- cand_m[cand_m$channel == ch, ]
    spend <- sel_row$total_spend

    theta <- sel_hyp[[paste0(ev, "_thetas")]]
    alpha <- sel_hyp[[paste0(ev, "_alphas")]]
    gamma <- sel_hyp[[paste0(ev, "_gammas")]]
    coef <- sel_row$coef
    expo <- dt[[ev]]

    inc_at <- function(m) channel_curve(expo, win_idx, theta, alpha, gamma, coef, m)

    # Self-check: reconstruction at m=1 must reproduce Robyn's own decomp.
    rebuilt <- inc_at(1)
    ref <- sel_row$xDecompAgg
    if (ref > 0 && abs(rebuilt - ref) / ref > 0.01) {
      stop(sprintf(
        "curve reconstruction mismatch for %s: rebuilt %.1f vs xDecompAgg %.1f",
        ch, rebuilt, ref
      ))
    }

    curve <- vapply(MULTIPLIERS, function(m) if (m == 0) 0 else inc_at(m), numeric(1))
    mroi <- (inc_at(1.01) - rebuilt) / (0.01 * spend)

    channels_out[[ch]] <- list(
      roi = list(
        point = sel_row$roi_total,
        interval_low = min(cand_rows$roi_total),
        interval_high = max(cand_rows$roi_total),
        interval_kind = "candidate_range"
      ),
      mroi = list(point = mroi),
      contribution_share = list(
        point = sel_row$xDecompAgg / total_revenue,
        interval_low = min(cand_rows$xDecompAgg) / total_revenue,
        interval_high = max(cand_rows$xDecompAgg) / total_revenue,
        interval_kind = "candidate_range"
      ),
      response_curve = list(
        multipliers = MULTIPLIERS,
        incremental_revenue = curve,
        kind = "selected_model"
      )
    )
  }

  result <- list(
    schema_version = "1.0",
    tool = "robyn",
    tool_version = as.character(packageVersion("Robyn")),
    arm = "national",
    seed_dataset = seed,
    run = list(
      tool_seed = robyn_seed,
      runtime_seconds = round(runtime, 1),
      hardware = HARDWARE,
      converged = converged,
      convergence_detail = list(
        conv_msg = conv_msgs,
        iterations = ITERATIONS,
        trials = TRIALS,
        ts_validation = TRUE,
        cores = CORES
      )
    ),
    channels = channels_out,
    extras = list(
      selected_model = selected,
      candidates = candidates,
      selection_path = selection_path,
      n_pareto_models = nrow(rhp),
      outputs_clustering_seconds = round(outputs_seconds, 1),
      candidate_roi_table = cand_m[, c("solID", "channel", "roi_total")]
    )
  )

  res_dir <- file.path(REPO, "runs", "robyn", "results")
  dir.create(res_dir, recursive = TRUE, showWarnings = FALSE)
  out_json <- file.path(res_dir, sprintf("robyn_national_seed%d.json", seed))
  write_json(result, out_json, auto_unbox = TRUE, digits = 10, pretty = TRUE)
  cat(sprintf("    wrote %s\n", out_json))
}

for (s in seeds) run_one(s)
cat("ROBYN RUNS DONE\n")
