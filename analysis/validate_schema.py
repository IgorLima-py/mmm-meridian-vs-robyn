"""Validate result and allocation JSONs against analysis/RESULTS_SCHEMA.md.

`scoring.py` reads what it recognises and walks past the rest: a channel
spelled differently, a missing ROI point, a curve on another grid or a key the
schema does not define would change a number or drop a row without a word.
This validator is where that is caught, before a file is scored.

Usage (from the repo root):
    python analysis/validate_schema.py --strict runs/*/results/*.json
    python analysis/validate_schema.py --strict --allocations runs/*/results/*allocation*.json

Two levels of finding:
    error    the scorer would crash, or silently misread or skip the file
    warning  outside the schema's letter but harmless to the scorer today
             (an unknown key, a file name off the convention)
--strict makes every warning an error. Exit 0: every file valid; 1: at least
one finding at the failing level; 2: no file to validate, or one that cannot
be read. A pattern that matches nothing is exit 2, never a silent pass.
"""

import argparse
import glob
import json
import math
import re
import sys
from pathlib import Path

from regret import BOUNDS, GRID

TOP_KEYS = {"schema_version", "tool", "tool_version", "arm", "seed_dataset",
            "run", "channels", "extras"}
ALLOCATION_TOP_KEYS = TOP_KEYS | {"kind", "bounds"}
RUN_KEYS = {"tool_seed", "runtime_seconds", "hardware", "converged",
            "convergence_detail"}
CHANNEL_KEYS = {"roi", "mroi", "contribution_share", "response_curve"}
METRIC_KEYS = {"point", "interval_low", "interval_high", "interval_kind"}
CURVE_KEYS = {"multipliers", "incremental_revenue", "kind"}
ARMS = {"national", "geo"}
# RESULTS_SCHEMA.md, "Semantics": the three uncertainty objects in use.
INTERVAL_KINDS = {"credible90", "candidate_range", "ols_ci90"}
CURVE_KINDS = {"posterior_median", "selected_model"}

# Allocations: a multiplier this far outside its bound, or a budget this far
# from the observed total, fails. Not measured — float-noise scale, so that
# an allocator that did not hold the limits or the budget is caught. If a
# tool's allocator reports a looser equality than this, C12 records the gap
# it measured and amends these with their origin.
BOUND_ATOL = 1e-9
BUDGET_RTOL = 1e-6


class Report:
    def __init__(self, path):
        self.path, self.errors, self.warnings = path, [], []

    def err(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)


def _num(x):
    return (isinstance(x, (int, float)) and not isinstance(x, bool)
            and math.isfinite(x))


def load_channels(data_root):
    """Channel names and window spend per seed, from the ground truths."""
    out = {}
    for p in sorted(Path(data_root).glob("seed*/ground_truth.json")):
        with open(p) as f:
            gt = json.load(f)
        out[gt["seed"]] = {c: v["spend_total"] for c, v in gt["channels"].items()}
    return out


def _common(doc, rep, truths, allowed_top):
    for k in sorted(set(doc) - allowed_top):
        rep.warn(f"unknown top-level key '{k}'")
    sv = doc.get("schema_version")
    if not isinstance(sv, str) or sv.split(".")[0] != "1":
        rep.err(f"schema_version {sv!r} is not 1.x (the scorer skips it)")
    tool = doc.get("tool")
    if not isinstance(tool, str) or not tool or tool != tool.lower():
        rep.err(f"tool {tool!r} is not a lowercase id")
    if not isinstance(doc.get("tool_version"), str):
        rep.err("tool_version missing or not a string")
    if doc.get("arm") not in ARMS:
        rep.err(f"arm {doc.get('arm')!r} not in {sorted(ARMS)}")
    seed = doc.get("seed_dataset")
    if not isinstance(seed, int) or isinstance(seed, bool):
        rep.err(f"seed_dataset {seed!r} is not an integer")
    elif seed not in truths:
        rep.err(f"no ground truth for seed {seed} (the scorer skips it)")
    run = doc.get("run")
    if not isinstance(run, dict):
        rep.err("run missing or not an object")
    else:
        for k in sorted(set(run) - RUN_KEYS):
            rep.warn(f"unknown key run.{k}")
        for k in sorted(RUN_KEYS - set(run)):
            rep.warn(f"run.{k} missing")
        if "converged" in run and not isinstance(run["converged"], bool):
            rep.err("run.converged is not true/false")
        if "runtime_seconds" in run and not _num(run["runtime_seconds"]):
            rep.err("run.runtime_seconds is not a finite number")
        if ("convergence_detail" in run
                and not isinstance(run["convergence_detail"], dict)):
            rep.err("run.convergence_detail is not an object")
    if "extras" in doc and not isinstance(doc["extras"], dict):
        rep.err("extras is not an object")
    chans = doc.get("channels")
    if not isinstance(chans, dict) or not chans:
        rep.err("channels missing, empty or not an object")
        return None
    if isinstance(seed, int) and seed in truths:
        want = set(truths[seed])
        for c in sorted(set(chans) - want):
            rep.err(f"channel '{c}' is not in the ground truth (the scorer "
                    "ignores it)")
        for c in sorted(want - set(chans)):
            rep.err(f"channel '{c}' missing (the scorer skips it)")
    return chans


