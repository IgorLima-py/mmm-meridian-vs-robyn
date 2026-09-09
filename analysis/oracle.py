"""Oracle models — is the truth recoverable from this dataset at all?

Both tools missed the true ROIs by roughly half, in the same direction. That is
also what a bug in our ground truth, export or scorer would look like. This
module settles which it is, by fitting models that KNOW things no real tool
knows and scoring them with the same pre-registered harness.

Four rungs, each removing one advantage:

  L1  oracle_geo_truebase       geo-level regressors built with the true
                                adstock/Hill parameters, true baseline and
                                control subtracted from revenue. Only the five
                                betas are free.
                                -> validates ground truth + schema + scorer.
                                   If L1 fails, the fault is ours.

  L2  oracle_nat_truebase       same, but regressors are rebuilt from the
                                NATIONAL aggregate exposure (adstock and Hill
                                applied after summing geos), true baseline
                                still known.
                                -> isolates the aggregation (Jensen) gap that
                                   any national-arm tool pays.

  L3  oracle_nat_estbase        national regressors, baseline ESTIMATED the way
                                a competent practitioner specifies it:
                                intercept + linear trend + 3 annual Fourier
                                harmonics + the observed control.
                                -> the ceiling for any national tool that knew
                                   adstock and saturation perfectly.

  L4  oracle_geo_estbase        geo regressors, per-geo intercepts + shared
                                trend/Fourier + control estimated.
                                -> the same ceiling for the geo arm.

Every rung uses ordinary least squares, unconstrained (a negative beta is
information, not something to hide). Exports the standard results schema so
`scoring.py` consumes them unchanged.

Usage (from the repo root):
    python analysis/oracle.py                       # all seeds -> runs/oracle/results/
    python analysis/oracle.py --seeds 101 --out /tmp/x
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from simulation.config import CONFIG, SEEDS          # noqa: E402
from simulation.core import World, adstock_geometric, hill   # noqa: E402

SCHEMA_VERSION = "1.0"
ORACLE_VERSION = "1.0.0"
N_FOURIER = 3            # annual harmonics in the estimated-baseline rungs
CI_Z = 1.6448536269514722                     # 90% two-sided normal quantile


# ---------------------------------------------------------------------------
# Regressor construction


def geo_unit_response(world, ch, mult=1.0):
    """(G, T_window) channel response before beta — the generator's own."""
    return world._unit_response(ch, mult)[:, world.win]


def national_unit_response(world, ch, mult=1.0):
    """(T_window,) response rebuilt from NATIONAL aggregate exposure.

    A national-arm tool never sees the geo split, so it can only apply adstock
    and Hill to the summed exposure. Because Hill is non-linear, this is not
    the sum of the geo-level responses — the difference is the aggregation gap
    L2 measures.
    """
    spec = world.cfg["channels"][ch]
    pop_tot = world.pop.sum()
    x_pc = world.imp[ch].sum(axis=0) * mult / pop_tot
    ad = adstock_geometric(x_pc, spec["adstock_alpha"],
                           world.cfg["adstock_max_lag"])
    u = ad / world.ref[ch]
    return (pop_tot * hill(u, spec["hill_k"], spec["hill_s"]))[world.win]


def baseline_design(n_weeks, control, geo_dummies=None):
    """Practitioner-style baseline: intercept(s) + linear trend + Fourier + control.

    `control` is the observed control series (already stacked to match rows).
    `geo_dummies` (G, ) group labels turn the single intercept into per-geo
    intercepts, stacked geo-major to match the regressor stacking.
    """
    t = np.arange(n_weeks)
    cols = [np.ones(n_weeks), t / n_weeks]
    for h in range(1, N_FOURIER + 1):
        cols.append(np.sin(2 * np.pi * h * t / 52.18))
        cols.append(np.cos(2 * np.pi * h * t / 52.18))
    base = np.column_stack(cols)                      # (T, 2 + 2*H)

    if geo_dummies is None:
        return np.column_stack([base, control])

    n_geos = geo_dummies
    # geo-major stacking: rows = [geo0 weeks..., geo1 weeks..., ...]
    shared = np.tile(base[:, 1:], (n_geos, 1))        # trend + Fourier shared
    inter = np.zeros((n_geos * n_weeks, n_geos))
    for g in range(n_geos):
        inter[g * n_weeks:(g + 1) * n_weeks, g] = 1.0
    return np.column_stack([inter, shared, control])


# ---------------------------------------------------------------------------
# Fitting


def fit_ols(y, X):
    """Unconstrained OLS. Returns (coef, se, sigma2, dof)."""
    coef, _, rank, _ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ coef
    dof = max(len(y) - rank, 1)
    sigma2 = float(resid @ resid) / dof
    xtx_inv = np.linalg.pinv(X.T @ X)
    se = np.sqrt(np.maximum(np.diag(xtx_inv) * sigma2, 0.0))
    return coef, se, sigma2, dof


