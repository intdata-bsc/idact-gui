import os
from enum import Enum
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidgetItem
from contextlib import ExitStack

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

from gui.functionality.popup_window import WindowType, PopUpWindow
from gui.helpers.worker import Worker

class IdactNotebook(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.parent = parent

        self.add_argument_window = AddArgumentWindow()
        self.remove_argument_window = RemoveArgumentWindow()
        self.show_native_arguments_window = ShowNativeArgumentsWindow()
        self.popup_window = PopUpWindow()

        ui_path = os.path.dirname(os.path.abspath(__file__))
        self.ui = uic.loadUi(os.path.join(ui_path, '../widgets_templates/deploy-notebook.ui'))
        # self.ui.cluster_name_deployn_edit.setText('ala')

        self.ui.deploy_button.clicked.connect(self.concurrent_deploy_notebook)
        self.ui.add_native_argument_button.clicked.connect(self.open_new_native_argument)
        self.ui.remove_native_argument_button.clicked.connect(self.open_remove_native_argument)
        self.ui.show_native_arguments_button.clicked.connect(self.open_show_native_argument)

        self.ui.cluster_name_deployn_edit.setText(self.parent.parameters['deploy_notebook_arguments']['cluster_name'])
        self.ui.nodes_edit.setValue(self.parent.parameters['deploy_notebook_arguments']['nodes'])
        self.ui.cores_edit.setValue(self.parent.parameters['deploy_notebook_arguments']['cores'])
        self.ui.memory_edit.setValue(int(self.parent.parameters['deploy_notebook_arguments']['memory_value']))
        self.ui.memory_unit_box.setCurrentText(self.parent.parameters['deploy_notebook_arguments']['memory_unit'])
        self.ui.walltime_edit.setText(self.parent.parameters['deploy_notebook_arguments']['walltime'])

        self.add_argument_window.ui.add_native_button.clicked.connect(self.add_new_native_argument)
        self.add_argument_window.ui.argument_name_edit.setText(self.parent.parameters['add_native_arguments']['argument_name'])
        self.add_argument_window.ui.value_name_edit.setText(self.parent.parameters['add_native_arguments']['value'])

        self.remove_argument_window.ui.remove_native_button.clicked.connect(self.remove_native_argument)
        self.remove_argument_window.ui.argument_name_edit.setText(self.parent.parameters['remove_native_arguments']['argument_name'])


        lay = QVBoxLayout(self)
        lay.addWidget(self.ui)
 
    def concurrent_deploy_notebook(self):
        worker = Worker(self.deploy_notebook)
        worker.signals.result.connect(self.handle_complete_deploy_notebook)
        worker.signals.error.connect(self.handle_error_deploy_notebook)
        self.parent.threadpool.start(worker)
        
    def handle_complete_deploy_notebook(self):
        self.popup_window.show_message("Notebook has been closed", WindowType.success)
    
    def handle_error_deploy_notebook(self):
        self.popup_window.show_message("An error occured while deploing notebook", WindowType.error)

    def deploy_notebook(self):
        cluster_name = self.ui.cluster_name_deployn_edit.text()
        self.parent.parameters['deploy_notebook_arguments']['cluster_name'] = cluster_name
        nodes = int(self.ui.nodes_edit.text())
        self.parent.parameters['deploy_notebook_arguments']['nodes'] = nodes
        cores = int(self.ui.cores_edit.text())
        self.parent.parameters['deploy_notebook_arguments']['cores'] = cores
        memory = self.ui.memory_edit.text()
        self.parent.parameters['deploy_notebook_arguments']['memory_value'] = memory
        unit = self.ui.memory_unit_box.currentText()
        self.parent.parameters['deploy_notebook_arguments']['memory_unit'] = unit
        walltime = self.ui.walltime_edit.text()
        self.parent.parameters['deploy_notebook_arguments']['walltime'] = walltime
        self.parent.saver.save(self.parameters)

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
            sleep_until_allocation_ends(nodes=nodes)
        return

    def open_new_native_argument(self):
        self.parent.add_argument_window.show()
    
    def open_remove_native_argument(self):
        self.parent.remove_argument_window.show()
    
    def open_show_native_argument(self):
        native_args_list = self.parent.native_args_saver.get_native_args_list()
        counter = len(native_args_list)
        self.parent.show_native_arguments_window.ui.table_widget.setRowCount(counter)
        self.parent.show_native_arguments_window.ui.table_widget.setColumnCount(2)

        for i in range(counter):
            self.parent.show_native_arguments_window.ui.table_widget.setItem(i, 0, QTableWidgetItem(native_args_list[i][0]))
            self.parent.show_native_arguments_window.ui.table_widget.setItem(i, 1, QTableWidgetItem(native_args_list[i][1]))
        self.parent.show_native_arguments_window.show()

    def add_new_native_argument(self):
        argument_name = self.add_argument_window.ui.argument_name_edit.text()
        self.parent.parameters['add_native_arguments']['argument_name'] = argument_name
        value = self.add_argument_window.ui.value_name_edit.text()
        self.parent.parameters['add_native_arguments']['value'] = value
        self.parent.saver.save(self.parameters)

        self.parent.native_args_saver.add_to_list(('--'+argument_name, value))

    def remove_native_argument(self):
        argument_name = self.remove_argument_window.ui.argument_name_edit.text()
        self.parent.parameters['remove_native_arguments']['argument_name'] = argument_name
        self.parent.saver.save(self.parameters)

        self.parent.native_args_saver.remove_native_arg(argument_name)


class AddArgumentWindow(QMainWindow):
    def __init__(self):
        super(AddArgumentWindow, self).__init__()
        self.ui = Ui_AddNativeArgument()
        self.ui.setupUi(self)


class RemoveArgumentWindow(QMainWindow):
    def __init__(self):
        super(RemoveArgumentWindow, self).__init__()
        self.ui = Ui_RemoveNativeArgument()
        self.ui.setupUi(self)


class ShowNativeArgumentsWindow(QMainWindow):
    def __init__(self):
        super(ShowNativeArgumentsWindow, self).__init__()
        self.ui = Ui_ShowNativeArgument()
        self.ui.setupUi(self)
