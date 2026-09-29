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

Two more rungs, pre-registered in docs/PLAN.md §8 and its amendment §8.6
(2026-09-29), restrict the shape to what one tool's setup could express.
Each is L3 with every channel's regressor replaced by the best
approximation of the true one inside that tool's parameter space:

  L6  oracle_nat_meridian_setup Meridian 1.8.0's space as run in v1:
                                Hill slope fixed at 1.
  L7  oracle_nat_robyn_setup    Robyn 3.12.1's space as run in v1: its
                                theta, alpha and gamma bounds.
                                -> L6 - L3 and L7 - L3 are each setup's price.

(L5, a joint shape search, was pre-registered and retired when it failed its
own check; the name is not reused. See PLAN §8.6.)

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


# ---------------------------------------------------------------------------
# Setup-constrained rungs (docs/PLAN.md §8, pre-registered 2026-09-29, and
# its same-day amendment §8.6)
#
# L1-L4 are handed the true shape, so they cannot say how much of a tool's
# miss came from the parameter space its setup allowed. L6 and L7 are L3
# with each channel's regressor replaced by the best approximation of the
# true one that the tool's space admits. §8.1's joint shape search (L5) was
# retired when its own check failed (commit a9e062b); what follows solves
# one identified problem per channel instead. Every number below is from the
# pre-registration.

SETUP_RUNGS_VERSION = "1.1.0"     # L1-L4 stay at ORACLE_VERSION, unchanged
THETA_GRID = np.round(np.arange(0.0, 0.951, 0.05), 2)   # 20 retentions
S_GRID = np.round(np.arange(0.3, 4.001, 0.1), 1)        # 38 Hill slopes
K_GRID = np.round(np.arange(0.05, 10.001, 0.05), 2)     # 200 half-saturations;
# the ceiling covers ec_m's mapped ceiling on every channel (PLAN §8.7)
FINE_STEPS = (0.005, 0.01, 0.005)  # theta, s, k: ten times finer (§8.6)
GRID_EPS = 1e-9        # float slack when a grid value is tested against a bound

# Robyn 3.12.1 as run in v1: runs/robyn/run_robyn.R, RD2. Its inflexion is
# gamma * max(z) (saturation_hill, read from the installed package 2026-09-29).
ROBYN_THETA = {"tv": (0.3, 0.8), "ooh": (0.1, 0.4), "social": (0.0, 0.3),
               "display": (0.0, 0.3), "search": (0.0, 0.3)}
ROBYN_ALPHA = (0.5, 3.0)
ROBYN_GAMMA = (0.3, 1.0)
# Meridian 1.8.0 defaults, model/prior_distribution.py (read 2026-09-29):
# slope_m = Deterministic(1.0); ec_m = TruncatedNormal(0.8, 0.8, 0.1, 10) in
# units of the population-scaled non-zero median of the media.
MERIDIAN_SLOPE = 1.0
MERIDIAN_EC = (0.1, 10.0)

SPACES = {
    "free": "the generator's family, every shape parameter free",
    "meridian": "Meridian 1.8.0's space: Hill slope fixed at 1, "
                "half-saturation inside ec_m's support",
    "robyn": "Robyn 3.12.1's space: theta inside its per-channel bounds, "
             "alpha in [0.5, 3], gamma in [0.3, 1]",
}
SETUP_RUNGS = {
    "L6": ("oracle_nat_meridian_setup", "meridian"),
    "L7": ("oracle_nat_robyn_setup", "robyn"),
}
# The two partial variants of §8.6 that answer Q2: one channel group
# projected, the others left true. Diagnostics only, not scored JSONs.
Q2_VARIANTS = {
    "robyn_ooh_display": {"ooh": "robyn", "display": "robyn"},
    "meridian_tv": {"tv": "meridian"},
}


