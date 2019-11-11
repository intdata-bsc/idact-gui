import os
from PyQt5 import uic
from PyQt5.QtWidgets import QVBoxLayout, QWidget


class About(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.parent = parent

        ui_path = os.path.dirname(os.path.abspath(__file__))
        self.ui = uic.loadUi(os.path.join(ui_path, '../widgets_templates/about.ui'))

        lay = QVBoxLayout(self)
        lay.addWidget(self.ui)
