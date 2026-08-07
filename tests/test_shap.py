import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.svm import SVC
from sklearn.datasets import make_classification

from src.explainability.shap_explainer import ShapExplainer


def test_shap_per_class_importance_handles_multiclass():
    X, y = make_classification(
        n_samples=150, n_features=5, n_informative=3, n_classes=4,
        n_clusters_per_class=1, random_state=42,
    )
    X = pd.DataFrame(X, columns=[f"f{i}" for i in range(5)])
    y = pd.Series(y)

    model = SVC(kernel="rbf", probability=False, random_state=42)
    model.fit(X, y)

    explainer = ShapExplainer(model, X)
    per_class = explainer.get_per_class_importance(X, y, top_k=2, representatives_per_class=4)

    assert isinstance(per_class, dict)
    assert len(per_class) == len(set(y))
    for features in per_class.values():
        assert len(features) == 2
        assert all(item["feature"] in X.columns for item in features)


def test_shap_explainer_runs_without_error():
    X, y = make_classification(
        n_samples=100, n_features=5, n_informative=3, random_state=42
    )
    X = pd.DataFrame(X, columns=[f"f{i}" for i in range(5)])
    y = pd.Series(y)

    model = SVC(kernel="rbf", probability=False, random_state=42)
    model.fit(X, y)

    explainer = ShapExplainer(model, X)
    summary = explainer.get_summary()

    assert isinstance(summary, dict)
    assert len(summary) == 5
    assert all(isinstance(v, float) for v in summary.values())
    assert all(v >= 0 for v in summary.values()), "Importance values should be non-negative"


def test_shap_per_class_importance_returns_top_k_features():
    X, y = make_classification(
        n_samples=120, n_features=5, n_informative=3, random_state=42
    )
    X = pd.DataFrame(X, columns=[f"f{i}" for i in range(5)])
    y = pd.Series(y)

    model = SVC(kernel="rbf", probability=False, random_state=42)
    model.fit(X, y)

    explainer = ShapExplainer(model, X)
    per_class = explainer.get_per_class_importance(X, y, top_k=3)

    assert isinstance(per_class, dict)
    assert len(per_class) == len(set(y))
    for label, features in per_class.items():
        assert len(features) == 3
        for item in features:
            assert "feature" in item and "importance" in item
            assert item["feature"] in X.columns
            assert isinstance(item["importance"], float)