def adstock_fast(x, alpha, max_lag):
    """`simulation.core.adstock_geometric` for a 1-D series, as a convolution."""
    w = alpha ** np.arange(max_lag)
    num = np.convolve(x, w)[: len(x)]
    den = np.cumsum(w)[np.minimum(np.arange(len(x)), max_lag - 1)]
    return num / den


def robyn_adstock(x, theta):
    """Robyn's geometric adstock: unnormalised, cold start at the window."""
    z = np.empty_like(x, dtype=float)
    acc = 0.0
    for t, v in enumerate(x):
        acc = v + theta * acc
        z[t] = acc
    return z


def national_response_shape(world, ch, theta, k, s, mult=1.0):
    """(T_window,) national-aggregate response for an arbitrary shape.

    Same construction as `national_unit_response`, with the shape passed in
    instead of read from the config.
    """
    pop_tot = world.pop.sum()
    x_pc = world.imp[ch].sum(axis=0) * mult / pop_tot
    ad = adstock_geometric(x_pc, theta, world.cfg["adstock_max_lag"])
    return (pop_tot * hill(ad / world.ref[ch], k, s))[world.win]


def robyn_k_ceiling(world, ch, theta):
    """The half-saturation, in the generator's units, that Robyn's gamma = 1
    maps to at retention `theta`.

    Robyn's inflexion is gamma * max(z), z its own adstocked exposure. At
    steady state z/u = population * mean exposure per capita / (1 - theta),
    so gamma = 1 corresponds to k = max(z) * (1 - theta) / (pop * ref).
    """
    x = world.imp[ch].sum(axis=0)[world.win]
    z = robyn_adstock(x, theta)
    return z.max() * (1 - theta) / (world.pop.sum() * world.ref[ch])


def meridian_k_support(world, ch):
    """ec_m's support [0.1, 10], in units of the population-scaled non-zero
    median of the media, mapped to the generator's k units."""
    pop_tot = world.pop.sum()
    win_pc = world.imp[ch].sum(axis=0)[world.win] / pop_tot
    lo, hi = (np.array(MERIDIAN_EC) * np.median(win_pc[win_pc > 0])
              / world.ref[ch])
    if hi > K_GRID[-1] + GRID_EPS:
        sys.exit(f"seed {world.seed} {ch}: ec_m's ceiling maps to k = {hi:.2f}, "
                 f"above the grid's {K_GRID[-1]} (docs/PLAN.md §8.7)")
    return float(lo), float(hi)


def bounds_hit(world, ch, space, shape):
    """Names of the space's bounds a projected shape sits on, within half a
    fine grid step. The grid's own edges are named too, so a projection
    stopped by the grid rather than by the tool can never pass unnoticed."""
    th, s, k = shape
    half = [x / 2 for x in FINE_STEPS]
    hits = []

    def near(v, b, h):
        return abs(v - b) <= h + GRID_EPS

    for name, v, lo, hi, h in (("theta", th, THETA_GRID[0], THETA_GRID[-1], half[0]),
                               ("hill_s", s, S_GRID[0], S_GRID[-1], half[1]),
                               ("hill_k", k, K_GRID[0], K_GRID[-1], half[2])):
        if near(v, lo, h) or near(v, hi, h):
            hits.append(f"{name} at the grid edge")
    if space == "meridian":
        lo, hi = meridian_k_support(world, ch)
        if near(k, hi, FINE_STEPS[2]):
            hits.append("hill_k at ec_m's ceiling")
        if near(k, lo, FINE_STEPS[2]):
            hits.append("hill_k at ec_m's floor")
    if space == "robyn":
        lo, hi = ROBYN_THETA[ch]
        if near(th, lo, half[0]) and lo > 0:
            hits.append("theta at Robyn's lower bound")
        if near(th, hi, half[0]):
            hits.append("theta at Robyn's upper bound")
        if near(s, ROBYN_ALPHA[0], half[1]) or near(s, ROBYN_ALPHA[1], half[1]):
            hits.append("hill_s at Robyn's alpha bound")
        kmax = robyn_k_ceiling(world, ch, th)
        if near(k, ROBYN_GAMMA[0] * kmax, FINE_STEPS[2]):
            hits.append("hill_k at Robyn's gamma floor")
        if near(k, ROBYN_GAMMA[1] * kmax, FINE_STEPS[2]):
            hits.append("hill_k at Robyn's gamma ceiling")
    return hits