def _filename(path, doc, rep, middle=""):
    p = Path(path)
    tool, arm, seed = doc.get("tool"), doc.get("arm"), doc.get("seed_dataset")
    want = f"{tool}_{arm}{middle}_seed{seed}.json"
    if p.name != want:
        rep.warn(f"file name is not '{want}' (RESULTS_SCHEMA.md convention)")
    fam = p.parent.parent.name
    if (p.parent.name != "results" or not isinstance(tool, str)
            or not (tool == fam or tool.startswith(fam + "_"))):
        rep.warn(f"file is not under runs/<tool>/results/ for tool {tool!r}")


def _metric(m, where, rep, need_point=True):
    if not isinstance(m, dict):
        rep.err(f"{where} is not an object")
        return
    for k in sorted(set(m) - METRIC_KEYS):
        rep.warn(f"unknown key {where}.{k}")
    if "point" not in m:
        if need_point:
            rep.err(f"{where}.point missing (the scorer skips the metric)")
    elif not _num(m["point"]):
        rep.err(f"{where}.point is not a finite number")
    lo, hi = "interval_low" in m, "interval_high" in m
    if lo != hi:
        rep.err(f"{where} has one interval end without the other (the "
                "scorer skips the interval)")
    if lo and hi:
        if not (_num(m["interval_low"]) and _num(m["interval_high"])):
            rep.err(f"{where} interval ends are not finite numbers")
        elif m["interval_low"] > m["interval_high"]:
            rep.err(f"{where} interval_low > interval_high")
        elif _num(m.get("point")) and not (
                m["interval_low"] <= m["point"] <= m["interval_high"]):
            rep.warn(f"{where}.point lies outside its own interval")
        if m.get("interval_kind") not in INTERVAL_KINDS:
            rep.err(f"{where}.interval_kind {m.get('interval_kind')!r} not in "
                    f"{sorted(INTERVAL_KINDS)}")
    elif "interval_kind" in m:
        rep.warn(f"{where}.interval_kind without an interval")


def _curve(rc, where, rep):
    if not isinstance(rc, dict):
        rep.err(f"{where} is not an object")
        return
    for k in sorted(set(rc) - CURVE_KEYS):
        rep.warn(f"unknown key {where}.{k}")
    x, y = rc.get("multipliers"), rc.get("incremental_revenue")
    if (not isinstance(x, list) or len(x) != len(GRID)
            or not all(_num(v) for v in x)
            or any(abs(a - b) > 1e-12 for a, b in zip(x, GRID))):
        rep.err(f"{where}.multipliers is not the generator grid {list(GRID)}")
    if (not isinstance(y, list) or len(y) != len(GRID)
            or not all(_num(v) for v in y)):
        rep.err(f"{where}.incremental_revenue is not {len(GRID)} finite numbers")
    elif y[0] != 0:
        rep.err(f"{where}.incremental_revenue[0] is {y[0]}, not 0 (the curve "
                "is incremental over the channel at zero)")
    if rc.get("kind") not in CURVE_KINDS:
        rep.err(f"{where}.kind {rc.get('kind')!r} not in {sorted(CURVE_KINDS)}")


