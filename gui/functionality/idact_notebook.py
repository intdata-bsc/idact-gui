from gui.decorators import addToClass
from idact.detail.jupyter_app.main import main as deploy_notebook
from gui.idact_app import IdactApp


class IdactNotebook:
    def __init__(self, idact_app):
        idact_app.ui.deploy_button.clicked.connect(idact_app.deploy_notebook)
        idact_app.ui.cluster_name_deployn_edit.setText(idact_app.parameters['deploy_notebook_arguments']['cluster_name'])
        idact_app.ui.nodes_edit.setValue(idact_app.parameters['deploy_notebook_arguments']['nodes'])
        idact_app.ui.cores_edit.setValue(idact_app.parameters['deploy_notebook_arguments']['cores'])
        idact_app.ui.memory_edit.setValue(int(idact_app.parameters['deploy_notebook_arguments']['memory_value']))
        idact_app.ui.memory_unit_box.setCurrentText(idact_app.parameters['deploy_notebook_arguments']['memory_unit'])
        idact_app.ui.walltime_edit.setText(idact_app.parameters['deploy_notebook_arguments']['walltime'])

    @addToClass(IdactApp)
    def deploy_notebook(self):
        cluster_name = self.ui.cluster_name_deployn_edit.text()
        self.parameters['deploy_notebook_arguments']['cluster_name'] = cluster_name
        nodes = int(self.ui.nodes_edit.text())
        self.parameters['deploy_notebook_arguments']['nodes'] = nodes
        cores = int(self.ui.cores_edit.text())
        self.parameters['deploy_notebook_arguments']['cores'] = cores
        memory = self.ui.memory_edit.text()
        self.parameters['deploy_notebook_arguments']['memory_value'] = memory
        unit = self.ui.memory_unit_box.currentText()
        self.parameters['deploy_notebook_arguments']['memory_unit'] = unit
        walltime = self.ui.walltime_edit.text()
        self.parameters['deploy_notebook_arguments']['walltime'] = walltime
        self.saver.save(self.parameters)

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


