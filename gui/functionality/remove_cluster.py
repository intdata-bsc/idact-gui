import os
from PyQt5 import uic
from PyQt5.QtWidgets import QVBoxLayout, QWidget

from idact.core.remove_cluster import remove_cluster
from idact import save_environment, load_environment

from gui.functionality.popup_window import WindowType, PopUpWindow
from gui.helpers.parameter_saver import ParameterSaver
from gui.helpers.worker import Worker


class RemoveCluster(QWidget):
    def __init__(self, data_provider, parent=None):
        QWidget.__init__(self, parent=parent)
        self.parent = parent
        self.data_provider = data_provider

        self.popup_window = PopUpWindow()
        self.saver = ParameterSaver()
        self.parameters = self.saver.get_map()

        ui_path = os.path.dirname(os.path.abspath(__file__))
        self.ui = uic.loadUi(os.path.join(ui_path, '../widgets_templates/remove-cluster.ui'))

        self.ui.remove_cluster_button.clicked.connect(self.concurrent_remove_cluster)

        self.current_cluster = ''
        self.cluster_names = self.data_provider.get_cluster_names()

        if len(self.cluster_names) > 0:
            self.current_cluster = self.cluster_names[0]
        else:
            self.current_cluster = ''

        self.data_provider.remove_cluster_signal.connect(self.handle_cluster_name_change)
        self.data_provider.add_cluster_signal.connect(self.handle_cluster_name_change)
        self.ui.cluster_names_box.activated[str].connect(self.item_pressed)
        self.ui.cluster_names_box.addItems(self.cluster_names)

        lay = QVBoxLayout(self)
        lay.addWidget(self.ui)

    def concurrent_remove_cluster(self):
        worker = Worker(self.remove_cluster)
        worker.signals.result.connect(self.handle_complete_remove_cluster)
        worker.signals.error.connect(self.handle_error_remove_cluster)
        self.parent.threadpool.start(worker)

    def handle_complete_remove_cluster(self):
        self.data_provider.remove_cluster_signal.emit()
        self.popup_window.show_message("The cluster has been successfully removed", WindowType.success)

    def handle_error_remove_cluster(self, exception):
        if isinstance(exception, KeyError):
            self.popup_window.show_message("The cluster does not exist", WindowType.error)
        else:
            self.popup_window.show_message("An error occured while removing cluster", WindowType.error)

    def remove_cluster(self):
        load_environment()

        cluster_name = self.current_cluster
        self.parameters['remove_cluster_arguments']['cluster_name'] = cluster_name
        self.saver.save(self.parameters)

        remove_cluster(cluster_name)
        save_environment()
        return

    def handle_cluster_name_change(self):
        self.cluster_names = self.data_provider.get_cluster_names()
        self.ui.cluster_names_box.clear()
        self.ui.cluster_names_box.addItems(self.cluster_names)

    def item_pressed(self, item_pressed):
        self.current_cluster = item_pressed
