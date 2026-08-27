"""Core generator: randomness draws, deterministic assembly, ground truth.

Design contract (PLAN D7): all randomness is drawn ONCE per seed in
`draw_randomness`; `media_contributions` is a pure deterministic function of
those draws plus per-channel spend multipliers, so every counterfactual
(zero-out, +1%, response-curve grid) reuses the same noise realizations.
Impressions are linear in spend, so counterfactual impressions are exact
rescalings of the factual ones.
"""

from datetime import date, timedelta

import numpy as np

from .config import CONFIG, GENERATOR_VERSION


def week_dates(cfg=CONFIG):
    """All simulated Mondays, warmup first; window = last n_weeks entries."""
    start = date.fromisoformat(cfg["window_start"]) - timedelta(
        weeks=cfg["warmup_weeks"])
    total = cfg["warmup_weeks"] + cfg["n_weeks"]
    return [start + timedelta(weeks=i) for i in range(total)]


def _flight_flags(rng, n_total_weeks, n_flights, flight_len):
    """0/1 flags for flight weeks, chosen per 52-week block without overlap."""
    flags = np.zeros(n_total_weeks)
    starts_all = []
    for block in range(0, n_total_weeks, 52):
        block_len = min(52, n_total_weeks - block)
        if block_len < flight_len:
            continue
        candidates = rng.permutation(block_len - flight_len + 1)
        accepted = []
        for c in candidates:
            if all(abs(c - a) > flight_len for a in accepted):
                accepted.append(int(c))
            if len(accepted) == n_flights:
                break
        for a in accepted:
            flags[block + a: block + a + flight_len] = 1.0
            starts_all.append(block + a)
    return flags, starts_all


def draw_randomness(seed, cfg=CONFIG):
    """Draw every stochastic element, in a fixed order (determinism contract:
    same seed + same generator version => identical outputs)."""
    rng = np.random.default_rng(seed)
    T = cfg["warmup_weeks"] + cfg["n_weeks"]
    G = cfg["n_geos"]
    channels = list(cfg["channels"])
    d = {"seed": seed, "T": T}

    # 1. flight calendars + wiggle z-scores (channel order = config order)
    d["flight_flags"], d["flight_starts"], d["wiggle_z"] = {}, {}, {}
    for ch in channels:
        pat = cfg["spend_patterns"][ch]
        src = pat.get("copy_calendar_of")
        if src is None:
            flags, starts = _flight_flags(rng, T, pat["flights_per_52w"],
                                          pat["flight_len"])
        else:
            # Share `calendar_overlap` of the source channel's flights
            # (shifted 0..shift_max weeks); fill the rest from an own,
            # independently drawn calendar. This is the correlation dial.
            flen = pat["flight_len"]
            shift = int(rng.integers(0, pat["calendar_shift_max"] + 1))
            src_starts = d["flight_starts"][src]
            n_join = int(round(pat["calendar_overlap"] * len(src_starts)))
            join_idx = set(rng.permutation(len(src_starts))[:n_join].tolist())
            joined = [i in join_idx for i in range(len(src_starts))]
            own_flags, own_starts = _flight_flags(
                rng, T, pat["flights_per_52w"], flen)
            flags = np.zeros(T)
            starts = []
            for s, j in zip(src_starts, joined):
                if j and s + shift + flen <= T:
                    flags[s + shift: s + shift + flen] = 1.0
                    starts.append(s + shift)
            target_n = len(src_starts)
            for s in own_starts:
                if len(starts) >= target_n:
                    break
                lo, hi = max(0, s - 1), min(T, s + flen + 1)
                if flags[lo:hi].sum() == 0:
                    flags[s: s + flen] = 1.0
                    starts.append(s)
        d["flight_flags"][ch] = flags
        d["flight_starts"][ch] = starts
        z = rng.standard_normal(T)
        corr = pat.get("wiggle_corr_with")
        if corr is not None:
            src_ch, rho = corr[0], float(corr[1])
            z = rho * d["wiggle_z"][src_ch] + np.sqrt(1 - rho ** 2) * z
        d["wiggle_z"][ch] = z

    # 2. geo allocation tilts: AR(1) in logs per (channel, geo)
    rho, sig = cfg["geo"]["tilt_rho"], cfg["geo"]["tilt_sigma"]
    tilts = np.zeros((len(channels), G, T))
    for ci in range(len(channels)):
        for g in range(G):
            eps = rng.standard_normal(T) * sig
            for t in range(1, T):
                eps[t] += rho * eps[t - 1]
            tilts[ci, g] = eps
    d["tilts"] = tilts

    # 3. fixed per-(channel, geo) CPM factors; weekly impression noise
    d["cpm_geo"] = np.exp(rng.standard_normal((len(channels), G))
                          * cfg["geo"]["cpm_geo_sd"])
    d["imp_noise"] = np.exp(rng.standard_normal((len(channels), G, T))
                            * cfg["geo"]["impression_noise_sd"])

    # 4. control AR(1)
    c = cfg["control"]
    idx = np.full(T, c["mean"])
    for t in range(1, T):
        idx[t] = (c["mean"] + c["ar_rho"] * (idx[t - 1] - c["mean"])
                  + rng.standard_normal() * c["ar_sigma"])
    d["control_index"] = idx

    # 5. geo revenue noise (standard normal; scaled at assembly)
    d["revenue_noise_z"] = rng.standard_normal((G, T))
    return d


