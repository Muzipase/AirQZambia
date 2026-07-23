from typing import Dict, Any


def compare_models(baseline_metrics: Dict[str, Any], optimized_metrics: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "accuracy_difference": optimized_metrics.get("accuracy", 0.0) - baseline_metrics.get("accuracy", 0.0),
        "precision_difference": optimized_metrics.get("precision", 0.0) - baseline_metrics.get("precision", 0.0),
        "recall_difference": optimized_metrics.get("recall", 0.0) - baseline_metrics.get("recall", 0.0),
        "f1_score_difference": optimized_metrics.get("f1_score", 0.0) - baseline_metrics.get("f1_score", 0.0),
    }
