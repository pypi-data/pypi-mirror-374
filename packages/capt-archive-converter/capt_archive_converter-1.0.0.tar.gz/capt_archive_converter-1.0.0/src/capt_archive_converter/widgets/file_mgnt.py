"""
FileManagementWidget for Comic Archive Processing Toolkit

Reusable widget for file/folder selection, file list display, and archive info panel.
Designed for integration into multiple GUI windows.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLabel, QFileDialog, QListWidgetItem
)

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtCore import Qt
from pathlib import Path


class FileManagementWidget(QWidget):
    """
    Widget for managing comic archive files and folders.
    Emits signals for file/folder selection and clearing.
    """

    files_changed = pyqtSignal(list)  # Emits list of loaded file paths

    def __init__(self, parent=None):
        """
        Initialize the FileManagementWidget.

        Args:
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setup_ui()
        self.loaded_files = []
        self.last_loaded_folder = None  # Track last loaded folder

    def show_context_menu(self, pos):
        """
        Show context menu for file list with options to refresh or remove selected files.

        Args:
            pos: Position to show the context menu.
        """
        from PyQt6.QtWidgets import QMenu
        menu = QMenu()
        refresh_action = menu.addAction("Refresh List")
        delete_action = menu.addAction("Remove Selected")
        action = menu.exec(self.file_list.mapToGlobal(pos))
        if action == refresh_action:
            self.refresh_file_list()
        elif action == delete_action:
            self.delete_selected_files()

    def file_list_key_press_event(self, event):
        """
        Handle key press events for the file list widget.
        Delete key removes selected files, F5 refreshes the list.

        Args:
            event: QKeyEvent or other event.
        """
        from PyQt6.QtGui import QKeyEvent
        if isinstance(event, QKeyEvent):
            if event.key() == Qt.Key.Key_Delete:
                self.delete_selected_files()
            elif event.key() == Qt.Key.Key_F5:
                self.refresh_file_list()
            else:
                QListWidget.keyPressEvent(self.file_list, event)
        else:
            QListWidget.keyPressEvent(self.file_list, event)

    def delete_selected_files(self):
        """
        Remove selected files from the loaded files list and update the display.
        Emits files_changed signal.
        """
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            full_path = item.data(Qt.ItemDataRole.UserRole)
            if full_path in self.loaded_files:
                self.loaded_files.remove(full_path)
        self.update_file_list()
        self.files_changed.emit(self.loaded_files)

    def dragEnterEvent(self, event):
        """
        Accept drag event if it contains URLs (files/folders).

        Args:
            event: QDragEnterEvent
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
        """
        Handle drop event for files/folders. Adds supported files to the loaded list.

        Args:
            event: QDropEvent
        """
        archive_exts = [".cbz", ".cbr", ".pdf"]
        files_to_add = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            p = Path(path)
            if p.is_file() and any(p.name.lower().endswith(ext) for ext in archive_exts):
                files_to_add.append(str(p))
            elif p.is_dir():
                for ext in archive_exts:
                    files_to_add.extend(str(f) for f in p.rglob(f"*{ext}"))
        if files_to_add:
            self.loaded_files.extend(files_to_add)
            self.update_file_list()
            self.files_changed.emit(self.loaded_files)

    def setup_ui(self):
        """
        Set up the user interface for the file management widget.
        Includes buttons, file list, and info panel.
        """
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        # Button row
        button_layout = QHBoxLayout()
        self.add_folder_btn = QPushButton("Add Folder")
        self.add_files_btn = QPushButton("Add File(s)")
        self.clear_all_btn = QPushButton("Clear All")
        self.refresh_file_list_btn = QPushButton("Refresh")
        button_layout.addWidget(self.add_folder_btn)
        button_layout.addWidget(self.add_files_btn)
        button_layout.addWidget(self.clear_all_btn)
        button_layout.addWidget(self.refresh_file_list_btn)
        layout.addLayout(button_layout)

        # File list display
        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(120)
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.file_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)
        self.file_list.keyPressEvent = self.file_list_key_press_event

        # Enable drag-and-drop reordering
        from PyQt6.QtWidgets import QAbstractItemView
        self.file_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.file_list.model().rowsMoved.connect(self.sync_loaded_files_with_list)

        layout.addWidget(self.file_list)

        # Info panel
        self.info_label = QLabel(
            "Total: 0 files, Size: 0 MB, CBZ: 0, CBR: 0, PDF: 0"
        )
        self.info_label.setStyleSheet(
            "color: #666; padding: 8px; border: 1px solid #ccc; border-radius: 3px;"
        )
        self.info_label.setMinimumHeight(30)
        layout.addWidget(self.info_label)

        # Connect signals
        self.add_folder_btn.clicked.connect(self.add_folder)
        self.add_files_btn.clicked.connect(self.add_files)
        self.clear_all_btn.clicked.connect(self.clear_all)
        self.refresh_file_list_btn.clicked.connect(self.refresh_file_list)

    def add_folder(self):
        """
        Open a dialog to select a folder and add all supported archive files from it.
        Updates loaded files and emits files_changed signal.
        """
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.last_loaded_folder = folder
            archive_exts = ["*.cbz", "*.cbr", "*.pdf"]
            files = []
            for ext in archive_exts:
                files.extend(str(f) for f in Path(folder).rglob(ext))
            self.loaded_files.extend(files)
            self.update_file_list()
            self.files_changed.emit(self.loaded_files)

    def add_files(self):
        """
        Open a dialog to select files and add them to the loaded files list.
        Emits files_changed signal.
        """
        files, _ = QFileDialog.getOpenFileNames(self, "Select Comic Archives", "", "Comic Archives (*.cbz *.cbr *.pdf)")
        if files:
            self.loaded_files.extend(files)
            self.update_file_list()
            self.files_changed.emit(self.loaded_files)

    def clear_all(self):
        """
        Clear all loaded files from the list and emit files_changed signal.
        """
        self.loaded_files = []
        self.update_file_list()
        self.files_changed.emit(self.loaded_files)

    def update_file_list(self):
        """
        Update the QListWidget display to match the loaded files list.
        Also updates the info panel.
        """
        self.file_list.clear()
        for f in self.loaded_files:
            file_name = Path(f).name
            item = QListWidgetItem(file_name)
            item.setData(Qt.ItemDataRole.UserRole, f)  # Store full path
            self.file_list.addItem(item)
        self.update_info_panel()

    def update_info_panel(self):
        """
        Update the info panel to show file counts and total size for loaded files.
        """
        total_files = len(self.loaded_files)
        cbz_count = sum(1 for f in self.loaded_files if f.lower().endswith('.cbz'))
        cbr_count = sum(1 for f in self.loaded_files if f.lower().endswith('.cbr'))
        pdf_count = sum(1 for f in self.loaded_files if f.lower().endswith('.pdf'))
        total_size = sum(Path(f).stat().st_size for f in self.loaded_files if Path(f).exists())
        total_size_mb = round(total_size / (1024 * 1024), 1)
        info_text = f"Total: {total_files} files, Size: {total_size_mb} MB, CBZ: {cbz_count}, CBR: {cbr_count}, PDF: {pdf_count}"
        self.info_label.setText(info_text)

    def get_selected_files(self):
        """
        Return the list of loaded files.
        (Extend to return only selected items if needed.)

        Returns:
            list: List of loaded file paths.
        """
        return self.loaded_files

    def refresh_file_list(self):
        """
        Rescan all parent folders of loaded files for supported files and update the list.
        Removes duplicates and emits files_changed signal.
        """
        archive_exts = ["*.cbz", "*.cbr", "*.pdf"]
        parent_dirs = set(Path(f).parent for f in self.loaded_files)
        files = []
        for folder in parent_dirs:
            for ext in archive_exts:
                files.extend(str(f) for f in folder.rglob(ext))
        # Remove duplicates and update
        self.loaded_files = list(dict.fromkeys(files))
        self.update_file_list()
        self.files_changed.emit(self.loaded_files)

    def sync_loaded_files_with_list(self, *args):
        """
        Sync the loaded files list with the QListWidget items after a drag-and-drop reorder.
        Emits files_changed signal.
        """
        self.loaded_files = [
            self.file_list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.file_list.count())
        ]
        self.files_changed.emit(self.loaded_files)
