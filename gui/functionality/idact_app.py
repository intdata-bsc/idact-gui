import sys

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QPushButton
from PyQt5.QtCore import QThreadPool

from gui.functionality.idact_notebook import IdactNotebook
from gui.functionality.add_cluster import AddCluster
from gui.functionality.remove_cluster import RemoveCluster
from gui.functionality.manage_jobs import ManageJobs
from gui.functionality.adjust_timeouts import AdjustTimeouts
from gui.functionality.show_logs_window import ShowLogsWindow


class IdactApp(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.setWindowTitle("Idact GUI")

        self.threadpool = QThreadPool()

        self.actions_file_name = None

        self.show_logs_window = ShowLogsWindow()
        sys.stdout = self.show_logs_window
        sys.stderr = self.show_logs_window

        lay = QVBoxLayout(self)
        self.tabs = QTabWidget(self)
        self.tab1 = IdactNotebook(self)
        self.tab2 = AddCluster(self)
        self.tab3 = RemoveCluster(self)
        self.tab4 = AdjustTimeouts(self)
        self.tab5 = ManageJobs(self)
        self.tabs.addTab(self.tab1, "Deploy Notebook")
        self.tabs.addTab(self.tab2, "Add Cluster")
        self.tabs.addTab(self.tab3, "Remove Cluster")
        self.tabs.addTab(self.tab4, "Adjust Timeouts")
        self.tabs.addTab(self.tab5, "Manage Jobs")
        lay.addWidget(self.tabs)

        logs_button = QPushButton('Show logs', self)
        logs_button.clicked.connect(self.show_logs_window.show)
        lay.addWidget(logs_button)
