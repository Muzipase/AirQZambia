import numpy as np
import pandas as pd
from typing import Dict


def _entropy(probs):
    probs = np.asarray(probs, dtype=float)
    probs = probs[probs > 0]
    return -np.sum(probs * np.log(probs)) if len(probs) else 0.0


def _gini(probs):
    probs = np.asarray(probs, dtype=float)
    return 1.0 - np.sum(probs ** 2)


def _jensen_shannon_divergence(p, q):
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    p = p / np.sum(p) if np.sum(p) else p
    q = q / np.sum(q) if np.sum(q) else q
    m = 0.5 * (p + q)
    return 0.5 * (_entropy(p) + _entropy(q) - 2 * _entropy(m))


def analyze_imbalance(df: pd.DataFrame, label_column: str = "aqi_category") -> Dict[str, float]:
    if df is None or label_column not in df.columns:
        return {"entropy": 0.0, "gini_coefficient": 0.0, "jensen_shannon_divergence": 0.0}

    counts = df[label_column].value_counts()
    distribution = counts.values.astype(float)
    uniform = np.ones_like(distribution) / len(distribution)

    return {
        "entropy": float(_entropy(distribution / np.sum(distribution))),
        "gini_coefficient": float(_gini(distribution / np.sum(distribution))),
        "jensen_shannon_divergence": float(_jensen_shannon_divergence(distribution, uniform)),
    }
