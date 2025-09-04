#!/usr/bin/env python3
"""
Educational Extension Example

Demonstrates how to use the educational extension for txttoqti.
This example shows the zero-configuration approach for educational institutions.

Author: Juliho C.C.
License: MIT
"""

from pathlib import Path
import tempfile
import os

def main():
    """Demonstrate educational extension usage."""
    
    # Create a temporary directory structure that mimics a course
    with tempfile.TemporaryDirectory() as temp_dir:
        print("🎓 Educational Extension Example")
        print("=" * 40)
        
        # Create course block directory
        course_dir = Path(temp_dir) / "curso-data-science" / "bloque-1"
        course_dir.mkdir(parents=True)
        
        # Create sample educational format questions
        questions_content = """Q1: What is the result of type(42) in Python?
A) <class 'float'>
B) <class 'int'>
C) <class 'str'>
D) <class 'number'>
RESPUESTA: B

Q2: If I execute name = "Barcelona" and then print(len(name)), what prints?
A) 8
B) 9
C) 10
D) Error
RESPUESTA: B

Q3: Which of the following creates a list in Python?
A) {}
B) ()
C) []
D) ""
RESPUESTA: C"""
        
        questions_file = course_dir / "preguntas-bloque-1.txt"
        questions_file.write_text(questions_content)
        
        print(f"📁 Created course structure: {course_dir}")
        print(f"📄 Created questions file: {questions_file.name}")
        print()
        
        # Change to the course directory
        original_cwd = os.getcwd()
        os.chdir(course_dir)
        
        try:
            # Import and use the educational extension
            from txttoqti.educational import QtiConverter
            
            print("🔍 Initializing Educational QTI Converter...")
            converter = QtiConverter()
            print("✅ Auto-detection successful!")
            print()
            
            # Show status
            print("📊 Current Status:")
            converter.show_status()
            print()
            
            # Get detailed file information
            print("📋 File Information:")
            file_info = converter.get_file_info()
            for key, value in file_info.items():
                if key != "working_directory":  # Skip long path
                    print(f"   {key}: {value}")
            print()
            
            # Perform conversion
            print("🔄 Starting conversion...")
            success = converter.convert()
            
            if success:
                print("✅ Conversion completed successfully!")
                
                # Check if output file was created
                output_file = course_dir / "bloque-1-canvas.zip"
                if output_file.exists():
                    print(f"📦 QTI package created: {output_file.name}")
                    print(f"   Size: {output_file.stat().st_size} bytes")
                
            else:
                print("❌ Conversion failed!")
            
        except ImportError:
            print("❌ Educational extension not available!")
            print("   Make sure to install txttoqti with educational support.")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            
        finally:
            os.chdir(original_cwd)


def demonstrate_cli_usage():
    """Show CLI usage examples."""
    print("\n🖥️  CLI Usage Examples:")
    print("=" * 40)
    
    print("Basic conversion (auto-detection):")
    print("  txttoqti-edu")
    print()
    
    print("Show current status:")
    print("  txttoqti-edu --status")
    print()
    
    print("Force regeneration:")
    print("  txttoqti-edu --force")
    print()
    
    print("Interactive troubleshooting:")
    print("  txttoqti-edu --interactive")
    print()
    
    print("Specify custom directory:")
    print("  txttoqti-edu --path /path/to/course/bloque-2")
    print()


def demonstrate_programmatic_usage():
    """Show programmatic usage examples."""
    print("\n💻 Programmatic Usage:")
    print("=" * 40)
    
    print("""
# Basic usage with auto-detection
from txttoqti.educational import QtiConverter

converter = QtiConverter()  # Auto-detects block structure
converter.show_status()     # Display current status
success = converter.convert()  # Convert to QTI

# Usage with specific path  
from pathlib import Path
converter = QtiConverter(script_path=Path("/course/bloque-2"))
success = converter.convert(force=True)  # Force regeneration

# Get detailed information
file_info = converter.get_file_info()
print(f"Block: {file_info['block_number']}")
print(f"Questions: {file_info['question_count']}")
""")


if __name__ == "__main__":
    main()
    demonstrate_cli_usage()
    demonstrate_programmatic_usage()