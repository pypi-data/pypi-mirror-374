from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any, List

import numpy as np
import pandas as pd

from .typing import infer_type, infer_task_from_target
from .stats import basic_profile, summarize_columns
from .assoc import numeric_vs_target, categorical_vs_target
from .plots import (
    plot_numeric_distribution,
    plot_categorical_counts,
    plot_corr_heatmap,
    plot_numeric_vs_target,
)
from .text import describe_numeric, describe_target_relation
from .report import Report, Section, Figure


@dataclass
class AnalyzeConfig:
    target: Optional[str] = None
    task: str = "auto"  # classification|regression|auto
    sample_max_rows: int = 100_000
    max_plots_per_section: int = 24
    random_state: int = 42


def analyze(df: pd.DataFrame, target: Optional[str] = None, task: str = "auto", **kwargs) -> Report:
    cfg = AnalyzeConfig(target=target, task=task, **kwargs)

    # Sampling for performance
    if len(df) > cfg.sample_max_rows:
        df = df.sample(cfg.sample_max_rows, random_state=cfg.random_state)

    y = None
    if cfg.target is not None and cfg.target in df.columns:
        y = df[cfg.target]
        X = df.drop(columns=[cfg.target])
    else:
        X = df.copy()

    # Task inference
    if cfg.task == "auto" and y is not None:
        task = infer_task_from_target(y)
    else:
        task = cfg.task if cfg.task in ("classification", "regression") else "classification"

    profile = basic_profile(df)
    col_summaries = summarize_columns(X)

    # Build sections
    sections: List[Section] = []

    # 1) Column overview table
    def _columns_table_html() -> str:
        rows = [
            "<tr><th>Column</th><th>dtype</th><th>% Missing</th><th>#Unique</th><th>Samples</th></tr>"
        ]
        for cs in col_summaries:
            samples = ", ".join(map(str, cs.sample_values))
            rows.append(
                f"<tr><td>{cs.name}</td><td>{cs.dtype}</td><td>{cs.pct_missing:.1f}</td><td>{cs.nunique}</td><td>{samples}</td></tr>"
            )
        return "<div class='card'><table>" + "".join(rows) + "</table></div>"

    sections: List[Section] = [
        Section(title="Sütun Özeti", content_html=_columns_table_html())
    ]

    # 2) Overall correlations (numeric only)
    num_cols = [c for c in X.columns if pd.api.types.is_numeric_dtype(X[c])]
    if len(num_cols) >= 2:
        heat = plot_corr_heatmap(X[num_cols])
        sections.append(Section(title="Korelasyon Isı Haritası", figures=[Figure("Spearman Korelasyon", heat)]))

    # 3) Univariate distributions
    uni_figs: List[Figure] = []
    comments: List[str] = []
    for cs in col_summaries[: cfg.max_plots_per_section]:
        s = X[cs.name]
        ctype = infer_type(s).name
        if ctype == "numeric":
            img = plot_numeric_distribution(s, title=cs.name)
            uni_figs.append(Figure(cs.name, img))
            desc = describe_numeric(cs.name, cs.numeric_stats)
            if desc:
                comments.append("<li>" + desc + "</li>")
        elif ctype in ("categorical", "boolean"):
            img = plot_categorical_counts(s, title=cs.name)
            uni_figs.append(Figure(cs.name, img))
    uni_html = "<ul>" + "".join(comments) + "</ul>"
    sections.append(Section(title="Tek Değişkenli Dağılımlar", content_html=uni_html, figures=uni_figs))

    # 4) Feature vs Target
    ft_figs: List[Figure] = []
    ft_comms: List[str] = []
    feature_scores: List[tuple[str, float]] = []
    if y is not None:
        for cs in col_summaries:
            s = X[cs.name]
            ctype = infer_type(s).name
            # plot
            try:
                img = plot_numeric_vs_target(s, y, title=cs.name)
                ft_figs.append(Figure(cs.name, img))
            except Exception:
                pass
            # metrics
            metrics: Dict[str, Any] = {}
            if ctype == "numeric":
                metrics = numeric_vs_target(s, y, task)
                score = (
                    float(metrics.get("auc", np.nan)) if task == "classification" else float(metrics.get("r2", np.nan))
                )
            elif ctype in ("categorical", "boolean"):
                metrics = categorical_vs_target(s.astype("object"), y, task)
                score = float(metrics.get("cramers_v", np.nan)) if task == "classification" else float("nan")
            else:
                score = float("nan")
            desc = describe_target_relation(cs.name, task, metrics)
            if desc:
                ft_comms.append("<li>" + desc + "</li>")
            if score == score:  # not NaN
                feature_scores.append((cs.name, score))
        ft_html = "<ul>" + "".join(ft_comms) + "</ul>"
        sections.append(Section(title="Öznitelik vs Hedef", content_html=ft_html, figures=ft_figs[: cfg.max_plots_per_section]))

    # Summary: top features
    feature_scores = [(n, float(s)) for n, s in feature_scores if s == s]
    feature_scores.sort(key=lambda x: abs(x[1]), reverse=True)
    top_features = feature_scores[:10]

    summary = {"top_features": top_features}

    return Report(profile=profile, sections=sections, summary=summary)
