import sys
from PyQt5.QtWidgets import QApplication

from gui.configuration_provider import ConfigurationProvider
from gui.functionality.idact_app import IdactApp

if __name__ == '__main__':
    app = QApplication(sys.argv)
    conf_provider = ConfigurationProvider()
    if not conf_provider.check_if_conf_file_exists():
        conf_provider.create_conf_file()
    window = IdactApp()
    window.show()
    sys.exit(app.exec_())
