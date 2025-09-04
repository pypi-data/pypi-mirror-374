#!/usr/bin/env python3
"""
End-to-end test demonstrating the original bug report scenario now works.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_original_bug_scenario():
    """Test the exact scenario described in the bug report."""
    print("Testing the original bug report scenario...")
    
    # Create a test file with the expected format from the bug report
    test_content = """1. ¿Cuál es la capital de México?
a) Guadalajara
b) Monterrey 
c) Ciudad de México
d) Cancún
Respuesta correcta: c"""
    
    test_file = "bug_test.txt"
    result = None  # Initialize result variable
    
    try:
        # Write the test file
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        print("✓ Created test file with bug report content")
        
        # Try to convert - this would previously fail with AttributeError
        from txttoqti import TxtToQtiConverter
        converter = TxtToQtiConverter()
        result = converter.convert_file(test_file)
        
        print("✓ convert_file() executed without AttributeError")
        print(f"✓ Result: {result}")
        
        # Verify the result
        if result and Path(result).exists():
            print("✓ QTI package file was created successfully")
            file_size = Path(result).stat().st_size
            print(f"   File size: {file_size} bytes")
            
            if file_size > 0:
                print("✓ QTI package is not empty")
            else:
                print("✗ QTI package is empty")
                return False
                
        else:
            print("✗ No QTI package file created")
            return False
            
        print("\n🎉 The original bug report scenario now works perfectly!")
        return True
        
    except AttributeError as e:
        if "'QTIGenerator' object has no attribute 'generate'" in str(e):
            print(f"✗ Original bug still exists: {e}")
            return False
        else:
            print(f"✗ Different AttributeError: {e}")
            return False
    except Exception as e:
        print(f"✗ Conversion failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        result = None  # Initialize to avoid unbound variable
        try:
            if os.path.exists(test_file):
                os.unlink(test_file)
            if 'result' in locals() and result and Path(result).exists():
                os.unlink(result)
        except Exception:
            pass

def test_suggested_test_case():
    """Test the suggested test case from the bug report."""
    print("\nTesting the suggested test case from the bug report...")
    
    test_text = """1. Test question?
a) Option A
b) Option B
c) Option C
d) Option D
Respuesta correcta: b"""
    
    test_file = "suggested_test.txt"
    result = None  # Initialize result variable
    
    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_text)
            
        from txttoqti import TxtToQtiConverter
        converter = TxtToQtiConverter()
        
        # This should not raise an AttributeError
        result = converter.convert_file(test_file)
        
        print("✓ No AttributeError raised")
        assert result is not None, "Result should not be None"
        assert result.endswith('.zip'), "Result should be a ZIP file"
        
        print("✓ Result is not None")
        print("✓ Result ends with '.zip'")
        print(f"   Created file: {result}")
        
        return True
        
    except Exception as e:
        print(f"✗ Suggested test case failed: {e}")
        return False
    finally:
        # Cleanup
        try:
            if os.path.exists(test_file):
                os.unlink(test_file)
            if result and Path(result).exists():
                os.unlink(result)
        except Exception:
            pass

def main():
    """Run all end-to-end tests."""
    print("Running end-to-end tests to verify bug fixes...\n")
    
    tests = [
        test_original_bug_scenario,
        test_suggested_test_case,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print(f"\n{'='*60}")
    print("End-to-End Test Results:")
    for i, (test, result) in enumerate(zip(tests, results)):
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{i+1}. {test.__name__}: {status}")
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nSummary: {passed}/{total} end-to-end tests passed")
    
    if passed == total:
        print("🎉 All end-to-end tests passed! The bug has been completely fixed.")
        return 0
    else:
        print("❌ Some end-to-end tests failed.")
        return 1

if __name__ == "__main__":
    exit(main())
