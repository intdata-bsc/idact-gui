from PyQt5.QtWidgets import QTableWidgetItem

from gui.helpers.decorators import addToClass
from gui.functionality.idact_app import IdactApp, WindowType
from gui.helpers.worker import Worker
from idact import load_environment, show_cluster, Walltime
from idact.detail.config.client.client_cluster_config import ClusterConfigImpl
from idact.detail.deployment.cancel_local_on_exit import cancel_local_on_exit
from idact.detail.deployment.cancel_on_exit import cancel_on_exit
from idact.detail.jupyter_app.app_allocation_parameters import \
    AppAllocationParameters
from idact.detail.jupyter_app.native_args_conversion import \
    convert_native_args_from_command_line_to_dict
from idact.detail.jupyter_app.override_parameters_if_possible import \
    override_parameters_if_possible
from idact.detail.jupyter_app.sleep_until_allocation_ends import \
    sleep_until_allocation_ends

from contextlib import ExitStack


class IdactNotebook:
    def __init__(self, idact_app):
        idact_app.ui.deploy_button.clicked.connect(idact_app.concurrent_deploy_notebook)
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
    def concurrent_deploy_notebook(self):
        worker = Worker(self.deploy_notebook)
        worker.signals.result.connect(self.handle_complete_deploy_notebook)
        worker.signals.error.connect(self.handle_error_deploy_notebook)
        self.threadpool.start(worker)
    
    @addToClass(IdactApp)
    def handle_complete_deploy_notebook(self):
        self.popup_window.show_message("Notebook has been closed", WindowType.success)
    
    @addToClass(IdactApp)
    def handle_error_deploy_notebook(self):
        self.popup_window.show_message("An error occured while deploing notebook", WindowType.error)
        self.ui.deploy_button.setEnabled(True)

    @addToClass(IdactApp)
    def deploy_notebook(self):
        self.ui.deploy_button.setEnabled(False)

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

        if len(walltime) == 0:
            raise ValueError('Walltime cannot be empty.')

        if ':' not in walltime:
            walltime_elements = walltime.split(" ")

            days = 0
            hours = 0
            minutes = 0
            seconds = 0

            for element in walltime_elements:
                letter = element[len(element) - 1]

                if letter == 'd':
                    if days != 0:
                        raise ValueError('Wrong walltime format. Days parameter is multiple defined.')
                    days = int(element[0:len(element)-1])
                elif letter == 'h':
                    if hours != 0:
                        raise ValueError('Wrong walltime format. Hours parameter is multiple defined.')
                    hours = int(element[0:len(element) - 1])
                elif letter == 'm':
                    if minutes != 0:
                        raise ValueError('Wrong walltime format. Minutes parameter is multiple defined.')
                    minutes = int(element[0:len(element) - 1])
                elif letter == 's':
                    if seconds != 0:
                        raise ValueError('Wrong walltime format. Seconds parameter is multiple defined.')
                    seconds = int(element[0:len(element) - 1])
                else:
                    raise ValueError('Wrong walltime format.')

            walltime = Walltime(days=days, hours=hours, minutes=minutes, seconds=seconds)

        
        with ExitStack() as stack:
            load_environment()

            cluster = show_cluster(name=cluster_name)

            config = cluster.config
            assert isinstance(config, ClusterConfigImpl)
            parameters = AppAllocationParameters.deserialize(
                serialized=config.notebook_defaults)

            native = self.native_args_saver.get_native_args_list()
            override_parameters_if_possible(parameters=parameters,
                                            nodes=nodes,
                                            cores=cores,
                                            memory_per_node=memory+unit,
                                            walltime=walltime,
                                            native_args=native)
            nodes = cluster.allocate_nodes(
                nodes=parameters.nodes,
                cores=parameters.cores,
                memory_per_node=parameters.memory_per_node,
                walltime=parameters.walltime,
                native_args=convert_native_args_from_command_line_to_dict(
                    native_args=parameters.native_args))
            stack.enter_context(cancel_on_exit(nodes))
            nodes.wait()

            notebook = nodes[0].deploy_notebook()
            stack.enter_context(cancel_local_on_exit(notebook))

            cluster.push_deployment(nodes)

            cluster.push_deployment(notebook)

            notebook.open_in_browser()
            self.ui.deploy_button.setEnabled(True)
            sleep_until_allocation_ends(nodes=nodes)
        return

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
