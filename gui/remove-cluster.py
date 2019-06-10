import sys
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import uic
# from idact.detail.cluster_app import main as cluster
from idact.core.remove_cluster import remove_cluster
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# work in progress - need updated idact to have cluster_app
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

Ui_MainWindow, QtBaseClass = uic.loadUiType('../widgets_templates/remove_cluster.ui')


class MyApp(QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.remove_cluster_button.clicked.connect(self.remove_cluster)

    def remove_cluster(self):
        cluster_name = self.ui.cluster_name_edit.text()
        remove_cluster(cluster_name)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
