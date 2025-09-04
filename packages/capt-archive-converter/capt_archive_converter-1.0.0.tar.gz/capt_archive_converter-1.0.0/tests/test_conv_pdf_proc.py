import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from pathlib import Path
from processors.arc_conv_pdf_proc import PdfArchiveConverter, ArchiveConversionError


@pytest.fixture
def converter():
    return PdfArchiveConverter()


def test_detect_archive_format_returns_none_for_unknown(converter):
    unknown_file = Path("unknown.xyz")
    result = converter.detect_archive_format(unknown_file)
    assert result is None
    

def test_convert_file_unsupported_format(converter):
    dummy_file = Path("dummy.pdf")
    result = converter.convert_file(dummy_file, "cbr")
    assert not result[2]
    assert "Unsupported conversion type" in result[3]
    

def test_convert_file_missing_file(converter):
    missing_file = Path("missing.pdf")
    result = converter.convert_file(missing_file, "cbz")
    assert not result[2]
    assert "not found" in result[3] or "No such file" in result[3] or "Unsupported conversion type" in result[3]
    

def test_convert_archive_invalid_format(converter):
    with pytest.raises(ArchiveConversionError):
        converter.convert_pdf_to_cbz(Path("invalid.pdf"))
        

def test_convert_batch_empty_list(converter):
    results = converter.convert_batch([], "cbz")
    assert results == []
    

def test_callbacks_are_called(monkeypatch):
    called = {"progress": False, "status": False}
    
    def progress_cb(current, total):
        called["progress"] = True
        
    def status_cb(msg):
        called["status"] = True
    conv = PdfArchiveConverter(progress_callback=progress_cb, status_callback=status_cb)
    
    def dummy_convert_pdf_to_cbz(*a, **kw):
        if hasattr(conv, "progress_callback") and conv.progress_callback:
            conv.progress_callback(50, 100)
        if hasattr(conv, "status_callback") and conv.status_callback:
            conv.status_callback("Dummy status")
        return Path("dummy.cbz")
    monkeypatch.setattr(conv, "convert_pdf_to_cbz", dummy_convert_pdf_to_cbz)
    dummy_file = Path("dummy.pdf")
    # Patch detect_archive_format to simulate PDF
    monkeypatch.setattr(conv, "detect_archive_format", lambda p: "PDF")
    result = conv.convert_file(dummy_file, "cbz")
    assert not result[2]
    assert called["progress"]
    assert called["status"]
    

def test_convert_file_real_pdf(converter):
    test_file = Path("tests/test-archive.pdf")
    result = converter.convert_file(test_file, "cbz")
    assert result[2]  # success should be True
    assert result[1].endswith(".cbz")
