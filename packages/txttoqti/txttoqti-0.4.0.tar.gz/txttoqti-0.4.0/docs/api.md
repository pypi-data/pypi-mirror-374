# API Documentation for txttoqti

## Overview

The `txttoqti` package provides a comprehensive API for converting text-based question banks into QTI (Question & Test Interoperability) packages compatible with Canvas LMS and other learning management systems. This document outlines all classes, methods, data models, and usage patterns.

## Core Classes

### TxtToQtiConverter

The `TxtToQtiConverter` class is the primary interface for converting text files to QTI packages.

```python
from txttoqti import TxtToQtiConverter
```

#### Constructor

```python
TxtToQtiConverter()
```

Creates a new converter instance with default settings.

#### Methods

##### `convert_file(txt_file, output_file=None, **kwargs)`

Converts a specified text file into a QTI package.

**Parameters:**
- `txt_file` (str): Path to the input text file
- `output_file` (str, optional): Path for the output QTI ZIP file. If not provided, generates filename automatically
- `**kwargs`: Additional conversion options

**Returns:**
- `str`: Path to the created QTI ZIP file

**Raises:**
- `FileError`: When input file cannot be read
- `ParseError`: When question format is invalid  
- `ValidationError`: When questions fail validation
- `ConversionError`: When QTI generation fails

**Example:**
```python
converter = TxtToQtiConverter()
qti_file = converter.convert_file("questions.txt", "quiz.zip")
```

### SmartConverter

The `SmartConverter` class provides intelligent conversion with change detection and caching.

```python
from txttoqti import SmartConverter
```

#### Constructor

```python
SmartConverter(cache_dir=None)
```

**Parameters:**
- `cache_dir` (str, optional): Directory for storing conversion cache

#### Methods

##### `convert_file(txt_file, output_file=None, force_update=False, **kwargs)`

Converts a text file with change detection optimization.

**Parameters:**
- `txt_file` (str): Path to input text file
- `output_file` (str, optional): Path for output QTI ZIP file
- `force_update` (bool): Force conversion even if no changes detected
- `**kwargs`: Additional conversion options

**Returns:**
- `str`: Path to the created QTI ZIP file

### QuestionParser

The `QuestionParser` class handles parsing of text-based question formats.

```python
from txttoqti import QuestionParser
```

#### Methods

##### `parse(txt_file)`

Parses a text file and extracts questions.

**Parameters:**
- `txt_file` (str): Path to the input text file

**Returns:**
- `List[Question]`: List of parsed question objects

**Raises:**
- `ParseError`: When file format is invalid or unreadable

**Example:**
```python
parser = QuestionParser()
questions = parser.parse("questions.txt")
for question in questions:
    print(f"Q{question.number}: {question.text}")
```

##### `parse_string(content)`

Parses questions from a string.

**Parameters:**
- `content` (str): Question text content

**Returns:**
- `List[Question]`: List of parsed question objects

### QTIGenerator

The `QTIGenerator` class creates QTI-compliant XML and ZIP packages.

```python
from txttoqti import QTIGenerator
```

#### Methods

##### `generate(questions, assessment_title="Quiz", **kwargs)`

Generates a complete QTI package from questions.

**Parameters:**
- `questions` (List[Question]): List of question objects
- `assessment_title` (str): Title for the assessment
- `**kwargs`: Additional QTI generation options

**Returns:**
- `str`: Path to the generated QTI ZIP file

##### `generate_xml(questions, **kwargs)`

Generates QTI XML content from questions.

**Parameters:**
- `questions` (List[Question]): List of question objects
- `**kwargs`: XML generation options

**Returns:**
- `str`: QTI-compliant XML string

### QuestionValidator

The `QuestionValidator` class validates question structure and content.

```python
from txttoqti import QuestionValidator
```

#### Methods

##### `validate(question)`

Validates a single question object.

**Parameters:**
- `question` (Question): Question object to validate

**Returns:**
- `Tuple[bool, List[str]]`: (is_valid, list_of_errors)

**Example:**
```python
validator = QuestionValidator()
is_valid, errors = validator.validate(question)
if not is_valid:
    print("Validation errors:", errors)
```

##### `validate_all(questions)`

Validates a list of questions.

**Parameters:**
- `questions` (List[Question]): List of questions to validate

**Returns:**
- `Tuple[bool, Dict[int, List[str]]]`: (all_valid, {question_number: errors})

## Data Models

### Question

Represents a single question with all its properties.

#### Attributes

