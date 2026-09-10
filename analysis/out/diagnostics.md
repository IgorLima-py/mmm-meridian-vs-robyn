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
