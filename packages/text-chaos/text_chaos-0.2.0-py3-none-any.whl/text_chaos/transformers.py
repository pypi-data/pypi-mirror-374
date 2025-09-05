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


def pirate_transform(text: str) -> str:
    """
    Transform text to pirate speak.

    Args:
        text: The input text to transform

    Returns:
        The text converted to pirate speak

    Example:
        >>> pirate_transform("Hello friend, how are you?")
        "Ahoy matey, how be ye? Arr!"
    """
    # Pirate word replacements
    pirate_replacements = {
        # Greetings
        r"\bhello\b": "ahoy",
        r"\bhi\b": "ahoy",
        r"\bhey\b": "ahoy",
        # People
        r"\bfriend\b": "matey",
        r"\bfriends\b": "mateys",
        r"\bman\b": "lad",
        r"\bwoman\b": "lass",
        r"\bpeople\b": "crew",
        r"\bguys\b": "mateys",
        # Pronouns and verbs
        r"\byou\b": "ye",
        r"\byour\b": "yer",
        r"\byou\'re\b": "ye be",
        r"\bare\b": "be",
        r"\bmy\b": "me",
        r"\bover\b": "o'er",
        r"\bfor\b": "fer",
        r"\bto\b": "ter",
        # Common words
        r"\bmoney\b": "doubloons",
        r"\bgold\b": "treasure",
        r"\bstop\b": "avast",
        r"\byes\b": "aye",
        r"\byeah\b": "aye",
        r"\bno\b": "nay",
        r"\bokay\b": "aye aye",
        r"\bok\b": "aye",
        r"\bdrink\b": "grog",
        r"\bfight\b": "battle",
        # Places
        r"\bhouse\b": "cabin",
        r"\bhome\b": "ship",
        r"\bbathroom\b": "head",
        r"\bkitchen\b": "galley",
        r"\bfloor\b": "deck",
        # Fun additions
        r"\bawesome\b": "shipshape",
        r"\bgreat\b": "grand",
        r"\bgood\b": "fine",
        r"\bbad\b": "cursed",
        r"\bterrible\b": "scurvy",
    }

    # Convert to lowercase for pattern matching, but preserve original case
    result = text

    # Apply pirate replacements
    for pattern, replacement in pirate_replacements.items():
        # Use case-insensitive matching
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    # Add pirate exclamations
    pirate_exclamations = [
        "Arr!",
        "Avast!",
        "Shiver me timbers!",
        "Batten down the hatches!",
        "Yo ho ho!",
    ]

    # Add an exclamation at the end if the text doesn't already end with punctuation
    if result and result[-1] not in ".!?":
        result += ", " + random.choice(pirate_exclamations)
    elif (
        result and random.random() < 0.3
    ):  # 30% chance to add exclamation even with punctuation
        result += " " + random.choice(pirate_exclamations)

    return result


def emojify_transform(text: str) -> str:
    """
    Replace words with corresponding emojis.

    Args:
        text: The input text to transform

    Returns:
        The text with words replaced by emojis

    Example:
        >>> emojify_transform("I love pizza")
        "I ❤️ 🍕"
    """
    emoji_map = {
        # Emotions
        r"\blove\b": "❤️",
        r"\bheart\b": "❤️",
        r"\bhappy\b": "😊",
        r"\bsad\b": "😢",
        r"\bangry\b": "😠",
        r"\bsmile\b": "😊",
        r"\bcry\b": "😢",
        r"\blaugh\b": "😂",
        # Food
        r"\bpizza\b": "🍕",
        r"\bburger\b": "🍔",
        r"\bcoffee\b": "☕",
        r"\bbeer\b": "🍺",
        r"\bwine\b": "🍷",
        r"\bcake\b": "🎂",
        r"\bapple\b": "🍎",
        r"\bbanana\b": "🍌",
        r"\btaco\b": "🌮",
        r"\bsushi\b": "🍣",
        r"\bbread\b": "🍞",
        r"\bchocolate\b": "🍫",
        # Animals
        r"\bdog\b": "🐶",
        r"\bcat\b": "🐱",
        r"\bbird\b": "🐦",
        r"\bfish\b": "🐟",
        r"\bcow\b": "🐄",
        r"\bpig\b": "🐷",
        r"\bmonkey\b": "🐵",
        r"\bhorse\b": "🐴",
        # Nature
        r"\bsun\b": "☀️",
        r"\bmoon\b": "🌙",
        r"\bstar\b": "⭐",
        r"\btree\b": "🌳",
        r"\bflower\b": "🌸",
        r"\bfire\b": "🔥",
        r"\bwater\b": "💧",
        r"\bsnow\b": "❄️",
        # Objects
        r"\bcar\b": "🚗",
        r"\bhouse\b": "🏠",
        r"\bphone\b": "📱",
        r"\bcomputer\b": "💻",
        r"\bbook\b": "📚",
        r"\bmusic\b": "🎵",
        r"\bgame\b": "🎮",
        r"\bball\b": "⚽",
        # Actions
        r"\brun\b": "🏃",
        r"\bwalk\b": "🚶",
        r"\bdance\b": "💃",
        r"\bsleep\b": "😴",
        r"\bwork\b": "💼",
        r"\btravel\b": "✈️",
        r"\bshopping\b": "🛒",
        r"\bcooking\b": "👨‍🍳",
    }

    result = text
    for pattern, emoji in emoji_map.items():
        result = re.sub(pattern, emoji, result, flags=re.IGNORECASE)

    return result