- `number` (int): Question number
- `text` (str): Question text
- `question_type` (QuestionType): Type of question
- `choices` (List[Choice]): Available answer choices
- `correct_answer` (str): Identifier of correct answer
- `points` (float): Point value (default: 1.0)
- `feedback` (str, optional): General feedback

#### Methods

##### `is_multiple_choice()`
Returns `True` if question is multiple choice.

##### `is_true_false()`
Returns `True` if question is true/false type.

##### `is_short_answer()`
Returns `True` if question requires text input.

### Choice

Represents an answer choice for multiple choice questions.

#### Attributes

- `identifier` (str): Choice identifier (A, B, C, D, etc.)
- `text` (str): Choice text content
- `correct` (bool): Whether this choice is correct

### Assessment

Represents a complete assessment/quiz.

#### Attributes

- `title` (str): Assessment title
- `questions` (List[Question]): List of questions
- `time_limit` (int, optional): Time limit in minutes
- `attempts_allowed` (int): Number of attempts allowed

### QuestionType

Enumeration of supported question types.

#### Values

- `QuestionType.MULTIPLE_CHOICE`
- `QuestionType.TRUE_FALSE`
- `QuestionType.SHORT_ANSWER`
- `QuestionType.ESSAY`

## Educational Extension

### QtiConverter (Educational)

Enhanced converter for educational workflows with auto-detection.

```python
from txttoqti.educational import QtiConverter
```

#### Constructor

```python
QtiConverter(script_path=None)
```

**Parameters:**
- `script_path` (Path, optional): Working directory path

#### Methods

##### `convert(force=False)`

Performs auto-detected conversion.

**Parameters:**
- `force` (bool): Force conversion even if no changes

**Returns:**
- `bool`: Success status

##### `show_status()`

Displays current conversion status information.

##### `get_file_info()`

Returns dictionary with file detection information.

**Returns:**
- `Dict`: File information including block number, input/output files

## Exceptions

### TxtToQtiError

Base exception class for all txttoqti errors.

```python
from txttoqti import TxtToQtiError
```

### ParseError

Raised when question parsing fails.

```python
from txttoqti import ParseError
```

### ValidationError

Raised when question validation fails.

```python
from txttoqti import ValidationError
```

### ConversionError

Raised when QTI conversion fails.

```python
from txttoqti import ConversionError
```

### FileError

Raised when file operations fail.

```python
from txttoqti import FileError
```

## Utility Functions

### `convert_txt_to_qti(txt_file, output_file=None, **kwargs)`

Convenience function for quick conversions.

**Parameters:**
- `txt_file` (str): Input text file path
- `output_file` (str, optional): Output QTI file path
- `**kwargs`: Additional conversion options

**Returns:**
- `str`: Path to created QTI file

**Example:**
```python
from txttoqti import convert_txt_to_qti

qti_file = convert_txt_to_qti("questions.txt")
print(f"Created: {qti_file}")
```

### Utility Module Functions

```python
from txttoqti import clean_text, validate_file, get_file_timestamp
```

##### `clean_text(text)`
Cleans and normalizes text content.

##### `validate_file(filepath)`  
Validates file accessibility and format.

##### `get_file_timestamp(filepath)`
Gets file modification timestamp.

## Configuration and Options

### Conversion Options

Common `**kwargs` options for conversion methods:

- `encoding` (str): File encoding (default: 'utf-8')
- `assessment_title` (str): Title for generated assessment
- `points_per_question` (float): Default points per question
- `shuffle_answers` (bool): Whether to shuffle answer choices
- `show_correct_answers` (bool): Whether to show correct answers in feedback

### Example with Options

```python
converter = TxtToQtiConverter()
qti_file = converter.convert_file(
    "questions.txt",
    assessment_title="Final Exam",
    points_per_question=2.0,
    shuffle_answers=True,
    show_correct_answers=False
)
```

## Error Handling Best Practices

```python
from txttoqti import (
    TxtToQtiConverter, 
    ParseError, 
    ValidationError, 
    ConversionError,
    FileError
)

def safe_convert(input_file):
    try:
        converter = TxtToQtiConverter()
        return converter.convert_file(input_file)
    except FileError as e:
        print(f"File error: {e}")
    except ParseError as e:
        print(f"Parse error: {e}")
    except ValidationError as e:
        print(f"Validation error: {e}")
    except ConversionError as e:
        print(f"Conversion error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return None
```

## Version Information

```python
import txttoqti
print(txttoqti.__version__)  # Package version
print(txttoqti.__author__)   # Author information
print(txttoqti.__license__)  # License information
```

For practical usage examples, see the [examples documentation](examples.md). For command-line usage, refer to the [CLI documentation](cli.md).