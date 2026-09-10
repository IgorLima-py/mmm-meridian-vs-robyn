---
description: Runs this repo's three gates in the required order — simulation.checks, then the oracle ladder, then the scoring harness — stopping at the first failure and saying what that specific failure means, and optionally redrawing the three figures. Use whenever results need regenerating, after any tool run is exported, or before quoting a number.
argument-hint: "[--selftest]"
allowed-tools: Bash(python -m simulation.checks *), Bash(python analysis/oracle.py *), Bash(python analysis/scoring.py *), Bash(python analysis/figures.py *), Read
disable-model-invocation: false
---

Run the three gates **in this order**, from the repo root. The order matters and
is written down nowhere else: each one is only meaningful if the previous passed.

## 1. The data gate

```
python -m simulation.checks
```

Exits 0 on success, 1 on failure. **If it fails, stop.** The simulated data no
longer matches its own contract (C1–C6: saturation operating point, the
correlation dial, media variance share, positivity, exact ROI calibration, and
byte-level determinism). Nothing downstream means anything until that is
resolved — do not "just run the scorer anyway".

## 2. The recoverability gate

```
python analysis/oracle.py --out runs/oracle/results
```

Fits four oracle rungs that are handed the true adstock and Hill parameters, and
scores them like any other estimator. It aborts if the rebuilt `World` disagrees
with the committed `national.csv` by more than 1e-6 relative — **that abort means
the committed data and the generator have drifted apart**, which invalidates
every ground-truth comparison in the repo. Investigate; do not regenerate the
data to make the message go away.

Watch the printed `beta_err_mean` per rung. If rung L1 (`oracle_geo_truebase`)
were to recover the betas poorly on *noiseless* revenue, the harness itself
would be broken — see `analysis/ORACLE.md`.

## 3. The scoring harness

```
python analysis/scoring.py --results runs --data data/sim --out analysis/out
```

Consumes only the results schema plus `ground_truth.json`. If
`--selftest` was passed to this command, run
`python analysis/scoring.py --selftest` **instead** of the above: it asserts the
scorer can tell an honest stub from a spend-share-biased one and prints
`selftest OK`. An `AssertionError` there means the scorer is broken and every
number it has ever produced is suspect.

Arguments passed to this command: $ARGUMENTS

## 4. The figures (only if a number moved)

```
python analysis/figures.py
```

Re-runs step 3 internally and redraws the three PNGs in `analysis/figures/`.
Run it whenever `analysis/out/summary.md` changed — a committed chart that
disagrees with the committed summary is the kind of contradiction the
`publication-auditor` exists to catch. Skip it when the gates only confirmed
that nothing moved. Needs matplotlib (`envs/analysis.lock.txt`); the three
gates above do not. `analysis/FIGURES.md` records what each chart shows.

## Then report

Read `analysis/out/summary.md` and report:

- Per tool-arm: mean absolute ROI error, signed bias, interval coverage, mean
  interval width.
- **The oracle rungs alongside the tools, never averaged with them.** The oracle
  is a diagnostic, not a competing estimator — it was given the answers. Its
  role is to say which channels were recoverable at all.
- What moved since the last run, if `analysis/out/summary.md` is committed and
  differs.

Keep it to a table and a few lines. Do not interpret the results into a verdict
here — that is the article's job, and `analysis/ORACLE.md` already holds the
standing interpretation.