def build_rung(world, rung):
    """Return (y, X, media_cols, unit_fn) for one rung.

    `media_cols` indexes the media columns inside X; `unit_fn(ch, mult)` gives
    the window-total unit response used for ROI and response curves, in the
    same units the fitted beta multiplies.
    """
    cfg = world.cfg
    channels = list(cfg["channels"])
    W = world.W
    win = world.win

    if rung in ("L1", "L4"):                          # geo-level rows
        G = cfg["n_geos"]
        media = np.column_stack(
            [geo_unit_response(world, ch).reshape(-1) for ch in channels])
        y_full = world.revenue[:, win].reshape(-1)
        control = np.tile(world.draws["control_index"][win], G)

        def unit_fn(ch, mult=1.0):
            return float(geo_unit_response(world, ch, mult).sum())

        if rung == "L1":
            y = (y_full
                 - world.baseline[:, win].reshape(-1)
                 - world.control_effect[:, win].reshape(-1))
            X = media
            return y, X, list(range(len(channels))), unit_fn
        X = np.column_stack([media, baseline_design(W, control, geo_dummies=G)])
        return y_full, X, list(range(len(channels))), unit_fn

    # national rows
    media = np.column_stack(
        [national_unit_response(world, ch) for ch in channels])
    y_full = world.revenue[:, win].sum(axis=0)
    control = world.draws["control_index"][win]

    def unit_fn(ch, mult=1.0):
        return float(national_unit_response(world, ch, mult).sum())

    if rung == "L2":
        y = (y_full
             - world.baseline[:, win].sum(axis=0)
             - world.control_effect[:, win].sum(axis=0))
        X = media
        return y, X, list(range(len(channels))), unit_fn
    if rung == "L3":
        X = np.column_stack([media, baseline_design(W, control)])
        return y_full, X, list(range(len(channels))), unit_fn
    raise ValueError(rung)


RUNGS = {
    "L1": ("oracle_geo_truebase", "geo",
           "geo regressors, true baseline and control removed"),
    "L2": ("oracle_nat_truebase", "national",
           "national aggregate regressors, true baseline and control removed"),
    "L3": ("oracle_nat_estbase", "national",
           "national aggregate regressors, baseline estimated "
           "(intercept + trend + 3 Fourier harmonics + control)"),
    "L4": ("oracle_geo_estbase", "geo",
           "geo regressors, baseline estimated "
           "(per-geo intercepts + trend + 3 Fourier harmonics + control)"),
}


def run_rung(world, rung, gt):
    tool, arm, note = RUNGS[rung]
    cfg = world.cfg
    channels = list(cfg["channels"])
    y, X, media_cols, unit_fn = build_rung(world, rung)
    coef, se, _, _ = fit_ols(y, X)

    resid = y - X @ coef
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - float(resid @ resid) / ss_tot if ss_tot > 0 else float("nan")

    out_channels = {}
    beta_rel_err = {}
    for i, ch in enumerate(channels):
        b, b_se = float(coef[media_cols[i]]), float(se[media_cols[i]])
        spend = gt["channels"][ch]["spend_total"]
        unit1 = unit_fn(ch, 1.0)
        inc = b * unit1
        lo, hi = (b - CI_Z * b_se) * unit1, (b + CI_Z * b_se) * unit1
        delta = cfg["mroi_delta"]
        inc_up = b * unit_fn(ch, 1.0 + delta)
        curve_m = cfg["response_curve_multipliers"]
        out_channels[ch] = {
            "roi": {"point": inc / spend,
                    "interval_low": lo / spend,
                    "interval_high": hi / spend,
                    "interval_kind": "ols_ci90"},
            "mroi": {"point": (inc_up - inc) / (delta * spend)},
            "contribution_share": {"point": inc / gt["total_revenue"]},
            "response_curve": {
                "multipliers": curve_m,
                "incremental_revenue": [b * unit_fn(ch, m) for m in curve_m],
                "kind": "selected_model"},
        }
        b_true = gt["channels"][ch]["params"]["beta_per_capita"]
        beta_rel_err[ch] = (b - b_true) / b_true

    return {
        "schema_version": SCHEMA_VERSION,
        "tool": tool,
        "tool_version": ORACLE_VERSION,
        "arm": arm,
        "seed_dataset": world.seed,
        "run": {
            "tool_seed": 0,
            "runtime_seconds": 0.0,
            "hardware": "OLS, any CPU",
            "converged": True,
            "convergence_detail": {"method": "closed-form OLS", "r2": r2},
        },
        "channels": out_channels,
        "extras": {
            "rung": rung,
            "what_the_oracle_knows": note,
            "n_rows": int(len(y)),
            "n_params": int(X.shape[1]),
            "r2": r2,
            "beta_rel_err": beta_rel_err,
            "note": ("Diagnostic, not a competing estimator: these models are "
                     "handed the true adstock and saturation parameters and "
                     "(L1/L2) the true baseline. They bound what is knowable "
                     "from this dataset; they are not a tool anyone can run."),
        },
    }


