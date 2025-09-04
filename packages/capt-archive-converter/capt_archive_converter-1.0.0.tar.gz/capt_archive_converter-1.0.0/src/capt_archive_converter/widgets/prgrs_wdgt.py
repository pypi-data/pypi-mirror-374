"""
ProgressWidget for Comic Archive Processing Toolkit

Reusable widget for displaying progress messages and a progress bar.
Designed for integration into multiple GUI windows.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QProgressBar, QGroupBox
from PyQt6.QtCore import pyqtSignal


class ProgressWidget(QWidget):
    """
    Widget for progress tracking: displays progress messages and a progress bar.
    Emits signals for progress updates and message appends.
    Designed for integration into multiple GUI windows.
    """
    progress_updated = pyqtSignal(int)  # Emits progress bar value
    message_appended = pyqtSignal(str)  # Emits appended message

    def __init__(self, parent=None):
        """
        Initialise the ProgressWidget.

        Args:
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """
        Set up the user interface for the progress widget.
        Includes a group box, progress text area, and progress bar.
        """
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        # Group box for consistent style
        self.progress_group = QGroupBox("Progress")
        group_layout = QVBoxLayout(self.progress_group)

        # Progress text area
        self.progress_text = QTextEdit()
        self.progress_text.setReadOnly(True)
        self.progress_text.setMinimumHeight(100)
        self.progress_text.setMaximumHeight(100)
        self.progress_text.setPlainText("Ready to start processing...")
        group_layout.addWidget(self.progress_text)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(25)
        self.progress_bar.setValue(0)
        group_layout.addWidget(self.progress_bar)

        layout.addWidget(self.progress_group)

    def append_message(self, message):
        """
        Append a status message to the text output.

        Args:
            message (str): The message to append.
        """
        self.progress_text.append(message)
        # Optionally scroll to bottom
        self.progress_text.verticalScrollBar().setValue(self.progress_text.verticalScrollBar().maximum())
        self.message_appended.emit(message)

    def set_progress(self, value: int):
        """
        Set the progress bar value and emit progress_updated signal.

        Args:
            value (int): Progress value (0-100).
        """
        self.progress_bar.setValue(value)
        self.progress_updated.emit(value)

    def clear(self):
        """
        Clear the progress text area and reset the progress bar to zero.
        """
        self.progress_text.clear()
        self.progress_bar.setValue(0)
