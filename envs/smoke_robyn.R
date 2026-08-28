# Robyn smoke test (PLAN Phase 1 gate): dt_simulated_weekly, ~200 iterations x
# 1 trial. Must (a) bind nevergrad via RETICULATE_PYTHON and (b) engage multiple
# cores — the whole point of running Robyn under WSL2 instead of native Windows.
# Run: Rscript envs/smoke_robyn.R
library(Robyn)

cat("Robyn", as.character(packageVersion("Robyn")), "on", R.version.string, "\n")
cat("cores visible:", parallel::detectCores(), "\n")

data("dt_simulated_weekly")
data("dt_prophet_holidays")

InputCollect <- robyn_inputs(
  dt_input = dt_simulated_weekly,
  dt_holidays = dt_prophet_holidays,
  date_var = "DATE",
  dep_var = "revenue",
  dep_var_type = "revenue",
  prophet_vars = c("trend", "season", "holiday"),
  prophet_country = "DE",
  context_vars = c("competitor_sales_B", "events"),
  paid_media_spends = c("tv_S", "ooh_S", "print_S", "facebook_S", "search_S"),
  paid_media_vars = c("tv_S", "ooh_S", "print_S", "facebook_I", "search_clicks_P"),
  organic_vars = "newsletter",
  window_start = "2016-01-01",
  window_end = "2018-12-31",
  adstock = "geometric"
)

# Standard demo.R bounds — this is a smoke test, not an experiment arm.
# NOTE (feeds Phase 4): with exposure metrics in paid_media_vars, Robyn names
# the hyperparameters after the EXPOSURE variables (facebook_I,
# search_clicks_P), not the spend columns.
hyperparameters <- list(
  facebook_I_alphas = c(0.5, 3), facebook_I_gammas = c(0.3, 1), facebook_I_thetas = c(0, 0.3),
  print_S_alphas = c(0.5, 3), print_S_gammas = c(0.3, 1), print_S_thetas = c(0.1, 0.4),
  tv_S_alphas = c(0.5, 3), tv_S_gammas = c(0.3, 1), tv_S_thetas = c(0.3, 0.8),
  search_clicks_P_alphas = c(0.5, 3), search_clicks_P_gammas = c(0.3, 1), search_clicks_P_thetas = c(0, 0.3),
  ooh_S_alphas = c(0.5, 3), ooh_S_gammas = c(0.3, 1), ooh_S_thetas = c(0.1, 0.4),
  newsletter_alphas = c(0.5, 3), newsletter_gammas = c(0.3, 1), newsletter_thetas = c(0.1, 0.4),
  train_size = c(0.5, 0.8)
)
InputCollect <- robyn_inputs(InputCollect = InputCollect, hyperparameters = hyperparameters)

t0 <- Sys.time()
OutputModels <- robyn_run(
  InputCollect = InputCollect,
  iterations = 200,
  trials = 1,
  ts_validation = TRUE,
  seed = 123
)
elapsed <- as.numeric(difftime(Sys.time(), t0, units = "secs"))

print(OutputModels)
cat(sprintf("robyn_run wall-clock: %.0fs\n", elapsed))
cat("smoke robyn OK\n")