def yoda_transform(text: str) -> str:
    """
    Transform text to Yoda-style speech patterns.

    Args:
        text: The input text to transform

    Returns:
        The text rearranged in Yoda's speech pattern

    Example:
        >>> yoda_transform("I love coding")
        "Coding, I love"
    """
    # Simple Yoda patterns - move verb/object to front
    yoda_patterns = [
        # "I [verb] [object]" -> "[object], I [verb]"
        (r"\bi\s+(love|like|hate|want|need|have)\s+(\w+)", r"\2, I \1"),
        # "You are [adjective]" -> "[adjective], you are"
        (r"\byou\s+are\s+(\w+)", r"\1, you are"),
        # "It is [adjective]" -> "[adjective], it is"
        (r"\bit\s+is\s+(\w+)", r"\1, it is"),
        # "I am [adjective]" -> "[adjective], I am"
        (r"\bi\s+am\s+(\w+)", r"\1, I am"),
        # "We should [verb]" -> "[verb], we should"
        (r"\bwe\s+should\s+(\w+)", r"\1, we should"),
        # "I will [verb]" -> "[verb], I will"
        (r"\bi\s+will\s+(\w+)", r"\1, I will"),
    ]

    result = text
    for pattern, replacement in yoda_patterns:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    # Add some Yoda-isms
    yoda_additions = [
        (r"\byes\b", "mmm, yes"),
        (r"\bno\b", "mmm, no"),
        (r"\bokay\b", "mmm, okay"),
    ]

    for pattern, replacement in yoda_additions:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    return result


def drunk_transform(text: str) -> str:
    """
    Add typos and missing letters to simulate drunk typing.

    Args:
        text: The input text to transform

    Returns:
        The text with drunk-style typos

    Example:
        >>> drunk_transform("hello there")
        "helo tehre"
    """
    result = ""
    i = 0

    while i < len(text):
        char = text[i]

        if char.isalpha():
            # 20% chance to introduce a typo
            if random.random() < 0.2:
                typo_type = random.choice(["skip", "swap", "double", "wrong"])

                if typo_type == "skip":
                    # Skip this character (missing letter)
                    pass
                elif typo_type == "swap" and i < len(text) - 1:
                    # Swap with next character
                    if text[i + 1].isalpha():
                        result += text[i + 1] + char
                        i += 1  # Skip next char since we used it
                    else:
                        result += char
                elif typo_type == "double":
                    # Double the character
                    result += char + char
                elif typo_type == "wrong":
                    # Replace with nearby keyboard key
                    keyboard_neighbors = {
                        "a": "s",
                        "b": "v",
                        "c": "x",
                        "d": "s",
                        "e": "r",
                        "f": "d",
                        "g": "f",
                        "h": "g",
                        "i": "u",
                        "j": "h",
                        "k": "j",
                        "l": "k",
                        "m": "n",
                        "n": "b",
                        "o": "i",
                        "p": "o",
                        "q": "w",
                        "r": "e",
                        "s": "a",
                        "t": "r",
                        "u": "y",
                        "v": "c",
                        "w": "q",
                        "x": "z",
                        "y": "t",
                        "z": "x",
                    }
                    wrong_char = keyboard_neighbors.get(char.lower(), char)
                    if char.isupper():
                        wrong_char = wrong_char.upper()
                    result += wrong_char
                else:
                    result += char
            else:
                result += char
        else:
            result += char

        i += 1

    return result


def shakespeare_transform(text: str) -> str:
    """
    Transform text to Shakespearean English.

    Args:
        text: The input text to transform

    Returns:
        The text in Shakespearean style

    Example:
        >>> shakespeare_transform("you are great")
        "thou art magnificent"
    """
    shakespeare_replacements = {
        # Pronouns
        r"\byou\b": "thou",
        r"\byour\b": "thy",
        r"\byou\'re\b": "thou art",
        r"\byours\b": "thine",
        # Verbs
        r"\bare\b": "art",
        r"\bdo\b": "dost",
        r"\bdoes\b": "doth",
        r"\bhave\b": "hast",
        r"\bhas\b": "hath",
        r"\bwill\b": "shall",
        r"\bcan\b": "canst",
        # Common words
        r"\bbefore\b": "ere",
        r"\bbetween\b": "betwixt",
        r"\bhere\b": "hither",
        r"\bthere\b": "thither",
        r"\bwhere\b": "whither",
        r"\bmust\b": "must needs",
        # Adjectives
        r"\bgreat\b": "magnificent",
        r"\bgood\b": "fair",
        r"\bbad\b": "ill",
        r"\bbeautiful\b": "beauteous",
        r"\bstrange\b": "passing strange",
        r"\bsmart\b": "wise",
        r"\bfunny\b": "mirthful",
        r"\bquick\b": "swift",
        # Expressions
        r"\byes\b": "aye",
        r"\bno\b": "nay",
        r"\bokay\b": "verily",
        r"\bhello\b": "hail",
        r"\bgoodbye\b": "farewell",
        r"\bmaybe\b": "mayhap",
    }

    result = text
    for pattern, replacement in shakespeare_replacements.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    return result


