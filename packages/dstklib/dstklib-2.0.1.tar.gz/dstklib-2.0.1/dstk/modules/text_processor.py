"""
This module provides utility functions for processing tokenized or lemmatized text represented as lists of strings 
or POS-tagged tuples. It supports common text normalization and transformation tasks, such as lowercasing, 
vocabulary extraction, and joining tokens into a single string. Additionally, it includes functionality for saving 
processed text or tagged data to a file in plain text or CSV format.

Core functionalities include:

* Converting spaCy tokens to strings (with optional lemmatization)
* Lowercasing and vocabulary extraction
* Joining word lists into full text strings
* Saving word lists or (token, POS) pairs to disk in a consistent format

This module is useful for preparing text data for further analysis, modeling, or storage.
"""

from pathlib import Path

from ..lib_types.dstk_types import Words, POSTaggedWordList, Token, POSTaggedWord

def tokens_to_text(tokens: Words[Token], lemmatize: bool = False) -> Words[str]:
    """
    Converts a list of spaCy Token objects to a list of words represented as strings.

    :param tokens: A list of spaCy tokens. 
    :type tokens: Words[Token]
    :param lemmatize: Whether to return the lemmatized form of each token. Defaults to False.
    :type lemmatize: bool

    :return: A list words represented as strings.
    :rtype: Words[str]
    """

    return [token.lemma_.lower() if lemmatize else token.text for token in tokens]

def to_lower(words: Words[str]) -> Words[str]:
    """
    Returns a list of lower cased words.

    :param words: A list words represented as strings.
    :type words: Words[str]

    :return: A list of words represented as strings.
    :rtype: Words[str]
    """
    
    return [word.lower() for word in words]

def get_vocabulary(words: Words[str]) -> Words[str]:
    """
    Returns the vocabulary a text.

    :param words: A list words represented as strings.
    :type words: Words[str]

    :return: A list of words represented as strings.
    :rtype: Words[str]
    """

    return sorted(set(words))

def join(words: Words[str]) -> str:
    """
    Joins a list of strings into a single string text.

    :param words: A list words represented as strings.
    :type words: Words[str]

    :return:  A single string formed by concatenating the input words separated by spaces.
    :rtype: Words[str]
    """

    return " ".join(words)
    
def save_to_file(words: Words[str] | POSTaggedWordList, path: str) -> str:
    """
    Saves a list of strings or (Token, POS) tuples in the specified path. If tokens is a list of strings, it saves each string in a new line. If it is a list of tuples, it saves each tuple in a new line as a pair or values separated by a comma, in a CSV format.

    :param words: A list words represented as strings or a list of POSTaggedWord tuples.
    :type words: Words[str] or POSTaggedWordList.
    :param path: The path where to save the list of words.
    :type path: str

    :return: The path where the file was saved.
    :rtype: str
    """

    with open(path, "w") as file:
        for word in words:
            if type(word) == str:
                file.write(word + "\n")
            elif isinstance(word, POSTaggedWord):
                if isinstance(word[0], str):
                    file.write(word[0] + "," + word[1] + "\n")
                else:
                    raise ValueError("You can only use save_to_file with a POSTaggedWordList if word is of type of str.")
            else:
                raise ValueError("You can only use save_to_file with Words[srt] | POSTaggedWordList")
    
    return str(Path(path).resolve())
