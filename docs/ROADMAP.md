# Roadmap

| id | state | machine | model | effort | objective |
|----|-------|---------|-------|--------|-----------|
| C0 | done | any | opus | high | Claude Code infrastructure, this roadmap, and the two session commands |
| C1 | done | karen | sonnet | medium | Robyn 4000x5 for seeds 102-104, so all five extracts share one spec |
| C2 | done | any | sonnet | medium | Per-channel recoverability gate in the simulator checks |
| C3 | next | any | opus | high | Phase 5: score every extract and build the three charts |
| C4 | blocked | any | opus | max | Phase 6: the ~1,000-word article |
| C5 | blocked | any | opus | high | Public README and a fresh-clone reproducibility pass |
| C6 | blocked | any | opus | max | Adversarial audit until the verdict is SHIP |
| C7 | blocked | any | opus | high | Post-publication: PyMC-Marketing as an independent third estimator |

<!-- HEADER-END -->

## How to read this file

One row = one chat = one session that ends in a committable state. The table
above is the whole queue; everything below it is detail, read only once a row
has been picked.

- `state`: todo, next, doing, blocked, done
- `machine`: karen (GPU desktop, admin, WSL2), dell (laptop, no admin), any
- `model`: opus, sonnet, haiku
- `effort`: low, medium, high, max

`/oi` reads only the table. `/tchau` updates the `state` column here and writes
the narrative handoff in `docs/STATUS.md`. This file queues work and never
explains it; that file explains and never queues.


## The model/effort trade-off, stated once

Overshooting costs money, undershooting costs rework. C1 and C2 run a committed
script and make a small, fully specified code change — Opus there is money
thrown away. C3 through C6 are analytical judgment and writing that goes public
under Igor's name, where a wrong framing is not a bug you patch later.

---

## C0 — Infrastructure — Claude Code setup, roadmap, session commands

**Done 2026-09-08.** `.claude/settings.json`, two hooks, the
`publication-auditor` subagent, the `/score` skill, this file, and rewritten
`/oi` and `/tchau`. Also fixed `.gitignore`, which excluded every one of those
paths and would have kept the whole setup off the second machine.

Preceded by the Task-A reassessment (`docs/REASSESSMENT_2026-09-08.md`) and the
oracle ladder (`analysis/oracle.py`, `analysis/ORACLE.md`, `runs/oracle/`).

---

## C1 — Robyn escalation — all five seeds on one documented spec

**Done 2026-09-09.** Seeds 102-104 ran at 4000×5. All three remained
non-converged by Robyn's own check (only seed101 converges at 4000×5; only
seed105 converges, at its pre-registered 2000×5). Escalation did not fix
convergence — a finding, not a defect. RD amendment closed with the dated
result in `runs/robyn/DECISIONS.md`. `/score` runs clean; Robyn national
interval coverage moved to 16% (was reported as ~20% before the escalation).

**Objective.** Run the pending 4000x5 escalation for seeds 102, 103 and 104 so
the committed Robyn extracts stop being a mix of two specs.

**Model/effort: sonnet, medium.** It runs a committed script with known
arguments and commits the JSONs it writes; no analytical judgment is involved.

**Prerequisites.** None. Karen only — needs the WSL2 R environment.

**Why it matters.** `runs/robyn/DECISIONS.md` amendment RD pre-registered one
escalation to 4000x5 for seeds 101-104. Only seed101 ran. Publishing seed101 at
4000x5 next to seeds 102-105 at 2000x5, unexplained, is exactly the kind of
undisclosed inconsistency this project exists to criticize.

**Command.**
```
wsl -d Ubuntu -u igor --cd /mnt/c/<repo> -- Rscript runs/robyn/run_robyn.R --iterations=4000 102 103 104
```
Roughly 20 min per seed on CPU, unattended. Never pass `quiet` — it crashes
Robyn 3.12.1 (friction F8).

**Definition of done.**
- `runs/robyn/results/robyn_national_seed10{2,3,4}.json` each record 4000
  iterations and their own convergence outcome, whatever it is.
- The RD amendment in `runs/robyn/DECISIONS.md` is closed with the result,
  including any seed that still fails Robyn's own convergence check.
- `/score` runs clean over the updated extracts.

**verificar:** `python analysis/scoring.py --results runs --data data/sim --out analysis/out` exits 0, the three JSONs `runs/robyn/results/robyn_national_seed10{2,3,4}.json` each carry `run.convergence_detail.iterations == 4000` (that is the exact path the exporter writes it to — it is not under `extras`), and the RD amendment in `runs/robyn/DECISIONS.md` carries a dated close line naming each seed's convergence outcome.

**Estimate.** 1.5 h, mostly unattended.

**Fallback.** If the escalation cannot run, revert seed101 to its 2000x5 result
so all five share the pre-registered spec. Do not publish the mix.

---

## C2 — Recoverability gate — the check that would have caught this

