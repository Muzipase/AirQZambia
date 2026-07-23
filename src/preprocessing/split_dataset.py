from sklearn.model_selection import train_test_split
import pandas as pd


def split_data(X: pd.DataFrame, y: pd.Series, test_size: float = 0.2, random_state: int = 42):
    """Split features and labels into training and test sets."""
    if X is None or y is None:
        return None, None, None, None

    stratify = None
    if len(y.unique()) > 1 and len(y) >= 4:
        class_counts = y.value_counts()
        if (class_counts >= 2).all():
            stratify = y

    return train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify,
    )
