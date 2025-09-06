"""
This module provides functions to apply weighting schemes to co-occurrence matrices commonly used in natural language processing and text mining.

Available weighting methods include:

* Pointwise Mutual Information (PMI) and Positive PMI (PPMI), which measure the association strength between co-occurring terms by comparing observed co-occurrence frequencies to expected frequencies under independence.
* Term Frequency-Inverse Document Frequency (Tf-idf), which reweights term importance based on frequency patterns, leveraging sklearn's TfidfTransformer.

These weighting techniques help enhance the semantic relevance of co-occurrence matrices, improving downstream tasks such as word embedding, clustering, and semantic similarity analysis.

All functions return weighted co-occurrence matrices as Pandas DataFrames for convenient further analysis.
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfTransformer

from ..lib_types import DataFrame, ndarray, Series, csr_matrix


def pmi(co_matrix: DataFrame, positive: bool = False) -> DataFrame:
    """
    Weights a Co-occurrence matrix by PMI or PPMI.
    
    :param co_matrix: A Co-occurrence matrix to be weighted.
    :type co_matrix: DataFrame
    :param positive: If True, weights the Co-ocurrence matrix by PPMI. If False, weighths it by PMI. Defaults to False.
    :type positive: bool

    :returns: A Co-occurrence matrix weighted by PMI or PPMI.
    :rtype: DataFrame
    """

    df: DataFrame = co_matrix

    col_totals: Series = df.sum(axis=0)
    total: float = col_totals.sum()
    row_totals: Series = df.sum(axis=1)
    expected: ndarray = np.outer(row_totals, col_totals) / total
    df = df / expected
    # Silence distracting warnings about log(0):
    with np.errstate(divide='ignore'):
        df = np.log(df)
    df[np.isinf(df)] = 0.0  # log(0) = 0
    if positive:
        df[df < 0] = 0.0

    return df

def tf_idf(co_matrix: DataFrame, **kwargs) -> DataFrame:
    """
    Weights a Co-occurrence matrix by Tf-idf.
    
    :param co_matrix: A Co-occurrence matrix to be weighted.
    :type co_matrix: DataFrame
    :param kwargs: Additional keyword arguments to pass to sklearn's TfidfTransformer. For more information check: https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfTransformer.html
        
    :returns: A Co-occurrence matrix weighted by Tf-idf.
    :rtype: DataFrame
    """

    transformer: TfidfTransformer = TfidfTransformer(**kwargs)
    tf_idf_matrix: csr_matrix = transformer.fit_transform(co_matrix)

    return pd.DataFrame(tf_idf_matrix.toarray(), index=co_matrix.index, columns=co_matrix.columns)