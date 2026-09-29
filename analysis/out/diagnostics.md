# Scenario diagnostics

Written by `python analysis/oracle.py --diagnostics`. These are the
scenario numbers `analysis/ORACLE.md`, `analysis/FIGURES.md` and the
article quote that the scoring harness does **not** produce -- so they
need a committed artifact of their own instead of living only in this
command's stdout.

Seeds: 101, 102, 103, 104, 105. Generator configuration:
`simulation/config.py`.

## Harness check -- noiseless geo recovery

Fitting L1's design to `y = M @ beta_true`, with no noise term, must
return the true betas.

    max |beta rel err| over 5 seed(s): 1.21e-14

That is machine precision, so the generator, the ground truth, the
results schema and the scorer agree with each other. Whatever the
tools' error is, it is not an artifact of this pipeline.

## Per-channel visibility (mean over seeds)

`signal_to_noise` is the standard deviation of the channel's true
national contribution over the standard deviation of national revenue
noise, computed on the national-aggregate regressor the national oracle
actually sees. `simulation.checks.channel_snr` -- the C7 gate -- applies
the same definition to the geo-level contribution summed to national and
lands within 0.02 of it on every channel.

```
         true_roi  contribution_share  regressor_cv  signal_to_noise
channel                                                             
tv            1.8              0.0778        0.5002           1.9108
search        3.5              0.0907        0.0880           0.3929
social        2.5              0.0432        0.1601           0.3393
ooh           0.8              0.0092        0.2332           0.1055
display       1.2              0.0156        0.1258           0.0960
```

## Cross-channel correlation, raw geo (pair means over seeds)

    range 0.660 (tv-social) .. 0.944 (display-search)
    tv-ooh=0.752  tv-social=0.660  tv-display=0.660  tv-search=0.667  ooh-social=0.844  ooh-display=0.856  ooh-search=0.870  social-display=0.917  social-search=0.928  display-search=0.944

## Cross-channel correlation, time-demeaned (pair means over seeds)

    range -0.048 (ooh-search) .. 0.461 (tv-ooh)
    tv-ooh=0.461  tv-social=0.091  tv-display=0.050  tv-search=0.048  ooh-social=0.018  ooh-display=-0.001  ooh-search=-0.048  social-display=0.086  social-search=0.036  display-search=0.022

The raw geo correlations are inflated by the population factor every
geo-level regressor carries; the time-demeaned view removes it, and is
the one to read for cross-channel collinearity.

## Setup-constrained rungs: the projections (docs/PLAN.md §8.6-8.7)

L6 and L7 are L3 with each channel's regressor replaced by the best
approximation of the true one inside one tool's parameter space. The
check: projecting onto the free space returns the true shape on 25 of 25 channel-seeds.

Projected shape per channel, range over seeds; `residual` is the share
of the true regressor's sum of squares the projection cannot reach
(mean over seeds); `bounds` counts the seeds on which the projection
sits on a bound of the space.

### Meridian's space

| channel | true (θ, s, k) | projected θ | s | k | residual | bounds |
|---|---|---|---|---|---|---|
| tv | 0.7, 2.0, 1.2 | 0.625-0.64 | 1 | 5.215-5.39 | 1.0e-02 | hill_k at ec_m's ceiling (5/5) |
| ooh | 0.6, 1.0, 1.0 | 0.6 | 1 | 1 | 6.9e-17 | — |
| social | 0.3, 0.9, 0.8 | 0.295-0.3 | 1 | 0.675-0.68 | 3.3e-06 | — |
| display | 0.4, 0.8, 0.9 | 0.395 | 1 | 0.63 | 7.4e-06 | — |
| search | 0.1, 0.7, 0.85 | 0.095-0.105 | 1 | 0.53 | 1.1e-05 | — |

### Robyn's space

| channel | true (θ, s, k) | projected θ | s | k | residual | bounds |
|---|---|---|---|---|---|---|
| tv | 0.7, 2.0, 1.2 | 0.7 | 2 | 1.2 | 1.8e-16 | — |
| ooh | 0.6, 1.0, 1.0 | 0.4 | 0.96-1.05 | 0.66-0.7 | 3.2e-03 | hill_k at Robyn's gamma floor (3/5); theta at Robyn's upper bound (5/5) |
| social | 0.3, 0.9, 0.8 | 0.3 | 0.9 | 0.8 | 3.1e-16 | theta at Robyn's upper bound (5/5) |
| display | 0.4, 0.8, 0.9 | 0.3 | 0.95-0.96 | 0.6 | 1.7e-04 | hill_k at Robyn's gamma floor (1/5); theta at Robyn's upper bound (5/5) |
| search | 0.1, 0.7, 0.85 | 0.1 | 0.7 | 0.85 | 3.0e-17 | — |