def national_spend(draws, cfg=CONFIG):
    """National weekly spend per channel; window mean == mean_weekly_spend."""
    T, W = draws["T"], cfg["n_weeks"]
    out = {}
    for ch, spec in cfg["channels"].items():
        pat = cfg["spend_patterns"][ch]
        mult = np.where(draws["flight_flags"][ch] > 0, pat["amp"], pat["base"])
        wig = np.exp(pat["wiggle_sd"] * draws["wiggle_z"][ch]
                     - 0.5 * pat["wiggle_sd"] ** 2)
        raw = mult * wig
        out[ch] = raw / raw[T - W:].mean() * spec["mean_weekly_spend"]
    return out


def geo_spend(draws, nat, cfg=CONFIG):
    """Allocate national spend to geos: pop share x AR(1) tilt, renormalized."""
    shares = np.array(cfg["pop_shares"])[:, None]           # G x 1
    out = {}
    for ci, ch in enumerate(cfg["channels"]):
        w = shares * np.exp(draws["tilts"][ci])              # G x T
        w /= w.sum(axis=0, keepdims=True)
        out[ch] = w * nat[ch][None, :]
    return out


def impressions(draws, geo_sp, cfg=CONFIG):
    """Exposure units per (geo, week): spend / CPM * 1000, with fixed geo CPM
    factors and weekly lognormal noise. Linear in spend by construction."""
    out = {}
    for ci, ch in enumerate(cfg["channels"]):
        cpu = cfg["channels"][ch]["cost_per_unit"]
        out[ch] = (geo_sp[ch] / (cpu * draws["cpm_geo"][ci][:, None])
                   * 1000.0 * draws["imp_noise"][ci])
    return out


def adstock_geometric(x, alpha, max_lag):
    """Normalized geometric adstock along axis -1 (Jin et al. eq. 1-2)."""
    w = alpha ** np.arange(max_lag)
    T = x.shape[-1]
    out = np.zeros_like(x, dtype=float)
    for t in range(T):
        lag = min(max_lag, t + 1)
        ww = w[:lag]
        out[..., t] = (x[..., t - lag + 1: t + 1][..., ::-1] * ww).sum(-1) / ww.sum()
    return out


def hill(u, k, s):
    """Hill saturation, Hill(k) = 0.5 (Jin et al. eq. 4)."""
    u = np.maximum(u, 0.0)
    return u ** s / (u ** s + k ** s)