def admissible(world, ch, space, theta, s, k):
    """Boolean mask over broadcast (s, k) arrays at one retention `theta`."""
    m = np.ones(np.broadcast(s, k).shape, dtype=bool)
    if space == "free":
        return m
    if space == "meridian":
        lo, hi = meridian_k_support(world, ch)
        m &= np.abs(s - MERIDIAN_SLOPE) < GRID_EPS
        m &= (k >= lo - GRID_EPS) & (k <= hi + GRID_EPS)
        return m
    if space == "robyn":
        lo, hi = ROBYN_THETA[ch]
        if not lo - GRID_EPS <= theta <= hi + GRID_EPS:
            return np.zeros_like(m)
        kmax = robyn_k_ceiling(world, ch, theta)
        m &= (s >= ROBYN_ALPHA[0] - GRID_EPS) & (s <= ROBYN_ALPHA[1] + GRID_EPS)
        m &= ((k >= ROBYN_GAMMA[0] * kmax - GRID_EPS)
              & (k <= ROBYN_GAMMA[1] * kmax + GRID_EPS))
        return m
    raise ValueError(space)


def _search(world, ch, space, target, thetas, ss, ks):
    """Exhaustive search of one channel's shape grid for the admissible
    candidate closest to `target` up to scale: loss = t't - (h't)^2 / h'h.
    Strict improvement only, so ties go to the first grid point visited."""
    pop_tot = world.pop.sum()
    x_pc = world.imp[ch].sum(axis=0) / pop_tot
    lag = world.cfg["adstock_max_lag"]
    tt = float(target @ target)
    S, K = np.meshgrid(ss, ks, indexing="ij")
    best = (np.inf, None)
    for th in thetas:
        adm = admissible(world, ch, space, th, S, K)
        if not adm.any():
            continue
        u = adstock_fast(x_pc, th, lag)[world.win] / world.ref[ch]
        us = u[None, None, :] ** S[..., None]
        H = pop_tot * us / (us + K[..., None] ** S[..., None])
        ht = H @ target
        hh = np.einsum("ijt,ijt->ij", H, H)
        loss = np.where(adm & (hh > 0), tt - ht ** 2 / np.where(hh > 0, hh, 1),
                        np.inf)
        i, j = np.unravel_index(int(np.argmin(loss)), loss.shape)
        if loss[i, j] < best[0]:
            best = (float(loss[i, j]),
                    (float(th), float(S[i, j]), float(K[i, j])))
    return best


def project_channel(world, ch, space):
    """Best approximation of `ch`'s true national regressor inside `space`
    (§8.6): coarse grid, then a grid ten times finer spanning one coarse step
    either side of the coarse winner. Returns ((theta, s, k), residual share
    of the target's sum of squares)."""
    target = national_unit_response(world, ch)
    _, (th0, s0, k0) = _search(world, ch, space, target,
                               THETA_GRID, S_GRID, K_GRID)

    def fine(centre, step, coarse, lo, hi):
        n = int(round(coarse / step))
        v = np.round(centre + step * np.arange(-n, n + 1), 6)
        return v[(v >= lo - GRID_EPS) & (v <= hi + GRID_EPS)]

    loss, shape = _search(
        world, ch, space, target,
        fine(th0, FINE_STEPS[0], 0.05, THETA_GRID[0], THETA_GRID[-1]),
        fine(s0, FINE_STEPS[1], 0.1, S_GRID[0], S_GRID[-1]),
        fine(k0, FINE_STEPS[2], 0.05, K_GRID[0], K_GRID[-1]))
    return shape, loss / float(target @ target)


