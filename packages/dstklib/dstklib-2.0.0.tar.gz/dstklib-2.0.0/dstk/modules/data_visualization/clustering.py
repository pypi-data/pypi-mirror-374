"""
Clustering utilities for word embeddings analysis and visualization.

This module provides functions to determine the optimal number of clusters for word embeddings using popular methods such as the Elbow method and Silhouette score. It also assigns cluster labels to the embeddings accordingly.

Key features:

* *elbow_method:* Applies the Elbow method on embeddings to find the best cluster count by minimizing inertia.
* *extract_silhouette_score:* Uses the Silhouette score to evaluate clustering quality and determine the optimal cluster number.
* Both functions support visualization of their respective metrics and can save plots to file.
* Cluster labels are appended to the embeddings DataFrame for easy downstream use, such as visualization or further analysis.

These utilities are designed to work seamlessly with word embedding DataFrames, enabling efficient and interpretable clustering analysis.
"""


import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from kneed import KneeLocator

from ...lib_types import DataFrame, Figure

def elbow_method(embeddings: DataFrame, max_clusters: int, show: bool = False, path: str | None = None) -> DataFrame:
    """
    Applies the Elbow method to determine the optimal number of clusters for word embeddings, and assigns cluster labels based on the identified value.

    :param embeddings: A dataframe containing the word embeddings.
    :type embeddings: DataFrame
    :param max_clusters: The maximum number of clusters to evaluate when applying the Elbow method.
    :type max_clusters: int
    :param show: If True, shows the plot. Defaults to False.
    :type show: bool
    :param path: If provided, saves the plot in the specified path. Defaults to None.
    :type path: str

    :returns: A copy of the input DataFrame with an additional `'cluster'` column containing the cluster labels.
    :rtype: DataFrame
    """
    df: DataFrame = embeddings.copy()
    means: list[int] = []
    inertias: list[float] = []

    for k in range(1, max_clusters):
        kmeans: KMeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(embeddings)

        means.append(k)
        inertias.append(kmeans.inertia_)

    elbow: KneeLocator = KneeLocator(means, inertias, curve="convex", direction="decreasing")

    elbow_plot: Figure = px.line(
        x=means, 
        y=inertias, 
        markers=True,
        title="Elbow method",
        labels={
            "x": "Number of clusters",
            "y": "Inertia"
        }
    )

    if path:
        elbow_plot.write_html(path)

    if show:
        elbow_plot.show()

    print(f"The best cluster is {elbow.knee} with an inertia of {elbow.knee_y}")

    cluster_kmeans: KMeans = KMeans(n_clusters=elbow.knee, random_state=42)
    df["cluster"] = cluster_kmeans.fit_predict(df)

    return df

def extract_silhouette_score(embeddings: DataFrame, max_clusters: int, show: bool = False, path: str | None = None, **kwargs) -> DataFrame:
    """
    Extracts the Silhouette score to determine the optimal number of clusters for word embeddings, and assigns cluster labels based on the identified value.

    :param embeddings: A dataframe containing the word embeddings.
    :type embeddings: DataFrame
    :param max_clusters: The maximum number of clusters to evaluate when applying the Elbow method.
    :type max_clusters: int
    :param show: If True, shows the plot. Defaults to False.
    :type show: bool
    :param path: If provided, saves the plot in the specified path. Defaults to None.
    :type path: str
    :param kwargs: Additional keyword arguments to pass to sklearn.metrics silhouette_score. For more information check: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html

    :returns: A copy of the input DataFrame with an additional `'cluster'` column containing the cluster labels.
    :rtype: DataFrame
    """
    df: DataFrame = embeddings.copy()

    sil_scores: list[tuple[int, float]] = []

    for k in range(2, max_clusters):
        kmeans: KMeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(embeddings)
        sil_score: float = silhouette_score(embeddings, kmeans.labels_, **kwargs)
        sil_scores.append((k, sil_score))

    highest_score: tuple[int, float] = max(sil_scores, key=lambda tup: tup[1])
    print(f"The best cluster is {highest_score[0]} with a Silhouette score of {highest_score[1]}")

    cluster_kmeans: KMeans = KMeans(n_clusters=highest_score[0], random_state=42)
    df["cluster"] = cluster_kmeans.fit_predict(df)

    clusters, scores = zip(*sil_scores)
    
    sil_plot: Figure = px.line(
        x=clusters, 
        y=scores, 
        markers=True,
        title="Silhouette Score",
        labels={
            "x": "Number of Clusters",
            "y": "Silhouette Scores"
        }
    )

    if path:
        sil_plot.write_html(path)

    if show:
        sil_plot.show()

    return df