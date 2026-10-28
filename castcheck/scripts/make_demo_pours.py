"""Create a SYNTHETIC pour log for demos (data/demo_pours.csv). Not real project data."""
from pathlib import Path
import numpy as np
import pandas as pd

rng = np.random.default_rng(7)
rows = []
for i in range(1, 13):
    f28 = rng.normal(6000, 400)
    c1, c2 = f28 * rng.normal(1, 0.02), f28 * rng.normal(1, 0.02)
    rows.append(dict(pour_id=f"P{i:02d}", date=f"2026-0{1 + (i - 1) // 4}-{(i - 1) % 4 * 7 + 3:02d}",
                     location=f"Deck span {(i - 1) // 3 + 1}", fc_psi=5000,
                     cyl1_7d=round(c1 * 0.70), cyl2_7d=round(c2 * 0.70),
                     cyl1_28d=round(c1), cyl2_28d=round(c2), fracture_type=int(rng.choice([1, 2, 3])),
                     slump_design_in=4.0, slump_ticket_in=round(rng.normal(4, 0.4), 1),
                     air_spec_pct=6.0, air_ticket_pct=round(rng.normal(6, 0.4), 1),
                     cure_temp_F=int(rng.normal(72, 3)), minutes_batch_to_place=int(rng.normal(55, 10))))
df = pd.DataFrame(rows)
# P07: water added on site (high slump, late truck)
df.loc[6, ["cyl1_7d", "cyl2_7d", "cyl1_28d", "cyl2_28d", "slump_ticket_in", "minutes_batch_to_place"]] = [3010, 3070, 4300, 4380, 7.5, 105]
# P10: testing problem (companions disagree, bad fracture, cold initial curing)
df.loc[9, ["cyl1_7d", "cyl2_7d", "cyl1_28d", "cyl2_28d", "fracture_type", "cure_temp_F"]] = [3500, 2650, 5000, 3700, 5, 52]
# P12: only 7-day breaks so far, trending low
df.loc[11, ["cyl1_7d", "cyl2_7d"]] = [3150, 3230]
df.loc[11, ["cyl1_28d", "cyl2_28d"]] = [np.nan, np.nan]
out = Path(__file__).resolve().parent.parent / "data" / "demo_pours.csv"
df.to_csv(out, index=False)
print(f"Wrote {out} ({len(df)} synthetic pours)")
