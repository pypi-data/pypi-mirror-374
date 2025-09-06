"""
This module provides hooks and utilities for converting between different data types used in the processing model. 

Currently, it includes a hook to convert trained word embedding models (Word2Vec or FastText) into pandas DataFrames, enabling easier manipulation and analysis of embeddings.

Additional conversion hooks can be added in the future to support other type transformations.
"""

import pandas as pd
import numpy as np
from .hook_tools import Hook

from ..lib_types import Words, ndarray, DataFrame, Word2Vec, FastText, NeuralModels

def model_to_dataframe(model: NeuralModels) -> DataFrame:
    """
    Converts a trained Word2Vec or FastText model into a DataFrame of word embeddings.

    :param model: A trained Word2Vec or FastText model.
    :type model: NeuralModels

    :return: A DataFrame containing the word embeddings and their associated labels.
    :rtype: DataFrame
    """

    word_vectors: ndarray
    labels: list[str]

    if isinstance(model, Word2Vec):
        word_vectors = model.wv[model.wv.index_to_key]
        labels = list(model.wv.index_to_key)
    elif isinstance(model, FastText):
        words: Words[str] = model.words
        word_vectors = np.array([model[word] for word in words])
        labels = words

    return pd.DataFrame(word_vectors, index=labels)

ModelToDataframe: Hook = Hook(name="ModelToDataframe", method=model_to_dataframe)

