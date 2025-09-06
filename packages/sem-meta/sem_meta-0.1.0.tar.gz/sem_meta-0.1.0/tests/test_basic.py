"""
Basic tests for sem-meta package imports and initialization.
"""
import pytest


def test_import_main_package():
    """Test that the main package can be imported."""
    import sem_meta
    assert sem_meta is not None


def test_import_main_components():
    """Test that main components can be imported."""
    from sem_meta import SEMMeta, OCRPS, ConvertScale, FullSEMKeys
    
    assert SEMMeta is not None
    assert OCRPS is not None
    assert ConvertScale is not None
    assert FullSEMKeys is not None


def test_module_imports():
    """Test that individual modules can be imported."""
    from sem_meta.metadata_Module import SEMMetaData
    from sem_meta.ocr_Module import SEMOCR
    from sem_meta.convert_Module import ConvertPS
    
    assert SEMMetaData is not None
    assert SEMOCR is not None
    assert ConvertPS is not None


def test_convert_module_basic():
    """Test basic functionality of ConvertPS class."""
    from sem_meta import ConvertScale
    
    # Test that we can create an instance
    converter = ConvertScale
    assert converter is not None
    
    # Test GetFloat method if it exists
    if hasattr(converter, 'GetFloat'):
        # This should extract the float from a string
        result = converter.GetFloat("Pixel size = 0.428 µm")
        assert isinstance(result, float)
        assert result == 0.428


def test_sem_keys_available():
    """Test that SEM keys are available."""
    from sem_meta import FullSEMKeys
    
    # FullSEMKeys should be importable
    assert FullSEMKeys is not None


if __name__ == "__main__":
    pytest.main([__file__])
