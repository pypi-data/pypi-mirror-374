"""
Archive Conversion Utilities for Comic Archive Processing Toolkit

Provides core functionality for comic archive processing including:
- CBR to CBZ conversion (RAR → ZIP)
- CBZ to CBR conversion (ZIP → RAR)
- PDF to CBZ conversion (PDF → PNGs → ZIP)
- Archive format detection and validation
- Progress tracking for conversion operations
- Error handling and recovery
"""

import zipfile
import rarfile
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

from capt_archive_converter.utils.logger import get_operation_logger


class ArchiveConversionError(Exception):
    """
    Custom exception for archive conversion errors.
    Raised when an archive conversion or validation operation fails.
    """
    pass


class ArchiveConverter:
    """
    Handles conversion and validation between CBR, CBZ, and PDF-to-CBZ archive formats.
    Provides format detection, archive validation, and utility methods for comic archives.
    """

    def __init__(self):
        """
        Initialize the archive converter with logging and supported image extensions.
        """
        self.logger = get_operation_logger('archive_converter')
        self.supported_image_extensions = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'
        }

    def detect_archive_format(self, archive_path: Path) -> Optional[str]:
        """
        Detect the format of an archive file or PDF.

        Args:
            archive_path (Path): Path to the file.

        Returns:
            str: 'CBZ', 'CBR', 'PDF', or None if format cannot be determined.
        """
        try:
            if archive_path.suffix.lower() == '.pdf':
                return 'PDF'
            if zipfile.is_zipfile(archive_path):
                return 'CBZ'
            if rarfile.is_rarfile(str(archive_path)):
                return 'CBR'
            return None
        except Exception as e:
            self.logger.error(f"Error detecting format for {archive_path}: {str(e)}")
            return None

    def validate_comic_archive(self, archive_path: Path) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate if an archive is a proper comic archive or PDF.

        Args:
            archive_path (Path): Path to the archive or PDF file.

        Returns:
            Tuple[bool, str, dict]: (is_valid, format, details_dict)
        """
        details = {
            'image_count': 0,
            'has_metadata': False,
            'has_folders': False,
            'image_files': [],
            'total_size': 0
        }

        format_type = self.detect_archive_format(archive_path)
        if not format_type:
            return False, 'UNKNOWN', details

        try:
            if format_type == 'CBZ':
                return self._validate_zip_archive(archive_path, details)
            elif format_type == 'CBR':
                return self._validate_rar_archive(archive_path, details)
            elif format_type == 'PDF':
                return self._validate_pdf_file(archive_path, details)
        except Exception as e:
            self.logger.error(f"Error validating file {archive_path}: {str(e)}")
            return False, format_type, details

        return False, format_type, details

    def _validate_pdf_file(self, archive_path: Path, details: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate a PDF file for comic archive suitability.

        Args:
            archive_path (Path): Path to the PDF file.
            details (dict): Details dictionary to populate.

        Returns:
            Tuple[bool, str, dict]: (is_valid, 'PDF', details_dict)
        """
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(str(archive_path))
            details['image_count'] = doc.page_count
            details['total_size'] = archive_path.stat().st_size
            doc.close()
            is_valid = details['image_count'] > 0
            return is_valid, 'PDF', details
        except Exception as e:
            self.logger.error(f"Error validating PDF {archive_path}: {str(e)}")
            return False, 'PDF', details

    def _validate_zip_archive(self, archive_path: Path, details: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate a ZIP-based comic archive (CBZ).

        Args:
            archive_path (Path): Path to the ZIP archive.
            details (dict): Details dictionary to populate.

        Returns:
            Tuple[bool, str, dict]: (is_valid, 'CBZ', details_dict)
        """
        try:
            with zipfile.ZipFile(archive_path, 'r') as zip_file:
                file_list = zip_file.namelist()
                for file_name in file_list:
                    file_path = Path(file_name)
                    if file_path.name.lower() == 'comicinfo.xml':
                        details['has_metadata'] = True
                    if len(file_path.parts) > 1:
                        details['has_folders'] = True
                    if file_path.suffix.lower() in self.supported_image_extensions:
                        details['image_count'] += 1
                        details['image_files'].append(file_name)
                        try:
                            file_info = zip_file.getinfo(file_name)
                            details['total_size'] += file_info.file_size
                        except Exception:
                            pass
                is_valid = details['image_count'] > 0
                return is_valid, 'CBZ', details
        except Exception as e:
            self.logger.error(f"Error validating ZIP archive {archive_path}: {str(e)}")
            return False, 'CBZ', details

    def _validate_rar_archive(self, archive_path: Path, details: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate a RAR-based comic archive (CBR).

        Args:
            archive_path (Path): Path to the RAR archive.
            details (dict): Details dictionary to populate.

        Returns:
            Tuple[bool, str, dict]: (is_valid, 'CBR', details_dict)
        """
        try:
            with rarfile.RarFile(str(archive_path), 'r') as rar_file:
                file_list = rar_file.namelist()
                for file_name in file_list:
                    file_path = Path(file_name)
                    if file_path.name.lower() == 'comicinfo.xml':
                        details['has_metadata'] = True
                    if len(file_path.parts) > 1:
                        details['has_folders'] = True
                    if file_path.suffix.lower() in self.supported_image_extensions:
                        details['image_count'] += 1
                        details['image_files'].append(file_name)
                        try:
                            file_info = rar_file.getinfo(file_name)
                            details['total_size'] += file_info.file_size
                        except Exception:
                            pass
                is_valid = details['image_count'] > 0
                return is_valid, 'CBR', details
        except Exception as e:
            self.logger.error(f"Error validating RAR archive {archive_path}: {str(e)}")
            return False, 'CBR', details


def get_archive_converter() -> ArchiveConverter:
    """
    Factory function to get an ArchiveConverter instance.

    Returns:
        ArchiveConverter: A new ArchiveConverter object.
    """
    return ArchiveConverter()
