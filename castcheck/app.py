"""CastCheck AI, local app. Run:  streamlit run app.py"""
import numpy as np
import pandas as pd
import streamlit as st

from castcheck.config import load_config, kgm3_to_lbyd3, ROOT, DEFAULT_CONFIG
from castcheck.mix_design import design_mix, inputs_from_preset
from castcheck.acceptance import evaluate_tests, strength_test, evaluate_cores
from castcheck.early_strength import failure_probability
from castcheck.diagnose import extract_evidence, diagnose, explain
from castcheck.optimize import MixOptimizer, Requirements
from castcheck.predict import CodeModel, load_uci, compare_models, save_models, load_models

st.set_page_config(page_title="CastCheck AI", page_icon="🧱", layout="wide")
cfg = load_config()

# ---------------- Sidebar: application and requirements ----------------
st.sidebar.title("CastCheck AI")
st.sidebar.caption("Concrete mix design, optimization, acceptance and diagnosis")
presets = cfg["presets"]
key = st.sidebar.selectbox("Application", list(presets), format_func=lambda k: presets[k]["label"])
p = dict(presets[key])
st.sidebar.caption(f"Exposure class {p['exposure_classes']}. The project specification governs; edit any value.")
p["fc_psi"] = st.sidebar.number_input("Specified f'c (psi)", 2500, 10000, int(p["fc_psi"]), 250)
use_limit = st.sidebar.checkbox("Apply max w/cm", value=p["max_wcm"] is not None)
p["max_wcm"] = st.sidebar.number_input("Max w/cm", 0.30, 0.70, float(p["max_wcm"] or 0.50), 0.01) if use_limit else None
p["slump"] = st.sidebar.selectbox("Slump (in)", ["1-2", "3-4", "6-7"], ["1-2", "3-4", "6-7"].index(p["slump"]))
sizes = cfg["aci211"]["nmsa_in"]
p["nmsa_in"] = st.sidebar.selectbox("Nominal max aggregate size (in)", sizes, sizes.index(p["nmsa_in"]))
p["air_entrained"] = st.sidebar.checkbox("Air-entrained", p["air_entrained"])
with st.sidebar.expander("Aggregate properties"):
    agg = dict(fm_fine=st.number_input("Fine aggregate FM", 2.3, 3.1, 2.70, 0.05),
               druw_coarse=st.number_input("Coarse dry-rodded unit wt (lb/ft3)", 85.0, 115.0, 100.0, 1.0),
               sg_coarse=st.number_input("Coarse SG (SSD)", 2.4, 3.0, 2.68, 0.01),
               sg_fine=st.number_input("Fine SG (SSD)", 2.4, 3.0, 2.64, 0.01),
               abs_coarse=st.number_input("Coarse absorption (%)", 0.0, 5.0, 0.5, 0.1) / 100,
               abs_fine=st.number_input("Fine absorption (%)", 0.0, 5.0, 0.7, 0.1) / 100,
               mc_coarse=st.number_input("Coarse moisture (%)", 0.0, 10.0, 1.0, 0.1) / 100,
               mc_fine=st.number_input("Fine moisture (%)", 0.0, 12.0, 4.0, 0.1) / 100)
    sd_known = st.checkbox("Plant standard deviation known")
    if sd_known:
        agg["std_dev_psi"] = st.number_input("Standard deviation (psi)", 200, 1200, 500, 25)
        agg["n_tests"] = st.number_input("Number of tests", 15, 200, 30, 1)

mix = design_mix(inputs_from_preset(p, **agg), cfg)

# ---------------- Strength models ----------------
if "models" not in st.session_state:
    st.session_state.models = load_models()
models = st.session_state.models or {}
model_choices = {"ACI w/c relationship (no data needed)": CodeModel(cfg)}
if "gbr" in models:
    model_choices = {"Gradient boosting (trained)": models["gbr"], "Linear regression (trained)": models["linear"], **model_choices}

