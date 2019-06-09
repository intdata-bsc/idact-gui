import sys
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import uic
from idact.detail.jupyter_app import main as deploy_notebook

Ui_MainWindow, QtBaseClass = uic.loadUiType('../widgets_templates/deploy_notebook.ui')


class MyApp(QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.deploy_button.clicked.connect(self.deploy_notebook)

    def deploy_notebook(self):
        cluster_name = self.ui.cluster_name_edit.text()
        nodes = self.ui.nodes_edit.text()
        cores = self.ui.cores_edit.text()
        memory = self.ui.memory_edit.text()
        walltime = self.ui.walltime_edit.text()

        deploy_notebook.main(cluster_name=cluster_name,
                             environment=None,
                             save_defaults=False,
                             reset_defaults=False,
                             nodes=nodes,
                             cores=cores,
                             memory_per_node=memory,
                             walltime=walltime)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
