"""
txt-to-qti: Universal converter from text-based question banks to Canvas LMS QTI packages

This library provides a simple, robust way to convert plain text question banks
into QTI (Question & Test Interoperability) packages compatible with Canvas LMS
and other learning management systems.

Main Features:
- Convert plain text to QTI packages
- Canvas LMS compatibility 
- Smart conversion with change detection
- Comprehensive validation
- No external dependencies (uses only Python standard library)

Example Usage:
    >>> import txttoqti
    >>> converter = txttoqti.TxtToQti()
    >>> converter.read_txt("questions.txt")
    >>> converter.save_to_qti("quiz.zip")

Quick conversion:
    >>> txttoqti.quick_convert("questions.txt", "quiz.zip")

Legacy interface (still supported):
    >>> from txttoqti import TxtToQtiConverter
    >>> converter = TxtToQtiConverter()
    >>> qti_file = converter.convert_file("questions.txt")

Author: Juliho C.C.
License: MIT
"""

__version__ = "0.5.0"
__author__ = "Juliho C.C."
__license__ = "MIT"

# Main API exports - New intuitive interface (recommended)
from .txttoqti import TxtToQti, quick_convert

# Legacy API exports (still supported)
from .converter import TxtToQtiConverter
from .parser import QuestionParser
from .qti_generator import QTIGenerator
from .validator import QuestionValidator
from .smart_converter import SmartConverter

# Model exports
from .models import Question, QuestionType, Choice, Assessment

# Exception exports
from .exceptions import (
    TxtToQtiError,
    ParseError,
    ValidationError,
    ConversionError,
    FileError,
)

# Utility exports
from .utils import (
    clean_text,
    validate_file,
    get_file_timestamp,
)

__all__ = [
    # Main interface (recommended)
    "TxtToQti",
    "quick_convert",
    
    # Legacy classes (still supported)
    "TxtToQtiConverter",
    "QuestionParser", 
    "QTIGenerator",
    "QuestionValidator",
    "SmartConverter",
    
    # Models
    "Question",
    "QuestionType",
    "Choice",
    "Assessment",
    
    # Exceptions
    "TxtToQtiError",
    "ParseError",
    "ValidationError", 
    "ConversionError",
    "FileError",
    
    # Utilities
    "clean_text",
    "validate_file",
    "get_file_timestamp",
    
    # Package info
    "__version__",
    "__author__",
    "__license__",
]

# Educational extension exports (optional import)
try:
    from .educational import QtiConverter as EducationalQtiConverter
    __all__.extend(["EducationalQtiConverter"])
except ImportError:
    # Educational extension not available
    pass

# Module-level convenience function
def convert_txt_to_qti(txt_file, output_file=None, **kwargs):
    """
    Convenience function to convert a text file to QTI package.
    
    Args:
        txt_file (str): Path to input text file
        output_file (str, optional): Path for output QTI ZIP file
        **kwargs: Additional options for conversion
        
    Returns:
        str: Path to created QTI ZIP file
        
    Example:
        >>> qti_file = convert_txt_to_qti("my_questions.txt")
    """
    converter = TxtToQtiConverter()
    return converter.convert_file(txt_file, output_file, **kwargs)