"""
Logging utilities for Comic Archive Processing Toolkit

Provides centralised logging configuration with operation-specific log files.
Supports different log levels for development and user-facing operation.
All operations create dedicated log files for easier troubleshooting.

Features:
- Operation-specific log files (convert_operations.log, shrink_operations.log, etc.)
- Console output with appropriate formatting
- Development vs production log levels
- Automatic log directory creation
"""

import logging
from pathlib import Path
from datetime import datetime


def setup_logging(log_level=logging.INFO):
    """
    Set up centralised logging configuration.

    Creates a logs directory and configures both console and file logging
    with appropriate formatters. Used by main application startup.

    Args:
        log_level: Logging level (default: INFO for users, DEBUG for development)
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear any existing handlers
    root_logger.handlers.clear()

    # Console handler with user-friendly format
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_format = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    console_handler.setFormatter(console_format)
    root_logger.addHandler(console_handler)

    # Main application log file with detailed format
    main_log_file = log_dir / "comic_toolkit_main.log"
    file_handler = logging.FileHandler(main_log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # Always capture detailed logs to file
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    root_logger.addHandler(file_handler)

    logging.info("C.A.P.T - logging initialised")
    logging.info(f"Log files location: {log_dir.absolute()}")


def get_operation_logger(operation_name: str) -> logging.Logger:
    """
    Create a dedicated logger for specific operations.

    Each major operation (convert, shrink, restore, finalise) gets its own
    log file for easier troubleshooting and user feedback.

    Args:
        operation_name: Name of the operation (e.g., 'convert', 'shrink', 'restore')

    Returns:
        Logger instance configured for the specified operation

    Example:
        logger = get_operation_logger('convert')
        logger.info("Starting CBR to CBZ conversion")
    """
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Create operation-specific logger
    logger_name = f"comic_toolkit.{operation_name}"
    logger = logging.getLogger(logger_name)

    # Avoid duplicate handlers if logger already exists
    if not logger.handlers:
        # Operation-specific log file
        log_file = log_dir / f"{operation_name}_operations.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # Detailed format for operation logs
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Also log to console (will inherit from root logger)
        logger.setLevel(logging.INFO)

    return logger


def log_operation_start(operation_name: str, details: str = "") -> logging.Logger:
    """
    Log the start of a major operation with timestamp and details.

    Args:
        operation_name: Name of the operation starting
        details: Additional details about the operation

    Returns:
        Logger instance for the operation
    """
    logger = get_operation_logger(operation_name)

    separator = "=" * 50
    logger.info(separator)
    logger.info(f"OPERATION START: {operation_name.upper()}")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if details:
        logger.info(f"Details: {details}")
    logger.info(separator)

    return logger


def log_operation_end(operation_name: str, success: bool = True, details: str = ""):
    """
    Log the completion of a major operation with success status.

    Args:
        operation_name: Name of the operation ending
        success: Whether the operation completed successfully
        details: Additional details about the completion
    """
    logger = get_operation_logger(operation_name)

    separator = "=" * 50
    status = "SUCCESS" if success else "FAILED"
    logger.info(separator)
    logger.info(f"OPERATION END: {operation_name.upper()} - {status}")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if details:
        logger.info(f"Details: {details}")
    logger.info(separator)
    logger.info("")  # Blank line for readability
