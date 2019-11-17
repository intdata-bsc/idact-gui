from PyQt5.QtWidgets import QWidget
from gui.helpers.ui_loader import UiLoader


class ProgramInfoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = UiLoader.load_ui_from_file('about.ui', self)
