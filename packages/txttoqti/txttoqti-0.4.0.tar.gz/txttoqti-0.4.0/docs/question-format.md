# Question Format Specification

This document describes the supported question format for the `txttoqti` package. The converter uses a single, standardized format to ensure consistency and ease of maintenance.

## Supported Question Types

### 1. Multiple Choice Questions

The txttoqti package uses a single, standardized format:

```
Q1: What is the result of type(42) in Python?
A) <class 'float'>
B) <class 'int'>
C) <class 'str'>
D) <class 'number'>
ANSWER: B
```

### 2. True/False Questions

```
Q2: Python is a compiled language.
A) True
B) False
ANSWER: B
```

### 3. Mixed Questions Example

```
Q3: What is the capital of France?
A) London
B) Berlin
C) Paris
D) Madrid
ANSWER: C

Q4: The Pacific Ocean is the largest ocean on Earth.
A) True
B) False
ANSWER: A
```

## Format Rules and Guidelines

### Question Numbering

Questions must start with `Q` followed by a number and colon: `Q1:`, `Q2:`, etc. Questions should be numbered sequentially starting from 1.

### Answer Options

#### Multiple Choice Options

- Use capital letters with parentheses: `A)`, `B)`, `C)`, `D)`
- Each option should be on a separate line
- Options should start immediately after the question line

#### Correct Answer Indication

- Use `ANSWER: [LETTER]` (e.g., `ANSWER: B`)
- The correct answer indicator should be on its own line after all options
- Use uppercase letters to match the format used in options

### Text Formatting

#### Encoding
- Use UTF-8 encoding for all text files
- Support for international characters (accents, special symbols, etc.)

#### Line Breaks
- Each question should be separated by at least one blank line
- Options should immediately follow the question text
- The correct answer should immediately follow the options

#### Whitespace
- No special indentation required
- No trailing whitespace on lines

## Advanced Features

### Question with Code Blocks

```
Q4: What does the following code print? print("Hello" + "World")
A) Hello World
B) HelloWorld
C) Hello+World
D) Error
ANSWER: B
```

### Questions with Special Characters

```
Q6: What is the correct way to create a dictionary in Python?
A) dict = []
B) dict = {}
C) dict = ()
D) dict = ""
ANSWER: B
```

### Questions with Mathematical Expressions

```
Q9: Which operator is used for exponentiation in Python?
A) ^
B) **
C) *
D) exp()
ANSWER: B
```

## File Structure Requirements

### File Naming
- Recommended: `questions.txt`, `sample_questions.txt`
- Block format: `questions-block-[NUMBER].txt` or `questions-module-[NUMBER].txt`

### File Organization
- One question bank per file
- Questions should be ordered sequentially
- Include a header comment describing the content (optional)

### Example File Header
```
# Sample Questions for txttoqti Converter
# Course: Introduction to Python Programming
# Block: 1 - Data Types and Variables

Q1: What is the result of type(42) in Python?
A) <class 'float'>
B) <class 'int'>
C) <class 'str'>
D) <class 'number'>
ANSWER: B
```

## Validation and Error Handling

### Common Format Errors

1. **Missing question number**: Questions must be properly numbered
2. **Incorrect answer format**: Answer indicators must match the expected pattern
3. **Missing options**: Multiple choice questions need at least 2 options
4. **Invalid correct answer**: The correct answer must reference an existing option
5. **Inconsistent formatting**: Mixing different formats within the same file

### Validation Tools

Use the interactive mode for format validation:

```bash
txttoqti-edu --interactive
```

Or programmatic validation:

```python
from txttoqti import QuestionValidator
from txttoqti.parser import QuestionParser

parser = QuestionParser()
questions = parser.parse("questions.txt")

validator = QuestionValidator()
for question in questions:
    is_valid, errors = validator.validate(question)
    if not is_valid:
        print(f"Question {question.number}: {errors}")
```

## Best Practices

1. **Consistency**: Use the standardized format throughout all question banks
2. **Clarity**: Write clear, unambiguous questions and options
3. **Testing**: Validate your format before conversion
4. **Encoding**: Always save files in UTF-8 encoding
5. **Backup**: Keep original text files as backup before conversion
6. **Sequential Numbering**: Always start with Q1: and number sequentially

## Troubleshooting

### Format Detection Issues
- Ensure consistent question numbering
- Check that all required elements are present
- Verify correct answer format matches option format

### Character Encoding Problems
- Save files as UTF-8
- Avoid copying from word processors that add hidden characters
- Use plain text editors

### Conversion Errors
- Run format validation first
- Check for trailing spaces or empty lines
- Ensure proper line endings (Unix/Linux: LF, Windows: CRLF)

For additional help with question formatting, use the interactive troubleshooting mode:

```bash
txttoqti-edu --interactive
```