def validate_result(path, doc, truths):
    rep = Report(path)
    if doc.get("kind") == "allocation":
        rep.err("allocation file: validate it with --allocations")
        return rep
    chans = _common(doc, rep, truths, TOP_KEYS)
    _filename(path, doc, rep)
    for c, v in (chans or {}).items():
        if not isinstance(v, dict):
            rep.err(f"channels.{c} is not an object")
            continue
        for k in sorted(set(v) - CHANNEL_KEYS):
            rep.warn(f"unknown key channels.{c}.{k}")
        if "roi" not in v:
            rep.err(f"channels.{c}.roi missing (the scorer skips ROI)")
        else:
            _metric(v["roi"], f"channels.{c}.roi", rep)
        for k in ("mroi", "contribution_share"):
            if k in v:
                _metric(v[k], f"channels.{c}.{k}", rep)
        if "response_curve" in v:
            _curve(v["response_curve"], f"channels.{c}.response_curve", rep)
    return rep


def validate_allocation(path, doc, truths):
    rep = Report(path)
    if doc.get("kind") != "allocation":
        rep.err(f"kind {doc.get('kind')!r}, not 'allocation'")
        return rep
    chans = _common(doc, rep, truths, ALLOCATION_TOP_KEYS)
    _filename(path, doc, rep, middle="_allocation")
    b = doc.get("bounds")
    if b not in BOUNDS:
        rep.err(f"bounds {b!r} is not a name in regret.BOUNDS {sorted(BOUNDS)}")
        return rep
    lo, hi = BOUNDS[b]
    ms = {}
    for c, v in (chans or {}).items():
        if not isinstance(v, dict) or not _num(v.get("multiplier")):
            rep.err(f"channels.{c}.multiplier missing or not a finite number")
            continue
        for k in sorted(set(v) - {"multiplier"}):
            rep.warn(f"unknown key channels.{c}.{k}")
        m = v["multiplier"]
        ms[c] = m
        if not lo - BOUND_ATOL <= m <= hi + BOUND_ATOL:
            rep.err(f"channels.{c}.multiplier {m} outside '{b}' [{lo}, {hi}]")
    seed = doc.get("seed_dataset")
    if seed in truths and set(ms) == set(truths[seed]):
        spend = truths[seed]
        total = sum(spend.values())
        used = sum(ms[c] * spend[c] for c in spend)
        if abs(used - total) > BUDGET_RTOL * total:
            rep.err(f"budget not held: allocation spends {used:,.0f} against "
                    f"the observed {total:,.0f} ({(used - total) / total:+.2e})")
    return rep


def expand(patterns):
    """Shell globs are not expanded by PowerShell; expand them here, and keep
    a pattern that matched nothing so it is reported, not dropped."""
    files, empty = [], []
    for pat in patterns:
        hits = sorted(glob.glob(pat)) if any(ch in pat for ch in "*?[") else [pat]
        (files.extend(hits) if hits else empty.append(pat))
    return files, empty


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--strict", action="store_true",
                    help="every warning is an error")
    ap.add_argument("--allocations", action="store_true",
                    help="the files are allocation JSONs; check their limits "
                         "against regret.BOUNDS and the budget")
    ap.add_argument("--data", default="data/sim")
    args = ap.parse_args()

    files, empty = expand(args.files)
    for pat in empty:
        print(f"no file matches {pat}")
    if not files:
        print("nothing to validate")
        sys.exit(2)
    truths = load_channels(args.data)
    if not truths:
        print(f"no ground_truth.json under {args.data}")
        sys.exit(2)

    unreadable, failed, n_warn = 0, 0, 0
    check = validate_allocation if args.allocations else validate_result
    for path in files:
        try:
            with open(path, encoding="utf-8") as f:
                doc = json.load(f)
        except (OSError, ValueError) as e:
            print(f"UNREADABLE {path}: {e}")
            unreadable += 1
            continue
        if not isinstance(doc, dict):
            print(f"UNREADABLE {path}: top level is not an object")
            unreadable += 1
            continue
        rep = check(path, doc, truths)
        bad = rep.errors + (rep.warnings if args.strict else [])
        n_warn += len(rep.warnings)
        if bad:
            failed += 1
        for m in rep.errors:
            print(f"ERROR   {path}: {m}")
        for m in rep.warnings:
            print(f"{'ERROR  ' if args.strict else 'warning'} {path}: {m}")

    ok = len(files) - failed - unreadable
    print(f"{ok} of {len(files)} file(s) valid"
          f"{' (strict)' if args.strict else ''}"
          f"{f'; {n_warn} warning(s)' if n_warn and not args.strict else ''}"
          f"{f'; {len(empty)} pattern(s) matched nothing' if empty else ''}")
    if unreadable or empty:
        sys.exit(2)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
