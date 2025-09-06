"""
txttoqti.py: Main user-friendly interface for txttoqti package.

This module provides an intuitive interface where users can create a txttoqti object
and use methods like .read_txt() and .save_to_qti() for a more natural workflow.

Example Usage:
    >>> import txttoqti
    >>> converter = txttoqti.TxtToQti()
    >>> converter.read_txt("questions.txt")
    >>> converter.save_to_qti("output.zip")
"""

from pathlib import Path
from typing import Optional, List, Union, Any
from .converter import TxtToQtiConverter
from .parser import QuestionParser
from .qti_generator import QTIGenerator
from .validator import QuestionValidator
from .models import Question
from .exceptions import TxtToQtiError, FileError, ParseError, ValidationError
from .logging_config import get_logger


class TxtToQti:
    """
    Main user interface for txttoqti conversion.
    
    This class provides an intuitive workflow where you:
    1. Create a TxtToQti object
    2. Load content using read_txt() or read_string()
    3. Save to QTI using save_to_qti()
    
    Example:
        >>> converter = TxtToQti()
        >>> converter.read_txt("my_questions.txt")
        >>> converter.save_to_qti("quiz.zip")
    """
    
    def __init__(self) -> None:
        """Initialize the TxtToQti converter."""
        self.logger = get_logger(__name__)
        self.parser = QuestionParser()
        self.qti_generator = QTIGenerator()
        self.validator = QuestionValidator()
        
        # Internal state
        self._questions: List[Question] = []
        self._source_content: str = ""
        self._source_file: Optional[str] = None
        
        self.logger.info("TxtToQti initialized")
    
    def read_txt(self, file_path: Union[str, Path]) -> 'TxtToQti':
        """
        Read questions from a text file.
        
        Args:
            file_path: Path to the text file containing questions
            
        Returns:
            Self for method chaining
            
        Raises:
            FileError: If file cannot be read
            ParseError: If questions cannot be parsed
            ValidationError: If questions are invalid
        """
        try:
            file_path = Path(file_path)
            self._source_file = str(file_path)
            
            if not file_path.exists():
                raise FileError(f"File not found: {file_path}", str(file_path), "read")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            return self.read_string(content)
            
        except (FileError, ParseError, ValidationError):
            raise
        except Exception as e:
            raise FileError(f"Cannot read file {file_path}: {e}", str(file_path), "read")
    
    def read_string(self, content: str) -> 'TxtToQti':
        """
        Read questions from a string.
        
        Args:
            content: String containing questions in txttoqti format
            
        Returns:
            Self for method chaining
            
        Raises:
            ParseError: If questions cannot be parsed
            ValidationError: If questions are invalid
        """
        try:
            self._source_content = content.strip()
            
            if not self._source_content:
                self.logger.warning("Empty content provided")
                self._questions = []
                return self
            
            # Parse questions
            self._questions = self.parser.parse(self._source_content)
            
            # Validate all questions
            for question in self._questions:
                self.validator.validate(question)
            
            self.logger.info(f"Successfully parsed {len(self._questions)} questions")
            return self
            
        except Exception as e:
            if isinstance(e, (ParseError, ValidationError)):
                raise
            raise ParseError(f"Failed to parse content: {e}")
    
    def save_to_qti(self, output_path: Union[str, Path, None] = None) -> str:
        """
        Save the loaded questions to a QTI ZIP file.
        
        Args:
            output_path: Path for the output QTI file. If None, generates a name.
            
        Returns:
            Path to the created QTI file
            
        Raises:
            TxtToQtiError: If no questions are loaded or save fails
        """
        if not self._questions:
            raise TxtToQtiError("No questions loaded. Use read_txt() or read_string() first.")
        
        try:
            # Generate output path if not provided
            if output_path is None:
                if self._source_file:
                    output_path = Path(self._source_file).with_suffix('.zip')
                else:
                    output_path = "assessment.zip"
            
            output_path = Path(output_path)
            
            # Generate QTI XML
            qti_xml = self.qti_generator.generate_qti_xml(self._questions)
            
            # Use the existing converter to create the package
            converter = TxtToQtiConverter()
            result = converter.convert(qti_xml, str(output_path))
            
            self.logger.info(f"Successfully saved QTI file: {result}")
            return result
            
        except Exception as e:
            raise TxtToQtiError(f"Failed to save QTI file: {e}")
    
    def get_questions(self) -> List[Question]:
        """
        Get the currently loaded questions.
        
        Returns:
            List of parsed Question objects
        """
        return self._questions.copy()
    
    def get_question_count(self) -> int:
        """
        Get the number of loaded questions.
        
        Returns:
            Number of questions
        """
        return len(self._questions)
    
    def is_empty(self) -> bool:
        """
        Check if any questions are loaded.
        
        Returns:
            True if no questions are loaded
        """
        return len(self._questions) == 0
    
    def clear(self) -> 'TxtToQti':
        """
        Clear all loaded questions and reset state.
        
        Returns:
            Self for method chaining
        """
        self._questions = []
        self._source_content = ""
        self._source_file = None
        self.logger.info("Cleared all questions")
        return self
    
    def validate(self) -> bool:
        """
        Validate all loaded questions.
        
        Returns:
            True if all questions are valid
            
        Raises:
            ValidationError: If any question is invalid
        """
        if not self._questions:
            raise TxtToQtiError("No questions loaded. Use read_txt() or read_string() first.")
        
        for i, question in enumerate(self._questions, 1):
            try:
                self.validator.validate(question)
            except ValidationError as e:
                raise ValidationError(f"Question {i} is invalid: {e}")
        
        self.logger.info(f"All {len(self._questions)} questions are valid")
        return True
    
    def preview(self, max_questions: int = 5) -> str:
        """
        Get a preview of the loaded questions.
        
        Args:
            max_questions: Maximum number of questions to include in preview
            
        Returns:
            String representation of questions
        """
        if not self._questions:
            return "No questions loaded."
        
        preview_lines = [f"Loaded {len(self._questions)} questions:\n"]
        
        for i, question in enumerate(self._questions[:max_questions], 1):
            preview_lines.append(f"Q{i}: {question.text}")
            for choice in question.choices:
                marker = "✓" if choice.is_correct else " "
                preview_lines.append(f"  [{marker}] {choice.id}) {choice.text}")
            preview_lines.append("")
        
        if len(self._questions) > max_questions:
            preview_lines.append(f"... and {len(self._questions) - max_questions} more questions")
        
        return "\n".join(preview_lines)
    
    def __repr__(self) -> str:
        """String representation of the TxtToQti object."""
        count = len(self._questions)
        source = self._source_file or "string"
        return f"TxtToQti(questions={count}, source={source})"
    
    def __len__(self) -> int:
        """Return the number of loaded questions."""
        return len(self._questions)
    
    def __bool__(self) -> bool:
        """Return True if questions are loaded."""
        return len(self._questions) > 0


# Convenience function for quick conversion
def quick_convert(input_file: Union[str, Path], output_file: Union[str, Path, None] = None) -> str:
    """
    Quick conversion function for single-line usage.
    
    Args:
        input_file: Path to input text file
        output_file: Path to output QTI file (optional)
        
    Returns:
        Path to created QTI file
        
    Example:
        >>> txttoqti.quick_convert("questions.txt", "quiz.zip")
    """
    converter = TxtToQti()
    converter.read_txt(input_file)
    return converter.save_to_qti(output_file)