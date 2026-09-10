"""Sanity checks on generated datasets (PLAN Phase 2 gate).

Usage (from the repo root, after generation):
    python -m simulation.checks                  # all seeds in config.SEEDS
    python -m simulation.checks --seeds 101

Checks per seed (FAIL = exit code 1; WARN = printed only):
  C1 identifiability: hill_k inside [p05, p90] of the realized adstock-
     normalized exposure u, and p90(u) > hill_k (saturation exercised).
  C2 correlation dial: national weekly spend corr — tv-ooh in [0.30, 0.65];
     every other pair |r| < 0.35.
  C3 variance decomposition: media_total share in [0.10, 0.35]
     (WARN if outside [0.15, 0.30]).
  C4 positivity: min weekly geo revenue > 0.
  C5 ROI calibration: counterfactual true ROI == config target (1e-6).
  C6 determinism: regenerating the seed reproduces byte-identical CSVs.
  C7 recoverability gate: per-channel signal-to-noise (std of the channel's
     true national contribution / std of national revenue noise, window
     weeks). WARN only, floor 0.15 — this does not fail the pipeline. It is
     the check `analysis/ORACLE.md` shows was missing before the v1 tool
     runs: the total media-variance check (C3) hid two channels (ooh,
     display) with almost no recoverable signal, later confirmed
     unrecoverable by the oracle. Run `analysis/oracle.py` for the ground
     truth this floor only approximates cheaply.
"""

import argparse
import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from .config import CONFIG, SEEDS
from .core import World
from .generate import frames

# C7 floor: below this, `analysis/ORACLE.md` found the oracle itself cannot
# recover the channel (ooh, display in v1) — WARN, not a scenario defect.
SNR_FLOOR = 0.15


def _hash(df):
    return hashlib.sha256(
        df.to_csv(index=False).encode("utf-8")).hexdigest()


def channel_snr(world):
    """C7 signal-to-noise per channel: std of the channel's true national
    contribution over std of national revenue noise, measurement window.

    Single source of truth — `analysis/figures.py` orders channels by it,
    so the charts and this gate can never disagree.
    """
    win = world.win
    noise_sd = world.noise[:, win].sum(0).std()
    return {ch: world.media[ch][:, win].sum(0).std() / noise_sd
            for ch in world.cfg["channels"]}


def check_seed(seed, data_root):
    world = World(seed)
    cfg = world.cfg
    win = world.win
    failures, warnings = [], []

    # C1 identifiability
    for ch, spec in cfg["channels"].items():
        u = world.adstocked_norm_exposure(ch)[:, win].ravel()
        p05, p90 = np.percentile(u, [5, 90])
        k = spec["hill_k"]
        if not (p05 <= k <= p90):
            failures.append(
                f"C1 {ch}: hill_k={k} outside u [p05={p05:.2f}, p90={p90:.2f}]")
        print(f"  C1 {ch}: u p05={p05:.2f} p50={np.percentile(u, 50):.2f} "
              f"p90={p90:.2f} | k={k}")

    # C2 spend correlations (national, window)
    nat = {ch: world.geo_spend[ch][:, win].sum(0) for ch in cfg["channels"]}
    names = list(nat)
    corr = np.corrcoef(np.array([nat[ch] for ch in names]))
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            r = corr[i, j]
            pair = f"{names[i]}-{names[j]}"
            if pair == "tv-ooh":
                if not (0.30 <= r <= 0.65):
                    failures.append(f"C2 {pair}: r={r:.2f} not in [0.30,0.65]")
                print(f"  C2 {pair}: r={r:.2f} (target 0.30-0.65)")
            elif abs(r) >= 0.35:
                failures.append(f"C2 {pair}: |r|={abs(r):.2f} >= 0.35")

    # C3 variance decomposition
    vd = world._variance_decomposition()
    ms = vd["media_total"]
    print(f"  C3 media_total var share = {ms:.2f} "
          f"(baseline {vd['baseline']:.2f}, control {vd['control']:.2f}, "
          f"noise {vd['noise']:.2f})")
    if not (0.10 <= ms <= 0.35):
        failures.append(f"C3 media var share {ms:.2f} outside [0.10, 0.35]")
    elif not (0.15 <= ms <= 0.30):
        warnings.append(f"C3 media var share {ms:.2f} outside ideal [0.15,0.30]")

    # C4 positivity
    rev_min = world.revenue[:, win].min()
    if rev_min <= 0:
        failures.append(f"C4 min revenue {rev_min:.1f} <= 0")

    # C5 ROI calibration
    for ch, spec in cfg["channels"].items():
        roi = (world.incremental_revenue(ch, 1.0)
               / world.geo_spend[ch][:, win].sum())
        if abs(roi - spec["true_roi"]) > 1e-6:
            failures.append(f"C5 {ch}: roi {roi} != target {spec['true_roi']}")

    # C7 per-channel signal-to-noise (recoverability gate; WARN only)
    for ch, snr in channel_snr(world).items():
        print(f"  C7 {ch}: signal-to-noise = {snr:.2f} (floor {SNR_FLOOR})")
        if snr < SNR_FLOOR:
            warnings.append(
                f"C7 {ch}: signal-to-noise {snr:.2f} below floor "
                f"{SNR_FLOOR} — see analysis/ORACLE.md")

    # C6 determinism vs files on disk
    seed_dir = Path(data_root) / f"seed{seed}"
    if seed_dir.exists():
        geo, nat_df, robyn = frames(world)
        for name, df in [("geo.csv", geo), ("national.csv", nat_df),
                         ("robyn.csv", robyn)]:
            on_disk = pd.read_csv(seed_dir / name, dtype=str)
            regen = pd.read_csv(
                __import__("io").StringIO(df.to_csv(index=False)), dtype=str)
            if not on_disk.equals(regen):
                failures.append(f"C6 {name}: regeneration differs from disk")
    else:
        warnings.append(f"C6 skipped: {seed_dir} not found (generate first)")

    return failures, warnings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=SEEDS)
    ap.add_argument("--data", default="data/sim")
    args = ap.parse_args()
    any_fail = False
    for seed in args.seeds:
        print(f"seed {seed}:")
        failures, warnings = check_seed(seed, args.data)
        for w in warnings:
            print(f"  WARN {w}")
        for f in failures:
            print(f"  FAIL {f}")
        if not failures:
            print("  OK")
        any_fail |= bool(failures)
    sys.exit(1 if any_fail else 0)


if __name__ == "__main__":
    main()
