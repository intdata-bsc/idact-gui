from PyQt5.QtCore import pyqtSignal, QObject
from idact.core.environment import load_environment
from idact.detail.environment.environment_provider import EnvironmentProvider


class DataProvider(QObject):
    add_cluster_signal = pyqtSignal()
    remove_cluster_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.cluster_names = []
        self.load_cluster_names()

    def load_cluster_names(self):
        load_environment()
        self.cluster_names = list(EnvironmentProvider().environment.clusters.keys())

    def get_cluster_names(self):
        self.load_cluster_names()
        return self.cluster_names