def diagnostics(seeds, data_root):
    """Every scenario number ORACLE.md quotes, derived here rather than by hand.

    Four blocks: the noiseless-recovery check that validates the harness, the
    per-channel visibility table, and the two correlation views (raw geo, which
    is inflated by the shared population factor, and time-demeaned, which is
    not).
    """
    channels = list(CONFIG["channels"])
    noiseless, vis, raw_c, dem_c = [], [], [], []

    for seed in seeds:
        world = World(seed, CONFIG)
        with open(Path(data_root) / f"seed{seed}" / "ground_truth.json") as f:
            gt = json.load(f)

        # 1. Noiseless recovery: y = M @ beta_true exactly. OLS must return it.
        M = np.column_stack(
            [geo_unit_response(world, ch).reshape(-1) for ch in channels])
        beta = np.array([world.beta_pc[ch] for ch in channels])
        coef, _, _, _ = fit_ols(M @ beta, M)
        noiseless.append(np.abs((coef - beta) / beta).max())

        # 2. Per-channel visibility.
        nat_noise = world.noise[:, world.win].sum(0)
        for ch in channels:
            n = national_unit_response(world, ch)
            contrib = world.beta_pc[ch] * n
            vis.append({
                "channel": ch,
                "true_roi": gt["channels"][ch]["true_roi"],
                "contribution_share": gt["channels"][ch][
                    "true_contribution_share"],
                "regressor_cv": float(n.std() / n.mean()),
                "signal_to_noise": float(contrib.std() / nat_noise.std()),
            })

        # 3. Correlation of the geo regressors, raw and time-demeaned.
        M3 = np.stack([geo_unit_response(world, ch) for ch in channels])
        iu = np.triu_indices(len(channels), 1)
        raw_c.append(np.corrcoef(M3.reshape(len(channels), -1))[iu])
        dem = M3 - M3.mean(axis=2, keepdims=True)
        dem_c.append(np.corrcoef(dem.reshape(len(channels), -1))[iu])

    print("== harness check: noiseless geo recovery ==")
    print(f"  max |beta rel err| over {len(seeds)} seed(s): "
          f"{max(noiseless):.2e}  (machine precision => harness sound)\n")

    print("== per-channel visibility (mean over seeds) ==")
    v = (pd.DataFrame(vis).groupby("channel").mean(numeric_only=True)
         .sort_values("signal_to_noise", ascending=False))
    print(v.round(4).to_string(), "\n")

    pairs = [f"{channels[i]}-{channels[j]}"
             for i, j in zip(*np.triu_indices(len(channels), 1))]
    for label, arr in (("raw geo", raw_c), ("time-demeaned", dem_c)):
        m = np.array(arr).mean(axis=0)
        lo, hi = pairs[int(m.argmin())], pairs[int(m.argmax())]
        print(f"== cross-channel correlation, {label} (pair means over seeds) ==")
        print(f"  range {m.min():.3f} ({lo}) .. {m.max():.3f} ({hi})")
        print("  " + "  ".join(f"{p}={x:.3f}" for p, x in zip(pairs, m)) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=SEEDS)
    ap.add_argument("--data", default="data/sim")
    ap.add_argument("--out", default="runs/oracle/results")
    ap.add_argument("--rungs", nargs="*", default=list(RUNGS))
    ap.add_argument("--diagnostics", action="store_true",
                    help="print the scenario diagnostics ORACLE.md cites, "
                         "instead of fitting and exporting the rungs")
    args = ap.parse_args()

    if args.diagnostics:
        diagnostics(args.seeds, args.data)
        return

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    report = []

    for seed in args.seeds:
        gt_path = Path(args.data) / f"seed{seed}" / "ground_truth.json"
        with open(gt_path) as f:
            gt = json.load(f)
        world = World(seed, CONFIG)

        # Contract check: the World we just rebuilt must be the committed data.
        nat = pd.read_csv(Path(args.data) / f"seed{seed}" / "national.csv")
        rebuilt = world.revenue[:, world.win].sum(axis=0)
        drift = float(np.max(np.abs(nat["revenue"].to_numpy() - rebuilt)))
        rel = drift / float(np.mean(rebuilt))
        if rel > 1e-6:
            sys.exit(f"seed {seed}: rebuilt revenue differs from national.csv "
                     f"(max abs {drift:.4f}, rel {rel:.2e}) — regenerate first")

        for rung in args.rungs:
            res = run_rung(world, rung, gt)
            name = f"{res['tool']}_{res['arm']}_seed{seed}.json"
            with open(out / name, "w") as f:
                json.dump(res, f, indent=1)
            errs = res["extras"]["beta_rel_err"]
            report.append({
                "seed": seed, "rung": rung, "tool": res["tool"],
                "r2": res["extras"]["r2"],
                "beta_abs_rel_err_mean": float(
                    np.mean([abs(v) for v in errs.values()])),
                "beta_abs_rel_err_max": float(
                    np.max([abs(v) for v in errs.values()])),
            })

    df = pd.DataFrame(report)
    print(df.groupby(["rung", "tool"])
            .agg(r2=("r2", "mean"),
                 beta_err_mean=("beta_abs_rel_err_mean", "mean"),
                 beta_err_max=("beta_abs_rel_err_max", "max"))
            .round(4).to_string())
    print(f"\nwrote {len(report)} result JSON(s) to {out}")


if __name__ == "__main__":
    main()
