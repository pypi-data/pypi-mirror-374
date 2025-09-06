#!/usr/bin/env python3
"""
basic_usage.py: Comprehensive examples of txttoqti usage with the new TxtToQti interface

This script demonstrates multiple ways to use txttoqti for converting
text-based question banks to QTI packages, featuring the new intuitive interface.

Example Usage:
    1. Ensure you have a text file with questions (e.g., sample_questions.txt).
    2. Run this script to see various conversion methods.

"""

import sys
from pathlib import Path

# Add src to path for examples
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import txttoqti


def new_interface_example():
    """Demonstrate the new TxtToQti interface (recommended)."""
    print("=== New TxtToQti Interface (Recommended) ===")
    
    # Create converter object
    converter = txttoqti.TxtToQti()
    
    # Load questions from file
    converter.read_txt("sample_questions.txt")
    
    print(f"Loaded {len(converter)} questions")
    
    # Preview what was loaded
    print("Preview:")
    print(converter.preview(max_questions=2))
    
    # Validate before saving
    converter.validate()
    
    # Save to QTI package
    output_file = converter.save_to_qti("new_interface_quiz.zip")
    print(f"✓ QTI package created: {output_file}")


def method_chaining_example():
    """Show method chaining for concise code."""
    print("\n=== Method Chaining ===")
    
    # One-liner conversion
    output_file = (txttoqti.TxtToQti()
                  .read_txt("sample_questions.txt")
                  .save_to_qti("chained_quiz.zip"))
    
    print(f"✓ Chained conversion: {output_file}")


def quick_conversion_example():
    """Show the quickest conversion method."""
    print("\n=== Quick Conversion ===")
    
    # Single function call for simple conversions
    output_file = txttoqti.quick_convert("sample_questions.txt", "quick_quiz.zip")
    print(f"✓ Quick conversion: {output_file}")


def string_content_example():
    """Convert questions from a string."""
    print("\n=== String Content Conversion ===")
    
    # Sample questions as a string
    questions_text = """Q1: What is the capital of France?
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
"""
    
    converter = txttoqti.TxtToQti()
    converter.read_string(questions_text)
    
    print(f"Loaded {len(converter)} questions from string")
    output_file = converter.save_to_qti("string_quiz.zip")
    print(f"✓ String conversion: {output_file}")


def legacy_interface_example():
    """Show the original interface (still supported)."""
    print("\n=== Legacy Interface (Still Supported) ===")
    
    # Original convenience function
    output_file = txttoqti.convert_txt_to_qti("sample_questions.txt", "legacy_quiz.zip")
    print(f"✓ Legacy conversion: {output_file}")


def main():
    """Run all examples."""
    print("txttoqti Usage Examples")
    print("=" * 40)
    
    # Create a sample questions file if it doesn't exist
    sample_file = Path("sample_questions.txt")
    if not sample_file.exists():
        sample_content = """Q1: What is Python?
A) A snake
B) A programming language  
C) A web browser
D) An operating system
ANSWER: B

Q2: Which of these is a Python web framework?
A) React
B) Angular
C) Django
D) jQuery
ANSWER: C

Q3: What does PEP stand for?
A) Python Enhancement Proposal
B) Python Execution Protocol
C) Python Error Prevention
D) Python Extension Package
ANSWER: A
"""
        sample_file.write_text(sample_content, encoding='utf-8')
        print(f"Created sample file: {sample_file}")
    
    try:
        new_interface_example()
        method_chaining_example()
        quick_conversion_example()
        string_content_example()
        legacy_interface_example()
        
        print(f"\n✓ All examples completed successfully!")
        print("Check the generated .zip files for your QTI packages.")
        
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up generated files
        cleanup_files = ["new_interface_quiz.zip", "chained_quiz.zip", "quick_quiz.zip", 
                        "string_quiz.zip", "legacy_quiz.zip", "sample_questions.txt"]
        for filename in cleanup_files:
            Path(filename).unlink(missing_ok=True)
        print("Cleaned up example files")


if __name__ == "__main__":
    main()