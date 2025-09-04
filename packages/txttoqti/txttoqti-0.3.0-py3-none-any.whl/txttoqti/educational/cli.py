"""
Educational CLI Interface

Enhanced command-line interface specifically designed for educational workflows.
Provides zero-configuration auto-detection and user-friendly error messages.

Author: Juliho C.C.
License: MIT
"""

import argparse
import sys
from pathlib import Path

from .converter import QtiConverter
from ..exceptions import TxtToQtiError


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser for educational CLI."""
    parser = argparse.ArgumentParser(
        prog="txttoqti-edu",
        description="Educational QTI Converter - Auto-detecting question bank converter for Canvas LMS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  txttoqti-edu                    # Convert with auto-detection
  txttoqti-edu --status          # Show current block status  
  txttoqti-edu --force           # Force regeneration
  txttoqti-edu --interactive     # Interactive troubleshooting mode

Supported Question Format:
  Q1: What is the result of type(42) in Python?
  A) <class 'float'>
  B) <class 'int'>
  C) <class 'str'>
  D) <class 'number'>
  RESPUESTA: B

The converter automatically detects your course block structure and
converts questions to Canvas-compatible QTI format.
        """
    )
    
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show current conversion status without performing conversion"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force regeneration even if no changes are detected"
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Enable interactive mode for troubleshooting format issues"
    )
    
    parser.add_argument(
        "--path",
        type=str,
        help="Specify working directory (defaults to current directory)"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    return parser


def main() -> int:
    """
    Main entry point for educational CLI.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Determine working path
        working_path = Path(args.path) if args.path else Path.cwd()
        
        # Initialize converter
        converter = QtiConverter(script_path=working_path)
        
        # Handle status-only request
        if args.status:
            converter.show_status()
            return 0
        
        # Handle interactive mode
        if args.interactive:
            return run_interactive_mode(converter)
        
        # Perform conversion
        success = converter.convert(force=args.force)
        return 0 if success else 1
        
    except TxtToQtiError as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        return 1
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def run_interactive_mode(converter: QtiConverter) -> int:
    """
    Run the converter in interactive troubleshooting mode.
    
    Args:
        converter: QtiConverter instance
        
    Returns:
        Exit code
    """
    print("🔍 Interactive Troubleshooting Mode")
    print("=" * 40)
    
    # Show current status
    converter.show_status()
    print()
    
    # Get file info for detailed analysis
    file_info = converter.get_file_info()
    
    if "error" in file_info:
        print("❌ Block Detection Issues:")
        print("   The converter couldn't detect your course block structure.")
        print("   Expected directory names: 'bloque-1', 'block-2', 'modulo-3', etc.")
        print("   Or files named: 'preguntas-bloque-1.txt', 'questions-block-2.txt', etc.")
        print()
        
        # Offer manual configuration
        block_num = input("Enter block number manually (or press Enter to exit): ").strip()
        if not block_num:
            return 1
        
        if not block_num.isdigit():
            print("❌ Invalid block number. Please enter a number.")
            return 1
        
        # Update converter with manual block number
        converter.block_num = block_num
        converter.input_filename = f"preguntas-bloque-{block_num}.txt"
        converter.output_filename = f"bloque-{block_num}-canvas.zip"
        converter.block_description = converter.block_detector.get_block_description(block_num)
        
        print(f"✅ Manual configuration: Block {block_num}")
        print()
    
    # Check input file
    if not file_info.get("input_exists", False):
        print("❌ Input File Missing:")
        print(f"   Expected file: {converter.input_filename}")
        print(f"   In directory: {converter.script_path}")
        print()
        
        # List available text files
        txt_files = list(converter.script_path.glob("*.txt"))
        if txt_files:
            print("📄 Available text files:")
            for i, txt_file in enumerate(txt_files, 1):
                print(f"   {i}. {txt_file.name}")
            print()
            
            choice = input("Select a file by number (or press Enter to exit): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(txt_files):
                selected_file = txt_files[int(choice) - 1]
                converter.input_filename = selected_file.name
                print(f"✅ Selected: {selected_file.name}")
                print()
            else:
                return 1
        else:
            print("   No .txt files found in directory.")
            return 1
    
    # Validate format if file exists
    input_path = converter.script_path / converter.input_filename
    if input_path.exists():
        print("🔍 Validating question format...")
        
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        is_valid, errors = converter.format_converter.validate_question_format(content)
        
        if is_valid:
            print("✅ Question format is valid!")
        else:
            print(f"⚠️ Found {len(errors)} format issues:")
            for error in errors[:3]:  # Show first 3 errors
                print(f"   • {error}")
            if len(errors) > 3:
                print(f"   ... and {len(errors) - 3} more")
            print()
            
            print("💡 Expected format:")
            print("   Q1: What is your question?")
            print("   A) First option")
            print("   B) Second option") 
            print("   C) Third option")
            print("   D) Fourth option")
            print("   RESPUESTA: B")
            print()
    
    # Ask if user wants to proceed
    proceed = input("Proceed with conversion? (Y/n): ").strip().lower()
    if proceed in ('', 'y', 'yes'):
        try:
            success = converter.convert(force=True)
            return 0 if success else 1
        except Exception as e:
            print(f"❌ Conversion failed: {e}")
            return 1
    else:
        print("⚠️ Conversion cancelled")
        return 1


if __name__ == "__main__":
    sys.exit(main())