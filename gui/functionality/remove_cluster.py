from gui.helpers.decorators import addToClass
from idact.core.remove_cluster import remove_cluster
from idact import save_environment, load_environment
from gui.functionality.idact_app import IdactApp, WindowTitle


class RemoveCluster:
    def __init__(self, idact_app):
        idact_app.ui.remove_cluster_button.clicked.connect(idact_app.remove_cluster)
        idact_app.ui.cluster_name_removec_edit.setText(idact_app.parameters['remove_cluster_arguments']['cluster_name'])

    @addToClass(IdactApp)
    def remove_cluster(self):
        load_environment()

        cluster_name = self.ui.cluster_name_removec_edit.text()
        self.parameters['remove_cluster_arguments']['cluster_name'] = cluster_name
        self.saver.save(self.parameters)
        try:
            remove_cluster(cluster_name)
            save_environment()
            self.popUpWindow.show_message("The cluster has been successfully deleted", WindowTitle.success)
        except KeyError as e:
            self.popUpWindow.show_message("The cluster does not exist", WindowTitle.error)


