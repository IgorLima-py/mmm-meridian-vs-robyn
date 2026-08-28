#!/usr/bin/env bash
# Idempotent Meridian environment setup (PLAN Phase 1, decision D1/D2).
# Host: WSL2 Ubuntu. Ubuntu 26.04 ships a Python newer than Meridian supports,
# so Python 3.12 comes from uv's standalone builds (pinned, reproducible).
# Run as the regular user: bash envs/setup_meridian.sh
set -euo pipefail

VENV="$HOME/venvs/meridian"
LOCK_DIR="$(cd "$(dirname "$0")" && pwd)"

if ! command -v uv >/dev/null 2>&1 && [ ! -x "$HOME/.local/bin/uv" ]; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="$HOME/.local/bin:$PATH"

uv python install 3.12
[ -d "$VENV" ] || uv venv --python 3.12 "$VENV"

# [and-cuda] pulls TF 2.21.x + tfp-nightly + CUDA wheels (documented oddity, D2)
uv pip install --python "$VENV/bin/python" "google-meridian[and-cuda]==1.8.0"

# TF 2.21's wheel has no RUNPATH to the pip nvidia/*/lib dirs, so the GPU is
# invisible unless the CUDA libs are already loaded. Preload them at interpreter
# startup; keeps a plain `~/venvs/meridian/bin/python` GPU-capable, no wrapper.
SC="$VENV/lib/python3.12/site-packages/sitecustomize.py"
cat > "$SC" <<'PYEOF'
"""Preload pip-installed NVIDIA CUDA libraries (written by envs/setup_meridian.sh)."""
import ctypes, glob, os

_here = os.path.dirname(__file__)
for _lib in sorted(glob.glob(os.path.join(_here, "nvidia", "*", "lib", "lib*.so*"))):
    try:
        ctypes.CDLL(_lib, mode=ctypes.RTLD_GLOBAL)
    except OSError:
        pass
PYEOF

uv pip freeze --python "$VENV/bin/python" > "$LOCK_DIR/meridian.lock.txt"
echo "meridian venv ready: $VENV"
