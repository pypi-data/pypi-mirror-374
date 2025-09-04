import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from pathlib import Path
from utils.arc_convert_util import (
    ArchiveConversionError,
    ArchiveConverter,
    get_archive_converter
)


def test_archive_conversion_error():
    with pytest.raises(ArchiveConversionError):
        raise ArchiveConversionError("Test error")


@pytest.fixture
def converter():
    return ArchiveConverter()


def test_detect_archive_format_pdf(converter, tmp_path):
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_bytes(b"%PDF-1.4\n%EOF\n")  # Minimal PDF header
    assert converter.detect_archive_format(pdf_file) == "PDF"


def test_detect_archive_format_zip(converter, tmp_path):
    import zipfile
    zip_file = tmp_path / "test.cbz"
    with zipfile.ZipFile(zip_file, "w") as zf:
        zf.writestr("page1.png", "data")
    assert converter.detect_archive_format(zip_file) == "CBZ"


def test_detect_archive_format_rar(converter):
    cbr_file = Path("tests/test-archive.cbr")
    if cbr_file.exists():
        assert converter.detect_archive_format(cbr_file) == "CBR"


def test_detect_archive_format_unknown(converter, tmp_path):
    unknown_file = tmp_path / "unknown.xyz"
    unknown_file.write_text("not an archive")
    assert converter.detect_archive_format(unknown_file) is None


def test_validate_comic_archive_zip(converter, tmp_path):
    import zipfile
    zip_file = tmp_path / "comic.cbz"
    with zipfile.ZipFile(zip_file, "w") as zf:
        zf.writestr("page1.png", "data")
        zf.writestr("comicinfo.xml", "<xml></xml>")
    valid, fmt, details = converter.validate_comic_archive(zip_file)
    assert valid
    assert fmt == "CBZ"
    assert details["image_count"] == 1
    assert details["has_metadata"]


def test_validate_comic_archive_pdf(converter, tmp_path):
    # Requires PyMuPDF (fitz)
    pdf_file = Path("tests/test_archive.pdf")
    if pdf_file.exists():
        valid, fmt, details = converter.validate_comic_archive(pdf_file)
        assert fmt == "PDF"
        assert details["image_count"] > 0


def test_validate_comic_archive_rar(converter):
    cbr_file = Path("tests/test-archive.cbr")
    if cbr_file.exists():
        valid, fmt, details = converter.validate_comic_archive(cbr_file)
        assert fmt == "CBR"
        assert details["image_count"] > 0


def test_get_archive_converter():
    conv = get_archive_converter()
    assert isinstance(conv, ArchiveConverter)
