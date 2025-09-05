import numpy as np
from density_aware_smote.smote import DensityAwareSMOTE
from collections import Counter

def test_resampling():
    X = np.array([[0.1], [0.2], [0.3], [0.4], [2.0], [2.1], [2.2]])
    y = np.array([0, 0, 0, 0, 1, 1, 1])
    smote = DensityAwareSMOTE(k_neighbors=2, random_state=42)
    X_res, y_res = smote.fit_resample(X, y)
    counts = Counter(y_res)
    assert counts[0] == counts[1], "Classes should be balanced"
