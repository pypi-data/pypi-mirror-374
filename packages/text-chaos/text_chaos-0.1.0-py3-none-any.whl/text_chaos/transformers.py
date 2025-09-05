"""
Text transformation functions for the text-chaos library.

This module contains all the individual transformation functions
that can be applied to text strings.
"""

import random
import re
from typing import Callable, Dict, List


def leet_transform(text: str) -> str:
    """
    Transform text to leet speak (1337 speak).

    Args:
        text: The input text to transform

    Returns:
        The text converted to leet speak

    Example:
        >>> leet_transform("Hello World")
        "H3110 W0r1d"
    """
    leet_map: Dict[str, str] = {
        "a": "4",
        "A": "4",
        "e": "3",
        "E": "3",
        "i": "1",
        "I": "1",
        "o": "0",
        "O": "0",
        "s": "5",
        "S": "5",
        "t": "7",
        "T": "7",
        "l": "1",
        "L": "1",
        "g": "9",
        "G": "9",
    }

    result = ""
    for char in text:
        result += leet_map.get(char, char)

    return result


def uwu_transform(text: str) -> str:
    """
    Transform text to uwu speak.

    Args:
        text: The input text to transform

    Returns:
        The text converted to uwu speak

    Example:
        >>> uwu_transform("Hello World")
        "Hewwo Wowwd uwu"
    """
    # Replace r and l with w
    text = re.sub(r"[rl]", "w", text)
    text = re.sub(r"[RL]", "W", text)

    # Replace some consonants
    text = re.sub(r"n([aeiou])", r"ny\1", text)
    text = re.sub(r"N([aeiou])", r"Ny\1", text)

    # Add uwu expressions
    uwu_expressions = [" uwu", " owo", " >w<", " ^w^"]
    if text and not any(expr in text for expr in uwu_expressions):
        text += random.choice(uwu_expressions)

    return text


def reverse_transform(text: str) -> str:
    """
    Reverse the input text.

    Args:
        text: The input text to transform

    Returns:
        The reversed text

    Example:
        >>> reverse_transform("Hello World")
        "dlroW olleH"
    """
    return text[::-1]


def zalgo_transform(text: str) -> str:
    """
    Add zalgo-style diacritical marks to text.

    Args:
        text: The input text to transform

    Returns:
        The text with zalgo effects

    Example:
        >>> zalgo_transform("Hello")
        "Ḧ̴̰e̵͎̾l̶̤̿l̴̰̈o̵͎̾"
    """
    # Zalgo combining characters (subset for safety)
    zalgo_chars = [
        "\u0300",
        "\u0301",
        "\u0302",
        "\u0303",
        "\u0304",
        "\u0305",
        "\u0307",
        "\u0308",
        "\u0309",
        "\u030a",
        "\u030b",
        "\u030c",
        "\u0316",
        "\u0317",
        "\u0318",
        "\u0319",
        "\u031a",
        "\u031b",
        "\u031c",
        "\u031d",
        "\u031e",
        "\u031f",
        "\u0320",
        "\u0321",
    ]

    result = ""
    for char in text:
        result += char
        if char.isalpha():  # Only add zalgo to letters
            # Add 1-3 random zalgo characters
            num_marks = random.randint(1, 3)
            for _ in range(num_marks):
                result += random.choice(zalgo_chars)

    return result


def mock_transform(text: str) -> str:
    """
    Transform text to mocking SpongeBob case (alternating caps).

    Args:
        text: The input text to transform

    Returns:
        The text in alternating caps

    Example:
        >>> mock_transform("Hello World")
        "hElLo WoRlD"
    """
    result = ""
    upper = False

    for char in text:
        if char.isalpha():
            result += char.upper() if upper else char.lower()
            upper = not upper
        else:
            result += char

    return result


# Registry of all available transformers
TRANSFORMERS: Dict[str, Callable[[str], str]] = {
    "leet": leet_transform,
    "uwu": uwu_transform,
    "reverse": reverse_transform,
    "zalgo": zalgo_transform,
    "mock": mock_transform,
}


def get_available_modes() -> List[str]:
    """
    Get a list of all available transformation modes.

    Returns:
        List of available transformation mode names
    """
    return list(TRANSFORMERS.keys())


def apply_transform(text: str, mode: str) -> str:
    """
    Apply a specific transformation to the given text.

    Args:
        text: The input text to transform
        mode: The transformation mode to apply

    Returns:
        The transformed text

    Raises:
        ValueError: If the specified mode is not available
    """
    if mode not in TRANSFORMERS:
        available_modes = ", ".join(get_available_modes())
        raise ValueError(
            f"Unknown transformation mode '{mode}'. Available modes: {available_modes}"
        )

    return TRANSFORMERS[mode](text)
