# Installation Instructions for txttoqti

## Prerequisites

Before installing `txttoqti`, make sure you have Python 3.10 or higher installed on your system. You can check your Python version by running the following command in your terminal:

```bash
python --version
```

## Installation from PyPI

To install the `txttoqti` package, you can use `pip`, Python's package manager. Open your terminal and run the following command:

```bash
pip install txttoqti
```

## Installation from Source

If you want to install `txttoqti` from source code, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/julihocc/txttoqti.git
   ```

2. Navigate to the project directory:

   ```bash
   cd txttoqti
   ```

3. Install the package using `pip`:

   ```bash
   pip install .
   ```

## Development Installation

For development, install the package in editable mode with development dependencies:

```bash
pip install -e ".[dev]"
```

## Dependencies

`txttoqti` has no external dependencies as it uses only Python's standard library. However, if you want to contribute to the package development, you can install the development dependencies:

```bash
pip install "txttoqti[dev]"
```

This will install testing and code quality tools like pytest, black, flake8, and mypy.

## Installation Verification

To verify that `txttoqti` has been installed correctly, you can run the following command in your terminal:

```bash
python -c "import txttoqti; print(txttoqti.__version__)"
```

This should display the installed version of the package.

You can also test the CLI commands:

```bash
txttoqti --help
txttoqti-edu --help
```