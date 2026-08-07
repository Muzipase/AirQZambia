"""
End-to-end ML pipeline: fetch data, preprocess, balance, train, evaluate.
Usage: python scripts/run_pipeline.py [--source auto|openmeteo|openaq] [--city Lusaka] [--historical]
"""
import sys
import argparse
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.paths import (
    RAW_DATA_PATH, PROCESSED_DATA_PATH,
    BASELINE_MODEL_PATH, OPTIMIZED_MODEL_PATH,
    METRICS_PATH, SCALER_PATH, SHAP_PLOTS_DIR, COMPARISON_PATH, CONFUSION_MATRIX_PATH, SHAP_PER_CLASS_PATH, ensure_dirs,
)
from src.ingestion.fetch_data import fetch_data
from src.preprocessing.clean_data import clean_data
from src.preprocessing.missing_values import fill_missing_values
from src.preprocessing.feature_engineering import engineer_features
from src.preprocessing.scaling import fit_scaler, save_scaler, apply_scaler_to_dataframe
from src.preprocessing.split_dataset import split_data
from src.preprocessing.multicollinearity import compute_vif
from src.balancing.smote_tomek import apply_smote_tomek
from src.models.baseline_svm import train_baseline_svm
from src.models.optimized_svm import train_optimized_svm
from src.evaluation.metrics import compute_metrics
from src.evaluation.comparison import compare_models
from src.evaluation.confusion_matrix import generate_confusion_matrix

import joblib
import pandas as pd
import json

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

NON_FEATURE_COLUMNS = {"aqi_category", "timestamp", "location", "city", "country"}


