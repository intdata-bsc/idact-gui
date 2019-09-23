from gui.functionality.idact_app import IdactApp
from pytestqt.qt_compat import qt_api


def test_basics(qtbot):
    assert qt_api.QApplication.instance() is not None
    window = IdactApp()
    qtbot.addWidget(window)
    window.show()

    assert window.isVisible()
    assert window.windowTitle() == 'Idact GUI'


def test():
    assert 1 == 1
