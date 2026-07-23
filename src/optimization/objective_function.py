from sklearn.model_selection import cross_val_score
from sklearn.svm import SVC
from src.optimization.search_space import get_svm_search_space


def svm_objective(trial, X, y, cv: int = 3):
    params = get_svm_search_space(trial)
    model = SVC(
        kernel=params["kernel"],
        C=params["C"],
        gamma=params["gamma"],
        degree=params.get("degree", 3),
        probability=False,
        random_state=42,
    )
    # For imbalanced multi-class problems prefer macro recall to emphasize minority classes
    scores = cross_val_score(model, X, y, cv=cv, scoring="recall_macro", n_jobs=-1)
    return float(scores.mean())
