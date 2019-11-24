""" One of the widgets that main window composes of.

    See :class:`.MainWindow`
    Similar modules: class:`.AddCluster`, :class:`.RemoveCluster`,
    :class:`.AdjustTimeouts`, :class:`.ManageJobs`
    Helpers: class:`.EditNativeArgumentsWindow`
"""
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QMessageBox
from idact import load_environment, show_cluster, Walltime
from idact.detail.config.client.client_cluster_config import ClusterConfigImpl
from idact.detail.jupyter_app.app_allocation_parameters import \
    AppAllocationParameters
from idact.detail.jupyter_app.override_parameters_if_possible import \
    override_parameters_if_possible

from gui.functionality.popup_window import WindowType, PopUpWindow
from gui.functionality.yes_or_no_window import YesOrNoWindow
from gui.helpers.custom_exceptions import NoClustersError
from gui.helpers.native_saver import NativeArgsSaver
from gui.helpers.parameter_saver import ParameterSaver
from gui.helpers.ui_loader import UiLoader
from gui.helpers.worker import Worker


class IdactNotebook(QWidget):
    """ Module of GUI that is responsible for deploying the notebook
    on the selected cluster.
    """

    def __init__(self, data_provider, parent=None):
        super().__init__(parent=parent)
        self.ui = UiLoader.load_ui_from_file('deploy-notebook.ui', self)

        self.parent = parent
        self.data_provider = data_provider

        self.edit_native_arguments_window = EditNativeArgumentsWindow()
        self.popup_window = PopUpWindow()
        self.native_args_saver = NativeArgsSaver()
        self.saver = ParameterSaver()
        self.parameters = self.saver.get_map()
        self.cluster = None

        self.ui.deploy_button.clicked.connect(self.concurrent_deploy_notebook)
        self.ui.edit_native_arguments_button.clicked.connect(self.open_edit_native_argument)

        self.ui.nodes_edit.setValue(self.parameters['deploy_notebook_arguments']['nodes'])
        self.ui.cores_edit.setValue(self.parameters['deploy_notebook_arguments']['cores'])
        self.ui.memory_edit.setValue(int(self.parameters['deploy_notebook_arguments']['memory_value']))
        self.ui.memory_unit_box.setCurrentText(self.parameters['deploy_notebook_arguments']['memory_unit'])
        self.ui.walltime_edit.setText(self.parameters['deploy_notebook_arguments']['walltime'])

        self.edit_native_arguments_window.ui.add_argument_button.clicked.connect(self.add_argument_row)
        self.edit_native_arguments_window.ui.remove_arguments_button.clicked.connect(self.remove_arguments)
        self.edit_native_arguments_window.ui.table_widget.itemSelectionChanged.connect(
            lambda: self.edit_native_arguments_window.ui.remove_arguments_button.setEnabled(
                len(self.edit_native_arguments_window.ui.table_widget.selectedIndexes()) > 0))
        self.edit_native_arguments_window.ui.save_arguments_button.clicked.connect(self.save_arguments)

        self.cluster_names = self.data_provider.get_cluster_names()

        self.data_provider.remove_cluster_signal.connect(self.handle_cluster_list_modification)
        self.data_provider.add_cluster_signal.connect(self.handle_cluster_list_modification)
        self.ui.cluster_names_box.addItems(self.cluster_names)

        self.ui.allocate_nodes_button.clicked.connect(self.concurrent_allocate_nodes)
        self.ui.begin_label.setDisabled(True)
        self.ui.begin_edit.setDisabled(True)
        self.ui.future_allocation.toggled.connect(self.change_buttons_to_disabled_or_not)

    def change_buttons_to_disabled_or_not(self):
        if self.ui.future_allocation.isChecked():
            self.ui.deploy_button.setDisabled(True)
            self.ui.begin_label.setDisabled(False)
            self.ui.begin_edit.setDisabled(False)

        else:
            self.ui.deploy_button.setDisabled(False)
            self.ui.begin_label.setDisabled(True)
            self.ui.begin_edit.setDisabled(True)

    def concurrent_allocate_nodes(self):
        self.ui.allocate_nodes_button.setEnabled(False)
        self.ui.deploy_button.setEnabled(False)
        worker = Worker(self.allocate_nodes)
        worker.signals.result.connect(self.handle_complete_allocate_nodes)
        worker.signals.error.connect(self.handle_error_allocate_nodes)
        self.parent.threadpool.start(worker)

    def handle_complete_allocate_nodes(self):
        self.ui.allocate_nodes_button.setEnabled(True)
        self.ui.deploy_button.setEnabled(True)
        self.popup_window.show_message("Nodes allocation has been submitted. \nYou can see job status in "
                                       "Notebooks->Manage Jobs", WindowType.success)

    def handle_error_allocate_nodes(self, exception):
        self.ui.allocate_nodes_button.setEnabled(True)
        self.ui.deploy_button.setEnabled(True)
        self.popup_window.show_message("An error occurred while allocating nodes", WindowType.error, exception)

    def allocate_nodes(self):
        cluster_name = str(self.ui.cluster_names_box.currentText())

        self.parameters['deploy_notebook_arguments']['cluster_name'] = cluster_name
        nodes = int(self.ui.nodes_edit.text())
        self.parameters['deploy_notebook_arguments']['nodes'] = nodes
        cores = int(self.ui.cores_edit.text())
        self.parameters['deploy_notebook_arguments']['cores'] = cores
        memory = self.ui.memory_edit.text()
        self.parameters['deploy_notebook_arguments']['memory_value'] = memory
        unit = self.ui.memory_unit_box.currentText()
        self.parameters['deploy_notebook_arguments']['memory_unit'] = unit
        walltime = self.validate_and_format_walltime(self.ui.walltime_edit.text())
        self.parameters['deploy_notebook_arguments']['walltime'] = walltime
        self.saver.save(self.parameters)
        begin = self.ui.begin_edit.text()

        load_environment()
        self.cluster = show_cluster(name=cluster_name)

        config = self.cluster.config
        assert isinstance(config, ClusterConfigImpl)
        parameters = AppAllocationParameters.deserialize(
            serialized=config.notebook_defaults)

        native_args = self.get_prepared_native_args()
        if begin and self.ui.future_allocation.isChecked():
            native_args['--begin'] = begin

        override_parameters_if_possible(parameters=parameters,
                                        nodes=nodes,
                                        cores=cores,
                                        memory_per_node=memory + unit,
                                        walltime=walltime,
                                        native_args=native_args.items())
        return self.cluster.allocate_nodes(
            nodes=parameters.nodes,
            cores=parameters.cores,
            memory_per_node=parameters.memory_per_node,
            walltime=parameters.walltime,
            native_args=native_args)

    def concurrent_deploy_notebook(self):
        """ Setups the worker that allows to run the deploy_notebook functionality
        in the parallel thread.
        """
        self.ui.allocate_nodes_button.setEnabled(False)
        self.ui.deploy_button.setEnabled(False)

        worker = Worker(self.deploy_notebook)
        worker.signals.result.connect(self.handle_complete_deploy_notebook)
        worker.signals.error.connect(self.handle_error_deploy_notebook)
        self.parent.threadpool.start(worker)

    def handle_complete_deploy_notebook(self):
        """ Handles the completion of deploy of the notebook.
        """
        self.change_buttons_to_disabled_or_not()
        self.ui.deploy_button.setEnabled(True)
        self.popup_window.show_message("Notebook has been deployed", WindowType.success)

    def handle_error_deploy_notebook(self, exception):
        """ Handles the error thrown while deploying the notebook.

            :param exception: Instance of the exception.
        """
        self.change_buttons_to_disabled_or_not()
        if isinstance(exception, NoClustersError):
            self.popup_window.show_message("There are no added clusters", WindowType.error)
        else:
            self.popup_window.show_message("An error occurred while deploying notebook", WindowType.error, exception)

    def deploy_notebook(self):
        """ Main function responsible for deploying the notebook.
        """
        nodes = self.allocate_nodes()
        nodes.wait()

        notebook = nodes[0].deploy_notebook()

        self.cluster.push_deployment(nodes)
        self.cluster.push_deployment(notebook)

        notebook.open_in_browser()

    @staticmethod
    def validate_and_format_walltime(walltime):
        """ Checks if walltime is correct and converts it to a proper format.

        :param walltime: Walltime string to check and convert.
                         Expected format: [days-]hours:minutes:seconds (for example 00:10:00)
                         or {days}d {hours}h {minutes}m {seconds}s - not all necessary and in any order
                         (for example 20m 30s)
        """
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
                number = element[0:len(element) - 1]
                if not number.isdigit():
                    raise ValueError('Wrong walltime format.')

                if letter == 'd':
                    if days != 0:
                        raise ValueError('Wrong walltime format. Days parameter is multiple defined.')
                    days = int(number)
                elif letter == 'h':
                    if hours != 0:
                        raise ValueError('Wrong walltime format. Hours parameter is multiple defined.')
                    hours = int(number)
                elif letter == 'm':
                    if minutes != 0:
                        raise ValueError('Wrong walltime format. Minutes parameter is multiple defined.')
                    minutes = int(number)
                elif letter == 's':
                    if seconds != 0:
                        raise ValueError('Wrong walltime format. Seconds parameter is multiple defined.')
                    seconds = int(number)
                else:
                    raise ValueError('Wrong walltime format.')

            walltime = str(Walltime(days=days, hours=hours, minutes=minutes, seconds=seconds))

        else:
            try:
                Walltime.from_string(walltime)
            except ValueError:
                raise ValueError('Wrong walltime format.')

        return walltime

    def get_prepared_native_args(self):
        """ Fetches the saved native_args from the native_args.json file.
        Converts them into proper format.
        """
        args = self.native_args_saver.get_native_args().copy()
        keys = list(args)

        for key in keys:
            if not key.startswith('--'):
                args['--' + key] = args.pop(key)
        return args

    def open_edit_native_argument(self):
        """ Opens the window with native arguments edition.
        """
        native_args = self.native_args_saver.get_native_args()
        counter = len(native_args)

        self.edit_native_arguments_window.ui.table_widget.setRowCount(counter)
        self.edit_native_arguments_window.ui.remove_arguments_button.setEnabled(False)

        row = 0
        for key in native_args.keys():
            self.edit_native_arguments_window.ui.table_widget.setItem(row, 0, QTableWidgetItem(key))
            self.edit_native_arguments_window.ui.table_widget.setItem(row, 1, QTableWidgetItem(native_args[key]))
            row += 1

        self.edit_native_arguments_window.show()
        self.edit_native_arguments_window.data_changed = False
        self.edit_native_arguments_window.ui.table_widget.cellChanged.connect(
            self.edit_native_arguments_window.set_that_data_changed)

    def add_argument_row(self):
        """ Adds the empty row to the native arguments table.
        """
        self.edit_native_arguments_window.ui.table_widget.setRowCount(
            self.edit_native_arguments_window.ui.table_widget.rowCount() + 1)

    def remove_arguments(self):
        """ Removes the selected native argument.
        """
        indexes = self.edit_native_arguments_window.ui.table_widget.selectedIndexes()

        for index in sorted(indexes, reverse=True):
            self.edit_native_arguments_window.ui.table_widget.removeRow(index.row())

        self.edit_native_arguments_window.set_that_data_changed()

    def save_arguments(self):
        """ Saves edited native arguments.
        """
        native_args = dict()

        for i in range(self.edit_native_arguments_window.ui.table_widget.rowCount()):
            name_item = self.edit_native_arguments_window.ui.table_widget.item(i, 0)
            value_item = self.edit_native_arguments_window.ui.table_widget.item(i, 1)

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
        self.edit_native_arguments_window.data_changed = False
        self.edit_native_arguments_window.close()

    def handle_cluster_list_modification(self):
        """ Handles the modification of the clusters list.
        """
        self.cluster_names = self.data_provider.get_cluster_names()
        self.ui.cluster_names_box.clear()
        self.ui.cluster_names_box.addItems(self.cluster_names)


class EditNativeArgumentsWindow(QWidget):
    """ Helper widget window for idact notebook native arguments.
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.ui = UiLoader.load_ui_from_file('edit-native.ui', self)

        self.data_changed = False
        self.yes_or_no_window = YesOrNoWindow()

    def set_that_data_changed(self):
        self.data_changed = True

    def show_warning_window(self, event):
        """ Shows warning window that some changes may not have been saved.

            :param event: close event
        """
        close_window = self.yes_or_no_window.show_message(
            "Some changes may not have been saved. \nDo you want to quit anyway?")
        self.yes_or_no_window.box.setDefaultButton(QMessageBox.No)
        if not close_window:
            event.ignore()

    def closeEvent(self, QCloseEvent):
        """ Overriden method on closing Edit native arguments window.

            :param QCloseEvent: close event
        """
        if self.data_changed:
            self.show_warning_window(QCloseEvent)
