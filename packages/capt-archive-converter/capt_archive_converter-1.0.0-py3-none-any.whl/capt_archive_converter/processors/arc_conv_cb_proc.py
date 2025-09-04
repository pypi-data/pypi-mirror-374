import tempfile
from pathlib import Path
from typing import Optional, Callable
from capt_archive_converter.utils.arc_convert_util import ArchiveConversionError, ArchiveConverter as UtilsArchiveConverter
from capt_archive_converter.utils.logger import get_operation_logger
from capt_archive_converter.utils.arc_conv_helpers import (
    extract_rar_archive,
    extract_zip_archive,
    create_zip_archive,
    create_rar_archive,
    create_per_file_progress_callback
)


class ArchiveArchiveConverter:
    """
    Processor class for CBR <-> CBZ conversions.
    """
    
    # Class-level constant for format mappings (static, shared across instances)
    FORMAT_MAP = {
        'CBR': {'extract': extract_rar_archive, 'create': create_zip_archive, 'target_suffix': '.cbz', 'target_format': 'CBZ'},
        'CBZ': {'extract': extract_zip_archive, 'create': create_rar_archive, 'target_suffix': '.cbr', 'target_format': 'CBR'}
    }

    def __init__(self, progress_callback=None, status_callback=None):
        """
        Initialize the ArchiveArchiveConverter.

        Args:
            progress_callback: Optional callback for progress updates.
            status_callback: Optional callback for status messages.
        """
        self.logger = get_operation_logger('archive_converter')
        self.progress_callback = progress_callback
        self.status_callback = status_callback  # Store the status_callback
        self.utils_converter = UtilsArchiveConverter()
        
        # Reference the class-level constant (no recreation needed)
        self.format_map = self.FORMAT_MAP

    def detect_archive_format(self, archive_path: Path) -> Optional[str]:
        return self.utils_converter.detect_archive_format(archive_path)

    def convert_batch(
        self,
        file_paths: list,
        target_format: str,
        delete_original: bool = False,
        status_callback: Optional[Callable[[str], None]] = None
    ) -> list:
        """
        Convert a batch of comic archives to the target format.

        Args:
            file_paths: List of full file paths to convert.
            target_format: 'cbz' or 'cbr'.
            delete_original: If True, delete original files after conversion.

        Returns:
            List of (original_path, converted_path, success, error_message)
        """
        results = []
        total_files = len(file_paths)
        for idx, file_path in enumerate(file_paths):
            is_last_file = (idx == total_files - 1)
            # Use the updated helper for per-file progress (0-100% per file)
            file_progress_callback = create_per_file_progress_callback(
                self.progress_callback, idx, total_files, is_last_file
            )
            
            result = self.convert_file(
                Path(file_path), target_format, delete_original, progress_callback=file_progress_callback, status_callback=lambda msg: status_callback(f"File {idx + 1}/{total_files}: {msg}") if status_callback else None
            )
            results.append(result)
        return results

    def convert_file(
        self,
        file_path: Path,
        target_format: str,
        delete_original: bool = False,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        status_callback: Optional[Callable[[str], None]] = None
    ) -> tuple:
        """
        Convert a single comic archive to the target format.

        Args:
            file_path: Full path to the archive.
            target_format: 'cbz' or 'cbr'.
            delete_original: If True, delete original after conversion.
            progress_callback: Optional callback for progress updates (normalized 0-100).
            status_callback: Optional callback for status updates (e.g., "Processing file...").

        Returns:
            (original_path, converted_path, success, error_message)
        """
        original_path = file_path
        converted_path = original_path.with_suffix(f'.{target_format}')
        success = False
        error_message = ""

        try:
            source_format = self.detect_archive_format(original_path)
            if (target_format == "cbz" and source_format == "CBR") or (target_format == "cbr" and source_format == "CBZ"):
                if status_callback:
                    status_callback(f"Processing {file_path.name}...")
                self.convert_archive(original_path, source_format, converted_path, progress_callback, status_callback)
            else:
                raise ArchiveConversionError("Unsupported conversion type or file extension.")

            success = converted_path.exists()
            if success:
                self.logger.info(f"Converted {original_path} to {converted_path}.")
                if delete_original:
                    original_path.unlink()
                    self.logger.info(f"Deleted original file: {original_path}")
            else:
                error_message = f"Conversion failed: {converted_path} was not created."
                self.logger.error(error_message)
        except Exception as exc:
            error_message = str(exc)
            self.logger.error(f"Failed to convert {original_path}: {error_message}")

        return str(original_path), str(converted_path), success, error_message

    def convert_archive(
        self,
        source_path: Path,
        source_format: str,
        output_path: Optional[Path] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        status_callback: Optional[Callable[[str], None]] = None,
        extract_start: int = 10,
        extract_end: int = 60,
        create_start: int = 60,
        create_end: int = 90
    ) -> Path:
        self.logger.info(f"Starting {source_format} to {self.format_map[source_format]['target_format']} conversion: {source_path}")

        if not source_path.exists():
            raise ArchiveConversionError(f"Source {source_format} file not found: {source_path}")

        if self.detect_archive_format(source_path) != source_format:
            raise ArchiveConversionError(f"File is not a valid {source_format} archive: {source_path}")

        if output_path is None:
            output_path = source_path.with_suffix(self.format_map[source_format]['target_suffix'])

        try:
            if status_callback:
                status_callback(f"Extracting {source_format} archive...")
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                if progress_callback:
                    progress_callback(extract_start, 100)
                self.format_map[source_format]['extract'](source_path, temp_path, progress_callback, extract_start, extract_end)
                if progress_callback:
                    progress_callback(extract_end, 100)
                if status_callback:
                    status_callback("Converting format...")
                self.format_map[source_format]['create'](temp_path, output_path, progress_callback, create_start, create_end)
                if status_callback:
                    status_callback(f"Packing into {self.format_map[source_format]['target_format']} archive...")
            if status_callback:
                status_callback("Cleaning up temporary files...")
            # Cleanup happens here (temp dir deleted)
            if progress_callback:
                progress_callback(100, 100)  # Now called after cleanup
            self.logger.info(f"{source_format} to {self.format_map[source_format]['target_format']} conversion complete: {output_path}")
            return output_path
        except Exception as e:
            error_msg = f"Failed to convert {source_format} to {self.format_map[source_format]['target_format']}: {str(e)}"
            self.logger.error(error_msg)
            raise ArchiveConversionError(error_msg)
