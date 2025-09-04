"""
Tests for block detection functionality.

Author: Juliho C.C.
License: MIT
"""

import unittest
import tempfile
from pathlib import Path

from txttoqti.educational.detector import BlockDetector


class TestBlockDetector(unittest.TestCase):
    """Test cases for BlockDetector class."""
    
    def test_detect_block_from_directory_bloque(self):
        """Test block detection from 'bloque-X' directory pattern."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create directory structure
            block_dir = Path(temp_dir) / "course" / "bloque-2"
            block_dir.mkdir(parents=True)
            
            block_num, input_file, output_file = BlockDetector.detect_block_info(block_dir)
            
            self.assertEqual(block_num, "2")
            self.assertEqual(input_file, "preguntas-bloque-2.txt")
            self.assertEqual(output_file, "bloque-2-canvas.zip")
    
    def test_detect_block_from_directory_block(self):
        """Test block detection from 'block-X' directory pattern."""
        with tempfile.TemporaryDirectory() as temp_dir:
            block_dir = Path(temp_dir) / "course" / "block-3"
            block_dir.mkdir(parents=True)
            
            block_num, input_file, output_file = BlockDetector.detect_block_info(block_dir)
            
            self.assertEqual(block_num, "3")
            self.assertEqual(input_file, "preguntas-bloque-3.txt")
            self.assertEqual(output_file, "bloque-3-canvas.zip")
    
    def test_detect_block_from_directory_modulo(self):
        """Test block detection from 'modulo-X' directory pattern."""
        with tempfile.TemporaryDirectory() as temp_dir:
            block_dir = Path(temp_dir) / "modulo-1"
            block_dir.mkdir(parents=True)
            
            block_num, input_file, output_file = BlockDetector.detect_block_info(block_dir)
            
            self.assertEqual(block_num, "1")
            self.assertEqual(input_file, "preguntas-bloque-1.txt")
            self.assertEqual(output_file, "bloque-1-canvas.zip")
    
    def test_detect_block_from_files_preguntas_bloque(self):
        """Test block detection from 'preguntas-bloque-X.txt' filename."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            
            # Create test file
            test_file = temp_dir_path / "preguntas-bloque-5.txt"
            test_file.write_text("Q1: Test question?")
            
            block_num, input_file, output_file = BlockDetector.detect_block_info(temp_dir_path)
            
            self.assertEqual(block_num, "5")
            self.assertEqual(input_file, "preguntas-bloque-5.txt")
            self.assertEqual(output_file, "bloque-5-canvas.zip")
    
    def test_detect_block_from_files_questions_block(self):
        """Test block detection from 'questions-block-X.txt' filename."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            
            # Create test file
            test_file = temp_dir_path / "questions-block-4.txt"
            test_file.write_text("1. Test question?")
            
            block_num, input_file, output_file = BlockDetector.detect_block_info(temp_dir_path)
            
            self.assertEqual(block_num, "4")
            self.assertEqual(input_file, "preguntas-bloque-4.txt")
            self.assertEqual(output_file, "bloque-4-canvas.zip")
    
    def test_detect_block_from_script_file_path(self):
        """Test block detection when given a file path instead of directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            block_dir = Path(temp_dir) / "bloque-7"
            block_dir.mkdir(parents=True)
            
            # Create a dummy script file
            script_file = block_dir / "script.py"
            script_file.write_text("# dummy script")
            
            block_num, input_file, output_file = BlockDetector.detect_block_info(script_file)
            
            self.assertEqual(block_num, "7")
            self.assertEqual(input_file, "preguntas-bloque-7.txt")
            self.assertEqual(output_file, "bloque-7-canvas.zip")
    
    def test_detect_block_failure(self):
        """Test block detection failure when no patterns match."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            
            # Create files that don't match patterns
            (temp_dir_path / "random.txt").write_text("content")
            (temp_dir_path / "notes.txt").write_text("content")
            
            with self.assertRaises(ValueError) as context:
                BlockDetector.detect_block_info(temp_dir_path)
            
            self.assertIn("Could not detect block number", str(context.exception))
    
    def test_extract_block_from_path_various_patterns(self):
        """Test extraction of block numbers from various path patterns."""
        test_cases = [
            ("/path/to/bloque-1", "1"),
            ("/path/to/bloque_2", "2"),
            ("/path/to/block-3", "3"),
            ("/path/to/block_4", "4"),
            ("/path/to/modulo-5", "5"),
            ("/path/to/module_6", "6"),
            ("/path/to/tema-7", "7"),
            ("/path/to/topic_8", "8"),
            ("/path/to/BLOQUE-9", "9"),  # Case insensitive
            ("/path/to/Block_10", "10"),  # Case insensitive
        ]
        
        for path_str, expected_num in test_cases:
            with self.subTest(path=path_str):
                result = BlockDetector._extract_block_from_path(Path(path_str))
                self.assertEqual(result, expected_num)
    
    def test_extract_block_from_path_no_match(self):
        """Test extraction when path doesn't contain block pattern."""
        no_match_paths = [
            "/path/to/random",
            "/path/to/course",
            "/path/to/questions",
            "/path/to/bloque",  # Missing number
            "/path/to/block",   # Missing number
        ]
        
        for path_str in no_match_paths:
            with self.subTest(path=path_str):
                result = BlockDetector._extract_block_from_path(Path(path_str))
                self.assertIsNone(result)
    
    def test_extract_block_from_files_various_patterns(self):
        """Test extraction of block numbers from various filename patterns."""
        test_cases = [
            ("preguntas-bloque-1.txt", "1"),
            ("preguntas_bloque_2.txt", "2"),
            ("questions-block-3.txt", "3"),
            ("questions_block_4.txt", "4"),
            ("bloque-5-preguntas.txt", "5"),
            ("bloque_6_preguntas.txt", "6"),
            ("block-7-questions.txt", "7"),
            ("block_8_questions.txt", "8"),
            ("PREGUNTAS-BLOQUE-9.TXT", "9"),  # Case insensitive
        ]
        
        for filename, expected_num in test_cases:
            with self.subTest(filename=filename):
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_dir_path = Path(temp_dir)
                    
                    # Create the test file
                    test_file = temp_dir_path / filename
                    test_file.write_text("content")
                    
                    result = BlockDetector._extract_block_from_files(temp_dir_path)
                    self.assertEqual(result, expected_num)
    
    def test_extract_block_from_files_no_match(self):
        """Test extraction when no files match block pattern."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            
            # Create files that don't match
            (temp_dir_path / "random.txt").write_text("content")
            (temp_dir_path / "notes.txt").write_text("content")
            (temp_dir_path / "preguntas.txt").write_text("content")  # Missing block number
            
            result = BlockDetector._extract_block_from_files(temp_dir_path)
            self.assertIsNone(result)
    
    def test_extract_block_from_files_non_directory(self):
        """Test extraction when path is not a directory."""
        with tempfile.NamedTemporaryFile() as temp_file:
            result = BlockDetector._extract_block_from_files(Path(temp_file.name))
            self.assertIsNone(result)
    
    def test_get_block_description_known_blocks(self):
        """Test getting descriptions for known block numbers."""
        expected_descriptions = {
            "1": "Python fundamentals",
            "2": "Data exploration", 
            "3": "Machine learning",
            "4": "Data visualization",
            "5": "Statistical analysis",
            "6": "Advanced topics",
        }
        
        for block_num, expected_desc in expected_descriptions.items():
            result = BlockDetector.get_block_description(block_num)
            self.assertEqual(result, expected_desc)
    
    def test_get_block_description_unknown_block(self):
        """Test getting descriptions for unknown block numbers."""
        unknown_blocks = ["7", "10", "15", "99"]
        
        for block_num in unknown_blocks:
            result = BlockDetector.get_block_description(block_num)
            self.assertEqual(result, f"Course block {block_num}")
    
    def test_detect_block_info_current_directory(self):
        """Test block detection using current directory (None parameter)."""
        # This test creates a temporary directory and changes to it
        with tempfile.TemporaryDirectory() as temp_dir:
            block_dir = Path(temp_dir) / "bloque-9"
            block_dir.mkdir(parents=True)
            
            # Change to the block directory
            import os
            original_cwd = os.getcwd()
            try:
                os.chdir(block_dir)
                
                # Test with None (should use current directory)
                block_num, input_file, output_file = BlockDetector.detect_block_info(None)
                
                self.assertEqual(block_num, "9")
                self.assertEqual(input_file, "preguntas-bloque-9.txt")
                self.assertEqual(output_file, "bloque-9-canvas.zip")
                
            finally:
                os.chdir(original_cwd)


if __name__ == '__main__':
    unittest.main()