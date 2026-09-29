# Scoring summary

## meridian — geo arm (2 seed(s))
- ROI bias (mean rel err): -0.499
- ROI |rel err| (mean): 0.499
- interval contains truth (rate): 0.500
- interval width / true ROI (mean): 1.196
- contribution |err| (pp, mean): 2.953
- pull toward spend share (mean, + = pulled): 0.082
- distance from spend share (pp, mean |gap| per channel-seed): 3.906
- curve rel err @0.5x spend (mean): -0.417
- curve rel err @1.0x spend (mean): -0.499
- runtime (s, mean): 1105.450
- ROI rank agreement with truth (Spearman over channels, mean over seeds): 0.200 (range -0.3 to 0.7)
- seeds passing the tool's own convergence check: 1 of 2 (not converged: 101)
- run spec: 2000/2000 adapt/burnin — seeds 101, 102
- same seeds, national arm: ROI |rel err| (mean) 0.470 — seeds 101, 102

| channel | mean ROI rel err | mean \|ROI rel err\| | effect share − spend share (pp) |
|---|---|---|---|
| display | -0.331 | 0.331 | +0.12 |
| ooh | -0.161 | 0.161 | -1.54 |
| search | -0.793 | 0.793 | -1.64 |
| social | -0.712 | 0.712 | -1.29 |
| tv | -0.501 | 0.501 | +4.35 |

## meridian — national arm (5 seed(s))
- ROI bias (mean rel err): -0.312
- ROI |rel err| (mean): 0.533
- interval contains truth (rate): 0.600
- interval width / true ROI (mean): 1.615
- contribution |err| (pp, mean): 2.612
- pull toward spend share (mean, + = pulled): 0.085
- distance from spend share (pp, mean |gap| per channel-seed): 4.618
- curve rel err @0.5x spend (mean): -0.201
- curve rel err @1.0x spend (mean): -0.312
- runtime (s, mean): 431.580
- ROI rank agreement with truth (Spearman over channels, mean over seeds): -0.060 (range -0.5 to 0.3)
- seeds passing the tool's own convergence check: 5 of 5
- run spec: 500/500 adapt/burnin — seeds 101, 102, 103, 104, 105

| channel | mean ROI rel err | mean \|ROI rel err\| | effect share − spend share (pp) |
|---|---|---|---|
| display | -0.381 | 0.381 | -3.41 |
| ooh | 0.553 | 0.553 | +1.92 |
| search | -0.697 | 0.697 | +0.66 |
| social | -0.698 | 0.698 | -4.27 |
| tv | -0.336 | 0.336 | +5.10 |

## oracle_geo_estbase — geo arm (5 seed(s))
- ROI bias (mean rel err): 0.091
- ROI |rel err| (mean): 0.932
- interval contains truth (rate): 0.560
- interval width / true ROI (mean): 1.555
- contribution |err| (pp, mean): 2.135
- pull toward spend share (mean, + = pulled): 0.031
- distance from spend share (pp, mean |gap| per channel-seed): 12.343
- curve rel err @0.5x spend (mean): 0.091
- curve rel err @1.0x spend (mean): 0.091
- runtime (s, mean): 0.000
- ROI rank agreement with truth (Spearman over channels, mean over seeds): 0.280 (range -0.7 to 1.0)
- seeds passing the tool's own convergence check: 5 of 5

| channel | mean ROI rel err | mean \|ROI rel err\| | effect share − spend share (pp) |
|---|---|---|---|
| display | 0.498 | 1.990 | -1.72 |
| ooh | 0.254 | 1.773 | -5.34 |
| search | -0.170 | 0.351 | +8.06 |
| social | -0.070 | 0.426 | +1.95 |
| tv | -0.057 | 0.120 | -2.95 |

## oracle_geo_truebase — geo arm (5 seed(s))
- ROI bias (mean rel err): 0.118
- ROI |rel err| (mean): 0.520
- interval contains truth (rate): 0.600
- interval width / true ROI (mean): 1.099
- contribution |err| (pp, mean): 1.202
- pull toward spend share (mean, + = pulled): 0.013
- distance from spend share (pp, mean |gap| per channel-seed): 7.611
- curve rel err @0.5x spend (mean): 0.118
- curve rel err @1.0x spend (mean): 0.118
- runtime (s, mean): 0.000
- ROI rank agreement with truth (Spearman over channels, mean over seeds): 0.600 (range -0.2 to 1.0)
- seeds passing the tool's own convergence check: 5 of 5

