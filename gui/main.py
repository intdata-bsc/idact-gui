import sys
from PyQt5.QtWidgets import QApplication

from gui.configuration_provider import ConfigurationProvider
from gui.functionality.add_cluster import AddCluster
from gui.functionality.idact_notebook import IdactNotebook
from gui.functionality.remove_cluster import RemoveCluster
from gui.functionality.idact_app import IdactApp

if __name__ == '__main__':
    app = QApplication(sys.argv)
    conf_provider = ConfigurationProvider()
    if not conf_provider.check_if_conf_file_exists():
        conf_provider.create_conf_file()
    window = IdactApp()
    AddCluster(window)
    RemoveCluster(window)
    IdactNotebook(window)
    window.show()
    sys.exit(app.exec_())
