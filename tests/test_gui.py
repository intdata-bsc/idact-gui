from gui.functionality.idact_app import IdactApp
from pytestqt.qt_compat import qt_api
from gui.configuration_provider import ConfigurationProvider

def test_basics(qtbot):
    assert qt_api.QApplication.instance() is not None
    conf_provider = ConfigurationProvider()
    if not conf_provider.check_if_conf_file_exists():
        conf_provider.create_conf_file()
    window = IdactApp()
    qtbot.addWidget(window)
    window.show()

    assert window.isVisible()
    assert window.windowTitle() == 'Idact GUI'


def test_true():
    assert 1 == 1
