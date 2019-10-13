
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QVBoxLayout, QWidget

from idact.core.remove_cluster import remove_cluster
from idact import save_environment, load_environment

from gui.functionality.popup_window import WindowType, PopUpWindow
from gui.helpers.worker import Worker


class RemoveCluster(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.parent = parent

        self.popup_window = PopUpWindow()

        ui_path = os.path.dirname(os.path.abspath(__file__))
        self.ui = uic.loadUi(os.path.join(ui_path, '../widgets_templates/remove-cluster.ui'))
        
        self.ui.remove_cluster_button.clicked.connect(self.concurrent_remove_cluster)
        self.ui.cluster_name_removec_edit.setText(self.parent.parameters['remove_cluster_arguments']['cluster_name'])

        lay = QVBoxLayout(self)
        lay.addWidget(self.ui)
     
    def concurrent_remove_cluster(self):
        worker = Worker(self.remove_cluster)
        worker.signals.result.connect(self.handle_complete_remove_cluster)
        worker.signals.error.connect(self.handle_error_remove_cluster)
        self.parent.threadpool.start(worker) 
    
    def handle_complete_remove_cluster(self):
        index = self.ui.cluster_names_box.findText(self.ui.cluster_name_removec_edit.text())
        self.ui.cluster_names_box.removeItem(index)
        self.popup_window.show_message("The cluster has been successfully removed", WindowType.success)
    
    def handle_error_remove_cluster(self, exception):
        if isinstance(exception, KeyError):
            self.popup_window.show_message("The cluster does not exist", WindowType.error)
        else:
            self.popup_window.show_message("An error occured while removing cluster", WindowType.error)

    def remove_cluster(self):
        load_environment()

        cluster_name = self.ui.cluster_name_removec_edit.text()
        self.parent.parameters['remove_cluster_arguments']['cluster_name'] = cluster_name
        self.parent.saver.save(self.parameters)
        
        remove_cluster(cluster_name)
        save_environment()
        return



