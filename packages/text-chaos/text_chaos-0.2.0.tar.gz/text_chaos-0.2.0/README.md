# text-chaos 🎭

[![PyPI version](https://badge.fury.io/py/text-chaos.svg)](https://badge.fury.io/py/text-chaos)
[![Python](https://img.shields.io/pypi/pyversions/text-chaos.svg)](https://pypi.python.org/pypi/text-chaos)
[![Tests](https://github.com/yourusername/text-chaos/workflows/Tests/badge.svg)](https://github.com/yourusername/text-chaos/actions)

A fun Python library for playful string manipulations! Transform your text with various chaotic and amusing effects like leet speak, uwu-ification, zalgo corruption, and more.

## ✨ Features

- 🔥 **Simple API**: One function call to rule them all
- 🎯 **Multiple transformations**: leet, uwu, reverse, zalgo, mock, and more
- 📦 **Extensible**: Easy to add custom transformations
- 🔍 **Type hints**: Full typing support for better IDE experience  
- 🧪 **Well tested**: Comprehensive test suite with pytest
- 🚀 **Fast**: Lightweight with no external dependencies

## 🚀 Installation

```bash
pip install text-chaos
```

## 📖 Quick Start

```python
import text_chaos

# Basic usage - defaults to leet speak
text_chaos.transform("Hello World!")
# Output: "H3110 W0r1d!"

# Try different transformation modes
text_chaos.transform("Hello World!", mode="uwu")
# Output: "Hewwo Wowwd! uwu"

text_chaos.transform("Hello World!", mode="reverse") 
# Output: "!dlroW olleH"

text_chaos.transform("Hello World!", mode="mock")
# Output: "hElLo WoRlD!"

# Transform multiple strings at once
text_chaos.batch_transform(["Hello", "World"], mode="leet")
# Output: ["H3110", "W0r1d"]

# See all available transformation modes
text_chaos.get_modes()
# Output: ['leet', 'uwu', 'reverse', 'zalgo', 'mock']
```

## 🎨 Available Transformations

| Mode | Description | Example |
|------|-------------|---------|
| `leet` | Convert to leet speak (1337) | `Hello` → `H3110` |
| `uwu` | UwU-ify text with cute speak | `Hello World` → `Hewwo Wowwd uwu` |
| `reverse` | Reverse the text | `Hello` → `olleH` |
| `zalgo` | Add zalgo/corruption effects | `Hello` → `H̴̰ë́l̶l̴̰ö̵` |
| `mock` | aLtErNaTiNg CaPs (mocking SpongeBob) | `Hello World` → `hElLo WoRlD` |

## 🔧 API Reference

### `transform(text: str, mode: str = "leet") -> str`

Transform a single string using the specified mode.

**Parameters:**
- `text` (str): The input text to transform
- `mode` (str, optional): The transformation mode. Defaults to "leet"

**Returns:**
- str: The transformed text

**Raises:**
- `ValueError`: If the specified mode is not available
- `TypeError`: If text is not a string

### `batch_transform(texts: List[str], mode: str = "leet") -> List[str]`

Transform multiple strings using the specified mode.

**Parameters:**
- `texts` (List[str]): List of input texts to transform
- `mode` (str, optional): The transformation mode. Defaults to "leet"

**Returns:**
- List[str]: List of transformed texts

### `get_modes() -> List[str]`

Get a list of all available transformation modes.

**Returns:**
- List[str]: Available transformation mode names

## 🛠️ Development

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/text-chaos.git
cd text-chaos

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=text_chaos --cov-report=html

# Run specific test file
pytest tests/test_text_chaos.py -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports  
isort src/ tests/

# Type checking
mypy src/

# Run all quality checks
black src/ tests/ && isort src/ tests/ && mypy src/ && pytest
```

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Add new transformations**: Create new functions in `src/text_chaos/transformers.py`
2. **Improve existing transformations**: Make them funnier, more accurate, or more efficient
3. **Fix bugs**: Check the issues tab for known problems
4. **Add tests**: Help us maintain high code coverage
5. **Improve documentation**: Better examples, clearer explanations

### Adding a New Transformation

1. Add your transformation function to `src/text_chaos/transformers.py`:

```python
def my_transform(text: str) -> str:
    \"\"\"
    Description of your transformation.
    
    Args:
        text: The input text to transform
        
    Returns:
        The transformed text
    \"\"\"
    # Your transformation logic here
    return transformed_text
```

2. Register it in the `TRANSFORMERS` dictionary:

```python
TRANSFORMERS = {
    # ... existing transformers
    "my_mode": my_transform,
}
```

3. Add tests in `tests/test_text_chaos.py`

4. Update this README with the new transformation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎉 Fun Examples

```python
import text_chaos

# Create some chaos!
text = "Python is awesome"

print("Original:", text)
print("Leet:", text_chaos.transform(text, "leet"))
print("UwU:", text_chaos.transform(text, "uwu"))  
print("Reverse:", text_chaos.transform(text, "reverse"))
print("Mock:", text_chaos.transform(text, "mock"))
print("Zalgo:", text_chaos.transform(text, "zalgo"))

# Chain transformations manually
chaotic_text = text_chaos.transform(text, "leet")
chaotic_text = text_chaos.transform(chaotic_text, "reverse")
print("Leet + Reverse:", chaotic_text)
```

## 🌟 Star History

If you found this library useful, please consider giving it a star on GitHub! ⭐

---

Made with ❤️ and a bit of chaos 🎭