**Done 2026-09-09.** Added C7 to `simulation/checks.py`: per-channel
signal-to-noise (std of true national contribution / std of national revenue
noise), printed for every seed, WARN-only below floor 0.15. All 5 seeds: ooh
and display fall under the floor in every seed (~0.09-0.12), matching
`analysis/ORACLE.md`'s independent finding that those two are unrecoverable;
`python -m simulation.checks` still exits 0. Documented in `docs/PLAN.md` §3
and `data/README.md`, both referencing `analysis/oracle.py` as the
pre-registered ground-truth step any future scenario should run before a GPU
commitment — C7 is disclosed as a cheap proxy, not a replacement for the
oracle.

**Objective.** Add a per-channel signal-to-noise floor to `simulation/checks.py`
and register the oracle as a pre-run step, so no future scenario reaches a GPU
before someone knows whether its truth is recoverable.

**Model/effort: sonnet, medium.** The analysis is already done and written up in
`analysis/ORACLE.md`; this is a small, fully specified code and docs change.

**Prerequisites.** None — runs in parallel with C1, on either machine.

**Why it matters.** Check C3 gates only the *total* media variance share into
[0.10, 0.35]. All five seeds passed it with roughly 85% of the media signal in
one channel and four channels below 1% each. The oracle later showed two of
those four are not recoverable by any estimator.

**Definition of done.**
- `python -m simulation.checks` prints a per-channel signal-to-noise line for
  every seed and **warns** (does not fail) below the floor — the v1 scenario has
  two channels under it, and that is a documented finding, not a regression.
- `docs/PLAN.md` §3 and `data/README.md` document the gate and the fact that v1
  was validated without it.
- `analysis/ORACLE.md` is referenced from `docs/PLAN.md` as a pre-registered
  step for any future scenario.

**verificar:** `python -m simulation.checks` exits 0 and prints one per-channel signal-to-noise line per seed, and `grep -c 'signal-to-noise' docs/PLAN.md data/README.md` returns non-zero for both.

**Estimate.** 1.5 h.

---

## C3 — Phase 5 — scoring and the three charts

**Objective.** Run the pre-registered harness over all committed extracts
(Meridian, Robyn, and the four oracle rungs) and build the three charts PLAN
Phase 5 specifies.

**Model/effort: opus, high.** Chart design and the oracle-versus-tools framing
are judgment calls that determine what the article can claim.

**Prerequisites.** C1 (so the Robyn numbers are final).

**Definition of done.**
- `analysis/out/summary.md` committed — the provenance every published number
  cites (a `summary.csv` is also un-ignored if a machine-readable form helps).
  The rest of `analysis/out/` stays gitignored and regenerable.
- Three figures in `analysis/figures/`: (1) estimated vs true ROI per channel
  per tool, **with the oracle as a third series** — that addition is what turns
  a tie into a result; (2) response curves against truth; (3) interval coverage
  and width.
- Every number in every figure regenerable by `/score` from committed inputs.
- Charts state that the data is simulated, in the caption, not the footnote.

**verificar:** `analysis/out/summary.md` is tracked by git (`git ls-files --error-unmatch` succeeds), `analysis/figures/` holds three files, and `python analysis/scoring.py --results runs --data data/sim --out <tmp>` reproduces every figure's numbers.

**Estimate.** 3 h.

---

## C4 — Article — the ~1,000-word piece

**Objective.** Write the article around the revised thesis: both tools missed by
roughly half, so did an oracle handed the true parameters, and the interesting
question is which channels were recoverable at all.

**Model/effort: opus, max.** This is the public deliverable; a wrong framing
costs the whole piece and cannot be patched after publication.

**Prerequisites.** C3.

**Definition of done.**
- `article/` holds ~1,000 words with: setup, results (conditional verdict, never
  an absolute winner), a decision guide, and **"What neither tool can tell
  you"** — the mandatory section, specific to what was actually run.
- Says the dataset is simulated up front, not in a caveat.
- States the exact versions (Meridian 1.8.0, Robyn 3.12.1) and that Meridian
  2.0.0 shipped 2026-09-03 with a different default backend.
- Never claims a production MMM was built. The permitted phrasing is a
  comparative analysis on simulated data.
- Every number traces to `analysis/out/summary.md` or a committed result JSON.

**verificar:** `article/` exists, its word count is 800-1300, it contains the literal heading "What neither tool can tell you", and `grep -i` finds both "simulated" and "1.8.0" in it.

**Estimate.** 4 h.

---

## C5 — Public README and reproducibility

**Objective.** Rewrite the README for a public audience and prove a fresh clone
reproduces the analysis.

**Model/effort: opus, high.** Public-facing writing, plus a verification that
has to actually be executed rather than asserted.

**Prerequisites.** C4.

