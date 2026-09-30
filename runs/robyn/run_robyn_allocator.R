# Robyn's own budget allocator over the models saved by run_robyn.R (C12).
#
# No refit: robyn_allocator() runs on the saved OutputCollect of the selected
# model (extras.selected_model in the committed result JSON). The InputCollect
# is not saved by run_robyn.R, so it is rebuilt with the same robyn_inputs()
# call; that step is deterministic (no sampling), and the script checks the
# rebuilt inputs against the saved model before using them.
#
# Limits are analysis/regret.py BOUNDS["primary"] = (0.5, 2.0), which are also
# Robyn 3.12.1's own defaults for scenario "max_response" (read from the
# installed source, 2026-09-29). Budget = the observed window total
# (total_budget = NULL). Output: one allocation JSON per seed in the schema of
# analysis/RESULTS_SCHEMA.md ("Allocation files").
#
# Run inside the WSL2 env, from the repo root (see envs/ENVIRONMENT.md):
#   Rscript runs/robyn/run_robyn_allocator.R 101 102 103 104 105
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
BOUNDS_NAME <- "primary"
BOUNDS_LO <- 0.5   # regret.BOUNDS["primary"]
BOUNDS_HI <- 2.0
HARDWARE <- sprintf("WSL2 Ubuntu 26.04, %d cores (Ryzen 5 5600G), R 4.5.2",
                    max(1L, parallel::detectCores() - 1L))

# Same hyperparameters as run_robyn.R (only the bounds matter for the rebuild;
# the fitted values come from OutputCollect).
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

run_one <- function(seed) {
  cat(sprintf("=== robyn allocator seed%d ===\n", seed))
  dt <- read.csv(file.path(REPO, "data", "sim", sprintf("seed%d", seed), "robyn.csv"))
  dt$DATE <- as.Date(dt$DATE)
  res_json <- file.path(REPO, "runs", "robyn", "results",
                        sprintf("robyn_national_seed%d.json", seed))
  prev <- fromJSON(res_json, simplifyVector = FALSE)
  selected <- prev$extras$selected_model
  heavy_dir <- file.path(REPO, "outputs", "robyn", sprintf("seed%d", seed))
  OutputCollect <- readRDS(file.path(heavy_dir, "OutputCollect.rds"))
  # Iterations of the saved run, for the DECISIONS entry (2000x5 vs 4000x5).
  iterations <- prev$run$convergence_detail$iterations

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

  # The rebuilt inputs must be the ones the model was fitted on: the window
  # spend Robyn saved per channel (xDecompAgg.total_spend) must equal the
  # window spend of the rebuilt data.
  xda <- as.data.frame(OutputCollect$xDecompAgg)
  saved_spend <- vapply(EXPO_VARS, function(ev)
    xda$total_spend[xda$solID == selected & xda$rn == ev][1], numeric(1))
  win_idx <- InputCollect$rollingWindowStartWhich:InputCollect$rollingWindowEndWhich
  rebuilt_spend <- vapply(SPEND_VARS, function(sv) sum(dt[[sv]][win_idx]), numeric(1))
  if (any(abs(saved_spend - rebuilt_spend) > 1e-6 * rebuilt_spend)) {
    stop(sprintf("seed%d: rebuilt inputs do not match the saved model's window spend",
                 seed))
  }

  t0 <- Sys.time()
  AllocatorCollect <- robyn_allocator(
    InputCollect = InputCollect,
    OutputCollect = OutputCollect,
    select_model = selected,
    scenario = "max_response",
    channel_constr_low = BOUNDS_LO,
    channel_constr_up = BOUNDS_HI,
    date_range = "all",
    total_budget = NULL,
    plots = FALSE,
    export = FALSE
  )
  runtime <- as.numeric(difftime(Sys.time(), t0, units = "secs"))

  o <- as.data.frame(AllocatorCollect$dt_optimOut)
  # Multiplier on the channel's whole window series = optimised / initial
  # average spend per period (the same period count on both sides).
  channels_out <- list()
  raw <- list()
  for (i in seq_along(CH)) {
    # dt_optimOut names channels after the exposure variables (friction F7),
    # its spend columns still hold money.
    row <- o[o$channels == EXPO_VARS[i], ]
    if (nrow(row) != 1) {
      stop(sprintf("allocator returned no row for %s (has: %s)", EXPO_VARS[i],
                   paste(o$channels, collapse = ", ")))
    }
    mult <- row$optmSpendUnit / row$initSpendUnit
    channels_out[[CH[i]]] <- list(multiplier = mult)
    raw[[CH[i]]] <- list(
      init_spend_unit = row$initSpendUnit, optm_spend_unit = row$optmSpendUnit,
      init_response_unit = row$initResponseUnit, optm_response_unit = row$optmResponseUnit
    )
  }
  init_total <- sum(o$initSpendUnit)
  optm_total <- sum(o$optmSpendUnit)

  result <- list(
    schema_version = "1.0",
    kind = "allocation",
    tool = "robyn",
    tool_version = as.character(packageVersion("Robyn")),
    arm = "national",
    seed_dataset = seed,
    bounds = BOUNDS_NAME,
    run = list(
      tool_seed = prev$run$tool_seed,
      runtime_seconds = round(runtime, 1),
      hardware = HARDWARE,
      converged = prev$run$converged,
      convergence_detail = list(
        fitted_run_iterations = iterations,
        fitted_run_trials = prev$run$convergence_detail$trials,
        allocator_optim_algo = "SLSQP_AUGLAG",
        allocator_maxeval = 1e5,
        allocator_constr_mode = "eq"
      )
    ),
    channels = channels_out,
    extras = list(
      selected_model = selected,
      scenario = "max_response",
      usecase = AllocatorCollect$usecase,
      budget_gap_relative = (optm_total - init_total) / init_total,
      per_channel = raw
    )
  )
  out_json <- file.path(REPO, "runs", "robyn", "results",
                        sprintf("robyn_national_allocation_seed%d.json", seed))
  write_json(result, out_json, auto_unbox = TRUE, digits = NA, pretty = TRUE)
  cat(sprintf("    wrote %s (budget gap %+.2e)\n", out_json,
              (optm_total - init_total) / init_total))
}

for (s in seeds) run_one(s)
cat("ROBYN ALLOCATOR DONE\n")