def run_pipeline(source: str = "auto", city: str = None, historical: bool = False):
    ensure_dirs()

    # 1. Fetch data
    if historical:
        logger.info("Fetching HISTORICAL data (2022-present)...")
        from src.ingestion.openmeteo_client import fetch_historical_data
        data = fetch_historical_data(city=city)
    else:
        logger.info("Fetching data (source=%s, city=%s)...", source, city)
        data = fetch_data(source=source, city=city)
    if data is None or data.empty:
        logger.error("No data retrieved. Aborting.")
        return False
    data.to_csv(RAW_DATA_PATH, index=False)
    logger.info("Fetched %d records, saved to %s", len(data), RAW_DATA_PATH)

    # 2. Preprocess
    logger.info("Preprocessing...")
    data = clean_data(data)
    data = fill_missing_values(data)
    data = engineer_features(data)

    feature_columns = [col for col in data.columns if col not in NON_FEATURE_COLUMNS]
    # Keep only numeric columns as features (exclude booleans, strings)
    feature_columns = [col for col in feature_columns if pd.api.types.is_numeric_dtype(data[col]) and not pd.api.types.is_bool_dtype(data[col])]
    _, scaler = fit_scaler(data[feature_columns])
    save_scaler(scaler, SCALER_PATH)
    data = apply_scaler_to_dataframe(data, scaler, feature_columns)
    data.to_csv(PROCESSED_DATA_PATH, index=False)
    logger.info("Preprocessed %d records, saved to %s", len(data), PROCESSED_DATA_PATH)

    # 3. Multicollinearity check
    feature_cols = [c for c in data.columns if c not in NON_FEATURE_COLUMNS and pd.api.types.is_numeric_dtype(data[c]) and not pd.api.types.is_bool_dtype(data[c])]
    vif_df = compute_vif(data, feature_cols)
    logger.info("VIF analysis:\n%s", vif_df.to_string(index=False))

    # 4. Split & balance
    X = data[feature_cols]
    y = data['aqi_category']

    X_train, X_test, y_train, y_test = split_data(X, y)
    logger.info("Split: train=%d, test=%d", len(X_train), len(X_test))

    X_train_bal, y_train_bal = apply_smote_tomek(X_train, y_train)
    logger.info("After SMOTE-Tomek: %d records (was %d)", len(X_train_bal), len(X_train))

    # Baseline trains on ORIGINAL imbalanced training data (no SMOTE),
    # per proposal §7.5. Optimized trains on the balanced set.
    X_train_base, y_train_base = X_train, y_train

    # Subsample if training sets are too large for SVM training speed
    MAX_TRAIN = 30000
    if len(X_train_base) > MAX_TRAIN:
        from sklearn.utils import resample
        X_train_base, y_train_base = resample(
            X_train_base, y_train_base, n_samples=MAX_TRAIN, random_state=42, stratify=y_train_base
        )
        logger.info("Baseline subsampled to %d records (imbalanced) for training speed", MAX_TRAIN)
    if len(X_train_bal) > MAX_TRAIN:
        from sklearn.utils import resample
        X_train_bal, y_train_bal = resample(
            X_train_bal, y_train_bal, n_samples=MAX_TRAIN, random_state=42, stratify=y_train_bal
        )
        logger.info("Optimized subsampled to %d records for training speed", MAX_TRAIN)

    # 5. Train baseline (imbalanced data)
    logger.info("Training baseline SVM on imbalanced data...")
    baseline_model = train_baseline_svm(X_train_base, y_train_base)
    joblib.dump(baseline_model, BASELINE_MODEL_PATH)
    logger.info("Baseline model saved to %s", BASELINE_MODEL_PATH)

    # 6. Train optimized
    logger.info("Training optimized SVM with Bayesian optimization...")
    optimized_model, best_params, study = train_optimized_svm(X_train_bal, y_train_bal)
    joblib.dump(optimized_model, OPTIMIZED_MODEL_PATH)
    logger.info("Optimized model saved to %s (best params: %s)", OPTIMIZED_MODEL_PATH, best_params)

    # 7. Evaluate
    baseline_metrics = compute_metrics(y_test, baseline_model.predict(X_test))
    optimized_metrics = compute_metrics(y_test, optimized_model.predict(X_test), save_path=METRICS_PATH)
    logger.info(
        "Baseline — Accuracy: %.4f, F1: %.4f",
        baseline_metrics['accuracy'], baseline_metrics['f1_score'],
    )
    logger.info(
        "Optimized — Accuracy: %.4f, F1: %.4f",
        optimized_metrics['accuracy'], optimized_metrics['f1_score'],
    )

    # 7b. Baseline vs optimized comparison
    comparison = compare_models(baseline_metrics, optimized_metrics)
    comparison["baseline_metrics"] = baseline_metrics
    comparison["optimized_metrics"] = optimized_metrics
    COMPARISON_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(COMPARISON_PATH, "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2)
    logger.info("Comparison saved to %s (accuracy delta: %+.4f)", COMPARISON_PATH, comparison["accuracy_difference"])

    # 7c. Confusion matrices for both models
    labels = sorted(set(y_test.tolist()))
    baseline_cm = generate_confusion_matrix(y_test, baseline_model.predict(X_test), labels=labels)
    optimized_cm = generate_confusion_matrix(y_test, optimized_model.predict(X_test), labels=labels)
    CONFUSION_MATRIX_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFUSION_MATRIX_PATH, "w", encoding="utf-8") as f:
        json.dump({"labels": labels, "baseline": baseline_cm, "optimized": optimized_cm}, f, indent=2)
    logger.info("Confusion matrices saved to %s", CONFUSION_MATRIX_PATH)

    # 8. Save SHAP beeswarm plot and per-class feature importance
    try:
        from src.explainability.shap_explainer import ShapExplainer
        explainer = ShapExplainer(optimized_model, X_train_bal)
        shap_sample = X_test.sample(n=min(50, len(X_test)), random_state=42)
        explainer.save_summary_plot(shap_sample, SHAP_PLOTS_DIR)

        per_class_importance = explainer.get_per_class_importance(X_test, y_test)
        SHAP_PER_CLASS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(SHAP_PER_CLASS_PATH, "w", encoding="utf-8") as f:
            json.dump(per_class_importance, f, indent=2)
        logger.info("Per-class SHAP importance saved to %s", SHAP_PER_CLASS_PATH)
    except Exception as e:
        logger.warning("Could not save SHAP artifacts: %s", e)

    logger.info("Pipeline complete.")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Air Quality ML Pipeline")
    parser.add_argument("--source", default="auto", choices=["auto", "openmeteo", "openaq"])
    parser.add_argument("--city", default=None)
    parser.add_argument("--historical", action="store_true", help="Fetch multi-year historical data from Open-Meteo (2022-present)")
    args = parser.parse_args()
    success = run_pipeline(source=args.source, city=args.city, historical=args.historical)
    sys.exit(0 if success else 1)
