import importlib
import pytest


def test_models_modules_importable():
	"""Ensure model modules are importable from the package namespace."""
	names = ["src.models.baseline_svm", "src.models.svm_pipeline", "src.models.optimized_svm"]
	for name in names:
		try:
			mod = importlib.import_module(name)
		except Exception as e:
			pytest.fail(f"Failed to import {name}: {e}")


def test_basic_sklearn_svm_training():
	
	sklearn = pytest.importorskip("sklearn")
	from sklearn.svm import SVC
	from sklearn.datasets import make_classification
	from sklearn.model_selection import train_test_split
	from sklearn.metrics import accuracy_score

	X, y = make_classification(n_samples=200, n_features=5, n_informative=3, n_redundant=0, random_state=0)
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
	clf = SVC(kernel="rbf", probability=False, random_state=0)
	clf.fit(X_train, y_train)
	preds = clf.predict(X_test)
	acc = accuracy_score(y_test, preds)
	assert acc >= 0.5

