"""Pre-registered scoring harness (PLAN §4, metrics M1-M5).

Tool-agnostic: consumes ONLY result JSONs in the schema defined in
RESULTS_SCHEMA.md plus the generator's ground_truth.json files.

Usage (from the repo root):
    python analysis/scoring.py --results runs --data data/sim --out analysis/out
    python analysis/scoring.py --selftest        # end-to-end check on stubs

Outputs: <out>/metrics_long.csv (one row per run x channel) and
<out>/summary.md (aggregates per tool x arm).
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

CURVE_EVAL_MULTIPLIERS = [0.5, 1.0]   # M3, Jin-style fixed evaluation points


def load_ground_truths(data_root):
    out = {}
    for p in sorted(Path(data_root).glob("seed*/ground_truth.json")):
        with open(p) as f:
            gt = json.load(f)
        out[gt["seed"]] = gt
    if not out:
        sys.exit(f"no ground_truth.json found under {data_root}")
    return out


def _curve_value(curve, m):
    return float(np.interp(m, curve["multipliers"],
                           curve["incremental_revenue"]))


def score_result(res, gt):
    """Rows of per-channel metrics for one result file."""
    rows = []
    tch, rch = gt["channels"], res["channels"]

    # effect shares among media (for M5), true and estimated
    true_inc = {c: v["true_roi"] * v["spend_total"] for c, v in tch.items()}
    true_eff = {c: v / sum(true_inc.values()) for c, v in true_inc.items()}
    est_contrib = {c: rch[c]["contribution_share"]["point"]
                   for c in rch if "contribution_share" in rch[c]}
    est_eff = ({c: v / sum(est_contrib.values())
                for c, v in est_contrib.items()}
               if est_contrib and sum(est_contrib.values()) > 0 else {})

    for ch, t in tch.items():
        if ch not in rch:
            continue
        r = rch[ch]
        row = {
            "tool": res["tool"], "arm": res["arm"],
            "seed": res["seed_dataset"], "channel": ch,
            "true_roi": t["true_roi"],
            "converged": res.get("run", {}).get("converged"),
            "runtime_seconds": res.get("run", {}).get("runtime_seconds"),
        }
        # M1 ROI recovery + interval containment
        roi = r.get("roi", {})
        if "point" in roi:
            row["roi_point"] = roi["point"]
            row["roi_rel_err"] = (roi["point"] - t["true_roi"]) / t["true_roi"]
        if "interval_low" in roi and "interval_high" in roi:
            row["roi_interval_kind"] = roi.get("interval_kind")
            row["roi_covered"] = bool(
                roi["interval_low"] <= t["true_roi"] <= roi["interval_high"])
            row["roi_interval_width_rel"] = (
                (roi["interval_high"] - roi["interval_low"]) / t["true_roi"])
        # M1b marginal ROI
        mroi = r.get("mroi", {})
        if "point" in mroi:
            row["mroi_rel_err"] = ((mroi["point"] - t["true_mroi"])
                                   / t["true_mroi"])
        # M2 contribution share (of total revenue), percentage points
        share = r.get("contribution_share", {})
        if "point" in share:
            row["contrib_err_pp"] = (share["point"]
                                     - t["true_contribution_share"]) * 100
        # M3 response-curve relative error at fixed multipliers
        if "response_curve" in r:
            for m in CURVE_EVAL_MULTIPLIERS:
                true_v = _curve_value(t["response_curve"], m)
                if true_v != 0:
                    est_v = _curve_value(r["response_curve"], m)
                    row[f"curve_rel_err_m{m}"] = (est_v - true_v) / true_v
        # M5 DECOMP.RSSD probe: signed pull of estimated media-effect share
        # toward spend share (positive = pulled toward spend allocation)
        if ch in est_eff:
            direction = np.sign(t["spend_share"] - true_eff[ch])
            row["rssd_pull"] = (est_eff[ch] - true_eff[ch]) * direction
        rows.append(row)
    return rows


def summarize(df):
    lines = ["# Scoring summary", ""]
    agg_spec = {
        "roi_rel_err": ["mean"], "roi_abs_rel_err": ["mean"],
        "roi_covered": ["mean"], "roi_interval_width_rel": ["mean"],
        "contrib_abs_err_pp": ["mean"], "rssd_pull": ["mean"],
        "curve_rel_err_m0.5": ["mean"], "curve_rel_err_m1.0": ["mean"],
        "runtime_seconds": ["mean"],
    }
    df = df.copy()
    df["roi_abs_rel_err"] = df.get("roi_rel_err", np.nan).abs()
    df["contrib_abs_err_pp"] = df.get("contrib_err_pp", np.nan).abs()
    present = {k: v for k, v in agg_spec.items() if k in df.columns}
    for (tool, arm), grp in df.groupby(["tool", "arm"]):
        lines.append(f"## {tool} — {arm} arm "
                     f"({grp['seed'].nunique()} seed(s))")
        agg = grp.agg({k: "mean" for k in present})
        rename = {
            "roi_rel_err": "ROI bias (mean rel err)",
            "roi_abs_rel_err": "ROI |rel err| (mean)",
            "roi_covered": "interval contains truth (rate)",
            "roi_interval_width_rel": "interval width / true ROI (mean)",
            "contrib_abs_err_pp": "contribution |err| (pp, mean)",
            "rssd_pull": "pull toward spend share (mean, + = pulled)",
            "curve_rel_err_m0.5": "curve rel err @0.5x spend (mean)",
            "curve_rel_err_m1.0": "curve rel err @1.0x spend (mean)",
            "runtime_seconds": "runtime (s, mean)",
        }
        for k in present:
            v = agg[k]
            if pd.notna(v):
                lines.append(f"- {rename.get(k, k)}: {v:.3f}")
        lines.append("")
        by_ch = grp.groupby("channel")["roi_rel_err"].mean()
        lines.append("| channel | mean ROI rel err |")
        lines.append("|---|---|")
        for ch, v in by_ch.items():
            lines.append(f"| {ch} | {v:.3f} |")
        lines.append("")
    return "\n".join(lines)


def run_scoring(results_root, data_root, out_root):
    gts = load_ground_truths(data_root)
    rows, skipped = [], []
    for p in sorted(Path(results_root).rglob("*.json")):
        with open(p) as f:
            res = json.load(f)
        if res.get("schema_version", "").split(".")[0] != "1":
            skipped.append(f"{p} (schema_version)")
            continue
        seed = res.get("seed_dataset")
        if seed not in gts:
            skipped.append(f"{p} (no ground truth for seed {seed})")
            continue
        rows.extend(score_result(res, gts[seed]))
    if not rows:
        sys.exit(f"no scoreable result JSONs under {results_root}")
    df = pd.DataFrame(rows)
    out = Path(out_root)
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "metrics_long.csv", index=False)
    text = summarize(df)
    if skipped:
        text += "\nSkipped files:\n" + "\n".join(f"- {s}" for s in skipped)
    (out / "summary.md").write_text(text, encoding="utf-8")
    print(f"scored {df['seed'].nunique()} seed(s), "
          f"{df[['tool', 'arm']].drop_duplicates().shape[0]} tool-arm(s) -> "
          f"{out / 'metrics_long.csv'}, {out / 'summary.md'}")
    return df


# ---------------------------------------------------------------------------
# Selftest: build two stub estimators from ground truth and score them.

def _stub(gt, kind, rng):
    channels = {}
    true_inc = {c: v["true_roi"] * v["spend_total"]
                for c, v in gt["channels"].items()}
    total_inc = sum(true_inc.values())
    spend = {c: v["spend_total"] for c, v in gt["channels"].items()}
    total_spend = sum(spend.values())
    for ch, t in gt["channels"].items():
        if kind == "good":       # truth + small noise, honest intervals
            roi = t["true_roi"] * (1 + rng.normal(0, 0.05))
            lo, hi = roi * 0.8, roi * 1.25
        else:                    # pulled toward spend-proportional allocation
            blended_inc = (0.5 * true_inc[ch]
                           + 0.5 * total_inc * spend[ch] / total_spend)
            roi = blended_inc / spend[ch]
            lo, hi = roi * 0.95, roi * 1.05      # overconfident
        inc = roi * spend[ch]
        curve = t["response_curve"]
        channels[ch] = {
            "roi": {"point": roi, "interval_low": lo, "interval_high": hi,
                    "interval_kind": "credible90"},
            "contribution_share": {"point": inc / gt["total_revenue"]},
            "response_curve": {
                "multipliers": curve["multipliers"],
                "incremental_revenue": [
                    v * roi / t["true_roi"]
                    for v in curve["incremental_revenue"]],
                "kind": "posterior_median"},
        }
    return {"schema_version": "1.0", "tool": f"stub_{kind}",
            "tool_version": "0", "arm": "national",
            "seed_dataset": gt["seed"],
            "run": {"tool_seed": 0, "runtime_seconds": 0.0,
                    "hardware": "selftest", "converged": True},
            "channels": channels}


def selftest(data_root, out_root):
    gts = load_ground_truths(data_root)
    rng = np.random.default_rng(0)
    stub_dir = Path(out_root) / "selftest_results"
    stub_dir.mkdir(parents=True, exist_ok=True)
    for seed, gt in gts.items():
        for kind in ("good", "biased"):
            with open(stub_dir / f"stub_{kind}_national_seed{seed}.json",
                      "w") as f:
                json.dump(_stub(gt, kind, rng), f)
    df = run_scoring(stub_dir, data_root, Path(out_root) / "selftest")
    good = df[df.tool == "stub_good"]["roi_rel_err"].abs().mean()
    biased = df[df.tool == "stub_biased"]["roi_rel_err"].abs().mean()
    pull_g = df[df.tool == "stub_good"]["rssd_pull"].mean()
    pull_b = df[df.tool == "stub_biased"]["rssd_pull"].mean()
    print(f"selftest: |ROI err| good={good:.3f} biased={biased:.3f}; "
          f"rssd_pull good={pull_g:.4f} biased={pull_b:.4f}")
    assert good < biased, "good stub should beat biased stub on ROI error"
    assert pull_b > 0.01 > abs(pull_g), \
        "rssd_pull should flag the spend-blended stub, not the honest one"
    print("selftest OK")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="runs")
    ap.add_argument("--data", default="data/sim")
    ap.add_argument("--out", default="analysis/out")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        selftest(args.data, args.out)
    else:
        run_scoring(args.results, args.data, args.out)


if __name__ == "__main__":
    main()
