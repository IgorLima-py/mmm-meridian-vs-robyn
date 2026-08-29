# Environments (PLAN Phase 1)

Everything below runs on the GPU desktop inside **WSL2 Ubuntu** (decision D1).
The setup is fully scripted and idempotent — a fresh machine reproduces it with:

```bash
# from an elevated Windows shell (once): wsl --install  → reboot → wsl --install -d Ubuntu --no-launch
sudo bash envs/apt_base.sh
bash envs/setup_meridian.sh
bash envs/setup_robyn.sh
```

## Host

| Component | Version / value |
|---|---|
| Windows | Windows 11 Pro 10.0.26200 |
| GPU | NVIDIA GeForce RTX 4070 SUPER, 12 GB VRAM |
| NVIDIA Windows driver | 610.88 (CUDA UMD 13.3) — CUDA inside WSL comes from pip `[and-cuda]` wheels, no toolkit install |
| CPU / RAM | AMD Ryzen 5 5600G (6c/12t), 32 GB host RAM |
| WSL | 2.7.12, kernel 6.18.33.2-microsoft-standard-WSL2 |
| Ubuntu distro | Ubuntu 26.04 LTS |
| WSL resources | defaults: 15 GB RAM visible, all 12 threads, 4 GB swap (raise via `.wslconfig` only if a run hits the ceiling) |

## Meridian env

- Ubuntu 26.04's system Python is newer than Meridian 1.8.0 supports, so Python
  **3.12** comes from `uv`'s pinned standalone builds (`envs/setup_meridian.sh`).
- venv: `~/venvs/meridian`; install: `google-meridian[and-cuda]==1.8.0`
  (hard-pins TF 2.21.x + a tfp-nightly build — documented oddity, D2).
- Exact package versions: `envs/meridian.lock.txt` (written by the setup script).
- Smoke tests: `envs/smoke_meridian_gpu.py` (TF sees GPU + import), then a tiny
  sampling run on Meridian sample data (stage 2, wall-clock recorded below).

## Robyn env

- R from Ubuntu 26.04 repos (≥ 4.2 required — actual version in the lock section
  below); Robyn 3.12.1 from CRAN into `~/R/library`.
- nevergrad in a dedicated Python **3.10** uv venv (`~/venvs/nevergrad`),
  pinned via `RETICULATE_PYTHON` in `~/.Renviron` (`envs/setup_robyn.sh`).
- Exact pip versions: `envs/nevergrad.lock.txt`.
- Smoke test: `dt_simulated_weekly`, ~200 iterations × 1 trial, must print
  "Using X cores" with X > 1 (the whole point of WSL over native Windows).

## Friction log (feeds M7)

| # | What happened | Cost |
|---|---|---|
| F1 | `shutdown /fw`-style WSL install needed **SVM enabled in BIOS** — virtualization was off from the factory; required a reboot into UEFI setup mid-install (`HCS_E_HYPERV_NOT_INSTALLED`) | ~20 min + physical access |
| F2 | The pre-reboot `wsl --install` claimed success for WSL itself but the Ubuntu distro registration silently failed; had to re-run `wsl --install -d Ubuntu --no-launch` after the reboot | ~5 min |
| F3 | Ubuntu 26.04's system Python is too new for Meridian 1.8.0 → uv-managed Python 3.12/3.10 instead of apt Python | design change, ~10 min |
| F4 | (Windows-native path not attempted — Meridian officially unsupported there; that fact is itself an M7 data point for the article) | — |
| F5 | TF 2.21.0's Linux wheel ships **no RUNPATH to the pip `nvidia/*/lib` dirs**, so `tensorflow[and-cuda]`-style installs see zero GPUs out of the box. Fixed by a `sitecustomize.py` that preloads the CUDA libs with `RTLD_GLOBAL` (written by `setup_meridian.sh`) | ~40 min diagnosis |
| F6 | Robyn's CRAN dependency tree (~90 pkgs) compiles from source on Linux and died twice on missing system libs: `fs` needs libuv headers, `RcppParallel`/`nloptr` need cmake. Added `cmake libuv1-dev libnlopt-dev` to `apt_base.sh`. Total compile time is tens of minutes even on 12 threads | ~2 restarts + long compile |
| F7 | When `paid_media_vars` carries exposure metrics, Robyn names hyperparameters after the **exposure** variables (`facebook_I_alphas`, `search_clicks_P_thetas`), not the spend columns most docs show. Passing spend-named bounds fails deep in `hyper_collector` with a cryptic `names ... must be the same length as the vector` error | ~15 min |
| F8 | `robyn_run(quiet = TRUE)` crashes in Robyn 3.12.1 (`object 'pb' not found`): the progress bar is only created when not quiet, but `close(pb)` runs unconditionally. Workaround: never pass `quiet` | one lost 2k×5 run |

## Versions actually installed

| Component | Version |
|---|---|
| uv-managed Pythons | 3.12.14 (Meridian), 3.10.21 (nevergrad) |
| google-meridian | 1.8.0 |
| tensorflow | 2.21.0 (XLA on CUDA; runtime 12.9.0, toolkit 12.5.0, cuDNN 9.24.0 — all from pip wheels) |
| full Meridian venv | `envs/meridian.lock.txt` |
| nevergrad | 1.0.12 (`envs/nevergrad.lock.txt`) |
| R | 4.5.2 (Ubuntu 26.04 repo) |
| Robyn | 3.12.1 (CRAN) |

Smoke-test wall-clocks (setup validation, not benchmarks):

- Meridian stage 1 (`smoke_meridian_gpu.py`): TF import + GPU matmul + meridian
  import in **9.9 s**; TF allocates 9 513 MB of the 12 GB VRAM.
- Meridian stage 2 (`smoke_meridian_model.py`): sample data (10 geos × 50 weeks
  × 3 channels), `sample_prior(5)` 1.0 s; `sample_posterior` 2 chains ×
  (100 adapt / 50 burn-in / 100 keep) **151 s** — dominated by one-off XLA
  compilation, so tiny runs understate GPU throughput.
- Robyn (`smoke_robyn.R`): `dt_simulated_weekly`, 200 iterations × 1 trial:
  `robyn_run` **26 s** on **11 cores** (multi-core confirmed — the reason for
  WSL2 over native Windows). Non-convergence at 200 iterations is expected.
