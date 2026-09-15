"""Optuna objective function for SVM hyperparameter tuning.

Defines the single-trial objective that samples hyperparameters from the search
space, fits an SVM, and returns the cross-validated macro recall score that
Optuna maximizes.
"""

from sklearn.model_selection import cross_val_score
from sklearn.svm import SVC
from src.optimization.search_space import get_svm_search_space


def svm_objective(trial, X, y, cv: int = 3):
    """Evaluate one set of SVM hyperparameters and return the mean macro recall."""
    params = get_svm_search_space(trial)
    model = SVC(
        kernel=params["kernel"],
        C=params["C"],
        gamma=params["gamma"],
        degree=params.get("degree", 3),
        probability=False,
        random_state=42,
    )
    # For imbalanced multi-class problems prefer macro recall to emphasize minority classes
    scores = cross_val_score(model, X, y, cv=cv, scoring="recall_macro", n_jobs=-1)
    return float(scores.mean())
