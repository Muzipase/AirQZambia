import pandas as pd
from typing import Dict


def get_class_distribution(y: pd.Series) -> Dict[str, int]:
    if y is None:
        return {}
    return y.value_counts().to_dict()
