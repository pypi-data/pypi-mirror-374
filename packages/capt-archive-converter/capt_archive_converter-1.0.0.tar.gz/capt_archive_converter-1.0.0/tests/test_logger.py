import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import logging
from utils.logger import (
    setup_logging,
    get_operation_logger,
    log_operation_start,
    log_operation_end
)


def test_setup_logging_creates_logs_dir(tmp_path, monkeypatch):
    # Patch Path to use tmp_path for logs
    monkeypatch.setattr("utils.logger.Path", lambda p="logs": tmp_path / "logs")
    setup_logging(logging.DEBUG)
    logs_dir = tmp_path / "logs"
    assert logs_dir.exists()
    assert (logs_dir / "comic_toolkit_main.log").exists()


def test_get_operation_logger_creates_file(tmp_path, monkeypatch):
    monkeypatch.setattr("utils.logger.Path", lambda p="logs": tmp_path / "logs")
    logger = get_operation_logger("convert")
    logs_dir = tmp_path / "logs"
    log_file = logs_dir / "convert_operations.log"
    logger.info("Test log entry")
    assert log_file.exists()
    with open(log_file, encoding="utf-8") as f:
        content = f.read()
    assert "Test log entry" in content


def test_log_operation_start_and_end(tmp_path, monkeypatch):
    monkeypatch.setattr("utils.logger.Path", lambda p="logs": tmp_path / "logs")
    log_operation_start("shrink", details="Shrink test details")
    log_operation_end("shrink", success=True, details="Shrink completed")
    logs_dir = tmp_path / "logs"
    log_file = logs_dir / "shrink_operations.log"
    assert log_file.exists()
    with open(log_file, encoding="utf-8") as f:
        content = f.read()
    assert "OPERATION START: SHRINK" in content
    assert "Details: Shrink test details" in content
    assert "OPERATION END: SHRINK - SUCCESS" in content
    assert "Details: Shrink completed" in content


def test_get_operation_logger_no_duplicate_handlers(tmp_path, monkeypatch):
    monkeypatch.setattr("utils.logger.Path", lambda p="logs": tmp_path / "logs")
    # Use logger to check handler count
    logger = get_operation_logger("convert")
    handler_count = len(logger.handlers)
    # Get logger again and check handler count is unchanged (no duplicates)
    logger2 = get_operation_logger("convert")
    assert len(logger2.handlers) == handler_count
