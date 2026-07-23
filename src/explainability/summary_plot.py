import shap
import pandas as pd


def create_summary_plot(explainer, X: pd.DataFrame):
    shap_values = explainer.explainer.shap_values(X)
    try:
        return shap.summary_plot(shap_values, X, show=False)
    except Exception:
        return None
