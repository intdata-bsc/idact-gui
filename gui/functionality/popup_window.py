""" One of the helper widgets.

    See: :class:`.ProgramInfoWindow`, :class:`.ShowLogsWindow`,
    :class:`.YesOrNoWindow`, :class:`.ShowJobsWindow`,
    :class:`.EditNativeArgumentsWindow`
"""
from enum import Enum
from PyQt5.QtWidgets import QWidget, QMessageBox


class WindowType(Enum):
    """ Available popup window types.

        :attr:`.success`: Window that shows a success message.

        :attr:`.error`: Window that shows an error message.

    """
    success = 1
    error = 2


class PopUpWindow(QWidget):
    """ Helper widget popup window.
    """
    def __init__(self):
        super().__init__()
        self.box = QMessageBox(self)
        self.box.addButton(QMessageBox.Ok)
        self.box.setDefaultButton(QMessageBox.Ok)

    def show_message(self, message, window_type, error_info=None):
        """ Shows the popup window.

            :param message: Message to be shown.
            :param window_type: Type of the window.
            :param error_info: Additional information about the error.
        """
        if window_type == WindowType.success:
            self.box.setWindowTitle("Success")
            self.box.setIcon(QMessageBox.Information)
        elif window_type == WindowType.error:
            self.box.setWindowTitle("Error")
            self.box.setIcon(QMessageBox.Critical)
        else:
            self.box.setIcon(QMessageBox.NoIcon)

        self.box.setText(message)
        self.box.setDetailedText("")

        if error_info:
            self.box.setDetailedText(str(error_info))

        ret = self.box.exec_()
        if ret == QMessageBox.Ok:
            return