tabs = st.tabs(["Mix design", "Optimize", "Lab results", "Early warning", "Diagnose", "Model comparison", "Settings"])

# ---------------- 1. Mix design ----------------
with tabs[0]:
    st.subheader(f"ACI 211.1 mix design: {presets[key]['label']}")
    for w in mix.warnings:
        st.warning(w)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("f'cr", f"{mix.fcr_psi:,.0f} psi")
    c2.metric("w/c", f"{mix.wc:.2f}")
    c3.metric("Air", f"{mix.air_pct:.1f} %")
    c4.metric("Ratio (C:F:CA)", mix.ratio)
    st.markdown("**Calculation steps**")
    st.dataframe(pd.DataFrame(mix.steps, columns=["Step", "Calculation"]), hide_index=True, use_container_width=True)
    st.markdown("**Batch weights per cubic yard**")
    bw = pd.DataFrame({"SSD (lb)": mix.ssd_lb, "Field, moisture-corrected (lb)": mix.field_lb}).round(0)
    st.dataframe(bw, use_container_width=True)

# ---------------- 2. Optimize ----------------
with tabs[1]:
    st.subheader("Optimize for cost and embodied carbon")
    st.caption("Searches cement, slag, fly ash, water, superplasticizer and aggregate amounts that meet "
               "strength, w/cm, SCM, minimum binder and workability limits, then shows the cost-carbon trade-off.")
    mname = st.selectbox("Strength model", list(model_choices))
    model = model_choices[mname]
    req = Requirements(mix.fcr_psi, p["max_wcm"], mix.air_pct, p["air_entrained"], p["max_fly_ash_frac"],
                       p["max_slag_frac"], p["max_total_scm_frac"], p["min_cementitious_kg"],
                       mix.ssd_lb["water"] / 1.68555)
    if st.button("Run optimizer", type="primary"):
        opt = MixOptimizer(model, req, cfg)
        base = opt.baseline_from_aci(mix.ssd_lb)
        with st.spinner("Searching mixes..."):
            par = opt.pareto()
        if par.empty:
            st.error("No mix met every requirement. Relax a limit in the sidebar or the config file.")
        else:
            st.session_state.opt = (par, base, opt.margin_mpa)
    if "opt" in st.session_state:
        par, base, margin = st.session_state.opt
        b_cost, b_co2 = float(base["cost_USD_m3"][0]), float(base["CO2_kg_m3"][0])
        low_c = par.loc[par["CO2_kg_m3"].idxmin()]
        a, b, c = st.columns(3)
        a.metric("ACI 211.1 mix", f"${b_cost:.0f}/m3", f"{b_co2:.0f} kg CO2e/m3", delta_color="off")
        b.metric("Lowest-cost mix", f"${par['cost_USD_m3'].min():.0f}/m3",
                 f"{(par.loc[par['cost_USD_m3'].idxmin(), 'CO2_kg_m3'] / b_co2 - 1) * 100:+.0f}% CO2e", delta_color="inverse")
        c.metric("Lowest-carbon mix", f"{low_c['CO2_kg_m3']:.0f} kg CO2e/m3",
                 f"{(low_c['CO2_kg_m3'] / b_co2 - 1) * 100:+.0f}% vs ACI mix", delta_color="inverse")
        chart = pd.concat([par.assign(mix="Optimized"), base.assign(mix="ACI 211.1")])
        st.scatter_chart(chart, x="cost_USD_m3", y="CO2_kg_m3", color="mix", size=None)
        show = par.drop(columns=["feasible", "meets_requirements", "in_data_range"]).round(2)
        st.dataframe(show, hide_index=True, use_container_width=True)
        pick = st.selectbox("Show a mix in lb/yd3", range(len(par)),
                            format_func=lambda i: f"${par['cost_USD_m3'][i]:.0f}/m3, {par['CO2_kg_m3'][i]:.0f} kg CO2e")
        cols = ["cement", "slag", "fly_ash", "water", "superplasticizer", "coarse_agg", "fine_agg"]
        st.dataframe(pd.DataFrame({"kg/m3": par.loc[pick, cols], "lb/yd3": kgm3_to_lbyd3(par.loc[pick, cols])})
                     .astype(float).round(1), use_container_width=True)
        st.info(f"Strength target includes a model-error margin of {margin:.1f} MPa. Optimized mixes are "
                "candidates for trial batches, not final designs. Prices and carbon factors are in the config file.")