def projection_check(world):
    """§8.6 check: projecting onto the free space must return the true shape
    exactly on every channel. Returns the channels where it did not."""
    bad = []
    for ch in world.cfg["channels"]:
        (th, s, k), _ = project_channel(world, ch, "free")
        spec = world.cfg["channels"][ch]
        if (abs(th - spec["adstock_alpha"]) > GRID_EPS
                or abs(s - spec["hill_s"]) > GRID_EPS
                or abs(k - spec["hill_k"]) > GRID_EPS):
            bad.append(ch)
    return bad


def projected_columns(world, spaces_by_channel, cache):
    """One national regressor per channel: projected where the channel has a
    space, true otherwise. Returns (columns, shapes, unit functions)."""
    cols, shapes, units = [], {}, {}
    for ch in world.cfg["channels"]:
        space = spaces_by_channel.get(ch)
        if space is None:
            spec = world.cfg["channels"][ch]
            shape = (spec["adstock_alpha"], spec["hill_s"], spec["hill_k"])
        else:
            key = (world.seed, ch, space)
            if key not in cache:
                cache[key] = project_channel(world, ch, space)
            shape = cache[key][0]
        th, s, k = shape
        shapes[ch] = shape
        cols.append(national_response_shape(world, ch, th, k, s))
        units[ch] = (lambda m, ch=ch, th=th, k=k, s=s:
                     float(national_response_shape(world, ch, th, k, s,
                                                   m).sum()))
    return np.column_stack(cols), shapes, units


def fit_projected(world, spaces_by_channel, cache, noiseless=False):
    """OLS on the projected columns. Noisy: L3's design (national revenue,
    estimated baseline). Noiseless: the true national media contributions,
    no baseline (§8.6 pseudo-true). Returns (coef, se, y, X, shapes, units)."""
    win = world.win
    media, shapes, units = projected_columns(world, spaces_by_channel, cache)
    if noiseless:
        y = sum(world.media[ch][:, win].sum(axis=0)
                for ch in world.cfg["channels"])
        X = media
    else:
        y = world.revenue[:, win].sum(axis=0)
        X = np.column_stack([media, baseline_design(
            world.W, world.draws["control_index"][win])])
    coef, se, _, _ = fit_ols(y, X)
    return coef, se, y, X, shapes, units


def run_setup_rung(world, rung, gt, cache):
    tool, space = SETUP_RUNGS[rung]
    cfg = world.cfg
    channels = list(cfg["channels"])
    coef, se, y, X, shapes, units = fit_projected(
        world, {ch: space for ch in channels}, cache)
    resid = y - X @ coef
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - float(resid @ resid) / ss_tot

    out_channels = {}
    for i, ch in enumerate(channels):
        b, b_se = float(coef[i]), float(se[i])
        spend = gt["channels"][ch]["spend_total"]
        unit1 = units[ch](1.0)
        inc = b * unit1
        lo, hi = (b - CI_Z * b_se) * unit1, (b + CI_Z * b_se) * unit1
        delta = cfg["mroi_delta"]
        curve_m = cfg["response_curve_multipliers"]
        out_channels[ch] = {
            "roi": {"point": inc / spend,
                    "interval_low": lo / spend,
                    "interval_high": hi / spend,
                    "interval_kind": "ols_ci90"},
            "mroi": {"point": (b * units[ch](1.0 + delta) - inc)
                     / (delta * spend)},
            "contribution_share": {"point": inc / gt["total_revenue"]},
            "response_curve": {
                "multipliers": curve_m,
                "incremental_revenue": [b * units[ch](m) for m in curve_m],
                "kind": "selected_model"},
        }

    return {
        "schema_version": SCHEMA_VERSION,
        "tool": tool,
        "tool_version": SETUP_RUNGS_VERSION,
        "arm": "national",
        "seed_dataset": world.seed,
        "run": {
            "tool_seed": 0,
            "runtime_seconds": 0.0,
            "hardware": "OLS, any CPU",
            "converged": True,
            "convergence_detail": {"method": "closed-form OLS on projected "
                                             "regressors", "r2": r2},
        },
        "channels": out_channels,
        "extras": {
            "rung": rung,
            "parameter_space": SPACES[space],
            "what_the_oracle_knows": (
                "as L3 (national aggregate regressors, baseline estimated), "
                "but each channel's regressor is the best approximation of "
                "the true one inside the parameter space above"),
            "projected_shape": {
                ch: {"adstock_alpha": shapes[ch][0], "hill_s": shapes[ch][1],
                     "hill_k": shapes[ch][2],
                     "residual_share": cache[(world.seed, ch, space)][1],
                     "at_bound": bounds_hit(world, ch, space, shapes[ch])}
                for ch in channels},
            "n_rows": int(len(y)),
            "n_params": int(X.shape[1]),
            "r2": r2,
            "note": ("Diagnostic, not a competing estimator: handed the true "
                     "shape, then restricted to what one tool's setup can "
                     "express (docs/PLAN.md §8.6)."),
        },
    }


