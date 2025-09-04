#!/usr/bin/env python3
"""
Test script to verify that the API mismatch issues have been resolved.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_basic_conversion():
    """Test that basic text to QTI conversion works."""
    print("Testing basic conversion...")
    
    try:
        from txttoqti import TxtToQtiConverter
        print("✓ Successfully imported TxtToQtiConverter")
    except ImportError as e:
        print(f"✗ Failed to import TxtToQtiConverter: {e}")
        return False
    
    # Create test content
    test_content = """1. ¿Cuál es la capital de México?
a) Guadalajara
b) Monterrey
c) Ciudad de México
d) Cancún
Respuesta correcta: c

2. La Tierra gira alrededor del Sol.
a) Verdadero
b) Falso
Respuesta correcta: a"""
    
    # Write test file
    test_file = "test_questions.txt"
    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        print("✓ Created test file")
    except Exception as e:
        print(f"✗ Failed to create test file: {e}")
        return False
    
    # Test conversion
    try:
        converter = TxtToQtiConverter()
        print("✓ Successfully created TxtToQtiConverter instance")
        
        result = converter.convert_file(test_file)
        print(f"✓ Successfully converted file: {result}")
        
        # Check if output file exists
        if result and Path(result).exists():
            print("✓ Output QTI file was created")
            print(f"   File size: {Path(result).stat().st_size} bytes")
        else:
            print("✗ Output QTI file was not created")
            return False
            
    except Exception as e:
        print(f"✗ Conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        try:
            os.unlink(test_file)
            if result and Path(result).exists():
                os.unlink(result)
        except Exception:
            pass
    
    return True

def test_qti_generator_methods():
    """Test that QTIGenerator has the expected methods."""
    print("\nTesting QTIGenerator methods...")
    
    try:
        from txttoqti.qti_generator import QTIGenerator
        print("✓ Successfully imported QTIGenerator")
        
        generator = QTIGenerator()
        
        # Check for both methods
        if hasattr(generator, 'generate_qti_xml'):
            print("✓ generate_qti_xml method exists")
        else:
            print("✗ generate_qti_xml method missing")
            return False
            
        if hasattr(generator, 'generate'):
            print("✓ generate method exists (backward compatibility)")
        else:
            print("✗ generate method missing")
            return False
            
        # Test with empty list
        try:
            generator.generate_qti_xml([])
            print("✓ generate_qti_xml can be called with empty list")
        except Exception as e:
            print(f"✗ generate_qti_xml failed with empty list: {e}")
            return False
            
    except ImportError as e:
        print(f"✗ Failed to import QTIGenerator: {e}")
        return False
    except Exception as e:
        print(f"✗ QTIGenerator test failed: {e}")
        return False
    
    return True

def test_question_parsing():
    """Test that questions can be parsed correctly."""
    print("\nTesting question parsing...")
    
    try:
        from txttoqti.parser import QuestionParser
        print("✓ Successfully imported QuestionParser")
        
        parser = QuestionParser()
        
        test_text = """1. Test question?
a) Option A
b) Option B
c) Option C
d) Option D
Respuesta correcta: b"""
        
        questions = parser.parse(test_text)
        print(f"✓ Successfully parsed {len(questions)} questions")
        
        if questions:
            q = questions[0]
            print(f"   Question ID: {q.id}")
            print(f"   Question text: {q.text}")
            print(f"   Question type: {q.question_type}")
            print(f"   Number of choices: {len(q.choices)}")
            
            correct_choices = [c for c in q.choices if c.is_correct]
            print(f"   Correct choices: {len(correct_choices)}")
            
        return True
        
    except Exception as e:
        print(f"✗ Question parsing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("Running API mismatch fix tests...\n")
    
    tests = [
        test_qti_generator_methods,
        test_question_parsing,
        test_basic_conversion,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print(f"\n{'='*50}")
    print("Test Results:")
    for i, (test, result) in enumerate(zip(tests, results)):
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{i+1}. {test.__name__}: {status}")
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nSummary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The API mismatch issue has been resolved.")
        return 0
    else:
        print("❌ Some tests failed. The issue may not be fully resolved.")
        return 1

if __name__ == "__main__":
    exit(main())
