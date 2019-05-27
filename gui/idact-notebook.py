import sys
from PyQt5.QtWidgets import QApplication, QPushButton, QDialog, QGridLayout, QLabel, QLineEdit
from idact.detail.jupyter_app import main as deploy_notebook


class App(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("idact notebook")
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

        self.labels['nodes_label'] = QLabel("Nodes", self)
        self.labels['cores_label'] = QLabel("Cores per node", self)
        self.labels['memory_label'] = QLabel("Memory per node (GiB)", self)
        self.labels['walltime_label'] = QLabel("Walltime", self)

        self.layout.addWidget(self.labels['cluster_name_label'], 0, 0)
        self.layout.addWidget(self.labels['nodes_label'], 1, 0)
        self.layout.addWidget(self.labels['cores_label'], 2, 0)
        self.layout.addWidget(self.labels['memory_label'], 3, 0)
        self.layout.addWidget(self.labels['walltime_label'], 4, 0)

        self.setLayout(self.layout)

    def create_edit(self):
            self.edits['cluster_name_edit'] = QLineEdit()
            self.edits['nodes_edit'] = QLineEdit()
            self.edits['cores_edit'] = QLineEdit()
            self.edits['memory_edit'] = QLineEdit()
            self.edits['walltime_edit'] = QLineEdit()

            self.layout.addWidget(self.edits['cluster_name_edit'], 0, 1)

            self.layout.addWidget(self.edits['nodes_edit'], 1, 1)
            self.layout.addWidget(self.edits['cores_edit'], 2, 1)
            self.layout.addWidget(self.edits['memory_edit'], 3, 1)
            self.layout.addWidget(self.edits['walltime_edit'], 4, 1)

    def create_button(self):
        self.buttons['deploy_button'] = QPushButton("Deploy Jupyter Notebook", self)
        self.buttons['deploy_button'].clicked.connect(self.deploy)
        self.layout.addWidget(self.buttons['deploy_button'])

    def deploy(self):
        cluster_name = self.edits['cluster_name_edit'].text()
        nodes = self.edits['nodes_edit'].text()
        cores = self.edits['cores_edit'].text()
        memory = self.edits['memory_edit'].text()
        walltime = self.edits['walltime_edit'].text()

        deploy_notebook.main(cluster_name=cluster_name,
                             environment=None,
                             save_defaults=False,
                             reset_defaults=False,
                             nodes=nodes,
                             cores=cores,
                             memory_per_node=memory+"GiB",
                             walltime=walltime,
                             native_arg=[
                                 ('partition', 'plgrid-testing')
                               ])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
