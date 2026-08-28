"""Meridian runs over the simulated datasets (PLAN Phase 3).

Fits Google Meridian 1.8.0 on data/sim/seed<NNN>/{national,geo}.csv and exports
one JSON per run in the pre-registered schema (analysis/RESULTS_SCHEMA.md).
Every modeling decision is documented in runs/meridian/DECISIONS.md.

Run inside the WSL2 env (see envs/ENVIRONMENT.md):
    ~/venvs/meridian/bin/python runs/meridian/run_meridian.py --arm national --seeds 101 102 103 104 105
    ~/venvs/meridian/bin/python runs/meridian/run_meridian.py --arm geo --seeds 101 102
"""
import argparse
import json
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]

CHANNELS = ["tv", "ooh", "social", "display", "search"]
MULTIPLIERS = [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0]

TOOL_SEED = 1          # D9: fixed tool seed for every run
N_CHAINS = 7           # documented in DECISIONS.md
N_ADAPT = 500
N_BURNIN = 500
N_KEEP = 1000
MAX_LAG = 13           # matches the generator's adstock support; see DECISIONS.md
RHAT_GATE = 1.1

HARDWARE = "WSL2 Ubuntu 26.04, RTX 4070 Super 12GB, TF 2.21 XLA/CUDA"


def load_input_data(arm: str, seed: int):
    from meridian.data import load

    csv_path = REPO / "data" / "sim" / f"seed{seed}" / f"{arm}.csv"
    coord_kwargs = dict(
        time="date",
        kpi="revenue",
        media=[f"{ch}_impressions" for ch in CHANNELS],
        media_spend=[f"{ch}_spend" for ch in CHANNELS],
    )
    if arm == "geo":
        # competitor_index is national-only; with the geo default of one knot
        # per time period it is collinear with the time effects and Meridian
        # rejects it as unidentifiable. See DECISIONS.md amendment 2026-08-28.
        coord_kwargs.update(geo="geo", population="population")
    else:
        coord_kwargs.update(controls=["competitor_index"])
    loader = load.CsvDataLoader(
        csv_path=str(csv_path),
        kpi_type="revenue",
        coord_to_columns=load.CoordToColumns(**coord_kwargs),
        media_to_channel={f"{ch}_impressions": ch for ch in CHANNELS},
        media_spend_to_channel={f"{ch}_spend": ch for ch in CHANNELS},
    )
    return loader.load(), csv_path


def draws_matrix(tensor) -> np.ndarray:
    """(n_chains, n_draws, n_channels) tensor -> (n_samples, n_channels)."""
    arr = np.asarray(tensor)
    if arr.ndim != 3:
        raise ValueError(f"expected 3D (chains, draws, channels), got {arr.shape}")
    return arr.reshape(-1, arr.shape[-1])


def summarize(samples: np.ndarray) -> dict:
    """Median + central 90% credible interval for one channel's draws."""
    return {
        "point": float(np.median(samples)),
        "interval_low": float(np.quantile(samples, 0.05)),
        "interval_high": float(np.quantile(samples, 0.95)),
        "interval_kind": "credible90",
    }


def convergence(idata) -> tuple[bool, dict]:
    import arviz as az

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        rhat = az.rhat(idata)
    max_rhat = float(
        np.nanmax([np.nanmax(v.values) for v in rhat.data_vars.values()])
    )
    n_div = None
    for group in ("sample_stats", "trace"):
        try:
            n_div = int(np.asarray(getattr(idata, group)["diverging"]).sum())
            break
        except Exception:
            continue
    detail = {
        "max_rhat": max_rhat,
        "rhat_gate": RHAT_GATE,
        "n_divergences": n_div,
        "n_chains": N_CHAINS,
        "n_adapt": N_ADAPT,
        "n_burnin": N_BURNIN,
        "n_keep": N_KEEP,
    }
    return max_rhat < RHAT_GATE, detail


