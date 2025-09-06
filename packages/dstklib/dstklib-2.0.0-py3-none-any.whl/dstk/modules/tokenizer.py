"""
This module provides utility functions for tokenizing texts using spaCy. 
It offers tools to process raw text into structured linguistic data, extract tokens and sentences, filter words by specific criteria (e.g., stop words, alphanumeric characters, part-of-speech), and 
generate POS-tagged outputs.

Core functionalities include:

* Segemtating a text by applying a spaCy language model to raw text
* Extracting tokens and sentences from processed documents
* Removing stop words and non-alphanumeric tokens
* Filtering tokens by part-of-speech (POS) tags
* Generating (token, POS) tuples for downstream NLP tasks

The module is intended to provide tools for text segmentation and tagging.
"""

import spacy

from ..lib_types.spacy_types import *
from ..lib_types.dstk_types import Words, POSTaggedWordList, POSTaggedWord, WordSenteces

def apply_model(text: str, model: str | Language) -> Doc:
    """
    Takes a text and analyzes it using a language model. It returns a processed version of the text that includes helpful information like the words, their meanings, and how they relate to each other.

    :param text: The text to be processed.
    :type text: str
    :param model: The name of the model to be used or its instance.
    :type model: str or Language

    :return: A spaCy Doc object with linguistic annotations.
    :rtype: Doc
    """

    nlp: Language

    if isinstance(model, str):
        nlp = spacy.load(model)
    else:
        nlp = model

    return nlp(text)


def get_tokens(document: Doc) -> Words[Token]:
    """
    Returns a list of spaCy tokens from a Doc object.

    :param docuument: A spaCy Doc object.
    :type document: Doc

    :return: A list of spaCy tokens.
    :rtype: Words[Token]
    """

    return [token for token in document]
    

def get_sentences(document: Doc) -> WordSenteces: # Check this one return type
    """
     Returns a list of sentences from a spaCy Doc, where each sentence is represented as a list of spaCy Token objects.
    
    :param document: A spaCy Doc object.
    :type document: Doc

    :return: A list of sentences, each sentence is a list of spaCy Tokens.
    :rtype: WordSentences
    """

    return [[token for token in sentence] for sentence in document.sents]

def remove_stop_words(tokens: Words[Token], custom_stop_words: list[str] | None = None) -> Words[Token]:
    """
    Filters tokens, returning only alphanumeric tokens that are not stop words.

    :param tokens: A list of spaCy tokens. 
    :type tokens: Words[Token]
    :param custom_stop_words: If provided, a list of custom stop words. Defaults to None. 
    :type custom_stop_words: list[str] or None

    :return: A list of spaCy tokens.
    :rtype: Words[Token]
    """

    lower_stop_words: list[str]

    if custom_stop_words:
        lower_stop_words = [word.lower() for word in custom_stop_words] 

    return [
            token for token in tokens
            if token.is_alpha and not token.is_stop and 
            (custom_stop_words is None or token.text.lower() not in lower_stop_words)
        ]

def alphanumeric_raw_tokenizer(tokens: Words[Token]) -> Words[Token]:
    """
    Tokenizes a text including only alphanumeric characters and stop words.

    :param tokens: A list of spaCy tokens. 
    :type tokens: Words[Token]

    :return: A list of spaCy tokens.
    :rtype: Words[Token] 
    """

    return [
        token 
        for token in tokens
        if token.text.isalpha()
    ]

def filter_by_pos(tokens: Words[Token], pos: str) -> Words[Token]:
    """
    Returns a list of spaCy tokens filtered by a spacific part-of-speech tag.

    :param tokens: A list of spaCy tokens.
    :type tokens: Words[Token]
    :param pos: The POS tag to filter by (e.g., 'NOUN', 'VERB', etc.). Case-sensitive.
    :type pos: str

    :return: A list of spaCy tokens.
    :rtype: Words[Token] 
    """

    return [token for token in tokens if token.pos_ == pos]

def pos_tagger(tokens: Words[Token]) -> POSTaggedWordList:
    """
    Returns a list of (Token, POS) tuples, pairing each token with its part-of-speech tag.

    :param tokens: A list of spaCy tokens.
    :type tokens: Words[Token]

    :return: A list of POSTaggedWord tuples.
    :rtype: POSTaggedWordList
    """

    return [POSTaggedWord(token, token.pos_) for token in tokens]