class World:
    """One seed's realized world: factual data plus exact counterfactuals."""

    def __init__(self, seed, cfg=CONFIG):
        self.cfg = cfg
        self.seed = seed
        self.dates = week_dates(cfg)
        self.W = cfg["n_weeks"]
        self.win = slice(cfg["warmup_weeks"], None)          # window weeks
        self.pop = (np.array(cfg["pop_shares"])
                    * cfg["total_population"])               # persons per geo

        self.draws = draw_randomness(seed, cfg)
        self.nat_spend = national_spend(self.draws, cfg)
        self.geo_spend = geo_spend(self.draws, self.nat_spend, cfg)
        self.imp = impressions(self.draws, self.geo_spend, cfg)

        # Normalization reference: national mean exposure per capita over the
        # window (deterministic given the seed; documented in data/README.md).
        self.ref = {ch: self.imp[ch][:, self.win].sum()
                    / (cfg["total_population"] * self.W)
                    for ch in cfg["channels"]}

        # Calibrate beta per capita so full-window counterfactual ROI hits the
        # target exactly (contributions are linear in beta).
        self.beta_pc = {}
        for ch, spec in cfg["channels"].items():
            unit = self._unit_response(ch, 1.0)[:, self.win].sum()
            spend = self.geo_spend[ch][:, self.win].sum()
            self.beta_pc[ch] = spec["true_roi"] * spend / unit

        self._assemble()

    def _unit_response(self, ch, mult):
        """pop_g * Hill(adstock(exposure per capita) / ref) for spend scaled
        by `mult` — the channel response before the beta scale."""
        spec = self.cfg["channels"][ch]
        x_pc = self.imp[ch] * mult / self.pop[:, None]
        ad = adstock_geometric(x_pc, spec["adstock_alpha"],
                               self.cfg["adstock_max_lag"])
        u = ad / self.ref[ch]
        return self.pop[:, None] * hill(u, spec["hill_k"], spec["hill_s"])

    def media_contribution(self, ch, mult=1.0):
        return self.beta_pc[ch] * self._unit_response(ch, mult)

    def adstocked_norm_exposure(self, ch):
        """u series (adstock-normalized exposure) — used by checks vs hill_k."""
        spec = self.cfg["channels"][ch]
        x_pc = self.imp[ch] / self.pop[:, None]
        ad = adstock_geometric(x_pc, spec["adstock_alpha"],
                               self.cfg["adstock_max_lag"])
        return ad / self.ref[ch]

    def _assemble(self):
        cfg, T = self.cfg, self.draws["T"]
        b = cfg["baseline"]
        shares = np.array(cfg["pop_shares"])[:, None]

        t_idx = np.arange(T) - cfg["warmup_weeks"]
        trend = 1.0 + b["trend_total"] * (t_idx / self.W)
        season = np.ones(T)
        for (h, amp), ph in zip(b["seasonality"], b["seasonality_phase"]):
            woy = np.array([d.isocalendar()[1] for d in self.dates])
            season += amp * np.sin(2 * np.pi * h * woy / 52.0 + ph)
        holiday = np.ones(T)
        for month, day, uplift in b["holidays"]:
            for t, d0 in enumerate(self.dates):
                span = [d0 + timedelta(days=i) for i in range(7)]
                if any(x.month == month and x.day == day for x in span):
                    holiday[t] += uplift
        self.baseline = shares * b["national_weekly"] * trend * season * holiday

        c = cfg["control"]
        self.control_effect = (-c["gamma"]
                               * (self.draws["control_index"] - c["mean"])
                               / c["mean"] * shares * b["national_weekly"])

        self.noise = (self.draws["revenue_noise_z"] * cfg["noise_cv_geo"]
                      * shares * b["national_weekly"])

        self.media = {ch: self.media_contribution(ch)
                      for ch in cfg["channels"]}
        self.revenue = (self.baseline + self.control_effect + self.noise
                        + sum(self.media.values()))

    # ---- ground truth ----------------------------------------------------

    def incremental_revenue(self, ch, mult):
        """Window-total incremental revenue of channel ch at spend x mult
        (vs. that channel zeroed out). Additive model => no cross terms."""
        if mult == 0.0:
            return 0.0
        return float(self.media_contribution(ch, mult)[:, self.win].sum())

    def ground_truth(self):
        cfg = self.cfg
        win = self.win
        total_rev = float(self.revenue[:, win].sum())
        total_spend = {ch: float(self.geo_spend[ch][:, win].sum())
                       for ch in cfg["channels"]}
        all_spend = sum(total_spend.values())
        delta = cfg["mroi_delta"]

        gt = {
            "generator_version": GENERATOR_VERSION,
            "seed": self.seed,
            "n_geos": cfg["n_geos"],
            "n_weeks": self.W,
            "window_start": str(self.dates[cfg["warmup_weeks"]]),
            "window_end": str(self.dates[-1]),
            "total_revenue": total_rev,
            "channels": {},
            "variance_decomposition": self._variance_decomposition(),
        }
        for ch, spec in cfg["channels"].items():
            inc = self.incremental_revenue(ch, 1.0)
            inc_up = self.incremental_revenue(ch, 1.0 + delta)
            curve = {
                "multipliers": cfg["response_curve_multipliers"],
                "spend": [m * total_spend[ch]
                          for m in cfg["response_curve_multipliers"]],
                "incremental_revenue": [self.incremental_revenue(ch, m)
                                        for m in
                                        cfg["response_curve_multipliers"]],
            }
            gt["channels"][ch] = {
                "params": {"adstock_alpha": spec["adstock_alpha"],
                           "hill_k": spec["hill_k"],
                           "hill_s": spec["hill_s"],
                           "beta_per_capita": self.beta_pc[ch],
                           "exposure_ref_per_capita": self.ref[ch]},
                "spend_total": total_spend[ch],
                "spend_share": total_spend[ch] / all_spend,
                "true_roi": inc / total_spend[ch],
                "true_mroi": (inc_up - inc) / (delta * total_spend[ch]),
                "true_contribution_share": inc / total_rev,
                "response_curve": curve,
            }
        return gt

    def _variance_decomposition(self):
        win = self.win
        nat = {"baseline": self.baseline[:, win].sum(0),
               "control": self.control_effect[:, win].sum(0),
               "noise": self.noise[:, win].sum(0)}
        for ch in self.cfg["channels"]:
            nat[f"media_{ch}"] = self.media[ch][:, win].sum(0)
        total = sum(nat.values())
        var_total = float(np.var(total))
        out = {k: float(np.var(v) / var_total) for k, v in nat.items()}
        out["media_total"] = float(
            np.var(sum(v for k, v in nat.items()
                       if k.startswith("media_"))) / var_total)
        out["_note"] = ("var(component)/var(total national revenue); shares "
                        "need not sum to 1 (covariances).")
        return out
