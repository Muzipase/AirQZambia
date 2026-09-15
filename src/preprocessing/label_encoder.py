"""Label encoding utilities for AQI category targets.

Wraps scikit-learn's ``LabelEncoder`` to provide a consistent interface for
converting string AQI categories (e.g. "Good", "Moderate") to integer labels
and back.  Used by the training pipeline and the FastAPI prediction endpoint.
"""

from sklearn.preprocessing import LabelEncoder
from typing import Tuple, List
import pandas as pd


def fit_label_encoder(y: pd.Series) -> Tuple[LabelEncoder, List[str]]:
    """Fit a label encoder on AQI category strings and return the encoder with its classes."""
    encoder = LabelEncoder()
    encoded = encoder.fit_transform(y.astype(str))
    return encoder, list(encoder.classes_)


def transform_labels(encoder: LabelEncoder, y: pd.Series) -> pd.Series:
    """Transform string AQI labels into their integer representations using a fitted encoder."""
    return pd.Series(encoder.transform(y.astype(str)), index=y.index)


def inverse_transform_labels(encoder: LabelEncoder, labels: List[int]) -> List[str]:
    """Convert integer labels back to human-readable AQI category strings."""
    return list(encoder.inverse_transform(labels))