| channel | mean ROI rel err | mean \|ROI rel err\| | effect share − spend share (pp) |
|---|---|---|---|
| display | 0.376 | 0.994 | -2.58 |
| ooh | 0.364 | 1.024 | -5.04 |
| search | -0.063 | 0.178 | +12.78 |
| social | -0.057 | 0.361 | +1.70 |
| tv | -0.029 | 0.044 | -6.86 |

## oracle_nat_estbase — national arm (5 seed(s))
- ROI bias (mean rel err): -0.008
- ROI |rel err| (mean): 0.598
- interval contains truth (rate): 0.920
- interval width / true ROI (mean): 2.753
- contribution |err| (pp, mean): 1.621
- pull toward spend share (mean, + = pulled): 0.025
- distance from spend share (pp, mean |gap| per channel-seed): 8.689
- curve rel err @0.5x spend (mean): -0.009
- curve rel err @1.0x spend (mean): -0.008
- runtime (s, mean): 0.000
- ROI rank agreement with truth (Spearman over channels, mean over seeds): 0.620 (range 0.0 to 0.9)
- seeds passing the tool's own convergence check: 5 of 5

| channel | mean ROI rel err | mean \|ROI rel err\| | effect share − spend share (pp) |
|---|---|---|---|
| display | 0.299 | 1.216 | -2.69 |
| ooh | -0.116 | 0.975 | -7.38 |
| search | -0.186 | 0.319 | +8.56 |
| social | -0.030 | 0.382 | +2.85 |
| tv | -0.008 | 0.098 | -1.34 |

## oracle_nat_meridian_setup — national arm (5 seed(s))
- ROI bias (mean rel err): 0.119
- ROI |rel err| (mean): 0.664
- interval contains truth (rate): 0.840
- interval width / true ROI (mean): 2.776
- contribution |err| (pp, mean): 1.834
- pull toward spend share (mean, + = pulled): 0.037
- distance from spend share (pp, mean |gap| per channel-seed): 8.081
- curve rel err @0.5x spend (mean): 0.188
- curve rel err @1.0x spend (mean): 0.119
- runtime (s, mean): 0.000
- ROI rank agreement with truth (Spearman over channels, mean over seeds): 0.620 (range 0.2 to 0.9)
- seeds passing the tool's own convergence check: 5 of 5

| channel | mean ROI rel err | mean \|ROI rel err\| | effect share − spend share (pp) |
|---|---|---|---|
| display | 0.459 | 1.334 | -3.14 |
| ooh | 0.097 | 1.062 | -6.82 |
| search | -0.114 | 0.303 | +8.06 |
| social | -0.048 | 0.417 | +0.41 |
| tv | 0.202 | 0.202 | +1.50 |

## oracle_nat_robyn_setup — national arm (5 seed(s))
- ROI bias (mean rel err): 0.058
- ROI |rel err| (mean): 0.635
- interval contains truth (rate): 0.920
- interval width / true ROI (mean): 2.784
- contribution |err| (pp, mean): 1.662
- pull toward spend share (mean, + = pulled): 0.027
- distance from spend share (pp, mean |gap| per channel-seed): 8.290
- curve rel err @0.5x spend (mean): 0.072
- curve rel err @1.0x spend (mean): 0.058
- runtime (s, mean): 0.000
- ROI rank agreement with truth (Spearman over channels, mean over seeds): 0.440 (range -0.6 to 0.9)
- seeds passing the tool's own convergence check: 5 of 5

| channel | mean ROI rel err | mean \|ROI rel err\| | effect share − spend share (pp) |
|---|---|---|---|
| display | 0.293 | 1.164 | -3.12 |
| ooh | 0.244 | 1.197 | -5.98 |
| search | -0.187 | 0.328 | +8.31 |
| social | -0.040 | 0.390 | +2.59 |
| tv | -0.020 | 0.094 | -1.80 |

## oracle_nat_truebase — national arm (5 seed(s))
- ROI bias (mean rel err): 0.065
- ROI |rel err| (mean): 0.432
- interval contains truth (rate): 0.880
- interval width / true ROI (mean): 1.338
- contribution |err| (pp, mean): 0.961
- pull toward spend share (mean, + = pulled): 0.006
- distance from spend share (pp, mean |gap| per channel-seed): 7.342
- curve rel err @0.5x spend (mean): 0.064
- curve rel err @1.0x spend (mean): 0.065
- runtime (s, mean): 0.000
- ROI rank agreement with truth (Spearman over channels, mean over seeds): 0.760 (range 0.3 to 1.0)
- seeds passing the tool's own convergence check: 5 of 5

