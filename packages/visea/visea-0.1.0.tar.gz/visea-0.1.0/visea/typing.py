from __future__ import annotations

from dataclasses import dataclass
import pandas as pd


@dataclass
class ColumnType:
    name: str  # numeric, categorical, datetime, boolean, text


def infer_type(s: pd.Series, high_card_threshold: int = 50) -> ColumnType:
    if pd.api.types.is_bool_dtype(s):
        return ColumnType("boolean")
    if pd.api.types.is_numeric_dtype(s):
        return ColumnType("numeric")
    if pd.api.types.is_datetime64_any_dtype(s):
        return ColumnType("datetime")
    # Treat small-cardinality object/string as categorical, else text
    if pd.api.types.is_object_dtype(s) or pd.api.types.is_categorical_dtype(s):
        nunq = s.dropna().nunique()
        if nunq <= high_card_threshold:
            return ColumnType("categorical")
        return ColumnType("text")
    return ColumnType("text")


def infer_task_from_target(y: pd.Series) -> str:
    if pd.api.types.is_numeric_dtype(y):
        # Heuristic: numeric with few unique values may still be classification
        nunq = y.dropna().nunique()
        if nunq <= 10 and set(y.dropna().unique()).issubset({0, 1}):
            return "classification"
        # If integer with very few classes treat as classification
        if pd.api.types.is_integer_dtype(y) and nunq <= 10:
            return "classification"
        return "regression"
    return "classification"
