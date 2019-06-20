from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from gui.saver import ParameterSaver

Ui_MainWindow, QtBaseClass = uic.loadUiType('../widgets_templates/gui.ui')


class IdactApp(QMainWindow):
    def __init__(self):
        super(IdactApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.saver = ParameterSaver()
        self.parameters = self.saver.get_map()
