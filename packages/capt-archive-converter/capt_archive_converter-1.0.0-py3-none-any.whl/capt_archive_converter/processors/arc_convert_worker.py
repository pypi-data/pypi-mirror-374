from PyQt6.QtCore import QObject, pyqtSignal
from capt_archive_converter.utils.logger import get_operation_logger
from capt_archive_converter.processors.arc_conv_pdf_proc import PdfArchiveConverter
from capt_archive_converter.processors.arc_conv_cb_proc import ArchiveArchiveConverter


class ConversionWorker(QObject):
    """
    Worker class for performing archive conversions in a separate thread.
    Emits progress, result, finished, and status signals for GUI updates.
    """
    progress = pyqtSignal(int, int)
    result = pyqtSignal(list)
    finished = pyqtSignal()
    status = pyqtSignal(str)  # New signal for intermediate status messages

    def __init__(self, file_paths, target_format, delete_original):
        """
        Initialize the ConversionWorker.

        Args:
            file_paths (list): List of file paths to convert.
            target_format (str): Target format for conversion ('cbz', 'cbr', 'pdf').
            delete_original (bool): Whether to delete original files after conversion.
        """
        super().__init__()
        self.file_paths = file_paths
        self.target_format = target_format
        self.delete_original = delete_original
        self.logger = get_operation_logger('conversion_worker')
        self.conversion_done = False  # Flag to control final progress emit
        self.last_progress_percent = -1  # Track last emitted progress to throttle updates

    def run(self):
        """
        Run the conversion process for all files.
        Uses the appropriate converter and emits results and finished signals.
        """
        def status_callback(message):
            self.status.emit(message)  # Define status callback as a function
        self.status_callback = status_callback  # Assign to self for later use
        # Simplified and robust converter selection
        if self.target_format == "pdf" or any(str(f).lower().endswith(".pdf") for f in self.file_paths):
            converter = PdfArchiveConverter(progress_callback=self.emit_progress, status_callback=status_callback)
            self.logger.info("Using PdfArchiveConverter")
        else:
            converter = ArchiveArchiveConverter(progress_callback=self.emit_progress, status_callback=status_callback)
            self.logger.info("Using ArchiveArchiveConverter")

        if self.status_callback:
            self.status_callback("Initializing PDF converter..." if self.target_format == "pdf" or any(str(f).lower().endswith(".pdf") for f in self.file_paths) else "Initializing archive converter...")
        self.logger.info(f"Target format: {self.target_format}, Files: {len(self.file_paths)}")
        if self.status_callback:
            self.status_callback(f"Starting conversion of {len(self.file_paths)} file(s)...")
        try:
            results = converter.convert_batch(
                self.file_paths, self.target_format, self.delete_original, status_callback=status_callback
            )
            self.logger.info(f"Conversion completed: {len(results)} files processed")
            if self.status_callback:
                self.status_callback("Conversion completed successfully.")
            self.result.emit(results)
            # Now emit the final progress 100% after result
            self.conversion_done = True
            self.progress.emit(100, 100)
        except Exception as e:
            self.logger.error(f"Conversion failed: {str(e)}")
            if self.status_callback:
                self.status_callback("Conversion failed.")
            self.result.emit([])  # Emit empty results on failure
            # Still emit final progress on failure
            self.conversion_done = True
            self.progress.emit(100, 100)
        finally:
            self.finished.emit()

    def emit_progress(self, current, total):
        """
        Emit progress signal for GUI updates, throttled to reduce emissions.
        Only emit if progress has changed by at least 1%.
        """
        if total > 0:
            percent = int((current / total) * 100)
            if abs(percent - self.last_progress_percent) >= 1 or percent == 100:  # Throttle to 1% changes or final 100%
                self.last_progress_percent = percent
                self.progress.emit(current, total)
        else:
            self.progress.emit(current, total)  # Emit for edge cases
