"""
Tests for educational QTI converter orchestration.

Author: Juliho C.C.
License: MIT
"""

import unittest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from txttoqti.educational.converter import QtiConverter
from txttoqti.exceptions import ConversionError, FileError


class TestQtiConverter(unittest.TestCase):
    """Test cases for QtiConverter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.educational_content = """Q1: What is Python?
A) A snake
B) A programming language  
C) A movie
D) A book
RESPUESTA: B

Q2: What is 2 + 2?
A) 3
B) 4
C) 5
D) 6
RESPUESTA: B"""
        
    def test_init_with_valid_block_structure(self):
        """Test initialization with valid block directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            block_dir = Path(temp_dir) / "bloque-1"
            block_dir.mkdir(parents=True)
            
            converter = QtiConverter(script_path=block_dir)
            
            self.assertEqual(converter.block_num, "1")
            self.assertEqual(converter.input_filename, "preguntas-bloque-1.txt")
            self.assertEqual(converter.output_filename, "bloque-1-canvas.zip")
            self.assertEqual(converter.block_description, "Python fundamentals")
    
    def test_init_with_invalid_block_structure(self):
        """Test initialization with invalid block directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid_dir = Path(temp_dir) / "random-directory"
            invalid_dir.mkdir(parents=True)
            
            converter = QtiConverter(script_path=invalid_dir)
            
            self.assertIsNone(converter.block_num)
            self.assertIsNone(converter.input_filename)
            self.assertIsNone(converter.output_filename)
            self.assertIsNone(converter.block_description)
    
    def test_show_status_with_valid_block(self):
        """Test show_status with valid block detection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            block_dir = Path(temp_dir) / "bloque-2"
            block_dir.mkdir(parents=True)
            
            # Create input file
            input_file = block_dir / "preguntas-bloque-2.txt"
            input_file.write_text(self.educational_content)
            
            converter = QtiConverter(script_path=block_dir)
            
            # Capture output
            import io
            import sys
            captured_output = io.StringIO()
            sys.stdout = captured_output
            
            try:
                converter.show_status()
                output = captured_output.getvalue()
                
                self.assertIn("Block 2: Data exploration", output)
                self.assertIn("Questions found: 2", output)
                self.assertIn("preguntas-bloque-2.txt", output)
                self.assertIn("bloque-2-canvas.zip", output)
                
            finally:
                sys.stdout = sys.__stdout__
    
    def test_show_status_with_invalid_block(self):
        """Test show_status with failed block detection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid_dir = Path(temp_dir) / "random"
            invalid_dir.mkdir(parents=True)
            
            converter = QtiConverter(script_path=invalid_dir)
            
            # Capture output
            import io
            import sys
            captured_output = io.StringIO()
            sys.stdout = captured_output
            
            try:
                converter.show_status()
                output = captured_output.getvalue()
                
                self.assertIn("Block detection failed", output)
                self.assertIn("bloque-1", output)  # Should suggest structure
                
            finally:
                sys.stdout = sys.__stdout__
    
    def test_get_file_info_with_valid_setup(self):
        """Test get_file_info with valid block and file setup."""
        with tempfile.TemporaryDirectory() as temp_dir:
            block_dir = Path(temp_dir) / "bloque-3"
            block_dir.mkdir(parents=True)
            
            # Create input file
            input_file = block_dir / "preguntas-bloque-3.txt"
            input_file.write_text(self.educational_content)
            
            converter = QtiConverter(script_path=block_dir)
            info = converter.get_file_info()
            
            self.assertEqual(info["block_number"], "3")
            self.assertEqual(info["block_description"], "Machine learning")
            self.assertTrue(info["input_exists"])
            self.assertFalse(info["output_exists"])
            self.assertEqual(info["question_count"], 2)
            self.assertTrue(info["needs_regeneration"])
    
    def test_get_file_info_with_invalid_block(self):
        """Test get_file_info with failed block detection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid_dir = Path(temp_dir) / "random"
            invalid_dir.mkdir(parents=True)
            
            converter = QtiConverter(script_path=invalid_dir)
            info = converter.get_file_info()
            
            self.assertIn("error", info)
            self.assertEqual(info["error"], "Block detection failed")
    
    def test_convert_with_missing_block_info(self):
        """Test convert with missing block detection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid_dir = Path(temp_dir) / "random"
            invalid_dir.mkdir(parents=True)
            
            converter = QtiConverter(script_path=invalid_dir)
            
            with self.assertRaises(ConversionError) as context:
                converter.convert()
            
            self.assertIn("Block detection failed", str(context.exception))
    
    def test_convert_with_missing_input_file(self):
        """Test convert with missing input file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            block_dir = Path(temp_dir) / "bloque-1"
            block_dir.mkdir(parents=True)
            
            converter = QtiConverter(script_path=block_dir)
            
            with self.assertRaises(FileError) as context:
                converter.convert()
            
            self.assertIn("Input file not found", str(context.exception))
    
    @patch('txttoqti.educational.utils.FileManager.file_changed')
    def test_convert_file_up_to_date_no_force(self, mock_file_changed):
        """Test convert when file is up to date and force=False."""
        mock_file_changed.return_value = False  # File hasn't changed
        
        with tempfile.TemporaryDirectory() as temp_dir:
            block_dir = Path(temp_dir) / "bloque-1"
            block_dir.mkdir(parents=True)
            
            # Create input file
            input_file = block_dir / "preguntas-bloque-1.txt"
            input_file.write_text(self.educational_content)
            
            converter = QtiConverter(script_path=block_dir)
            
            # Capture output
            import io
            import sys
            captured_output = io.StringIO()
            sys.stdout = captured_output
            
            try:
                result = converter.convert()
                output = captured_output.getvalue()
                
                self.assertTrue(result)
                self.assertIn("up to date", output)
                
            finally:
                sys.stdout = sys.__stdout__
    
    @patch('txttoqti.converter.TxtToQtiConverter.convert_file')
    @patch('txttoqti.educational.utils.FileManager.file_changed')
    def test_convert_with_force(self, mock_file_changed, mock_txttoqti_convert):
        """Test convert with force=True."""
        mock_file_changed.return_value = False  # File hasn't changed
        mock_txttoqti_convert.return_value = "output.zip"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            block_dir = Path(temp_dir) / "bloque-1"
            block_dir.mkdir(parents=True)
            
            # Create input file
            input_file = block_dir / "preguntas-bloque-1.txt"
            input_file.write_text(self.educational_content)
            
            converter = QtiConverter(script_path=block_dir)
            
            with patch('builtins.input', return_value='y'):
                result = converter.convert(force=True)
            
            self.assertTrue(result)
            mock_txttoqti_convert.assert_called_once()
    
    def test_convert_with_format_validation_errors(self):
        """Test convert with format validation errors and user cancellation."""
        invalid_content = """Q1: Invalid question
A) Option 1
A) Duplicate option
C) Option 3
RESPUESTA: B"""  # B is not in choices
        
        with tempfile.TemporaryDirectory() as temp_dir:
            block_dir = Path(temp_dir) / "bloque-1"
            block_dir.mkdir(parents=True)
            
            # Create input file with invalid content
            input_file = block_dir / "preguntas-bloque-1.txt"
            input_file.write_text(invalid_content)
            
            converter = QtiConverter(script_path=block_dir)
            
            # Mock user input to cancel conversion
            with patch('builtins.input', return_value='n'):
                result = converter.convert()
                
                self.assertFalse(result)
    
    @patch('txttoqti.converter.TxtToQtiConverter.convert_file')
    def test_convert_success(self, mock_txttoqti_convert):
        """Test successful conversion process."""
        mock_txttoqti_convert.return_value = "output.zip"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            block_dir = Path(temp_dir) / "bloque-1"
            block_dir.mkdir(parents=True)
            
            # Create input file
            input_file = block_dir / "preguntas-bloque-1.txt"
            input_file.write_text(self.educational_content)
            
            converter = QtiConverter(script_path=block_dir)
            
            # Mock user input to continue with validation errors (if any)
            with patch('builtins.input', return_value='y'):
                # Capture output
                import io
                import sys
                captured_output = io.StringIO()
                sys.stdout = captured_output
                
                try:
                    result = converter.convert()
                    output = captured_output.getvalue()
                    
                    self.assertTrue(result)
                    self.assertIn("Converting preguntas-bloque-1.txt", output)
                    self.assertIn("QTI file created", output)
                    mock_txttoqti_convert.assert_called_once()
                    
                finally:
                    sys.stdout = sys.__stdout__
    
    @patch('txttoqti.converter.TxtToQtiConverter.convert_file')
    def test_convert_txttoqti_failure(self, mock_txttoqti_convert):
        """Test conversion failure in txttoqti step."""
        mock_txttoqti_convert.side_effect = Exception("txttoqti conversion failed")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            block_dir = Path(temp_dir) / "bloque-1"
            block_dir.mkdir(parents=True)
            
            # Create input file
            input_file = block_dir / "preguntas-bloque-1.txt"
            input_file.write_text(self.educational_content)
            
            converter = QtiConverter(script_path=block_dir)
            
            with patch('builtins.input', return_value='y'):
                with self.assertRaises(ConversionError) as context:
                    converter.convert()
                
                self.assertIn("Conversion failed", str(context.exception))
    
    def test_init_with_string_path(self):
        """Test initialization with string path instead of Path object."""
        with tempfile.TemporaryDirectory() as temp_dir:
            block_dir = Path(temp_dir) / "bloque-4"
            block_dir.mkdir(parents=True)
            
            # Pass string instead of Path
            converter = QtiConverter(script_path=str(block_dir))
            
            self.assertEqual(converter.block_num, "4")
            self.assertEqual(converter.input_filename, "preguntas-bloque-4.txt")
    
    def test_init_with_none_path(self):
        """Test initialization with None path (should use current directory)."""
        # This test would require changing directory, so we'll just verify
        # that the converter initializes without error
        converter = QtiConverter(script_path=None)
        
        # Should initialize without error, though block detection may fail
        self.assertIsNotNone(converter)
        self.assertIsNotNone(converter.file_manager)
        self.assertIsNotNone(converter.format_converter)
        self.assertIsNotNone(converter.block_detector)


if __name__ == '__main__':
    unittest.main()