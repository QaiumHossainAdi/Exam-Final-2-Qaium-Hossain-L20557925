"""ACI 211.1 absolute-volume mix design (US units), with every step recorded.

Each step is appended to `steps` so an engineer can check the calculation line by line.
"""
from dataclasses import dataclass, field
import numpy as np

from .config import load_config

UNIT_WT_WATER = 62.4  # lb/ft3
YD3_FT3 = 27.0


@dataclass
class MixInputs:
    fc_psi: float
    slump: str = "3-4"                # "1-2", "3-4" or "6-7" in
    nmsa_in: float = 1.0
    air_entrained: bool = False
    air_exposure: str = "mild"       # mild / moderate / severe
    max_wcm: float | None = None     # exposure limit; None = no limit
    std_dev_psi: float | None = None  # plant standard deviation, if known
    n_tests: int | None = None
    fm_fine: float = 2.70
    druw_coarse: float = 100.0       # dry-rodded unit weight, lb/ft3
    sg_cement: float = 3.15
    sg_coarse: float = 2.68
    sg_fine: float = 2.64
    abs_coarse: float = 0.005        # absorption, fraction
    abs_fine: float = 0.007
    mc_coarse: float = 0.010         # field moisture content, fraction
    mc_fine: float = 0.040
    fcr_psi: float | None = None     # set to use your own f'cr instead of the ACI rule


@dataclass
class MixResult:
    fcr_psi: float
    wc: float
    air_pct: float
    ssd_lb: dict        # per yd3, SSD aggregates
    field_lb: dict      # per yd3, corrected for stockpile moisture
    ratio: str          # cement : fine : coarse by mass (SSD)
    steps: list = field(default_factory=list)
    warnings: list = field(default_factory=list)


def required_average_strength(fc, std_dev=None, n_tests=None, cfg=None):
    """ACI 318-19 26.4.3 / ACI 301 required average strength f'cr. Returns (fcr, explanation)."""
    cfg = cfg or load_config()
    if std_dev is None:
        if fc < 3000:
            return fc + 1000, "No strength records: f'cr = f'c + 1000"
        if fc <= 5000:
            return fc + 1200, "No strength records: f'cr = f'c + 1200"
        return 1.10 * fc + 700, "No strength records: f'cr = 1.10 f'c + 700"

    k = 1.0
    if n_tests is not None:
        if n_tests < 15:
            raise ValueError("Fewer than 15 tests: use the no-records rule (std_dev=None).")
        k = float(np.interp(n_tests, cfg["fcr"]["s_modifier_tests"], cfg["fcr"]["s_modifier"]))
    s = std_dev * k
    a = fc + 1.34 * s
    b = fc + 2.33 * s - 500 if fc <= 5000 else 0.90 * fc + 2.33 * s
    return max(a, b), f"s = {std_dev:.0f} x {k:.2f} = {s:.0f} psi; f'cr = max({a:.0f}, {b:.0f})"


def _nmsa_index(nmsa, sizes):
    for i, s in enumerate(sizes):
        if abs(s - nmsa) < 1e-6:
            return i
    raise ValueError(f"Nominal max size {nmsa} in not in table {sizes}")


