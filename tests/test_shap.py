import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.svm import SVC
from sklearn.datasets import make_classification

from src.explainability.shap_explainer import ShapExplainer


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
