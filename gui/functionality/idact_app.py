import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PyQt5.QtCore import QThreadPool
from PyQt5 import uic
from idact import load_environment

from gui.functionality.idact_notebook import IdactNotebook
from gui.functionality.add_cluster import AddCluster
from gui.functionality.remove_cluster import RemoveCluster
from gui.functionality.manage_jobs import ManageJobs
from gui.functionality.adjust_timeouts import AdjustTimeouts

class IdactApp(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.setWindowTitle("Idact GUI")

        self.threadpool = QThreadPool()

        self.actions_file_name = None

        lay = QVBoxLayout(self)
        self.tabs = QTabWidget(self)
        self.tab1 = IdactNotebook(self)
        self.tab2 = AddCluster(self)
        self.tab3 = RemoveCluster(self)
        self.tab4 = AdjustTimeouts(self)
        self.tab5 = ManageJobs(self)
        self.tabs.addTab(self.tab1,"Deploy Notebook")
        self.tabs.addTab(self.tab2,"Add Cluster")
        self.tabs.addTab(self.tab3,"Remove Cluster")
        self.tabs.addTab(self.tab4,"Adjust Timeouts")
        self.tabs.addTab(self.tab5,"Manage Jobs")
        lay.addWidget(self.tabs)
    





