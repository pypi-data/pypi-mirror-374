"""
Provides a set of type guard functions to safely and explicitly check the types of various token and workflow-related objects.

These functions help with runtime type checking and enable more precise type hinting and static analysis when working with linguistic data structures such as:

* POS-tagged word lists
* Collocates lists
* Sentences (token or string sequences)
* Workflow step definitions
* Token-based collocates

By using these type guards, code can branch safely based on the structure and types of input data, improving robustness and developer experience.

Example:

.. code-block:: python

    if is_pos_tags(tokens):
        # tokens is now narrowed to POSTaggedWordList type
        process_pos_tags(tokens)
"""

from typing import Any, TypeGuard
from ..lib_types import POSTaggedWordList, CollocatesList, Sentences, Token, Workflow, POSTaggedWord, Bigram, Collocates

def is_pos_tags(tokens: Any) -> TypeGuard[POSTaggedWordList]:
    """
    Checks if the input is a list of POS-tagged words (POSTaggedWordList).

    :param tokens: The object to check.
    :type tokens: Any

    :return: True if `tokens` is a non-empty list where all elements are instances of POSTaggedWord, otherwise False.
    :rtype: bool
    """

    if not isinstance(tokens, list) or not tokens:
        return False
    return all(isinstance(item, POSTaggedWord) for item in tokens)

def is_collocates(tokens: Any) -> TypeGuard[CollocatesList]:
    """
    Checks if the input is a list of collocate tuples, where each tuple contains strings or Token instances, cexcluding types like POSTaggedWord or Bigram.

    :param tokens: The object to check.
    :type tokens: Any

    :return: True if `tokens` is a non-empty list of tuples of strings or Token instances (excluding POSTaggedWord and Bigram), otherwise False.
    :rtype: bool
    """

    if not isinstance(tokens, list) or not tokens:
        return False

    return all(
        isinstance(item, tuple) and
        not isinstance(item, POSTaggedWord) and
        not isinstance(item, Bigram) and
        all(
            isinstance(word, str) or
            isinstance(word, Token)
            for word in item
        )
        for item in tokens
    )

def is_sentence(tokens: Any) -> TypeGuard[Sentences]:
    """
    Checks if the input is a list of sentences, where each sentence is either:
    
    * A list of Token instances,
    * A list of strings, or
    * A list of POSTaggedWord instances.

    :param tokens: The object to check.
    :type tokens: Any

    :return: True if `tokens` matches the described sentence structure, otherwise False.
    :rtype: bool
    """

    if not isinstance(tokens, list) or not tokens:
        return False

    return (
        isinstance(tokens, list) and 
        all(
            (
                isinstance(item, list) and 
                (
                    all(isinstance(token, Token) for token in item) or 
                    all(isinstance(token, str) for token in item)
                )
            ) or is_pos_tags(item)
            for item in tokens
        )
    )

def is_workflow(workflow: Any) -> TypeGuard[Workflow]:
    """
    Checks if the input is a workflow structure, i.e., a non-empty list of dictionaries where each dictionary maps string method names to argument dictionaries with string keys.

    :param workflow: The object to check.
    :type workflow: Any

    :return: True if `workflow` matches the workflow structure, otherwise False.
    :rtype: bool
    """

    if not isinstance(workflow, list) or not workflow:
        return False

    return all(
        isinstance(method, dict) and
        all(
            isinstance(key, str) and
            isinstance(value, dict) and
            all(
                isinstance(arg, str)
                for arg in value.keys()
            )
            for key, value  in method.items()
        )
        for method in workflow
    )

def is_token_collocates(collocates: Collocates) -> TypeGuard[Collocates[Token]]:
    """
    Checks if the input collocates tuple consists exclusively of Token instances and excludes Bigram and POSTaggedWord types.

    :param collocates: The collocates tuple to check.
    :type collocates: Collocates

    :return: True if all elements in `collocates` are Token instances and not Bigram or POSTaggedWord, otherwise False.
    :rtype: bool
    """

    return isinstance(collocates, tuple) and not isinstance(collocates, Bigram) and not isinstance(collocates, POSTaggedWord) and all(
        isinstance(token, Token)
        for token in collocates
    )