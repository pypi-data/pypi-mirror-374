"""
This module provides functions to compute geometric distance and similarity measures  between word embeddings, enabling semantic comparison of words in vector space.

Available metrics include:

* Euclidean distance
* Manhattan distance
* Cosine similarity

Additionally, it offers a method to find the nearest semantic neighbors of a given word based on specified distance or similarity metrics using scikit-learn's NearestNeighbors.

All functions operate on word embeddings represented as Pandas DataFrames indexed by words, facilitating easy integration with common NLP and Computational Linguistic workflows.
"""

from sklearn.neighbors import NearestNeighbors
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from ..lib_types import ndarray, Series, DataFrame, Neighbors, Neighbor

def euclidean_distance(embeddings: DataFrame, first_word: str, second_word: str) -> float:
    """
    Computes the Euclidean distance between the embeddings of two words.

    :param embeddings: A dataframe containing the word embeddings.
    :type embeddings: DataFrame
    :param first_word: The first word in the pair.
    :type first_word: str
    :param second_word: The second word in the pair.
    :type second_word: str

    :returns: The Euclidean distance between the first and second word.
    :rtype: float
    """

    first_word_vector: Series = embeddings.loc[first_word]
    second_word_vector: Series = embeddings.loc[second_word]

    return float(np.linalg.norm(first_word_vector - second_word_vector))

def manhattan_distance(embeddings: DataFrame, first_word: str, second_word: str) -> float:
    """
    Computes the Manhattan distance between the embeddings of two words.

    :param embeddings: A dataframe containing the word embeddings.
    :type embeddings: DataFrame
    :param first_word: The first word in the pair.
    :type first_word: str
    :param second_word: The second word in the pair.
    :type second_word: str

    :returns: The Manhattan distance between the first and second word.
    :rtype: float
    """

    first_word_vector: Series = embeddings.loc[first_word]
    second_word_vector: Series = embeddings.loc[second_word]

    return np.sum(np.abs(first_word_vector - second_word_vector))

def cos_similarity(embeddings: DataFrame, first_word: str, second_word: str) -> float:
    """
    Computes the cosine similarity between the embeddings of two words.

    :param embeddings: A dataframe containing the word embeddings.
    :type embeddings: DataFrame
    :param first_word: The first word in the pair.
    :type first_word: str
    :param second_word: The second word in the pair.
    :type second_word: str

    :returns: The cosine similarity between the first and second word.
    :rtype: float
    """

    first_word_vector: ndarray = np.array(embeddings.loc[first_word]).reshape(1, -1)
    second_word_vector: ndarray = np.array(embeddings.loc[second_word]).reshape(1, -1)

    cos_sim: ndarray = cosine_similarity(first_word_vector, second_word_vector)

    return cos_sim[0][0]

def nearest_neighbors(embeddings: DataFrame, word: str, metric: str = "cosine", n_words: int = 5, **kwargs) -> Neighbors:
    """
    Returns the top N most semantically similar words to a given target word, based on the specified distance or similarity metric.

    :param embeddings: A dataframe containing the word embeddings.
    :type embeddings: DataFrame
    :param word: The target word to find neighbors for.
    :type word: str
    :param metric: The distance or similarity metric to use (e.g., 'cosine', 'euclidean'). Defaults to 'cosine'.
    :type metric: str
    :param n_words: Number of nearest neighbors to return. Defaults to 5.
    :type of n_words: int
    :param kwargs: Additional keyword arguments to pass to sklearn's NearestNeighbors. For more information check: https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.NearestNeighbors.html

    :returns: A list of `Neighbor` namedtuples, one for each word close to the target word.
    :rtype: Neighbors
    """

    neighbors: NearestNeighbors = NearestNeighbors(n_neighbors=n_words, algorithm="auto", metric=metric, **kwargs)
    neighbors.fit(embeddings.to_numpy())

    word_vector: Series = embeddings.loc[word]

    distances: ndarray
    indices: ndarray
    distances, indices = neighbors.kneighbors([word_vector], n_neighbors=n_words + 1)

    neighbor_tuples = zip(indices[0], distances[0])

    results: Neighbors = [Neighbor(embeddings.index[index], 1 - distance) for index, distance in neighbor_tuples if embeddings.index[index] != word]

    return results