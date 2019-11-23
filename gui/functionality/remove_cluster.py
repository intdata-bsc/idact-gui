""" One of the widgets that main window composes of.

    See :class:`.MainWindow`
    Similar modules: class:`.AddCluster`, :class:`.IdactNotebook`,
    :class:`.AdjustTimeouts`, :class:`.ManageJobs`
"""
from PyQt5.QtWidgets import QWidget

from idact.core.remove_cluster import remove_cluster
from idact import save_environment, load_environment

from gui.functionality.popup_window import WindowType, PopUpWindow
from gui.helpers.ui_loader import UiLoader
from gui.helpers.worker import Worker
from gui.helpers.custom_exceptions import NoClustersError


class RemoveCluster(QWidget):
    """ Module of GUI that is responsible for the removal of the
    selected cluster.
    """

    def __init__(self, data_provider, parent=None):
        super().__init__(parent=parent)
        self.ui = UiLoader.load_ui_from_file('remove-cluster.ui', self)

        self.parent = parent
        self.data_provider = data_provider

        self.popup_window = PopUpWindow()

        self.ui.remove_cluster_button.clicked.connect(self.concurrent_remove_cluster)

        self.current_cluster = ''
        self.cluster_names = self.data_provider.get_cluster_names()

        if len(self.cluster_names) > 0:
            self.current_cluster = self.cluster_names[0]
        else:
            self.current_cluster = ''

        self.data_provider.remove_cluster_signal.connect(self.handle_cluster_list_modification)
        self.data_provider.add_cluster_signal.connect(self.handle_cluster_list_modification)
        self.ui.cluster_names_box.addItems(self.cluster_names)

    def concurrent_remove_cluster(self):
        """ Setups the worker that allows to run the remove_cluster functionality
        in the parallel thread.
        """
        worker = Worker(self.remove_cluster)
        worker.signals.result.connect(self.handle_complete_remove_cluster)
        worker.signals.error.connect(self.handle_error_remove_cluster)
        self.parent.threadpool.start(worker)

    def handle_complete_remove_cluster(self):
        """ Handles the completion of removing cluster.
        """
        self.data_provider.remove_cluster_signal.emit()
        self.popup_window.show_message("The cluster has been successfully removed", WindowType.success)

    def handle_error_remove_cluster(self, exception):
        """ Handles the error thrown while removing a cluster.

            :param exception: Instance of the exception.
        """
        if isinstance(exception, NoClustersError):
            self.popup_window.show_message("There are no added clusters", WindowType.error)
        elif isinstance(exception, KeyError):
            self.popup_window.show_message("The cluster does not exist", WindowType.error)
        else:
            self.popup_window.show_message("An error occurred while removing cluster", WindowType.error, exception)

    def remove_cluster(self):
        """ Main function responsible for removing a cluster.
        """
        load_environment()

        cluster_name = str(self.ui.cluster_names_box.currentText())

        if not cluster_name:
            raise NoClustersError()

        remove_cluster(cluster_name)
        save_environment()
        return

    def handle_cluster_list_modification(self):
        """ Handles the modification of the clusters list.
        """
        self.cluster_names = self.data_provider.get_cluster_names()
        self.ui.cluster_names_box.clear()
        self.ui.cluster_names_box.addItems(self.cluster_names)
