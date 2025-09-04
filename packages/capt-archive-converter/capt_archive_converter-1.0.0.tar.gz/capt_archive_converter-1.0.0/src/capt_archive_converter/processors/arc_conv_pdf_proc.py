import tempfile
import zipfile
from pathlib import Path
from typing import Optional, Callable
import fitz  # PyMuPDF
from PIL import Image

from capt_archive_converter.utils.arc_convert_util import ArchiveConversionError, ArchiveConverter as UtilsArchiveConverter
from capt_archive_converter.utils.logger import get_operation_logger
from capt_archive_converter.utils.arc_conv_helpers import create_zip_archive, create_per_file_progress_callback


class PdfArchiveConverter:
    """
    Processor class for PDF <-> CBZ conversions.
    """

    def __init__(self, progress_callback=None, status_callback=None):
        """
        Initialize the PdfArchiveConverter.

        Args:
            progress_callback: Optional callback for progress updates.
            status_callback: Optional callback for status messages.
        """
        self.logger = get_operation_logger('pdf_converter')
        self.progress_callback = progress_callback
        self.status_callback = status_callback  # Add status_callback
        self.utils_converter = UtilsArchiveConverter()

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
            target_format: 'cbz' or 'pdf'.
            delete_original: If True, delete original files after conversion.
            status_callback: Optional callback for status messages.

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
            target_format: 'cbz' or 'pdf'.
            delete_original: If True, delete original after conversion.
            progress_callback: Optional callback for progress updates (normalized 0-100).
            status_callback: Optional callback for status messages.

        Returns:
            (original_path, converted_path, success, error_message)
        """
        original_path = file_path
        converted_path = original_path.with_suffix(f'.{target_format.lower()}')  # Ensure lowercase suffix
        success = False
        error_message = ""

        try:
            source_format = self.detect_archive_format(original_path)
            # Case-insensitive checks for robustness
            if (target_format.lower() == "cbz" and source_format.upper() == "PDF") or \
               (target_format.lower() == "pdf" and source_format.upper() == "CBZ"):
                if status_callback:
                    status_callback("Initializing PDF converter...")
                if target_format.lower() == "cbz":
                    self.convert_pdf_to_cbz(original_path, converted_path, progress_callback, status_callback)
                else:
                    self.convert_cbz_to_pdf(original_path, converted_path, progress_callback, status_callback)
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

    def convert_pdf_to_cbz(
        self,
        pdf_path: Path,
        output_path: Optional[Path] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        status_callback: Optional[Callable[[str], None]] = None,
        extract_start: int = 10,
        extract_end: int = 80,
        create_start: int = 90,
        create_end: int = 100
    ) -> Path:
        self.logger.info(f"Starting PDF to CBZ conversion: {pdf_path}")

        if not pdf_path.exists():
            raise ArchiveConversionError(f"Source PDF file not found: {pdf_path}")

        if self.detect_archive_format(pdf_path) != 'PDF':
            raise ArchiveConversionError(f"File is not a valid PDF: {pdf_path}")

        if output_path is None:
            output_path = pdf_path.with_suffix('.cbz')

        try:
            if status_callback:
                status_callback(f"Processing {pdf_path.name}...")
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                if progress_callback:
                    progress_callback(extract_start, 100)  # 10% - Setup/validation done
                if status_callback:
                    status_callback("Extracting PDF pages...")

                doc = fitz.open(str(pdf_path))
                total_pages = doc.page_count

                if progress_callback:
                    progress_callback(extract_start + 20, 100)  # Adjusted for parameterization

                for i, page in enumerate(doc):
                    pix = page.get_pixmap()
                    img_path = temp_path / f"page_{i + 1:03d}.png"
                    pix.save(str(img_path))
                    if progress_callback and total_pages > 0:
                        progress = extract_start + int(((i + 1) / total_pages) * (extract_end - extract_start))
                        progress_callback(progress, 100)

                doc.close()

                if progress_callback:
                    progress_callback(create_start, 100)  # 90% - Archive creation done
                if status_callback:
                    status_callback("Packing into CBZ archive...")

                create_zip_archive(temp_path, output_path, progress_callback, create_start, create_end)

                if progress_callback:
                    progress_callback(create_end, 100)  # 100% - Complete
                if status_callback:
                    status_callback("Cleaning up temporary files...")
        except Exception as e:
            error_msg = f"Failed to convert PDF to CBZ: {str(e)}"
            self.logger.error(error_msg)
            raise ArchiveConversionError(error_msg)

    def convert_cbz_to_pdf(
        self,
        cbz_path: Path,
        output_path: Optional[Path] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        status_callback: Optional[Callable[[str], None]] = None,
        extract_start: int = 10,
        extract_end: int = 80,
        create_start: int = 90,
        create_end: int = 100
    ) -> Path:
        self.logger.info(f"Starting CBZ to PDF conversion: {cbz_path}")

        if not cbz_path.exists():
            raise ArchiveConversionError(f"Source CBZ file not found: {cbz_path}")

        if self.detect_archive_format(cbz_path) != 'CBZ':
            raise ArchiveConversionError(f"File is not a valid CBZ archive: {cbz_path}")

        if output_path is None:
            output_path = cbz_path.with_suffix('.pdf')

        try:
            if status_callback:
                status_callback(f"Processing {cbz_path.name}...")
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                with zipfile.ZipFile(cbz_path, 'r') as zip_file:
                    image_files = [
                        f for f in zip_file.namelist()
                        if Path(f).suffix.lower() in self.utils_converter.supported_image_extensions
                    ]
                    image_files.sort()
                    total_images = len(image_files)
                    if total_images == 0:
                        raise ArchiveConversionError("No images found in CBZ archive.")

                    if status_callback:
                        status_callback("Extracting images from CBZ...")

                    extracted_images = []
                    for i, img_name in enumerate(image_files):
                        img_path = temp_path / Path(img_name).name
                        with zip_file.open(img_name) as img_file, open(img_path, 'wb') as out_file:
                            out_file.write(img_file.read())
                        extracted_images.append(str(img_path))
                        if progress_callback:
                            progress = extract_start + int(((i + 1) / total_images) * (extract_end - extract_start))
                            progress_callback(progress, 100)

                pil_images = []
                for img_file in extracted_images:
                    img = Image.open(img_file)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    pil_images.append(img)

                if not pil_images:
                    raise ArchiveConversionError("No valid images to convert to PDF.")

                if status_callback:
                    status_callback("Converting images to PDF...")

                pil_images[0].save(
                    output_path,
                    save_all=True,
                    append_images=pil_images[1:],
                    format='PDF'
                )

                if progress_callback:
                    progress_callback(create_start, 100)  # 90% - PDF creation done
                if status_callback:
                    status_callback("Creating PDF file...")
                if progress_callback:
                    progress_callback(create_end, 100)  # 100% - Complete
                if status_callback:
                    status_callback("Cleaning up temporary files...")
        except Exception as e:
            error_msg = f"Failed to convert CBZ to PDF: {str(e)}"
            self.logger.error(error_msg)
            raise ArchiveConversionError(error_msg)
        
    def _create_zip_archive(
        self,
        source_path: Path,
        zip_path: Path,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        start_progress: int = 0,
        end_progress: int = 100
    ):
        try:
            all_files = list(source_path.rglob('*'))
            files_to_archive = [f for f in all_files if f.is_file()]
            total_files = len(files_to_archive)
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for i, file_path in enumerate(files_to_archive):
                    relative_path = file_path.relative_to(source_path)
                    zip_file.write(file_path, relative_path)
                    if progress_callback and total_files > 0:
                        current_progress = start_progress + (
                            ((i + 1) / total_files) * (end_progress - start_progress)
                        )
                        progress_callback(int(current_progress), 100)
        except Exception as e:
            raise ArchiveConversionError(f"Failed to create ZIP archive: {str(e)}")
