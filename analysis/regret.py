"""Budget regret with a neutral optimiser (docs/PLAN.md §8.5, amended §8.6).

An ROI error only matters if it moves money. This module asks what each
estimator's response curves would cost if a planner used them to reallocate
the same total budget, and scores that allocation on the TRUE curves.

- Allocation: one multiplier per channel, scaling the channel's whole observed
  spend series (the response curve's own definition). The total budget is
  fixed at observed window spend: sum m_c * spend_c = sum spend_c.
- Curves: piecewise-linear interpolation of the 10-point curves on the
  generator's multiplier grid, true ones from ground_truth.json, estimated
  ones from each result JSON's `response_curve`. The same interpolation is
  used to optimise and to evaluate, so the true curves give a regret of 0.
- Optimiser: exact, by vertex enumeration. The objective is separable and
  piecewise linear, the constraint is one budget line inside a box, so an
  optimum sits where every channel but at most one is on a breakpoint. No
  numerical optimiser, nothing to converge.
- Metric: regret = (R_true(a*) - R_true(a_hat)) / R_true(a*), the share of
  the achievable incremental revenue lost; uplift captured =
  (R_true(a_hat) - R_true(1)) / (R_true(a*) - R_true(1)), 1 being the
  observed allocation. Negative uplift: the estimator's plan is worse than
  not reallocating at all.

Allocation files (`"kind": "allocation"`, RESULTS_SCHEMA.md) carry an
allocation a tool's own optimiser chose (C12); they are scored the same way,
with a_hat read from the file instead of optimised here.

Usage (from the repo root):
    python analysis/regret.py                  # print the table
    python analysis/regret.py --selftest
"""

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np

# The generator's response-curve grid (simulation/config.py,
# "response_curve_multipliers"; RESULTS_SCHEMA.md makes it mandatory).
# Every ground truth read here is checked against it.
GRID = (0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0)

# Per-channel multiplier limits, same for every channel (docs/PLAN.md §8.5).
BOUNDS = {
    # Robyn 3.12.1 robyn_allocator's default for max_response, read from the
    # installed source on the run machine, 2026-09-29. Both ends are grid
    # points. C12 runs both tools' own allocators with these limits.
    "primary": (0.5, 2.0),
    # Meridian 1.8.0's default for a fixed-budget optimisation,
    # SPEND_CONSTRAINT_DEFAULT_FIXED_BUDGET = 0.3 in constants.py, read
    # 2026-09-29. Neutral optimiser only.
    "sensitivity": (0.7, 1.3),
}

# The estimators §8.5 lists (L5 removed by §8.6), in table order:
# (label, tool id, arm, note printed beside the row).
ESTIMATORS = [
    ("Meridian", "meridian", "national", ""),
    ("Meridian", "meridian", "geo", "two seeds only"),
    ("Robyn", "robyn", "national", ""),
    ("oracle L2", "oracle_nat_truebase", "national", "true shape, true baseline"),
    ("oracle L3", "oracle_nat_estbase", "national", "true shape, estimated baseline"),
    ("oracle L6", "oracle_nat_meridian_setup", "national", "shape projected on Meridian's setup"),
    ("oracle L7", "oracle_nat_robyn_setup", "national", "shape projected on Robyn's setup"),
]

# Two allocations tie when their objective differs by less than this share of
# the optimum. Not measured: an objective here is a sum of five numbers of
# order 1e7-1e8, whose float error is of order 1e-15 relative; 1e-9 leaves six
# orders of margin and is still far below any regret worth reporting.
TIE_RTOL = 1e-9
# A multiplier this close to a bound is on it. Same reasoning: float noise on
# (budget - rest) / spend with budgets of order 1e8.
BOUND_ATOL = 1e-9


