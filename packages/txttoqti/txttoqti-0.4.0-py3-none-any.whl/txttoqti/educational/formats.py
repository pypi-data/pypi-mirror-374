"""
Educational Format Converter

Handles conversion between educational question formats and txttoqti-compatible format.
Supports the common educational format: Q1: A) B) C) D) RESPUESTA: X

Author: Juliho C.C.
License: MIT
"""

import re
from typing import List, Tuple
from pathlib import Path


class FormatConverter:
    """
    Converts between educational and txttoqti formats.
    
    Educational format:
        Q1: What is the result of type(42) in Python?
        A) <class 'float'>
        B) <class 'int'>
        C) <class 'str'>
        D) <class 'number'>
        RESPUESTA: B
    
    txttoqti format:
        1. What is the result of type(42) in Python?
        a) <class 'float'>
        b) <class 'int'>
        c) <class 'str'>
        d) <class 'number'>
        Respuesta correcta: b
    """
    
    # Conversion methods removed - parser now handles educational format directly
    
    @staticmethod
    def validate_question_format(content: str) -> Tuple[bool, List[str]]:
        """
        Validate the educational question format.
        
        Args:
            content: Text content to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        lines = content.strip().split('\n')
        
        question_pattern = re.compile(r'^Q(\d+):\s*(.+)$')
        choice_pattern = re.compile(r'^([ABCD])\)\s*(.+)$')
        answer_pattern = re.compile(r'^RESPUESTA:\s*([A-Z])$')
        
        current_question = None
        choices_for_question = []
        question_numbers = []
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            # Check question format
            question_match = question_pattern.match(line)
            if question_match:
                question_num = int(question_match.group(1))
                
                # Check for duplicate question numbers
                if question_num in question_numbers:
                    errors.append(f"Line {line_num}: Duplicate question number Q{question_num}")
                else:
                    question_numbers.append(question_num)
                
                # Reset for new question
                current_question = question_num
                choices_for_question = []
                continue
            
            # Check choice format
            choice_match = choice_pattern.match(line)
            if choice_match:
                choice_letter = choice_match.group(1)
                
                if current_question is None:
                    errors.append(f"Line {line_num}: Choice found without preceding question")
                elif choice_letter in choices_for_question:
                    errors.append(f"Line {line_num}: Duplicate choice {choice_letter} for question Q{current_question}")
                else:
                    choices_for_question.append(choice_letter)
                continue
            
            # Check answer format
            answer_match = answer_pattern.match(line)
            if answer_match:
                answer_letter = answer_match.group(1)
                
                if current_question is None:
                    errors.append(f"Line {line_num}: Answer found without preceding question")
                elif answer_letter not in choices_for_question:
                    errors.append(f"Line {line_num}: Answer {answer_letter} does not match any choice for question Q{current_question}")
                continue
            
            # If no pattern matches, it might be an error
            if line:  # Non-empty line that doesn't match any pattern
                errors.append(f"Line {line_num}: Unrecognized format: '{line}'")
        
        # Check for sequential question numbering
        if question_numbers:
            expected_sequence = list(range(1, len(question_numbers) + 1))
            if sorted(question_numbers) != expected_sequence:
                errors.append("Question numbers are not sequential starting from 1")
        
        is_valid = len(errors) == 0
        return is_valid, errors