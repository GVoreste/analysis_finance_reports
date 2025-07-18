"""Utilities of general interest common to all formats and that can be used
for creating `pdf_filter` or `text_extract` or `deserialize` functions
"""

from typing import Callable, TypeVar, ParamSpec


def normalize_string(string: str, lower: bool = True) -> str:
    """Normalize a string by:
    1. Stripping leading/trailing whitespace
    2. Converting to lowercase if `lower`
    3. Collapsing multiple whitespaces into single spaces

    Parameters
    ----------
    string : str
        Input string to normalize
    lower : bool
        Determine if the string has to be lowered

    Returns
    -------
    str
        Normalized string
    """
    string = string.strip()
    if lower:
        string = string.lower()
    string = " ".join(string.split())
    return string


def normalize_word(word: str, lower: bool = False) -> str:
    """Normalize a word by:
    1. Stripping leading/trailing whitespace
    2. Removing all whitespace between characters
    3. Converting to lowercase if `lower`

    Parameters
    ----------
    word : str
        Input word to normalize
    lower : bool
        Determine if the string has to be lowered

    Returns
    -------
    str
        Normalized word with no whitespace
    """
    word = word.strip()
    word = "".join(word.split())
    if lower:
        word = word.lower()
    return word


P = ParamSpec("P")
R = TypeVar("R")


def default_if_not_implemented(default_func: Callable[P, R]) -> Callable[P, R]:
    """Replace the decorated function with a default given as argument of the decorator
    if the decorated function raise a `NotImplementedError` or return `None`

    Parameters
    ----------
    default_func : Callable[P,R]
        default function

    Returns
    -------
    Callable[P,R]
        the default function if the deorated function is overwritten, if not the decorated function
    """

    def wrapper(primary_func):
        def func(*args, **kwargs):
            try:
                result = primary_func(*args, **kwargs)
                if result is not None:
                    return result
            except NotImplementedError:
                pass
            return default_func(*args, **kwargs)

        return func

    return wrapper


def overwrite_if_implemented(primary_func: Callable[P, R]) -> Callable[P, R]:
    """Replace the decorated default function with a function given as argument of the decorator
    if that function do not raise a `NotImplementedError` or return `None`

    Parameters
    ----------
    primary_func : Callable[P,R]
        implementation of a function

    Returns
    -------
    Callable[P,R]
        the function given as argument of the decorator if implemented,
        otherwise the decorated default
    """

    def wrapper(default_func):
        def func(*args, **kwargs):
            try:
                result = primary_func(*args, **kwargs)
                if result is not None:
                    return result
            except NotImplementedError:
                pass
            return default_func(*args, **kwargs)

        return func

    return wrapper