def _curve(mult, inc):
    x = np.asarray(mult, dtype=float)
    y = np.asarray(inc, dtype=float)
    if x.shape != (len(GRID),) or not np.allclose(x, GRID, rtol=0, atol=1e-12):
        raise ValueError(f"curve not on the generator grid: {list(mult)}")
    if y.shape != x.shape or not np.all(np.isfinite(y)):
        raise ValueError("curve values missing or not finite")
    return x, y


def revenue(curves, m):
    """Sum over channels of the interpolated incremental revenue at m."""
    return float(sum(np.interp(m[c], *curves[c]) for c in curves))


def optimise(curves, spend, bounds):
    """Exact maximiser of sum_c f_c(m_c) s.t. sum_c m_c spend_c = sum spend_c,
    lo <= m_c <= hi, each f_c piecewise linear on GRID.

    Returns (allocation, value, n_tied), n_tied being how many distinct
    candidate vertices reach the optimum within TIE_RTOL (1 = unique vertex).
    """
    lo, hi = bounds
    chans = list(curves)
    s = np.array([spend[c] for c in chans], dtype=float)
    budget = s.sum()
    # Breakpoints inside the box, plus the box ends.
    bp = [np.unique(np.clip(np.r_[[g for g in GRID if lo <= g <= hi], lo, hi],
                            lo, hi)) for _ in chans]
    best_val, best_m, cand_vals, cand_ms = -np.inf, None, [], []
    for j in range(len(chans)):
        others = [i for i in range(len(chans)) if i != j]
        grids = np.array(list(itertools.product(*[bp[i] for i in others])))
        rest = grids @ s[others]
        mj = (budget - rest) / s[j]
        ok = (mj >= lo - BOUND_ATOL) & (mj <= hi + BOUND_ATOL)
        if not ok.any():
            continue
        grids, mj = grids[ok], np.clip(mj[ok], lo, hi)
        val = np.interp(mj, *curves[chans[j]])
        for col, i in enumerate(others):
            val = val + np.interp(grids[:, col], *curves[chans[i]])
        full = np.empty((len(mj), len(chans)))
        full[:, others] = grids
        full[:, j] = mj
        cand_vals.append(val)
        cand_ms.append(full)
    vals = np.concatenate(cand_vals)
    ms = np.concatenate(cand_ms)
    k = int(np.argmax(vals))
    best_val, best_m = float(vals[k]), ms[k]
    tied = ms[vals >= best_val - TIE_RTOL * abs(best_val)]
    n_tied = len(np.unique(np.round(tied, 9), axis=0))
    return dict(zip(chans, best_m.tolist())), best_val, n_tied


def true_curves(gt):
    out = {}
    for c, v in gt["channels"].items():
        out[c] = _curve(v["response_curve"]["multipliers"],
                        v["response_curve"]["incremental_revenue"])
    return out


def spend_of(gt):
    return {c: v["spend_total"] for c, v in gt["channels"].items()}


def score_allocation(gt, a_hat, bounds_name, n_tied=1, tcurves=None):
    """Regret and uplift of allocation a_hat, judged on the true curves."""
    tc = tcurves or true_curves(gt)
    a_star, r_star, _ = optimise(tc, spend_of(gt), BOUNDS[bounds_name])
    r_hat = revenue(tc, a_hat)
    r_obs = revenue(tc, {c: 1.0 for c in tc})
    gain = r_star - r_obs
    return {
        "bounds": bounds_name,
        "regret": (r_star - r_hat) / r_star,
        "uplift_captured": (r_hat - r_obs) / gain if gain > 0 else np.nan,
        "achievable_uplift": gain / r_obs,
        "n_tied": n_tied,
        **{f"m_hat_{c}": a_hat[c] for c in tc},
        **{f"m_star_{c}": a_star[c] for c in tc},
    }


def regret_of_result(res, gt, bounds_name):
    """Optimise on the estimator's curves, evaluate on the true ones."""
    est = {c: _curve(res["channels"][c]["response_curve"]["multipliers"],
                     res["channels"][c]["response_curve"]["incremental_revenue"])
           for c in gt["channels"]}
    a_hat, _, n_tied = optimise(est, spend_of(gt), BOUNDS[bounds_name])
    return score_allocation(gt, a_hat, bounds_name, n_tied)


