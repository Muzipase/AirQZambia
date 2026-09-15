"""Generate a scikit-learn classification report as a dictionary.

Exposes the full precision / recall / f1 / support breakdown for each
class; used by the evaluation stage and the FastAPI response payload.
"""

from sklearn.metrics import classification_report
from typing import Dict, Any


def generate_classification_report(y_true, y_pred) -> Dict[str, Any]:
    """Return the classification report as a nested dictionary.

    Args:
        y_true: Ground-truth labels.
        y_pred: Predicted labels.

    Returns:
        Dictionary keyed by class label with per-class metrics,
        plus aggregate rows.
    """
    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
    return report
