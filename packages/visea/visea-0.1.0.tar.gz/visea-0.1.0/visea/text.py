from __future__ import annotations

from typing import Dict


def describe_numeric(name: str, stats: Dict[str, float]) -> str:
    parts = []
    if stats is None:
        return ""
    skew = stats.get("skew")
    if skew is not None:
        if abs(skew) > 1.0:
            parts.append("belirgin eğiklik (skew) var")
        elif abs(skew) > 0.5:
            parts.append("ılımlı eğiklik var")
    iqr = stats.get("iqr")
    if iqr is not None and iqr == 0:
        parts.append("varyans çok düşük (neredeyse sabit)")
    if parts:
        return f"{name} için: " + ", ".join(parts) + "."
    return ""


def describe_target_relation(name: str, task: str, metrics: Dict[str, float]) -> str:
    if task == "classification":
        auc = metrics.get("auc")
        if auc is not None and auc == auc:  # not NaN
            if auc >= 0.8:
                return f"{name} hedef için güçlü ayırıcı (AUC≈{auc:.2f})."
            if auc >= 0.65:
                return f"{name} hedef için makul ayırıcı (AUC≈{auc:.2f})."
        cv = metrics.get("cramers_v")
        if cv is not None and cv == cv:
            if cv >= 0.3:
                return f"{name} ile hedef arasında güçlü nominal ilişki (Cramer's V≈{cv:.2f})."
    else:
        r2 = metrics.get("r2")
        if r2 is not None and r2 == r2:
            if r2 >= 0.5:
                return f"{name} hedef varyansının anlamlı kısmını açıklar (R²≈{r2:.2f})."
            if r2 >= 0.2:
                return f"{name} hedef ile orta düzey ilişki gösterir (R²≈{r2:.2f})."
        sp = metrics.get("spearman")
        if sp is not None and sp == sp and abs(sp) >= 0.4:
            return f"{name} hedef ile sıralı korelasyon gösterir (Spearman≈{sp:.2f})."
    return ""
