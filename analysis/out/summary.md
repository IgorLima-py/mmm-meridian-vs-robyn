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
- seeds passing the tool's own convergence check: 5 of 5

| channel | mean ROI rel err | mean \|ROI rel err\| | effect share − spend share (pp) |
|---|---|---|---|
| display | 0.299 | 1.216 | -2.69 |
| ooh | -0.116 | 0.975 | -7.38 |
| search | -0.186 | 0.319 | +8.56 |
| social | -0.030 | 0.382 | +2.85 |
| tv | -0.008 | 0.098 | -1.34 |

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
- seeds passing the tool's own convergence check: 2 of 5 (not converged: 102, 103, 104)
- run spec: 2000x5 iterations x trials — seeds 105; 4000x5 iterations x trials — seeds 101, 102, 103, 104  **mixed spec: means below blend them**

| channel | mean ROI rel err | mean \|ROI rel err\| | effect share − spend share (pp) |
|---|---|---|---|
| display | -0.428 | 0.428 | -0.35 |
| ooh | -0.156 | 0.230 | -0.55 |
| search | -0.792 | 0.792 | +0.91 |
| social | -0.717 | 0.717 | +0.09 |
| tv | -0.610 | 0.610 | -0.11 |
