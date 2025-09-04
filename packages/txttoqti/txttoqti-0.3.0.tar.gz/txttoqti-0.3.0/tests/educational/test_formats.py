"""
Tests for educational format conversion.

Author: Juliho C.C.
License: MIT
"""

import unittest
import tempfile
from pathlib import Path

from txttoqti.educational.formats import FormatConverter


class TestFormatConverter(unittest.TestCase):
    """Test cases for FormatConverter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.educational_content = """Q1: What is the result of type(42) in Python?
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

        self.expected_txttoqti_content = """1. What is the result of type(42) in Python?
a) <class 'float'>
b) <class 'int'>
c) <class 'str'>
d) <class 'number'>
Respuesta correcta: b

2. If I execute name = "Barcelona" and then print(len(name)), what prints?
a) 8
b) 9
c) 10
d) Error
Respuesta correcta: b"""
    
    def test_convert_content(self):
        """Test content conversion from educational to txttoqti format."""
        result = FormatConverter._convert_content(self.educational_content)
        self.assertEqual(result, self.expected_txttoqti_content)
    
    def test_convert_to_txttoqti_format(self):
        """Test file conversion from educational to txttoqti format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as input_file:
            input_file.write(self.educational_content)
            input_path = input_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as output_file:
            output_path = output_file.name
        
        try:
            result_path = FormatConverter.convert_to_txttoqti_format(input_path, output_path)
            
            self.assertEqual(result_path, output_path)
            
            with open(output_path, 'r', encoding='utf-8') as f:
                result_content = f.read()
            
            self.assertEqual(result_content, self.expected_txttoqti_content)
            
        finally:
            Path(input_path).unlink()
            Path(output_path).unlink()
    
    def test_convert_nonexistent_file(self):
        """Test conversion with non-existent input file."""
        with self.assertRaises(FileNotFoundError):
            FormatConverter.convert_to_txttoqti_format("nonexistent.txt", "output.txt")
    
    def test_validate_question_format_valid(self):
        """Test validation of valid educational format."""
        is_valid, errors = FormatConverter.validate_question_format(self.educational_content)
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
    
    def test_single_question_conversion(self):
        """Test conversion of single question."""
        single_question = """Q1: What is Python?
A) A snake
B) A programming language
C) A movie
D) A book
RESPUESTA: B"""
        
        expected = """1. What is Python?
a) A snake
b) A programming language
c) A movie
d) A book
Respuesta correcta: b"""
        
        result = FormatConverter._convert_content(single_question)
        self.assertEqual(result, expected)
    
    def test_empty_content_conversion(self):
        """Test conversion of empty content."""
        result = FormatConverter._convert_content("")
        self.assertEqual(result, "")
    
    def test_content_with_empty_lines(self):
        """Test conversion with empty lines preserved."""
        content_with_empty_lines = """Q1: First question?
A) Option 1
B) Option 2
C) Option 3
D) Option 4
RESPUESTA: A


Q2: Second question?
A) Option 1
B) Option 2
C) Option 3
D) Option 4
RESPUESTA: B"""
        
        result = FormatConverter._convert_content(content_with_empty_lines)
        self.assertIn("\n\n\n", result)  # Empty lines should be preserved


if __name__ == '__main__':
    unittest.main()