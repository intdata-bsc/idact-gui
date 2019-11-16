from enum import Enum
from PyQt5.QtWidgets import QWidget, QMessageBox


class WindowType(Enum):
    success = 1
    error = 2


class PopUpWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.box = QMessageBox(self)
        self.box.addButton(QMessageBox.Ok)
        self.box.setDefaultButton(QMessageBox.Ok)

    def show_message(self, message, window_type, error_info=None):
        if window_type == WindowType.success:
            self.box.setWindowTitle("Success")
            self.box.setIcon(QMessageBox.Information)
        elif window_type == WindowType.error:
            self.box.setWindowTitle("Error")
            self.box.setIcon(QMessageBox.Critical)
        else:
            self.box.setIcon(QMessageBox.NoIcon)

        self.box.setText(message)

        if error_info:
            self.box.setDetailedText('Details: ' + str(error_info))

        ret = self.box.exec_()
        if ret == QMessageBox.Ok:
            return
