import streamlit as st
import requests
import pandas as pd
from style_assets import insert_style

API_BASE_URL = "http://localhost:8000"

st.set_page_config(page_title="Model Evaluation", page_icon="📈", layout="wide")
insert_style()

@st.cache_data
def fetch_evaluation_metrics():
    try:
        response = requests.get(f"{API_BASE_URL}/api/evaluation/metrics", timeout=5)
        return response.json() if response.ok else None
    except Exception:
        return None

@st.cache_data
def fetch_model_comparison():
    try:
        response = requests.get(f"{API_BASE_URL}/api/evaluation/comparison", timeout=5)
        return response.json() if response.ok else None
    except Exception:
        return None

@st.cache_data
def get_sample_metrics():
    return {
        "accuracy": 0.88,
        "precision": 0.85,
        "recall": 0.86,
        "f1_score": 0.86,
        "roc_auc": 0.91,
        "support": 120,
    }

st.title("Model Evaluation")

st.markdown("Review model performance metrics, cross-validation results, and classification details.")

metrics = fetch_evaluation_metrics() or {"metrics": get_sample_metrics()}
if "metrics" in metrics:
    values = metrics["metrics"] if isinstance(metrics["metrics"], dict) else metrics
else:
    values = metrics

col1, col2, col3, col4 = st.columns(4)
col1.metric("Accuracy", values.get("accuracy", 0.0))
col2.metric("Precision", values.get("precision", 0.0))
col3.metric("Recall", values.get("recall", 0.0))
col4.metric("F1 Score", values.get("f1_score", 0.0))

st.markdown("---")

st.subheader("Model Metrics Table")
metrics_table = pd.DataFrame(
    [
        {"metric": k, "value": v}
        for k, v in values.items()
        if k in ["accuracy", "precision", "recall", "f1_score", "roc_auc"]
    ]
)
st.dataframe(metrics_table)

st.markdown("---")

st.subheader("Algorithms & Computation Formulas")
st.write(
    "Algorithms used by the hybrid framework with their current values and the formulas used for computation."
)

def format_pct(value):
    try:
        return f"{float(value) * 100:.2f}%"
    except (TypeError, ValueError):
        return "N/A"

def format_pp(value):
    try:
        return f"{float(value) * 100:+.2f} pp"
    except (TypeError, ValueError):
        return "N/A"

comparison_data = fetch_model_comparison() or {}
baseline_metrics = comparison_data.get("baseline_metrics", {})
optimized_metrics = comparison_data.get("optimized_metrics", {})

algorithms_table = pd.DataFrame(
    [
        {
            "Algorithm": "Baseline SVM (RBF kernel)",
            "Value": format_pct(baseline_metrics.get("accuracy", values.get("accuracy"))),
            "Formula": "K(xᵢ, xⱼ) = exp(−γ‖xᵢ − xⱼ‖²); f(x) = sgn(Σ αᵢyᵢK(xᵢ, x) + b), C = 1.0, γ = scale",
        },
        {
            "Algorithm": "Optimized SVM (hybrid framework)",
            "Value": format_pct(optimized_metrics.get("accuracy", values.get("accuracy"))),
            "Formula": "Same RBF decision rule with tuned C ∈ [0.1, 10] (log-scale), γ ∈ {scale, auto}, kernel ∈ {rbf, poly}",
        },
        {
            "Algorithm": "Bayesian Optimization (TPE)",
            "Value": format_pp(comparison_data.get("accuracy_difference", 0)),
            "Formula": "EI(x) = E[max(f(x) − f(x⁺), 0)] maximized over a TPE surrogate of cross-validation accuracy",
        },
        {
            "Algorithm": "SMOTE-Tomek balancing",
            "Value": "k = min(5, n_min − 1)",
            "Formula": "SMOTE: x_new = xᵢ + λ(x_zi − xᵢ), λ ~ U(0, 1); Tomek removes mutual nearest-neighbour pairs of different classes",
        },
        {
            "Algorithm": "SHAP explainability",
            "Value": "mean |φᵢ| per class",
            "Formula": "φᵢ = Σ over S ⊆ F∖{i} of [|S|!(|F|−|S|−1)!/|F|!] · [f(S ∪ {i}) − f(S)]",
        },
        {
            "Algorithm": "Accuracy",
            "Value": format_pct(values.get("accuracy")),
            "Formula": "(TP + TN) / (TP + TN + FP + FN)",
        },
        {
            "Algorithm": "Precision (weighted)",
            "Value": format_pct(values.get("precision")),
            "Formula": "TP / (TP + FP), averaged over classes weighted by support",
        },
        {
            "Algorithm": "Recall (weighted)",
            "Value": format_pct(values.get("recall")),
            "Formula": "TP / (TP + FN), averaged over classes weighted by support",
        },
        {
            "Algorithm": "F1 Score",
            "Value": format_pct(values.get("f1_score")),
            "Formula": "2 × Precision × Recall / (Precision + Recall)",
        },
    ]
)
st.dataframe(algorithms_table)

st.markdown("---")

st.subheader("Cross-Validation")
folds = st.slider("Folds", min_value=3, max_value=10, value=5)
if st.button("Run Cross-Validation"):
    try:
        response = requests.post(f"{API_BASE_URL}/api/evaluation/cross-validate?folds={folds}", timeout=10)
        if response.ok:
            cv_result = response.json()
            st.success("Cross-validation completed")
            st.metric("Mean Accuracy", cv_result.get("mean_accuracy", "N/A"))
            st.metric("Std Accuracy", cv_result.get("std_accuracy", "N/A"))
            if "cv_results" in cv_result:
                st.json(cv_result["cv_results"])
        else:
            st.error("Failed to run cross-validation on the backend.")
            st.write(response.text)
    except Exception as exc:
        st.error(f"Unable to run cross-validation: {exc}")

st.markdown("---")

st.subheader("Evaluation Guidance")
st.write(
    "Use the metrics above to compare model behavior and detect overfitting. "
    "A strong F1 score with balanced precision and recall indicates a good classification model for air quality categories."
)
