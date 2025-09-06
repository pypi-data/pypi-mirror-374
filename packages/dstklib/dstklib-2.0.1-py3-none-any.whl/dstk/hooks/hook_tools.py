"""
Module providing the Hook class for wrapping callable methods with a strict single-argument interface.

The Hook class allows encapsulating any callable that accepts exactly one argument, enforcing this constraint at runtime. It supports invocation, argument validation, and renaming of the hook instance.

This module is useful for building extensible and modular modela where hooks act as customizable processing steps.
"""

from __future__ import annotations
from typing import Any, Callable
from inspect import signature, Signature, Parameter
from copy import deepcopy
from collections.abc import ValuesView

class Hook:
    """
    Represents a callable hook that wraps a single-argument function.

    A Hook encapsulates a method that must accept exactly one argument, enabling
    modular processing steps or callbacks within workflows or pipelines.

    :param name: A descriptive name for the hook.
    :type name: str
    :param method: A callable that takes exactly one argument and performs some operation
    :type method: Callable[[Any], Any]

    Usage:
    
    .. code-block:: python

        CustomHook = Hook("example_hook", some_function)
        result = CustomHook(data)  # Calls some_function(data)
    """

    def __init__(self, name: str, method: Callable[[Any], Any]):
        """
        Initializes WorkflowBuilder with given attributes.
        """

        self.name: str = name
        self.method: Callable = method

    def __call__(self, *args, **kwargs) -> Any:
        """
        Invokes the wrapped method with the provided arguments.

        Ensures that the wrapped method accepts exactly one argument before calling it. Raises a ValueError if the method signature does not conform to this requirement.

        :param args: Positional arguments to pass to the wrapped method.
        :param kwargs: Keyword arguments to pass to the wrapped method.

        :return: The result of calling the wrapped method with the given arguments.
        :rtype: Any

        :raises ValueError: If the wrapped method does not accept exactly one argument.
        """
        if not self._check_args():
            raise ValueError("A hook must accept exactly one argument")

        return self.method(*args, **kwargs)

    def _check_args(self) -> bool:
        """
        Checks whether the wrapped method accepts exactly one argument (positional or keyword).

        :return: True if the method accepts exactly one argument, False otherwise.
        :rtype: bool
        """
        sig: Signature = signature(self.method)
        params: ValuesView[Parameter] = sig.parameters.values()

        normalized_params: list[Parameter] = [param for param in params if param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD, param.KEYWORD_ONLY)]

        return True if len(normalized_params) == 1 else False

    def rename(self, new_name: str) -> Hook:
        """
        Creates a new Hook instance with the same method but a different name.

        :param new_name: The new name for the hook.
        :type new_name: str

        :return: A new Hook instance with the updated name.
        :rtype: Hook
        """
        new_instance: Hook = deepcopy(self)
        new_instance.name = new_name

        return new_instance