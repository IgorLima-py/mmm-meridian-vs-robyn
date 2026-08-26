# BRIEF — Meridian vs Robyn: an MMM Comparison

**What this is:** the same dataset run through the two leading open-source marketing
mix modelling tools — Google Meridian and Meta Robyn — with a simulated ground truth
so the comparison can say which tool recovered reality, under which conditions, and
what neither tool can tell you.

**Effort:** ~8h.

---

## THE ANGLE — and it matters enormously

❌ **This piece does not claim "I built an MMM."**

✅ **It says: "here are two MMM tools, here's how they differ, here's how to read
them."**

That framing is stronger, not weaker:
- It centres the **method's limits**, which is precisely what a sophisticated reader
  tests for
- It's genuinely useful — most people evaluating MMM don't know how to choose
- It's honest
- **Nobody can dispute it**, because it claims a comparison, not a result

---

## THE QUESTION

> **"Same data, two open-source MMM tools. Where do they agree, where do they
> diverge, and what should you do about it?"**

---

## SCOPE

**In:**
- One dataset — ideally **simulated with known ground truth**: several channels
  with known adstock and saturation, seasonality, a trend, and noise
- Run through **Google Meridian** and **Meta Robyn**
- Compare: channel contribution estimates, ROI/mROI, saturation and adstock
  handling, uncertainty representation, prior sensitivity, runtime, setup effort
- **If simulated:** compare both against the known true coefficients — the
  strongest possible version of the piece, because it can state which tool
  recovered reality better under which conditions
- A decision guide: which to pick, when, and why

**Out:**
- Any real advertiser's data
- A claim that either tool is "better" in general — they make different
  assumptions and the honest answer is conditional

---

## METHOD

1. **Build or select the dataset (~2h).** Simulating is more work and much more
   valuable: ground truth turns "the outputs differ" into "this one was closer to
   reality."
2. **Run Meridian (~2h).** Document setup, priors, and every decision made.
3. **Run Robyn (~2h).** Same.
4. **Compare (~1h).** Contribution by channel, recovery of true parameters,
   sensitivity to priors, runtime, setup difficulty.
5. **Write (~1h).** ~1,000 words + comparison table + one chart showing both
   estimates against truth.

---

## THE SECTION THAT MAKES IT CREDIBLE

**"What neither tool can tell you."** Multicollinearity between channels that
always move together, the impossibility of separating effects with no variation,
the fact that priors do more work than most users realise, and why MMM does not
replace incrementality testing.

Practitioners will read that section and conclude the author has actually used
these tools rather than run a tutorial. That is the entire point.

---

## OPEN QUESTIONS FOR THE PLANNING SESSION

Research thoroughly before building:

1. **Current versions and docs** of Meridian and Robyn; installation requirements
   on Windows (Robyn is R-based, Meridian is Python) — check known setup pain.
2. **Demo datasets** each tool ships with — usable? Or is simulation clearly better?
3. **Simulation design:** what does the literature say about simulating MMM data
   with realistic adstock/saturation? Any reference implementations?
4. **Prior art:** existing Meridian-vs-Robyn comparisons — what did they cover,
   what did they miss, what should this piece do differently or better?
5. **Compute:** expected runtime of each tool on a laptop; whether any step needs
   special hardware.

---

## DEFINITION OF DONE

- [ ] Dataset built (ideally simulated with known truth)
- [ ] Both tools run and documented, decisions included
- [ ] Comparison table + chart vs. ground truth
- [ ] "What neither tool can tell you" section written
- [ ] Repo fully reproducible (code + simulated dataset + seeds)
- [ ] Decision guide written

---

## PITFALLS

- **Reproducibility is the credibility signal here** — pin versions, set seeds,
  include the exact configs. A reader must be able to re-run everything.
- **Don't crown a winner.** The honest answer is conditional; the piece says under
  which conditions each tool did better.
- **Don't drift into "I built an MMM" phrasing** anywhere — README, comments,
  commit messages included.
