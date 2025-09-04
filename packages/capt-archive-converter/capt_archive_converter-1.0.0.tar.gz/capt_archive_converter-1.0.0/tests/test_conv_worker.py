import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from processors.arc_convert_worker import ConversionWorker


class DummyConverter:
    def __init__(self, *a, **kw):
        self.progress_callback = kw.get("progress_callback")
        self.status_callback = kw.get("status_callback")
        
    def convert_batch(self, file_paths, target_format, delete_original, status_callback=None):
        if self.progress_callback:
            self.progress_callback(1, 2)
        if self.status_callback:
            self.status_callback("Dummy status")
        return [("file1", "file1.cbz", True, "")]
    

@pytest.fixture
def worker(monkeypatch):
    # Patch both converters to DummyConverter
    monkeypatch.setattr("processors.arc_convert_worker.PdfArchiveConverter", DummyConverter)
    monkeypatch.setattr("processors.arc_convert_worker.ArchiveArchiveConverter", DummyConverter)
    return ConversionWorker(["file1.cbr"], "cbz", False)


def test_worker_initialization(worker):
    assert worker.file_paths == ["file1.cbr"]
    assert worker.target_format == "cbz"
    assert worker.delete_original is False
    

def test_converter_selection_pdf(monkeypatch):
    monkeypatch.setattr("processors.arc_convert_worker.PdfArchiveConverter", DummyConverter)
    w = ConversionWorker(["file1.pdf"], "pdf", False)
    # Run should use PdfArchiveConverter (no error means success)
    w.emit_progress = lambda c, t: None
    w.status_callback = lambda msg: None
    w.result = DummySignal()
    w.progress = DummySignal()
    w.finished = DummySignal()
    w.run()
    

def test_converter_selection_archive(monkeypatch):
    monkeypatch.setattr("processors.arc_convert_worker.ArchiveArchiveConverter", DummyConverter)
    w = ConversionWorker(["file1.cbr"], "cbz", False)
    w.emit_progress = lambda c, t: None
    w.status_callback = lambda msg: None
    w.result = DummySignal()
    w.progress = DummySignal()
    w.finished = DummySignal()
    w.run()
    

def test_emit_progress_throttling(worker):
    # Should only emit when progress changes by >= 1% or is 100%
    emitted = []
    
    def fake_emit(current, total):
        emitted.append((current, total))
    worker.progress = DummySignal(fake_emit)
    worker.emit_progress(1, 100)
    worker.emit_progress(2, 100)
    worker.emit_progress(2, 100)  # Should not emit again
    worker.emit_progress(100, 100)
    assert emitted[0] == (1, 100)
    assert emitted[-1] == (100, 100)
    

def test_error_handling(monkeypatch):
    class FailingConverter:
        def __init__(self, *a, **kw):
            pass
        
        def convert_batch(self, *a, **kw):
            raise Exception("fail")
    
    monkeypatch.setattr("processors.arc_convert_worker.ArchiveArchiveConverter", FailingConverter)
    w = ConversionWorker(["file1.cbr"], "cbz", False)
    results = []
    statuses = []
    w.result = DummySignal(lambda r: results.append(r))
    w.progress = DummySignal()
    w.finished = DummySignal()
    w.status = DummySignal(lambda msg: statuses.append(msg))
    w.emit_progress = lambda c, t: None
    w.run()
    assert results[0] == []
    assert any("failed" in msg.lower() for msg in statuses)
    

class DummySignal:
    def __init__(self, func=None):
        self.func = func
        
    def emit(self, *a, **kw):
        if self.func:
            self.func(*a, **kw)