# ---------------- Pour log ----------------
@st.cache_data
def load_pours(file):
    return pd.read_csv(file)

def pour_table(df):
    rows = []
    for _, r in df.iterrows():
        t28 = strength_test([r.get("cyl1_28d"), r.get("cyl2_28d")], "6x12", cfg)
        t7 = strength_test([r.get("cyl1_7d"), r.get("cyl2_7d")], "6x12", cfg)
        rows.append({**r.to_dict(), "test_28d": t28["strength"], "range_28d_pct": t28["range_pct"],
                     "range_limit_pct": t28["range_limit_pct"], "test_7d": t7["strength"]})
    return pd.DataFrame(rows)

POUR_COLUMNS = {
    "pour_id": st.column_config.TextColumn("Pour ID", help="Unique name, e.g. P01", required=True),
    "date": st.column_config.TextColumn("Date", help="YYYY-MM-DD"),
    "location": st.column_config.TextColumn("Location", help="Group name, e.g. Deck span 1"),
    "fc_psi": st.column_config.NumberColumn("f'c (psi)", min_value=1000, max_value=15000, step=50, required=True),
    "cyl1_7d": st.column_config.NumberColumn("Cyl 1, 7-day (psi)", min_value=0, step=10),
    "cyl2_7d": st.column_config.NumberColumn("Cyl 2, 7-day (psi)", min_value=0, step=10),
    "cyl1_28d": st.column_config.NumberColumn("Cyl 1, 28-day (psi)", min_value=0, step=10, help="Leave empty if not tested yet"),
    "cyl2_28d": st.column_config.NumberColumn("Cyl 2, 28-day (psi)", min_value=0, step=10, help="Leave empty if not tested yet"),
    "fracture_type": st.column_config.NumberColumn("Fracture type (1-6)", min_value=1, max_value=6, step=1, help="ASTM C39 fracture pattern"),
    "slump_design_in": st.column_config.NumberColumn("Design slump (in)", min_value=0.0, max_value=10.0, step=0.5),
    "slump_ticket_in": st.column_config.NumberColumn("Measured slump (in)", min_value=0.0, max_value=12.0, step=0.1),
    "air_spec_pct": st.column_config.NumberColumn("Specified air (%)", min_value=0.0, max_value=12.0, step=0.1),
    "air_ticket_pct": st.column_config.NumberColumn("Measured air (%)", min_value=0.0, max_value=15.0, step=0.1),
    "cure_temp_F": st.column_config.NumberColumn("Initial curing temp (F)", min_value=0, max_value=120, step=1),
    "minutes_batch_to_place": st.column_config.NumberColumn("Batch to placement (min)", min_value=0, max_value=300, step=1),
}
PRESENTATION = ROOT / "data" / "presentation"


