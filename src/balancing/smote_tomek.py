import pandas as pd
from imblearn.combine import SMOTETomek
from imblearn.over_sampling import SMOTE
from typing import Tuple


def apply_smote_tomek(X: pd.DataFrame, y: pd.Series) -> Tuple[pd.DataFrame, pd.Series]:
    if X is None or y is None:
        return pd.DataFrame(), pd.Series(dtype=object)

    min_class_count = y.value_counts().min()
    k_neighbors = max(1, min(5, min_class_count - 1))

    smote = SMOTE(random_state=42, k_neighbors=k_neighbors)
    sampler = SMOTETomek(random_state=42, smote=smote)
    X_resampled, y_resampled = sampler.fit_resample(X, y)

    X_balanced = pd.DataFrame(X_resampled, columns=X.columns)
    y_balanced = pd.Series(y_resampled, name=y.name)

    return X_balanced, y_balanced
