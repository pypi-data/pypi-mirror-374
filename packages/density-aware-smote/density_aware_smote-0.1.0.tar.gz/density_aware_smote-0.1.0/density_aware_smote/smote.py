import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.utils import check_random_state


class DensityAwareSMOTE:
    """
    Density Aware SMOTE implementation.

    Generates synthetic samples for the minority class while
    considering local density to avoid oversampling sparse regions
    or undersampling dense regions.

    Parameters
    ----------
    k_neighbors : int, default=5
        Number of nearest neighbors to use for interpolation.

    sampling_strategy : str, float, or dict, default='auto'
        - 'auto' : balance minority to majority class count
        - float : ratio of minority to majority after resampling
        - dict : {class_label: target_count}

    density_exponent : float, default=1.0
        Controls influence of density in probability distribution:
        - 0.0 → uniform sampling (like standard SMOTE)
        - >1.0 → emphasize high-density regions
        - <1.0 → emphasize low-density regions

    neighbor_selection : {'random', 'nearest', 'farthest'}, default='random'
        Strategy for selecting neighbor when generating synthetic samples:
        - 'random'   : randomly pick a neighbor (classic SMOTE)
        - 'nearest'  : always pick the closest neighbor
        - 'farthest' : always pick the farthest neighbor

    random_state : int, default=None
        Random seed for reproducibility.

    Examples
    --------
    >>> import numpy as np
    >>> from density_aware_smote.smote import DensityAwareSMOTE
    >>> from collections import Counter
    >>> X = np.array([[0.1], [0.2], [0.3], [0.4], [2.0], [2.1], [2.2]])
    >>> y = np.array([0, 0, 0, 0, 1, 1, 1])
    >>> print("Before:", Counter(y))
    Before: Counter({0: 4, 1: 3})
    >>> smote = DensityAwareSMOTE(k_neighbors=2, density_exponent=0.5, random_state=42)
    >>> X_res, y_res = smote.fit_resample(X, y)
    >>> print("After:", Counter(y_res))
    After: Counter({0: 4, 1: 4})
    """

    def __init__(
        self,
        k_neighbors=5,
        sampling_strategy="auto",
        density_exponent=1.0,
        neighbor_selection="random",
        random_state=None,
    ):
        self.k_neighbors = k_neighbors
        self.sampling_strategy = sampling_strategy
        self.density_exponent = density_exponent
        self.neighbor_selection = neighbor_selection
        self.random_state = check_random_state(random_state)

    def _calculate_densities(self, X_minority):
        """Compute normalized density distribution for minority samples."""
        nbrs = NearestNeighbors(n_neighbors=self.k_neighbors + 1).fit(X_minority)
        distances, _ = nbrs.kneighbors(X_minority)

        # Exclude self-distance (0)
        avg_distances = distances[:, 1:].mean(axis=1)
        densities = 1 / (avg_distances + 1e-10)

        # Apply exponent control
        densities = np.power(densities, self.density_exponent)

        return densities / densities.sum()

    def _generate_samples(self, X_minority, n_samples, densities):
        """Generate synthetic samples according to density-aware probabilities."""
        n_minority, n_features = X_minority.shape
        synthetic_samples = np.zeros((n_samples, n_features))

        # Choose minority samples weighted by density
        idx = self.random_state.choice(
            np.arange(n_minority), size=n_samples, p=densities
        )

        nbrs = NearestNeighbors(n_neighbors=self.k_neighbors + 1).fit(X_minority)
        distances, neighbor_idx = nbrs.kneighbors(X_minority)

        for i, sample_idx in enumerate(idx):
            neighbors = neighbor_idx[sample_idx][1:]  # exclude self
            neighbor_distances = distances[sample_idx][1:]

            if self.neighbor_selection == "random":
                chosen_neighbor = self.random_state.choice(neighbors)

            elif self.neighbor_selection == "nearest":
                chosen_neighbor = neighbors[np.argmin(neighbor_distances)]

            elif self.neighbor_selection == "farthest":
                chosen_neighbor = neighbors[np.argmax(neighbor_distances)]

            else:
                raise ValueError(
                    "Invalid neighbor_selection. Choose from {'random','nearest','farthest'}"
                )

            diff = X_minority[chosen_neighbor] - X_minority[sample_idx]
            gap = self.random_state.rand()
            synthetic_samples[i] = X_minority[sample_idx] + gap * diff

        return synthetic_samples

    def fit_resample(self, X, y):
        """
        Apply Density Aware SMOTE to balance dataset.

        Parameters
        ----------
        X : np.ndarray
            Feature matrix.
        y : np.ndarray
            Target vector.

        Returns
        -------
        X_resampled : np.ndarray
            Resampled feature matrix.
        y_resampled : np.ndarray
            Resampled target vector.
        """
        from collections import Counter

        class_counts = Counter(y)
        minority_class = min(class_counts, key=class_counts.get)
        majority_class = max(class_counts, key=class_counts.get)

        n_minority = class_counts[minority_class]
        n_majority = class_counts[majority_class]

        # Determine how many samples to generate
        if self.sampling_strategy == "auto":
            n_samples_to_generate = n_majority - n_minority

        elif isinstance(self.sampling_strategy, float):
            target_minority = int(n_majority * self.sampling_strategy)
            n_samples_to_generate = max(0, target_minority - n_minority)

        elif isinstance(self.sampling_strategy, dict):
            if minority_class not in self.sampling_strategy:
                raise ValueError("Minority class not specified in sampling_strategy dict.")
            target_minority = self.sampling_strategy[minority_class]
            n_samples_to_generate = max(0, target_minority - n_minority)

        else:
            raise ValueError("Invalid sampling_strategy type.")

        # Extract minority samples
        X_minority = X[y == minority_class]

        # Compute density distribution
        densities = self._calculate_densities(X_minority)

        # Generate synthetic samples
        synthetic_samples = self._generate_samples(
            X_minority, n_samples_to_generate, densities
        )

        # Resample dataset
        X_resampled = np.vstack([X, synthetic_samples])
        y_resampled = np.hstack([y, np.full(n_samples_to_generate, minority_class)])

        return X_resampled, y_resampled