def load_ground_truths(data_root):
    out = {}
    for p in sorted(Path(data_root).glob("seed*/ground_truth.json")):
        with open(p) as f:
            gt = json.load(f)
        true_curves(gt)            # raises if a truth is off the grid
        out[gt["seed"]] = gt
    if not out:
        sys.exit(f"no ground_truth.json found under {data_root}")
    return out


def collect(results_root, gts):
    """One row per (estimator, seed, bounds), and one per allocation file.
    Returns (rows, missing estimators)."""
    rows, found, missing = [], set(), []
    for p in sorted(Path(results_root).rglob("*.json")):
        with open(p) as f:
            res = json.load(f)
        seed = res.get("seed_dataset")
        if seed not in gts:
            continue
        key = (res.get("tool"), res.get("arm"))
        if res.get("kind") == "allocation":
            a_hat = {c: float(v["multiplier"]) for c, v in res["channels"].items()}
            row = score_allocation(gts[seed], a_hat, res["bounds"])
            rows.append({"label": f"{res['tool'].capitalize()} own allocator",
                         "tool": res["tool"], "arm": res["arm"], "seed": seed,
                         "note": "the tool's optimiser (C12)", **row})
            continue
        for label, tool, arm, note in ESTIMATORS:
            if key == (tool, arm):
                # response_curve is optional in the schema: a run without one
                # has no plan to score, and says so instead of crashing.
                if any("response_curve" not in res["channels"].get(c, {})
                       for c in gts[seed]["channels"]):
                    missing.append(f"{label} ({arm}) seed {seed}: no "
                                   "response curve on every channel")
                    continue
                found.add(key)
                for b in BOUNDS:
                    rows.append({"label": label, "tool": tool, "arm": arm,
                                 "seed": seed, "note": note,
                                 **regret_of_result(res, gts[seed], b)})
    missing += [f"{lab} ({arm})" for lab, t, arm, _ in ESTIMATORS
                if (t, arm) not in found]
    return rows, missing


def _rng(v):
    return f"{v.mean():.3f} ({v.min():.3f} to {v.max():.3f})"


