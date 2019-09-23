from gui.helpers.decorators import addToClass
from gui.helpers.worker import Worker
from idact.core.remove_cluster import remove_cluster
from idact import save_environment, load_environment
from gui.functionality.idact_app import IdactApp, WindowType


class RemoveCluster:
    def __init__(self, idact_app):
        idact_app.ui.remove_cluster_button.clicked.connect(idact_app.concurrent_remove_cluster)
        idact_app.ui.cluster_name_removec_edit.setText(idact_app.parameters['remove_cluster_arguments']['cluster_name'])

    @addToClass(IdactApp)
    def concurrent_remove_cluster(self):
        worker = Worker(self.remove_cluster)
        worker.signals.result.connect(self.handle_complete_remove_cluster)
        worker.signals.error.connect(self.handle_error_remove_cluster)
        self.threadpool.start(worker) 
    
    @addToClass(IdactApp)
    def handle_complete_remove_cluster(self):
        self.popup_window.show_message("The cluster has been successfully removed", WindowType.success)
    
    @addToClass(IdactApp)
    def handle_error_remove_cluster(self, exception):
        if isinstance(exception, KeyError):
            self.popup_window.show_message("The cluster does not exist", WindowType.error)
        else:
            self.popup_window.show_message("An error occured while removing cluster", WindowType.error)


    @addToClass(IdactApp)
    def remove_cluster(self):
        load_environment()

        cluster_name = self.ui.cluster_name_removec_edit.text()
        self.parameters['remove_cluster_arguments']['cluster_name'] = cluster_name
        self.saver.save(self.parameters)
        
        remove_cluster(cluster_name)
        save_environment()

        return


