"""
sem_meta: Unified interface for SEM image processing.

Exposes:
- SEMMeta: Metadata extraction and formatting
- OCRPS: OCR-based pixel size estimation
- ConvertScale: Unit conversion and error analysis
- FullSEMKeys: Standardized metadata key list
"""

# Explicit imports from internal modules
from .metadata_Module import SEMMetaData
from .ocr_Module import SEMOCR
from .convert_Module import ConvertPS
from .SEMKEYS import FullSEMKeys
from .OCR_NOISE_DB import (
    noisy_cases_for_1μπ, noisy_cases_for_2μπ,
    noisy_cases_for_10μ, prefixes_for_10μ,
    noisy_cases_for_20μπ, noisy_cases_for_100μπ,
    noisy_cases_for_1mm, known_corrupted_substrings,
    known_noisy_prefixes)



# Instantiate main interfaces
SEMMeta = SEMMetaData()
OCRPS = SEMOCR()
ConvertScale = ConvertPS()