def summary_lines(rows, missing, gts):
    """The `## Budget regret` section of analysis/out/summary.md."""
    import pandas as pd
    df = pd.DataFrame(rows)
    lo, hi = BOUNDS["primary"]
    slo, shi = BOUNDS["sensitivity"]
    lines = ["## Budget regret (docs/PLAN.md §8.5)", "",
             "Each estimator's response curves are handed to the same exact "
             "optimiser, which reallocates the observed total budget with every "
             f"channel's multiplier inside [{lo}, {hi}] (Robyn's allocator "
             "default); the plan is then scored on the true curves. Regret: "
             "the share of the achievable incremental revenue the plan loses. "
             "Uplift captured: the share of the best plan's gain over the "
             "observed allocation that this plan keeps; negative means the "
             "plan is worse than not reallocating. The last column repeats "
             f"regret with the multipliers inside [{slo}, {shi}] (Meridian's "
             "fixed-budget default). Mean over seeds, range in brackets.", "",
             "| estimator | arm | seeds | regret | uplift captured "
             f"| regret, [{slo}, {shi}] |",
             "|---|---|---|---|---|---|"]
    # §8.5's order first, then the tools' own allocators (C12).
    present = set(zip(df["label"], df["arm"]))
    order = [(lab, arm) for lab, _, arm, _ in ESTIMATORS if (lab, arm) in present]
    order += sorted(present - set(order))
    for label, arm in order:
        g = df[(df.label == label) & (df.arm == arm)]
        p = g[g.bounds == "primary"].sort_values("seed")
        s = g[g.bounds == "sensitivity"].sort_values("seed")
        note = g["note"].iloc[0]
        lines.append(f"| {label}{' — ' + note if note else ''} | {arm} "
                     f"| {len(p)} | {_rng(p.regret)} "
                     f"| {_rng(p.uplift_captured)} "
                     f"| {_rng(s.regret) if len(s) else '—'} |")

    # Reference, not an estimator: keeping the observed allocation.
    ref = []
    for seed, gt in sorted(gts.items()):
        tc = true_curves(gt)
        for b in BOUNDS:
            ref.append({"seed": seed, "bounds": b, **score_allocation(
                gt, {c: 1.0 for c in tc}, b, tcurves=tc)})
    ref = pd.DataFrame(ref)
    rp, rs = ref[ref.bounds == "primary"], ref[ref.bounds == "sensitivity"]
    lines.append(f"| *reference: keep the observed allocation* | — "
                 f"| {len(rp)} | {_rng(rp.regret)} | 0 by definition "
                 f"| {_rng(rs.regret)} |")
    lines += ["",
              "The reference row is not an estimator and was not "
              "pre-registered: it is the bar any plan has to clear. The best "
              "plan's gain over the observed allocation, as a share of the "
              "observed allocation's incremental revenue: "
              + ", ".join(f"seed {s} {v:.1%}" for s, v in
                          zip(rp.seed, rp.achievable_uplift))
              + f" at [{lo}, {hi}]; "
              + ", ".join(f"{v:.1%}" for v in rs.achievable_uplift)
              + f" at [{slo}, {shi}].", ""]

    # Seed by seed, primary limits.
    prim = df[df.bounds == "primary"]
    seeds = sorted(prim.seed.unique())
    lines += [f"Regret seed by seed, multipliers in [{lo}, {hi}]:", "",
              "| estimator | arm | " + " | ".join(str(s) for s in seeds) + " |",
              "|---|---|" + "---|" * len(seeds)]
    for label, arm in order:
        g = prim[(prim.label == label) & (prim.arm == arm)].set_index("seed")
        lines.append(f"| {label} | {arm} | " + " | ".join(
            f"{g.regret[s]:.3f}" if s in g.index else "—" for s in seeds) + " |")

    tied = df[df.n_tied > 1]
    lines.append("")
    if len(tied):
        lines.append("- tied optima on the estimator's own curves (the plan "
                     "above is the first vertex found; another tied plan "
                     "would score differently): "
                     + "; ".join(f"{r.label} {r.arm} seed {r.seed} "
                                 f"[{r.bounds}], {r.n_tied} vertices"
                                 for r in tied.itertuples()))
    else:
        lines.append("- every estimator's optimum is a unique vertex: no plan "
                     "above was picked from a tie.")
    if missing:
        lines.append("- not in the table (no result file, or a file without "
                     "curves): " + "; ".join(missing))
    return lines + [""]


# ---------------------------------------------------------------------------
# Selftest.

def test_true_curves_zero_regret(gts):
    """The true curves, handed in as an estimator, lose nothing."""
    for seed, gt in gts.items():
        res = {"channels": {c: {"response_curve": v["response_curve"]}
                            for c, v in gt["channels"].items()}}
        for b in BOUNDS:
            r = regret_of_result(res, gt, b)
            assert abs(r["regret"]) <= 1e-9, (seed, b, r["regret"])
            if r["achievable_uplift"] > 0:
                assert abs(r["uplift_captured"] - 1) <= 1e-9, (seed, b, r)


