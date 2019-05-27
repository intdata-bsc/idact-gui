import sys
from PyQt5.QtWidgets import QApplication, QPushButton, QDialog, QGridLayout, QLabel, QLineEdit
from idact.core.auth import AuthMethod, KeyType
from idact.detail.cluster_app import main as deploy_notebook


class App(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("add cluster")
        self.width = 600
        self.height = 300
        self.resize(self.width, self.height)
        self.layout = QGridLayout()
        self.labels = {}
        self.edits = {}
        self.buttons = {}

        self.create_layout()

        self.create_edit()
        self.create_button()
        self.show()

    def create_layout(self):
        self.labels['cluster_name_label'] = QLabel("Cluster name", self)
        self.labels['user_label'] = QLabel("User", self)
        self.labels['host_label'] = QLabel("Host", self)

        self.layout.addWidget(self.labels['cluster_name_label'], 0, 0)
        self.layout.addWidget(self.labels['user_label'], 1, 0)
        self.layout.addWidget(self.labels['host_label'], 2, 0)

        self.setLayout(self.layout)

    def create_edit(self):
            self.edits['cluster_name_edit'] = QLineEdit()
            self.edits['user_edit'] = QLineEdit()
            self.edits['host_edit'] = QLineEdit()

            self.layout.addWidget(self.edits['cluster_name_edit'], 0, 1)
            self.layout.addWidget(self.edits['user_edit'], 1, 1)
            self.layout.addWidget(self.edits['host_edit'], 2, 1)

    def create_button(self):
        self.buttons['add_cluster_button'] = QPushButton("Add Cluster", self)
        self.buttons['add_cluster_button'].clicked.connect(self.add_cluster)
        self.layout.addWidget(self.buttons['add_cluster_button'])

    def add_cluster(self):
        cluster_name = self.edits['cluster_name_edit'].text()
        user = self.edits['user_edit'].text()
        host = self.edits['host_edit'].text()

        deploy_notebook.main(cluster_name=cluster_name,
                             user=user,
                             host=host,
                             port=22,
                             auth=AuthMethod.PUBLIC_KEY,
                             key=KeyType.RSA,
                             install_key=True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
