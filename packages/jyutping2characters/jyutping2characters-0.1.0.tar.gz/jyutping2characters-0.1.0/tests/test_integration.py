"""
Integration tests for the main API functions.
"""

import tempfile
import json
import os
from unittest.mock import patch, MagicMock

# We'll test the basic functionality without requiring external dependencies


def test_sample_transcription():
    """Test basic transcription functionality with minimal data."""
    # Create minimal test data
    test_data = [
        ("我", "ngo5", 100.0),
        ("你", "nei5", 90.0),
        ("好", "hou2", 80.0),
        ("你好", "nei5hou2", 200.0),  # Higher frequency than components
    ]
    
    # Test the transcriber directly
    from jyutping2characters.transcriber import JyutpingTranscriber
    transcriber = JyutpingTranscriber(test_data)
    
    # Test individual characters
    assert transcriber.transcribe("ngo5") == "我"
    
    # Test phrase preference
    result = transcriber.transcribe("nei5hou2")
    assert result == "你好"  # Should prefer the phrase over individual chars
    
    print("✅ Basic transcription tests passed")


def test_data_builder_functions():
    """Test data builder utility functions."""
    from jyutping2characters.data_builder import get_cache_dir, get_cached_data_path
    
    # Test cache directory creation
    cache_dir = get_cache_dir()
    assert cache_dir.exists()
    assert cache_dir.is_dir()
    
    # Test cache path generation
    cache_path = get_cached_data_path()
    assert cache_path.parent == cache_dir
    assert cache_path.name == "mapping.json"
    
    print("✅ Data builder utility tests passed")


def test_cli_parser():
    """Test CLI parser functionality."""
    from jyutping2characters.cli import create_parser
    
    parser = create_parser()
    
    # Test transcribe command parsing
    args = parser.parse_args(['transcribe', 'test_input'])
    assert args.command == 'transcribe'
    assert args.text == 'test_input'
    
    # Test other commands
    args = parser.parse_args(['warmup'])
    assert args.command == 'warmup'
    
    args = parser.parse_args(['info'])
    assert args.command == 'info'
    
    args = parser.parse_args(['build-data'])
    assert args.command == 'build-data'
    
    args = parser.parse_args(['clear-cache'])
    assert args.command == 'clear-cache'
    
    print("✅ CLI parser tests passed")


def test_package_import():
    """Test that package imports correctly."""
    try:
        import jyutping2characters
        assert hasattr(jyutping2characters, 'transcribe')
        assert hasattr(jyutping2characters, 'warmup')
        assert hasattr(jyutping2characters, 'clear_cache')
        assert hasattr(jyutping2characters, 'JyutpingTranscriber')
        assert hasattr(jyutping2characters, '__version__')
        print("✅ Package import tests passed")
    except ImportError as e:
        print(f"❌ Package import failed: {e}")
        raise


if __name__ == "__main__":
    """Run basic integration tests."""
    print("🧪 Running integration tests...")
    
    try:
        test_sample_transcription()
        test_data_builder_functions()
        test_cli_parser()
        test_package_import()
        print("\n🎉 All integration tests passed!")
    except Exception as e:
        print(f"\n❌ Integration tests failed: {e}")
        raise