def test_perturbed_curve():
    """Two channels, linear curves, the answer worked out by hand.

    spend A = 100, B = 40, budget 140, multipliers in [0.5, 2].
    True: A returns 1 per unit spend (f_A = 100 m), B returns 2 (f_B = 80 m).
      Best plan: B at its ceiling, m_B = 2 (80 spent), A gets the other 60,
      m_A = 0.6 — strictly between breakpoints 0.5 and 0.75.
      R* = 60 + 160 = 220. Observed: R(1) = 100 + 80 = 180.
    Estimator: A's curve tripled by hand (it thinks A returns 3).
      Its plan: B at its floor, m_B = 0.5 (20 spent), A gets 120, m_A = 1.2.
      R_true(a_hat) = 120 + 40 = 160.
    Regret = (220 - 160) / 220 = 3/11. Uplift captured = (160 - 180) /
    (220 - 180) = -1/2.
    """
    g = np.array(GRID)
    gt = {"channels": {
        "A": {"spend_total": 100.0, "response_curve": {
            "multipliers": list(GRID), "incremental_revenue": list(100 * g)}},
        "B": {"spend_total": 40.0, "response_curve": {
            "multipliers": list(GRID), "incremental_revenue": list(80 * g)}}}}
    res = {"channels": {
        "A": {"response_curve": {"multipliers": list(GRID),
                                 "incremental_revenue": list(300 * g)}},
        "B": gt["channels"]["B"]}}
    r = regret_of_result(res, gt, "primary")
    assert abs(r["m_star_A"] - 0.6) < 1e-12 and r["m_star_B"] == 2.0, r
    assert abs(r["m_hat_A"] - 1.2) < 1e-12 and r["m_hat_B"] == 0.5, r
    assert abs(r["regret"] - 3 / 11) < 1e-12, r["regret"]
    assert abs(r["uplift_captured"] + 0.5) < 1e-12, r["uplift_captured"]


def test_optimiser_beats_dense_search(gts, n=200_000):
    """No feasible allocation drawn at random beats the vertex optimum.
    Draws four multipliers uniformly in the box and solves for the fifth."""
    rng = np.random.default_rng(20260929)
    for seed, gt in gts.items():
        tc, sp = true_curves(gt), spend_of(gt)
        chans = list(tc)
        s = np.array([sp[c] for c in chans])
        for b, (lo, hi) in BOUNDS.items():
            _, best, _ = optimise(tc, sp, (lo, hi))
            for j in range(len(chans)):
                others = [i for i in range(len(chans)) if i != j]
                m = rng.uniform(lo, hi, size=(n, len(others)))
                mj = (s.sum() - m @ s[others]) / s[j]
                ok = (mj >= lo) & (mj <= hi)
                val = np.interp(mj[ok], *tc[chans[j]])
                for col, i in enumerate(others):
                    val = val + np.interp(m[ok, col], *tc[chans[i]])
                assert val.max() <= best * (1 + 1e-12), (seed, b, val.max(), best)


def test_allocation_file(gts):
    """An allocation file at the true optimum scores 0; at the observed
    allocation, it scores the reference regret."""
    gt = next(iter(gts.values()))
    tc = true_curves(gt)
    a_star, r_star, _ = optimise(tc, spend_of(gt), BOUNDS["primary"])
    assert abs(score_allocation(gt, a_star, "primary")["regret"]) < 1e-12
    obs = score_allocation(gt, {c: 1.0 for c in tc}, "primary")
    assert abs(obs["uplift_captured"]) < 1e-12
    assert abs(obs["regret"] - (r_star - revenue(tc, {c: 1.0 for c in tc}))
               / r_star) < 1e-12


def selftest(data_root):
    gts = load_ground_truths(data_root)
    test_true_curves_zero_regret(gts)
    test_perturbed_curve()
    test_optimiser_beats_dense_search(gts)
    test_allocation_file(gts)
    print("regret selftest OK: true curves 0 regret on "
          f"{len(gts)} seeds x {len(BOUNDS)} bounds; hand-worked case 3/11; "
          "no random feasible plan beats the vertex optimum")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="runs")
    ap.add_argument("--data", default="data/sim")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        selftest(args.data)
        return
    gts = load_ground_truths(args.data)
    rows, missing = collect(args.results, gts)
    if not rows:
        sys.exit("no regret to report: " + "; ".join(missing))
    print("\n".join(summary_lines(rows, missing, gts)))


if __name__ == "__main__":
    main()
