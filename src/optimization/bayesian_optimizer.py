import optuna
from src.optimization.objective_function import svm_objective


def optimize_svm_hyperparameters(X, y, n_trials: int = 20, cv: int = 3):
    # Adjust CV folds: StratifiedKFold requires at least 2 samples per class
    min_class_count = y.value_counts().min()
    cv = min(cv, max(2, min_class_count))
    if cv < 2:
        cv = 2
    
    pruner = optuna.pruners.MedianPruner(n_startup_trials=5, n_warmup_steps=0)
    study = optuna.create_study(direction="maximize", pruner=pruner)
    study.optimize(lambda trial: svm_objective(trial, X, y, cv=cv), n_trials=n_trials)
    return study.best_params, study