def enter_pours():
    """Editable pour log: start blank or from a sample file, then type or paste rows."""
    starts = {"Blank table": None, "Demo pour log": ROOT / "data" / "demo_pours.csv",
              **{f"Sample: {f.stem.replace('_', ' ')}": f for f in sorted(PRESENTATION.glob("*.csv"))}}
    start = st.selectbox("Start from", list(starts), help="Changing this replaces the table below.")
    if starts[start] is None:
        base = pd.DataFrame([{"pour_id": "P01", "fc_psi": float(p["fc_psi"])}], columns=list(POUR_COLUMNS))
    else:
        base = pd.read_csv(starts[start])
    base = base.reindex(columns=list(POUR_COLUMNS))
    for c in POUR_COLUMNS:
        if c not in ("pour_id", "date", "location"):
            base[c] = pd.to_numeric(base[c], errors="coerce")
        else:
            base[c] = base[c].astype("string")
    st.caption("Type or paste (Ctrl+V from Excel) one row per pour. Add rows with the + at the bottom; "
               "select rows and press Delete to remove them. Empty 28-day cells mean the test is still pending.")
    edited = st.data_editor(base, column_config=POUR_COLUMNS, num_rows="dynamic", hide_index=True,
                            use_container_width=True, key=f"pour_editor_{start}")
    edited = edited.dropna(subset=["pour_id", "fc_psi"])
    edited = edited[edited["pour_id"].str.strip() != ""]
    st.download_button("Download this table as CSV", edited.to_csv(index=False), "my_pour_log.csv", "text/csv",
                       help="Save your entries; upload the file later to continue.")
    return edited.reset_index(drop=True)


with tabs[2]:
    st.subheader("Lab results and ACI 318 acceptance")
    source = st.radio("Pour data", ["Demo data", "Upload a CSV", "Enter data myself"], horizontal=True)
    if source == "Enter data myself":
        raw = enter_pours()
        if raw.empty:
            st.info("Add at least one pour with a Pour ID and f'c to see results.")
            st.stop()
    else:
        up = st.file_uploader("Pour log CSV (same columns as data/demo_pours.csv)", type="csv") if source == "Upload a CSV" else None
        if source == "Upload a CSV" and up is None:
            st.info("Choose a CSV file. Until then the demo pour log is shown.")
        if up is None:
            st.caption("Showing the SYNTHETIC demo pour log.")
        raw = load_pours(up if up is not None else ROOT / "data" / "demo_pours.csv")
    pours = pour_table(raw)
    st.session_state.pours = pours
    done = pours.dropna(subset=["test_28d"])
    fc = float(done["fc_psi"].iloc[0]) if len(done) else p["fc_psi"]
    res = evaluate_tests(fc, done["test_28d"].tolist(), done["pour_id"].tolist(), cfg)
    res["companion range %"] = done["range_28d_pct"].round(1).values
    def color(v):
        return {"Accept": "background-color: #d9f2e3", "Low average": "background-color: #fff1c2",
                "Investigate (cores)": "background-color: #f9d6d5"}.get(v, "")
    if res.empty:
        st.info("No 28-day results yet. Acceptance appears once 28-day cylinder strengths are entered.")
    else:
        st.dataframe(res.style.map(color, subset=["verdict"]), hide_index=True, use_container_width=True)
        st.caption(f"f'c = {fc:,.0f} psi. Each test is the average of two 6x12 cylinders at 28 days.")

# ---------------- 4. Early warning ----------------
with tabs[3]:
    st.subheader("Early warning from 7-day breaks")
    pours = st.session_state.pours
    ctype = st.selectbox("Cement type", list(cfg["early_strength"]["cement_types"]))
    cv = st.slider("Assumed scatter of the estimate (CV)", 0.04, 0.20, float(cfg["early_strength"]["prediction_cv"]), 0.01)
    rows = []
    for _, r in pours.dropna(subset=["test_7d"]).iterrows():
        fp = failure_probability(r["test_7d"], 7, r["fc_psi"], ctype, cv, cfg)
        rows.append({"pour": r["pour_id"], "7-day test (psi)": round(r["test_7d"]),
                     "estimated 28-day (psi)": round(fp["estimate_28_psi"]),
                     "actual 28-day (psi)": None if pd.isna(r["test_28d"]) else round(r["test_28d"]),
                     "P(below f'c)": fp["p_below_fc"], "P(below individual limit)": fp["p_below_individual_limit"]})
    ew = pd.DataFrame(rows)
    if ew.empty:
        st.info("No 7-day results yet.")
    else:
        st.dataframe(ew.style.format({"P(below f'c)": "{:.0%}", "P(below individual limit)": "{:.0%}"})
                     .background_gradient(subset=["P(below individual limit)"], cmap="Reds", vmin=0, vmax=1),
                     hide_index=True, use_container_width=True)
    st.caption("ACI 209R time-strength relation. The scatter (CV) is an assumption until calibrated with your own 7/28-day pairs.")

