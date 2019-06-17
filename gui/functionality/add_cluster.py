from gui.decorators import addToClass
from idact.core.auth import AuthMethod, KeyType
from idact.core.add_cluster import add_cluster
from gui.idact_app import IdactApp


class AddCluster:
    def __init__(self, idact_app):
        idact_app.ui.add_cluster_button.clicked.connect(idact_app.add_cluster)

    @addToClass(IdactApp)
    def add_cluster(self):
        cluster_name = self.ui.cluster_name_addc_edit.text()
        user = self.ui.user_edit.text()
        host = self.ui.host_edit.text()
        port = int(self.ui.port_edit.text())
        auth = self.ui.auth_method_box.currentText()
        if auth == 'PUBLIC_KEY':
            key = self.ui.key_type_box.currentText()
            if key == 'RSA_KEY':
                add_cluster(name=cluster_name,
                            user=user,
                            host=host,
                            port=port,
                            auth=AuthMethod.PUBLIC_KEY,
                            key=KeyType.RSA,
                            install_key=True)
        elif auth == 'ASK_EVERYTIME':
            add_cluster(name=cluster_name,
                        user=user,
                        host=host,
                        port=port,
                        auth=AuthMethod.ASK)
