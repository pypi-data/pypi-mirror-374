# Example Usage of the txttoqti Package

This document provides comprehensive examples of how to use the `txttoqti` package for converting text-based question banks into QTI packages compatible with Canvas LMS and other learning management systems.

## Basic Usage

### Simple Conversion

To get started with the `txttoqti` package, you can use the following example:

```python
from txttoqti import TxtToQtiConverter

# Create an instance of the converter
converter = TxtToQtiConverter()

# Convert a text file containing questions to a QTI package
qti_file = converter.convert_file("examples/sample_questions.txt")

print(f"QTI package created: {qti_file}")
```

### Using the Convenience Function

For quick conversions, use the module-level convenience function:

```python
from txttoqti import convert_txt_to_qti

# Convert directly with minimal code
qti_file = convert_txt_to_qti("examples/sample_questions.txt")
print(f"QTI package created: {qti_file}")

# With custom output path
qti_file = convert_txt_to_qti(
    "examples/sample_questions.txt", 
    "custom_quiz.zip"
)
```

## Command-Line Interface Examples

### Basic CLI Usage

```bash
# Using the txttoqti command
txttoqti -i examples/sample_questions.txt -o output_package.zip

# Using module form
python -m txttoqti.cli -i questions.txt -o my_quiz.zip

# Let the system auto-generate output filename
txttoqti -i questions.txt
```

### Educational CLI Usage

```bash
# Zero-configuration conversion with auto-detection
txttoqti-edu

# Check current status
txttoqti-edu --status

# Force regeneration
txttoqti-edu --force

# Interactive troubleshooting mode
txttoqti-edu --interactive

# Verbose output
txttoqti-edu --verbose

# Custom working directory
txttoqti-edu --path /path/to/course/materials
```

## Advanced Conversion Examples

### Using SmartConverter with Change Detection

```python
from txttoqti import SmartConverter

# Create an instance of the smart converter
smart_converter = SmartConverter()

# Convert a text file with change detection
# Will only regenerate if the source file has changed
qti_file = smart_converter.convert_file("examples/sample_questions.txt")

print(f"Smart QTI package created: {qti_file}")

# Force conversion even if no changes detected
qti_file = smart_converter.convert_file(
    "examples/sample_questions.txt",
    force_update=True
)
```

## Question Parsing and Validation Examples

### Parsing Questions

```python
from txttoqti import QuestionParser

# Create a parser instance
parser = QuestionParser()

# Parse questions from a text file
questions = parser.parse("examples/sample_questions.txt")

# Iterate through parsed questions
for question in questions:
    print(f"Question {question.number}: {question.text}")
    print(f"Type: {question.question_type}")
    print(f"Options: {len(question.choices)}")
    print(f"Correct answer: {question.correct_answer}")
    print("-" * 40)
```

### Validating Questions

```python
from txttoqti import QuestionValidator, QuestionParser

# Parse questions first
parser = QuestionParser()
questions = parser.parse("examples/sample_questions.txt")

# Create validator instance
validator = QuestionValidator()

# Validate each question
all_valid = True
for question in questions:
    is_valid, errors = validator.validate(question)
    if not is_valid:
        all_valid = False
        print(f"Question {question.number} has errors:")
        for error in errors:
            print(f"  - {error}")

if all_valid:
    print("All questions are valid!")
else:
    print("Some questions need to be fixed.")
```

### File-level Validation

```python
from txttoqti import QuestionValidator
from txttoqti.parser import QuestionParser

# Validate an entire file
def validate_question_file(filepath):
    try:
        parser = QuestionParser()
        questions = parser.parse(filepath)
        
        validator = QuestionValidator()
        total_questions = len(questions)
        valid_questions = 0
        
        for question in questions:
            is_valid, errors = validator.validate(question)
            if is_valid:
                valid_questions += 1
            else:
                print(f"Question {question.number}: {', '.join(errors)}")
        
        print(f"Validation complete: {valid_questions}/{total_questions} questions are valid")
        return valid_questions == total_questions
        
    except Exception as e:
        print(f"Error validating file: {e}")
        return False

# Usage
is_valid = validate_question_file("examples/sample_questions.txt")
```

## Educational Extension Examples

### Using the Educational QTI Converter

