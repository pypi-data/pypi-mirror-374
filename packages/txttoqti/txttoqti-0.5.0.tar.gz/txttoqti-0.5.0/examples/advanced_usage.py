#!/usr/bin/env python3
"""
advanced_usage.py: Advanced examples of txttoqti usage

This script demonstrates advanced features of the txttoqti package including
batch processing, validation, error handling, and integration patterns.
"""

import sys
from pathlib import Path
import tempfile

# Add src to path for examples
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import txttoqti


def batch_processing_example():
    """Process multiple question files in batch."""
    print("=== Batch Processing ===")
    
    # Create multiple sample files
    sample_files = []
    contents = [
        """Q1: Python Question Set A
A) Option A1
B) Option B1
C) Option C1
D) Option D1
ANSWER: A
""",
        """Q1: Python Question Set B  
A) Option A2
B) Option B2
C) Option C2
D) Option D2
ANSWER: B
""",
        """Q1: Python Question Set C
A) Option A3
B) Option B3
C) Option C3
D) Option D3
ANSWER: C
"""
    ]
    
    # Create temporary files
    for i, content in enumerate(contents, 1):
        temp_file = Path(f"batch_questions_{i}.txt")
        temp_file.write_text(content, encoding='utf-8')
        sample_files.append(temp_file)
    
    converter = txttoqti.TxtToQti()
    
    try:
        # Process each file
        for txt_file in sample_files:
            output_name = f"batch_{txt_file.stem}.zip"
            converter.read_txt(txt_file).save_to_qti(output_name).clear()
            print(f"✓ Processed {txt_file} → {output_name}")
            
    finally:
        # Clean up
        for temp_file in sample_files:
            temp_file.unlink(missing_ok=True)
        for output_file in Path(".").glob("batch_*.zip"):
            output_file.unlink(missing_ok=True)


def validation_and_error_handling():
    """Demonstrate validation and error handling."""
    print("\n=== Validation and Error Handling ===")
    
    # Valid content
    valid_content = """Q1: Valid question?
A) Yes
B) No
C) Maybe
D) Unknown
ANSWER: A
"""
    
    # Invalid content (missing answer)
    invalid_content = """Q1: Invalid question?
A) Yes
B) No
C) Maybe
D) Unknown
"""
    
    converter = txttoqti.TxtToQti()
    
    # Test valid content
    print("Testing valid content...")
    try:
        converter.read_string(valid_content)
        converter.validate()
        print("✓ Valid content passed validation")
        converter.clear()
    except Exception as e:
        print(f"✗ Unexpected error with valid content: {e}")
    
    # Test invalid content
    print("Testing invalid content...")
    try:
        converter.read_string(invalid_content)
        converter.validate()
        print("✗ Invalid content should have failed validation")
    except txttoqti.ValidationError as e:
        print(f"✓ Invalid content correctly failed validation: {e}")
    except Exception as e:
        print(f"✗ Unexpected error type: {e}")
    
    # Test empty content
    print("Testing empty content...")
    converter.read_string("")
    if converter.is_empty():
        print("✓ Empty content correctly detected")
    else:
        print("✗ Empty content detection failed")


def working_with_question_objects():
    """Show how to work with Question objects directly."""
    print("\n=== Working with Question Objects ===")
    
    content = """Q1: What is the capital of Japan?
A) Seoul
B) Tokyo
C) Beijing
D) Bangkok
ANSWER: B

Q2: What is 5 + 3?
A) 6
B) 7
C) 8
D) 9
ANSWER: C
"""
    
    converter = txttoqti.TxtToQti()
    converter.read_string(content)
    
    # Get question objects
    questions = converter.get_questions()
    
    print(f"Retrieved {len(questions)} question objects:")
    for i, question in enumerate(questions, 1):
        print(f"\nQuestion {i}:")
        print(f"  Text: {question.text}")
        print(f"  Type: {question.question_type}")
        print(f"  Choices:")
        for choice in question.choices:
            marker = "✓" if choice.is_correct else " "
            print(f"    [{marker}] {choice.id}: {choice.text}")


