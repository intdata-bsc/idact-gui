""" One of the helpers for the gui application.

    Similar modules: class:`.NativeArgsSaver`, :class:`.ParameterSaver`,
    :class:`.UiLoader`, :class:`.Worker`, :class:`.ConfigurationProvider`
"""
from PyQt5.QtCore import pyqtSignal, QObject
from idact.core.environment import load_environment
from idact.detail.environment.environment_provider import EnvironmentProvider


class DataProvider(QObject):
    """ Provides the data about clusters inside the .idact.conf file.

        :attr:`.add_cluster_signal`: Signal used to inform about adding a new cluster.
        :attr:`.remove_cluster_signal`: Signal used to inform about removing a cluster.
    """
    add_cluster_signal = pyqtSignal()
    remove_cluster_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.cluster_names = []
        self.load_cluster_names()

    def load_cluster_names(self):
        """ Fetches the cluster names.
        """
        load_environment()
        self.cluster_names = list(EnvironmentProvider().environment.clusters.keys())

    def get_cluster_names(self):
        """ Returns fetched cluster names.
        """
        self.load_cluster_names()
        return self.cluster_names