**Definition of done.**
- README states the question, the answer, the limitations, and how to re-run.
- A fresh clone runs simulation -> checks -> oracle -> scoring from the
  documented commands, on a machine without the model environments.
- The version table is complete and pinned, including the `tfp-nightly` pin
  oddity and its risk.
- Full history passes the public test: no hostnames, no absolute local paths, no
  real data, no forbidden phrasing, anywhere in any commit.

**verificar:** A clone into an empty directory runs `python -m simulation.generate`, `python -m simulation.checks`, `python analysis/oracle.py` and `python analysis/scoring.py` with exit 0 using only README instructions, on a machine without the model environments.

**Estimate.** 2.5 h.

---

## C6 — Adversarial audit — SHIP or fix

**Objective.** Run `publication-auditor` against the finished piece and act on
every finding until the verdict is SHIP.

**Model/effort: opus, max.** It is the last gate before publication and its job
is to find what every earlier pass missed.

**Prerequisites.** C5.

**Definition of done.**
- The auditor returns SHIP.
- Every BLOCK finding is fixed, or explicitly disclosed in the limitations
  section with the reason it was not fixed.
- The audit output is committed alongside the piece, so the reader can see the
  piece was adversarially reviewed and what it was reviewed for.

**verificar:** The `publication-auditor` output is committed under `analysis/` and its last line reads `VERDICT: SHIP`.

**Estimate.** 2 h.

---

## Not in this roadmap

Stretch arms S1-S4 and the rest of `docs/BACKLOG.md`, including a Meridian
GeoX calibration arm. The scope guard stands: the Robyn-dormancy timing angle
is perishable and nothing below v1 may delay publication. Reopen the backlog
after C6 ships.

The one backlog item that has been promoted into the queue is PyMC-Marketing,
now **C7** — still post-publication, still blocked behind C6, but written down
with its fairness trap so it does not have to be rediscovered.

One adjacent item worth queuing later: a git `pre-commit` hook mirroring
`.claude/hooks/guard_publication.py`, so the same protections apply to commits
made outside Claude Code. It belongs in the idempotent `envs/` setup scripts,
because `.git/hooks/` does not travel through git.

---

## C7 — Third estimator — PyMC-Marketing, after v1 ships

**Objective.** Run PyMC-Marketing on the same simulated data through the same
pre-registered harness, and find out what value *it* collapses toward.

**Model/effort: opus, high.** The exporter is mechanical, but the input mapping
is a fairness decision with a known trap (below), and interpreting a third
anchor is the analytical part.

**Prerequisites.** C6. **This is explicitly post-publication** — it must not
delay v1. The Robyn-dormancy timing angle is perishable; this is not.

**Why it is worth doing at all, given the oracle already exists.** The oracle
settled the defensive question — it proves the failure is not a simulator bug,
which is what a third tool would only have argued by accumulation. What remains
is a genuinely open question the oracle cannot answer: Meridian shrinks toward
the median of its ROI prior (~1.22), Robyn toward a single spend-proportional
ROI. **A third independent estimator either collapses toward an anchor of its
own — which makes "the estimate is the tool's prior, not a measurement" a
pattern instead of a coincidence — or it does not, which is more interesting
still.** Secondary: the only published benchmark involving Meridian was written
by PyMC Labs, the vendor of the tool that won it. A run by someone with no horse
in the race is worth something.

**The trap, and it is the whole fairness problem.** PyMC-Marketing's default
saturation is **logistic**, not Hill. The generator uses geometric adstock +
Hill precisely because that is the intersection of Meridian's and Robyn's model
families (PLAN D3) — it is *not* inside PyMC's default. Running PyMC on its
defaults would hand it a functional form it does not have, and any resulting
error would be a statement about the mismatch, not about the tool. Two honest
options, and the choice must be pre-registered before the first run, in a
`runs/pymc/DECISIONS.md` written the way MD1-MD11 and RD1-RD13 were:

1. Configure PyMC with a Hill saturation transform, matching the others, and
   disclose that this is not its default; or
2. Run it on its default logistic and report it as a *third* scenario — the
   "nobody's functional form" question, which is stretch arm S4 — never mixed
   into the same table as the other two.

Option 1 keeps the comparison like-for-like and is the recommended one. Do not
average the two.

**Also decide before starting.** The repo name `mmm-meridian-vs-robyn` becomes
wrong. A GitHub rename redirects old URLs, so it is cheap — but it is a decision
to make deliberately, not a side effect, and the published article's links point
here.

**verificar:** `runs/pymc/results/pymc_national_seed10{1..5}.json` exist in the
v1.0 schema, `python analysis/scoring.py --results runs --data data/sim --out <tmp>`
scores them alongside the existing tool-arms without any change to
`analysis/scoring.py`, `runs/pymc/DECISIONS.md` records the saturation choice
with a date **before** the first run's timestamp, and the pinned version is in
`envs/`.

**Estimate.** 4 h, plus environment setup on a machine with the Python stack.
