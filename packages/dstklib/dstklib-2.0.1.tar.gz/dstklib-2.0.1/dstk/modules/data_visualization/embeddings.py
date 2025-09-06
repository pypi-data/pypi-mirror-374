"""
Visualization utilities for word embeddings using UMAP dimensionality reduction.

This module provides a function to project high-dimensional word embeddings into 2D or 3D space for visualization purposes. It uses UMAP to reduce dimensionality while preserving local and global structure, enabling intuitive exploration of semantic relationships between words.

Key features:

* Supports 2D and 3D scatter plots of word embeddings.
* Optionally displays word labels and cluster assignments.
* Allows customization of UMAP parameters such as number of neighbors, distance metric, and minimum distance.
* Supports saving interactive Plotly visualizations as HTML files.

This utility helps linguists, NLP practitioners, and data scientists gain insights from embedding spaces through visual inspection.
"""

import plotly.express as px
from umap import UMAP
import pandas as pd

from ...lib_types import ndarray, DataFrame, Figure


def plot_embeddings(embeddings: DataFrame, n_dimensions: int = 2, labels: bool = False, show: bool = True, path: str | None = None, umap_neighbors: int = 15, umap_metric: str = "cosine", umap_dist: float = 0.1) -> Figure:
    """
    Generates a plot of the word embedddings using UMAP for dimensionality reduction.

    :param embeddings: A dataframe containing the word embeddings.
    :type embeddings: DataFrame
    :n_dimensions: The number of dimensions for the plot. Must be 2 or 3 corresponding to a 2D or 3D scatter plot respectively. This also determines the dimensionality UMAP will reduce the embeddings to. Defaults to 2.
    :type n_dimensions: int
    :param labels: Whether to show word labels on each point. Defaults to False.
    :type labels: bool
    :param show: If True, shows the plot. Defaults to False.
    :type show: bool
    :param path: If provided, saves the plot in the specified path. Defaults to None.
    :type path: str
    :param umap_neighbors: Controls how UMAP balances local versus global structure. Higher values consider a broader context when reducing dimensions. Defaults to 15.
    :type umap_neighbors: int
    :param umap_metric: The distance metric UMAP uses to assess similarity between words (e.g., "cosine", "euclidean"). Defaults to "cosine", which is common for word embeddings.
    :type umap_metric: str
    :param umap_dist: Controls how tightly UMAP packs points together. Lower values keep similar words closer in the 2D space. Defaults to 0.1.
    :type umap_dist: float

    :return: A Plotly Figure object containing the 2D or 3D scatter plot.
    :rtype: Figure
    """

    if n_dimensions not in (2, 3):
        raise ValueError("Only 2D or 3D plots are supported (n_dimensions=2 or 3)")

    reducer: UMAP = UMAP(n_components=n_dimensions, n_neighbors=umap_neighbors, min_dist=umap_dist, metric=umap_metric)
    umap_embeddings: ndarray = reducer.fit_transform(embeddings)

    cols: list[str] = [f"Semantic Axis {i+1}" for i in range(n_dimensions)]

    umap_df = pd.DataFrame(umap_embeddings, index=embeddings.index, columns=cols)

    if "cluster" in embeddings.columns:
        umap_df["Cluster"] = embeddings["cluster"]
    else: 
        umap_df["Cluster"] = "None"

    umap_df["Word"] = umap_df.index

    scatter: Figure

    if n_dimensions == 2:
        scatter = px.scatter(
            umap_df, 
            x=cols[0], 
            y=cols[1], 
            color="Cluster",
            text="Word" if labels else None,
            hover_data=["Word"] + cols + ["Cluster"],
            title="2D Projection of word embeddings",
            color_continuous_scale="Spectral"
        )

        scatter.update_traces(textfont_size=10, textposition="top center")
    else:
        scatter = scatter = px.scatter_3d(
            umap_df, 
            x=cols[0], 
            y=cols[1],
            z=cols[2],
            color="Cluster",
            text="Word" if labels else None,
            hover_data=["Word"] + cols + ["Cluster"],
            title="3D Projection of word embeddings",
            color_continuous_scale="Spectral"
        )

        scatter.update_traces(textfont_size=14, textposition="top center")

    if path:
        scatter.write_html(path)

    if show:
        scatter.show()
    
    return scatter