def custom_output_paths():
    """Demonstrate custom output path handling."""
    print("\n=== Custom Output Paths ===")
    
    content = """Q1: Test question?
A) Option A
B) Option B
C) Option C
D) Option D
ANSWER: A
"""
    
    converter = txttoqti.TxtToQti()
    converter.read_string(content)
    
    # Save with custom paths
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Save with absolute path
        abs_output = temp_path / "absolute_path_quiz.zip"
        result = converter.save_to_qti(str(abs_output))
        print(f"✓ Saved with absolute path: {result}")
        
        # Save with relative path in subdirectory
        subdir = temp_path / "subdir"
        subdir.mkdir()
        rel_output = subdir / "relative_quiz.zip"
        result = converter.save_to_qti(str(rel_output))
        print(f"✓ Saved in subdirectory: {result}")
        
        # Auto-generated name
        result = converter.save_to_qti()
        print(f"✓ Auto-generated name: {result}")
        Path(result).unlink(missing_ok=True)  # Clean up the auto-generated file


def memory_efficient_processing():
    """Show memory-efficient processing patterns."""
    print("\n=== Memory Efficient Processing ===")
    
    # Simulate processing large numbers of questions
    large_content_parts = []
    for i in range(1, 6):  # Create 5 questions
        part = f"""Q{i}: Question number {i}?
A) Option A{i}
B) Option B{i}
C) Option C{i}
D) Option D{i}
ANSWER: A
"""
        large_content_parts.append(part)
    
    large_content = "\n".join(large_content_parts)
    
    # Process and immediately save to avoid keeping everything in memory
    converter = txttoqti.TxtToQti()
    
    print("Processing large question set...")
    converter.read_string(large_content)
    print(f"Loaded {len(converter)} questions")
    
    # Save and clear immediately
    output_file = converter.save_to_qti("large_quiz.zip")
    print(f"✓ Saved large quiz: {output_file}")
    
    # Clear memory
    converter.clear()
    print("✓ Memory cleared")
    
    # Clean up
    Path("large_quiz.zip").unlink(missing_ok=True)


def integration_with_other_tools():
    """Show integration patterns with other tools."""
    print("\n=== Integration Patterns ===")
    
    # Simulate reading from a database or API (using string for demo)
    def simulate_database_fetch():
        """Simulate fetching questions from external source."""
        return """Q1: Database question?
A) MySQL
B) PostgreSQL
C) SQLite
D) All of the above
ANSWER: D
"""
    
    # Simulate processing pipeline
    def process_questions_pipeline(source_data):
        """Process questions through a pipeline."""
        converter = txttoqti.TxtToQti()
        
        # Load data
        converter.read_string(source_data)
        
        # Validate
        try:
            converter.validate()
            print("✓ Questions validated in pipeline")
        except Exception as e:
            print(f"✗ Pipeline validation failed: {e}")
            return None
        
        # Transform (could add custom processing here)
        print(f"✓ Pipeline processed {len(converter)} questions")
        
        # Output
        return converter.save_to_qti("pipeline_quiz.zip")
    
    # Run the pipeline
    print("Running processing pipeline...")
    db_data = simulate_database_fetch()
    result = process_questions_pipeline(db_data)
    
    if result:
        print(f"✓ Pipeline completed: {result}")
        Path(result).unlink(missing_ok=True)  # Clean up
    else:
        print("✗ Pipeline failed")


def main():
    """Run all advanced examples."""
    print("txttoqti Advanced Usage Examples")
    print("=" * 45)
    
    try:
        batch_processing_example()
        validation_and_error_handling()
        working_with_question_objects()
        custom_output_paths()
        memory_efficient_processing()
        integration_with_other_tools()
        
        print(f"\n✓ All advanced examples completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Error running advanced examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()