import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import ConvertWindow
from pytestqt.qtbot import QtBot
import pytest


@pytest.fixture
def app(qtbot: QtBot):
    window = ConvertWindow()
    qtbot.addWidget(window)
    return window


def test_window_opens(app):
    assert app.windowTitle() == "C.A.P.T - Archive Converter"
    

def test_widget_exists(app):
    assert app.file_management is not None
    assert app.progress_widget is not None
    assert app.convert_btn is not None
    assert app.close_btn is not None
    
    
def test_radio_button_selection_updates_progress(app, qtbot):
    app.radio_buttons['cbz_to_cbr'].setChecked(True)
    qtbot.wait(50)
    assert "CBR (from CBZ)" in app.progress_widget.progress_text.toPlainText()
    
    
def test_convert_no_files_shows_error(app, qtbot):
    app.file_management.get_selected_files = lambda: []
    app.convert_btn.click()
    qtbot.wait(50)
    assert "No files selected for conversion" in app.progress_widget.progress_text.toPlainText()
