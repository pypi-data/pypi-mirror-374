"""
Educational Utilities

Provides file management and auto-detection utilities for educational workflows.

Author: Juliho C.C.
License: MIT
"""

import hashlib
import re
from pathlib import Path
from typing import Optional


class FileManager:
    """
    Manages file operations for educational QTI conversion.
    
    Provides utilities for counting questions, detecting file changes,
    and managing checksum files for change detection.
    """
    
    @staticmethod
    def count_questions(file_path: str) -> int:
        """
        Count the number of questions in a text file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Number of questions found
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count questions using regex patterns for both formats
            educational_pattern = re.compile(r'^\s*Q\d+:', re.MULTILINE)
            txttoqti_pattern = re.compile(r'^\s*\d+\.', re.MULTILINE)
            
            educational_count = len(educational_pattern.findall(content))
            txttoqti_count = len(txttoqti_pattern.findall(content))
            
            # Return the higher count (assuming one format is used consistently)
            return max(educational_count, txttoqti_count)
            
        except Exception as e:
            raise ValueError(f"Error counting questions: {e}")
    
    @staticmethod
    def file_changed(file_path: str, checksum_dir: Optional[str] = None) -> bool:
        """
        Check if a file has changed since last checksum was calculated.
        
        Args:
            file_path: Path to the file to check
            checksum_dir: Directory to store checksum files (defaults to same as file)
            
        Returns:
            True if file has changed or no previous checksum exists
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Determine checksum file location
        if checksum_dir:
            checksum_path = Path(checksum_dir) / f"{path.name}.checksum"
        else:
            checksum_path = path.parent / f"{path.name}.checksum"
        
        # Calculate current file checksum
        current_checksum = FileManager._calculate_md5(path)
        
        # Check if checksum file exists and compare
        if checksum_path.exists():
            try:
                with open(checksum_path, 'r', encoding='utf-8') as f:
                    stored_checksum = f.read().strip()
                
                if current_checksum == stored_checksum:
                    return False  # File hasn't changed
                    
            except Exception:
                pass  # If we can't read checksum file, assume changed
        
        # Update checksum file
        try:
            checksum_path.parent.mkdir(parents=True, exist_ok=True)
            with open(checksum_path, 'w', encoding='utf-8') as f:
                f.write(current_checksum)
        except Exception:
            pass  # If we can't write checksum, continue anyway
        
        return True  # File has changed or no previous checksum
    
    @staticmethod
    def _calculate_md5(file_path: Path) -> str:
        """Calculate MD5 checksum of a file."""
        hash_md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()


