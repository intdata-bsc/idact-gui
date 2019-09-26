from PyQt5.QtWidgets import QLineEdit

from gui.helpers.decorators import addToClass
from idact.core.auth import AuthMethod, KeyType
from idact.core.add_cluster import add_cluster
from idact import save_environment, load_environment
from gui.functionality.idact_app import IdactApp, WindowType
from idact.detail.log.get_logger import get_logger


class AddCluster:
    def __init__(self, idact_app):
        idact_app.ui.password_edit.setEchoMode(QLineEdit.Password)
        idact_app.ui.add_cluster_button.clicked.connect(idact_app.add_cluster)
        idact_app.ui.cluster_name_addc_edit.setText(idact_app.parameters['add_cluster_arguments']['cluster_name'])
        idact_app.ui.user_edit.setText(idact_app.parameters['add_cluster_arguments']['user'])
        idact_app.ui.host_edit.setText(idact_app.parameters['add_cluster_arguments']['host'])
        idact_app.ui.port_edit.setValue(idact_app.parameters['add_cluster_arguments']['port'])
        idact_app.ui.auth_method_box.setCurrentText(idact_app.parameters['add_cluster_arguments']['authentication'])
        idact_app.ui.key_type_box.setCurrentText(idact_app.parameters['add_cluster_arguments']['key_type'])

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

        log = get_logger(__name__)

        log.info("Loading environment...")
        load_environment()

        log.info("Adding cluster...")

        try:
            if auth == 'PUBLIC_KEY':
                key = self.ui.key_type_box.currentText()
                if key == 'RSA_KEY':
                    cluster = add_cluster(name=cluster_name,
                                          user=user,
                                          host=host,
                                          port=port,
                                          auth=AuthMethod.PUBLIC_KEY,
                                          key=KeyType.RSA,
                                          install_key=True)

            elif auth == 'ASK_EVERYTIME':
                cluster = add_cluster(name=cluster_name,
                                      user=user,
                                      host=host,
                                      port=port,
                                      auth=AuthMethod.ASK)

        except ValueError as e:
            self.popup_window.show_message("Cluster already exists", WindowType.error)


        cluster.config.use_jupyter_lab = False
        actions = ["module load plgrid/tools/python-intel/3.6.2"]
        cluster.config.setup_actions.jupyter = actions

        node = cluster.get_access_node()
        node.connect(password=password)

        save_environment()

        self.popup_window.show_message("The cluster has been successfully added", WindowType.success)

