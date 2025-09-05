from __future__ import annotations

import io
import base64
from typing import Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def _fig_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=120)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("ascii")


def plot_numeric_distribution(s: pd.Series, title: Optional[str] = None) -> str:
    s = pd.to_numeric(s, errors="coerce").dropna()
    fig, ax = plt.subplots(figsize=(4, 3))
    if len(s) == 0:
        ax.text(0.5, 0.5, "No data", ha="center", va="center")
    else:
        sns.histplot(s, bins=30, kde=True, ax=ax)
    ax.set_title(title or s.name)
    return _fig_to_base64(fig)


def plot_categorical_counts(s: pd.Series, title: Optional[str] = None, top: int = 20) -> str:
    vc = s.astype("object").value_counts().head(top)
    fig, ax = plt.subplots(figsize=(4, 3))
    sns.barplot(x=vc.values, y=vc.index.astype(str), ax=ax, orient="h")
    ax.set_title(title or s.name)
    return _fig_to_base64(fig)


def plot_corr_heatmap(df_num: pd.DataFrame, title: str = "Correlation (spearman)") -> str:
    if df_num.shape[1] < 2:
        fig, ax = plt.subplots(figsize=(3, 2))
        ax.text(0.5, 0.5, "Insufficient numeric features", ha="center", va="center")
        ax.set_title(title)
        return _fig_to_base64(fig)
    corr = df_num.corr(method="spearman")
    mask = np.triu(np.ones_like(corr, dtype=bool))
    fig, ax = plt.subplots(figsize=(4, 3))
    sns.heatmap(corr, mask=mask, cmap="coolwarm", center=0, square=True, cbar_kws={"shrink": 0.6}, ax=ax)
    ax.set_title(title)
    return _fig_to_base64(fig)


def plot_numeric_vs_target(x: pd.Series, y: pd.Series, title: Optional[str] = None) -> str:
    df = pd.DataFrame({"x": pd.to_numeric(x, errors="coerce"), "y": y}).dropna()
    fig, ax = plt.subplots(figsize=(4, 3))
    if df.empty:
        ax.text(0.5, 0.5, "No data", ha="center", va="center")
    else:
        y_clean = df["y"]
        nunq = y_clean.nunique()
        if nunq <= 10 and set(y_clean.unique()).issubset({0, 1}):
            sns.kdeplot(data=df, x="x", hue="y", common_norm=False, fill=True, ax=ax)
        elif nunq <= 10:
            sns.boxplot(data=df, x="y", y="x", ax=ax)
            ax.set_xlabel("target")
            ax.set_ylabel(x.name or "x")
        else:
            sns.regplot(data=df, x="x", y="y", scatter_kws={"s": 10, "alpha": 0.5}, line_kws={"color": "red"}, ax=ax)
    ax.set_title(title or (x.name or "feature"))
    return _fig_to_base64(fig)
