"""Create SYNTHETIC batch tickets (target vs actual) matching data/presentation/*.csv.

One file per application (data/presentation/<preset>_batches.csv), same columns as the
live app's data/demo_batches.csv. Tickets agree with the problems planted in the pour logs:
water added on site -> site water; batching error and early risk -> cement short; high air ->
admixture overdosed; testing problem and cold curing -> clean ticket. Not real data.
"""
from pathlib import Path
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_presentation_data import SCENARIOS, OUT  # noqa: E402

# Approved mixes per yd3: lb for materials, fl oz for admixture (illustrative values)
MIXES = {
    "bridge_deck_deicing": dict(cement=517, scm=141, water=263, fine=1150, coarse=1750, admix=30),  # w/cm 0.40
    "road_pavement":       dict(cement=450, scm=150, water=270, fine=1150, coarse=1900, admix=24),  # w/cm 0.45
    "parking_lot":         dict(cement=420, scm=140, water=285, fine=1300, coarse=1750, admix=20),  # w/cm 0.51
    "interior_slab":       dict(cement=470, scm=120, water=295, fine=1350, coarse=1750, admix=18),  # w/cm 0.50
}
SD = {"cement": .004, "scm": .004, "water": .008, "fine": .007, "coarse": .006, "admix": .01}


def make(key, seed):
    s, mix = SCENARIOS[key], MIXES[key]
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(16):
        load = 10.0
        r = {"pour_id": f"P{i + 1:02d}", "load_yd3": load}
        for k, v in mix.items():
            t = v * load
            # normal scatter, kept inside the ASTM C94 tolerances
            dev = float(np.clip(rng.normal(0, SD[k]), -0.008 if k in ("cement", "scm") else -0.018,
                                0.008 if k in ("cement", "scm") else 0.018))
            r[f"{k}_t"], r[f"{k}_a"] = round(t), round(t * (1 + dev))
        r["site_water_gal"] = 0
        prob = s["problems"].get(i)
        if prob == "water_added":
            r["site_water_gal"] = 25
        elif prob == "batching_error":
            r["cement_a"] = round(r["cement_t"] * 0.968)
        elif prob == "high_air":
            r["admix_a"] = round(r["admix_t"] * 1.12)
        elif prob == "early_risk":
            r["cement_a"] = round(r["cement_t"] * 0.978)
        elif prob == "low_average":   # drift inside tolerance: a bit more water, a bit less cement
            r["water_a"] = round(r["water_t"] * 1.022)
            r["cement_a"] = round(r["cement_t"] * 0.994)
        rows.append(r)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for n, key in enumerate(SCENARIOS):
        df = make(key, seed=200 + n)
        path = OUT / f"{key}_batches.csv"
        df.to_csv(path, index=False)
        print(f"Wrote {path.name} ({len(df)} synthetic batch tickets)")
