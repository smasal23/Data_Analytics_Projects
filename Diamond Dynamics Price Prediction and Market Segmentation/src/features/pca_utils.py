from __future__ import annotations

import pandas as pd
from sklearn.decomposition import PCA


def fit_pca(
    X: pd.DataFrame,
    n_components: int | float | None = None,
    random_state: int = 42,
):
    pca = PCA(n_components = n_components, random_state = random_state)
    pca.fit(X)
    return pca


def build_explained_variance_table(pca: PCA):
    return pd.DataFrame({
        "component": [f"PC{i+1}" for i in range(len(pca.explained_variance_ratio_))],
        "explained_variance_ratio": pca.explained_variance_ratio_,
        "cumulative_explained_variance_ratio": pca.explained_variance_ratio_.cumsum(),
    })