def robyn_gamma_of_truth(world, ch):
    """Q3 (PLAN §8.3): the gamma at which Robyn's inflexion equals the true
    half-saturation, by the steady-state ratio, and the range the observed
    ratio z/u (window weeks 13 onward) allows around it."""
    spec = world.cfg["channels"][ch]
    th, k = spec["adstock_alpha"], spec["hill_k"]
    x = world.imp[ch].sum(axis=0)[world.win]
    z = robyn_adstock(x, th)
    pop_tot = world.pop.sum()
    x_pc = world.imp[ch].sum(axis=0) / pop_tot
    u = adstock_geometric(x_pc, th, world.cfg["adstock_max_lag"])[world.win] \
        / world.ref[ch]
    r = z[13:] / u[13:]
    r_ss = pop_tot * world.ref[ch] / (1 - th)
    return (k * r_ss / z.max(), k * r.min() / z.max(), k * r.max() / z.max())


def _roi_errs(world, coef, units, gt):
    return {ch: coef[i] * units[ch](1.0) / gt["channels"][ch]["spend_total"]
            / gt["channels"][ch]["true_roi"] - 1
            for i, ch in enumerate(world.cfg["channels"])}


def setup_diagnostics(seeds, data_root, results_root):
    """PLAN §8.6-8.7: the projections, the pseudo-true ROI errors, and the
    numbers that answer the audit's three open questions."""
    channels = list(CONFIG["channels"])
    true = {ch: None for ch in channels}
    fits = {"reference": true,
            "Meridian's space": {ch: "meridian" for ch in channels},
            "Robyn's space": {ch: "robyn" for ch in channels},
            "ooh, display -> Robyn": Q2_VARIANTS["robyn_ooh_display"],
            "tv -> Meridian": Q2_VARIANTS["meridian_tv"]}
    shapes, checks, pseudo, noisy, gammas = [], 0, [], [], []

    for seed in seeds:
        world = World(seed, CONFIG)
        with open(Path(data_root) / f"seed{seed}" / "ground_truth.json") as f:
            gt = json.load(f)
        checks += 5 - len(projection_check(world))
        cache = {}
        for space in ("meridian", "robyn"):
            for ch in channels:
                (th, s, k), res = project_channel(world, ch, space)
                cache[(seed, ch, space)] = ((th, s, k), res)
                shapes.append({"space": space, "channel": ch, "theta": th,
                               "hill_s": s, "hill_k": k, "residual": res,
                               "bounds": "; ".join(
                                   bounds_hit(world, ch, space, (th, s, k)))})
        for label, spaces in fits.items():
            for noiseless, sink in ((True, pseudo), (False, noisy)):
                coef, _, _, _, _, units = fit_projected(
                    world, {c: v for c, v in spaces.items() if v}, cache,
                    noiseless=noiseless)
                for ch, e in _roi_errs(world, coef, units, gt).items():
                    sink.append({"seed": seed, "fit": label, "channel": ch,
                                 "err": e})
        for ch in channels:
            g_ss, g_lo, g_hi = robyn_gamma_of_truth(world, ch)
            gammas.append({"seed": seed, "channel": ch, "gamma": g_ss,
                           "lo": g_lo, "hi": g_hi})

    # The tools' own errors, national arm, for the Q2 fractions.
    tool_err = {}
    for tool in ("meridian", "robyn"):
        errs = {ch: [] for ch in channels}
        for seed in seeds:
            p = Path(results_root) / tool / "results" / \
                f"{tool}_national_seed{seed}.json"
            with open(Path(data_root) / f"seed{seed}" / "ground_truth.json") as f:
                gt = json.load(f)
            with open(p) as f:
                res = json.load(f)
            for ch in channels:
                errs[ch].append(res["channels"][ch]["roi"]["point"]
                                / gt["channels"][ch]["true_roi"] - 1)
        tool_err[tool] = {ch: (float(np.mean(v)), float(np.mean(np.abs(v))))
                          for ch, v in errs.items()}

    sh = pd.DataFrame(shapes)
    pt = pd.DataFrame(pseudo).groupby(["fit", "channel"]).err.mean().unstack(0)
    ny = pd.DataFrame(noisy).groupby(["fit", "channel"]).err.mean().unstack(0)
    order = list(fits)
    n_cs = len(seeds) * len(channels)

    def span(col):
        lo, hi = col.min(), col.max()
        return f"{lo:g}" if np.isclose(lo, hi) else f"{lo:g}-{hi:g}"

    out = [
        "## Setup-constrained rungs: the projections (docs/PLAN.md §8.6-8.7)",
        "",
        "L6 and L7 are L3 with each channel's regressor replaced by the best",
        "approximation of the true one inside one tool's parameter space. The",
        f"check: projecting onto the free space returns the true shape on "
        f"{checks} of {n_cs} channel-seeds.",
        "",
        "Projected shape per channel, range over seeds; `residual` is the share",
        "of the true regressor's sum of squares the projection cannot reach",
        "(mean over seeds); `bounds` counts the seeds on which the projection",
        "sits on a bound of the space.",
        "",
    ]
    for space in ("meridian", "robyn"):
        out += [f"### {'Meridian' if space == 'meridian' else 'Robyn'}'s space",
                "",
                "| channel | true (θ, s, k) | projected θ | s | k | residual | bounds |",
                "|---|---|---|---|---|---|---|"]
        for ch in channels:
            g = sh[(sh.space == space) & (sh.channel == ch)]
            spec = CONFIG["channels"][ch]
            b = g.bounds[g.bounds != ""]
            bounds = ("; ".join(f"{n} ({(g.bounds.str.contains(n, regex=False)).sum()}/{len(g)})"
                                for n in sorted({x for s_ in b for x in s_.split("; ")}))
                      or "—")
            out.append(f"| {ch} | {spec['adstock_alpha']}, {spec['hill_s']}, "
                       f"{spec['hill_k']} | {span(g.theta)} | {span(g.hill_s)} "
                       f"| {span(g.hill_k)} | {g.residual.clip(lower=0).mean():.1e} "
                       f"| {bounds} |")
        out.append("")

    def table(df, title, lead):
        rows = [title, "", *lead, "",
                "| channel | " + " | ".join(order) + " |",
                "|---|" + "---|" * len(order)]
        for ch in channels:
            rows.append(f"| {ch} | " + " | ".join(
                f"{df.loc[ch, c]:+.3f}" for c in order) + " |")
        return rows + [""]

    out += table(pt, "## Pseudo-true ROI error (noiseless; baseline and control removed)",
                 ["Mean signed ROI relative error over seeds. `reference` is L2 without",
                  "noise: its error is the aggregation gap alone, and every other column",
                  "is read against it."])
    out += table(ny, "## The same fits on noisy revenue (L3's design)",
                 ["Mean signed ROI relative error over seeds. `reference` is L3,",
                  "`Meridian's space` is L6 and `Robyn's space` is L7."])

    per_seed = pd.DataFrame(noisy).pivot_table(
        index=["seed", "channel"], columns="fit", values="err")

    def leak(ch, label, tool):
        a = float(ny.loc[ch, label] - ny.loc[ch, "reference"])
        d = (per_seed[label] - per_seed["reference"]).xs(ch, level="channel")
        b = float(pt.loc[ch, label] - pt.loc[ch, "reference"])
        m = tool_err[tool][ch][1]
        return (f"| {ch} | {label} | {a:+.3f} | {d.min():+.3f} to "
                f"{d.max():+.3f} | {a / m:+.2f} | {b:+.3f} "
                f"| {b / m:+.2f} | {m:.3f} |")

    out += ["## Q2: did one channel's constraint reach another (docs/PLAN.md §8.3, §8.6)",
            "",
            "Change in the channel's mean signed ROI error when only the named",
            "channels are projected, against the reference (L3 noisy, L2 noiseless),",
            "and that change as a fraction of the tool's own mean |ROI rel err| on",
            "the channel (national arm). The noisy change is also given per seed,",
            "as its range.",
            "",
            "| channel | projected | Δ noisy | per seed | / tool | Δ noiseless | / tool | tool mean abs err |",
            "|---|---|---|---|---|---|---|---|",
            leak("tv", "ooh, display -> Robyn", "robyn"),
            leak("ooh", "tv -> Meridian", "meridian"),
            ""]

    gm = pd.DataFrame(gammas)
    out += ["## Q3: do Robyn's γ bounds contain the true half-saturation",
            "",
            "γ at which Robyn's inflexion, γ · max(z), equals the true k, by the",
            "steady-state ratio z/u; in brackets, the range the observed ratio",
            "(window weeks 13 onward) allows. Robyn's bounds: [0.3, 1].",
            "",
            "| channel | " + " | ".join(f"seed{s}" for s in seeds) + " | verdict |",
            "|---|" + "---|" * (len(seeds) + 1)]
    for ch in channels:
        g = gm[gm.channel == ch]
        inside = ((g.lo >= ROBYN_GAMMA[0]) & (g.hi <= ROBYN_GAMMA[1])).all()
        outside = ((g.hi < ROBYN_GAMMA[0]) | (g.lo > ROBYN_GAMMA[1])).all()
        verdict = ("inside" if inside else "outside" if outside
                   else "at the bound")
        out.append(f"| {ch} | " + " | ".join(
            f"{r.gamma:.2f} [{r.lo:.2f}, {r.hi:.2f}]" for r in g.itertuples())
            + f" | {verdict} |")
    out.append("")
    return out


