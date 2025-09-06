"""
This module provides functions to construct common matrix representations used in text analysis and natural language processing.

Key features include:

* Creating a Document-Term Matrix (DTM) from a corpus of text, leveraging sklearn's CountVectorizer with customizable parameters such as stop word removal and n-gram range.
* Generating a Co-occurrence Matrix from a given Document-Term Matrix, capturing how frequently terms co-occur across documents.

These matrices are foundational for many NLP and Computational Linguistics tasks, including topic modeling, word embedding training, and network analysis. The output is provided as Pandas DataFrames for ease of analysis and integration with data science workflows.
"""

from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import pandas as pd

from ..lib_types import csr_matrix, DataFrame, ndarray

def create_dtm(corpus: list[str], **kwargs) -> DataFrame:
    """
    Creates Document Term Matrix (DTM).

    :param corpus: A list of sentences or collocations from which to build a matrix.
    :type corpus: list[str]
    :param kwargs: Additional keyword arguments to pass to sklearn's CountVectorizer. Common options include:

        * **stop_words:** If provided, a list of stopwords to remove from the corpus.
        * **ngram_range:** A tuple (min_n, max_n) specifying the range of n-grams to consider.
    
    For more information check: https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.CountVectorizer.html

    :return: A Document Term Matrix (DTM).
    :rtype: DataFrame.
    """

    vectorizer: CountVectorizer = CountVectorizer(**kwargs)

    dtm: csr_matrix = vectorizer.fit_transform(corpus)

    return pd.DataFrame(dtm.toarray(), index=np.array(corpus), columns=vectorizer.get_feature_names_out())

def create_co_occurrence_matrix(dtm: DataFrame) -> DataFrame:
    """
    Creates a Co-occurrence matrix from a Document Term Matrix (DTM).

    :param dtm: A Document Term Matrix (DTM) from which to build a Co-occurrence matrix.
    :type dtm: DataFrame

    :return: A Co-occurrence matrix.
    :rtype: DataFrame
    """
    matrix: ndarray = dtm.to_numpy()

    co_matrix: ndarray = matrix.T @ matrix

    return pd.DataFrame(co_matrix, index=dtm.columns, columns=dtm.columns)