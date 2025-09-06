"""
This module provides utilities for extracting context-based collocates, bigrams, and n-grams from a list of words or tokens. It is designed to support both raw string tokens and spaCy `Token` objects, allowing for flexibility in preprocessing pipelines.

The functions in this module focus on identifying co-occurrence patterns around a specific target word,  as well as extracting fixed-length n-grams from sequences of tokens. This is useful for tasks such as collocation analysis, feature engineering for machine learning models, and exploratory corpus analysis.

Core functionalities include:

* Extracting left and right context windows around a target word
* Creating directed and undirected bigrams centered on a target
* Generating fixed-length n-grams from a sequence of words
* Counting the frequency of collocated words in context windows

The module is compatible with both plain string tokens and spaCy Tokens.
"""


from collections import Counter
import pandas as pd 

from typing import Generator
from ..lib_types import Words, WordCounts, DataFrame, CollocatesList, BigramList, DirectedCollocateList, Token, Bigram


def _find_contexts(words: Words, target_word: str, window_size: tuple[int, int]) -> Generator[tuple[Words, Words], None, None]:
    """
    Yields left and right contexts for each occurrence of a target word in a list of words.

    :param words: A list of words (strings or spaCy Tokens).
    :type words: Words

    :param target_word: The word to find within the list.
    :type target_word: str

    :param window_size: A tuple representing the number of words to include before and after the target word.
    :type window_size: tuple[int, int]

    :return: An Geberator of tuples, where each tuple contains the left and right context around a matched word.
    :rtype: Generator[tuple[Words, Words], None, None]
    """

    for index, word in enumerate(words):
        word_to_compare = word.text if isinstance(word, Token) else word
        if word_to_compare == target_word:
            start: int = max(0, index - window_size[0])
            end: int = min(len(words), index + window_size[1] + 1)

            left_context: Words = words[start:index]
            right_context: Words = words[index + 1:end]

            yield (left_context, right_context)

def extract_collocates(words: Words, target_word: str, window_size: tuple[int, int]) -> CollocatesList:
    """
    Extracts the context words of the target word, returned as tuples whose lenght corresponds to the specified window_size.

    :param words: A list of spaCy tokens or words represented as strings.
    :type words: Words
    :param target_word: The word to find within the list.
    :type target_word: str
    :param window_size: A tuple indicating how many words to capture to the left and right of the target.
    :type window_size: tuple[int, int]

    :returns: A list of collocates (left and right context words) of the target word.
    :rtype: CollocatesList
    """

    return [tuple(left + right) for left, right in _find_contexts(words, target_word, window_size)]

def extract_directed_bigrams(words: Words, target_word: str, window_size: tuple[int, int]) -> DirectedCollocateList:
    """
    Extracts directed bigrams (left and right context words) around a target word.

    For each occurrence of `target_word` in the input `words`, this function collects two types of bigrams:
    * Left bigrams: (context_word, ("L", target_word))
    * Right bigrams: (context_word, ("R", target_word))

    :param words: A list of spaCy tokens or words represented as strings.
    :type words: Words

    :param target_word: The word to search for in the list.
    :type target_word: str

    :param window_size: A tuple indicating how many words to capture to the left and right of the target.
    :type window_size: tuple[int, int]

    :return: A list of directed bigrams in the form `(word, ("L" | "R", target_word))`.
    :rtype: DirectedCollocateList
    """
    bigrams: DirectedCollocateList = []

    for left, right in _find_contexts(words, target_word, window_size):
        bigrams.extend([(word, ("L", target_word)) for word in left])
        bigrams.extend([(word, ("R", target_word)) for word in right])
    
    return bigrams
    
def extract_undirected_bigrams(words: Words, target_word: str, window_size: tuple[int, int]) -> BigramList:
    """
    Extracts undirected bigrams surrounding a target word.

    For each occurrence of `target_word`, this function collects all context words within the specified window (both left and right), and forms a `Bigram` with:
    
    * `collocate`: the context word
    * `target_word`: the target word

    :param words: A list of spaCy tokens or words represented as strings.
    :type words: Words

    :param target_word: The word to search for in the list.
    :type target_word: str

    :param window_size: A tuple indicating how many words to capture to the left and right of the target.
    :type window_size: tuple[int, int]

    :return: A list of `Bigram` namedtuples, one for each context word around each target occurrence.
    :rtype: BigramList
    """
    bigrams: BigramList = []

    for left, right in _find_contexts(words, target_word, window_size):
        bigrams.extend([Bigram(collocate=word, target_word=target_word) for word in left + right])

    return bigrams

def extract_ngrams(words: Words, window_size: int) -> CollocatesList:
    """
    Splits the tokens into groups of window_size consecutive words and joins each group into a string.

    :param words: A list of spaCy tokens or words represented as strings.
    :type words: Words
    :param window_size: size of the square context window.
    :type window_size: int

    :return: A list of tuples, where each tuple contains `window_size` consecutive words from the input.
    :rtype: CollocatesList
    """

    ngrams: CollocatesList = [tuple(words[index:index + window_size]) for index in range(len(words) - window_size + 1)]
    return ngrams

def count_collocates(collocates: CollocatesList) -> DataFrame:
    """
    Counts the frequency of words in a list of collocations and returns the result as a DataFrame.

    :param collocates: A list of collocations, where each collocation is a tuple of words.
    :type collocates: CollocatesList

    :return: A DataFrame with two columns: "word" and "count", sorted by frequency.
    :rtype: DataFrame
    """

    all_words: Words = [word.text if isinstance(word, Token) else word for collocation in collocates for word in collocation]
    word_counts: WordCounts = Counter(all_words)
    word_counts_df: DataFrame = pd.DataFrame(word_counts.items(), columns=["word", "count"])
    
    return word_counts_df