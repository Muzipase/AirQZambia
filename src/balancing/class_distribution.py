"""Compute per-class sample counts for a target series.

Used by the balancing stage to inspect label imbalance before and
after resampling (SMOTE-Tomek). The returned dictionary feeds into
``imbalance_analysis`` for entropy / Gini metrics.
"""

import pandas as pd
from typing import Dict


def get_class_distribution(y: pd.Series) -> Dict[str, int]:
    """Return a mapping of class labels to their sample counts."""
    if y is None:
        return {}
    return y.value_counts().to_dict()
