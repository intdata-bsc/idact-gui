""" Basic tests for idact-gui.
"""
from pytestqt.qt_compat import qt_api
from gui.helpers.configuration_provider import ConfigurationProvider
from gui.functionality.main_window import MainWindow


def test_basics(qtbot):
    """ Tests if idact-gui renders itself.
    """
    assert qt_api.QApplication.instance() is not None
    conf_provider = ConfigurationProvider()
    if not conf_provider.check_if_conf_file_exists():
        conf_provider.create_conf_file()
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()

    assert window.isVisible()
    assert window.windowTitle() == 'Idact'