def piglatin_transform(text: str) -> str:
    """
    Transform text to Pig Latin.

    Args:
        text: The input text to transform

    Returns:
        The text converted to Pig Latin

    Example:
        >>> piglatin_transform("hello world")
        "ello-hay orld-way"
    """

    def pig_latin_word(word: str) -> str:
        if not word.isalpha():
            return word

        vowels = "aeiouAEIOU"

        # If word starts with vowel, add "way"
        if word[0] in vowels:
            return word + "way"

        # Find first vowel
        first_vowel = -1
        for i, char in enumerate(word):
            if char in vowels:
                first_vowel = i
                break

        if first_vowel == -1:  # No vowels found
            return word + "ay"

        # Move consonants to end and add "ay"
        consonants = word[:first_vowel]
        rest = word[first_vowel:]

        return rest + consonants + "ay"

    words = re.findall(r"\b\w+\b|\W+", text)
    result = ""

    for word_match in words:
        if re.match(r"\w+", word_match):
            # Preserve case
            if word_match.isupper():
                pig_word = pig_latin_word(word_match.lower()).upper()
            elif word_match[0].isupper():
                pig_word = pig_latin_word(word_match.lower())
                pig_word = pig_word[0].upper() + pig_word[1:]
            else:
                pig_word = pig_latin_word(word_match)
            result += pig_word
        else:
            result += word_match

    return result


def morse_transform(text: str) -> str:
    """
    Transform text to Morse code.

    Args:
        text: The input text to transform

    Returns:
        The text converted to Morse code

    Example:
        >>> morse_transform("hello")
        ".... . .-.. .-.. ---"
    """
    morse_code = {
        "A": ".-",
        "B": "-...",
        "C": "-.-.",
        "D": "-..",
        "E": ".",
        "F": "..-.",
        "G": "--.",
        "H": "....",
        "I": "..",
        "J": ".---",
        "K": "-.-",
        "L": ".-..",
        "M": "--",
        "N": "-.",
        "O": "---",
        "P": ".--.",
        "Q": "--.-",
        "R": ".-.",
        "S": "...",
        "T": "-",
        "U": "..-",
        "V": "...-",
        "W": ".--",
        "X": "-..-",
        "Y": "-.--",
        "Z": "--..",
        "0": "-----",
        "1": ".----",
        "2": "..---",
        "3": "...--",
        "4": "....-",
        "5": ".....",
        "6": "-....",
        "7": "--...",
        "8": "---..",
        "9": "----.",
        " ": "/",
    }

    result = []
    for char in text.upper():
        if char in morse_code:
            result.append(morse_code[char])
        elif char == " ":
            result.append("/")

    return " ".join(result)


def roman_transform(text: str) -> str:
    """
    Transform numbers to Roman numerals.

    Args:
        text: The input text to transform

    Returns:
        The text with numbers converted to Roman numerals

    Example:
        >>> roman_transform("the year 2025")
        "the year MMXXV"
    """

    def to_roman(num: int) -> str:
        if num <= 0 or num > 3999:
            return str(num)  # Return original if out of range

        values = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
        numerals = [
            "M",
            "CM",
            "D",
            "CD",
            "C",
            "XC",
            "L",
            "XL",
            "X",
            "IX",
            "V",
            "IV",
            "I",
        ]

        result = ""
        for i, value in enumerate(values):
            count = num // value
            if count:
                result += numerals[i] * count
                num -= value * count
        return result

    # Find all numbers in the text
    def replace_number(match) -> str:
        num = int(match.group())
        return to_roman(num)

    return re.sub(r"\b\d+\b", replace_number, text)


# Registry of all available transformers
TRANSFORMERS: Dict[str, Callable[[str], str]] = {
    "leet": leet_transform,
    "uwu": uwu_transform,
    "reverse": reverse_transform,
    "zalgo": zalgo_transform,
    "mock": mock_transform,
    "pirate": pirate_transform,
    "emojify": emojify_transform,
    "yoda": yoda_transform,
    "drunk": drunk_transform,
    "shakespeare": shakespeare_transform,
    "piglatin": piglatin_transform,
    "morse": morse_transform,
    "roman": roman_transform,
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
