from PyQt5.QtWidgets import QWidget, QLineEdit, QFileDialog

from idact.core.auth import AuthMethod, KeyType
from idact.core.add_cluster import add_cluster
from idact.detail.config.client.setup_actions_config import SetupActionsConfigImpl
from idact.detail.add_cluster_app import actions_parser as parser
from idact import save_environment, load_environment

from gui.functionality.popup_window import WindowType, PopUpWindow
from gui.helpers.parameter_saver import ParameterSaver
from gui.helpers.ui_loader import UiLoader
from gui.helpers.worker import Worker
from gui.helpers.custom_exceptions import EmptyFieldError


class AddCluster(QWidget):

    def __init__(self, data_provider, parent=None):
        super().__init__(parent=parent)
        self.ui = UiLoader.load_ui_from_file('add-cluster.ui', self)

        self.parent = parent
        self.data_provider = data_provider

        self.popup_window = PopUpWindow()
        self.saver = ParameterSaver()
        self.parameters = self.saver.get_map()

        self.ui.password_edit.setEchoMode(QLineEdit.Password)
        self.ui.add_cluster_button.clicked.connect(self.concurrent_add_cluster)
        self.ui.cluster_name_addc_edit.setText(self.parameters['add_cluster_arguments']['cluster_name'])
        self.ui.user_edit.setText(self.parameters['add_cluster_arguments']['user'])
        self.ui.host_edit.setText(self.parameters['add_cluster_arguments']['host'])
        self.ui.port_edit.setValue(self.parameters['add_cluster_arguments']['port'])
        self.ui.add_actions_file_button.clicked.connect(self.open_actions_file_dialog)
        self.ui.delete_actions_file_button.clicked.connect(self.delete_actions_file)
        self.ui.add_key_button.clicked.connect(self.add_key)
        self.ui.delete_key_button.clicked.connect(self.delete_key)
        self.ui.auth_method_box.currentIndexChanged.connect(self.auth_method_toggled)
        self.actions_file_name = None
        self.key_path = None

    def auth_method_toggled(self):
        if self.ui.auth_method_box.currentText() == 'GENERATE_KEY':
            self.ui.password_edit.setDisabled(False)
            self.ui.add_key_button.setDisabled(True)
            self.ui.delete_key_button.setDisabled(True)
        else:
            self.ui.password_edit.setDisabled(True)
            self.ui.add_key_button.setDisabled(False)
            self.ui.delete_key_button.setDisabled(True)

        if self.key_path is not None:
            self.ui.delete_key_button.setDisabled(False)

    def concurrent_add_cluster(self):
        worker = Worker(self.add_cluster)
        worker.signals.result.connect(self.handle_complete_add_cluster)
        worker.signals.error.connect(self.handle_error_add_cluster)
        self.parent.threadpool.start(worker)

    def handle_complete_add_cluster(self):
        self.data_provider.add_cluster_signal.emit()
        self.popup_window.show_message("The cluster has been successfully added", WindowType.success)

    def handle_error_add_cluster(self, exception):
        if isinstance(exception, EmptyFieldError):
            self.popup_window.show_message("Cluster name cannot be empty", WindowType.error)
        elif isinstance(exception, ValueError):
            self.popup_window.show_message("Cluster already exists", WindowType.error)
        else:
            self.popup_window.show_message("An error occured while adding cluster", WindowType.error, exception)

    def add_cluster(self):
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
            save_environment()
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
            save_environment()

    def open_actions_file_dialog(self):
        self.actions_file_name, _ = QFileDialog.getOpenFileName()
        if self.actions_file_name:
            self.ui.selected_file_path_browser.setText(self.actions_file_name)
            self.ui.selected_file_path_browser.setEnabled(True)
            self.ui.delete_actions_file_button.setEnabled(True)

    def delete_actions_file(self):
        self.actions_file_name = None
        self.ui.selected_file_path_browser.setText("")
        self.ui.selected_file_path_browser.setEnabled(False)
        self.ui.delete_actions_file_button.setEnabled(False)

    def add_key(self):
        self.key_path, _ = QFileDialog.getOpenFileName()
        if self.key_path:
            self.ui.selected_key_browser.setText(self.key_path)
            self.ui.selected_key_browser.setEnabled(True)
            self.ui.delete_key_button.setEnabled(True)

    def delete_key(self):
        self.key_path = None
        self.ui.selected_key_browser.setText("")
        self.ui.selected_key_browser.setEnabled(False)
        self.ui.delete_key_button.setEnabled(False)
