# Changelog for txttoqti

## [0.3.0] - 2025-09-02
### Added
- **NEW**: Educational Extension Module - Complete zero-configuration educational workflow
- Auto-detection of course block structure from directory paths and filenames
- Educational format conversion (Q1:/A)/B)/RESPUESTA: format to txttoqti format)
- Smart change detection with MD5 checksums to avoid unnecessary regeneration
- Enhanced educational CLI (`txttoqti-edu`) with interactive troubleshooting mode
- Comprehensive test suite for educational extension (100+ test cases)
- Educational examples and documentation with real-world usage patterns
- Support for various directory naming conventions (bloque-X, block-X, modulo-X, etc.)

### Enhanced
- Added optional `EducationalQtiConverter` export to main package
- Extended CLI with new `txttoqti-edu` entry point for educational workflows
- Improved package structure with educational extension module
- Added comprehensive documentation and examples for institutional usage

### Technical Details
- Added `txttoqti.educational` module with 6 core components
- Implemented `QtiConverter` orchestration class with auto-detection
- Added `BlockDetector` for intelligent course structure recognition  
- Created `FormatConverter` for educational format bridge
- Implemented `FileManager` with smart change detection
- Added educational CLI with enhanced user experience
- Created extensive test coverage for all educational components

## [0.2.0] - 2025-09-02
### Fixed
- **CRITICAL**: Resolved API mismatch bug that made the package completely unusable
- Fixed `AttributeError: 'QTIGenerator' object has no attribute 'generate'` by correcting method calls
- Fixed file extension handling in conversion process (.qti vs .xml)

### Added
- Complete QTI 2.1 XML generation functionality with proper schema compliance
- Comprehensive question validation system for all question types
- Robust error handling and informative error messages
- Backward compatibility methods to maintain API stability
- Extensive test suite covering API fixes and end-to-end scenarios

### Improved
- Enhanced QTI generator with proper XML namespace handling
- Better validation for multiple choice, true/false, and short answer questions
- Improved code coverage and testing infrastructure
- Added development dependencies for better testing experience

### Technical Details
- Replaced skeleton QTI generator implementation with full functionality
- Added proper XML document structure with minidom formatting
- Implemented comprehensive validation logic for all supported question types
- Created extensive test coverage to prevent regression of critical bugs

## [1.0.0] - 2023-10-01
### Added
- Initial release of the txttoqti package.
- Implemented core functionality for converting text-based question banks to QTI packages.
- Added command-line interface for user interaction.
- Included comprehensive validation for question formats.
- Provided utility functions for text cleaning and file validation.
- Created unit tests for core functionalities and integration tests for component interactions.

### Documentation
- Added README.md with project overview, installation instructions, and usage examples.
- Created API documentation in docs/api.md.
- Included examples of usage in docs/examples.md.
- Provided installation instructions in docs/installation.md.