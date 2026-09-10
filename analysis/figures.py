"""Phase 5 figures (PLAN Phase 5) — the three charts, from committed inputs.

Usage (from the repo root):
    python analysis/figures.py
    python analysis/figures.py --results runs --data data/sim
        --out analysis/out --figures analysis/figures

Where the numbers come from, precisely (`analysis/FIGURES.md` says the same):

  * every ROI, error, coverage and width value -> `scoring.run_scoring()`, the
    same call that writes the committed `analysis/out/summary.md`;
  * the response curves -> the committed result JSONs, interpolated onto the
    ground-truth multiplier grid;
  * two numbers are derived HERE and nowhere else — the channel ordering, via
    `simulation.checks.channel_snr` (the C7 gate's own function), and Robyn's
    portfolio-level ROI anchor in figure 1. Both are printed to stdout on
    every run so they can be checked.

The three figures:
  fig1_roi_per_channel.png  estimated vs true ROI per channel, per estimator,
                            with the oracle as a third series
  fig2_response_curves.png  estimated vs true response curves
  fig3_intervals.png        interval coverage and interval width

Figures 1 and 2 are national-arm only. Mixing Meridian's geo arm into one
column and not the others would not be a comparison (analysis/ORACLE.md); the
geo runs appear only in figure 3, in their own labelled block.
"""

import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt                              # noqa: E402
import numpy as np                                           # noqa: E402
import pandas as pd                                          # noqa: E402
from matplotlib.lines import Line2D                          # noqa: E402
from matplotlib.patches import Patch                         # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scoring import load_ground_truths, run_scoring          # noqa: E402
from simulation.checks import SNR_FLOOR, channel_snr         # noqa: E402
from simulation.core import World                            # noqa: E402

# Colour-blind-safe (Okabe-Ito). Truth is always black.
C_TRUTH = "#000000"
C_MERIDIAN = "#0072B2"
C_ROBYN = "#D55E00"
C_ORACLE = "#009E73"

# The like-for-like national comparison. The oracle rung is L3 — the one that
# estimates its own baseline, exactly as both tools must. L2 (true baseline)
# would hand the oracle an advantage the tools never get.
SERIES = [
    ("meridian", "national", "Meridian 1.8.0", C_MERIDIAN),
    ("robyn", "national", "Robyn 3.12.1", C_ROBYN),
    ("oracle_nat_estbase", "national", "Oracle L3 (true form, own baseline)",
     C_ORACLE),
]

# Meridian's default ROI prior is LogNormal(0.2, 0.9); its median is e^0.2.
# Source: meridian/model/prior_distribution.py, cited in analysis/ORACLE.md.
MERIDIAN_PRIOR_MEDIAN = float(np.exp(0.2))

SIMULATED = ("Simulated data — 8 geos x 156 weeks, generator 1.0.0, 5 seeds. "
             "Not an advertiser dataset; no real campaign is described here.")

# Travels with every Robyn series, on every chart: these caveats are recorded
# in runs/robyn/DECISIONS.md and must not live only there.
ROBYN_CAVEAT = ("Robyn: 3 of its 5 seeds fail its own convergence check, and "
                "the five are not one spec — seeds 101-104 ran at 4000x5,\n"
                "seed105 at its converged 2000x5 (runs/robyn/DECISIONS.md).")


def channel_order(data_root):
    """Channels by mean signal-to-noise, descending, plus how many clear the
    C7 floor — the split between the two recoverability regimes."""
    snrs = {}
    for p in sorted(Path(data_root).glob("seed*/ground_truth.json")):
        seed = json.loads(p.read_text())["seed"]
        for ch, v in channel_snr(World(seed)).items():
            snrs.setdefault(ch, []).append(v)
    mean_snr = {ch: float(np.mean(v)) for ch, v in snrs.items()}
    order = sorted(mean_snr, key=mean_snr.get, reverse=True)
    n_recoverable = sum(mean_snr[ch] >= SNR_FLOOR for ch in order)
    return order, mean_snr, n_recoverable


def load_results(results_root):
    out = []
    for p in sorted(Path(results_root).rglob("*.json")):
        res = json.loads(p.read_text())
        if res.get("schema_version", "").split(".")[0] == "1":
            out.append(res)
    return out


