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

Three more rungs, pre-registered in docs/PLAN.md §8 (2026-09-29), stop
handing over the shape. They share L3's design and ESTIMATE adstock and Hill
from the data, each inside one parameter space:

  L5  oracle_nat_fitshape       the generator's family, free.
                                -> what estimating the shape costs.
  L6  oracle_nat_meridian_setup Meridian 1.8.0's space as run in v1:
                                Hill slope fixed at 1.
  L7  oracle_nat_robyn_setup    Robyn 3.12.1's space as run in v1: its
                                theta, alpha and gamma bounds.
                                -> L6 - L5 and L7 - L5 are each setup's price.

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
# Setup-constrained rungs (docs/PLAN.md §8, pre-registered 2026-09-29)
#
# L1-L4 are handed the true shape, so they cannot say how much of a tool's
# miss came from the parameter space its setup allowed. L5-L7 estimate the
# shape on a grid, each inside one parameter space, and share everything
# else with L3. Every number below is from the pre-registration.

SETUP_RUNGS_VERSION = "1.1.0"     # L1-L4 stay at ORACLE_VERSION, unchanged
THETA_GRID = np.round(np.arange(0.0, 0.951, 0.05), 2)   # 20 retentions
S_GRID = np.round(np.arange(0.3, 4.001, 0.1), 1)        # 38 Hill slopes
K_GRID = np.round(np.arange(0.05, 4.001, 0.05), 2)      # 80 half-saturations
N_STARTS = 8           # truth projected to the space + 7 random grid points
MAX_CYCLES = 50
SSR_TIE = 1e-9         # a start "reached the best SSR" within this, relative
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

