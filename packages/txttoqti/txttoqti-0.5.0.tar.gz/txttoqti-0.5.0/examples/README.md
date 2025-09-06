# txttoqti Examples

This directory contains comprehensive examples demonstrating how to use the txttoqti package with the new intuitive TxtToQti interface.

## Files

### `basic_usage.py`
Demonstrates fundamental usage patterns:
- **New TxtToQti Interface**: The recommended way to use txttoqti
- **Method Chaining**: Concise one-liner conversions
- **Quick Conversion**: Single function call for simple tasks
- **String Content**: Converting questions from strings instead of files
- **Legacy Interface**: Original API (still supported)

**Run it:**
```bash
cd examples
python3 basic_usage.py
```

### `advanced_usage.py`
Shows advanced features and integration patterns:
- **Batch Processing**: Handle multiple question files
- **Validation & Error Handling**: Robust error management
- **Question Objects**: Working with parsed question data
- **Custom Output Paths**: Flexible file organization  
- **Memory Efficiency**: Patterns for large datasets
- **Integration**: Pipeline and external tool integration

**Run it:**
```bash
cd examples  
python3 advanced_usage.py
```

### `sample_questions.txt`
Example question file in the correct format for testing the examples.

## Question Format

Questions should follow this format:

```
Q1: What is the capital of France?
A) London
B) Paris
C) Berlin  
D) Madrid
ANSWER: B

Q2: What is 2 + 2?
A) 3
B) 4
C) 5
D) 6  
ANSWER: B
```

## Quick Start

The simplest way to convert questions:

```python
import txttoqti

# Create converter
converter = txttoqti.TxtToQti()

# Load and convert
converter.read_txt("questions.txt")
converter.save_to_qti("quiz.zip")
```

Or even simpler:

```python
import txttoqti
txttoqti.quick_convert("questions.txt", "quiz.zip")
```

## Features Demonstrated

- ✅ **File-based conversion**: Load questions from text files
- ✅ **String-based conversion**: Load questions from strings  
- ✅ **Method chaining**: Fluent interface design
- ✅ **Validation**: Check question format before conversion
- ✅ **Preview**: See what questions were loaded
- ✅ **Error handling**: Robust error management
- ✅ **Batch processing**: Handle multiple files efficiently
- ✅ **Memory management**: Clear and reuse converter objects
- ✅ **Custom paths**: Flexible output file organization
- ✅ **Legacy support**: Backward compatibility maintained

## Running Examples

1. **Navigate to examples directory:**
   ```bash
   cd examples
   ```

2. **Run basic examples:**
   ```bash
   python3 basic_usage.py
   ```

3. **Run advanced examples:**
   ```bash  
   python3 advanced_usage.py
   ```

Both scripts are self-contained and will create sample question files if needed, then clean up after themselves.

## Integration Ideas

The examples show how txttoqti can integrate with:
- **Database systems**: Load questions from SQL queries
- **Web APIs**: Convert questions from REST endpoints  
- **File processors**: Batch convert multiple question banks
- **Educational platforms**: Automated quiz generation
- **Content management**: Dynamic QTI package creation

## Support

For more information:
- Check the main README.md in the project root
- Review the API documentation in CLAUDE.md
- See test files in tests/ for additional usage patterns