def _provenance(fig):
    fig.text(0.005, 0.005,
             "Regenerate: python analysis/figures.py  (calls "
             "analysis/scoring.py over runs/ and data/sim/)",
             fontsize=6.5, color="#666666", ha="left", va="bottom")


def _caption(fig, title, subtitle):
    fig.suptitle(title, fontsize=13.5, fontweight="bold", x=0.008, ha="left",
                 y=0.985)
    fig.text(0.008, 0.945, subtitle, fontsize=8.6, color="#333333",
             ha="left", va="top")


# ---------------------------------------------------------------------------
# Figure 1 — estimated vs true ROI per channel, oracle as third series.

def fig_roi_per_channel(df, gts, order, mean_snr, n_recoverable, path):
    d = df[df.arm == "national"]
    true_roi = d.groupby("channel").true_roi.mean()
    spend = {seed: {ch: v["spend_total"] for ch, v in gt["channels"].items()}
             for seed, gt in gts.items()}

    # Robyn's anchor: the single ROI an equal-effect-per-spend decomposition
    # implies, computed from Robyn's OWN point estimates, mean over seeds.
    per_seed = []
    for seed, g in d[d.tool == "robyn"].groupby("seed"):
        roi = g.set_index("channel").roi_point
        sp = spend[seed]
        per_seed.append(sum(roi[ch] * sp[ch] for ch in roi.index)
                        / sum(sp[ch] for ch in roi.index))
    rb_portfolio = float(np.mean(per_seed))

    fig, ax = plt.subplots(figsize=(11.2, 6.6))
    offsets = np.linspace(-0.24, 0.24, len(SERIES))
    rng = np.random.default_rng(0)          # jitter only; never touches values

    if n_recoverable < len(order):
        ax.axvspan(n_recoverable - 0.5, len(order) - 0.4, color="#f2f2f2",
                   zorder=0)
        ax.axvline(n_recoverable - 0.5, color="#999999", ls="--", lw=1,
                   zorder=1)

    for i, ch in enumerate(order):
        ax.hlines(true_roi[ch], i - 0.44, i + 0.44, color=C_TRUTH, lw=2.6,
                  zorder=5)
        for off, (tool, arm, _label, colour) in zip(offsets, SERIES):
            g = d[(d.tool == tool) & (d.arm == arm) & (d.channel == ch)]
            if g.empty:
                continue
            x = i + off + rng.uniform(-0.045, 0.045, len(g))
            conv = g.converged.fillna(False).to_numpy(dtype=bool)
            pt = g.roi_point.to_numpy()
            ax.scatter(x[conv], pt[conv], s=34, color=colour, alpha=0.85,
                       zorder=4, linewidths=0)
            ax.scatter(x[~conv], pt[~conv], s=44, facecolors="none",
                       edgecolors=colour, linewidths=1.3, zorder=4)
            ax.hlines(pt.mean(), i + off - 0.105, i + off + 0.105,
                      color=colour, lw=3, zorder=6)

    top = ax.get_ylim()[1]
    ax.axhline(MERIDIAN_PRIOR_MEDIAN, color=C_MERIDIAN, ls=":", lw=1.1,
               alpha=0.8, zorder=2)
    box = dict(facecolor="white", edgecolor="none", pad=1.2, alpha=0.85)
    ax.text(-0.55, MERIDIAN_PRIOR_MEDIAN,
            f"Meridian ROI-prior median {MERIDIAN_PRIOR_MEDIAN:.2f}",
            color=C_MERIDIAN, fontsize=7.8, va="bottom", ha="left",
            bbox=box, zorder=7)
    ax.axhline(rb_portfolio, color=C_ROBYN, ls=":", lw=1.1, alpha=0.8,
               zorder=2)
    ax.text(-0.55, rb_portfolio,
            f"Robyn's own portfolio-level ROI {rb_portfolio:.2f}",
            color=C_ROBYN, fontsize=7.8, va="top", ha="left",
            bbox=box, zorder=7)

    ax.set_xticks(range(len(order)))
    ax.set_xticklabels([f"{ch}\nS/N {mean_snr[ch]:.2f}" for ch in order],
                       fontsize=9.5)
    ax.set_ylabel("ROI (incremental revenue per unit of spend)")
    ax.set_xlim(-0.6, len(order) - 0.4)
    ax.grid(axis="y", color="#e6e6e6", lw=0.8, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)

    ax.text(-0.55, top, "the truth is in the data here:\n"
            "the oracle comes closer than either tool", fontsize=8.4,
            color="#555555", va="top", ha="left")
    if n_recoverable < len(order):
        ax.text(n_recoverable - 0.42, top,
                f"signal-to-noise below the C7 floor of {SNR_FLOOR}:\n"
                "the oracle misses these too — nobody could recover them",
                fontsize=8.4, color="#555555", va="top", ha="left")

    handles = [Line2D([], [], color=C_TRUTH, lw=2.6, label="true ROI")]
    handles += [Line2D([], [], color=c, marker="o", lw=3, ms=6, label=lab)
                for _, _, lab, c in SERIES]
    handles += [
        Line2D([], [], color="#555555", marker="o", ls="none", ms=6,
               markerfacecolor="none", label="run did not converge"),
        Line2D([], [], color="#555555", lw=3, label="mean over 5 seeds"),
    ]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.10),
              ncol=3, frameon=False, fontsize=8.6)

    _caption(
        fig, "Both tools miss the ROIs that this dataset does contain",
        SIMULATED + "\nOne dot per seed, national arm only. The oracle is not "
        "a competing estimator: it is handed the generator's true adstock and "
        "Hill parameters and only fits the five betas.\nWhere the oracle "
        "lands on the true ROI, the data held the answer and the tool missed "
        "it. Where the oracle misses too, no estimator could have done "
        "better.\n" + ROBYN_CAVEAT)
    _provenance(fig)
    fig.subplots_adjust(top=0.79, bottom=0.205, left=0.062, right=0.985)
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return rb_portfolio


