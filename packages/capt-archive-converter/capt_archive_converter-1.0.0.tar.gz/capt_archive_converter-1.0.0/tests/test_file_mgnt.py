import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from widgets.file_mgnt import FileManagementWidget


@pytest.fixture
def app(qtbot):
    widget = FileManagementWidget()
    qtbot.addWidget(widget)
    return widget


def test_widget_initialization(app):
    assert hasattr(app, "file_list")
    assert hasattr(app, "info_label")
    assert hasattr(app, "add_files_btn")
    assert hasattr(app, "add_folder_btn")


def test_add_files_updates_list_and_emits_signal(app, qtbot, tmp_path, monkeypatch):
    test_file = tmp_path / "test.cbz"
    test_file.write_text("dummy")
    called = []
    app.files_changed.connect(lambda files: called.append(files))
    # Mock QFileDialog.getOpenFileNames to return our test file
    monkeypatch.setattr("PyQt6.QtWidgets.QFileDialog.getOpenFileNames", lambda *a, **kw: ([str(test_file)], ""))
    app.add_files()
    assert str(test_file) in app.loaded_files
    assert called  # Signal emitted


def test_clear_all_clears_files_and_emits_signal(app, qtbot, tmp_path):
    test_file = tmp_path / "test.cbz"
    test_file.write_text("dummy")
    app.loaded_files = [str(test_file)]
    called = []
    app.files_changed.connect(lambda files: called.append(files))
    app.clear_all()
    assert app.loaded_files == []
    assert called  # Signal emitted


def test_delete_selected_files_removes_file(app, qtbot, tmp_path):
    test_file = tmp_path / "test.cbz"
    test_file.write_text("dummy")
    app.loaded_files = [str(test_file)]
    app.update_file_list()
    item = app.file_list.item(0)
    app.file_list.setCurrentItem(item)
    app.delete_selected_files()
    assert str(test_file) not in app.loaded_files


def test_update_info_panel_displays_correct_info(app, qtbot, tmp_path):
    test_file = tmp_path / "test.cbz"
    test_file.write_text("dummy")
    app.loaded_files = [str(test_file)]
    app.update_info_panel()
    assert "Total: 1 files" in app.info_label.text()
    assert "CBZ: 1" in app.info_label.text()


def test_get_selected_files_returns_loaded_files(app, qtbot, tmp_path):
    test_file = tmp_path / "test.cbz"
    test_file.write_text("dummy")
    app.loaded_files = [str(test_file)]
    assert app.get_selected_files() == [str(test_file)]