# ---------------- 5. Diagnose ----------------
with tabs[4]:
    st.subheader("Diagnose a low test")
    pours = st.session_state.pours
    low = pours[pours["test_28d"] < pours["fc_psi"]]["pour_id"].tolist()
    pid = st.selectbox("Pour", pours["pour_id"], index=pours["pour_id"].tolist().index(low[0]) if low else 0)
    r = pours[pours["pour_id"] == pid].iloc[0].to_dict()
    rec = dict(r, companion_range_pct=r["range_28d_pct"])
    ev = extract_evidence(rec, cfg)
    left, right = st.columns([2, 3])
    with left:
        st.markdown("**Evidence from the record**")
        st.dataframe(pd.DataFrame(explain(ev), columns=["Evidence", "Present"]), hide_index=True, use_container_width=True)
    with right:
        st.markdown("**Most likely causes**")
        dx = diagnose(ev, cfg)
        st.dataframe(dx[["cause", "probability"]].style.format({"probability": "{:.0%}"})
                     .bar(subset=["probability"], vmin=0, vmax=1, color="#7aa6c2"),
                     hide_index=True, use_container_width=True)
        st.success(f"Next step: {dx.loc[0, 'next_step']}")
    with st.expander("Check core results (ACI 318-19 26.12.6)"):
        cores = [st.number_input(f"Core {i + 1} (psi)", 0, 15000, 0, 50, key=f"core{i}") for i in range(3)]
        if all(cores):
            cr = evaluate_cores(r["fc_psi"], cores, cfg)
            (st.success if cr["adequate"] else st.error)(
                f"Average {cr['average_psi']:.0f} psi (limit {cr['average_limit_psi']:.0f}); lowest {cr['min_psi']:.0f} psi "
                f"(limit {cr['single_limit_psi']:.0f}). Concrete is {'structurally adequate' if cr['adequate'] else 'not adequate by the core criteria'}.")

# ---------------- 6. Model comparison ----------------
with tabs[5]:
    st.subheader("Code relationship vs. data-driven models")
    try:
        data = load_uci()
        st.caption(f"UCI Concrete Compressive Strength dataset: {len(data):,} mixes.")
        if st.button("Train and compare models", type="primary"):
            with st.spinner("Training..."):
                metrics, fitted = compare_models(data, cfg=cfg)
            save_models(fitted)
            st.session_state.models = fitted
            st.session_state.metrics = metrics
        if "metrics" in st.session_state:
            st.dataframe(st.session_state.metrics.round(3), hide_index=True, use_container_width=True)
            st.caption("Held-out 20% of mixes. The trained models are now available in the Optimize tab.")
    except FileNotFoundError as e:
        st.info(f"{e} Download it from https://archive.ics.uci.edu/dataset/165/concrete+compressive+strength")

# ---------------- 7. Settings ----------------
with tabs[6]:
    st.subheader("Rules and factors")
    st.write(f"Every code limit, table, price, carbon factor and diagnosis likelihood is in `{DEFAULT_CONFIG.relative_to(ROOT)}`. "
             "Edit the file and reload the page.")
    st.json({"presets": cfg["presets"][key], "materials": cfg["materials"], "diagnosis priors":
             {k: v["prior"] for k, v in cfg["diagnosis"]["causes"].items()}}, expanded=False)
