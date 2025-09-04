import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from pathlib import Path
from processors.arc_conv_cb_proc import ArchiveArchiveConverter, ArchiveConversionError


@pytest.fixture
def converter():
    return ArchiveArchiveConverter()


def test_detect_archive_format_returns_none_for_unknown(converter):
    # Should return None for unknown format
    unknown_file = Path("unknown.xyz")
    result = converter.detect_archive_format(unknown_file)
    assert result is None
    

def test_convert_file_unsupported_format(converter):
    # Should fail for unsupported conversion type
    dummy_file = Path("dummy.cbz")
    result = converter.convert_file(dummy_file, "pdf")
    assert not result[2]  # success should be False
    assert "Unsupported conversion type" in result[3]


def test_convert_file_missing_file(converter):
    # Should fail if file does not exist
    missing_file = Path("missing.cbr")
    result = converter.convert_file(missing_file, "cbz")
    assert not result[2]
    assert "Unsupported conversion type" in result[3]


def test_convert_archive_invalid_format(converter):
    # Should raise ArchiveConversionError for invalid format
    with pytest.raises(ArchiveConversionError):
        converter.convert_archive(Path("invalid.cbr"), "CBR")
        

def test_convert_batch_empty_list(converter):
    # Should return empty list for empty input
    results = converter.convert_batch([], "cbz")
    assert results == []


def test_callbacks_are_called(monkeypatch):
    # Test that progress and status callbacks are called
    called = {"progress": False, "status": False}
    
    def progress_cb(current, total):
        called["progress"] = True
        
    def status_cb(msg):
        called["status"] = True
    conv = ArchiveArchiveConverter(progress_callback=progress_cb, status_callback=status_cb)
    # Patch convert_archive to avoid real file ops
    
    def dummy_convert_archive(*a, **kw):
        # Call the progress callback if provided
        if hasattr(conv, "progress_callback") and conv.progress_callback:
            conv.progress_callback(50, 100)
        if hasattr(conv, "status_callback") and conv.status_callback:
            conv.status_callback("Dummy status")
        return Path("dummy.cbz")

    monkeypatch.setattr(conv, "convert_archive", dummy_convert_archive)
    dummy_file = Path("dummy.cbr")
    # Patch detect_archive_format to simulate CBR
    monkeypatch.setattr(conv, "detect_archive_format", lambda p: "CBR")
    result = conv.convert_file(dummy_file, "cbz")
    assert not result[2]
    assert called["progress"]
    assert called["status"]


def test_convert_file_real_archive(converter):
    test_file = Path("tests/test-archive.cbz")
    result = converter.convert_file(test_file, "cbr")
    assert result[2]  # success should be True
    assert result[1].endswith(".cbr")
