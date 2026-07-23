from sklearn.svm import SVC


def train_baseline_svm(X, y, random_state: int = 42):
    model = SVC(kernel="rbf", C=1.0, gamma="scale", probability=False, random_state=random_state)
    model.fit(X, y)
    return model
