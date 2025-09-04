# Comic Archive Processing Toolkit (C.A.P.T) - Archive Converter v1.0.0
# Copyright (C) 2023 Your Name or Organization
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys

from capt_archive_converter.widgets.file_mgnt import FileManagementWidget
from capt_archive_converter.widgets.prgrs_wdgt import ProgressWidget
"""
Convert Window for Comic Archive Processing Toolkit (C.A.P.T)

Independent window for CBR ↔ CBZ archive conversion operations.
Features file management, format selection, and real-time progress tracking.
Completely self-contained window that can run independently.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QGroupBox, QRadioButton, QCheckBox, QWidget, QButtonGroup, QApplication
)
from PyQt6.QtCore import QThread, Qt
from capt_archive_converter.utils.logger import get_operation_logger
from capt_archive_converter.processors.arc_convert_worker import ConversionWorker


class ConvertWindow(QMainWindow):
    """
    Independent convert window for archive conversion operations.

    Features:
    - File and folder management interface
    - CBR ↔ CBZ format selection
    - Real-time progress tracking with scrolling updates
    - Professional layout as standalone window
    - No parent dependencies - completely independent
    """

    def __init__(self):
        """Initialise the independent convert window."""
        super().__init__()
        self.setWindowTitle("C.A.P.T - Archive Converter")
        self.setGeometry(600, 200, 384, 655)
        self.setMinimumSize(384, 655)
        self.setMaximumSize(384, 660)

        self.logger = get_operation_logger('convert_window')
        self.setup_ui()
        self.connect_signals()
        self.update_info_display()

        self.logger.info("Convert window initialised successfully")

    def progress_widget_update(self, current, total):
        """
        Update the progress widget with the current progress percentage.
        Called by the ConversionWorker via signal during conversion.

        Args:
            current (int): Current progress value.
            total (int): Total value for completion.
        """
        percent = int((current / total) * 100) if total else 0
        self.progress_widget.set_progress(percent)
        QApplication.processEvents()

    def setup_ui(self):
        """
        Set up the main user interface for the convert window.
        Adds file management, conversion options, progress widget, and action buttons.
        """
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # File Management Section
        self.file_management = FileManagementWidget()
        layout.addWidget(self.file_management)

        # Conversion Options Section (refactored)
        self.create_conversion_options_section(layout)

        # Progress Section (refactored)
        self.progress_widget = ProgressWidget()
        layout.addWidget(self.progress_widget)

        # Action Buttons
        self.create_action_buttons(layout)

    def create_conversion_options_section(self, layout):
        """
        Create the conversion options section with format selection and additional options.

        Args:
            layout (QVBoxLayout): The main layout to add the options group to.
        """
        options_group = QGroupBox("Conversion Options")
        options_layout = QVBoxLayout(options_group)

        # Format selection radio buttons with mapping
        self.format_group = QButtonGroup()
        self.radio_buttons = {
            'cbr_to_cbz': QRadioButton(),
            'cbz_to_cbr': QRadioButton(),
            'pdf_to_cbz': QRadioButton(),
            'cbz_to_pdf': QRadioButton()
        }
        self.radio_buttons['cbr_to_cbz'].setChecked(True)  # Default to CBZ

        # Create layouts for pairs of formats
        format_pairs = [
            ("CBR → CBZ", self.radio_buttons['cbr_to_cbz'], "CBZ → CBR", self.radio_buttons['cbz_to_cbr']),
            ("PDF → CBZ", self.radio_buttons['pdf_to_cbz'], "CBZ → PDF", self.radio_buttons['cbz_to_pdf'])
        ]

        for label1, radio1, label2, radio2 in format_pairs:
            format_layout = QHBoxLayout()
            format_layout.addStretch(1)
            format_layout.addWidget(QLabel(label1))
            format_layout.addWidget(radio1)
            format_layout.addStretch(2)
            format_layout.addWidget(radio2)
            format_layout.addWidget(QLabel(label2))
            format_layout.addStretch(1)
            options_layout.addLayout(format_layout)

            self.format_group.addButton(radio1)
            self.format_group.addButton(radio2)

        # Additional options: delete original files checkbox
        delete_layout = QVBoxLayout()
        delete_label = QLabel("Delete Original Files")
        delete_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.delete_original_cb = QCheckBox()
        self.delete_original_cb.setToolTip("Delete original files after successful conversion")
        cb_layout = QHBoxLayout()
        cb_layout.addStretch()
        cb_layout.addWidget(self.delete_original_cb)
        cb_layout.addStretch()
        delete_layout.addWidget(delete_label)
        delete_layout.addLayout(cb_layout)
        options_layout.addLayout(delete_layout)

        layout.addWidget(options_group)

    def create_action_buttons(self, layout):
        """
        Create and add the Convert and Close action buttons to the layout.

        Args:
            layout (QVBoxLayout): The main layout to add the buttons to.
        """
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.convert_btn = QPushButton("Convert")
        self.convert_btn.setDefault(True)
        self.convert_btn.setMinimumHeight(35)
        self.convert_btn.setStyleSheet("font-weight: bold;")
        button_layout.addWidget(self.convert_btn)
        self.close_btn = QPushButton("Close")
        self.close_btn.setMinimumHeight(35)
        button_layout.addWidget(self.close_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

    def connect_signals(self):
        """
        Connect UI signals (button clicks, radio toggles) to their respective handler methods.
        """
        # Format selection: use dict for efficiency
        self.format_descriptions = {
            'cbr_to_cbz': "CBZ (from CBR)",
            'cbz_to_cbr': "CBR (from CBZ)",
            'pdf_to_cbz': "CBZ (from PDF)",
            'cbz_to_pdf': "PDF (from CBZ)"
        }
        for key, radio in self.radio_buttons.items():
            radio.toggled.connect(lambda checked, desc=self.format_descriptions[key]: self.update_conversion_options(checked, desc))

        # Action buttons
        self.convert_btn.clicked.connect(self.start_conversion)
        self.close_btn.clicked.connect(self.close)

    def update_conversion_options(self, checked, target_format):
        """
        Update conversion options display when a format radio button is checked.

        Args:
            checked (bool): Whether the radio button is checked.
            target_format (str): The target format description.
        """
        if checked:
            self.append_progress(f"🎯 Target format: {target_format}")

    def start_conversion(self):
        """
        Start the archive conversion process using ConversionWorker in a separate QThread.
        Validates user selections, sets up worker and thread, and connects signals for progress/results.
        """
        # Determine target format using dict for efficiency
        target_format_map = {
            'cbr_to_cbz': "cbz",
            'cbz_to_cbr': "cbr",
            'pdf_to_cbz': "cbz",
            'cbz_to_pdf': "pdf"
        }
        target_format = None
        for key, radio in self.radio_buttons.items():
            if radio.isChecked():
                target_format = target_format_map[key]
                break
        if not target_format:
            self.append_progress("❌ No conversion format selected")
            return

        delete_original = self.delete_original_cb.isChecked()
        self.append_progress("🚀 Starting conversion process...")
        self.append_progress(f"   Target format: {target_format.upper()}")
        self.append_progress(f"   Delete originals: {'Yes' if delete_original else 'No'}")

        selected_files = self.file_management.get_selected_files()
        if not selected_files:
            self.append_progress("❌ No files selected for conversion")
            return

        # All conversion logic is now handled by ConversionWorker
        self.thread = QThread()
        self.worker = ConversionWorker(selected_files, target_format, delete_original)
        self.worker.moveToThread(self.thread)

        # Connect worker signals in order: progress first, then status for better sync
        self.worker.progress.connect(self.progress_widget_update)
        self.worker.status.connect(self.append_progress_with_progress)  # Use new method for synced messages
        self.worker.result.connect(self.handle_conversion_results)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def handle_conversion_results(self, results):
        """
        Handle the results from the ConversionWorker after conversion completes.
        Updates the progress widget with success/failure messages for each file.

        Args:
            results (list): List of tuples (original_path, converted_path, success, error_message)
        """
        from pathlib import Path
        for original_path, converted_path, success, error_message in results:
            status = "✅ Successfully converted:" if success else "❌ Failed:"
            file_name = Path(converted_path if success else original_path).name
            message = f"{status} {file_name}"
            if not success:
                message += f" - {error_message}"
            self.append_progress(message)
        self.append_progress("🏁 Conversion process completed")
        self.update_info_display()

    def append_progress_with_progress(self, message):
        """
        Append a status message with progress context for better sync.
        Includes current progress in the message if available, and delays bar update slightly.
        """
        current_progress = self.progress_widget.progress_bar.value()
        synced_message = f"{message} ({current_progress}%)" if current_progress > 0 else message
        self.append_progress(synced_message)
        # Small delay to ensure text updates before bar (if needed)
        QApplication.processEvents()

    def update_info_display(self):
        """
        Update the file information display panel in the file management widget.
        """
        self.file_management.update_info_panel()

    def append_progress(self, message):
        """
        Append a message to the progress widget for user feedback.

        Args:
            message (str): The message to display in the progress widget.
        """
        self.progress_widget.append_message(message)

    def closeEvent(self, event):
        """
        Handle the window close event and log the closure.

        Args:
            event (QCloseEvent): The close event object.
        """
        self.logger.info("Convert window closing")
        event.accept()


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    app.setApplicationName("C.A.P.T - Archive Converter v1.0.0")
    QApplication.setStyle("Fusion")
    window = ConvertWindow()
    window.show()
    sys.exit(app.exec())
    

if __name__ == "__main__":
    main()
