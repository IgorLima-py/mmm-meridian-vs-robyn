"""Generate the simulated datasets + ground truth.

Usage (from the repo root):
    python -m simulation.generate                 # all seeds in config.SEEDS
    python -m simulation.generate --seeds 101     # one seed
    python -m simulation.generate --out data/sim  # explicit output root

Per seed, writes data/sim/seed<NNN>/:
    geo.csv           geo-week panel (Meridian geo arm)
    national.csv      national aggregate (Meridian national arm)
    robyn.csv         national aggregate in Robyn column convention
    ground_truth.json counterfactual truths + generator params
"""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .config import CONFIG, SEEDS
from .core import World


def frames(world):
    cfg = world.cfg
    win = world.win
    dates = [str(d) for d in world.dates[cfg["warmup_weeks"]:]]
    W, G = world.W, cfg["n_geos"]

    rows = []
    for g in range(G):
        df = pd.DataFrame({
            "date": dates,
            "geo": f"geo_{g + 1}",
            "population": int(round(world.pop[g])),
            "revenue": np.round(world.revenue[g, win], 2),
            "competitor_index": np.round(
                world.draws["control_index"][win], 3),
        })
        for ch in cfg["channels"]:
            df[f"{ch}_spend"] = np.round(world.geo_spend[ch][g, win], 2)
            df[f"{ch}_impressions"] = np.round(
                world.imp[ch][g, win]).astype(np.int64)
        rows.append(df)
    geo = pd.concat(rows, ignore_index=True)

    nat = pd.DataFrame({
        "date": dates,
        "population": int(cfg["total_population"]),
        "revenue": np.round(world.revenue[:, win].sum(0), 2),
        "competitor_index": np.round(world.draws["control_index"][win], 3),
    })
    for ch in cfg["channels"]:
        nat[f"{ch}_spend"] = np.round(world.geo_spend[ch][:, win].sum(0), 2)
        nat[f"{ch}_impressions"] = np.round(
            world.imp[ch][:, win].sum(0)).astype(np.int64)

    robyn = pd.DataFrame({"DATE": dates, "revenue": nat["revenue"],
                          "competitor_index": nat["competitor_index"]})
    for ch in cfg["channels"]:
        robyn[f"{ch}_S"] = nat[f"{ch}_spend"]
    for ch in cfg["channels"]:
        robyn[f"{ch}_I"] = nat[f"{ch}_impressions"]

    return geo, nat, robyn


def generate_seed(seed, out_root):
    world = World(seed)
    geo, nat, robyn = frames(world)
    out = Path(out_root) / f"seed{seed}"
    out.mkdir(parents=True, exist_ok=True)
    geo.to_csv(out / "geo.csv", index=False)
    nat.to_csv(out / "national.csv", index=False)
    robyn.to_csv(out / "robyn.csv", index=False)
    with open(out / "ground_truth.json", "w") as f:
        json.dump(world.ground_truth(), f, indent=2)
    return world, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=SEEDS)
    ap.add_argument("--out", default="data/sim")
    args = ap.parse_args()
    for seed in args.seeds:
        world, out = generate_seed(seed, args.out)
        gt = world.ground_truth()
        media_share = gt["variance_decomposition"]["media_total"]
        print(f"seed {seed}: wrote {out}  "
              f"(media var share {media_share:.2f}, "
              f"total revenue {gt['total_revenue']:.3e})")


if __name__ == "__main__":
    main()