# ---------------------------------------------------------------------------
# Figure 2 — response curves against truth.

def fig_response_curves(results, gts, order, n_recoverable, path):
    fig, axes = plt.subplots(1, len(order), figsize=(14.2, 6.8))
    scale = 1e6

    for i, (ch, ax) in enumerate(zip(order, axes)):
        mult = np.array(gts[list(gts)[0]]["channels"][ch]
                        ["response_curve"]["multipliers"])
        truth = np.mean(
            [np.interp(mult, gt["channels"][ch]["response_curve"]
                       ["multipliers"],
                       gt["channels"][ch]["response_curve"]
                       ["incremental_revenue"])
             for gt in gts.values()], axis=0) / scale
        if i >= n_recoverable:
            ax.set_facecolor("#f7f7f7")
        ax.plot(mult, truth, color=C_TRUTH, lw=2.4, zorder=5)

        for tool, arm, _label, colour in SERIES:
            curves = [
                np.interp(mult,
                          r["channels"][ch]["response_curve"]["multipliers"],
                          r["channels"][ch]["response_curve"]
                          ["incremental_revenue"]) / scale
                for r in results
                if r["tool"] == tool and r["arm"] == arm
                and ch in r["channels"]
                and "response_curve" in r["channels"][ch]]
            if not curves:
                continue
            arr = np.array(curves)
            ax.fill_between(mult, arr.min(0), arr.max(0), color=colour,
                            alpha=0.16, lw=0)
            dashed = colour == C_ORACLE
            ax.plot(mult, arr.mean(0), color=colour, lw=2.0,
                    ls=(0, (5, 2)) if dashed else "-",
                    zorder=6 if dashed else 3)

        for m in (0.5, 1.0):
            ax.axvline(m, color="#bbbbbb", ls=":", lw=0.9, zorder=1)
        ax.set_title(ch, fontsize=10.5, fontweight="bold")
        ax.set_xlabel("spend multiplier")
        ax.grid(color="#ececec", lw=0.7)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        if i == 0:
            ax.set_ylabel("incremental revenue (millions)")

    axes[0].text(0.05, 0.95, "scored at 0.5x and 1.0x",
                 transform=axes[0].transAxes, fontsize=7.4, color="#777777",
                 va="top")
    if n_recoverable < len(order):
        axes[n_recoverable].text(
            0.05, 0.95, "below the S/N floor",
            transform=axes[n_recoverable].transAxes, fontsize=7.4,
            color="#777777", va="top")

    handles = [Line2D([], [], color=C_TRUTH, lw=2.4, label="truth")]
    handles += [Line2D([], [], color=c, lw=2.0,
                       ls=(0, (5, 2)) if c == C_ORACLE else "-", label=lab)
                for _, _, lab, c in SERIES]
    handles += [Patch(facecolor="#999999", alpha=0.25,
                      label="range across the 5 seeds")]
    fig.legend(handles=handles, loc="lower center", ncol=5, frameon=False,
               fontsize=8.6, bbox_to_anchor=(0.5, 0.012))

    _caption(
        fig, "On the channels this data can measure, the curves are wrong at every budget",
        SIMULATED
        + "\nMean over 5 seeds, national arm only; the band is the seed-to-seed range. Panels are ordered by signal-to-noise;"
        + "\nthe two shaded panels sit below the recoverability floor, where the oracle fails as well."
        + "\nThe plotted means: Robyn sits below the truth everywhere on tv, search and social; Meridian does on search and social,"
        + "\nbut over-states tv up to 0.5x spend (2.4x the truth at 0.25x, 1.16x at 0.5x), crossing under between 0.5x and 0.75x."
        + "\nBands, not means, are what individual seeds do: all five Meridian seeds are above the truth on tv at 0.25x, and one"
        + "\nRobyn seed grazes it there (+0.1%). On the two unmeasurable channels both wander — Robyn's mean ooh curve crosses"
        + "\nthe truth between 1.25x and 1.5x."
        + "\nMeridian's curves are its own counterfactual; Robyn has no equivalent, so its curves are reconstructed from its"
        + "\nselected model's own fitted parameters, checked against its xDecompAgg at 1.0x (runs/robyn/DECISIONS.md RD9)."
        + "\n" + ROBYN_CAVEAT)
    _provenance(fig)
    fig.subplots_adjust(top=0.60, bottom=0.185, left=0.055, right=0.99,
                        wspace=0.26)
    fig.savefig(path, dpi=200)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 3 — interval coverage and width.