| channel | mean ROI rel err | mean \|ROI rel err\| | effect share − spend share (pp) |
|---|---|---|---|
| display | 0.182 | 0.759 | -3.89 |
| ooh | 0.229 | 0.968 | -5.57 |
| search | -0.023 | 0.152 | +14.19 |
| social | -0.038 | 0.243 | +2.01 |
| tv | -0.022 | 0.039 | -6.74 |

## robyn — national arm (5 seed(s))
- ROI bias (mean rel err): -0.540
- ROI |rel err| (mean): 0.555
- interval contains truth (rate): 0.160
- interval width / true ROI (mean): 0.277
- contribution |err| (pp, mean): 3.180
- pull toward spend share (mean, + = pulled): 0.067
- distance from spend share (pp, mean |gap| per channel-seed): 0.538
- curve rel err @0.5x spend (mean): -0.637
- curve rel err @1.0x spend (mean): -0.540
- runtime (s, mean): 1017.080
- ROI rank agreement with truth (Spearman over channels, mean over seeds): 0.420 (range -0.5 to 1.0)
- seeds passing the tool's own convergence check: 2 of 5 (not converged: 102, 103, 104)
- run spec: 2000x5 iterations x trials — seeds 105; 4000x5 iterations x trials — seeds 101, 102, 103, 104  **mixed spec: means below blend them**

| channel | mean ROI rel err | mean \|ROI rel err\| | effect share − spend share (pp) |
|---|---|---|---|
| display | -0.428 | 0.428 | -0.35 |
| ooh | -0.156 | 0.230 | -0.55 |
| search | -0.792 | 0.792 | +0.91 |
| social | -0.717 | 0.717 | +0.09 |
| tv | -0.610 | 0.610 | -0.11 |

## Meridian − Robyn, national arm, seed by seed

D = mean over the five channels of |ROI rel err|, Meridian minus Robyn; negative means Meridian was closer on that seed.

| seed | Meridian | Robyn | D |
|---|---|---|---|
| 101 | 0.545 | 0.450 | +0.095 |
| 102 | 0.394 | 0.556 | -0.162 |
| 103 | 0.756 | 0.454 | +0.302 |
| 104 | 0.426 | 0.699 | -0.273 |
| 105 | 0.543 | 0.617 | -0.074 |

- mean D: -0.022; standard deviation (ddof=1): 0.226; range -0.273 to +0.302
- Meridian lower on 3 of 5 seeds, Robyn lower on 2

## Setup decomposition, national arm (docs/PLAN.md §8.3, §8.6)

Each tool's mean |ROI rel err| over seeds, split exactly into three terms: L3's error (the shape known, the baseline estimated); the setup's price, the rung restricted to the tool's parameter space (L6 for Meridian, L7 for Robyn) minus L3; and the rest, the tool minus that rung. The rest mixes the cost of estimating the shape, a difficulty of the data, with the tool's own machinery. A negative term is reported as it is. Channels marked * are below the recoverability floor, where no term means anything.

| tool | channel | tool \|err\| | L3 | setup's price | rest |
|---|---|---|---|---|---|
| meridian | display* | 0.381 | 1.216 | +0.118 | -0.953 |
| meridian | ooh* | 0.553 | 0.975 | +0.087 | -0.509 |
| meridian | search | 0.697 | 0.319 | -0.017 | +0.394 |
| meridian | social | 0.698 | 0.382 | +0.035 | +0.281 |
| meridian | tv | 0.336 | 0.098 | +0.104 | +0.134 |
| robyn | display* | 0.428 | 1.216 | -0.052 | -0.736 |
| robyn | ooh* | 0.230 | 0.975 | +0.222 | -0.967 |
| robyn | search | 0.792 | 0.319 | +0.009 | +0.464 |
| robyn | social | 0.717 | 0.382 | +0.008 | +0.327 |
| robyn | tv | 0.610 | 0.098 | -0.004 | +0.516 |

The same three pieces with their sign (mean signed ROI rel err over seeds). Not pre-registered: added because the table above apportions sizes, and a setup that pushes the estimate one way cannot explain a miss the other way.

