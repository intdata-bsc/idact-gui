""" Main module of the GUI application. It composes all the widgets
into one window.

    See: class:`.AddCluster`, :class:`.RemoveCluster`,
    :class:`.IdactNotebook`, :class:`.AdjustTimeouts`,
    :class:`.ManageJobs`
"""
import sys

from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QMainWindow

from gui.functionality.add_cluster import AddCluster
from gui.functionality.adjust_timeouts import AdjustTimeouts
from gui.functionality.idact_notebook import IdactNotebook
from gui.functionality.manage_jobs import ManageJobs
from gui.functionality.program_info_window import ProgramInfoWindow
from gui.functionality.remove_cluster import RemoveCluster
from gui.functionality.show_logs_window import ShowLogsWindow
from gui.helpers.data_provider import DataProvider
from gui.helpers.ui_loader import UiLoader


class MainWindow(QMainWindow):
    def __init__(self):
        self.show_logs_window = ShowLogsWindow()
        sys.stdout = self.show_logs_window
        sys.stderr = self.show_logs_window

        super(MainWindow, self).__init__()
        self.ui = UiLoader.load_ui_from_file('main-window.ui', self)

        self.data_provider = DataProvider()
        self.program_info_window = ProgramInfoWindow()
        self.actions_file_name = None
        self.threadpool = QThreadPool()

        self.setCentralWidget(IdactNotebook(self.data_provider, self))

        self.ui.deploy_notebook_action.triggered.connect(self.handle_deploy_notebook_action)
        self.ui.see_running_notebooks_action.triggered.connect(self.handle_see_running_notebooks_action)

        self.ui.add_cluster_action.triggered.connect(self.handle_add_cluster_action)
        self.ui.remove_cluster_action.triggered.connect(self.handle_remove_cluster_action)
        self.ui.edit_configuration_action.triggered.connect(self.handle_edit_configuration_action)

        self.ui.show_logs_action.triggered.connect(self.handle_show_logs_action)

        self.ui.see_help_action.triggered.connect(self.handle_see_help_action)
        self.ui.about_the_program_action.triggered.connect(self.handle_about_the_program_action)

    def handle_deploy_notebook_action(self):
        self.setCentralWidget(IdactNotebook(self.data_provider, self))

    def handle_see_running_notebooks_action(self):
        self.setCentralWidget(ManageJobs(self.data_provider, self))

    def handle_add_cluster_action(self):
        self.setCentralWidget(AddCluster(self.data_provider, self))

    def handle_remove_cluster_action(self):
        self.setCentralWidget(RemoveCluster(self.data_provider, self))

    def handle_edit_configuration_action(self):
        self.setCentralWidget(AdjustTimeouts(self.data_provider, self))

    def handle_show_logs_action(self):
        self.show_logs_window.show()

    def handle_see_help_action(self):
        pass

    def handle_about_the_program_action(self):
        self.program_info_window.show()
