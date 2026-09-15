"""Baseline SVM model with default hyperparameters.

Trains an RBF-kernel SVC using scikit-learn defaults (C=1.0, gamma='scale')
to establish a performance reference that the Bayesian-optimized model can be
compared against.
"""

from sklearn.svm import SVC


def train_baseline_svm(X, y, random_state: int = 42):
    """Train a baseline RBF SVM classifier and return the fitted model."""
    model = SVC(kernel="rbf", C=1.0, gamma="scale", probability=False, random_state=random_state)
    model.fit(X, y)
    return model
