"""Strength prediction: code-based relationship vs. linear regression vs. gradient boosting.

Data: UCI Concrete Compressive Strength dataset (1,030 mixes, kg/m3 and MPa).
Download it from https://archive.ics.uci.edu/dataset/165/concrete+compressive+strength
and save Concrete_Data.xls (or a CSV with the same 9 columns in order) in data/.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .config import load_config, psi_to_mpa, ROOT

FEATURES = ["cement", "slag", "fly_ash", "water", "superplasticizer", "coarse_agg", "fine_agg", "age"]
TARGET = "strength"
MODEL_PATH = ROOT / "models" / "strength_models.joblib"


def load_uci(path=None):
    """Load the UCI file (.xls/.xlsx/.csv). Columns are mapped by position."""
    if path is None:
        cands = sorted((ROOT / "data").glob("Concrete_Data*")) + sorted((ROOT / "data").glob("concrete_data*"))
        if not cands:
            raise FileNotFoundError("Put Concrete_Data.xls (UCI) in the data/ folder.")
        path = cands[0]
    path = Path(path)
    df = pd.read_csv(path) if path.suffix.lower() == ".csv" else pd.read_excel(path)
    if df.shape[1] != 9:
        raise ValueError(f"Expected 9 columns, found {df.shape[1]}.")
    df.columns = FEATURES + [TARGET]
    return df.astype(float)


# ---------------- Code-based model ----------------
class CodeModel:
    """ACI 211.1 w/c-strength table (non-air-entrained) fitted as f = A exp(-B w/c),
    applied to an effective w/cm with SCM efficiency factors, and aged with ACI 209R."""
    name = "ACI w/c relationship"

    def __init__(self, cfg=None):
        cfg = cfg or load_config()
        t = cfg["aci211"]
        wc = np.array(t["wc_non_ae"], dtype=float)
        f = psi_to_mpa(np.array(t["wc_strength_psi"], dtype=float))
        slope, intercept = np.polyfit(wc, np.log(f), 1)
        self.A, self.B = float(np.exp(intercept)), float(-slope)
        self.kf, self.ks = cfg["fallback_model"]["k_fly_ash"], cfg["fallback_model"]["k_slag"]
        p = cfg["early_strength"]["cement_types"]["Type I"]
        self.a, self.b = p["a"], p["b"]
        self.rmse_mpa = None

    def effective_wcm(self, X):
        binder = X["cement"] + self.ks * X["slag"] + self.kf * X["fly_ash"]
        return X["water"] / binder

    def predict(self, X):
        X = pd.DataFrame(X, columns=FEATURES)
        f28 = self.A * np.exp(-self.B * self.effective_wcm(X))
        t = X["age"].to_numpy()
        age_factor = (t / (self.a + self.b * t)) / (28 / (self.a + self.b * 28))
        return np.asarray(f28 * age_factor)


class SklearnModel:
    def __init__(self, name, estimator, lower=None, upper=None):
        self.name, self.est, self.lower, self.upper = name, estimator, lower, upper
        self.rmse_mpa = None

    def fit(self, X, y):
        self.est.fit(X[FEATURES], y)
        if self.lower is not None:
            self.lower.fit(X[FEATURES], y)
            self.upper.fit(X[FEATURES], y)
        return self

    def predict(self, X):
        return self.est.predict(pd.DataFrame(X, columns=FEATURES))

    def interval(self, X):
        """80% prediction interval (10th-90th percentile), if quantile models were trained."""
        if self.lower is None:
            return None
        X = pd.DataFrame(X, columns=FEATURES)
        return self.lower.predict(X), self.upper.predict(X)


def _gbr(**kw):
    return GradientBoostingRegressor(n_estimators=600, learning_rate=0.05, max_depth=4,
                                     subsample=0.8, random_state=42, **kw)


def compare_models(df, seed=42, quantiles=True, cfg=None):
    """Fit models on a training split and score all three on held-out 28-day mixes.

    Returns (metrics DataFrame, dict of fitted models).
    """
    train, test = train_test_split(df, test_size=0.2, random_state=seed)
    models = {
        "code": CodeModel(cfg),
        "linear": SklearnModel("Linear regression", make_pipeline(StandardScaler(), LinearRegression())).fit(train, train[TARGET]),
        "gbr": SklearnModel("Gradient boosting", _gbr(),
                            _gbr(loss="quantile", alpha=0.1) if quantiles else None,
                            _gbr(loss="quantile", alpha=0.9) if quantiles else None).fit(train, train[TARGET]),
    }
    rows = []
    for key, m in models.items():
        for subset, d in (("28-day test mixes", test[test["age"] == 28]), ("all test mixes", test)):
            pred = m.predict(d[FEATURES])
            rmse = float(np.sqrt(mean_squared_error(d[TARGET], pred)))
            if subset == "28-day test mixes":
                m.rmse_mpa = rmse
            rows.append({"model": m.name, "subset": subset, "n": len(d),
                         "MAE (MPa)": mean_absolute_error(d[TARGET], pred),
                         "MAE (psi)": mean_absolute_error(d[TARGET], pred) * 145.038,
                         "RMSE (MPa)": rmse, "R2": r2_score(d[TARGET], pred)})
    return pd.DataFrame(rows), models


def save_models(models, path=MODEL_PATH):
    import joblib
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(models, path)


def load_models(path=MODEL_PATH):
    import joblib
    return joblib.load(path) if Path(path).exists() else None