| tool | channel | tool | L3 | setup's shift | rest |
|---|---|---|---|---|---|
| meridian | display* | -0.381 | +0.299 | +0.160 | -0.840 |
| meridian | ooh* | +0.553 | -0.116 | +0.214 | +0.455 |
| meridian | search | -0.697 | -0.186 | +0.072 | -0.583 |
| meridian | social | -0.698 | -0.030 | -0.018 | -0.650 |
| meridian | tv | -0.336 | -0.008 | +0.210 | -0.538 |
| robyn | display* | -0.428 | +0.299 | -0.006 | -0.721 |
| robyn | ooh* | -0.156 | -0.116 | +0.360 | -0.399 |
| robyn | search | -0.792 | -0.186 | -0.001 | -0.605 |
| robyn | social | -0.717 | -0.030 | -0.010 | -0.677 |
| robyn | tv | -0.610 | -0.008 | -0.012 | -0.590 |
## Budget regret (docs/PLAN.md §8.5)

Each estimator's response curves are handed to the same exact optimiser, which reallocates the observed total budget with every channel's multiplier inside [0.5, 2.0] (Robyn's allocator default); the plan is then scored on the true curves. Regret: the share of the achievable incremental revenue the plan loses. Uplift captured: the share of the best plan's gain over the observed allocation that this plan keeps; negative means the plan is worse than not reallocating. The last column repeats regret with the multipliers inside [0.7, 1.3] (Meridian's fixed-budget default). Mean over seeds, range in brackets.

| estimator | arm | seeds | regret | uplift captured | regret, [0.7, 1.3] |
|---|---|---|---|---|---|
| Meridian | national | 5 | 0.056 (0.026 to 0.079) | 0.064 (-0.384 to 0.573) | 0.034 (0.014 to 0.050) |
| Meridian — two seeds only | geo | 2 | 0.069 (0.030 to 0.108) | -0.131 (-0.770 to 0.508) | 0.054 (0.017 to 0.092) |
| Robyn | national | 5 | 0.059 (0.005 to 0.132) | 0.008 (-1.207 to 0.920) | 0.034 (0.001 to 0.077) |
| oracle L2 — true shape, true baseline | national | 5 | 0.007 (0.000 to 0.021) | 0.882 (0.660 to 1.000) | 0.004 (0.000 to 0.015) |
| oracle L3 — true shape, estimated baseline | national | 5 | 0.022 (0.011 to 0.035) | 0.626 (0.434 to 0.816) | 0.009 (0.000 to 0.029) |
| oracle L6 — shape projected on Meridian's setup | national | 5 | 0.023 (0.004 to 0.060) | 0.614 (0.000 to 0.936) | 0.016 (0.001 to 0.044) |
| oracle L7 — shape projected on Robyn's setup | national | 5 | 0.025 (0.011 to 0.036) | 0.575 (0.396 to 0.816) | 0.012 (0.000 to 0.028) |
| *reference: keep the observed allocation* | — | 5 | 0.060 (0.057 to 0.061) | 0 by definition | 0.045 (0.042 to 0.045) |

The reference row is not an estimator and was not pre-registered: it is the bar any plan has to clear. The best plan's gain over the observed allocation, as a share of the observed allocation's incremental revenue: seed 101 6.5%, seed 102 6.5%, seed 103 6.4%, seed 104 6.5%, seed 105 6.0% at [0.5, 2.0]; 4.7%, 4.7%, 4.6%, 4.7%, 4.4% at [0.7, 1.3].

Regret seed by seed, multipliers in [0.5, 2.0]:

| estimator | arm | 101 | 102 | 103 | 104 | 105 |
|---|---|---|---|---|---|---|
| Meridian | national | 0.058 | 0.038 | 0.078 | 0.026 | 0.079 |
| Meridian | geo | 0.030 | 0.108 | — | — | — |
| Robyn | national | 0.033 | 0.043 | 0.132 | 0.005 | 0.081 |
| oracle L2 | national | 0.021 | 0.000 | 0.009 | 0.005 | 0.001 |
| oracle L3 | national | 0.035 | 0.011 | 0.021 | 0.013 | 0.032 |
| oracle L6 | national | 0.030 | 0.011 | 0.060 | 0.004 | 0.011 |
| oracle L7 | national | 0.035 | 0.011 | 0.036 | 0.013 | 0.032 |

- every estimator's optimum is a unique vertex: no plan above was picked from a tie.
