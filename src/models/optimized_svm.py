"""Bayesian-optimized SVM model.

Delegates hyperparameter search to the Optuna-based optimizer, then trains
an SVC with the discovered best parameters.  Returns the fitted model, the
best parameter dictionary, and the Optuna study for post-hoc analysis.
"""

from sklearn.svm import SVC
from src.optimization.bayesian_optimizer import optimize_svm_hyperparameters


def train_optimized_svm(X, y, n_trials: int = 10):
    """Run Bayesian optimization and train an SVM with the best-found hyperparameters."""
    best_params, study = optimize_svm_hyperparameters(X, y, n_trials=n_trials)
    model = SVC(
        kernel=best_params.get("kernel", "rbf"),
        C=best_params.get("C", 1.0),
        gamma=best_params.get("gamma", "scale"),
        degree=best_params.get("degree", 3),
        probability=False,
        random_state=42,
    )
    model.fit(X, y)
    return model, best_params, study
