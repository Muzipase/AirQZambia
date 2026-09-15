"""Perform k-fold cross-validation on a given estimator.

Returns per-fold accuracy scores plus summary statistics (mean / std)
so the pipeline can report both a single-number metric and its
variability.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import cross_validate
from typing import Dict, Any


def cross_validate_model(model, X: pd.DataFrame, y: pd.Series, cv: int = 5) -> Dict[str, Any]:
    """Run cross-validation and collect accuracy statistics.

    Args:
        model: A scikit-learn compatible estimator.
        X: Feature matrix.
        y: Target labels.
        cv: Number of folds (default 5).

    Returns:
        Dictionary with ``test_accuracy`` (per-fold), ``mean_accuracy``,
        and ``std_accuracy``.
    """
    if model is None or X is None or y is None:
        return {"test_accuracy": []}

    cv_results = cross_validate(
        model,
        X,
        y,
        cv=cv,
        scoring=["accuracy"],
        return_train_score=False,
        n_jobs=1,
    )

    return {
        "test_accuracy": [float(score) for score in cv_results.get("test_accuracy", [])],
        "mean_accuracy": float(np.mean(cv_results.get("test_accuracy", []))) if len(cv_results.get("test_accuracy", [])) else 0.0,
        "std_accuracy": float(np.std(cv_results.get("test_accuracy", []))) if len(cv_results.get("test_accuracy", [])) else 0.0,
    }
