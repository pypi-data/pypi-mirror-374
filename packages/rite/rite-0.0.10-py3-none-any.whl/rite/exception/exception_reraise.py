# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Reraise Utility Function
========================

This function allows re-raising exceptions while preserving their traceback.
Useful for exception handling when working with custom error propagation.

"""


# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

# Import | Standard Library
from types import TracebackType
from typing import List, Optional, Type, TypeVar

# Import | Libraries

# Import | Local Modules


# =============================================================================
# Type Definitions
# =============================================================================

# Type variable for exceptions
E = TypeVar("E", bound=BaseException)


# =============================================================================
# Functions
# =============================================================================


def reraise(
    tp: Type[E],
    value: Optional[E] = None,
    tb: Optional[TracebackType] = None,
) -> None:
    """
    Re-raises an exception of the given type, optionally with a specific
    value and traceback.

    Args:
        tp (Type[E]): The exception type to be raised.
        value (Optional[E]): The exception instance (if not provided, a new
            instance of `tp` is created).
        tb (Optional[TracebackType]): The traceback to be attached to the
            exception.

    Raises:
        The specified exception type with the provided traceback (if any).

    Example:
        try:
            1 / 0
        except ZeroDivisionError as e:
            reraise(ZeroDivisionError, e, e.__traceback__)
    """
    if value is None:
        value = tp()

    if value.__traceback__ is not tb:
        raise value.with_traceback(tb)

    raise value


# def reraise(tp, value, tb=None):
#     """ """
#     if value is None:
#         value = tp()
#     if value.__traceback__ is not tb:
#         raise value.with_traceback(tb)
#     raise value

# =============================================================================
# Exports
# =============================================================================

__all__: List[str] = [
    "reraise",
]
