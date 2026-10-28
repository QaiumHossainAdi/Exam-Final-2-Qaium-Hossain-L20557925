"""Probabilistic diagnosis of a low strength test (naive Bayes).

Evidence is read from the test record; the likelihood tables live in the config,
so they can be revised from expert judgment or learned from confirmed cases.
"""
import pandas as pd

from .config import load_config


def extract_evidence(record: dict, cfg=None):
    """Turn a pour/test record into yes/no evidence. Missing data -> None (skipped).

    record keys (all optional): companion_range_pct, range_limit_pct, fracture_type,
    slump_design_in, slump_ticket_in, air_spec_pct, air_ticket_pct, cure_temp_F,
    minutes_batch_to_place
    """
    th = (cfg or load_config())["diagnosis"]["thresholds"]
    g = lambda k: None if record.get(k) is None or pd.isna(record.get(k)) else record[k]
    ev = {}
    r, lim = g("companion_range_pct"), g("range_limit_pct")
    ev["companion_range_high"] = None if r is None or lim is None else r > lim
    ft = g("fracture_type")
    ev["fracture_abnormal"] = None if ft is None else int(ft) not in th["normal_fracture_types"]
    sd, st = g("slump_design_in"), g("slump_ticket_in")
    ev["slump_over_design"] = None if sd is None or st is None else st - sd > th["slump_excess_in"]
    a_s, a_t = g("air_spec_pct"), g("air_ticket_pct")
    ev["air_over_spec"] = None if a_s is None or a_t is None else a_t - a_s > th["air_excess_pct"]
    ct = g("cure_temp_F")
    ev["cure_temp_out"] = None if ct is None else not (th["cure_temp_F"][0] <= ct <= th["cure_temp_F"][1])
    mins = g("minutes_batch_to_place")
    ev["late_delivery"] = None if mins is None else mins > th["max_minutes"]
    return ev


def diagnose(evidence: dict, cfg=None):
    """Posterior probability of each cause given the observed evidence.

    Returns a DataFrame sorted by probability with the recommended next step.
    """
    d = (cfg or load_config())["diagnosis"]
    post = {}
    for cause, info in d["causes"].items():
        p = info["prior"]
        for ev_name, present in evidence.items():
            if present is None:
                continue
            like = d["evidence"][ev_name][cause]
            p *= like if present else (1 - like)
        post[cause] = p
    total = sum(post.values()) or 1.0
    rows = [{"cause": d["causes"][c]["label"], "probability": p / total,
             "next_step": d["causes"][c]["next_step"], "key": c} for c, p in post.items()]
    return pd.DataFrame(rows).sort_values("probability", ascending=False).reset_index(drop=True)


def explain(evidence: dict):
    """Plain-language list of the evidence used."""
    names = {"companion_range_high": "companion cylinders disagree beyond ASTM C39 range",
             "fracture_abnormal": "abnormal fracture type",
             "slump_over_design": "ticket slump well above design",
             "air_over_spec": "air content above specification",
             "cure_temp_out": "initial curing temperature outside 60-80 F",
             "late_delivery": "more than 90 minutes from batching to placement"}
    return [(names[k], "yes" if v else "no") for k, v in evidence.items() if v is not None]
