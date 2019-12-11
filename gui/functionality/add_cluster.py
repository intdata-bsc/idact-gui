""" One of the widgets that main window composes of.

    See :class:`.MainWindow`
    Similar modules: :class:`.RemoveCluster`, :class:`.IdactNotebook`,
    :class:`.AdjustTimeouts`, :class:`.ManageJobs`
"""
from PyQt5.QtWidgets import QWidget, QLineEdit, QFileDialog

from idact.core.auth import AuthMethod, KeyType
from idact.core.add_cluster import add_cluster
from idact.detail.config.client.setup_actions_config import SetupActionsConfigImpl
from idact.detail.add_cluster_app import actions_parser as parser
from idact import save_environment, load_environment

from gui.functionality.loading_window import LoadingWindow
from gui.functionality.popup_window import WindowType, PopUpWindow
from gui.helpers.parameter_saver import ParameterSaver
from gui.helpers.ui_loader import UiLoader
from gui.helpers.worker import Worker
from gui.helpers.custom_exceptions import EmptyFieldError


class AddCluster(QWidget):
    """ Module of GUI that is responsible for allowing the addition of the
    new cluster.
    """

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.ui = UiLoader.load_ui_from_file('add-cluster.ui', self)

        self.parent = parent

        self.popup_window = PopUpWindow()
        self.loading_window = LoadingWindow()
        self.saver = ParameterSaver()
        self.parameters = self.saver.get_map()

        self.ui.password_edit.setEchoMode(QLineEdit.Password)
        self.ui.add_cluster_button.clicked.connect(self.concurrent_add_cluster)
        self.ui.cluster_name_addc_edit.setText(self.parameters['add_cluster_arguments']['cluster_name'])
        self.ui.user_edit.setText(self.parameters['add_cluster_arguments']['user'])
        self.ui.host_edit.setText(self.parameters['add_cluster_arguments']['host'])
        self.ui.port_edit.setValue(self.parameters['add_cluster_arguments']['port'])
        self.ui.add_actions_file_button.clicked.connect(self.open_actions_file_dialog)
        self.ui.clear_actions_file_button.clicked.connect(self.clear_actions_file)
        self.ui.add_key_button.clicked.connect(self.add_key)
        self.ui.clear_key_button.clicked.connect(self.clear_key)
        self.ui.auth_method_box.currentIndexChanged.connect(self.auth_method_toggled)
        self.actions_file_name = None
        self.key_path = None

    def auth_method_toggled(self):
        """ Handles the change of authentication method.
        """
        if self.ui.auth_method_box.currentText() == 'GENERATE_KEY':
            self.ui.password_label.setDisabled(False)
            self.ui.password_edit.setDisabled(False)
            self.ui.private_key_label.setDisabled(True)
            self.ui.currently_selected_key.setDisabled(True)
            self.ui.add_key_button.setDisabled(True)
            self.ui.clear_key_button.setDisabled(True)
        else:
            self.ui.password_label.setDisabled(True)
            self.ui.password_edit.setDisabled(True)
            self.ui.private_key_label.setDisabled(False)
            self.ui.currently_selected_key.setDisabled(False)
            self.ui.add_key_button.setDisabled(False)
            self.ui.clear_key_button.setDisabled(True)

        if self.key_path is not None:
            self.ui.clear_key_button.setDisabled(False)

    def concurrent_add_cluster(self):
        """ Setups the worker that allows to run the add_cluster functionality
        in the parallel thread.
        """
        self.loading_window.show_message("Cluster is being added and tested")
        self.ui.add_cluster_button.setDisabled(True)

        worker = Worker(self.add_cluster)
        worker.signals.result.connect(self.handle_complete_add_cluster)
        worker.signals.error.connect(self.handle_error_add_cluster)
        self.parent.threadpool.start(worker)

    def handle_complete_add_cluster(self):
        """ Handles the completion of adding cluster.
        """
        self.loading_window.close()
        self.ui.add_cluster_button.setDisabled(False)
        save_environment()
        self.parent.data_provider.add_cluster_signal.emit()
        self.popup_window.show_message("The cluster has been successfully added", WindowType.success)

    def handle_error_add_cluster(self, exception):
        """ Handles the error thrown while adding a cluster.

            :param exception: Instance of the exception.
        """
        self.loading_window.close()
        self.ui.add_cluster_button.setDisabled(False)
        if isinstance(exception, EmptyFieldError):
            self.popup_window.show_message("Cluster name cannot be empty", WindowType.error)
        elif isinstance(exception, ValueError):
            self.popup_window.show_message("Cluster already exists", WindowType.error)
        else:
            self.popup_window.show_message("An error occurred while adding cluster", WindowType.error, exception)

    def add_cluster(self):
        """ Main function responsible for adding a cluster.
        """
        load_environment()

        cluster_name = self.ui.cluster_name_addc_edit.text()

        if not cluster_name:
            raise EmptyFieldError()

        self.parameters['add_cluster_arguments']['cluster_name'] = cluster_name
        user = self.ui.user_edit.text()
        self.parameters['add_cluster_arguments']['user'] = user
        host = self.ui.host_edit.text()
        self.parameters['add_cluster_arguments']['host'] = host
        port = int(self.ui.port_edit.text())
        self.parameters['add_cluster_arguments']['port'] = port
        self.saver.save(self.parameters)
        auth = self.ui.auth_method_box.currentText()
        password = self.ui.password_edit.text()
        use_jupyter_lab = self.ui.use_jupyter_lab_check_box.isChecked()

        setup_actions = None
        if self.actions_file_name is not None:
            setup_actions = SetupActionsConfigImpl()
            setup_actions.jupyter = parser.parse_actions(self.actions_file_name)

        if auth == 'GENERATE_KEY':
            cluster = add_cluster(name=cluster_name,
                                  user=user,
                                  host=host,
                                  port=port,
                                  auth=AuthMethod.GENERATE_KEY,
                                  key=KeyType.RSA,
                                  install_key=True,
                                  setup_actions=setup_actions,
                                  use_jupyter_lab=use_jupyter_lab)
            node = cluster.get_access_node()
            node.connect(password=password)
        else:
            cluster = add_cluster(name=cluster_name,
                                  user=user,
                                  host=host,
                                  port=port,
                                  auth=AuthMethod.PRIVATE_KEY,
                                  key=self.key_path,
                                  install_key=False,
                                  setup_actions=setup_actions,
                                  use_jupyter_lab=use_jupyter_lab)
            node = cluster.get_access_node()
            node.connect()

    def open_actions_file_dialog(self):
        """ Opens the window dialog that allows to select an actions file.
        """
        self.actions_file_name, _ = QFileDialog.getOpenFileName()
        if self.actions_file_name:
            self.ui.selected_file_path_browser.setText(self.actions_file_name)
            self.ui.selected_file_path_browser.setEnabled(True)
            self.ui.clear_actions_file_button.setEnabled(True)

    def clear_actions_file(self):
        """ Removes the selection of the actions file.
        """
        self.actions_file_name = None
        self.ui.selected_file_path_browser.setText("")
        self.ui.selected_file_path_browser.setEnabled(False)
        self.ui.clear_actions_file_button.setEnabled(False)

    def add_key(self):
        """ Opens the window dialog that allows to select a private key file.
        """
        self.key_path, _ = QFileDialog.getOpenFileName()
        if self.key_path:
            self.ui.selected_key_browser.setText(self.key_path)
            self.ui.selected_key_browser.setEnabled(True)
            self.ui.clear_key_button.setEnabled(True)

    def clear_key(self):
        """ Removes the selection of the private key file.
        """
        self.key_path = None
        self.ui.selected_key_browser.setText("")
        self.ui.selected_key_browser.setEnabled(False)
        self.ui.clear_key_button.setEnabled(False)
