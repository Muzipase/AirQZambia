from sklearn.preprocessing import LabelEncoder
from typing import Tuple, List
import pandas as pd


def fit_label_encoder(y: pd.Series) -> Tuple[LabelEncoder, List[str]]:
    encoder = LabelEncoder()
    encoded = encoder.fit_transform(y.astype(str))
    return encoder, list(encoder.classes_)


def transform_labels(encoder: LabelEncoder, y: pd.Series) -> pd.Series:
    return pd.Series(encoder.transform(y.astype(str)), index=y.index)


def inverse_transform_labels(encoder: LabelEncoder, labels: List[int]) -> List[str]:
    return list(encoder.inverse_transform(labels))
