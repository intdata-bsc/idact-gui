import os
from PyQt5 import uic
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLineEdit, QFileDialog

from idact.core.auth import AuthMethod, KeyType
from idact.core.add_cluster import add_cluster
from idact.detail.config.client.setup_actions_config import SetupActionsConfigImpl
from idact.detail.add_cluster_app import actions_parser as parser
from idact import save_environment, load_environment

from gui.functionality.popup_window import WindowType, PopUpWindow
from gui.helpers.parameter_saver import ParameterSaver
from gui.helpers.worker import Worker


class AddCluster(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.parent = parent

        self.popup_window = PopUpWindow()
        self.saver = ParameterSaver()
        self.parameters = self.saver.get_map()

        ui_path = os.path.dirname(os.path.abspath(__file__))
        self.ui = uic.loadUi(os.path.join(ui_path, '../widgets_templates/add-cluster.ui'))
        
        self.ui.password_edit.setEchoMode(QLineEdit.Password)
        self.ui.add_cluster_button.clicked.connect(self.concurrent_add_cluster)
        self.ui.cluster_name_addc_edit.setText(self.parameters['add_cluster_arguments']['cluster_name'])
        self.ui.user_edit.setText(self.parameters['add_cluster_arguments']['user'])
        self.ui.host_edit.setText(self.parameters['add_cluster_arguments']['host'])
        self.ui.port_edit.setValue(self.parameters['add_cluster_arguments']['port'])
        self.ui.auth_method_box.setCurrentText(self.parameters['add_cluster_arguments']['authentication'])
        self.ui.key_type_box.setCurrentText(self.parameters['add_cluster_arguments']['key_type'])
        self.ui.add_actions_file_button.clicked.connect(self.open_actions_file_dialog)
        self.ui.delete_actions_file_button.clicked.connect(self.delete_actions_file)

        self.actions_file_name = None

        lay = QVBoxLayout(self)
        lay.addWidget(self.ui)

    def concurrent_add_cluster(self):
        worker = Worker(self.add_cluster)
        worker.signals.result.connect(self.handle_complete_add_cluster)
        worker.signals.error.connect(self.handle_error_add_cluster)
        self.parent.threadpool.start(worker) 
    
    def handle_complete_add_cluster(self):
        self.popup_window.show_message("The cluster has been successfully added", WindowType.success)
    
    def handle_error_add_cluster(self, exception):
        if isinstance(exception, ValueError):
            self.popup_window.show_message("Cluster already exists", WindowType.error)
        else:
            self.popup_window.show_message("An error occured while adding cluster", WindowType.error)

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
