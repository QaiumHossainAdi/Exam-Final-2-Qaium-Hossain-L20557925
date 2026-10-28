"""Estimate 28-day strength from early breaks and the probability of failing acceptance.

Uses the ACI 209R relation f(t) = t / (a + b t) * f28. The spread of the estimate
(prediction_cv) is an assumption until calibrated with your own 7/28-day pairs.
"""
import numpy as np
from scipy.stats import norm

from .config import load_config
from .acceptance import individual_limit


def aci209_fraction(t, a, b):
    return t / (a + b * t)


def estimate_28day(strength_t, age_days, cement_type="Type I", cfg=None):
    p = (cfg or load_config())["early_strength"]["cement_types"][cement_type]
    return strength_t * aci209_fraction(28, p["a"], p["b"]) / aci209_fraction(age_days, p["a"], p["b"])


def failure_probability(strength_t, age_days, fc, cement_type="Type I", cv=None, cfg=None):
    """Return the estimated 28-day strength and the probability it falls below
    the ACI individual-test limit and below f'c."""
    cfg = cfg or load_config()
    cv = cv if cv is not None else cfg["early_strength"]["prediction_cv"]
    mean = estimate_28day(strength_t, age_days, cement_type, cfg)
    sd = mean * cv
    lim = individual_limit(fc, cfg)
    return {"estimate_28_psi": mean, "sd_psi": sd,
            "p_below_individual_limit": float(norm.cdf(lim, mean, sd)),
            "p_below_fc": float(norm.cdf(fc, mean, sd)),
            "individual_limit_psi": lim}


def calibrate(pairs_7_28, age_days=7):
    """Learn the 7-to-28 ratio and its scatter from your own pairs [(f7, f28), ...].

    Returns (mean ratio f28/f7, cv). Use the cv in failure_probability(cv=...).
    """
    arr = np.asarray(pairs_7_28, dtype=float)
    r = arr[:, 1] / arr[:, 0]
    return float(r.mean()), float(r.std(ddof=1) / r.mean()) if len(r) > 1 else None
