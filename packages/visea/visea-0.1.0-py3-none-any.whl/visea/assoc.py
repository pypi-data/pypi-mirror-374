from __future__ import annotations

from typing import Dict, Any

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score, r2_score, mean_absolute_error
from sklearn.linear_model import LinearRegression
from .stats import pearson_spearman, anova_f, cramers_v


def numeric_vs_target(x: pd.Series, y: pd.Series, task: str) -> Dict[str, Any]:
    res: Dict[str, Any] = {}
    if task == "classification":
        # Attempt univariate AUC/APS for binary case
        y_clean = y.dropna()
        if set(np.unique(y_clean)) <= {0, 1}:
            df = pd.DataFrame({"x": pd.to_numeric(x, errors="coerce"), "y": y}).dropna()
            if len(df) >= 10 and df["y"].nunique() == 2:
                try:
                    res["auc"] = float(roc_auc_score(df["y"], df["x"]))
                    res["aps"] = float(average_precision_score(df["y"], df["x"]))
                except Exception:
                    res["auc"] = np.nan
                    res["aps"] = np.nan
        # ANOVA as generic signal
        f = anova_f(x, y)
        res.update({"anova_f": f.get("f"), "anova_p": f.get("p")})
    else:
        # Regression: correlation + univariate R2/MAE
        corr = pearson_spearman(x, y)
        res.update({"pearson": corr["pearson"], "spearman": corr["spearman"]})
        df = pd.DataFrame({"x": pd.to_numeric(x, errors="coerce"), "y": pd.to_numeric(y, errors="coerce")}).dropna()
        if len(df) >= 10:
            X = df[["x"]].values
            model = LinearRegression().fit(X, df["y"].values)
            pred = model.predict(X)
            res["r2"] = float(r2_score(df["y"], pred))
            res["mae"] = float(mean_absolute_error(df["y"], pred))
        else:
            res["r2"] = np.nan
            res["mae"] = np.nan
    return res


def categorical_vs_target(x: pd.Series, y: pd.Series, task: str) -> Dict[str, Any]:
    res: Dict[str, Any] = {}
    if task == "classification":
        # Cramer's V for association strength
        try:
            res["cramers_v"] = cramers_v(x, y)
        except Exception:
            res["cramers_v"] = np.nan
    else:
        # Regression: ANOVA across target bins? Use correlation of means across binned x
        df = pd.DataFrame({"x": x, "y": pd.to_numeric(y, errors="coerce")}).dropna()
        if df.empty:
            return {"groups": np.nan}
        means = df.groupby("x")["y"].mean()
        res["groups"] = int(len(means))
        res["range"] = float(means.max() - means.min()) if len(means) else np.nan
    return res
