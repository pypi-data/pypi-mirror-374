# txttoqti

txttoqti is a universal converter that transforms text-based question banks into QTI (Question & Test Interoperability) packages compatible with Canvas LMS and other learning management systems. This package is designed to simplify the process of creating QTI packages from plain text files, making it easier for educators and developers to manage and distribute assessments.

## Features

- **Universal Format Support**: Convert plain text question banks to QTI packages
- **Canvas LMS Compatibility**: Full compatibility with Canvas LMS and other QTI-compliant systems
- **Smart Conversion**: Change detection and incremental updates with `SmartConverter`
- **Educational Workflow**: Zero-configuration auto-detection for educational environments
- **Comprehensive Validation**: Built-in question format validation and error reporting
- **Multiple Interfaces**: Command-line tools, Python API, and educational CLI
- **No Dependencies**: Uses only Python standard library (Python 3.10+)

## Quick Start

### Installation

Install from PyPI:
```bash
pip install txttoqti
```

Or install from source:
```bash
git clone https://github.com/julihocc/txttoqti.git
cd txttoqti
pip install .
```

### Basic Usage

**New Intuitive Python API (Recommended):**
```python
import txttoqti

# Create converter object
converter = txttoqti.TxtToQti()

# Load questions from file
converter.read_txt("questions.txt")

# Save to QTI package  
converter.save_to_qti("quiz.zip")

# Or chain methods together
converter.read_txt("questions.txt").save_to_qti("quiz.zip")
```

**Quick One-Line Conversion:**
```python
import txttoqti
txttoqti.quick_convert("questions.txt", "quiz.zip")
```

**Command Line:**
```bash
# Basic CLI
txttoqti -i questions.txt -o quiz.zip

# Educational CLI with auto-detection
txttoqti-edu
```

### Question Format

Questions should follow this format:

```
Q1: What is the result of type(42) in Python?
A) <class 'float'>
B) <class 'int'>
C) <class 'str'>
D) <class 'number'>
ANSWER: B
```

## Documentation

| Document | Description |
|----------|-------------|
| [Installation Guide](docs/installation.md) | Detailed installation instructions and setup |
| [API Reference](docs/api.md) | Complete API documentation with all classes and methods |
| [CLI Documentation](docs/cli.md) | Command-line interface usage and options |
| [Question Format](docs/question-format.md) | Supported question formats and validation rules |
| [Examples](docs/examples.md) | Comprehensive usage examples and integration patterns |

## Supported Question Types

- **Multiple Choice**: Standard A/B/C/D format with single correct answer
- **True/False**: Binary choice questions
- **Short Answer**: Text input questions
- **Essay**: Long-form text responses

## Command-Line Tools

### Basic CLI (`txttoqti`)
Simple, direct conversion tool:
```bash
txttoqti -i input.txt -o output.zip
```

### Educational CLI (`txttoqti-edu`)
Enhanced tool with auto-detection and interactive features:
```bash
txttoqti-edu --interactive  # Interactive troubleshooting
txttoqti-edu --status      # Show current status
txttoqti-edu --force       # Force regeneration
```

## Advanced Features

### Working with Multiple Files
```python
import txttoqti
from pathlib import Path

converter = txttoqti.TxtToQti()

# Process multiple files
for txt_file in Path("questions").glob("*.txt"):
    output_name = txt_file.stem + ".zip"
    converter.read_txt(txt_file).save_to_qti(output_name).clear()
```

### Validation and Preview
```python
import txttoqti

converter = txttoqti.TxtToQti()
converter.read_txt("questions.txt")

# Check what was loaded
print(f"Loaded {len(converter)} questions")
print(converter.preview())

# Validate before saving
if converter.validate():
    converter.save_to_qti("validated_quiz.zip")
```

### Working with Strings
```python
import txttoqti

# Load questions from a string (useful for dynamic content)
questions_text = """
Q1: What is Python?
A) A snake
B) A programming language
C) A tool
D) A framework
ANSWER: B
"""

converter = txttoqti.TxtToQti()
converter.read_string(questions_text)
converter.save_to_qti("string_quiz.zip")
```

### Legacy Interfaces (Still Supported)

#### Smart Conversion
```python
from txttoqti import SmartConverter

converter = SmartConverter()
# Only converts if source file has changed
qti_file = converter.convert_file("questions.txt")
```

#### Educational Workflows
```python
from txttoqti.educational import QtiConverter

converter = QtiConverter()  # Auto-detects course structure
success = converter.convert()
```

#### Original API
```python
from txttoqti import TxtToQtiConverter

converter = TxtToQtiConverter()
qti_file = converter.convert_file("questions.txt")
```

## Requirements

- Python 3.10 or higher
- No external dependencies (uses only standard library)

## Contributing

Contributions are welcome! Please feel free to:

- Submit bug reports and feature requests via [GitHub Issues](https://github.com/julihocc/txttoqti/issues)
- Submit pull requests for improvements
- Improve documentation
- Add support for additional question formats

### Development Setup

```bash
git clone https://github.com/julihocc/txttoqti.git
cd txttoqti
pip install -e ".[dev]"
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: Comprehensive guides in the `docs/` directory
- **Examples**: See `examples/` directory for sample question files
- **Issues**: Report bugs on [GitHub Issues](https://github.com/julihocc/txttoqti/issues)
- **Interactive Help**: Use `txttoqti-edu --interactive` for troubleshooting

## Related Projects

- [QTI Specification](https://www.imsglobal.org/question/) - Official QTI standards
- [Canvas LMS](https://www.instructure.com/canvas) - Learning management system