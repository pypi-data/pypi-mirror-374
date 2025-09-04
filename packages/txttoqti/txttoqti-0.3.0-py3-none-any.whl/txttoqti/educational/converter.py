"""
Educational QTI Converter

Main orchestration class for educational QTI conversion workflow.
Provides zero-configuration auto-detection and enhanced educational features.

Author: Juliho C.C.
License: MIT
"""

import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

from ..converter import TxtToQtiConverter
from ..exceptions import ConversionError, FileError, ValidationError
from ..logging_config import get_logger

from .detector import BlockDetector
from .formats import FormatConverter
from .utils import FileManager


class QtiConverter:
    """
    Educational QTI converter with auto-detection and format conversion.
    
    This class provides a higher-level interface for educational institutions,
    automatically detecting course structure and handling format conversion.
    
    Example:
        >>> converter = QtiConverter()  # Auto-detects everything
        >>> converter.show_status()     # Shows current block info  
        >>> converter.convert()         # Handles format conversion + QTI generation
    """
    
    def __init__(self, script_path: Optional[Path] = None) -> None:
        """
        Initialize the educational converter.
        
        Args:
            script_path: Path to script file (optional, uses cwd if None)
        """
        self.logger = get_logger(__name__)
        self.script_path = script_path or Path.cwd()
        
        # Initialize core components
        self.file_manager = FileManager()
        self.format_converter = FormatConverter()
        self.block_detector = BlockDetector()
        self.txttoqti_converter = TxtToQtiConverter()
        
        # Auto-detect block information
        try:
            self.block_num, self.input_filename, self.output_filename = \
                self.block_detector.detect_block_info(self.script_path)
            self.block_description = self.block_detector.get_block_description(self.block_num)
        except ValueError as e:
            self.logger.error(f"Auto-detection failed: {e}")
            self.block_num = None
            self.input_filename = None
            self.output_filename = None
            self.block_description = None
        
        self.logger.info("Educational QTI Converter initialized")
    
    def show_status(self) -> None:
        """Display current conversion status and file information."""
        if not self.block_num:
            print("❌ Block detection failed")
            print("   Ensure you're in a directory with block structure (e.g., 'bloque-1')")
            print("   or have files named like 'preguntas-bloque-1.txt'")
            return
        
        print(f"📚 Block {self.block_num}: {self.block_description}")
        print(f"📁 Working directory: {self.script_path}")
        print(f"📄 Input file: {self.input_filename}")
        print(f"📦 Output file: {self.output_filename}")
        
        # Check if input file exists
        input_path = self.script_path / self.input_filename
        if input_path.exists():
            try:
                question_count = self.file_manager.count_questions(str(input_path))
                print(f"❓ Questions found: {question_count}")
                
                # Check if file has changed
                has_changed = self.file_manager.file_changed(str(input_path))
                change_status = "needs regeneration" if has_changed else "up to date"
                print(f"🔄 Status: {change_status}")
                
            except Exception as e:
                print(f"⚠️ Error reading file: {e}")
        else:
            print(f"❌ Input file not found: {input_path}")
        
        # Check if output file exists
        output_path = self.script_path / self.output_filename
        if output_path.exists():
            print(f"✅ QTI file exists: {output_path}")
        else:
            print(f"🔄 QTI file will be created: {output_path}")
    
    def convert(self, force: bool = False) -> bool:
        """
        Convert educational questions to QTI format.
        
        Args:
            force: Force regeneration even if file hasn't changed
            
        Returns:
            True if conversion was successful
            
        Raises:
            ConversionError: If conversion fails
            FileError: If required files are missing
        """
        if not self.block_num:
            raise ConversionError("Block detection failed. Cannot proceed with conversion.")
        
        input_path = self.script_path / self.input_filename
        output_path = self.script_path / self.output_filename
        
        # Check if input file exists
        if not input_path.exists():
            raise FileError(f"Input file not found: {input_path}")
        
        self.logger.info(f"Starting conversion for block {self.block_num}")
        
        try:
            # Check if regeneration is needed
            if not force and not self.file_manager.file_changed(str(input_path)):
                print(f"✅ {self.output_filename} is up to date (use --force to regenerate)")
                return True
            
            # Validate format first
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            is_valid, errors = self.format_converter.validate_question_format(content)
            
            if not is_valid:
                print("❌ Question format validation failed:")
                for error in errors[:5]:  # Show first 5 errors
                    print(f"   • {error}")
                if len(errors) > 5:
                    print(f"   ... and {len(errors) - 5} more errors")
                
                user_input = input("Continue anyway? (y/N): ").strip().lower()
                if user_input != 'y':
                    return False
            
            # Convert format to txttoqti compatible
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, 
                                           encoding='utf-8') as temp_file:
                temp_path = temp_file.name
            
            try:
                converted_file = self.format_converter.convert_to_txttoqti_format(
                    str(input_path), temp_path
                )
                
                # Generate QTI using txttoqti
                print(f"🔄 Converting {self.input_filename} to QTI format...")
                qti_output = self.txttoqti_converter.convert_file(
                    converted_file, str(output_path)
                )
                
                print(f"✅ QTI file created: {qti_output}")
                self.logger.info(f"Conversion completed successfully: {qti_output}")
                return True
                
            finally:
                # Clean up temporary file
                temp_file_path = Path(temp_path)
                if temp_file_path.exists():
                    temp_file_path.unlink()
        
        except Exception as e:
            error_msg = f"Conversion failed: {e}"
            self.logger.error(error_msg)
            print(f"❌ {error_msg}")
            raise ConversionError(error_msg) from e
    
    def get_file_info(self) -> Dict[str, Any]:
        """
        Get comprehensive file information for the current block.
        
        Returns:
            Dictionary with file information and status
        """
        if not self.block_num:
            return {"error": "Block detection failed"}
        
        input_path = self.script_path / self.input_filename
        output_path = self.script_path / self.output_filename
        
        info = {
            "block_number": self.block_num,
            "block_description": self.block_description,
            "working_directory": str(self.script_path),
            "input_file": self.input_filename,
            "output_file": self.output_filename,
            "input_exists": input_path.exists(),
            "output_exists": output_path.exists(),
        }
        
        if input_path.exists():
            try:
                info["question_count"] = self.file_manager.count_questions(str(input_path))
                info["needs_regeneration"] = self.file_manager.file_changed(str(input_path))
            except Exception as e:
                info["file_error"] = str(e)
        
        return info