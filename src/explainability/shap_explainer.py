import logging
from pathlib import Path

import numpy as np
import pandas as pd
import shap

logger = logging.getLogger(__name__)

N_KMEANS_BACKGROUND = 50


class ShapExplainer:
    def __init__(self, model, background_data: pd.DataFrame):
        self.model = model
        self.background_data = background_data.copy()
        self.feature_names = list(background_data.columns)

        n_clusters = min(N_KMEANS_BACKGROUND, len(self.background_data))
        kmeans_obj = shap.kmeans(self.background_data, n_clusters)
        background_kmeans = pd.DataFrame(kmeans_obj.data, columns=self.feature_names)
        logger.info("SHAP background: %d kmeans clusters from %d samples", n_clusters, len(self.background_data))

        self.explainer = shap.KernelExplainer(
            self._model_predict, background_kmeans, link="identity"
        )

    def _model_predict(self, data: np.ndarray) -> np.ndarray:
        df = pd.DataFrame(data, columns=self.feature_names)
        if hasattr(self.model, "predict_proba") and callable(getattr(self.model, "predict_proba", None)):
            return self.model.predict_proba(df)
        return self.model.decision_function(df)

    def get_summary(self):
        n_clusters = min(25, len(self.background_data))
        kmeans_obj = shap.kmeans(self.background_data, n_clusters)
        sample = pd.DataFrame(kmeans_obj.data, columns=self.feature_names)
        shap_values = self.explainer.shap_values(sample)

        if isinstance(shap_values, list):
            aggregated = np.mean([np.abs(values).mean(axis=0) for values in shap_values], axis=0)
        else:
            aggregated = np.mean(np.abs(shap_values), axis=0)

        return {
            feature: float(aggregated[idx])
            for idx, feature in enumerate(self.feature_names)
        }

    def get_per_class_importance(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        top_k: int = 3,
        max_per_class: int = 100,
    ) -> dict:
        """Return the top-k most influential features per AQI category.

        Uses the mean absolute SHAP value of the predicted class for each
        sample, grouped by the true category. Subsamples up to ``max_per_class``
        rows per category to keep KernelExplainer computation tractable.
        """
        X = X.reset_index(drop=True)
        y = pd.Series(list(y)).reset_index(drop=True)

        sampled_idx = []
        for label in y.unique():
            sampled_idx.extend(np.where(y.values == label)[0][:max_per_class].tolist())
        X = X.iloc[sampled_idx]
        y = y.iloc[sampled_idx]
        predictions = self.model.predict(X)

        raw = self.explainer.shap_values(X)
        if isinstance(raw, list):
            shap_by_class = {str(cls): np.asarray(v) for cls, v in zip(self.model.classes_, raw)}
            class_key = lambda p: str(p)
        elif isinstance(raw, np.ndarray) and raw.ndim == 3:
            shap_by_class = {str(cls): raw[i] for i, cls in enumerate(self.model.classes_)}
            class_key = lambda p: str(p)
        else:
            shap_by_class = {None: np.asarray(raw)}
            class_key = lambda p: None

        result = {}
        for label in y.unique():
            mask = (y.values == label)
            rows = [shap_by_class[class_key(predictions[i])][i] for i in range(len(X)) if mask[i]]
            if not rows:
                continue
            mean_abs = np.mean(np.abs(np.array(rows)), axis=0)
            order = np.argsort(mean_abs)[::-1][:top_k]
            result[str(label)] = [
                {"feature": self.feature_names[idx], "importance": float(mean_abs[idx])}
                for idx in order
            ]
        return result

    def explain_instance(self, input_df: pd.DataFrame):
        shap_values = self.explainer.shap_values(input_df)
        if isinstance(shap_values, list):
            values = [vals[0].tolist() if len(vals) else [] for vals in shap_values]
        else:
            values = shap_values[0].tolist() if shap_values.ndim > 1 else shap_values.tolist()

        ev = getattr(self.explainer, "expected_value", None)
        if ev is not None:
            base_values = [float(v) for v in ev] if hasattr(ev, "__iter__") else [float(ev)]
        else:
            base_values = []
        return {
            "feature_names": self.feature_names,
            "shap_values": values,
            "base_values": base_values,
        }

    def save_summary_plot(self, X: pd.DataFrame, save_dir: Path) -> Path:
        """Save SHAP beeswarm plot as high-res PNG for non-Python stakeholders."""
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        save_dir.mkdir(parents=True, exist_ok=True)
        shap_values = self.explainer.shap_values(X)

        plt.figure(figsize=(10, 6))
        shap.summary_plot(shap_values, X, show=False)
        plt.tight_layout()

        png_path = save_dir / "shap_beeswarm.png"
        plt.savefig(str(png_path), dpi=200, bbox_inches="tight")
        plt.close()
        logger.info("SHAP beeswarm plot saved to %s", png_path)
        return png_path
