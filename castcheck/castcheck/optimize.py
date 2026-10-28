"""Find the lowest-cost / lowest-carbon mix that still meets strength and durability limits.

Decision variables (kg/m3): cement, slag, fly ash, water, superplasticizer, coarse aggregate.
Fine aggregate fills the remaining volume of 1 m3 (absolute volume method).
Strength comes from any model with .predict() (code relationship or ML).
"""
from dataclasses import dataclass
import numpy as np
import pandas as pd
from scipy.optimize import differential_evolution

from .config import load_config, psi_to_mpa, mpa_to_psi, lbyd3_to_kgm3
from .predict import FEATURES

VARS = ["cement", "slag", "fly_ash", "water", "superplasticizer", "coarse_agg"]
MATERIALS = VARS + ["fine_agg"]


@dataclass
class Requirements:
    fcr_psi: float
    max_wcm: float | None
    air_pct: float
    air_entrained: bool
    max_fly_ash_frac: float = 1.0
    max_slag_frac: float = 1.0
    max_total_scm_frac: float = 1.0
    min_cementitious_kg: float = 0.0
    water_table_kg: float = 0.0      # ACI 211.1 table water for the slump/NMSA, kg/m3


class MixOptimizer:
    def __init__(self, model, req: Requirements, cfg=None):
        self.cfg = cfg or load_config()
        self.model, self.req = model, req
        o, m = self.cfg["optimizer"], self.cfg["materials"]
        self.bounds = [tuple(o["bounds"][v]) for v in VARS]
        self.sg = np.array([m[v]["sg"] for v in MATERIALS])
        self.cost = np.array([m[v]["cost"] for v in MATERIALS])
        self.co2 = np.array([m[v]["co2"] for v in MATERIALS])
        rmse = getattr(model, "rmse_mpa", None) or 0.0
        self.margin_mpa = o["model_margin_k"] * rmse
        self.target_mpa = psi_to_mpa(req.fcr_psi) + self.margin_mpa
        self.air_factor = 1 - (o["air_strength_loss_per_pct"] * max(req.air_pct - 2.0, 0) if req.air_entrained else 0)
        self.cost_ref = self.co2_ref = 1.0

    # ---- evaluation of many candidate mixes at once (columns = candidates) ----
    def complete(self, x):
        x = np.atleast_2d(x)
        vol = (x / (self.sg[:6, None] * 1000)).sum(axis=0) + self.req.air_pct / 100
        fine = (1 - vol) * self.sg[6] * 1000
        return np.vstack([x, fine])          # 7 x S, kg/m3

    def strength(self, full):
        X = pd.DataFrame(full.T, columns=MATERIALS)
        X["age"] = 28.0
        return self.model.predict(X[FEATURES]) * self.air_factor

    def penalties(self, full, f):
        """Engineering requirements only. Zero means the mix meets every requirement."""
        c, s, fa, w, sp, ca, fi = full
        binder = c + s + fa
        o, r = self.cfg["optimizer"], self.req
        p = np.zeros(full.shape[1])
        if r.max_wcm is not None:
            p += np.maximum(w / binder - r.max_wcm, 0) / r.max_wcm
        p += np.maximum(fa / binder - r.max_fly_ash_frac, 0)
        p += np.maximum(s / binder - r.max_slag_frac, 0)
        p += np.maximum((fa + s) / binder - r.max_total_scm_frac, 0)
        p += np.maximum(r.min_cementitious_kg - binder, 0) / max(r.min_cementitious_kg, 1)
        if r.water_table_kg:
            dose = np.minimum(sp / (o["sp_full_dose_frac"] * binder), 1.0)
            w_min = r.water_table_kg * (1 - o["max_sp_water_reduction"] * dose)
            p += np.maximum(w_min - w, 0) / r.water_table_kg
        p += np.maximum(self.target_mpa - f, 0) / self.target_mpa
        p += np.maximum(-fi, 0)
        return p

    def range_penalty(self, full):
        """Distance outside the training-data range for fine aggregate (others are bounded)."""
        lo, hi = self.cfg["optimizer"]["fine_agg_range"]
        fi = full[6]
        return np.maximum(lo - fi, 0) / lo + np.maximum(fi - hi, 0) / hi

    def objective(self, x, weight):
        full = self.complete(x)
        f = self.strength(full)
        cost, co2 = self.cost @ full, self.co2 @ full
        score = (1 - weight) * cost / self.cost_ref + weight * co2 / self.co2_ref
        return score + 100 * (self.penalties(full, f) + self.range_penalty(full))

    # ---- public API ----
    def summarize(self, full):
        full = np.asarray(full, dtype=float)
        full = full if full.ndim == 2 else full[:, None]
        f = self.strength(full)
        df = pd.DataFrame(full.T, columns=MATERIALS)
        binder = df["cement"] + df["slag"] + df["fly_ash"]
        df["w/cm"] = df["water"] / binder
        df["SCM %"] = (df["slag"] + df["fly_ash"]) / binder * 100
        df["strength_MPa"] = f
        df["strength_psi"] = mpa_to_psi(f)
        df["cost_USD_m3"] = self.cost @ full
        df["CO2_kg_m3"] = self.co2 @ full
        df["meets_requirements"] = self.penalties(full, f) < 1e-6
        df["in_data_range"] = self.range_penalty(full) < 1e-9
        df["feasible"] = df["meets_requirements"] & df["in_data_range"]
        return df

    def baseline_from_aci(self, ssd_lb):
        """Convert an ACI 211.1 result (lb/yd3, SSD) into the optimizer's units for comparison."""
        v = {k: lbyd3_to_kgm3(ssd_lb.get(k, 0.0)) for k in ["cement", "water", "coarse_agg", "fine_agg"]}
        full = np.array([[v["cement"]], [0], [0], [v["water"]], [0], [v["coarse_agg"]], [v["fine_agg"]]])
        df = self.summarize(full)
        self.cost_ref, self.co2_ref = float(df["cost_USD_m3"][0]), float(df["CO2_kg_m3"][0])
        return df

    def solve(self, weight=0.5, maxiter=200):
        res = differential_evolution(self.objective, self.bounds, args=(weight,), vectorized=True,
                                     updating="deferred", seed=self.cfg["optimizer"]["seed"],
                                     maxiter=maxiter, popsize=20, tol=1e-7, polish=False)
        return self.summarize(self.complete(res.x[:, None]))

    def pareto(self, n=None, maxiter=200):
        """Sweep cost-vs-carbon weight; return the feasible trade-off mixes."""
        n = n or self.cfg["optimizer"]["pareto_points"]
        out = []
        for w in np.linspace(0, 1, n):
            d = self.solve(w, maxiter)
            d.insert(0, "carbon_weight", round(w, 2))
            out.append(d)
        df = pd.concat(out, ignore_index=True)
        df = df[df["feasible"]].copy()
        key = pd.DataFrame({"c": df["cost_USD_m3"].round(1), "e": df["CO2_kg_m3"].round(0)})
        return df[~key.duplicated()].sort_values("cost_USD_m3").reset_index(drop=True)
