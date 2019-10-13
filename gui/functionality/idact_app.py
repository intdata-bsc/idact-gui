import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PyQt5.QtCore import QThreadPool
from PyQt5 import uic
from idact.detail.environment.environment_provider import EnvironmentProvider
from idact import load_environment

from gui.functionality.idact_notebook import IdactNotebook
from gui.functionality.add_cluster import AddCluster
from gui.functionality.remove_cluster import RemoveCluster
from gui.functionality.manage_jobs import ManageJobs
from gui.functionality.adjust_timeouts import AdjustTimeouts
from gui.helpers.native_saver import NativeArgsSaver
from gui.helpers.saver import ParameterSaver

class IdactApp(QWidget):
    def __init__(self):
        super(IdactApp, self).__init__()

        self.threadpool = QThreadPool()

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
        self.tabs.addTab(self.tab3,"Remove Cluster")
        self.tabs.addTab(self.tab4,"Adjust Timeouts")
        self.tabs.addTab(self.tab5,"Manage Jobs")
        lay.addWidget(self.tabs)
    
    def load_cluster_names(self):
        load_environment()
        self.cluster_names = list(EnvironmentProvider().environment.clusters.keys())





