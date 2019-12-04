""" One of the helper widgets.

    See: :class:`.ProgramInfoWindow`, :class:`.PopUpWindow`,
    :class:`.ShowLogsWindow`, :class:`.ShowJobsWindow`,
    :class:`.EditNativeArgumentsWindow`, :class:`.HelpWindow`
"""
from PyQt5.QtWidgets import QWidget, QMessageBox


class ConfirmationWindow(QWidget):
    """ Helper widget window for confirmation.
    """

    def __init__(self):
        super().__init__()
        self.box = QMessageBox(self)
        self.box.addButton(QMessageBox.Yes)
        self.box.addButton(QMessageBox.No)
        self.box.setDefaultButton(QMessageBox.No)
        self.box.setWindowTitle("Warning")
        self.box.setIcon(QMessageBox.Question)

    def show_message(self, message):
        """ Shows the message in the confirmation dialog.

            :param message: Message text to be shown.
        """
        self.box.setText(message)
        ret = self.box.exec_()
        if ret == QMessageBox.Yes:
            return True
        else:
            return False
