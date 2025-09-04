"""
validator.py: Question validation functionality for txttoqti package.

Validates question objects to ensure they meet the requirements
for QTI conversion.
"""

from typing import List, Tuple
from .models import Question, QuestionType
from .exceptions import ValidationError
from .logging_config import get_logger


class QuestionValidator:
    """
    QuestionValidator: A class to validate the structure and content of questions.

    This class ensures that questions meet the required format and contain
    all necessary components before conversion to QTI packages.
    """

    def __init__(self):
        self.logger = get_logger(__name__)

    def validate(self, question: Question) -> bool:
        """
        Validate a single question.

        Args:
            question (Question): The question object to validate.

        Returns:
            bool: True if the question is valid.
            
        Raises:
            ValidationError: If the question is invalid.
        """
        try:
            # Check if question has text
            if not question.text or not question.text.strip():
                raise ValidationError(f"Question {question.id} has empty text")
            
            # Check question type specific validations
            if question.question_type == QuestionType.MULTIPLE_CHOICE:
                self._validate_multiple_choice(question)
            elif question.question_type == QuestionType.TRUE_FALSE:
                self._validate_true_false(question)
            elif question.question_type == QuestionType.SHORT_ANSWER:
                self._validate_short_answer(question)
            
            # Check points
            if question.points < 0:
                raise ValidationError(f"Question {question.id} has negative points: {question.points}")
            
            self.logger.debug(f"Question {question.id} validated successfully")
            return True
            
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Validation failed for question {question.id}: {e}")

    def _validate_multiple_choice(self, question: Question) -> None:
        """Validate multiple choice question."""
        if not question.choices:
            raise ValidationError(f"Multiple choice question {question.id} has no choices")
        
        if len(question.choices) < 2:
            raise ValidationError(f"Multiple choice question {question.id} must have at least 2 choices")
        
        correct_count = sum(1 for choice in question.choices if choice.is_correct)
        if correct_count == 0:
            raise ValidationError(f"Multiple choice question {question.id} has no correct answer")
        
        if correct_count > 1:
            raise ValidationError(f"Multiple choice question {question.id} has multiple correct answers")
            
        # Check all choices have text
        for i, choice in enumerate(question.choices):
            if not choice.text or not choice.text.strip():
                raise ValidationError(f"Choice {i+1} in question {question.id} has empty text")

    def _validate_true_false(self, question: Question) -> None:
        """Validate true/false question."""
        if not question.choices:
            raise ValidationError(f"True/false question {question.id} has no choices")
            
        if len(question.choices) != 2:
            raise ValidationError(f"True/false question {question.id} must have exactly 2 choices")
        
        correct_count = sum(1 for choice in question.choices if choice.is_correct)
        if correct_count != 1:
            raise ValidationError(f"True/false question {question.id} must have exactly one correct answer")

    def _validate_short_answer(self, question: Question) -> None:
        """Validate short answer question."""
        # Short answer questions don't need choices, but if they have a correct answer, it should be set
        if question.choices:
            self.logger.warning(f"Short answer question {question.id} has choices, which will be ignored")

    def validate_questions(self, questions: List[Question]) -> List[Tuple[Question, bool]]:
        """
        Validate a list of questions.

        Args:
            questions (List[Question]): A list of question objects to validate.

        Returns:
            List[Tuple[Question, bool]]: A list of tuples containing the question and its validity status.
        """
        results = []
        for question in questions:
            try:
                is_valid = self.validate(question)
                results.append((question, is_valid))
            except ValidationError as e:
                self.logger.error(f"Validation failed for question {question.id}: {e}")
                results.append((question, False))
        return results