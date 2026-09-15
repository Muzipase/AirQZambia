"""Scikit-learn Pipeline combining StandardScaler with an SVM classifier.

Ensures that scaling is consistently applied during both training and
inference, preventing train/serve skew when the model is deployed.
"""

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


def create_svm_pipeline(kernel: str = "rbf", C: float = 1.0, gamma: str = "scale") -> Pipeline:
    """Build and return a two-step Pipeline: StandardScaler followed by SVC."""
    return Pipeline(
        [
            ("scaler", StandardScaler()),
            ("svm", SVC(kernel=kernel, C=C, gamma=gamma, probability=False, random_state=42)),
        ]
    )
