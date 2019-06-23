from PyQt5.QtWidgets import QTableWidgetItem

from gui.decorators import addToClass
from idact.detail.jupyter_app.main import main as deploy_notebook
from gui.idact_app import IdactApp, AddArgumentApp


class IdactNotebook:
    def __init__(self, idact_app):
        idact_app.ui.deploy_button.clicked.connect(idact_app.deploy_notebook)
        idact_app.ui.add_native_argument_button.clicked.connect(idact_app.open_new_native_argument)
        idact_app.ui.remove_native_argument_button.clicked.connect(idact_app.open_remove_native_argument)
        idact_app.ui.show_native_arguments_button.clicked.connect(idact_app.open_show_native_argument)

        idact_app.ui.cluster_name_deployn_edit.setText(idact_app.parameters['deploy_notebook_arguments']['cluster_name'])
        idact_app.ui.nodes_edit.setValue(idact_app.parameters['deploy_notebook_arguments']['nodes'])
        idact_app.ui.cores_edit.setValue(idact_app.parameters['deploy_notebook_arguments']['cores'])
        idact_app.ui.memory_edit.setValue(int(idact_app.parameters['deploy_notebook_arguments']['memory_value']))
        idact_app.ui.memory_unit_box.setCurrentText(idact_app.parameters['deploy_notebook_arguments']['memory_unit'])
        idact_app.ui.walltime_edit.setText(idact_app.parameters['deploy_notebook_arguments']['walltime'])

        idact_app.add_argument_window.ui.add_native_button.clicked.connect(idact_app.add_new_native_argument)
        idact_app.add_argument_window.ui.argument_name_edit.setText(idact_app.parameters['add_native_arguments']['argument_name'])
        idact_app.add_argument_window.ui.value_name_edit.setText(idact_app.parameters['add_native_arguments']['value'])

        idact_app.remove_argument_window.ui.remove_native_button.clicked.connect(idact_app.remove_native_argument)
        idact_app.remove_argument_window.ui.argument_name_edit.setText(idact_app.parameters['remove_native_arguments']['argument_name'])

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
                        native_arg=self.native_args_saver.get_native_args_list())

    @addToClass(IdactApp)
    def open_new_native_argument(self):
        self.add_argument_window.show()

    @addToClass(IdactApp)
    def add_new_native_argument(self):
        argument_name = self.add_argument_window.ui.argument_name_edit.text()
        self.parameters['add_native_arguments']['argument_name'] = argument_name
        value = self.add_argument_window.ui.value_name_edit.text()
        self.parameters['add_native_arguments']['value'] = value
        self.saver.save(self.parameters)

        self.native_args_saver.add_to_list(('--'+argument_name, value))

    @addToClass(IdactApp)
    def open_remove_native_argument(self):
        self.remove_argument_window.show()

    @addToClass(IdactApp)
    def remove_native_argument(self):
        argument_name = self.remove_argument_window.ui.argument_name_edit.text()
        self.parameters['remove_native_arguments']['argument_name'] = argument_name
        self.saver.save(self.parameters)

        self.native_args_saver.remove_native_arg(argument_name)

    @addToClass(IdactApp)
    def open_show_native_argument(self):
        native_args_list = self.native_args_saver.get_native_args_list()
        counter = len(native_args_list)
        self.show_native_arguments_window.ui.table_widget.setRowCount(counter)
        self.show_native_arguments_window.ui.table_widget.setColumnCount(2)

        for i in range(counter):
            self.show_native_arguments_window.ui.table_widget.setItem(i, 0, QTableWidgetItem(native_args_list[i][0]))
            self.show_native_arguments_window.ui.table_widget.setItem(i, 1, QTableWidgetItem(native_args_list[i][1]))
        self.show_native_arguments_window.show()
