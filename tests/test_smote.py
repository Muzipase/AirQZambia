import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.svm import SVC
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

from src.balancing.smote_tomek import apply_smote_tomek
from src.balancing.imbalance_analysis import analyze_imbalance


def test_smote_tomek_increases_minority_samples():
    X, y = make_classification(
        n_samples=100, n_features=5, n_informative=3,
        weights=[0.7, 0.3], random_state=42
    )
    X = pd.DataFrame(X, columns=[f"f{i}" for i in range(5)])
    y = pd.Series(["Good"] * 70 + ["Moderate"] * 30)

    X_bal, y_bal = apply_smote_tomek(X, y)

    assert len(X_bal) >= len(X), "Balanced set should be >= original size"
    assert set(y_bal.unique()) == set(y.unique()), "All classes should be preserved"
    minority_before = y.value_counts().min()
    minority_after = y_bal.value_counts().min()
    assert minority_after >= minority_before, "Minority class should grow or stay"


def test_analyze_imbalance_returns_valid_metrics():
    df = pd.DataFrame({"aqi_category": ["Good"] * 80 + ["Moderate"] * 15 + ["Unhealthy"] * 5})
    result = analyze_imbalance(df)

    assert "entropy" in result
    assert "gini_coefficient" in result
    assert result["entropy"] > 0, "Non-uniform distribution should have positive entropy"
    assert 0 <= result["gini_coefficient"] <= 1
