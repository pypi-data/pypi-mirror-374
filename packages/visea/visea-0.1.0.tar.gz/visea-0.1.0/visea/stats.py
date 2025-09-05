from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any

import numpy as np
import pandas as pd
from scipy import stats as sstats


@dataclass
class ColumnSummary:
    name: str
    dtype: str
    n_missing: int
    pct_missing: float
    nunique: int
    sample_values: list
    numeric_stats: Dict[str, float] | None = None


def basic_profile(df: pd.DataFrame) -> Dict[str, Any]:
    return {
        "n_rows": int(len(df)),
        "n_cols": int(df.shape[1]),
        "memory_mb": float(df.memory_usage(deep=True).sum() / (1024 ** 2)),
        "dtypes": {c: str(dt) for c, dt in df.dtypes.items()},
    }


def numeric_describe(s: pd.Series) -> Dict[str, float]:
    s = pd.to_numeric(s, errors="coerce")
    desc = s.describe()
    skew = s.skew()
    kurt = s.kurtosis()
    q1 = float(desc["25%"])
    q3 = float(desc["75%"])
    iqr = q3 - q1
    return {
        "mean": float(desc["mean"]) if not np.isnan(desc["mean"]) else np.nan,
        "std": float(desc["std"]) if not np.isnan(desc["std"]) else np.nan,
        "min": float(desc["min"]) if not np.isnan(desc["min"]) else np.nan,
        "q1": q1,
        "median": float(desc["50%"]),
        "q3": q3,
        "max": float(desc["max"]) if not np.isnan(desc["max"]) else np.nan,
        "skew": float(skew) if not np.isnan(skew) else np.nan,
        "kurtosis": float(kurt) if not np.isnan(kurt) else np.nan,
        "iqr": float(iqr) if not np.isnan(iqr) else np.nan,
    }


def summarize_columns(df: pd.DataFrame) -> list[ColumnSummary]:
    summaries: list[ColumnSummary] = []
    for col in df.columns:
        s = df[col]
        n_missing = int(s.isna().sum())
        pct_missing = float((n_missing / len(df)) * 100) if len(df) else 0.0
        nunique = int(s.dropna().nunique())
        sample_values = s.dropna().unique().tolist()[:5]
        numeric_stats = numeric_describe(s) if pd.api.types.is_numeric_dtype(s) else None
        summaries.append(
            ColumnSummary(
                name=col,
                dtype=str(s.dtype),
                n_missing=n_missing,
                pct_missing=pct_missing,
                nunique=nunique,
                sample_values=sample_values,
                numeric_stats=numeric_stats,
            )
        )
    return summaries


def pearson_spearman(x: pd.Series, y: pd.Series) -> Dict[str, float]:
    x = pd.to_numeric(x, errors="coerce")
    y = pd.to_numeric(y, errors="coerce")
    mask = x.notna() & y.notna()
    if mask.sum() < 3:
        return {"pearson": np.nan, "spearman": np.nan}
    rp = sstats.pearsonr(x[mask], y[mask])[0]
    rs = sstats.spearmanr(x[mask], y[mask]).correlation
    return {"pearson": float(rp), "spearman": float(rs)}


def anova_f(x: pd.Series, y: pd.Series) -> Dict[str, float]:
    # x: numeric, y: categorical target (classification)
    df = pd.DataFrame({"x": pd.to_numeric(x, errors="coerce"), "y": y}).dropna()
    groups = [grp["x"].values for _, grp in df.groupby("y")]
    if len(groups) < 2:
        return {"f": np.nan, "p": np.nan}
    F, p = sstats.f_oneway(*groups)
    return {"f": float(F), "p": float(p)}


def cramers_v(x: pd.Series, y: pd.Series) -> float:
    # x,y categorical
    table = pd.crosstab(x, y)
    if table.size == 0:
        return float("nan")
    chi2 = sstats.chi2_contingency(table, correction=False)[0]
    n = table.values.sum()
    r, k = table.shape
    if n == 0 or min(k, r) <= 1:
        return float("nan")
    return float(np.sqrt((chi2 / n) / (min(k - 1, r - 1))))
