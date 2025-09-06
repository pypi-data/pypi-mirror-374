# sem-meta

A unified Python package for SEM (Scanning Electron Microscopy) image processing, providing metadata extraction, OCR-based pixel size estimation, and unit conversion utilities.

## Features

- **SEMMetaData**: Extract and format metadata from SEM images
- **SEMOCR**: OCR-based pixel size estimation from scale bars
- **ConvertPS**: Unit conversion and error analysis for pixel size data
- **FullSEMKeys**: Standardized metadata key list for SEM images

## Installation

Install from PyPI:

```bash
pip install sem-meta
```

## Quick Start

```python
from sem_meta import SEMMeta, OCRPS, ConvertScale, FullSEMKeys

# Extract metadata from SEM images
metadata = SEMMeta.extract_metadata("path/to/sem/image.tif")

# Perform OCR on scale bars
pixel_size = OCRPS.extract_pixel_size("path/to/image/with/scalebar.tif")

# Convert units
converted_size = ConvertScale.convert_units(pixel_size, "μm", "nm")

# Access standardized SEM metadata keys
sem_keys = FullSEMKeys
```

## Main Components

### SEMMetaData
Extracts and processes metadata from SEM image files, particularly TIFF files with EXIF data.

### SEMOCR
Uses OCR (Optical Character Recognition) to extract pixel size information from scale bars in SEM images. Includes noise filtering and error correction for common OCR mistakes.

### ConvertPS
Handles unit conversion and normalization for pixel size measurements, supporting various scientific units commonly used in microscopy.

### FullSEMKeys
Provides a standardized set of metadata keys for consistent SEM image annotation and data extraction.

## Dependencies

- numpy: Numerical computations
- PIL (Pillow): Image processing
- pymysql: SQL safety utilities
- termcolor: Terminal output styling
- matplotlib: Visualization
- opencv-python: Advanced image preprocessing
- pytesseract: OCR functionality

## Requirements

- Python 3.6+
- Tesseract OCR engine (for OCR functionality)

### Installing Tesseract

**Ubuntu/Debian:**
```bash
sudo apt install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

## Usage Examples

### Extracting SEM Metadata

```python
from sem_meta import SEMMeta

# Initialize and extract metadata
sem_processor = SEMMeta
metadata = sem_processor.extract_metadata("sample.tif")
print(metadata)
```

### OCR-based Scale Bar Reading

```python
from sem_meta import OCRPS

# Extract pixel size from scale bar
ocr_processor = OCRPS
pixel_size = ocr_processor.extract_pixel_size("sem_image.tif")
print(f"Pixel size: {pixel_size}")
```

### Unit Conversion

```python
from sem_meta import ConvertScale

# Convert between units
converter = ConvertScale
result = converter.convert_units("0.5 μm", "nm")
print(f"Converted: {result}")
```

## File Structure

```
sem-meta/
├── src/
│   └── sem_meta/
│       ├── __init__.py
│       ├── metadata_Module.py    # SEMMetaData class
│       ├── ocr_Module.py         # SEMOCR class
│       ├── convert_Module.py     # ConvertPS class
│       ├── SEMKEYS.py           # FullSEMKeys definitions
│       └── OCR_NOISE_DB.py      # OCR noise patterns database
├── README.md
├── LICENSE
└── pyproject.toml
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

- Ahmed Khalil - Initial work

## Acknowledgments

- Built for the SEM imaging community
- Supports various SEM manufacturers' metadata formats
- Includes extensive OCR noise pattern recognition

## Support

If you encounter any problems or have questions, please open an issue on the GitHub repository.
