#!/usr/bin/env bash
# Idempotent Robyn environment setup (PLAN Phase 1, decision D1/D2).
# Host: WSL2 Ubuntu. R comes from the Ubuntu repos (>= 4.2 satisfied);
# nevergrad lives in a dedicated Python 3.10 venv pinned via RETICULATE_PYTHON.
# Run as the regular user: bash envs/setup_robyn.sh
set -euo pipefail

LOCK_DIR="$(cd "$(dirname "$0")" && pwd)"
NG_VENV="$HOME/venvs/nevergrad"

sudo DEBIAN_FRONTEND=noninteractive apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq r-base r-base-dev

export PATH="$HOME/.local/bin:$PATH"
uv python install 3.10
[ -d "$NG_VENV" ] || uv venv --python 3.10 "$NG_VENV"
uv pip install --python "$NG_VENV/bin/python" nevergrad
uv pip freeze --python "$NG_VENV/bin/python" > "$LOCK_DIR/nevergrad.lock.txt"

touch "$HOME/.Renviron"
grep -q '^RETICULATE_PYTHON=' "$HOME/.Renviron" || \
  echo "RETICULATE_PYTHON=$NG_VENV/bin/python" >> "$HOME/.Renviron"
mkdir -p "$HOME/R/library"
grep -q '^R_LIBS_USER=' "$HOME/.Renviron" || \
  echo "R_LIBS_USER=$HOME/R/library" >> "$HOME/.Renviron"

Rscript -e 'if (!requireNamespace("Robyn", quietly = TRUE)) install.packages("Robyn", repos = "https://cloud.r-project.org")'
Rscript -e 'cat("Robyn", as.character(packageVersion("Robyn")), "on R", R.version.string, "\n")'
echo "robyn env ready"
