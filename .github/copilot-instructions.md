# GitHub Copilot Workspace Instructions

## Project overview
This repository is an air quality analysis framework built around a Streamlit app, with modular packages for data ingestion, preprocessing, modeling, evaluation, explainability, optimization, and visualization.

## What this workspace is for
- Run the app and explore model output interactively.
- Develop and validate machine learning pipelines for air quality classification or regression.
- Build reusable components for preprocessing, model training, evaluation, and reporting.

## Key folders
- `app/`: Streamlit application entrypoint and pages.
- `src/`: Python package source code.
  - `ingestion/`: data retrieval and validation.
  - `preprocessing/`: cleaning, feature engineering, scaling, and splitting.
  - `models/`: SVM baselines, pipelines, model saving/loading.
  - `optimization/`: hyperparameter search and objective functions.
  - `evaluation/`: metrics, comparison, cross-validation, confusion matrices.
  - `explainability/`: SHAP explainers and visual summaries.
  - `visualization/`: charts, dashboards, and report generation.
  - `utils/`: helpers, exporters, logging, timers.
- `tests/`: unit and integration tests for pipeline components.
- `config/`: YAML configuration and shared constants.
- `data/`, `models/`: runtime data and saved model artifacts.

## How to run
1. Create a Python environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Streamlit app:
   ```bash
   streamlit run app/streamlit_app.py
   ```

## Testing
- Run all tests with:
  ```bash
  pytest
  ```

## Coding conventions
- Keep functions small and single-responsibility.
- Use type hints for public functions and classes.
- Prefer explicit imports and clear module boundaries.
- Keep Streamlit pages focused on UI; move logic into `src/`.

## When working in this workspace
- Prefer changes in `src/` over ad-hoc logic in `app/`.
- Add tests for new functionality in `tests/`.
- Use `config/config.yaml` and `config/constants.py` for reusable settings.

## Suggested prompts for Copilot
- `Implement ingestion and preprocessing for OpenAQ data.`
- `Create a Streamlit dashboard that shows model predictions and SHAP explanations.`
- `Write unit tests for the SVM training pipeline and evaluation metrics.`
- `Add hyperparameter optimization using Optuna for SVM classifiers.`
