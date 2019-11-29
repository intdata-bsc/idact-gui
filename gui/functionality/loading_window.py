from PyQt5.QtWidgets import QWidget
from gui.helpers.ui_loader import UiLoader


class LoadingWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = UiLoader.load_ui_from_file('loading.ui', self)

    def show_message(self, message):
        self.ui.message_label.setText(message)
        self.show()
