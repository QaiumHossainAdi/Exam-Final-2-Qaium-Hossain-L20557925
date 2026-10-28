"""Run with `pytest` or `python tests/test_castcheck.py`."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
from castcheck.config import load_config
from castcheck.mix_design import MixInputs, design_mix, required_average_strength, inputs_from_preset
from castcheck.acceptance import evaluate_tests, individual_limit, strength_test, evaluate_cores
from castcheck.early_strength import failure_probability, aci209_fraction
from castcheck.diagnose import diagnose, extract_evidence
from castcheck.predict import CodeModel
from castcheck.optimize import MixOptimizer, Requirements

CFG = load_config()


def test_aci211_example_1():
    """ACI 211.1 Example 1 (US): non-AE, 3-4 in slump, 1-1/2 in NMSA, f'cr 3500 psi,
    DRUW 100 lb/ft3, FM 2.80. Expected: water 300 lb, air 1%, w/c ~0.62, cement ~484 lb,
    coarse 0.71 x 27 x 100 = 1917 lb (dry)."""
    r = design_mix(MixInputs(fc_psi=3500, fcr_psi=3500, slump="3-4", nmsa_in=1.5, fm_fine=2.80,
                             druw_coarse=100, sg_coarse=2.68, sg_fine=2.64, abs_coarse=0.005, abs_fine=0.007), CFG)
    assert r.ssd_lb["water"] == 300 and r.air_pct == 1.0
    assert abs(r.wc - 0.62) < 0.01
    assert abs(r.ssd_lb["cement"] - 484) < 8
    assert abs(r.ssd_lb["coarse_agg"] / 1.005 - 1917) < 1


def test_fcr_rules():
    assert required_average_strength(2500, cfg=CFG)[0] == 3500
    assert required_average_strength(4000, cfg=CFG)[0] == 5200
    assert round(required_average_strength(6000, cfg=CFG)[0]) == 7300
    # s = 500 psi, 30+ tests, f'c 4000: max(4670, 4665) = 4670
    assert round(required_average_strength(4000, 500, 30, CFG)[0]) == 4670


def test_exposure_limit_governs():
    r = design_mix(inputs_from_preset(CFG["presets"]["bridge_deck_deicing"]), CFG)
    # f'cr 6200 psi is beyond the AE table: w/c is extrapolated, must not exceed the F3 limit
    assert r.wc <= 0.40 and r.warnings


def test_individual_limits():
    assert individual_limit(5000, CFG) == 4500
    assert individual_limit(6000, CFG) == 5400


def test_acceptance_edges():
    df = evaluate_tests(4000, [4000, 4000, 4000, 3500, 3499], cfg=CFG)
    assert list(df["individual_ok"]) == [True, True, True, True, False]
    assert df.loc[3, "verdict"] == "Low average"          # avg 3833 < 4000
    assert df.loc[4, "verdict"] == "Investigate (cores)"


def test_companion_range():
    t = strength_test([5000, 3700], "6x12", CFG)
    assert t["range_ok"] is False and abs(t["strength"] - 4350) < 1e-9


def test_cores():
    assert evaluate_cores(5000, [4300, 4400, 4200], CFG)["adequate"] is True
    assert evaluate_cores(5000, [4300, 4400, 3700], CFG)["adequate"] is False


def test_early_strength():
    assert abs(aci209_fraction(7, 4.0, 0.85) - 0.703) < 0.001
    p = failure_probability(3190, 7, 5000, cfg=CFG)
    assert 4400 < p["estimate_28_psi"] < 4700 and p["p_below_fc"] > 0.5


def test_diagnosis_water_added():
    ev = extract_evidence(dict(slump_design_in=4, slump_ticket_in=7.5, minutes_batch_to_place=105,
                               companion_range_pct=1.8, range_limit_pct=8.0, fracture_type=2), CFG)
    assert diagnose(ev, CFG).loc[0, "key"] == "water_added"


def test_diagnosis_testing_problem():
    ev = extract_evidence(dict(companion_range_pct=29.9, range_limit_pct=8.0, fracture_type=5,
                               cure_temp_F=52, slump_design_in=4, slump_ticket_in=3.2), CFG)
    assert diagnose(ev, CFG).loc[0, "key"] == "testing_problem"


def test_code_model_matches_table():
    m = CodeModel(CFG)
    X = pd.DataFrame([dict(cement=400, slag=0, fly_ash=0, water=0.57 * 400, superplasticizer=0,
                           coarse_agg=1000, fine_agg=800, age=28)])
    assert abs(m.predict(X)[0] * 145.038 - 4000) < 300


def test_optimizer_meets_constraints_and_beats_baseline():
    preset = CFG["presets"]["bridge_deck_deicing"]
    mix = design_mix(inputs_from_preset(preset), CFG)
    req = Requirements(mix.fcr_psi, preset["max_wcm"], mix.air_pct, True, preset["max_fly_ash_frac"],
                       preset["max_slag_frac"], preset["max_total_scm_frac"], preset["min_cementitious_kg"],
                       mix.ssd_lb["water"] / 1.68555)
    opt = MixOptimizer(CodeModel(CFG), req, CFG)
    base = opt.baseline_from_aci(mix.ssd_lb)
    best = opt.solve(weight=1.0, maxiter=150)
    assert bool(best["feasible"][0])
    assert best["w/cm"][0] <= 0.40 + 1e-6
    assert best["CO2_kg_m3"][0] < base["CO2_kg_m3"][0]


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            try:
                fn(); print("PASS", name)
            except Exception as e:
                fails += 1; print("FAIL", name, type(e).__name__, e)
    print(f"{fails} failed"); sys.exit(1 if fails else 0)
