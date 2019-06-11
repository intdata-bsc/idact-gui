import sys
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import uic
from idact.core.auth import AuthMethod, KeyType
from idact.detail.cluster_app import main as cluster_app

Ui_MainWindow, QtBaseClass = uic.loadUiType('../widgets_templates/add_cluster.ui')


class MyApp(QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.add_cluster_button.clicked.connect(self.add_cluster)

    def add_cluster(self):
        cluster_name = self.ui.cluster_name_edit.text()
        user = self.ui.user_edit.text()
        host = self.ui.host_edit.text()
        port = int(self.ui.port_edit.text())
        auth = self.ui.auth_method_box.currentText()
        if auth == 'PUBLIC_KEY':
            key = self.ui.key_type_box.currentText()
            if key == 'RSA_KEY':
                cluster_app.main(cluster_name=cluster_name,
                                 user=user,
                                 host=host,
                                 port=port,
                                 auth=AuthMethod.PUBLIC_KEY,
                                 key=KeyType.RSA,
                                 install_key=True)
        elif auth == 'ASK_EVERYTIME':
            cluster_app.main(cluster_name=cluster_name,
                             user=user,
                             host=host,
                             port=port,
                             auth=AuthMethod.ASK)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