def run_one(arm: str, seed: int, outputs_dir: Path, results_dir: Path) -> None:
    import meridian
    from meridian.analysis import analyzer
    from meridian.model import model, spec

    print(f"=== {arm} seed{seed}: loading ===", flush=True)
    data, csv_path = load_input_data(arm, seed)
    total_revenue = float(pd.read_csv(csv_path)["revenue"].sum())

    # Knots: geo arm keeps Meridian's default (n_times); the national default
    # (1 knot) cannot express the simulated seasonal baseline, so the national
    # arm uses Meridian's own Automatic Knot Selection. See DECISIONS.md.
    if arm == "national":
        ms = spec.ModelSpec(enable_aks=True, max_lag=MAX_LAG)
    else:
        ms = spec.ModelSpec(max_lag=MAX_LAG)

    mmm = model.Meridian(input_data=data, model_spec=ms)

    print(f"=== {arm} seed{seed}: sampling ===", flush=True)
    t0 = time.time()
    mmm.sample_posterior(
        n_chains=N_CHAINS,
        n_adapt=N_ADAPT,
        n_burnin=N_BURNIN,
        n_keep=N_KEEP,
        seed=TOOL_SEED,
    )
    runtime = time.time() - t0

    converged, conv_detail = convergence(mmm.inference_data)
    conv_detail["n_knots"] = int(mmm.knot_info.n_knots)
    print(
        f"    sampled in {runtime:.0f}s; max_rhat={conv_detail['max_rhat']:.4f} "
        f"divergences={conv_detail['n_divergences']} knots={conv_detail['n_knots']}",
        flush=True,
    )

    an = analyzer.Analyzer(mmm)
    ch_names = [str(c) for c in np.asarray(data.media.coords["media_channel"].values)]

    roi = draws_matrix(an.roi())
    mroi = draws_matrix(an.marginal_roi())
    inc = draws_matrix(an.incremental_outcome(include_non_paid_channels=False))
    contrib = inc / total_revenue

    print(f"=== {arm} seed{seed}: response curves ===", flush=True)
    curves = {ch: [] for ch in ch_names}
    for m in MULTIPLIERS:
        if m == 0.0:
            med = np.zeros(len(ch_names))
        else:
            inc_m = draws_matrix(
                an.incremental_outcome(
                    scaling_factor1=m, include_non_paid_channels=False
                )
            )
            med = np.median(inc_m, axis=0)
        for i, ch in enumerate(ch_names):
            curves[ch].append(float(med[i]))

    channels_out = {}
    for i, ch in enumerate(ch_names):
        channels_out[ch] = {
            "roi": summarize(roi[:, i]),
            "mroi": {"point": float(np.median(mroi[:, i]))},
            "contribution_share": summarize(contrib[:, i]),
            "response_curve": {
                "multipliers": MULTIPLIERS,
                "incremental_revenue": curves[ch],
                "kind": "posterior_median",
            },
        }

    result = {
        "schema_version": "1.0",
        "tool": "meridian",
        "tool_version": meridian.__version__,
        "arm": arm,
        "seed_dataset": seed,
        "run": {
            "tool_seed": TOOL_SEED,
            "runtime_seconds": round(runtime, 1),
            "hardware": HARDWARE,
            "converged": bool(converged),
            "convergence_detail": conv_detail,
        },
        "channels": channels_out,
        "extras": {
            "model_spec": {
                "priors": "meridian_default",
                "enable_aks": arm == "national",
                "n_knots_used": conv_detail["n_knots"],
                "max_lag": MAX_LAG,
            },
            "runtime_includes_xla_compile": True,
        },
    }

    results_dir.mkdir(parents=True, exist_ok=True)
    out_json = results_dir / f"meridian_{arm}_seed{seed}.json"
    out_json.write_text(json.dumps(result, indent=2) + "\n")

    outputs_dir.mkdir(parents=True, exist_ok=True)
    model.save_mmm(mmm, str(outputs_dir / f"meridian_{arm}_seed{seed}.pkl"))
    print(f"    wrote {out_json.relative_to(REPO)}", flush=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--arm", choices=["national", "geo"], required=True)
    p.add_argument("--seeds", type=int, nargs="+", required=True)
    args = p.parse_args()

    outputs_dir = REPO / "outputs" / "meridian"      # gitignored (heavy)
    results_dir = REPO / "runs" / "meridian" / "results"  # committed extracts

    for seed in args.seeds:
        run_one(args.arm, seed, outputs_dir, results_dir)


if __name__ == "__main__":
    main()
