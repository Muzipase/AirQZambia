"""Compute standard classification metrics and optionally persist them.

Accuracy, weighted precision / recall / F1, and a full per-class
report are returned as a flat dictionary suitable for JSON
serialisation and downstream comparison.
"""

import json
import logging
import numpy as np
from pathlib import Path
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def compute_metrics(y_true, y_pred, save_path: Optional[Path] = None) -> Dict[str, Any]:
    """Evaluate predictions and return a metrics dictionary.

    Args:
        y_true: Ground-truth labels.
        y_pred: Predicted labels.
        save_path: If provided the metrics are written as JSON to this path.

    Returns:
        Dictionary containing overall and per-class metrics.
    """
    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, average="weighted", zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, average="weighted", zero_division=0)),
        "f1_score": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        "per_class_metrics": {},
    }

    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
    class_metrics = {
        label: {
            "precision": float(values.get("precision", 0.0)),
            "recall": float(values.get("recall", 0.0)),
            "f1_score": float(values.get("f1-score", 0.0)),
            "support": int(values.get("support", 0)),
        }
        for label, values in report.items()
        if label not in ["accuracy", "macro avg", "weighted avg"]
    }

    metrics["per_class_metrics"] = class_metrics

    if save_path is not None:
        try:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(metrics, f, indent=2)
        except Exception as exc:
            logger.warning("Failed to save metrics to %s: %s", save_path, exc)

    return metrics
