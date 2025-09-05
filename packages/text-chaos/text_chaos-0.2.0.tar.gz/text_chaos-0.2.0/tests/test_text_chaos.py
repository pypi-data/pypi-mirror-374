"""
Tests for the text-chaos library.
"""

import pytest

from text_chaos import batch_transform, get_modes, transform
from text_chaos.transformers import (
    apply_transform,
    drunk_transform,
    emojify_transform,
    get_available_modes,
    leet_transform,
    mock_transform,
    morse_transform,
    piglatin_transform,
    pirate_transform,
    reverse_transform,
    roman_transform,
    shakespeare_transform,
    uwu_transform,
    yoda_transform,
    zalgo_transform,
)


class TestTransformers:
    """Test individual transformer functions."""

    def test_leet_transform(self):
        """Test leet speak transformation."""
        assert leet_transform("hello") == "h3110"
        assert leet_transform("HELLO") == "H3110"
        assert leet_transform("test") == "7357"
        assert leet_transform("") == ""
        assert leet_transform("123") == "123"  # Numbers unchanged

    def test_uwu_transform(self):
        """Test uwu transformation."""
        result = uwu_transform("hello world")
        assert "w" in result  # r/l should be replaced with w
        assert any(expr in result for expr in [" uwu", " owo", " >w<", " ^w^"])

        assert "w" in uwu_transform("really")
        assert "ny" in uwu_transform("anime")

    def test_reverse_transform(self):
        """Test text reversal."""
        assert reverse_transform("hello") == "olleh"
        assert reverse_transform("") == ""
        assert reverse_transform("a") == "a"
        assert reverse_transform("Hello World") == "dlroW olleH"

    def test_zalgo_transform(self):
        """Test zalgo transformation."""
        original = "hello"
        result = zalgo_transform(original)

        # Should be longer due to combining characters
        assert len(result) > len(original)

        # Should contain original characters
        # Note: This is a simplified test since zalgo adds combining chars
        assert "h" in result
        assert "e" in result

    def test_mock_transform(self):
        """Test mocking SpongeBob case transformation."""
        result = mock_transform("hello world")

        # Should have mixed case
        assert result != "hello world"
        assert result != "HELLO WORLD"

        # Test specific pattern
        assert mock_transform("abcd") == "aBcD"
        assert mock_transform("") == ""

    def test_pirate_transform(self):
        """Test pirate speak transformation."""
        result = pirate_transform("hello friend")

        # Should contain pirate replacements
        assert "ahoy" in result.lower()
        assert "matey" in result.lower()

        # Should add pirate exclamations
        pirate_exclamations = [
            "arr!",
            "avast!",
            "shiver me timbers!",
            "batten down the hatches!",
            "yo ho ho!",
        ]
        assert any(excl.lower() in result.lower() for excl in pirate_exclamations)

        # Test specific replacements
        assert (
            pirate_transform("you are my friend") != "you are my friend"
        )  # Should be transformed
        result2 = pirate_transform("yes I have money")
        assert "aye" in result2.lower()
        assert "doubloons" in result2.lower()

        # Test empty string
        assert pirate_transform("") == ""

    def test_emojify_transform(self):
        """Test emoji transformation."""
        result = emojify_transform("I love pizza")
        assert "❤️" in result
        assert "🍕" in result

        result2 = emojify_transform("happy dog")
        assert "😊" in result2 or "🐶" in result2

        # Test that non-matching words remain unchanged
        assert emojify_transform("xyz") == "xyz"
        assert emojify_transform("") == ""

    def test_yoda_transform(self):
        """Test Yoda speech transformation."""
        result = yoda_transform("I love coding")
        assert "coding" in result.lower()
        assert "love" in result.lower()

        result2 = yoda_transform("you are great")
        assert "great" in result2.lower()

        # Test yoda-isms
        result3 = yoda_transform("yes")
        assert "mmm" in result3.lower()

        assert yoda_transform("") == ""

    def test_drunk_transform(self):
        """Test drunk typing transformation."""
        # Since drunk transform is random, test multiple times
        original = "hello there friend"
        results = [drunk_transform(original) for _ in range(10)]

        # At least some results should be different from original
        changed = sum(1 for result in results if result != original)
        assert changed > 0  # Should have some changes

        # Test empty string
        assert drunk_transform("") == ""

        # Test non-alphabetic characters remain unchanged
        result = drunk_transform("123!@#")
        assert "123" in result and "!@#" in result

    def test_shakespeare_transform(self):
        """Test Shakespearean transformation."""
        result = shakespeare_transform("you are great")
        assert "thou" in result.lower()
        assert "art" in result.lower()
        assert "magnificent" in result.lower()

        result2 = shakespeare_transform("yes")
        assert "aye" in result2.lower()

        result3 = shakespeare_transform("hello")
        assert "hail" in result3.lower()

        assert shakespeare_transform("") == ""

    def test_piglatin_transform(self):
        """Test Pig Latin transformation."""
        # Words starting with consonants
        assert "ello" in piglatin_transform("hello").lower()
        assert "ay" in piglatin_transform("hello").lower()

        # Words starting with vowels
        result = piglatin_transform("apple")
        assert "way" in result.lower()

        # Test case preservation
        result2 = piglatin_transform("Hello")
        assert result2[0].isupper()  # First letter should be uppercase

        assert piglatin_transform("") == ""

    def test_morse_transform(self):
        """Test Morse code transformation."""
        result = morse_transform("hello")

        # Should contain morse code patterns
        assert "." in result or "-" in result
        assert " " in result  # Spaces between morse letters

        # Test specific letter
        result2 = morse_transform("a")
        assert ".-" in result2

        # Test space handling
        result3 = morse_transform("a b")
        assert "/" in result3  # Spaces become /

        assert morse_transform("") == ""

    def test_roman_transform(self):
        """Test Roman numeral transformation."""
        result = roman_transform("the year 2025")
        assert "MMXXV" in result

        result2 = roman_transform("I have 5 cats")
        assert "V" in result2

        result3 = roman_transform("born in 1990")
        assert "MCMXC" in result3

        # Test edge cases
        assert roman_transform("no numbers here") == "no numbers here"
        assert roman_transform("") == ""

        # Test out of range numbers (should remain unchanged)
        result4 = roman_transform("the year 5000")
        assert "5000" in result4  # Should not be converted


