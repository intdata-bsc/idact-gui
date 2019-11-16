from PyQt5.QtWidgets import QWidget

from idact.core.remove_cluster import remove_cluster
from idact import save_environment, load_environment

from gui.functionality.popup_window import WindowType, PopUpWindow
from gui.helpers.parameter_saver import ParameterSaver
from gui.helpers.ui_loader import UiLoader
from gui.helpers.worker import Worker
from gui.helpers.custom_exceptions import NoClustersError


class RemoveCluster(QWidget):
    def __init__(self, data_provider, parent=None):
        super().__init__(parent=parent)
        self.ui = UiLoader.load_ui_from_file('remove-cluster.ui', self)

        self.parent = parent
        self.data_provider = data_provider

        self.popup_window = PopUpWindow()
        self.saver = ParameterSaver()
        self.parameters = self.saver.get_map()

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
        worker = Worker(self.remove_cluster)
        worker.signals.result.connect(self.handle_complete_remove_cluster)
        worker.signals.error.connect(self.handle_error_remove_cluster)
        self.parent.threadpool.start(worker)

    def handle_complete_remove_cluster(self):
        self.data_provider.remove_cluster_signal.emit()
        self.popup_window.show_message("The cluster has been successfully removed", WindowType.success)

    def handle_error_remove_cluster(self, exception):
        if isinstance(exception, NoClustersError):
            self.popup_window.show_message("There are no added clusters", WindowType.error)
        elif isinstance(exception, KeyError):
            self.popup_window.show_message("The cluster does not exist", WindowType.error)
        else:
            self.popup_window.show_message("An error occurred while removing cluster", WindowType.error, exception)

    def remove_cluster(self):
        load_environment()

        cluster_name = str(self.ui.cluster_names_box.currentText())

        if not cluster_name:
            raise NoClustersError()

        self.parameters['remove_cluster_arguments']['cluster_name'] = cluster_name
        self.saver.save(self.parameters)

        remove_cluster(cluster_name)
        save_environment()
        return

    def handle_cluster_list_modification(self):
        self.cluster_names = self.data_provider.get_cluster_names()
        self.ui.cluster_names_box.clear()
        self.ui.cluster_names_box.addItems(self.cluster_names)
