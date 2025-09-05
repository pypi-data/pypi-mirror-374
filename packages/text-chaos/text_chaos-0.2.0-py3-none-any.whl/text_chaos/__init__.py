"""
text-chaos: A fun library for playful string manipulations.

This library provides various text transformations including leet speak,
uwu speak, zalgo text, and more!
"""

from typing import List, Union

from .transformers import TRANSFORMERS, apply_transform, get_available_modes

# Version
__version__ = "0.2.0"

# Public API
__all__ = ["transform", "get_available_modes", "batch_transform", "__version__"]


def transform(text: str, mode: str = "leet") -> str:
    """
    Transform text using the specified mode.

    This is the main entry point for the text-chaos library.

    Args:
        text: The input text to transform
        mode: The transformation mode to apply. Available modes can be
              retrieved using get_available_modes()

    Returns:
        The transformed text

    Raises:
        ValueError: If the specified mode is not available
        TypeError: If text is not a string

    Example:
        >>> import text_chaos
        >>> text_chaos.transform("Hello World", "leet")
        'H3110 W0r1d'
        >>> text_chaos.transform("Hello World", "uwu")
        'Hewwo Wowwd uwu'
        >>> text_chaos.transform("Hello World", "reverse")
        'dlroW olleH'
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text).__name__}")

    return apply_transform(text, mode)


def batch_transform(texts: List[str], mode: str = "leet") -> List[str]:
    """
    Transform multiple texts using the specified mode.

    Args:
        texts: List of input texts to transform
        mode: The transformation mode to apply

    Returns:
        List of transformed texts

    Raises:
        ValueError: If the specified mode is not available
        TypeError: If texts is not a list or contains non-strings

    Example:
        >>> import text_chaos
        >>> text_chaos.batch_transform(["Hello", "World"], "leet")
        ['H3110', 'W0r1d']
    """
    if not isinstance(texts, list):
        raise TypeError(f"Expected list, got {type(texts).__name__}")

    result = []
    for i, text in enumerate(texts):
        if not isinstance(text, str):
            raise TypeError(f"Expected str at index {i}, got {type(text).__name__}")
        result.append(transform(text, mode))

    return result


def get_modes() -> List[str]:
    """
    Get a list of all available transformation modes.

    Returns:
        List of available transformation mode names

    Example:
        >>> import text_chaos
        >>> text_chaos.get_modes()
        ['leet', 'uwu', 'reverse', 'zalgo', 'mock']
    """
    return get_available_modes()
