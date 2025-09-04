import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from pathlib import Path
from utils.arc_conv_helpers import (
    extract_rar_archive,
    extract_zip_archive,
    create_zip_archive,
    create_rar_archive,
    create_per_file_progress_callback
)


def test_extract_zip_archive(tmp_path):
    # Create a test ZIP file
    import zipfile
    zip_path = tmp_path / "test.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("file.txt", "hello")
    extract_path = tmp_path / "extracted"
    extract_path.mkdir()
    called = []
    extract_zip_archive(zip_path, extract_path, lambda c, t: called.append((c, t)))
    assert (extract_path / "file.txt").exists()
    assert called  # Progress callback called
    

def test_extract_zip_archive_error(tmp_path):
    # Try to extract a non-zip file
    fake_zip = tmp_path / "fake.zip"
    fake_zip.write_text("not a zip")
    extract_path = tmp_path / "extracted"
    extract_path.mkdir()
    with pytest.raises(RuntimeError):
        extract_zip_archive(fake_zip, extract_path)
        

def test_create_zip_archive(tmp_path):
    # Create files to zip
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.txt").write_text("A")
    (src / "b.txt").write_text("B")
    zip_path = tmp_path / "out.zip"
    called = []
    create_zip_archive(src, zip_path, lambda c, t: called.append((c, t)))
    assert zip_path.exists()
    import zipfile
    with zipfile.ZipFile(zip_path) as zf:
        assert "a.txt" in zf.namelist()
        assert "b.txt" in zf.namelist()
    assert called  # Progress callback called
    

def test_create_zip_archive_error(tmp_path):
    # Try to zip a non-existent directory
    src = tmp_path / "missing"
    zip_path = tmp_path / "out.zip"
    with pytest.raises(RuntimeError):
        create_zip_archive(src, zip_path)


def test_create_rar_archive_subprocess(monkeypatch, tmp_path):
    # Mock subprocess.run to simulate rar creation
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.txt").write_text("A")
    rar_path = tmp_path / "out.rar"
    called = []
    
    class DummyResult:
        returncode = 0
        stderr = ""
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: DummyResult())
    create_rar_archive(src, rar_path, lambda c, t: called.append((c, t)))
    assert called  # Progress callback called


def test_create_rar_archive_missing_tool(monkeypatch, tmp_path):
    # Simulate missing rar tool
    src = tmp_path / "src"
    src.mkdir()
    rar_path = tmp_path / "out.rar"
    
    def raise_fn(*a, **kw):
        raise FileNotFoundError()
    monkeypatch.setattr("subprocess.run", raise_fn)
    with pytest.raises(RuntimeError):
        create_rar_archive(src, rar_path)


def test_create_per_file_progress_callback():
    called = []
    cb = create_per_file_progress_callback(lambda p, t: called.append((p, t)), 0, 2, False)
    cb(1, 2)
    assert called[0][0] <= 99  # Not last file, should not emit 100%
    called_last = []
    cb_last = create_per_file_progress_callback(lambda p, t: called_last.append((p, t)), 1, 2, True)
    cb_last(2, 2)
    assert called_last[0][0] == 100  # Last file emits 100%


def test_extract_rar_archive(tmp_path):
    rar_path = Path("tests/rar-extraction-test.rar")
    extract_path = tmp_path / "extracted_rar"
    extract_path.mkdir()
    called = []
    extract_rar_archive(rar_path, extract_path, lambda c, t: called.append((c, t)))
    # Check that at least one file was extracted
    extracted_files = list(extract_path.iterdir())
    assert extracted_files
    assert called  # Progress callback called