class TestMainAPI:
    """Test the main API functions."""

    def test_transform_basic(self):
        """Test basic transform functionality."""
        result = transform("hello", "leet")
        assert result == "h3110"

        result = transform("hello", "reverse")
        assert result == "olleh"

    def test_transform_default_mode(self):
        """Test transform with default mode."""
        result = transform("hello")  # Should default to leet
        assert result == "h3110"

    def test_transform_invalid_mode(self):
        """Test transform with invalid mode."""
        with pytest.raises(ValueError, match="Unknown transformation mode"):
            transform("hello", "invalid_mode")

    def test_transform_type_validation(self):
        """Test transform input type validation."""
        with pytest.raises(TypeError, match="Expected str"):
            transform(123, "leet")

        with pytest.raises(TypeError, match="Expected str"):
            transform(None, "leet")

    def test_batch_transform(self):
        """Test batch transformation."""
        texts = ["hello", "world"]
        results = batch_transform(texts, "leet")

        assert len(results) == 2
        assert results[0] == "h3110"
        assert results[1] == "w0r1d"

    def test_batch_transform_empty_list(self):
        """Test batch transform with empty list."""
        result = batch_transform([], "leet")
        assert result == []

    def test_batch_transform_type_validation(self):
        """Test batch transform input validation."""
        with pytest.raises(TypeError, match="Expected list"):
            batch_transform("not a list", "leet")

        with pytest.raises(TypeError, match="Expected str at index"):
            batch_transform(["hello", 123], "leet")

    def test_get_modes(self):
        """Test getting available modes."""
        modes = get_modes()

        assert isinstance(modes, list)
        assert len(modes) > 0
        assert "leet" in modes
        assert "uwu" in modes
        assert "reverse" in modes
        assert "pirate" in modes
        assert "emojify" in modes
        assert "yoda" in modes
        assert "drunk" in modes
        assert "shakespeare" in modes
        assert "piglatin" in modes
        assert "morse" in modes
        assert "roman" in modes


class TestTransformerRegistry:
    """Test the transformer registry system."""

    def test_get_available_modes(self):
        """Test getting available transformation modes."""
        modes = get_available_modes()

        expected_modes = [
            "leet",
            "uwu",
            "reverse",
            "zalgo",
            "mock",
            "pirate",
            "emojify",
            "yoda",
            "drunk",
            "shakespeare",
            "piglatin",
            "morse",
            "roman",
        ]
        for mode in expected_modes:
            assert mode in modes

    def test_apply_transform(self):
        """Test applying transformations through the registry."""
        result = apply_transform("hello", "leet")
        assert result == "h3110"

        result = apply_transform("hello", "reverse")
        assert result == "olleh"

    def test_apply_transform_invalid_mode(self):
        """Test apply_transform with invalid mode."""
        with pytest.raises(ValueError, match="Unknown transformation mode"):
            apply_transform("hello", "nonexistent")


class TestIntegration:
    """Integration tests for the complete library."""

    def test_all_modes_work(self):
        """Test that all registered modes work without errors."""
        test_text = "Hello World"

        for mode in get_modes():
            result = transform(test_text, mode)
            assert isinstance(result, str)
            # Each transformation should change the text somehow
            # (except potentially edge cases)

    def test_chaining_not_directly_supported(self):
        """Test that we can manually chain transformations."""
        text = "hello world"

        # Apply leet first, then reverse
        leet_result = transform(text, "leet")
        final_result = transform(leet_result, "reverse")

        assert final_result != text
        assert final_result != leet_result

    def test_empty_string_handling(self):
        """Test that all transformations handle empty strings gracefully."""
        for mode in get_modes():
            result = transform("", mode)
            assert isinstance(result, str)
            # Most transformations should return empty string for empty input
            # (uwu might add expressions, so we just check it's a string)

    @pytest.mark.parametrize("mode", ["leet", "reverse", "mock"])
    def test_deterministic_modes(self, mode):
        """Test that some modes are deterministic."""
        text = "hello world"

        result1 = transform(text, mode)
        result2 = transform(text, mode)

        assert result1 == result2

    def test_unicode_handling(self):
        """Test handling of unicode characters."""
        unicode_text = "héllo wörld 🌍"

        # Should not crash on unicode input
        for mode in ["leet", "reverse"]:
            result = transform(unicode_text, mode)
            assert isinstance(result, str)