def design_mix(inp: MixInputs, cfg=None) -> MixResult:
    cfg = cfg or load_config()
    t = cfg["aci211"]
    steps, warnings = [], []

    # Step 1: required average strength
    if inp.fcr_psi is not None:
        fcr, why = inp.fcr_psi, "f'cr given by user"
    else:
        fcr, why = required_average_strength(inp.fc_psi, inp.std_dev_psi, inp.n_tests, cfg)
    steps.append(("1. Required average strength", f"{why} -> f'cr = {fcr:.0f} psi"))

    # Step 2: mixing water and air
    i = _nmsa_index(inp.nmsa_in, t["nmsa_in"])
    table = t["water_ae"] if inp.air_entrained else t["water_non_ae"]
    water = float(table[inp.slump][i])
    air = float(t["total_air_pct"][inp.air_exposure][i]) if inp.air_entrained else float(t["entrapped_air_pct"][i])
    kind = f"air-entrained, {inp.air_exposure} exposure" if inp.air_entrained else "non-air-entrained"
    steps.append(("2. Water and air", f"Slump {inp.slump} in, NMSA {inp.nmsa_in} in, {kind}: water = {water:.0f} lb/yd3, air = {air:.1f}%"))

    # Step 3: water-cement ratio from strength, then exposure limit
    if inp.air_entrained:
        xs, ys = t["wc_ae_strength_psi"], t["wc_ae"]
    else:
        xs, ys = t["wc_strength_psi"], t["wc_non_ae"]
    if fcr > xs[-1]:
        warnings.append(f"f'cr {fcr:.0f} psi is above the ACI 211.1 table ({xs[-1]} psi). w/c is extrapolated; use trial batches.")
        # Abrams-type fit ln(f) = c0 + c1 * w/c through the table, solved for w/c
        c1, c0 = np.polyfit(ys, np.log(xs), 1)
        wc_strength = float((np.log(fcr) - c0) / c1)
    else:
        wc_strength = float(np.interp(fcr, xs, ys))
    wc = wc_strength
    detail = f"Strength table: w/c = {wc_strength:.3f}"
    if inp.max_wcm is not None and inp.max_wcm < wc:
        wc = inp.max_wcm
        detail += f"; exposure limit {inp.max_wcm:.2f} governs"
    steps.append(("3. Water-cement ratio", f"{detail} -> w/c = {wc:.3f}"))

    # Step 4: cement
    cement = water / wc
    steps.append(("4. Cement", f"{water:.0f} / {wc:.3f} = {cement:.0f} lb/yd3"))
    if cement > 750:
        warnings.append(f"Cement content {cement:.0f} lb/yd3 is very high (heat, shrinkage, cost). "
                        "Use a water reducer to cut water, add SCMs, or run the optimizer.")

    # Step 5: coarse aggregate
    fm = min(max(inp.fm_fine, t["coarse_fm"][0]), t["coarse_fm"][-1])
    if fm != inp.fm_fine:
        warnings.append(f"Fineness modulus {inp.fm_fine} is outside 2.40-3.00; table value at {fm} used.")
    vol_frac = float(np.interp(fm, t["coarse_fm"], t["coarse_volume"][i]))
    coarse_od = vol_frac * YD3_FT3 * inp.druw_coarse
    coarse = coarse_od * (1 + inp.abs_coarse)
    steps.append(("5. Coarse aggregate", f"Volume fraction {vol_frac:.3f} (FM {fm:.2f}) x 27 ft3 x {inp.druw_coarse:.0f} lb/ft3 = {coarse_od:.0f} lb dry -> {coarse:.0f} lb SSD"))

    # Step 6: fine aggregate by absolute volume
    v_water = water / UNIT_WT_WATER
    v_cement = cement / (inp.sg_cement * UNIT_WT_WATER)
    v_coarse = coarse / (inp.sg_coarse * UNIT_WT_WATER)
    v_air = air / 100 * YD3_FT3
    v_fine = YD3_FT3 - (v_water + v_cement + v_coarse + v_air)
    fine = v_fine * inp.sg_fine * UNIT_WT_WATER
    steps.append(("6. Fine aggregate (absolute volume)",
                  f"27 - (water {v_water:.2f} + cement {v_cement:.2f} + coarse {v_coarse:.2f} + air {v_air:.2f}) = {v_fine:.2f} ft3 -> {fine:.0f} lb SSD"))
    if v_fine <= 0:
        raise ValueError("No volume left for fine aggregate; check inputs.")

    # Step 7: moisture correction (SSD -> stockpile condition)
    def wet(ssd, mc, ab):
        return ssd * (1 + mc) / (1 + ab), ssd * (mc - ab) / (1 + ab)
    coarse_wet, free_c = wet(coarse, inp.mc_coarse, inp.abs_coarse)
    fine_wet, free_f = wet(fine, inp.mc_fine, inp.abs_fine)
    water_batch = water - free_c - free_f
    steps.append(("7. Moisture correction",
                  f"Free water from coarse {free_c:+.0f} lb, fine {free_f:+.0f} lb -> batch water {water_batch:.0f} lb"))

    ssd = {"cement": cement, "water": water, "fine_agg": fine, "coarse_agg": coarse}
    fld = {"cement": cement, "water": water_batch, "fine_agg": fine_wet, "coarse_agg": coarse_wet}
    ratio = f"1 : {fine / cement:.2f} : {coarse / cement:.2f}"
    steps.append(("8. Mix ratio (by mass, SSD)", f"cement : fine : coarse = {ratio}, w/c {wc:.2f}"))

    return MixResult(fcr, wc, air, ssd, fld, ratio, steps, warnings)


def inputs_from_preset(preset: dict, **overrides) -> MixInputs:
    kw = dict(fc_psi=preset["fc_psi"], slump=preset["slump"], nmsa_in=preset["nmsa_in"],
              air_entrained=preset["air_entrained"], air_exposure=preset["air_exposure"],
              max_wcm=preset["max_wcm"])
    kw.update(overrides)
    return MixInputs(**kw)
