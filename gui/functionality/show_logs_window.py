from PyQt5.QtWidgets import QWidget

from gui.helpers.ui_loader import UiLoader


class ShowLogsWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.ui = UiLoader.load_ui_from_file('logs.ui', self)

    def write(self, text):
        self.ui.logs_browser.append(text)

    def flush(self):
        pass
