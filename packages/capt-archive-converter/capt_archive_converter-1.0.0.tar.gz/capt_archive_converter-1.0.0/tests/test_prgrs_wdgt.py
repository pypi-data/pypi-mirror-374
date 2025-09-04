import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from widgets.prgrs_wdgt import ProgressWidget


@pytest.fixture
def widget(qtbot):
    w = ProgressWidget()
    qtbot.addWidget(w)
    return w


def test_widget_initialization(widget):
    assert widget.progress_text.toPlainText().startswith("Ready to start")
    assert widget.progress_bar.value() == 0


def test_append_message_updates_text_and_emits_signal(widget, qtbot):
    called = []
    widget.message_appended.connect(lambda msg: called.append(msg))
    widget.append_message("Processing started")
    assert "Processing started" in widget.progress_text.toPlainText()
    assert called and called[0] == "Processing started"


def test_set_progress_updates_bar_and_emits_signal(widget, qtbot):
    called = []
    widget.progress_updated.connect(lambda val: called.append(val))
    widget.set_progress(42)
    assert widget.progress_bar.value() == 42
    assert called and called[0] == 42
    

def test_clear_resets_text_and_bar(widget):
    widget.append_message("Test message")
    widget.set_progress(99)
    widget.clear()
    assert widget.progress_text.toPlainText() == ""
    assert widget.progress_bar.value() == 0
