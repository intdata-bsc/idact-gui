from PyQt5.QtWidgets import QLineEdit

from gui.helpers.decorators import addToClass
from PyQt5.QtWidgets import QFileDialog
from idact.detail.config.client.setup_actions_config import SetupActionsConfigImpl
from gui.helpers.worker import Worker
from idact.core.auth import AuthMethod, KeyType
from idact.core.add_cluster import add_cluster
from idact import save_environment, load_environment
from gui.functionality.idact_app import IdactApp, WindowType
from idact.detail.add_cluster_app import actions_parser as parser


class AddCluster:
    def __init__(self, idact_app):
        idact_app.ui.password_edit.setEchoMode(QLineEdit.Password)
        idact_app.ui.add_cluster_button.clicked.connect(idact_app.concurrent_add_cluster)
        idact_app.ui.cluster_name_addc_edit.setText(idact_app.parameters['add_cluster_arguments']['cluster_name'])
        idact_app.ui.user_edit.setText(idact_app.parameters['add_cluster_arguments']['user'])
        idact_app.ui.host_edit.setText(idact_app.parameters['add_cluster_arguments']['host'])
        idact_app.ui.port_edit.setValue(idact_app.parameters['add_cluster_arguments']['port'])
        idact_app.ui.auth_method_box.setCurrentText(idact_app.parameters['add_cluster_arguments']['authentication'])
        idact_app.ui.key_type_box.setCurrentText(idact_app.parameters['add_cluster_arguments']['key_type'])
        idact_app.ui.add_actions_file_button.clicked.connect(idact_app.open_actions_file_dialog)
        idact_app.ui.delete_actions_file_button.clicked.connect(idact_app.delete_actions_file)

    @addToClass(IdactApp)
    def concurrent_add_cluster(self):
        worker = Worker(self.add_cluster)
        worker.signals.result.connect(self.handle_complete_add_cluster)
        worker.signals.error.connect(self.handle_error_add_cluster)
        self.threadpool.start(worker) 
    
    @addToClass(IdactApp)
    def handle_complete_add_cluster(self):
        self.popup_window.show_message("The cluster has been successfully added", WindowType.success)
    
    @addToClass(IdactApp)
    def handle_error_add_cluster(self, exception):
        if isinstance(exception, ValueError):
            self.popup_window.show_message("Cluster already exists", WindowType.error)
        else:
            self.popup_window.show_message("An error occured while adding cluster", WindowType.error)

    @addToClass(IdactApp)
    def add_cluster(self):
        load_environment()

        cluster_name = self.ui.cluster_name_addc_edit.text()
        self.parameters['add_cluster_arguments']['cluster_name'] = cluster_name
        user = self.ui.user_edit.text()
        self.parameters['add_cluster_arguments']['user'] = user
        host = self.ui.host_edit.text()
        self.parameters['add_cluster_arguments']['host'] = host
        port = int(self.ui.port_edit.text())
        self.parameters['add_cluster_arguments']['port'] = port
        auth = self.ui.auth_method_box.currentText()
        self.parameters['add_cluster_arguments']['authentication'] = auth
        self.parameters['add_cluster_arguments']['key_type'] = self.ui.key_type_box.currentText()
        self.saver.save(self.parameters)
        password = self.ui.password_edit.text()

        use_jupyter_lab = self.ui.use_jupyter_lab_check_box.isChecked()

        setup_actions = None
        if self.actions_file_name is not None:
            setup_actions = SetupActionsConfigImpl()
            setup_actions.jupyter = parser.parse_actions(self.actions_file_name)

        if auth == 'PUBLIC_KEY':
            key = self.ui.key_type_box.currentText()
            if key == 'RSA_KEY':
                cluster = add_cluster(name=cluster_name,
                                        user=user,
                                        host=host,
                                        port=port,
                                        auth=AuthMethod.PUBLIC_KEY,
                                        key=KeyType.RSA,
                                        install_key=True,
                                        setup_actions=setup_actions,
                                        use_jupyter_lab=use_jupyter_lab)
        elif auth == 'ASK_EVERYTIME':
            cluster = add_cluster(name=cluster_name,
                                    user=user,
                                    host=host,
                                    port=port,
                                    auth=AuthMethod.ASK,
                                    setup_actions=setup_actions,
                                    use_jupyter_lab=use_jupyter_lab)

        node = cluster.get_access_node()
        node.connect(password=password)

        save_environment()
        return

    @addToClass(IdactApp)
    def open_actions_file_dialog(self):
        self.actions_file_name, _ = QFileDialog.getOpenFileName()
        if self.actions_file_name:
            self.ui.selected_file_path_browser.setText(self.actions_file_name)
            self.ui.selected_file_path_browser.setEnabled(True)
            self.ui.delete_actions_file_button.setEnabled(True)

    @addToClass(IdactApp)
    def delete_actions_file(self):
        self.actions_file_name = None
        self.ui.selected_file_path_browser.setText("")
        self.ui.selected_file_path_browser.setEnabled(False)
        self.ui.delete_actions_file_button.setEnabled(False)

