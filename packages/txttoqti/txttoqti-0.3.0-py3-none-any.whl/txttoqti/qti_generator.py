"""
qti_generator.py: This module defines the QTIGenerator class, which is responsible for generating QTI-compliant XML from parsed questions.

The QTIGenerator class provides methods to create the necessary XML structure required for QTI packages, ensuring that the output is compatible with various learning management systems.

Main Features:
- Generate QTI XML from parsed questions
- Support for different question types
- Validation of generated XML structure

Example Usage:
    >>> from txttoqti.qti_generator import QTIGenerator
    >>> generator = QTIGenerator()
    >>> xml_output = generator.generate_qti_xml(parsed_questions)
    >>> print(xml_output)

"""

import uuid
from typing import List
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

from .models import Question, QuestionType
from .logging_config import get_logger


class QTIGenerator:
    """Generate QTI 2.1 compliant XML from parsed questions."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
    def generate_qti_xml(self, parsed_questions: List[Question]) -> str:
        """
        Generate QTI-compliant XML from parsed questions.

        Args:
            parsed_questions (List[Question]): A list of parsed question objects.

        Returns:
            str: A string containing the QTI XML representation of the questions.
        """
        self.logger.info(f"Generating QTI XML for {len(parsed_questions)} questions")
        
        # Create root assessment element
        assessment = Element('assessmentTest')
        assessment.set('xmlns', 'http://www.imsglobal.org/xsd/imsqti_v2p1')
        assessment.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        assessment.set('xsi:schemaLocation', 
                      'http://www.imsglobal.org/xsd/imsqti_v2p1 '
                      'http://www.imsglobal.org/xsd/qti/qtiv2p1/imsqti_v2p1.xsd')
        assessment.set('identifier', f'assessment_{uuid.uuid4().hex[:8]}')
        assessment.set('title', 'Assessment')
        
        # Add assessment metadata
        self._add_assessment_metadata(assessment)
        
        # Add test parts
        test_part = SubElement(assessment, 'testPart')
        test_part.set('identifier', 'testpart1')
        test_part.set('navigationMode', 'linear')
        test_part.set('submissionMode', 'individual')
        
        # Add assessment sections
        section = SubElement(test_part, 'assessmentSection')
        section.set('identifier', 'section1')
        section.set('title', 'Questions')
        section.set('visible', 'true')
        
        # Add questions to the section
        for question in parsed_questions:
            self._add_assessment_item_ref(section, question)
        
        # Add the actual question items
        for question in parsed_questions:
            question_element = self._create_question_element(question)
            assessment.append(question_element)
        
        # Convert to string and format
        xml_str = tostring(assessment, encoding='unicode')
        dom = minidom.parseString(xml_str)
        formatted_xml = dom.toprettyxml(indent='  ')
        
        # Remove extra blank lines
        lines = [line for line in formatted_xml.split('\n') if line.strip()]
        return '\n'.join(lines)

    def _add_assessment_metadata(self, assessment: Element) -> None:
        """Add metadata to the assessment."""
        # Add timing constraints
        time_limits = SubElement(assessment, 'timeLimits')
        time_limits.set('maxTime', '3600')  # 1 hour default
        
    def _add_assessment_item_ref(self, section: Element, question: Question) -> None:
        """Add an assessment item reference to the section."""
        item_ref = SubElement(section, 'assessmentItemRef')
        item_ref.set('identifier', question.id)
        item_ref.set('href', f'{question.id}.xml')
        
    def _create_question_element(self, question: Question) -> Element:
        """
        Create an XML element for a single question.

        Args:
            question: The parsed question object.

        Returns:
            Element: An XML element representing the question.
        """
        # Create assessment item
        item = Element('assessmentItem')
        item.set('xmlns', 'http://www.imsglobal.org/xsd/imsqti_v2p1')
        item.set('identifier', question.id)
        item.set('title', f'Question {question.id}')
        item.set('adaptive', 'false')
        item.set('timeDependent', 'false')
        
        # Add response declaration
        self._add_response_declaration(item, question)
        
        # Add outcome declaration (for scoring)
        self._add_outcome_declaration(item)
        
        # Add item body (the question content)
        self._add_item_body(item, question)
        
        # Add response processing
        self._add_response_processing(item, question)
        
        return item

    def _add_response_declaration(self, item: Element, question: Question) -> None:
        """Add response declaration for the question."""
        response_decl = SubElement(item, 'responseDeclaration')
        response_decl.set('identifier', 'RESPONSE')
        
        if question.question_type == QuestionType.MULTIPLE_CHOICE:
            response_decl.set('cardinality', 'single')
            response_decl.set('baseType', 'identifier')
            
            # Add correct response
            correct_response = SubElement(response_decl, 'correctResponse')
            for choice in question.choices:
                if choice.is_correct:
                    value = SubElement(correct_response, 'value')
                    value.text = choice.id.split('_')[-1].upper()  # Extract choice letter
                    break
                    
        elif question.question_type == QuestionType.TRUE_FALSE:
            response_decl.set('cardinality', 'single')
            response_decl.set('baseType', 'identifier')
            
            # Add correct response
            correct_response = SubElement(response_decl, 'correctResponse')
            for choice in question.choices:
                if choice.is_correct:
                    value = SubElement(correct_response, 'value')
                    value.text = choice.id.split('_')[-1].upper()
                    break
                    
        elif question.question_type == QuestionType.SHORT_ANSWER:
            response_decl.set('cardinality', 'single')
            response_decl.set('baseType', 'string')
            
            # For short answer, we might have a sample correct response
            if question.correct_answer:
                correct_response = SubElement(response_decl, 'correctResponse')
                value = SubElement(correct_response, 'value')
                value.text = question.correct_answer

    def _add_outcome_declaration(self, item: Element) -> None:
        """Add outcome declaration for scoring."""
        outcome_decl = SubElement(item, 'outcomeDeclaration')
        outcome_decl.set('identifier', 'SCORE')
        outcome_decl.set('cardinality', 'single')
        outcome_decl.set('baseType', 'float')
        
        # Default value
        default_value = SubElement(outcome_decl, 'defaultValue')
        value = SubElement(default_value, 'value')
        value.text = '0'

    def _add_item_body(self, item: Element, question: Question) -> None:
        """Add the item body containing the question text and choices."""
        item_body = SubElement(item, 'itemBody')
        
        # Add question text
        div = SubElement(item_body, 'div')
        div.set('class', 'question-text')
        p = SubElement(div, 'p')
        p.text = question.text
        
        if question.question_type in [QuestionType.MULTIPLE_CHOICE, QuestionType.TRUE_FALSE]:
            # Add choice interaction
            choice_interaction = SubElement(item_body, 'choiceInteraction')
            choice_interaction.set('responseIdentifier', 'RESPONSE')
            choice_interaction.set('shuffle', 'false')
            choice_interaction.set('maxChoices', '1')
            
            # Add choices
            for choice in question.choices:
                choice_element = SubElement(choice_interaction, 'simpleChoice')
                choice_element.set('identifier', choice.id.split('_')[-1].upper())
                choice_element.text = choice.text
                
        elif question.question_type == QuestionType.SHORT_ANSWER:
            # Add text entry interaction
            text_interaction = SubElement(item_body, 'textEntryInteraction')
            text_interaction.set('responseIdentifier', 'RESPONSE')
            text_interaction.set('expectedLength', '50')

    def _add_response_processing(self, item: Element, question: Question) -> None:
        """Add response processing for automatic scoring."""
        response_processing = SubElement(item, 'responseProcessing')
        response_processing.set('template', 
            'http://www.imsglobal.org/question/qti_v2p1/rptemplates/match_correct')

    def _validate_xml_structure(self, xml_string: str) -> bool:
        """
        Validate the generated XML structure.

        Args:
            xml_string (str): The XML string to validate.

        Returns:
            bool: True if the XML structure is valid, False otherwise.
        """
        try:
            minidom.parseString(xml_string)
            return True
        except Exception as e:
            self.logger.error(f"XML validation failed: {e}")
            return False

    def generate(self, questions: List[Question]) -> str:
        """
        Alias for generate_qti_xml for backward compatibility.
        
        Args:
            questions: List of parsed question objects
            
        Returns:
            QTI XML string
        """
        return self.generate_qti_xml(questions)