# The parameter spaces. The first three are the rungs; all five are the
# pseudo-true projections of PLAN §8.2.
SPACES = {
    "free": "the generator's family, all shape parameters free",
    "meridian": "Meridian 1.8.0's space: Hill slope fixed at 1, "
                "half-saturation inside ec_m's support",
    "robyn": "Robyn 3.12.1's space: theta inside its per-channel bounds, "
             "alpha in [0.5, 3], gamma in [0.3, 1]",
    "cap_ooh_display": "free, except ooh's and display's theta capped at "
                       "Robyn's bounds",
    "tv_slope1": "free, except tv's Hill slope fixed at 1",
}
SETUP_RUNGS = {
    "L5": ("oracle_nat_fitshape", "free", 5),
    "L6": ("oracle_nat_meridian_setup", "meridian", 6),
    "L7": ("oracle_nat_robyn_setup", "robyn", 7),
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


def robyn_k_ceiling(world, ch):
    """Per theta on the grid: the half-saturation, in the generator's units,
    that Robyn's gamma = 1 maps to.

    Robyn's inflexion is gamma * max(z), z its own adstocked exposure. At
    steady state z/u = population * mean exposure per capita / (1 - theta),
    so gamma = 1 corresponds to k = max(z) * (1 - theta) / (pop * ref).
    """
    x = world.imp[ch].sum(axis=0)[world.win]
    scale = world.pop.sum() * world.ref[ch]
    return np.array([robyn_adstock(x, th).max() * (1 - th) / scale
                     for th in THETA_GRID])


class ChannelGrid:
    """Every candidate national regressor of one channel on the shape grid."""

    def __init__(self, world, ch):
        cfg = world.cfg
        self.ch = ch
        pop_tot = world.pop.sum()
        x_pc = world.imp[ch].sum(axis=0) / pop_tot
        lag = cfg["adstock_max_lag"]
        u = []
        for th in THETA_GRID:
            fast = adstock_fast(x_pc, th, lag)
            ref = adstock_geometric(x_pc, th, lag)
            assert np.max(np.abs(fast - ref)) <= 1e-12 * np.max(np.abs(ref)), \
                f"adstock_fast drifted from the generator's adstock on {ch}"
            u.append(fast[world.win] / world.ref[ch])
        u = np.array(u)[:, None, None, :]                     # (nθ,1,1,W)
        us = u ** S_GRID[None, :, None, None]
        ks = K_GRID[None, None, :, None] ** S_GRID[None, :, None, None]
        self.shape = (len(THETA_GRID), len(S_GRID), len(K_GRID))
        self.H = (pop_tot * us / (us + ks)).reshape(-1, u.shape[-1])
        self.HH = np.einsum("ij,ij->i", self.H, self.H)
        win_pc = x_pc[world.win]
        self.median_over_ref = float(np.median(win_pc[win_pc > 0])
                                     / world.ref[ch])
        self.robyn_kmax = robyn_k_ceiling(world, ch)

    def mask(self, space):
        """Boolean (nθ, nS, nK) admissible set of this channel in `space`."""
        th = THETA_GRID[:, None, None]
        s = S_GRID[None, :, None]
        k = K_GRID[None, None, :]
        m = np.ones(self.shape, dtype=bool)
        if space == "meridian" or (space == "tv_slope1" and self.ch == "tv"):
            m &= np.abs(s - MERIDIAN_SLOPE) < GRID_EPS
        if space == "meridian":
            lo, hi = np.array(MERIDIAN_EC) * self.median_over_ref
            m &= (k >= lo - GRID_EPS) & (k <= hi + GRID_EPS)
        if space == "robyn" or (space == "cap_ooh_display"
                                and self.ch in ("ooh", "display")):
            lo, hi = ROBYN_THETA[self.ch]
            m &= (th >= lo - GRID_EPS) & (th <= hi + GRID_EPS)
        if space == "robyn":
            m &= (s >= ROBYN_ALPHA[0] - GRID_EPS) & (s <= ROBYN_ALPHA[1] + GRID_EPS)
            kmax = self.robyn_kmax[:, None, None]
            m &= ((k >= ROBYN_GAMMA[0] * kmax - GRID_EPS)
                  & (k <= ROBYN_GAMMA[1] * kmax + GRID_EPS))
        return m

    def unravel(self, flat):
        i, j, l = np.unravel_index(flat, self.shape)
        return float(THETA_GRID[i]), float(S_GRID[j]), float(K_GRID[l])

    def nearest(self, mask, theta, s, k):
        """Flat index of the admissible grid point nearest the given shape,
        distance measured in grid steps; ties go to the lowest index."""
        d = (np.abs(THETA_GRID[:, None, None] - theta) / 0.05
             + np.abs(S_GRID[None, :, None] - s) / 0.1
             + np.abs(K_GRID[None, None, :] - k) / 0.05)
        d = np.where(mask, d, np.inf)
        return int(np.argmin(d.reshape(-1)))


def fit_shape(y, base, grids, masks, starts):
    """Coordinate descent over channels on the shape grid (PLAN §8.1).

    For one channel, every admissible shape is scored in closed form with the
    other four channels and the baseline held fixed: residualise y on those
    columns, and a candidate column c lowers the SSR by (c'y_r)^2 / c'M c.
    Cycle through the channels until none moves. Returns one record per
    start, in start order.
    """
    channels = list(grids)
    flat_masks = {ch: masks[ch].reshape(-1) for ch in channels}
    records = []
    for start in starts:
        cur = dict(start)
        cycles = 0
        for cycles in range(1, MAX_CYCLES + 1):
            moved = False
            for ch in channels:
                g = grids[ch]
                others = [grids[c].H[cur[c]] for c in channels if c != ch]
                Z = np.column_stack(others + ([base] if base is not None else []))
                Q, _ = np.linalg.qr(Z)
                yr = y - Q @ (Q.T @ y)
                yy = float(yr @ yr)
                cy = g.H @ yr
                HQ = g.H @ Q
                cc = g.HH - np.einsum("ij,ij->i", HQ, HQ)
                ok = flat_masks[ch] & (cc > 1e-12 * g.HH)
                ssr = np.full(g.H.shape[0], np.inf)
                ssr[ok] = yy - cy[ok] ** 2 / cc[ok]
                best = int(np.argmin(ssr))
                now = ssr[cur[ch]]
                if best != cur[ch] and (not np.isfinite(now)
                                        or ssr[best] < now - 1e-12 * abs(now)):
                    cur[ch] = best
                    moved = True
            if not moved:
                break
        X = np.column_stack([grids[c].H[cur[c]] for c in channels]
                            + ([base] if base is not None else []))
        coef, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
        resid = y - X @ coef
        records.append({"shape": cur, "ssr": float(resid @ resid),
                        "cycles": cycles})
    return records


def make_starts(grids, masks, world, rng_key, with_truth=True, n=N_STARTS):
    """Start 0 is the truth projected into the space (if `with_truth`); the
    rest are admissible grid points drawn uniformly, rng seeded by `rng_key`."""
    rng = np.random.default_rng(rng_key)
    starts = []
    if with_truth:
        starts.append({ch: g.nearest(masks[ch],
                                     *_true_shape(world, ch))
                       for ch, g in grids.items()})
    while len(starts) < n:
        starts.append({ch: int(rng.choice(np.flatnonzero(masks[ch].reshape(-1))))
                       for ch in grids})
    return starts


def _true_shape(world, ch):
    spec = world.cfg["channels"][ch]
    return spec["adstock_alpha"], spec["hill_s"], spec["hill_k"]


def best_of(records, grids):
    """The winning start, and how many others landed on it."""
    ssrs = np.array([r["ssr"] for r in records])
    b = int(np.argmin(ssrs))
    win = records[b]
    reached = [i for i, r in enumerate(records)
               if r["shape"] == win["shape"]
               or r["ssr"] <= win["ssr"] * (1 + SSR_TIE)]
    return b, win, reached


def boundary_flags(g, mask, flat):
    """Fitted parameters sitting on an edge of the admissible set, holding
    the other two at their fitted values. A parameter with one admissible
    value (Meridian's slope) is fixed, not on a boundary."""
    i, j, l = np.unravel_index(flat, g.shape)
    out = []
    for name, line, pos in (("theta", mask[:, j, l], i),
                            ("hill_s", mask[i, :, l], j),
                            ("hill_k", mask[i, j, :], l)):
        adm = np.flatnonzero(line)
        if len(adm) > 1 and pos in (adm.min(), adm.max()):
            out.append(f"{name}_{'low' if pos == adm.min() else 'high'}")
    return out


def channel_grids(world):
    return {ch: ChannelGrid(world, ch) for ch in world.cfg["channels"]}


def optimiser_check(world, grids):
    """PLAN §8.1 stop rule: on revenue built exactly from L2's regressors with
    the true shape, no noise and no baseline, the search from the seven
    random starts alone must return the true ROI to 1e-9 on every channel.
    """
    channels = list(grids)
    beta = {ch: world.beta_pc[ch] for ch in channels}
    y = sum(beta[ch] * national_unit_response(world, ch) for ch in channels)
    masks = {ch: g.mask("free") for ch, g in grids.items()}
    # rng key (seed, 0): rung numbers 5-7 key the rungs themselves.
    starts = make_starts(grids, masks, world, [world.seed, 0],
                         with_truth=False, n=N_STARTS - 1)
    records = fit_shape(y, None, grids, masks, starts)
    _, win, reached = best_of(records, grids)
    shape = {ch: grids[ch].unravel(win["shape"][ch]) for ch in channels}
    cols = [national_response_shape(world, ch, shape[ch][0], shape[ch][2],
                                    shape[ch][1]) for ch in channels]
    coef, _, _, _ = fit_ols(y, np.column_stack(cols))
    errs = {}
    for i, ch in enumerate(channels):
        unit = national_unit_response(world, ch).sum()
        roi_true = beta[ch] * unit
        roi_fit = coef[i] * cols[i].sum()
        errs[ch] = abs(roi_fit - roi_true) / abs(roi_true)
    return {"max_roi_rel_err": max(errs.values()),
            "starts_reaching_best": len(reached),
            "n_starts": len(records),
            "passed": max(errs.values()) <= 1e-9}


def fit_space(world, grids, space, rng_key, truebase=False):
    """Fit one parameter space. Returns (winner shape per channel, OLS
    pieces, start bookkeeping). `truebase` gives L2's noiseless design."""
    cfg = world.cfg
    channels = list(cfg["channels"])
    win = world.win
    masks = {ch: g.mask(space) for ch, g in grids.items()}
    if truebase:
        # Pseudo-true (PLAN §8.2): the true national media contributions,
        # summed from the geo level -- noise, baseline and control removed.
        y = sum(world.media[ch][:, win].sum(axis=0) for ch in channels)
        base = None
    else:
        y = world.revenue[:, win].sum(axis=0)
        base = baseline_design(world.W, world.draws["control_index"][win])
    starts = make_starts(grids, masks, world, rng_key)
    records = fit_shape(y, base, grids, masks, starts)
    b, win_rec, reached = best_of(records, grids)
    shape = {ch: grids[ch].unravel(win_rec["shape"][ch]) for ch in channels}
    media = np.column_stack([national_response_shape(
        world, ch, shape[ch][0], shape[ch][2], shape[ch][1]) for ch in channels])
    X = media if base is None else np.column_stack([media, base])
    coef, _, _, _ = fit_ols(y, X)
    book = {
        "n_starts": len(records),
        "random_starts_reaching_best": sum(1 for i in reached if i != 0),
        "truth_start_is_best": b == 0,
        "cycles_of_best": win_rec["cycles"],
        "at_boundary": {ch: boundary_flags(grids[ch], masks[ch],
                                           win_rec["shape"][ch])
                        for ch in channels},
    }
    return shape, coef, y, X, book


def run_setup_rung(world, rung, gt, grids):
    tool, space, number = SETUP_RUNGS[rung]
    cfg = world.cfg
    channels = list(cfg["channels"])
    shape, coef, y, X, book = fit_space(world, grids, space,
                                        [world.seed, number])
    resid = y - X @ coef
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - float(resid @ resid) / ss_tot

    out_channels = {}
    for i, ch in enumerate(channels):
        theta, s, k = shape[ch]
        b = float(coef[i])

        def unit(mult, ch=ch, theta=theta, k=k, s=s):
            return float(national_response_shape(world, ch, theta, k, s,
                                                 mult).sum())

        spend = gt["channels"][ch]["spend_total"]
        inc = b * unit(1.0)
        delta = cfg["mroi_delta"]
        curve_m = cfg["response_curve_multipliers"]
        out_channels[ch] = {
            "roi": {"point": inc / spend},
            "mroi": {"point": (b * unit(1.0 + delta) - inc) / (delta * spend)},
            "contribution_share": {"point": inc / gt["total_revenue"]},
            "response_curve": {
                "multipliers": curve_m,
                "incremental_revenue": [b * unit(m) for m in curve_m],
                "kind": "selected_model"},
        }

    return {
        "schema_version": SCHEMA_VERSION,
        "tool": tool,
        "tool_version": SETUP_RUNGS_VERSION,
        "arm": "national",
        "seed_dataset": world.seed,
        "run": {
            "tool_seed": number,
            "runtime_seconds": 0.0,
            "hardware": "grid search + OLS, any CPU",
            "converged": True,
            "convergence_detail": {
                "method": "coordinate descent on the shape grid, "
                          "OLS for betas and baseline",
                "r2": r2, **{k: v for k, v in book.items()
                             if k != "at_boundary"}},
        },
        "channels": out_channels,
        "extras": {
            "rung": rung,
            "parameter_space": SPACES[space],
            "what_the_oracle_knows": (
                "national aggregate exposure with the pre-window warm-up, "
                "the generator's adstock and Hill family; shape estimated "
                "inside the parameter space above; baseline estimated "
                "(intercept + trend + 3 Fourier harmonics + control)"),
            "fitted_shape": {ch: {"adstock_alpha": shape[ch][0],
                                  "hill_s": shape[ch][1],
                                  "hill_k": shape[ch][2]}
                             for ch in channels},
            "at_boundary": book["at_boundary"],
            "n_rows": int(len(y)),
            "n_linear_params": int(X.shape[1]),
            "r2": r2,
            "note": ("Diagnostic, not a competing estimator. No interval is "
                     "exported: an OLS interval conditional on a fitted "
                     "shape ignores the shape's uncertainty (PLAN §8.1)."),
        },
    }


def diagnostics(seeds, data_root,
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

    # PLAN §8.1 stop rule: the optimiser is checked on every seed before any
    # setup-constrained rung is exported, and a failure exports none of them.
    if any(r in SETUP_RUNGS for r in args.rungs):
        failed = []
        for seed in args.seeds:
            world = World(seed, CONFIG)
            chk = optimiser_check(world, channel_grids(world))
            print(f"optimiser check seed{seed}: max |ROI rel err| "
                  f"{chk['max_roi_rel_err']:.1e}, "
                  f"{chk['starts_reaching_best']} of {chk['n_starts']} "
                  f"random starts on the winner -> "
                  f"{'pass' if chk['passed'] else 'FAIL'}")
            if not chk["passed"]:
                failed.append(seed)
        if failed:
            sys.exit(f"optimiser check failed on seed(s) {failed}: no L5-L7 "
                     f"result is exported (docs/PLAN.md §8.1)")

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

        grids = None
        for rung in args.rungs:
            if rung in SETUP_RUNGS:
                grids = grids or channel_grids(world)
                res = run_setup_rung(world, rung, gt, grids)
            else:
                res = run_rung(world, rung, gt)
            name = f"{res['tool']}_{res['arm']}_seed{seed}.json"
            with open(out / name, "w") as f:
                json.dump(res, f, indent=1)
            # ROI error rather than beta error: a fitted shape rescales beta,
            # so only the ROI is comparable across all seven rungs.
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
