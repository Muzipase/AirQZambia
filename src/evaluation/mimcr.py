from sklearn.metrics import classification_report
from typing import Dict, Any


def generate_classification_report(y_true, y_pred) -> Dict[str, Any]:
    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
    return report