```python
from txttoqti.educational import QtiConverter
from pathlib import Path

# Initialize with auto-detection
converter = QtiConverter()

# Convert with status reporting
success = converter.convert()

if success:
    print("Conversion completed successfully!")
else:
    print("Conversion failed. Check the logs.")

# Show detailed status
converter.show_status()
```

### Custom Educational Workflow

```python
from txttoqti.educational import QtiConverter
from pathlib import Path

# Custom working directory
converter = QtiConverter(script_path=Path("/path/to/course"))

# Get file information
file_info = converter.get_file_info()
print(f"Block number: {file_info.get('block_num')}")
print(f"Input file: {file_info.get('input_file')}")
print(f"Output file: {file_info.get('output_file')}")

# Force conversion
success = converter.convert(force=True)
```

## Error Handling Examples

### Basic Error Handling

```python
from txttoqti import TxtToQtiConverter, TxtToQtiError

converter = TxtToQtiConverter()

try:
    qti_file = converter.convert_file("nonexistent_file.txt")
    print(f"Success: {qti_file}")
except TxtToQtiError as e:
    print(f"Conversion error: {e}")
except FileNotFoundError:
    print("Input file not found")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Comprehensive Error Handling

```python
from txttoqti import (
    TxtToQtiConverter, 
    ParseError, 
    ValidationError, 
    ConversionError,
    FileError
)

def safe_convert(input_file, output_file=None):
    try:
        converter = TxtToQtiConverter()
        return converter.convert_file(input_file, output_file)
        
    except FileError as e:
        print(f"File access error: {e}")
    except ParseError as e:
        print(f"Question parsing error: {e}")
    except ValidationError as e:
        print(f"Question validation error: {e}")
    except ConversionError as e:
        print(f"QTI conversion error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    return None

# Usage
result = safe_convert("questions.txt", "my_quiz.zip")
if result:
    print(f"Successfully created: {result}")
else:
    print("Conversion failed")
```

## Batch Processing Examples

### Convert Multiple Files

```python
from txttoqti import TxtToQtiConverter
from pathlib import Path

converter = TxtToQtiConverter()
input_dir = Path("question_banks")
output_dir = Path("qti_packages")

# Ensure output directory exists
output_dir.mkdir(exist_ok=True)

# Process all .txt files
for txt_file in input_dir.glob("*.txt"):
    output_file = output_dir / f"{txt_file.stem}.zip"
    
    try:
        result = converter.convert_file(str(txt_file), str(output_file))
        print(f"✅ Converted: {txt_file.name} → {result}")
    except Exception as e:
        print(f"❌ Failed: {txt_file.name} - {e}")
```

### Automated Course Processing

```python
from txttoqti.educational import QtiConverter
from pathlib import Path
import sys

def process_course_blocks(course_dir):
    """Process all blocks in a course directory."""
    course_path = Path(course_dir)
    
    if not course_path.exists():
        print(f"Course directory not found: {course_dir}")
        return False
    
    # Find all block directories
    block_dirs = [d for d in course_path.iterdir() 
                  if d.is_dir() and ('bloque' in d.name or 'block' in d.name)]
    
    if not block_dirs:
        print("No block directories found")
        return False
    
    success_count = 0
    for block_dir in sorted(block_dirs):
        print(f"\nProcessing: {block_dir.name}")
        
        converter = QtiConverter(script_path=block_dir)
        if converter.convert():
            success_count += 1
            print(f"✅ {block_dir.name} completed")
        else:
            print(f"❌ {block_dir.name} failed")
    
    print(f"\nProcessed {success_count}/{len(block_dirs)} blocks successfully")
    return success_count == len(block_dirs)

# Usage
if __name__ == "__main__":
    course_directory = sys.argv[1] if len(sys.argv) > 1 else "."
    success = process_course_blocks(course_directory)
    sys.exit(0 if success else 1)
```

## Integration Examples

### Web Application Integration

```python
from flask import Flask, request, send_file, jsonify
from txttoqti import convert_txt_to_qti
import tempfile
import os

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_questions():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as tmp:
            file.save(tmp.name)
            
            # Convert to QTI
            qti_file = convert_txt_to_qti(tmp.name)
            
            # Clean up temporary file
            os.unlink(tmp.name)
            
            # Send QTI file as download
            return send_file(qti_file, as_attachment=True)
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

These examples demonstrate the flexibility and power of the `txttoqti` package for various use cases, from simple conversions to complex educational workflows. For more detailed information, please refer to the [API documentation](api.md) and [CLI documentation](cli.md).