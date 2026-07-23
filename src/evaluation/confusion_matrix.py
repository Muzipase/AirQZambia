import numpy as np
from sklearn.metrics import confusion_matrix
from typing import Dict, Any, List


def generate_confusion_matrix(y_true, y_pred, labels: List[str] = None) -> Dict[str, Any]:
    matrix = confusion_matrix(y_true, y_pred, labels=labels)
    return {
        "labels": labels if labels is not None else [],
        "matrix": matrix.tolist(),
        "shape": matrix.shape,
    }
