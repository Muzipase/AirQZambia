"""Compare evaluation metrics between the baseline and optimised SVM models.

The resulting deltas are surfaced in the Streamlit command centre so
stakeholders can quickly gauge the benefit of Bayesian hyperparameter
tuning.
"""

from typing import Dict, Any


def compare_models(baseline_metrics: Dict[str, Any], optimized_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Compute the difference in metrics between two model runs.

    Args:
        baseline_metrics: Metrics dict produced by ``compute_metrics``
            for the untuned SVM.
        optimized_metrics: Metrics dict for the Bayesian-optimised SVM.

    Returns:
        Dictionary of scalar deltas plus a per-class recall breakdown.
    """
    per_class_recall_difference = {}
    baseline_per_class = baseline_metrics.get("per_class_metrics") or {}
    optimized_per_class = optimized_metrics.get("per_class_metrics") or {}
    for label in baseline_per_class:
        baseline_recall = float(baseline_per_class[label].get("recall", 0.0))
        optimized_recall = float(optimized_per_class.get(label, {}).get("recall", 0.0))
        per_class_recall_difference[label] = optimized_recall - baseline_recall

    return {
        "accuracy_difference": optimized_metrics.get("accuracy", 0.0) - baseline_metrics.get("accuracy", 0.0),
        "precision_difference": optimized_metrics.get("precision", 0.0) - baseline_metrics.get("precision", 0.0),
        "recall_difference": optimized_metrics.get("recall", 0.0) - baseline_metrics.get("recall", 0.0),
        "f1_score_difference": optimized_metrics.get("f1_score", 0.0) - baseline_metrics.get("f1_score", 0.0),
        "per_class_recall_difference": per_class_recall_difference,
    }
