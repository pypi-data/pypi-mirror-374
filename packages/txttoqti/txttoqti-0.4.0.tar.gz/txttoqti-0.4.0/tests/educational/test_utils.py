"""
Tests for educational utilities (FileManager).

Author: Juliho C.C.
License: MIT
"""

import unittest
import tempfile
import hashlib
from pathlib import Path

from txttoqti.educational.utils import FileManager


class TestFileManager(unittest.TestCase):
    """Test cases for FileManager class."""
    
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
        
        self.txttoqti_content = """1. What is Python?
a) A snake
b) A programming language
c) A movie
d) A book
Respuesta correcta: b

2. What is 2 + 2?
a) 3
b) 4
c) 5
d) 6
Respuesta correcta: b"""
    
    def test_count_questions_educational_format(self):
        """Test question counting in educational format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.educational_content)
            temp_path = f.name
        
        try:
            count = FileManager.count_questions(temp_path)
            self.assertEqual(count, 2)
        finally:
            Path(temp_path).unlink()
    
    def test_count_questions_txttoqti_format(self):
        """Test question counting in txttoqti format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.txttoqti_content)
            temp_path = f.name
        
        try:
            count = FileManager.count_questions(temp_path)
            self.assertEqual(count, 2)
        finally:
            Path(temp_path).unlink()
    
    def test_count_questions_nonexistent_file(self):
        """Test question counting with non-existent file."""
        with self.assertRaises(FileNotFoundError):
            FileManager.count_questions("nonexistent.txt")
    
    def test_count_questions_empty_file(self):
        """Test question counting with empty file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("")
            temp_path = f.name
        
        try:
            count = FileManager.count_questions(temp_path)
            self.assertEqual(count, 0)
        finally:
            Path(temp_path).unlink()
    
    def test_file_changed_new_file(self):
        """Test file change detection for new file (no previous checksum)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.educational_content)
            temp_path = f.name
        
        try:
            # First check should return True (no previous checksum)
            changed = FileManager.file_changed(temp_path)
            self.assertTrue(changed)
        finally:
            Path(temp_path).unlink()
            # Clean up checksum file if it was created
            checksum_path = Path(temp_path + ".checksum")
            if checksum_path.exists():
                checksum_path.unlink()
    
    def test_file_changed_unchanged_file(self):
        """Test file change detection for unchanged file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.educational_content)
            temp_path = f.name
        
        try:
            # First check creates checksum
            FileManager.file_changed(temp_path)
            
            # Second check should return False (file unchanged)
            changed = FileManager.file_changed(temp_path)
            self.assertFalse(changed)
        finally:
            Path(temp_path).unlink()
            # Clean up checksum file
            checksum_path = Path(temp_path + ".checksum")
            if checksum_path.exists():
                checksum_path.unlink()
    
    def test_file_changed_modified_file(self):
        """Test file change detection for modified file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.educational_content)
            temp_path = f.name
        
        try:
            # First check creates checksum
            FileManager.file_changed(temp_path)
            
            # Modify the file
            with open(temp_path, 'w') as f:
                f.write(self.educational_content + "\n\nQ3: New question?")
            
            # Second check should return True (file changed)
            changed = FileManager.file_changed(temp_path)
            self.assertTrue(changed)
        finally:
            Path(temp_path).unlink()
            # Clean up checksum file
            checksum_path = Path(temp_path + ".checksum")
            if checksum_path.exists():
                checksum_path.unlink()
    
    def test_file_changed_custom_checksum_dir(self):
        """Test file change detection with custom checksum directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            
            # Create test file
            test_file = temp_dir_path / "test.txt"
            with open(test_file, 'w') as f:
                f.write(self.educational_content)
            
            # Create checksum directory
            checksum_dir = temp_dir_path / "checksums"
            checksum_dir.mkdir()
            
            # Test with custom checksum directory
            changed = FileManager.file_changed(str(test_file), str(checksum_dir))
            self.assertTrue(changed)  # First time should be True
            
            # Check that checksum file was created in custom directory
            checksum_file = checksum_dir / "test.txt.checksum"
            self.assertTrue(checksum_file.exists())
            
            # Second check should be False
            changed = FileManager.file_changed(str(test_file), str(checksum_dir))
            self.assertFalse(changed)
    
    def test_file_changed_nonexistent_file(self):
        """Test file change detection with non-existent file."""
        with self.assertRaises(FileNotFoundError):
            FileManager.file_changed("nonexistent.txt")
    
    def test_calculate_md5(self):
        """Test MD5 calculation for file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.educational_content)
            temp_path = f.name
        
        try:
            path_obj = Path(temp_path)
            calculated_md5 = FileManager._calculate_md5(path_obj)
            
            # Verify it's a valid MD5 hash (32 hex characters)
            self.assertEqual(len(calculated_md5), 32)
            self.assertTrue(all(c in '0123456789abcdef' for c in calculated_md5))
            
            # Calculate expected MD5
            expected_md5 = hashlib.md5(self.educational_content.encode('utf-8')).hexdigest()
            self.assertEqual(calculated_md5, expected_md5)
            
        finally:
            Path(temp_path).unlink()
    
    def test_mixed_format_question_counting(self):
        """Test question counting with mixed formats (should take the higher count)."""
        mixed_content = """1. Regular txttoqti question?
a) Option 1
b) Option 2

Q2: Educational format question?
A) Option 1
B) Option 2
RESPUESTA: A

3. Another txttoqti question?
a) Option 1
b) Option 2"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(mixed_content)
            temp_path = f.name
        
        try:
            count = FileManager.count_questions(temp_path)
            # Should detect 2 txttoqti questions and 1 educational question, return max (2)
            self.assertEqual(count, 2)
        finally:
            Path(temp_path).unlink()


if __name__ == '__main__':
    unittest.main()