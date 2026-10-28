"""Strength acceptance per ACI 318-19 26.12.3 (cylinders) and 26.12.6 (cores)."""
import numpy as np
import pandas as pd

from .config import load_config


def individual_limit(fc, cfg=None):
    a = (cfg or load_config())["acceptance"]
    if fc <= a["low_strength_threshold_psi"]:
        return fc - a["individual_minus_psi"]
    return a["individual_fraction_high"] * fc


def strength_test(cylinders, size="6x12", cfg=None):
    """Average companion cylinders into one strength test and check ASTM C39 range.

    Returns dict: strength, range_pct, range_limit_pct (None if not tabulated), range_ok.
    """
    cfg = cfg or load_config()
    c = [float(x) for x in cylinders if x is not None and not pd.isna(x)]
    if not c:
        return {"strength": np.nan, "range_pct": np.nan, "range_limit_pct": None, "range_ok": None}
    avg = float(np.mean(c))
    rng = (max(c) - min(c)) / avg * 100 if len(c) > 1 else 0.0
    limit = cfg["acceptance"]["companion_range_pct"].get(f"{size}_{len(c)}")
    ok = None if limit is None or len(c) < 2 else rng <= limit
    return {"strength": avg, "range_pct": rng, "range_limit_pct": limit, "range_ok": ok}


def evaluate_tests(fc, strengths, labels=None, cfg=None):
    """Apply both ACI 318 criteria to a time-ordered list of 28-day strength tests.

    (a) every average of three consecutive tests >= f'c
    (b) no individual test below f'c - 500 (f'c <= 5000) or 0.90 f'c (f'c > 5000)
    """
    cfg = cfg or load_config()
    lim = individual_limit(fc, cfg)
    labels = labels or [f"Test {i + 1}" for i in range(len(strengths))]
    rows = []
    for i, s in enumerate(strengths):
        avg3 = float(np.mean(strengths[i - 2:i + 1])) if i >= 2 else np.nan
        ind_ok = s >= lim
        avg_ok = None if np.isnan(avg3) else avg3 >= fc
        if not ind_ok:
            verdict = "Investigate (cores)"
            reason = f"{s:.0f} psi is below the individual limit {lim:.0f} psi"
        elif avg_ok is False:
            verdict = "Low average"
            reason = f"3-test average {avg3:.0f} psi is below f'c {fc:.0f} psi; raise the average strength"
        else:
            verdict = "Accept"
            reason = "Meets both criteria" if avg_ok else "Meets individual limit (fewer than 3 tests for the average)"
        rows.append({"test": labels[i], "strength_psi": round(s), "avg_of_3_psi": None if np.isnan(avg3) else round(avg3),
                     "individual_ok": ind_ok, "average_ok": avg_ok, "verdict": verdict, "reason": reason})
    return pd.DataFrame(rows)


def evaluate_cores(fc, cores, cfg=None):
    """ACI 318-19 26.12.6.1: average of three cores >= 0.85 f'c and no core < 0.75 f'c."""
    a = (cfg or load_config())["acceptance"]
    avg = float(np.mean(cores))
    avg_lim, one_lim = a["core_avg_fraction"] * fc, a["core_single_fraction"] * fc
    ok = avg >= avg_lim and min(cores) >= one_lim
    return {"average_psi": avg, "average_limit_psi": avg_lim, "min_psi": min(cores),
            "single_limit_psi": one_lim, "adequate": ok}
