import sys
from PyQt5.QtWidgets import QApplication
from gui.functionality.add_cluster import AddCluster
from gui.functionality.idact_notebook import IdactNotebook
from gui.functionality.remove_cluster import RemoveCluster
from gui.idact_app import IdactApp

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = IdactApp()
    AddCluster(window)
    RemoveCluster(window)
    IdactNotebook(window)
    window.show()
    sys.exit(app.exec_())
