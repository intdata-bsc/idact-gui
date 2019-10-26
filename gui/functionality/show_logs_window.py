import os

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QVBoxLayout


class ShowLogsWindow(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.setWindowTitle('Show logs window')

        ui_path = os.path.dirname(os.path.abspath(__file__))
        self.ui = uic.loadUi(os.path.join(ui_path, '../widgets_templates/logs.ui'))

        lay = QVBoxLayout(self)
        lay.addWidget(self.ui)

    def write(self, text):
        self.ui.logs_browser.append(text)
