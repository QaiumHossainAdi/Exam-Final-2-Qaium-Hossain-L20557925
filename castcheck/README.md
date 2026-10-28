# CastCheck AI

An optimization and probabilistic decision tool for concrete mix design and acceptance.
It runs entirely on a local computer.

**Design → Optimize → Predict → Accept → Diagnose**

1. **Mix design**: ACI 211.1 absolute-volume method, every step shown so an engineer can check it.
2. **Optimize**: finds the lowest-cost and lowest-carbon mixes (cement, slag, fly ash, water,
   superplasticizer, aggregates) that meet strength, w/cm, SCM, minimum-binder and workability
   limits, and shows the cost-carbon trade-off against the ACI 211.1 mix.
3. **Lab results**: ACI 318-19 acceptance (3-test average and individual-test rules), ASTM C39
   companion-cylinder range check.
4. **Early warning**: 28-day strength estimated from 7-day breaks (ACI 209R) with the
   *probability* of failing acceptance.
5. **Diagnose**: naive Bayes ranking of likely causes of a low test (testing problem, water
   added, batching error, high air, poor curing) with the next step, plus core acceptance.
6. **Model comparison**: ACI w/c relationship vs. linear regression vs. gradient boosting on the
   UCI dataset (1,030 mixes). Trained models can then drive the optimizer.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows   (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
python scripts/make_demo_pours.py   # synthetic demo pour log (already included)
streamlit run app.py
```

On Windows you can instead double-click `setup_castcheck.bat` once, then `run_castcheck.bat`.

For the model comparison, download `Concrete_Data.xls` from
https://archive.ics.uci.edu/dataset/165/concrete+compressive+strength into `data/`,
then click **Train and compare models**.

Tests: `pytest` (or `python tests/test_castcheck.py`).

## Project structure

```
config/castcheck.yaml    every code limit, table, preset, price, carbon factor, likelihood
castcheck/mix_design.py  ACI 211.1 design, f'cr rules
castcheck/acceptance.py  ACI 318 acceptance, ASTM C39 range, core criteria
castcheck/early_strength.py  7-to-28-day estimate, probability of failure, calibration
castcheck/predict.py     UCI loader, code model, ML models, comparison
castcheck/optimize.py    cost/carbon optimizer (differential evolution), Pareto front
castcheck/diagnose.py    naive Bayes diagnosis
app.py                   Streamlit interface
tests/                   unit tests, including the ACI 211.1 worked example
```

## Where to extend it

| Idea | Where |
|---|---|
| Change a code limit, add an exposure preset | `config/castcheck.yaml` (no code changes) |
| Local material prices or EPD carbon data | `materials` in the config |
| A new strength model (e.g. neural network, XGBoost) | any class with `.predict(X)` in `predict.py`; the optimizer accepts it unchanged |
| New optimization goal (e.g. heat of hydration, shrinkage) | `MixOptimizer.objective` / `penalties` |
| New diagnosis evidence or cause | `diagnosis` in the config + `extract_evidence` |
| Learn diagnosis likelihoods from confirmed cases | replace the config tables with counts from your records |
| Calibrate the 7-day estimate | `early_strength.calibrate(pairs)` with your own 7/28-day pairs |

## Limits (read before use)

- Values marked ASSUMED in the config (prices, carbon factors, SP water reduction, priors) are
  placeholders. Replace them with supplier, EPD and project data.
- The UCI data contains no air-entrained mixes; air is handled by an assumed strength loss.
- Optimized mixes are candidates for trial batches, not approved designs.
- The demo pour log is synthetic.
- Check every result against the current code edition and the project specification.
