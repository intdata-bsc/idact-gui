import sys
from PyQt5.QtWidgets import QApplication

from gui.helpers.configuration_provider import ConfigurationProvider
from gui.functionality.main_window import MainWindow

if __name__ == '__main__':
    app = QApplication([])
    conf_provider = ConfigurationProvider()
    if not conf_provider.check_if_conf_file_exists():
        conf_provider.create_conf_file()
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
