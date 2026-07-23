from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


def create_svm_pipeline(kernel: str = "rbf", C: float = 1.0, gamma: str = "scale") -> Pipeline:
    return Pipeline(
        [
            ("scaler", StandardScaler()),
            ("svm", SVC(kernel=kernel, C=C, gamma=gamma, probability=False, random_state=42)),
        ]
    )
