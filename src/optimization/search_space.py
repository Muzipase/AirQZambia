from optuna.trial import Trial


def get_svm_search_space(trial: Trial) -> dict:
    kernel = trial.suggest_categorical("kernel", ["rbf", "poly"])
    params = {
        "kernel": kernel,
        "C": trial.suggest_float("C", 0.1, 10.0, log=True),
        "gamma": trial.suggest_categorical("gamma", ["scale", "auto"]),
    }

    if kernel == "poly":
        params["degree"] = trial.suggest_int("degree", 2, 4)
    else:
        params["degree"] = 3

    return params
