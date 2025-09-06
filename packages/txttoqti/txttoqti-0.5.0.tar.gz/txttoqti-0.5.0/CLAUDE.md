# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

txttoqti is a Python package that converts text-based question banks into QTI (Question & Test Interoperability) packages compatible with Canvas LMS. The project uses only Python standard library dependencies and follows a modular architecture with dual interfaces: a basic converter and an enhanced educational extension.

## Commands

### Development and Testing
- `python -m pytest` - Run all unit tests with coverage (configured in pyproject.toml)
- `python -m pytest --cov=src/txttoqti --cov-report=term-missing --cov-report=html` - Run tests with detailed coverage
- `python -m pytest tests/` - Run specific test directory
- `make test` - Run tests with coverage via Makefile
- `make test-fast` - Run tests without coverage
- `python scripts/dev.py test` - Alternative test runner

### Code Quality and Formatting
- `make lint` - Run flake8 and mypy linting
- `make format` - Format code with black
- `python -m black src tests scripts` - Format specific directories
- `python -m flake8 src tests` - Run flake8 linting
- `python -m mypy src` - Run type checking

### Package Management
- `pip install -e ".[dev]"` - Install in development mode with dev dependencies
- `make install-dev` - Install development dependencies
- `make build` - Build package for distribution
- `make clean` - Clean build artifacts and cache files

### CLI Usage
- `txttoqti -i questions.txt -o output.zip` - Basic conversion (installed package)
- `txttoqti-edu` - Educational CLI with auto-detection
- `python -m txttoqti.cli -i questions.txt -o output.zip` - Module execution
- `python -m txttoqti.educational.cli` - Educational module execution

### Publishing (Development)
- `./scripts/publish.sh test` - Publish to TestPyPI
- `./scripts/publish.sh prod` - Publish to production PyPI

## Architecture

The codebase follows a layered architecture with clear separation between core conversion logic and educational workflows.

### Core Components (src/txttoqti/)
- **converter.py**: Main `TxtToQtiConverter` orchestrates the entire conversion pipeline
- **parser.py**: `QuestionParser` handles text parsing and question extraction with validation
- **qti_generator.py**: `QTIGenerator` creates QTI-compliant XML structures and ZIP packages
- **validator.py**: `QuestionValidator` provides comprehensive question format validation
- **smart_converter.py**: `SmartConverter` adds change detection and incremental updates
- **models.py**: Data models (`Question`, `Choice`, `Assessment`) with `QuestionType` enum
- **cli.py**: Basic command-line interface with argparse

### Educational Extension (src/txttoqti/educational/)
The educational package provides a higher-level interface designed for academic workflows:
- **converter.py**: `QtiConverter` with auto-detection and zero-configuration setup
- **detector.py**: `BlockDetector` automatically identifies course structure and file patterns
- **formats.py**: `FormatConverter` handles educational format conversions (Q1:/A)/B)/ANSWER:)
- **utils.py**: `FileManager` provides batch processing and file management utilities
- **cli.py**: Enhanced CLI with interactive features and progress reporting

### Supporting Infrastructure
- **exceptions.py**: Hierarchical exception system (TxtToQtiError, ParseError, ValidationError, ConversionError, FileError)
- **utils.py**: Core utilities (clean_text, validate_file, get_file_timestamp)
- **logging_config.py**: Centralized logging configuration
- **__init__.py**: Package exports with educational extension auto-import

### Entry Points and Interfaces
The package provides multiple interfaces:
1. **New Intuitive API** (recommended): `TxtToQti` class with `.read_txt()` and `.save_to_qti()` methods
2. **Quick Conversion**: `quick_convert()` function for one-line usage
3. **Legacy API**: Original `TxtToQtiConverter` (still supported)
4. **Basic CLI** (`txttoqti`): Direct file conversion with explicit input/output paths
5. **Educational CLI** (`txttoqti-edu`): Auto-detecting interface for academic environments
6. **Module execution**: `python -m txttoqti.cli` and `python -m txttoqti.educational.cli`

#### New Intuitive Interface Usage
```python
import txttoqti

# Create converter object
converter = txttoqti.TxtToQti()

# Load questions from file
converter.read_txt("questions.txt")

# Or load from string
converter.read_string(question_text)

# Save to QTI package
converter.save_to_qti("quiz.zip")

# Additional methods
print(f"Loaded {len(converter)} questions")
print(converter.preview())
converter.validate()
converter.clear()

# Method chaining support
converter.read_txt("questions.txt").save_to_qti("output.zip")

# Quick conversion
txttoqti.quick_convert("questions.txt", "quiz.zip")
```

### Question Format Support
- **Standard Format**: Q1:/A)/B)/RESPUESTA: pattern with numbered questions and lettered choices
- **Multiple Choice**: A/B/C/D format with single correct answer identification
- **Educational Formats**: Auto-detection of common academic question patterns
- **Validation**: Comprehensive format checking with detailed error reporting

### Testing Architecture
- **tests/test_core.py**: Unit tests for core converter functionality
- **tests/test_integration.py**: End-to-end integration tests
- **tests/test_txttoqti_interface.py**: Tests for the new TxtToQti interface
- **tests/test_e2e.py**: End-to-end scenario tests
- **tests/test_fix.py**: Regression and bug fix verification tests
- **tests/educational/**: Specialized tests for educational extension
- **Coverage**: Configured for src/txttoqti with HTML and terminal reporting
- **Pytest configuration**: Centralized in pyproject.toml with strict markers and verbose output
- **Organization**: All test files are properly contained within the tests/ directory

### Build and Distribution
- **pyproject.toml**: Modern Python packaging with optional dependencies (dev, test)
- **Scripts**: `txttoqti` and `txttoqti-edu` entry points for installed package
- **Makefile**: Development workflow commands
- **Publishing**: Secure token-based publishing to PyPI via scripts/publish.sh