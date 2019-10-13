import os
from enum import Enum
from PyQt5.QtWidgets import QMainWindow, QWidget, QMessageBox, QStackedWidget, QVBoxLayout, QTabWidget
from PyQt5.QtCore import QThreadPool
from PyQt5 import uic
from idact.detail.environment.environment_provider import EnvironmentProvider
from idact import load_environment

from gui.functionality.idact_notebook import IdactNotebook
from gui.functionality.remove_cluster import RemoveCluster
from gui.helpers.native_saver import NativeArgsSaver
from gui.helpers.saver import ParameterSaver

class IdactApp(QWidget):
    def __init__(self):
        super(IdactApp, self).__init__()

        self.threadpool = QThreadPool()
        self.popup_window = PopUpWindow()

        self.actions_file_name = None
        self.saver = ParameterSaver()
        self.native_args_saver = NativeArgsSaver()
        self.parameters = self.saver.get_map()
        self.cluster_names = []
        self.current_cluster = ''
        self.load_cluster_names()

        lay = QVBoxLayout(self)
        self.tabs = QTabWidget(self)
        self.tab1 = IdactNotebook(self)
        self.tab2 = AddCluster(self)
        self.tab3 = RemoveCluster(self)
        self.tab4 = AdjustTimeouts(self)
        self.tab5 = ManageJobs(self)
        self.tabs.addTab(self.tab1,"Deploy Notebook")
        self.tabs.addTab(self.tab2,"Add Cluster")
        self.tabs.addTab(self.tab2,"Remove Cluster")
        self.tabs.addTab(self.tab2,"Adjust Timeouts")
        self.tabs.addTab(self.tab2,"Manage Jobs")
        lay.addWidget(self.tabs)
    
    def load_cluster_names(self):
        load_environment()
        self.cluster_names = list(EnvironmentProvider().environment.clusters.keys())



class PopUpWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.box = QMessageBox(self)
        self.box.addButton(QMessageBox.Ok)
        self.box.setDefaultButton(QMessageBox.Ok)

    def show_message(self, message, window_type):
        if window_type == WindowType.success:
            self.box.setWindowTitle("Success")
            self.box.setIcon(QMessageBox.Information)
        elif window_type == WindowType.error:
            self.box.setWindowTitle("Error")
            self.box.setIcon(QMessageBox.Critical)
        else:
            self.box.setIcon(QMessageBox.NoIcon)

        self.box.setText(message)
        ret = self.box.exec_()
        if ret == QMessageBox.Ok:
            return


class WindowType(Enum):
    success = 1
    error = 2
