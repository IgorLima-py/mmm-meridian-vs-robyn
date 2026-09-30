"""Meridian's own budget optimiser over the models saved by run_meridian.py (C12).

No refit: each national-arm model is loaded from outputs/meridian/*.pkl and
BudgetOptimizer.optimize() runs on its posterior. Limits are
analysis/regret.py BOUNDS["primary"] = (0.5, 2.0) as multipliers on the
channel's observed window spend. Meridian states its limits relative to the
historical spend, (1 - lower) * spend and (1 + upper) * spend, so the
multiplier limits (0.5, 2.0) are spend_constraint_lower=0.5 and
spend_constraint_upper=1.0. Budget = the observed window total (the default of
a fixed-budget run). Everything else is Meridian's default.

Output: one allocation JSON per seed in the schema of
analysis/RESULTS_SCHEMA.md ("Allocation files").

Run inside the WSL2 env, from the repo root (see envs/ENVIRONMENT.md):
    ~/venvs/meridian/bin/python runs/meridian/run_meridian_allocator.py --seeds 101 102 103 104 105
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "analysis"))
from regret import BOUNDS  # noqa: E402

CHANNELS = ["tv", "ooh", "social", "display", "search"]
BOUNDS_NAME = "primary"
HARDWARE = "WSL2 Ubuntu 26.04, RTX 4070 Super 12GB, TF 2.21 XLA/CUDA"


def run_one(seed: int, gtol: float, out_dir: Path) -> None:
    import meridian
    from meridian.analysis import optimizer
    from meridian.model import model

    lo, hi = BOUNDS[BOUNDS_NAME]
    print(f"=== meridian allocator national seed{seed} ===", flush=True)
    mmm = model.load_mmm(str(REPO / "outputs" / "meridian" /
                             f"meridian_national_seed{seed}.pkl"))
    prev = json.loads((REPO / "runs" / "meridian" / "results" /
                       f"meridian_national_seed{seed}.json").read_text())

    t0 = time.time()
    res = optimizer.BudgetOptimizer(mmm).optimize(
        fixed_budget=True,
        spend_constraint_lower=1.0 - lo,
        spend_constraint_upper=hi - 1.0,
        gtol=gtol,
    )
    runtime = time.time() - t0

    optm = res.optimized_data.spend
    names = [str(c) for c in np.asarray(res.optimized_data.channel.values)]
    optm_by = {c: float(optm.sel(channel=c)) for c in names}
    if set(names) != set(CHANNELS):
        raise RuntimeError(f"unexpected channels {names}")
    # The multiplier is against the channel's OBSERVED window spend, taken from
    # the model's input data. Not from res.nonoptimized_data: Meridian rounds
    # the budget for its grid (gtol) and builds that table from the rounded
    # budget (120.1M against the observed 120.12M on seeds 101-105).
    ms = mmm.input_data.media_spend
    hist = np.asarray(ms).reshape(-1, len(CHANNELS)).sum(axis=0)
    hist_by = {str(c): float(v) for c, v in
               zip(np.asarray(mmm.input_data.media_spend.coords["media_channel"].values), hist)}
    init_total, optm_total = sum(hist_by.values()), sum(optm_by.values())
    grid_budget = float(res.optimized_data.attrs["budget"])

    result = {
        "schema_version": "1.0",
        "kind": "allocation",
        "tool": "meridian",
        "tool_version": meridian.__version__,
        "arm": "national",
        "seed_dataset": seed,
        "bounds": BOUNDS_NAME,
        "run": {
            "tool_seed": prev["run"]["tool_seed"],
            "runtime_seconds": round(runtime, 1),
            "hardware": HARDWARE,
            "converged": prev["run"]["converged"],
            "convergence_detail": {
                "fixed_budget": True,
                "spend_constraint_lower": 1.0 - lo,
                "spend_constraint_upper": hi - 1.0,
                "gtol": gtol,
                "use_posterior": True,
            },
        },
        "channels": {c: {"multiplier": optm_by[c] / hist_by[c]} for c in CHANNELS},
        "extras": {
            "budget_gap_relative": (optm_total - init_total) / init_total,
            "observed_spend": hist_by,
            "optimised_spend": optm_by,
            "grid_budget": grid_budget,
        },
    }
    out = out_dir / f"meridian_national_allocation_seed{seed}.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"    {runtime:.0f}s, budget gap {result['extras']['budget_gap_relative']:+.2e}; "
          f"wrote {out.relative_to(REPO)}", flush=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--seeds", type=int, nargs="+", required=True)
    # Meridian's default (optimizer.BudgetOptimizer.optimize signature, 1.8.0).
    p.add_argument("--gtol", type=float, default=0.0001)
    args = p.parse_args()
    out_dir = REPO / "runs" / "meridian" / "results"
    for seed in args.seeds:
        run_one(seed, args.gtol, out_dir)


if __name__ == "__main__":
    main()
