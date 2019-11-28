""" Basic tests for idact-gui.
"""
import pytest
from pytestqt.qt_compat import qt_api
from gui.helpers.configuration_provider import ConfigurationProvider
from gui.functionality.main_window import MainWindow
from gui.helpers.parameter_saver import ParameterSaver
from gui.helpers.data_provider import DataProvider
from gui.functionality.idact_notebook import IdactNotebook
from gui.functionality.manage_jobs import ManageJobs
from gui.functionality.add_cluster import AddCluster
from gui.functionality.remove_cluster import RemoveCluster
from gui.functionality.adjust_timeouts import AdjustTimeouts
from gui.functionality.program_info_window import ProgramInfoWindow
from gui.functionality.help_window import HelpWindow


@pytest.fixture()
def window():
    assert qt_api.QApplication.instance() is not None
    conf_provider = ConfigurationProvider()
    if not conf_provider.check_if_conf_file_exists():
        conf_provider.create_conf_file()
    window = MainWindow()
    return window


def test_basics(window, qtbot):
    """ Tests if idact-gui renders itself.
    """
    window.show()

    assert window.isVisible()
    assert window.windowTitle() == 'Idact GUI'


def test_deploy_notebook_window(window, qtbot):
    """ Tests if it is possible to open deploy notebook window.
    """
    window.show()
    window.deploy_notebook_action.trigger()

    saver = ParameterSaver()
    data_provider = DataProvider()
    assert window.centralWidget().__class__ == IdactNotebook(data_provider).__class__


def test_manage_jobs_window(window, qtbot):
    """ Tests if it is possible to open manage jobs window.
    """
    window.show()
    window.manage_jobs_action.trigger()

    saver = ParameterSaver()
    data_provider = DataProvider()

    assert window.centralWidget().__class__ == ManageJobs(data_provider).__class__


def test_add_cluster_window(window, qtbot):
    """ Tests if it is possible to open add cluster window.
    """
    window.show()
    window.add_cluster_action.trigger()

    saver = ParameterSaver()
    data_provider = DataProvider()

    assert window.centralWidget().__class__ == AddCluster(data_provider).__class__


def test_remove_cluster_window(window, qtbot):
    """ Tests if it is possible to open remove cluster window.
    """
    window.show()
    window.remove_cluster_action.trigger()

    saver = ParameterSaver()
    data_provider = DataProvider()

    assert window.centralWidget().__class__ == RemoveCluster(data_provider).__class__


def test_edit_configuration_window(window, qtbot):
    """ Tests if it is possible to open edit configuration window.
    """
    window.show()
    window.edit_configuration_action.trigger()

    saver = ParameterSaver()
    data_provider = DataProvider()

    assert window.centralWidget().__class__ == AdjustTimeouts(data_provider).__class__


def test_logs_window(window, qtbot):
    """ Tests if it is possible to open logs window.
    """
    window.show()
    window.show_logs_action.trigger()

    assert window.show_logs_window.isVisible()
    assert window.show_logs_window.windowTitle() == 'Logs'


def test_help_window(window, qtbot):
    """ Tests if it is possible to open help window.
    """
    window.show()
    window.see_help_action.trigger()

    assert window.help_window.isVisible()
    assert window.help_window.windowTitle() == 'Help'


def test_about_window(window, qtbot):
    """ Tests if it is possible to open help window.
    """
    window.show()
    window.about_the_program_action.trigger()

    assert window.program_info_window.isVisible()
    assert window.program_info_window.windowTitle() == 'About'


