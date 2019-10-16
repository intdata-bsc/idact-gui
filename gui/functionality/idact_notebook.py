import os
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidgetItem
from contextlib import ExitStack

from idact import load_environment, show_cluster, Walltime
from idact.detail.config.client.client_cluster_config import ClusterConfigImpl
from idact.detail.deployment.cancel_local_on_exit import cancel_local_on_exit
from idact.detail.deployment.cancel_on_exit import cancel_on_exit
from idact.detail.jupyter_app.app_allocation_parameters import \
    AppAllocationParameters
from idact.detail.jupyter_app.override_parameters_if_possible import \
    override_parameters_if_possible
from idact.detail.jupyter_app.sleep_until_allocation_ends import \
    sleep_until_allocation_ends

from gui.functionality.popup_window import WindowType, PopUpWindow
from gui.helpers.native_saver import NativeArgsSaver
from gui.helpers.parameter_saver import ParameterSaver
from gui.helpers.worker import Worker


class IdactNotebook(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.parent = parent

        self.show_native_arguments_window = ShowNativeArgumentsWindow()
        self.popup_window = PopUpWindow()
        self.native_args_saver = NativeArgsSaver()
        self.saver = ParameterSaver()
        self.parameters = self.saver.get_map()

        ui_path = os.path.dirname(os.path.abspath(__file__))
        self.ui = uic.loadUi(os.path.join(ui_path, '../widgets_templates/deploy-notebook.ui'))

        self.ui.deploy_button.clicked.connect(self.concurrent_deploy_notebook)
        self.ui.show_native_arguments_button.clicked.connect(self.open_show_native_argument)

        self.ui.cluster_name_deployn_edit.setText(self.parameters['deploy_notebook_arguments']['cluster_name'])
        self.ui.nodes_edit.setValue(self.parameters['deploy_notebook_arguments']['nodes'])
        self.ui.cores_edit.setValue(self.parameters['deploy_notebook_arguments']['cores'])
        self.ui.memory_edit.setValue(int(self.parameters['deploy_notebook_arguments']['memory_value']))
        self.ui.memory_unit_box.setCurrentText(self.parameters['deploy_notebook_arguments']['memory_unit'])
        self.ui.walltime_edit.setText(self.parameters['deploy_notebook_arguments']['walltime'])

        self.show_native_arguments_window.ui.add_argument_button.clicked.connect(self.add_argument_row)
        self.show_native_arguments_window.ui.remove_arguments_button.clicked.connect(self.remove_arguments)
        self.show_native_arguments_window.ui.table_widget.itemSelectionChanged.connect(
            lambda: self.show_native_arguments_window.ui.remove_arguments_button.setEnabled(
                len(self.show_native_arguments_window.ui.table_widget.selectedIndexes()) > 0))
        self.show_native_arguments_window.ui.save_arguments_button.clicked.connect(self.save_arguments)

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

            native_args = self.prepare_native_args(self.native_args_saver.get_native_args())
            override_parameters_if_possible(parameters=parameters,
                                            nodes=nodes,
                                            cores=cores,
                                            memory_per_node=memory+unit,
                                            walltime=walltime,
                                            native_args=native_args.items())
            nodes = cluster.allocate_nodes(
                nodes=parameters.nodes,
                cores=parameters.cores,
                memory_per_node=parameters.memory_per_node,
                walltime=parameters.walltime,
                native_args=native_args)
            stack.enter_context(cancel_on_exit(nodes))
            nodes.wait()

            notebook = nodes[0].deploy_notebook()
            stack.enter_context(cancel_local_on_exit(notebook))

            cluster.push_deployment(nodes)

            cluster.push_deployment(notebook)

            notebook.open_in_browser()
            sleep_until_allocation_ends(nodes=nodes)
        return

    def prepare_native_args(self, args):
        prepared_args = args.copy()
        keys = list(prepared_args)

        for key in keys:
            if not key.startswith('--'):
                prepared_args['--'+key] = prepared_args.pop(key)
        return prepared_args

    def open_show_native_argument(self):
        native_args = self.native_args_saver.get_native_args()
        counter = len(native_args)

        self.show_native_arguments_window.ui.table_widget.setRowCount(counter)
        self.show_native_arguments_window.ui.remove_arguments_button.setEnabled(False)

        row = 0
        for key in native_args.keys():
            self.show_native_arguments_window.ui.table_widget.setItem(row, 0, QTableWidgetItem(key))
            self.show_native_arguments_window.ui.table_widget.setItem(row, 1, QTableWidgetItem(native_args[key]))
            row += 1

        self.show_native_arguments_window.show()

    def add_argument_row(self):
        self.show_native_arguments_window.ui.table_widget.setRowCount(
            self.show_native_arguments_window.ui.table_widget.rowCount() + 1)

    def remove_arguments(self):
        indexes = self.show_native_arguments_window.ui.table_widget.selectedIndexes()

        for index in sorted(indexes, reverse=True):
            self.show_native_arguments_window.ui.table_widget.removeRow(index.row())

    def save_arguments(self):
        native_args = dict()

        for i in range(self.show_native_arguments_window.ui.table_widget.rowCount()):
            name_item = self.show_native_arguments_window.ui.table_widget.item(i, 0)
            value_item = self.show_native_arguments_window.ui.table_widget.item(i, 1)

            name = None
            value = None
            if name_item is not None and value_item is not None:
                name = str(name_item.text())
                value = str(value_item.text())

            if not name or not value:
                self.popup_window.show_message("Name or value is empty", WindowType.error)
                return

            native_args[name] = value

        self.native_args_saver.save(native_args)
        self.show_native_arguments_window.close()


class ShowNativeArgumentsWindow(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.setWindowTitle('Show native arguments')
        
        ui_path = os.path.dirname(os.path.abspath(__file__))
        self.ui = uic.loadUi(os.path.join(ui_path, '../widgets_templates/show-native.ui'))
        
        lay = QVBoxLayout(self)
        lay.addWidget(self.ui)
