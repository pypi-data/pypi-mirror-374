import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def plot_class_distribution(y_before, y_after, labels=None):
    """Compare class distributions before and after resampling."""
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))

    sns.countplot(x=y_before, ax=ax[0], order=np.unique(y_before))
    ax[0].set_title("Before Resampling")
    if labels:
        ax[0].set_xticklabels(labels)

    sns.countplot(x=y_after, ax=ax[1], order=np.unique(y_after))
    ax[1].set_title("After Resampling")
    if labels:
        ax[1].set_xticklabels(labels)

    plt.tight_layout()
    plt.show()


def plot_synthetic_samples(X, y, X_resampled, y_resampled, title="Synthetic Samples"):
    """Visualize original and synthetic samples in 2D space."""
    if X.shape[1] != 2:
        raise ValueError("plot_synthetic_samples only supports 2D features.")

    n_original = len(X)
    X_syn = X_resampled[n_original:]
    y_syn = y_resampled[n_original:]

    plt.figure(figsize=(8, 6))
    plt.scatter(X[:, 0], X[:, 1], c=y, alpha=0.6, label="Original")
    plt.scatter(X_syn[:, 0], X_syn[:, 1], c=y_syn, marker="x", s=80, label="Synthetic")
    plt.title(title)
    plt.legend()
    plt.show()


def plot_decision_boundary(model, X, y, title="Decision Boundary"):
    """Plot the decision boundary of a classifier (2D features only)."""
    if X.shape[1] != 2:
        raise ValueError("plot_decision_boundary only supports 2D features.")

    x_min, x_max = X[:, 0].min() - 0.5, X[:, 0].max() + 0.5
    y_min, y_max = X[:, 1].min() - 0.5, X[:, 1].max() + 0.5
    xx, yy = np.meshgrid(
        np.linspace(x_min, x_max, 200), np.linspace(y_min, y_max, 200)
    )

    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    plt.figure(figsize=(8, 6))
    plt.contourf(xx, yy, Z, alpha=0.3)
    plt.scatter(X[:, 0], X[:, 1], c=y, edgecolor="k", s=40)
    plt.title(title)
    plt.show()
