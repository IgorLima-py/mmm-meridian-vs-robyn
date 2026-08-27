"""Simulation configuration — the single source of truth for the generating
process.

Every number here is a documented modeling assumption; the rationale for the
functional forms and parameter ranges is in docs/PLAN.md §3 and data/README.md.
Functional forms: geometric adstock (normalized weighted average, Jin et al.
2017 eq. 1-2) followed by Hill saturation (eq. 4-5) — the intersection of
Meridian's and Robyn's model families.
"""

GENERATOR_VERSION = "1.0.0"

# Dataset seeds for the primary arm (PLAN D9).
SEEDS = [101, 102, 103, 104, 105]

CONFIG = {
    "version": GENERATOR_VERSION,

    # Panel
    "n_geos": 8,
    "pop_shares": [0.28, 0.18, 0.14, 0.11, 0.09, 0.08, 0.07, 0.05],
    "total_population": 50_000_000,
    "n_weeks": 156,                 # modeling window: 3 years, weekly
    "warmup_weeks": 26,             # simulated before the window for adstock
                                    # burn-in, then dropped from all outputs
    "window_start": "2023-01-02",   # a Monday
    "adstock_max_lag": 13,          # weeks (Jin et al. 2017 use L=13)

    # Baseline: geo-share-scaled level x trend x seasonality x holidays
    "baseline": {
        "national_weekly": 5_000_000.0,     # revenue units per week at t=0
        "trend_total": 0.10,                # +10% linearly over the window
        "seasonality": [[1, 0.09], [2, 0.04]],   # [yearly harmonic, amplitude]
        "seasonality_phase": [0.0, 0.8],
        "holidays": [                        # [month, day, uplift] -> applied
            [11, 25, 0.25],                  # to the week containing the date
            [12, 25, 0.18],
            [5, 15, 0.10],
        ],
    },

    # One national control variable, AR(1) around a level of 100.
    "control": {
        "name": "competitor_index",
        "ar_rho": 0.85,
        "ar_sigma": 1.5,
        "mean": 100.0,
        # revenue effect: -gamma * (index-100)/100 * geo_share * national_weekly
        "gamma": 1.0,
    },

    # Weekly iid Gaussian noise per geo, sd = cv * geo baseline level.
    "noise_cv_geo": 0.07,

    # Channels. Units:
    #   mean_weekly_spend: national, revenue units
    #   cost_per_unit: spend per 1000 exposure units (CPM-like)
    #   adstock_alpha: geometric retention (equals Robyn's theta; inside
    #                  Robyn's recommended bounds per channel type - PLAN D5)
    #   hill_k: half-saturation, in units of mean adstocked exposure per capita
    #   hill_s: Hill slope (S>1 => S-shaped curve)
    #   true_roi: calibration target = incremental revenue / spend, full window
    "channels": {
        "tv":      {"mean_weekly_spend": 300_000, "cost_per_unit": 12.0,
                    "adstock_alpha": 0.7, "hill_k": 1.2, "hill_s": 2.0,
                    "true_roi": 1.8},
        "ooh":     {"mean_weekly_spend": 80_000, "cost_per_unit": 6.0,
                    "adstock_alpha": 0.6, "hill_k": 1.0, "hill_s": 1.0,
                    "true_roi": 0.8},
        "social":  {"mean_weekly_spend": 120_000, "cost_per_unit": 7.0,
                    "adstock_alpha": 0.3, "hill_k": 0.8, "hill_s": 0.9,
                    "true_roi": 2.5},
        "display": {"mean_weekly_spend": 90_000, "cost_per_unit": 5.0,
                    "adstock_alpha": 0.4, "hill_k": 0.9, "hill_s": 0.8,
                    "true_roi": 1.2},
        "search":  {"mean_weekly_spend": 180_000, "cost_per_unit": 25.0,
                    "adstock_alpha": 0.1, "hill_k": 0.85, "hill_s": 0.7,
                    "true_roi": 3.5},
    },

    # National spend patterns: always-on base + flights + lognormal wiggle.
    # ooh copies tv's flight calendar (shifted) and correlates its wiggle with
    # tv's -> the deliberate multicollinearity dial (PLAN §3).
    "spend_patterns": {
        "tv":      {"base": 0.50, "flights_per_52w": 4, "flight_len": 4,
                    "amp": 2.0, "wiggle_sd": 0.12},
        "ooh":     {"base": 0.50, "flights_per_52w": 4, "flight_len": 4,
                    "amp": 1.85, "wiggle_sd": 0.12,
                    "copy_calendar_of": "tv", "calendar_shift_max": 1,
                    "calendar_overlap": 0.75,
                    "wiggle_corr_with": ["tv", 0.6]},
        "social":  {"base": 0.70, "flights_per_52w": 5, "flight_len": 3,
                    "amp": 1.75, "wiggle_sd": 0.12},
        "display": {"base": 0.70, "flights_per_52w": 4, "flight_len": 3,
                    "amp": 1.65, "wiggle_sd": 0.12},
        "search":  {"base": 0.70, "flights_per_52w": 3, "flight_len": 2,
                    "amp": 1.45, "wiggle_sd": 0.10},
    },

    # Geo-level texture: allocation tilt (AR(1) in logs), fixed per-geo CPM
    # factors, and weekly impression noise. Gives the geo arm real variation.
    "geo": {
        "tilt_rho": 0.9,
        "tilt_sigma": 0.04,
        "cpm_geo_sd": 0.08,
        "impression_noise_sd": 0.06,
    },

    # Ground-truth outputs
    "response_curve_multipliers": [0.0, 0.25, 0.5, 0.75, 1.0,
                                   1.25, 1.5, 2.0, 2.5, 3.0],
    "mroi_delta": 0.01,
}
