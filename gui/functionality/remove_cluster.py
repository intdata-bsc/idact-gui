from gui.decorators import addToClass
from idact.core.remove_cluster import remove_cluster
from gui.idact_app import IdactApp


class RemoveCluster:
    def __init__(self, idact_app):
        idact_app.ui.remove_cluster_button.clicked.connect(idact_app.remove_cluster)

    @addToClass(IdactApp)
    def remove_cluster(self):
        cluster_name = self.ui.cluster_name_removec_edit.text()
        remove_cluster(cluster_name)

