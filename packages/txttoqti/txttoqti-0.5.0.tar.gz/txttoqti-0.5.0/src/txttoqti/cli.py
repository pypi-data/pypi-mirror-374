"""
cli: Command-line interface for the txttoqti package

This module provides a command-line interface for the txttoqti package, allowing users to convert text-based question banks to QTI packages directly from the terminal.

Usage:
    $ txttoqti -i questions.txt -o output.zip
    $ python -m txttoqti.cli [options]

Options:
    -h, --help          Show this help message and exit
    -i, --input FILE    Path to the input text file containing questions
    -o, --output FILE   Path for the output QTI ZIP file
    -v, --version       Show the version of the txttoqti package

Examples:
    $ txttoqti -i questions.txt -o quiz.zip
    $ python -m txttoqti.cli -i questions.txt -o output.zip

Note: For more advanced usage, consider using the Python API:
    import txttoqti
    converter = txttoqti.TxtToQti()
    converter.read_txt("questions.txt").save_to_qti("quiz.zip")

    Or for quick conversion:
    txttoqti.quick_convert("questions.txt", "quiz.zip")
"""

import argparse
from .converter import TxtToQtiConverter
from . import __version__

def main():
    parser = argparse.ArgumentParser(
        description="Convert text-based question banks to QTI packages.",
        epilog="""Examples:
  txttoqti -i questions.txt -o quiz.zip
  txttoqti -i my_questions.txt
  
For advanced usage, consider the Python API:
  import txttoqti
  converter = txttoqti.TxtToQti()
  converter.read_txt("questions.txt").save_to_qti("quiz.zip")
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('-i', '--input', required=True, help='Path to the input text file containing questions')
    parser.add_argument('-o', '--output', help='Path for the output QTI ZIP file (default: auto-generated)')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')

    args = parser.parse_args()

    converter = TxtToQtiConverter()
    qti_file = converter.convert_file(args.input, args.output)
    print(f"QTI package created: {qti_file}")

if __name__ == "__main__":
    main()