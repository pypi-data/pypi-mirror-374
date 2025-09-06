# Command-Line Interface (CLI) Documentation

The `txttoqti` package provides two command-line interfaces for converting text-based question banks to QTI packages compatible with Canvas LMS.

## Basic CLI (`txttoqti`)

The basic CLI provides simple, direct conversion functionality.

### Usage

```bash
txttoqti [OPTIONS]
```

### Options

- `-i, --input FILE`: Path to the input text file containing questions (required)
- `-o, --output FILE`: Path for the output QTI ZIP file (optional)
- `-v, --version`: Show the version of the txttoqti package
- `-h, --help`: Show help message and exit

### Examples

Convert a text file to QTI package:
```bash
txttoqti -i questions.txt -o my_quiz.zip
```

Convert with automatic output naming:
```bash
txttoqti -i sample_questions.txt
```

Check version:
```bash
txttoqti --version
```

You can also use the module form:
```bash
python -m txttoqti.cli -i questions.txt -o output.zip
```

## Educational CLI (`txttoqti-edu`)

The educational CLI provides enhanced functionality with auto-detection, interactive troubleshooting, and educational workflow optimizations.

### Usage

```bash
txttoqti-edu [OPTIONS]
```

### Options

- `--status`: Show current conversion status without performing conversion
- `--force`: Force regeneration even if no changes are detected
- `--interactive`: Enable interactive mode for troubleshooting format issues
- `--path PATH`: Specify working directory (defaults to current directory)
- `--verbose, -v`: Enable verbose output
- `-h, --help`: Show help message and exit

### Examples

Convert with auto-detection (zero configuration):
```bash
txttoqti-edu
```

Show current status:
```bash
txttoqti-edu --status
```

Force regeneration:
```bash
txttoqti-edu --force
```

Interactive troubleshooting mode:
```bash
txttoqti-edu --interactive
```

Convert with verbose output:
```bash
txttoqti-edu --verbose
```

Specify custom working directory:
```bash
txttoqti-edu --path /path/to/course/materials
```

### Auto-Detection Features

The educational CLI automatically detects:

- Course block structure from directory names (`bloque-1`, `block-2`, `modulo-3`)
- Input files named `preguntas-bloque-X.txt` or `questions-block-X.txt`
- Output naming convention: `bloque-X-canvas.zip`

### Interactive Mode

When using `--interactive`, the CLI provides:

- File detection diagnostics
- Question format validation
- Manual configuration options
- Step-by-step troubleshooting guidance
- Error correction suggestions

### Supported Question Format

The educational CLI supports this standardized format:

```
Q1: What is the result of type(42) in Python?
A) <class 'float'>
B) <class 'int'>
C) <class 'str'>
D) <class 'number'>
RESPUESTA: B
```

## Error Handling

Both CLIs provide meaningful error messages:

- **File not found**: Clear indication of missing input files
- **Format errors**: Detailed validation messages with line numbers
- **Permission errors**: Guidance on file access issues
- **Conversion errors**: Specific error descriptions with suggested fixes

## Integration with Other Tools

The CLI tools can be integrated into educational workflows:

### Batch Processing

```bash
# Process multiple files
for file in *.txt; do
    txttoqti -i "$file" -o "${file%.txt}.zip"
done
```

### Course Management Scripts

```bash
#!/bin/bash
# Check status and convert if needed
txttoqti-edu --status
if [ $? -ne 0 ]; then
    txttoqti-edu --force
fi
```

### Continuous Integration

```bash
# In CI/CD pipeline
txttoqti-edu --verbose || exit 1
```

## Troubleshooting

Common issues and solutions:

1. **Command not found**: Ensure package is properly installed with `pip install txttoqti`
2. **Permission denied**: Check file permissions and directory access
3. **Format validation errors**: Use `txttoqti-edu --interactive` for detailed format checking
4. **Auto-detection fails**: Use manual file selection with `--interactive` mode or specify exact paths

For more help, use `--help` with either command or refer to the [examples documentation](examples.md).