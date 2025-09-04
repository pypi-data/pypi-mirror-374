"""
Educational Extension for txttoqti

This module provides a higher-level, auto-detecting interface specifically designed 
for academic institutions and course management workflows.

Main Features:
- Zero-configuration auto-detection of course structure
- Educational format conversion (Q1:/A)/B)/RESPUESTA: format)
- Smart change detection and batch processing
- Enhanced educational CLI with progress reporting

Example Usage:
    >>> from txttoqti.educational import QtiConverter
    >>> converter = QtiConverter()  # Auto-detects everything
    >>> converter.show_status()     # Shows current block info
    >>> converter.convert()         # Handles format conversion + QTI generation
    
Author: Juliho C.C.
License: MIT
"""

from .converter import QtiConverter
from .detector import BlockDetector
from .formats import FormatConverter
from .utils import FileManager

__all__ = [
    "QtiConverter",
    "BlockDetector", 
    "FormatConverter",
    "FileManager",
]