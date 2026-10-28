"""Create SYNTHETIC presentation pour logs, one per application preset (data/presentation/*.csv).

Values are realistic but invented: plant mean strength near f'cr with a typical
standard deviation, 7-day breaks about 70% of 28-day (Type I cement), ticket slump,
air and delivery times near spec. Each log also contains a few planted problem
pours so every part of the app has something to show. Not real project data.
"""
from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent.parent / "data" / "presentation"

# Each scenario: preset key, f'c, mean/sd of 28-day strength, design slump, air spec,
# typical curing temperature, pour dates, locations, and planted problem pours.
SCENARIOS = {
    "bridge_deck_deicing": dict(
        fc=5000, mean=6150, sd=380, slump=4.0, air=6.0, cure=72, start="2026-01-05", every=7,
        locations=[f"Deck span {i}" for i in (1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4)],
        problems={6: "water_added", 10: "testing_problem", 13: "high_air", 15: "early_risk"}),
    "road_pavement": dict(
        fc=4500, mean=5650, sd=420, slump=1.5, air=5.5, cure=74, start="2026-05-04", every=4,
        locations=[f"Lane {1 + (i // 8)}, Sta {10 + i % 8}+00" for i in range(16)],
        problems={4: "high_air", 9: "water_added", 12: "testing_problem", 15: "early_risk"}),
    "parking_lot": dict(
        fc=3500, mean=4650, sd=360, slump=4.0, air=4.5, cure=70, start="2026-04-06", every=5,
        locations=[f"Bay {b}" for b in "AAABBBBCCCCDDDEE"],
        problems={7: "low_average", 8: "low_average", 9: "low_average", 12: "cold_curing", 15: "early_risk"}),
    "interior_slab": dict(
        fc=4000, mean=5150, sd=400, slump=4.0, air=None, cure=68, start="2025-11-03", every=6,
        locations=[f"Level {1 + i // 6}, Grid {'ABCDEF'[i % 6]}-{'BCDEFG'[i % 6]}" for i in range(16)],
        problems={5: "batching_error", 9: "cold_curing", 11: "testing_problem", 15: "early_risk"}),
}


def pour(rng, s, f28, problem=None):
    """One pour record. f28 is the true 28-day strength of the load."""
    r = dict(fracture_type=int(rng.choice([1, 2, 3])),
             slump_design_in=s["slump"],
             slump_ticket_in=round(float(np.clip(rng.normal(s["slump"], 0.4), s["slump"] - 1.0, s["slump"] + 0.9)), 1),
             air_spec_pct=s["air"] if s["air"] is not None else 3.0,
             air_ticket_pct=round(float(rng.normal(s["air"], 0.4)) if s["air"] is not None else float(rng.normal(1.8, 0.3)), 1),
             cure_temp_F=int(np.clip(rng.normal(s["cure"], 3), 62, 78)),
             minutes_batch_to_place=int(np.clip(rng.normal(55, 12), 25, 85)))
    spread = 0.02          # companion cylinders agree within ASTM C39 range
    if problem == "water_added":          # extra water on site, late truck
        f28 = s["fc"] * 0.80
        r.update(slump_ticket_in=round(s["slump"] + 3.0, 1), minutes_batch_to_place=112)
    elif problem == "high_air":           # admixture overdose
        f28 = s["fc"] * 0.84
        r.update(air_ticket_pct=round((s["air"] or 3.0) + 2.6, 1))
    elif problem == "batching_error":     # short on cement, everything else normal
        f28 = s["fc"] * 0.83
    elif problem == "cold_curing":        # cylinders left in the cold the first day
        f28 = s["fc"] * 0.84
        r.update(cure_temp_F=46)
    elif problem == "low_average":        # gradual drift: each test passes alone, average does not
        f28 = s["fc"] * rng.uniform(0.95, 0.99)
    if problem == "testing_problem":      # one bad cylinder, bad fracture, cold box; the concrete itself is fine
        c1, c2 = s["fc"] * 1.02, s["fc"] * 0.66
        r.update(fracture_type=5, cure_temp_F=54)
    else:
        c1, c2 = f28 * rng.normal(1, spread), f28 * rng.normal(1, spread)
    ratio = rng.normal(0.70, 0.015)
    r.update(cyl1_7d=round(c1 * ratio), cyl2_7d=round(c2 * ratio), cyl1_28d=round(c1), cyl2_28d=round(c2))
    return r


def make(key, s, seed):
    rng = np.random.default_rng(seed)
    dates = pd.date_range(s["start"], periods=16, freq=f"{s['every']}D")
    rows = []
    for i in range(16):
        prob = s["problems"].get(i)
        # normal pours: keep clear of the limits so only planted problems show up
        f28 = float(np.clip(rng.normal(s["mean"], s["sd"]), s["fc"] + 350, s["mean"] + 2 * s["sd"]))
        if prob == "early_risk":
            f28 = s["fc"] * 0.86
        r = pour(rng, s, f28, None if prob == "early_risk" else prob)
        if i >= 14:   # the two latest pours have only 7-day breaks so far
            r.update(cyl1_28d=None, cyl2_28d=None)
        rows.append(dict(pour_id=f"P{i + 1:02d}", date=dates[i].date().isoformat(), location=s["locations"][i],
                         fc_psi=s["fc"], **r))
    cols = ["pour_id", "date", "location", "fc_psi", "cyl1_7d", "cyl2_7d", "cyl1_28d", "cyl2_28d", "fracture_type",
            "slump_design_in", "slump_ticket_in", "air_spec_pct", "air_ticket_pct", "cure_temp_F", "minutes_batch_to_place"]
    df = pd.DataFrame(rows)[cols]
    df["cyl1_28d"] = df["cyl1_28d"].astype("Int64")
    df["cyl2_28d"] = df["cyl2_28d"].astype("Int64")
    return df


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for n, (key, s) in enumerate(SCENARIOS.items()):
        df = make(key, s, seed=100 + n)
        path = OUT / f"{key}.csv"
        df.to_csv(path, index=False)
        print(f"Wrote {path.name} ({len(df)} synthetic pours)")
