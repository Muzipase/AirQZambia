"""Generate a confusion matrix and return it as a JSON-serialisable dict.

Used by the evaluation stage and exposed via the FastAPI endpoint so
the frontend can render the matrix as a heat-map.
"""

import numpy as np
from sklearn.metrics import confusion_matrix
from typing import Dict, Any, List


def generate_confusion_matrix(y_true, y_pred, labels: List[str] = None) -> Dict[str, Any]:
    """Build a confusion matrix from ground-truth and predicted labels.

    Args:
        y_true: Ground-truth class labels.
        y_pred: Predicted class labels.
        labels: Ordered list of class names for axis ordering.

    Returns:
        Dictionary with ``labels``, the raw ``matrix`` (as nested list),
        and ``shape``.
    """
    matrix = confusion_matrix(y_true, y_pred, labels=labels)
    return {
        "labels": labels if labels is not None else [],
        "matrix": matrix.tolist(),
        "shape": matrix.shape,
    }