INTERVAL_ROWS = [
    ("oracle_nat_truebase", "national", "Oracle L2 — true baseline",
     C_ORACLE, "OLS 90% CI"),
    ("oracle_nat_estbase", "national", "Oracle L3 — own baseline",
     C_ORACLE, "OLS 90% CI"),
    ("meridian", "national", "Meridian — national", C_MERIDIAN,
     "90% credible"),
    ("robyn", "national", "Robyn — national", C_ROBYN,
     "Pareto candidate range"),
    ("oracle_geo_truebase", "geo", "Oracle L1 — true baseline", C_ORACLE,
     "OLS 90% CI"),
    ("oracle_geo_estbase", "geo", "Oracle L4 — own baseline", C_ORACLE,
     "OLS 90% CI"),
    ("meridian", "geo", "Meridian — geo", C_MERIDIAN, "90% credible"),
]
CANDIDATE_RANGE = "Pareto candidate range"


def fig_intervals(df, path):
    rows = []
    for tool, arm, label, colour, kind in INTERVAL_ROWS:
        g = df[(df.tool == tool) & (df.arm == arm)]
        if g.empty:
            continue
        seeds = g.groupby("seed").converged.first()
        rows.append({
            "label": label, "colour": colour, "kind": kind, "arm": arm,
            "coverage": g.roi_covered.mean(),
            "width": g.roi_interval_width_rel.mean(),
            "n_obs": int(g.roi_covered.notna().sum()),
            "n_seeds": int(seeds.size),
            "n_bad": int((~seeds.fillna(False).astype(bool)).sum()),
        })
    r = pd.DataFrame(rows)
    y = np.arange(len(r))[::-1].astype(float)
    y[r.arm.to_numpy() == "geo"] -= 0.7      # gap between the two arm blocks

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.8, 5.2), sharey=True)
    for ax, col, title, xlabel in [
            (ax1, "coverage", "Does the interval contain the truth?",
             "share of channel-seed intervals covering the true ROI"),
            (ax2, "width", "How wide is it?",
             "mean interval width / true ROI")]:
        for yi, row in zip(y, r.itertuples()):
            hatch = "///" if row.kind == CANDIDATE_RANGE else None
            ax.barh(yi, getattr(row, col), height=0.62, color=row.colour,
                    alpha=0.88, hatch=hatch, edgecolor="white", zorder=3)
            ax.text(getattr(row, col) + (0.014 if col == "coverage" else 0.05),
                    yi, f"{getattr(row, col):.2f}", va="center", fontsize=8.8,
                    color="#333333", zorder=4)
        ax.set_title(title, fontsize=10.5, fontweight="bold", loc="left")
        ax.set_xlabel(xlabel, fontsize=8.4)
        ax.grid(axis="x", color="#ececec", lw=0.8, zorder=0)
        ax.set_axisbelow(True)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.tick_params(axis="y", length=0)

    ax1.axvline(0.90, color="#333333", ls="--", lw=1.2, zorder=5)
    ax1.text(0.90, y.max() + 0.62, "nominal 90% ", fontsize=8,
             color="#333333", va="bottom", ha="right")
    ax1.set_xlim(0, 1.05)

    labels = [f"{row.label}  ({row.kind})"
              + (f"\n{row.n_bad} of {row.n_seeds} seeds did not converge"
                 if row.n_bad else "")
              for row in r.itertuples()]
    ax1.set_yticks(y)
    ax1.set_yticklabels(labels, fontsize=8.4)
    ax1.set_ylim(y.min() - 0.7, y.max() + 0.7)
    ax1.tick_params(axis="y", length=0)

    nat_bottom = y[r.arm.to_numpy() == "national"].min()
    for ax in (ax1, ax2):
        ax.axhline(nat_bottom - 0.42, color="#dddddd", lw=1, zorder=1)
    ax1.text(0.008, nat_bottom - 0.62, "geo arm", fontsize=7.8,
             color="#888888", va="top")

    _caption(
        fig, "Well-calibrated intervals were available in this dataset",
        SIMULATED
        + "\nThe oracle rung that estimates its own baseline (L3) covers the "
        "truth 92% of the time against a nominal 90%, on the same data the "
        "tools saw —\nso \"the data were hard\" does not explain the tools' "
        "miscalibration."
        "\nRobyn's bar is hatched because its interval is the spread across "
        "Pareto-front candidate models, not a posterior interval: it is not "
        "a 90%\ninterval, and neither its coverage nor its width is "
        "comparable to the others' — a narrow candidate spread is not a "
        "confident posterior.\n"
        "Robyn's five seeds are also not one spec: 101-104 ran at 4000x5, seed105 at its converged 2000x5 (runs/robyn/DECISIONS.md).\n"
        "Meridian escalated too: its geo arm shipped at 2000/2000 adapt/burnin, a 3rd attempt after 500/500 and 1000/1000 failed, carrying 64 and 122\n"
        "divergent transitions against 1-6 per national run (runs/meridian/DECISIONS.md). Its national arm needed no escalation.")
    _provenance(fig)
    fig.subplots_adjust(top=0.655, bottom=0.115, left=0.245, right=0.985,
                        wspace=0.06)
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="runs")
    ap.add_argument("--data", default="data/sim")
    ap.add_argument("--out", default="analysis/out")
    ap.add_argument("--figures", default="analysis/figures")
    args = ap.parse_args()

    df = run_scoring(args.results, args.data, args.out)
    gts = load_ground_truths(args.data)
    results = load_results(args.results)
    order, mean_snr, n_recoverable = channel_order(args.data)

    figdir = Path(args.figures)
    figdir.mkdir(parents=True, exist_ok=True)
    rb = fig_roi_per_channel(df, gts, order, mean_snr, n_recoverable,
                             figdir / "fig1_roi_per_channel.png")
    fig_response_curves(results, gts, order, n_recoverable,
                        figdir / "fig2_response_curves.png")
    iv = fig_intervals(df, figdir / "fig3_intervals.png")

    print("channel order by signal-to-noise: "
          + ", ".join(f"{c} {mean_snr[c]:.2f}" for c in order))
    print(f"Robyn portfolio-level ROI from its own estimates: {rb:.2f}")
    print(iv[["label", "kind", "coverage", "width", "n_obs",
              "n_bad"]].to_string(index=False))
    print(f"wrote 3 figure(s) to {figdir}")


if __name__ == "__main__":
    main()
