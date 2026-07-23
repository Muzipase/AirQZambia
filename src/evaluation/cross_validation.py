import numpy as np
import pandas as pd
from sklearn.model_selection import cross_validate
from typing import Dict, Any


def cross_validate_model(model, X: pd.DataFrame, y: pd.Series, cv: int = 5) -> Dict[str, Any]:
    if model is None or X is None or y is None:
        return {"test_accuracy": []}

    cv_results = cross_validate(
        model,
        X,
        y,
        cv=cv,
        scoring=["accuracy"],
        return_train_score=False,
        n_jobs=-1,
    )

    return {
        "test_accuracy": [float(score) for score in cv_results.get("test_accuracy", [])],
        "mean_accuracy": float(np.mean(cv_results.get("test_accuracy", []))) if len(cv_results.get("test_accuracy", [])) else 0.0,
        "std_accuracy": float(np.std(cv_results.get("test_accuracy", []))) if len(cv_results.get("test_accuracy", [])) else 0.0,
    }
