"""
Tests for educational format validation.

Author: Juliho C.C.
License: MIT
"""

import unittest

from txttoqti.educational.formats import FormatConverter


class TestFormatConverter(unittest.TestCase):
    """Test cases for FormatConverter validation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.valid_educational_content = """Q1: What is the result of type(42) in Python?
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
RESPUESTA: B"""
    
    # Conversion tests removed - parser now handles educational format directly
    # Only validation functionality remains
    
    def test_validate_question_format_valid(self):
        """Test validation of valid educational format."""
        is_valid, errors = FormatConverter.validate_question_format(self.valid_educational_content)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_validate_question_format_invalid_duplicate_question(self):
        """Test validation with duplicate question numbers."""
        invalid_content = """Q1: First question?
A) Option 1
B) Option 2
C) Option 3
D) Option 4
RESPUESTA: A

Q1: Duplicate question?
A) Option 1
B) Option 2
C) Option 3
D) Option 4
RESPUESTA: B"""
        
        is_valid, errors = FormatConverter.validate_question_format(invalid_content)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("Duplicate question number" in error for error in errors))
    
    def test_validate_question_format_invalid_duplicate_choice(self):
        """Test validation with duplicate choices."""
        invalid_content = """Q1: What is the answer?
A) Option 1
A) Duplicate option
C) Option 3
D) Option 4
RESPUESTA: A"""
        
        is_valid, errors = FormatConverter.validate_question_format(invalid_content)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("Duplicate choice" in error for error in errors))
    
    def test_validate_question_format_invalid_answer_not_in_choices(self):
        """Test validation with answer not matching any choice."""
        invalid_content = """Q1: What is the answer?
A) Option 1
B) Option 2
C) Option 3
D) Option 4
RESPUESTA: E"""
        
        is_valid, errors = FormatConverter.validate_question_format(invalid_content)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("does not match any choice" in error for error in errors))
    
    def test_validate_question_format_non_sequential_questions(self):
        """Test validation with non-sequential question numbers."""
        invalid_content = """Q1: First question?
A) Option 1
B) Option 2
C) Option 3
D) Option 4
RESPUESTA: A

Q3: Skipped question 2?
A) Option 1
B) Option 2
C) Option 3
D) Option 4
RESPUESTA: B"""
        
        is_valid, errors = FormatConverter.validate_question_format(invalid_content)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("not sequential" in error for error in errors))
    
    def test_validate_question_format_unrecognized_line(self):
        """Test validation with unrecognized format."""
        invalid_content = """Q1: What is the answer?
A) Option 1
B) Option 2
C) Option 3
D) Option 4
RESPUESTA: A
This line doesn't match any pattern"""
        
        is_valid, errors = FormatConverter.validate_question_format(invalid_content)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("Unrecognized format" in error for error in errors))


if __name__ == '__main__':
    unittest.main()