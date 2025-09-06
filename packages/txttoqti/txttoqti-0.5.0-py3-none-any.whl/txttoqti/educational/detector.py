"""
Block Detection Utilities

Auto-detection of course structure from directory paths and filenames.
Separated from utils.py for cleaner organization.

Author: Juliho C.C.
License: MIT
"""

import re
from pathlib import Path
from typing import Optional, Tuple


class BlockDetector:
    """
    Auto-detects course structure from directory paths and filenames.
    
    Supports various naming conventions for educational content organization.
    """
    
    @staticmethod
    def detect_block_info(script_path: Optional[Path] = None) -> Tuple[str, str, str]:
        """
        Detect block information from script path or current directory.
        
        Args:
            script_path: Path to the script file (optional, uses cwd if None)
            
        Returns:
            Tuple of (block_number, input_filename, output_filename)
            
        Raises:
            ValueError: If block number cannot be detected
        """
        if script_path is None:
            script_path = Path.cwd()
        elif isinstance(script_path, str):
            script_path = Path(script_path)
        
        # If script_path is a file, use its parent directory
        if script_path.is_file():
            script_path = script_path.parent
        
        # Try to extract block number from directory path
        block_num = BlockDetector._extract_block_from_path(script_path)
        
        if block_num is None:
            # Try to extract from existing files in directory
            block_num = BlockDetector._extract_block_from_files(script_path)
        
        if block_num is None:
            raise ValueError(
                f"Could not detect block number from path: {script_path}. "
                f"Expected directory structure like 'block-1', 'module-2', or files like 'questions-block-1.txt'"
            )
        
        # Generate standard filenames based on detected pattern
        if BlockDetector._is_legacy_pattern(script_path):
            # Use Spanish naming for backward compatibility 
            input_filename = f"preguntas-bloque-{block_num}.txt"
            output_filename = f"bloque-{block_num}-canvas.zip"
        else:
            # Use English naming for new projects
            input_filename = f"questions-block-{block_num}.txt"
            output_filename = f"block-{block_num}-canvas.zip"
        
        return block_num, input_filename, output_filename
    
    @staticmethod
    def _extract_block_from_path(path: Path) -> Optional[str]:
        """Extract block number from directory path."""
        path_str = str(path).lower()
        
        # Common patterns for block detection (English preferred, Spanish for compatibility)
        patterns = [
            r'block[-_]?(\d+)',
            r'module[-_]?(\d+)', 
            r'topic[-_]?(\d+)',
            r'unit[-_]?(\d+)',
            r'lesson[-_]?(\d+)',
            r'chapter[-_]?(\d+)',
            # Legacy Spanish patterns for backward compatibility
            r'bloque[-_]?(\d+)',
            r'modulo[-_]?(\d+)',
            r'tema[-_]?(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, path_str)
            if match:
                return match.group(1)
        
        return None
    
    @staticmethod
    def _extract_block_from_files(directory: Path) -> Optional[str]:
        """Extract block number from existing files in directory."""
        if not directory.is_dir():
            return None
        
        # Look for files with block numbers (English preferred, Spanish for compatibility)
        patterns = [
            r'questions[-_]?block[-_]?(\d+)\.txt',
            r'questions[-_]?module[-_]?(\d+)\.txt',
            r'block[-_]?(\d+)[-_]?questions\.txt',
            r'module[-_]?(\d+)[-_]?questions\.txt',
            # Legacy Spanish patterns for backward compatibility  
            r'preguntas[-_]?bloque[-_]?(\d+)\.txt',
            r'bloque[-_]?(\d+)[-_]?preguntas\.txt',
        ]
        
        # Look for both .txt and .TXT files
        txt_files = list(directory.glob('*.txt')) + list(directory.glob('*.TXT'))
        for file_path in txt_files:
            filename = file_path.name.lower()
            for pattern in patterns:
                match = re.search(pattern, filename)
                if match:
                    return match.group(1)
        
        return None
    
    @staticmethod
    def _is_legacy_pattern(path: Path) -> bool:
        """Check if path uses legacy Spanish naming patterns."""
        path_str = str(path).lower()
        
        # Check directory names for Spanish patterns
        legacy_dir_patterns = [r'bloque[-_]?(\d+)', r'modulo[-_]?(\d+)', r'tema[-_]?(\d+)']
        for pattern in legacy_dir_patterns:
            if re.search(pattern, path_str):
                return True
                
        # Check for existing Spanish filename patterns in directory
        if path.is_dir():
            for file_path in path.glob('*.txt'):
                filename = file_path.name.lower()
                if re.search(r'preguntas[-_]?bloque[-_]?\d+\.txt', filename):
                    return True
                    
        return False
    
    @staticmethod
    def get_block_description(block_num: str) -> str:
        """
        Get a human-readable description for a block number.
        
        Args:
            block_num: Block number as string
            
        Returns:
            Descriptive string for the block
        """
        descriptions = {
            "1": "Python fundamentals",
            "2": "Data exploration", 
            "3": "Machine learning",
            "4": "Data visualization",
            "5": "Statistical analysis",
            "6": "Advanced topics",
        }
        
        return descriptions.get(block_num, f"Course block {block_num}")