"""
This module provides function decorators that adapt the input types of processing functions to improve flexibility and composability across workflows.

Specifically, it includes:

* `accepts_sentences_and_collocates`: Allows a function to seamlessly handle both individual token sequences and lists of such sequences (e.g., sentences or collocate groups).
* `accepts_tags`: Allows functions designed for plain tokens to accept and return POS-tagged inputs (POSTaggedWord), preserving tag alignment.

These adaptors make it easier to integrate diverse data types into a unified processing pipeline without requiring duplication of logic.
"""

from functools import wraps
import inspect
from inspect import BoundArguments
from .typeguards import is_sentence, is_collocates, is_pos_tags

from typing import TypeVar, Any, Callable, Sized, Iterable, cast
from ..lib_types import Token, Sentences, POSTaggedWordList, POSTaggedWord

T = TypeVar("T", bound=Sized)

def accepts_sentences_and_collocates(method: Callable[..., T]) -> Callable[..., list[T] | T]:
    """
    Decorator that allows a function to accept either a single input (e.g., a list of tokens or collocates) or a list of such inputs (e.g., sentences or collocate groups). If a list of inputs is passed, the 
    function is applied to each element in the list, and a list of results is returned.

    If the input is not a list of sentences or collocates, the function is applied normally.

    :param method: The function to wrap.
    :type method: Callable[..., T]

    :return: A wrapped function that handles both single and batched inputs.
    :rtype: Callable[..., list[T] | T]
    """

    @wraps(method)
    def wrapper(*args: Any, **kwargs: Any) -> list[T] | T:
        signature = inspect.signature(method)
        bound_args: BoundArguments = signature.bind(*args, **kwargs)
        bound_args.apply_defaults()

        tokens = next(iter(bound_args.arguments.values()), None)

        if is_sentence(tokens) or is_collocates(tokens):
            processed_sentences = [method(sentence, **kwargs) for sentence in tokens]

            return [sentence for sentence in processed_sentences if sentence]
        else: 
            return method(tokens, **kwargs)
    return wrapper


def accepts_tags(method: Callable[..., T]) -> Callable[..., POSTaggedWordList | T]:
    """
    Decorator that allows a function designed to operate on plain tokens to also handle POS-tagged word inputs (i.e., sequences of POSTaggedWord). 

    The function will automatically extract the token part, apply the method, and then re-attach the POS tags to the result. If the number of returned tokens does not match the original length, the POS tags are inferred from a lowercase mapping of the original words.

    :param method: The function to wrap.
    :type method: Callable[..., T]

    :return: A wrapped function that processes POS-tagged input and returns a POSTaggedWordList.
    :rtype: Callable[..., POSTaggedWordList | T]
    """

    @wraps(method)
    def wrapper(*args: Any, **kwargs: Any) -> POSTaggedWordList | T:
        signature = inspect.signature(method)
        bound_args = signature.bind(*args, **kwargs)
        bound_args.apply_defaults()

        tokens = next(iter(bound_args.arguments.values()), None)

        if is_pos_tags(tokens):
            words, pos = zip(*tokens)

            result = method(list(words), **kwargs) 

            if len(result) == len(tokens):
                return [POSTaggedWord(word, pos_tag) for word, pos_tag in zip(cast(Iterable, result), pos)]
            else:
                original_pos_map = dict(zip([word.text.lower() if isinstance(word, Token) else word.lower() for word in words], pos))

                print(words, pos, original_pos_map)
                result_with_pos = [POSTaggedWord(word, original_pos_map[word.text.lower() if isinstance(word, Token) else word.lower()]) for word in cast(Iterable, result)]

                return result_with_pos
        else:
            return method(tokens, **kwargs)

    return wrapper
