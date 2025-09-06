# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of sem-meta package
- SEMMetaData class for metadata extraction from SEM images
- SEMOCR class for OCR-based pixel size estimation
- ConvertPS class for unit conversion and error analysis
- FullSEMKeys standardized metadata key definitions
- OCR noise pattern database for improved accuracy
- Support for TIFF images with EXIF metadata
- Comprehensive documentation and examples

### Features
- Metadata extraction from SEM TIFF files
- OCR processing of scale bars in SEM images
- Unit conversion utilities for microscopy measurements
- Noise filtering for OCR results
- Standardized SEM metadata keys
- SQL-safe string escaping
- Colored terminal output for better user experience

### Dependencies
- numpy for numerical computations
- Pillow for image processing
- PyMySQL for SQL safety utilities
- termcolor for terminal styling
- matplotlib for visualization
- opencv-python for image preprocessing
- pytesseract for OCR functionality

## [0.1.0] - 2025-09-05

### Added
- Initial package structure
- Core functionality for SEM image processing
- MIT License
- Basic documentation
