from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic

from gui.native_saver import NativeArgsSaver
from gui.saver import ParameterSaver

Ui_MainWindow, QtBaseClass = uic.loadUiType('../widgets_templates/gui.ui')
Ui_AddNativeArgument, QtBaseClass = uic.loadUiType('../widgets_templates/add-native.ui')
Ui_RemoveNativeArgument, QtBaseClass = uic.loadUiType('../widgets_templates/remove-native.ui')
Ui_ShowNativeArgument, QtBaseClass = uic.loadUiType('../widgets_templates/show-native.ui')
Ui_Error, QtBaseClass = uic.loadUiType('../widgets_templates/error.ui')


class IdactApp(QMainWindow):
    def __init__(self):
        super(IdactApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.saver = ParameterSaver()
        self.native_args_saver = NativeArgsSaver()
        self.add_argument_window = AddArgumentApp()
        self.remove_argument_window = RemoveArgumentApp()
        self.show_native_arguments_window = ShowNativeArgumentsApp()
        self.parameters = self.saver.get_map()


class AddArgumentApp(QMainWindow):
    def __init__(self):
        super(AddArgumentApp, self).__init__()
        self.ui = Ui_AddNativeArgument()
        self.ui.setupUi(self)


class RemoveArgumentApp(QMainWindow):
    def __init__(self):
        super(RemoveArgumentApp, self).__init__()
        self.ui = Ui_RemoveNativeArgument()
        self.ui.setupUi(self)


class ShowNativeArgumentsApp(QMainWindow):
    def __init__(self):
        super(ShowNativeArgumentsApp, self).__init__()
        self.ui = Ui_ShowNativeArgument()
        self.ui.setupUi(self)

class ErrorApp(QMainWindow):
    def __init__(self, message="Error occured"):
        super(ErrorApp, self).__init__()
        self.ui = Ui_Error()
        self.ui.setupUi(self)
        self.ui.label.setText(message)
