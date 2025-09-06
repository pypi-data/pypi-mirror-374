#!/usr/bin/env python3
"""
Test the new TxtToQti interface.
"""

import sys
import os
import unittest
from pathlib import Path
import tempfile

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from txttoqti import TxtToQti, quick_convert
from txttoqti.exceptions import TxtToQtiError, ParseError, ValidationError


class TestTxtToQtiInterface(unittest.TestCase):
    """Test cases for the new TxtToQti interface."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.converter = TxtToQti()
        self.sample_content = """Q1: What is the capital of France?
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
    
    def test_read_string(self):
        """Test reading questions from a string."""
        self.converter.read_string(self.sample_content)
        self.assertEqual(len(self.converter), 2)
        self.assertFalse(self.converter.is_empty())
        
        questions = self.converter.get_questions()
        self.assertEqual(len(questions), 2)
        self.assertEqual(questions[0].text, "What is the capital of France?")
        self.assertEqual(questions[1].text, "What is 2 + 2?")
    
    def test_read_txt_from_file(self):
        """Test reading questions from a file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.sample_content)
            temp_file = f.name
        
        try:
            self.converter.read_txt(temp_file)
            self.assertEqual(len(self.converter), 2)
        finally:
            os.unlink(temp_file)
    
    def test_save_to_qti(self):
        """Test saving to QTI file."""
        self.converter.read_string(self.sample_content)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test.zip"
            result = self.converter.save_to_qti(str(output_file))
            
            self.assertEqual(result, str(output_file))
            self.assertTrue(output_file.exists())
            self.assertGreater(output_file.stat().st_size, 0)
    
    def test_method_chaining(self):
        """Test that methods can be chained."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.sample_content)
            temp_file = f.name
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "chained.zip"
            
            try:
                result = self.converter.read_txt(temp_file).save_to_qti(str(output_file))
                self.assertTrue(Path(result).exists())
            finally:
                os.unlink(temp_file)
    
    def test_validate(self):
        """Test validation of loaded questions."""
        self.converter.read_string(self.sample_content)
        self.assertTrue(self.converter.validate())
    
    def test_preview(self):
        """Test preview functionality."""
        self.converter.read_string(self.sample_content)
        preview = self.converter.preview()
        self.assertIn("Loaded 2 questions", preview)
        self.assertIn("What is the capital of France?", preview)
        self.assertIn("Paris", preview)
    
    def test_clear(self):
        """Test clearing loaded questions."""
        self.converter.read_string(self.sample_content)
        self.assertEqual(len(self.converter), 2)
        
        self.converter.clear()
        self.assertEqual(len(self.converter), 0)
        self.assertTrue(self.converter.is_empty())
    
    def test_empty_content(self):
        """Test handling of empty content."""
        self.converter.read_string("")
        self.assertTrue(self.converter.is_empty())
        self.assertEqual(len(self.converter), 0)
    
    def test_save_without_loading(self):
        """Test that saving without loading questions raises error."""
        with self.assertRaises(TxtToQtiError):
            self.converter.save_to_qti("test.zip")
    
    def test_validate_without_loading(self):
        """Test that validating without loading questions raises error."""
        with self.assertRaises(TxtToQtiError):
            self.converter.validate()
    
    def test_repr(self):
        """Test string representation."""
        repr_str = repr(self.converter)
        self.assertIn("TxtToQti", repr_str)
        self.assertIn("questions=0", repr_str)
        
        self.converter.read_string(self.sample_content)
        repr_str = repr(self.converter)
        self.assertIn("questions=2", repr_str)
    
    def test_bool_conversion(self):
        """Test boolean conversion."""
        self.assertFalse(bool(self.converter))
        
        self.converter.read_string(self.sample_content)
        self.assertTrue(bool(self.converter))


class TestQuickConvert(unittest.TestCase):
    """Test cases for quick_convert function."""
    
    def test_quick_convert(self):
        """Test quick conversion function."""
        sample_content = """Q1: Quick test?
A) Yes
B) No
ANSWER: A
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(sample_content)
            input_file = f.name
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "quick.zip"
            
            try:
                result = quick_convert(input_file, str(output_file))
                self.assertEqual(result, str(output_file))
                self.assertTrue(output_file.exists())
            finally:
                os.unlink(input_file)


if __name__ == '__main__':
    unittest.main()