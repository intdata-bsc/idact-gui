from gui.decorators import addToClass
from idact.detail.jupyter_app.main import main as deploy_notebook
from gui.idact_app import IdactApp


class IdactNotebook:
    def __init__(self, idact_app):
        idact_app.ui.deploy_button.clicked.connect(idact_app.deploy_notebook)

    @addToClass(IdactApp)
    def deploy_notebook(self):
        cluster_name = self.ui.cluster_name_deployn_edit.text()
        nodes = int(self.ui.nodes_edit.text())
        cores = int(self.ui.cores_edit.text())
        memory = self.ui.memory_edit.text()
        unit = self.ui.memory_unit_box.currentText()
        walltime = self.ui.walltime_edit.text()

        deploy_notebook(cluster_name=cluster_name,
                        environment=None,
                        save_defaults=False,
                        reset_defaults=False,
                        nodes=nodes,
                        cores=cores,
                        memory_per_node=memory+unit,
                        walltime=walltime,
                        native_arg=[
                            ('--partition', 'plgrid-testing')  # TODO
                        ])