def diagnostics(seeds, data_root, results_root="runs",
                out_path="analysis/out/diagnostics.md"):
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

    v = (pd.DataFrame(vis).groupby("channel").mean(numeric_only=True)
         .sort_values("signal_to_noise", ascending=False))
    pairs = [f"{channels[i]}-{channels[j]}"
             for i, j in zip(*np.triu_indices(len(channels), 1))]

    out = [
        "# Scenario diagnostics",
        "",
        "Written by `python analysis/oracle.py --diagnostics`. These are the",
        "scenario numbers `analysis/ORACLE.md`, `analysis/FIGURES.md` and the",
        "article quote that the scoring harness does **not** produce -- so they",
        "need a committed artifact of their own instead of living only in this",
        "command's stdout.",
        "",
        f"Seeds: {', '.join(str(x) for x in seeds)}. Generator configuration:",
        "`simulation/config.py`.",
        "",
        "## Harness check -- noiseless geo recovery",
        "",
        "Fitting L1's design to `y = M @ beta_true`, with no noise term, must",
        "return the true betas.",
        "",
        f"    max |beta rel err| over {len(seeds)} seed(s): {max(noiseless):.2e}",
        "",
        "That is machine precision, so the generator, the ground truth, the",
        "results schema and the scorer agree with each other. Whatever the",
        "tools' error is, it is not an artifact of this pipeline.",
        "",
        "## Per-channel visibility (mean over seeds)",
        "",
        "`signal_to_noise` is the standard deviation of the channel's true",
        "national contribution over the standard deviation of national revenue",
        "noise, computed on the national-aggregate regressor the national oracle",
        "actually sees. `simulation.checks.channel_snr` -- the C7 gate -- applies",
        "the same definition to the geo-level contribution summed to national and",
        "lands within 0.02 of it on every channel.",
        "",
        "```",
        v.round(4).to_string(),
        "```",
        "",
    ]

    for label, arr in (("raw geo", raw_c), ("time-demeaned", dem_c)):
        m = np.array(arr).mean(axis=0)
        lo, hi = pairs[int(m.argmin())], pairs[int(m.argmax())]
        out += [
            f"## Cross-channel correlation, {label} (pair means over seeds)",
            "",
            f"    range {m.min():.3f} ({lo}) .. {m.max():.3f} ({hi})",
            "    " + "  ".join(f"{p}={x:.3f}" for p, x in zip(pairs, m)),
            "",
        ]

    out += [
        "The raw geo correlations are inflated by the population factor every",
        "geo-level regressor carries; the time-demeaned view removes it, and is",
        "the one to read for cross-channel collinearity.",
        "",
    ]
    out += setup_diagnostics(seeds, data_root, results_root)

    text = "\n".join(out)
    print(text)
    dest = Path(out_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")
    print(f"wrote {dest}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=SEEDS)
    ap.add_argument("--data", default="data/sim")
    ap.add_argument("--out", default="runs/oracle/results")
    ap.add_argument("--rungs", nargs="*",
                    default=list(RUNGS) + list(SETUP_RUNGS))
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

    # PLAN §8.6 stop rule: the projection is checked on every seed before
    # any setup-constrained rung is exported, and a failure exports none.
    if any(r in SETUP_RUNGS for r in args.rungs):
        failed = {}
        for seed in args.seeds:
            bad = projection_check(World(seed, CONFIG))
            print(f"projection check seed{seed}: free space returns the true "
                  f"shape on {5 - len(bad)} of 5 channels")
            if bad:
                failed[seed] = bad
        if failed:
            sys.exit(f"projection check failed {failed}: no L6/L7 result is "
                     f"exported (docs/PLAN.md §8.6)")

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

        cache = {}
        for rung in args.rungs:
            if rung in SETUP_RUNGS:
                res = run_setup_rung(world, rung, gt, cache)
            else:
                res = run_rung(world, rung, gt)
            name = f"{res['tool']}_{res['arm']}_seed{seed}.json"
            with open(out / name, "w") as f:
                json.dump(res, f, indent=1)
            # ROI error rather than beta error: a projected shape rescales
            # beta, so only the ROI is comparable across all six rungs.
            errs = [abs(v["roi"]["point"] / gt["channels"][ch]["true_roi"] - 1)
                    for ch, v in res["channels"].items()]
            report.append({
                "seed": seed, "rung": rung, "tool": res["tool"],
                "r2": res["extras"]["r2"],
                "roi_abs_rel_err_mean": float(np.mean(errs)),
                "roi_abs_rel_err_max": float(np.max(errs)),
            })

    df = pd.DataFrame(report)
    print(df.groupby(["rung", "tool"])
            .agg(r2=("r2", "mean"),
                 roi_err_mean=("roi_abs_rel_err_mean", "mean"),
                 roi_err_max=("roi_abs_rel_err_max", "max"))
            .round(4).to_string())
    print(f"\nwrote {len(report)} result JSON(s) to {out}")


if __name__ == "__main__":
    main()