## Pseudo-true ROI error (noiseless; baseline and control removed)

Mean signed ROI relative error over seeds. `reference` is L2 without
noise: its error is the aggregation gap alone, and every other column
is read against it.

| channel | reference | Meridian's space | Robyn's space | ooh, display -> Robyn | tv -> Meridian |
|---|---|---|---|---|---|
| tv | -0.006 | +0.231 | -0.005 | -0.005 | +0.230 |
| ooh | +0.001 | -0.028 | -0.011 | -0.011 | -0.038 |
| social | -0.001 | -0.079 | -0.004 | -0.004 | -0.077 |
| display | +0.021 | -0.270 | +0.030 | +0.030 | -0.267 |
| search | +0.002 | -0.110 | +0.002 | +0.002 | -0.110 |

## The same fits on noisy revenue (L3's design)

Mean signed ROI relative error over seeds. `reference` is L3,
`Meridian's space` is L6 and `Robyn's space` is L7.

| channel | reference | Meridian's space | Robyn's space | ooh, display -> Robyn | tv -> Meridian |
|---|---|---|---|---|---|
| tv | -0.008 | +0.202 | -0.020 | -0.020 | +0.201 |
| ooh | -0.116 | +0.097 | +0.244 | +0.244 | +0.093 |
| social | -0.030 | -0.048 | -0.040 | -0.040 | -0.046 |
| display | +0.299 | +0.459 | +0.293 | +0.293 | +0.465 |
| search | -0.186 | -0.114 | -0.187 | -0.187 | -0.109 |

## Q2: did one channel's constraint reach another (docs/PLAN.md §8.3, §8.6)

Change in the channel's mean signed ROI error when only the named
channels are projected, against the reference (L3 noisy, L2 noiseless),
and that change as a fraction of the tool's own mean |ROI rel err| on
the channel (national arm). The noisy change is also given per seed,
as its range.

| channel | projected | Δ noisy | per seed | / tool | Δ noiseless | / tool | tool mean abs err |
|---|---|---|---|---|---|---|---|
| tv | ooh, display -> Robyn | -0.012 | -0.035 to +0.015 | -0.02 | +0.000 | +0.00 | 0.610 |
| ooh | tv -> Meridian | +0.210 | -0.207 to +0.497 | +0.38 | -0.039 | -0.07 | 0.553 |

## Q3: do Robyn's γ bounds contain the true half-saturation

γ at which Robyn's inflexion, γ · max(z), equals the true k, by the
steady-state ratio z/u; in brackets, the range the observed ratio
(window weeks 13 onward) allows. Robyn's bounds: [0.3, 1].

| channel | seed101 | seed102 | seed103 | seed104 | seed105 | verdict |
|---|---|---|---|---|---|---|
| tv | 0.67 [0.66, 0.68] | 0.62 [0.61, 0.63] | 0.65 [0.64, 0.66] | 0.63 [0.63, 0.65] | 0.59 [0.59, 0.61] | inside |
| ooh | 0.51 [0.51, 0.51] | 0.49 [0.49, 0.49] | 0.49 [0.49, 0.49] | 0.50 [0.50, 0.50] | 0.48 [0.48, 0.48] | inside |
| social | 0.41 [0.41, 0.41] | 0.42 [0.42, 0.42] | 0.44 [0.44, 0.44] | 0.41 [0.41, 0.41] | 0.43 [0.43, 0.43] | inside |
| display | 0.47 [0.47, 0.47] | 0.48 [0.48, 0.48] | 0.48 [0.48, 0.48] | 0.49 [0.49, 0.49] | 0.47 [0.47, 0.47] | inside |
| search | 0.41 [0.41, 0.41] | 0.36 [0.36, 0.36] | 0.39 [0.39, 0.39] | 0.40 [0.40, 0.40] | 0.40 [0.40, 0.40] | inside |
